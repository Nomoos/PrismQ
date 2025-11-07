# ISSUE-WORKER-001: Implement Cleanup Task Worker

## Status
🔴 **NOT STARTED** - Belongs in Worker/Workers Project

## Component
Worker/Workers (Not Client)

## Type
Feature

## Priority
Medium

## Description
Create a worker component that can execute cleanup operations when triggered by the Client API. This worker should run independently of the Client and handle cleanup tasks via a task queue.

## Problem Statement
The Client currently executes cleanup operations directly in the API handler. For better separation of concerns and scalability, cleanup operations should be handled by dedicated workers that:
- Run independently of the Client
- Can be scaled horizontally
- Execute tasks from a queue
- Handle errors and retries

## Solution
Implement a cleanup worker that:
1. Listens to a task queue for cleanup tasks
2. Executes cleanup operations (old runs, temp files)
3. Returns results to the Client
4. Handles errors with retry logic

## Proposed Implementation

### Worker Structure
```
Workers/cleanup_worker/
├── main.py          # Worker entry point
├── tasks.py         # Task handlers
├── config.py        # Worker configuration
└── requirements.txt # Dependencies
```

### Task Handler Example
```python
# tasks.py
from worker_base import TaskHandler

class CleanupRunsTask(TaskHandler):
    task_type = "cleanup_runs"
    
    async def execute(self, payload: dict) -> dict:
        max_age_hours = payload.get("max_age_hours", 24)
        
        # Execute cleanup logic
        cleanup_count = await cleanup_old_runs(max_age_hours)
        
        return {
            "status": "success",
            "runs_cleaned": cleanup_count,
            "max_age_hours": max_age_hours
        }
```

### Worker Entry Point
```python
# main.py
from worker_base import Worker
from tasks import CleanupRunsTask, CleanupTempFilesTask

worker = Worker(
    name="cleanup_worker",
    queue_name="maintenance_tasks"
)

worker.register_handler(CleanupRunsTask())
worker.register_handler(CleanupTempFilesTask())

if __name__ == "__main__":
    worker.start()
```

## Scope
**Operations to Support**:
1. Cleanup old runs based on age threshold
2. Cleanup temporary files based on age threshold
3. Log cleanup statistics
4. Handle cleanup errors gracefully

**Features**:
- Configurable cleanup thresholds
- Error handling with retry logic
- Detailed logging
- Metrics reporting (items cleaned, time taken, errors)
- Graceful shutdown

## Acceptance Criteria
- [ ] Worker can be started independently
- [ ] Worker listens to task queue for cleanup tasks
- [ ] Worker executes cleanup operations correctly
- [ ] Worker returns cleanup results to queue
- [ ] Configurable cleanup thresholds (max_age_hours)
- [ ] Error handling with exponential backoff retry
- [ ] Worker logs all operations
- [ ] Worker can be stopped gracefully
- [ ] Unit tests for task handlers
- [ ] Integration tests with task queue

## Task Queue Integration
**Recommended Approach**: Use existing queue infrastructure in `Backend/src/queue/`
- Task database schema already exists
- Worker support implemented
- Task handler registry available
- Scheduling strategies available

**Queue Schema**:
```sql
CREATE TABLE task_queue (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    payload TEXT,
    status TEXT DEFAULT 'queued',
    max_attempts INTEGER DEFAULT 3,
    attempts INTEGER DEFAULT 0,
    created_at_utc TEXT,
    run_after_utc TEXT,
    ...
)
```

## Configuration
```python
# config.py
class CleanupWorkerConfig:
    queue_name = "maintenance_tasks"
    max_concurrent_tasks = 5
    retry_max_attempts = 3
    retry_backoff_multiplier = 2.0
    default_max_age_hours = 24
    log_level = "INFO"
```

## Dependencies
None (independent worker)

## Related Issues
- ISSUE-CLIENT-002: Add On-Demand Maintenance API Endpoints
- ISSUE-INTEGRATION-001: Connect Client API to Worker Task Queue
- ISSUE-WORKER-002: Implement Health Check Worker

## Integration with Client
**Before** (Current):
```python
# Client executes directly
@router.post("/system/maintenance/cleanup-runs")
async def trigger_cleanup(max_age_hours: int = 24):
    result = await cleanup_old_runs(max_age_hours)
    return result
```

**After** (With Worker):
```python
# Client enqueues task
@router.post("/system/maintenance/cleanup-runs")
async def trigger_cleanup(max_age_hours: int = 24):
    task_id = await queue.enqueue(
        task_type="cleanup_runs",
        payload={"max_age_hours": max_age_hours}
    )
    return {"status": "queued", "task_id": task_id}
```

## Recommendations

### 1. Worker Location
**Option A**: Same repository, separate directory
```
PrismQ.Client/
├── Backend/
├── Frontend/
└── Workers/
    └── cleanup_worker/
```

**Option B**: Separate repository
```
PrismQ.Workers/
└── cleanup_worker/
```

**Recommendation**: Start with Option A for easier development, move to Option B when workers mature.

### 2. Deployment
- Workers should be deployable independently
- Docker container per worker type
- Can scale workers horizontally based on load
- Environment variables for configuration

### 3. Monitoring
- Health check endpoint for worker
- Metrics: tasks processed, errors, processing time
- Logging: structured logs for debugging
- Alerting: notify on repeated failures

## Next Steps
1. Decide on worker architecture (same repo vs separate)
2. Create worker base classes (if not using existing infrastructure)
3. Implement cleanup worker as proof of concept
4. Test worker with existing task queue
5. Update Client API to enqueue tasks (ISSUE-INTEGRATION-001)
6. Deploy and monitor worker in test environment

## Notes
- Worker should be stateless for easy scaling
- Use existing `Backend/src/core/maintenance.py` functions
- Consider using existing `Backend/src/queue/worker.py` infrastructure
- Worker should handle both sync and async cleanup functions
