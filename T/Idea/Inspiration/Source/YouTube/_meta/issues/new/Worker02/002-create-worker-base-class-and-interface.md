# Issue #002: Create Worker Base Class and Interface

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 02 - Python Specialist  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: Critical (Foundational)  
**Duration**: 2-3 days  
**Dependencies**: None (First issue to implement)

---

## Worker Details: Worker02 - Python Specialist

**Role**: Core Infrastructure Implementation  
**Expertise Required**: 
- Python 3.10+ (Protocol, TypedDict, dataclasses)
- SOLID principles (especially ISP, DIP)
- Design patterns (Factory, Strategy, Repository)
- SQLite (connection management, transactions)
- Testing (pytest, mocking, fixtures)

**Collaboration**:
- **Worker06** (Database): Coordinate on schema integration (#004)
- **Worker01** (PM): Daily standup, progress reporting

**See**: `_meta/issues/new/Worker02/README.md` for complete role description

---

## Objective

Create a base worker class and protocol (interface) following SOLID principles that will serve as the foundation for all YouTube scraping workers. This establishes the contract that all worker implementations must follow.

---

## Problem Statement

The current YouTube module uses plugins that are not integrated with a worker/queue system. We need to create a worker abstraction that:

1. Defines the interface for worker implementations
2. Provides common functionality (polling, claiming, reporting)
3. Follows SOLID principles (especially ISP and DIP)
4. Integrates with SQLite queue system
5. Supports different scraping modes as task types

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**One Responsibility**: Base worker handles task lifecycle management only
- Task claiming from queue
- Task execution delegation
- Result reporting
- Error handling

**NOT Responsible For**:
- Actual scraping logic (delegated to plugins)
- Database schema (handled by queue system)
- API endpoints (handled by Worker03)

### Open/Closed Principle (OCP) ✅
**Open for Extension**:
- New worker types can extend `BaseWorker`
- New task types can be registered
- New result handlers can be added

**Closed for Modification**:
- Core polling/claiming logic remains stable
- Task lifecycle is standardized
- Base interface doesn't change

### Liskov Substitution Principle (LSP) ✅
**Substitutability**:
- Any `BaseWorker` subclass can be used wherever `WorkerProtocol` is expected
- All workers follow the same lifecycle
- Consistent behavior across implementations

### Interface Segregation Principle (ISP) ✅
**Minimal Interface**:
```python
class WorkerProtocol(Protocol):
    def claim_task(self) -> Optional[Task]: ...
    def process_task(self, task: Task) -> TaskResult: ...
    def report_result(self, task: Task, result: TaskResult) -> None: ...
```

Only essential methods, no unnecessary dependencies.

### Dependency Inversion Principle (DIP) ✅
**Depend on Abstractions**:
- Workers depend on `WorkerProtocol`, not concrete classes
- Queue dependency injected via constructor
- Config dependency injected via constructor

---

## Proposed Solution

### 1. Define Worker Protocol (Interface)

**File**: `Sources/Content/Shorts/YouTube/src/workers/__init__.py`

```python
from typing import Protocol, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """Task execution status."""
    QUEUED = "queued"
    CLAIMED = "claimed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a task from the queue."""
    id: int
    task_type: str  # 'channel_scrape', 'trending_scrape', 'keyword_search'
    parameters: Dict[str, Any]
    priority: int
    status: TaskStatus
    retry_count: int
    max_retries: int
    created_at: str
    claimed_at: Optional[str] = None


@dataclass
class TaskResult:
    """Result of task processing."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    items_processed: int = 0
    metrics: Optional[Dict[str, Any]] = None


class WorkerProtocol(Protocol):
    """Protocol (interface) that all workers must implement.
    
    Following Interface Segregation Principle - minimal interface.
    """
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from the queue using configured strategy.
        
        Returns:
            Task if available, None otherwise
        """
        ...
    
    def process_task(self, task: Task) -> TaskResult:
        """Process a claimed task.
        
        Args:
            task: The task to process
            
        Returns:
            TaskResult with success status and data
        """
        ...
    
    def report_result(self, task: Task, result: TaskResult) -> None:
        """Report task result back to queue and TaskManager API.
        
        Args:
            task: The completed task
            result: The task execution result
        """
        ...
```

### 2. Implement Base Worker Class

**File**: `Sources/Content/Shorts/YouTube/src/workers/base_worker.py`

```python
"""Base worker implementation following SOLID principles."""

import logging
import time
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timezone
from abc import ABC, abstractmethod

from ..core.config import Config
from ..core.database import Database
from . import Task, TaskResult, TaskStatus, WorkerProtocol


logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """Base worker class providing common functionality.
    
    Follows Single Responsibility Principle:
    - Manages task lifecycle
    - Handles polling and claiming
    - Reports results
    
    Does NOT handle:
    - Specific scraping logic (abstract method)
    - Queue implementation (injected dependency)
    - API integration (separate responsibility)
    """
    
    def __init__(
        self,
        worker_id: str,
        queue_db_path: str,
        config: Config,
        results_db: Database,
        strategy: str = "LIFO",
        heartbeat_interval: int = 30,
    ):
        """Initialize worker with injected dependencies (DIP).
        
        Args:
            worker_id: Unique worker identifier
            queue_db_path: Path to SQLite queue database
            config: Configuration object
            results_db: Database for storing results
            strategy: Task claiming strategy (FIFO, LIFO, PRIORITY)
            heartbeat_interval: Seconds between heartbeats
        """
        self.worker_id = worker_id
        self.queue_db_path = queue_db_path
        self.config = config
        self.results_db = results_db
        self.strategy = strategy
        self.heartbeat_interval = heartbeat_interval
        
        # State
        self.running = False
        self.current_task: Optional[Task] = None
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.last_heartbeat = time.time()
        
        # Queue connection (lazy initialization)
        self._queue_conn = None
        
        logger.info(
            f"Worker {self.worker_id} initialized "
            f"(strategy: {self.strategy})"
        )
    
    @property
    def queue_conn(self):
        """Lazy queue connection (one per worker)."""
        if self._queue_conn is None:
            import sqlite3
            self._queue_conn = sqlite3.connect(
                self.queue_db_path,
                check_same_thread=False
            )
            self._queue_conn.row_factory = sqlite3.Row
            # Enable WAL mode for concurrent access
            self._queue_conn.execute("PRAGMA journal_mode=WAL")
            self._queue_conn.execute("PRAGMA busy_timeout=5000")
        return self._queue_conn
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from queue using configured strategy.
        
        Implements atomic claiming with IMMEDIATE transaction.
        
        Returns:
            Task if available and claimed, None otherwise
        """
        try:
            # Build ORDER BY clause based on strategy
            if self.strategy == "FIFO":
                order_by = "created_at ASC"
            elif self.strategy == "LIFO":
                order_by = "created_at DESC"
            elif self.strategy == "PRIORITY":
                order_by = "priority DESC, created_at ASC"
            else:
                raise ValueError(f"Unknown strategy: {self.strategy}")
            
            # Atomic claim with IMMEDIATE transaction
            cursor = self.queue_conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            
            try:
                # Find available task
                cursor.execute(f"""
                    SELECT id, task_type, parameters, priority, 
                           status, retry_count, max_retries, created_at
                    FROM task_queue
                    WHERE status = 'queued'
                      AND (run_after_utc IS NULL OR run_after_utc <= ?)
                    ORDER BY {order_by}
                    LIMIT 1
                """, (datetime.now(timezone.utc).isoformat(),))
                
                row = cursor.fetchone()
                if not row:
                    cursor.execute("ROLLBACK")
                    return None
                
                # Claim the task
                task_id = row['id']
                now = datetime.now(timezone.utc).isoformat()
                
                cursor.execute("""
                    UPDATE task_queue
                    SET status = 'claimed',
                        claimed_at = ?,
                        claimed_by = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (now, self.worker_id, now, task_id))
                
                cursor.execute("COMMIT")
                
                # Create Task object
                task = Task(
                    id=task_id,
                    task_type=row['task_type'],
                    parameters=eval(row['parameters']),  # JSON in SQLite
                    priority=row['priority'],
                    status=TaskStatus.CLAIMED,
                    retry_count=row['retry_count'],
                    max_retries=row['max_retries'],
                    created_at=row['created_at'],
                    claimed_at=now
                )
                
                self.current_task = task
                logger.info(
                    f"Worker {self.worker_id} claimed task {task_id} "
                    f"(type: {task.task_type})"
                )
                return task
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise
                
        except Exception as e:
            logger.error(f"Error claiming task: {e}")
            return None
    
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        """Process a claimed task - MUST be implemented by subclass.
        
        This is where the actual scraping logic goes.
        Subclasses implement specific scraping behavior.
        
        Args:
            task: The task to process
            
        Returns:
            TaskResult with success status and data
        """
        pass
    
    def report_result(self, task: Task, result: TaskResult) -> None:
        """Report task result to queue and save data.
        
        Updates:
        1. Queue task status
        2. Results database
        3. TaskManager API (if configured)
        
        Args:
            task: The completed task
            result: The execution result
        """
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            # Update queue status
            if result.success:
                new_status = "completed"
                self.tasks_processed += 1
            else:
                new_status = "failed"
                self.tasks_failed += 1
            
            cursor = self.queue_conn.cursor()
            cursor.execute("""
                UPDATE task_queue
                SET status = ?,
                    completed_at = ?,
                    result_data = ?,
                    error_message = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                new_status,
                now,
                str(result.data) if result.data else None,
                result.error,
                now,
                task.id
            ))
            self.queue_conn.commit()
            
            # Save results to database if successful
            if result.success and result.data:
                self._save_results(task, result)
            
            # Update TaskManager API (if configured)
            self._update_task_manager(task, result)
            
            logger.info(
                f"Worker {self.worker_id} completed task {task.id} "
                f"(status: {new_status}, items: {result.items_processed})"
            )
            
        except Exception as e:
            logger.error(f"Error reporting result: {e}")
    
    def _save_results(self, task: Task, result: TaskResult) -> None:
        """Save results to database - to be customized by subclass."""
        # Default implementation - can be overridden
        pass
    
    def _update_task_manager(self, task: Task, result: TaskResult) -> None:
        """Update TaskManager API - to be implemented with API client."""
        # Placeholder for TaskManager API integration
        # Will be implemented in Issue #016
        pass
    
    def run_once(self) -> bool:
        """Execute one iteration of the worker loop.
        
        Returns:
            True if a task was processed, False otherwise
        """
        # Send heartbeat if needed
        self._send_heartbeat()
        
        # Try to claim a task
        task = self.claim_task()
        if not task:
            return False
        
        try:
            # Process the task
            result = self.process_task(task)
            
            # Report the result
            self.report_result(task, result)
            
            return True
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing task {task.id}: {e}")
            result = TaskResult(
                success=False,
                error=str(e)
            )
            self.report_result(task, result)
            return False
        
        finally:
            self.current_task = None
    
    def run(self, poll_interval: int = 5, max_iterations: Optional[int] = None):
        """Run the worker loop.
        
        Args:
            poll_interval: Seconds to wait between polls
            max_iterations: Maximum iterations (None = infinite)
        """
        self.running = True
        iteration = 0
        
        logger.info(f"Worker {self.worker_id} starting...")
        
        try:
            while self.running:
                # Check iteration limit
                if max_iterations and iteration >= max_iterations:
                    break
                
                # Process one task
                processed = self.run_once()
                
                # Wait if no task was available
                if not processed:
                    time.sleep(poll_interval)
                
                iteration += 1
                
        except KeyboardInterrupt:
            logger.info(f"Worker {self.worker_id} interrupted")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the worker gracefully."""
        self.running = False
        if self._queue_conn:
            self._queue_conn.close()
        logger.info(
            f"Worker {self.worker_id} stopped "
            f"(processed: {self.tasks_processed}, failed: {self.tasks_failed})"
        )
    
    def _send_heartbeat(self):
        """Send heartbeat to queue."""
        now = time.time()
        if now - self.last_heartbeat >= self.heartbeat_interval:
            try:
                cursor = self.queue_conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO worker_heartbeats
                    (worker_id, last_heartbeat, tasks_processed, tasks_failed)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.worker_id,
                    datetime.now(timezone.utc).isoformat(),
                    self.tasks_processed,
                    self.tasks_failed
                ))
                self.queue_conn.commit()
                self.last_heartbeat = now
            except Exception as e:
                logger.warning(f"Failed to send heartbeat: {e}")
```

### 3. Create Worker Factory

**File**: `Sources/Content/Shorts/YouTube/src/workers/factory.py`

```python
"""Worker factory for creating worker instances."""

from typing import Dict, Type
from .base_worker import BaseWorker
from ..core.config import Config
from ..core.database import Database


class WorkerFactory:
    """Factory for creating worker instances (Factory Pattern).
    
    Follows Open/Closed Principle - new workers can be registered
    without modifying the factory logic.
    """
    
    def __init__(self):
        self._worker_types: Dict[str, Type[BaseWorker]] = {}
    
    def register(self, task_type: str, worker_class: Type[BaseWorker]):
        """Register a worker class for a task type.
        
        Args:
            task_type: Task type identifier
            worker_class: Worker class to handle this task type
        """
        self._worker_types[task_type] = worker_class
    
    def create(
        self,
        task_type: str,
        worker_id: str,
        queue_db_path: str,
        config: Config,
        results_db: Database,
        **kwargs
    ) -> BaseWorker:
        """Create a worker instance for a task type.
        
        Args:
            task_type: Type of task to handle
            worker_id: Unique worker identifier
            queue_db_path: Path to queue database
            config: Configuration
            results_db: Results database
            **kwargs: Additional worker arguments
            
        Returns:
            Worker instance
            
        Raises:
            ValueError: If task type not registered
        """
        if task_type not in self._worker_types:
            raise ValueError(f"Unknown task type: {task_type}")
        
        worker_class = self._worker_types[task_type]
        return worker_class(
            worker_id=worker_id,
            queue_db_path=queue_db_path,
            config=config,
            results_db=results_db,
            **kwargs
        )
    
    def get_supported_types(self) -> list[str]:
        """Get list of supported task types."""
        return list(self._worker_types.keys())


# Global factory instance
worker_factory = WorkerFactory()
```

---

## Implementation Plan

### Step 1: Create Worker Package Structure
```
Sources/Content/Shorts/YouTube/src/workers/
├── __init__.py          # Protocol and data classes
├── base_worker.py       # BaseWorker implementation
└── factory.py           # WorkerFactory
```

### Step 2: Implement Protocol and Data Classes
- Define `WorkerProtocol` interface
- Create `Task` and `TaskResult` dataclasses
- Create `TaskStatus` enum

### Step 3: Implement BaseWorker
- Task claiming logic with atomic transactions
- Abstract `process_task()` method
- Result reporting
- Heartbeat mechanism
- Worker lifecycle (run/stop)

### Step 4: Implement WorkerFactory
- Registration mechanism
- Worker instantiation
- Type safety checks

### Step 5: Add Tests
- Test task claiming (different strategies)
- Test result reporting
- Test worker lifecycle
- Test factory registration

---

## Acceptance Criteria

- [ ] `WorkerProtocol` defined with minimal interface (ISP)
- [ ] `BaseWorker` implements common functionality (SRP)
- [ ] `WorkerFactory` allows registration of worker types (OCP)
- [ ] Atomic task claiming with IMMEDIATE transaction
- [ ] LIFO strategy implemented (default)
- [ ] Heartbeat mechanism working
- [ ] Worker lifecycle (start/stop) functional
- [ ] Dependencies injected via constructor (DIP)
- [ ] Unit tests with >80% coverage
- [ ] Type hints complete
- [ ] Documentation complete

---

## Testing Strategy

### Unit Tests

**File**: `Sources/Content/Shorts/YouTube/_meta/tests/test_base_worker.py`

```python
import pytest
from unittest.mock import Mock, patch
from src.workers import Task, TaskResult, TaskStatus
from src.workers.base_worker import BaseWorker


class TestWorker(BaseWorker):
    """Concrete worker for testing."""
    
    def process_task(self, task: Task) -> TaskResult:
        return TaskResult(
            success=True,
            data={"test": "data"},
            items_processed=1
        )


def test_worker_initialization():
    """Test worker initializes correctly."""
    worker = TestWorker(
        worker_id="test-worker",
        queue_db_path=":memory:",
        config=Mock(),
        results_db=Mock()
    )
    assert worker.worker_id == "test-worker"
    assert worker.strategy == "LIFO"
    assert not worker.running


def test_task_claiming_lifo():
    """Test LIFO task claiming."""
    # Setup queue with multiple tasks
    # Assert most recent task is claimed
    pass


def test_task_claiming_atomic():
    """Test atomic task claiming prevents double-claiming."""
    # Setup two workers
    # Have them claim simultaneously
    # Assert only one succeeds
    pass


def test_result_reporting():
    """Test result reporting updates queue."""
    # Process a task
    # Assert queue updated correctly
    # Assert results saved
    pass


def test_worker_lifecycle():
    """Test worker start/stop."""
    # Start worker
    # Process some tasks
    # Stop worker
    # Assert clean shutdown
    pass
```

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/src/workers/__init__.py`
2. `Sources/Content/Shorts/YouTube/src/workers/base_worker.py`
3. `Sources/Content/Shorts/YouTube/src/workers/factory.py`
4. `Sources/Content/Shorts/YouTube/_meta/tests/test_base_worker.py`
5. `Sources/Content/Shorts/YouTube/_meta/tests/test_worker_factory.py`

---

## Dependencies

### External
- SQLite3 (standard library)
- Python 3.10+ (for Protocol support)

### Internal
- Config from `src/core/config.py`
- Database from `src/core/database.py`
- Queue database schema (from Issue #004)

---

## Estimated Effort

**2-3 days**:
- Day 1: Protocol, data classes, BaseWorker skeleton
- Day 2: Complete BaseWorker implementation, factory
- Day 3: Tests, documentation, refinement

---

## Target Platform

- Windows (primary)
- Python 3.10+
- SQLite 3.35+ (WAL mode support)

---

## Related Issues

- **#001**: Master plan (parent)
- **#003**: Task polling mechanism (next)
- **#004**: Queue schema design (parallel)
- **#016**: TaskManager API integration (future)

---

## Notes

### Design Decisions

1. **Why Protocol?**
   - Type-safe interface definition
   - Clear contract for implementations
   - Supports static type checking

2. **Why Abstract Base Class?**
   - Provides common implementation
   - Enforces interface through abstract methods
   - Better than multiple inheritance

3. **Why Factory Pattern?**
   - Decouples worker creation from usage
   - Easy to add new worker types
   - Testable in isolation

### Future Enhancements

- Support for PRIORITY and WEIGHTED_RANDOM strategies
- Worker pool management
- Distributed worker coordination
- Advanced retry strategies

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker02 - Python Specialist  
**Estimated Start**: Week 1, Day 1  
**Estimated Completion**: Week 1, Day 3
