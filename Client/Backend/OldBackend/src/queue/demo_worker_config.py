#!/usr/bin/env python
"""
Demo script for worker configuration loading (Issue #328).

This script demonstrates:
- Loading worker configuration from JSON, YAML, TOML files
- Loading configuration from environment variables
- Environment variable overrides
- Creating workers with configuration
- Saving configuration to files

Usage:
    cd Client/Backend
    python src/queue/demo_worker_config.py
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from queue.worker_config import (
    WorkerConfigurationManager,
    load_worker_config,
)
from queue.models import SchedulingStrategy, WorkerConfig
from queue.scheduling import TaskClaimerFactory
from queue.database import QueueDatabase


def demo_json_config():
    """Demonstrate loading configuration from JSON file."""
    print("\n" + "="*70)
    print("Demo 1: Load Configuration from JSON")
    print("="*70)
    
    json_path = Path(__file__).parent / "examples" / "worker_config.json"
    
    config = load_worker_config(str(json_path), apply_env_overrides=False)
    
    print(f"\n✓ Loaded configuration from: {json_path.name}")
    print(f"  Worker ID: {config.worker_id}")
    print(f"  Strategy: {config.scheduling_strategy.value}")
    print(f"  Lease Duration: {config.lease_duration_seconds}s")
    print(f"  Poll Interval: {config.poll_interval_seconds}s")
    print(f"  Max Retries: {config.max_retries}")
    print(f"  Capabilities: {config.capabilities}")


def demo_yaml_config():
    """Demonstrate loading configuration from YAML file."""
    print("\n" + "="*70)
    print("Demo 2: Load Configuration from YAML")
    print("="*70)
    
    yaml_path = Path(__file__).parent / "examples" / "worker_priority.yaml"
    
    try:
        config = load_worker_config(str(yaml_path), apply_env_overrides=False)
        
        print(f"\n✓ Loaded configuration from: {yaml_path.name}")
        print(f"  Worker ID: {config.worker_id}")
        print(f"  Strategy: {config.scheduling_strategy.value}")
        print(f"  Lease Duration: {config.lease_duration_seconds}s")
        print(f"  Capabilities: {config.capabilities}")
    except ImportError as e:
        print(f"\n⚠ YAML support requires PyYAML: {e}")
        print("  Install with: pip install pyyaml")


def demo_toml_config():
    """Demonstrate loading configuration from TOML file."""
    print("\n" + "="*70)
    print("Demo 3: Load Configuration from TOML")
    print("="*70)
    
    toml_path = Path(__file__).parent / "examples" / "worker_fifo.toml"
    
    try:
        config = load_worker_config(str(toml_path), apply_env_overrides=False)
        
        print(f"\n✓ Loaded configuration from: {toml_path.name}")
        print(f"  Worker ID: {config.worker_id}")
        print(f"  Strategy: {config.scheduling_strategy.value}")
        print(f"  Capabilities: {config.capabilities}")
    except ImportError as e:
        print(f"\n⚠ TOML support requires tomli: {e}")
        print("  Install with: pip install tomli")


def demo_env_variables():
    """Demonstrate loading configuration from environment variables."""
    print("\n" + "="*70)
    print("Demo 4: Load Configuration from Environment Variables")
    print("="*70)
    
    # Set environment variables
    os.environ["PRISMQ_WORKER_ID"] = "worker-env-demo"
    os.environ["PRISMQ_WORKER_SCHEDULING_STRATEGY"] = "fifo"
    os.environ["PRISMQ_WORKER_LEASE_DURATION_SECONDS"] = "45"
    os.environ["PRISMQ_WORKER_POLL_INTERVAL_SECONDS"] = "2"
    os.environ["PRISMQ_WORKER_MAX_RETRIES"] = "5"
    os.environ["PRISMQ_WORKER_CAPABILITIES"] = '{"region": "us-east", "test": true}'
    
    # Load from environment
    config = load_worker_config()  # No file path = load from env
    
    print(f"\n✓ Loaded configuration from environment variables")
    print(f"  Worker ID: {config.worker_id}")
    print(f"  Strategy: {config.scheduling_strategy.value}")
    print(f"  Lease Duration: {config.lease_duration_seconds}s")
    print(f"  Poll Interval: {config.poll_interval_seconds}s")
    print(f"  Max Retries: {config.max_retries}")
    print(f"  Capabilities: {config.capabilities}")
    
    # Clean up environment
    for key in [
        "PRISMQ_WORKER_ID",
        "PRISMQ_WORKER_SCHEDULING_STRATEGY",
        "PRISMQ_WORKER_LEASE_DURATION_SECONDS",
        "PRISMQ_WORKER_POLL_INTERVAL_SECONDS",
        "PRISMQ_WORKER_MAX_RETRIES",
        "PRISMQ_WORKER_CAPABILITIES",
    ]:
        os.environ.pop(key, None)


def demo_env_overrides():
    """Demonstrate environment variable overrides."""
    print("\n" + "="*70)
    print("Demo 5: Environment Variable Overrides")
    print("="*70)
    
    json_path = Path(__file__).parent / "examples" / "worker_config.json"
    
    # Load without overrides
    config_no_override = load_worker_config(str(json_path), apply_env_overrides=False)
    print(f"\n  Without env override:")
    print(f"    Worker ID: {config_no_override.worker_id}")
    print(f"    Strategy: {config_no_override.scheduling_strategy.value}")
    
    # Set environment override
    os.environ["PRISMQ_WORKER_ID"] = "worker-override"
    os.environ["PRISMQ_WORKER_SCHEDULING_STRATEGY"] = "fifo"
    
    # Load with overrides
    config_with_override = load_worker_config(str(json_path), apply_env_overrides=True)
    print(f"\n  With env override:")
    print(f"    Worker ID: {config_with_override.worker_id}")
    print(f"    Strategy: {config_with_override.scheduling_strategy.value}")
    
    print(f"\n✓ Environment variables override file configuration")
    
    # Clean up
    os.environ.pop("PRISMQ_WORKER_ID", None)
    os.environ.pop("PRISMQ_WORKER_SCHEDULING_STRATEGY", None)


def demo_save_config():
    """Demonstrate saving configuration to file."""
    print("\n" + "="*70)
    print("Demo 6: Save Configuration to File")
    print("="*70)
    
    # Create a configuration
    config = WorkerConfig(
        worker_id="worker-saved",
        capabilities={"region": "us-west", "gpu": "RTX5090"},
        scheduling_strategy=SchedulingStrategy.WEIGHTED_RANDOM,
        lease_duration_seconds=90,
        poll_interval_seconds=2,
        max_retries=4,
    )
    
    print(f"\n  Created configuration:")
    print(f"    Worker ID: {config.worker_id}")
    print(f"    Strategy: {config.scheduling_strategy.value}")
    
    # Save to temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "saved_config.json"
        
        manager = WorkerConfigurationManager()
        manager.save_to_file(config, str(save_path))
        
        print(f"\n✓ Saved configuration to: {save_path.name}")
        
        # Load it back
        loaded_config = manager.load_from_file(str(save_path))
        
        print(f"\n✓ Loaded configuration back:")
        print(f"    Worker ID: {loaded_config.worker_id}")
        print(f"    Strategy: {loaded_config.scheduling_strategy.value}")


def demo_worker_with_config():
    """Demonstrate creating a worker with configuration."""
    print("\n" + "="*70)
    print("Demo 7: Create Worker with Configuration")
    print("="*70)
    
    json_path = Path(__file__).parent / "examples" / "worker_config.json"
    
    # Load configuration
    config = load_worker_config(str(json_path), apply_env_overrides=False)
    
    print(f"\n  Configuration loaded:")
    print(f"    Worker ID: {config.worker_id}")
    print(f"    Strategy: {config.scheduling_strategy.value}")
    
    # Create database (in-memory for demo)
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo.db"
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        # Create task claimer based on configuration
        claimer = TaskClaimerFactory.create(config.scheduling_strategy, db)
        
        print(f"\n✓ Created task claimer: {claimer.__class__.__name__}")
        
        # Insert test tasks
        db.execute(
            "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
            ("test_task", '{"data": "test"}', 50)
        )
        db.get_connection().commit()
        
        print(f"✓ Inserted test task")
        
        # Claim task using configuration
        task = claimer.claim_task(
            worker_id=config.worker_id,
            capabilities=config.capabilities,
            lease_seconds=config.lease_duration_seconds
        )
        
        if task:
            print(f"\n✓ Worker claimed task:")
            print(f"    Task ID: {task.id}")
            print(f"    Task Type: {task.type}")
            print(f"    Locked By: {task.locked_by}")
            print(f"    Lease Duration: {config.lease_duration_seconds}s")
        
        db.close()


def demo_all_strategies():
    """Demonstrate all scheduling strategies with configuration."""
    print("\n" + "="*70)
    print("Demo 8: All Scheduling Strategies")
    print("="*70)
    
    examples_dir = Path(__file__).parent / "examples"
    
    configs = {
        "FIFO": examples_dir / "worker_fifo.toml",
        "LIFO": examples_dir / "worker_lifo.json",
        "Priority": examples_dir / "worker_priority.yaml",
        "Weighted Random": examples_dir / "worker_weighted_random.yaml",
    }
    
    print("\n  Available worker configurations:")
    
    for strategy_name, config_path in configs.items():
        try:
            config = load_worker_config(str(config_path), apply_env_overrides=False)
            print(f"\n    {strategy_name}:")
            print(f"      File: {config_path.name}")
            print(f"      Worker ID: {config.worker_id}")
            print(f"      Strategy: {config.scheduling_strategy.value}")
        except (ImportError, FileNotFoundError) as e:
            print(f"\n    {strategy_name}:")
            print(f"      File: {config_path.name}")
            print(f"      ⚠ Skipped: {e}")


def main():
    """Run all configuration demos."""
    print("="*70)
    print("Worker Configuration System - Issue #328")
    print("="*70)
    
    # Run demos
    demo_json_config()
    demo_yaml_config()
    demo_toml_config()
    demo_env_variables()
    demo_env_overrides()
    demo_save_config()
    demo_worker_with_config()
    demo_all_strategies()
    
    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70)
    
    print("\n✓ Worker configuration system ready for production use!")
    print("\nFeatures demonstrated:")
    print("  ✓ JSON configuration loading")
    print("  ✓ YAML configuration loading (requires PyYAML)")
    print("  ✓ TOML configuration loading (requires tomli)")
    print("  ✓ Environment variable configuration")
    print("  ✓ Environment variable overrides")
    print("  ✓ Configuration saving")
    print("  ✓ Worker creation with configuration")
    print("  ✓ All scheduling strategies")
    print("\nNext steps:")
    print("  - Create worker configuration files for your workers")
    print("  - Use load_worker_config() to load configuration")
    print("  - Set environment variables for deployment-specific overrides")
    print("  - See examples/README.md for detailed usage guide")


if __name__ == "__main__":
    main()
