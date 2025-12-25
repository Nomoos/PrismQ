# Worker Task Queue Database

This directory contains the database schema and management for the worker task queue system.

## Overview

The worker task queue database provides persistent storage for:
- Task queue management
- Worker health tracking
- Task execution history and audit logs
- Monitoring and statistics

## Architecture

### Database Schema

The schema consists of three main tables:

1. **task_queue**: Main task storage
   - Task type, parameters (JSON), priority (1-10)
   - Status tracking (queued, claimed, running, completed, failed, cancelled)
   - Worker assignment and claiming
   - Retry logic with configurable max retries
   - Timestamps for created, updated, completed

2. **worker_heartbeats**: Worker health monitoring
   - Worker ID and last heartbeat timestamp
   - Task processing statistics
   - Current task assignment
   - Worker strategy (FIFO, LIFO, PRIORITY)

3. **task_logs**: Audit trail
   - Task and worker events
   - Event types (created, claimed, started, progress, completed, failed, retry)
   - Detailed messages and structured data (JSON)

### Views

Three monitoring views are provided:
- `v_active_tasks`: Currently active tasks (queued, claimed, running)
- `v_worker_status`: Worker health and activity
- `v_task_stats`: Task statistics by type and status

### Indexes

Six indexes optimize performance:
- `idx_task_queue_claiming`: Critical for fast task claiming (<10ms)
- `idx_task_queue_worker`: Worker-based queries
- `idx_task_queue_created`: Time-based queries
- `idx_worker_heartbeat`: Finding stale workers
- `idx_task_logs_task`: Task history queries
- `idx_task_logs_worker`: Worker activity queries

## Configuration

The database is optimized for Windows with the following PRAGMA settings:

- **journal_mode = WAL**: Write-Ahead Logging for concurrent access
- **busy_timeout = 5000**: 5-second timeout for SQLITE_BUSY
- **synchronous = NORMAL**: Balance between safety and speed
- **cache_size = -10000**: 10MB cache
- **mmap_size = 30000000000**: 30GB memory-mapped I/O (for RTX 5090 system)
- **auto_vacuum = INCREMENTAL**: Space reclamation
- **temp_store = MEMORY**: In-memory temporary storage

## Usage

### Initialize Database

```bash
python scripts/init_queue_db.py
```

This creates the database at `data/worker_queue.db` with all tables, indexes, and views.

### Using in Python

```python
from workers.queue_database import QueueDatabase

# Initialize database
db = QueueDatabase('data/worker_queue.db')

# Get a connection
conn = db.get_connection()
cursor = conn.cursor()

# Insert a task
cursor.execute('''
    INSERT INTO task_queue 
    (task_type, parameters, priority, created_at, updated_at)
    VALUES (?, ?, ?, datetime('now'), datetime('now'))
''', ('channel_scrape', '{"channel_url": "..."}', 8))
conn.commit()

# Claim a task (simulated)
cursor.execute('''
    SELECT id FROM task_queue
    WHERE status = 'queued'
    ORDER BY priority DESC, created_at DESC
    LIMIT 1
''')
task = cursor.fetchone()

# Update task status
cursor.execute('''
    UPDATE task_queue
    SET status = 'claimed', claimed_by = ?, claimed_at = datetime('now')
    WHERE id = ?
''', ('worker-001', task['id']))
conn.commit()

conn.close()
```

### Monitoring

```python
# Get database statistics
stats = db.get_stats()
print(f"Active workers: {stats['active_workers']}")
print(f"Task counts: {stats['status_counts']}")
print(f"Database size: {stats['db_size_mb']} MB")

# Get PRAGMA settings
pragma_info = db.get_pragma_info()
print(f"Journal mode: {pragma_info['journal_mode']}")
```

### Maintenance

```python
# Perform WAL checkpoint
db.checkpoint()

# Vacuum database to reclaim space
db.vacuum()
# Workers Module

This module implements the worker base class and factory for the YouTube Shorts scraping system, following SOLID design principles.

## Overview

The workers module provides a foundational framework for implementing task-based workers that process jobs from a SQLite queue.

## Key Components

### WorkerProtocol
A Protocol (interface) defining the minimal contract that all workers must implement:
- `claim_task()` - Claim a task from the queue
- `process_task()` - Process the claimed task
- `report_result()` - Report the task result

### BaseWorker
An abstract base class providing common worker functionality:
- Atomic task claiming using SQLite IMMEDIATE transactions
- Support for LIFO, FIFO, and PRIORITY claiming strategies
- Heartbeat mechanism for worker health monitoring
- Task lifecycle management (claim → process → report)
- Error handling and logging

### WorkerFactory
A factory for creating worker instances:
- Register worker classes for different task types
- Create worker instances with dependency injection
- Follows Open/Closed Principle (extensible without modification)

## Usage Example

```python
from src.workers import Task, TaskResult, BaseWorker
from src.workers.factory import worker_factory

# 1. Define a custom worker
class MyWorker(BaseWorker):
    def process_task(self, task: Task) -> TaskResult:
        # Implement your scraping logic here
        data = scrape_data(task.parameters)
        return TaskResult(
            success=True,
            data=data,
            items_processed=len(data)
        )

# 2. Register the worker
worker_factory.register("my_task_type", MyWorker)

# 3. Create a worker instance
worker = worker_factory.create(
    task_type="my_task_type",
    worker_id="worker-1",
    queue_db_path="queue.db",
    config=config,
    results_db=results_db
)

# 4. Run the worker
worker.run(poll_interval=5)
```

## SOLID Principles

### Single Responsibility Principle (SRP)
- `BaseWorker` only handles task lifecycle management
- Task claiming, processing, and reporting are separate concerns
- Scraping logic is delegated to subclasses

### Open/Closed Principle (OCP)
- New worker types can be added without modifying existing code
- Factory registration allows extension without modification

### Liskov Substitution Principle (LSP)
- Any `BaseWorker` subclass can be used wherever `WorkerProtocol` is expected
- All workers follow the same lifecycle

### Interface Segregation Principle (ISP)
- `WorkerProtocol` defines only essential methods
- No client is forced to depend on methods it doesn't use

### Dependency Inversion Principle (DIP)
- Workers depend on abstractions (Config, Database)
- Dependencies are injected via constructor
- No direct coupling to concrete implementations

## Task Claiming Strategies

### LIFO (Last In, First Out) - Default
Claims the most recently added task first. Useful for processing the latest content.

### FIFO (First In, First Out)
Claims the oldest task first. Ensures fair processing order.

### PRIORITY
Claims tasks based on priority value (higher priority first). When priorities are equal, uses FIFO ordering.

## Database Schema

The workers module expects the following tables in the queue database:

```sql
CREATE TABLE task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    parameters TEXT,  -- JSON
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'queued',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TEXT NOT NULL,
    claimed_at TEXT,
    claimed_by TEXT,
    completed_at TEXT,
    updated_at TEXT,
    run_after_utc TEXT,
    result_data TEXT,  -- JSON
    error_message TEXT
);

CREATE TABLE worker_heartbeats (
    worker_id TEXT PRIMARY KEY,
    last_heartbeat TEXT NOT NULL,
    tasks_processed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0
);
```

## Testing

Run the test suite:

```bash
python -m pytest _meta/tests/test_queue_database.py -v
```

Tests cover:
- Database initialization
- Schema validation (tables, indexes, views)
- PRAGMA settings
- Constraints and foreign keys
- Performance requirements (<10ms for task claiming)
- Multiple connections
- Views functionality

## Performance

The schema is optimized for:
- **Fast task claiming**: <10ms requirement met (tested with 1000 tasks)
- **Concurrent access**: WAL mode allows simultaneous reads during writes
- **Windows optimization**: Proper PRAGMA settings for SSD and large RAM
- **Efficient queries**: Strategic indexes on frequently accessed columns

## SOLID Principles

The implementation follows SOLID principles:

- **Single Responsibility**: QueueDatabase class focuses only on DB setup and configuration
- **Open/Closed**: Schema can be extended via views and indexes without changes
- **Dependency Inversion**: Standard SQL interface allows switching databases later

## Files

- `schema.sql`: Complete database schema (tables, indexes, views)
- `queue_database.py`: QueueDatabase class for management
- `__init__.py`: Package initialization

## Related Issues

This implementation addresses Issue #004 from the YouTube Worker Refactor Master Plan (#001).

## License

Proprietary - PrismQ
The workers module includes comprehensive tests:
- `test_base_worker.py` - 23 tests for BaseWorker functionality
- `test_worker_factory.py` - 12 tests for WorkerFactory

Coverage:
- `__init__.py` - 100%
- `base_worker.py` - 90%
- `factory.py` - 100%

Run tests:
```bash
pytest _meta/tests/test_base_worker.py _meta/tests/test_worker_factory.py -v
```

## Configuration

Workers require the following configuration:
- `worker_id` - Unique identifier for this worker instance
- `queue_db_path` - Path to SQLite queue database
- `config` - Config object with application settings
- `results_db` - Database instance for storing results
- `strategy` - Task claiming strategy (LIFO, FIFO, PRIORITY)
- `heartbeat_interval` - Seconds between heartbeat updates

## Concurrency

The workers module uses SQLite's Write-Ahead Logging (WAL) mode for concurrent access:
- Multiple workers can read simultaneously
- Atomic task claiming prevents double-claiming
- IMMEDIATE transactions ensure consistency

## Error Handling

Workers handle errors gracefully:
- Exceptions in `process_task()` are caught and reported
- Failed tasks are marked with error messages
- Workers continue processing after errors
- Heartbeat failures are logged as warnings

## Future Enhancements

Planned improvements:
- Support for WEIGHTED_RANDOM claiming strategy
- Worker pool management
- Distributed worker coordination
- Advanced retry strategies with exponential backoff
- Task timeout handling
- Worker pause/resume functionality
