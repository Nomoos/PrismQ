# Worker Support Documentation

**Issue**: Worker 01 - Support other workers and check validity  
**Created**: 2025-11-05  
**Purpose**: Help Workers 02-06 integrate with queue infrastructure

---

## Overview

This document provides guidance, tools, and best practices for Workers 02-06 to successfully integrate with the queue infrastructure built by Worker 01 (Issue #321).

**Worker 01's Role in Phase 2**: Code review support and integration validation

---

## Quick Start for Other Workers

### 1. Validate Your Environment

Before starting your work, ensure the queue infrastructure is working:

```python
from Client.Backend.src.queue.validation import quick_validate

if quick_validate():
    print("✅ Queue infrastructure ready!")
else:
    print("❌ Infrastructure validation failed")
```

### 2. Validate Your Integration

After implementing your feature, test integration with the queue:

```python
from Client.Backend.src.queue import QueueDatabase
from Client.Backend.src.queue.validation import validate_worker_integration

db = QueueDatabase("queue.db")
db.initialize_schema()

if validate_worker_integration(db, "your-worker-id"):
    print("✅ Integration successful!")
```

### 3. Run Comprehensive Validation

For full validation with performance benchmarks:

```bash
cd Client/Backend
python -m src.queue.validation /path/to/queue.db
```

---

## Integration Patterns

### Pattern 1: Enqueueing Tasks (Worker 02)

**Use Case**: Client API needs to enqueue tasks

```python
from Client.Backend.src.queue import QueueDatabase
import json

db = QueueDatabase("queue.db")

with db.transaction() as conn:
    cursor = conn.execute(
        "INSERT INTO task_queue "
        "(type, status, priority, payload, created_at_utc, run_after_utc) "
        "VALUES (?, ?, ?, ?, datetime('now'), datetime('now')) "
        "RETURNING id",
        ('video_processing', 'queued', 50, json.dumps({'video_id': 123}))
    )
    task_id = cursor.fetchone()[0]

print(f"Enqueued task #{task_id}")
```

**Key Points**:
- ✅ Always use `datetime('now')` for UTC timestamps
- ✅ Always use transactions for data modification
- ✅ Use RETURNING clause to get task ID efficiently
- ✅ Serialize payload as JSON string

### Pattern 2: Claiming Tasks (Worker 03)

**Use Case**: Worker engine needs to claim available tasks

```python
from Client.Backend.src.queue import QueueDatabase

db = QueueDatabase("queue.db")

# Atomic claim operation
with db.transaction() as conn:
    cursor = conn.execute(
        """
        WITH candidate AS (
            SELECT id
            FROM task_queue
            WHERE status = 'queued'
                AND run_after_utc <= datetime('now')
            ORDER BY priority ASC, id ASC
            LIMIT 1
        )
        UPDATE task_queue
        SET status = 'leased',
            reserved_at_utc = datetime('now'),
            lease_until_utc = datetime('now', '+60 seconds'),
            locked_by = ?
        WHERE id = (SELECT id FROM candidate)
        RETURNING *
        """,
        ('worker-1',)
    )
    claimed_task = cursor.fetchone()
    
    if claimed_task:
        print(f"Claimed task #{claimed_task[0]}")
```

**Key Points**:
- ✅ Use CTE (WITH clause) + UPDATE for atomic claiming
- ✅ Always check run_after_utc for scheduled tasks
- ✅ Set lease_until_utc to prevent indefinite locks
- ✅ Use RETURNING to get full task data

### Pattern 3: Using Scheduling Strategies (Worker 04)

**Use Case**: Different scheduling strategies for different workers

```python
from Client.Backend.src.queue import (
    QueueDatabase, 
    SchedulingStrategy, 
    TaskClaimerFactory
)

db = QueueDatabase("queue.db")

# Use FIFO strategy
claimer = TaskClaimerFactory.create(SchedulingStrategy.FIFO, db)
task = claimer.claim_task("worker-1", {}, lease_seconds=60)

# Use Priority strategy
claimer = TaskClaimerFactory.create(SchedulingStrategy.PRIORITY, db)
task = claimer.claim_task("worker-2", {}, lease_seconds=60)
```

**Key Points**:
- ✅ Use TaskClaimerFactory for strategy selection
- ✅ All strategies are atomic (no duplicate claims)
- ✅ Strategy is configured per-worker, not per-queue

### Pattern 4: Observability Queries (Worker 05)

**Use Case**: Get queue statistics and metrics

```python
from Client.Backend.src.queue import QueueDatabase

db = QueueDatabase("queue.db")

with db.connection() as conn:
    # Get queue statistics
    cursor = conn.execute(
        """
        SELECT 
            status,
            COUNT(*) as count,
            AVG(priority) as avg_priority
        FROM task_queue
        GROUP BY status
        """
    )
    
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} tasks (avg priority: {row[2]:.1f})")
```

**Key Points**:
- ✅ Use read-only connection for metrics queries
- ✅ Avoid long-running analytical queries during peak hours
- ✅ Use indexes for better performance

### Pattern 5: Maintenance Operations (Worker 06)

**Use Case**: Cleanup completed tasks and optimize database

```python
from Client.Backend.src.queue import QueueDatabase

db = QueueDatabase("queue.db")

# Delete old completed tasks
with db.transaction() as conn:
    conn.execute(
        """
        DELETE FROM task_queue
        WHERE status = 'completed'
            AND completed_at_utc < datetime('now', '-7 days')
        """
    )
    deleted = conn.total_changes

print(f"Deleted {deleted} old completed tasks")

# Optimize database
with db.connection() as conn:
    conn.execute("VACUUM")
    conn.execute("PRAGMA optimize")
```

**Key Points**:
- ✅ Run VACUUM during low-traffic periods
- ✅ Use PRAGMA optimize before shutdown
- ✅ Consider archiving instead of deleting important data

---

## Common Integration Patterns

### Using the QueueDatabase Class

The recommended way to interact with the queue:

```python
from Client.Backend.src.queue import QueueDatabase

# Initialize
db = QueueDatabase("/path/to/queue.db")
db.initialize_schema()  # Safe to call multiple times

# Read-only operations
with db.connection() as conn:
    cursor = conn.execute("SELECT * FROM task_queue WHERE status = 'queued'")
    tasks = cursor.fetchall()

# Write operations (use transaction)
with db.transaction() as conn:
    conn.execute(
        "UPDATE task_queue SET status = 'completed' WHERE id = ?",
        (task_id,)
    )
```

### Using Configuration Settings

Always use production-optimized configuration:

```python
from Client.Backend.src.queue.config import (
    get_default_db_path,
    ensure_db_directory,
    MAX_CONCURRENT_WORKERS,
    PRODUCTION_PRAGMAS,
)

# Get platform-appropriate database path
db_path = get_default_db_path()
ensure_db_directory(db_path)

# Respect worker limits
print(f"Max concurrent workers: {MAX_CONCURRENT_WORKERS}")
```

### Error Handling

Always handle queue-specific exceptions:

```python
from Client.Backend.src.queue import QueueDatabase, QueueDatabaseError, QueueBusyError

db = QueueDatabase("queue.db")

try:
    with db.transaction() as conn:
        # Your database operation
        pass
        
except QueueBusyError as e:
    # Database is locked, retry with exponential backoff
    print(f"Database busy: {e}")
    
except QueueDatabaseError as e:
    # General database error
    print(f"Database error: {e}")
```

---

## Code Review Checklist

When Worker 01 reviews your code, these items will be checked:

### ✅ Database Operations

- [ ] Using `QueueDatabase` class (not raw sqlite3)
- [ ] Using `db.transaction()` for write operations
- [ ] Using `db.connection()` for read operations
- [ ] Proper error handling with try/except
- [ ] Using parameterized queries (no SQL injection)
- [ ] Using `datetime('now')` for UTC timestamps

### ✅ Data Models

- [ ] Using `Task`, `Worker`, `TaskLog` dataclasses
- [ ] Proper JSON serialization/deserialization
- [ ] Using `Task.from_dict()` for database rows
- [ ] Using `Task.get_payload()` for payload parsing

### ✅ Configuration

- [ ] Using `PRODUCTION_PRAGMAS` from config
- [ ] Respecting `MAX_CONCURRENT_WORKERS` limit
- [ ] Using `get_default_db_path()` for database location
- [ ] Not hardcoding paths or configuration

### ✅ Performance

- [ ] Queries use appropriate indexes
- [ ] Avoiding SELECT * (specify columns)
- [ ] Using LIMIT for potentially large result sets
- [ ] Transactions are short and focused

### ✅ Concurrency

- [ ] Atomic operations using UPDATE...RETURNING
- [ ] Proper isolation with BEGIN IMMEDIATE
- [ ] No race conditions in task claiming
- [ ] Handling SQLITE_BUSY errors gracefully

### ✅ Testing

- [ ] Unit tests for your feature
- [ ] Integration tests with queue
- [ ] Running validation script (validation.py)
- [ ] Performance impact measured

---

## Common Pitfalls

### ❌ DON'T: Use raw datetime strings

```python
# ❌ Wrong - timezone issues
conn.execute("... WHERE created_at_utc > '2025-01-01 00:00:00'")

# ✅ Correct - SQLite's datetime function
conn.execute("... WHERE created_at_utc > datetime('now', '-1 day')")
```

### ❌ DON'T: Forget transactions for writes

```python
# ❌ Wrong - no transaction
with db.connection() as conn:
    conn.execute("UPDATE task_queue SET status = 'completed' WHERE id = ?", (1,))

# ✅ Correct - use transaction
with db.transaction() as conn:
    conn.execute("UPDATE task_queue SET status = 'completed' WHERE id = ?", (1,))
```

### ❌ DON'T: Use SELECT * in production

```python
# ❌ Wrong - fetches unnecessary data
cursor = conn.execute("SELECT * FROM task_queue")

# ✅ Correct - specify columns
cursor = conn.execute("SELECT id, type, status FROM task_queue")
```

### ❌ DON'T: Claim tasks without atomic operations

```python
# ❌ Wrong - race condition
cursor = conn.execute("SELECT id FROM task_queue WHERE status = 'queued' LIMIT 1")
task_id = cursor.fetchone()[0]
conn.execute("UPDATE task_queue SET status = 'leased' WHERE id = ?", (task_id,))

# ✅ Correct - atomic with UPDATE...RETURNING
cursor = conn.execute(
    "UPDATE task_queue SET status = 'leased' "
    "WHERE id = (SELECT id FROM task_queue WHERE status = 'queued' LIMIT 1) "
    "RETURNING id"
)
```

---

## Testing Your Integration

### Step 1: Run Validation Script

```bash
cd Client/Backend
python -m src.queue.validation /path/to/test.db
```

Expected output:
```
======================================================================
QUEUE INFRASTRUCTURE VALIDATION
======================================================================

Running: Configuration... ✅ PASS
Running: Database Connection... ✅ PASS
Running: Schema Integrity... ✅ PASS
Running: PRAGMA Settings... ✅ PASS
Running: Data Models... ✅ PASS
Running: Transaction Isolation... ✅ PASS
Running: Index Performance... ✅ PASS
Running: Error Handling... ✅ PASS

======================================================================
✅ ALL VALIDATIONS PASSED
======================================================================
```

### Step 2: Test Worker Integration

```python
from Client.Backend.src.queue import QueueDatabase
from Client.Backend.src.queue.validation import validate_worker_integration

db = QueueDatabase("/tmp/test_queue.db")
db.initialize_schema()

# Test your worker ID
assert validate_worker_integration(db, "your-worker-id")
```

### Step 3: Run Your Unit Tests

```bash
cd Client/Backend
python -m pytest _meta/tests/Backend/test_your_feature.py -v
```

---

## Performance Guidelines

### Expected Performance Targets

Based on Issue #337 benchmarking:

| Operation | Target | Notes |
|-----------|--------|-------|
| Task Enqueue | <10ms | Single task insert |
| Task Claim | <5ms | Atomic claim operation |
| Task Update | <5ms | Status or result update |
| Queue Stats | <50ms | COUNT queries with indexes |
| Throughput | 200-400 tasks/min | With 4-6 concurrent workers |

### Optimizing Your Queries

1. **Use indexes**: All common queries should use existing indexes
2. **Limit result sets**: Always use LIMIT for potentially large queries
3. **Avoid subqueries**: Use JOINs or CTEs instead when possible
4. **Batch operations**: Group multiple inserts/updates when possible

---

## Getting Help

### From Worker 01 (Backend Engineer)

**Areas of Support**:
- Database schema questions
- PRAGMA configuration issues
- Transaction isolation problems
- Performance optimization
- Code review feedback

**How to Request Help**:
1. Open an issue with label `worker-01-support`
2. Include code snippet showing the problem
3. Include error messages if any
4. Mention which integration pattern you're using

### From Documentation (Worker 08)

For documentation questions:
- API documentation: `Client/Backend/src/queue/QUEUE_API.md`
- Scheduling strategies: `Client/Backend/src/queue/SCHEDULING_STRATEGIES.md`
- Configuration: `Client/Backend/src/queue/config.py`
- Core README: `Client/Backend/src/queue/README.md`

### From Research (Worker 09)

For performance questions:
- Benchmarking results: Issue #337
- Concurrency tuning: Issue #337
- Performance expectations: `Client/Backend/src/queue/config.py`

---

## Integration Timeline

### Week 2-3: Parallel Development

| Worker | Issue | Integration Points | Support Needed |
|--------|-------|-------------------|----------------|
| Worker 02 | #323 | Client API | Enqueue patterns, validation |
| Worker 03 | #325 | Worker Engine | Claim patterns, atomicity |
| Worker 04 | #327 | Scheduling | Strategy selection, performance |
| Worker 05 | #329 | Observability | Query optimization, metrics |
| Worker 06 | #331 | Maintenance | Cleanup patterns, VACUUM |

**Worker 01 is available for code review and support throughout Week 2-3**

---

## Success Criteria

Your integration is complete when:

1. ✅ Validation script passes (all 8 checks)
2. ✅ Worker integration test passes
3. ✅ Your unit tests pass with >80% coverage
4. ✅ Code review approved by Worker 01
5. ✅ No SQLITE_BUSY errors in normal operation
6. ✅ Performance meets targets (see Performance Guidelines)
7. ✅ Documentation updated for your feature

---

## Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| `database.py` | QueueDatabase connection manager |
| `models.py` | Task, Worker, TaskLog data models |
| `schema.py` | Database schema SQL |
| `config.py` | Production PRAGMA settings |
| `exceptions.py` | Custom exception classes |
| `scheduling.py` | Task claiming strategies |
| `validation.py` | Integration validation tools |

### Key Classes

| Class | Purpose |
|-------|---------|
| `QueueDatabase` | Main database interface |
| `Task` | Task data model |
| `TaskClaimerFactory` | Create scheduling strategies |
| `QueueValidator` | Validation and testing |

### Key Functions

| Function | Purpose |
|----------|---------|
| `quick_validate()` | Quick validation check |
| `validate_worker_integration()` | Test worker integration |
| `get_default_db_path()` | Get platform DB path |
| `apply_pragmas()` | Apply PRAGMA settings |

---

## Version History

- **v1.0.0** (2025-11-05): Initial version
  - Validation tools
  - Integration patterns
  - Code review checklist
  - Common pitfalls

---

**Created by**: Worker 01 - Backend Engineer  
**For**: Workers 02-06 (Phase 2 Integration)  
**Status**: Active Support (Week 2-3)
