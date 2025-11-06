"""Unit tests for ProcessManager."""

import asyncio
import pytest
from pathlib import Path
from src.core.process_manager import ProcessManager, ProcessResult


@pytest.mark.asyncio
async def test_process_manager_initialization():
    """Test ProcessManager initialization."""
    pm = ProcessManager()
    assert isinstance(pm.processes, dict)
    assert isinstance(pm.log_buffers, dict)
    assert len(pm.processes) == 0
    assert len(pm.log_buffers) == 0


@pytest.mark.asyncio
async def test_run_simple_process():
    """Test running a simple process successfully."""
    pm = ProcessManager()
    
    # Run a simple echo command
    result = await pm.run_process(
        run_id="test_run_1",
        command=["echo", "Hello, World!"]
    )
    
    assert isinstance(result, ProcessResult)
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout
    assert result.error is None


@pytest.mark.asyncio
async def test_run_process_with_error():
    """Test running a process that fails."""
    pm = ProcessManager()
    
    # Run a command that doesn't exist
    result = await pm.run_process(
        run_id="test_run_2",
        command=["nonexistent_command_xyz"]
    )
    
    assert result.exit_code == -1
    assert result.error is not None


@pytest.mark.asyncio
async def test_run_process_captures_logs():
    """Test that process output is captured in log buffers."""
    pm = ProcessManager()
    
    # Run a command that produces output
    await pm.run_process(
        run_id="test_run_3",
        command=["echo", "test output"]
    )
    
    # Check logs were captured
    logs = pm.get_logs("test_run_3")
    assert len(logs) > 0
    assert logs[0]["stream"] == "stdout"
    assert "test output" in logs[0]["message"]
    assert "timestamp" in logs[0]


@pytest.mark.asyncio
async def test_get_logs_with_tail():
    """Test getting logs with tail limit."""
    pm = ProcessManager()
    
    # Manually add some log entries
    pm.log_buffers["test_run_4"] = [
        {"timestamp": "2025-01-01T00:00:00", "stream": "stdout", "message": f"Line {i}"}
        for i in range(10)
    ]
    
    # Get last 3 lines
    logs = pm.get_logs("test_run_4", tail=3)
    assert len(logs) == 3
    assert logs[-1]["message"] == "Line 9"
    assert logs[0]["message"] == "Line 7"


@pytest.mark.asyncio
async def test_get_logs_nonexistent_run():
    """Test getting logs for non-existent run."""
    pm = ProcessManager()
    logs = pm.get_logs("nonexistent_run")
    assert logs == []


@pytest.mark.asyncio
async def test_cancel_process():
    """Test cancelling a running process."""
    pm = ProcessManager()
    
    # Start a long-running process
    async def start_long_process():
        return await pm.run_process(
            run_id="test_run_5",
            command=["sleep", "10"]
        )
    
    # Start the process
    task = asyncio.create_task(start_long_process())
    
    # Give it time to start
    await asyncio.sleep(0.2)
    
    # Cancel it
    success = await pm.cancel_process("test_run_5")
    assert success is True
    
    # Wait for the task to complete
    result = await task
    # Process should have been killed, exit code will be non-zero
    assert result.exit_code != 0 or result.error is not None
    
    # Clean up
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_cancel_nonexistent_process():
    """Test cancelling a non-existent process."""
    pm = ProcessManager()
    success = await pm.cancel_process("nonexistent")
    assert success is False


@pytest.mark.asyncio
async def test_run_process_with_cwd():
    """Test running a process with a specific working directory."""
    pm = ProcessManager()
    
    # Run pwd command to check working directory
    result = await pm.run_process(
        run_id="test_run_6",
        command=["pwd"],
        cwd=Path("/tmp")
    )
    
    assert result.exit_code == 0
    assert "/tmp" in result.stdout


@pytest.mark.asyncio
async def test_concurrent_processes():
    """Test running multiple processes concurrently."""
    pm = ProcessManager()
    
    # Start multiple processes
    tasks = [
        pm.run_process(
            run_id=f"test_run_concurrent_{i}",
            command=["echo", f"Process {i}"]
        )
        for i in range(5)
    ]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    # All should succeed
    assert len(results) == 5
    for i, result in enumerate(results):
        assert result.exit_code == 0
        assert f"Process {i}" in result.stdout
    
    # Check logs for all runs
    for i in range(5):
        logs = pm.get_logs(f"test_run_concurrent_{i}")
        assert len(logs) > 0
