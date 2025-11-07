# ISSUE-WORKER-002: Implement Health Check Worker

## Status
🔴 **NOT STARTED** - Belongs in Worker/Workers Project

## Component
Worker/Workers (Not Client)

## Type
Feature

## Priority
Medium

## Description
Create a worker component that performs comprehensive system health checks when requested by the Client API. This worker should collect system metrics, evaluate health status, and return results via task queue.

## Problem Statement
The Client currently executes health checks directly in the API handler. For better separation of concerns and to enable more comprehensive health checks without blocking API responses, health check operations should be handled by dedicated workers.

## Solution
Implement a health check worker that:
1. Listens to task queue for health check tasks
2. Collects system metrics (CPU, memory, disk, asyncio tasks)
3. Evaluates health status based on thresholds
4. Returns comprehensive health report
5. Logs health check results

## Proposed Implementation

### Worker Structure
```
Workers/health_worker/
├── main.py          # Worker entry point
├── tasks.py         # Health check task handlers
├── config.py        # Thresholds and configuration
├── collectors.py    # Metric collection utilities
└── requirements.txt # Dependencies (psutil, etc.)
```

### Task Handler Example
```python
# tasks.py
import psutil
from worker_base import TaskHandler

class HealthCheckTask(TaskHandler):
    task_type = "health_check"
    
    async def execute(self, payload: dict) -> dict:
        # Collect system metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent(interval=1)
        
        # Evaluate health
        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Memory check
        health["checks"]["memory"] = {
            "percent_used": memory.percent,
            "status": "ok" if memory.percent < 80 else "warning"
        }
        if memory.percent > 80:
            health["status"] = "warning"
        
        # Disk check
        health["checks"]["disk"] = {
            "percent_used": disk.percent,
            "status": "ok" if disk.percent < 90 else "warning"
        }
        if disk.percent > 90:
            health["status"] = "warning"
        
        # CPU check
        health["checks"]["cpu"] = {
            "percent_used": cpu,
            "status": "ok" if cpu < 90 else "warning"
        }
        if cpu > 90:
            health["status"] = "warning"
        
        return health
```

## Scope
**Metrics to Collect**:
1. Memory usage (percent, available, total)
2. Disk usage (percent, free space)
3. CPU usage (percent, load average)
4. Asyncio task count (if applicable)
5. System uptime
6. Network connectivity (optional)

**Health Evaluation**:
- Compare metrics against configurable thresholds
- Determine overall health status: healthy, warning, error
- Include detailed check results for each metric

**Features**:
- Configurable warning/error thresholds
- Detailed metric collection
- Health status aggregation
- Historical health tracking (optional)
- Alerting on unhealthy status

## Acceptance Criteria
- [ ] Worker collects all specified metrics
- [ ] Worker evaluates health status correctly
- [ ] Configurable thresholds for warnings/errors
- [ ] Returns structured health report
- [ ] Error handling for metric collection failures
- [ ] Worker logs health check results
- [ ] Unit tests for metric collectors
- [ ] Unit tests for health evaluation logic
- [ ] Integration tests with task queue

## Configuration
```python
# config.py
class HealthCheckConfig:
    # Thresholds
    memory_warning_threshold = 80  # percent
    memory_error_threshold = 95
    
    disk_warning_threshold = 90  # percent
    disk_error_threshold = 95
    
    cpu_warning_threshold = 90  # percent
    cpu_error_threshold = 95
    
    tasks_warning_threshold = 100  # count
    tasks_error_threshold = 200
    
    # Collection settings
    cpu_sample_interval = 1.0  # seconds
    
    # Queue settings
    queue_name = "maintenance_tasks"
    task_type = "health_check"
```

## Response Format
```json
{
    "timestamp": "2025-11-06T15:47:26.925603",
    "status": "healthy",
    "checks": {
        "memory": {
            "percent_used": 9.4,
            "available_mb": 7234.5,
            "total_mb": 8000.0,
            "status": "ok"
        },
        "disk": {
            "percent_used": 71.9,
            "free_gb": 45.2,
            "total_gb": 160.0,
            "status": "ok"
        },
        "cpu": {
            "percent_used": 12.5,
            "load_average": [1.2, 1.5, 1.8],
            "status": "ok"
        },
        "asyncio_tasks": {
            "count": 5,
            "status": "ok"
        }
    }
}
```

## Dependencies
**Required**:
- `psutil` - System metrics collection

**Optional**:
- `aiohttp` - Network connectivity checks
- `prometheus_client` - Metrics export

## Related Issues
- ISSUE-CLIENT-002: Add On-Demand Maintenance API Endpoints
- ISSUE-INTEGRATION-001: Connect Client API to Worker Task Queue
- ISSUE-WORKER-001: Implement Cleanup Task Worker

## Integration with Client
**Before** (Current):
```python
# Client executes directly
@router.post("/system/maintenance/health-check")
async def trigger_health_check():
    health = await check_system_health()
    return health
```

**After** (With Worker):
```python
# Client enqueues task
@router.post("/system/maintenance/health-check")
async def trigger_health_check():
    task_id = await queue.enqueue(
        task_type="health_check",
        payload={}
    )
    return {"status": "queued", "task_id": task_id}

# Get health check result
@router.get("/system/maintenance/tasks/{task_id}")
async def get_task_result(task_id: int):
    task = await queue.get_task(task_id)
    return task.result
```

## Recommendations

### 1. Metric Collection
- Use `psutil` for cross-platform metrics
- Cache metrics briefly to avoid excessive sampling
- Handle collection errors gracefully (return "unknown" status)
- Consider platform-specific optimizations

### 2. Health Evaluation
- Use configurable thresholds
- Support multiple severity levels (ok, warning, error)
- Aggregate status (worst status wins)
- Include all check details in response

### 3. Alerting (Optional)
- Send alerts when status changes from healthy to warning/error
- Rate limit alerts to avoid spam
- Include metric details in alert

### 4. Historical Tracking (Future)
- Store health check results in database
- Display health trends over time
- Alert on degrading trends

## Next Steps
1. Implement basic health check worker
2. Test metric collection on target platforms
3. Tune thresholds based on actual system behavior
4. Integrate with task queue
5. Update Client API to use worker
6. Add UI for displaying health status (ISSUE-CLIENT-005)

## Notes
- Worker should handle missing psutil gracefully
- Consider different thresholds for different environments (dev vs prod)
- Health checks should be fast (<5 seconds)
- Use existing `Backend/src/core/maintenance.py::check_system_health()` as reference
