"""Integration tests for concurrent run management."""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.core.module_runner import ModuleRunner
from src.core.output_capture import OutputCapture
from src.core.process_manager import ProcessManager
from src.core.resource_manager import ResourceManager
from src.core.run_registry import RunRegistry
from src.core.exceptions import ResourceLimitException
from src.models.run import RunStatus


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
def module_runner_with_resources(temp_history_file, temp_log_dir):
    """Create a ModuleRunner instance with ResourceManager."""
    registry = RunRegistry(history_file=temp_history_file)
    process_manager = ProcessManager()
    output_capture = OutputCapture(log_dir=temp_log_dir)
    resource_manager = ResourceManager(cpu_threshold_percent=80.0, memory_required_gb=1.0)
    runner = ModuleRunner(
        registry=registry,
        process_manager=process_manager,
        output_capture=output_capture,
        resource_manager=resource_manager,
        max_concurrent_runs=5
    )
    return runner


@pytest.mark.asyncio
async def test_module_runner_checks_resources_before_run(module_runner_with_resources):
    """Test that ModuleRunner checks resources before allowing a run."""
    runner = module_runner_with_resources
    
    # Mock resource manager to reject runs
    with patch.object(runner.resource_manager, 'check_resources_available', return_value=(False, "CPU too high")):
        # Attempt to execute module - should fail due to resource constraints
        with pytest.raises(ResourceLimitException, match="Insufficient system resources"):
            await runner.execute_module(
                module_id="test_module",
                module_name="Test Module",
                script_path=Path("/tmp/test_script.py"),
                parameters={"key": "value"}
            )


@pytest.mark.asyncio
async def test_module_runner_allows_run_when_resources_available(module_runner_with_resources):
    """Test that ModuleRunner allows run when resources are available."""
    runner = module_runner_with_resources
    
    # Mock resource manager to accept runs
    with patch.object(runner.resource_manager, 'check_resources_available', return_value=(True, None)):
        # Execute module - should succeed
        run = await runner.execute_module(
            module_id="test_module",
            module_name="Test Module",
            script_path=Path("/tmp/test_script.py"),
            parameters={"key": "value"}
        )
        
        assert run is not None
        assert run.status == RunStatus.QUEUED
        assert run.module_id == "test_module"


@pytest.mark.asyncio
async def test_concurrent_runs_respect_max_limit(module_runner_with_resources):
    """Test that concurrent runs respect the max_concurrent_runs limit."""
    runner = module_runner_with_resources
    runner.max_concurrent_runs = 3
    
    # Mock resource manager to always allow
    with patch.object(runner.resource_manager, 'check_resources_available', return_value=(True, None)):
        # Create 3 runs - should all succeed
        runs = []
        for i in range(3):
            run = await runner.execute_module(
                module_id=f"module_{i}",
                module_name=f"Module {i}",
                script_path=Path(f"/tmp/script_{i}.py"),
                parameters={}
            )
            runs.append(run)
        
        # All 3 should be active
        active = runner.registry.get_active_runs()
        assert len(active) == 3
        
        # 4th run should fail due to max limit
        with pytest.raises(ResourceLimitException, match="Max concurrent runs"):
            await runner.execute_module(
                module_id="module_4",
                module_name="Module 4",
                script_path=Path("/tmp/script_4.py"),
                parameters={}
            )


@pytest.mark.asyncio
async def test_concurrent_runs_with_resource_constraints(module_runner_with_resources):
    """Test concurrent runs with simulated resource constraints."""
    runner = module_runner_with_resources
    runner.max_concurrent_runs = 10
    
    # Simulate resource manager rejecting after 5 runs
    call_count = 0
    
    def mock_check_resources():
        nonlocal call_count
        call_count += 1
        if call_count <= 5:
            return (True, None)
        else:
            return (False, "System resources exhausted")
    
    with patch.object(runner.resource_manager, 'check_resources_available', side_effect=mock_check_resources):
        # Create 5 runs - should all succeed
        successful_runs = []
        for i in range(5):
            run = await runner.execute_module(
                module_id=f"module_{i}",
                module_name=f"Module {i}",
                script_path=Path(f"/tmp/script_{i}.py"),
                parameters={}
            )
            successful_runs.append(run)
        
        assert len(successful_runs) == 5
        
        # 6th run should fail due to resource constraints
        with pytest.raises(ResourceLimitException, match="Insufficient system resources"):
            await runner.execute_module(
                module_id="module_6",
                module_name="Module 6",
                script_path=Path("/tmp/script_6.py"),
                parameters={}
            )


@pytest.mark.asyncio
async def test_resource_manager_integration(temp_history_file, temp_log_dir):
    """Test that ResourceManager properly integrates with ModuleRunner."""
    # Create a runner with real ResourceManager
    registry = RunRegistry(history_file=temp_history_file)
    process_manager = ProcessManager()
    output_capture = OutputCapture(log_dir=temp_log_dir)
    resource_manager = ResourceManager(cpu_threshold_percent=95.0, memory_required_gb=0.1)
    
    runner = ModuleRunner(
        registry=registry,
        process_manager=process_manager,
        output_capture=output_capture,
        resource_manager=resource_manager,
        max_concurrent_runs=3
    )
    
    # Execute a module - should check resources
    run = await runner.execute_module(
        module_id="test_module",
        module_name="Test Module",
        script_path=Path("/tmp/test_script.py"),
        parameters={"test": "value"}
    )
    
    assert run is not None
    assert run.status == RunStatus.QUEUED
    
    # Verify resource manager was used (implicitly by not raising an exception)
    stats = resource_manager.get_system_stats()
    assert "cpu_percent" in stats
    assert "memory_available_gb" in stats
