# Quick Reference: Task Database Writing

**For**: PrismQ.IdeaInspiration  
**Date**: November 6, 2025  
**Status**: ✅ Production Ready

---

## TL;DR

✅ **Task database writing IS WORKING**
- Use `POST /queue/enqueue` REST API endpoint
- Or use `QueueDatabase` class directly
- Full ACID transactions supported
- Idempotency built-in

---

## Quick Start Examples

### 1. Using REST API (Recommended)

```bash
# Start the backend server
cd Client/Backend
python -m src.uvicorn_runner

# Enqueue a task
curl -X POST http://localhost:8000/queue/enqueue \
  -H "Content-Type: application/json" \
  -d '{
    "type": "youtube_search",
    "priority": 100,
    "payload": {"query": "AI trends 2025"},
    "max_attempts": 5,
    "idempotency_key": "search-20251106-001"
  }'

# Response:
# {
#   "task_id": 1,
#   "status": "queued",
#   "created_at_utc": "2025-11-06T10:00:00Z",
#   "message": "Task enqueued successfully"
# }
```

### 2. Using Python QueueDatabase Class

```python
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path("Client/Backend/src")))

from queue import QueueDatabase
import json

# Initialize database
db = QueueDatabase("C:/Data/PrismQ/queue/queue.db")  # Windows
# db = QueueDatabase("/tmp/prismq/queue/queue.db")  # Linux
db.initialize_schema()

# Insert task with transaction
with db.transaction() as conn:
    cursor = conn.execute(
        """
        INSERT INTO task_queue (type, priority, payload, idempotency_key)
        VALUES (?, ?, ?, ?)
        """,
        (
            "youtube_search",
            100,
            json.dumps({"query": "AI trends 2025"}),
            "search-20251106-001"
        )
    )
    task_id = cursor.lastrowid

print(f"Task created with ID: {task_id}")

# Query task status
cursor = db.execute(
    "SELECT id, type, status, priority FROM task_queue WHERE id = ?",
    (task_id,)
)
task = dict(cursor.fetchone())
print(f"Task status: {task['status']}")

db.close()
```

### 3. Using Task Model

```python
from queue import QueueDatabase, Task
from datetime import datetime, timezone

db = QueueDatabase()
db.initialize_schema()

# Create task object
task = Task(
    type="reddit_scrape",
    priority=50,
    payload='{"subreddit": "MachineLearning"}',
    status="queued",
    max_attempts=5,
    run_after_utc=datetime.now(timezone.utc),
    idempotency_key="reddit-ml-001"
)

# Convert to dict for insertion
task_dict = task.to_dict()

# Insert using model data
with db.transaction() as conn:
    conn.execute(
        """
        INSERT INTO task_queue (
            type, priority, payload, status, max_attempts, 
            run_after_utc, idempotency_key
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task.type,
            task.priority,
            task.payload,
            task.status,
            task.max_attempts,
            task.run_after_utc.isoformat() if task.run_after_utc else None,
            task.idempotency_key
        )
    )

db.close()
```

---

## Common Operations

### Check Queue Statistics

```python
from queue import QueueDatabase

db = QueueDatabase()
cursor = db.execute(
    """
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN status = 'queued' THEN 1 ELSE 0 END) as queued,
        SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
    FROM task_queue
    """
)
stats = dict(cursor.fetchone())
print(f"Total: {stats['total']}, Queued: {stats['queued']}")
```

### Update Task Status

```python
from queue import QueueDatabase

db = QueueDatabase()

# Update to processing
with db.transaction() as conn:
    conn.execute(
        """
        UPDATE task_queue
        SET status = ?,
            processing_started_utc = datetime('now'),
            locked_by = ?,
            updated_at_utc = datetime('now')
        WHERE id = ?
        """,
        ("processing", "worker-01", task_id)
    )

# Update to completed
with db.transaction() as conn:
    conn.execute(
        """
        UPDATE task_queue
        SET status = ?,
            finished_at_utc = datetime('now'),
            updated_at_utc = datetime('now')
        WHERE id = ?
        """,
        ("completed", task_id)
    )
```

### List Tasks with Filters

```bash
# Get all queued tasks
curl http://localhost:8000/queue/tasks?status=queued&limit=100

# Get tasks of specific type
curl http://localhost:8000/queue/tasks?type=youtube_search

# Get recent tasks
curl http://localhost:8000/queue/tasks?limit=10
```

### Cancel a Task

```bash
curl -X POST http://localhost:8000/queue/tasks/123/cancel

# Response:
# {
#   "task_id": 123,
#   "status": "failed",
#   "message": "Task cancelled successfully"
# }
```

---

## Database Schema

```sql
-- Main task queue table
CREATE TABLE task_queue (
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
  updated_at_utc     DATETIME NOT NULL DEFAULT (datetime('now'))
);

-- Unique constraint for idempotency
CREATE UNIQUE INDEX uq_task_idempotency
  ON task_queue (idempotency_key)
  WHERE idempotency_key IS NOT NULL;
```

---

## Task Status Flow

```
QUEUED
  ↓ (worker claims task)
PROCESSING
  ↓
  ├─→ COMPLETED (success)
  ├─→ FAILED (max retries exceeded)
  └─→ CANCELLED (user cancellation)
```

---

## Error Handling

### Idempotency (Duplicate Prevention)

```python
# First insert
task_id = enqueue_task("search-key-001", {...})  # Returns ID 1

# Second insert with same key
task_id = enqueue_task("search-key-001", {...})  # Returns ID 1 (same task)
# No duplicate created!
```

### Transaction Rollback

```python
try:
    with db.transaction() as conn:
        conn.execute("INSERT INTO task_queue ...")
        conn.execute("INSERT INTO task_logs ...")
        # Both succeed or both roll back
except Exception as e:
    print(f"Transaction rolled back: {e}")
    # Database is unchanged
```

### Database Busy

```python
from queue import QueueBusyError

try:
    db.execute("INSERT INTO task_queue ...")
except QueueBusyError:
    # Database is locked, retry after delay
    time.sleep(0.1)
    db.execute("INSERT INTO task_queue ...")
```

---

## Performance Tips

1. **Use transactions for multiple operations**
   ```python
   with db.transaction() as conn:
       for task in tasks:
           conn.execute("INSERT INTO task_queue ...", task)
   # Single commit for all inserts
   ```

2. **Use execute_many for batch inserts**
   ```python
   db.execute_many(
       "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
       [("type1", "{}"), ("type2", "{}"), ("type3", "{}")]
   )
   ```

3. **Use indexes for common queries**
   ```sql
   -- Already created:
   CREATE INDEX ix_task_status_prio_time
     ON task_queue (status, priority, run_after_utc);
   ```

---

## Testing

### Run Existing Tests

```bash
cd Client/Backend

# Run all queue tests
pytest _meta/tests/Backend/queue/ -v

# Run specific test file
pytest _meta/tests/Backend/queue/test_queue_database.py -v

# Run with coverage
pytest _meta/tests/Backend/queue/ --cov=src.queue
```

### Manual Testing

```python
# Use the demo script
cd Client/Backend
python src/queue/demo_scheduling.py

# Or run the investigation demo
python /tmp/demo_task_database_writing.py
```

---

## File Locations

### Core Implementation
- `Client/Backend/src/queue/database.py` - Database connection
- `Client/Backend/src/queue/schema.py` - SQL schema
- `Client/Backend/src/queue/models.py` - Data models
- `Client/Backend/src/api/queue.py` - REST API

### Tests
- `Client/_meta/tests/Backend/queue/test_queue_database.py` - Database tests
- `Client/_meta/tests/Backend/queue/test_integration_validation.py` - Integration tests

### Documentation
- `_meta/issues/wip/TASK_DATABASE_WRITE_INVESTIGATION.md` - Full investigation
- `_meta/issues/wip/ZJISTENI_STAVU_ZAPISU_TASKU.md` - Czech summary
- `Client/Backend/src/queue/README.md` - Queue system overview

---

## Default Database Locations

### Windows
```
C:\Data\PrismQ\queue\queue.db
```

### Linux/macOS
```
/tmp/prismq/queue/queue.db
```

### Custom Path
```python
# Via environment variable
os.environ["PRISMQ_QUEUE_DB_PATH"] = "/custom/path/queue.db"

# Or directly in code
db = QueueDatabase("/custom/path/queue.db")
```

---

## Next Steps

### To Use Today:
1. ✅ Use REST API endpoints (`POST /queue/enqueue`)
2. ✅ Use `QueueDatabase` class directly in Python
3. ✅ Database persistence is production-ready

### To Wait For (Issue #339 - Week 4):
1. ⚠️ `QueuedTaskManager` integration with `BackgroundTaskManager`
2. ⚠️ Feature flag configuration
3. ⚠️ Seamless backend switching (in-memory ↔ persistent)

---

**Last Updated**: November 6, 2025  
**Status**: ✅ Fully Functional and Production Ready
