# Issue #339: Integrate SQLite Queue with BackgroundTaskManager

**Parent Issue**: #320 (SQLite Queue Analysis)  
**Worker**: Worker 10 - Senior Engineer  
**Status**: Planning (Phase 1) ✅ COMPLETE  
**Priority**: High  
**Duration**: 1 week (Phase 3 - Week 4)  
**Dependencies**: ✅ #321 (COMPLETE), #323, #325, #327, #329, #331 (Phase 2 components)

---

## Objective

Create a seamless integration layer between the new SQLite queue system and the existing `BackgroundTaskManager`, ensuring backward compatibility while enabling gradual migration to the persistent queue architecture.

---

## Phase 1 Planning (Week 1) - This Document

This document represents Worker 10's **Phase 1 deliverable**: comprehensive planning and integration design for the SQLite queue system integration.

### Planning Scope

1. **Architecture Analysis** - Document current vs. future state
2. **Integration Strategy** - Define the compatibility layer approach  
3. **Migration Path** - Plan gradual transition strategy
4. **Risk Assessment** - Identify integration challenges
5. **Acceptance Criteria** - Define success metrics
6. **Implementation Roadmap** - Breakdown work for Phase 3

---

## Current State Analysis

### Existing BackgroundTaskManager Architecture

**Location**: `Client/Backend/src/core/task_manager.py`  
**Implementation Status**: ✅ **Completed** (Issue #310 - November 2025)

**Key Features**:
- Fire-and-forget task execution
- In-memory task tracking via `RunRegistry`
- Status updates (QUEUED → RUNNING → COMPLETED/FAILED/CANCELLED)
- Task cancellation support
- Graceful shutdown with `wait_all()`
- Exception handling and logging
- Task observability helpers (`get_active_task_count()`, `get_active_task_ids()`, `is_task_active()`)

**Current Data Flow**:
```
Client/UI → BackgroundTaskManager.start_task() → asyncio.create_task()
                                                        ↓
                                               In-memory execution
                                                        ↓
                                               RunRegistry updates
```

**Limitations**:
- ❌ No persistence (tasks lost on crash)
- ❌ Single process only (no distributed work)
- ❌ No retry logic
- ❌ No priority management
- ❌ Limited observability

### Current Integration Points

**1. TaskOrchestrator** (`task_orchestrator.py`)
- Implementation Status: ✅ **Completed** (Issue #313 - November 2025)
- Unified interface for all task patterns
- Lazily loads `BackgroundTaskManager`
- Provides pattern-based execution
- Integrates all 6 patterns from BACKGROUND_TASKS_BEST_PRACTICES.md

**2. Run Model** (`models/run.py`)
- `Run` object with status tracking
- `RunStatus` enum: QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
- Parameters, timestamps, error messages

**3. RunRegistry** (`run_registry.py`)
- In-memory storage of Run objects
- Status updates and queries
- No persistence layer

**4. API Endpoints**
- `POST /api/modules/{module_id}/run` - Start module execution
- `GET /api/runs/{run_id}` - Get run status
- `POST /api/runs/{run_id}/cancel` - Cancel run

---

## Proposed Architecture

### Future State with SQLite Queue

**New Components** (from Phase 2):
- `queue/database.py` - SQLite connection and schema (#321)
- `api/queue_endpoints.py` - Enqueue/poll/cancel APIs (#323)
- `queue/worker.py` - Task claiming and execution engine (#325)
- `queue/strategies.py` - FIFO/LIFO/Priority scheduling (#327)
- `queue/observability.py` - Metrics and monitoring (#329)
- `queue/maintenance.py` - Backup and cleanup (#331)

**New Data Flow**:
```
Client/UI → QueueClient.enqueue() → SQLite task_queue table
                                            ↓
                                    Worker.claim_task() (atomic lease)
                                            ↓
                                    Worker.execute_task()
                                            ↓
                                    Worker.finalize_task()
                                            ↓
                                    SQLite status update
```

**Benefits**:
- ✅ Persistence (survives crashes)
- ✅ Multi-process workers
- ✅ Retry with exponential backoff
- ✅ Priority/FIFO/LIFO scheduling
- ✅ Rich observability

---

## Integration Strategy

### Option A: Direct Replacement (High Risk)

**Approach**: Replace `BackgroundTaskManager` entirely with SQLite queue

**Pros**:
- Clean architecture
- Full feature set immediately
- No dual code paths

**Cons**:
- ❌ **Breaking change** - requires updating all callers
- ❌ High risk of bugs
- ❌ No rollback path
- ❌ "Big bang" deployment

**Verdict**: ❌ **NOT RECOMMENDED**

### Option B: Adapter Pattern (Recommended)

**Approach**: Create `QueuedTaskManager` that implements the same interface as `BackgroundTaskManager` but uses SQLite queue underneath

**Pros**:
- ✅ Backward compatible
- ✅ Gradual migration
- ✅ Feature flag toggle
- ✅ Easy rollback
- ✅ Preserve existing API

**Cons**:
- Temporary dual code paths
- Slightly more complex initially

**Verdict**: ✅ **RECOMMENDED**

### Option C: Hybrid Mode (Maximum Flexibility)

**Approach**: Support both in-memory and persistent queues with runtime selection

**Pros**:
- ✅ Maximum flexibility
- ✅ Use in-memory for dev, persistent for prod
- ✅ A/B testing capability

**Cons**:
- More complex configuration
- Longer maintenance burden

**Verdict**: ✅ **RECOMMENDED as enhancement to Option B**

---

## Detailed Design: Adapter Pattern

### 1. QueuedTaskManager Class

**File**: `Client/Backend/src/core/queued_task_manager.py` (new)

**Interface Compatibility**:
```python
class QueuedTaskManager:
    """
    Drop-in replacement for BackgroundTaskManager using SQLite queue.
    
    Implements same interface as BackgroundTaskManager but persists
    tasks to SQLite queue and uses worker processes for execution.
    """
    
    def __init__(self, queue_client: QueueClient, registry: RunRegistry):
        """
        Initialize queued task manager.
        
        Args:
            queue_client: Client for SQLite queue operations
            registry: RunRegistry for backward compatibility
        """
        self.queue_client = queue_client
        self.registry = registry
    
    def start_task(self, run: Run, coro: Awaitable) -> str:
        """
        Start task by enqueueing to SQLite queue.
        
        Maps Run object to queue task format and enqueues.
        Returns run_id immediately (fire-and-forget).
        
        Args:
            run: Run object with task metadata
            coro: Coroutine to execute (serialized as task payload)
            
        Returns:
            Run ID for tracking
        """
        # Convert Run + coroutine to queue task format
        task = self._run_to_task(run, coro)
        
        # Enqueue to SQLite
        task_id = self.queue_client.enqueue(task)
        
        # Update registry (optional, for backward compat)
        self.registry.update_run(run)
        
        return run.run_id
    
    async def cancel_task(self, run_id: str) -> bool:
        """
        Cancel task by updating queue status.
        
        Args:
            run_id: Run identifier
            
        Returns:
            True if cancelled, False if not found or already completed
        """
        return await self.queue_client.cancel_task(run_id)
    
    async def wait_all(self) -> None:
        """
        Wait for all queued tasks to complete.
        
        Polls queue until no tasks remain in QUEUED or RUNNING status.
        """
        await self.queue_client.wait_until_empty()
    
    def get_active_task_count(self) -> int:
        """
        Get the number of currently active tasks.
        
        Returns:
            Number of tasks in QUEUED or RUNNING status
        """
        return self.queue_client.get_active_count()
    
    def get_active_task_ids(self) -> List[str]:
        """
        Get IDs of all active tasks.
        
        Returns:
            List of run IDs for tasks in QUEUED or RUNNING status
        """
        return self.queue_client.get_active_task_ids()
    
    def is_task_active(self, run_id: str) -> bool:
        """
        Check if a task is currently active.
        
        Args:
            run_id: Run ID to check
            
        Returns:
            True if task is QUEUED or RUNNING, False otherwise
        """
        return self.queue_client.is_task_active(run_id)
    
    def _run_to_task(self, run: Run, coro: Awaitable) -> Task:
        """
        Convert Run object + coroutine to queue Task format.
        
        Maps Run model fields to queue task_queue schema.
        Serializes coroutine as executable payload.
        """
        # Implementation in Phase 3
        pass
```

**Key Design Decisions**:

1. **Coroutine Serialization Challenge**
   - Problem: Can't pickle arbitrary coroutines
   - Solution: Serialize module path + parameters instead
   - Approach: `{"module": "Sources.youtube", "method": "search", "params": {...}}`

2. **Status Synchronization**
   - Queue worker updates SQLite task_queue status
   - QueuedTaskManager polls for status changes
   - Updates RunRegistry for backward compatibility

3. **Error Handling**
   - Queue worker captures exceptions
   - Stores in task_queue.error_message
   - QueuedTaskManager propagates to Run object

### 2. Configuration Toggle

**File**: `Client/Backend/src/core/config.py`

**Feature Flag**:
```python
class TaskExecutionConfig:
    """Configuration for task execution backend."""
    
    # Feature flag: "in-memory" or "queue"
    TASK_BACKEND: Literal["in-memory", "queue"] = "in-memory"
    
    # SQLite queue database path (if queue backend)
    QUEUE_DB_PATH: str = "C:/Data/queue/queue.db"
    
    # Fallback to in-memory on queue errors
    QUEUE_FALLBACK_ENABLED: bool = True
```

### 3. Factory Pattern

**File**: `Client/Backend/src/core/task_manager_factory.py` (new)

```python
def create_task_manager(config: TaskExecutionConfig) -> Union[BackgroundTaskManager, QueuedTaskManager]:
    """
    Factory method to create task manager based on configuration.
    
    Args:
        config: Task execution configuration
        
    Returns:
        BackgroundTaskManager (in-memory) or QueuedTaskManager (persistent)
    """
    registry = RunRegistry()
    
    if config.TASK_BACKEND == "queue":
        try:
            queue_client = QueueClient(db_path=config.QUEUE_DB_PATH)
            return QueuedTaskManager(queue_client, registry)
        except Exception as e:
            if config.QUEUE_FALLBACK_ENABLED:
                logger.warning(f"Queue init failed, falling back to in-memory: {e}")
                return BackgroundTaskManager(registry)
            raise
    else:
        return BackgroundTaskManager(registry)
```

### 4. TaskOrchestrator Integration

**File**: `Client/Backend/src/core/task_orchestrator.py` (modify)

**Change**:
```python
def _get_task_manager(self):
    """Lazy load task manager (in-memory or queue)."""
    if self._task_manager is None:
        from .task_manager_factory import create_task_manager
        from .config import TaskExecutionConfig
        
        config = TaskExecutionConfig()
        self._task_manager = create_task_manager(config)
    return self._task_manager
```

**Impact**: Zero change to callers - TaskOrchestrator transparently uses queue backend when configured

---

## API Compatibility Layer

### Queue Task Schema to Run Object Mapping

**SQLite task_queue columns → Run object fields**:

| task_queue Column | Run Object Field | Notes |
|-------------------|------------------|-------|
| `id` | `run_id` (convert to string) | SQLite autoincrement → string ID |
| `type` | `module_id` | Task type maps to module ID |
| `status` | `status` | Map queue statuses to RunStatus enum |
| `payload` | `parameters` | JSON payload → parameters dict |
| `created_at_utc` | `created_at` | Direct mapping |
| `processing_started_utc` | `started_at` | Direct mapping |
| `finished_at_utc` | `completed_at` | Direct mapping |
| `error_message` | `error_message` | Direct mapping |
| `attempts` | N/A | Queue-specific, not in Run model |
| `priority` | N/A | Queue-specific, could extend Run |

**Status Mapping**:

| Queue Status | RunStatus Enum | Notes |
|--------------|----------------|-------|
| `queued` | `QUEUED` | Direct mapping |
| `leased` | `RUNNING` | Worker claimed, now executing |
| `completed` | `COMPLETED` | Success |
| `failed` | `FAILED` | Max retries exceeded |
| `cancelled` | `CANCELLED` | User cancellation |

### Polling Mechanism

**Challenge**: Queue workers update SQLite, but API needs to know status changes

**Solution 1: Polling** (Simple)
```python
async def get_run_status(run_id: str) -> Run:
    """Poll queue for task status."""
    task = await queue_client.get_task(run_id)
    return _task_to_run(task)
```

**Solution 2: Webhooks** (Future Enhancement)
- Worker posts status updates to callback URL
- API receives push notifications
- Lower latency, more complex

**Phase 3 Approach**: Start with polling (Solution 1), document webhook hook points for future

---

## Migration Strategy

### Phase 3 Implementation Plan (Week 4)

**Day 1-2: Core Adapter**
- [ ] Create `QueuedTaskManager` class
- [ ] Implement `start_task()` with queue enqueue
- [ ] Implement `cancel_task()` with queue cancel
- [ ] Implement `wait_all()` with queue polling
- [ ] Create `_run_to_task()` and `_task_to_run()` converters

**Day 3-4: Configuration & Factory**
- [ ] Create `TaskExecutionConfig` with feature flag
- [ ] Create `task_manager_factory.py`
- [ ] Update `TaskOrchestrator._get_task_manager()`
- [ ] Add fallback logic for queue initialization errors

**Day 5: Integration Testing**
- [ ] Test with `TASK_BACKEND="queue"`
- [ ] Verify backward compatibility with existing API
- [ ] Test failover to in-memory mode
- [ ] Performance benchmarking (queue vs in-memory)

**Day 6-7: Documentation & Rollback**
- [ ] Update architecture docs
- [ ] Create migration guide (see #340)
- [ ] Document rollback procedure
- [ ] Code review with Workers 1-6

### Gradual Rollout Plan

**Week 1 (Phase 3)**: Development environment only
- Enable `TASK_BACKEND="queue"` in dev
- Test all API endpoints
- Monitor for issues

**Week 2**: Staging environment
- Deploy to staging with queue backend
- Run smoke tests
- Performance testing

**Week 3**: Production canary (10% traffic)
- Route 10% of task requests to queue backend
- Monitor error rates, latency
- Compare with in-memory baseline

**Week 4**: Production rollout (100%)
- If canary successful, route 100% to queue
- Keep in-memory fallback enabled
- Monitor for 1 week

**Week 5**: Cleanup
- If stable, remove in-memory code paths (optional)
- Or keep hybrid mode for flexibility

---

## Risk Assessment

### Integration Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Coroutine serialization fails** | Medium | High | Use module path + params instead of pickle |
| **Status mapping edge cases** | Medium | Medium | Comprehensive test coverage for all statuses |
| **Performance regression** | Low | High | Benchmark queue vs in-memory, optimize queries |
| **SQLite locking issues** | Medium | High | Use WAL mode, busy_timeout, test under load |
| **Queue worker crashes** | Medium | Medium | Retry logic (#326), heartbeat monitoring (#329) |
| **Migration breaks existing API** | Low | Critical | Adapter pattern preserves interface, thorough testing |
| **Data loss on crash** | Low | Critical | SQLite ACID guarantees, regular backups (#331) |

### Contingency Plans

**If Queue Backend Fails**:
1. Feature flag toggle: Set `TASK_BACKEND="in-memory"`
2. Restart service (no code changes needed)
3. In-memory mode resumes immediately

**If Serialization Issues**:
1. Start with simple module calls (module path + params)
2. Phase 2: Add support for more complex coroutines if needed
3. Document supported task types

**If Performance Issues**:
1. Tune SQLite pragmas (Worker 09's research #337)
2. Add caching layer for frequently polled tasks
3. Optimize SQL queries with proper indexes

---

## Acceptance Criteria

### Functional Requirements

- [ ] `QueuedTaskManager` implements same interface as `BackgroundTaskManager`
- [ ] Feature flag toggles between in-memory and queue backends
- [ ] All existing API endpoints work unchanged with queue backend
- [ ] Task status updates propagate from queue to API responses
- [ ] Task cancellation works via queue cancel operation
- [ ] Graceful shutdown waits for queue tasks to complete

### Non-Functional Requirements

- [ ] **Backward Compatibility**: Zero API changes for existing callers
- [ ] **Performance**: Queue backend latency ≤ 2x in-memory backend
- [ ] **Reliability**: Queue backend error rate ≤ 0.1% under normal load
- [ ] **Observability**: All queue operations logged and monitored
- [ ] **Rollback Time**: ≤ 5 minutes to switch back to in-memory mode
- [ ] **Test Coverage**: ≥ 90% coverage for adapter layer

### Integration Test Scenarios

1. **Happy Path**
   - Start task with queue backend
   - Poll status until completed
   - Verify result matches in-memory behavior

2. **Cancellation**
   - Start task with queue backend
   - Cancel before completion
   - Verify task status = CANCELLED

3. **Error Handling**
   - Start task that raises exception
   - Verify status = FAILED
   - Verify error_message populated

4. **Fallback**
   - Simulate queue initialization failure
   - Verify fallback to in-memory mode
   - Verify tasks execute successfully

5. **Multi-Process**
   - Enqueue 10 tasks
   - Start 3 worker processes
   - Verify all tasks complete
   - Verify no duplicate execution

6. **Crash Recovery**
   - Enqueue 5 tasks
   - Kill worker mid-execution
   - Restart worker
   - Verify tasks retry and complete

---

## Dependencies

### Requires from Phase 2 Workers

**Worker 01** (#321):
- SQLite schema and database module
- Connection management
- Transaction handling

**Worker 02** (#323):
- `QueueClient.enqueue()` API
- `QueueClient.get_task()` for polling
- `QueueClient.cancel_task()` for cancellation

**Worker 03** (#325):
- Worker engine that executes tasks
- Status updates to SQLite
- Error handling

**Worker 04** (#327):
- Scheduling strategy (default: FIFO acceptable)

**Worker 05** (#329):
- Logging and metrics integration
- Heartbeat monitoring (for worker health)

**Worker 06** (#331):
- Backup utilities (for production readiness)

### Provides to Phase 3

**Worker 07** (#333 - Testing):
- Integration test interfaces
- Test fixtures for queue operations

**Worker 08** (#336 - Documentation):
- Integration architecture diagrams
- API compatibility documentation

**Worker 09** (#337 - Research):
- Performance baselines for comparison

---

## Success Metrics

### Phase 1 Success (This Planning Document)

- [x] Current architecture fully documented
- [x] Integration strategy defined (Adapter Pattern)
- [x] Migration path planned (Gradual Rollout)
- [x] Risks identified and mitigated
- [x] Acceptance criteria defined
- [x] Implementation roadmap created

### Phase 3 Success (Week 4 Implementation)

- [ ] QueuedTaskManager implemented and tested
- [ ] Feature flag configuration working
- [ ] All acceptance criteria met
- [ ] Integration tests passing (≥90% coverage)
- [ ] Performance benchmarks meet targets
- [ ] Documentation updated
- [ ] Ready for staging deployment

---

## Related Documentation

### Dependencies
- [#320 SQLite Queue Analysis](../Infrastructure_DevOps/320-sqlite-queue-analysis-and-design.md)
- [#321 Core Infrastructure](../Worker01/321-implement-sqlite-queue-core-infrastructure.md)
- [#323 Client API](../Worker02/323-implement-queue-client-api.md)
- [#325 Worker Engine](../Worker03/325-implement-queue-worker-engine.md)

### Deliverables
- [#340 Migration Utilities](340-create-migration-utilities-and-rollback-procedures.md)

### References
- [Worker Allocation Matrix](../Infrastructure_DevOps/QUEUE-SYSTEM-PARALLELIZATION.md)
- [Background Tasks Best Practices](../../../Client/Backend/_meta/docs/BACKGROUND_TASKS_BEST_PRACTICES.md)

---

## Notes

### Implementation Status Update (November 2025)

**Completed Components** (All 6 Background Task Patterns):
- ✅ **ExecutionPatterns** (Issue #307) - Simple module execution pattern (Pattern 1)
- ✅ **ExecutionPatterns** (Issue #308) - Long-running task pattern with output streaming (Pattern 2)
- ✅ **ConcurrentExecutor** (Issue #309) - Concurrent execution pattern (Pattern 3)
- ✅ **BackgroundTaskManager** (Issue #310) - Fire-and-forget with tracking (Pattern 4)
- ✅ **PeriodicTaskManager** (Issue #311) - Periodic task execution (Pattern 5)
- ✅ **ResourcePool** (Issue #312) - Resource pooling pattern (Pattern 6)
- ✅ **TaskOrchestrator** (Issue #313) - Integrates all 6 background task patterns

**SQLite Queue Infrastructure** (Phase 1 Foundation):
- ✅ **QueueDatabase** (Issue #321) - Core SQLite infrastructure with schema, models, and connection management
- ✅ **Queue Architecture Docs** (Issue #335) - Comprehensive documentation and API reference
- ✅ **Scheduling Research** (Issue #338) - Performance analysis framework ready

**Impact on Planning**:
- ✅ **All 6 Background Task Patterns** from BACKGROUND_TASKS_BEST_PRACTICES.md are now fully implemented
- ✅ **Phase 1 Foundation Complete** - Core infrastructure (#321) ready for Phase 2 workers
- All current state analysis remains accurate and validated
- BackgroundTaskManager (Pattern 4) has 3 bonus helper methods: `get_active_task_count()`, `get_active_task_ids()`, `is_task_active()`
- QueuedTaskManager adapter design updated to include these helper methods
- Integration points validated against actual implementations
- TaskOrchestrator successfully integrates all 6 patterns
- **Ready for Phase 2** - Workers 02-06 can now begin implementation
- No changes required to core adapter pattern strategy

### Design Principles Applied

This integration follows SOLID principles (from repository guidelines):

- **Single Responsibility**: QueuedTaskManager only adapts interface
- **Open/Closed**: Extends system without modifying existing code
- **Liskov Substitution**: QueuedTaskManager substitutes BackgroundTaskManager
- **Interface Segregation**: Minimal interface (start_task, cancel_task, wait_all)
- **Dependency Inversion**: Depends on QueueClient abstraction

### Future Enhancements

**Post-Phase 3 Improvements**:
1. **Webhook Support**: Push notifications instead of polling
2. **Priority Support**: Extend Run model with priority field
3. **Advanced Retry**: Expose retry configuration in API
4. **Batch Operations**: Enqueue multiple tasks in one call
5. **Task Dependencies**: Support task chains (A → B → C)

**Not in Scope for Phase 3**:
- Distributed workers across multiple hosts (single Windows host for now)
- Real-time streaming of task output (polling sufficient initially)
- Advanced scheduling (cron-like periodic tasks - use PeriodicTaskManager)

---

**Status**: ✅ Phase 1 Planning Complete  
**Next Phase**: Integration planning during Week 2-3  
**Implementation**: Week 4 (after all Phase 2 components ready)  
**Owner**: Worker 10 - Senior Engineer
