# Worker06 - Database Specialist

**Role**: Database Schema Design & Data Storage  
**Language**: Python 3.10+ (SQLite, SQL)  
**Project**: YouTube Worker Refactor  
**Duration**: Weeks 1-2 (3 issues total)

---

## Overview

Worker06 is a **database specialist** responsible for designing and implementing the SQLite database schema for the worker queue system and results storage. This role requires expertise in:

- SQLite optimization (especially WAL mode, Windows)
- Database schema design
- SQL query optimization and indexing
- Data migration strategies
- ACID transaction management
- Python sqlite3 module

---

## Skills Required

### Core Competencies
- ✅ **SQL**: Advanced SQL (DDL, DML, indexes, views, triggers)
- ✅ **SQLite**: WAL mode, PRAGMA settings, Windows optimization
- ✅ **Database Design**: Normalization, schema versioning, migrations
- ✅ **Performance**: Query optimization, index design, EXPLAIN QUERY PLAN
- ✅ **Transactions**: ACID, isolation levels, IMMEDIATE transactions
- ✅ **Python**: sqlite3 module, connection pooling, thread safety

### Domain Knowledge
- ✅ **Queue Systems**: Task queue patterns, atomic operations
- ✅ **Data Modeling**: Entity relationships, constraints
- ✅ **Windows**: File system behaviors, locking mechanisms
- ✅ **Monitoring**: Database statistics, query profiling

### Tools & Libraries
- SQLite 3.35+ (WAL mode support)
- Python sqlite3 module
- DB Browser for SQLite (GUI tool)
- sqlitebrowser (CLI tool)
- pytest (testing)

---

## Assigned Issues (3 Total)

### Phase 1: Database Foundation (Issues #004-#008)

#### Issue #004: Design Worker Task Schema in SQLite ⭐ CRITICAL
**Duration**: 1-2 days  
**Priority**: Critical (blocking all worker issues)  
**Dependencies**: None

**Deliverables**:
- 3-table schema:
  - `task_queue` - Main queue with atomic claiming
  - `worker_heartbeats` - Worker health monitoring
  - `task_logs` - Audit trail
- Critical indexes for <10ms claiming performance
- Monitoring views (v_active_tasks, v_worker_status, v_task_stats)
- Windows-optimized PRAGMA settings
- `QueueDatabase` management class (Python)
- Migration scripts
- Unit tests

**SQL Schema**:
```sql
-- task_queue: Main queue
CREATE TABLE task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,  -- 'channel_scrape', 'trending_scrape', 'keyword_search'
    parameters TEXT NOT NULL,  -- JSON
    priority INTEGER NOT NULL DEFAULT 5,
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
    CHECK (status IN ('queued', 'claimed', 'running', 'completed', 'failed', 'cancelled'))
);

-- Critical index for fast claiming
CREATE INDEX idx_task_queue_claiming 
    ON task_queue(status, priority DESC, created_at DESC)
    WHERE status = 'queued';
```

**Python Components**:
```python
# src/workers/queue_database.py
class QueueDatabase:
    """Manages worker queue database with Windows optimizations."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._initialize()
    
    def _initialize(self):
        """Initialize database with schema and PRAGMA settings."""
        conn = self.get_connection()
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        # ... more Windows optimizations
```

**Key Challenges**:
- Windows file system locking
- WAL mode configuration
- Partial index design for performance
- IMMEDIATE transaction timing

---

#### Issue #007: Implement Result Storage Layer
**Duration**: 2 days  
**Priority**: High  
**Dependencies**: #004 (schema must exist)

**Deliverables**:
- Results database schema
- Storage abstraction (Repository pattern)
- Deduplication logic (source, source_id constraint)
- Metrics storage
- Query interfaces
- Unit tests

**SQL Schema**:
```sql
-- results_table: Scraped content storage
CREATE TABLE youtube_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,  -- 'youtube_channel', 'youtube_trending'
    source_id TEXT NOT NULL,  -- YouTube video ID
    title TEXT NOT NULL,
    description TEXT,
    tags TEXT,  -- JSON array
    metrics TEXT,  -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(source, source_id)  -- Deduplication
);

CREATE INDEX idx_results_source ON youtube_results(source, created_at DESC);
```

**Python Components**:
```python
# src/workers/result_storage.py
class ResultStorage:
    """Repository pattern for result storage."""
    
    def save_result(self, task: Task, result: TaskResult) -> int:
        """Save task result with deduplication."""
        pass
    
    def get_result(self, source: str, source_id: str) -> Optional[Dict]:
        """Retrieve a result by source and source_id."""
        pass
```

**Key Challenges**:
- Deduplication strategy
- Bulk insert optimization
- JSON storage in SQLite
- Query performance for large datasets

---

#### Issue #008: Create Migration Utilities for Data Transfer
**Duration**: 1-2 days  
**Priority**: High  
**Dependencies**: #004, #007

**Deliverables**:
- Schema versioning system
- Migration scripts (up/down)
- Data migration from old to new format
- Rollback procedures
- Migration testing framework
- Documentation

**Python Components**:
```python
# scripts/migrations/migration_manager.py
class MigrationManager:
    """Manages database schema migrations."""
    
    def get_current_version(self) -> int:
        """Get current schema version."""
        pass
    
    def migrate_up(self, target_version: Optional[int] = None):
        """Apply migrations up to target version."""
        pass
    
    def migrate_down(self, target_version: int):
        """Rollback migrations to target version."""
        pass

# migrations/001_initial_schema.py
class Migration001:
    def up(self, conn: sqlite3.Connection):
        """Apply migration."""
        conn.executescript("""
            CREATE TABLE task_queue (...);
            CREATE INDEX idx_task_queue_claiming (...);
        """)
    
    def down(self, conn: sqlite3.Connection):
        """Rollback migration."""
        conn.execute("DROP TABLE task_queue")
```

**Key Challenges**:
- Version tracking
- Idempotent migrations
- Data preservation during migration
- Testing rollback scenarios

---

## SQL Best Practices

### PRAGMA Settings (Windows Optimized)
```sql
-- Enable Write-Ahead Logging (critical for concurrent access)
PRAGMA journal_mode = WAL;

-- Handle SQLITE_BUSY gracefully (5 seconds)
PRAGMA busy_timeout = 5000;

-- Optimize for Windows SSD
PRAGMA synchronous = NORMAL;

-- Memory-mapped I/O (faster on Windows, RTX 5090 has 64GB RAM)
PRAGMA mmap_size = 30000000000;  -- 30GB

-- Cache size (10MB)
PRAGMA cache_size = -10000;

-- Auto-vacuum for maintenance
PRAGMA auto_vacuum = INCREMENTAL;

-- Temp store in memory
PRAGMA temp_store = MEMORY;
```

### Transaction Patterns
```sql
-- IMMEDIATE transaction for atomic claiming (prevents SQLITE_BUSY)
BEGIN IMMEDIATE;
SELECT id FROM task_queue WHERE status = 'queued' LIMIT 1;
UPDATE task_queue SET status = 'claimed' WHERE id = ?;
COMMIT;

-- DEFERRED for read-mostly operations
BEGIN;
SELECT * FROM task_queue WHERE status = 'completed';
COMMIT;
```

### Index Design
```sql
-- Partial index (WHERE clause) - reduces index size
CREATE INDEX idx_task_queue_claiming 
    ON task_queue(status, priority DESC, created_at DESC)
    WHERE status = 'queued';  -- Only index queued tasks

-- Multi-column index for common queries
CREATE INDEX idx_results_source_time 
    ON youtube_results(source, created_at DESC);

-- Use EXPLAIN QUERY PLAN to verify index usage
EXPLAIN QUERY PLAN
SELECT * FROM task_queue WHERE status = 'queued' ORDER BY priority DESC;
```

### Query Optimization
```python
# Use parameterized queries (prevents SQL injection, better caching)
cursor.execute(
    "SELECT * FROM task_queue WHERE status = ? ORDER BY priority DESC",
    ('queued',)
)

# Batch operations for better performance
cursor.executemany(
    "INSERT INTO task_logs (task_id, event_type, timestamp) VALUES (?, ?, ?)",
    [(1, 'started', '2025-11-11T12:00:00Z'),
     (2, 'started', '2025-11-11T12:00:01Z')]
)
```

---

## Python Database Standards

### Connection Management
```python
class QueueDatabase:
    """Thread-safe database connection management."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._local = threading.local()  # Thread-local storage
    
    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local connection."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
```

### Error Handling
```python
try:
    cursor.execute("BEGIN IMMEDIATE")
    # ... operations
    cursor.execute("COMMIT")
except sqlite3.OperationalError as e:
    cursor.execute("ROLLBACK")
    if "database is locked" in str(e):
        # Retry with backoff
        time.sleep(0.1)
        # ... retry logic
    else:
        raise
```

### Testing Standards
```python
def test_atomic_claiming():
    """Test atomic task claiming prevents double-claiming."""
    # Arrange: Create 1 task
    db = QueueDatabase(':memory:')
    # ... insert task
    
    # Act: Two workers try to claim simultaneously
    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(worker1.claim_task)
        future2 = executor.submit(worker2.claim_task)
        task1 = future1.result()
        task2 = future2.result()
    
    # Assert: Only one succeeds
    assert (task1 is not None) != (task2 is not None)
```

---

## Timeline & Milestones

### Week 1 (Days 1-5)
- ✅ Day 1-2: Complete #004 (Database Schema)
- ⏳ Day 3-4: Complete #007 (Result Storage)
- ⏳ Day 5: Complete #008 (Migrations)

### Week 2 (Days 6-10)
- ⏳ Buffer for testing and optimization
- ⏳ Support Worker02 with query optimization
- ⏳ Performance testing and tuning

---

## Collaboration Points

### With Worker02 (Python Specialist)
- **Week 1**: Coordinate on schema design (#002, #004)
- **Week 1-2**: Optimize queries for worker performance
- **Daily**: Support on SQLite connection issues

### With Worker05 (DevOps)
- **Week 3**: Provide database metrics (#018)
- **Week 3**: Setup monitoring queries

### With Worker04 (QA/Testing)
- **Week 3-4**: Provide test database fixtures
- **Week 4**: Support database performance testing (#022)

---

## Performance Targets

### Query Performance
- [ ] Task claiming: <10ms (P95)
- [ ] Result insertion: <5ms (P95)
- [ ] Statistics queries: <100ms (P95)

### Database Size
- [ ] Queue database: <100MB (1M tasks)
- [ ] Results database: <1GB (100K results)
- [ ] Index overhead: <20% of data size

### Concurrency
- [ ] Support 4-8 concurrent workers
- [ ] SQLITE_BUSY rate: <2%
- [ ] Write conflicts: <1%

---

## Success Criteria

### Deliverables
- [ ] All 3 issues completed
- [ ] Schema documentation complete
- [ ] Migration system tested
- [ ] Performance benchmarks met
- [ ] Unit tests >80% coverage

### Quality
- [ ] ACID compliance verified
- [ ] No data loss under failure scenarios
- [ ] Rollback procedures tested
- [ ] Windows compatibility verified

---

## Resources

### Documentation
- SQLite WAL: https://sqlite.org/wal.html
- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- SQLite optimization: https://sqlite.org/optoverview.html
- Windows SQLite: https://sqlite.org/windows.html

### Internal References
- Master Plan: `_meta/issues/new/400-refactor-youtube-as-worker-master-plan.md`
- SQLite Queue Examples: Issues #320-340 (PrismQ.Client)

### Tools
- DB Browser for SQLite: https://sqlitebrowser.org/
- SQLite Analyzer: Built into SQLite CLI

---

## Contact

**Primary Contact**: Worker06 - Database Specialist  
**Backup**: Worker01 - Project Manager  
**Technical Support**: Worker02 - Python Specialist (integration)

---

**Status**: 📋 Ready for Assignment  
**Created**: 2025-11-11  
**Last Updated**: 2025-11-11  
**Issues**: 3 total (1 completed, 2 remaining)
