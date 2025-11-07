# Worker Configuration Examples

This directory contains example worker configuration files demonstrating different scheduling strategies and configuration formats.

## Available Examples

### 1. `worker_config.json` - Default Configuration
Basic JSON configuration with priority scheduling strategy.

**Use Case**: General-purpose worker for standard operations.

### 2. `worker_priority.yaml` - Priority Strategy
YAML configuration for a high-priority worker.

**Use Case**: Time-sensitive operations that need to jump ahead in the queue.

### 3. `worker_fifo.toml` - FIFO Strategy
TOML configuration with First-In-First-Out scheduling.

**Use Case**: Fair processing of background jobs where submission order matters.

### 4. `worker_weighted_random.yaml` - Weighted Random Strategy
YAML configuration with probabilistic task selection.

**Use Case**: Load balancing across workers to prevent complete starvation of low-priority tasks.

### 5. `worker_lifo.json` - LIFO Strategy
JSON configuration with Last-In-First-Out scheduling.

**Use Case**: User-triggered actions where latest requests should be prioritized.

## Configuration Fields

All configuration files support the following fields:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `worker_id` | string | Yes | - | Unique identifier for the worker |
| `capabilities` | object | No | `{}` | Worker capabilities for task filtering |
| `scheduling_strategy` | string | No | `"priority"` | Scheduling strategy: `fifo`, `lifo`, `priority`, `weighted_random` |
| `lease_duration_seconds` | integer | No | `60` | How long to lease a task (in seconds) |
| `poll_interval_seconds` | integer | No | `1` | How often to poll for new tasks (in seconds) |
| `max_retries` | integer | No | `3` | Maximum retry attempts for failed tasks |

## Scheduling Strategies

### FIFO (First-In-First-Out)
- **Ordering**: Oldest task first (submission order)
- **Fairness**: High
- **Starvation Risk**: Low
- **Best For**: Background jobs, bulk imports

### LIFO (Last-In-First-Out)
- **Ordering**: Newest task first (reverse submission order)
- **Fairness**: Low
- **Starvation Risk**: High
- **Best For**: User-triggered actions, canceling older requests

### Priority
- **Ordering**: Priority value (lower number = higher priority)
- **Fairness**: None
- **Starvation Risk**: High (for low-priority tasks)
- **Best For**: Time-sensitive operations with clear priorities

### Weighted Random
- **Ordering**: Probabilistic based on priority
- **Fairness**: Medium
- **Starvation Risk**: Low
- **Best For**: Load balancing, preventing complete starvation

## Usage

### Load from JSON
```python
from Client.Backend.src.queue import load_worker_config

config = load_worker_config("examples/worker_config.json")
print(f"Worker: {config.worker_id}")
print(f"Strategy: {config.scheduling_strategy.value}")
```

### Load from YAML
```python
config = load_worker_config("examples/worker_priority.yaml")
```

### Load from TOML
```python
config = load_worker_config("examples/worker_fifo.toml")
```

### Load with Environment Variable Overrides
```bash
# Set environment variables
export PRISMQ_WORKER_ID=worker-override
export PRISMQ_WORKER_SCHEDULING_STRATEGY=fifo

# Load configuration (env vars take precedence)
python -c "
from Client.Backend.src.queue import load_worker_config
config = load_worker_config('examples/worker_config.json')
print(config.worker_id)  # Prints: worker-override
"
```

### Load from Environment Only
```bash
export PRISMQ_WORKER_ID=worker-env
export PRISMQ_WORKER_SCHEDULING_STRATEGY=priority
export PRISMQ_WORKER_CAPABILITIES='{"region": "us-west", "gpu": "RTX5090"}'
export PRISMQ_WORKER_LEASE_DURATION_SECONDS=30

python -c "
from Client.Backend.src.queue import load_worker_config
config = load_worker_config()  # No file path = load from env
print(config.worker_id)  # Prints: worker-env
"
```

## Creating a Worker with Configuration

```python
from Client.Backend.src.queue import (
    load_worker_config,
    QueueDatabase,
    TaskClaimerFactory,
)

# Load configuration
config = load_worker_config("examples/worker_config.json")

# Create database connection
db = QueueDatabase()
db.initialize_schema()

# Create task claimer based on configuration
claimer = TaskClaimerFactory.create(config.scheduling_strategy, db)

# Worker loop
while True:
    # Claim task using configured strategy
    task = claimer.claim_task(
        worker_id=config.worker_id,
        capabilities=config.capabilities,
        lease_seconds=config.lease_duration_seconds
    )
    
    if task:
        print(f"Processing task {task.id}")
        # Process task...
    
    # Wait before polling again
    import time
    time.sleep(config.poll_interval_seconds)
```

## Environment Variables

All configuration values can be overridden using environment variables:

- `PRISMQ_WORKER_ID` - Worker identifier
- `PRISMQ_WORKER_SCHEDULING_STRATEGY` - Scheduling strategy
- `PRISMQ_WORKER_LEASE_DURATION_SECONDS` - Lease duration
- `PRISMQ_WORKER_POLL_INTERVAL_SECONDS` - Poll interval
- `PRISMQ_WORKER_MAX_RETRIES` - Maximum retries
- `PRISMQ_WORKER_CAPABILITIES` - JSON string of capabilities

Environment variables take precedence over file configuration.

## Advanced: Custom Configuration Formats

You can register custom configuration loaders:

```python
from Client.Backend.src.queue import WorkerConfigurationManager

class XMLConfigLoader:
    def load(self, file_path: str) -> dict:
        # Custom XML parsing logic
        pass

manager = WorkerConfigurationManager()
manager.register_loader('.xml', XMLConfigLoader())
config = manager.load_from_file('worker.xml')
```

## Validation

All configurations are validated on load:
- `worker_id` is required
- `scheduling_strategy` must be one of: `fifo`, `lifo`, `priority`, `weighted_random`
- Numeric fields must be valid integers
- Capabilities must be valid JSON

Invalid configurations will raise a `ValueError` with a descriptive error message.
