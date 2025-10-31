"""Tests for Amazon Bestsellers metrics calculation."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.metrics import CommerceMetrics


def test_commerce_metrics_creation():
    """Test creating CommerceMetrics instance."""
    metrics = CommerceMetrics(
        sales_rank=10,
        category_rank=2,
        rating=4.5,
        review_count=1000,
        price=99.99,
        currency="USD"
    )
    
    assert metrics.sales_rank == 10
    assert metrics.category_rank == 2
    assert metrics.rating == 4.5
    assert metrics.review_count == 1000
    assert metrics.price == 99.99


def test_calculate_derived_metrics():
    """Test calculation of derived metrics."""
    metrics = CommerceMetrics(
        price=79.99,
        original_price=99.99,
        rating=4.5,
        review_count=1000,
        rank_change_24h=-5
    )
    
    metrics.calculate_derived_metrics()
    
    # Check discount percentage
    assert metrics.discount_percentage is not None
    assert 19 < metrics.discount_percentage < 21  # ~20%
    
    # Check popularity score
    assert metrics.popularity_score is not None
    assert 0 <= metrics.popularity_score <= 10
    
    # Check trend strength
    assert metrics.trend_strength is not None
    assert 0 <= metrics.trend_strength <= 10
    
    # Check consumer interest
    assert metrics.consumer_interest is not None
    assert 0 <= metrics.consumer_interest <= 10


def test_from_amazon():
    """Test creating CommerceMetrics from Amazon product data."""
    product_data = {
        'asin': 'B001TEST',
        'price': 99.99,
        'original_price': 129.99,
        'rating': 4.7,
        'review_count': 5000,
        'sales_rank': 15,
        'category_rank': 3,
        'rank_change_24h': -5,
        'seller_rating': 4.8,
        'seller_feedback_count': 10000,
        'has_prime': True,
        'bestseller_badge': True,
        'amazon_choice': False
    }
    
    metrics = CommerceMetrics.from_amazon(product_data)
    
    assert metrics.price == 99.99
    assert metrics.original_price == 129.99
    assert metrics.rating == 4.7
    assert metrics.review_count == 5000
    assert metrics.sales_rank == 15
    assert metrics.category_rank == 3
    assert metrics.has_prime is True
    assert metrics.bestseller_badge is True


def test_to_dict():
    """Test converting metrics to dictionary."""
    metrics = CommerceMetrics(
        sales_rank=10,
        rating=4.5,
        review_count=1000,
        price=99.99
    )
    
    metrics_dict = metrics.to_dict()
    
    assert isinstance(metrics_dict, dict)
    assert metrics_dict['sales_rank'] == 10
    assert metrics_dict['rating'] == 4.5
    assert metrics_dict['review_count'] == 1000
    assert metrics_dict['price'] == 99.99


def test_popularity_score_calculation():
    """Test popularity score calculation with different inputs."""
    # High rating, high reviews
    metrics1 = CommerceMetrics(rating=5.0, review_count=10000)
    metrics1.calculate_derived_metrics()
    
    # Low rating, low reviews
    metrics2 = CommerceMetrics(rating=2.0, review_count=10)
    metrics2.calculate_derived_metrics()
    
    assert metrics1.popularity_score > metrics2.popularity_score


def test_trend_strength_positive_change():
    """Test trend strength with rank improvement."""
    metrics = CommerceMetrics(rank_change_24h=-10)  # Improved by 10 positions
    metrics.calculate_derived_metrics()
    
    # Trend strength is min(10, abs(-10) / 10) = 1.0
    assert metrics.trend_strength >= 1.0


def test_trend_strength_negative_change():
    """Test trend strength with rank decline."""
    metrics = CommerceMetrics(rank_change_24h=10)  # Declined by 10 positions
    metrics.calculate_derived_metrics()
    
    assert metrics.trend_strength < 5


def test_consumer_interest_combines_metrics():
    """Test that consumer interest combines popularity and trend."""
    metrics = CommerceMetrics(
        rating=4.5,
        review_count=1000,
        rank_change_24h=-5
    )
    metrics.calculate_derived_metrics()
    
    assert metrics.consumer_interest is not None
    # Consumer interest should be weighted combination
    expected = metrics.popularity_score * 0.6 + metrics.trend_strength * 0.4
    assert abs(metrics.consumer_interest - expected) < 0.01
