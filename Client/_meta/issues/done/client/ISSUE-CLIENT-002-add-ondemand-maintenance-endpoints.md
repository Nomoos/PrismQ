# ISSUE-CLIENT-002: Add On-Demand Maintenance API Endpoints

## Status
✅ **COMPLETED**

## Component
Backend/src/api/system.py

## Type
Feature

## Priority
High

## Description
Create REST API endpoints that allow the UI to trigger maintenance operations on-demand instead of running them automatically. This enables UI-driven background operations while maintaining the Client's on-demand architecture principle.

## Problem Statement
After removing automatic periodic tasks (ISSUE-CLIENT-001), maintenance operations need to be available via API endpoints so the UI can trigger them when needed.

## Solution
Add four new POST endpoints to the system API that wrap existing maintenance functions:
1. Cleanup old runs
2. System health check
3. Cleanup temporary files
4. Log statistics

## Changes Made
**File**: `Backend/src/api/system.py`

**Added Endpoints**:

### 1. POST /api/system/maintenance/cleanup-runs
```python
@router.post("/system/maintenance/cleanup-runs")
async def trigger_cleanup_old_runs(
    max_age_hours: int = 24,
    runner: ModuleRunner = Depends(get_module_runner)
):
    cleanup_count = await cleanup_old_runs(
        max_age_hours=max_age_hours,
        registry=runner.registry
    )
    return {
        "status": "success",
        "runs_cleaned": cleanup_count,
        "max_age_hours": max_age_hours
    }
```

### 2. POST /api/system/maintenance/health-check
```python
@router.post("/system/maintenance/health-check")
async def trigger_system_health_check():
    health = await check_system_health()
    return health
```

### 3. POST /api/system/maintenance/cleanup-temp-files
```python
@router.post("/system/maintenance/cleanup-temp-files")
async def trigger_cleanup_temp_files(max_age_hours: int = 24):
    cleanup_count = await cleanup_temp_files(max_age_hours=max_age_hours)
    return {
        "status": "success",
        "files_cleaned": cleanup_count,
        "max_age_hours": max_age_hours
    }
```

### 4. POST /api/system/maintenance/log-statistics
```python
@router.post("/system/maintenance/log-statistics")
async def trigger_log_statistics():
    stats = await log_statistics()
    return stats
```

## Acceptance Criteria
- [x] All 4 endpoints respond with appropriate data
- [x] Endpoints accept required parameters (e.g., max_age_hours)
- [x] Operations execute only when endpoints are called
- [x] Error handling for invalid requests
- [x] Endpoints return structured JSON responses

## Testing
**Manual Testing**:
```bash
✅ POST /api/system/maintenance/cleanup-runs - 200 OK
✅ POST /api/system/maintenance/health-check - 200 OK
✅ POST /api/system/maintenance/cleanup-temp-files - 200 OK
✅ POST /api/system/maintenance/log-statistics - 200 OK
```

**Integration Testing**:
- All on-demand architecture tests pass (6/6)
- Endpoints verified in `test_ondemand_architecture.py`

## Usage Example
**Frontend Code**:
```typescript
// User clicks "Clean Old Data" button
const response = await axios.post('/api/system/maintenance/cleanup-runs', {
  max_age_hours: 24
});
console.log('Cleaned up:', response.data.runs_cleaned);
```

## Dependencies
- ISSUE-CLIENT-001: Remove Automatic Periodic Tasks

## Related Issues
- ISSUE-CLIENT-003: Create On-Demand Architecture Documentation
- ISSUE-CLIENT-004: Add Test Suite for On-Demand Architecture
- ISSUE-WORKER-001: Implement Cleanup Task Worker (future)

## Commit
1e767c2 - Disable automatic periodic tasks, enable on-demand maintenance via API

## Notes
- Endpoints currently execute maintenance functions directly (synchronous)
- Future enhancement: Convert to async task queue pattern (see ISSUE-INTEGRATION-001)
- All maintenance functions imported from `Backend/src/core/maintenance.py`
- Error handling uses FastAPI's exception handling middleware
