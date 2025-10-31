"""Tests for Meme Tracker plugin."""

import pytest
from unittest.mock import Mock
from src.plugins.meme_tracker_plugin import MemeTrackerPlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    config.max_results = 10
    config.retry_delay_seconds = 1
    return config


@pytest.fixture
def plugin(mock_config):
    return MemeTrackerPlugin(mock_config)


def test_get_source_name(plugin):
    assert plugin.get_source_name() == "meme_tracker"


def test_scrape_returns_list(plugin):
    signals = plugin.scrape()
    assert isinstance(signals, list)


def test_scrape_stub_mode(plugin):
    signals = plugin.scrape(limit=5)
    assert len(signals) == 5


def test_signal_structure(plugin):
    signals = plugin.scrape(limit=1)
    signal = signals[0]
    assert signal['signal_type'] == 'meme'
    assert 'meme' in signal['tags']
    assert 'virality_score' in signal['extra']


def test_platform_filter(plugin):
    signals = plugin.scrape(platform='reddit', limit=5)
    assert isinstance(signals, list)


def test_velocity_calculation(plugin):
    velocity = plugin._calculate_velocity(8.5)
    assert 0 <= velocity <= 100


def test_status_determination(plugin):
    assert plugin._determine_status(90.0) == 'viral'
    assert plugin._determine_status(70.0) == 'trending'
