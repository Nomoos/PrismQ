# Queue Observability Guide

**Issue**: #329 - Queue Observability  
**Version**: 1.1.0  
**Last Updated**: 2025-11-05

---

## Overview

The PrismQ SQLite Queue system includes comprehensive observability features for monitoring, debugging, and analyzing queue performance. This guide covers the observability infrastructure implemented in Issue #329.

### Key Components

1. **TaskLogger** - Persistent task-level logging to database
2. **QueueLogger** - Integrated logging (database + application logs)
3. **QueueMetrics** - Real-time queue metrics and statistics
4. **WorkerHeartbeat** - Worker health monitoring and management
5. **SQL Views** - Dashboard-ready aggregated metrics

---

## Quick Start

### Basic Usage

```python
from src.queue import (
    QueueDatabase,
    TaskLogger,
    QueueLogger,
    QueueMetrics,
    WorkerHeartbeat,
)

# Initialize database
db = QueueDatabase("C:/Data/PrismQ/queue/queue.db")
db.initialize_schema()

# Create observability components
task_logger = TaskLogger(db)
queue_logger = QueueLogger(db)
metrics = QueueMetrics(db)
heartbeat = WorkerHeartbeat(db)

# Log task event
task_logger.log(task_id=123, level="INFO", message="Task started")

# Get queue health
health = metrics.get_queue_health_summary()
print(f"Queue depth: {health['queue_depth']}")
print(f"Active workers: {health['active_workers']}")

# Update worker heartbeat
heartbeat.update_heartbeat("worker-1", {"type": "classifier"})
```

---

## TaskLogger

Manages task-level logging to the `task_logs` table.

### Features

- Persistent log storage in SQLite
- Log level filtering (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Additional details as JSON
- Log retrieval with pagination
- Automatic log cleanup

### API Reference

#### log()

```python
task_logger.log(
    task_id: int,
    level: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
)
```

**Parameters:**
- `task_id`: ID of the task
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `message`: Log message
- `details`: Optional additional details as dictionary

**Example:**
```python
task_logger.log(
    task_id=123,
    level="ERROR",
    message="Task failed due to network timeout",
    details={"error_code": "TIMEOUT", "retry_count": 3}
)
```

#### get_task_logs()

```python
logs = task_logger.get_task_logs(
    task_id: int,
    level: Optional[str] = None,
    limit: int = 100
)
```

**Returns:** List of TaskLog objects (newest first)

**Example:**
```python
# Get all logs for task
logs = task_logger.get_task_logs(task_id=123)

# Get only ERROR logs
error_logs = task_logger.get_task_logs(task_id=123, level="ERROR")

# Get last 10 logs
recent_logs = task_logger.get_task_logs(task_id=123, limit=10)
```

#### get_recent_logs()

```python
logs = task_logger.get_recent_logs(
    limit: int = 100,
    level: Optional[str] = None
)
```

Get recent logs across all tasks.

#### delete_old_logs()

```python
deleted_count = task_logger.delete_old_logs(days=30)
```

Delete logs older than specified number of days.

---

## QueueLogger

Integrates task logging with application logging for unified observability.

### Features

- Dual logging: database + application logger
- Specialized methods for common events
- Automatic log level determination
- Contextual information

### API Reference

#### log_task_event()

```python
queue_logger.log_task_event(
    task_id: int,
    level: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
)
```

Log event to both database and application logs.

#### log_task_transition()

```python
queue_logger.log_task_transition(
    task_id: int,
    from_status: str,
    to_status: str,
    details: Optional[Dict[str, Any]] = None
)
```

Log task status transition with automatic level selection:
- `failed`, `dead_letter` → ERROR
- `completed` → INFO
- Other transitions → DEBUG

**Example:**
```python
queue_logger.log_task_transition(
    task_id=123,
    from_status="processing",
    to_status="failed",
    details={"worker_id": "worker-1", "duration_seconds": 45}
)
```

#### log_task_error()

```python
queue_logger.log_task_error(
    task_id: int,
    error: Exception,
    details: Optional[Dict[str, Any]] = None
)
```

Log task error with exception details.

**Example:**
```python
try:
    process_task(task)
except ValueError as e:
    queue_logger.log_task_error(
        task_id=123,
        error=e,
        details={"input_data": task.payload}
    )
```

#### log_task_retry()

```python
queue_logger.log_task_retry(
    task_id: int,
    attempt: int,
    max_attempts: int,
    next_run_after: datetime,
    details: Optional[Dict[str, Any]] = None
)
```

Log retry attempt with scheduling information.

---

## QueueMetrics

Provides real-time queue metrics and statistics using efficient SQL queries.

### Features

- Queue depth metrics (total, by status, by type)
- Age tracking (oldest queued task)
- Success/failure rates
- Throughput analysis
- Processing time percentiles
- Retry statistics
- Worker activity monitoring
- Comprehensive health summary

### API Reference

#### get_queue_depth()

```python
depth = metrics.get_queue_depth(
    task_type: Optional[str] = None,
    status: Optional[str] = None
)
```

**Example:**
```python
# Total tasks
total = metrics.get_queue_depth()

# Queued tasks only
queued = metrics.get_queue_depth(status="queued")

# Classify tasks
classify_tasks = metrics.get_queue_depth(task_type="classify")

# Queued classify tasks
queued_classify = metrics.get_queue_depth(
    task_type="classify",
    status="queued"
)
```

#### get_queue_depth_by_status()

```python
depth_by_status = metrics.get_queue_depth_by_status()
# Returns: {'queued': 50, 'processing': 5, 'completed': 200}
```

#### get_queue_depth_by_type()

```python
depth_by_type = metrics.get_queue_depth_by_type()
# Returns: {'classify': 100, 'score': 50}
```

#### get_oldest_queued_task_age()

```python
age_seconds = metrics.get_oldest_queued_task_age()
# Returns: 3600 (or None if queue is empty)
```

Indicates queue backlog. High values suggest processing bottleneck.

#### get_success_failure_rates()

```python
rates = metrics.get_success_failure_rates(hours=24)
```

**Returns:**
```python
{
    "success_count": 450,
    "failure_count": 50,
    "total_count": 500,
    "success_rate": 0.9,    # 90%
    "failure_rate": 0.1     # 10%
}
```

#### get_worker_activity()

```python
workers = metrics.get_worker_activity()
```

**Returns:** List of worker info with:
- `worker_id`
- `capabilities`
- `heartbeat_utc`
- `active_tasks`
- `seconds_since_heartbeat`

#### get_throughput_metrics()

```python
throughput = metrics.get_throughput_metrics(hours=1)
```

**Returns:**
```python
{
    "tasks_completed": 120,
    "tasks_per_minute": 2.0,
    "avg_processing_time_seconds": 15.5
}
```

#### get_retry_metrics()

```python
retry_stats = metrics.get_retry_metrics(hours=24)
```

**Returns:**
```python
{
    "total_tasks": 500,
    "tasks_with_retries": 75,
    "retry_rate": 0.15,
    "avg_attempts": 1.2,
    "max_attempts_reached": 5
}
```

#### get_processing_time_percentiles()

```python
percentiles = metrics.get_processing_time_percentiles(
    hours=24,
    task_type: Optional[str] = None
)
```

**Returns:**
```python
{
    "p50": 10.5,   # 50th percentile (median)
    "p95": 45.2,   # 95th percentile
    "p99": 89.7    # 99th percentile
}
```

#### get_queue_health_summary()

```python
health = metrics.get_queue_health_summary()
```

**Returns:** Comprehensive health report with all key metrics:
```python
{
    "queue_depth": {"queued": 50, "processing": 5, "completed": 200},
    "oldest_queued_task_age_seconds": 120,
    "success_failure_rates_24h": {...},
    "throughput_1h": {...},
    "active_workers": 3,
    "retry_metrics_24h": {...},
    "timestamp": "2025-11-05T12:00:00+00:00"
}
```

---

## WorkerHeartbeat

Manages worker lifecycle and health monitoring.

### Features

- Worker registration and heartbeat updates
- Active/stale worker detection
- Worker statistics
- Stale task reclamation
- Worker cleanup

### API Reference

#### update_heartbeat()

```python
heartbeat.update_heartbeat(
    worker_id: str,
    capabilities: Dict[str, Any]
)
```

**Example:**
```python
heartbeat.update_heartbeat(
    worker_id="worker-1",
    capabilities={
        "type": "classifier",
        "version": "1.0",
        "max_concurrent_tasks": 5
    }
)
```

#### get_active_workers()

```python
active_workers = heartbeat.get_active_workers()
```

Returns workers with heartbeat within `stale_threshold_seconds` (default: 300).

#### get_stale_workers()

```python
stale_workers = heartbeat.get_stale_workers()
```

Returns workers with no heartbeat within threshold.

#### cleanup_stale_workers()

```python
deleted_count = heartbeat.cleanup_stale_workers(force=False)
```

**Parameters:**
- `force=False`: Only remove workers with no active tasks
- `force=True`: Remove all stale workers regardless

**Example:**
```python
# Safe cleanup (preserves workers with active tasks)
deleted = heartbeat.cleanup_stale_workers()

# Force cleanup (removes all stale workers)
deleted = heartbeat.cleanup_stale_workers(force=True)
```

#### get_worker_stats()

```python
stats = heartbeat.get_worker_stats(worker_id="worker-1")
```

**Returns:**
```python
{
    "worker_id": "worker-1",
    "capabilities": '{"type": "classifier"}',
    "heartbeat_utc": "2025-11-05 12:00:00",
    "seconds_since_heartbeat": 45,
    "is_active": True,
    "active_tasks_count": 2,
    "total_tasks_processed": 150,
    "completed_tasks": 145,
    "failed_tasks": 5,
    "success_rate": 0.967
}
```

#### get_all_workers_summary()

```python
workers = heartbeat.get_all_workers_summary()
```

Returns summary of all workers (active and stale).

#### reclaim_stale_worker_tasks()

```python
reclaimed_count = heartbeat.reclaim_stale_worker_tasks()
```

Reclaims tasks from stale workers by:
- Setting status to `queued`
- Clearing `locked_by`
- Incrementing `attempts`

Allows tasks to be picked up by active workers.

---

## SQL Views

Dashboard-ready views for efficient querying.

### v_queue_status_summary

```sql
SELECT * FROM v_queue_status_summary;
```

**Columns:**
- `status`: Task status
- `task_count`: Number of tasks
- `avg_attempts`: Average attempts
- `oldest_task`: Oldest task timestamp
- `newest_task`: Newest task timestamp

### v_queue_type_summary

```sql
SELECT * FROM v_queue_type_summary;
```

**Columns:**
- `type`: Task type
- `status`: Task status
- `task_count`: Number of tasks
- `avg_priority`: Average priority

### v_worker_status

```sql
SELECT * FROM v_worker_status
WHERE seconds_since_heartbeat < 300;
```

**Columns:**
- `worker_id`: Worker identifier
- `capabilities`: Worker capabilities JSON
- `heartbeat_utc`: Last heartbeat timestamp
- `active_tasks`: Number of processing tasks
- `seconds_since_heartbeat`: Age of heartbeat

### v_task_performance

```sql
SELECT * FROM v_task_performance
WHERE task_count > 10;
```

**Columns:**
- `type`: Task type
- `status`: Task status
- `task_count`: Number of tasks
- `avg_processing_seconds`: Average processing time
- `avg_attempts`: Average attempts

### v_recent_failures

```sql
SELECT * FROM v_recent_failures
LIMIT 10;
```

**Columns:**
- `id`: Task ID
- `type`: Task type
- `status`: Task status (failed/dead_letter)
- `attempts`: Number of attempts
- `error_message`: Error message
- `finished_at_utc`: Failure timestamp

---

## Dashboard Integration

### Example: Grafana Query

```sql
-- Queue depth over time
SELECT 
    datetime(created_at_utc, 'unixepoch') as time,
    COUNT(*) as value,
    status as metric
FROM task_queue
WHERE created_at_utc >= datetime('now', '-1 hour')
GROUP BY time, status
ORDER BY time;
```

### Example: Real-time Health Monitor

```python
import time
from datetime import datetime

def monitor_queue_health(db, interval_seconds=60):
    """Monitor queue health and log alerts."""
    metrics = QueueMetrics(db)
    
    while True:
        health = metrics.get_queue_health_summary()
        
        # Check for issues
        queued = health["queue_depth"].get("queued", 0)
        if queued > 100:
            print(f"WARNING: High queue depth: {queued} tasks")
        
        oldest_age = health["oldest_queued_task_age_seconds"]
        if oldest_age and oldest_age > 3600:  # 1 hour
            print(f"WARNING: Oldest task age: {oldest_age}s")
        
        success_rate = health["success_failure_rates_24h"]["success_rate"]
        if success_rate < 0.9:  # Below 90%
            print(f"WARNING: Low success rate: {success_rate:.1%}")
        
        time.sleep(interval_seconds)
```

### Example: Worker Health Check

```python
def check_worker_health(db):
    """Check and reclaim stale worker tasks."""
    heartbeat = WorkerHeartbeat(db)
    
    # Get stale workers
    stale = heartbeat.get_stale_workers()
    if stale:
        print(f"Found {len(stale)} stale workers")
        
        # Reclaim their tasks
        reclaimed = heartbeat.reclaim_stale_worker_tasks()
        print(f"Reclaimed {reclaimed} tasks")
        
        # Cleanup stale workers
        deleted = heartbeat.cleanup_stale_workers()
        print(f"Cleaned up {deleted} workers")
```

---

## Best Practices

### 1. Regular Heartbeats

Workers should send heartbeats at least every 60 seconds:

```python
import threading
import time

def heartbeat_thread(db, worker_id, capabilities):
    """Send heartbeat every 60 seconds."""
    heartbeat = WorkerHeartbeat(db)
    
    while True:
        heartbeat.update_heartbeat(worker_id, capabilities)
        time.sleep(60)

# Start heartbeat in background
threading.Thread(
    target=heartbeat_thread,
    args=(db, "worker-1", {"type": "classifier"}),
    daemon=True
).start()
```

### 2. Log Cleanup

Schedule regular log cleanup to prevent database bloat:

```python
from datetime import datetime
import schedule

def cleanup_old_logs(db):
    """Clean up logs older than 30 days."""
    logger = TaskLogger(db)
    deleted = logger.delete_old_logs(days=30)
    print(f"Deleted {deleted} old logs at {datetime.now()}")

# Run daily at 2 AM
schedule.every().day.at("02:00").do(cleanup_old_logs, db)
```

### 3. Structured Logging

Use consistent detail structures for easier querying:

```python
# Good: Structured details
queue_logger.log_task_error(
    task_id=123,
    error=error,
    details={
        "error_code": "NETWORK_TIMEOUT",
        "retry_count": 3,
        "endpoint": "https://api.example.com",
        "duration_ms": 5000
    }
)

# Avoid: Unstructured details
queue_logger.log_task_error(
    task_id=123,
    error=error,
    details={"message": "Network timeout after 3 retries on https://api.example.com"}
)
```

### 4. Performance Monitoring

Monitor key metrics regularly:

```python
def daily_performance_report(db):
    """Generate daily performance report."""
    metrics = QueueMetrics(db)
    
    # Get 24h metrics
    rates = metrics.get_success_failure_rates(hours=24)
    throughput = metrics.get_throughput_metrics(hours=24)
    retry_stats = metrics.get_retry_metrics(hours=24)
    percentiles = metrics.get_processing_time_percentiles(hours=24)
    
    # Generate report
    print("=== Daily Queue Performance Report ===")
    print(f"Tasks completed: {rates['success_count']}")
    print(f"Success rate: {rates['success_rate']:.1%}")
    print(f"Throughput: {throughput['tasks_per_minute']:.2f} tasks/min")
    print(f"Retry rate: {retry_stats['retry_rate']:.1%}")
    print(f"Processing time (p95): {percentiles['p95']:.2f}s")
```

---

## Troubleshooting

### High Queue Depth

**Symptoms:**
- `get_queue_depth(status="queued")` returns high values
- `get_oldest_queued_task_age()` returns large values

**Solutions:**
1. Check active workers: `metrics.get_worker_activity()`
2. Scale up workers if needed
3. Check for stale workers: `heartbeat.get_stale_workers()`
4. Reclaim stale tasks: `heartbeat.reclaim_stale_worker_tasks()`

### Low Success Rate

**Symptoms:**
- `get_success_failure_rates()` shows low success_rate

**Solutions:**
1. Check recent failures: `SELECT * FROM v_recent_failures`
2. Review error logs: `task_logger.get_recent_logs(level="ERROR")`
3. Check task retry metrics: `metrics.get_retry_metrics()`
4. Investigate common error patterns

### Stale Workers

**Symptoms:**
- `get_stale_workers()` returns workers
- Tasks stuck in "processing" status

**Solutions:**
1. Investigate why workers stopped (logs, crashes)
2. Reclaim their tasks: `heartbeat.reclaim_stale_worker_tasks()`
3. Clean up stale workers: `heartbeat.cleanup_stale_workers()`
4. Restart workers if needed

### Slow Processing

**Symptoms:**
- High processing time percentiles
- Low throughput

**Solutions:**
1. Check processing time distribution: `get_processing_time_percentiles()`
2. Identify slow task types: `SELECT * FROM v_task_performance`
3. Optimize slow tasks
4. Consider parallel processing

---

## Performance Considerations

### Query Efficiency

All metrics queries use indexes for performance:
- `ix_task_status_prio_time` for status queries
- `ix_task_type_status` for type queries
- `ix_logs_task` for log retrieval

### Logging Overhead

Task logging has minimal overhead (<1ms per log):
- Asynchronous writes (non-blocking)
- Batch log retrieval
- Efficient JSON serialization

### View Performance

SQL views are lightweight and don't store data:
- Computed on-demand
- Leverage existing indexes
- Can be materialized if needed for large datasets

---

## Related Documentation

- [SQLite Queue Architecture](./ARCHITECTURE.md)
- [Core Infrastructure (#321)](./../issues/done/321-implement-sqlite-queue-core-infrastructure.md)
- [Queue Analysis (#320)](./../issues/new/Infrastructure_DevOps/320-sqlite-queue-analysis-and-design.md)
- [API Reference](./API_REFERENCE.md)

---

**Version**: 1.1.0  
**Last Updated**: 2025-11-05  
**Implemented**: Issue #329
