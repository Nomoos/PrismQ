"""
Simple test script for worker configuration loading (Issue #328).

Tests basic functionality without requiring pytest.
"""

import json
import os
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from queue.worker_config import (
    WorkerConfigurationManager,
    load_worker_config,
    JSONConfigLoader,
)
from queue.models import WorkerConfig, SchedulingStrategy


def test_json_config_loader():
    """Test JSON configuration loading."""
    print("\nTest 1: JSON Configuration Loader")
    
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
        print("  ✓ JSON file loaded successfully")


def test_load_from_dict():
    """Test loading configuration from dictionary."""
    print("\nTest 2: Load from Dictionary")
    
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
    assert config.lease_duration_seconds == 60  # Default
    print("  ✓ Configuration loaded from dict with defaults")


def test_load_from_env():
    """Test loading configuration from environment variables."""
    print("\nTest 3: Load from Environment Variables")
    
    # Set environment variables
    os.environ["PRISMQ_WORKER_ID"] = "env-worker"
    os.environ["PRISMQ_WORKER_SCHEDULING_STRATEGY"] = "weighted_random"
    os.environ["PRISMQ_WORKER_LEASE_DURATION_SECONDS"] = "90"
    os.environ["PRISMQ_WORKER_CAPABILITIES"] = '{"test": true}'
    
    try:
        manager = WorkerConfigurationManager()
        config = manager.load_from_env()
        
        assert config.worker_id == "env-worker"
        assert config.scheduling_strategy == SchedulingStrategy.WEIGHTED_RANDOM
        assert config.lease_duration_seconds == 90
        assert config.capabilities == {"test": True}
        print("  ✓ Configuration loaded from environment")
    finally:
        # Clean up
        for key in [
            "PRISMQ_WORKER_ID",
            "PRISMQ_WORKER_SCHEDULING_STRATEGY",
            "PRISMQ_WORKER_LEASE_DURATION_SECONDS",
            "PRISMQ_WORKER_CAPABILITIES",
        ]:
            os.environ.pop(key, None)


def test_env_overrides():
    """Test environment variable overrides."""
    print("\nTest 4: Environment Variable Overrides")
    
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
            print("  ✓ File config loaded without override")
            
            # Load with overrides
            config_with_override = manager.load_from_file(
                str(config_path),
                apply_env_overrides=True
            )
            assert config_with_override.worker_id == "override-worker"
            print("  ✓ Environment variable overrode file config")
        finally:
            os.environ.pop("PRISMQ_WORKER_ID", None)
            os.environ.pop("PRISMQ_WORKER_SCHEDULING_STRATEGY", None)


def test_save_to_file():
    """Test saving configuration to file."""
    print("\nTest 5: Save Configuration to File")
    
    config = WorkerConfig(
        worker_id="save-worker",
        capabilities={"test": True},
        scheduling_strategy=SchedulingStrategy.LIFO,
        lease_duration_seconds=120,
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
        assert saved_data["scheduling_strategy"] == "lifo"
        print("  ✓ Configuration saved and reloaded successfully")


def test_all_strategies():
    """Test all scheduling strategies."""
    print("\nTest 6: All Scheduling Strategies")
    
    strategies = {
        "fifo": SchedulingStrategy.FIFO,
        "lifo": SchedulingStrategy.LIFO,
        "priority": SchedulingStrategy.PRIORITY,
        "weighted_random": SchedulingStrategy.WEIGHTED_RANDOM,
    }
    
    manager = WorkerConfigurationManager()
    
    for strategy_value, strategy_enum in strategies.items():
        config_dict = {
            "worker_id": f"worker-{strategy_value}",
            "scheduling_strategy": strategy_value,
        }
        
        config = manager.load_from_dict(config_dict)
        
        assert config.worker_id == f"worker-{strategy_value}"
        assert config.scheduling_strategy == strategy_enum
    
    print("  ✓ All 4 scheduling strategies tested successfully")


def test_error_handling():
    """Test error handling."""
    print("\nTest 7: Error Handling")
    
    manager = WorkerConfigurationManager()
    
    # Test missing worker_id
    try:
        manager.load_from_dict({"scheduling_strategy": "fifo"})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "worker_id is required" in str(e)
        print("  ✓ Missing worker_id raises ValueError")
    
    # Test invalid strategy
    try:
        manager.load_from_dict({
            "worker_id": "test",
            "scheduling_strategy": "invalid"
        })
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid scheduling strategy" in str(e)
        print("  ✓ Invalid strategy raises ValueError")
    
    # Test nonexistent file
    loader = JSONConfigLoader()
    try:
        loader.load("/nonexistent/config.json")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("  ✓ Nonexistent file raises FileNotFoundError")


def test_convenience_function():
    """Test load_worker_config convenience function."""
    print("\nTest 8: Convenience Function")
    
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
        print("  ✓ load_worker_config() works correctly")


def main():
    """Run all tests."""
    print("="*70)
    print("Worker Configuration Tests - Issue #328")
    print("="*70)
    
    tests = [
        test_json_config_loader,
        test_load_from_dict,
        test_load_from_env,
        test_env_overrides,
        test_save_to_file,
        test_all_strategies,
        test_error_handling,
        test_convenience_function,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n  ✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
