# Issue #321: Implement SQLite Queue Core Infrastructure

**Parent Issue**: #320 (SQLite Queue Analysis)  
**Worker**: Worker 01 - Backend Engineer  
**Status**: New  
**Priority**: High  
**Duration**: 1-2 weeks  
**Dependencies**: None - Can start immediately

---

## Objective

Implement the foundational SQLite database infrastructure for the PrismQ task queue, including schema creation, connection management, transaction handling, and Windows-optimized configuration.

---

## Requirements

### 1. Database Schema Implementation

Create the following tables with proper indexes:

#### `task_queue` Table
```sql
CREATE TABLE IF NOT EXISTS task_queue (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  type               TEXT NOT NULL,
  priority           INTEGER NOT NULL DEFAULT 100,
  payload            TEXT NOT NULL,
  compatibility      TEXT NOT NULL DEFAULT '{}',
  
  status             TEXT NOT NULL DEFAULT 'queued',
  attempts           INTEGER NOT NULL DEFAULT 0,
  max_attempts       INTEGER NOT NULL DEFAULT 5,
  
  run_after_utc      DATETIME NOT NULL DEFAULT (datetime('now')),
  lease_until_utc    DATETIME,
  reserved_at_utc    DATETIME,
  processing_started_utc DATETIME,
  finished_at_utc    DATETIME,
  
  locked_by          TEXT,
  error_message      TEXT,
  idempotency_key    TEXT,
  
  created_at_utc     DATETIME NOT NULL DEFAULT (datetime('now')),
  updated_at_utc     DATETIME NOT NULL DEFAULT (datetime('now')),
  
  -- Generated columns for JSON filtering
  -- region: from compatibility (worker matching), format: from payload (task data)
  region             TEXT GENERATED ALWAYS AS (json_extract(compatibility, '$.region')) VIRTUAL,
  format             TEXT GENERATED ALWAYS AS (json_extract(payload, '$.format')) VIRTUAL
);
```

#### Indexes
```sql
CREATE INDEX IF NOT EXISTS ix_task_status_prio_time
  ON task_queue (status, priority, run_after_utc, id);

CREATE INDEX IF NOT EXISTS ix_task_type_status
  ON task_queue (type, status);

CREATE INDEX IF NOT EXISTS ix_task_region 
  ON task_queue (region);

CREATE INDEX IF NOT EXISTS ix_task_format 
  ON task_queue (format);

CREATE UNIQUE INDEX IF NOT EXISTS uq_task_idempotency
  ON task_queue (idempotency_key)
  WHERE idempotency_key IS NOT NULL;
```

#### `workers` Table
```sql
CREATE TABLE IF NOT EXISTS workers (
  worker_id      TEXT PRIMARY KEY,
  capabilities   TEXT NOT NULL,
  heartbeat_utc  DATETIME NOT NULL DEFAULT (datetime('now'))
);
```

#### `task_logs` Table
```sql
CREATE TABLE IF NOT EXISTS task_logs (
  log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id    INTEGER NOT NULL,
  at_utc     DATETIME NOT NULL DEFAULT (datetime('now')),
  level      TEXT NOT NULL,
  message    TEXT,
  details    TEXT,
  FOREIGN KEY (task_id) REFERENCES task_queue(id)
);

CREATE INDEX IF NOT EXISTS ix_logs_task 
  ON task_logs (task_id, at_utc);
```

### 2. Windows-Optimized PRAGMAs

Implement initialization function that sets:

```python
PRAGMAS = {
    'journal_mode': 'WAL',           # Enable WAL for concurrency
    'synchronous': 'NORMAL',         # Balance durability vs performance
    'busy_timeout': 5000,            # 5 seconds for lock retries
    'wal_autocheckpoint': 1000,      # Checkpoint every 1000 pages
    'foreign_keys': 'ON',            # Enable FK constraints
    'temp_store': 'MEMORY',          # Temp tables in memory
    'mmap_size': 134217728,          # 128MB memory-mapped I/O
    'page_size': 4096,               # Match filesystem block size
    'cache_size': -20000,            # ~20MB cache (negative = KiB, kibibytes)
}
```

### 3. Connection Management

#### Requirements
- Single connection per process with optional pooling
- Proper initialization of PRAGMAs on connection
- Context manager support for transactions
- Thread-safe operations
- Graceful connection closing

#### API Design
```python
class QueueDatabase:
    """
    SQLite database connection manager for task queue.
    
    Follows SOLID principles:
    - Single Responsibility: Manages DB connection lifecycle
    - Dependency Inversion: Uses Protocol for extensibility
    """
    
    def __init__(self, db_path: str):
        """Initialize database connection."""
        
    def initialize_schema(self) -> None:
        """Create tables and indexes if they don't exist."""
        
    def get_connection(self) -> sqlite3.Connection:
        """Get the active connection."""
        
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single SQL statement."""
        
    def execute_many(self, sql: str, param_list: List[tuple]) -> None:
        """Execute SQL with multiple parameter sets."""
        
    def transaction(self) -> ContextManager:
        """Context manager for transactions."""
        
    def close(self) -> None:
        """Close database connection."""
```

### 4. Transaction Handling

Implement transaction utilities:

```python
@contextmanager
def immediate_transaction(conn: sqlite3.Connection):
    """
    Context manager for IMMEDIATE transactions.
    
    Ensures atomic operations for task claiming.
    """
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
```

### 5. Database Location

- **Default Path**: `C:\Data\PrismQ\queue\queue.db` (Windows)
- **Configurable**: Via environment variable `PRISMQ_QUEUE_DB_PATH`
- **Auto-create**: Directory if it doesn't exist
- **Validation**: Ensure path is on local SSD, not network share

---

## Technical Specifications

### Technology Stack
- **Python**: 3.10.x (project requirement)
- **Library**: `sqlite3` (standard library, no dependencies)
- **Optional**: `aiosqlite` for async support (future)

### File Structure
```
Client/Backend/src/queue/
├── __init__.py
├── database.py          # QueueDatabase class
├── schema.py            # Schema constants and SQL
├── models.py            # Task, Worker, TaskLog dataclasses
└── exceptions.py        # Custom exceptions
```

### Error Handling
```python
class QueueDatabaseError(Exception):
    """Base exception for queue database errors."""

class QueueBusyError(QueueDatabaseError):
    """Raised when database is locked (SQLITE_BUSY)."""
    
class QueueSchemaError(QueueDatabaseError):
    """Raised when schema operation fails."""
```

---

## Implementation Steps

### Step 1: Create Module Structure (Day 1)
- [ ] Create `Client/Backend/src/queue/` directory
- [ ] Create `__init__.py`, `database.py`, `schema.py`, `models.py`, `exceptions.py`
- [ ] Add module to `pyproject.toml` dependencies

### Step 2: Implement Schema (Day 1-2)
- [ ] Define SQL constants in `schema.py`
- [ ] Implement `initialize_schema()` method
- [ ] Create schema migration utilities
- [ ] Test schema creation on Windows

### Step 3: Connection Management (Day 2-3)
- [ ] Implement `QueueDatabase` class
- [ ] Add PRAGMA initialization
- [ ] Implement connection pooling (if needed)
- [ ] Add thread-safety mechanisms

### Step 4: Transaction Support (Day 3-4)
- [ ] Implement `immediate_transaction()` context manager
- [ ] Add transaction helpers
- [ ] Test concurrent transactions

### Step 5: Data Models (Day 4-5)
- [ ] Create Task dataclass with validation
- [ ] Create Worker dataclass
- [ ] Create TaskLog dataclass
- [ ] Add serialization methods (to_dict, from_dict)

### Step 6: Testing (Day 6-8)
- [ ] Unit tests for database initialization
- [ ] Unit tests for schema creation
- [ ] Unit tests for connection management
- [ ] Integration tests for transactions
- [ ] Windows-specific tests

### Step 7: Documentation (Day 9-10)
- [ ] API documentation in docstrings
- [ ] Usage examples
- [ ] Configuration guide
- [ ] Windows deployment notes

---

## Testing Requirements

### Unit Tests
```python
def test_database_initialization():
    """Test database file creation and PRAGMA setup."""

def test_schema_creation():
    """Test all tables and indexes are created."""

def test_connection_reuse():
    """Test connection is reused properly."""

def test_transaction_commit():
    """Test transaction commits successfully."""

def test_transaction_rollback():
    """Test transaction rolls back on error."""

def test_sqlite_busy_handling():
    """Test SQLITE_BUSY error handling with timeout."""
```

### Integration Tests
```python
def test_concurrent_transactions():
    """Test multiple threads can access database safely."""

def test_windows_file_locking():
    """Test file locking behaves correctly on Windows."""

def test_wal_checkpoint():
    """Test WAL checkpointing doesn't block operations."""
```

### Performance Tests
```python
def test_insert_throughput():
    """Measure task insertion rate."""

def test_query_performance():
    """Measure task query performance with indexes."""
```

---

## Acceptance Criteria

- [ ] SQLite database created at configured path
- [ ] All tables (task_queue, workers, task_logs) exist with proper schema
- [ ] All indexes created for performance
- [ ] PRAGMAs applied correctly on connection
- [ ] Connection can be reused across operations
- [ ] Transactions work with IMMEDIATE isolation
- [ ] Thread-safe operations verified
- [ ] SQLITE_BUSY errors handled gracefully
- [ ] Works on Windows 10/11 with local SSD
- [ ] All tests passing with >80% coverage
- [ ] Documentation complete

---

## Integration Points

### Depends On
- None (foundational component)

### Used By
- Worker 02: Client API (#323) - for enqueue operations
- Worker 03: Worker Engine (#325) - for task claiming
- Worker 04: Scheduling (#327) - for different claim strategies
- Worker 05: Observability (#329) - for metrics queries
- Worker 06: Maintenance (#331) - for backup and optimization

---

## Best Practices

1. **SOLID Principles**
   - Single Responsibility: Each class has one job
   - Dependency Inversion: Depend on abstractions (Protocols)
   - Interface Segregation: Minimal, focused interfaces

2. **Error Handling**
   - Always use context managers for connections
   - Catch and wrap SQLITE_BUSY errors
   - Log all database errors

3. **Performance**
   - Reuse connections
   - Use parameterized queries
   - Batch operations when possible

4. **Windows Compatibility**
   - Test on Windows filesystem
   - Avoid network paths
   - Use proper path handling (`pathlib`)

---

## Resources

- [SQLite WAL Mode](https://sqlite.org/wal.html)
- [Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite PRAGMA Cheatsheet](https://www.sqlite.org/pragma.html)
- Web research results from #320

---

## Success Metrics

- Database initialization time: <100ms
- Connection overhead: <10ms
- Transaction throughput: >100 tx/sec
- SQLITE_BUSY error rate: <1%
- Test coverage: >80%

---

**Status**: Ready to Start  
**Assigned**: Worker 01 - Backend Engineer  
**Labels**: `backend`, `database`, `sqlite`, `infrastructure`
