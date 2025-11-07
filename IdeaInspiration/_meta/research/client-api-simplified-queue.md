# Client API - Simplified Queue Research

**Created**: 2025-11-05  
**Purpose**: Research simplified approach for Client API queue operations  
**Related**: Issue #323 (Worker 02 - Client API)

---

## Overview

This research document explores a **simplified approach** to the Client API for the SQLite-based task queue system. Instead of the comprehensive design outlined in #320, this focuses on the core operations:

1. **Save tasks to database** (enqueue)
2. **Load tasks from database** (query/poll)
3. **Priority-based ordering** (max/increasing priority)

---

## Problem Statement

The full queue design (#320) includes:
- Multiple scheduling strategies (FIFO, LIFO, Priority, Weighted Random)
- Worker engines with lease management
- Comprehensive observability
- Retry logic and dead-letter handling

**Simplification Goal**: Create a minimal viable Client API that focuses on basic persistence and priority-based task retrieval.

---

## Simplified Design

### Core Operations

#### 1. Save Task (Enqueue)

**Purpose**: Persist a task to the database with priority

**API**:
```python
async def enqueue_task(
    task_type: str,
    parameters: dict,
    priority: int = 0,
    idempotency_key: Optional[str] = None
) -> str:
    """
    Save a task to the queue database.
    
    Args:
        task_type: Type of task (e.g., "module_run", "content_fetch")
        parameters: Task parameters as JSON
        priority: Task priority (higher = more important)
        idempotency_key: Optional key for deduplication
        
    Returns:
        task_id: Unique identifier for the task
    """
```

**Database Schema**:
```sql
CREATE TABLE task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    task_type TEXT NOT NULL,
    parameters TEXT NOT NULL,  -- JSON
    priority INTEGER DEFAULT 0,
    status TEXT DEFAULT 'queued',  -- queued, running, completed, failed
    idempotency_key TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT
);

CREATE INDEX idx_task_queue_status_priority 
    ON task_queue(status, priority DESC, created_at ASC);
CREATE UNIQUE INDEX idx_task_queue_idempotency 
    ON task_queue(idempotency_key) WHERE idempotency_key IS NOT NULL;
```

**Implementation**:
```python
import sqlite3
import json
from datetime import datetime, timezone
from uuid import uuid4

class SimplifiedQueueClient:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database with schema."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                task_type TEXT NOT NULL,
                parameters TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'queued',
                idempotency_key TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                error_message TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_queue_status_priority 
                ON task_queue(status, priority DESC, created_at ASC)
        """)
        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_task_queue_idempotency 
                ON task_queue(idempotency_key) 
                WHERE idempotency_key IS NOT NULL
        """)
        conn.commit()
        conn.close()
    
    async def enqueue_task(
        self,
        task_type: str,
        parameters: dict,
        priority: int = 0,
        idempotency_key: Optional[str] = None
    ) -> str:
        """Save a task to the queue."""
        task_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Check for duplicate idempotency key
            if idempotency_key:
                cursor = conn.execute(
                    "SELECT task_id FROM task_queue WHERE idempotency_key = ?",
                    (idempotency_key,)
                )
                existing = cursor.fetchone()
                if existing:
                    return existing[0]  # Return existing task_id
            
            # Insert new task
            conn.execute("""
                INSERT INTO task_queue 
                    (task_id, task_type, parameters, priority, idempotency_key, 
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                task_type,
                json.dumps(parameters),
                priority,
                idempotency_key,
                now,
                now
            ))
            conn.commit()
            return task_id
        finally:
            conn.close()
```

#### 2. Load Tasks (Query/Poll)

**Purpose**: Retrieve tasks from database ordered by priority

**API**:
```python
async def get_next_task(
    task_types: Optional[List[str]] = None
) -> Optional[dict]:
    """
    Get the next highest-priority queued task.
    
    Args:
        task_types: Optional filter for specific task types
        
    Returns:
        Task dict or None if no tasks available
    """
```

**Implementation**:
```python
    async def get_next_task(
        self,
        task_types: Optional[List[str]] = None
    ) -> Optional[dict]:
        """Get next task ordered by priority (highest first)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            query = """
                SELECT task_id, task_type, parameters, priority, created_at
                FROM task_queue
                WHERE status = 'queued'
            """
            params = []
            
            if task_types:
                placeholders = ','.join('?' * len(task_types))
                query += f" AND task_type IN ({placeholders})"
                params.extend(task_types)
            
            query += " ORDER BY priority DESC, created_at ASC LIMIT 1"
            
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                "task_id": row["task_id"],
                "task_type": row["task_type"],
                "parameters": json.loads(row["parameters"]),
                "priority": row["priority"],
                "created_at": row["created_at"]
            }
        finally:
            conn.close()
```

#### 3. Claim Task (Atomic)

**Purpose**: Atomically mark a task as running

**API**:
```python
async def claim_task(task_id: str) -> bool:
    """
    Atomically claim a task for processing.
    
    Args:
        task_id: Task to claim
        
    Returns:
        True if claimed successfully, False if already claimed
    """
```

**Implementation**:
```python
    async def claim_task(self, task_id: str) -> bool:
        """Atomically claim a task."""
        conn = sqlite3.connect(self.db_path)
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            # Use IMMEDIATE transaction for atomicity
            conn.execute("BEGIN IMMEDIATE")
            
            # Try to update if status is still 'queued'
            cursor = conn.execute("""
                UPDATE task_queue 
                SET status = 'running', 
                    started_at = ?,
                    updated_at = ?
                WHERE task_id = ? AND status = 'queued'
            """, (now, now, task_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
```

#### 4. Complete Task

**Purpose**: Mark a task as completed or failed

**API**:
```python
async def complete_task(
    task_id: str,
    status: str,  # "completed" or "failed"
    error_message: Optional[str] = None
) -> None:
    """Mark a task as completed or failed."""
```

**Implementation**:
```python
    async def complete_task(
        self,
        task_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """Mark task as completed or failed."""
        if status not in ["completed", "failed"]:
            raise ValueError(f"Invalid status: {status}")
        
        conn = sqlite3.connect(self.db_path)
        try:
            now = datetime.now(timezone.utc).isoformat()
            conn.execute("""
                UPDATE task_queue
                SET status = ?,
                    completed_at = ?,
                    updated_at = ?,
                    error_message = ?
                WHERE task_id = ?
            """, (status, now, now, error_message, task_id))
            conn.commit()
        finally:
            conn.close()
```

#### 5. Get Task Status

**Purpose**: Query the current status of a task

**API**:
```python
async def get_task_status(task_id: str) -> Optional[dict]:
    """Get current status and details of a task."""
```

**Implementation**:
```python
    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get task status."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute("""
                SELECT task_id, task_type, parameters, priority, status,
                       created_at, started_at, completed_at, error_message
                FROM task_queue
                WHERE task_id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                "task_id": row["task_id"],
                "task_type": row["task_type"],
                "parameters": json.loads(row["parameters"]),
                "priority": row["priority"],
                "status": row["status"],
                "created_at": row["created_at"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
                "error_message": row["error_message"]
            }
        finally:
            conn.close()
```

---

## Priority Ordering Strategy

### Max Increasing Priority

The simplified design uses a straightforward priority ordering:

1. **Higher priority number = Higher importance**
   - Priority 100 > Priority 50 > Priority 0
   
2. **Within same priority, use FIFO (created_at ASC)**
   - Older tasks processed first
   
3. **SQL Ordering**:
   ```sql
   ORDER BY priority DESC, created_at ASC
   ```

**Example**:
```python
# Low priority background task
await queue.enqueue_task("cleanup", {}, priority=0)

# Normal priority user action
await queue.enqueue_task("module_run", {...}, priority=50)

# High priority critical task
await queue.enqueue_task("emergency_stop", {}, priority=100)

# Retrieval order: emergency_stop -> module_run -> cleanup
```

---

## Comparison: Simplified vs Full Design

| Feature | Simplified | Full Design (#320) |
|---------|-----------|-------------------|
| **Scheduling** | Priority only | FIFO, LIFO, Priority, Weighted Random |
| **Worker Management** | Manual claim/complete | Lease-based with heartbeat |
| **Retry Logic** | Not included | Exponential backoff |
| **Dead Letter** | Not included | Automatic after max attempts |
| **Observability** | Basic status only | Logs, metrics, monitoring |
| **Maintenance** | Manual | Automated sweeper, VACUUM |
| **Complexity** | ~200 LOC | ~2000+ LOC |
| **Implementation Time** | 1-2 days | 4 weeks (10 workers) |

---

## Integration with BackgroundTaskManager

### Current Flow
```python
# Current (in-memory)
run = Run(run_id=..., status=RunStatus.QUEUED, ...)
task_manager.start_task(run, my_coroutine())
```

### Proposed Flow with Simplified Queue
```python
# With simplified queue
queue = SimplifiedQueueClient("C:/Data/PrismQ/queue.db")

# Enqueue
task_id = await queue.enqueue_task(
    task_type="module_run",
    parameters={"module_id": "...", "run_id": "..."},
    priority=50
)

# Worker loop
while True:
    task = await queue.get_next_task()
    if task:
        if await queue.claim_task(task["task_id"]):
            try:
                # Execute task
                await execute_module_run(task["parameters"])
                await queue.complete_task(task["task_id"], "completed")
            except Exception as e:
                await queue.complete_task(
                    task["task_id"], "failed", str(e)
                )
    await asyncio.sleep(1)
```

---

## Benefits of Simplified Approach

### Pros ✅
1. **Minimal Code**: ~200 lines vs 2000+ lines
2. **Easy to Understand**: Single file, clear logic
3. **Fast Implementation**: 1-2 days vs 4 weeks
4. **Adequate for Current Needs**: Handles 100-500 tasks/min
5. **Upgradable**: Can enhance later with features from full design

### Cons ⚠️
1. **No Retry Logic**: Must handle externally
2. **No Worker Heartbeat**: Manual health monitoring
3. **No Dead Letter**: Failed tasks stay in queue
4. **Limited Scheduling**: Priority-only (no FIFO/LIFO/Weighted)
5. **Manual Maintenance**: No automated cleanup

---

## When to Upgrade

Consider migrating to full design (#320) when:

- **Throughput** exceeds 500 tasks/min
- **Multiple scheduling strategies** are needed
- **Automated retry and dead-letter** handling required
- **Comprehensive observability** becomes critical
- **High availability** with worker heartbeats needed

---

## Recommendation

**Start with Simplified Approach**:
1. Implement the 5 core operations (200 LOC)
2. Test with current workload (100-200 tasks/min)
3. Monitor for bottlenecks or missing features
4. Upgrade incrementally to full design if needed

**Reasoning**:
- Follows YAGNI principle (You Aren't Gonna Need It)
- Delivers value quickly (1-2 days vs 4 weeks)
- Reduces risk of over-engineering
- Provides learning opportunity before full implementation
- Easy migration path (same database schema)

---

## Next Steps

### Immediate
- [ ] Review this research with team
- [ ] Decide: Simplified vs Full Design
- [ ] Create issue for chosen approach

### If Simplified Approved
- [ ] Implement `SimplifiedQueueClient` (1 day)
- [ ] Write unit tests (0.5 day)
- [ ] Create REST API endpoints (0.5 day)
- [ ] Update BackgroundTaskManager integration (0.5 day)
- [ ] Test with real workload (0.5 day)

**Total**: ~3 days to production

### If Full Design Approved
- Follow the 20-issue plan in #320 (4 weeks)

---

## Conclusion

The simplified Client API approach provides **80% of the value with 20% of the complexity**. It focuses on the core requirement: persistent, priority-based task queuing with database storage.

This research demonstrates that a minimal viable implementation can be achieved quickly while maintaining upgrade path to the comprehensive design if future requirements demand it.

**Recommendation**: Start simple, validate with real usage, upgrade when proven necessary.
