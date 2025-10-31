"""Tests for Google News plugin."""

import pytest
from unittest.mock import Mock
from src.plugins.google_news_plugin import GoogleNewsPlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock(spec=Config)
    config.max_results = 10
    config.retry_delay_seconds = 1
    config.language = 'en'
    config.google_news_region = 'US'
    return config


@pytest.fixture
def plugin(mock_config):
    """Create a GoogleNewsPlugin instance."""
    plugin = GoogleNewsPlugin(mock_config)
    # Force stub mode for consistent testing
    plugin.api = None
    return plugin


def test_get_source_name(plugin):
    """Test that source name is returned correctly."""
    assert plugin.get_source_name() == "google_news"


def test_scrape_returns_list(plugin):
    """Test that scrape returns a list."""
    signals = plugin.scrape()
    assert isinstance(signals, list)


def test_scrape_stub_mode(plugin):
    """Test scraping in stub mode (without gnews)."""
    signals = plugin.scrape(limit=5)
    
    assert len(signals) == 5
    assert all(isinstance(s, dict) for s in signals)


def test_signal_structure(plugin):
    """Test that signals have the correct structure."""
    signals = plugin.scrape(limit=1)
    
    assert len(signals) == 1
    signal = signals[0]
    
    # Required fields
    assert 'source_id' in signal
    assert 'signal_type' in signal
    assert 'name' in signal
    assert 'description' in signal
    assert 'tags' in signal
    assert 'metrics' in signal
    assert 'temporal' in signal
    assert 'extra' in signal
    
    # Signal type should be 'news'
    assert signal['signal_type'] == 'news'
    
    # Tags should include google_news
    assert 'google_news' in signal['tags']
    assert 'news' in signal['tags']
    
    # Metrics should have required fields
    assert 'volume' in signal['metrics']
    assert 'velocity' in signal['metrics']
    assert 'acceleration' in signal['metrics']
    
    # Extra fields
    assert 'publisher' in signal['extra']
    assert 'url' in signal['extra']
    
    # Temporal fields
    assert 'first_seen' in signal['temporal']
    assert 'current_status' in signal['temporal']


def test_max_results_limit(plugin):
    """Test that max_results limit is respected."""
    signals = plugin.scrape(limit=3)
    assert len(signals) == 3
    
    signals = plugin.scrape(limit=7)
    assert len(signals) == 7


def test_error_handling(plugin):
    """Test error handling in scrape method."""
    # Should not raise even with invalid parameters
    signals = plugin.scrape(limit=0)
    assert isinstance(signals, list)
    assert len(signals) == 0


def test_sample_news_content(plugin):
    """Test that sample news have expected content."""
    signals = plugin._get_sample_news(8)
    
    assert len(signals) <= 8
    assert all('name' in s for s in signals)
    assert all('description' in s for s in signals)
    assert all('extra' in s for s in signals)
    assert all('publisher' in s['extra'] for s in signals)


def test_signal_strength_calculation(plugin):
    """Test signal strength calculation."""
    # Longer content should give higher strength
    strength1 = plugin._calculate_signal_strength(
        "Short title",
        "Short description"
    )
    strength2 = plugin._calculate_signal_strength(
        "This is a much longer title with more words",
        "This is a much longer description with significantly more content and details"
    )
    
    assert strength2 > strength1
    assert 0 <= strength1 <= 10
    assert 0 <= strength2 <= 10


def test_scrape_with_keywords(plugin):
    """Test scraping with keyword parameter."""
    signals = plugin.scrape(keywords="technology", limit=3)
    
    assert isinstance(signals, list)
    assert len(signals) <= 3


def test_scrape_with_topic(plugin):
    """Test scraping with topic parameter."""
    signals = plugin.scrape(topic="sports", limit=3)
    
    assert isinstance(signals, list)
    assert len(signals) <= 3


def test_create_signal_with_publisher_dict(plugin):
    """Test signal creation when publisher is a dictionary."""
    news_item = {
        'title': 'Test Article',
        'description': 'Test description',
        'publisher': {'title': 'Test Publisher'},
        'url': 'https://example.com'
    }
    
    signal = plugin._create_signal(news_item)
    assert signal['extra']['publisher'] == 'Test Publisher'


def test_create_signal_with_publisher_string(plugin):
    """Test signal creation when publisher is a string."""
    news_item = {
        'title': 'Test Article',
        'description': 'Test description',
        'publisher': 'Test Publisher',
        'url': 'https://example.com'
    }
    
    signal = plugin._create_signal(news_item)
    assert signal['extra']['publisher'] == 'Test Publisher'
