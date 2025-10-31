"""Tests for Amazon Bestsellers commerce processor."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.commerce_processor import CommerceProcessor


def test_process_amazon_product():
    """Test processing Amazon product data to unified format."""
    product_data = {
        'asin': 'B001TEST',
        'title': 'Test Product',
        'brand': 'Test Brand',
        'category': 'Electronics',
        'price': 99.99,
        'currency': 'USD',
        'seller_name': 'Test Seller',
        'seller_rating': 4.8,
        'seller_feedback_count': 10000,
        'sales_rank': 15,
        'category_rank': 3,
        'rating': 4.7,
        'review_count': 5000,
        'review_velocity': 50,
        'rank_change_24h': -5,
        'original_price': 129.99,
        'review_momentum': 'increasing'
    }
    
    unified = CommerceProcessor.process_amazon_product(product_data)
    
    assert unified['source'] == 'amazon_bestsellers'
    assert unified['source_id'] == 'B001TEST'
    assert unified['product']['name'] == 'Test Product'
    assert unified['product']['brand'] == 'Test Brand'
    assert unified['product']['category'] == 'Electronics'
    assert unified['product']['price'] == 99.99
    assert unified['product']['currency'] == 'USD'
    
    assert unified['seller']['name'] == 'Test Seller'
    assert unified['seller']['rating'] == 4.8
    assert unified['seller']['feedback_count'] == 10000
    
    assert unified['metrics']['sales_rank'] == 15
    assert unified['metrics']['category_rank'] == 3
    assert unified['metrics']['rating'] == 4.7
    assert unified['metrics']['review_count'] == 5000
    
    assert 'universal_metrics' in unified
    assert 'popularity_score' in unified['universal_metrics']
    assert 'trend_strength' in unified['universal_metrics']
    assert 'consumer_interest' in unified['universal_metrics']


def test_extract_tags_from_product():
    """Test extracting tags from product data."""
    product_data = {
        'category': 'Electronics',
        'brand': 'Test Brand',
        'bestseller_badge': True,
        'amazon_choice': True,
        'has_prime': True,
        'price': 99.99
    }
    
    tags = CommerceProcessor.extract_tags_from_product(product_data)
    
    assert 'Electronics' in tags
    assert 'Test Brand' in tags
    assert 'bestseller' in tags
    assert 'amazon_choice' in tags
    assert 'prime' in tags
    assert 'mid_range' in tags  # Price is 99.99


def test_extract_tags_price_ranges():
    """Test price range tagging."""
    # Budget product
    product1 = {'price': 19.99}
    tags1 = CommerceProcessor.extract_tags_from_product(product1)
    assert 'budget' in tags1
    
    # Mid-range product
    product2 = {'price': 75.00}
    tags2 = CommerceProcessor.extract_tags_from_product(product2)
    assert 'mid_range' in tags2
    
    # Premium product
    product3 = {'price': 299.99}
    tags3 = CommerceProcessor.extract_tags_from_product(product3)
    assert 'premium' in tags3


def test_extract_tags_minimal_data():
    """Test extracting tags with minimal product data."""
    product_data = {
        'category': 'Books'
    }
    
    tags = CommerceProcessor.extract_tags_from_product(product_data)
    
    assert 'Books' in tags
    assert tags.count(',') < 3  # Should have minimal tags


def test_extract_tags_no_badges():
    """Test extracting tags when no badges are present."""
    product_data = {
        'category': 'Home & Kitchen',
        'brand': 'Generic Brand',
        'bestseller_badge': False,
        'amazon_choice': False,
        'has_prime': False,
        'price': 15.99
    }
    
    tags = CommerceProcessor.extract_tags_from_product(product_data)
    
    assert 'bestseller' not in tags
    assert 'amazon_choice' not in tags
    assert 'prime' not in tags
    assert 'budget' in tags


def test_unified_format_structure():
    """Test that unified format has all required fields."""
    product_data = {
        'asin': 'B001TEST',
        'title': 'Test',
        'price': 99.99,
        'rating': 4.5,
        'review_count': 100,
        'sales_rank': 10
    }
    
    unified = CommerceProcessor.process_amazon_product(product_data)
    
    # Check required top-level keys
    assert 'source' in unified
    assert 'source_id' in unified
    assert 'product' in unified
    assert 'seller' in unified
    assert 'metrics' in unified
    assert 'trends' in unified
    assert 'universal_metrics' in unified
    
    # Check product fields
    assert 'name' in unified['product']
    assert 'brand' in unified['product']
    assert 'category' in unified['product']
    assert 'price' in unified['product']
    assert 'currency' in unified['product']


def test_price_change_calculation():
    """Test that price change percentage is calculated."""
    product_data = {
        'asin': 'B001TEST',
        'title': 'Test',
        'price': 79.99,
        'original_price': 99.99,
        'rating': 4.5,
        'review_count': 100
    }
    
    unified = CommerceProcessor.process_amazon_product(product_data)
    
    assert unified['trends']['price_change_pct'] is not None
    # Should be ~20% discount
    assert 19 < unified['trends']['price_change_pct'] < 21
