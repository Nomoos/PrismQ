"""Output capture service for real-time log streaming."""

import asyncio
import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional

import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Represents a single log line with metadata."""
    
    timestamp: datetime
    level: str
    message: str
    stream: str  # 'stdout' or 'stderr'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "stream": self.stream
        }


class OutputCapture:
    """
    Captures and manages output from running modules.
    
    Responsibilities:
    - Capture stdout/stderr in real-time
    - Buffer logs in memory (circular buffer)
    - Write logs to persistent files
    - Provide log retrieval (polling)
    - Broadcast logs to SSE subscribers
    
    This class follows SOLID principles:
    - Single Responsibility: Only handles output capture and streaming
    - Open/Closed: Extensible through subclassing or composition
    - Dependency Inversion: Uses abstractions (Path, asyncio streams)
    """
    
    def __init__(self, log_dir: Path, max_buffer_size: int = 10000):
        """
        Initialize output capture service.
        
        Args:
            log_dir: Directory for storing log files
            max_buffer_size: Maximum number of log entries to keep in memory
        """
        self.log_dir = log_dir
        self.max_buffer_size = max_buffer_size
        
        # Circular buffers for each run (in-memory)
        self.log_buffers: Dict[str, deque] = {}
        
        # File handles for persistent logs
        self.log_files: Dict[str, Path] = {}
        
        # SSE subscribers for each run (Queue per subscriber)
        self.sse_subscribers: Dict[str, List[asyncio.Queue]] = {}
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    async def start_capture(
        self,
        run_id: str,
        stdout_stream,
        stderr_stream
    ) -> tuple:
        """
        Start capturing output from a subprocess.
        
        Args:
            run_id: Unique run identifier
            stdout_stream: Subprocess stdout stream
            stderr_stream: Subprocess stderr stream
            
        Returns:
            Tuple of (stdout_task, stderr_task) for monitoring
        """
        # Initialize buffer (circular with max size)
        self.log_buffers[run_id] = deque(maxlen=self.max_buffer_size)
        
        # Initialize SSE subscribers list
        self.sse_subscribers[run_id] = []
        
        # Create log file path
        log_file = self.log_dir / f"{run_id}.log"
        self.log_files[run_id] = log_file
        
        # Start capture tasks
        stdout_task = asyncio.create_task(
            self._capture_stream(run_id, stdout_stream, "stdout")
        )
        stderr_task = asyncio.create_task(
            self._capture_stream(run_id, stderr_stream, "stderr")
        )
        
        logger.info(f"Started output capture for run {run_id}")
        
        return stdout_task, stderr_task
    
    async def _capture_stream(
        self,
        run_id: str,
        stream,
        stream_type: str
    ):
        """
        Capture output from a single stream.
        
        Args:
            run_id: Run identifier
            stream: AsyncIO stream to read from
            stream_type: Type of stream ("stdout" or "stderr")
        """
        async with aiofiles.open(self.log_files[run_id], mode='a') as log_file:
            while True:
                line = await stream.readline()
                if not line:
                    break
                
                line_str = line.decode('utf-8').rstrip()
                
                # Parse log level from line (simple heuristic)
                level = self._parse_log_level(line_str, stream_type)
                
                # Create log entry
                entry = LogEntry(
                    timestamp=datetime.now(timezone.utc),
                    level=level,
                    message=line_str,
                    stream=stream_type
                )
                
                # Add to buffer (automatically removes oldest if full)
                self.log_buffers[run_id].append(entry)
                
                # Write to file
                await log_file.write(
                    f"[{entry.timestamp.isoformat()}] [{entry.level}] [{stream_type}] {line_str}\n"
                )
                await log_file.flush()
                
                # Broadcast to SSE subscribers
                await self._broadcast_to_subscribers(run_id, entry)
        
        logger.debug(f"Finished capturing {stream_type} for run {run_id}")
    
    def _parse_log_level(self, message: str, stream_type: str) -> str:
        """
        Parse log level from message content.
        
        Args:
            message: Log message
            stream_type: Stream type (stdout/stderr)
            
        Returns:
            Log level string
        """
        message_upper = message.upper()
        
        # Check for common log level patterns
        if "ERROR" in message_upper or "EXCEPTION" in message_upper:
            return "ERROR"
        elif "WARNING" in message_upper or "WARN" in message_upper:
            return "WARNING"
        elif "DEBUG" in message_upper:
            return "DEBUG"
        elif "CRITICAL" in message_upper or "FATAL" in message_upper:
            return "CRITICAL"
        elif "INFO" in message_upper:
            return "INFO"
        else:
            # Default based on stream type
            return "ERROR" if stream_type == "stderr" else "INFO"
    
    async def _broadcast_to_subscribers(self, run_id: str, entry: LogEntry):
        """
        Broadcast log entry to all SSE subscribers.
        
        Args:
            run_id: Run identifier
            entry: Log entry to broadcast
        """
        if run_id not in self.sse_subscribers:
            return
        
        # Send to all subscribers (non-blocking)
        for queue in self.sse_subscribers[run_id]:
            try:
                queue.put_nowait(entry)
            except asyncio.QueueFull:
                logger.warning(
                    f"SSE queue full for run {run_id}, dropping message"
                )
    
    def get_logs(
        self,
        run_id: str,
        tail: Optional[int] = None,
        since: Optional[datetime] = None
    ) -> List[LogEntry]:
        """
        Get logs for a run.
        
        Args:
            run_id: Run identifier
            tail: Return last N lines
            since: Return logs after this timestamp
            
        Returns:
            List of log entries
        """
        if run_id not in self.log_buffers:
            return []
        
        logs = list(self.log_buffers[run_id])
        
        # Filter by timestamp
        if since:
            logs = [log for log in logs if log.timestamp > since]
        
        # Apply tail limit
        if tail:
            logs = logs[-tail:]
        
        return logs
    
    async def subscribe_sse(self, run_id: str) -> AsyncIterator[LogEntry]:
        """
        Subscribe to real-time log updates via SSE.
        
        Args:
            run_id: Run identifier
            
        Yields:
            LogEntry objects as they arrive
        """
        # Create queue for this subscriber
        queue = asyncio.Queue(maxsize=100)
        
        # Add to subscribers list
        if run_id not in self.sse_subscribers:
            self.sse_subscribers[run_id] = []
        self.sse_subscribers[run_id].append(queue)
        
        try:
            # Send existing logs first
            for entry in self.get_logs(run_id):
                yield entry
            
            # Then stream new logs
            while True:
                entry = await queue.get()
                yield entry
        finally:
            # Cleanup on disconnect
            if run_id in self.sse_subscribers:
                self.sse_subscribers[run_id].remove(queue)
    
    def cleanup_run(self, run_id: str):
        """
        Clean up resources for a completed run.
        
        Args:
            run_id: Run identifier
        """
        # Keep buffer and file for historical access
        # Only clear SSE subscribers
        if run_id in self.sse_subscribers:
            self.sse_subscribers[run_id].clear()
        
        logger.debug(f"Cleaned up SSE subscribers for run {run_id}")
    
    async def read_log_file(self, run_id: str) -> str:
        """
        Read entire log file from disk.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Complete log file contents
        """
        if run_id not in self.log_files:
            return ""
        
        log_file = self.log_files[run_id]
        if not log_file.exists():
            return ""
        
        async with aiofiles.open(log_file, mode='r') as f:
            return await f.read()
