"""Tests for Etsy Trending plugin."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plugins.etsy_trending import EtsyTrendingPlugin
from core.config import Config
import tempfile


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("ETSY_CATEGORIES=jewelry,home-living\n")
        f.write("ETSY_MAX_LISTINGS=5\n")
        f.write("ETSY_DELAY_SECONDS=0.1\n")
        env_path = f.name
    
    config = Config(env_path, interactive=False)
    yield config
    
    import os
    if os.path.exists(env_path):
        os.unlink(env_path)


def test_plugin_initialization(mock_config):
    """Test plugin initialization with config."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    assert plugin.max_listings == 5
    assert plugin.categories == ["jewelry", "home-living"]
    assert plugin.delay == 0.1


def test_get_source_name(mock_config):
    """Test getting source name."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    assert plugin.get_source_name() == "etsy_trending"


def test_scrape_returns_products(mock_config):
    """Test that scrape returns product list."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    products = plugin.scrape()
    
    assert isinstance(products, list)
    assert len(products) > 0


def test_scrape_respects_category_config(mock_config):
    """Test that scrape respects category configuration."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    products = plugin.scrape()
    
    # Should have products from both categories
    categories = set(p['category'] for p in products)
    assert 'jewelry' in categories or 'home-living' in categories


def test_create_mock_product(mock_config):
    """Test creating a mock product."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    product = plugin._create_mock_product("jewelry", 0)
    
    # Check required fields
    assert 'listing_id' in product
    assert 'title' in product
    assert 'shop_name' in product
    assert 'category' in product
    assert 'price' in product
    assert 'currency' in product
    assert 'rating' in product
    assert 'review_count' in product
    
    # Check values
    assert product['category'] == 'jewelry'
    assert product['currency'] == 'USD'
    
    # Check platform_specific has views
    assert 'platform_specific' in product
    assert 'views' in product['platform_specific']


def test_mock_product_variations(mock_config):
    """Test that mock products have variations."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    product1 = plugin._create_mock_product("jewelry", 0)
    product2 = plugin._create_mock_product("jewelry", 1)
    
    # Different products should have different attributes
    assert product1['listing_id'] != product2['listing_id']
    assert product1['title'] != product2['title']
    assert product1['price'] != product2['price']


def test_mock_product_has_platform_specific(mock_config):
    """Test that mock products have platform-specific data."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    product = plugin._create_mock_product("jewelry", 0)
    
    assert 'platform_specific' in product
    assert 'platform' in product['platform_specific']
    assert product['platform_specific']['platform'] == 'etsy'


def test_scrape_category(mock_config):
    """Test scraping a single category."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    products = plugin._scrape_category("jewelry")
    
    assert isinstance(products, list)
    assert len(products) > 0
    # All products should be from jewelry category
    for product in products:
        assert product['category'] == "jewelry"


def test_format_tags(mock_config):
    """Test format_tags method from base class."""
    plugin = EtsyTrendingPlugin(mock_config)
    
    tags = ['jewelry', 'handmade', 'unique']
    formatted = plugin.format_tags(tags)
    
    assert formatted == 'jewelry,handmade,unique'
