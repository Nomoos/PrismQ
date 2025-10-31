# Issue #104: Capture and Stream Module Output

**Type**: Feature  
**Priority**: High  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1-2 weeks  
**Dependencies**: #103 (Backend Module Runner)  
**Can be parallelized with**: #107 (Frontend Log Display)

---

## Description

Extend the backend to capture stdout/stderr output from running modules in real-time and provide endpoints for both polling-based log retrieval and real-time streaming via Server-Sent Events (SSE). This enables users to monitor module progress live, similar to Script-Server's real-time output feature.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│           Running Module (subprocess)                 │
│                                                        │
│  stdout ─────┐                                        │
│  stderr ─────┤                                        │
└──────────────┼────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────┐
│            OutputCapture Service                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  - Read stdout/stderr asynchronously           │  │
│  │  - Buffer logs in memory (circular buffer)     │  │
│  │  - Write logs to file                          │  │
│  │  - Broadcast to SSE subscribers                │  │
│  └────────────────────────────────────────────────┘  │
└───────────┬──────────────────────────────────────────┘
            │
            ├─────────────────┬────────────────────────┐
            ▼                 ▼                        ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
    │ Log Buffer   │  │  Log File    │  │  SSE Broadcaster │
    │ (Memory)     │  │  (Disk)      │  │  (WebSocket alt) │
    └──────────────┘  └──────────────┘  └──────────────────┘
            │                 │                        │
            └─────────────────┴────────────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   API Endpoints     │
                   │ - GET /logs         │
                   │ - GET /logs/stream  │
                   └─────────────────────┘
```

## Core Components

### 1. OutputCapture Service

```python
# src/core/output_capture.py

import asyncio
from typing import Dict, List, Optional, AsyncIterator
from datetime import datetime
from pathlib import Path
from collections import deque
import aiofiles
import logging

logger = logging.getLogger(__name__)

class LogEntry:
    """Represents a single log line."""
    def __init__(self, timestamp: datetime, level: str, message: str, stream: str):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.stream = stream  # 'stdout' or 'stderr'
    
    def to_dict(self):
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
    """
    
    def __init__(self, log_dir: Path, max_buffer_size: int = 10000):
        self.log_dir = log_dir
        self.max_buffer_size = max_buffer_size
        
        # Circular buffers for each run (in-memory)
        self.log_buffers: Dict[str, deque] = {}
        
        # File handles for persistent logs
        self.log_files: Dict[str, Path] = {}
        
        # SSE subscribers for each run
        self.sse_subscribers: Dict[str, List[asyncio.Queue]] = {}
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    async def start_capture(self, run_id: str, stdout_stream, stderr_stream):
        """
        Start capturing output from a subprocess.
        
        Args:
            run_id: Unique run identifier
            stdout_stream: Subprocess stdout stream
            stderr_stream: Subprocess stderr stream
        """
        # Initialize buffer
        self.log_buffers[run_id] = deque(maxlen=self.max_buffer_size)
        
        # Initialize SSE subscribers list
        self.sse_subscribers[run_id] = []
        
        # Create log file
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
    
    async def _capture_stream(self, run_id: str, stream, stream_type: str):
        """Capture output from a single stream."""
        async with aiofiles.open(self.log_files[run_id], mode='a') as log_file:
            while True:
                line = await stream.readline()
                if not line:
                    break
                
                line_str = line.decode('utf-8').rstrip()
                
                # Parse log level from line (simple heuristic)
                level = self._parse_log_level(line_str)
                
                # Create log entry
                entry = LogEntry(
                    timestamp=datetime.utcnow(),
                    level=level,
                    message=line_str,
                    stream=stream_type
                )
                
                # Add to buffer
                self.log_buffers[run_id].append(entry)
                
                # Write to file
                await log_file.write(f"[{entry.timestamp.isoformat()}] [{entry.level}] {line_str}\n")
                await log_file.flush()
                
                # Broadcast to SSE subscribers
                await self._broadcast_to_subscribers(run_id, entry)
        
        logger.info(f"Finished capturing {stream_type} for run {run_id}")
    
    def _parse_log_level(self, message: str) -> str:
        """Parse log level from message (simple heuristic)."""
        message_upper = message.upper()
        if "ERROR" in message_upper or "EXCEPTION" in message_upper:
            return "ERROR"
        elif "WARNING" in message_upper or "WARN" in message_upper:
            return "WARNING"
        elif "DEBUG" in message_upper:
            return "DEBUG"
        elif "INFO" in message_upper:
            return "INFO"
        else:
            return "INFO"
    
    async def _broadcast_to_subscribers(self, run_id: str, entry: LogEntry):
        """Broadcast log entry to all SSE subscribers."""
        if run_id not in self.sse_subscribers:
            return
        
        # Send to all subscribers
        for queue in self.sse_subscribers[run_id]:
            try:
                await queue.put(entry)
            except asyncio.QueueFull:
                logger.warning(f"SSE queue full for run {run_id}, dropping message")
    
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
            self.sse_subscribers[run_id].remove(queue)
    
    def cleanup_run(self, run_id: str):
        """Clean up resources for a completed run."""
        # Keep buffer and file, only clear SSE subscribers
        if run_id in self.sse_subscribers:
            self.sse_subscribers[run_id].clear()
    
    async def read_log_file(self, run_id: str) -> str:
        """Read entire log file from disk."""
        if run_id not in self.log_files:
            return ""
        
        log_file = self.log_files[run_id]
        if not log_file.exists():
            return ""
        
        async with aiofiles.open(log_file, mode='r') as f:
            return await f.read()
```

### 2. API Endpoints

```python
# src/api/logs.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
from ..core.output_capture import OutputCapture
from ..models.log import LogResponse

router = APIRouter()

@router.get("/runs/{run_id}/logs", response_model=LogResponse)
async def get_run_logs(
    run_id: str,
    tail: Optional[int] = 500,
    since: Optional[str] = None,
    capture: OutputCapture = Depends(get_output_capture)
):
    """
    Get logs for a specific run (polling endpoint).
    
    Query Parameters:
    - tail: Number of recent lines to return (default: 500)
    - since: ISO timestamp to get logs after (optional)
    """
    # Parse since timestamp
    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    # Get logs
    logs = capture.get_logs(run_id, tail=tail, since=since_dt)
    
    return LogResponse(
        run_id=run_id,
        logs=[log.to_dict() for log in logs],
        total_lines=len(logs),
        truncated=tail is not None and len(logs) == tail
    )

@router.get("/runs/{run_id}/logs/stream")
async def stream_run_logs(
    run_id: str,
    capture: OutputCapture = Depends(get_output_capture)
):
    """
    Stream logs in real-time using Server-Sent Events (SSE).
    
    This endpoint keeps the connection open and sends new log
    entries as they arrive.
    """
    async def event_generator():
        async for log_entry in capture.subscribe_sse(run_id):
            # Format as SSE
            data = log_entry.to_dict()
            yield f"data: {json.dumps(data)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

@router.get("/runs/{run_id}/logs/download")
async def download_log_file(
    run_id: str,
    capture: OutputCapture = Depends(get_output_capture)
):
    """
    Download complete log file for a run.
    """
    log_content = await capture.read_log_file(run_id)
    
    if not log_content:
        raise HTTPException(status_code=404, detail="Log file not found")
    
    return StreamingResponse(
        iter([log_content]),
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={run_id}.log"
        }
    )
```

### 3. Integration with ModuleRunner

```python
# Update to src/core/module_runner.py

async def _execute_async(self, run: Run, script_path: Path, parameters: Dict):
    """Internal async execution handler."""
    try:
        # Update status to running
        run.status = RunStatus.RUNNING
        run.started_at = datetime.utcnow()
        self.registry.update_run(run)
        
        # Build command
        command = self._build_command(script_path, parameters)
        
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=script_path.parent
        )
        
        # Start output capture
        stdout_task, stderr_task = await self.output_capture.start_capture(
            run_id=run.run_id,
            stdout_stream=process.stdout,
            stderr_stream=process.stderr
        )
        
        # Wait for process completion
        exit_code = await process.wait()
        
        # Wait for output capture to complete
        await stdout_task
        await stderr_task
        
        # Update run with results
        run.status = RunStatus.COMPLETED if exit_code == 0 else RunStatus.FAILED
        run.completed_at = datetime.utcnow()
        run.exit_code = exit_code
        run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
        
    except Exception as e:
        run.status = RunStatus.FAILED
        run.error_message = str(e)
        run.completed_at = datetime.utcnow()
    finally:
        self.registry.update_run(run)
        self.output_capture.cleanup_run(run.run_id)
```

---

## Log Format

### Standard Log Entry
```json
{
  "timestamp": "2025-10-30T15:45:25.123456Z",
  "level": "INFO",
  "message": "Processing video 1/50...",
  "stream": "stdout"
}
```

### Log Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

---

## Server-Sent Events (SSE)

### Why SSE over WebSockets?
- **Simpler**: Unidirectional (server → client)
- **HTTP**: Works with standard HTTP infrastructure
- **Automatic Reconnection**: Browsers handle reconnection
- **EventSource API**: Native browser support

### Example SSE Stream
```
data: {"timestamp": "2025-10-30T15:45:25Z", "level": "INFO", "message": "Starting..."}

data: {"timestamp": "2025-10-30T15:45:26Z", "level": "INFO", "message": "Processing..."}

data: {"timestamp": "2025-10-30T15:45:28Z", "level": "ERROR", "message": "Failed to connect"}
```

---

## Tasks

### Core Implementation
- [x] Implement `OutputCapture` service
- [x] Add circular buffer for in-memory logs
- [x] Implement log file writing (async)
- [x] Add log level parsing
- [x] Implement SSE subscriber management
- [x] Add log cleanup on run completion

### API Endpoints
- [x] Implement GET `/api/runs/{run_id}/logs` (polling)
- [x] Implement GET `/api/runs/{run_id}/logs/stream` (SSE)
- [x] Implement GET `/api/runs/{run_id}/logs/download`
- [x] Add query parameter handling (tail, since)
- [x] Implement proper streaming response headers

### Integration
- [x] Integrate `OutputCapture` with `ModuleRunner`
- [x] Update process execution to capture streams
- [x] Add dependency injection for `OutputCapture`

### Testing
- [x] Unit tests for `OutputCapture`
- [x] Test circular buffer behavior
- [x] Test SSE streaming
- [x] Test log file persistence
- [x] Test concurrent log capture
- [x] Test memory limits

### Documentation
- [x] Document log format
- [x] Document SSE protocol
- [x] Add usage examples

---

## Acceptance Criteria

- [x] Logs captured in real-time from running modules
- [x] Logs available via polling endpoint with tail/since filters
- [x] SSE endpoint streams logs in real-time
- [x] Logs persisted to disk for historical access
- [x] Memory usage controlled via circular buffer
- [x] Log levels parsed correctly
- [x] Multiple concurrent captures work correctly
- [x] SSE connections cleaned up on disconnect
- [x] Unit tests achieve >80% coverage

## Performance Targets

- Capture rate: >10,000 lines/second
- SSE latency: <100ms from log generation to client
- Memory per run: <10MB for 10,000 log lines
- Concurrent streams: Support 10+ simultaneous SSE connections

## Related Issues

- **Depends on**: #103 (Backend Module Runner)
- **Parallel**: #107 (Frontend Log Display)
- **Related**: #102 (API Design)

## References

- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastAPI Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Python asyncio Streams](https://docs.python.org/3/library/asyncio-stream.html)
- [Script-Server Real-Time Output](https://github.com/bugy/script-server#real-time-script-output)
