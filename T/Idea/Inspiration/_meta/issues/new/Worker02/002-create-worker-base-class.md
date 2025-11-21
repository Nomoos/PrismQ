# Issue #002: Create Worker Base Class and Interface

## Status
New

## Priority
High

## Category
Feature - Infrastructure

## Description

Create the foundational worker base class and interface that will be used by all YouTube scraping workers. This establishes the core abstraction for task execution following the worker pattern from PrismQ.Client.

## Problem Statement

The YouTube Shorts Source module needs to transition from direct execution to a worker-based architecture. The first step is creating a robust, SOLID-compliant base class that defines the worker contract and provides common functionality.

## Proposed Solution

Create an abstract `YouTubeWorkerBase` class that:
- Defines the worker interface (task polling, execution, result reporting)
- Implements common functionality (logging, metrics, error handling)
- Follows SOLID principles, especially Dependency Inversion
- Provides hooks for plugin-specific implementations

## Acceptance Criteria

- [ ] `YouTubeWorkerBase` abstract class created in `Sources/Content/Shorts/YouTube/src/core/worker_base.py`
- [ ] Abstract methods defined: `execute_task()`, `validate_parameters()`
- [ ] Common methods implemented: `poll_task()`, `report_result()`, `handle_error()`
- [ ] Dependency injection for Config, Database, TaskQueue
- [ ] Comprehensive logging with worker identification
- [ ] Type hints for all methods and parameters
- [ ] Docstrings following Google style
- [ ] Unit tests with >80% coverage
- [ ] SOLID principles compliance verified

## Technical Details

### Implementation Approach

1. Create `worker_base.py` in `src/core/`
2. Define `YouTubeWorkerBase` abstract class with ABC
3. Use Protocol for dependency interfaces
4. Implement common task lifecycle methods
5. Add logging and metrics collection

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/src/core/worker_base.py`
  - Abstract worker base class
  - Common task execution logic
  - Error handling patterns

- **Create**: `Sources/Content/Shorts/YouTube/src/core/task_queue.py`
  - Task queue interface (Protocol)
  - For dependency injection

- **Create**: `Sources/Content/Shorts/YouTube/tests/test_worker_base.py`
  - Unit tests for worker base class
  - Mock dependencies

### Class Structure

```python
from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass

class TaskQueue(Protocol):
    """Protocol for task queue dependency"""
    def claim_task(self, worker_id: str) -> Optional[Dict[str, Any]]:
        ...
    def update_task_status(self, task_id: str, status: str) -> None:
        ...

@dataclass
class WorkerConfig:
    """Worker configuration"""
    worker_id: str
    worker_type: str
    poll_interval: int = 5
    max_retries: int = 3

class YouTubeWorkerBase(ABC):
    """Base class for all YouTube workers"""
    
    def __init__(self, config: WorkerConfig, task_queue: TaskQueue):
        self.config = config
        self.task_queue = task_queue
        
    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the worker-specific task logic"""
        pass
    
    @abstractmethod
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate task parameters"""
        pass
    
    def poll_and_execute(self) -> None:
        """Main worker loop: poll, execute, report"""
        pass
    
    def handle_error(self, task_id: str, error: Exception) -> None:
        """Handle task execution errors"""
        pass
```

### Dependencies

- Python 3.10+
- typing module for Protocol
- abc module for abstract base class
- dataclasses for configuration
- logging for worker logging

### SOLID Principles Analysis

**Single Responsibility Principle (SRP)**
- ✅ Worker base class only handles task lifecycle
- ✅ Task execution logic delegated to subclasses
- ✅ Dependencies injected (Config, TaskQueue)

**Open/Closed Principle (OCP)**
- ✅ Open for extension via abstract methods
- ✅ Closed for modification (stable base implementation)

**Liskov Substitution Principle (LSP)**
- ✅ All worker implementations can substitute base class
- ✅ Contract clearly defined via abstract methods

**Interface Segregation Principle (ISP)**
- ✅ Minimal interface with only essential methods
- ✅ TaskQueue protocol has focused responsibility

**Dependency Inversion Principle (DIP)**
- ✅ Depends on TaskQueue protocol (abstraction)
- ✅ Config injected via constructor
- ✅ No direct dependencies on concrete implementations

## Estimated Effort
2 days

## Target Platform
- Windows
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [x] Unit tests for `YouTubeWorkerBase` methods
- [x] Mock TaskQueue implementation
- [x] Test error handling scenarios
- [x] Test lifecycle methods (poll, execute, report)
- [x] Verify dependency injection works correctly
- [ ] Integration tests (later phase)

## Related Issues

- Issue #001 - Master Plan (YouTube Worker Refactor)
- Issue #003 - Implement Task Polling Mechanism (depends on this)
- Issue #004 - Design Worker Task Schema in SQLite (parallel)

## Notes

- Keep the base class focused and minimal
- Avoid adding YouTube-specific logic (that goes in plugins)
- Use Protocol for dependency injection (DIP)
- Ensure easy testability with dependency injection
- Document all public methods thoroughly
- Consider async/await for future scalability (optional in MVP)

## References

- [Worker Implementation Template](https://github.com/Nomoos/PrismQ.Client/blob/3d8301aa5641d772fa39d84f9c0a54c18ee7c1d2/_meta/templates/WORKER_IMPLEMENTATION_TEMPLATE.md)
- [SOLID Principles Guide](_meta/docs/SOLID_PRINCIPLES.md)
- [Python Protocol Documentation](https://docs.python.org/3/library/typing.html#typing.Protocol)
