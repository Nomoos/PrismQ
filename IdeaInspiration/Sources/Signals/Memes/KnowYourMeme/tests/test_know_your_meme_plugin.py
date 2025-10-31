"""Tests for Know Your Meme plugin."""

import pytest
from unittest.mock import Mock
from src.plugins.know_your_meme_plugin import KnowYourMemePlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    config.max_results = 10
    config.retry_delay_seconds = 1
    return config


@pytest.fixture
def plugin(mock_config):
    return KnowYourMemePlugin(mock_config)


def test_get_source_name(plugin):
    assert plugin.get_source_name() == "know_your_meme"


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
    assert 'kym' in signal['tags']
    assert 'status' in signal['extra']
    assert 'origin' in signal['extra']


def test_category_filter(plugin):
    signals = plugin.scrape(category='confirmed', limit=5)
    assert isinstance(signals, list)


def test_velocity_calculation(plugin):
    velocity = plugin._calculate_velocity(8.0, 'confirmed')
    assert 0 <= velocity <= 100


def test_status_in_extra(plugin):
    signals = plugin.scrape(limit=1)
    assert 'status' in signals[0]['extra']
