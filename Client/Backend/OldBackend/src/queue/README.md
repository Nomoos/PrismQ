# SQLite Queue Module

Production-ready SQLite-based task queue for PrismQ.IdeaInspiration with comprehensive observability and Windows optimization.

## Overview

This module provides a robust, thread-safe SQLite database layer for managing task queues in the PrismQ system. It includes comprehensive observability features for monitoring, debugging, and performance analysis. Optimized for Windows SSD performance and fully cross-platform compatible.

## Features

### Core Infrastructure (#321)
- **Windows-Optimized**: PRAGMA settings tuned for Windows SSD performance
- **Thread-Safe**: RLock-based synchronization for concurrent access
- **Transactional**: IMMEDIATE transactions for atomic operations
- **Type-Safe**: Dataclasses with full serialization support
- **Well-Tested**: 84% test coverage with 41 passing tests

### Observability (#329)
- **Task Logging**: Persistent task-level logging to database
- **Integrated Logging**: Dual logging (database + application logs)
- **Real-time Metrics**: Queue depth, throughput, success rates
- **Worker Monitoring**: Heartbeat tracking and health monitoring
- **SQL Views**: Dashboard-ready aggregated metrics
- **Performance Analytics**: Processing time percentiles, retry metrics

### Production Configuration (#337)
- **Benchmarked**: Validated 100-1000 tasks/minute
- **Low Latency**: <10ms claim, <5ms enqueue
- **High Reliability**: <1% SQLITE_BUSY rate

## Quick Start

### Basic Usage

```python
from queue import QueueDatabase, Task

# Create database connection
db = QueueDatabase()  # Uses default path or PRISMQ_QUEUE_DB_PATH env var
db.initialize_schema()

# Insert a task
with db.transaction() as conn:
    conn.execute(
        "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
        ("video_processing", '{"format": "mp4"}', 50)
    )

# Query tasks
cursor = db.execute("SELECT * FROM task_queue WHERE status = ?", ("queued",))
for row in cursor:
    task = Task.from_dict(dict(row))
    print(f"Task {task.id}: {task.type}")

# Close connection
db.close()
```

### Observability Features

```python
from queue import QueueLogger, QueueMetrics, WorkerHeartbeat

# Create observability components
logger = QueueLogger(db)
metrics = QueueMetrics(db)
heartbeat = WorkerHeartbeat(db)

# Log task events
logger.log_task_event(task_id=123, level="INFO", message="Task started")
logger.log_task_transition(task_id=123, from_status="queued", to_status="processing")

# Get queue health
health = metrics.get_queue_health_summary()
print(f"Queue depth: {health['queue_depth']}")
print(f"Success rate: {health['success_failure_rates_24h']['success_rate']:.1%}")

# Update worker heartbeat
heartbeat.update_heartbeat("worker-1", {"type": "classifier", "version": "1.0"})

# Check worker health
active_workers = heartbeat.get_active_workers()
stale_workers = heartbeat.get_stale_workers()
```

## Database Schema

### Tables

#### `task_queue`
Primary table for task management with the following key columns:
- `id`: Autoincrement primary key
- `type`: Task type identifier
- `priority`: Priority level (default: 100, lower = higher priority)
- `payload`: JSON task data
- `compatibility`: JSON worker compatibility requirements
- `status`: Task status (queued, processing, completed, failed)
- `attempts`: Number of execution attempts
- Generated columns: `region`, `format` (from JSON fields)

#### `workers`
Worker registration and heartbeat tracking:
- `worker_id`: Unique worker identifier
- `capabilities`: JSON worker capabilities
- `heartbeat_utc`: Last heartbeat timestamp

#### `task_logs`
Task execution logging:
- `log_id`: Autoincrement primary key
- `task_id`: Foreign key to task_queue
- `at_utc`: Timestamp of log entry
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `message`: Log message
- `details`: Additional JSON details

### SQL Views (Issue #329)

Dashboard-ready views for observability:

#### `v_queue_status_summary`
Queue status aggregation with task counts and timestamps.

#### `v_queue_type_summary`
Task counts grouped by type and status with average priority.

#### `v_worker_status`
Worker health monitoring with active tasks and heartbeat age.

#### `v_task_performance`
Processing time and attempt statistics by task type.

#### `v_recent_failures`
Last 100 failed or dead-letter tasks with error messages.

### Indexes

Performance-optimized indexes:
- `ix_task_status_prio_time`: Multi-column index for task claiming
- `ix_task_type_status`: Index for filtering by task type
- `ix_task_region`, `ix_task_format`: Generated column indexes
- `uq_task_idempotency`: Unique constraint on idempotency keys

## Configuration

### Database Location

Default paths:
- **Windows**: `C:\Data\PrismQ\queue\queue.db`
- **Linux/macOS**: `/tmp/prismq/queue/queue.db`

Override with environment variable:
```bash
export PRISMQ_QUEUE_DB_PATH=/path/to/custom/queue.db
```

### PRAGMA Settings

Windows-optimized settings applied on connection:

```python
PRAGMAS = {
    'journal_mode': 'WAL',           # Write-Ahead Logging for concurrency
    'synchronous': 'NORMAL',         # Balance durability vs performance
    'busy_timeout': 5000,            # 5 seconds for lock retries
    'wal_autocheckpoint': 1000,      # Checkpoint every 1000 pages
    'foreign_keys': 'ON',            # Enable FK constraints
    'temp_store': 'MEMORY',          # Temp tables in memory
    'mmap_size': 134217728,          # 128MB memory-mapped I/O
    'page_size': 4096,               # Match filesystem block size
    'cache_size': -20000,            # ~20MB cache
}
```

## API Reference

### Core Infrastructure

#### QueueDatabase

Main database connection manager.

```python
class QueueDatabase:
    def __init__(self, db_path: Optional[str] = None)
    def initialize_schema(self) -> None
    def get_connection(self) -> sqlite3.Connection
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor
    def execute_many(self, sql: str, param_list: List[tuple]) -> None
    def transaction(self) -> ContextManager[sqlite3.Connection]
    def close(self) -> None
```

**Context Manager Support:**
```python
with QueueDatabase() as db:
    db.initialize_schema()
    # ... use database
# Automatically closed
```

### Observability Components

#### TaskLogger

Persistent task-level logging.

```python
class TaskLogger:
    def log(task_id: int, level: str, message: str, details: Optional[Dict] = None)
    def get_task_logs(task_id: int, level: Optional[str] = None, limit: int = 100) -> List[TaskLog]
    def get_recent_logs(limit: int = 100, level: Optional[str] = None) -> List[TaskLog]
    def delete_old_logs(days: int = 30) -> int
```

#### QueueLogger

Integrated logging (database + application).

```python
class QueueLogger:
    def log_task_event(task_id: int, level: str, message: str, details: Optional[Dict] = None)
    def log_task_transition(task_id: int, from_status: str, to_status: str, details: Optional[Dict] = None)
    def log_task_error(task_id: int, error: Exception, details: Optional[Dict] = None)
    def log_task_retry(task_id: int, attempt: int, max_attempts: int, next_run_after: datetime, details: Optional[Dict] = None)
```

#### QueueMetrics

Real-time metrics and statistics.

```python
class QueueMetrics:
    def get_queue_depth(task_type: Optional[str] = None, status: Optional[str] = None) -> int
    def get_queue_depth_by_status() -> Dict[str, int]
    def get_queue_depth_by_type() -> Dict[str, int]
    def get_oldest_queued_task_age() -> Optional[int]
    def get_success_failure_rates(hours: int = 24) -> Dict[str, Any]
    def get_worker_activity() -> List[Dict[str, Any]]
    def get_throughput_metrics(hours: int = 1) -> Dict[str, Any]
    def get_retry_metrics(hours: int = 24) -> Dict[str, Any]
    def get_processing_time_percentiles(hours: int = 24, task_type: Optional[str] = None) -> Dict[str, float]
    def get_queue_health_summary() -> Dict[str, Any]
```

#### WorkerHeartbeat

Worker health monitoring and management.

```python
class WorkerHeartbeat:
    def update_heartbeat(worker_id: str, capabilities: Dict[str, Any])
    def get_active_workers() -> List[Worker]
    def get_stale_workers() -> List[Worker]
    def cleanup_stale_workers(force: bool = False) -> int
    def get_worker_stats(worker_id: str) -> Dict[str, Any]
    def get_all_workers_summary() -> List[Dict[str, Any]]
    def reclaim_stale_worker_tasks() -> int
```

### Data Models

#### Task
```python
@dataclass
class Task:
    id: Optional[int]
    type: str
    priority: int = 100
    payload: str = "{}"
    status: str = "queued"
    # ... additional fields
    
    def to_dict(self) -> Dict[str, Any]
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task"
    def get_payload_dict(self) -> Dict[str, Any]
    def get_compatibility_dict(self) -> Dict[str, Any]
```

#### Worker
```python
@dataclass
class Worker:
    worker_id: str
    capabilities: str = "{}"
    heartbeat_utc: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Worker"
    def get_capabilities_dict(self) -> Dict[str, Any]
```

#### TaskLog
```python
@dataclass
class TaskLog:
    log_id: Optional[int]
    task_id: int
    level: str = "INFO"
    message: Optional[str] = None
    details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskLog"
```

### Exceptions

```python
class QueueDatabaseError(Exception):
    """Base exception for queue database errors."""

class QueueBusyError(QueueDatabaseError):
    """Raised when database is locked (SQLITE_BUSY)."""

class QueueSchemaError(QueueDatabaseError):
    """Raised when schema operation fails."""
```

## Thread Safety

The `QueueDatabase` class is thread-safe:

```python
import threading

db = QueueDatabase()
db.initialize_schema()

def worker_task():
    with db.transaction() as conn:
        conn.execute(
            "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
            ("test", "{}")
        )

threads = [threading.Thread(target=worker_task) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Performance Characteristics

- **Database initialization**: <100ms
- **Connection overhead**: <10ms
- **Transaction throughput**: >100 tx/sec
- **SQLITE_BUSY error rate**: <1%

## Testing

Run tests:
```bash
cd Client
PYTHONPATH=/path/to/Backend python -m pytest _meta/tests/Backend/queue/ -v
```

Run specific test modules:
```bash
# Core infrastructure tests
python -m pytest _meta/tests/Backend/queue/test_queue_database.py -v

# Observability tests
python -m pytest _meta/tests/Backend/queue/test_logger.py -v
python -m pytest _meta/tests/Backend/queue/test_metrics.py -v
python -m pytest _meta/tests/Backend/queue/test_heartbeat.py -v
```

Run with coverage:
```bash
python -m pytest _meta/tests/Backend/queue/ --cov=src/queue --cov-report=term-missing
```

**Test Coverage:**
- Core Infrastructure: 84% (41 tests)
- Observability: 100% (69 tests)
  - TaskLogger: 22 tests
  - QueueLogger: 7 tests
  - QueueMetrics: 26 tests
  - WorkerHeartbeat: 18 tests

## Best Practices

### 1. Use Context Managers

```python
# Good
with db.transaction() as conn:
    conn.execute("INSERT ...")

# Also good
with QueueDatabase() as db:
    db.initialize_schema()
```

### 2. Parameterize Queries

```python
# Good - prevents SQL injection
db.execute("SELECT * FROM task_queue WHERE type = ?", (task_type,))

# Bad - vulnerable to SQL injection
db.execute(f"SELECT * FROM task_queue WHERE type = '{task_type}'")
```

### 3. Handle Errors

```python
from queue import QueueBusyError, QueueDatabaseError

try:
    with db.transaction() as conn:
        conn.execute("INSERT ...")
except QueueBusyError:
    # Retry logic
    pass
except QueueDatabaseError as e:
    # Log error
    logger.error(f"Database error: {e}")
```

### 4. Batch Operations

```python
# Efficient batch insert
tasks = [("type1", "{}"), ("type2", "{}"), ("type3", "{}")]
db.execute_many(
    "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
    tasks
)
```

## Integration Points

This module is used by:
- **Worker 02**: Client API (#323) - for enqueue operations ✅ **IMPLEMENTED**
- **Worker 03**: Worker Engine (#325, #326) - for task claiming and retry logic ✅ **IMPLEMENTED**
- **Worker 04**: Scheduling (#327) - for different claim strategies ✅ **IMPLEMENTED**
- **Worker 05**: Observability (#329) - for metrics queries
- **Worker 06**: Maintenance (#331) - for backup and optimization

## Additional Documentation

- **[QUEUE_API.md](./QUEUE_API.md)** - REST API documentation
  - Enqueue task endpoint
  - Task status polling
  - Task cancellation
  - Queue statistics
  - Request/response examples
  - Best practices

- **[RETRY_LOGIC.md](./RETRY_LOGIC.md)** - Retry logic and worker engine ✅ **NEW**
  - Task lifecycle management
  - Exponential backoff retry
  - Dead-letter handling
  - Worker execution loop
  - Lease renewal
  - Usage examples

- **[SCHEDULING_STRATEGIES.md](./SCHEDULING_STRATEGIES.md)** - Scheduling strategies
  - FIFO, LIFO, Priority, Weighted Random
  - Strategy comparison
  - Performance characteristics
  - Use cases
- **Worker 03**: Worker Engine (#325) - for task claiming
- **Worker 04**: Scheduling (#327) - for different claim strategies ✅ **IMPLEMENTED**
- **Worker 04**: Configuration (#328) - for worker configuration ✅ **IMPLEMENTED**
- **Worker 05**: Observability (#329) - for metrics queries
- **Worker 06**: Maintenance (#331) - for backup and optimization

## Worker Configuration

See [WORKER_CONFIGURATION.md](./WORKER_CONFIGURATION.md) for worker configuration system (Issue #328):
- Loading configuration from JSON, YAML, TOML files
- Environment variable overrides
- Scheduling strategy configuration
- Worker capabilities setup
- Complete usage examples
- **Worker 05**: Observability (#329, #330) - for metrics queries ✅ **IMPLEMENTED**
- **Worker 06**: Maintenance (#331) - for backup and optimization

## Monitoring and Observability (Issue #330)

### QueueMonitoring

Worker heartbeat and observability manager for queue monitoring.

```python
from queue import QueueDatabase, QueueMonitoring

db = QueueDatabase()
db.initialize_schema()
monitoring = QueueMonitoring(db)

# Register worker
monitoring.register_worker("worker-01", {"cpu": 8, "gpu": True})

# Update heartbeat
monitoring.update_heartbeat("worker-01")

# Get active workers
active = monitoring.get_active_workers(active_threshold_seconds=60)

# Get stale workers
stale = monitoring.get_stale_workers(stale_threshold_seconds=300)

# Get queue metrics
metrics = monitoring.get_queue_metrics()
print(f"Queue depth: {metrics['queue_depth_by_status']}")
print(f"Success rate: {metrics['success_rate']}")

# Get worker activity
activity = monitoring.get_worker_activity()
for worker in activity:
    print(f"{worker['worker_id']}: {worker['seconds_since_heartbeat']}s ago")
```

### Monitoring Features

#### Worker Registration
- Register workers with capabilities
- UPSERT pattern (handles both new and existing workers)
- Automatic heartbeat timestamp on registration

#### Heartbeat Updates
- Update worker heartbeat timestamp
- Returns True/False based on success
- Used to track worker liveness

#### Stale Worker Detection
- Identify workers that haven't sent heartbeat recently
- Configurable threshold (default: 300 seconds / 5 minutes)
- Useful for cleanup and alerting

#### Queue Metrics
- Queue depth by status and type
- Task success/failure rates
- Age of oldest queued task
- Worker statistics (total, active, stale)
- Dashboard-ready metrics

#### Worker Activity
- Track all workers with heartbeat timestamps
- Calculate time since last heartbeat
- View worker capabilities
- Sorted by most recent heartbeat

### Running the Demo

```bash
cd Client/Backend
PYTHONPATH=$(pwd) python3 src/queue/demo_monitoring.py
```

The demo showcases:
- Worker registration and heartbeat updates
- Stale worker detection and cleanup
- Queue metrics collection
- Worker activity tracking
- Complete worker lifecycle

- **Worker 04**: Scheduling (#327) - for different claim strategies
- **Worker 05**: Observability (#329) - **COMPLETE** - metrics and logging
- **Worker 06**: Maintenance (#331) - for backup and optimization

## Documentation

- **[Queue Observability Guide](./../../../../../_meta/docs/QUEUE_OBSERVABILITY.md)** - Complete observability documentation with examples
- **[Core Infrastructure Issue](./../../../../../_meta/issues/done/321-implement-sqlite-queue-core-infrastructure.md)** - Implementation details
- **[Observability Issue](./../../../../../_meta/issues/new/Worker05/329-implement-queue-observability.md)** - Observability features
- **[Queue Analysis](./../../../../../_meta/issues/new/Infrastructure_DevOps/320-sqlite-queue-analysis-and-design.md)** - Design decisions

## Version History

- **1.1.0** - Added comprehensive observability (Issue #329)
  - TaskLogger for task-level logging
  - QueueLogger for integrated logging
  - QueueMetrics for real-time metrics
  - WorkerHeartbeat for worker monitoring
  - SQL views for dashboard integration
  - 69 passing tests for observability

- **1.0.0** - Initial release (Issue #321)
  - Core infrastructure
  - Windows-optimized PRAGMA settings
  - Thread-safe operations
  - 41 passing tests
## Maintenance and Operations

### Backup and Restore

```python
from queue import QueueBackup

# Create backup manager
backup = QueueBackup(db)

# Create a backup (non-blocking)
backup_path = backup.create_backup(name="daily")

# Verify backup integrity
is_valid = backup.verify_backup(backup_path)

# List all backups
backups = backup.list_backups()

# Cleanup old backups (keep last 10)
backup.cleanup_old_backups(keep_count=10)

# Restore from backup
backup.restore_backup(backup_path)
```

### Maintenance Operations

```python
from queue import QueueMaintenance

# Create maintenance manager
maint = QueueMaintenance(db)

# WAL checkpoint
result = maint.checkpoint(mode=QueueMaintenance.CHECKPOINT_PASSIVE)

# Update query planner statistics (fast, non-blocking)
maint.analyze()

# Reclaim free space (slow, blocks writes)
maint.vacuum()

# Check database integrity
results = maint.integrity_check()  # Returns ["ok"] if healthy

# Clean up stale leases (crashed workers)
count = maint.cleanup_stale_leases(timeout_seconds=300)

# Get database statistics
stats = maint.get_database_stats()
print(f"Size: {stats['total_size_mb']:.2f} MB")
print(f"WAL: {stats['wal_size_mb']:.2f} MB")

# Combined optimization
result = maint.optimize(full=False)  # ANALYZE only
result = maint.optimize(full=True)   # ANALYZE + VACUUM
```

For detailed maintenance procedures, see:
- [Queue Maintenance Runbook](/_meta/docs/QUEUE_MAINTENANCE_RUNBOOK.md)
- [SQLite Queue Troubleshooting Guide](/_meta/docs/SQLITE_QUEUE_TROUBLESHOOTING.md)
## API Documentation

See [QUEUE_API.md](./QUEUE_API.md) for complete REST API documentation including:
- Enqueue task endpoint
- Task status polling
- Task cancellation
- Queue statistics
- Request/response examples
- Best practices

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
