# Scoring Worker Architecture

This document describes the architecture of the Scoring Worker implementation, which follows the PrismQ Worker pattern for distributed task processing.

## Overview

The Scoring Worker refactors the Scoring module to support distributed task processing while maintaining backward compatibility with the existing ScoringEngine API.

### Key Features

- **Distributed Processing**: Multiple workers can process scoring tasks concurrently
- **Task Queue**: SQLite-based persistent queue with ACID guarantees
- **TaskManager Integration**: Optional centralized coordination via TaskManager API
- **Claiming Strategies**: Flexible task claiming (FIFO, LIFO, PRIORITY)
- **Backward Compatible**: Existing ScoringEngine API remains unchanged

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      TaskManager API (External)                  │
│                  Centralized Task Coordination                   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Task Registration
                                 │ Task Claiming
                                 │ Result Reporting
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Scoring Worker                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  BaseScoringWorker (Abstract)                             │  │
│  │  - Task lifecycle management                              │  │
│  │  - Queue interaction                                      │  │
│  │  - TaskManager integration                                │  │
│  │  - Heartbeat monitoring                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │ extends                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ScoringWorker (Concrete)                                 │  │
│  │  - TextScoring: Score text content                        │  │
│  │  - EngagementScoring: Score engagement metrics            │  │
│  │  - BatchScoring: Score multiple items                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │ uses                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ScoringEngine                                            │  │
│  │  - Text quality scoring                                   │  │
│  │  - Engagement metrics                                     │  │
│  │  - Universal content score                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Read/Write
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SQLite Queue Database                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  task_queue                                               │  │
│  │  - Task storage with status tracking                      │  │
│  │  - Atomic claiming with transactions                      │  │
│  │  └───────────────────────────────────────────────────────┘  │
│  │  worker_heartbeats                                        │  │
│  │  - Worker status tracking                                 │  │
│  │  └───────────────────────────────────────────────────────┘  │
│  │  task_history                                             │  │
│  │  - Execution history for monitoring                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## SOLID Principles

The implementation follows SOLID design principles:

### Single Responsibility Principle (SRP)

Each class has one reason to change:

- **BaseScoringWorker**: Task lifecycle management
- **ScoringWorker**: Scoring-specific logic
- **ClaimingStrategy**: Task ordering logic
- **WorkerFactory**: Worker instantiation

### Open/Closed Principle (OCP)

The system is open for extension, closed for modification:

- New claiming strategies can be added without modifying existing code
- New task types can be added by subclassing `BaseScoringWorker`
- New scoring methods can be added to `ScoringEngine` without breaking workers

### Liskov Substitution Principle (LSP)

Workers are interchangeable through common protocol:

- Any `WorkerProtocol` implementation can be used
- Claiming strategies are interchangeable through `ClaimingStrategy` interface

### Interface Segregation Principle (ISP)

Focused, minimal interfaces:

- `WorkerProtocol`: Only essential worker methods
- `ClaimingStrategy`: Only task ordering concern

### Dependency Inversion Principle (DIP)

Depends on abstractions, not concrete implementations:

- Workers depend on `Config` abstraction, not specific config implementation
- Workers depend on `ScoringEngine` abstraction
- Dependencies injected via constructor

## Components

### 1. Worker Protocol (`__init__.py`)

Defines the worker interface and data models:

```python
class WorkerProtocol(Protocol):
    def claim_task(self) -> Optional[Task]
    def process_task(self, task: Task) -> TaskResult
    def report_result(self, task: Task, result: TaskResult) -> None
```

**Data Models:**
- `Task`: Task representation with parameters
- `TaskResult`: Processing result with success status
- `TaskStatus`: Task status enumeration

### 2. Base Worker (`base_scoring_worker.py`)

Abstract base class providing common functionality:

- **Task Claiming**: Atomic claiming using SQLite transactions
- **Queue Management**: Lazy connection, WAL mode for concurrency
- **Heartbeat**: Periodic status updates
- **Backoff**: Exponential backoff when queue is empty
- **TaskManager Integration**: Optional API coordination

**Key Methods:**
- `claim_task()`: Atomic task claiming with strategy
- `report_result()`: Update queue and TaskManager
- `run()`: Main worker loop with exponential backoff
- `run_once()`: Single iteration for testing

### 3. Concrete Worker (`scoring_worker.py`)

Implements specific scoring logic:

- **Task Type Registration**: Registers with TaskManager API
- **Text Scoring**: Process text quality scoring tasks
- **Engagement Scoring**: Process engagement metrics tasks
- **Batch Scoring**: Process multiple items in one task

**Task Handlers:**
- `_process_text_scoring()`: Text quality analysis
- `_process_engagement_scoring()`: Engagement metrics
- `_process_batch_scoring()`: Batch processing

### 4. Claiming Strategies (`claiming_strategies.py`)

Pluggable task claiming behavior:

- **FIFO**: First In, First Out (oldest first)
- **LIFO**: Last In, First Out (newest first)
- **PRIORITY**: High-priority tasks first

**Strategy Pattern:**
```python
class ClaimingStrategy(ABC):
    def get_order_by_clause(self) -> str
    def get_name(self) -> str
```

### 5. Worker Factory (`factory.py`)

Factory for creating configured workers:

```python
worker = WorkerFactory.create_scoring_worker(
    worker_id="my-worker",
    strategy="PRIORITY",
    enable_taskmanager=True
)
```

### 6. Queue Database (`schema.sql`)

SQLite schema with:

- **task_queue**: Task storage with status tracking
- **worker_heartbeats**: Worker status monitoring
- **task_history**: Execution history for debugging

**Features:**
- ACID guarantees with transactions
- WAL mode for concurrent access
- Indexes for efficient claiming
- Delayed execution support

## Task Types

### 1. TextScoring

Score text content quality.

**Parameters:**
```json
{
  "title": "Content Title",
  "description": "Description",
  "text_content": "Full content",
  "metadata": {}
}
```

**Result:**
```json
{
  "score_breakdown": {
    "overall_score": 85.5,
    "title_score": 78.2,
    "text_quality_score": 82.3
  }
}
```

### 2. EngagementScoring

Score based on engagement metrics.

**Parameters:**
```json
{
  "views": 1000000,
  "likes": 50000,
  "comments": 1000,
  "platform": "youtube"
}
```

**Result:**
```json
{
  "engagement_score": 65.8,
  "score_details": { ... }
}
```

### 3. BatchScoring

Score multiple items efficiently.

**Parameters:**
```json
{
  "items": [
    { "title": "Item 1", ... },
    { "title": "Item 2", ... }
  ]
}
```

**Result:**
```json
{
  "results": [...],
  "total_items": 10,
  "successful": 10
}
```

## Integration Modes

### Local Queue Mode

Worker processes tasks from local SQLite queue only:

```python
worker = WorkerFactory.create_scoring_worker(
    enable_taskmanager=False
)
```

**Use Cases:**
- Standalone operation
- Development and testing
- Single-machine deployments

### TaskManager API Mode

Worker integrates with external TaskManager API:

```python
worker = WorkerFactory.create_scoring_worker(
    enable_taskmanager=True  # Default
)
```

**Features:**
- Centralized task coordination
- Cross-module task sharing
- Distributed monitoring
- Fault tolerance

**API Operations:**
1. **Register Task Types**: Define available task types
2. **Claim Tasks**: Claim from centralized queue
3. **Report Results**: Send completion status

## Worker Lifecycle

```
1. Initialize
   - Connect to queue database
   - Initialize scoring engine
   - Connect to TaskManager API (optional)

2. Register Task Types (if TaskManager enabled)
   - Define task type schemas
   - Register with API
   - Store task_type_ids

3. Main Loop
   - Send heartbeat (periodic)
   - Claim task (atomic)
   - Process task
   - Report result
   - Backoff if no tasks

4. Shutdown
   - Complete current task
   - Update status
   - Close connections
```

## Claiming Process

Task claiming is atomic and concurrent-safe:

```sql
BEGIN IMMEDIATE;

-- Find available task
SELECT * FROM task_queue
WHERE status = 'queued'
ORDER BY {strategy_order}
LIMIT 1;

-- Claim the task
UPDATE task_queue
SET status = 'claimed',
    claimed_by = 'worker-id',
    claimed_at = 'timestamp'
WHERE id = task_id;

COMMIT;
```

**Concurrency Guarantees:**
- `BEGIN IMMEDIATE`: Lock entire database
- Atomic read-modify-write
- No lost updates or double-claiming

## Exponential Backoff

When queue is empty, worker backs off exponentially:

```
Initial: 5s
After 1st empty: 7.5s (× 1.5)
After 2nd empty: 11.25s (× 1.5)
After 3rd empty: 16.875s (× 1.5)
...
Maximum: 60s (configurable)
```

**Benefits:**
- Reduces CPU usage when idle
- Maintains responsiveness
- Configurable for different workloads

## Error Handling

### Task-Level Errors

Caught and reported as task failures:

```python
try:
    result = process_task(task)
except Exception as e:
    result = TaskResult(success=False, error=str(e))
```

### Worker-Level Errors

Fatal errors stop the worker:

```python
try:
    worker.run()
except KeyboardInterrupt:
    # Graceful shutdown
except Exception as e:
    # Fatal error, log and exit
```

### TaskManager Errors

Non-fatal, logged as warnings:

```python
try:
    taskmanager_client.complete_task(...)
except Exception as e:
    logger.warning(f"Failed to report to TaskManager: {e}")
    # Task still marked as completed locally
```

## Monitoring

### Worker Heartbeats

Workers send heartbeats to track status:

```sql
INSERT OR REPLACE INTO worker_heartbeats
(worker_id, last_heartbeat, tasks_processed, tasks_failed)
VALUES (?, ?, ?, ?);
```

### Task History

Track task execution:

```sql
INSERT INTO task_history
(task_id, worker_id, status, timestamp, duration_seconds)
VALUES (?, ?, ?, ?, ?);
```

### Queue Monitoring

Check queue state:

```sql
SELECT status, COUNT(*) 
FROM task_queue 
GROUP BY status;
```

## Testing Strategy

### Unit Tests

- Test each component in isolation
- Mock dependencies (Config, TaskManager)
- Focus on business logic

### Integration Tests

- Test worker with real queue database
- Test TaskManager integration
- Test concurrent workers

### Example Tests

```python
def test_claim_task_success(worker):
    # Add task to queue
    # Claim task
    # Verify status updated

def test_process_text_scoring(worker):
    # Create task
    # Process task
    # Verify result structure

def test_run_once_with_task(worker):
    # Add task
    # Run once
    # Verify processed
```

## Deployment

### Single Worker

```bash
python scripts/run_worker.py --worker-id scorer-01
```

### Multiple Workers

```bash
# Terminal 1
python scripts/run_worker.py --worker-id scorer-01 --strategy PRIORITY

# Terminal 2
python scripts/run_worker.py --worker-id scorer-02 --strategy FIFO
```

### Production Considerations

- Use process manager (systemd, supervisor)
- Configure logging appropriately
- Monitor heartbeats and queue depth
- Set appropriate backoff parameters
- Enable TaskManager for coordination

## Future Enhancements

1. **Result Persistence**: Save results to Model/IdeaInspiration database
2. **Task Dependencies**: Support task chains and workflows
3. **Priority Adjustment**: Dynamic priority based on metrics
4. **Dead Letter Queue**: Handle permanently failed tasks
5. **Distributed Queue**: Replace SQLite with Redis/PostgreSQL
6. **Metrics**: Prometheus metrics for monitoring
7. **Auto-scaling**: Dynamic worker count based on queue depth

## References

- [Worker Pattern Example](../../../Source/TaskManager/_meta/examples/worker_example.py)
- [Video Worker Implementation](../../../Source/Video/YouTube/Channel/src/workers/)
- [TaskManager API Documentation](../../../Source/TaskManager/README.md)
- [SOLID Principles](../_meta/docs/SOLID_PRINCIPLES.md)
