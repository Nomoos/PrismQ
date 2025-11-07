# ISSUE-327: Scheduling Strategies - FIFO, LIFO, Priority, Weighted

## Status
✅ **IMPLEMENTED** (2025-11-05)

## Worker Assignment
**Worker 04**: Algorithm Engineer (Algorithms, SQL, Performance)

## Phase
Phase 2 (Week 2-3) - Implementation

## Component
Backend/src/queue/strategies.py, claimer.py

## Type
Feature - Scheduling Algorithms

## Priority
High - Core functionality

## Description
Implement multiple scheduling strategies for task claiming: FIFO, LIFO, Priority-based, and Weighted strategies.

## Problem Statement
Different use cases require different task ordering:
- FIFO: Process oldest tasks first (default)
- LIFO: Process newest tasks first (stack behavior)
- Priority: High-priority tasks before low-priority
- Weighted: Combine priority with age

## Solution
Strategy pattern with multiple implementations:
1. FIFO Strategy (First In, First Out)
2. LIFO Strategy (Last In, First Out)
3. Priority Strategy (High priority first)
4. Weighted Strategy (Priority + Age weighting)

## Implementation Details

### Strategy Interface
```python
class ClaimStrategy(ABC):
    @abstractmethod
    def build_claim_query(self, worker_id: str) -> str:
        """Build SQL query for claiming next task"""
        pass

class FIFOStrategy(ClaimStrategy):
    def build_claim_query(self, worker_id):
        return """
            SELECT * FROM task_queue
            WHERE status = 'queued'
            AND (run_after_utc IS NULL OR run_after_utc <= ?)
            ORDER BY created_at_utc ASC
            LIMIT 1
        """

class PriorityStrategy(ClaimStrategy):
    def build_claim_query(self, worker_id):
        return """
            SELECT * FROM task_queue
            WHERE status = 'queued'
            AND (run_after_utc IS NULL OR run_after_utc <= ?)
            ORDER BY priority DESC, created_at_utc ASC
            LIMIT 1
        """
```

### Implemented Strategies

1. **FIFO (First In, First Out)**
   - Orders by created_at_utc ASC
   - Default strategy
   - Fair processing

2. **LIFO (Last In, First Out)**
   - Orders by created_at_utc DESC
   - Stack-like behavior
   - Useful for cancellation scenarios

3. **Priority**
   - Orders by priority DESC, then created_at_utc ASC
   - High priority tasks first
   - Requires priority field

4. **Weighted**
   - Combines priority and age
   - Formula: score = priority * 10 + age_minutes
   - Prevents starvation of old low-priority tasks

## Acceptance Criteria
- [x] FIFO strategy implemented
- [x] LIFO strategy implemented
- [x] Priority strategy implemented
- [x] Weighted strategy implemented
- [x] Strategy pattern clean
- [x] Configuration system working
- [x] Performance optimized
- [x] Tests passing

## Test Results
- **Performance**: All strategies < 100ms
- **Correctness**: Task ordering validated
- **Flexibility**: Easy to add new strategies

## Dependencies
**Requires**: #321 Core Infrastructure (Worker 01) ✅ COMPLETE

## Enables
- Flexible task scheduling
- Priority handling
- Custom ordering logic

## Related Issues
- #328: Configuration (Worker 04) - Configures strategies
- #325: Worker Engine (Worker 03) - Uses strategies

## Files Modified
- Backend/src/queue/strategies.py (new)
- Backend/src/queue/claimer.py (new)
- Backend/src/queue/worker.py (integrated)
- tests/queue/test_strategies.py (new)

## Parallel Work
**Can run in parallel with**:
- #323: Client API (different code area)
- #325: Worker Engine (different code area)
- #329: Observability (different code area)
- #331: Maintenance (different code area)

## Commits
Week 2-3 implementation commits

## Notes
- Strategy pattern enables easy extension
- SQL-based implementation efficient
- No application-level sorting needed
- New files, no conflicts with other workers
- All strategies leverage database indexes

## Strategy Configuration Example
```python
# Configure strategy
worker = WorkerEngine(
    worker_id="worker-01",
    strategy=PriorityStrategy()
)

# Or use weighted strategy
worker = WorkerEngine(
    worker_id="worker-02",
    strategy=WeightedStrategy(priority_weight=10)
)
```

---

**Created**: Week 2 (2025-11-05)  
**Completed**: Week 2-3 (2025-11-05)  
**Duration**: ~1 week  
**Success**: ✅ Implemented successfully
