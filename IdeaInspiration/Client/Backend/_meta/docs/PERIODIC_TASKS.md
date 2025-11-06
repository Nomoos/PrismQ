# Periodic Tasks Guide

**Platform**: Windows (primary), Linux/macOS (supported)  
**Last Updated**: 2025-11-05

## Overview

The PrismQ Client Backend includes a robust periodic task system for running scheduled maintenance operations, health checks, and cleanup tasks. This guide explains how to use the periodic task infrastructure and create custom periodic tasks.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Built-in Maintenance Tasks](#built-in-maintenance-tasks)
4. [Creating Custom Tasks](#creating-custom-tasks)
5. [Task Management](#task-management)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Using Built-in Maintenance Tasks

The backend automatically starts several maintenance tasks on startup:

```python
# In src/main.py - these are started automatically
from src.core.periodic_tasks import PeriodicTaskManager
from src.core.maintenance import MAINTENANCE_TASKS

# Manager is initialized globally
periodic_task_manager = PeriodicTaskManager()

# Tasks are registered and started during application startup
# See lifespan() function in main.py
```

**Default Maintenance Tasks**:
- **cleanup_old_runs** - Runs every 1 hour, removes run data older than 24 hours
- **system_health_check** - Runs every 5 minutes, monitors system resources
- **cleanup_temp_files** - Runs every 6 hours, removes old temporary files
- **log_statistics** - Runs every 15 minutes, logs system statistics

### Creating a Simple Periodic Task

```python
from datetime import timedelta
from src.core.periodic_tasks import PeriodicTask

async def my_task():
    """Custom periodic task."""
    print("Running my periodic task!")
    # Your task logic here

# Create and start the task
task = PeriodicTask(
    name="my_task",
    interval=timedelta(minutes=30),
    task_func=my_task
)
task.start()

# Later... stop the task
await task.stop()
```

---

## Core Concepts

### PeriodicTask Class

The `PeriodicTask` class provides the foundation for periodic execution:

**Key Features**:
- ✅ **Configurable intervals** using `timedelta`
- ✅ **Graceful start/stop** with event signaling
- ✅ **Error handling** - errors don't stop the scheduler
- ✅ **Statistics tracking** - run count, error count, last run time
- ✅ **Resource cleanup** - proper asyncio task management

**Example**:

```python
from datetime import timedelta
from src.core.periodic_tasks import PeriodicTask

async def cleanup_task():
    """Clean up temporary data."""
    # Cleanup logic here
    pass

task = PeriodicTask(
    name="cleanup",
    interval=timedelta(hours=1),
    task_func=cleanup_task
)

# Start the task
task.start()

# Check if running
if task.is_running:
    print("Task is running")

# Get statistics
stats = task.statistics
print(f"Runs: {stats['run_count']}, Errors: {stats['error_count']}")

# Stop the task
await task.stop()
```

### PeriodicTaskManager Class

The `PeriodicTaskManager` class provides centralized management of multiple tasks:

**Key Features**:
- ✅ **Centralized registration** of multiple tasks
- ✅ **Lifecycle management** - start/stop all tasks together
- ✅ **Statistics aggregation** - get stats for all tasks
- ✅ **Name-based lookup** - retrieve tasks by name

**Example**:

```python
from datetime import timedelta
from src.core.periodic_tasks import PeriodicTaskManager

manager = PeriodicTaskManager()

# Register multiple tasks
manager.register_task(
    name="task1",
    interval=timedelta(minutes=5),
    task_func=my_task_1
)
manager.register_task(
    name="task2",
    interval=timedelta(minutes=10),
    task_func=my_task_2
)

# Start all tasks at once
manager.start_all()

# Get a specific task
task1 = manager.get_task("task1")

# Get statistics for all tasks
all_stats = manager.get_all_statistics()

# Stop all tasks
await manager.stop_all()
```

---

## Built-in Maintenance Tasks

### 1. Cleanup Old Runs

**Function**: `cleanup_old_runs(max_age_hours, registry)`

Removes completed run data older than the specified age to prevent unbounded growth of the run registry.

**Configuration**:
```python
{
    "name": "cleanup_old_runs",
    "interval": timedelta(hours=1),
    "func": cleanup_old_runs,
    "kwargs": {"max_age_hours": 24},
    "description": "Clean up run data older than 24 hours"
}
```

**Behavior**:
- Runs every 1 hour
- Removes runs with status `COMPLETED`, `FAILED`, or `CANCELLED`
- Only removes runs older than 24 hours
- Keeps `RUNNING` runs regardless of age
- Logs number of runs cleaned up

### 2. System Health Check

**Function**: `check_system_health()`

Monitors system resources and logs warnings if any are concerning.

**Configuration**:
```python
{
    "name": "system_health_check",
    "interval": timedelta(minutes=5),
    "func": check_system_health,
    "description": "Monitor system resource usage"
}
```

**Monitored Resources**:
- **Memory usage** - warns if >80%
- **Disk usage** - warns if >90%
- **CPU usage** - warns if >90% (1-second average)
- **Asyncio tasks** - warns if >100 active tasks

**Returns**:
```python
{
    "timestamp": "2025-11-05T12:00:00",
    "status": "healthy",  # or "warning", "error"
    "checks": {
        "memory": {"percent_used": 60.0, "status": "ok"},
        "disk": {"percent_used": 70.0, "status": "ok"},
        "cpu": {"percent_used": 30.0, "status": "ok"},
        "asyncio_tasks": {"count": 25, "status": "ok"}
    }
}
```

### 3. Cleanup Temp Files

**Function**: `cleanup_temp_files(temp_dir, max_age_hours)`

Removes temporary files older than the specified age.

**Configuration**:
```python
{
    "name": "cleanup_temp_files",
    "interval": timedelta(hours=6),
    "func": cleanup_temp_files,
    "kwargs": {"max_age_hours": 24},
    "description": "Clean up temporary files older than 24 hours"
}
```

**Behavior**:
- Runs every 6 hours
- Removes files in temp directory older than 24 hours
- Recursively processes subdirectories
- Handles permission errors gracefully
- Logs number of files cleaned up

### 4. Log Statistics

**Function**: `log_statistics()`

Logs system statistics for monitoring and debugging.

**Configuration**:
```python
{
    "name": "log_statistics",
    "interval": timedelta(minutes=15),
    "func": log_statistics,
    "description": "Log system statistics for monitoring"
}
```

**Logged Information**:
- Total asyncio tasks
- Pending asyncio tasks
- Memory usage percentage
- CPU usage percentage
- Disk usage percentage

---

## Creating Custom Tasks

### Basic Task

Create a simple async function:

```python
from datetime import timedelta
from src.core.periodic_tasks import PeriodicTask

async def my_custom_task():
    """My custom periodic task."""
    # Your logic here
    print("Running custom task!")

# Create and start
task = PeriodicTask(
    name="my_custom_task",
    interval=timedelta(minutes=30),
    task_func=my_custom_task
)
task.start()
```

### Task with Arguments

Pass arguments to your task function:

```python
async def task_with_args(database_url: str, threshold: int):
    """Task that needs configuration."""
    # Use database_url and threshold
    pass

task = PeriodicTask(
    name="task_with_args",
    interval=timedelta(hours=1),
    task_func=task_with_args,
    "postgresql://localhost/db",  # positional arg
    threshold=100  # keyword arg
)
task.start()
```

### Task with Error Handling

Tasks automatically handle errors without stopping:

```python
async def resilient_task():
    """Task with built-in error handling."""
    try:
        # Risky operation
        result = await risky_operation()
        
    except SpecificError as e:
        # Handle specific errors
        logger.warning(f"Expected error: {e}")
        
    except Exception as e:
        # Unexpected errors are logged by PeriodicTask
        # but task continues running
        raise

task = PeriodicTask(
    name="resilient_task",
    interval=timedelta(minutes=10),
    task_func=resilient_task
)
task.start()
```

### Registering with Application Lifecycle

Add custom tasks to application startup:

```python
# In src/main.py

from src.core.periodic_tasks import periodic_task_manager
from src.core.maintenance import MAINTENANCE_TASKS

# Add your custom task to MAINTENANCE_TASKS
CUSTOM_TASKS = [
    {
        "name": "my_custom_task",
        "interval": timedelta(hours=2),
        "func": my_custom_task,
        "kwargs": {"param": "value"},
        "description": "My custom maintenance task"
    }
]

# In lifespan() function:
for task_config in MAINTENANCE_TASKS + CUSTOM_TASKS:
    periodic_task_manager.register_task(
        name=task_config["name"],
        interval=task_config["interval"],
        task_func=task_config["func"],
        **task_config.get("kwargs", {})
    )

periodic_task_manager.start_all()
```

---

## Task Management

### Starting and Stopping Tasks

```python
# Start a task
task.start()

# Check if running
if task.is_running:
    print("Task is active")

# Stop gracefully (waits up to 5 seconds)
await task.stop()

# Stop with custom timeout
await task.stop(timeout=10.0)
```

### Getting Task Statistics

```python
# Get statistics for a single task
stats = task.statistics
print(f"Name: {stats['name']}")
print(f"Interval: {stats['interval']}")
print(f"Running: {stats['is_running']}")
print(f"Run count: {stats['run_count']}")
print(f"Error count: {stats['error_count']}")
print(f"Last run: {stats['last_run']}")

# Get statistics for all tasks in manager
all_stats = manager.get_all_statistics()
for stats in all_stats:
    print(f"{stats['name']}: {stats['run_count']} runs, {stats['error_count']} errors")
```

### Managing Multiple Tasks

```python
manager = PeriodicTaskManager()

# Register tasks
manager.register_task("task1", timedelta(minutes=5), task1_func)
manager.register_task("task2", timedelta(minutes=10), task2_func)
manager.register_task("task3", timedelta(hours=1), task3_func)

# Start all
manager.start_all()

# Get individual task
task1 = manager.get_task("task1")

# Stop all
await manager.stop_all()
```

---

## Best Practices

### 1. Choose Appropriate Intervals

**Guidelines**:
- **Fast tasks (< 1 second)**: Can run every 1-5 minutes
- **Medium tasks (1-10 seconds)**: Run every 10-30 minutes
- **Slow tasks (> 10 seconds)**: Run every 1-6 hours
- **Heavy tasks (> 1 minute)**: Run every 6-24 hours

**Examples**:
```python
# Quick health check - every 5 minutes
PeriodicTask("health", timedelta(minutes=5), check_health)

# Medium cleanup - every 30 minutes
PeriodicTask("cleanup", timedelta(minutes=30), cleanup_temp)

# Heavy maintenance - every 6 hours
PeriodicTask("maintenance", timedelta(hours=6), deep_maintenance)
```

### 2. Handle Errors Gracefully

Errors in periodic tasks are caught automatically, but you should still handle expected errors:

```python
async def robust_task():
    """Task with proper error handling."""
    try:
        # Risky operation
        await risky_operation()
        
    except ExpectedError as e:
        # Log and handle gracefully
        logger.warning(f"Expected error: {e}")
        # Don't raise - task will continue
        
    except Exception as e:
        # Log unexpected errors
        logger.exception("Unexpected error in task")
        # PeriodicTask will catch this and continue
        raise
```

### 3. Avoid Blocking Operations

Use async operations to avoid blocking the event loop:

```python
# ❌ BAD - blocks event loop
async def blocking_task():
    result = subprocess.run(['command'])  # Blocks!
    time.sleep(60)  # Blocks!

# ✅ GOOD - uses async operations
async def async_task():
    from src.core.subprocess_wrapper import SubprocessWrapper
    
    wrapper = SubprocessWrapper()
    try:
        process, stdout, stderr = await wrapper.create_subprocess('command')
        await process.wait()
    finally:
        wrapper.cleanup()
    
    await asyncio.sleep(60)  # Yields control
```

### 4. Monitor Task Performance

Track execution time and errors:

```python
from datetime import datetime

async def monitored_task():
    """Task that monitors its own performance."""
    start = datetime.now()
    
    try:
        # Task logic here
        await do_work()
        
        duration = (datetime.now() - start).total_seconds()
        logger.info(f"Task completed in {duration:.2f}s")
        
    except Exception as e:
        duration = (datetime.now() - start).total_seconds()
        logger.error(f"Task failed after {duration:.2f}s: {e}")
        raise
```

### 5. Use Appropriate Logging Levels

```python
async def well_logged_task():
    """Task with appropriate logging."""
    # DEBUG for routine execution
    logger.debug("Starting routine task")
    
    # INFO for important events
    logger.info("Processing 100 items")
    
    # WARNING for concerning but non-critical issues
    if items_failed > 0:
        logger.warning(f"{items_failed} items failed")
    
    # ERROR for failures
    if critical_error:
        logger.error("Critical error occurred", exc_info=True)
```

### 6. Clean Up Resources

Always clean up resources, even in periodic tasks:

```python
async def cleanup_task():
    """Task that properly cleans up resources."""
    connection = None
    try:
        connection = await open_database()
        await connection.cleanup_old_data()
        
    finally:
        if connection:
            await connection.close()
```

---

## Troubleshooting

### Task Not Starting

**Problem**: Task doesn't seem to be running

**Solutions**:
```python
# Check if task is registered
task = manager.get_task("my_task")
if task is None:
    print("Task not registered!")

# Check if task is running
if not task.is_running:
    print("Task is not running")
    task.start()

# Check for registration errors in logs
# Look for "Failed to register task" messages
```

### Task Stopping Unexpectedly

**Problem**: Periodic task stops running

**Causes**:
1. Uncaught exception in task function
2. Application shutdown
3. Task was explicitly stopped

**Solutions**:
```python
# Check task statistics
stats = task.statistics
print(f"Error count: {stats['error_count']}")
print(f"Last run: {stats['last_run']}")

# Check logs for exceptions
# Look for "Error in periodic task" messages

# Restart task if needed
if not task.is_running:
    task.start()
```

### High Resource Usage

**Problem**: Periodic tasks using too much CPU/memory

**Solutions**:
1. **Increase interval** - tasks running too frequently
2. **Optimize task logic** - reduce work per execution
3. **Add rate limiting** - throttle expensive operations

```python
# Increase interval
task = PeriodicTask(
    name="heavy_task",
    interval=timedelta(hours=6),  # Was every hour
    task_func=heavy_task
)

# Add throttling in task
async def throttled_task():
    for item in items:
        await process_item(item)
        await asyncio.sleep(0.1)  # Throttle processing
```

### Task Taking Too Long

**Problem**: Task execution time exceeds interval

**Solution**: Increase interval or optimize task

```python
# Monitor execution time
async def timed_task():
    start = datetime.now()
    
    try:
        await do_work()
    finally:
        duration = (datetime.now() - start).total_seconds()
        logger.info(f"Task took {duration:.2f}s")
        
        # Warn if taking too long
        if duration > 50:  # For 60-second interval
            logger.warning(
                f"Task taking {duration:.2f}s - "
                f"consider increasing interval or optimizing"
            )
```

---

## See Also

- [Background Tasks Best Practices](BACKGROUND_TASKS_BEST_PRACTICES.md)
- [API Reference](../API_REFERENCE.md)
- [Logging Best Practices](/_meta/docs/LOGGING_BEST_PRACTICES.md)
- [System Architecture](/_meta/docs/ARCHITECTURE.md)

---

**Last Updated**: 2025-11-05  
**Maintainer**: PrismQ Team  
**Feedback**: Create an issue in `_meta/issues/new/`
