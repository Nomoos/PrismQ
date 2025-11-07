# Execution Patterns Usage Guide

This document provides examples and guidance for using the execution patterns module, which implements Pattern 1 from the Background Tasks Best Practices guide.

## Overview

The `execution_patterns` module provides a simplified, best-practices-compliant interface for executing PrismQ modules as subprocesses with proper error handling, resource cleanup, and output capture.

## Pattern 1: Simple Module Execution

### Basic Usage

```python
import asyncio
from pathlib import Path
from src.core.execution_patterns import execute_module

async def run_module():
    """Execute a PrismQ module."""
    
    # Define module details
    script_path = Path("/path/to/module/main.py")
    args = ["--param1", "value1", "--param2", "value2"]
    cwd = script_path.parent
    
    # Execute the module
    exit_code, stdout, stderr = await execute_module(
        script_path=script_path,
        args=args,
        cwd=cwd
    )
    
    # Handle results
    if exit_code == 0:
        print("Module executed successfully!")
        print(f"Output: {stdout}")
    else:
        print(f"Module failed with exit code {exit_code}")
        print(f"Error: {stderr}")

# Run the async function
asyncio.run(run_module())
```

### With Explicit Run Mode

```python
from src.core.execution_patterns import execute_module
from src.core.subprocess_wrapper import RunMode

async def run_with_threaded_mode():
    """Execute module with explicit THREADED mode (Windows safe)."""
    
    exit_code, stdout, stderr = await execute_module(
        script_path=Path("/path/to/script.py"),
        args=["--param", "value"],
        cwd=Path("/path/to"),
        mode=RunMode.THREADED  # Explicitly use THREADED mode
    )
    
    return exit_code, stdout, stderr
```

### Error Handling

```python
from pathlib import Path
from src.core.execution_patterns import execute_module

async def run_with_error_handling():
    """Execute module with comprehensive error handling."""
    
    script_path = Path("/path/to/module.py")
    
    try:
        exit_code, stdout, stderr = await execute_module(
            script_path=script_path,
            args=["--mode", "process"],
            cwd=script_path.parent
        )
        
        if exit_code != 0:
            # Module executed but returned error
            print(f"Module failed: {stderr}")
            # Handle module-specific error
            
    except FileNotFoundError as e:
        # Script doesn't exist
        print(f"Script not found: {e}")
        
    except PermissionError as e:
        # Permission denied
        print(f"Permission denied: {e}")
        
    except RuntimeError as e:
        # Subprocess creation failed
        print(f"Execution failed: {e}")
        
    except asyncio.CancelledError:
        # Task was cancelled
        print("Execution cancelled")
        raise  # Re-raise to propagate cancellation
```

### Concurrent Execution

```python
import asyncio
from pathlib import Path
from src.core.execution_patterns import execute_module

async def run_multiple_modules():
    """Execute multiple modules concurrently."""
    
    modules = [
        (Path("/path/to/module1.py"), ["--arg1", "val1"]),
        (Path("/path/to/module2.py"), ["--arg2", "val2"]),
        (Path("/path/to/module3.py"), ["--arg3", "val3"]),
    ]
    
    # Create tasks for all modules
    tasks = [
        execute_module(
            script_path=script,
            args=args,
            cwd=script.parent
        )
        for script, args in modules
    ]
    
    # Execute all concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Module {i} failed with exception: {result}")
        else:
            exit_code, stdout, stderr = result
            print(f"Module {i} completed with exit code {exit_code}")
```

### With Timeout

```python
import asyncio
from pathlib import Path
from src.core.execution_patterns import execute_module

async def run_with_timeout():
    """Execute module with timeout."""
    
    try:
        exit_code, stdout, stderr = await asyncio.wait_for(
            execute_module(
                script_path=Path("/path/to/module.py"),
                args=[],
                cwd=Path("/path/to")
            ),
            timeout=300.0  # 5 minutes
        )
        
        return exit_code, stdout, stderr
        
    except asyncio.TimeoutError:
        print("Module execution timed out after 5 minutes")
        raise
```

### Cancellation Support

```python
import asyncio
from pathlib import Path
from src.core.execution_patterns import execute_module

async def run_with_cancellation():
    """Execute module with cancellation support."""
    
    # Create the execution task
    task = asyncio.create_task(
        execute_module(
            script_path=Path("/path/to/long_running_module.py"),
            args=[],
            cwd=Path("/path/to")
        )
    )
    
    # Simulate doing other work
    await asyncio.sleep(5)
    
    # Cancel if needed
    if should_cancel():
        print("Cancelling execution...")
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            print("Execution cancelled successfully")
    else:
        # Wait for completion
        exit_code, stdout, stderr = await task
        print(f"Completed with exit code {exit_code}")
```

## Integration with ModuleRunner

The `execute_module` pattern can be used alongside the existing `ModuleRunner` class for scenarios where you need a simpler, more direct execution interface:

```python
from src.core.execution_patterns import execute_module
from src.core import get_module_runner

# For simple, one-off executions - use execute_module
exit_code, stdout, stderr = await execute_module(
    script_path=Path("script.py"),
    args=["--quick"],
    cwd=Path(".")
)

# For full lifecycle management with tracking - use ModuleRunner
runner = get_module_runner()
run = await runner.execute_module(
    module_id="my-module",
    module_name="My Module",
    script_path=Path("script.py"),
    parameters={"param": "value"}
)
```

## Run Modes

The pattern supports all SubprocessWrapper run modes:

- **AUTO (default)**: Automatically detects best mode for the platform
  - Windows: THREADED mode
  - Linux/macOS: ASYNC mode
  
- **THREADED**: Uses thread pool for subprocess execution (Windows safe)
  ```python
  execute_module(script, args, cwd, mode=RunMode.THREADED)
  ```
  
- **ASYNC**: Uses asyncio subprocess (requires ProactorEventLoop on Windows)
  ```python
  execute_module(script, args, cwd, mode=RunMode.ASYNC)
  ```
  
- **DRY_RUN**: Logs command without execution (for testing)
  ```python
  execute_module(script, args, cwd, mode=RunMode.DRY_RUN)
  ```
  
- **LOCAL**: Synchronous execution in thread pool (for debugging)
  ```python
  execute_module(script, args, cwd, mode=RunMode.LOCAL)
  ```

## Best Practices

### 1. Always Use Context for Working Directory

```python
# Good - explicit working directory
await execute_module(
    script_path=Path("module/main.py"),
    args=[],
    cwd=Path("module")  # Set proper working directory
)

# Bad - no working directory set
await execute_module(
    script_path=Path("module/main.py"),
    args=[],
    cwd=Path(".")  # May not be what the module expects
)
```

### 2. Handle Exit Codes Appropriately

```python
exit_code, stdout, stderr = await execute_module(...)

if exit_code == 0:
    # Success
    process_output(stdout)
elif exit_code == 1:
    # Module-specific error
    handle_module_error(stderr)
elif exit_code < 0:
    # Terminated by signal (Unix)
    handle_termination(exit_code)
else:
    # Other error
    handle_error(exit_code, stderr)
```

### 3. Use Appropriate Logging

The pattern automatically logs at appropriate levels:
- INFO: Process start/completion
- DEBUG: Command details, output lines
- WARNING: Non-zero exit codes
- ERROR: Exceptions

Configure your logger to control verbosity:

```python
import logging

# Detailed logging for debugging
logging.getLogger('src.core.execution_patterns').setLevel(logging.DEBUG)

# Minimal logging for production
logging.getLogger('src.core.execution_patterns').setLevel(logging.INFO)
```

### 4. Resource Cleanup is Automatic

The pattern uses `try`/`finally` to ensure resources are cleaned up:

```python
# No need to manually cleanup - handled automatically
exit_code, stdout, stderr = await execute_module(...)

# Resources are cleaned up even if execution fails or is cancelled
```

### 5. Test with DRY_RUN Mode

```python
# Test your integration without actually running modules
from src.core.subprocess_wrapper import RunMode

exit_code, stdout, stderr = await execute_module(
    script_path=Path("module.py"),
    args=["--test"],
    cwd=Path("."),
    mode=RunMode.DRY_RUN  # No actual execution
)

# Verify your logic works with mock output
assert exit_code == 0
```

## Comparison with ModuleRunner

| Feature | execute_module | ModuleRunner |
|---------|---------------|--------------|
| Use Case | Simple, direct execution | Full lifecycle management |
| State Tracking | No | Yes (Run objects) |
| Output Streaming | No | Yes (SSE support) |
| Concurrent Runs | Manual via asyncio.gather | Built-in with limits |
| Resource Management | Manual | Automatic |
| Complexity | Low | Higher |
| Best For | Scripts, utilities | Production modules |

## See Also

- [Background Tasks Best Practices](../docs/BACKGROUND_TASKS_BEST_PRACTICES.md) - Full guide with all patterns
- [SubprocessWrapper Documentation](../docs/SUBPROCESS_WRAPPER.md) - Details on run modes
- [ModuleRunner API](../API_REFERENCE.md) - Full module execution API

## Support

For issues or questions:
- Create an issue in `_meta/issues/new/`
- See troubleshooting in [Background Tasks Best Practices](../docs/BACKGROUND_TASKS_BEST_PRACTICES.md)
