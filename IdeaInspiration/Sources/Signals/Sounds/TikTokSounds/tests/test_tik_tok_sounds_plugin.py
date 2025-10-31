"""Tests for TikTok Sounds plugin."""

import pytest
from unittest.mock import Mock
from src.plugins.tik_tok_sounds_plugin import TikTokSoundsPlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock(spec=Config)
    config.max_results = 10
    config.retry_delay_seconds = 1
    return config


@pytest.fixture
def plugin(mock_config):
    """Create a TikTokSoundsPlugin instance."""
    plugin = TikTokSoundsPlugin(mock_config)
    plugin.api = None  # Force stub mode
    return plugin


def test_get_source_name(plugin):
    """Test that source name is returned correctly."""
    assert plugin.get_source_name() == "tiktok_sounds"


def test_scrape_returns_list(plugin):
    """Test that scrape returns a list."""
    signals = plugin.scrape()
    assert isinstance(signals, list)


def test_scrape_stub_mode(plugin):
    """Test scraping in stub mode."""
    signals = plugin.scrape(limit=5)
    assert len(signals) == 5
    assert all(isinstance(s, dict) for s in signals)


def test_signal_structure(plugin):
    """Test that signals have the correct structure."""
    signals = plugin.scrape(limit=1)
    assert len(signals) == 1
    signal = signals[0]
    
    assert 'source_id' in signal
    assert 'signal_type' in signal
    assert 'name' in signal
    assert 'description' in signal
    assert 'tags' in signal
    assert 'metrics' in signal
    assert 'temporal' in signal
    assert 'extra' in signal
    
    assert signal['signal_type'] == 'sound'
    assert 'tiktok' in signal['tags']
    assert 'sound' in signal['tags']
    assert 'volume' in signal['metrics']
    assert 'velocity' in signal['metrics']
    assert 'acceleration' in signal['metrics']
    assert 'artist' in signal['extra']
    assert 'duration_seconds' in signal['extra']


def test_max_results_limit(plugin):
    """Test that max_results limit is respected."""
    signals = plugin.scrape(limit=3)
    assert len(signals) == 3
    
    signals = plugin.scrape(limit=7)
    assert len(signals) == 7


def test_error_handling(plugin):
    """Test error handling in scrape method."""
    signals = plugin.scrape(limit=0)
    assert isinstance(signals, list)
    assert len(signals) == 0


def test_velocity_calculation(plugin):
    """Test velocity calculation logic."""
    velocity1 = plugin._calculate_velocity(5000000)  # High usage
    velocity2 = plugin._calculate_velocity(50000)    # Low usage
    
    assert velocity1 > velocity2
    assert 0 <= velocity1 <= 100
    assert 0 <= velocity2 <= 100


def test_status_determination(plugin):
    """Test status determination based on velocity."""
    assert plugin._determine_status(80.0) == 'rising'
    assert plugin._determine_status(50.0) == 'peak'
    assert plugin._determine_status(30.0) == 'stable'
    assert plugin._determine_status(10.0) == 'declining'
