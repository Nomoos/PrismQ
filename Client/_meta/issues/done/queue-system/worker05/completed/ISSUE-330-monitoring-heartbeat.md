# ISSUE-330: Monitoring and Heartbeat - Worker Health Tracking

## Status
✅ **COMPLETE** (2025-11-05)

## Worker Assignment
**Worker 05**: DevOps/Monitoring (SQL, Metrics, Logging)

## Phase
Phase 2 (Week 2-3) - Implementation

## Component
Backend/src/queue/monitoring.py, heartbeat.py

## Type
Feature - Monitoring and Health Tracking

## Priority
High - Required for reliable operations

## Description
Implement worker monitoring and heartbeat mechanism to track worker health and detect failures.

## Problem Statement
Need to:
- Track active workers
- Detect worker failures
- Reclaim abandoned tasks
- Monitor worker health
- Alert on issues

## Solution
Monitoring system with:
1. Worker heartbeat mechanism
2. Failure detection
3. Task reclamation
4. Worker registry
5. Health tracking

## Implementation Details

### Heartbeat Mechanism
```python
class WorkerHeartbeat:
    def __init__(self, worker_id, interval=30):
        self.worker_id = worker_id
        self.interval = interval
    
    async def start(self):
        while self.running:
            await self.send_heartbeat()
            await asyncio.sleep(self.interval)
    
    async def send_heartbeat(self):
        await db.update_worker_heartbeat(
            worker_id=self.worker_id,
            timestamp=utc_now()
        )
```

### Failure Detection
```python
async def detect_failed_workers():
    # Find workers with stale heartbeats
    stale_threshold = utc_now() - timedelta(minutes=2)
    
    failed_workers = await db.query("""
        SELECT worker_id FROM worker_registry
        WHERE last_heartbeat < ?
        AND status = 'active'
    """, [stale_threshold])
    
    return failed_workers

async def reclaim_abandoned_tasks(worker_id):
    # Reset tasks claimed by failed worker
    await db.update("""
        UPDATE task_queue
        SET status = 'queued', claimed_by = NULL
        WHERE claimed_by = ? AND status = 'claimed'
    """, [worker_id])
```

### Worker Registry
```sql
CREATE TABLE worker_registry (
    worker_id TEXT PRIMARY KEY,
    status TEXT DEFAULT 'active',
    last_heartbeat TEXT,
    tasks_processed INTEGER DEFAULT 0,
    started_at TEXT,
    metadata TEXT
);
```

## Acceptance Criteria
- [x] Heartbeat mechanism working
- [x] Failure detection accurate
- [x] Task reclamation functional
- [x] Worker registry maintained
- [x] Health tracking complete
- [x] Tests passing
- [x] Integration with #329

## Test Results
- **Integration**: Works with #329 Observability
- **Reliability**: Detects failures within 2 minutes
- **Recovery**: Tasks reclaimed successfully

## Dependencies
**Requires**: 
- #321 Core Infrastructure (Worker 01) ✅ COMPLETE
- #329 Observability (Worker 05) ✅ COMPLETE

## Enables
- Reliable task execution
- Automatic failure recovery
- Worker health monitoring
- Operational visibility

## Related Issues
- #329: Observability (same worker)
- #325: Worker Engine (Worker 03) - Uses heartbeat
- #326: Retry Logic (Worker 03) - Complements this

## Files Modified
- Backend/src/queue/monitoring.py (new)
- Backend/src/queue/heartbeat.py (new)
- Backend/src/queue/worker.py (integrated)
- Backend/src/queue/schema.py (added worker_registry table)
- tests/queue/test_monitoring.py (new)

## Commits
Week 2-3 implementation commits

## Notes
- Heartbeat interval configurable (default 30s)
- Failure detection threshold 2x heartbeat interval
- Automatic task reclamation prevents task loss
- Worker registry tracks all workers
- Part of 69 tests in #329 observability suite

## Monitoring Examples

### Worker Registration
```python
# Worker registers on startup
worker = WorkerEngine(worker_id="worker-01")
await worker.register()

# Start heartbeat
heartbeat = WorkerHeartbeat(worker.id)
await heartbeat.start()
```

### Failure Detection
```python
# Monitor for failures
monitor = WorkerMonitor()
failed = await monitor.detect_failed_workers()

for worker_id in failed:
    logger.warning("worker_failed", worker_id=worker_id)
    await monitor.reclaim_tasks(worker_id)
    await monitor.mark_worker_failed(worker_id)
```

### Health Dashboard
```json
{
  "active_workers": 3,
  "failed_workers": 1,
  "workers": [
    {
      "id": "worker-01",
      "status": "active",
      "last_heartbeat": "2025-11-05T10:15:30Z",
      "tasks_processed": 142
    },
    {
      "id": "worker-02",
      "status": "failed",
      "last_heartbeat": "2025-11-05T10:10:00Z",
      "tasks_processed": 89
    }
  ]
}
```

---

**Created**: Week 2 (2025-11-05)  
**Completed**: Week 2-3 (2025-11-05)  
**Duration**: Part of Week 2-3  
**Success**: ✅ Complete, integrated with observability
