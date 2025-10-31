"""Tests for creative metrics module."""

import pytest
from src.core.metrics import CreativeMetrics


def test_creative_metrics_initialization():
    """Test CreativeMetrics initialization with defaults."""
    metrics = CreativeMetrics()
    
    assert metrics.emotional_impact == 0.0
    assert metrics.versatility == 0.0
    assert metrics.inspiration_value == 0.0
    assert metrics.content_type == 'lyrics'
    assert metrics.content_format == 'text'
    assert metrics.platform == 'manual'


def test_creative_metrics_from_genius():
    """Test creating CreativeMetrics from Genius data."""
    genius_data = {
        'id': 12345,
        'title': 'Test Song',
        'url': 'https://genius.com/test',
        'primary_artist': {
            'name': 'Test Artist'
        },
        'stats': {
            'pageviews': 100000,
            'hot': 500
        }
    }
    
    metrics = CreativeMetrics.from_genius(genius_data)
    
    assert metrics.content_type == 'lyrics'
    assert metrics.platform == 'genius'
    assert metrics.creator == 'Test Artist'
    assert metrics.work_title == 'Test Song'
    assert metrics.source_url == 'https://genius.com/test'
    assert metrics.emotional_impact > 0  # Calculated from hot score
    assert metrics.versatility == 5.0  # Default
    assert metrics.inspiration_value > 0  # Calculated


def test_creative_metrics_from_manual():
    """Test creating CreativeMetrics from manual data."""
    manual_data = {
        'type': 'lyrics',
        'format': 'text',
        'creator': 'Manual Artist',
        'work_title': 'Manual Song',
        'themes': ['love', 'loss'],
        'mood': 'melancholic',
        'style': 'modern',
        'license': 'CC-BY',
        'emotional_impact': 8.5,
        'versatility': 6.0,
        'inspiration_value': 7.5
    }
    
    metrics = CreativeMetrics.from_manual(manual_data)
    
    assert metrics.content_type == 'lyrics'
    assert metrics.platform == 'manual'
    assert metrics.creator == 'Manual Artist'
    assert metrics.work_title == 'Manual Song'
    assert metrics.themes == ['love', 'loss']
    assert metrics.mood == 'melancholic'
    assert metrics.emotional_impact == 8.5
    assert metrics.versatility == 6.0
    assert metrics.inspiration_value == 7.5


def test_creative_metrics_to_dict():
    """Test converting metrics to dictionary."""
    metrics = CreativeMetrics(
        emotional_impact=8.0,
        versatility=7.0,
        inspiration_value=7.5,
        creator='Test Artist',
        themes=['test']
    )
    
    result = metrics.to_dict()
    
    assert isinstance(result, dict)
    assert result['emotional_impact'] == 8.0
    assert result['versatility'] == 7.0
    assert result['creator'] == 'Test Artist'
    assert result['themes'] == ['test']


def test_calculate_derived_metrics():
    """Test calculation of derived metrics."""
    metrics = CreativeMetrics(
        emotional_impact=8.0,
        versatility=6.0,
        inspiration_value=0.0  # Will be calculated
    )
    
    metrics.calculate_derived_metrics()
    
    # Should be average of emotional_impact and versatility
    expected = (8.0 + 6.0) / 2
    assert metrics.inspiration_value == expected
