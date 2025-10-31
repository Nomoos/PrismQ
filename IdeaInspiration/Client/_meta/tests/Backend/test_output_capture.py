"""Unit tests for OutputCapture service."""

import asyncio
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta
import tempfile
import shutil

from src.core.output_capture import OutputCapture, LogEntry


@pytest.fixture
def temp_log_dir():
    """Create a temporary log directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def output_capture(temp_log_dir):
    """Create an OutputCapture instance."""
    return OutputCapture(log_dir=temp_log_dir, max_buffer_size=100)


@pytest.mark.asyncio
async def test_output_capture_initialization(output_capture, temp_log_dir):
    """Test OutputCapture initialization."""
    assert output_capture.log_dir == temp_log_dir
    assert output_capture.max_buffer_size == 100
    assert len(output_capture.log_buffers) == 0
    assert len(output_capture.log_files) == 0
    assert len(output_capture.sse_subscribers) == 0
    assert temp_log_dir.exists()


@pytest.mark.asyncio
async def test_start_capture(output_capture):
    """Test starting capture for a run."""
    run_id = "test_run_start"
    
    # Create a simple process to get real streams
    process = await asyncio.create_subprocess_exec(
        "echo", "test",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Start capture
    stdout_task, stderr_task = await output_capture.start_capture(
        run_id=run_id,
        stdout_stream=process.stdout,
        stderr_stream=process.stderr
    )
    
    # Verify initialization
    assert run_id in output_capture.log_buffers
    assert run_id in output_capture.log_files
    assert run_id in output_capture.sse_subscribers
    
    # Wait for process to complete
    await process.wait()
    await stdout_task
    await stderr_task


@pytest.mark.asyncio
async def test_capture_stream_creates_log_entries(output_capture):
    """Test that capturing a stream creates log entries."""
    run_id = "test_run_456"
    
    # Create a simple process that outputs to stdout
    process = await asyncio.create_subprocess_exec(
        "echo", "Hello World",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Start capture
    stdout_task, stderr_task = await output_capture.start_capture(
        run_id=run_id,
        stdout_stream=process.stdout,
        stderr_stream=process.stderr
    )
    
    # Wait for process to complete
    await process.wait()
    await stdout_task
    await stderr_task
    
    # Check logs were captured
    logs = output_capture.get_logs(run_id)
    assert len(logs) > 0
    assert any("Hello World" in log.message for log in logs)


@pytest.mark.asyncio
async def test_log_level_parsing(output_capture):
    """Test log level parsing from message content."""
    # Test different log levels
    test_cases = [
        ("ERROR: Something went wrong", "stderr", "ERROR"),
        ("WARNING: Be careful", "stdout", "WARNING"),
        ("DEBUG: Detailed info", "stdout", "DEBUG"),
        ("INFO: Normal message", "stdout", "INFO"),
        ("Regular output", "stdout", "INFO"),
        ("Regular error", "stderr", "ERROR"),
    ]
    
    for message, stream, expected_level in test_cases:
        level = output_capture._parse_log_level(message, stream)
        assert level == expected_level


@pytest.mark.asyncio
async def test_get_logs_with_tail(output_capture):
    """Test getting logs with tail parameter."""
    run_id = "test_run_tail"
    
    # Add some log entries manually
    output_capture.log_buffers[run_id] = []
    for i in range(50):
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            message=f"Log line {i}",
            stream="stdout"
        )
        output_capture.log_buffers[run_id].append(entry)
    
    # Get last 10 logs
    logs = output_capture.get_logs(run_id, tail=10)
    assert len(logs) == 10
    assert logs[-1].message == "Log line 49"
    assert logs[0].message == "Log line 40"


@pytest.mark.asyncio
async def test_get_logs_with_since(output_capture):
    """Test getting logs with since parameter."""
    run_id = "test_run_since"
    
    # Add log entries with different timestamps
    output_capture.log_buffers[run_id] = []
    base_time = datetime.now(timezone.utc)
    
    for i in range(10):
        entry = LogEntry(
            timestamp=base_time + timedelta(seconds=i),
            level="INFO",
            message=f"Log line {i}",
            stream="stdout"
        )
        output_capture.log_buffers[run_id].append(entry)
    
    # Get logs since middle timestamp
    since_time = base_time + timedelta(seconds=5)
    logs = output_capture.get_logs(run_id, since=since_time)
    
    # Should get logs from index 6-9 (4 logs)
    assert len(logs) == 4
    assert logs[0].message == "Log line 6"


@pytest.mark.asyncio
async def test_circular_buffer_behavior(output_capture):
    """Test that circular buffer maintains max size."""
    run_id = "test_run_circular"
    output_capture.max_buffer_size = 10
    
    # Add more entries than max buffer size
    output_capture.log_buffers[run_id] = []
    from collections import deque
    output_capture.log_buffers[run_id] = deque(maxlen=10)
    
    for i in range(20):
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            message=f"Log line {i}",
            stream="stdout"
        )
        output_capture.log_buffers[run_id].append(entry)
    
    # Should only have last 10 entries
    logs = output_capture.get_logs(run_id)
    assert len(logs) == 10
    assert logs[0].message == "Log line 10"
    assert logs[-1].message == "Log line 19"


@pytest.mark.asyncio
async def test_log_file_persistence(output_capture, temp_log_dir):
    """Test that logs are persisted to disk."""
    run_id = "test_run_persist"
    
    # Create a simple process
    process = await asyncio.create_subprocess_exec(
        "echo", "Test log message",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Start capture
    stdout_task, stderr_task = await output_capture.start_capture(
        run_id=run_id,
        stdout_stream=process.stdout,
        stderr_stream=process.stderr
    )
    
    await process.wait()
    await stdout_task
    await stderr_task
    
    # Check log file exists
    log_file = temp_log_dir / f"{run_id}.log"
    assert log_file.exists()
    
    # Read and verify content
    log_content = await output_capture.read_log_file(run_id)
    assert "Test log message" in log_content


@pytest.mark.asyncio
async def test_sse_subscription(output_capture):
    """Test SSE subscription for real-time logs."""
    run_id = "test_run_sse"
    
    # Add some initial logs
    output_capture.log_buffers[run_id] = []
    for i in range(5):
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level="INFO",
            message=f"Initial log {i}",
            stream="stdout"
        )
        output_capture.log_buffers[run_id].append(entry)
    
    # Subscribe to SSE
    output_capture.sse_subscribers[run_id] = []
    
    received_logs = []
    
    async def consume_sse():
        count = 0
        async for log_entry in output_capture.subscribe_sse(run_id):
            received_logs.append(log_entry)
            count += 1
            if count >= 5:  # Stop after receiving initial logs
                break
    
    # Start consuming
    task = asyncio.create_task(consume_sse())
    
    # Wait briefly
    await asyncio.sleep(0.1)
    
    # Cancel task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Should have received initial logs
    assert len(received_logs) >= 5


@pytest.mark.asyncio
async def test_cleanup_run(output_capture):
    """Test cleanup of run resources."""
    run_id = "test_run_cleanup"
    
    # Setup some data
    output_capture.log_buffers[run_id] = []
    output_capture.sse_subscribers[run_id] = [asyncio.Queue()]
    
    # Cleanup
    output_capture.cleanup_run(run_id)
    
    # SSE subscribers should be cleared
    assert len(output_capture.sse_subscribers[run_id]) == 0
    
    # But buffer should remain for historical access
    assert run_id in output_capture.log_buffers


@pytest.mark.asyncio
async def test_concurrent_capture(output_capture):
    """Test capturing logs from multiple runs concurrently."""
    run_ids = ["run_1", "run_2", "run_3"]
    
    async def capture_run(run_id):
        process = await asyncio.create_subprocess_exec(
            "echo", f"Output from {run_id}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout_task, stderr_task = await output_capture.start_capture(
            run_id=run_id,
            stdout_stream=process.stdout,
            stderr_stream=process.stderr
        )
        
        await process.wait()
        await stdout_task
        await stderr_task
    
    # Run captures concurrently
    await asyncio.gather(*[capture_run(run_id) for run_id in run_ids])
    
    # Verify all runs have logs
    for run_id in run_ids:
        logs = output_capture.get_logs(run_id)
        assert len(logs) > 0
        assert any(run_id in log.message for log in logs)


@pytest.mark.asyncio
async def test_log_entry_to_dict(output_capture):
    """Test LogEntry serialization to dict."""
    entry = LogEntry(
        timestamp=datetime(2025, 10, 31, 12, 0, 0, tzinfo=timezone.utc),
        level="INFO",
        message="Test message",
        stream="stdout"
    )
    
    result = entry.to_dict()
    
    assert result["level"] == "INFO"
    assert result["message"] == "Test message"
    assert result["stream"] == "stdout"
    assert "timestamp" in result
    assert "2025-10-31" in result["timestamp"]


@pytest.mark.asyncio
async def test_empty_logs_for_nonexistent_run(output_capture):
    """Test getting logs for a run that doesn't exist."""
    logs = output_capture.get_logs("nonexistent_run")
    assert logs == []


@pytest.mark.asyncio
async def test_read_nonexistent_log_file(output_capture):
    """Test reading log file that doesn't exist."""
    content = await output_capture.read_log_file("nonexistent_run")
    assert content == ""
