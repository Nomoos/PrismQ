"""Execution patterns for background tasks following best practices.

This module implements standardized patterns for executing PrismQ modules
and background tasks with proper error handling, resource cleanup, and
cross-platform compatibility.

Follows SOLID principles:
- Single Responsibility: Each pattern handles a specific execution scenario
- Open/Closed: Extensible patterns without modifying core implementation
- Liskov Substitution: All patterns follow consistent interfaces
- Interface Segregation: Minimal, focused pattern implementations
- Dependency Inversion: Depends on SubprocessWrapper abstraction
"""Execution patterns for background tasks.

This module implements documented patterns from BACKGROUND_TASKS_BEST_PRACTICES.md
for reliable, cross-platform background task execution.

Primary Platform: Windows (with support for Linux/macOS)
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Tuple

from .subprocess_wrapper import SubprocessWrapper, RunMode
from typing import Optional

from .subprocess_wrapper import SubprocessWrapper
from .output_capture import OutputCapture

logger = logging.getLogger(__name__)


async def execute_module(
    script_path: Path,
    args: List[str],
    cwd: Path,
    mode: RunMode = None
) -> Tuple[int, str, str]:
    """Execute a module script and capture output (Pattern 1).
    
    This implements Pattern 1 from BACKGROUND_TASKS_BEST_PRACTICES.md:
    Simple Module Execution with proper error handling, resource cleanup,
    and comprehensive output capture.
    
    Args:
        script_path: Path to the Python script to execute
        args: Command-line arguments to pass to the script
        cwd: Working directory for the subprocess
        mode: Optional RunMode override (auto-detected if None)
        
    Returns:
        Tuple of (exit_code, stdout, stderr) where stdout and stderr are
        decoded strings containing the full output
        
    Raises:
        FileNotFoundError: If script_path does not exist
        PermissionError: If script is not executable
        RuntimeError: If subprocess creation fails
        
    Example:
        >>> from pathlib import Path
        >>> exit_code, stdout, stderr = await execute_module(
        ...     script_path=Path("/path/to/script.py"),
        ...     args=["--param", "value"],
        ...     cwd=Path("/path/to")
        ... )
        >>> if exit_code == 0:
        ...     print("Success:", stdout)
        ... else:
        ...     print("Failed:", stderr)
    """
    # Validate script exists before attempting execution
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Auto-detect mode if not specified
    wrapper = SubprocessWrapper(mode=mode)
    
    try:
        # Build command
        cmd = ['python', str(script_path)] + args
        
        logger.info(f"Executing module: {script_path.name} with {len(args)} arguments")
        logger.debug(f"Command: {' '.join(cmd)}")
        logger.debug(f"Working directory: {cwd}")
        
        # Create subprocess with proper error handling
async def execute_long_running_task(
    run_id: str,
    script_path: Path,
    output_capture: OutputCapture,
    args: Optional[list] = None,
    cwd: Optional[Path] = None
) -> int:
    """Execute a long-running task with real-time output capture.
    
    This implements Pattern 2 from BACKGROUND_TASKS_BEST_PRACTICES.md:
    - Real-time output streaming via OutputCapture
    - Proper cancellation handling
    - Graceful process termination with timeout
    - Background task lifecycle management
    
    Args:
        run_id: Unique identifier for this run
        script_path: Path to the script to execute
        output_capture: Service for capturing and streaming output
        args: Optional command-line arguments
        cwd: Working directory (defaults to script parent directory)
        
    Returns:
        Process exit code
        
    Raises:
        asyncio.CancelledError: If task is cancelled
        Exception: If task execution fails
        
    Example:
        >>> output_capture = OutputCapture(log_dir=Path("logs"))
        >>> exit_code = await execute_long_running_task(
        ...     run_id="run-123",
        ...     script_path=Path("module.py"),
        ...     output_capture=output_capture
        ... )
    """
    wrapper = SubprocessWrapper()
    
    # Use script parent directory if cwd not specified
    if cwd is None:
        cwd = script_path.parent
    
    # Build command
    cmd = ['python', str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        # Create subprocess
        process, stdout, stderr = await wrapper.create_subprocess(
            *cmd,
            cwd=cwd
        )
        
        logger.info(f"Started process PID={process.pid} for {script_path.name}")
        
        # Collect output line by line for better logging and monitoring
        stdout_data = []
        stderr_data = []
        
        async def read_stream(stream, buffer, stream_name: str):
            """Read output stream line by line."""
            line_count = 0
            while True:
                line = await stream.readline()
                if not line:
                    break
                buffer.append(line)
                line_count += 1
                decoded_line = line.decode('utf-8', errors='replace').strip()
                logger.debug(f"[{stream_name}] {decoded_line}")
            
            logger.debug(f"Read {line_count} lines from {stream_name}")
        
        # Read both streams concurrently to avoid deadlocks
        await asyncio.gather(
            read_stream(stdout, stdout_data, "stdout"),
            read_stream(stderr, stderr_data, "stderr")
        )
        
        # Wait for process completion
        exit_code = await process.wait()
        
        # Decode output
        stdout_str = b''.join(stdout_data).decode('utf-8', errors='replace')
        stderr_str = b''.join(stderr_data).decode('utf-8', errors='replace')
        
        if exit_code == 0:
            logger.info(f"Process completed successfully with exit code {exit_code}")
        else:
            # Log error with preview of stderr for debugging
            stderr_preview = stderr_str[:200] + "..." if len(stderr_str) > 200 else stderr_str
            logger.warning(
                f"Process completed with non-zero exit code {exit_code}. "
                f"stderr: {stderr_preview}"
            )
        
        return (exit_code, stdout_str, stderr_str)
        
    except asyncio.CancelledError:
        logger.warning(f"Module execution cancelled for {script_path.name}")
        raise
        
    except FileNotFoundError as e:
        logger.error(f"File not found during execution: {e}")
        raise
        
    except PermissionError as e:
        logger.error(f"Permission denied executing {script_path.name}: {e}")
        raise
        
    except Exception as e:
        logger.exception(f"Unexpected error executing {script_path.name}")
        raise RuntimeError(f"Module execution failed: {e}") from e
        
    finally:
        # Always cleanup resources
        wrapper.cleanup()
        logger.debug(f"Cleaned up subprocess wrapper for {script_path.name}")
        logger.info(f"Started long-running task {run_id}, PID={process.pid}")
        
        async def stream_output():
            """Stream stdout to output capture service."""
            while True:
                line = await stdout.readline()
                if not line:
                    break
                    
                # Send to output capture service for SSE streaming
                await output_capture.append_line(run_id, line.decode())
        
        async def stream_errors():
            """Stream stderr to output capture service."""
            while True:
                line = await stderr.readline()
                if not line:
                    break
                    
                # Send to output capture service for SSE streaming
                await output_capture.append_line(run_id, line.decode(), stream='stderr')
        
        # Start output streaming as background tasks
        stream_stdout_task = asyncio.create_task(stream_output())
        stream_stderr_task = asyncio.create_task(stream_errors())
        
        # Wait for process or cancellation
        try:
            exit_code = await process.wait()
            logger.info(f"Task {run_id} completed with exit code {exit_code}")
            return exit_code
            
        except asyncio.CancelledError:
            logger.warning(f"Task {run_id} cancelled, terminating process")
            
            # Graceful termination
            try:
                await process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning(f"Process {process.pid} did not terminate gracefully, killing")
                await process.kill()
                await process.wait()
            
            raise
            
        finally:
            # Ensure streaming tasks are cleaned up
            stream_stdout_task.cancel()
            stream_stderr_task.cancel()
            
            try:
                await asyncio.gather(
                    stream_stdout_task,
                    stream_stderr_task,
                    return_exceptions=True
                )
            except asyncio.CancelledError:
                pass
                
    finally:
        wrapper.cleanup()
