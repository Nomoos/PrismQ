"""Tests for NewsAPI plugin."""

import pytest
from unittest.mock import Mock
from src.plugins.news_api_plugin import NewsApiPlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    config.max_results = 10
    config.retry_delay_seconds = 1
    config.api_key = None
    return config


@pytest.fixture
def plugin(mock_config):
    plugin = NewsApiPlugin(mock_config)
    plugin.api = None  # Force stub mode
    return plugin


def test_get_source_name(plugin):
    assert plugin.get_source_name() == "news_api"


def test_scrape_returns_list(plugin):
    signals = plugin.scrape()
    assert isinstance(signals, list)


def test_scrape_stub_mode(plugin):
    signals = plugin.scrape(limit=3)
    assert len(signals) == 3
    assert all(isinstance(s, dict) for s in signals)


def test_signal_structure(plugin):
    signals = plugin.scrape(limit=1)
    assert len(signals) == 1
    signal = signals[0]
    
    assert signal['signal_type'] == 'news'
    assert 'newsapi' in signal['tags']
    assert 'source' in signal['extra']
    assert 'url' in signal['extra']
    assert 'author' in signal['extra']


def test_max_results_limit(plugin):
    signals = plugin.scrape(limit=2)
    assert len(signals) == 2


def test_scrape_with_query(plugin):
    signals = plugin.scrape(query="technology", limit=3)
    assert isinstance(signals, list)


def test_scrape_with_category(plugin):
    signals = plugin.scrape(category="business", limit=3)
    assert isinstance(signals, list)
