# Issue #004: Design Worker Task Schema in SQLite

## Status
New

## Priority
High

## Category
Feature - Database

## Description

Design and implement the SQLite database schema for the worker task queue system. This schema will store task definitions, track task status, enable LIFO claiming, and support retry logic.

## Problem Statement

The worker-based architecture requires a persistent task queue in SQLite. The schema must support task lifecycle management (QUEUED → RUNNING → COMPLETED/FAILED), LIFO claiming, priority management, worker tracking, and failure handling with retries.

## Proposed Solution

Create a comprehensive SQLite schema with:
- `task_queue` table for task persistence
- Task lifecycle status tracking
- Worker assignment and heartbeat monitoring
- Priority and retry management
- LIFO support via timestamps
- Indexes for efficient queries

## Acceptance Criteria

- [ ] SQLite schema designed and documented
- [ ] `task_queue` table created with all required fields
- [ ] Indexes created for performance (status, priority, created_at)
- [ ] Migration script to create/update schema
- [ ] Schema validation utility
- [ ] Foreign key constraints (if applicable)
- [ ] Timestamp fields with proper defaults
- [ ] Documentation of all fields and their purposes
- [ ] Unit tests for schema creation
- [ ] Sample data insertion tests

## Technical Details

### Implementation Approach

1. Design complete schema with all lifecycle fields
2. Create migration script with CREATE TABLE statements
3. Add indexes for query optimization
4. Implement schema validation
5. Add sample data for testing

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/src/core/task_schema.py`
  - Schema creation functions
  - Migration utilities
  - Schema validation

- **Create**: `Sources/Content/Shorts/YouTube/migrations/001_create_task_queue.sql`
  - SQL migration script
  - Table definitions
  - Index definitions

- **Create**: `Sources/Content/Shorts/YouTube/tests/test_task_schema.py`
  - Schema creation tests
  - Validation tests
  - Sample data tests

### Database Schema

```sql
-- Task Queue Table
CREATE TABLE IF NOT EXISTS task_queue (
    -- Primary key
    task_id TEXT PRIMARY KEY,
    
    -- Task identification
    task_type TEXT NOT NULL,  -- 'youtube_channel', 'youtube_trending', 'youtube_keyword'
    
    -- Task parameters (JSON)
    parameters TEXT NOT NULL,  -- JSON string with task-specific params
    
    -- Task status lifecycle
    status TEXT NOT NULL DEFAULT 'QUEUED',
    -- Status values: QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    
    -- Priority and ordering
    priority INTEGER DEFAULT 0,  -- Higher = more important
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Worker tracking
    worker_id TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_heartbeat TIMESTAMP,
    
    -- Results and error handling
    result TEXT,  -- JSON string with task results
    error TEXT,   -- Error message if failed
    
    -- Retry management
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Audit fields
    created_by TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (status IN ('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    CHECK (retry_count <= max_retries),
    CHECK (priority >= 0)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_task_status 
    ON task_queue(status);

CREATE INDEX IF NOT EXISTS idx_task_priority_created 
    ON task_queue(priority DESC, created_at DESC)
    WHERE status = 'QUEUED';

CREATE INDEX IF NOT EXISTS idx_task_worker 
    ON task_queue(worker_id)
    WHERE status = 'RUNNING';

CREATE INDEX IF NOT EXISTS idx_task_heartbeat 
    ON task_queue(last_heartbeat)
    WHERE status = 'RUNNING';

-- Task type statistics view
CREATE VIEW IF NOT EXISTS task_stats AS
SELECT 
    task_type,
    status,
    COUNT(*) as count,
    AVG(CAST((julianday(completed_at) - julianday(started_at)) * 24 * 60 AS REAL)) as avg_duration_minutes
FROM task_queue
WHERE completed_at IS NOT NULL
GROUP BY task_type, status;
```

### Python Schema Management

```python
import sqlite3
from pathlib import Path
from typing import Optional

class TaskSchemaManager:
    """Manages task queue database schema"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def create_schema(self) -> None:
        """Create or update task queue schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Load and execute migration SQL
            migration_sql = self._load_migration('001_create_task_queue.sql')
            conn.executescript(migration_sql)
            
    def validate_schema(self) -> bool:
        """Validate that schema exists and is correct"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='task_queue'
            """)
            return cursor.fetchone() is not None
            
    def get_schema_version(self) -> Optional[int]:
        """Get current schema version"""
        # Implementation for versioning
        pass
    
    def _load_migration(self, filename: str) -> str:
        """Load SQL migration file"""
        migration_path = Path(__file__).parent.parent / 'migrations' / filename
        return migration_path.read_text()
```

### Task Queue API

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime

@dataclass
class TaskDefinition:
    """Task definition for queue insertion"""
    task_type: str
    parameters: Dict[str, Any]
    priority: int = 0
    max_retries: int = 3
    created_by: str = 'system'

class TaskQueueManager:
    """High-level API for task queue operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def enqueue_task(self, task: TaskDefinition) -> str:
        """Add task to queue"""
        task_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO task_queue 
                (task_id, task_type, parameters, priority, max_retries, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                task.task_type,
                json.dumps(task.parameters),
                task.priority,
                task.max_retries,
                task.created_by
            ))
            
        return task_id
    
    def update_task_status(
        self, 
        task_id: str, 
        status: str,
        error: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update task status and results"""
        with sqlite3.connect(self.db_path) as conn:
            if status == 'COMPLETED':
                conn.execute("""
                    UPDATE task_queue
                    SET status = ?,
                        completed_at = CURRENT_TIMESTAMP,
                        result = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                """, (status, json.dumps(result) if result else None, task_id))
                
            elif status == 'FAILED':
                conn.execute("""
                    UPDATE task_queue
                    SET status = ?,
                        completed_at = CURRENT_TIMESTAMP,
                        error = ?,
                        retry_count = retry_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                """, (status, error, task_id))
```

### Dependencies

- SQLite3 (built-in Python)
- Python 3.10+
- json module for parameter serialization

### SOLID Principles Analysis

**Single Responsibility Principle (SRP)**
- ✅ TaskSchemaManager handles schema creation only
- ✅ TaskQueueManager handles queue operations only
- ✅ Separate concerns for schema vs. data

**Open/Closed Principle (OCP)**
- ✅ Schema can be extended with new fields via migrations
- ✅ Closed for modification (stable core fields)

**Liskov Substitution Principle (LSP)**
- ✅ Not applicable (not using inheritance)

**Interface Segregation Principle (ISP)**
- ✅ Focused interfaces (schema vs. queue operations)
- ✅ No forced dependencies

**Dependency Inversion Principle (DIP)**
- ✅ Depends on database path (abstraction)
- ✅ No hard-coded database structure

## Estimated Effort
2 days

## Target Platform
- Windows
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [x] Schema creation tests
- [x] Index verification tests
- [x] Constraint validation tests
- [x] Task insertion tests
- [x] Task update tests (status transitions)
- [x] LIFO query tests (ORDER BY created_at DESC)
- [x] Priority query tests
- [x] Concurrent access tests
- [ ] Migration tests (schema upgrades)

## Related Issues

- Issue #001 - Master Plan
- Issue #002 - Worker Base Class (uses this schema)
- Issue #003 - Task Polling (queries this schema)
- Issue #007 - Result Storage Layer (writes to this schema)

## Notes

### Schema Design Decisions

1. **LIFO Support**: `created_at DESC` in index for efficient newest-first queries
2. **JSON Parameters**: Flexible parameter storage without schema changes
3. **Status Enum**: CHECK constraint ensures valid status values
4. **Heartbeat**: `last_heartbeat` detects stuck workers
5. **Retry Logic**: `retry_count` and `max_retries` for failure handling
6. **Audit Trail**: `created_by`, `created_at`, `updated_at` for tracking

### Performance Considerations

- Composite index on (priority DESC, created_at DESC) for fast task claiming
- Partial indexes with WHERE clause reduce index size
- Status index for quick filtering
- Worker index for monitoring active tasks

### Future Enhancements

- Add task dependencies (parent_task_id)
- Add task groups for batch operations
- Add scheduled_at for delayed task execution
- Add metrics table for performance tracking

## Migration Strategy

1. Create initial schema (001_create_task_queue.sql)
2. Add version tracking table (future)
3. Support schema upgrades via numbered migrations
4. Rollback support for testing

## Security Considerations

- No sensitive data in parameters (use references)
- Error messages should not expose system internals
- Worker_id validation to prevent spoofing
- SQL injection prevention via parameterized queries
