# SQLite Queue System - API Reference

**Version**: 1.0  
**Status**: Phase 1 Implementation  
**Created**: 2025-11-05  
**Last Updated**: 2025-11-05

---

## Table of Contents

- [Overview](#overview)
- [Core Classes](#core-classes)
  - [QueueDatabase](#queuedatabase)
  - [Task (Model)](#task-model)
  - [Worker (Model)](#worker-model)
  - [TaskLog (Model)](#tasklog-model)
- [Exceptions](#exceptions)
- [Usage Examples](#usage-examples)
- [Error Handling](#error-handling)

---

## Overview

The SQLite Queue System provides a simple, type-safe API for task queue operations. This document covers the **Phase 1** implementation (Core Infrastructure from Issue #321).

**Import Path**:
```python
from queue import QueueDatabase, Task, Worker, TaskLog
from queue import QueueDatabaseError, QueueBusyError, QueueSchemaError
```

**Module Structure**:
```
Client/Backend/src/queue/
├── database.py     # QueueDatabase class
├── models.py       # Task, Worker, TaskLog dataclasses
├── schema.py       # SQL schema constants
├── exceptions.py   # Custom exceptions
└── __init__.py     # Package exports
```

---

## Core Classes

### QueueDatabase

**Purpose**: Manage SQLite connection lifecycle and transactions

**Class Definition**:
```python
class QueueDatabase:
    """
    SQLite database connection manager for task queue.
    
    Follows SOLID principles:
    - Single Responsibility: Manages DB connection lifecycle
    - Dependency Inversion: Uses Protocol for extensibility
    - Open/Closed: Can be extended without modification
    
    Thread-safe connection management with proper transaction support.
    """
```

#### Constructor

```python
def __init__(self, db_path: Optional[str] = None) -> None:
    """
    Initialize database connection.
    
    Args:
        db_path: Path to database file. If None, uses default path.
                Default: C:\\Data\\PrismQ\\queue\\queue.db (Windows)
                        or /tmp/prismq/queue/queue.db (Linux/macOS)
    
    Environment Variables:
        PRISMQ_QUEUE_DB_PATH: Override default database path
    
    Examples:
        >>> # Use default path
        >>> db = QueueDatabase()
        
        >>> # Custom path
        >>> db = QueueDatabase("C:/custom/path/queue.db")
        
        >>> # Environment variable
        >>> import os
        >>> os.environ["PRISMQ_QUEUE_DB_PATH"] = "D:/data/queue.db"
        >>> db = QueueDatabase()  # Uses D:/data/queue.db
    """
```

#### Methods

##### initialize_schema()

```python
def initialize_schema(self) -> None:
    """
    Create tables and indexes if they don't exist.
    
    Creates:
        - task_queue table with indexes
        - workers table
        - task_logs table with indexes
    
    Raises:
        QueueSchemaError: If schema creation fails
    
    Examples:
        >>> db = QueueDatabase()
        >>> db.initialize_schema()
        >>> # Tables and indexes created
    
    Notes:
        - Safe to call multiple times (uses IF NOT EXISTS)
        - Automatically creates directory if needed
        - Applies all PRAGMA settings
    """
```

##### get_connection()

```python
def get_connection(self) -> sqlite3.Connection:
    """
    Get the active connection, creating it if necessary.
    
    Returns:
        sqlite3.Connection: Active connection with PRAGMAs applied
    
    Raises:
        QueueDatabaseError: If connection cannot be established
    
    Examples:
        >>> db = QueueDatabase()
        >>> conn = db.get_connection()
        >>> cursor = conn.execute("SELECT COUNT(*) FROM task_queue")
        >>> count = cursor.fetchone()[0]
    
    Notes:
        - Connection is reused (singleton pattern)
        - Thread-safe (uses RLock)
        - Row factory enabled (dict-like access)
    """
```

##### execute()

```python
def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
    """
    Execute a single SQL statement.
    
    Args:
        sql: SQL statement to execute
        params: Query parameters (prevents SQL injection)
    
    Returns:
        sqlite3.Cursor: Query result cursor
    
    Raises:
        QueueDatabaseError: If execution fails
        QueueBusyError: If database is locked (SQLITE_BUSY)
    
    Examples:
        >>> # Query tasks
        >>> cursor = db.execute(
        ...     "SELECT * FROM task_queue WHERE status = ?",
        ...     ("queued",)
        ... )
        >>> for row in cursor:
        ...     print(row['id'], row['type'])
        
        >>> # Insert task
        >>> db.execute(
        ...     "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
        ...     ("video_processing", '{"format": "mp4"}')
        ... )
    
    Security:
        - ALWAYS use parameterized queries
        - NEVER use string formatting (f-strings)
    """
```

##### execute_many()

```python
def execute_many(self, sql: str, param_list: List[tuple]) -> None:
    """
    Execute SQL with multiple parameter sets (batch operation).
    
    Args:
        sql: SQL statement to execute
        param_list: List of parameter tuples
    
    Raises:
        QueueDatabaseError: If execution fails
    
    Examples:
        >>> # Batch insert
        >>> tasks = [
        ...     ("task1", "{}"),
        ...     ("task2", "{}"),
        ...     ("task3", "{}"),
        ... ]
        >>> db.execute_many(
        ...     "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
        ...     tasks
        ... )
    
    Performance:
        - More efficient than individual execute() calls
        - Uses single transaction
    """
```

##### transaction()

```python
@contextmanager
def transaction(self) -> ContextManager[sqlite3.Connection]:
    """
    Context manager for transactions.
    
    Yields:
        sqlite3.Connection: Connection for transaction
    
    Raises:
        QueueDatabaseError: If transaction fails
    
    Examples:
        >>> # Atomic operation
        >>> with db.transaction() as conn:
        ...     conn.execute("INSERT INTO task_queue ...")
        ...     conn.execute("UPDATE workers ...")
        ... # Auto-commit on success
        
        >>> # Rollback on error
        >>> try:
        ...     with db.transaction() as conn:
        ...         conn.execute("INSERT ...")
        ...         raise ValueError("Error!")
        ... except ValueError:
        ...     pass  # Transaction rolled back
    
    Notes:
        - Uses BEGIN IMMEDIATE for atomic claiming
        - Auto-commit on success
        - Auto-rollback on exception
    """
```

##### close()

```python
def close(self) -> None:
    """
    Close database connection.
    
    Examples:
        >>> db = QueueDatabase()
        >>> db.initialize_schema()
        >>> # ... use database
        >>> db.close()
    
    Notes:
        - Safe to call multiple times
        - Thread-safe
        - WAL checkpoint performed
    """
```

#### Context Manager Support

```python
# QueueDatabase supports context manager protocol
with QueueDatabase() as db:
    db.initialize_schema()
    # ... use database
# Auto-closed on exit
```

---

### Task (Model)

**Purpose**: Represent a task in the queue

**Class Definition**:
```python
@dataclass
class Task:
    """
    Represents a task in the queue.
    
    Follows SOLID principles:
    - Single Responsibility: Represents task data only
    - Open/Closed: Can be extended without modification
    """
```

#### Fields

```python
id: Optional[int] = None                       # Autoincrement primary key
type: str = ""                                  # Task type (e.g., "video_processing")
priority: int = 100                             # Priority level (lower = higher priority)
payload: str = "{}"                             # JSON task data
compatibility: str = "{}"                       # JSON worker compatibility requirements

status: str = "queued"                          # Task status (queued, processing, completed, failed)
attempts: int = 0                               # Current attempt count
max_attempts: int = 5                           # Maximum retry attempts

run_after_utc: Optional[datetime] = None        # Earliest time to run
lease_until_utc: Optional[datetime] = None      # Lease expiration time
reserved_at_utc: Optional[datetime] = None      # When task was claimed
processing_started_utc: Optional[datetime] = None  # When processing began
finished_at_utc: Optional[datetime] = None      # When task completed/failed

locked_by: Optional[str] = None                 # Worker ID that claimed task
error_message: Optional[str] = None             # Last error message
idempotency_key: Optional[str] = None           # Unique key for duplicate detection

created_at_utc: Optional[datetime] = None       # Task creation time
updated_at_utc: Optional[datetime] = None       # Last update time
```

#### Methods

##### to_dict()

```python
def to_dict(self) -> Dict[str, Any]:
    """
    Convert task to dictionary representation.
    
    Returns:
        Dict with all task fields (datetimes as ISO strings)
    
    Examples:
        >>> task = Task(id=1, type="test", priority=50)
        >>> task_dict = task.to_dict()
        >>> print(task_dict["priority"])  # 50
    """
```

##### from_dict()

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Task":
    """
    Create Task from dictionary representation.
    
    Args:
        data: Dictionary with task fields
    
    Returns:
        Task instance
    
    Examples:
        >>> row = db.execute("SELECT * FROM task_queue WHERE id = 1").fetchone()
        >>> task = Task.from_dict(dict(row))
        >>> print(task.type, task.priority)
    
    Notes:
        - Handles both ISO format and SQLite datetime format
        - Provides defaults for missing fields
    """
```

##### get_payload_dict()

```python
def get_payload_dict(self) -> Dict[str, Any]:
    """
    Parse payload JSON to dictionary.
    
    Returns:
        Parsed payload as dictionary
    
    Examples:
        >>> task = Task(payload='{"format": "mp4", "quality": "hd"}')
        >>> payload = task.get_payload_dict()
        >>> print(payload["format"])  # "mp4"
    """
```

##### get_compatibility_dict()

```python
def get_compatibility_dict(self) -> Dict[str, Any]:
    """
    Parse compatibility JSON to dictionary.
    
    Returns:
        Parsed compatibility as dictionary
    
    Examples:
        >>> task = Task(compatibility='{"region": "us-west", "gpu": true}')
        >>> compat = task.get_compatibility_dict()
        >>> print(compat["region"])  # "us-west"
    """
```

#### Usage Examples

```python
# Create task
task = Task(
    type="video_processing",
    priority=50,
    payload='{"video_id": "abc123", "format": "mp4"}',
    compatibility='{"region": "us-west", "gpu": true}'
)

# Insert into database
with db.transaction() as conn:
    cursor = conn.execute("""
        INSERT INTO task_queue (type, priority, payload, compatibility)
        VALUES (?, ?, ?, ?)
    """, (task.type, task.priority, task.payload, task.compatibility))
    task.id = cursor.lastrowid

# Query task
cursor = db.execute("SELECT * FROM task_queue WHERE id = ?", (task.id,))
row = cursor.fetchone()
loaded_task = Task.from_dict(dict(row))

# Access payload
payload = loaded_task.get_payload_dict()
print(f"Processing video: {payload['video_id']}")
```

---

### Worker (Model)

**Purpose**: Represent a worker process

**Class Definition**:
```python
@dataclass
class Worker:
    """
    Represents a worker process.
    
    Workers register themselves and send heartbeats to indicate they're alive.
    """
```

#### Fields

```python
worker_id: str                                  # Unique worker identifier (e.g., "worker-01")
capabilities: str = "{}"                        # JSON worker capabilities
heartbeat_utc: Optional[datetime] = None        # Last heartbeat timestamp
```

#### Methods

##### to_dict()

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert worker to dictionary representation."""
```

##### from_dict()

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Worker":
    """Create Worker from dictionary representation."""
```

##### get_capabilities_dict()

```python
def get_capabilities_dict(self) -> Dict[str, Any]:
    """Parse capabilities JSON to dictionary."""
```

#### Usage Examples

```python
# Register worker
worker = Worker(
    worker_id="worker-01",
    capabilities='{"region": "us-west", "gpu": true, "max_memory_gb": 32}'
)

with db.transaction() as conn:
    conn.execute("""
        INSERT OR REPLACE INTO workers (worker_id, capabilities, heartbeat_utc)
        VALUES (?, ?, datetime('now'))
    """, (worker.worker_id, worker.capabilities))

# Update heartbeat
db.execute("""
    UPDATE workers
    SET heartbeat_utc = datetime('now')
    WHERE worker_id = ?
""", (worker.worker_id,))

# Check worker capabilities
caps = worker.get_capabilities_dict()
if caps.get("gpu"):
    print("Worker has GPU support")
```

---

### TaskLog (Model)

**Purpose**: Represent a task execution log entry

**Class Definition**:
```python
@dataclass
class TaskLog:
    """
    Represents a log entry for task execution.
    
    Used for debugging and monitoring.
    """
```

#### Fields

```python
log_id: Optional[int] = None                    # Autoincrement primary key
task_id: int = 0                                # Foreign key to task_queue
at_utc: Optional[datetime] = None               # Log timestamp
level: str = "INFO"                             # Log level (INFO, WARNING, ERROR)
message: Optional[str] = None                   # Short log message
details: Optional[str] = None                   # Additional JSON details
```

#### Methods

##### to_dict()

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert log to dictionary representation."""
```

##### from_dict()

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "TaskLog":
    """Create TaskLog from dictionary representation."""
```

#### Usage Examples

```python
# Create log entry
log = TaskLog(
    task_id=123,
    level="INFO",
    message="Started processing",
    details='{"step": "download", "progress": 0.0}'
)

with db.transaction() as conn:
    conn.execute("""
        INSERT INTO task_logs (task_id, level, message, details)
        VALUES (?, ?, ?, ?)
    """, (log.task_id, log.level, log.message, log.details))

# Query logs for task
cursor = db.execute("""
    SELECT * FROM task_logs
    WHERE task_id = ?
    ORDER BY at_utc ASC
""", (123,))

for row in cursor:
    log = TaskLog.from_dict(dict(row))
    print(f"[{log.level}] {log.message}")
```

---

## Exceptions

### QueueDatabaseError

**Purpose**: Base exception for all queue database errors

```python
class QueueDatabaseError(Exception):
    """Base exception for queue database errors."""
```

**Usage**:
```python
try:
    db = QueueDatabase()
    db.initialize_schema()
except QueueDatabaseError as e:
    logger.error(f"Database error: {e}")
```

### QueueBusyError

**Purpose**: Raised when database is locked (SQLITE_BUSY)

```python
class QueueBusyError(QueueDatabaseError):
    """Raised when database is locked (SQLITE_BUSY)."""
```

**Usage**:
```python
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        with db.transaction() as conn:
            conn.execute("INSERT ...")
        break  # Success
    except QueueBusyError:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise  # Give up after max retries
```

### QueueSchemaError

**Purpose**: Raised when schema operation fails

```python
class QueueSchemaError(QueueDatabaseError):
    """Raised when schema operation fails."""
```

**Usage**:
```python
try:
    db.initialize_schema()
except QueueSchemaError as e:
    logger.error(f"Schema creation failed: {e}")
    # Check disk space, permissions, etc.
```

---

## Usage Examples

### Basic Usage

```python
from queue import QueueDatabase, Task

# 1. Create database
db = QueueDatabase()
db.initialize_schema()

# 2. Insert task
with db.transaction() as conn:
    cursor = conn.execute("""
        INSERT INTO task_queue (type, payload, priority)
        VALUES (?, ?, ?)
    """, ("video_processing", '{"video_id": "abc123"}', 50))
    task_id = cursor.lastrowid
    print(f"Created task {task_id}")

# 3. Query tasks
cursor = db.execute("""
    SELECT * FROM task_queue
    WHERE status = 'queued'
    ORDER BY priority ASC
    LIMIT 10
""")

for row in cursor:
    task = Task.from_dict(dict(row))
    print(f"Task {task.id}: {task.type} (priority {task.priority})")

# 4. Close connection
db.close()
```

### Atomic Task Claiming

```python
# Worker claims next task atomically
worker_id = "worker-01"

with db.transaction() as conn:
    # Step 1: Find next task
    cursor = conn.execute("""
        SELECT * FROM task_queue
        WHERE status = 'queued'
          AND run_after_utc <= datetime('now')
        ORDER BY priority ASC, run_after_utc ASC
        LIMIT 1
    """)
    row = cursor.fetchone()
    
    if row:
        task = Task.from_dict(dict(row))
        
        # Step 2: Claim task with lease
        conn.execute("""
            UPDATE task_queue
            SET status = 'processing',
                locked_by = ?,
                lease_until_utc = datetime('now', '+5 minutes'),
                reserved_at_utc = datetime('now'),
                processing_started_utc = datetime('now')
            WHERE id = ?
        """, (worker_id, task.id))
        
        print(f"Claimed task {task.id}")
```

### Batch Operations

```python
# Enqueue multiple tasks efficiently
tasks = [
    ("task1", '{"data": "A"}', 100),
    ("task2", '{"data": "B"}', 50),
    ("task3", '{"data": "C"}', 75),
]

db.execute_many("""
    INSERT INTO task_queue (type, payload, priority)
    VALUES (?, ?, ?)
""", tasks)

print(f"Enqueued {len(tasks)} tasks")
```

### Context Manager Pattern

```python
# Automatic resource cleanup
with QueueDatabase() as db:
    db.initialize_schema()
    
    # Insert tasks
    with db.transaction() as conn:
        conn.execute("INSERT INTO task_queue ...")
    
    # Query tasks
    cursor = db.execute("SELECT * FROM task_queue")
    for row in cursor:
        print(row['id'])
# Database automatically closed
```

---

## Error Handling

### Common Patterns

#### Retry on SQLITE_BUSY

```python
import time

def execute_with_retry(db, sql, params, max_retries=3):
    """Execute SQL with exponential backoff on SQLITE_BUSY."""
    for attempt in range(max_retries):
        try:
            return db.execute(sql, params)
        except QueueBusyError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait_time)
            else:
                raise  # Give up
```

#### Graceful Degradation

```python
from queue import QueueDatabaseError

def enqueue_task_safe(db, task_type, payload):
    """Enqueue task with fallback to in-memory queue."""
    try:
        with db.transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO task_queue (type, payload)
                VALUES (?, ?)
            """, (task_type, payload))
            return cursor.lastrowid
    except QueueDatabaseError as e:
        logger.warning(f"Queue unavailable: {e}, using in-memory fallback")
        # Fallback to BackgroundTaskManager
        return fallback_queue.enqueue(task_type, payload)
```

#### Logging and Monitoring

```python
import logging

logger = logging.getLogger(__name__)

def claim_task_with_logging(db, worker_id):
    """Claim task with detailed logging."""
    try:
        with db.transaction() as conn:
            # Claim logic...
            logger.info(f"Worker {worker_id} claimed task {task_id}")
            return task
    except QueueBusyError:
        logger.warning(f"Worker {worker_id}: Database busy, retrying...")
        raise
    except QueueDatabaseError as e:
        logger.error(f"Worker {worker_id}: Database error: {e}")
        raise
```

---

## Best Practices

### 1. Always Use Parameterized Queries

```python
# ✅ Good - Safe from SQL injection
db.execute("SELECT * FROM task_queue WHERE type = ?", (task_type,))

# ❌ Bad - Vulnerable to SQL injection
db.execute(f"SELECT * FROM task_queue WHERE type = '{task_type}'")
```

### 2. Use Context Managers

```python
# ✅ Good - Automatic cleanup
with db.transaction() as conn:
    conn.execute("INSERT ...")

# ❌ Bad - Manual commit/rollback
conn = db.get_connection()
conn.execute("BEGIN")
conn.execute("INSERT ...")
conn.commit()  # What if exception happens?
```

### 3. Handle Errors Appropriately

```python
# ✅ Good - Specific error handling
try:
    db.initialize_schema()
except QueueBusyError:
    # Retry logic
    pass
except QueueSchemaError:
    # Schema-specific handling
    pass
except QueueDatabaseError:
    # General fallback
    pass
```

### 4. Use Batch Operations

```python
# ✅ Good - Efficient batch insert
db.execute_many("INSERT INTO task_queue ...", tasks)

# ❌ Bad - Individual inserts
for task in tasks:
    db.execute("INSERT INTO task_queue ...", task)
```

---

## Performance Tips

### Connection Reuse

```python
# ✅ Good - Reuse connection
db = QueueDatabase()
for i in range(1000):
    db.execute("INSERT ...")
db.close()

# ❌ Bad - Create new connection each time
for i in range(1000):
    with QueueDatabase() as db:
        db.execute("INSERT ...")
```

### Index Usage

```python
# ✅ Good - Uses ix_task_status_prio_time index
db.execute("""
    SELECT * FROM task_queue
    WHERE status = 'queued'
    ORDER BY priority ASC, run_after_utc ASC
    LIMIT 1
""")

# ❌ Bad - No index, full table scan
db.execute("""
    SELECT * FROM task_queue
    WHERE payload LIKE '%video%'
""")
```

### Batch Queries

```python
# ✅ Good - Single query
cursor = db.execute("SELECT * FROM task_queue WHERE id IN (?, ?, ?)", (1, 2, 3))

# ❌ Bad - Multiple queries
for task_id in [1, 2, 3]:
    cursor = db.execute("SELECT * FROM task_queue WHERE id = ?", (task_id,))
```

---

## Future API (Phase 2-3)

The following APIs will be added in future phases:

### QueueClient (Issue #323)

```python
class QueueClient:
    def enqueue(self, type: str, payload: dict, priority: int = 100) -> int
    def get_status(self, task_id: int) -> Task
    def cancel(self, task_id: int) -> bool
```

### QueueWorker (Issue #325)

```python
class QueueWorker:
    def claim_next_task(self) -> Optional[Task]
    def complete_task(self, task_id: int, result: dict) -> None
    def fail_task(self, task_id: int, error: str) -> None
    def renew_lease(self, task_id: int) -> None
```

### SchedulingStrategy (Issue #327)

```python
class FIFOStrategy:
    def get_next_task_sql(self) -> str

class LIFOStrategy:
    def get_next_task_sql(self) -> str

class PriorityStrategy:
    def get_next_task_sql(self) -> str

class WeightedRandomStrategy:
    def get_next_task_sql(self) -> str
```

---

**Document Version**: 1.0  
**Phase**: Phase 1 - Core Infrastructure  
**Status**: Complete  
**Next**: Update with #323-#332 implementations
