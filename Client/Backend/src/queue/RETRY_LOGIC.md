# Retry Logic and Worker Engine

**Issue #326: Retry Logic and Dead-Letter Handling**

This module implements comprehensive retry logic and worker task execution for the SQLite queue system.

## Features

### Task Lifecycle Management

- **Task Completion**: Mark tasks as successfully completed
- **Task Failure**: Handle task failures with configurable retry behavior
- **Lease Renewal**: Extend task leases for long-running operations
- **Error Capture**: Store detailed error messages for failed tasks

### Retry Logic

- **Exponential Backoff**: Automatic retry with exponentially increasing delays
- **Jitter**: Randomized delays to prevent thundering herd problem
- **Max Attempts**: Configurable maximum retry attempts per task
- **Dead-Letter Handling**: Move tasks to failed status after max attempts

### Worker Engine

- **Task Claiming**: Automatic task claiming with configurable strategies
- **Worker Loop**: Continuous task processing with polling
- **Error Handling**: Automatic retry on task handler exceptions
- **Graceful Shutdown**: Clean worker loop termination

## Components

### TaskExecutor

Handles low-level task lifecycle operations:

```python
from src.queue import QueueDatabase, TaskExecutor

db = QueueDatabase()
db.initialize_schema()

executor = TaskExecutor(db)

# Complete a task
executor.complete_task(task_id=1)

# Fail a task with retry
executor.fail_task(
    task_id=2,
    error_message="Processing failed",
    retry=True  # Requeue with exponential backoff
)

# Renew task lease
executor.renew_lease(task_id=3, lease_seconds=120)
```

### WorkerEngine

High-level worker that claims and processes tasks:

```python
from src.queue import QueueDatabase, WorkerEngine, SchedulingStrategy, Task

db = QueueDatabase()
db.initialize_schema()

# Create worker
worker = WorkerEngine(
    db=db,
    worker_id="worker-001",
    capabilities={"cpu": 8, "gpu": "RTX5090"},
    scheduling_strategy=SchedulingStrategy.PRIORITY,
    lease_seconds=60,
    poll_interval_seconds=1.0
)

# Define task handler
def process_task(task: Task):
    """Process a task. Raise exception on failure."""
    import json
    payload = json.loads(task.payload)
    
    # Do work...
    print(f"Processing {task.type}: {payload}")
    
    # If this raises an exception, task will be retried

# Process one task
worker.claim_and_process(process_task)

# Or run continuous worker loop
worker.run_loop(process_task)  # Runs until worker.stop() is called
```

### RetryConfig

Configure retry behavior:

```python
from src.queue import RetryConfig

config = RetryConfig(
    initial_delay_seconds=1.0,    # Initial delay before first retry
    max_delay_seconds=300.0,      # Maximum delay (5 minutes)
    backoff_multiplier=2.0,       # Exponential backoff multiplier
    jitter_factor=0.1             # Add ±10% randomness
)
```

## Retry Behavior

### Exponential Backoff Formula

```
delay = initial_delay * (backoff_multiplier ^ (attempt - 1))
delay = min(delay, max_delay)
delay *= (1.0 ± jitter_factor)  # Random jitter
```

### Example Progression

With default config (`initial_delay=1.0s`, `multiplier=2.0`, `jitter=0.1`):

| Attempt | Base Delay | With Jitter (±10%) |
|---------|------------|-------------------|
| 1       | 1s         | 0.9s - 1.1s      |
| 2       | 2s         | 1.8s - 2.2s      |
| 3       | 4s         | 3.6s - 4.4s      |
| 4       | 8s         | 7.2s - 8.8s      |
| 5       | 16s        | 14.4s - 17.6s    |

### Dead-Letter Handling

When a task reaches `max_attempts`:

1. Task status changes to `'failed'`
2. Final error message is stored
3. `finished_at_utc` timestamp is set
4. Task will not be retried further

Query dead-letter tasks:

```sql
SELECT * FROM task_queue
WHERE status = 'failed'
ORDER BY finished_at_utc DESC;
```

## Task Statuses

| Status | Description |
|--------|-------------|
| `queued` | Task is waiting to be claimed |
| `leased` | Task has been claimed by a worker |
| `completed` | Task completed successfully |
| `failed` | Task failed (dead-letter) |

## Database Schema

The retry logic uses these fields from `task_queue`:

```sql
attempts           INTEGER      -- Current number of attempts
max_attempts       INTEGER      -- Maximum retry attempts
error_message      TEXT         -- Last error message
run_after_utc      DATETIME     -- Earliest time to retry
lease_until_utc    DATETIME     -- Lease expiration time
locked_by          TEXT         -- Worker ID that claimed task
finished_at_utc    DATETIME     -- Completion/failure timestamp
```

## Worker Loop Pattern

### Basic Worker

```python
def main():
    db = QueueDatabase()
    db.initialize_schema()
    
    worker = WorkerEngine(
        db=db,
        worker_id="worker-001",
        scheduling_strategy=SchedulingStrategy.PRIORITY
    )
    
    def handle_task(task: Task):
        # Your task processing logic
        pass
    
    # Run until Ctrl+C
    try:
        worker.run_loop(handle_task)
    except KeyboardInterrupt:
        worker.stop()
        print("Worker stopped")

if __name__ == "__main__":
    main()
```

### Worker with Max Iterations

```python
# Process exactly 10 tasks then stop
worker.run_loop(handle_task, max_iterations=10)
```

### Manual Task Processing

```python
# Process tasks manually
while True:
    claimed = worker.claim_and_process(handle_task)
    if not claimed:
        time.sleep(1.0)  # Wait if no tasks available
```

## Error Handling

### Retryable Errors

Raise any exception to trigger retry:

```python
def handle_task(task: Task):
    if network_error:
        raise ConnectionError("Network unavailable")  # Will retry
```

### Non-Retryable Errors

For permanent failures, fail task without retry:

```python
from src.queue import TaskExecutor

def handle_task(task: Task):
    try:
        # Process task
        pass
    except ValidationError as e:
        # Permanent error - don't retry
        executor = TaskExecutor(db)
        executor.fail_task(task.id, str(e), retry=False)
        return  # Don't raise exception
```

## Lease Renewal

For long-running tasks, renew the lease periodically:

```python
import threading

def handle_long_task(task: Task):
    executor = TaskExecutor(db)
    
    # Start lease renewal thread
    stop_renewal = threading.Event()
    
    def renew_periodically():
        while not stop_renewal.is_set():
            time.sleep(30)  # Renew every 30 seconds
            executor.renew_lease(task.id, lease_seconds=60)
    
    renewal_thread = threading.Thread(target=renew_periodically)
    renewal_thread.start()
    
    try:
        # Do long-running work
        for i in range(100):
            time.sleep(5)  # Simulate work
    finally:
        stop_renewal.set()
        renewal_thread.join()
```

## Testing

Run comprehensive tests:

```bash
# Test retry logic
pytest Client/_meta/tests/Backend/queue/test_retry_logic.py -v

# Test all queue functionality
pytest Client/_meta/tests/Backend/queue/ -v
```

## Demonstrations

Run demo scripts to see retry logic in action:

```bash
# Core infrastructure demo
python Client/Backend/src/queue/demo.py

# Retry logic demo
python Client/Backend/src/queue/demo_retry.py
```

## Performance Considerations

### Backoff Strategy

- **Initial delay**: Set low (1s) for fast failures
- **Max delay**: Set high (300s) for persistent issues
- **Jitter**: Always use jitter to prevent thundering herd

### Lease Duration

- **Short tasks**: 60 seconds
- **Medium tasks**: 120-300 seconds
- **Long tasks**: Use lease renewal instead of long initial lease

### Poll Interval

- **High throughput**: 0.1-1.0 seconds
- **Low throughput**: 1.0-5.0 seconds
- **Batch processing**: 5.0-10.0 seconds

## Best Practices

1. **Set appropriate max_attempts**: 3-5 for most tasks
2. **Use task-specific retry logic**: Some errors shouldn't retry
3. **Monitor dead-letter queue**: Review failed tasks regularly
4. **Use worker capabilities**: Filter tasks by worker capabilities
5. **Implement idempotency**: Tasks should be safe to retry
6. **Log errors clearly**: Include context in error messages
7. **Use lease renewal**: For tasks longer than lease duration
8. **Graceful shutdown**: Always call `worker.stop()` on exit

## Integration with Issue #327

This retry logic works with all scheduling strategies:

- **FIFO**: Oldest tasks first
- **LIFO**: Newest tasks first
- **Priority**: High-priority tasks first
- **Weighted Random**: Probabilistic priority-based selection

Example:

```python
# Use FIFO strategy for fair processing
worker = WorkerEngine(
    db=db,
    worker_id="fair-worker",
    scheduling_strategy=SchedulingStrategy.FIFO
)

# Use Priority strategy for time-sensitive tasks
worker = WorkerEngine(
    db=db,
    worker_id="priority-worker",
    scheduling_strategy=SchedulingStrategy.PRIORITY
)
```

## Related Issues

- **#321**: Core Infrastructure (Database, Schema, Models)
- **#327**: Scheduling Strategies (FIFO, LIFO, Priority, Weighted Random)
- **#329**: Queue Observability (Metrics, Logging)
- **#331**: Database Maintenance (Backup, Cleanup)

## SOLID Principles

This implementation follows SOLID design principles:

- **Single Responsibility**: Each class has one clear responsibility
  - `TaskExecutor`: Task lifecycle operations
  - `WorkerEngine`: Worker coordination and task processing
  - `RetryConfig`: Retry configuration
  
- **Open/Closed**: Extended without modification
  - Custom task handlers via callable interface
  - Custom retry configs via dataclass
  
- **Liskov Substitution**: TaskExecutor works with any QueueDatabase
  
- **Interface Segregation**: Focused interfaces
  - `claim_and_process()` for single task
  - `run_loop()` for continuous processing
  
- **Dependency Inversion**: Depends on abstractions
  - Depends on `QueueDatabase` interface
  - Uses `TaskClaimer` protocol from scheduling module

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
