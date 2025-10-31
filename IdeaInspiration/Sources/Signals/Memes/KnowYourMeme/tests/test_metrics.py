"""Tests for universal metrics."""

import pytest
from src.core.metrics import UniversalMetrics


def test_from_know_your_meme_basic():
    """Test creating universal metrics from Google Trends data."""
    metrics = {
        'volume': 50,
        'velocity': 25.0,
        'acceleration': 10.0,
        'geographic_spread': ['US', 'UK', 'CA']
    }
    
    um = UniversalMetrics.from_know_your_meme(metrics)
    
    assert um.trend_strength is not None
    assert um.virality_score is not None
    assert um.velocity == 25.0
    assert um.acceleration == 10.0
    assert um.geographic_spread == 3


def test_trend_strength_calculation():
    """Test trend strength calculation."""
    # High volume should give high trend strength
    high_volume_metrics = {
        'volume': 100,
        'velocity': 0.0,
        'acceleration': 0.0,
        'geographic_spread': []
    }
    
    um_high = UniversalMetrics.from_know_your_meme(high_volume_metrics)
    assert um_high.trend_strength == 10.0
    
    # Low volume should give low trend strength
    low_volume_metrics = {
        'volume': 10,
        'velocity': 0.0,
        'acceleration': 0.0,
        'geographic_spread': []
    }
    
    um_low = UniversalMetrics.from_know_your_meme(low_volume_metrics)
    assert um_low.trend_strength < um_high.trend_strength


def test_virality_score_calculation():
    """Test virality score calculation."""
    # High velocity should give high virality
    high_velocity_metrics = {
        'volume': 50,
        'velocity': 50.0,
        'acceleration': 25.0,
        'geographic_spread': []
    }
    
    um_viral = UniversalMetrics.from_know_your_meme(high_velocity_metrics)
    assert um_viral.virality_score > 0
    
    # Zero velocity should give zero virality
    zero_velocity_metrics = {
        'volume': 50,
        'velocity': 0.0,
        'acceleration': 0.0,
        'geographic_spread': []
    }
    
    um_flat = UniversalMetrics.from_know_your_meme(zero_velocity_metrics)
    assert um_flat.virality_score == 0.0


def test_to_dict():
    """Test converting to dictionary."""
    um = UniversalMetrics(
        trend_strength=8.5,
        virality_score=7.2,
        velocity=25.0,
        acceleration=10.0,
        geographic_spread=3
    )
    
    d = um.to_dict()
    
    assert isinstance(d, dict)
    assert d['trend_strength'] == 8.5
    assert d['virality_score'] == 7.2
    assert d['velocity'] == 25.0
    assert d['acceleration'] == 10.0
    assert d['geographic_spread'] == 3


def test_geographic_spread():
    """Test geographic spread calculation."""
    metrics = {
        'volume': 50,
        'velocity': 0.0,
        'acceleration': 0.0,
        'geographic_spread': ['US', 'UK', 'CA', 'AU', 'DE']
    }
    
    um = UniversalMetrics.from_know_your_meme(metrics)
    assert um.geographic_spread == 5


def test_max_values_capped():
    """Test that values are capped at maximum."""
    # Very high values should be capped at 10.0
    extreme_metrics = {
        'volume': 10000,
        'velocity': 1000.0,
        'acceleration': 1000.0,
        'geographic_spread': []
    }
    
    um = UniversalMetrics.from_know_your_meme(extreme_metrics)
    
    # Trend strength and virality should be capped at 10.0
    assert um.trend_strength <= 10.0
    assert um.virality_score <= 10.0
