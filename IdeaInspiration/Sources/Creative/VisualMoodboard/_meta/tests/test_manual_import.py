"""Tests for manual import plugin."""

import pytest
import tempfile
import json
import csv
from pathlib import Path
from src.plugins.manual_import_plugin import ManualImportPlugin
from src.core.config import Config


@pytest.fixture
def plugin():
    """Create a ManualImportPlugin instance."""
    with tempfile.TemporaryDirectory() as temp_dir:
        env_file = Path(temp_dir) / ".env"
        env_file.touch()
        config = Config(str(env_file), interactive=False)
        yield ManualImportPlugin(config)


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file with test data."""
    data = [
        {
            "title": "Test Song 1 - Artist 1",
            "content": "Test lyrics 1",
            "creator": "Artist 1",
            "themes": ["love", "hope"],
            "emotional_impact": 8.5
        },
        {
            "title": "Test Song 2 - Artist 2",
            "content": "Test lyrics 2",
            "creator": "Artist 2",
            "themes": ["loss"],
            "emotional_impact": 7.0
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(data, f)
        json_path = f.name
    
    yield json_path
    
    if Path(json_path).exists():
        Path(json_path).unlink()


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file with test data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'content', 'creator', 'themes', 'emotional_impact'])
        writer.writeheader()
        writer.writerow({
            'title': 'CSV Song 1 - Artist',
            'content': 'CSV lyrics',
            'creator': 'CSV Artist',
            'themes': 'love,hope',
            'emotional_impact': '9.0'
        })
        csv_path = f.name
    
    yield csv_path
    
    if Path(csv_path).exists():
        Path(csv_path).unlink()


def test_plugin_source_name(plugin):
    """Test getting source name."""
    assert plugin.get_source_name() == 'manual'


def test_import_from_json(plugin, temp_json_file):
    """Test importing from JSON file."""
    resources = plugin.import_from_json(temp_json_file)
    
    assert len(resources) == 2
    assert resources[0]['title'] == 'Test Song 1 - Artist 1'
    assert resources[0]['content'] == 'Test lyrics 1'
    assert 'manual' in resources[0]['tags']
    assert 'love' in resources[0]['tags']
    assert resources[0]['metrics']['creator'] == 'Artist 1'


def test_import_from_csv(plugin, temp_csv_file):
    """Test importing from CSV file."""
    resources = plugin.import_from_csv(temp_csv_file)
    
    assert len(resources) == 1
    assert resources[0]['title'] == 'CSV Song 1 - Artist'
    assert resources[0]['content'] == 'CSV lyrics'
    assert 'manual' in resources[0]['tags']
    assert resources[0]['metrics']['emotional_impact'] == 9.0


def test_import_single(plugin):
    """Test importing a single visual resource."""
    resource = plugin.import_single(
        title='Single Song - Artist',
        content='Single visual resource',
        creator='Single Artist',
        themes=['test', 'manual'],
        emotional_impact=8.0,
        versatility=7.0
    )
    
    assert resource['title'] == 'Single Song - Artist'
    assert resource['content'] == 'Single visual resource'
    assert 'manual' in resource['tags']
    assert 'test' in resource['tags']
    assert resource['metrics']['emotional_impact'] == 8.0
    assert resource['metrics']['versatility'] == 7.0
    assert 'manual_' in resource['source_id']  # Should have hash-based ID
