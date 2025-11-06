# Streaming Guide

**Platform**: Windows (primary), Linux/macOS (supported)  
**Last Updated**: 2025-11-05

## Overview

This guide explains how to implement real-time output streaming for long-running tasks in the PrismQ Client Backend. It covers the integration between execution patterns, output capture, and SSE (Server-Sent Events) streaming.

## Quick Start

### Basic Long-Running Task with Streaming

```python
import asyncio
from pathlib import Path
from src.core.execution_patterns import execute_long_running_task
from src.core.output_capture import OutputCapture

async def run_module_with_streaming():
    # Setup output capture
    log_dir = Path("logs")
    output_capture = OutputCapture(log_dir=log_dir)
    
    # Execute long-running task
    run_id = "run-123"
    script_path = Path("modules/my_module.py")
    
    exit_code = await execute_long_running_task(
        run_id=run_id,
        script_path=script_path,
        output_capture=output_capture
    )
    
    print(f"Task completed with exit code: {exit_code}")
```

## Architecture

### Components

1. **execution_patterns.py** - Implements Pattern 2 (Long-Running Background Task)
2. **output_capture.py** - Captures and streams output in real-time
3. **subprocess_wrapper.py** - Cross-platform subprocess execution
4. **SSE endpoints** - FastAPI endpoints for real-time log streaming

### Data Flow

```
Module Script
    ↓ stdout/stderr
Subprocess Wrapper
    ↓ line-by-line
Execution Pattern (execute_long_running_task)
    ↓ streaming
Output Capture (append_line)
    ↓ broadcast
SSE Subscribers
    ↓ HTTP
Frontend Client
```

## Pattern 2: Long-Running Background Task

This pattern from `BACKGROUND_TASKS_BEST_PRACTICES.md` provides:

- ✅ Real-time output streaming
- ✅ Proper cancellation handling
- ✅ Graceful process termination
- ✅ Background task lifecycle management

### Implementation

```python
from src.core.execution_patterns import execute_long_running_task

async def execute_long_running_task(
    run_id: str,
    script_path: Path,
    output_capture: OutputCapture,
    args: Optional[list] = None,
    cwd: Optional[Path] = None
) -> int:
    """Execute a long-running task with real-time output capture."""
    # Implementation handles:
    # - Subprocess creation
    # - Output streaming (stdout + stderr)
    # - Cancellation handling
    # - Graceful termination
    # - Resource cleanup
```

### Key Features

#### 1. Real-Time Output Streaming

Output is captured and streamed line-by-line as it's produced:

```python
async def stream_output():
    """Stream stdout to output capture service."""
    while True:
        line = await stdout.readline()
        if not line:
            break
        await output_capture.append_line(run_id, line.decode())
```

#### 2. Cancellation Handling

Tasks can be cancelled gracefully with proper cleanup:

```python
try:
    exit_code = await process.wait()
except asyncio.CancelledError:
    # Graceful termination with timeout
    await process.terminate()
    await asyncio.wait_for(process.wait(), timeout=5.0)
    raise
```

#### 3. Dual Stream Capture

Both stdout and stderr are captured separately:

```python
# Start both streaming tasks
stream_stdout_task = asyncio.create_task(stream_output())
stream_stderr_task = asyncio.create_task(stream_errors())

# Clean up both when done
finally:
    stream_stdout_task.cancel()
    stream_stderr_task.cancel()
```

## Output Capture API

### append_line Method

The new `append_line` method added to `OutputCapture` enables streaming:

```python
async def append_line(
    self,
    run_id: str,
    line: str,
    stream: str = 'stdout'
) -> None:
    """Append a single line to the output capture buffer and broadcast."""
```

#### Usage Examples

```python
# Append stdout line
await output_capture.append_line("run-123", "Processing item 1\n")

# Append stderr line
await output_capture.append_line("run-123", "Warning!\n", stream='stderr')
```

#### Features

- **Auto-initialization**: Creates buffers/files if they don't exist
- **Whitespace stripping**: Removes trailing whitespace from lines
- **Log level parsing**: Automatically detects log levels
- **SSE broadcasting**: Sends to all subscribers in real-time
- **Persistent storage**: Writes to log file
- **Thread-safe**: Can be called concurrently

## SSE Streaming Integration

### Subscribe to Logs

```python
async def stream_logs(run_id: str):
    """Subscribe to real-time log updates."""
    async for log_entry in output_capture.subscribe_sse(run_id):
        print(f"[{log_entry.timestamp}] {log_entry.message}")
```

### FastAPI SSE Endpoint

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/runs/{run_id}/logs/stream")
async def stream_run_logs(run_id: str):
    """Stream logs via SSE."""
    async def event_generator():
        async for entry in output_capture.subscribe_sse(run_id):
            yield f"data: {entry.to_dict()}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

## Complete Example: Background Task with Streaming

```python
import asyncio
from pathlib import Path
from src.core.execution_patterns import execute_long_running_task
from src.core.output_capture import OutputCapture
from src.core.run_registry import RunRegistry
from src.models.run import Run, RunStatus

async def execute_module_with_streaming(
    module_id: str,
    script_path: Path,
    parameters: dict
):
    """Execute a module with real-time log streaming."""
    
    # Create run record
    run_registry = RunRegistry()
    run = Run(
        module_id=module_id,
        parameters=parameters,
        status=RunStatus.RUNNING
    )
    await run_registry.create_run(run)
    
    # Setup output capture
    log_dir = Path("logs")
    output_capture = OutputCapture(log_dir=log_dir)
    
    try:
        # Execute with streaming
        exit_code = await execute_long_running_task(
            run_id=run.run_id,
            script_path=script_path,
            output_capture=output_capture
        )
        
        # Update run status
        run.status = RunStatus.COMPLETED if exit_code == 0 else RunStatus.FAILED
        run.exit_code = exit_code
        await run_registry.update_run(run)
        
        return run
        
    except asyncio.CancelledError:
        # Task was cancelled
        run.status = RunStatus.CANCELLED
        await run_registry.update_run(run)
        raise
        
    except Exception as e:
        # Task failed
        run.status = RunStatus.FAILED
        run.error_message = str(e)
        await run_registry.update_run(run)
        raise
        
    finally:
        # Cleanup
        output_capture.cleanup_run(run.run_id)
```

## Cancellation Example

```python
import asyncio

async def run_cancellable_task():
    """Run a task that can be cancelled."""
    
    # Start task
    task = asyncio.create_task(
        execute_long_running_task(
            run_id="cancel-demo",
            script_path=Path("long_script.py"),
            output_capture=output_capture
        )
    )
    
    # Let it run for a bit
    await asyncio.sleep(2.0)
    
    # Cancel it
    task.cancel()
    
    # Handle cancellation
    try:
        await task
    except asyncio.CancelledError:
        print("Task was cancelled gracefully")
```

## Best Practices

### 1. Always Use Output Capture

```python
# ✅ Good: Use OutputCapture for streaming
output_capture = OutputCapture(log_dir=Path("logs"))
exit_code = await execute_long_running_task(
    run_id=run_id,
    script_path=script_path,
    output_capture=output_capture
)

# ❌ Bad: Direct subprocess without streaming
process = await asyncio.create_subprocess_exec(...)
```

### 2. Clean Up Subscribers

```python
# ✅ Good: Always cleanup
try:
    exit_code = await execute_long_running_task(...)
finally:
    output_capture.cleanup_run(run_id)

# ❌ Bad: Missing cleanup
exit_code = await execute_long_running_task(...)
# SSE subscribers not cleaned up!
```

### 3. Handle Cancellation

```python
# ✅ Good: Catch and re-raise CancelledError
try:
    await execute_long_running_task(...)
except asyncio.CancelledError:
    # Log cancellation
    logger.info("Task cancelled")
    # Re-raise for proper cleanup
    raise

# ❌ Bad: Swallow CancelledError
try:
    await execute_long_running_task(...)
except asyncio.CancelledError:
    pass  # Don't do this!
```

### 4. Set Appropriate Timeouts

```python
# ✅ Good: Use timeout for long tasks
try:
    exit_code = await asyncio.wait_for(
        execute_long_running_task(...),
        timeout=3600  # 1 hour
    )
except asyncio.TimeoutError:
    logger.error("Task exceeded timeout")
```

### 5. Monitor Resource Usage

```python
# ✅ Good: Check system resources
from src.core.resource_manager import ResourceManager

resource_manager = ResourceManager()
if await resource_manager.check_resources():
    await execute_long_running_task(...)
else:
    raise ResourceLimitException("Insufficient resources")
```

## Testing

### Unit Test Example

```python
import pytest
from pathlib import Path

@pytest.mark.asyncio
async def test_streaming_execution(tmp_path):
    """Test long-running task with streaming."""
    # Create test script
    script = tmp_path / "test.py"
    script.write_text("print('Hello from streaming')")
    
    # Setup
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    output_capture = OutputCapture(log_dir=log_dir)
    
    # Execute
    exit_code = await execute_long_running_task(
        run_id="test-1",
        script_path=script,
        output_capture=output_capture
    )
    
    # Verify
    assert exit_code == 0
    logs = output_capture.get_logs("test-1")
    assert len(logs) == 1
    assert "Hello from streaming" in logs[0].message
```

## Troubleshooting

### Issue: No Output Captured

**Cause**: Script output not flushed

**Solution**: Ensure scripts flush output:
```python
import sys
print("Message", flush=True)
sys.stdout.flush()
```

### Issue: Partial Output Missing

**Cause**: Buffer size limit reached

**Solution**: Increase buffer size:
```python
output_capture = OutputCapture(
    log_dir=log_dir,
    max_buffer_size=50000  # Increase from default 10000
)
```

### Issue: SSE Connection Lost

**Cause**: Long idle periods without output

**Solution**: Send keepalive messages:
```python
async def keepalive():
    while True:
        await asyncio.sleep(30)
        await output_capture.append_line(run_id, "# keepalive")
```

### Issue: Memory Growth

**Cause**: Too many subscribers not cleaned up

**Solution**: Always cleanup:
```python
finally:
    output_capture.cleanup_run(run_id)
```

## Performance Considerations

### Optimal Settings

```python
# For typical modules (100-1000 lines of output)
output_capture = OutputCapture(
    log_dir=log_dir,
    max_buffer_size=10000  # Default
)

# For verbose modules (10,000+ lines)
output_capture = OutputCapture(
    log_dir=log_dir,
    max_buffer_size=50000  # Increased
)

# For minimal memory usage
output_capture = OutputCapture(
    log_dir=log_dir,
    max_buffer_size=1000  # Reduced
)
```

### Concurrent Runs

```python
# Limit concurrent runs to avoid resource exhaustion
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

async def execute_with_limit(run_id, script_path):
    async with semaphore:
        return await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture
        )
```

## See Also

- [Background Tasks Best Practices](BACKGROUND_TASKS_BEST_PRACTICES.md) - Complete guide to all patterns
- [Windows Setup Guide](../WINDOWS_SETUP.md) - Windows-specific setup
- [API Reference](../API_REFERENCE.md) - Complete API documentation
- [Log Streaming Guide](../LOG_STREAMING_GUIDE.md) - SSE implementation details

---

**Last Updated**: 2025-11-05  
**Maintainer**: PrismQ Team  
**Feedback**: Create an issue in `_meta/issues/new/`
