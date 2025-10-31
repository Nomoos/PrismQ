"""Tests for Amazon Bestsellers database operations."""

import pytest
import tempfile
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    db = Database(db_path, interactive=False)
    yield db
    
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_database_creation(temp_db):
    """Test database creation and initialization."""
    assert os.path.exists(temp_db.db_path)


def test_insert_product(temp_db):
    """Test inserting a product."""
    success = temp_db.insert_product(
        source="amazon_bestsellers",
        source_id="B001TEST",
        title="Test Product",
        brand="Test Brand",
        category="Electronics",
        price=99.99,
        currency="USD",
        description="Test description",
        tags="electronics,test",
        score=8.5,
        score_dictionary='{"popularity": 8.5}'
    )
    
    assert success is True


def test_insert_duplicate_product(temp_db):
    """Test inserting duplicate product (should update)."""
    # Insert first time
    temp_db.insert_product(
        source="amazon_bestsellers",
        source_id="B001TEST",
        title="Test Product",
        brand="Test Brand",
        category="Electronics",
        price=99.99
    )
    
    # Insert again (should update)
    success = temp_db.insert_product(
        source="amazon_bestsellers",
        source_id="B001TEST",
        title="Test Product Updated",
        brand="Test Brand",
        category="Electronics",
        price=89.99
    )
    
    assert success is False  # False indicates update, not insert


def test_get_all_products(temp_db):
    """Test retrieving all products."""
    # Insert test products
    for i in range(5):
        temp_db.insert_product(
            source="amazon_bestsellers",
            source_id=f"B00{i}TEST",
            title=f"Test Product {i}",
            category="Electronics",
            price=99.99 + i
        )
    
    products = temp_db.get_all_products(limit=10)
    assert len(products) == 5


def test_get_products_by_category(temp_db):
    """Test retrieving products by category."""
    # Insert products in different categories
    temp_db.insert_product(
        source="amazon_bestsellers",
        source_id="B001ELEC",
        title="Electronics Product",
        category="Electronics",
        price=99.99
    )
    temp_db.insert_product(
        source="amazon_bestsellers",
        source_id="B002BOOK",
        title="Book Product",
        category="Books",
        price=19.99
    )
    
    electronics = temp_db.get_products_by_category("Electronics", limit=10)
    books = temp_db.get_products_by_category("Books", limit=10)
    
    assert len(electronics) == 1
    assert len(books) == 1
    assert electronics[0]['category'] == "Electronics"
    assert books[0]['category'] == "Books"


def test_get_statistics(temp_db):
    """Test getting database statistics."""
    # Insert test products
    for i in range(3):
        temp_db.insert_product(
            source="amazon_bestsellers",
            source_id=f"B00{i}TEST",
            title=f"Test Product {i}",
            category="Electronics",
            price=99.99
        )
    
    stats = temp_db.get_statistics()
    assert stats['total'] == 3
    assert 'amazon_bestsellers' in stats['by_source']
    assert stats['by_source']['amazon_bestsellers'] == 3
    assert 'Electronics' in stats['by_category']
    assert stats['by_category']['Electronics'] == 3


def test_database_schema(temp_db):
    """Test that database has correct schema."""
    import sqlite3
    conn = sqlite3.connect(temp_db.db_path)
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    assert 'products' in tables
    
    # Check products table columns
    cursor.execute("PRAGMA table_info(products)")
    columns = {row[1] for row in cursor.fetchall()}
    required_columns = {'id', 'source', 'source_id', 'title', 'brand', 'category', 
                       'price', 'currency', 'description', 'tags', 'score', 
                       'score_dictionary', 'created_at', 'updated_at'}
    assert required_columns.issubset(columns)
    
    conn.close()


def test_get_recent_products(temp_db):
    """Test getting recent products."""
    # Insert test products
    for i in range(3):
        temp_db.insert_product(
            source="amazon_bestsellers",
            source_id=f"B00{i}TEST",
            title=f"Test Product {i}",
            category="Electronics",
            price=99.99
        )
    
    # Get recent products (should work same as get_all_products)
    products = temp_db.get_all_products(limit=2)
    assert len(products) == 2


def test_get_product_by_id(temp_db):
    """Test retrieving a specific product by source and ID."""
    # Insert a product
    temp_db.insert_product(
        source="amazon_bestsellers",
        source_id="B001SPECIFIC",
        title="Specific Product",
        category="Electronics",
        price=99.99,
        brand="Test Brand"
    )
    
    # Retrieve it
    product = temp_db.get_product("amazon_bestsellers", "B001SPECIFIC")
    
    assert product is not None
    assert product['source_id'] == "B001SPECIFIC"
    assert product['title'] == "Specific Product"
    assert product['brand'] == "Test Brand"
    
    # Try to get non-existent product
    not_found = temp_db.get_product("amazon_bestsellers", "B999NOTEXIST")
    assert not_found is None
