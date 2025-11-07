# Issue Organization: Client On-Demand Architecture

## Overview

This document organizes the work completed for implementing on-demand architecture in the Client project. It breaks down the implementation into separate tickets for better tracking and identifies work that belongs in worker/workers components.

## Issue Categories

### 1. Client-Specific Issues (UI, API, On-Demand Communication)

These issues are specific to the Client project managing UI, API, and background communications triggered on-demand.

#### ISSUE-001: Remove Automatic Periodic Tasks from Client Backend
**Component**: Backend/src/main.py  
**Type**: Breaking Change  
**Priority**: High  
**Status**: ✅ Completed

**Description**:
Remove automatic periodic task execution from the Client backend to ensure all operations are triggered on-demand by UI requests.

**Changes**:
- Remove `PeriodicTaskManager` instantiation
- Remove automatic registration of `MAINTENANCE_TASKS`
- Update startup logging to indicate on-demand mode

**Acceptance Criteria**:
- ✅ No periodic tasks start automatically on server startup
- ✅ Server logs "Background operations configured for on-demand execution only"
- ✅ All existing functionality remains intact

**Dependencies**: None

---

#### ISSUE-002: Add On-Demand Maintenance API Endpoints
**Component**: Backend/src/api/system.py  
**Type**: Feature  
**Priority**: High  
**Status**: ✅ Completed

**Description**:
Create REST API endpoints that allow the UI to trigger maintenance operations on-demand instead of running them automatically.

**Changes**:
- Add `POST /api/system/maintenance/cleanup-runs` endpoint
- Add `POST /api/system/maintenance/health-check` endpoint
- Add `POST /api/system/maintenance/cleanup-temp-files` endpoint
- Add `POST /api/system/maintenance/log-statistics` endpoint

**Acceptance Criteria**:
- ✅ All 4 endpoints return appropriate responses
- ✅ Endpoints accept required parameters (e.g., max_age_hours)
- ✅ Operations execute only when endpoints are called
- ✅ Error handling for invalid requests

**Dependencies**: ISSUE-001

---

#### ISSUE-003: Create On-Demand Architecture Documentation
**Component**: Documentation  
**Type**: Documentation  
**Priority**: Medium  
**Status**: ✅ Completed

**Description**:
Document the on-demand architecture principles, endpoints, and migration guide for developers.

**Changes**:
- Create `ONDEMAND_ARCHITECTURE.md` with architecture principles
- Include endpoint documentation with examples
- Provide migration guide for developers
- Update `README.md` to reference on-demand architecture

**Acceptance Criteria**:
- ✅ Complete architecture documentation
- ✅ All endpoints documented with examples
- ✅ Migration guide provided
- ✅ README updated

**Dependencies**: ISSUE-001, ISSUE-002

---

#### ISSUE-004: Add Test Suite for On-Demand Architecture
**Component**: _meta/tests/Backend/integration/  
**Type**: Testing  
**Priority**: High  
**Status**: ✅ Completed

**Description**:
Create comprehensive test suite to validate that the Client follows on-demand architecture principles.

**Changes**:
- Create `test_ondemand_architecture.py`
- Test that no periodic tasks start automatically
- Test all maintenance endpoints work correctly
- Test UI-driven communication pattern
- Verify operations require explicit requests

**Acceptance Criteria**:
- ✅ 6+ tests validating on-demand behavior
- ✅ All tests pass
- ✅ Coverage includes negative tests (no auto-execution)

**Dependencies**: ISSUE-001, ISSUE-002

---

### 2. Worker/Workers Issues (Background Task Execution)

These issues involve actual task execution and should be handled by worker components, not the Client.

#### ISSUE-005: [WORKER] Implement Cleanup Task Worker
**Component**: Worker/Workers (Not Client)  
**Type**: Feature  
**Priority**: Medium  
**Status**: 🔴 Not Started - Belongs in Worker Project

**Description**:
Create a worker component that can execute cleanup operations when triggered by the Client API.

**Scope**:
- Cleanup old runs based on age threshold
- Cleanup temporary files
- Log cleanup statistics
- Handle cleanup errors gracefully

**Acceptance Criteria**:
- Worker can be invoked via task queue or direct call
- Configurable cleanup thresholds
- Returns cleanup results (count of items cleaned)
- Error handling and retry logic

**Recommendation**: This should be implemented in a separate Worker project/module that the Client can invoke via API or task queue.

**Dependencies**: None (independent worker)

---

#### ISSUE-006: [WORKER] Implement Health Check Worker
**Component**: Worker/Workers (Not Client)  
**Type**: Feature  
**Priority**: Medium  
**Status**: 🔴 Not Started - Belongs in Worker Project

**Description**:
Create a worker component that performs comprehensive system health checks when requested.

**Scope**:
- Check memory usage
- Check disk usage
- Check CPU usage
- Check asyncio task counts
- Aggregate health status

**Acceptance Criteria**:
- Worker returns comprehensive health metrics
- Configurable thresholds for warnings
- Works independently of Client
- Can be invoked on-demand

**Recommendation**: This should be implemented in a separate Worker project/module.

**Dependencies**: None (independent worker)

---

#### ISSUE-007: [WORKER] Implement Statistics Logger Worker
**Component**: Worker/Workers (Not Client)  
**Type**: Feature  
**Priority**: Low  
**Status**: 🔴 Not Started - Belongs in Worker Project

**Description**:
Create a worker component that collects and logs system statistics when requested.

**Scope**:
- Collect asyncio task statistics
- Collect system resource statistics
- Log statistics in structured format
- Return statistics to caller

**Acceptance Criteria**:
- Worker collects comprehensive statistics
- Statistics can be logged or returned
- Works independently of Client
- Can be invoked on-demand

**Recommendation**: This should be implemented in a separate Worker project/module.

**Dependencies**: None (independent worker)

---

### 3. Integration Issues (Client ↔ Worker)

These issues involve integrating the Client API with Worker components.

#### ISSUE-008: [INTEGRATION] Connect Client API to Worker Task Queue
**Component**: Backend/src/api/, Worker Integration  
**Type**: Integration  
**Priority**: High  
**Status**: 🔴 Not Started - Future Work

**Description**:
Integrate the Client's on-demand maintenance endpoints with a worker task queue so operations are executed by workers instead of directly in the API handler.

**Scope**:
- Configure task queue (e.g., Redis, RabbitMQ, or database-backed queue)
- Update maintenance endpoints to enqueue tasks instead of executing directly
- Handle task status tracking and results retrieval
- Implement timeout and retry logic

**Acceptance Criteria**:
- Maintenance endpoints enqueue tasks to queue
- Workers pick up and execute tasks
- API can retrieve task status and results
- Error handling for queue failures

**Recommendation**: This is future work after workers are implemented.

**Dependencies**: ISSUE-002, ISSUE-005, ISSUE-006, ISSUE-007

---

#### ISSUE-009: [INTEGRATION] Add Worker Health Monitoring to Client UI
**Component**: Frontend/src/, Backend/src/api/  
**Type**: Feature  
**Priority**: Medium  
**Status**: 🔴 Not Started - Future Work

**Description**:
Add UI components to monitor worker health and trigger maintenance operations from the frontend.

**Scope**:
- Add maintenance panel to dashboard
- Display last maintenance execution times
- Add buttons to trigger maintenance operations
- Show worker health status

**Acceptance Criteria**:
- UI displays maintenance status
- Users can trigger maintenance operations
- Real-time updates of operation status
- Error messages displayed to users

**Recommendation**: This is future work after API endpoints are integrated with workers.

**Dependencies**: ISSUE-002, ISSUE-008

---

## Parallelization Opportunities

### Phase 1: Client-Only Work (Can be parallelized)
These issues can be worked on in parallel as they have minimal dependencies:

**Track A**: Backend Changes
- ISSUE-001: Remove periodic tasks ✅ DONE
- ISSUE-002: Add on-demand endpoints ✅ DONE

**Track B**: Documentation
- ISSUE-003: Create documentation ✅ DONE (can be done while Track A is in progress)

**Track C**: Testing
- ISSUE-004: Add test suite ✅ DONE (can be done after Track A is complete)

### Phase 2: Worker Development (Can be parallelized)
These worker issues are independent and can be developed in parallel:

**Track A**: Cleanup Worker
- ISSUE-005: Implement cleanup worker (independent)

**Track B**: Health Check Worker
- ISSUE-006: Implement health check worker (independent)

**Track C**: Statistics Worker
- ISSUE-007: Implement statistics logger worker (independent)

### Phase 3: Integration (Sequential)
These must be done after workers are complete:

**Sequential Work**:
1. ISSUE-008: Connect Client API to Worker Task Queue
2. ISSUE-009: Add Worker Health Monitoring to Client UI

---

## Recommendations

### 1. Separation of Concerns
**Current State**: ✅ Client now manages only UI, API, and on-demand communications

**Recommendation**: Keep maintenance logic (`Backend/src/core/maintenance.py`) in Client for now, but:
- Move actual worker implementations to a separate Worker project
- Client API should only enqueue tasks, not execute them directly
- Workers should be deployable independently

### 2. Worker Architecture
**Recommendation**: Create a new Worker project structure:
```
Workers/
├── cleanup_worker/
│   ├── main.py
│   └── tasks.py
├── health_worker/
│   ├── main.py
│   └── tasks.py
├── statistics_worker/
│   ├── main.py
│   └── tasks.py
└── shared/
    ├── queue.py
    └── config.py
```

### 3. Task Queue Integration
**Recommendation**: Use existing queue infrastructure in `Backend/src/queue/`:
- Database-backed queue already exists
- Worker support already implemented
- Task handler registry available
- Scheduling strategies available

**Next Steps**:
1. Review `Backend/src/queue/` implementation
2. Determine if it fits worker needs
3. Create worker tasks that use the queue
4. Update Client API to enqueue instead of execute

### 4. API Evolution
**Current State**: API endpoints execute maintenance directly

**Recommendation**: Evolve to async task pattern:
```python
@router.post("/system/maintenance/cleanup-runs")
async def trigger_cleanup_old_runs(max_age_hours: int = 24):
    # Enqueue task instead of executing
    task_id = await queue.enqueue(
        task_type="cleanup_runs",
        payload={"max_age_hours": max_age_hours}
    )
    return {"status": "queued", "task_id": task_id}

@router.get("/system/maintenance/tasks/{task_id}")
async def get_task_status(task_id: int):
    task = await queue.get_task(task_id)
    return {"status": task.status, "result": task.result}
```

### 5. Gradual Migration Path
**Recommendation**: 
1. ✅ **Phase 1 Complete**: Client API endpoints work (synchronous execution)
2. **Phase 2 (Next)**: Implement workers in separate project
3. **Phase 3**: Update Client API to use task queue (async execution)
4. **Phase 4**: Add UI for monitoring worker tasks

This allows incremental adoption without breaking existing functionality.

---

## Current Status Summary

### Completed (Client Work)
- ✅ ISSUE-001: Remove automatic periodic tasks
- ✅ ISSUE-002: Add on-demand maintenance endpoints
- ✅ ISSUE-003: Create on-demand architecture documentation
- ✅ ISSUE-004: Add test suite for on-demand architecture

### Not Started (Worker Work)
- 🔴 ISSUE-005: Implement cleanup task worker
- 🔴 ISSUE-006: Implement health check worker
- 🔴 ISSUE-007: Implement statistics logger worker

### Future Work (Integration)
- 🔴 ISSUE-008: Connect Client API to worker task queue
- 🔴 ISSUE-009: Add worker health monitoring to Client UI

---

## Priority Recommendations

### Immediate Next Steps
1. **Decision**: Determine if workers should be in same repository or separate project
2. **Planning**: Design worker architecture and task queue integration
3. **Implementation**: Start with ISSUE-005 (cleanup worker) as proof of concept

### High Priority
- ISSUE-005: Cleanup worker (most frequently needed)
- ISSUE-008: Task queue integration (enables async execution)

### Medium Priority
- ISSUE-006: Health check worker (useful for monitoring)
- ISSUE-009: Worker monitoring UI (improves user experience)

### Low Priority
- ISSUE-007: Statistics logger worker (nice to have)

---

## Conclusion

The Client implementation is **complete** for Phase 1 (on-demand architecture). The work has been properly separated into:

1. **Client Issues** (✅ Complete): Managing UI, API, and on-demand communications
2. **Worker Issues** (🔴 Not Started): Actual task execution in separate workers
3. **Integration Issues** (🔴 Future): Connecting Client API to worker task queue

This organization allows clear separation of concerns and enables parallel development of independent components.
