# ISSUE-CLIENT-001: Remove Automatic Periodic Tasks from Client Backend

## Status
✅ **COMPLETED**

## Component
Backend/src/main.py

## Type
Breaking Change

## Priority
High

## Description
Remove automatic periodic task execution from the Client backend to ensure all operations are triggered on-demand by UI requests. This aligns with the Client architecture principle that all background operations should be initiated by UI → API requests.

## Problem Statement
The Client backend was automatically starting periodic maintenance tasks (cleanup, health checks, statistics logging) every 5-60 minutes without any user interaction. This violated the design principle that the Client should only manage UI, API, and background communications triggered on-demand.

## Solution
1. Remove `PeriodicTaskManager` instantiation from `main.py`
2. Remove automatic registration of `MAINTENANCE_TASKS`
3. Remove automatic startup of periodic tasks
4. Remove shutdown code for periodic tasks
5. Update startup logging to indicate on-demand mode

## Changes Made
**File**: `Backend/src/main.py`

**Before**:
```python
from .core.periodic_tasks import PeriodicTaskManager
from .core.maintenance import MAINTENANCE_TASKS

# Initialize periodic task manager (global instance)
periodic_task_manager = PeriodicTaskManager()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Registering periodic maintenance tasks...")
    for task_config in MAINTENANCE_TASKS:
        periodic_task_manager.register_task(...)
    periodic_task_manager.start_all()
    
    yield
    
    # Shutdown
    await periodic_task_manager.stop_all(timeout=10.0)
```

**After**:
```python
# Note: Periodic maintenance tasks are now disabled in favor of on-demand execution
# All background operations are triggered via API endpoints based on UI requests
logger.info("Background operations configured for on-demand execution only")
```

## Acceptance Criteria
- [x] No `PeriodicTaskManager` instantiated in main.py
- [x] No periodic tasks start automatically on server startup
- [x] Server logs "Background operations configured for on-demand execution only"
- [x] All existing API functionality remains intact
- [x] Integration tests pass

## Testing
- Verified no periodic task manager in main module
- Confirmed server starts without periodic tasks
- All integration tests pass (5/5)

## Dependencies
None

## Related Issues
- ISSUE-CLIENT-002: Add On-Demand Maintenance API Endpoints
- ISSUE-CLIENT-003: Create On-Demand Architecture Documentation

## Commit
1e767c2 - Disable automatic periodic tasks, enable on-demand maintenance via API

## Notes
- Maintenance functions remain in `Backend/src/core/maintenance.py` for reuse
- `PeriodicTaskManager` class remains available for future use if needed
- This change is backward compatible with existing functionality
