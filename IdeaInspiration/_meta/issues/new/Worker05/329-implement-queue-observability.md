# Issue #329: Implement Queue Observability

**Parent Issue**: #320 (SQLite Queue Analysis)  
**Worker**: Worker 05 - DevOps/Monitoring Engineer  
**Status**: New  
**Priority**: High  
**Duration**: 3-5 days  
**Dependencies**: #321 (Core Infrastructure) - ✅ Complete

---

## Objective

Implement comprehensive observability infrastructure for the SQLite task queue, including task logging, metrics collection, dashboard-ready SQL views, and integration with the existing logging system.

---

## Requirements

### 1. Task Logging Implementation

#### TaskLogger Class
Create a `TaskLogger` class to manage task-level logging:

```python
class TaskLogger:
    """
    Manages task-level logging to the task_logs table.
    
    Follows SOLID principles:
    - Single Responsibility: Handles task log persistence
    - Dependency Inversion: Depends on QueueDatabase abstraction
    - Open/Closed: Extensible without modification
    """
    
    def __init__(self, db: QueueDatabase):
        """Initialize with database connection."""
        
    def log(
        self,
        task_id: int,
        level: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a task event to task_logs table.
        
        Args:
            task_id: ID of the task
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            details: Optional additional details as JSON
        """
        
    def get_task_logs(
        self,
        task_id: int,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[TaskLog]:
        """
        Retrieve logs for a specific task.
        
        Args:
            task_id: ID of the task
            level: Filter by log level (optional)
            limit: Maximum number of logs to retrieve
            
        Returns:
            List of TaskLog objects ordered by timestamp (newest first)
        """
```

#### Integration Points
- Automatically log task state transitions (queued → claimed → processing → completed/failed)
- Log errors with full stack traces
- Log retry attempts with exponential backoff details
- Log lease renewals for long-running tasks

---

### 2. Queue Metrics Collection

#### QueueMetrics Class
Create a `QueueMetrics` class for real-time metrics:

```python
class QueueMetrics:
    """
    Provides real-time queue metrics and statistics.
    
    Follows SOLID principles:
    - Single Responsibility: Aggregates queue metrics
    - Dependency Inversion: Depends on QueueDatabase abstraction
    """
    
    def __init__(self, db: QueueDatabase):
        """Initialize with database connection."""
        
    def get_queue_depth(
        self,
        task_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Get number of tasks in queue.
        
        Args:
            task_type: Filter by task type (optional)
            status: Filter by status (optional)
            
        Returns:
            Count of matching tasks
        """
        
    def get_queue_depth_by_status(self) -> Dict[str, int]:
        """
        Get task counts grouped by status.
        
        Returns:
            Dict mapping status -> count
            Example: {'queued': 50, 'processing': 5, 'completed': 200}
        """
        
    def get_queue_depth_by_type(self) -> Dict[str, int]:
        """
        Get task counts grouped by type.
        
        Returns:
            Dict mapping task type -> count
        """
        
    def get_oldest_queued_task_age(self) -> Optional[int]:
        """
        Get age in seconds of the oldest queued task.
        
        Returns:
            Age in seconds, or None if queue is empty
        """
        
    def get_success_failure_rates(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Calculate success/failure rates over time period.
        
        Args:
            hours: Time period in hours (default: 24)
            
        Returns:
            Dict with success_count, failure_count, success_rate, failure_rate
        """
        
    def get_worker_activity(self) -> List[Dict[str, Any]]:
        """
        Get current worker activity and heartbeats.
        
        Returns:
            List of worker info with capabilities, heartbeat, active tasks
        """
        
    def get_throughput_metrics(
        self,
        hours: int = 1
    ) -> Dict[str, float]:
        """
        Calculate throughput metrics.
        
        Args:
            hours: Time period in hours
            
        Returns:
            Dict with tasks_completed, tasks_per_minute, avg_processing_time_seconds
        """
```

#### Key Metrics
- **Queue Depth**: Total tasks by status (queued, processing, completed, failed, dead_letter)
- **Task Age**: Age of oldest queued task (queue lag indicator)
- **Success/Failure Rates**: Completed vs failed tasks over time period
- **Worker Activity**: Active workers, heartbeats, assigned tasks
- **Throughput**: Tasks completed per minute
- **Processing Time**: Average, p50, p95, p99 processing durations
- **Retry Rate**: Tasks requiring retries vs first-time successes
- **Dead Letter Rate**: Tasks reaching max_attempts

---

### 3. Dashboard-Ready SQL Views

Create SQL views for easy dashboard integration:

#### View: `v_queue_status_summary`
```sql
CREATE VIEW IF NOT EXISTS v_queue_status_summary AS
SELECT
    status,
    COUNT(*) as task_count,
    AVG(attempts) as avg_attempts,
    MIN(created_at_utc) as oldest_task,
    MAX(created_at_utc) as newest_task
FROM task_queue
GROUP BY status;
```

#### View: `v_queue_type_summary`
```sql
CREATE VIEW IF NOT EXISTS v_queue_type_summary AS
SELECT
    type,
    status,
    COUNT(*) as task_count,
    AVG(priority) as avg_priority
FROM task_queue
GROUP BY type, status;
```

#### View: `v_worker_status`
```sql
CREATE VIEW IF NOT EXISTS v_worker_status AS
SELECT
    w.worker_id,
    w.capabilities,
    w.heartbeat_utc,
    COUNT(t.id) as active_tasks,
    ROUND((JULIANDAY('now') - JULIANDAY(w.heartbeat_utc)) * 86400) as seconds_since_heartbeat
FROM workers w
LEFT JOIN task_queue t ON t.locked_by = w.worker_id AND t.status = 'processing'
GROUP BY w.worker_id;
```

#### View: `v_task_performance`
```sql
CREATE VIEW IF NOT EXISTS v_task_performance AS
SELECT
    type,
    status,
    COUNT(*) as task_count,
    AVG(JULIANDAY(finished_at_utc) - JULIANDAY(processing_started_utc)) * 86400 as avg_processing_seconds,
    AVG(attempts) as avg_attempts
FROM task_queue
WHERE finished_at_utc IS NOT NULL
GROUP BY type, status;
```

#### View: `v_recent_failures`
```sql
CREATE VIEW IF NOT EXISTS v_recent_failures AS
SELECT
    id,
    type,
    status,
    attempts,
    error_message,
    finished_at_utc
FROM task_queue
WHERE status IN ('failed', 'dead_letter')
ORDER BY finished_at_utc DESC
LIMIT 100;
```

---

### 4. Integration with Existing Logging System

#### Logger Integration
Integrate queue observability with existing `Client/Backend/src/core/logger.py`:

```python
import logging
from typing import Optional
from .logger import setup_logging

class QueueLogger:
    """
    Integrates queue logging with application logging.
    
    Bridges task_logs database persistence with standard Python logging.
    """
    
    def __init__(self, db: QueueDatabase, app_logger: Optional[logging.Logger] = None):
        """
        Initialize with database and optional application logger.
        
        Args:
            db: QueueDatabase instance
            app_logger: Optional logger, defaults to queue logger
        """
        self.task_logger = TaskLogger(db)
        self.app_logger = app_logger or logging.getLogger("prismq.queue")
        
    def log_task_event(
        self,
        task_id: int,
        level: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log task event to both database and application logs.
        
        Args:
            task_id: Task ID
            level: Log level
            message: Log message
            details: Optional details
        """
        # Log to database
        self.task_logger.log(task_id, level, message, details)
        
        # Log to application logger
        log_method = getattr(self.app_logger, level.lower(), self.app_logger.info)
        log_method(f"Task {task_id}: {message}", extra={"task_id": task_id, "details": details})
```

#### Structured Logging
Enhance log messages with contextual information:
- Task ID
- Task type
- Worker ID
- Attempt number
- Processing duration
- Error details

---

### 5. Worker Heartbeat and Monitoring

#### Heartbeat Mechanism
```python
class WorkerHeartbeat:
    """
    Manages worker heartbeat updates and monitoring.
    
    Detects stale workers and enables worker health monitoring.
    """
    
    def __init__(self, db: QueueDatabase, stale_threshold_seconds: int = 300):
        """
        Initialize heartbeat manager.
        
        Args:
            db: QueueDatabase instance
            stale_threshold_seconds: Seconds before worker considered stale (default: 5 minutes)
        """
        
    def update_heartbeat(self, worker_id: str, capabilities: Dict[str, Any]) -> None:
        """
        Update or create worker heartbeat.
        
        Args:
            worker_id: Unique worker identifier
            capabilities: Worker capabilities as dict
        """
        
    def get_active_workers(self) -> List[Worker]:
        """
        Get list of active workers (recent heartbeat).
        
        Returns:
            List of Worker objects with recent heartbeat
        """
        
    def get_stale_workers(self) -> List[Worker]:
        """
        Get list of stale workers (no recent heartbeat).
        
        Returns:
            List of Worker objects with stale heartbeat
        """
        
    def cleanup_stale_workers(self) -> int:
        """
        Remove stale workers from registry.
        
        Returns:
            Number of workers removed
        """
```

---

## Implementation Details

### File Structure
```
Client/Backend/src/queue/
├── __init__.py              # Export public classes
├── database.py              # QueueDatabase (existing)
├── models.py                # Task, Worker, TaskLog (existing)
├── schema.py                # Schema + Views (update)
├── logger.py                # NEW: TaskLogger, QueueLogger
├── metrics.py               # NEW: QueueMetrics
├── heartbeat.py             # NEW: WorkerHeartbeat
└── views.py                 # NEW: SQL view definitions
```

### Testing
```
Client/_meta/tests/Backend/queue/
├── test_queue_database.py   # (existing)
├── test_logger.py            # NEW: TaskLogger, QueueLogger tests
├── test_metrics.py           # NEW: QueueMetrics tests
├── test_heartbeat.py         # NEW: WorkerHeartbeat tests
└── test_views.py             # NEW: SQL view tests
```

---

## Success Criteria

- [x] Issue document created
- [ ] `TaskLogger` class implemented with full logging functionality
- [ ] `QueueMetrics` class providing all key metrics
- [ ] SQL views created for dashboard integration
- [ ] `QueueLogger` integrating with existing logging system
- [ ] `WorkerHeartbeat` for worker health monitoring
- [ ] Unit tests with >80% coverage
- [ ] Integration tests with database
- [ ] Documentation updated with observability guide
- [ ] Example usage and dashboard queries documented

---

## Technical Requirements

### Performance
- Minimal overhead: <1ms for log writes
- Efficient metrics queries using indexes
- Views should leverage existing indexes
- Async logging for high-throughput scenarios

### Compatibility
- Windows 10/11 optimized
- Python 3.10.x compatible
- Thread-safe operations
- Works with SQLite WAL mode

### Best Practices
- Follow SOLID principles
- Type hints on all functions
- Comprehensive docstrings
- Error handling and logging
- Graceful degradation

---

## Documentation Requirements

### API Documentation
- Docstrings for all public classes and methods
- Type hints for parameters and return values
- Usage examples in docstrings

### Observability Guide
Create `_meta/docs/QUEUE_OBSERVABILITY.md` with:
- Overview of observability features
- How to use TaskLogger and QueueMetrics
- SQL view reference
- Dashboard integration examples
- Monitoring best practices
- Troubleshooting guide

### Example Queries
Document common queries:
- Queue health check
- Performance bottleneck detection
- Worker status monitoring
- Error rate tracking
- Throughput analysis

---

## Integration Examples

### Basic Usage
```python
from src.queue import QueueDatabase, TaskLogger, QueueMetrics

# Initialize
db = QueueDatabase()
logger = TaskLogger(db)
metrics = QueueMetrics(db)

# Log task event
logger.log(task_id=123, level="INFO", message="Task started processing")

# Get metrics
queue_depth = metrics.get_queue_depth(status="queued")
success_rate = metrics.get_success_failure_rates(hours=24)
oldest_task_age = metrics.get_oldest_queued_task_age()

print(f"Queue depth: {queue_depth}")
print(f"Success rate: {success_rate['success_rate']:.2%}")
print(f"Oldest task age: {oldest_task_age}s")
```

### Dashboard Queries
```python
# Get queue status summary
conn = db.get_connection()
cursor = conn.execute("SELECT * FROM v_queue_status_summary")
status_summary = [dict(row) for row in cursor.fetchall()]

# Get worker health
cursor = conn.execute("""
    SELECT * FROM v_worker_status 
    WHERE seconds_since_heartbeat < 300
    ORDER BY active_tasks DESC
""")
active_workers = [dict(row) for row in cursor.fetchall()]
```

---

## Related Issues

- #321: Core Infrastructure (✅ Complete - Dependency)
- #330: Worker Heartbeat and Monitoring (Covered in this issue)
- #323: Client API (Future - Will use these metrics)
- #325: Worker Engine (Future - Will use TaskLogger)
- #335: Documentation (Will document observability features)

---

## Timeline

### Day 1-2: Core Implementation
- [ ] Create `logger.py` with TaskLogger
- [ ] Create `metrics.py` with QueueMetrics
- [ ] Create `heartbeat.py` with WorkerHeartbeat
- [ ] Update `schema.py` with SQL views

### Day 3: Integration
- [ ] Create `QueueLogger` for integration with app logging
- [ ] Update `__init__.py` exports
- [ ] Test integration with existing queue code

### Day 4: Testing
- [ ] Write unit tests for all new classes
- [ ] Integration tests with database
- [ ] Performance benchmarking
- [ ] Windows-specific testing

### Day 5: Documentation
- [ ] Complete docstrings
- [ ] Create observability guide
- [ ] Document example queries
- [ ] Update README

---

## Notes

- Task logs table (`task_logs`) already exists in schema from #321
- Workers table exists for heartbeat tracking
- Existing logging system in `Client/Backend/src/core/logger.py` should be integrated
- Focus on performance: use indexes, avoid N+1 queries
- Make views materialized if needed for large datasets
- Consider log rotation/cleanup for task_logs table

---

**Status**: New - Ready to Start  
**Created**: 2025-11-05  
**Last Updated**: 2025-11-05
