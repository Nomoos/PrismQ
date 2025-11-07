# ISSUE-339: Integration - BackgroundTaskManager Adapter

## Status
⏳ **PLANNED** - Ready to Start

## Worker Assignment
**Worker 10**: Senior Engineer (Integration, Architecture)

## Phase
Phase 3 (Week 4) - Integration & Testing

## Component
Backend/src/core/task_manager.py (integration layer)

## Type
Feature - Integration

## Priority
High - Required for production use

## Description
Create integration layer (QueuedTaskManager) that adapts the new queue system to work with existing BackgroundTaskManager interface, enabling transparent migration.

## Problem Statement
Current system uses BackgroundTaskManager interface:
- Existing code depends on this interface
- Need backward compatibility during migration
- Want gradual rollout capability
- Must maintain existing behavior

## Solution
Create QueuedTaskManager adapter that:
1. Implements BackgroundTaskManager interface
2. Delegates to new queue system
3. Maintains backward compatibility
4. Enables gradual migration
5. Provides feature parity

## Implementation Details

### Adapter Pattern
```python
class QueuedTaskManager(BackgroundTaskManager):
    """Adapter: BackgroundTaskManager → Queue System"""
    
    def __init__(self, queue: QueueDatabase):
        self.queue = queue
        self.handler_registry = TaskHandlerRegistry()
    
    async def register_task(self, task_type: str, handler: Callable):
        """Register task handler (compatibility)"""
        self.handler_registry.register(task_type, handler)
    
    async def schedule_task(self, task_type: str, payload: dict, **kwargs):
        """Schedule task (delegates to queue.enqueue)"""
        return await self.queue.enqueue(
            type=task_type,
            payload=payload,
            priority=kwargs.get("priority", 5),
            run_after=kwargs.get("run_after")
        )
    
    async def get_task_status(self, task_id: str):
        """Get status (delegates to queue.poll)"""
        return await self.queue.poll(task_id)
    
    async def cancel_task(self, task_id: str):
        """Cancel task (delegates to queue.cancel)"""
        return await self.queue.cancel(task_id)
```

### Interface Compatibility
```python
# Old interface (BackgroundTaskManager)
manager = BackgroundTaskManager()
await manager.schedule_task("cleanup_runs", {"max_age_hours": 24})

# New interface (QueuedTaskManager) - same API
manager = QueuedTaskManager(queue)
await manager.schedule_task("cleanup_runs", {"max_age_hours": 24})
```

### Migration Strategy
```python
# Phase 1: Add adapter (backward compatible)
# Old code continues to work
manager = QueuedTaskManager(queue)

# Phase 2: Gradual migration
# New code can use queue directly
task_id = await queue.enqueue(type="cleanup_runs", payload={})

# Phase 3: Remove old interface
# All code uses queue system
```

## Integration Points

### 1. Task Registration
- Map old handler registration to new registry
- Support both sync and async handlers
- Maintain handler lifecycle

### 2. Task Scheduling
- Convert schedule_task calls to enqueue
- Map parameters (priority, delay, etc.)
- Return compatible task IDs

### 3. Status Queries
- Map get_task_status to poll
- Convert response format
- Maintain error handling

### 4. Cancellation
- Map cancel_task to queue.cancel
- Handle cancellation states
- Maintain compatibility

## Acceptance Criteria
- [ ] QueuedTaskManager adapter created
- [ ] Implements BackgroundTaskManager interface
- [ ] All methods delegated correctly
- [ ] Backward compatibility maintained
- [ ] Existing tests pass with adapter
- [ ] New tests for adapter added
- [ ] Migration guide written
- [ ] Integration tests passing

## Dependencies
**Requires**: 
- #321-#332: All Phase 2 features ✅ COMPLETE
- #333: Testing results ⏳ PENDING (for validation)

**Blocked By**: 
- Partial: Waiting for #333 testing to validate
- Can start planning and design now

## Blocks
- #340: Migration utilities (Worker 10)
- Production deployment
- Complete system integration

## Related Issues
- #340: Migration (Worker 10) - Dependent issue
- All Phase 2 issues - Integrates their work
- #336: Operations Guide (Worker 08) - Needs integration docs

## Parallel Work
**Cannot run in parallel with**:
- #340: Migration (same worker, depends on this)

**Can run in parallel with**:
- #333-#334: Testing (different focus)
- #335-#336: Documentation (different area)

## Files to Create/Modify
```
Backend/src/core/
├── task_manager.py (modify - add adapter)
├── queued_task_manager.py (new - adapter implementation)
└── background_task_manager.py (existing - interface)

Backend/src/queue/
└── integration.py (new - integration helpers)

tests/integration/
├── test_queued_task_manager.py (new)
├── test_backward_compatibility.py (new)
└── test_migration_scenarios.py (new)
```

## Integration Testing

### Test Scenarios
```python
@pytest.mark.integration
async def test_backward_compatibility():
    """Verify old code works with new adapter"""
    manager = QueuedTaskManager(queue)
    
    # Old-style usage should work
    task_id = await manager.schedule_task(
        "cleanup_runs",
        {"max_age_hours": 24}
    )
    
    status = await manager.get_task_status(task_id)
    assert status["status"] in ["queued", "completed"]

@pytest.mark.integration
async def test_handler_registration():
    """Verify handler registration compatibility"""
    manager = QueuedTaskManager(queue)
    
    # Register handler old-style
    await manager.register_task("test_task", test_handler)
    
    # Execute via new queue system
    task_id = await queue.enqueue(type="test_task", payload={})
    
    # Verify execution
    result = await wait_for_completion(task_id)
    assert result["status"] == "completed"
```

## Migration Path

### Phase 1: Add Adapter (Week 4, Days 1-2)
```python
# Install adapter
from core.queued_task_manager import QueuedTaskManager

# Replace old manager
# OLD: manager = BackgroundTaskManager()
# NEW: manager = QueuedTaskManager(queue)
```

### Phase 2: Validate (Week 4, Day 3)
- Run all existing tests
- Verify backward compatibility
- Check performance parity

### Phase 3: Documentation (Week 4, Day 4)
- Integration guide
- Migration procedures
- Rollback steps

### Phase 4: Rollout (Post Week 4)
- Deploy to staging
- Monitor integration
- Production deployment

## Rollback Plan

### If Integration Fails
1. Keep old BackgroundTaskManager available
2. Configuration toggle between old/new
3. Can switch back instantly
4. No data loss (queue independent)

### Configuration Toggle
```python
# config.py
USE_QUEUE_SYSTEM = os.getenv("USE_QUEUE_SYSTEM", "false") == "true"

if USE_QUEUE_SYSTEM:
    manager = QueuedTaskManager(queue)
else:
    manager = BackgroundTaskManager()  # Old system
```

## Performance Considerations

### Overhead
- Adapter adds minimal overhead (<1ms)
- Queue system more efficient overall
- Better monitoring and observability
- Improved reliability (retry, recovery)

### Benefits
- Persistent task queue
- Better failure handling
- Horizontal scaling
- Task prioritization

## Timeline
- **Week 4, Day 1**: Design and adapter skeleton
- **Week 4, Day 2**: Implementation
- **Week 4, Day 3**: Testing and validation
- **Week 4, Day 4**: Documentation
- **Week 4, Day 5**: Integration testing with #333
- **Week 4, Day 6-7**: Polish and review

## Notes
- High-priority work for Week 4
- Enables production deployment
- Maintains backward compatibility
- Low-risk integration approach
- Can roll back if needed
- Coordinate with Worker 07 testing

---

**Created**: Week 4 (Planned)  
**Status**: ⏳ Ready to start  
**Blockers**: None - can start  
**Priority**: High
