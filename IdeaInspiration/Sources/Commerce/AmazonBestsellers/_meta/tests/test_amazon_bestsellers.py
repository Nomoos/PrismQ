"""Tests for Amazon Bestsellers plugin."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plugins.amazon_bestsellers import AmazonBestsellersPlugin
from core.config import Config
import tempfile


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("AMAZON_CATEGORIES=Electronics,Books\n")
        f.write("AMAZON_MAX_PRODUCTS=5\n")
        f.write("AMAZON_DOMAIN=amazon.com\n")
        f.write("AMAZON_DELAY_SECONDS=0.1\n")
        env_path = f.name
    
    config = Config(env_path, interactive=False)
    yield config
    
    import os
    if os.path.exists(env_path):
        os.unlink(env_path)


def test_plugin_initialization(mock_config):
    """Test plugin initialization with config."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    assert plugin.domain == "amazon.com"
    assert plugin.max_products == 5
    assert plugin.categories == ["Electronics", "Books"]
    assert plugin.delay == 0.1


def test_get_source_name(mock_config):
    """Test getting source name."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    assert plugin.get_source_name() == "amazon_bestsellers"


def test_scrape_returns_products(mock_config):
    """Test that scrape returns product list."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    products = plugin.scrape()
    
    assert isinstance(products, list)
    assert len(products) > 0


def test_scrape_respects_category_limit(mock_config):
    """Test that scrape respects category configuration."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    products = plugin.scrape()
    
    # Should have products from both categories
    categories = set(p['category'] for p in products)
    assert 'Electronics' in categories
    assert 'Books' in categories


def test_create_mock_product(mock_config):
    """Test creating a mock product."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    product = plugin._create_mock_product("Electronics", 0)
    
    # Check required fields
    assert 'asin' in product
    assert 'title' in product
    assert 'brand' in product
    assert 'category' in product
    assert 'price' in product
    assert 'currency' in product
    assert 'rating' in product
    assert 'review_count' in product
    assert 'sales_rank' in product
    assert 'category_rank' in product
    
    # Check values
    assert product['category'] == 'Electronics'
    assert product['currency'] == 'USD'
    assert product['sales_rank'] == 1  # Index 0 + 1
    assert product['in_stock'] is True


def test_mock_product_variations(mock_config):
    """Test that mock products have variations."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    product1 = plugin._create_mock_product("Electronics", 0)
    product2 = plugin._create_mock_product("Electronics", 1)
    
    # Different products should have different attributes
    assert product1['asin'] != product2['asin']
    assert product1['title'] != product2['title']
    assert product1['price'] != product2['price']
    assert product1['sales_rank'] != product2['sales_rank']


def test_mock_product_has_platform_specific(mock_config):
    """Test that mock products have platform-specific data."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    product = plugin._create_mock_product("Electronics", 0)
    
    assert 'platform_specific' in product
    assert 'fulfillment' in product['platform_specific']
    assert 'url' in product['platform_specific']
    assert 'amazon.com' in product['platform_specific']['url']


def test_mock_product_pricing(mock_config):
    """Test mock product pricing logic."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    product = plugin._create_mock_product("Electronics", 0)
    
    # Should have price and original price
    assert 'price' in product
    assert 'original_price' in product
    # Original price should be higher (discount scenario)
    assert product['original_price'] > product['price']


def test_mock_product_seller_info(mock_config):
    """Test mock product seller information."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    product = plugin._create_mock_product("Electronics", 0)
    
    assert 'seller_name' in product
    assert 'seller_rating' in product
    assert 'seller_feedback_count' in product
    # Seller rating should be reasonable
    assert 0 <= product['seller_rating'] <= 5


def test_scrape_with_api_not_implemented(mock_config):
    """Test that API scraping raises NotImplementedError."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    with pytest.raises(NotImplementedError):
        plugin.scrape_with_api("test_key", "test_secret")


def test_plugin_headers(mock_config):
    """Test that plugin has proper headers set."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    assert hasattr(plugin, 'headers')
    assert 'User-Agent' in plugin.headers
    assert 'Mozilla' in plugin.headers['User-Agent']


def test_format_tags(mock_config):
    """Test format_tags method from base class."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    tags = ['Electronics', 'Books', 'Tech']
    formatted = plugin.format_tags(tags)
    
    assert formatted == 'Electronics,Books,Tech'


def test_format_tags_with_spaces(mock_config):
    """Test format_tags handles whitespace correctly."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    tags = [' Electronics ', '  Books  ', 'Tech']
    formatted = plugin.format_tags(tags)
    
    assert formatted == 'Electronics,Books,Tech'


def test_format_tags_with_empty_strings(mock_config):
    """Test format_tags filters empty strings."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    tags = ['Electronics', '', 'Books', '  ', 'Tech']
    formatted = plugin.format_tags(tags)
    
    assert formatted == 'Electronics,Books,Tech'


def test_scrape_category(mock_config):
    """Test scraping a single category."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    products = plugin._scrape_category("Electronics")
    
    assert isinstance(products, list)
    assert len(products) > 0
    # All products should be from Electronics category
    for product in products:
        assert product['category'] == "Electronics"


def test_mock_product_prime_variations(mock_config):
    """Test that Prime availability varies."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    product_even = plugin._create_mock_product("Electronics", 0)
    product_odd = plugin._create_mock_product("Electronics", 1)
    
    # Even index should have Prime
    assert product_even['has_prime'] is True
    # Odd index should not have Prime
    assert product_odd['has_prime'] is False


def test_mock_product_rank_matches_index(mock_config):
    """Test that product rank matches its index."""
    plugin = AmazonBestsellersPlugin(mock_config)
    
    for i in range(3):
        product = plugin._create_mock_product("Electronics", i)
        assert product['sales_rank'] == i + 1
        assert product['category_rank'] == i + 1
