"""Integration tests for Amazon Bestsellers source."""

import pytest
import tempfile
import os
from pathlib import Path

from src.core.config import Config
from src.core.database import Database
from src.plugins.amazon_bestsellers import AmazonBestsellersPlugin
from src.core.commerce_processor import CommerceProcessor
from src.core.metrics import CommerceMetrics


@pytest.fixture
def temp_setup():
    """Create temporary environment for integration testing."""
    temp_dir = tempfile.mkdtemp()
    env_path = Path(temp_dir) / ".env"
    
    with open(env_path, 'w') as f:
        f.write(f"DATABASE_URL=sqlite:///{temp_dir}/integration_test.db\n")
        f.write("AMAZON_CATEGORIES=Electronics\n")
        f.write("AMAZON_MAX_PRODUCTS=3\n")
        f.write("AMAZON_DELAY_SECONDS=0.1\n")
    
    yield temp_dir, str(env_path)
    
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_full_scrape_workflow(temp_setup):
    """Test complete scraping workflow from config to database storage."""
    temp_dir, env_path = temp_setup
    
    # 1. Load configuration
    config = Config(env_path, interactive=False)
    assert config.amazon_categories == ["Electronics"]
    
    # 2. Initialize database
    db = Database(config.database_path, interactive=False)
    
    # 3. Create plugin and scrape
    plugin = AmazonBestsellersPlugin(config)
    products = plugin.scrape()
    
    assert len(products) > 0
    
    # 4. Process and save each product
    saved_count = 0
    for product in products:
        # Transform to unified format
        unified = CommerceProcessor.process_amazon_product(product)
        
        # Create metrics
        metrics = CommerceMetrics.from_amazon(product)
        
        # Save to database
        success = db.insert_product(
            source=unified['source'],
            source_id=unified['source_id'],
            title=unified['product']['name'],
            brand=unified['product'].get('brand'),
            category=unified['product'].get('category'),
            price=unified['product'].get('price'),
            currency=unified['product'].get('currency', 'USD'),
            description=product.get('description'),
            tags=CommerceProcessor.extract_tags_from_product(product),
            score=metrics.consumer_interest or 0.0,
            score_dictionary=str(metrics.to_dict())
        )
        
        if success:
            saved_count += 1
    
    assert saved_count == len(products)
    
    # 5. Verify data in database
    all_products = db.get_all_products(limit=10)
    assert len(all_products) == saved_count
    
    # 6. Check statistics
    stats = db.get_statistics()
    assert stats['total'] == saved_count
    assert 'amazon_bestsellers' in stats['by_source']


def test_deduplication_workflow(temp_setup):
    """Test that duplicate products are handled correctly."""
    temp_dir, env_path = temp_setup
    
    config = Config(env_path, interactive=False)
    db = Database(config.database_path, interactive=False)
    
    # Insert same product twice
    product_data = {
        'asin': 'B001DEDUP',
        'title': 'Dedup Test Product',
        'category': 'Electronics',
        'price': 99.99
    }
    
    unified = CommerceProcessor.process_amazon_product(product_data)
    
    # First insert
    success1 = db.insert_product(
        source=unified['source'],
        source_id=unified['source_id'],
        title=unified['product']['name'],
        category=unified['product'].get('category'),
        price=unified['product'].get('price')
    )
    
    # Second insert (should update, not create new)
    success2 = db.insert_product(
        source=unified['source'],
        source_id=unified['source_id'],
        title=unified['product']['name'] + " Updated",
        category=unified['product'].get('category'),
        price=89.99
    )
    
    assert success1 is True  # First insert successful
    assert success2 is False  # Second is update
    
    # Should still have only one product
    stats = db.get_statistics()
    assert stats['total'] == 1


def test_metrics_calculation_integration(temp_setup):
    """Test metrics calculation in full workflow."""
    temp_dir, env_path = temp_setup
    
    product_data = {
        'asin': 'B001METRICS',
        'title': 'Metrics Test',
        'price': 79.99,
        'original_price': 99.99,
        'rating': 4.5,
        'review_count': 1000,
        'sales_rank': 10,
        'rank_change_24h': -5
    }
    
    # Create metrics
    metrics = CommerceMetrics.from_amazon(product_data)
    
    # Should have calculated derived metrics
    assert metrics.discount_percentage is not None
    assert metrics.popularity_score is not None
    assert metrics.trend_strength is not None
    assert metrics.consumer_interest is not None
    
    # Verify ranges
    assert 0 <= metrics.popularity_score <= 10
    assert 0 <= metrics.trend_strength <= 10
    assert 0 <= metrics.consumer_interest <= 10


def test_database_product_retrieval(temp_setup):
    """Test various database retrieval methods."""
    temp_dir, env_path = temp_setup
    
    config = Config(env_path, interactive=False)
    db = Database(config.database_path, interactive=False)
    
    # Insert test products in different categories
    for i, category in enumerate(['Electronics', 'Books', 'Electronics']):
        db.insert_product(
            source="amazon_bestsellers",
            source_id=f"B00{i}DB",
            title=f"Product {i}",
            category=category,
            price=99.99 + i
        )
    
    # Test get_all_products
    all_prods = db.get_all_products(limit=10)
    assert len(all_prods) == 3
    
    # Test get_products_by_category
    electronics = db.get_products_by_category("Electronics", limit=10)
    assert len(electronics) == 2
    
    books = db.get_products_by_category("Books", limit=10)
    assert len(books) == 1
    
    # Test statistics
    stats = db.get_statistics()
    assert stats['total'] == 3
    assert stats['by_category']['Electronics'] == 2
    assert stats['by_category']['Books'] == 1
