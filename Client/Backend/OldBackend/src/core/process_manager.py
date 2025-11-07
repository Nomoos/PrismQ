"""Process manager for executing module subprocesses."""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    """Result of a subprocess execution."""
    
    exit_code: int
    stdout: str
    stderr: str
    error: Optional[str] = None


class ProcessManager:
    """
    Manages subprocess execution for module runs.
    
    Responsibilities:
    - Create and monitor subprocesses
    - Capture stdout/stderr in real-time
    - Handle process cancellation
    - Track process PIDs
    
    This class follows SOLID principles:
    - Single Responsibility: Only handles process execution and monitoring
    - Open/Closed: Extensible through subclassing if needed
    - Dependency Inversion: Depends on asyncio abstractions, not concrete implementations
    """
    
    def __init__(self):
        """Initialize process manager with empty process and log tracking."""
        self.processes: Dict[str, asyncio.subprocess.Process] = {}
        self.log_buffers: Dict[str, list] = {}
    
    async def run_process(
        self,
        run_id: str,
        command: list[str],
        cwd: Optional[Path] = None
    ) -> ProcessResult:
        """
        Execute a subprocess and capture output.
        
        Args:
            run_id: Unique run identifier
            command: Command to execute as a list of arguments
            cwd: Working directory for the process
            
        Returns:
            ProcessResult with exit code and captured output
            
        Raises:
            Exception: If process creation fails
        """
        try:
            # Create subprocess with piped stdout/stderr
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            self.processes[run_id] = process
            self.log_buffers[run_id] = []
            
            logger.info(f"Started process for run {run_id}, PID: {process.pid}")
            
            # Read output streams asynchronously
            stdout_task = asyncio.create_task(self._read_stream(
                process.stdout, run_id, "stdout"
            ))
            stderr_task = asyncio.create_task(self._read_stream(
                process.stderr, run_id, "stderr"
            ))
            
            # Wait for process completion
            exit_code = await process.wait()
            
            # Wait for output streams to complete
            stdout = await stdout_task
            stderr = await stderr_task
            
            logger.info(f"Process for run {run_id} completed with exit code {exit_code}")
            
            return ProcessResult(
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr
            )
            
        except Exception as e:
            logger.error(f"Error running process for {run_id}: {e}")
            return ProcessResult(
                exit_code=-1,
                stdout="",
                stderr="",
                error=str(e)
            )
        finally:
            # Cleanup process reference
            if run_id in self.processes:
                del self.processes[run_id]
    
    async def _read_stream(self, stream, run_id: str, stream_type: str) -> str:
        """
        Read stream line by line and buffer output.
        
        Args:
            stream: AsyncIO stream to read from
            run_id: Run identifier for log buffering
            stream_type: Type of stream ("stdout" or "stderr")
            
        Returns:
            Complete output as a single string
        """
        output_lines = []
        
        while True:
            line = await stream.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8').rstrip()
            output_lines.append(line_str)
            
            # Add to log buffer with timestamp
            from datetime import datetime, timezone
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stream": stream_type,
                "message": line_str
            }
            self.log_buffers[run_id].append(log_entry)
        
        return "\n".join(output_lines)
    
    async def cancel_process(self, run_id: str) -> bool:
        """
        Cancel a running process.
        
        Attempts graceful termination first, then forces kill if needed.
        
        Args:
            run_id: Run identifier
            
        Returns:
            True if process was cancelled, False if not found
        """
        if run_id not in self.processes:
            return False
        
        process = self.processes[run_id]
        
        try:
            # Try graceful termination first
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning(f"Process {run_id} didn't terminate gracefully, killing...")
            process.kill()
            await process.wait()
        
        logger.info(f"Cancelled process for run {run_id}")
        return True
    
    def get_logs(self, run_id: str, tail: Optional[int] = None) -> list:
        """
        Get logs for a run.
        
        Args:
            run_id: Run identifier
            tail: Optional number of recent lines to return
            
        Returns:
            List of log entries
        """
        logs = self.log_buffers.get(run_id, [])
        if tail:
            return logs[-tail:]
        return logs
