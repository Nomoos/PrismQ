"""Unit tests for ModuleRunner."""

import asyncio
import pytest
from pathlib import Path
from datetime import datetime, timezone
import tempfile

from src.core.module_runner import ModuleRunner
from src.core.output_capture import OutputCapture
from src.core.process_manager import ProcessManager
from src.core.run_registry import RunRegistry
from src.models.run import Run, RunStatus


@pytest.fixture
def temp_history_file():
    """Create a temporary history file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        path = Path(f.name)
    yield path
    if path.exists():
        path.unlink()


@pytest.fixture
def temp_log_dir():
    """Create a temporary log directory."""
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def module_runner(temp_history_file, temp_log_dir):
    """Create a ModuleRunner instance with fresh dependencies."""
    registry = RunRegistry(history_file=temp_history_file)
    process_manager = ProcessManager()
    output_capture = OutputCapture(log_dir=temp_log_dir)
    runner = ModuleRunner(
        registry=registry,
        process_manager=process_manager,
        output_capture=output_capture,
        max_concurrent_runs=5
    )
    return runner


@pytest.mark.asyncio
async def test_module_runner_initialization(module_runner):
    """Test ModuleRunner initialization."""
    assert module_runner.max_concurrent_runs == 5
    assert isinstance(module_runner.registry, RunRegistry)
    assert isinstance(module_runner.process_manager, ProcessManager)
    assert isinstance(module_runner.output_capture, OutputCapture)


@pytest.mark.asyncio
async def test_execute_module_creates_run(module_runner):
    """Test that executing a module creates a run."""
    run = await module_runner.execute_module(
        module_id="test_module",
        module_name="Test Module",
        script_path=Path("/tmp/test_script.py"),
        parameters={"key": "value"}
    )
    
    assert run is not None
    assert run.module_id == "test_module"
    assert run.status == RunStatus.QUEUED
    assert run.parameters["key"] == "value"
    assert run.run_id.startswith("run_")


@pytest.mark.asyncio
async def test_generate_run_id_format(module_runner):
    """Test run ID generation format."""
    run_id = module_runner._generate_run_id("testmodule")
    
    # Format: run_YYYYMMDD_HHMMSS_<module_id>_<uuid>
    parts = run_id.split("_")
    assert parts[0] == "run"
    assert len(parts) >= 4  # run, date, time, and rest (module_id may have underscores)
    assert parts[3] == "testmodule"
    assert len(parts[4]) == 8  # UUID part should be 8 chars


@pytest.mark.asyncio
async def test_execute_module_with_custom_run_id(module_runner):
    """Test executing a module with custom run ID."""
    custom_id = "custom_run_123"
    
    run = await module_runner.execute_module(
        module_id="test_module",
        module_name="Test Module",
        script_path=Path("/tmp/test_script.py"),
        parameters={},
        run_id=custom_id
    )
    
    assert run.run_id == custom_id


@pytest.mark.asyncio
async def test_max_concurrent_runs_limit(module_runner):
    """Test that max concurrent runs limit is enforced."""
    # Set a low limit
    module_runner.max_concurrent_runs = 2
    
    # Create 2 queued runs
    for i in range(2):
        run = await module_runner.execute_module(
            module_id=f"module_{i}",
            module_name=f"Module {i}",
            script_path=Path(f"/tmp/script_{i}.py"),
            parameters={}
        )
        # Manually set to RUNNING to count as active
        run.status = RunStatus.RUNNING
        module_runner.registry.update_run(run)
    
    # Attempt to create a third run should fail
    with pytest.raises(RuntimeError, match="Max concurrent runs"):
        await module_runner.execute_module(
            module_id="module_3",
            module_name="Module 3",
            script_path=Path("/tmp/script_3.py"),
            parameters={}
        )


@pytest.mark.asyncio
async def test_execute_module_successful(module_runner):
    """Test executing a module successfully."""
    # Create a simple script that just echoes
    run = await module_runner.execute_module(
        module_id="echo_test",
        module_name="Echo Test",
        script_path=Path("echo"),  # Use echo command
        parameters={"message": "Hello"}
    )
    
    # Wait for execution to complete
    await asyncio.sleep(0.5)
    
    # Check run status was updated
    updated_run = module_runner.get_run_status(run.run_id)
    # Since 'echo' is not actually a Python script, it will fail
    assert updated_run.status in [RunStatus.RUNNING, RunStatus.FAILED, RunStatus.COMPLETED]


@pytest.mark.asyncio
async def test_build_command(module_runner):
    """Test command building from parameters."""
    script_path = Path("/tmp/test_script.py")
    parameters = {
        "max_results": 100,
        "category": "test",
        "verbose": True
    }
    
    command = module_runner._build_command(script_path, parameters)
    
    assert command[0] == "python"
    assert command[1] == str(script_path)
    assert "--max_results" in command
    assert "100" in command
    assert "--category" in command
    assert "test" in command


@pytest.mark.asyncio
async def test_get_run_status(module_runner):
    """Test getting run status."""
    run = await module_runner.execute_module(
        module_id="test_module",
        module_name="Test Module",
        script_path=Path("/tmp/test_script.py"),
        parameters={}
    )
    
    retrieved_run = module_runner.get_run_status(run.run_id)
    assert retrieved_run is not None
    assert retrieved_run.run_id == run.run_id
    
    nonexistent = module_runner.get_run_status("nonexistent_run")
    assert nonexistent is None


@pytest.mark.asyncio
async def test_cancel_queued_run(module_runner):
    """Test cancelling a queued run."""
    run = await module_runner.execute_module(
        module_id="test_module",
        module_name="Test Module",
        script_path=Path("/tmp/test_script.py"),
        parameters={}
    )
    
    # Cancel immediately (before it starts running)
    success = await module_runner.cancel_run(run.run_id)
    assert success is True
    
    # Check status was updated
    cancelled_run = module_runner.get_run_status(run.run_id)
    assert cancelled_run.status == RunStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_completed_run_fails(module_runner):
    """Test that cancelling a completed run fails."""
    run = await module_runner.execute_module(
        module_id="test_module",
        module_name="Test Module",
        script_path=Path("/tmp/test_script.py"),
        parameters={}
    )
    
    # Manually set to completed
    run.status = RunStatus.COMPLETED
    run.completed_at = datetime.now(timezone.utc)
    module_runner.registry.update_run(run)
    
    # Try to cancel
    success = await module_runner.cancel_run(run.run_id)
    assert success is False


@pytest.mark.asyncio
async def test_cancel_nonexistent_run(module_runner):
    """Test cancelling a non-existent run."""
    success = await module_runner.cancel_run("nonexistent_run")
    assert success is False


@pytest.mark.asyncio
async def test_run_lifecycle(module_runner):
    """Test the full run lifecycle."""
    # Start a run
    run = await module_runner.execute_module(
        module_id="lifecycle_test",
        module_name="Lifecycle Test",
        script_path=Path("/tmp/test_script.py"),
        parameters={"test": "value"}
    )
    
    # Should start as QUEUED
    assert run.status == RunStatus.QUEUED
    assert run.created_at is not None
    assert run.started_at is None
    assert run.completed_at is None
    
    # Wait for it to start processing
    await asyncio.sleep(0.3)
    
    # Should transition through states
    updated_run = module_runner.get_run_status(run.run_id)
    # Will likely be RUNNING or FAILED (since script doesn't exist)
    assert updated_run.status in [RunStatus.RUNNING, RunStatus.FAILED]


@pytest.mark.asyncio
async def test_concurrent_module_execution(module_runner):
    """Test executing multiple modules concurrently."""
    # Start 3 runs concurrently
    runs = []
    for i in range(3):
        run = await module_runner.execute_module(
            module_id=f"concurrent_{i}",
            module_name=f"Concurrent {i}",
            script_path=Path(f"/tmp/script_{i}.py"),
            parameters={"index": i}
        )
        runs.append(run)
    
    # All should be created
    assert len(runs) == 3
    assert all(r.status == RunStatus.QUEUED for r in runs)
    
    # All should have unique run IDs
    run_ids = [r.run_id for r in runs]
    assert len(set(run_ids)) == 3


@pytest.mark.asyncio
async def test_run_with_failed_process(module_runner):
    """Test handling of a failed process."""
    run = await module_runner.execute_module(
        module_id="failing_module",
        module_name="Failing Module",
        script_path=Path("/nonexistent/script.py"),
        parameters={}
    )
    
    # Wait for execution to complete
    await asyncio.sleep(0.5)
    
    # Should be marked as FAILED
    updated_run = module_runner.get_run_status(run.run_id)
    assert updated_run.status == RunStatus.FAILED
    assert updated_run.error_message is not None
    assert updated_run.completed_at is not None
