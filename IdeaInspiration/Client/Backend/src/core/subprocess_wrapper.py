"""Cross-platform subprocess wrapper for Windows compatibility.

This module provides a unified interface for subprocess execution that works
across different platforms and execution modes.

Primary Platform: Windows (with support for Linux/macOS)
"""

import asyncio
import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from .exceptions import SubprocessPolicyException

logger = logging.getLogger(__name__)


class RunMode(str, Enum):
    """Execution modes for subprocess wrapper.
    
    - LOCAL: Synchronous subprocess for dev/debug
    - ASYNC: Asyncio subprocess (Linux/macOS or Windows with ProactorEventLoop)
    - THREADED: Thread-based wrapper around subprocess.Popen (Windows safe)
    - DRY_RUN: Logs command without execution (CI testing)
    """
    LOCAL = "local"
    ASYNC = "async"
    THREADED = "threaded"
    DRY_RUN = "dry-run"


@dataclass
class SubprocessResult:
    """Result from subprocess execution."""
    exit_code: int
    stdout: bytes
    stderr: bytes
    pid: Optional[int] = None


class SubprocessWrapper:
    """Cross-platform subprocess wrapper with multiple execution modes.
    
    This class provides a unified interface for running subprocesses that works
    reliably across Windows, Linux, and macOS with different execution strategies.
    
    Follows SOLID principles:
    - Single Responsibility: Handles cross-platform subprocess execution
    - Open/Closed: Extensible via RunMode enum
    - Liskov Substitution: All modes implement the same interface
    - Dependency Inversion: Depends on standard library abstractions
    """
    
    def __init__(self, mode: Optional[RunMode] = None, max_workers: int = 4):
        """Initialize subprocess wrapper.
        
        Args:
            mode: Execution mode (auto-detected if None)
            max_workers: Maximum thread pool workers for THREADED mode
        """
        self.mode = mode or self._detect_mode()
        self.executor = ThreadPoolExecutor(max_workers=max_workers) if self.mode == RunMode.THREADED else None
        logger.info(f"SubprocessWrapper initialized with mode: {self.mode}")
    
    @staticmethod
    def _detect_mode() -> RunMode:
        """Auto-detect the best execution mode for the current platform.
        
        Returns:
            Recommended RunMode for the platform
        """
        if sys.platform == 'win32':
            # On Windows, always use THREADED mode by default for maximum compatibility.
            # Even when ProactorEventLoopPolicy is set, if an event loop was created
            # before the policy was set (e.g., by uvicorn --reload), subprocess operations
            # will fail. THREADED mode works reliably regardless of how the server is started.
            # 
            # Note: Users can explicitly request ASYNC mode by:
            # 1. Setting PRISMQ_RUN_MODE=async environment variable, OR
            # 2. Passing mode=RunMode.ASYNC to SubprocessWrapper constructor
            # (Requires ProactorEventLoopPolicy to be set before any event loop is created)
            logger.info("Windows platform detected - using THREADED mode for reliability")
            return RunMode.THREADED
        else:
            # Linux/macOS can use ASYNC mode safely
            logger.info(f"Platform {sys.platform} detected - using ASYNC mode")
            return RunMode.ASYNC
    
    async def create_subprocess(
        self,
        *args,
        stdout=None,
        stderr=None,
        cwd: Optional[Path] = None,
        **kwargs
    ) -> Tuple[asyncio.subprocess.Process, asyncio.StreamReader, asyncio.StreamReader]:
        """Create a subprocess with appropriate strategy based on mode.
        
        Args:
            *args: Command arguments
            stdout: Stdout handling (defaults to PIPE)
            stderr: Stderr handling (defaults to PIPE)
            cwd: Working directory
            **kwargs: Additional subprocess arguments
            
        Returns:
            Tuple of (process, stdout_reader, stderr_reader) or compatible wrapper
            
        Raises:
            NotImplementedError: If ASYNC mode fails on unsupported platform
            RuntimeError: If subprocess creation fails
        """
        if stdout is None:
            stdout = asyncio.subprocess.PIPE
        if stderr is None:
            stderr = asyncio.subprocess.PIPE
        
        logger.debug(f"Creating subprocess with mode {self.mode}: {args[0] if args else 'unknown'}")
        
        if self.mode == RunMode.DRY_RUN:
            return await self._dry_run_subprocess(*args, cwd=cwd)
        elif self.mode == RunMode.LOCAL:
            return await self._local_subprocess(*args, stdout=stdout, stderr=stderr, cwd=cwd, **kwargs)
        elif self.mode == RunMode.THREADED:
            return await self._threaded_subprocess(*args, stdout=stdout, stderr=stderr, cwd=cwd, **kwargs)
        elif self.mode == RunMode.ASYNC:
            return await self._async_subprocess(*args, stdout=stdout, stderr=stderr, cwd=cwd, **kwargs)
        else:
            raise ValueError(f"Unknown run mode: {self.mode}")
    
    async def _async_subprocess(
        self, *args, stdout, stderr, cwd, **kwargs
    ) -> Tuple[asyncio.subprocess.Process, asyncio.StreamReader, asyncio.StreamReader]:
        """Create subprocess using asyncio (requires proper event loop).
        
        This is the most efficient method but requires Windows ProactorEventLoop
        or Linux/macOS.
        
        Raises:
            SubprocessPolicyException: If Windows event loop policy not configured
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=stdout,
                stderr=stderr,
                cwd=cwd,
                **kwargs
            )
            logger.info(f"ASYNC subprocess created, PID: {process.pid}")
            return process, process.stdout, process.stderr
        except NotImplementedError as e:
            # Get current policy for error message
            policy = asyncio.get_event_loop_policy()
            current_policy = type(policy).__name__
            
            logger.error(
                "asyncio.create_subprocess_exec not supported on this platform. "
                "On Windows, ensure ProactorEventLoopPolicy is set or use THREADED mode."
            )
            raise SubprocessPolicyException(
                "ASYNC mode requires Windows ProactorEventLoopPolicy. "
                "Set mode=THREADED or configure event loop policy.",
                current_policy=current_policy
            ) from e
    
    async def _threaded_subprocess(
        self, *args, stdout, stderr, cwd, **kwargs
    ) -> Tuple["ThreadedProcess", "ThreadedStreamReader", "ThreadedStreamReader"]:
        """Create subprocess using thread pool (Windows safe).
        
        This wraps subprocess.Popen in a thread pool to provide async-like
        interface without requiring specific event loop policies.
        """
        loop = asyncio.get_event_loop()
        
        # Run subprocess.Popen in thread pool
        def _create_process():
            return subprocess.Popen(
                args,
                stdout=subprocess.PIPE if stdout == asyncio.subprocess.PIPE else stdout,
                stderr=subprocess.PIPE if stderr == asyncio.subprocess.PIPE else stderr,
                cwd=cwd,
                **kwargs
            )
        
        process = await loop.run_in_executor(self.executor, _create_process)
        logger.info(f"THREADED subprocess created, PID: {process.pid}")
        
        # Wrap in ThreadedProcess for consistent interface
        threaded_proc = ThreadedProcess(process, self.executor)
        return threaded_proc, threaded_proc.stdout, threaded_proc.stderr
    
    async def _local_subprocess(
        self, *args, stdout, stderr, cwd, **kwargs
    ) -> Tuple["LocalProcess", "LocalStreamReader", "LocalStreamReader"]:
        """Create subprocess synchronously (for dev/debug).
        
        This runs subprocess.run synchronously in a thread pool to avoid
        blocking the event loop.
        """
        loop = asyncio.get_event_loop()
        
        def _run_process():
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE if stdout == asyncio.subprocess.PIPE else stdout,
                stderr=subprocess.PIPE if stderr == asyncio.subprocess.PIPE else stderr,
                cwd=cwd,
                **kwargs
            )
            return result
        
        result = await loop.run_in_executor(None, _run_process)
        logger.info(f"LOCAL subprocess completed, exit code: {result.returncode}")
        
        # Wrap in LocalProcess for consistent interface
        local_proc = LocalProcess(result)
        return local_proc, local_proc.stdout, local_proc.stderr
    
    async def _dry_run_subprocess(
        self, *args, cwd, **kwargs
    ) -> Tuple["DryRunProcess", "DryRunStreamReader", "DryRunStreamReader"]:
        """Log command without execution (for CI testing)."""
        cmd_str = " ".join(str(arg) for arg in args)
        logger.info(f"DRY_RUN mode - would execute: {cmd_str}")
        logger.info(f"  Working directory: {cwd}")
        
        dry_proc = DryRunProcess(args, cwd)
        return dry_proc, dry_proc.stdout, dry_proc.stderr
    
    def cleanup(self):
        """Cleanup resources."""
        if self.executor:
            self.executor.shutdown(wait=False)


class ThreadedProcess:
    """Wrapper around subprocess.Popen to provide async-like interface."""
    
    def __init__(self, popen: subprocess.Popen, executor: ThreadPoolExecutor):
        self._popen = popen
        self._executor = executor
        self.pid = popen.pid
        self.returncode = None
        
        # Create threaded stream readers
        self.stdout = ThreadedStreamReader(popen.stdout, executor) if popen.stdout else None
        self.stderr = ThreadedStreamReader(popen.stderr, executor) if popen.stderr else None
    
    async def wait(self) -> int:
        """Wait for process completion."""
        loop = asyncio.get_event_loop()
        self.returncode = await loop.run_in_executor(self._executor, self._popen.wait)
        return self.returncode
    
    def terminate(self):
        """Terminate the process."""
        self._popen.terminate()
    
    def kill(self):
        """Kill the process."""
        self._popen.kill()


class ThreadedStreamReader:
    """Async wrapper around file stream for reading in thread pool."""
    
    def __init__(self, stream, executor: ThreadPoolExecutor):
        self._stream = stream
        self._executor = executor
    
    async def readline(self) -> bytes:
        """Read a line from the stream."""
        if not self._stream:
            return b''
        
        loop = asyncio.get_event_loop()
        try:
            line = await loop.run_in_executor(self._executor, self._stream.readline)
            return line
        except Exception as e:
            logger.debug(f"Error reading line: {e}")
            return b''


class LocalProcess:
    """Wrapper around completed subprocess.CompletedProcess."""
    
    def __init__(self, result: subprocess.CompletedProcess):
        self._result = result
        self.pid = None  # Process already completed
        self.returncode = result.returncode
        self.stdout = LocalStreamReader(result.stdout)
        self.stderr = LocalStreamReader(result.stderr)
    
    async def wait(self) -> int:
        """Return the already-completed exit code."""
        return self.returncode
    
    def terminate(self):
        """No-op for already completed process."""
        pass
    
    def kill(self):
        """No-op for already completed process."""
        pass


class LocalStreamReader:
    """Wrapper around completed output bytes."""
    
    def __init__(self, output: bytes):
        self._lines = output.split(b'\n') if output else []
        self._index = 0
    
    async def readline(self) -> bytes:
        """Read next line from buffered output."""
        if self._index < len(self._lines):
            line = self._lines[self._index]
            self._index += 1
            return line + b'\n'
        return b''


class DryRunProcess:
    """Mock process for dry-run mode."""
    
    def __init__(self, args, cwd):
        # Use -1 as PID to indicate this is a mock process (not a real system PID)
        self.pid = -1
        self.returncode = 0
        self.stdout = DryRunStreamReader(f"DRY_RUN: stdout for {args[0]}")
        self.stderr = DryRunStreamReader("")
    
    async def wait(self) -> int:
        """Immediately return success."""
        await asyncio.sleep(0.1)  # Simulate minimal execution time
        return 0
    
    def terminate(self):
        """No-op for dry run."""
        pass
    
    def kill(self):
        """No-op for dry run."""
        pass


class DryRunStreamReader:
    """Mock stream reader for dry-run mode."""
    
    def __init__(self, message: str):
        self._lines = [message.encode()] if message else []
        self._index = 0
    
    async def readline(self) -> bytes:
        """Read mocked output."""
        if self._index < len(self._lines):
            line = self._lines[self._index]
            self._index += 1
            return line + b'\n'
        return b''
