# Issue #004: Design Worker Task Schema in SQLite

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 06 - Database Specialist  
**Language**: Python 3.10+ (SQLite, SQL)  
**Status**: New  
**Priority**: Critical (Foundational)  
**Duration**: 1-2 days  
**Dependencies**: None (Can be done in parallel with #002)

---

## Worker Details: Worker06 - Database Specialist

**Role**: Database Schema Design & Optimization  
**Expertise Required**:
- SQLite WAL mode and Windows optimization
- Database schema design and normalization
- SQL query optimization and indexing
- ACID transactions and isolation levels
- Python sqlite3 module

**Collaboration**:
- **Worker02** (Python): Coordinate on table structure and query patterns
- **Worker05** (DevOps): Provide monitoring views and statistics
- **Worker01** (PM): Daily standup, performance validation

**See**: `_meta/issues/new/Worker06/README.md` for complete role description

---

## Objective

Design and implement the SQLite database schema for the worker task queue system. This schema must support task persistence, claiming, retries, and monitoring for the YouTube scraping workers.

---

## Problem Statement

The YouTube workers need a persistent task queue to:
1. Store tasks across restarts
2. Support atomic task claiming by multiple workers
3. Track task status and history
4. Enable monitoring and observability
5. Support different claiming strategies (LIFO, FIFO, PRIORITY)

The schema must be optimized for:
- Windows file system
- SQLite WAL mode
- Concurrent worker access
- Fast task claiming (<10ms)
- Efficient monitoring queries

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**Database Schema Responsibilities**:
- Store task queue data
- Track worker heartbeats
- Log task history
- Provide query interfaces

**NOT Responsible For**:
- Task execution logic
- Worker implementation
- Business logic

### Open/Closed Principle (OCP) ✅
**Extensibility**:
- Can add new task types without schema changes
- Can add new status values via enum
- Can extend with views and indexes

**Stability**:
- Core tables remain unchanged
- Only additions, no breaking changes

### Dependency Inversion Principle (DIP) ✅
**Interface Through SQL**:
- Workers depend on schema contract, not implementation
- Standard SQL interface
- Can migrate to different database later

---

## Proposed Schema

### Table 1: task_queue

**Purpose**: Main task storage and queue

```sql
CREATE TABLE IF NOT EXISTS task_queue (
    -- Identity
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,  -- 'channel_scrape', 'trending_scrape', 'keyword_search'
    
    -- Parameters (stored as JSON text)
    parameters TEXT NOT NULL,  -- JSON: {"channel_url": "...", "top_n": 50}
    
    -- Scheduling
    priority INTEGER NOT NULL DEFAULT 5,  -- 1 (lowest) to 10 (highest)
    run_after_utc TEXT,  -- ISO 8601: '2025-11-11T12:00:00Z'
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'queued',  
        -- 'queued', 'claimed', 'running', 'completed', 'failed', 'cancelled'
    
    -- Worker assignment
    claimed_by TEXT,  -- worker_id
    claimed_at TEXT,  -- ISO 8601 timestamp
    
    -- Retry logic
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    
    -- Results
    result_data TEXT,  -- JSON result data
    error_message TEXT,  -- Error details if failed
    
    -- Timestamps
    created_at TEXT NOT NULL,  -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,  -- ISO 8601 timestamp
    completed_at TEXT,  -- ISO 8601 timestamp
    
    -- Constraints
    CHECK (priority BETWEEN 1 AND 10),
    CHECK (retry_count <= max_retries),
    CHECK (status IN ('queued', 'claimed', 'running', 'completed', 'failed', 'cancelled'))
);

-- Indexes for fast claiming (critical for performance)
CREATE INDEX IF NOT EXISTS idx_task_queue_claiming 
    ON task_queue(status, priority DESC, created_at DESC)
    WHERE status = 'queued';

-- Index for monitoring queries
CREATE INDEX IF NOT EXISTS idx_task_queue_worker
    ON task_queue(claimed_by, status);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_task_queue_created
    ON task_queue(created_at);
```

### Table 2: worker_heartbeats

**Purpose**: Track active workers and their health

```sql
CREATE TABLE IF NOT EXISTS worker_heartbeats (
    worker_id TEXT PRIMARY KEY,
    last_heartbeat TEXT NOT NULL,  -- ISO 8601 timestamp
    tasks_processed INTEGER NOT NULL DEFAULT 0,
    tasks_failed INTEGER NOT NULL DEFAULT 0,
    current_task_id INTEGER,  -- Reference to task_queue.id
    strategy TEXT NOT NULL DEFAULT 'LIFO',  -- 'FIFO', 'LIFO', 'PRIORITY'
    
    -- Metadata
    started_at TEXT NOT NULL,  -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,  -- ISO 8601 timestamp
    
    FOREIGN KEY (current_task_id) REFERENCES task_queue(id)
);

-- Index for finding stale workers
CREATE INDEX IF NOT EXISTS idx_worker_heartbeat
    ON worker_heartbeats(last_heartbeat);
```

### Table 3: task_logs

**Purpose**: Audit trail and debugging

```sql
CREATE TABLE IF NOT EXISTS task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    worker_id TEXT,
    event_type TEXT NOT NULL,  
        -- 'created', 'claimed', 'started', 'progress', 'completed', 'failed', 'retry'
    message TEXT,
    details TEXT,  -- JSON for structured data
    timestamp TEXT NOT NULL,  -- ISO 8601 timestamp
    
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (worker_id) REFERENCES worker_heartbeats(worker_id)
);

-- Index for task history queries
CREATE INDEX IF NOT EXISTS idx_task_logs_task
    ON task_logs(task_id, timestamp);

-- Index for worker activity queries
CREATE INDEX IF NOT EXISTS idx_task_logs_worker
    ON task_logs(worker_id, timestamp);
```

### Views for Monitoring

```sql
-- Active tasks view
CREATE VIEW IF NOT EXISTS v_active_tasks AS
SELECT 
    t.id,
    t.task_type,
    t.status,
    t.claimed_by,
    t.priority,
    t.retry_count,
    t.created_at,
    t.claimed_at,
    CAST((julianday('now') - julianday(t.created_at)) * 24 * 60 AS INTEGER) as age_minutes
FROM task_queue t
WHERE t.status IN ('queued', 'claimed', 'running');

-- Worker status view
CREATE VIEW IF NOT EXISTS v_worker_status AS
SELECT 
    w.worker_id,
    w.last_heartbeat,
    w.tasks_processed,
    w.tasks_failed,
    w.strategy,
    t.task_type as current_task_type,
    t.id as current_task_id,
    CAST((julianday('now') - julianday(w.last_heartbeat)) * 60 AS INTEGER) as minutes_since_heartbeat
FROM worker_heartbeats w
LEFT JOIN task_queue t ON w.current_task_id = t.id;

-- Task statistics view
CREATE VIEW IF NOT EXISTS v_task_stats AS
SELECT 
    task_type,
    status,
    COUNT(*) as count,
    AVG(retry_count) as avg_retries,
    MIN(created_at) as oldest,
    MAX(created_at) as newest
FROM task_queue
GROUP BY task_type, status;
```

---

## Database Configuration

### PRAGMA Settings (Windows Optimized)

```sql
-- Enable Write-Ahead Logging for concurrent access
PRAGMA journal_mode = WAL;

-- Handle SQLITE_BUSY gracefully
PRAGMA busy_timeout = 5000;  -- 5 seconds

-- Optimize for Windows SSD
PRAGMA synchronous = NORMAL;  -- Balance safety and speed

-- Cache size (in pages, negative = KB)
PRAGMA cache_size = -10000;  -- 10MB cache

-- Memory-mapped I/O (faster on Windows)
PRAGMA mmap_size = 30000000000;  -- 30GB (RTX 5090 has plenty RAM)

-- Auto-vacuum for maintenance
PRAGMA auto_vacuum = INCREMENTAL;

-- Temp store in memory
PRAGMA temp_store = MEMORY;
```

---

## Implementation Plan

### Step 1: Create Schema File

**File**: `Sources/Content/Shorts/YouTube/src/workers/schema.sql`

```sql
-- Worker Task Queue Schema
-- Version: 1.0
-- Created: 2025-11-11

-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS task_logs;
DROP TABLE IF EXISTS worker_heartbeats;
DROP TABLE IF EXISTS task_queue;

-- Drop views
DROP VIEW IF EXISTS v_active_tasks;
DROP VIEW IF EXISTS v_worker_status;
DROP VIEW IF EXISTS v_task_stats;

-- Create tables
[Insert table definitions here]

-- Create indexes
[Insert index definitions here]

-- Create views
[Insert view definitions here]
```

### Step 2: Create Schema Manager

**File**: `Sources/Content/Shorts/YouTube/src/workers/queue_database.py`

```python
"""Queue database management."""

import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class QueueDatabase:
    """Manages the worker queue database.
    
    Follows Single Responsibility: Database setup and configuration only.
    """
    
    def __init__(self, db_path: str):
        """Initialize queue database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize on first use
        self._initialize()
    
    def _initialize(self):
        """Initialize database with schema and PRAGMA settings."""
        conn = self.get_connection()
        
        try:
            # Set PRAGMA settings (Windows optimized)
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA busy_timeout = 5000")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -10000")
            conn.execute("PRAGMA mmap_size = 30000000000")
            conn.execute("PRAGMA auto_vacuum = INCREMENTAL")
            conn.execute("PRAGMA temp_store = MEMORY")
            
            # Load and execute schema
            schema_file = Path(__file__).parent / "schema.sql"
            if schema_file.exists():
                with open(schema_file) as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
            else:
                # Inline schema if file not found
                self._create_schema(conn)
            
            conn.commit()
            logger.info(f"Queue database initialized: {self.db_path}")
            
        finally:
            conn.close()
    
    def _create_schema(self, conn: sqlite3.Connection):
        """Create schema inline (fallback)."""
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                parameters TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 5,
                run_after_utc TEXT,
                status TEXT NOT NULL DEFAULT 'queued',
                claimed_by TEXT,
                claimed_at TEXT,
                retry_count INTEGER NOT NULL DEFAULT 0,
                max_retries INTEGER NOT NULL DEFAULT 3,
                result_data TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                CHECK (priority BETWEEN 1 AND 10),
                CHECK (retry_count <= max_retries),
                CHECK (status IN ('queued', 'claimed', 'running', 
                                 'completed', 'failed', 'cancelled'))
            )
        """)
        
        # Create indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_queue_claiming 
            ON task_queue(status, priority DESC, created_at DESC)
            WHERE status = 'queued'
        """)
        
        # [Additional tables, indexes, views]
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection.
        
        Each worker should have its own connection.
        
        Returns:
            SQLite connection with row factory
        """
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def vacuum(self):
        """Perform VACUUM to reclaim space."""
        conn = self.get_connection()
        try:
            conn.execute("VACUUM")
            logger.info("Database vacuumed")
        finally:
            conn.close()
    
    def checkpoint(self):
        """Perform WAL checkpoint."""
        conn = self.get_connection()
        try:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            logger.info("WAL checkpoint completed")
        finally:
            conn.close()
    
    def get_stats(self) -> dict:
        """Get database statistics.
        
        Returns:
            Dictionary with database stats
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Total tasks by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM task_queue
                GROUP BY status
            """)
            status_counts = {row['status']: row['count'] 
                           for row in cursor.fetchall()}
            
            # Active workers
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM worker_heartbeats
                WHERE julianday('now') - julianday(last_heartbeat) < 0.0021
            """)  # < 3 minutes
            active_workers = cursor.fetchone()['count']
            
            # Database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()['size']
            
            return {
                'status_counts': status_counts,
                'active_workers': active_workers,
                'db_size_bytes': db_size,
                'db_size_mb': db_size / (1024 * 1024)
            }
            
        finally:
            conn.close()
```

### Step 3: Create Migration Script

**File**: `Sources/Content/Shorts/YouTube/scripts/init_queue_db.py`

```python
"""Initialize or migrate the queue database."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from workers.queue_database import QueueDatabase


def main():
    """Initialize queue database."""
    db_path = Path(__file__).parent.parent / "data" / "worker_queue.db"
    
    print(f"Initializing queue database: {db_path}")
    
    # Create database
    queue_db = QueueDatabase(str(db_path))
    
    # Show stats
    stats = queue_db.get_stats()
    print(f"\nDatabase initialized:")
    print(f"  Size: {stats['db_size_mb']:.2f} MB")
    print(f"  Active workers: {stats['active_workers']}")
    print(f"  Task counts: {stats['status_counts']}")
    
    print("\n✅ Queue database ready!")


if __name__ == "__main__":
    main()
```

---

## Acceptance Criteria

- [ ] Schema file created with all tables, indexes, views
- [ ] PRAGMA settings optimized for Windows
- [ ] QueueDatabase class implemented
- [ ] Indexes support fast claiming (<10ms)
- [ ] Atomic operations via IMMEDIATE transactions
- [ ] Views provide monitoring interface
- [ ] Migration script works
- [ ] Database size optimized (auto_vacuum)
- [ ] Unit tests for schema operations
- [ ] Documentation complete

---

## Testing Strategy

### Unit Tests

**File**: `Sources/Content/Shorts/YouTube/_meta/tests/test_queue_database.py`

```python
import pytest
import tempfile
from pathlib import Path
from src.workers.queue_database import QueueDatabase


def test_database_initialization():
    """Test database initializes with correct schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = QueueDatabase(str(db_path))
        
        # Check tables exist
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        tables = {row[0] for row in cursor.fetchall()}
        
        assert 'task_queue' in tables
        assert 'worker_heartbeats' in tables
        assert 'task_logs' in tables
        
        conn.close()


def test_pragma_settings():
    """Test PRAGMA settings are correct."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = QueueDatabase(str(db_path))
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check WAL mode
        cursor.execute("PRAGMA journal_mode")
        assert cursor.fetchone()[0] == 'wal'
        
        # Check busy timeout
        cursor.execute("PRAGMA busy_timeout")
        assert cursor.fetchone()[0] == 5000
        
        conn.close()


def test_index_exists():
    """Test critical indexes exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = QueueDatabase(str(db_path))
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index'
        """)
        indexes = {row[0] for row in cursor.fetchall()}
        
        assert 'idx_task_queue_claiming' in indexes
        
        conn.close()


def test_view_exists():
    """Test monitoring views exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = QueueDatabase(str(db_path))
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
        """)
        views = {row[0] for row in cursor.fetchall()}
        
        assert 'v_active_tasks' in views
        assert 'v_worker_status' in views
        
        conn.close()
```

### Performance Tests

```python
def test_claiming_performance():
    """Test task claiming is fast (<10ms)."""
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = QueueDatabase(str(db_path))
        conn = db.get_connection()
        
        # Insert 1000 tasks
        cursor = conn.cursor()
        for i in range(1000):
            cursor.execute("""
                INSERT INTO task_queue 
                (task_type, parameters, created_at, updated_at)
                VALUES (?, ?, datetime('now'), datetime('now'))
            """, ('test', '{}'))
        conn.commit()
        
        # Measure claim time
        start = time.time()
        cursor.execute("""
            SELECT id FROM task_queue
            WHERE status = 'queued'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        cursor.fetchone()
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 10, f"Claiming took {elapsed_ms}ms (expected <10ms)"
        
        conn.close()
```

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/src/workers/schema.sql`
2. `Sources/Content/Shorts/YouTube/src/workers/queue_database.py`
3. `Sources/Content/Shorts/YouTube/scripts/init_queue_db.py`
4. `Sources/Content/Shorts/YouTube/_meta/tests/test_queue_database.py`

---

## Dependencies

### External
- SQLite 3.35+ (WAL mode support)
- Python 3.10+

### Internal
- None (foundational issue)

---

## Estimated Effort

**1-2 days**:
- Day 1: Schema design, SQL file, QueueDatabase class
- Day 2: Tests, optimization, documentation

---

## Target Platform

- Windows (primary)
- SQLite 3.35+ with WAL mode
- Local SSD (optimized for fast I/O)

---

## Related Issues

- **#001**: Master plan (parent)
- **#002**: Worker base class (parallel)
- **#003**: Task polling (depends on this)
- **#007**: Result storage (depends on this)

---

## Notes

### Design Decisions

1. **Why JSON for parameters?**
   - Flexible schema
   - No migration needed for new parameters
   - Easy to query with json_extract if needed

2. **Why separate task_logs table?**
   - Keeps task_queue lean for fast claiming
   - Detailed audit trail without bloat
   - Can be purged independently

3. **Why views for monitoring?**
   - Encapsulate complex queries
   - Consistent interface
   - Easy to update without code changes

### Performance Considerations

- **Index on (status, priority, created_at)**: Critical for fast claiming
- **WHERE clause in index**: Partial index reduces size
- **WAL mode**: Allows concurrent reads during writes
- **IMMEDIATE transactions**: Prevents SQLITE_BUSY on claim

### Future Enhancements

- Partitioning by date (for archival)
- Additional indexes for analytics
- Sharding for extreme scale (unlikely needed)

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker06 - Database Specialist  
**Estimated Start**: Week 1, Day 1 (parallel with #002)  
**Estimated Completion**: Week 1, Day 2
