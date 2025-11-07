# Migration Guide - TaskOrchestrator Integration

**Purpose**: Guide for migrating existing code to use the new TaskOrchestrator and pattern-based architecture.

**Last Updated**: 2025-11-05

---

## Overview

This guide helps you migrate from:
- Direct `execute_module()` calls → TaskOrchestrator
- Direct pattern usage → Unified orchestrator interface
- Custom subprocess handling → Standardized patterns

---

## Quick Migration Checklist

- [ ] Identify current task execution patterns
- [ ] Map to appropriate TaskPattern
- [ ] Update imports to use TaskOrchestrator
- [ ] Test with new interface
- [ ] Update error handling
- [ ] Verify all functionality works

---

## Migration Scenarios

### Scenario 1: From Direct execute_module() to TaskOrchestrator

**Before:**
```python
from Client.Backend.src.core.execution_patterns import execute_module
from pathlib import Path

# Direct function call
exit_code, stdout, stderr = await execute_module(
    script_path=Path("process.py"),
    args=["--input", "data.csv"],
    cwd=Path("/path/to/cwd")
)

if exit_code == 0:
    print(f"Success: {stdout}")
else:
    print(f"Error: {stderr}")
```

**After (Pattern 1 - Simple):**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern
from pathlib import Path

# Using TaskOrchestrator
orchestrator = TaskOrchestrator()
exit_code, stdout, stderr = await orchestrator.execute(
    script_path=Path("process.py"),
    args=["--input", "data.csv"],
    pattern=TaskPattern.SIMPLE,  # Explicit pattern
    cwd=Path("/path/to/cwd")
)

if exit_code == 0:
    print(f"Success: {stdout}")
else:
    print(f"Error: {stderr}")
```

**Or with auto-selection:**
```python
from Client.Backend.src.core import TaskOrchestrator
from pathlib import Path

orchestrator = TaskOrchestrator()
# Let orchestrator auto-select SIMPLE pattern (default)
exit_code, stdout, stderr = await orchestrator.execute(
    script_path=Path("process.py"),
    args=["--input", "data.csv"],
    cwd=Path("/path/to/cwd")
)
```

---

### Scenario 2: From Loop to Concurrent Execution

**Before:**
```python
results = []
for video_path in video_paths:
    exit_code, stdout, stderr = await execute_module(
        script_path=Path("process_video.py"),
        args=[str(video_path)],
        cwd=Path.cwd()
    )
    results.append((exit_code, stdout, stderr))
```

**After (Pattern 3 - Concurrent):**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
results = await orchestrator.execute(
    script_path=Path("process_video.py"),
    args=["--batch"],
    pattern=TaskPattern.CONCURRENT,
    concurrent_tasks=5,  # Process 5 at a time
    tasks=video_paths
)
```

**Benefits:**
- ✅ Parallel execution (much faster)
- ✅ Resource limits automatically enforced
- ✅ Better error handling

---

### Scenario 3: From Blocking to Fire-and-Forget

**Before:**
```python
# This blocks waiting for email to send
exit_code, stdout, stderr = await execute_module(
    script_path=Path("send_email.py"),
    args=["--to", "user@example.com", "--subject", "Report"],
    cwd=Path.cwd()
)
# Continue after email sent
process_next_task()
```

**After (Pattern 4 - Fire-and-Forget):**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
# Returns immediately, email sent in background
run = await orchestrator.execute(
    script_path=Path("send_email.py"),
    args=["--to", "user@example.com", "--subject", "Report"],
    pattern=TaskPattern.FIRE_AND_FORGET,
    wait_for_result=False
)
# Continue immediately (don't wait for email)
process_next_task()

# Optional: Check status later
# status = run.status
```

**Benefits:**
- ✅ Non-blocking - continue immediately
- ✅ Status tracking available if needed
- ✅ Better user experience

---

### Scenario 4: From Manual Scheduling to Periodic Tasks

**Before:**
```python
import asyncio

async def cleanup_loop():
    while True:
        exit_code, stdout, stderr = await execute_module(
            script_path=Path("cleanup.py"),
            args=[],
            cwd=Path.cwd()
        )
        await asyncio.sleep(3600)  # Wait 1 hour

# Start in background
asyncio.create_task(cleanup_loop())
```

**After (Pattern 5 - Periodic):**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
# Set up periodic task - automatically managed
task = await orchestrator.execute(
    script_path=Path("cleanup.py"),
    args=[],
    pattern=TaskPattern.PERIODIC,
    interval_seconds=3600,  # Every hour
    task_name="cleanup_temp_files",
    enabled=True
)

# Task runs automatically every hour
# Can disable later: task.enabled = False
```

**Benefits:**
- ✅ Automatic scheduling
- ✅ Built-in error handling and retry
- ✅ Easy enable/disable

---

### Scenario 5: Adding Progress Tracking to Long Tasks

**Before:**
```python
# No progress visibility
exit_code, stdout, stderr = await execute_module(
    script_path=Path("train_model.py"),
    args=["--epochs", "100"],
    cwd=Path.cwd()
)
# User waits with no updates
```

**After (Pattern 2 - Long-Running):**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
# Streams progress in real-time
exit_code = await orchestrator.execute(
    script_path=Path("train_model.py"),
    args=["--epochs", "100"],
    pattern=TaskPattern.LONG_RUNNING,
    streaming=True,
    run_id="training_session_123"
)

# Progress streamed via OutputCapture
# User sees real-time updates
```

**Benefits:**
- ✅ Real-time progress updates
- ✅ Cancellable mid-execution
- ✅ Better user experience

---

### Scenario 6: High-Frequency Tasks with Pooling

**Before:**
```python
# Creates new subprocess for each request
for i in range(1000):
    exit_code, stdout, stderr = await execute_module(
        script_path=Path("query.py"),
        args=["--id", str(i)],
        cwd=Path.cwd()
    )
    # Slow due to subprocess creation overhead
```

**After (Pattern 6 - Pooled):**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

orchestrator = TaskOrchestrator()
# Reuses resources from pool
for i in range(1000):
    result = await orchestrator.execute(
        script_path=Path("query.py"),
        args=["--id", str(i)],
        pattern=TaskPattern.POOLED,
        use_pool=True
    )
# Much faster due to resource reuse
```

**Benefits:**
- ✅ Resource reuse - better performance
- ✅ Lower overhead
- ✅ Optimized for high throughput

---

## Step-by-Step Migration Process

### Step 1: Analyze Current Code

Identify all places where you:
1. Call `execute_module()` directly
2. Use `execute_long_running_task()` directly
3. Manage background tasks manually
4. Have custom scheduling logic
5. Create subprocesses directly

### Step 2: Choose Patterns

For each identified usage, select the appropriate pattern:

| Current Code | Recommended Pattern | Reason |
|--------------|-------------------|--------|
| Simple subprocess call | Pattern 1 (Simple) | Direct replacement |
| Long task with output | Pattern 2 (Long-Running) | Add progress tracking |
| Loop processing items | Pattern 3 (Concurrent) | Parallelize for speed |
| Background operation | Pattern 4 (Fire-and-Forget) | Non-blocking |
| Scheduled task | Pattern 5 (Periodic) | Automated scheduling |
| High-frequency calls | Pattern 6 (Pooled) | Performance optimization |

### Step 3: Update Imports

**Old imports:**
```python
from Client.Backend.src.core.execution_patterns import execute_module
from Client.Backend.src.core.execution_patterns import execute_long_running_task
from Client.Backend.src.core.concurrent_executor import ConcurrentExecutor
from Client.Backend.src.core.task_manager import BackgroundTaskManager
from Client.Backend.src.core.periodic_tasks import PeriodicTaskManager
from Client.Backend.src.core.resource_pool import ResourcePool
```

**New imports:**
```python
from Client.Backend.src.core import TaskOrchestrator, TaskPattern, PatternAdvisor
```

That's it! One import instead of many.

### Step 4: Create Orchestrator Instance

**Add once in your module/class:**
```python
orchestrator = TaskOrchestrator()
```

**Or use dependency injection:**
```python
class MyService:
    def __init__(self, orchestrator: TaskOrchestrator = None):
        self.orchestrator = orchestrator or TaskOrchestrator()
```

### Step 5: Update Task Execution

Replace direct pattern calls with orchestrator:

```python
# Instead of managing patterns separately:
result = await self.orchestrator.execute(
    script_path=script_path,
    args=args,
    pattern=TaskPattern.SIMPLE,  # or auto-select
    **options
)
```

### Step 6: Update Error Handling

Error handling is similar, but return types may differ:

```python
try:
    result = await orchestrator.execute(
        script_path=Path("task.py"),
        args=[],
        pattern=TaskPattern.SIMPLE
    )
    # result is (exit_code, stdout, stderr) for SIMPLE
    exit_code, stdout, stderr = result
except FileNotFoundError:
    logger.error("Script not found")
except Exception as e:
    logger.error(f"Execution failed: {e}")
```

### Step 7: Test Thoroughly

Test each migrated function:
1. ✅ Basic functionality works
2. ✅ Error handling works
3. ✅ Performance is acceptable
4. ✅ Resource cleanup happens

---

## Pattern-Specific Migration Notes

### Pattern 1 (Simple)
- **Return type**: `Tuple[int, str, str]` (exit_code, stdout, stderr)
- **Backward compatible**: Yes, drop-in replacement
- **Changes needed**: Minimal

### Pattern 2 (Long-Running)
- **Return type**: `int` (exit_code only)
- **Requires**: `run_id` parameter for tracking
- **Output access**: Via OutputCapture, not return value

### Pattern 3 (Concurrent)
- **Return type**: `List[Any]` (list of results)
- **Requires**: `tasks` parameter with items to process
- **Changes needed**: Restructure loop to batch operation

### Pattern 4 (Fire-and-Forget)
- **Return type**: `Run` object
- **Access result**: Poll `run.status` later
- **Changes needed**: Remove result-dependent code

### Pattern 5 (Periodic)
- **Return type**: `PeriodicTask` object
- **Management**: Enable/disable via task object
- **Changes needed**: Remove manual scheduling loop

### Pattern 6 (Pooled)
- **Return type**: Same as underlying execution
- **Requires**: Pool initialization
- **Changes needed**: Add `use_pool=True`

---

## Common Migration Issues

### Issue 1: Different Return Types

**Problem**: Pattern 2 returns `int` instead of tuple

**Solution**: Access output via OutputCapture
```python
from Client.Backend.src.core import get_output_capture

output_capture = get_output_capture()
exit_code = await orchestrator.execute(
    script_path=Path("task.py"),
    pattern=TaskPattern.LONG_RUNNING,
    run_id="my_task"
)
# Get output from OutputCapture
lines = output_capture.get_output("my_task")
```

### Issue 2: Auto-Selection Not Working

**Problem**: Wrong pattern auto-selected

**Solution**: Be explicit or adjust kwargs
```python
# Option 1: Be explicit
result = await orchestrator.execute(
    script_path=Path("task.py"),
    pattern=TaskPattern.SIMPLE  # Explicit
)

# Option 2: Adjust kwargs for auto-selection
result = await orchestrator.execute(
    script_path=Path("task.py"),
    streaming=True  # Forces LONG_RUNNING
)
```

### Issue 3: Missing Dependencies

**Problem**: Pattern needs RunRegistry or other dependencies

**Solution**: Use singleton getters
```python
from Client.Backend.src.core import get_run_registry

registry = get_run_registry()
# Registry automatically provided to patterns
```

---

## Testing Your Migration

### Unit Tests

```python
import pytest
from Client.Backend.src.core import TaskOrchestrator, TaskPattern

@pytest.mark.asyncio
async def test_simple_execution():
    orchestrator = TaskOrchestrator()
    exit_code, stdout, stderr = await orchestrator.execute(
        script_path=Path("test_script.py"),
        args=[],
        pattern=TaskPattern.SIMPLE
    )
    assert exit_code == 0
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_workflow_migration():
    """Test migrated workflow works end-to-end"""
    orchestrator = TaskOrchestrator()
    
    # Your migrated workflow
    result = await my_migrated_function(orchestrator)
    
    # Verify results
    assert result is not None
```

---

## Performance Comparison

Measure before and after migration:

```python
import time

# Before migration
start = time.time()
for item in items:
    await old_function(item)
old_duration = time.time() - start

# After migration
start = time.time()
result = await orchestrator.execute(
    script_path=Path("process.py"),
    pattern=TaskPattern.CONCURRENT,
    tasks=items
)
new_duration = time.time() - start

print(f"Speedup: {old_duration / new_duration:.2f}x")
```

---

## Rollback Strategy

If migration causes issues, you can rollback:

1. **Keep old code temporarily:**
```python
# Old implementation (keep for now)
def old_execute(script_path, args):
    from Client.Backend.src.core.execution_patterns import execute_module
    return execute_module(script_path, args, Path.cwd())

# New implementation
def new_execute(script_path, args):
    orchestrator = TaskOrchestrator()
    return orchestrator.execute(script_path, args, pattern=TaskPattern.SIMPLE)

# Use feature flag
if USE_NEW_ORCHESTRATOR:
    execute = new_execute
else:
    execute = old_execute
```

2. **Gradual migration:**
   - Migrate one module at a time
   - Test thoroughly before next module
   - Keep old code until all tests pass

---

## Getting Help

**PatternAdvisor can help choose the right pattern:**
```python
from Client.Backend.src.core import PatternAdvisor

# Get recommendation
pattern = PatternAdvisor.recommend(
    expected_duration_seconds=120,
    requires_streaming=True
)

# Get explanation
info = PatternAdvisor.explain(pattern)
print(f"Use when: {info['use_when']}")
print(f"Benefits: {info['benefits']}")
```

**Documentation:**
- Pattern details: `Client/Backend/_meta/docs/BACKGROUND_TASKS_BEST_PRACTICES.md`
- Pattern comparison: `Client/Backend/_meta/docs/PATTERN_COMPARISON.md`
- Examples: `Client/Backend/_meta/examples/pattern_integration_examples.py`

---

## Summary

**Migration is straightforward:**

1. ✅ Import `TaskOrchestrator` and `TaskPattern`
2. ✅ Create orchestrator instance
3. ✅ Replace direct calls with `orchestrator.execute()`
4. ✅ Choose pattern (or let it auto-select)
5. ✅ Test thoroughly

**Benefits after migration:**

- ✅ Unified interface for all patterns
- ✅ Auto-pattern selection
- ✅ Better error handling
- ✅ Easier testing
- ✅ More maintainable code

**Questions?** See examples in `Client/Backend/_meta/examples/pattern_integration_examples.py`
