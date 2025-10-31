"""Tests for Instagram Audio Trends plugin."""

import pytest
from unittest.mock import Mock
from src.plugins.instagram_audio_trends_plugin import InstagramAudioTrendsPlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    config.max_results = 10
    config.retry_delay_seconds = 1
    return config


@pytest.fixture
def plugin(mock_config):
    plugin = InstagramAudioTrendsPlugin(mock_config)
    plugin.api = None
    return plugin


def test_get_source_name(plugin):
    assert plugin.get_source_name() == "instagram_audio_trends"


def test_scrape_returns_list(plugin):
    signals = plugin.scrape()
    assert isinstance(signals, list)


def test_scrape_stub_mode(plugin):
    signals = plugin.scrape(limit=5)
    assert len(signals) == 5
    assert all(isinstance(s, dict) for s in signals)


def test_signal_structure(plugin):
    signals = plugin.scrape(limit=1)
    assert len(signals) == 1
    signal = signals[0]
    
    assert signal['signal_type'] == 'audio'
    assert 'instagram' in signal['tags']
    assert 'audio' in signal['tags']
    assert 'artist' in signal['extra']
    assert 'duration_seconds' in signal['extra']


def test_max_results_limit(plugin):
    signals = plugin.scrape(limit=3)
    assert len(signals) == 3


def test_velocity_calculation(plugin):
    velocity = plugin._calculate_velocity(3000000)
    assert 0 <= velocity <= 100


def test_status_determination(plugin):
    assert plugin._determine_status(80.0) == 'rising'
    assert plugin._determine_status(50.0) == 'peak'
