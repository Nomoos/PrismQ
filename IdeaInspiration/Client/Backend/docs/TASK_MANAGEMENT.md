# Task Management Guide

**Module**: Client Backend  
**Component**: BackgroundTaskManager  
**Pattern**: Fire-and-Forget with Tracking (Pattern 4)  
**Last Updated**: 2025-11-05

## Overview

The `BackgroundTaskManager` provides a clean interface for launching background tasks without waiting for completion while maintaining automatic status tracking. This implements Pattern 4 from the [Background Tasks Best Practices](./BACKGROUND_TASKS_BEST_PRACTICES.md) guide.

## Key Features

- **Fire-and-Forget Execution**: Start tasks and return immediately
- **Automatic Status Tracking**: Tasks automatically update their status in the RunRegistry
- **Task Cancellation**: Cancel running tasks gracefully
- **Graceful Shutdown**: Wait for all tasks to complete before shutdown
- **Exception Handling**: Automatic exception catching with status propagation
- **SOLID Design**: Clean separation of concerns with dependency injection

## Quick Start

### Basic Usage

```python
import asyncio
from datetime import datetime, timezone
from src.core.task_manager import BackgroundTaskManager
from src.core.run_registry import RunRegistry
from src.models.run import Run, RunStatus

# Initialize
registry = RunRegistry()
task_manager = BackgroundTaskManager(registry)

# Create a run object
run = Run(
    run_id="unique-task-id",
    module_id="my-module",
    module_name="My Module",
    status=RunStatus.QUEUED,
    created_at=datetime.now(timezone.utc),
    parameters={"key": "value"}
)

# Define your background work
async def my_background_work():
    await asyncio.sleep(5)
    # Do some work
    return "result"

# Add run to registry
registry.add_run(run)

# Start the task (returns immediately)
task_id = task_manager.start_task(run, my_background_work())

# Task runs in background, status automatically tracked
# You can continue with other work here

# Later, before shutdown:
await task_manager.wait_all()
```

## API Reference

### BackgroundTaskManager

#### Constructor

```python
BackgroundTaskManager(registry: RunRegistry)
```

**Parameters:**
- `registry`: RunRegistry instance for tracking task status

**Example:**
```python
registry = RunRegistry()
task_manager = BackgroundTaskManager(registry)
```

#### start_task

```python
start_task(run: Run, coro: Awaitable) -> str
```

Start a background task without waiting for completion.

**Parameters:**
- `run`: Run object for tracking (should have status=QUEUED)
- `coro`: Coroutine to execute in the background

**Returns:**
- `str`: Run ID for tracking the task

**Example:**
```python
async def my_task():
    await asyncio.sleep(10)
    return "done"

task_id = task_manager.start_task(run, my_task())
print(f"Started task: {task_id}")
# Returns immediately, task runs in background
```

#### cancel_task

```python
async cancel_task(run_id: str) -> bool
```

Cancel a running background task.

**Parameters:**
- `run_id`: ID of the task to cancel

**Returns:**
- `bool`: True if task was successfully cancelled, False if not found or already completed

**Example:**
```python
success = await task_manager.cancel_task("task-123")
if success:
    print("Task cancelled successfully")
else:
    print("Task not found or already completed")
```

#### wait_all

```python
async wait_all() -> None
```

Wait for all background tasks to complete. Useful for graceful shutdown.

**Example:**
```python
# Before shutting down the application
await task_manager.wait_all()
print("All background tasks completed")
```

#### get_active_task_count

```python
get_active_task_count() -> int
```

Get the number of currently active tasks.

**Returns:**
- `int`: Number of tasks currently running

**Example:**
```python
count = task_manager.get_active_task_count()
print(f"Active tasks: {count}")
```

#### get_active_task_ids

```python
get_active_task_ids() -> List[str]
```

Get IDs of all active tasks.

**Returns:**
- `List[str]`: List of run IDs for active tasks

**Example:**
```python
active_ids = task_manager.get_active_task_ids()
for task_id in active_ids:
    print(f"Task {task_id} is running")
```

#### is_task_active

```python
is_task_active(run_id: str) -> bool
```

Check if a task is currently active.

**Parameters:**
- `run_id`: Run ID to check

**Returns:**
- `bool`: True if task is active, False otherwise

**Example:**
```python
if task_manager.is_task_active("task-123"):
    print("Task is still running")
else:
    print("Task completed or not found")
```

## Status Flow

The BackgroundTaskManager automatically manages the following status transitions:

```
QUEUED → RUNNING → COMPLETED (success)
                 → FAILED (exception)
                 → CANCELLED (cancelled)
```

### Status Details

| Status | Description | Trigger |
|--------|-------------|---------|
| QUEUED | Initial state before task starts | Set by caller before calling start_task |
| RUNNING | Task is currently executing | Automatically set when task starts |
| COMPLETED | Task finished successfully | Automatically set when task completes without exception |
| FAILED | Task raised an exception | Automatically set when task raises exception |
| CANCELLED | Task was cancelled | Automatically set when cancel_task is called |

## Usage Patterns

### Pattern 1: Simple Background Task

```python
# Start a simple background task
async def cleanup_old_data():
    await asyncio.sleep(1)
    # Perform cleanup
    print("Cleanup complete")

run = Run(
    run_id="cleanup-task",
    module_id="maintenance",
    module_name="Cleanup",
    status=RunStatus.QUEUED,
    created_at=datetime.now(timezone.utc),
    parameters={}
)

registry.add_run(run)
task_manager.start_task(run, cleanup_old_data())
```

### Pattern 2: Multiple Concurrent Tasks

```python
# Start multiple tasks concurrently
tasks = []
for i in range(5):
    run = Run(
        run_id=f"task-{i}",
        module_id="batch-processor",
        module_name="Batch Processor",
        status=RunStatus.QUEUED,
        created_at=datetime.now(timezone.utc),
        parameters={"index": i}
    )
    registry.add_run(run)
    
    async def process_item(index):
        await asyncio.sleep(1)
        print(f"Processed item {index}")
    
    task_manager.start_task(run, process_item(i))

print(f"Started {task_manager.get_active_task_count()} tasks")
```

### Pattern 3: Task with Cancellation

```python
# Start a long-running task that can be cancelled
async def long_operation():
    try:
        for i in range(100):
            await asyncio.sleep(0.1)
            print(f"Step {i}")
    except asyncio.CancelledError:
        print("Operation cancelled")
        raise

run = Run(
    run_id="long-task",
    module_id="processor",
    module_name="Processor",
    status=RunStatus.QUEUED,
    created_at=datetime.now(timezone.utc),
    parameters={}
)

registry.add_run(run)
task_id = task_manager.start_task(run, long_operation())

# Later, if needed:
await task_manager.cancel_task(task_id)
```

### Pattern 4: Graceful Shutdown

```python
# Application shutdown handler
async def shutdown_handler():
    print("Shutting down...")
    
    # Cancel all active tasks
    active_tasks = task_manager.get_active_task_ids()
    for task_id in active_tasks:
        await task_manager.cancel_task(task_id)
    
    # Or wait for all to complete naturally
    await task_manager.wait_all()
    
    print("All background tasks completed")
```

### Pattern 5: Monitoring Task Progress

```python
# Monitor active tasks
async def monitor_tasks():
    while True:
        active_count = task_manager.get_active_task_count()
        active_ids = task_manager.get_active_task_ids()
        
        print(f"Active tasks: {active_count}")
        
        for task_id in active_ids:
            run = registry.get_run(task_id)
            print(f"  {task_id}: {run.status}")
        
        await asyncio.sleep(5)
```

## Integration with Existing Code

### With ModuleRunner

The BackgroundTaskManager can be integrated with the existing ModuleRunner to provide fire-and-forget module execution:

```python
from src.core.module_runner import ModuleRunner
from src.core.task_manager import BackgroundTaskManager

# Existing ModuleRunner
module_runner = ModuleRunner(
    registry=registry,
    process_manager=process_manager
)

# New BackgroundTaskManager
task_manager = BackgroundTaskManager(registry)

# Execute module in background
async def run_module_async(module_id: str, parameters: dict):
    run = await module_runner.execute_module(module_id, parameters)
    # Module execution happens asynchronously via ModuleRunner
    return run

# Start as background task
run = Run(
    run_id="module-run-123",
    module_id="youtube-source",
    module_name="YouTube Source",
    status=RunStatus.QUEUED,
    created_at=datetime.now(timezone.utc),
    parameters={"channel": "example"}
)

registry.add_run(run)
task_manager.start_task(run, run_module_async("youtube-source", {"channel": "example"}))
```

### With FastAPI Endpoints

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

# Global task manager (initialized at startup)
task_manager: BackgroundTaskManager = None

@app.on_event("startup")
async def startup_event():
    global task_manager
    registry = RunRegistry()
    task_manager = BackgroundTaskManager(registry)

@app.post("/modules/{module_id}/run-async")
async def run_module_async(module_id: str, parameters: dict):
    """Start a module run in the background."""
    run = Run(
        run_id=str(uuid.uuid4()),
        module_id=module_id,
        module_name=module_id.title(),
        status=RunStatus.QUEUED,
        created_at=datetime.now(timezone.utc),
        parameters=parameters
    )
    
    async def module_work():
        # Actual module execution logic
        await asyncio.sleep(10)
    
    registry.add_run(run)
    task_id = task_manager.start_task(run, module_work())
    
    return {"task_id": task_id, "status": "started"}

@app.delete("/tasks/{task_id}")
async def cancel_task_endpoint(task_id: str):
    """Cancel a running task."""
    success = await task_manager.cancel_task(task_id)
    return {"success": success}

@app.get("/tasks/active")
async def get_active_tasks():
    """Get list of active tasks."""
    return {
        "count": task_manager.get_active_task_count(),
        "tasks": task_manager.get_active_task_ids()
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Wait for all tasks before shutdown."""
    await task_manager.wait_all()
```

## Error Handling

### Exception Propagation

Exceptions in background tasks are caught and logged, with the task status updated to FAILED:

```python
async def failing_task():
    raise ValueError("Something went wrong")

# This will:
# 1. Catch the exception
# 2. Log it with logger.exception()
# 3. Set run.status = RunStatus.FAILED
# 4. Set run.error_message = "Something went wrong"
# 5. Update the registry
```

### Cancellation Handling

Tasks can be cancelled gracefully:

```python
async def cancellable_task():
    try:
        for i in range(100):
            await asyncio.sleep(0.1)
            # Cancellation can occur at any await point
    except asyncio.CancelledError:
        # Clean up resources
        print("Task cancelled, cleaning up")
        raise  # Re-raise to mark as cancelled
```

## Best Practices

### ✅ DO

1. **Always add run to registry before starting task**
   ```python
   registry.add_run(run)
   task_manager.start_task(run, my_task())
   ```

2. **Use unique run IDs**
   ```python
   run_id = str(uuid.uuid4())
   ```

3. **Handle CancelledError in long tasks**
   ```python
   async def my_task():
       try:
           # work
       except asyncio.CancelledError:
           # cleanup
           raise
   ```

4. **Wait for all tasks before shutdown**
   ```python
   await task_manager.wait_all()
   ```

5. **Monitor active task count to avoid overload**
   ```python
   if task_manager.get_active_task_count() > max_tasks:
       # Wait or reject new tasks
   ```

### ❌ DON'T

1. **Don't start task without adding to registry first**
   ```python
   # Bad - run not in registry
   task_manager.start_task(run, my_task())
   ```

2. **Don't reuse run IDs without completing previous task**
   ```python
   # Bad - may cause confusion
   task_manager.start_task(run, task1())
   task_manager.start_task(run, task2())  # Same run object
   ```

3. **Don't ignore active tasks during shutdown**
   ```python
   # Bad - tasks may be terminated abruptly
   sys.exit(0)
   ```

4. **Don't swallow CancelledError**
   ```python
   # Bad - cancellation won't propagate
   try:
       await asyncio.sleep(10)
   except asyncio.CancelledError:
       pass  # Don't just ignore it
   ```

5. **Don't create unbounded tasks**
   ```python
   # Bad - could exhaust system resources
   while True:
       task_manager.start_task(run, my_task())
   ```

## Testing

See the comprehensive test suite in `_meta/tests/test_task_manager.py` for examples of:

- Unit testing task execution
- Testing cancellation
- Testing multiple concurrent tasks
- Integration testing with RunRegistry
- Edge case handling

Run tests with:

```bash
pytest _meta/tests/test_task_manager.py -v
```

## Performance Considerations

- **Task Overhead**: Each task has minimal overhead (~1KB memory)
- **Concurrency Limit**: No hard limit, but monitor system resources
- **Status Updates**: Registry updates are synchronous but fast (~1ms)
- **Cleanup**: Tasks are automatically removed from active list on completion

## Troubleshooting

### Tasks not starting

**Symptom**: `start_task` returns but task never runs

**Possible Causes:**
- Event loop not running
- Coroutine not properly awaited
- Exception during task startup

**Solution:**
- Ensure you're in an async context
- Check logs for exceptions
- Verify run object is valid

### Tasks not completing

**Symptom**: `wait_all` hangs indefinitely

**Possible Causes:**
- Task has infinite loop
- Task is waiting on external resource
- Deadlock condition

**Solution:**
- Use timeouts in task code
- Check for blocking operations
- Use cancel_task to interrupt

### Memory leaks

**Symptom**: Memory usage grows over time

**Possible Causes:**
- Tasks not being removed from active list
- Registry not being cleaned up
- Large objects in run parameters

**Solution:**
- Ensure tasks complete or are cancelled
- Use `registry.cleanup_old_runs()` periodically
- Limit parameter size

## Related Documentation

- [Background Tasks Best Practices](./BACKGROUND_TASKS_BEST_PRACTICES.md) - Full guide with all patterns
- [API Reference](./API_REFERENCE.md) - Complete API documentation
- [Run Registry](../src/core/run_registry.py) - Run tracking implementation
- [Module Runner](../src/core/module_runner.py) - Module execution service

## See Also

- **Pattern 1**: Simple Module Execution
- **Pattern 2**: Long-Running Background Task
- **Pattern 3**: Concurrent Module Execution
- **Pattern 5**: Periodic Background Tasks
- **Pattern 6**: Resource Pooling

## Contributing

When extending BackgroundTaskManager:

1. Follow SOLID principles
2. Add comprehensive tests
3. Update this documentation
4. Consider backward compatibility
5. Log important events

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-05 | Initial implementation of Pattern 4 |
