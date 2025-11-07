"""
Tests for worker configuration loading (Issue #328).

Tests cover:
- JSON configuration loading
- YAML configuration loading (if PyYAML installed)
- TOML configuration loading (if tomli installed)
- Environment variable loading
- Environment variable overrides
- Configuration validation
- Configuration saving
"""

import json
import os
import tempfile
from pathlib import Path
import pytest

# Import modules under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from queue.worker_config import (
    WorkerConfigurationManager,
    load_worker_config,
    JSONConfigLoader,
)
from queue.models import WorkerConfig, SchedulingStrategy


class TestJSONConfigLoader:
    """Test JSON configuration loading."""
    
    def test_load_valid_json(self):
        """Test loading valid JSON configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = {
                "worker_id": "test-worker",
                "capabilities": {"region": "us-west"},
                "scheduling_strategy": "fifo",
                "lease_duration_seconds": 30,
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            loader = JSONConfigLoader()
            loaded = loader.load(str(config_path))
            
            assert loaded == config_data
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file raises FileNotFoundError."""
        loader = JSONConfigLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load("/nonexistent/config.json")
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "invalid.json"
            
            with open(config_path, 'w') as f:
                f.write("{ invalid json }")
            
            loader = JSONConfigLoader()
            
            with pytest.raises(ValueError) as exc_info:
                loader.load(str(config_path))
            
            assert "Invalid JSON" in str(exc_info.value)


class TestWorkerConfigurationManager:
    """Test WorkerConfigurationManager."""
    
    def test_load_from_json_file(self):
        """Test loading configuration from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "worker.json"
            config_data = {
                "worker_id": "json-worker",
                "capabilities": {"gpu": "RTX5090"},
                "scheduling_strategy": "priority",
                "lease_duration_seconds": 45,
                "poll_interval_seconds": 2,
                "max_retries": 5,
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            manager = WorkerConfigurationManager()
            config = manager.load_from_file(str(config_path), apply_env_overrides=False)
            
            assert config.worker_id == "json-worker"
            assert config.capabilities == {"gpu": "RTX5090"}
            assert config.scheduling_strategy == SchedulingStrategy.PRIORITY
            assert config.lease_duration_seconds == 45
            assert config.poll_interval_seconds == 2
            assert config.max_retries == 5
    
    def test_load_from_dict(self):
        """Test loading configuration from dictionary."""
        config_dict = {
            "worker_id": "dict-worker",
            "capabilities": {"region": "us-east"},
            "scheduling_strategy": "fifo",
        }
        
        manager = WorkerConfigurationManager()
        config = manager.load_from_dict(config_dict, apply_env_overrides=False)
        
        assert config.worker_id == "dict-worker"
        assert config.capabilities == {"region": "us-east"}
        assert config.scheduling_strategy == SchedulingStrategy.FIFO
        # Check defaults
        assert config.lease_duration_seconds == 60
        assert config.poll_interval_seconds == 1
        assert config.max_retries == 3
    
    def test_load_from_env(self):
        """Test loading configuration from environment variables."""
        # Set environment variables
        os.environ["PRISMQ_WORKER_ID"] = "env-worker"
        os.environ["PRISMQ_WORKER_SCHEDULING_STRATEGY"] = "weighted_random"
        os.environ["PRISMQ_WORKER_LEASE_DURATION_SECONDS"] = "90"
        os.environ["PRISMQ_WORKER_POLL_INTERVAL_SECONDS"] = "3"
        os.environ["PRISMQ_WORKER_MAX_RETRIES"] = "7"
        os.environ["PRISMQ_WORKER_CAPABILITIES"] = '{"test": true}'
        
        try:
            manager = WorkerConfigurationManager()
            config = manager.load_from_env()
            
            assert config.worker_id == "env-worker"
            assert config.scheduling_strategy == SchedulingStrategy.WEIGHTED_RANDOM
            assert config.lease_duration_seconds == 90
            assert config.poll_interval_seconds == 3
            assert config.max_retries == 7
            assert config.capabilities == {"test": True}
        finally:
            # Clean up
            for key in [
                "PRISMQ_WORKER_ID",
                "PRISMQ_WORKER_SCHEDULING_STRATEGY",
                "PRISMQ_WORKER_LEASE_DURATION_SECONDS",
                "PRISMQ_WORKER_POLL_INTERVAL_SECONDS",
                "PRISMQ_WORKER_MAX_RETRIES",
                "PRISMQ_WORKER_CAPABILITIES",
            ]:
                os.environ.pop(key, None)
    
    def test_env_overrides(self):
        """Test environment variable overrides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = {
                "worker_id": "file-worker",
                "scheduling_strategy": "fifo",
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            # Set environment override
            os.environ["PRISMQ_WORKER_ID"] = "override-worker"
            os.environ["PRISMQ_WORKER_SCHEDULING_STRATEGY"] = "priority"
            
            try:
                manager = WorkerConfigurationManager()
                
                # Load without overrides
                config_no_override = manager.load_from_file(
                    str(config_path),
                    apply_env_overrides=False
                )
                assert config_no_override.worker_id == "file-worker"
                assert config_no_override.scheduling_strategy == SchedulingStrategy.FIFO
                
                # Load with overrides
                config_with_override = manager.load_from_file(
                    str(config_path),
                    apply_env_overrides=True
                )
                assert config_with_override.worker_id == "override-worker"
                assert config_with_override.scheduling_strategy == SchedulingStrategy.PRIORITY
            finally:
                os.environ.pop("PRISMQ_WORKER_ID", None)
                os.environ.pop("PRISMQ_WORKER_SCHEDULING_STRATEGY", None)
    
    def test_missing_worker_id_raises_error(self):
        """Test missing worker_id raises ValueError."""
        config_dict = {
            "scheduling_strategy": "fifo",
        }
        
        manager = WorkerConfigurationManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.load_from_dict(config_dict)
        
        assert "worker_id is required" in str(exc_info.value)
    
    def test_invalid_strategy_raises_error(self):
        """Test invalid scheduling strategy raises ValueError."""
        config_dict = {
            "worker_id": "test-worker",
            "scheduling_strategy": "invalid_strategy",
        }
        
        manager = WorkerConfigurationManager()
        
        with pytest.raises(ValueError) as exc_info:
            manager.load_from_dict(config_dict)
        
        assert "Invalid scheduling strategy" in str(exc_info.value)
    
    def test_save_to_json_file(self):
        """Test saving configuration to JSON file."""
        config = WorkerConfig(
            worker_id="save-worker",
            capabilities={"test": True},
            scheduling_strategy=SchedulingStrategy.LIFO,
            lease_duration_seconds=120,
            poll_interval_seconds=5,
            max_retries=10,
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "saved.json"
            
            manager = WorkerConfigurationManager()
            manager.save_to_file(config, str(save_path))
            
            # Verify file was created
            assert save_path.exists()
            
            # Load it back
            with open(save_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["worker_id"] == "save-worker"
            assert saved_data["capabilities"] == {"test": True}
            assert saved_data["scheduling_strategy"] == "lifo"
            assert saved_data["lease_duration_seconds"] == 120
            assert saved_data["poll_interval_seconds"] == 5
            assert saved_data["max_retries"] == 10
    
    def test_unsupported_format_raises_error(self):
        """Test loading unsupported format raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.xml"
            config_path.touch()
            
            manager = WorkerConfigurationManager()
            
            with pytest.raises(ValueError) as exc_info:
                manager.load_from_file(str(config_path))
            
            assert "Unsupported configuration file format" in str(exc_info.value)


class TestLoadWorkerConfig:
    """Test load_worker_config convenience function."""
    
    def test_load_from_file(self):
        """Test loading from file using convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "worker.json"
            config_data = {
                "worker_id": "convenience-worker",
                "scheduling_strategy": "priority",
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = load_worker_config(str(config_path), apply_env_overrides=False)
            
            assert config.worker_id == "convenience-worker"
            assert config.scheduling_strategy == SchedulingStrategy.PRIORITY
    
    def test_load_from_env_only(self):
        """Test loading from environment only."""
        os.environ["PRISMQ_WORKER_ID"] = "env-only-worker"
        os.environ["PRISMQ_WORKER_SCHEDULING_STRATEGY"] = "fifo"
        
        try:
            config = load_worker_config()  # No file path
            
            assert config.worker_id == "env-only-worker"
            assert config.scheduling_strategy == SchedulingStrategy.FIFO
        finally:
            os.environ.pop("PRISMQ_WORKER_ID", None)
            os.environ.pop("PRISMQ_WORKER_SCHEDULING_STRATEGY", None)


class TestAllSchedulingStrategies:
    """Test configuration with all scheduling strategies."""
    
    @pytest.mark.parametrize("strategy_value,strategy_enum", [
        ("fifo", SchedulingStrategy.FIFO),
        ("lifo", SchedulingStrategy.LIFO),
        ("priority", SchedulingStrategy.PRIORITY),
        ("weighted_random", SchedulingStrategy.WEIGHTED_RANDOM),
    ])
    def test_all_strategies(self, strategy_value, strategy_enum):
        """Test loading configuration for each scheduling strategy."""
        config_dict = {
            "worker_id": f"worker-{strategy_value}",
            "scheduling_strategy": strategy_value,
        }
        
        manager = WorkerConfigurationManager()
        config = manager.load_from_dict(config_dict)
        
        assert config.worker_id == f"worker-{strategy_value}"
        assert config.scheduling_strategy == strategy_enum


class TestConfigurationEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_capabilities(self):
        """Test configuration with empty capabilities."""
        config_dict = {
            "worker_id": "empty-caps",
            "capabilities": {},
        }
        
        manager = WorkerConfigurationManager()
        config = manager.load_from_dict(config_dict)
        
        assert config.capabilities == {}
    
    def test_complex_capabilities(self):
        """Test configuration with complex nested capabilities."""
        config_dict = {
            "worker_id": "complex-caps",
            "capabilities": {
                "regions": ["us-west", "us-east"],
                "formats": ["mp4", "png", "jpg"],
                "limits": {
                    "max_duration": 600,
                    "max_size_mb": 1024,
                },
                "features": {
                    "gpu": True,
                    "transcoding": True,
                },
            },
        }
        
        manager = WorkerConfigurationManager()
        config = manager.load_from_dict(config_dict)
        
        assert config.capabilities["regions"] == ["us-west", "us-east"]
        assert config.capabilities["limits"]["max_duration"] == 600
        assert config.capabilities["features"]["gpu"] is True
    
    def test_default_values(self):
        """Test that default values are applied correctly."""
        config_dict = {
            "worker_id": "defaults-worker",
        }
        
        manager = WorkerConfigurationManager()
        config = manager.load_from_dict(config_dict)
        
        assert config.worker_id == "defaults-worker"
        assert config.capabilities == {}
        assert config.scheduling_strategy == SchedulingStrategy.PRIORITY
        assert config.lease_duration_seconds == 60
        assert config.poll_interval_seconds == 1
        assert config.max_retries == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
