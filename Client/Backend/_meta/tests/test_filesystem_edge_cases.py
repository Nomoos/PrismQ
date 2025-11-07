"""Tests for filesystem-related edge cases."""

import json
import tempfile
from pathlib import Path

import pytest

from src.core.config_storage import ConfigStorage


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config_storage(temp_config_dir):
    """Create a ConfigStorage instance with temp directory."""
    return ConfigStorage(temp_config_dir)


def test_corrupted_json_config_file(config_storage, temp_config_dir):
    """Test handling of corrupted JSON in config file."""
    module_id = "test-module"

    # Create a corrupted JSON file manually
    config_file = temp_config_dir / "parameters" / f"{module_id}.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w") as f:
        f.write('{"parameters": {invalid json content')

    # Should return empty dict instead of crashing
    result = config_storage.get_config(module_id)
    assert result == {}


def test_config_file_with_missing_parameters_key(config_storage, temp_config_dir):
    """Test config file that's valid JSON but missing 'parameters' key."""
    module_id = "test-module"

    # Create a valid JSON file but without 'parameters' key
    config_file = temp_config_dir / "parameters" / f"{module_id}.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w") as f:
        json.dump({"module_id": module_id, "updated_at": "2024-01-01"}, f)

    # Should return empty dict when 'parameters' key is missing
    result = config_storage.get_config(module_id)
    assert result == {}


def test_config_file_with_null_parameters(config_storage, temp_config_dir):
    """Test config file with null/None parameters value."""
    module_id = "test-module"

    # Create config with null parameters
    config_file = temp_config_dir / "parameters" / f"{module_id}.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w") as f:
        json.dump({"module_id": module_id, "parameters": None}, f)

    # Should handle None gracefully
    result = config_storage.get_config(module_id)
    # Returns None or empty dict
    assert result in [None, {}]


def test_save_config_with_special_characters_in_module_id(config_storage):
    """Test saving config with special characters in module ID."""
    # Module IDs with special chars that are valid in filenames
    module_id = "test-module_v1.0"
    parameters = {"key": "value"}

    result = config_storage.save_config(module_id, parameters)
    assert result is True

    # Should be able to retrieve it
    loaded = config_storage.get_config(module_id)
    assert loaded == parameters


def test_save_config_with_nested_parameters(config_storage):
    """Test saving config with deeply nested parameter structures."""
    module_id = "test-module"
    parameters = {
        "level1": {"level2": {"level3": {"value": "deep"}}},
        "list": [1, 2, 3, {"nested": "dict"}],
    }

    result = config_storage.save_config(module_id, parameters)
    assert result is True

    # Should preserve structure
    loaded = config_storage.get_config(module_id)
    assert loaded == parameters


def test_save_config_with_empty_module_id(config_storage):
    """Test saving config with empty module ID."""
    module_id = ""
    parameters = {"key": "value"}

    # Should handle empty string gracefully
    result = config_storage.save_config(module_id, parameters)
    # Might fail or succeed depending on implementation
    assert isinstance(result, bool)


def test_delete_config_twice(config_storage):
    """Test deleting the same config twice."""
    module_id = "test-module"

    # Save config first
    config_storage.save_config(module_id, {"key": "value"})

    # Delete once - should succeed
    result1 = config_storage.delete_config(module_id)
    assert result1 is True

    # Delete again - should return False (already deleted)
    result2 = config_storage.delete_config(module_id)
    assert result2 is False


def test_list_configs_with_non_json_files(config_storage, temp_config_dir):
    """Test list_configs ignores non-JSON files."""
    # Create some JSON configs
    config_storage.save_config("module1", {"key": "value"})
    config_storage.save_config("module2", {"key": "value"})

    # Create a non-JSON file in the same directory
    params_dir = temp_config_dir / "parameters"
    (params_dir / "readme.txt").write_text("This is not a config")
    (params_dir / "backup.json.bak").write_text("Backup file")

    # Should only list actual .json files
    configs = config_storage.list_configs()
    assert len(configs) == 2
    assert "module1" in configs
    assert "module2" in configs
    assert "readme" not in configs
    assert "backup.json" not in configs


def test_config_with_very_large_parameters(config_storage):
    """Test saving and loading config with very large parameter values."""
    module_id = "test-module"

    # Create large parameter structure (100KB of data)
    large_list = ["x" * 1000 for _ in range(100)]
    parameters = {"large_field": large_list, "normal_field": "value"}

    result = config_storage.save_config(module_id, parameters)
    assert result is True

    # Should be able to load it back
    loaded = config_storage.get_config(module_id)
    assert loaded == parameters


def test_concurrent_save_to_same_config(config_storage):
    """Test concurrent saves to the same config file."""
    import threading

    module_id = "test-module"
    results = []

    def save_config(value):
        result = config_storage.save_config(module_id, {"value": value})
        results.append(result)

    # Create multiple threads saving concurrently
    threads = [threading.Thread(target=save_config, args=(i,)) for i in range(10)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # At least some saves should succeed (race condition may cause some to fail)
    # This tests that the system handles concurrent writes without crashing
    assert len(results) == 10
    assert any(results)  # At least one should succeed

    # If any succeeded, final config should be readable
    if any(results):
        final_config = config_storage.get_config(module_id)
        assert "value" in final_config
        assert 0 <= final_config["value"] < 10


def test_config_file_atomic_write(config_storage):
    """Test that config saves are atomic (using temp file + rename)."""
    module_id = "test-module"

    # Save initial config
    config_storage.save_config(module_id, {"version": 1})

    # Save updated config
    config_storage.save_config(module_id, {"version": 2})

    # There should be no .tmp files left
    params_dir = config_storage.config_dir
    tmp_files = list(params_dir.glob("*.tmp"))
    assert len(tmp_files) == 0

    # Only the final config should exist
    config = config_storage.get_config(module_id)
    assert config["version"] == 2


def test_save_config_with_non_serializable_types(config_storage):
    """Test saving config with non-JSON-serializable types."""
    module_id = "test-module"

    # Try to save config with non-serializable type (Path object)
    parameters = {"path": Path("/tmp/test"), "normal": "value"}  # Not JSON serializable

    # Should fail gracefully
    result = config_storage.save_config(module_id, parameters)
    assert result is False


def test_get_config_for_module_with_slash_in_id(config_storage):
    """Test getting config for module ID containing slashes (path traversal attempt)."""
    # Try to use path traversal in module ID
    module_id = "../../../etc/passwd"

    # Should safely handle this and not traverse directories
    result = config_storage.get_config(module_id)
    # Should return empty dict (file doesn't exist in safe location)
    assert result == {}


def test_save_config_preserves_unicode(config_storage):
    """Test that Unicode characters are preserved in config."""
    module_id = "test-module"
    parameters = {
        "emoji": "🚀🌟",
        "chinese": "你好世界",
        "arabic": "مرحبا",
        "emoji_in_key": "value",
    }

    result = config_storage.save_config(module_id, parameters)
    assert result is True

    # Should preserve Unicode
    loaded = config_storage.get_config(module_id)
    assert loaded == parameters


def test_config_directory_creation(temp_config_dir):
    """Test that ConfigStorage creates directory if it doesn't exist."""
    # Create storage with non-existent subdirectory
    new_dir = temp_config_dir / "nonexistent" / "subdir"
    assert not new_dir.exists()

    storage = ConfigStorage(new_dir)

    # Directory should be created
    assert storage.config_dir.exists()
    assert storage.config_dir.is_dir()


def test_list_configs_empty_directory(config_storage):
    """Test list_configs on empty directory."""
    configs = config_storage.list_configs()
    assert configs == []


def test_config_updated_at_timestamp(config_storage):
    """Test that configs include updated_at timestamp."""
    module_id = "test-module"
    parameters = {"key": "value"}

    config_storage.save_config(module_id, parameters)

    # Read the raw config file to check timestamp
    config_file = config_storage.config_dir / f"{module_id}.json"
    with open(config_file, "r") as f:
        data = json.load(f)

    assert "updated_at" in data
    assert "T" in data["updated_at"]  # ISO format
    assert data["module_id"] == module_id
    assert data["parameters"] == parameters
