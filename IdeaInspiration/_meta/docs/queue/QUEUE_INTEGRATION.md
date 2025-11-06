# SQLite Queue System - Integration Guide

**Version**: 1.0  
**Status**: Phase 1 Implementation  
**Created**: 2025-11-05  
**Last Updated**: 2025-11-05

---

## Table of Contents

- [Overview](#overview)
- [Integration with BackgroundTaskManager](#integration-with-backgroundtaskmanager)
- [Use Case Examples](#use-case-examples)
- [Migration Strategy](#migration-strategy)
- [Production Deployment](#production-deployment)

---

## Overview

This guide covers integrating the SQLite Queue System with existing PrismQ components and migrating from the current `BackgroundTaskManager` to the persistent queue.

**Integration Goals**:
1. **Backward Compatibility**: Maintain existing API where possible
2. **Gradual Migration**: Support parallel deployment (queue + in-memory)
3. **Zero Downtime**: Migrate without service interruption
4. **Rollback Plan**: Easy rollback if issues arise

---

## Integration with BackgroundTaskManager

### Current Architecture

```python
# Client/Backend/src/core/task_manager.py
class BackgroundTaskManager:
    """Current in-memory task execution."""
    
    def __init__(self, registry: RunRegistry):
        self.registry = registry
        self.tasks = {}  # In-memory task storage
    
    def start_task(self, run: Run, coroutine):
        """Fire-and-forget task execution."""
        task = asyncio.create_task(coroutine)
        self.tasks[run.id] = task
        # ⚠️ Lost on crash!
```

**Limitations**:
- ❌ No persistence (tasks lost on crash)
- ❌ No distributed work (single process)
- ❌ No priority management
- ❌ No retry logic
- ❌ Minimal observability

### Proposed Architecture (Future - Phase 2)

```python
# Client/Backend/src/core/task_manager.py
from queue import QueueDatabase, QueueClient

class BackgroundTaskManager:
    """Queue-backed task execution."""
    
    def __init__(self, registry: RunRegistry, queue: Optional[QueueClient] = None):
        self.registry = registry
        
        if queue:
            self.queue = queue  # Use SQLite queue
        else:
            self.tasks = {}  # Fallback to in-memory
    
    def start_task(self, run: Run, coroutine, priority: int = 100):
        """Enqueue task for persistent execution."""
        if self.queue:
            # Enqueue to SQLite queue
            task_id = self.queue.enqueue(
                type="background_task",
                payload={
                    "run_id": run.id,
                    "coroutine": serialize_coroutine(coroutine)
                },
                priority=priority
            )
            return task_id
        else:
            # Fallback to in-memory
            task = asyncio.create_task(coroutine)
            self.tasks[run.id] = task
            return run.id
```

### Migration Phases

#### Phase 1: Parallel Deployment ✅ Current

**Status**: Core infrastructure implemented

```python
# Both systems coexist
task_manager_legacy = BackgroundTaskManager(registry)  # In-memory
task_manager_queue = BackgroundTaskManager(registry, queue=client)  # Queue-backed

# Route new tasks to queue
task_manager_queue.start_task(run, coroutine)

# Keep old tasks in-memory
task_manager_legacy.start_task(run, coroutine)
```

#### Phase 2: Gradual Migration (Future - Issue #339)

**Status**: Planned

```python
# Route by task type
if task_type in QUEUE_ENABLED_TYPES:
    task_manager_queue.start_task(run, coroutine)
else:
    task_manager_legacy.start_task(run, coroutine)
```

#### Phase 3: Full Migration (Future)

**Status**: Planned

```python
# All tasks use queue
task_manager = BackgroundTaskManager(registry, queue=client)
task_manager.start_task(run, coroutine)
```

---

## Use Case Examples

### Use Case 1: Background Data Processing

**Scenario**: Process video content in background

**Requirements**:
- Persistence: Tasks survive crashes
- Priority: User-initiated > Scheduled
- Retry: Network failures (max 5 attempts)

**Implementation**:

```python
from queue import QueueDatabase, Task
import json

db = QueueDatabase()

# Enqueue video processing task
def enqueue_video_processing(video_id: str, priority: int = 100):
    """Enqueue video processing task."""
    payload = {
        "video_id": video_id,
        "format": "mp4",
        "quality": "1080p"
    }
    
    with db.transaction() as conn:
        cursor = conn.execute("""
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
        """, ("video_processing", json.dumps(payload), priority, 5))
        
        task_id = cursor.lastrowid
    
    return task_id

# User-initiated (high priority)
task_id = enqueue_video_processing("abc123", priority=50)

# Scheduled batch (low priority)
task_id = enqueue_video_processing("def456", priority=200)
```

**Worker Implementation**:

```python
# Worker process
from queue import QueueDatabase, Task
import json
import time

db = QueueDatabase()
worker_id = "worker-video-01"

def process_video(video_id: str, format: str, quality: str):
    """Process video."""
    # Actual processing logic
    print(f"Processing video {video_id}: {format} @ {quality}")
    time.sleep(5)  # Simulate work
    return {"status": "success", "output_path": f"/videos/{video_id}.mp4"}

# Worker loop
while True:
    # Claim next task (priority-based)
    with db.transaction() as conn:
        cursor = conn.execute("""
            SELECT * FROM task_queue
            WHERE status = 'queued'
              AND type = 'video_processing'
              AND run_after_utc <= datetime('now')
            ORDER BY priority ASC, run_after_utc ASC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if row:
            task = Task.from_dict(dict(row))
            
            # Claim with lease
            conn.execute("""
                UPDATE task_queue
                SET status = 'processing',
                    locked_by = ?,
                    lease_until_utc = datetime('now', '+10 minutes'),
                    processing_started_utc = datetime('now')
                WHERE id = ?
            """, (worker_id, task.id))
    
    if row:
        try:
            # Parse payload
            payload = json.loads(task.payload)
            
            # Process
            result = process_video(
                payload["video_id"],
                payload["format"],
                payload["quality"]
            )
            
            # Mark completed
            db.execute("""
                UPDATE task_queue
                SET status = 'completed',
                    finished_at_utc = datetime('now')
                WHERE id = ?
            """, (task.id,))
            
            print(f"✅ Completed task #{task.id}")
            
        except Exception as e:
            # Retry or fail
            if task.attempts + 1 < task.max_attempts:
                # Retry with exponential backoff
                backoff_minutes = 2 ** task.attempts
                db.execute("""
                    UPDATE task_queue
                    SET status = 'queued',
                        attempts = attempts + 1,
                        locked_by = NULL,
                        lease_until_utc = NULL,
                        run_after_utc = datetime('now', ? || ' minutes'),
                        error_message = ?
                    WHERE id = ?
                """, (backoff_minutes, str(e), task.id))
                
                print(f"🔄 Retry task #{task.id} in {backoff_minutes} minutes")
            else:
                # Max attempts reached
                db.execute("""
                    UPDATE task_queue
                    SET status = 'failed',
                        finished_at_utc = datetime('now'),
                        error_message = ?
                    WHERE id = ?
                """, (str(e), task.id))
                
                print(f"❌ Failed task #{task.id}: {e}")
    else:
        # No tasks, sleep
        time.sleep(5)
```

### Use Case 2: User-Initiated Actions (LIFO)

**Scenario**: User clicks "Refresh" - process latest request first

**Requirements**:
- LIFO: Latest request processed first
- Fast: Short lease duration (1 minute)
- Single-attempt: No retries (user can retry manually)

**Implementation**:

```python
# Enqueue user action
def enqueue_user_action(user_id: str, action: str):
    """Enqueue user-initiated action (LIFO)."""
    payload = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.now().isoformat()
    }
    
    with db.transaction() as conn:
        cursor = conn.execute("""
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
        """, ("user_action", json.dumps(payload), 10, 1))  # High priority, no retry
        
        return cursor.lastrowid

# Worker (LIFO order)
cursor = conn.execute("""
    SELECT * FROM task_queue
    WHERE status = 'queued'
      AND type = 'user_action'
    ORDER BY run_after_utc DESC, id DESC  -- LIFO (newest first)
    LIMIT 1
""")
```

### Use Case 3: Scheduled Tasks (Priority)

**Scenario**: Time-sensitive operations with priority levels

**Requirements**:
- Priority: Critical > High > Normal > Low
- Deadline: Must run after specific time
- Idempotency: Prevent duplicate scheduled tasks

**Implementation**:

```python
# Enqueue scheduled task with idempotency key
def enqueue_scheduled_task(task_name: str, priority: int, run_after: datetime):
    """Enqueue scheduled task with idempotency."""
    idempotency_key = f"scheduled:{task_name}:{run_after.isoformat()}"
    
    try:
        with db.transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO task_queue (type, payload, priority, run_after_utc, idempotency_key)
                VALUES (?, ?, ?, ?, ?)
            """, ("scheduled_task", json.dumps({"task": task_name}), 
                  priority, run_after, idempotency_key))
            
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Duplicate idempotency key - task already scheduled
        print(f"Task {task_name} already scheduled for {run_after}")
        return None

# Priority levels
PRIORITY_CRITICAL = 10
PRIORITY_HIGH = 50
PRIORITY_NORMAL = 100
PRIORITY_LOW = 200

# Schedule critical task
enqueue_scheduled_task(
    "daily_backup",
    priority=PRIORITY_CRITICAL,
    run_after=datetime.now() + timedelta(hours=1)
)
```

### Use Case 4: Load Balancing (Weighted Random)

**Scenario**: Distribute work across multiple workers

**Requirements**:
- Load Balancing: No worker starvation
- Fair Distribution: Weighted by priority
- High Throughput: Minimal contention

**Implementation** (Future - Issue #327):

```python
# Worker with weighted random selection
cursor = conn.execute("""
    SELECT * FROM task_queue
    WHERE status = 'queued'
      AND type = ?
    ORDER BY RANDOM()  -- Weighted random (future: add priority weights)
    LIMIT 1
""", ("load_balanced_task",))
```

---

## Migration Strategy

### Pre-Migration Checklist

- [ ] **Backup existing system** (database, code, configs)
- [ ] **Test queue in staging** (dev/test environment)
- [ ] **Identify critical tasks** (which tasks to migrate first)
- [ ] **Monitor metrics** (task throughput, latency, errors)
- [ ] **Prepare rollback plan** (switch back to in-memory if needed)

### Step-by-Step Migration

#### Step 1: Deploy Queue Infrastructure (Week 1)

```bash
# 1. Deploy queue database
cd Client/Backend
python -c "from queue import QueueDatabase; QueueDatabase().initialize_schema()"

# 2. Verify database created
ls -lh C:\Data\PrismQ\queue\queue.db

# 3. Test basic operations
python Client/Backend/src/queue/demo.py
```

#### Step 2: Parallel Deployment (Week 2)

```python
# 1. Initialize both systems
from queue import QueueDatabase, QueueClient
from core.task_manager import BackgroundTaskManager

# Legacy (in-memory)
task_manager_legacy = BackgroundTaskManager(registry)

# Queue (persistent)
db = QueueDatabase()
client = QueueClient(db)  # Future: Issue #323
task_manager_queue = BackgroundTaskManager(registry, queue=client)

# 2. Route specific task types to queue
QUEUE_ENABLED_TYPES = ["video_processing", "batch_classification"]

def start_task(run, coroutine, task_type):
    if task_type in QUEUE_ENABLED_TYPES:
        return task_manager_queue.start_task(run, coroutine)
    else:
        return task_manager_legacy.start_task(run, coroutine)
```

#### Step 3: Gradual Rollout (Week 3)

```python
# Increase percentage of tasks routed to queue
import random

QUEUE_ROLLOUT_PERCENTAGE = 50  # Start with 50%

def start_task(run, coroutine, task_type):
    # Route based on percentage
    if random.random() < QUEUE_ROLLOUT_PERCENTAGE / 100:
        return task_manager_queue.start_task(run, coroutine)
    else:
        return task_manager_legacy.start_task(run, coroutine)

# Gradually increase: 10% -> 25% -> 50% -> 75% -> 100%
```

#### Step 4: Monitor and Validate (Week 4)

```python
# Monitor queue metrics
def get_queue_metrics():
    cursor = db.execute("""
        SELECT 
            status,
            COUNT(*) as count,
            AVG(JULIANDAY(finished_at_utc) - JULIANDAY(processing_started_utc)) * 86400 as avg_duration_sec
        FROM task_queue
        WHERE created_at_utc > datetime('now', '-1 hour')
        GROUP BY status
    """)
    
    for row in cursor:
        print(f"{row['status']}: {row['count']} tasks, avg {row['avg_duration_sec']:.1f}s")

# Alert on issues
def check_queue_health():
    # Check for stuck tasks
    cursor = db.execute("""
        SELECT COUNT(*) as stuck_count
        FROM task_queue
        WHERE status = 'processing'
          AND processing_started_utc < datetime('now', '-10 minutes')
    """)
    
    stuck_count = cursor.fetchone()['stuck_count']
    if stuck_count > 0:
        print(f"⚠️ Warning: {stuck_count} stuck tasks")
    
    # Check SQLITE_BUSY errors
    # (Future: Issue #329 - Observability)
```

#### Step 5: Full Migration (Week 5+)

```python
# Route all tasks to queue
task_manager = BackgroundTaskManager(registry, queue=client)

# Disable legacy system
# task_manager_legacy = None  # Remove in-memory fallback
```

### Rollback Plan

If issues arise, revert to in-memory system:

```python
# 1. Disable queue routing
QUEUE_ENABLED_TYPES = []  # Empty list = no queue routing

# 2. Drain queue (optional)
# Let existing tasks complete, but don't enqueue new ones

# 3. Investigate issues
# - Check logs for errors
# - Review metrics for anomalies
# - Test queue in isolation

# 4. Fix and redeploy
# Once fixed, restart gradual rollout
```

---

## Production Deployment

### Infrastructure Setup

```bash
# 1. Create data directory
mkdir -p C:\Data\PrismQ\queue

# 2. Set permissions (Windows)
icacls C:\Data\PrismQ\queue /grant Users:F

# 3. Configure environment
$env:PRISMQ_QUEUE_DB_PATH = "C:\Data\PrismQ\queue\queue.db"

# 4. Initialize database
python -c "from queue import QueueDatabase; QueueDatabase().initialize_schema()"
```

### Worker Deployment

```bash
# 1. Start worker processes
# Windows (PowerShell)
for ($i=1; $i -le 4; $i++) {
    Start-Process python -ArgumentList "worker.py --id worker-$i" -WindowStyle Hidden
}

# Linux/macOS (systemd or supervisor)
# See _meta/docs/queue/QUEUE_OPERATIONAL_GUIDE.md (Future: Issue #336)
```

### Monitoring Setup

```python
# Prometheus metrics (Future: Issue #329)
from prometheus_client import Gauge, Counter

queue_size = Gauge('queue_size', 'Number of queued tasks')
processing_size = Gauge('queue_processing', 'Number of processing tasks')
completed_total = Counter('queue_completed_total', 'Total completed tasks')
failed_total = Counter('queue_failed_total', 'Total failed tasks')

def update_metrics():
    cursor = db.execute("""
        SELECT status, COUNT(*) as count
        FROM task_queue
        GROUP BY status
    """)
    
    for row in cursor:
        if row['status'] == 'queued':
            queue_size.set(row['count'])
        elif row['status'] == 'processing':
            processing_size.set(row['count'])
```

### Backup and Recovery

```python
# Daily backup (Future: Issue #331)
import sqlite3
from datetime import datetime

def backup_database():
    """Perform online backup."""
    source = sqlite3.connect("C:/Data/PrismQ/queue/queue.db")
    backup_path = f"C:/Backups/PrismQ/queue-{datetime.now().strftime('%Y%m%d')}.db"
    dest = sqlite3.connect(backup_path)
    
    with dest:
        source.backup(dest)
    
    source.close()
    dest.close()
    print(f"✅ Backup created: {backup_path}")

# Schedule daily
# Windows Task Scheduler or Linux cron
```

---

## Best Practices

### 1. Idempotency

```python
# Always use idempotency keys for duplicate prevention
idempotency_key = f"{task_type}:{unique_identifier}"

with db.transaction() as conn:
    try:
        conn.execute("""
            INSERT INTO task_queue (type, payload, idempotency_key)
            VALUES (?, ?, ?)
        """, (task_type, payload, idempotency_key))
    except sqlite3.IntegrityError:
        # Duplicate - task already exists
        pass
```

### 2. Graceful Degradation

```python
# Fallback to in-memory if queue unavailable
try:
    task_id = task_manager_queue.start_task(run, coroutine)
except QueueDatabaseError:
    logger.warning("Queue unavailable, using in-memory fallback")
    task_id = task_manager_legacy.start_task(run, coroutine)
```

### 3. Monitoring and Alerts

```python
# Alert on high failure rate
def check_failure_rate():
    cursor = db.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE status = 'failed') * 100.0 / COUNT(*) as failure_rate
        FROM task_queue
        WHERE created_at_utc > datetime('now', '-1 hour')
    """)
    
    failure_rate = cursor.fetchone()['failure_rate']
    if failure_rate > 5.0:  # >5% failure rate
        send_alert(f"High failure rate: {failure_rate:.1f}%")
```

---

**Document Version**: 1.0  
**Phase**: Phase 1 - Core Infrastructure  
**Status**: Complete  
**Next**: Update with QueueClient/QueueWorker integration (Phase 2)
