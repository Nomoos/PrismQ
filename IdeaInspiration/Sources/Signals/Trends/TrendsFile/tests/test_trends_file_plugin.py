"""Tests for TrendsFile plugin."""

import pytest
import tempfile
import os
import json
import csv
from unittest.mock import Mock
from src.plugins.trends_file_plugin import TrendsFilePlugin
from src.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock(spec=Config)
    config.trends_file_max_results = 10
    config.retry_delay_seconds = 1
    return config


@pytest.fixture
def plugin(mock_config):
    """Create a TrendsFilePlugin instance."""
    return TrendsFilePlugin(mock_config)


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'description', 'volume', 'tags', 'first_seen'])
        writer.writeheader()
        writer.writerow({
            'name': 'Test Trend 1',
            'description': 'Test description 1',
            'volume': '1000000',
            'tags': 'ai,tech',
            'first_seen': '2024-10-20T00:00:00Z'
        })
        writer.writerow({
            'name': 'Test Trend 2',
            'description': 'Test description 2',
            'volume': '2000000',
            'tags': 'health,wellness',
            'first_seen': '2024-10-21T00:00:00Z'
        })
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        data = [
            {
                'name': 'JSON Trend 1',
                'description': 'JSON test description 1',
                'volume': 3000000,
                'tags': ['crypto', 'finance'],
                'first_seen': '2024-10-22T00:00:00Z'
            },
            {
                'name': 'JSON Trend 2',
                'description': 'JSON test description 2',
                'volume': 4000000,
                'tags': ['food', 'cooking'],
                'first_seen': '2024-10-23T00:00:00Z'
            }
        ]
        json.dump(data, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_get_source_name(plugin):
    """Test that source name is returned correctly."""
    assert plugin.get_source_name() == "trends_file"


def test_scrape_returns_list(plugin):
    """Test that scrape returns a list."""
    signals = plugin.scrape()
    assert isinstance(signals, list)


def test_scrape_stub_mode(plugin):
    """Test scraping in stub mode (no file)."""
    signals = plugin.scrape(limit=5)
    assert len(signals) == 5


def test_scrape_csv_file(plugin, temp_csv_file):
    """Test importing from CSV file."""
    signals = plugin.scrape(file_path=temp_csv_file, format='csv')
    assert len(signals) == 2
    assert signals[0]['name'] == 'Test Trend 1'
    assert signals[0]['metrics']['volume'] == 1000000
    assert 'ai' in signals[0]['tags']


def test_scrape_json_file(plugin, temp_json_file):
    """Test importing from JSON file."""
    signals = plugin.scrape(file_path=temp_json_file, format='json')
    assert len(signals) == 2
    assert signals[0]['name'] == 'JSON Trend 1'
    assert signals[0]['metrics']['volume'] == 3000000
    assert 'crypto' in signals[0]['tags']


def test_scrape_csv_with_limit(plugin, temp_csv_file):
    """Test importing from CSV with limit."""
    signals = plugin.scrape(file_path=temp_csv_file, format='csv', limit=1)
    assert len(signals) == 1


def test_scrape_json_with_limit(plugin, temp_json_file):
    """Test importing from JSON with limit."""
    signals = plugin.scrape(file_path=temp_json_file, format='json', limit=1)
    assert len(signals) == 1


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
    assert signal['signal_type'] == 'trend'
    
    # Check metrics structure
    assert 'signal_strength' in signal['metrics']
    assert 'volume' in signal['metrics']
    assert 'virality' in signal['metrics']
    
    # Check temporal structure
    assert 'first_observed' in signal['temporal']
    assert 'current_status' in signal['temporal']
    
    # Check extra fields
    assert 'source_type' in signal['extra']


def test_sample_trends_content(plugin):
    """Test that sample trends have valid content."""
    signals = plugin.scrape(limit=3)
    
    for signal in signals:
        assert len(signal['name']) > 0
        assert signal['metrics']['volume'] > 0
        assert 0 <= signal['metrics']['virality'] <= 1
        assert 0 <= signal['metrics']['signal_strength'] <= 10
        assert 'trend' in signal['tags']
        assert 'imported' in signal['tags']


def test_invalid_format(plugin):
    """Test that invalid format raises ValueError."""
    with pytest.raises(ValueError):
        plugin.scrape(file_path='dummy.txt', format='txt')

