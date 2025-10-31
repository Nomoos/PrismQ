"""Tests for Google Trends plugin."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.plugins.google_trends_plugin import GoogleTrendsPlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock(spec=Config)
    config.google_trends_region = "US"
    config.google_trends_language = "en-US"
    config.google_trends_timeframe = "now 7-d"
    config.google_trends_max_results = 10
    config.retry_delay_seconds = 1
    return config


@pytest.fixture
def plugin(mock_config):
    """Create a GoogleTrendsPlugin instance with mocked pytrends."""
    with patch('src.plugins.google_trends_plugin.TrendReq') as mock_trend_req:
        mock_pytrends = MagicMock()
        mock_trend_req.return_value = mock_pytrends
        plugin = GoogleTrendsPlugin(mock_config)
        plugin.pytrends = mock_pytrends
        return plugin


def test_get_source_name(plugin):
    """Test that source name is returned correctly."""
    assert plugin.get_source_name() == "google_trends"


def test_scrape_returns_list(plugin):
    """Test that scrape returns a list."""
    # Mock trending searches
    import pandas as pd
    mock_df = pd.DataFrame({0: ['AI trends', 'Machine learning', 'Deep learning']})
    plugin.pytrends.trending_searches.return_value = mock_df
    
    signals = plugin.scrape()
    assert isinstance(signals, list)


def test_scrape_trending_searches(plugin):
    """Test scraping trending searches."""
    import pandas as pd
    mock_df = pd.DataFrame({0: ['AI trends', 'Machine learning']})
    plugin.pytrends.trending_searches.return_value = mock_df
    
    signals = plugin._get_trending_searches()
    
    assert len(signals) == 2
    assert signals[0]['name'] == 'AI trends'
    assert signals[0]['signal_type'] == 'trend'
    assert signals[0]['metrics']['volume'] == 100
    assert 'google' in signals[0]['tags']


def test_signal_structure(plugin):
    """Test that signals have correct structure."""
    import pandas as pd
    mock_df = pd.DataFrame({0: ['Test query']})
    plugin.pytrends.trending_searches.return_value = mock_df
    
    signals = plugin._get_trending_searches()
    
    assert len(signals) == 1
    signal = signals[0]
    
    # Check required fields
    assert 'source_id' in signal
    assert 'signal_type' in signal
    assert 'name' in signal
    assert 'description' in signal
    assert 'tags' in signal
    assert 'metrics' in signal
    assert 'temporal' in signal
    
    # Check metrics structure
    assert 'volume' in signal['metrics']
    assert 'velocity' in signal['metrics']
    assert 'acceleration' in signal['metrics']
    assert 'geographic_spread' in signal['metrics']
    
    # Check temporal structure
    assert 'first_seen' in signal['temporal']
    assert 'current_status' in signal['temporal']


def test_max_results_limit(plugin):
    """Test that max results limit is respected."""
    import pandas as pd
    # Create more results than the limit
    mock_df = pd.DataFrame({0: [f'Query {i}' for i in range(20)]})
    plugin.pytrends.trending_searches.return_value = mock_df
    
    signals = plugin._get_trending_searches()
    
    # Should only return up to max_results (10)
    assert len(signals) <= plugin.config.google_trends_max_results


def test_error_handling(plugin):
    """Test error handling during scraping."""
    # Simulate an error
    plugin.pytrends.trending_searches.side_effect = Exception("API Error")
    
    # Should not raise, but return empty list
    signals = plugin.scrape()
    assert isinstance(signals, list)
    assert len(signals) == 0
