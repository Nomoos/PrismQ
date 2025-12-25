# Issue #003: Implement Task Polling Mechanism

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 02 - Python Specialist  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: Critical  
**Duration**: 2 days  
**Dependencies**: #002 (Worker Base Class), #004 (Database Schema)

---

## Worker Details: Worker02 - Python Specialist

**Role**: Task Polling & Claiming Strategies  
**Expertise Required**:
- Python Protocol typing (Python 3.10+)
- SQLite IMMEDIATE transactions
- Algorithm design (FIFO, LIFO, Priority, Weighted Random)
- Backoff mechanisms
- Performance optimization (<10ms target)

**Collaboration**:
- **Worker06** (Database): Coordinate on index design for fast claiming
- **Worker01** (PM): Daily standup, performance benchmarking

**See**: `_meta/issues/new/Worker02/README.md` for complete role description

---

## Objective

Implement a robust task polling mechanism that workers use to continuously check for and claim available tasks from the SQLite queue. This is the core of the worker loop that enables persistent, distributed task execution.

---

## Problem Statement

Workers need to:
1. Continuously poll the queue for available tasks
2. Support different claiming strategies (LIFO, FIFO, PRIORITY, WEIGHTED_RANDOM)
3. Handle edge cases (no tasks available, concurrent claims, database busy)
4. Optimize polling to avoid database thrashing
5. Support graceful shutdown

The polling mechanism must be:
- Efficient (minimal CPU/database load when idle)
- Reliable (no lost tasks, no double-claiming)
- Configurable (poll interval, strategy, timeout)
- Observable (metrics, logging)

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**One Responsibility**: Task polling and claiming coordination

**TaskPoller class**:
- Poll queue for available tasks
- Apply claiming strategy
- Handle polling lifecycle
- Manage polling state

**NOT Responsible For**:
- Task execution (BaseWorker)
- Database schema (QueueDatabase)
- Strategy implementation (ClaimingStrategy classes)

### Open/Closed Principle (OCP) ✅
**Open for Extension**:
- New claiming strategies can be added
- Polling behavior can be customized
- Polling events can be extended

**Closed for Modification**:
- Core polling loop remains stable
- Strategy interface is fixed
- Database interaction is standardized

### Liskov Substitution Principle (LSP) ✅
**Substitutability**:
- All ClaimingStrategy implementations can substitute the base
- Pollers with different strategies behave consistently
- No unexpected behavior changes

### Interface Segregation Principle (ISP) ✅
**Minimal Interface**:
```python
class ClaimingStrategy(Protocol):
    def get_order_by_clause(self) -> str: ...
```

Only the essential method needed for strategy selection.

### Dependency Inversion Principle (DIP) ✅
**Depend on Abstractions**:
- TaskPoller depends on ClaimingStrategy protocol
- Queue connection injected
- Config injected

---

## Proposed Solution

### 1. Define Claiming Strategy Protocol

**File**: `Sources/Content/Shorts/YouTube/src/workers/claiming_strategies.py`

```python
"""Claiming strategies for task queue."""

from typing import Protocol
from abc import ABC, abstractmethod


class ClaimingStrategy(Protocol):
    """Protocol for task claiming strategies.
    
    Following Interface Segregation Principle - minimal interface.
    """
    
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause for this strategy.
        
        Returns:
            SQL ORDER BY clause (without 'ORDER BY' keyword)
        """
        ...


class BaseCla import Strategy(ABC):
    """Base class for claiming strategies with common functionality."""
    
    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause - must be implemented by subclass."""
        pass
    
    def __str__(self) -> str:
        """String representation."""
        return self.__class__.__name__


class FIFOStrategy(BaseClaimStrategy):
    """First-In-First-Out: Oldest tasks first.
    
    Use case: Background jobs, batch processing
    Fairness: High (no starvation)
    """
    
    def get_order_by_clause(self) -> str:
        return "created_at ASC, priority DESC"


class LIFOStrategy(BaseClaimStrategy):
    """Last-In-First-Out: Newest tasks first.
    
    Use case: User-initiated actions, interactive work
    Fairness: Low (old tasks may starve)
    """
    
    def get_order_by_clause(self) -> str:
        return "created_at DESC, priority DESC"


class PriorityStrategy(BaseClaimStrategy):
    """Priority-based: Highest priority first, then FIFO.
    
    Use case: Time-sensitive tasks, SLA requirements
    Fairness: None (low priority may starve)
    """
    
    def get_order_by_clause(self) -> str:
        return "priority DESC, created_at ASC"


class WeightedRandomStrategy(BaseClaimStrategy):
    """Weighted random selection based on priority.
    
    Use case: Load balancing, preventing priority starvation
    Fairness: Medium (probabilistic)
    """
    
    def get_order_by_clause(self) -> str:
        # SQLite RANDOM() with priority weighting
        # Higher priority = more likely to be selected
        return "priority * (1.0 + 0.1 * (10 - RANDOM() % 10)) DESC"


# Strategy registry
STRATEGIES = {
    'FIFO': FIFOStrategy(),
    'LIFO': LIFOStrategy(),
    'PRIORITY': PriorityStrategy(),
    'WEIGHTED_RANDOM': WeightedRandomStrategy(),
}


def get_strategy(name: str) -> BaseClaimStrategy:
    """Get a claiming strategy by name.
    
    Args:
        name: Strategy name (FIFO, LIFO, PRIORITY, WEIGHTED_RANDOM)
        
    Returns:
        Strategy instance
        
    Raises:
        ValueError: If strategy name is unknown
    """
    if name not in STRATEGIES:
        raise ValueError(
            f"Unknown strategy: {name}. "
            f"Valid strategies: {', '.join(STRATEGIES.keys())}"
        )
    return STRATEGIES[name]
```

### 2. Implement Task Poller

**File**: `Sources/Content/Shorts/YouTube/src/workers/task_poller.py`

```python
"""Task polling mechanism for workers."""

import logging
import time
import sqlite3
from typing import Optional, Callable
from datetime import datetime, timezone

from . import Task, TaskStatus
from .claiming_strategies import get_strategy, BaseClaimStrategy


logger = logging.getLogger(__name__)


class TaskPoller:
    """Manages task polling for workers.
    
    Follows Single Responsibility Principle:
    - Polls queue for available tasks
    - Applies claiming strategy
    - Manages polling lifecycle
    
    Does NOT handle:
    - Task execution (worker's job)
    - Database schema (QueueDatabase)
    - Result reporting (worker's job)
    """
    
    def __init__(
        self,
        queue_conn: sqlite3.Connection,
        worker_id: str,
        strategy: str = "LIFO",
        poll_interval: float = 5.0,
        max_idle_polls: int = 12,  # 1 minute at 5s interval
    ):
        """Initialize task poller.
        
        Args:
            queue_conn: SQLite connection to queue database
            worker_id: Unique worker identifier
            strategy: Claiming strategy name
            poll_interval: Seconds between polls when idle
            max_idle_polls: Max consecutive empty polls before backoff
        """
        self.queue_conn = queue_conn
        self.worker_id = worker_id
        self.strategy_name = strategy
        self.strategy = get_strategy(strategy)
        self.poll_interval = poll_interval
        self.max_idle_polls = max_idle_polls
        
        # State
        self.running = False
        self.polls_total = 0
        self.polls_successful = 0
        self.polls_empty = 0
        self.consecutive_empty = 0
        
        logger.info(
            f"TaskPoller initialized for worker {worker_id} "
            f"(strategy: {strategy}, interval: {poll_interval}s)"
        )
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from the queue using configured strategy.
        
        Uses IMMEDIATE transaction for atomic claiming to prevent
        SQLITE_BUSY and double-claiming.
        
        Returns:
            Task if available and claimed, None otherwise
        """
        self.polls_total += 1
        
        try:
            cursor = self.queue_conn.cursor()
            
            # Begin IMMEDIATE transaction (locks database immediately)
            cursor.execute("BEGIN IMMEDIATE")
            
            try:
                # Build query with strategy's ORDER BY
                order_by = self.strategy.get_order_by_clause()
                now_utc = datetime.now(timezone.utc).isoformat()
                
                # Find available task
                query = f"""
                    SELECT id, task_type, parameters, priority, 
                           status, retry_count, max_retries, created_at
                    FROM task_queue
                    WHERE status = 'queued'
                      AND (run_after_utc IS NULL OR run_after_utc <= ?)
                    ORDER BY {order_by}
                    LIMIT 1
                """
                
                cursor.execute(query, (now_utc,))
                row = cursor.fetchone()
                
                if not row:
                    # No tasks available
                    cursor.execute("ROLLBACK")
                    self.polls_empty += 1
                    self.consecutive_empty += 1
                    return None
                
                # Claim the task
                task_id = row['id']
                
                update_query = """
                    UPDATE task_queue
                    SET status = 'claimed',
                        claimed_at = ?,
                        claimed_by = ?,
                        updated_at = ?
                    WHERE id = ?
                """
                
                cursor.execute(update_query, (
                    now_utc,
                    self.worker_id,
                    now_utc,
                    task_id
                ))
                
                # Commit transaction
                cursor.execute("COMMIT")
                
                # Log successful claim
                cursor.execute("""
                    INSERT INTO task_logs 
                    (task_id, worker_id, event_type, message, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    task_id,
                    self.worker_id,
                    'claimed',
                    f'Task claimed by {self.worker_id} using {self.strategy_name}',
                    now_utc
                ))
                self.queue_conn.commit()
                
                # Create Task object
                task = Task(
                    id=task_id,
                    task_type=row['task_type'],
                    parameters=eval(row['parameters']),  # Safe: from our DB
                    priority=row['priority'],
                    status=TaskStatus.CLAIMED,
                    retry_count=row['retry_count'],
                    max_retries=row['max_retries'],
                    created_at=row['created_at'],
                    claimed_at=now_utc
                )
                
                # Update stats
                self.polls_successful += 1
                self.consecutive_empty = 0
                
                logger.info(
                    f"Worker {self.worker_id} claimed task {task_id} "
                    f"(type: {task.task_type}, strategy: {self.strategy_name})"
                )
                
                return task
                
            except Exception as e:
                # Rollback on any error
                cursor.execute("ROLLBACK")
                raise
                
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                logger.warning(f"Database busy during claim (will retry): {e}")
                self.polls_empty += 1
                return None
            else:
                logger.error(f"Operational error claiming task: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error claiming task: {e}", exc_info=True)
            self.polls_empty += 1
            return None
    
    def poll_once(
        self,
        on_task: Callable[[Task], None],
        on_idle: Optional[Callable[[], None]] = None
    ) -> bool:
        """Execute one polling iteration.
        
        Args:
            on_task: Callback when task is claimed
            on_idle: Optional callback when no task available
            
        Returns:
            True if task was claimed, False otherwise
        """
        # Try to claim a task
        task = self.claim_task()
        
        if task:
            # Task claimed - invoke callback
            try:
                on_task(task)
                return True
            except Exception as e:
                logger.error(f"Error in on_task callback: {e}", exc_info=True)
                return False
        else:
            # No task available - invoke idle callback
            if on_idle:
                try:
                    on_idle()
                except Exception as e:
                    logger.warning(f"Error in on_idle callback: {e}")
            
            # Apply backoff if many consecutive empty polls
            if self.consecutive_empty >= self.max_idle_polls:
                backoff_interval = min(
                    self.poll_interval * 2,
                    60.0  # Max 1 minute backoff
                )
                logger.debug(
                    f"Applying backoff: {backoff_interval}s "
                    f"({self.consecutive_empty} consecutive empty polls)"
                )
                time.sleep(backoff_interval)
            else:
                time.sleep(self.poll_interval)
            
            return False
    
    def run(
        self,
        on_task: Callable[[Task], None],
        on_idle: Optional[Callable[[], None]] = None,
        max_iterations: Optional[int] = None
    ):
        """Run the polling loop.
        
        Args:
            on_task: Callback when task is claimed
            on_idle: Optional callback when no task available
            max_iterations: Max iterations (None = infinite)
        """
        self.running = True
        iteration = 0
        
        logger.info(
            f"TaskPoller starting for worker {self.worker_id} "
            f"(strategy: {self.strategy_name})"
        )
        
        try:
            while self.running:
                # Check iteration limit
                if max_iterations and iteration >= max_iterations:
                    logger.info("Max iterations reached, stopping")
                    break
                
                # Poll once
                self.poll_once(on_task, on_idle)
                
                iteration += 1
                
        except KeyboardInterrupt:
            logger.info("Polling interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error in polling loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the polling loop."""
        self.running = False
        logger.info(
            f"TaskPoller stopped for worker {self.worker_id} "
            f"(polls: {self.polls_total}, "
            f"successful: {self.polls_successful}, "
            f"empty: {self.polls_empty})"
        )
    
    def get_stats(self) -> dict:
        """Get polling statistics.
        
        Returns:
            Dictionary with polling metrics
        """
        return {
            'worker_id': self.worker_id,
            'strategy': self.strategy_name,
            'polls_total': self.polls_total,
            'polls_successful': self.polls_successful,
            'polls_empty': self.polls_empty,
            'success_rate': (
                self.polls_successful / self.polls_total 
                if self.polls_total > 0 else 0.0
            ),
            'consecutive_empty': self.consecutive_empty,
            'running': self.running
        }
```

### 3. Update BaseWorker to Use TaskPoller

**File**: `Sources/Content/Shorts/YouTube/src/workers/base_worker.py` (modification)

```python
# Add to BaseWorker class

from .task_poller import TaskPoller

def __init__(self, ...):
    # ... existing init code ...
    
    # Create task poller
    self.poller = TaskPoller(
        queue_conn=self.queue_conn,
        worker_id=self.worker_id,
        strategy=self.strategy,
        poll_interval=getattr(config, 'poll_interval', 5.0)
    )

def claim_task(self) -> Optional[Task]:
    """Claim a task using poller."""
    return self.poller.claim_task()

def run(self, poll_interval: int = 5, max_iterations: Optional[int] = None):
    """Run the worker using poller."""
    
    def on_task(task: Task):
        """Process claimed task."""
        try:
            result = self.process_task(task)
            self.report_result(task, result)
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            result = TaskResult(success=False, error=str(e))
            self.report_result(task, result)
    
    def on_idle():
        """Handle idle state."""
        self._send_heartbeat()
    
    # Run poller
    self.poller.run(
        on_task=on_task,
        on_idle=on_idle,
        max_iterations=max_iterations
    )
```

---

## Implementation Plan

### Step 1: Create Claiming Strategies
- Define `ClaimingStrategy` protocol
- Implement FIFO, LIFO, PRIORITY, WEIGHTED_RANDOM
- Create strategy registry

### Step 2: Implement TaskPoller
- Atomic task claiming with IMMEDIATE transaction
- Strategy-based ORDER BY clause
- Backoff mechanism for idle periods
- Statistics tracking

### Step 3: Update BaseWorker
- Integrate TaskPoller
- Use poller in worker loop
- Handle callbacks

### Step 4: Add Tests
- Test each claiming strategy
- Test atomic claiming (no double-claim)
- Test backoff mechanism
- Test statistics

---

## Acceptance Criteria

- [ ] All 4 claiming strategies implemented (FIFO, LIFO, PRIORITY, WEIGHTED_RANDOM)
- [ ] Atomic claiming prevents double-claiming
- [ ] Backoff mechanism reduces database load when idle
- [ ] Statistics tracking works correctly
- [ ] SQLITE_BUSY handled gracefully
- [ ] TaskPoller integrates with BaseWorker
- [ ] Unit tests with >80% coverage
- [ ] Performance: claiming <10ms (P95)
- [ ] Documentation complete

---

## Testing Strategy

### Unit Tests

**File**: `Sources/Content/Shorts/YouTube/_meta/tests/test_task_poller.py`

```python
import pytest
import sqlite3
from datetime import datetime, timezone
from src.workers.task_poller import TaskPoller
from src.workers.claiming_strategies import get_strategy


def test_fifo_strategy():
    """Test FIFO claims oldest task first."""
    # Setup: Insert 3 tasks with different timestamps
    # Assert: Oldest task is claimed first
    pass


def test_lifo_strategy():
    """Test LIFO claims newest task first."""
    # Setup: Insert 3 tasks with different timestamps
    # Assert: Newest task is claimed first
    pass


def test_priority_strategy():
    """Test PRIORITY claims highest priority first."""
    # Setup: Insert 3 tasks with different priorities
    # Assert: Highest priority claimed first
    pass


def test_atomic_claiming():
    """Test atomic claiming prevents double-claim."""
    # Setup: 2 pollers, 1 task
    # Execute: Both try to claim simultaneously
    # Assert: Only one succeeds
    pass


def test_backoff_mechanism():
    """Test backoff kicks in after consecutive empty polls."""
    # Setup: Poller with max_idle_polls=3
    # Execute: Poll 5 times with no tasks
    # Assert: Backoff applied after 3rd poll
    pass


def test_sqlite_busy_handling():
    """Test graceful handling of SQLITE_BUSY."""
    # Setup: Lock database in another thread
    # Execute: Try to claim
    # Assert: Returns None, logs warning
    pass
```

---

## Files to Create/Modify

**Create**:
1. `Sources/Content/Shorts/YouTube/src/workers/claiming_strategies.py`
2. `Sources/Content/Shorts/YouTube/src/workers/task_poller.py`
3. `Sources/Content/Shorts/YouTube/_meta/tests/test_claiming_strategies.py`
4. `Sources/Content/Shorts/YouTube/_meta/tests/test_task_poller.py`

**Modify**:
5. `Sources/Content/Shorts/YouTube/src/workers/base_worker.py` (integrate poller)

---

## Dependencies

### Requires
- #002: Worker Base Class (BaseWorker must exist)
- #004: Database Schema (task_queue table must exist)

### Enables
- #005: Plugin refactoring (needs working poller)
- #006: Error handling (needs task claiming)
- All plugin migration issues (#009-#012)

---

## Estimated Effort

**2 days**:
- Day 1: Claiming strategies, TaskPoller implementation
- Day 2: BaseWorker integration, tests, documentation

---

## Target Platform

- Windows (primary)
- Python 3.10+
- SQLite 3.35+ (WAL mode, IMMEDIATE transactions)

---

## Related Issues

- **#001**: Master plan (parent)
- **#002**: Worker base class (prerequisite)
- **#004**: Database schema (prerequisite)
- **#005**: Plugin refactor (enabled by this)

---

## Notes

### Design Decisions

1. **Why Protocol for Strategy?**
   - Type-safe interface
   - Easy to add new strategies
   - Testable in isolation

2. **Why IMMEDIATE transaction?**
   - Prevents SQLITE_BUSY during claim
   - Atomic claiming guaranteed
   - Better concurrency than BEGIN

3. **Why Backoff mechanism?**
   - Reduces database load when idle
   - Prevents CPU spinning
   - Scales well with many workers

4. **Why Callbacks in poll_once?**
   - Decouples polling from execution
   - Easier to test
   - Flexible integration

### Performance Considerations

- **Index on (status, priority, created_at)**: Critical for fast claiming
- **WHERE status = 'queued'**: Partial index reduces size
- **LIMIT 1**: Only fetch one task
- **IMMEDIATE transaction**: Faster than deferred

### Future Enhancements

- Dynamic strategy switching
- Multi-task claiming (batching)
- Priority boost for aging tasks
- Advanced scheduling (time-based, dependencies)

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker02 - Python Specialist  
**Estimated Start**: Week 1, Day 3 (after #002)  
**Estimated Completion**: Week 1, Day 5
