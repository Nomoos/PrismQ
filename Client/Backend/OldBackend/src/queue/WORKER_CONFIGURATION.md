# Worker Configuration System

Comprehensive configuration loading system for queue workers supporting multiple file formats and environment variable overrides.

**Part of Issue #328: Worker Strategy Configuration**

## Overview

The Worker Configuration System provides a flexible, extensible way to configure queue workers with support for:

- **Multiple file formats**: JSON, YAML, TOML
- **Environment variable overrides**: Deploy-specific configuration
- **Validation**: Type-safe configuration with clear error messages
- **Defaults**: Sensible default values for optional settings
- **SOLID design**: Extensible architecture following best practices

## Quick Start

### Load from JSON File

```python
from Client.Backend.src.queue import load_worker_config

# Load configuration
config = load_worker_config("worker.json")

# Use configuration
print(f"Worker: {config.worker_id}")
print(f"Strategy: {config.scheduling_strategy.value}")
```

### Load from Environment

```bash
# Set environment variables
export PRISMQ_WORKER_ID=worker-01
export PRISMQ_WORKER_SCHEDULING_STRATEGY=priority
export PRISMQ_WORKER_CAPABILITIES='{"region": "us-west"}'

# Load configuration (no file needed)
python -c "
from Client.Backend.src.queue import load_worker_config
config = load_worker_config()
print(config.worker_id)
"
```

## Configuration Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `worker_id` | string | **Yes** | - | Unique identifier for the worker |
| `capabilities` | object | No | `{}` | Worker capabilities for task filtering |
| `scheduling_strategy` | string | No | `"priority"` | Task scheduling strategy |
| `lease_duration_seconds` | integer | No | `60` | Task lease duration |
| `poll_interval_seconds` | integer | No | `1` | Queue polling interval |
| `max_retries` | integer | No | `3` | Maximum retry attempts |

### Scheduling Strategies

The `scheduling_strategy` field accepts:

- `"fifo"` - First-In-First-Out (oldest tasks first)
- `"lifo"` - Last-In-First-Out (newest tasks first)
- `"priority"` - Priority-based (lower number = higher priority)
- `"weighted_random"` - Probabilistic selection weighted by priority

See [SCHEDULING_STRATEGIES.md](./SCHEDULING_STRATEGIES.md) for detailed strategy comparison.

### Capabilities

The `capabilities` field is a flexible JSON object that can include any worker-specific metadata:

```json
{
  "region": "us-west",
  "gpu": "RTX5090",
  "cpu_cores": 16,
  "ram_gb": 64,
  "formats": ["mp4", "png", "jpg"],
  "max_video_duration": 600,
  "features": {
    "transcoding": true,
    "gpu_acceleration": true
  }
}
```

Future task claiming logic can use these capabilities for filtering.

## Configuration File Formats

### JSON Format

**File**: `worker.json`

```json
{
  "worker_id": "worker-01",
  "capabilities": {
    "region": "us-west",
    "gpu": "RTX5090"
  },
  "scheduling_strategy": "priority",
  "lease_duration_seconds": 60,
  "poll_interval_seconds": 1,
  "max_retries": 3
}
```

**Pros**:
- No external dependencies
- Built-in Python support
- Widely supported

### YAML Format

**File**: `worker.yaml`

Requires: `pip install pyyaml`

```yaml
worker_id: worker-01
capabilities:
  region: us-west
  gpu: RTX5090
  formats:
    - mp4
    - png
    - jpg
scheduling_strategy: priority
lease_duration_seconds: 60
poll_interval_seconds: 1
max_retries: 3
```

**Pros**:
- Human-readable
- Supports comments
- Less verbose than JSON

### TOML Format

**File**: `worker.toml`

Requires: `pip install tomli`

```toml
worker_id = "worker-01"
scheduling_strategy = "priority"
lease_duration_seconds = 60
poll_interval_seconds = 1
max_retries = 3

[capabilities]
region = "us-west"
gpu = "RTX5090"
formats = ["mp4", "png", "jpg"]
```

**Pros**:
- Clean syntax
- Good for nested structures
- Python standard in 3.11+

## Environment Variables

All configuration values can be set via environment variables:

| Variable | Configuration Field |
|----------|-------------------|
| `PRISMQ_WORKER_ID` | `worker_id` |
| `PRISMQ_WORKER_SCHEDULING_STRATEGY` | `scheduling_strategy` |
| `PRISMQ_WORKER_LEASE_DURATION_SECONDS` | `lease_duration_seconds` |
| `PRISMQ_WORKER_POLL_INTERVAL_SECONDS` | `poll_interval_seconds` |
| `PRISMQ_WORKER_MAX_RETRIES` | `max_retries` |
| `PRISMQ_WORKER_CAPABILITIES` | `capabilities` (JSON string) |

### Environment Variable Overrides

Environment variables **override** file configuration:

```python
# Load from file
config = load_worker_config("worker.json")  # worker_id: "worker-01"

# With PRISMQ_WORKER_ID=worker-override set:
config = load_worker_config("worker.json")  # worker_id: "worker-override"

# Disable overrides:
config = load_worker_config("worker.json", apply_env_overrides=False)
```

## API Reference

### `load_worker_config()`

Convenience function to load worker configuration.

```python
def load_worker_config(
    file_path: Optional[str] = None,
    apply_env_overrides: bool = True
) -> WorkerConfig:
    """
    Load worker configuration.
    
    Args:
        file_path: Path to config file (if None, loads from env only)
        apply_env_overrides: Whether to apply environment overrides
        
    Returns:
        WorkerConfig instance
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If configuration is invalid
    """
```

**Examples**:

```python
# Load from file
config = load_worker_config("worker.json")

# Load from environment only
config = load_worker_config()

# Load from file without env overrides
config = load_worker_config("worker.json", apply_env_overrides=False)
```

### `WorkerConfigurationManager`

Low-level configuration manager with full control.

```python
from Client.Backend.src.queue import WorkerConfigurationManager

manager = WorkerConfigurationManager()

# Load from file
config = manager.load_from_file("worker.json")

# Load from dictionary
config = manager.load_from_dict({"worker_id": "test", ...})

# Load from environment
config = manager.load_from_env()

# Save to file
manager.save_to_file(config, "saved.json")

# Register custom loader
manager.register_loader('.xml', XMLConfigLoader())
```

### `WorkerConfig`

Dataclass representing worker configuration.

```python
@dataclass
class WorkerConfig:
    worker_id: str
    capabilities: Dict[str, Any] = field(default_factory=dict)
    scheduling_strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY
    lease_duration_seconds: int = 60
    poll_interval_seconds: int = 1
    max_retries: int = 3
```

## Usage Patterns

### Basic Worker Loop

```python
from Client.Backend.src.queue import (
    load_worker_config,
    QueueDatabase,
    TaskClaimerFactory,
)
import time

# Load configuration
config = load_worker_config("worker.json")

# Initialize database
db = QueueDatabase()
db.initialize_schema()

# Create task claimer based on configuration
claimer = TaskClaimerFactory.create(config.scheduling_strategy, db)

# Worker loop
while True:
    # Claim task
    task = claimer.claim_task(
        worker_id=config.worker_id,
        capabilities=config.capabilities,
        lease_seconds=config.lease_duration_seconds
    )
    
    if task:
        try:
            # Process task
            process_task(task)
            
            # Mark as completed
            db.execute(
                "UPDATE task_queue SET status = 'completed' WHERE id = ?",
                (task.id,)
            )
        except Exception as e:
            # Mark as failed
            db.execute(
                "UPDATE task_queue SET status = 'failed', error_message = ? WHERE id = ?",
                (str(e), task.id)
            )
    
    # Wait before polling again
    time.sleep(config.poll_interval_seconds)
```

### Multiple Workers with Different Strategies

```python
# Worker 1: Priority strategy for critical tasks
config1 = load_worker_config("worker_priority.yaml")
claimer1 = TaskClaimerFactory.create(config1.scheduling_strategy, db)

# Worker 2: FIFO strategy for background jobs
config2 = load_worker_config("worker_fifo.toml")
claimer2 = TaskClaimerFactory.create(config2.scheduling_strategy, db)

# Worker 3: Weighted random for balanced load
config3 = load_worker_config("worker_balanced.json")
claimer3 = TaskClaimerFactory.create(config3.scheduling_strategy, db)
```

### Dynamic Configuration Reload

```python
import signal

current_config = load_worker_config("worker.json")

def reload_config(signum, frame):
    """Reload configuration on SIGHUP."""
    global current_config
    current_config = load_worker_config("worker.json")
    print(f"Configuration reloaded: {current_config.worker_id}")

signal.signal(signal.SIGHUP, reload_config)
```

## Example Configurations

See [examples/](./examples/) directory for complete examples:

- `worker_config.json` - Default configuration
- `worker_priority.yaml` - Priority strategy
- `worker_fifo.toml` - FIFO strategy
- `worker_lifo.json` - LIFO strategy
- `worker_weighted_random.yaml` - Weighted random strategy

## Validation

Configuration is validated on load:

### Valid Configuration

```python
config = load_worker_config("worker.json")
# ✓ Validation passes
```

### Invalid: Missing worker_id

```python
# config.json: {"scheduling_strategy": "fifo"}
config = load_worker_config("config.json")
# ✗ ValueError: worker_id is required in configuration
```

### Invalid: Unknown Strategy

```python
# config.json: {"worker_id": "test", "scheduling_strategy": "invalid"}
config = load_worker_config("config.json")
# ✗ ValueError: Invalid scheduling strategy: invalid. 
#    Valid strategies: fifo, lifo, priority, weighted_random
```

### Invalid: Bad Integer

```bash
export PRISMQ_WORKER_LEASE_DURATION_SECONDS=not_a_number
python -c "from queue import load_worker_config; load_worker_config()"
# ✗ ValueError: Invalid integer value for PRISMQ_WORKER_LEASE_DURATION_SECONDS
```

## Advanced: Custom Configuration Loaders

Extend the system with custom file formats:

```python
from queue.worker_config import WorkerConfigurationManager, ConfigLoader

class XMLConfigLoader:
    """Custom XML configuration loader."""
    
    def load(self, file_path: str) -> dict:
        import xml.etree.ElementTree as ET
        tree = ET.parse(file_path)
        root = tree.getroot()
        # Parse XML and return dict
        return {
            "worker_id": root.find("worker_id").text,
            # ...
        }

# Register custom loader
manager = WorkerConfigurationManager()
manager.register_loader('.xml', XMLConfigLoader())

# Use custom loader
config = manager.load_from_file('worker.xml')
```

## Best Practices

### 1. Use Configuration Files for Static Settings

Store worker identity, capabilities, and strategy in configuration files.

### 2. Use Environment Variables for Deployment-Specific Settings

Override worker_id, lease duration, or other deploy-specific values via environment variables.

### 3. Validate Early

Load configuration at startup to catch errors early:

```python
# At startup
try:
    config = load_worker_config("worker.json")
except ValueError as e:
    logger.error(f"Invalid configuration: {e}")
    sys.exit(1)
```

### 4. Version Control Configuration Templates

Keep template configurations in version control:

```
configs/
  ├── worker.template.json
  ├── worker.dev.json
  └── worker.prod.json
```

### 5. Document Your Capabilities Schema

Document what capabilities your system uses:

```json
{
  "capabilities": {
    "region": "us-west",        // Required: Worker region
    "gpu": "RTX5090",            // Optional: GPU model
    "formats": ["mp4", "png"],   // Required: Supported formats
    "max_duration": 600          // Optional: Max video duration in seconds
  }
}
```

## Testing

Run tests:

```bash
cd Client/Backend
python _meta/tests/test_worker_config_simple.py
```

Run demo:

```bash
cd Client/Backend
python src/queue/demo_worker_config.py
```

## Integration with Issue #327

This configuration system integrates with the scheduling strategies implemented in Issue #327:

```python
from queue import load_worker_config, TaskClaimerFactory, QueueDatabase

# Load configuration (includes scheduling strategy)
config = load_worker_config("worker.json")

# Create appropriate claimer based on configured strategy
db = QueueDatabase()
claimer = TaskClaimerFactory.create(config.scheduling_strategy, db)

# Claimer is now FIFOTaskClaimer, LIFOTaskClaimer, 
# PriorityTaskClaimer, or WeightedRandomTaskClaimer
# depending on configuration
```

## Troubleshooting

### PyYAML not installed

```
ImportError: PyYAML is required for YAML configuration. Install with: pip install pyyaml
```

**Solution**: `pip install pyyaml`

### tomli not installed

```
ImportError: tomli is required for TOML configuration. Install with: pip install tomli
```

**Solution**: `pip install tomli`

### Invalid JSON in environment variable

```
ValueError: Invalid JSON in PRISMQ_WORKER_CAPABILITIES: {"test": true}
```

**Solution**: Ensure proper JSON escaping in environment variables:

```bash
export PRISMQ_WORKER_CAPABILITIES='{"test": true}'  # Single quotes
```

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
