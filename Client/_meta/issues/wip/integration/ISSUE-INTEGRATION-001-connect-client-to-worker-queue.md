# ISSUE-INTEGRATION-001: Connect Client API to Worker Task Queue

## Status
🔴 **NOT STARTED** - Future Work

## Component
Backend/src/api/, Backend/src/queue/, Worker Integration

## Type
Integration

## Priority
High

## Description
Integrate the Client's on-demand maintenance endpoints with a worker task queue so operations are executed by workers instead of directly in the API handler. This enables async execution, better scalability, and separation of concerns.

## Problem Statement
Currently, the Client API endpoints execute maintenance operations directly in the API handler:
```python
@router.post("/system/maintenance/cleanup-runs")
async def trigger_cleanup(max_age_hours: int = 24):
    # Executes directly - blocks until complete
    result = await cleanup_old_runs(max_age_hours)
    return result
```

This approach has limitations:
- Blocks API response until operation completes
- Can't scale workers independently
- Limited error handling and retry logic
- Difficult to monitor long-running operations

## Solution
Convert maintenance endpoints to enqueue tasks to a worker queue:
```python
@router.post("/system/maintenance/cleanup-runs")
async def trigger_cleanup(max_age_hours: int = 24):
    # Enqueue task - returns immediately
    task_id = await queue.enqueue(
        task_type="cleanup_runs",
        payload={"max_age_hours": max_age_hours}
    )
    return {"status": "queued", "task_id": task_id}

@router.get("/system/maintenance/tasks/{task_id}")
async def get_task_status(task_id: int):
    # Check task status
    task = await queue.get_task(task_id)
    return {
        "status": task.status,
        "result": task.result,
        "error": task.error_message
    }
```

## Scope

### 1. Update API Endpoints
Convert 4 maintenance endpoints to use task queue:
- POST /api/system/maintenance/cleanup-runs
- POST /api/system/maintenance/health-check
- POST /api/system/maintenance/cleanup-temp-files
- POST /api/system/maintenance/log-statistics

### 2. Add Task Status Endpoints
Create new endpoints for task tracking:
- GET /api/system/maintenance/tasks/{task_id} - Get task status and result
- GET /api/system/maintenance/tasks - List recent tasks
- DELETE /api/system/maintenance/tasks/{task_id} - Cancel task

### 3. Configure Queue Integration
Set up queue database and configuration:
- Use existing `Backend/src/queue/database.py`
- Configure task types and handlers
- Set retry policies and timeouts

### 4. Update Documentation
Update on-demand architecture docs with async pattern

## Implementation Plan

### Phase 1: Queue Setup
```python
# Backend/src/queue/config.py
MAINTENANCE_TASK_TYPES = {
    "cleanup_runs": {
        "max_attempts": 3,
        "timeout": 300,  # 5 minutes
        "priority": 5
    },
    "health_check": {
        "max_attempts": 2,
        "timeout": 30,
        "priority": 3
    },
    "cleanup_temp_files": {
        "max_attempts": 3,
        "timeout": 300,
        "priority": 5
    },
    "log_statistics": {
        "max_attempts": 2,
        "timeout": 10,
        "priority": 1
    }
}
```

### Phase 2: Update Endpoints
```python
# Backend/src/api/system.py
from ..queue import QueueDatabase

@router.post("/system/maintenance/cleanup-runs", response_model=TaskResponse)
async def trigger_cleanup_old_runs(
    max_age_hours: int = 24,
    db: QueueDatabase = Depends(get_queue_db)
):
    """Enqueue cleanup task."""
    task_id = await db.enqueue_task(
        task_type="cleanup_runs",
        payload={"max_age_hours": max_age_hours},
        priority=5
    )
    return TaskResponse(
        task_id=task_id,
        status="queued",
        message="Cleanup task enqueued"
    )

@router.get("/system/maintenance/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: int,
    db: QueueDatabase = Depends(get_queue_db)
):
    """Get task status and result."""
    task = await db.get_task(task_id)
    return TaskStatusResponse(
        task_id=task.id,
        status=task.status,
        result=task.result,
        error_message=task.error_message,
        created_at=task.created_at_utc,
        finished_at=task.finished_at_utc
    )
```

### Phase 3: Response Models
```python
# Backend/src/models/maintenance.py
from pydantic import BaseModel
from typing import Optional

class TaskResponse(BaseModel):
    task_id: int
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: int
    status: str  # queued, leased, completed, failed
    result: Optional[dict]
    error_message: Optional[str]
    created_at: str
    finished_at: Optional[str]
```

## Acceptance Criteria
- [ ] All 4 maintenance endpoints enqueue tasks instead of executing directly
- [ ] Endpoints return task_id immediately
- [ ] Task status endpoint returns current status and result
- [ ] Workers can claim and execute tasks
- [ ] Retry logic works for failed tasks
- [ ] Task results are persisted and retrievable
- [ ] Error messages captured for failed tasks
- [ ] Timeout handling for long-running tasks
- [ ] Integration tests pass
- [ ] Documentation updated

## Testing Strategy

### Unit Tests
- Test endpoint returns task_id
- Test task enqueuing with correct parameters
- Test task status retrieval

### Integration Tests
- End-to-end: enqueue → worker executes → retrieve result
- Test retry on failure
- Test timeout handling
- Test concurrent task execution

### Load Tests
- Multiple simultaneous task submissions
- Worker scaling under load

## Dependencies
- ISSUE-CLIENT-002: Add On-Demand Maintenance API Endpoints (✅ Complete)
- ISSUE-WORKER-001: Implement Cleanup Task Worker (🔴 Not Started)
- ISSUE-WORKER-002: Implement Health Check Worker (🔴 Not Started)

## Related Issues
- ISSUE-CLIENT-005: Add Worker Health Monitoring to Client UI (future)

## Migration Strategy

### Option 1: Gradual Migration (Recommended)
1. Keep direct execution endpoints as default
2. Add async endpoints with `/async` suffix
3. Test async endpoints in production
4. Switch UI to use async endpoints
5. Remove direct execution endpoints

### Option 2: Big Bang Migration
1. Update all endpoints to use queue
2. Deploy workers simultaneously
3. Update frontend to poll for results

**Recommendation**: Use Option 1 for safer migration.

## Backward Compatibility
- Maintain synchronous execution as fallback
- Add feature flag: `USE_TASK_QUEUE=true/false`
- Document both sync and async patterns

## Performance Considerations
- Queue operations should be fast (<50ms)
- Task status endpoint should be cacheable
- Consider WebSocket for real-time status updates
- Add task TTL to prevent database growth

## Monitoring
- Track task queue depth
- Monitor task completion times
- Alert on high failure rates
- Dashboard showing task statistics

## Next Steps
1. Review existing `Backend/src/queue/` implementation
2. Confirm queue schema supports maintenance tasks
3. Implement task status endpoints
4. Update maintenance endpoints to enqueue tasks
5. Test with workers (ISSUE-WORKER-001, ISSUE-WORKER-002)
6. Update frontend to handle async pattern (ISSUE-CLIENT-005)
7. Deploy and monitor in production

## Notes
- Queue database already exists at `Backend/src/queue/database.py`
- Worker support already implemented in `Backend/src/queue/worker.py`
- Task handler registry available in `Backend/src/queue/task_handler_registry.py`
- Consider using existing infrastructure instead of creating new
