# Background Tasks Best Practices

**Platform**: Windows (primary), Linux/macOS (supported)  
**Context**: Lessons learned from historical async subprocess issues  
**Last Updated**: 2025-11-04

## Executive Summary

This guide documents best practices for implementing background tasks in the PrismQ Client Backend, addressing historical issues with asyncio subprocess operations on Windows and providing patterns for reliable, cross-platform background task execution.

**Key Takeaways**:
- ✅ Always use `SubprocessWrapper` for subprocess operations
- ✅ Set Windows event loop policy **before** creating any event loops
- ✅ Prefer THREADED mode on Windows for maximum reliability
- ✅ Use proper async context managers for cleanup
- ✅ Handle exceptions at all async boundaries
- ✅ Monitor and limit concurrent background tasks

## Table of Contents

1. [Historical Context](#historical-context)
2. [Core Principles](#core-principles)
3. [Subprocess Execution Patterns](#subprocess-execution-patterns)
4. [Background Task Patterns](#background-task-patterns)
5. [Error Handling](#error-handling)
6. [Resource Management](#resource-management)
7. [Testing Background Tasks](#testing-background-tasks)
8. [Common Anti-Patterns](#common-anti-patterns)
9. [Troubleshooting](#troubleshooting)

---

## Historical Context

### The Windows Subprocess Problem

**Issue**: Prior to implementing `SubprocessWrapper`, the backend experienced `NotImplementedError` when running modules on Windows.

**Root Cause**: Python's asyncio uses `SelectorEventLoop` by default on Windows, which doesn't support asynchronous subprocess operations. The `ProactorEventLoop` is required.

**Timeline**:
1. **Initial Problem**: Users reported module execution failures on Windows
2. **PR #131**: Fixed by implementing `WindowsProactorEventLoopPolicy` in `uvicorn_runner.py`
3. **Enhancement**: Created `SubprocessWrapper` with auto-detection and fallback modes
4. **Current State**: Robust, cross-platform subprocess execution with multiple execution modes

### Lessons Learned

1. **Event Loop Policy Timing Matters**: The event loop policy must be set **before** any event loop is created
2. **Auto-Detection is Unreliable**: Different startup methods (direct uvicorn, reload mode, etc.) can affect event loop creation
3. **Fallback Strategies are Essential**: THREADED mode provides a reliable fallback
4. **Platform-Specific Testing is Critical**: What works on Linux may fail on Windows
5. **Documentation is Key**: Users need clear guidance on proper startup procedures

---

## Core Principles

### 1. Isolation Principle

**Background tasks should be isolated from the main application lifecycle.**

✅ **Good**: Background tasks use separate subprocess/thread pool
```python
from src.core.subprocess_wrapper import SubprocessWrapper

wrapper = SubprocessWrapper()  # Auto-detects best mode
process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
```

❌ **Bad**: Background tasks block the main event loop
```python
# Don't do this - blocks event loop
result = subprocess.run(['python', 'script.py'])
```

### 2. Explicit Resource Management

**Always clean up resources, even when tasks fail.**

✅ **Good**: Use context managers and cleanup methods
```python
wrapper = SubprocessWrapper(mode=RunMode.THREADED)
try:
    process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
    # ... use process ...
finally:
    wrapper.cleanup()  # Always cleanup
```

❌ **Bad**: Leak thread pools or file handles
```python
wrapper = SubprocessWrapper(mode=RunMode.THREADED)
process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
# Missing cleanup - thread pool not shut down
```

### 3. Defensive Programming

**Expect failures and handle them gracefully.**

✅ **Good**: Handle all exception types
```python
try:
    await execute_module(module_id, params)
except SubprocessPolicyException as e:
    logger.error(f"Event loop policy error: {e}")
    # Provide actionable error message
except ModuleExecutionException as e:
    logger.error(f"Module execution failed: {e}")
except Exception as e:
    logger.exception("Unexpected error in background task")
    # Still log and handle unknown errors
```

### 4. Platform Awareness

**Write code that works reliably across Windows, Linux, and macOS.**

✅ **Good**: Use platform-aware abstractions
```python
from src.core.subprocess_wrapper import SubprocessWrapper

# SubprocessWrapper handles platform differences
wrapper = SubprocessWrapper()  # Auto-detects best mode for platform
```

❌ **Bad**: Assume Unix-only behavior
```python
# Fails on Windows without ProactorEventLoop
process = await asyncio.create_subprocess_exec('python', 'script.py')
```

### 5. Observability

**Make background tasks observable through logging and monitoring.**

✅ **Good**: Log important events with context
```python
logger.info(f"Starting background task for module {module_id}")
logger.debug(f"Using subprocess mode: {wrapper.mode}")
# ... execute task ...
logger.info(f"Background task completed in {duration:.2f}s")
```

---

## Subprocess Execution Patterns

> **Note**: All code examples below include the necessary imports. The examples use actual classes from the PrismQ Client Backend codebase:
> - `src.core.subprocess_wrapper` - Cross-platform subprocess wrapper
> - `src.core.output_capture` - Output capture and streaming service  
> - `src.core.resource_manager` - System resource monitoring
> - `src.core.run_registry` - Run state management
> - `src.models.run` - Run data models
> 
> Each example also shows logger setup. Use your module's logger via `logging.getLogger(__name__)`.

### Pattern 1: Simple Module Execution

**Use Case**: Run a PrismQ module as a subprocess

```python
import asyncio
import logging
from pathlib import Path
from typing import List, Tuple
from src.core.subprocess_wrapper import SubprocessWrapper, RunMode

# Logger setup (use your module's logger)
logger = logging.getLogger(__name__)

async def execute_module(
    script_path: Path,
    args: List[str],
    cwd: Path
) -> Tuple[int, str, str]:
    """Execute a module script and capture output.
    
    Args:
        script_path: Path to the Python script
        args: Command-line arguments
        cwd: Working directory
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    wrapper = SubprocessWrapper()  # Auto-detect mode
    
    try:
        # Build command
        cmd = ['python', str(script_path)] + args
        
        # Create subprocess
        process, stdout, stderr = await wrapper.create_subprocess(
            *cmd,
            cwd=cwd
        )
        
        logger.info(f"Started process PID={process.pid} for {script_path.name}")
        
        # Collect output
        stdout_data = []
        stderr_data = []
        
        # Read output line by line
        async def read_stream(stream, buffer):
            while True:
                line = await stream.readline()
                if not line:
                    break
                buffer.append(line)
                logger.debug(f"Output: {line.decode().strip()}")
        
        # Read both streams concurrently
        await asyncio.gather(
            read_stream(stdout, stdout_data),
            read_stream(stderr, stderr_data)
        )
        
        # Wait for process completion
        exit_code = await process.wait()
        
        logger.info(f"Process completed with exit code {exit_code}")
        
        return (
            exit_code,
            b''.join(stdout_data).decode(),
            b''.join(stderr_data).decode()
        )
        
    finally:
        wrapper.cleanup()
```

### Pattern 2: Long-Running Background Task

**Use Case**: Execute a task that runs for an extended period with progress updates

```python
import asyncio
import logging
from pathlib import Path
from src.core.subprocess_wrapper import SubprocessWrapper
from src.core.output_capture import OutputCapture

logger = logging.getLogger(__name__)

async def execute_long_running_task(
    run_id: str,
    script_path: Path,
    output_capture: OutputCapture
) -> None:
    """Execute a long-running task with real-time output capture.
    
    Args:
        run_id: Unique identifier for this run
        script_path: Path to the script to execute
        output_capture: Service for capturing and streaming output
    """
    wrapper = SubprocessWrapper()
    
    try:
        process, stdout, stderr = await wrapper.create_subprocess(
            'python', str(script_path),
            cwd=script_path.parent
        )
        
        logger.info(f"Started long-running task {run_id}, PID={process.pid}")
        
        async def stream_output():
            """Stream output to output capture service."""
            while True:
                line = await stdout.readline()
                if not line:
                    break
                    
                # Send to output capture service for SSE streaming
                await output_capture.append_line(run_id, line.decode())
        
        # Start output streaming as background task
        stream_task = asyncio.create_task(stream_output())
        
        # Wait for process or cancellation
        try:
            exit_code = await process.wait()
            logger.info(f"Task {run_id} completed with exit code {exit_code}")
        except asyncio.CancelledError:
            logger.warning(f"Task {run_id} cancelled, terminating process")
            await process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
            raise
        finally:
            # Ensure streaming task is cleaned up
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass
                
    finally:
        wrapper.cleanup()
```

### Pattern 3: Concurrent Module Execution

**Use Case**: Run multiple modules concurrently with resource limits

```python
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from src.core.subprocess_wrapper import SubprocessWrapper
from src.core.resource_manager import ResourceManager

logger = logging.getLogger(__name__)

class ConcurrentExecutor:
    """Execute multiple modules concurrently with resource limits."""
    
    def __init__(
        self,
        max_concurrent: int = 10,
        resource_manager: ResourceManager = None
    ):
        self.max_concurrent = max_concurrent
        self.resource_manager = resource_manager
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.wrapper = SubprocessWrapper()
    
    async def execute_module(
        self,
        module_id: str,
        script_path: Path,
        args: List[str]
    ) -> Dict:
        """Execute a single module with resource management.
        
        Args:
            module_id: Module identifier
            script_path: Path to module script
            args: Command-line arguments
            
        Returns:
            Execution result dictionary
        """
        async with self.semaphore:  # Limit concurrency
            # Check resources before starting
            if self.resource_manager:
                if not await self.resource_manager.check_resources():
                    raise ResourceLimitException("Insufficient system resources")
            
            logger.info(f"Executing module {module_id}")
            
            try:
                process, stdout, stderr = await self.wrapper.create_subprocess(
                    'python', str(script_path), *args,
                    cwd=script_path.parent
                )
                
                exit_code = await process.wait()
                
                return {
                    'module_id': module_id,
                    'exit_code': exit_code,
                    'success': exit_code == 0
                }
                
            except Exception as e:
                logger.error(f"Module {module_id} failed: {e}", exc_info=True)
                return {
                    'module_id': module_id,
                    'exit_code': -1,
                    'success': False,
                    'error': str(e)
                }
    
    async def execute_batch(
        self,
        modules: List[Tuple[str, Path, List[str]]]
    ) -> List[Dict]:
        """Execute multiple modules concurrently.
        
        Args:
            modules: List of (module_id, script_path, args) tuples
            
        Returns:
            List of execution results
        """
        tasks = [
            self.execute_module(module_id, script_path, args)
            for module_id, script_path, args in modules
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def cleanup(self):
        """Clean up resources."""
        self.wrapper.cleanup()
```

---

## Background Task Patterns

### Pattern 4: Fire-and-Forget with Tracking

**Use Case**: Start a background task without waiting for completion, but track its status

```python
import asyncio
import logging
from src.core.run_registry import RunRegistry
from src.models.run import Run, RunStatus

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manage fire-and-forget background tasks with status tracking."""
    
    def __init__(self, registry: RunRegistry):
        self.registry = registry
        self.tasks: dict[str, asyncio.Task] = {}
    
    async def _execute_task(self, run: Run, coro):
        """Execute task and update status in registry."""
        try:
            # Update status to running
            run.status = RunStatus.RUNNING
            await self.registry.update_run(run)
            
            # Execute the actual task
            result = await coro
            
            # Update status to completed
            run.status = RunStatus.COMPLETED
            run.exit_code = 0
            await self.registry.update_run(run)
            
            logger.info(f"Task {run.run_id} completed successfully")
            
        except asyncio.CancelledError:
            run.status = RunStatus.CANCELLED
            await self.registry.update_run(run)
            logger.warning(f"Task {run.run_id} was cancelled")
            raise
            
        except Exception as e:
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            await self.registry.update_run(run)
            logger.exception(f"Task {run.run_id} failed")
            
        finally:
            # Remove from active tasks
            self.tasks.pop(run.run_id, None)
    
    def start_task(self, run: Run, coro) -> str:
        """Start a background task.
        
        Args:
            run: Run object for tracking
            coro: Coroutine to execute
            
        Returns:
            Run ID for tracking
        """
        # Create and store task
        task = asyncio.create_task(self._execute_task(run, coro))
        self.tasks[run.run_id] = task
        
        logger.info(f"Started background task {run.run_id}")
        return run.run_id
    
    async def cancel_task(self, run_id: str) -> bool:
        """Cancel a running background task.
        
        Args:
            run_id: ID of the task to cancel
            
        Returns:
            True if task was cancelled, False if not found
        """
        task = self.tasks.get(run_id)
        if not task:
            logger.warning(f"Task {run_id} not found")
            return False
        
        if task.done():
            logger.info(f"Task {run_id} already completed")
            return False
        
        logger.info(f"Cancelling task {run_id}")
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        return True
    
    async def wait_all(self):
        """Wait for all background tasks to complete."""
        if not self.tasks:
            return
        
        logger.info(f"Waiting for {len(self.tasks)} background tasks")
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)
```

### Pattern 5: Periodic Background Tasks

**Use Case**: Run a task periodically (e.g., cleanup, health checks)

```python
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PeriodicTask:
    """Execute a task periodically in the background."""
    
    def __init__(
        self,
        name: str,
        interval: timedelta,
        task_func,
        *args,
        **kwargs
    ):
        self.name = name
        self.interval = interval
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self._task: asyncio.Task = None
        self._stop_event = asyncio.Event()
    
    async def _run_periodic(self):
        """Run the task periodically until stopped."""
        logger.info(f"Starting periodic task '{self.name}' (interval={self.interval})")
        
        while not self._stop_event.is_set():
            try:
                # Execute the task
                logger.debug(f"Executing periodic task '{self.name}'")
                await self.task_func(*self.args, **self.kwargs)
                
            except Exception as e:
                logger.error(
                    f"Error in periodic task '{self.name}': {e}",
                    exc_info=True
                )
            
            # Wait for next interval or stop signal
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.interval.total_seconds()
                )
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue to next iteration
        
        logger.info(f"Stopped periodic task '{self.name}'")
    
    def start(self):
        """Start the periodic task."""
        if self._task and not self._task.done():
            logger.warning(f"Periodic task '{self.name}' already running")
            return
        
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_periodic())
    
    async def stop(self):
        """Stop the periodic task."""
        if not self._task or self._task.done():
            logger.warning(f"Periodic task '{self.name}' not running")
            return
        
        logger.info(f"Stopping periodic task '{self.name}'")
        self._stop_event.set()
        
        try:
            await asyncio.wait_for(self._task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning(f"Periodic task '{self.name}' did not stop gracefully")
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


# Example usage
async def cleanup_old_runs():
    """Example periodic cleanup task."""
    logger.info("Running cleanup of old runs")
    # Cleanup logic here
    pass

# Start periodic cleanup
cleanup_task = PeriodicTask(
    name="cleanup_old_runs",
    interval=timedelta(hours=1),
    task_func=cleanup_old_runs
)
cleanup_task.start()
```

---

## Error Handling

### Exception Hierarchy

Always catch and handle exceptions at appropriate levels:

```python
from src.core.exceptions import (
    SubprocessPolicyException,
    ModuleExecutionException,
    ResourceLimitException,
)

async def execute_with_error_handling(module_id: str, params: dict):
    """Execute module with comprehensive error handling."""
    try:
        # Attempt execution
        result = await execute_module(module_id, params)
        return result
        
    except SubprocessPolicyException as e:
        # Event loop policy issue - provide actionable guidance
        logger.error(
            f"Event loop policy error for {module_id}: {e}. "
            f"Restart server with: python -m src.uvicorn_runner"
        )
        raise
        
    except ResourceLimitException as e:
        # Resource constraints - may be temporary
        logger.warning(f"Resource limit for {module_id}: {e}")
        raise
        
    except ModuleExecutionException as e:
        # Module-specific error
        logger.error(f"Module {module_id} execution failed: {e}")
        raise
        
    except asyncio.CancelledError:
        # Task was cancelled - cleanup and re-raise
        logger.info(f"Module {module_id} execution cancelled")
        raise
        
    except Exception as e:
        # Unexpected error - log with full traceback
        logger.exception(f"Unexpected error executing {module_id}")
        raise ModuleExecutionException(f"Unexpected error: {e}") from e
```

### Timeout Handling

Always set reasonable timeouts for background tasks:

```python
import asyncio

async def execute_with_timeout(
    coro,
    timeout: float,
    task_name: str = "task"
) -> any:
    """Execute a coroutine with timeout.
    
    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds
        task_name: Name for logging
        
    Returns:
        Result of the coroutine
        
    Raises:
        asyncio.TimeoutError: If task exceeds timeout
    """
    try:
        result = await asyncio.wait_for(coro, timeout=timeout)
        logger.info(f"{task_name} completed within {timeout}s")
        return result
        
    except asyncio.TimeoutError:
        logger.error(f"{task_name} exceeded timeout of {timeout}s")
        raise
    
    except Exception as e:
        logger.error(f"{task_name} failed: {e}", exc_info=True)
        raise
```

---

## Resource Management

### Pattern 6: Resource Pooling

**Use Case**: Reuse expensive resources (thread pools, connections)

```python
from src.core.subprocess_wrapper import SubprocessWrapper, RunMode
from contextlib import asynccontextmanager

class ResourcePool:
    """Pool of reusable resources for background tasks."""
    
    def __init__(self, max_workers: int = 10):
        self.wrapper = SubprocessWrapper(
            mode=RunMode.THREADED,
            max_workers=max_workers
        )
        self._initialized = True
    
    @asynccontextmanager
    async def acquire_subprocess(self):
        """Acquire a subprocess slot from the pool."""
        # The ThreadPoolExecutor in SubprocessWrapper handles pooling
        try:
            yield self.wrapper
        finally:
            pass  # Cleanup handled by context manager
    
    def cleanup(self):
        """Clean up all pooled resources."""
        if self._initialized:
            self.wrapper.cleanup()
            self._initialized = False


# Usage
pool = ResourcePool(max_workers=10)

async def use_pooled_resource():
    async with pool.acquire_subprocess() as wrapper:
        process, stdout, stderr = await wrapper.create_subprocess(
            'python', 'script.py'
        )
        await process.wait()

# Cleanup on shutdown
pool.cleanup()
```

### Memory Management

Monitor and limit memory usage:

```python
import psutil
import asyncio

class MemoryMonitor:
    """Monitor memory usage and prevent resource exhaustion."""
    
    def __init__(
        self,
        max_memory_percent: float = 80.0,
        check_interval: float = 5.0
    ):
        self.max_memory_percent = max_memory_percent
        self.check_interval = check_interval
        self._monitoring = False
    
    def check_memory(self) -> bool:
        """Check if memory usage is within limits.
        
        Returns:
            True if memory is OK, False if limit exceeded
        """
        memory = psutil.virtual_memory()
        current_percent = memory.percent
        
        if current_percent > self.max_memory_percent:
            logger.warning(
                f"Memory usage at {current_percent:.1f}% "
                f"(limit: {self.max_memory_percent:.1f}%)"
            )
            return False
        
        logger.debug(f"Memory usage: {current_percent:.1f}%")
        return True
    
    async def monitor_continuously(self):
        """Continuously monitor memory usage."""
        self._monitoring = True
        
        while self._monitoring:
            if not self.check_memory():
                logger.error("Memory limit exceeded!")
                # Could trigger cleanup, reject new tasks, etc.
            
            await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self._monitoring = False
```

---

## Testing Background Tasks

### Unit Testing Async Functions

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_execute_module_success():
    """Test successful module execution."""
    from src.core.subprocess_wrapper import SubprocessWrapper
    
    wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)  # Use DRY_RUN for testing
    
    try:
        process, stdout, stderr = await wrapper.create_subprocess(
            'python', '--version'
        )
        
        exit_code = await process.wait()
        assert exit_code == 0
        
    finally:
        wrapper.cleanup()


@pytest.mark.asyncio
async def test_execute_module_timeout():
    """Test module execution timeout handling."""
    from src.core.subprocess_wrapper import SubprocessWrapper
    
    wrapper = SubprocessWrapper(mode=RunMode.LOCAL)
    
    try:
        process, stdout, stderr = await wrapper.create_subprocess(
            'python', '-c', 'import time; time.sleep(10)'
        )
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(process.wait(), timeout=1.0)
            
    finally:
        wrapper.cleanup()


@pytest.mark.asyncio
async def test_concurrent_execution():
    """Test concurrent module execution."""
    from src.core.subprocess_wrapper import SubprocessWrapper
    
    wrapper = SubprocessWrapper()
    
    try:
        # Start multiple processes
        processes = []
        for i in range(3):
            process, stdout, stderr = await wrapper.create_subprocess(
                'python', '-c', f'print("{i}")'
            )
            processes.append(process)
        
        # Wait for all
        exit_codes = await asyncio.gather(
            *[p.wait() for p in processes]
        )
        
        assert all(code == 0 for code in exit_codes)
        
    finally:
        wrapper.cleanup()
```

### Integration Testing

```python
import pytest
from pathlib import Path

@pytest.mark.asyncio
async def test_full_module_execution_flow():
    """Test complete module execution flow."""
    from src.core.module_runner import ModuleRunner
    from src.core.run_registry import RunRegistry
    from src.core.process_manager import ProcessManager
    
    # Setup
    registry = RunRegistry()
    process_manager = ProcessManager()
    runner = ModuleRunner(
        registry=registry,
        process_manager=process_manager
    )
    
    # Execute module
    module_id = "test-module"
    script_path = Path("test_script.py")
    params = {"test": "value"}
    
    run = await runner.execute_module(
        module_id=module_id,
        module_name="Test Module",
        script_path=script_path,
        parameters=params
    )
    
    # Verify
    assert run is not None
    assert run.status == RunStatus.COMPLETED
    assert run.exit_code == 0
```

---

## Common Anti-Patterns

### ❌ Anti-Pattern 1: Direct asyncio.create_subprocess_exec on Windows

**Problem**: Fails without ProactorEventLoop

```python
# DON'T DO THIS
process = await asyncio.create_subprocess_exec(
    'python', 'script.py',
    stdout=asyncio.subprocess.PIPE
)
```

**Solution**: Use SubprocessWrapper

```python
# DO THIS
from src.core.subprocess_wrapper import SubprocessWrapper

wrapper = SubprocessWrapper()
process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
```

### ❌ Anti-Pattern 2: Blocking Calls in Async Functions

**Problem**: Blocks the event loop

```python
# DON'T DO THIS
async def bad_async_function():
    result = subprocess.run(['python', 'script.py'])  # Blocks!
    return result
```

**Solution**: Use async subprocess wrapper

```python
# DO THIS
async def good_async_function():
    wrapper = SubprocessWrapper()
    try:
        process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
        exit_code = await process.wait()
        return exit_code
    finally:
        wrapper.cleanup()
```

### ❌ Anti-Pattern 3: Missing Cleanup

**Problem**: Resource leaks

```python
# DON'T DO THIS
async def leaky_function():
    wrapper = SubprocessWrapper(mode=RunMode.THREADED)
    process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
    # Missing wrapper.cleanup() - thread pool not shut down
```

**Solution**: Always cleanup

```python
# DO THIS
async def proper_function():
    wrapper = SubprocessWrapper(mode=RunMode.THREADED)
    try:
        process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
        await process.wait()
    finally:
        wrapper.cleanup()
```

### ❌ Anti-Pattern 4: Swallowing Exceptions

**Problem**: Errors go unnoticed

```python
# DON'T DO THIS
async def silent_failure():
    try:
        await risky_operation()
    except Exception:
        pass  # Error lost!
```

**Solution**: Log and re-raise or handle appropriately

```python
# DO THIS
async def proper_error_handling():
    try:
        await risky_operation()
    except Exception as e:
        logger.exception("Operation failed")
        raise  # Re-raise for caller to handle
```

### ❌ Anti-Pattern 5: Unbounded Concurrency

**Problem**: Resource exhaustion

```python
# DON'T DO THIS
tasks = [execute_module(m) for m in modules]  # Could be thousands!
results = await asyncio.gather(*tasks)
```

**Solution**: Use semaphore to limit concurrency

```python
# DO THIS
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

async def execute_with_limit(module):
    async with semaphore:
        return await execute_module(module)

tasks = [execute_with_limit(m) for m in modules]
results = await asyncio.gather(*tasks)
```

---

## Troubleshooting

### Issue: NotImplementedError on Windows

**Symptom**:
```
NotImplementedError: Subprocess operations not supported
```

**Cause**: Windows SelectorEventLoop doesn't support async subprocess

**Solutions**:
1. **Use uvicorn_runner** (Recommended):
   ```powershell
   python -m src.uvicorn_runner
   ```

2. **Set environment variable**:
   ```powershell
   $env:PRISMQ_RUN_MODE = "threaded"
   python -m src.main
   ```

3. **Explicitly use THREADED mode in code**:
   ```python
   wrapper = SubprocessWrapper(mode=RunMode.THREADED)
   ```

### Issue: Event Loop Already Running

**Symptom**:
```
RuntimeError: This event loop is already running
```

**Cause**: Attempting to run async code from sync context with existing loop

**Solution**: Use `asyncio.create_task` or `loop.create_task` instead of `asyncio.run`

```python
# In async context
task = asyncio.create_task(my_async_function())

# Don't use asyncio.run() when a loop is already running
```

### Issue: Process Doesn't Terminate

**Symptom**: Background process keeps running after cancellation

**Solution**: Properly handle termination

```python
async def terminate_gracefully(process):
    """Terminate process with timeout."""
    process.terminate()
    try:
        await asyncio.wait_for(process.wait(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Process didn't terminate, killing it")
        process.kill()
        await process.wait()
```

### Issue: Memory Leak in Background Tasks

**Symptom**: Memory usage grows over time

**Solutions**:
1. **Ensure cleanup is always called**:
   ```python
   finally:
       wrapper.cleanup()
   ```

2. **Monitor for orphaned tasks**:
   ```python
   # Periodically check for lingering tasks
   tasks = asyncio.all_tasks()
   logger.info(f"Active tasks: {len(tasks)}")
   ```

3. **Use weak references for callbacks**:
   ```python
   import weakref
   
   callback_ref = weakref.ref(callback_func)
   ```

### Issue: High CPU Usage

**Symptom**: Server uses 100% CPU

**Cause**: Tight loop without awaiting

**Solution**: Always await or sleep in loops

```python
# BAD - tight loop
while True:
    if check_condition():
        break

# GOOD - sleep between checks
while True:
    if check_condition():
        break
    await asyncio.sleep(0.1)  # Yield control
```

---

## Quick Reference

### Checklist for New Background Tasks

- [ ] Use `SubprocessWrapper` for subprocess operations
- [ ] Handle platform differences (Windows vs Unix)
- [ ] Set appropriate timeouts
- [ ] Implement proper error handling
- [ ] Add logging at key points
- [ ] Clean up resources in finally blocks
- [ ] Limit concurrency with semaphores
- [ ] Test on both Windows and Linux
- [ ] Document special requirements
- [ ] Add integration tests

### Environment Variables

| Variable | Values | Default | Purpose |
|----------|--------|---------|---------|
| `PRISMQ_RUN_MODE` | `async`, `threaded`, `local`, `dry-run` | Auto-detect | Force subprocess execution mode |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | Control logging verbosity |

### See Also

- [Task Management Guide](TASK_MANAGEMENT.md) - **NEW** Fire-and-forget task execution (Pattern 4 implementation)
- [Subprocess Execution Modes](RUN_MODES.md)
- [Windows Testing Guide](WINDOWS_TESTING.md)
- [API Reference](../API_REFERENCE.md)
- [Logging Best Practices](/_meta/docs/LOGGING_BEST_PRACTICES.md)

---

**Last Updated**: 2025-11-04  
**Maintainer**: PrismQ Team  
**Feedback**: Create an issue in `_meta/issues/new/`
