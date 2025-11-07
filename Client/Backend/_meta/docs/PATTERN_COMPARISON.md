# Pattern Comparison Guide

**Purpose**: Help developers choose the right background task pattern for their use case.

**Last Updated**: 2025-11-05

---

## Quick Decision Matrix

Use this matrix to quickly determine which pattern fits your needs:

| Your Need | Recommended Pattern | Alternative |
|-----------|-------------------|-------------|
| Quick task (<60s) | Simple (Pattern 1) | - |
| Long task with progress | Long-Running (Pattern 2) | - |
| Multiple tasks in parallel | Concurrent (Pattern 3) | - |
| Launch and forget | Fire-and-Forget (Pattern 4) | - |
| Scheduled/recurring | Periodic (Pattern 5) | - |
| High-frequency (>10/min) | Pooled (Pattern 6) | - |

---

## Detailed Pattern Comparison

### Pattern 1: Simple Module Execution

**File**: `execution_patterns.py` → `execute_module()`

**When to Use:**
- Task completes in under 60 seconds
- You need the complete output immediately
- Simple, straightforward execution

**Benefits:**
- ✅ Simple to use - just call and await
- ✅ Full error handling built-in
- ✅ Complete output capture (stdout/stderr)
- ✅ Synchronous workflow - easy to reason about

**Limitations:**
- ❌ Blocks until complete
- ❌ No streaming output
- ❌ Not suitable for long-running tasks

**Example Use Cases:**
- Quick data validation
- File format conversion
- Simple calculations
- Configuration updates

**Code Example:**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
exit_code, stdout, stderr = await orchestrator.execute(
    script_path=Path("validate_data.py"),
    args=["--source", "data.csv"],
    pattern=TaskPattern.SIMPLE
)
if exit_code == 0:
    print(f"Success: {stdout}")
```

---

### Pattern 2: Long-Running Background Task

**File**: `execution_patterns.py` → `execute_long_running_task()`

**When to Use:**
- Task takes more than 60 seconds
- You need real-time progress updates
- Task should be cancellable

**Benefits:**
- ✅ Real-time output streaming via OutputCapture
- ✅ Cancellable mid-execution
- ✅ Progress tracking
- ✅ Better user experience for long operations

**Limitations:**
- ❌ More complex setup than Simple
- ❌ Requires OutputCapture integration
- ❌ Slightly more overhead

**Example Use Cases:**
- ML model training
- Large dataset processing
- Video encoding
- Database migrations

**Code Example:**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
exit_code = await orchestrator.execute(
    script_path=Path("train_model.py"),
    args=["--epochs", "100"],
    pattern=TaskPattern.LONG_RUNNING,
    streaming=True,
    run_id="training_job_123"
)
```

---

### Pattern 3: Concurrent Module Execution

**File**: `concurrent_executor.py` → `ConcurrentExecutor`

**When to Use:**
- Multiple independent tasks to run simultaneously
- Need to limit concurrent execution
- Batch processing scenarios

**Benefits:**
- ✅ Parallel execution for speed
- ✅ Resource limits with semaphores
- ✅ Batch processing support
- ✅ Efficient use of CPU/GPU resources

**Limitations:**
- ❌ Requires resource management
- ❌ Higher memory usage
- ❌ More complex error handling

**Example Use Cases:**
- Processing 100s of images/videos
- Batch API requests
- Parallel data transformations
- Multi-dataset evaluation

**Code Example:**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
results = await orchestrator.execute(
    script_path=Path("process_item.py"),
    args=["--batch"],
    pattern=TaskPattern.CONCURRENT,
    concurrent_tasks=10,
    max_concurrent=10,
    tasks=[item1, item2, item3, ...]
)
```

---

### Pattern 4: Fire-and-Forget with Tracking

**File**: `task_manager.py` → `BackgroundTaskManager`

**When to Use:**
- Launch task without waiting for result
- Need status tracking but not immediate result
- Background operations

**Benefits:**
- ✅ Non-blocking - returns immediately
- ✅ Status tracking via RunRegistry
- ✅ Background execution
- ✅ Can query status later

**Limitations:**
- ❌ No direct result access
- ❌ Requires polling for status
- ❌ More complex if you need the result

**Example Use Cases:**
- Sending analytics events
- Generating reports
- Email notifications
- Audit logging

**Code Example:**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
run = await orchestrator.execute(
    script_path=Path("send_email.py"),
    args=["--to", "user@example.com"],
    pattern=TaskPattern.FIRE_AND_FORGET,
    wait_for_result=False
)
# Returns immediately, check run.status later
```

---

### Pattern 5: Periodic Background Tasks

**File**: `periodic_tasks.py` → `PeriodicTaskManager`

**When to Use:**
- Task needs to run on a schedule
- Maintenance or cleanup operations
- Recurring data sync

**Benefits:**
- ✅ Automated scheduling
- ✅ Configurable intervals
- ✅ Built-in retry logic
- ✅ Enable/disable support

**Limitations:**
- ❌ Not for one-time tasks
- ❌ Requires scheduler management
- ❌ Task must be idempotent

**Example Use Cases:**
- Nightly cleanup
- Hourly data sync
- Health checks
- Cache invalidation

**Code Example:**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
task = await orchestrator.execute(
    script_path=Path("cleanup.py"),
    args=[],
    pattern=TaskPattern.PERIODIC,
    interval_seconds=3600,  # Every hour
    task_name="cleanup_temp_files"
)
```

---

### Pattern 6: Resource Pooling

**File**: `resource_pool.py` → `ResourcePool`

**When to Use:**
- High-frequency task execution (>10 tasks/min)
- Need to reuse expensive resources
- Performance is critical

**Benefits:**
- ✅ Resource reuse - better performance
- ✅ Lower overhead
- ✅ Connection pooling
- ✅ Optimized for throughput

**Limitations:**
- ❌ More complex initialization
- ❌ Pool size tuning needed
- ❌ Resource lifecycle management

**Example Use Cases:**
- API request handling
- Database queries
- Frequent file operations
- High-throughput services

**Code Example:**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
result = await orchestrator.execute(
    script_path=Path("query_db.py"),
    args=["--query", "SELECT * FROM users"],
    pattern=TaskPattern.POOLED,
    use_pool=True
)
```

---

## Pattern Selection Flowchart

```
Start
  │
  ├─ Runs on schedule? ──YES──> Pattern 5 (Periodic)
  │       │
  │      NO
  │       │
  ├─ Need streaming output? ──YES──> Pattern 2 (Long-Running)
  │       │
  │      NO
  │       │
  ├─ Multiple tasks in parallel? ──YES──> Pattern 3 (Concurrent)
  │       │
  │      NO
  │       │
  ├─ Don't need result? ──YES──> Pattern 4 (Fire-and-Forget)
  │       │
  │      NO
  │       │
  ├─ High frequency (>10/min)? ──YES──> Pattern 6 (Pooled)
  │       │
  │      NO
  │       │
  └─────> Pattern 1 (Simple)
```

---

## Performance Comparison

| Pattern | Overhead | Throughput | Memory | Best For |
|---------|----------|------------|--------|----------|
| Simple | Low | Medium | Low | Single tasks |
| Long-Running | Medium | Low | Medium | Progress tracking |
| Concurrent | High | High | High | Batch processing |
| Fire-and-Forget | Low | High | Low | Background ops |
| Periodic | Medium | N/A | Medium | Scheduled tasks |
| Pooled | Low | Very High | Medium | High frequency |

---

## Combining Patterns

Patterns can be combined in the same workflow:

### Example: Video Processing Pipeline

```python
# 1. Periodic cleanup (Pattern 5)
await orchestrator.execute(
    script_path=Path("cleanup.py"),
    pattern=TaskPattern.PERIODIC,
    interval_seconds=3600
)

# 2. Concurrent batch processing (Pattern 3)
results = await orchestrator.execute(
    script_path=Path("process_videos.py"),
    pattern=TaskPattern.CONCURRENT,
    concurrent_tasks=5,
    tasks=video_list
)

# 3. Send notification (Pattern 4)
await orchestrator.execute(
    script_path=Path("notify.py"),
    pattern=TaskPattern.FIRE_AND_FORGET,
    wait_for_result=False
)
```

---

## Common Pitfalls

### Pattern 1 (Simple)
- ❌ Using for long-running tasks → Use Pattern 2
- ❌ Using for multiple tasks → Use Pattern 3

### Pattern 2 (Long-Running)
- ❌ Forgetting OutputCapture setup
- ❌ Not handling cancellation properly

### Pattern 3 (Concurrent)
- ❌ No semaphore limits → Resource exhaustion
- ❌ Too many concurrent tasks → Performance degradation

### Pattern 4 (Fire-and-Forget)
- ❌ Expecting immediate results
- ❌ Not checking status later

### Pattern 5 (Periodic)
- ❌ Non-idempotent tasks → Duplicate operations
- ❌ Forgetting to disable when not needed

### Pattern 6 (Pooled)
- ❌ Pool size too small → Bottleneck
- ❌ Pool size too large → Resource waste

---

## Migration Between Patterns

### From Simple → Long-Running
```python
# Before
exit_code, stdout, stderr = await execute_module(script_path, args, cwd)

# After
from Client.Backend.src.core import TaskOrchestrator, TaskPattern
orchestrator = TaskOrchestrator()
exit_code = await orchestrator.execute(
    script_path=script_path,
    args=args,
    pattern=TaskPattern.LONG_RUNNING,
    streaming=True
)
```

### From Direct → Concurrent
```python
# Before
for item in items:
    result = await process(item)

# After
orchestrator = TaskOrchestrator()
results = await orchestrator.execute(
    script_path=Path("process.py"),
    pattern=TaskPattern.CONCURRENT,
    concurrent_tasks=5,
    tasks=items
)
```

---

## Summary

**Use PatternAdvisor for automatic selection:**
```python
from Client.Backend.src.core import PatternAdvisor

pattern = PatternAdvisor.recommend(
    expected_duration_seconds=300,
    requires_streaming=True,
    concurrent_tasks=1,
    needs_result=True,
    recurring=False,
    high_frequency=False
)
```

**Or let TaskOrchestrator auto-select:**
```python
# Auto-selects based on kwargs
result = await orchestrator.execute(
    script_path=Path("task.py"),
    streaming=True  # Auto-selects LONG_RUNNING
)
```

---

**For more details**, see:
- `Client/Backend/_meta/docs/BACKGROUND_TASKS_BEST_PRACTICES.md`
- `Client/Backend/src/core/task_orchestrator.py`
- `Client/Backend/_meta/examples/pattern_integration_examples.py`
