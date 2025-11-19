# Issue #327: Implement Queue Scheduling Strategies

**Parent Issue**: #320 (SQLite Queue Analysis)  
**Worker**: Worker 04 - Algorithm Engineer  
**Status**: New  
**Priority**: High  
**Duration**: 1 week  
**Dependencies**: #321 (Core Infrastructure)

---

## Objective

Implement four different task queue scheduling strategies (FIFO, LIFO, Priority, Weighted Random) with a configuration mechanism to switch between them, ensuring fair task distribution and preventing starvation.

---

## Background

The original issue requests:
> "Consider FIFO, LIFO, Priority Q, Weighted Random (make issue for implementing switch on worker)"

Different scheduling strategies are needed for different use cases:
- **FIFO**: Fair processing, background jobs
- **LIFO**: Latest tasks first, user-triggered actions
- **Priority**: Time-sensitive operations
- **Weighted Random**: Load balancing, preventing starvation

---

## Requirements

### 1. FIFO (First-In-First-Out)

**Use Case**: Fair processing where order of submission matters

**Implementation**:
```sql
-- Claim oldest available task
WITH candidate AS (
  SELECT id
  FROM task_queue
  WHERE status = 'queued'
    AND run_after_utc <= datetime('now')
    -- Capability filters applied here
  ORDER BY id ASC  -- FIFO: oldest first
  LIMIT 1
)
UPDATE task_queue
SET status = 'leased',
    reserved_at_utc = datetime('now'),
    lease_until_utc = datetime('now', printf('+%d seconds', :lease_seconds)),
    locked_by = :worker_id
WHERE id = (SELECT id FROM candidate);
```

**Guarantees**: Tasks processed in submission order (within priority level)

### 2. LIFO (Last-In-First-Out)

**Use Case**: User-triggered operations where latest request should be prioritized

**Implementation**:
```sql
-- Claim newest available task
WITH candidate AS (
  SELECT id
  FROM task_queue
  WHERE status = 'queued'
    AND run_after_utc <= datetime('now')
  ORDER BY id DESC  -- LIFO: newest first
  LIMIT 1
)
UPDATE task_queue
SET status = 'leased',
    reserved_at_utc = datetime('now'),
    lease_until_utc = datetime('now', printf('+%d seconds', :lease_seconds)),
    locked_by = :worker_id
WHERE id = (SELECT id FROM candidate);
```

**Guarantees**: Latest tasks processed first (can starve old tasks)

### 3. Priority Queue

**Use Case**: Time-sensitive operations need to jump ahead

**Implementation**:
```sql
-- Claim highest priority task (lower number = higher priority)
WITH candidate AS (
  SELECT id
  FROM task_queue
  WHERE status = 'queued'
    AND run_after_utc <= datetime('now')
  ORDER BY priority ASC, id ASC  -- Priority first, then FIFO within same priority
  LIMIT 1
)
UPDATE task_queue
SET status = 'leased',
    reserved_at_utc = datetime('now'),
    lease_until_utc = datetime('now', printf('+%d seconds', :lease_seconds)),
    locked_by = :worker_id
WHERE id = (SELECT id FROM candidate);
```

**Guarantees**: Higher priority (lower number) always processed first

### 4. Weighted Random

**Use Case**: Probabilistic selection based on priority, prevents complete starvation

**Implementation**:
```sql
-- Claim task with weighted random selection
-- Higher priority (lower number) has higher probability
-- Formula: RANDOM() * (1.0 / (priority + 1))
--   - priority=1:   weight ~ 1.0   (highest)
--   - priority=10:  weight ~ 0.09  (~10x less than p=1)
--   - priority=100: weight ~ 0.01  (~100x less than p=1)
-- This ensures priority 1 has ~10x more probability than priority 10
WITH candidate AS (
  SELECT id
  FROM task_queue
  WHERE status = 'queued'
    AND run_after_utc <= datetime('now')
  ORDER BY RANDOM() * (1.0 / (priority + 1)) DESC
  LIMIT 1
)
UPDATE task_queue
SET status = 'leased',
    reserved_at_utc = datetime('now'),
    lease_until_utc = datetime('now', printf('+%d seconds', :lease_seconds)),
    locked_by = :worker_id
WHERE id = (SELECT id FROM candidate);
```

**Guarantees**: 
- Priority 1 has ~10x more probability than priority 10
- Priority 100 still has some chance to run
- No complete starvation

---

## Technical Design

### Scheduling Strategy Enum

```python
from enum import Enum

class SchedulingStrategy(str, Enum):
    """Task queue scheduling strategies."""
    
    FIFO = "fifo"               # First-In-First-Out
    LIFO = "lifo"               # Last-In-First-Out
    PRIORITY = "priority"       # Priority-based (lower number first)
    WEIGHTED_RANDOM = "weighted_random"  # Probabilistic with priority weights
```

### Worker Configuration

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class WorkerConfig:
    """Worker configuration including scheduling strategy."""
    
    worker_id: str
    capabilities: Dict[str, any]  # e.g., {"region": "us", "formats": ["video"]}
    scheduling_strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY
    lease_duration_seconds: int = 60
    poll_interval_seconds: int = 1
    max_retries: int = 3
```

### Task Claimer Interface

```python
from abc import ABC, abstractmethod
from typing import Optional, Protocol

class TaskClaimer(Protocol):
    """
    Protocol for task claiming strategies.
    
    Follows SOLID Interface Segregation principle.
    """
    
    def claim_task(
        self,
        worker_id: str,
        capabilities: Dict[str, any],
        lease_seconds: int
    ) -> Optional[Task]:
        """
        Claim a single task based on strategy.
        
        Returns None if no tasks available.
        """
        ...
```

### Strategy Implementation

```python
class FIFOTaskClaimer:
    """First-In-First-Out task claiming."""
    
    def __init__(self, db: QueueDatabase):
        self.db = db
    
    def claim_task(
        self,
        worker_id: str,
        capabilities: Dict[str, any],
        lease_seconds: int
    ) -> Optional[Task]:
        """Claim oldest available task."""
        # Implementation using FIFO SQL

class LIFOTaskClaimer:
    """Last-In-First-Out task claiming."""
    # Similar structure with LIFO SQL

class PriorityTaskClaimer:
    """Priority-based task claiming."""
    # Similar structure with Priority SQL

class WeightedRandomTaskClaimer:
    """Weighted random task claiming."""
    # Similar structure with Weighted Random SQL
```

### Strategy Factory

```python
class TaskClaimerFactory:
    """
    Factory for creating task claimers.
    
    Follows SOLID Open/Closed principle - can add strategies without modifying existing code.
    """
    
    @staticmethod
    def create(
        strategy: SchedulingStrategy,
        db: QueueDatabase
    ) -> TaskClaimer:
        """Create task claimer based on strategy."""
        
        if strategy == SchedulingStrategy.FIFO:
            return FIFOTaskClaimer(db)
        elif strategy == SchedulingStrategy.LIFO:
            return LIFOTaskClaimer(db)
        elif strategy == SchedulingStrategy.PRIORITY:
            return PriorityTaskClaimer(db)
        elif strategy == SchedulingStrategy.WEIGHTED_RANDOM:
            return WeightedRandomTaskClaimer(db)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
```

---

## Implementation Steps

### Step 1: Define Enum and Models (Day 1)
- [ ] Create `SchedulingStrategy` enum
- [ ] Create `WorkerConfig` dataclass
- [ ] Define `TaskClaimer` Protocol
- [ ] Add to module structure

### Step 2: Implement FIFO Strategy (Day 1-2)
- [ ] Create `FIFOTaskClaimer` class
- [ ] Implement SQL query with capability filtering
- [ ] Add atomic claiming with transactions
- [ ] Unit tests for FIFO

### Step 3: Implement LIFO Strategy (Day 2)
- [ ] Create `LIFOTaskClaimer` class
- [ ] Implement SQL query
- [ ] Unit tests for LIFO

### Step 4: Implement Priority Strategy (Day 3)
- [ ] Create `PriorityTaskClaimer` class
- [ ] Implement SQL query
- [ ] Unit tests for Priority

### Step 5: Implement Weighted Random Strategy (Day 3-4)
- [ ] Create `WeightedRandomTaskClaimer` class
- [ ] Implement weighted random SQL
- [ ] Test probability distribution
- [ ] Unit tests for Weighted Random

### Step 6: Strategy Factory (Day 4)
- [ ] Create `TaskClaimerFactory`
- [ ] Integration tests for all strategies
- [ ] Benchmark strategy performance

### Step 7: Worker Integration (Day 5)
- [ ] Update worker loop to use strategies
- [ ] Configuration loading
- [ ] Strategy switching at runtime
- [ ] End-to-end tests

---

## Testing Requirements

### Unit Tests

```python
def test_fifo_ordering():
    """Test FIFO claims oldest task first."""
    # Enqueue tasks in order: 1, 2, 3
    # Claim should get 1, then 2, then 3

def test_lifo_ordering():
    """Test LIFO claims newest task first."""
    # Enqueue tasks in order: 1, 2, 3
    # Claim should get 3, then 2, then 1

def test_priority_ordering():
    """Test priority claims high priority first."""
    # Enqueue: priority 100, 50, 1
    # Claim should get priority 1 first

def test_weighted_random_distribution():
    """Test weighted random distribution matches expected probabilities."""
    # Enqueue 100 tasks: 50 at priority 1, 50 at priority 100
    # Claim all 100 tasks
    # Priority 1 tasks should be claimed ~2x more often

def test_capability_filtering():
    """Test all strategies respect capability filters."""
    # Enqueue tasks with different region requirements
    # Worker with region=US should only claim US tasks
```

### Integration Tests

```python
def test_strategy_switching():
    """Test worker can switch strategies dynamically."""
    
def test_concurrent_claims_different_strategies():
    """Test multiple workers with different strategies don't conflict."""

def test_starvation_prevention():
    """Test weighted random prevents complete starvation."""
```

### Performance Tests

```python
def test_strategy_claim_latency():
    """Measure claim latency for each strategy."""
    # Should be <10ms for all strategies

def test_strategy_throughput():
    """Measure claims/second for each strategy."""
```

---

## Comparison Matrix

| Strategy | Ordering | Fairness | Starvation Risk | Use Case |
|----------|----------|----------|-----------------|----------|
| **FIFO** | Submission order | High | Low | Background jobs, imports |
| **LIFO** | Reverse submission | Low | High | User actions, cancel older |
| **Priority** | Priority value | None | High (for low priority) | Time-sensitive ops |
| **Weighted Random** | Probabilistic | Medium | Low | Load balancing |

---

## Configuration Examples

### FIFO Worker (Default)
```python
worker_config = WorkerConfig(
    worker_id="worker-1",
    capabilities={"region": "us"},
    scheduling_strategy=SchedulingStrategy.FIFO,
    lease_duration_seconds=60
)
```

### Priority Worker (Critical Tasks)
```python
worker_config = WorkerConfig(
    worker_id="worker-critical",
    capabilities={"region": "us", "priority_only": True},
    scheduling_strategy=SchedulingStrategy.PRIORITY,
    lease_duration_seconds=30
)
```

### Weighted Random Worker (Balanced)
```python
worker_config = WorkerConfig(
    worker_id="worker-balanced",
    capabilities={},
    scheduling_strategy=SchedulingStrategy.WEIGHTED_RANDOM,
    lease_duration_seconds=60
)
```

---

## Acceptance Criteria

- [ ] All 4 scheduling strategies implemented (FIFO, LIFO, Priority, Weighted Random)
- [ ] Each strategy respects capability filtering
- [ ] Atomic claiming works for all strategies
- [ ] Strategy can be configured per worker
- [ ] Strategy can be switched at runtime
- [ ] No duplicate task claims across strategies
- [ ] Tests verify ordering guarantees
- [ ] Performance benchmarks documented
- [ ] Weighted random distribution validated
- [ ] All tests passing with >80% coverage
- [ ] Documentation complete with examples

---

## Integration Points

### Depends On
- #321: Core Infrastructure (database and schema)

### Used By
- #325: Worker Engine (uses strategies for claiming)
- #333: Testing (benchmarks strategy performance)

---

## Success Metrics

- Claim latency: <10ms for all strategies
- Strategy switching overhead: <1ms
- Weighted random distribution: Within 10% of expected probabilities
- Zero duplicate claims across all strategies
- Test coverage: >85%

---

**Status**: Ready to Start (after #321)  
**Assigned**: Worker 04 - Algorithm Engineer  
**Labels**: `algorithms`, `scheduling`, `queue`, `backend`
