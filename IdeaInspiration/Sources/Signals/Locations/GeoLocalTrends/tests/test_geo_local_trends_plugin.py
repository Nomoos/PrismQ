"""Tests for GeoLocalTrends plugin."""

import pytest
from unittest.mock import Mock
from src.plugins.geo_local_trends_plugin import GeoLocalTrendsPlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock(spec=Config)
    config.geo_local_trends_max_results = 10
    config.retry_delay_seconds = 1
    return config


@pytest.fixture
def plugin(mock_config):
    """Create a GeoLocalTrendsPlugin instance."""
    return GeoLocalTrendsPlugin(mock_config)


def test_get_source_name(plugin):
    """Test that source name is returned correctly."""
    assert plugin.get_source_name() == "geo_local_trends"


def test_scrape_returns_list(plugin):
    """Test that scrape returns a list."""
    signals = plugin.scrape()
    assert isinstance(signals, list)


def test_scrape_default_limit(plugin):
    """Test scraping with default limit."""
    signals = plugin.scrape()
    assert len(signals) <= plugin.config.geo_local_trends_max_results


def test_scrape_custom_limit(plugin):
    """Test scraping with custom limit."""
    signals = plugin.scrape(limit=5)
    assert len(signals) == 5


def test_scrape_location_filter(plugin):
    """Test scraping with location filter."""
    signals = plugin.scrape(location='Tokyo', limit=10)
    assert len(signals) > 0
    # Should find Tokyo-related trends
    tokyo_found = any('Tokyo' in s['extra']['location'] for s in signals)
    assert tokyo_found


def test_signal_structure(plugin):
    """Test that signals have correct structure."""
    signals = plugin.scrape(limit=1)
    assert len(signals) == 1
    signal = signals[0]
    
    # Check required fields
    assert 'signal_type' in signal
    assert 'name' in signal
    assert 'source' in signal
    assert 'signal_id' in signal
    assert 'description' in signal
    assert 'tags' in signal
    assert 'metrics' in signal
    assert 'temporal' in signal
    assert 'extra' in signal
    
    # Check signal type
    assert signal['signal_type'] == 'location'
    
    # Check metrics structure
    assert 'signal_strength' in signal['metrics']
    assert 'volume' in signal['metrics']
    assert 'spread_score' in signal['metrics']
    assert 'virality' in signal['metrics']
    
    # Check temporal structure
    assert 'first_observed' in signal['temporal']
    assert 'current_status' in signal['temporal']
    
    # Check extra fields
    assert 'location' in signal['extra']
    assert 'country' in signal['extra']
    assert 'category' in signal['extra']


def test_sample_geo_trends_content(plugin):
    """Test that sample geo trends have valid content."""
    signals = plugin.scrape(limit=3)
    
    for signal in signals:
        assert len(signal['name']) > 0
        assert len(signal['extra']['location']) > 0
        assert len(signal['extra']['country']) > 0
        assert signal['metrics']['volume'] > 0
        assert 0 <= signal['metrics']['virality'] <= 1
        assert 0 <= signal['metrics']['signal_strength'] <= 10
        assert 'location' in signal['tags']

