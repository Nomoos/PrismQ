# Queue Monitoring API Documentation

**Issue #330: Worker Heartbeat and Monitoring**

This document describes the monitoring and observability API for the SQLite queue system.

## Overview

The `QueueMonitoring` class provides comprehensive monitoring and observability features for the queue system, including:
- Worker registration and heartbeat management
- Stale worker detection
- Queue metrics and statistics
- Worker activity tracking

## Quick Start

```python
from queue import QueueDatabase, QueueMonitoring

# Initialize database and monitoring
db = QueueDatabase()
db.initialize_schema()
monitoring = QueueMonitoring(db)

# Register a worker
monitoring.register_worker("worker-01", {"cpu": 8, "gpu": True})

# Update heartbeat
monitoring.update_heartbeat("worker-01")

# Get metrics
metrics = monitoring.get_queue_metrics()
```

## API Reference

### Worker Registration

#### `register_worker(worker_id: str, capabilities: Optional[Dict[str, Any]] = None) -> None`

Register or update a worker in the registry.

Uses UPSERT pattern (INSERT OR REPLACE) to handle both new workers and updates for existing workers.

**Parameters:**
- `worker_id` (str): Unique identifier for the worker
- `capabilities` (dict, optional): Worker capabilities dictionary. Default: `{}`

**Raises:**
- `QueueDatabaseError`: If registration fails

**Example:**
```python
# Register worker with capabilities
monitoring.register_worker("worker-01", {
    "cpu": 8,
    "memory_gb": 16,
    "gpu": True,
    "types": ["video", "audio"]
})

# Register worker without capabilities
monitoring.register_worker("worker-02")

# Re-register worker (updates capabilities and heartbeat)
monitoring.register_worker("worker-01", {"cpu": 16})
```

### Heartbeat Management

#### `update_heartbeat(worker_id: str) -> bool`

Update worker heartbeat timestamp.

**Parameters:**
- `worker_id` (str): Unique identifier for the worker

**Returns:**
- `bool`: True if heartbeat was updated, False if worker not found

**Raises:**
- `QueueDatabaseError`: If update fails

**Example:**
```python
# Update heartbeat
success = monitoring.update_heartbeat("worker-01")
if success:
    print("Heartbeat updated")
else:
    print("Worker not found")
```

**Best Practice:**
Workers should update their heartbeat regularly (e.g., every 30 seconds) to indicate they are alive and processing tasks.

### Worker Queries

#### `get_worker(worker_id: str) -> Optional[Worker]`

Get worker information by ID.

**Parameters:**
- `worker_id` (str): Unique identifier for the worker

**Returns:**
- `Worker` object if found, `None` otherwise

**Raises:**
- `QueueDatabaseError`: If query fails

**Example:**
```python
worker = monitoring.get_worker("worker-01")
if worker:
    print(f"Worker: {worker.worker_id}")
    print(f"Capabilities: {worker.get_capabilities_dict()}")
    print(f"Last heartbeat: {worker.heartbeat_utc}")
```

#### `get_all_workers() -> List[Worker]`

Get all registered workers.

**Returns:**
- List of `Worker` objects

**Raises:**
- `QueueDatabaseError`: If query fails

**Example:**
```python
workers = monitoring.get_all_workers()
print(f"Total workers: {len(workers)}")
for worker in workers:
    print(f"- {worker.worker_id}")
```

#### `get_active_workers(active_threshold_seconds: int = 60) -> List[Worker]`

Get workers that have sent heartbeat recently.

A worker is considered active if its last heartbeat is within the threshold.

**Parameters:**
- `active_threshold_seconds` (int, optional): Seconds since last heartbeat to consider active. Default: 60

**Returns:**
- List of active `Worker` objects

**Raises:**
- `QueueDatabaseError`: If query fails

**Example:**
```python
# Get workers active in last 60 seconds
active = monitoring.get_active_workers(active_threshold_seconds=60)
print(f"Active workers: {len(active)}")

# Get workers active in last 5 minutes
active = monitoring.get_active_workers(active_threshold_seconds=300)
```

#### `get_stale_workers(stale_threshold_seconds: int = 300) -> List[Worker]`

Get workers that haven't sent heartbeat recently.

A worker is considered stale if its last heartbeat is older than the threshold.

**Parameters:**
- `stale_threshold_seconds` (int, optional): Seconds since last heartbeat to consider stale. Default: 300 (5 minutes)

**Returns:**
- List of stale `Worker` objects

**Raises:**
- `QueueDatabaseError`: If query fails

**Example:**
```python
# Get workers stale for more than 5 minutes
stale = monitoring.get_stale_workers(stale_threshold_seconds=300)

# Clean up stale workers
for worker in stale:
    print(f"Removing stale worker: {worker.worker_id}")
    monitoring.remove_worker(worker.worker_id)
```

### Worker Removal

#### `remove_worker(worker_id: str) -> bool`

Remove a worker from the registry.

Useful for cleanup of permanently offline workers.

**Parameters:**
- `worker_id` (str): Unique identifier for the worker

**Returns:**
- `bool`: True if worker was removed, False if not found

**Raises:**
- `QueueDatabaseError`: If removal fails

**Example:**
```python
# Remove specific worker
removed = monitoring.remove_worker("worker-01")
if removed:
    print("Worker removed")
else:
    print("Worker not found")
```

### Queue Metrics

#### `get_queue_metrics() -> Dict[str, Any]`

Get comprehensive queue metrics for monitoring.

**Returns:**
Dictionary with the following keys:
- `queue_depth_by_status` (dict): Count of tasks by status
- `queue_depth_by_type` (dict): Count of queued tasks by type
- `oldest_queued_task_age_seconds` (int or None): Age of oldest queued task in seconds
- `task_statistics` (dict): Statistics for completed/failed tasks
- `success_rate` (float or None): Ratio of completed to finished tasks
- `failure_rate` (float or None): Ratio of failed to finished tasks
- `total_workers` (int): Total registered workers
- `active_workers` (int): Workers active in last 60 seconds
- `stale_workers` (int): Workers stale for more than 5 minutes

**Raises:**
- `QueueDatabaseError`: If queries fail

**Example:**
```python
metrics = monitoring.get_queue_metrics()

# Queue depth
print(f"Queued: {metrics['queue_depth_by_status'].get('queued', 0)}")
print(f"Processing: {metrics['queue_depth_by_status'].get('processing', 0)}")
print(f"Completed: {metrics['queue_depth_by_status'].get('completed', 0)}")
print(f"Failed: {metrics['queue_depth_by_status'].get('failed', 0)}")

# Task statistics
if metrics['success_rate'] is not None:
    print(f"Success rate: {metrics['success_rate']:.1%}")
    print(f"Failure rate: {metrics['failure_rate']:.1%}")

# Worker statistics
print(f"Total workers: {metrics['total_workers']}")
print(f"Active workers: {metrics['active_workers']}")
print(f"Stale workers: {metrics['stale_workers']}")

# Oldest task
if metrics['oldest_queued_task_age_seconds'] is not None:
    age_minutes = metrics['oldest_queued_task_age_seconds'] / 60
    print(f"Oldest queued task: {age_minutes:.1f} minutes old")
```

**Dashboard Example:**
```python
import time

while True:
    metrics = monitoring.get_queue_metrics()
    
    # Clear screen and display dashboard
    print("\033[2J\033[H")  # ANSI clear screen
    print("=" * 60)
    print("Queue Dashboard")
    print("=" * 60)
    print(f"\nQueue Status:")
    for status, count in metrics['queue_depth_by_status'].items():
        print(f"  {status}: {count}")
    
    print(f"\nWorkers:")
    print(f"  Active: {metrics['active_workers']} / {metrics['total_workers']}")
    print(f"  Stale: {metrics['stale_workers']}")
    
    if metrics['success_rate'] is not None:
        print(f"\nTask Performance:")
        print(f"  Success: {metrics['success_rate']:.1%}")
        print(f"  Failure: {metrics['failure_rate']:.1%}")
    
    time.sleep(5)  # Update every 5 seconds
```

### Worker Activity

#### `get_worker_activity() -> List[Dict[str, Any]]`

Get worker activity summary.

**Returns:**
List of dictionaries with the following keys:
- `worker_id` (str): Worker identifier
- `capabilities` (str): JSON string of worker capabilities
- `heartbeat_utc` (str): Timestamp of last heartbeat
- `seconds_since_heartbeat` (int): Seconds since last heartbeat

**Raises:**
- `QueueDatabaseError`: If query fails

**Example:**
```python
activity = monitoring.get_worker_activity()

print("Worker Activity:")
for worker in activity:
    worker_id = worker['worker_id']
    seconds_ago = worker['seconds_since_heartbeat']
    capabilities = json.loads(worker['capabilities'])
    
    status = "🟢 ACTIVE" if seconds_ago < 60 else "🔴 STALE"
    print(f"{status} {worker_id}: {seconds_ago}s ago - {capabilities}")
```

## Common Patterns

### Worker Health Check

```python
def check_worker_health(monitoring: QueueMonitoring):
    """Check health of all workers and alert on stale workers."""
    stale = monitoring.get_stale_workers(stale_threshold_seconds=300)
    
    if stale:
        print(f"⚠️  WARNING: {len(stale)} stale workers detected!")
        for worker in stale:
            print(f"  - {worker.worker_id}")
            # Send alert to monitoring system
            # send_alert(f"Worker {worker.worker_id} is stale")
        return False
    else:
        print("✅ All workers healthy")
        return True
```

### Worker Heartbeat Loop

```python
import time
import signal
import sys

class Worker:
    def __init__(self, worker_id: str, monitoring: QueueMonitoring):
        self.worker_id = worker_id
        self.monitoring = monitoring
        self.running = True
        
        # Register on startup
        self.monitoring.register_worker(self.worker_id, {"cpu": 8})
        
        # Setup graceful shutdown
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
    
    def shutdown(self, signum, frame):
        """Handle shutdown signal."""
        print(f"Shutting down {self.worker_id}...")
        self.running = False
        self.monitoring.remove_worker(self.worker_id)
        sys.exit(0)
    
    def run(self):
        """Main worker loop with heartbeat updates."""
        while self.running:
            try:
                # Update heartbeat
                self.monitoring.update_heartbeat(self.worker_id)
                
                # Process tasks
                # ... task processing logic ...
                
                # Sleep before next iteration
                time.sleep(30)  # Update heartbeat every 30 seconds
                
            except Exception as e:
                print(f"Error in worker loop: {e}")
                time.sleep(5)

# Usage
worker = Worker("worker-01", monitoring)
worker.run()
```

### Stale Worker Cleanup Job

```python
def cleanup_stale_workers(monitoring: QueueMonitoring):
    """Periodic job to clean up stale workers."""
    # Get workers stale for more than 10 minutes
    stale = monitoring.get_stale_workers(stale_threshold_seconds=600)
    
    for worker in stale:
        print(f"Removing stale worker: {worker.worker_id}")
        monitoring.remove_worker(worker.worker_id)
    
    return len(stale)

# Run as cron job or scheduled task
# Every 5 minutes: cleanup_stale_workers(monitoring)
```

### Metrics Collection for Monitoring System

```python
def collect_metrics_for_prometheus(monitoring: QueueMonitoring):
    """Collect metrics in Prometheus format."""
    metrics = monitoring.get_queue_metrics()
    
    # Queue depth metrics
    for status, count in metrics['queue_depth_by_status'].items():
        print(f'queue_depth{{status="{status}"}} {count}')
    
    # Worker metrics
    print(f'workers_total {metrics["total_workers"]}')
    print(f'workers_active {metrics["active_workers"]}')
    print(f'workers_stale {metrics["stale_workers"]}')
    
    # Task performance metrics
    if metrics['success_rate'] is not None:
        print(f'task_success_rate {metrics["success_rate"]}')
        print(f'task_failure_rate {metrics["failure_rate"]}')
    
    # Oldest task age
    if metrics['oldest_queued_task_age_seconds'] is not None:
        print(f'oldest_task_age_seconds {metrics["oldest_queued_task_age_seconds"]}')
```

## Performance Considerations

- **Heartbeat Frequency**: Update heartbeats every 30-60 seconds to balance liveness detection with database load
- **Stale Threshold**: Set stale threshold to 2-3x heartbeat interval (e.g., 5 minutes for 30-second heartbeats)
- **Metrics Polling**: Query metrics at reasonable intervals (e.g., every 5-10 seconds for dashboards)
- **Cleanup Jobs**: Run stale worker cleanup periodically (e.g., every 5 minutes)

## Error Handling

All monitoring functions raise `QueueDatabaseError` if database operations fail. Always wrap calls in try-except blocks:

```python
from queue import QueueDatabaseError

try:
    monitoring.update_heartbeat("worker-01")
except QueueDatabaseError as e:
    logger.error(f"Failed to update heartbeat: {e}")
    # Retry or alert
```

## See Also

- [Queue Core Infrastructure](./README.md)
- [Scheduling Strategies](./SCHEDULING_STRATEGIES.md)
- [Queue API](./QUEUE_API.md)
- Issue #330: Worker Heartbeat and Monitoring
- Issue #329: Queue Observability
