# Issue #003: Implement Task Polling Mechanism

## Status
New

## Priority
High

## Category
Feature - Infrastructure

## Description

Implement the task polling mechanism that workers will use to claim and process tasks from the SQLite queue. This provides the core polling loop with LIFO (Last-In-First-Out) task claiming strategy.

## Problem Statement

Workers need a reliable mechanism to poll the SQLite task queue, claim tasks atomically, and handle concurrent access. The polling must be efficient, respect priorities, and implement LIFO claiming by default.

## Proposed Solution

Create a `TaskPoller` class that:
- Polls SQLite queue at configurable intervals
- Claims tasks atomically using SQL transactions
- Implements LIFO claiming strategy
- Handles concurrent worker access
- Supports priority-based task selection
- Includes backoff strategies for empty queues

## Acceptance Criteria

- [ ] `TaskPoller` class created in `Sources/Content/Shorts/YouTube/src/core/task_poller.py`
- [ ] LIFO task claiming implemented with SQL ORDER BY
- [ ] Atomic task claiming using SQLite transactions
- [ ] Configurable poll interval (default 5 seconds)
- [ ] Empty queue backoff (exponential or linear)
- [ ] Priority-based task selection support
- [ ] Worker heartbeat mechanism
- [ ] Type hints and comprehensive docstrings
- [ ] Unit tests with >80% coverage
- [ ] Integration tests with SQLite database

## Technical Details

### Implementation Approach

1. Create `task_poller.py` in `src/core/`
2. Implement atomic task claiming with SQL
3. Add polling loop with configurable interval
4. Implement backoff for empty queues
5. Add worker heartbeat tracking

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/src/core/task_poller.py`
  - TaskPoller class
  - LIFO claiming logic
  - Backoff strategies

- **Create**: `Sources/Content/Shorts/YouTube/tests/test_task_poller.py`
  - Unit tests with mock database
  - Concurrent access tests
  - LIFO verification tests

### Class Structure

```python
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time
import sqlite3

@dataclass
class PollerConfig:
    """Task poller configuration"""
    poll_interval: int = 5
    max_backoff: int = 60
    backoff_multiplier: float = 1.5
    priority_enabled: bool = True

class TaskPoller:
    """Polls SQLite queue for tasks using LIFO strategy"""
    
    def __init__(self, db_path: str, worker_id: str, config: PollerConfig):
        self.db_path = db_path
        self.worker_id = worker_id
        self.config = config
        self._current_backoff = config.poll_interval
        
    def claim_next_task(self) -> Optional[Dict[str, Any]]:
        """
        Claim the next available task using LIFO strategy.
        
        Returns:
            Task dictionary if claimed, None if no tasks available
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                # LIFO: ORDER BY created_at DESC (newest first)
                cursor = conn.execute("""
                    SELECT task_id, task_type, parameters, priority, created_at
                    FROM task_queue
                    WHERE status = 'QUEUED'
                    ORDER BY priority DESC, created_at DESC
                    LIMIT 1
                """)
                
                task = cursor.fetchone()
                if not task:
                    conn.rollback()
                    return None
                
                # Claim the task
                conn.execute("""
                    UPDATE task_queue
                    SET status = 'RUNNING',
                        worker_id = ?,
                        started_at = CURRENT_TIMESTAMP
                    WHERE task_id = ? AND status = 'QUEUED'
                """, (self.worker_id, task[0]))
                
                conn.commit()
                
                # Reset backoff on successful claim
                self._current_backoff = self.config.poll_interval
                
                return {
                    'task_id': task[0],
                    'task_type': task[1],
                    'parameters': task[2],
                    'priority': task[3],
                    'created_at': task[4]
                }
                
            except Exception as e:
                conn.rollback()
                raise
    
    def poll_loop(self, callback):
        """
        Main polling loop that claims tasks and executes callback.
        
        Args:
            callback: Function to call with claimed task
        """
        while True:
            task = self.claim_next_task()
            
            if task:
                callback(task)
            else:
                # Backoff when no tasks available
                time.sleep(self._current_backoff)
                self._increase_backoff()
    
    def _increase_backoff(self) -> None:
        """Increase backoff time exponentially"""
        self._current_backoff = min(
            self._current_backoff * self.config.backoff_multiplier,
            self.config.max_backoff
        )
    
    def update_heartbeat(self, task_id: str) -> None:
        """Update worker heartbeat for long-running tasks"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE task_queue
                SET last_heartbeat = CURRENT_TIMESTAMP
                WHERE task_id = ? AND worker_id = ?
            """, (task_id, self.worker_id))
```

### Dependencies

- Issue #002 - Worker Base Class (uses TaskPoller)
- Issue #004 - SQLite Task Schema (must exist first)
- SQLite3 (built-in)
- Python 3.10+

### SOLID Principles Analysis

**Single Responsibility Principle (SRP)**
- ✅ TaskPoller only handles task claiming from queue
- ✅ Does not execute tasks (worker's responsibility)

**Open/Closed Principle (OCP)**
- ✅ Open for extension (custom claiming strategies)
- ✅ Closed for modification (stable polling logic)

**Liskov Substitution Principle (LSP)**
- ✅ Can be extended for different claiming strategies
- ✅ Interface remains consistent

**Interface Segregation Principle (ISP)**
- ✅ Focused interface (claim, poll, heartbeat)
- ✅ No unnecessary methods

**Dependency Inversion Principle (DIP)**
- ✅ Depends on database path (abstraction)
- ✅ Config injected for flexibility

## Estimated Effort
2 days

## Target Platform
- Windows
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [x] Unit tests for task claiming logic
- [x] Test LIFO ordering (newest task claimed first)
- [x] Test atomic claiming (no double-claiming)
- [x] Test concurrent access (multiple workers)
- [x] Test backoff mechanism
- [x] Test priority-based selection
- [x] Test heartbeat updates
- [ ] Integration tests with real SQLite database

## Related Issues

- Issue #001 - Master Plan
- Issue #002 - Worker Base Class (depends on this)
- Issue #004 - SQLite Task Schema (required first)
- Issue #337 - Queue Optimization (future enhancement)

## Notes

- LIFO is default but could be made configurable (FIFO optional)
- Consider using SQLite's `BEGIN IMMEDIATE` for proper locking
- Exponential backoff prevents CPU spinning when queue is empty
- Heartbeat mechanism prevents stuck tasks
- Priority + LIFO: high priority first, then newest within priority
- Test with multiple concurrent workers to ensure atomicity
- Windows-compatible (no Unix-specific features)

## Performance Considerations

- SQLite transactions are fast for single-row updates
- Index on `status` and `created_at` for efficient queries
- Backoff reduces polling overhead when queue is empty
- Heartbeat updates should be infrequent (every 30s minimum)
