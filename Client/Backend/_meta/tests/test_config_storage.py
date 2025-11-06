"""Tests for ConfigStorage service."""

import pytest
import json
from pathlib import Path
from datetime import datetime

from src.core.config_storage import ConfigStorage


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    return tmp_path / "test_configs"


@pytest.fixture
def config_storage(temp_config_dir):
    """Create a ConfigStorage instance with temporary directory."""
    return ConfigStorage(temp_config_dir)


def test_config_storage_initialization(config_storage, temp_config_dir):
    """Test ConfigStorage initialization creates directory."""
    assert config_storage.config_dir.exists()
    assert config_storage.config_dir.is_dir()
    assert config_storage.config_dir == temp_config_dir / "parameters"


def test_save_config(config_storage):
    """Test saving a configuration."""
    module_id = "test-module"
    parameters = {"param1": "value1", "param2": 42, "param3": True}
    
    success = config_storage.save_config(module_id, parameters)
    
    assert success is True
    assert (config_storage.config_dir / f"{module_id}.json").exists()


def test_get_config(config_storage):
    """Test retrieving a saved configuration."""
    module_id = "test-module"
    parameters = {"param1": "value1", "param2": 42}
    
    config_storage.save_config(module_id, parameters)
    loaded_params = config_storage.get_config(module_id)
    
    assert loaded_params == parameters


def test_get_nonexistent_config(config_storage):
    """Test retrieving a config that doesn't exist."""
    loaded_params = config_storage.get_config("nonexistent-module")
    
    assert loaded_params == {}


def test_delete_config(config_storage):
    """Test deleting a configuration."""
    module_id = "test-module"
    parameters = {"param1": "value1"}
    
    config_storage.save_config(module_id, parameters)
    assert config_storage.get_config(module_id) == parameters
    
    success = config_storage.delete_config(module_id)
    
    assert success is True
    assert config_storage.get_config(module_id) == {}


def test_delete_nonexistent_config(config_storage):
    """Test deleting a config that doesn't exist."""
    success = config_storage.delete_config("nonexistent-module")
    
    assert success is False


def test_list_configs(config_storage):
    """Test listing all saved configurations."""
    # Save multiple configs
    config_storage.save_config("module1", {"param": "value1"})
    config_storage.save_config("module2", {"param": "value2"})
    config_storage.save_config("module3", {"param": "value3"})
    
    configs = config_storage.list_configs()
    
    assert len(configs) == 3
    assert "module1" in configs
    assert "module2" in configs
    assert "module3" in configs


def test_list_configs_empty(config_storage):
    """Test listing configs when none exist."""
    configs = config_storage.list_configs()
    
    assert configs == []


def test_save_config_preserves_structure(config_storage):
    """Test that saved config has correct JSON structure."""
    module_id = "test-module"
    parameters = {"param1": "value1", "param2": 42}
    
    config_storage.save_config(module_id, parameters)
    
    # Read raw JSON file
    config_file = config_storage.config_dir / f"{module_id}.json"
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    assert data["module_id"] == module_id
    assert data["parameters"] == parameters
    assert "updated_at" in data
    # Verify updated_at is a valid ISO timestamp
    datetime.fromisoformat(data["updated_at"])


def test_save_config_updates_timestamp(config_storage):
    """Test that saving config updates the timestamp."""
    module_id = "test-module"
    
    config_storage.save_config(module_id, {"param": "value1"})
    config_file = config_storage.config_dir / f"{module_id}.json"
    with open(config_file, 'r') as f:
        data1 = json.load(f)
    
    # Small delay to ensure different timestamp
    import time
    time.sleep(0.01)
    
    config_storage.save_config(module_id, {"param": "value2"})
    with open(config_file, 'r') as f:
        data2 = json.load(f)
    
    assert data1["updated_at"] != data2["updated_at"]
    assert data1["parameters"] != data2["parameters"]


def test_get_config_handles_corrupted_file(config_storage):
    """Test that get_config handles corrupted JSON gracefully."""
    module_id = "test-module"
    config_file = config_storage.config_dir / f"{module_id}.json"
    
    # Create corrupted JSON file
    config_file.write_text("{ invalid json content")
    
    loaded_params = config_storage.get_config(module_id)
    
    assert loaded_params == {}


def test_save_config_with_unicode(config_storage):
    """Test saving config with unicode characters."""
    module_id = "test-module"
    parameters = {
        "text": "Hello 世界 🌍",
        "emoji": "🎉🎊",
        "special": "café résumé"
    }
    
    success = config_storage.save_config(module_id, parameters)
    loaded_params = config_storage.get_config(module_id)
    
    assert success is True
    assert loaded_params == parameters


def test_save_config_with_nested_structures(config_storage):
    """Test saving config with nested dictionaries and lists."""
    module_id = "test-module"
    parameters = {
        "nested_dict": {
            "key1": "value1",
            "key2": {"nested_key": "nested_value"}
        },
        "list": [1, 2, 3, "four"],
        "mixed": {
            "numbers": [1, 2, 3],
            "strings": ["a", "b", "c"]
        }
    }
    
    success = config_storage.save_config(module_id, parameters)
    loaded_params = config_storage.get_config(module_id)
    
    assert success is True
    assert loaded_params == parameters


def test_config_storage_concurrent_access(config_storage):
    """Test concurrent save/load operations."""
    import concurrent.futures
    
    def save_and_load(module_num):
        module_id = f"module-{module_num}"
        params = {"value": module_num}
        config_storage.save_config(module_id, params)
        return config_storage.get_config(module_id)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(save_and_load, i) for i in range(10)]
        results = [f.result() for f in futures]
    
    # Verify all saves were successful
    assert len(results) == 10
    configs = config_storage.list_configs()
    assert len(configs) == 10
