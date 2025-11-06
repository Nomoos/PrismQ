"""Unit tests for BackgroundTaskManager."""

import asyncio
import pytest
from pathlib import Path
from datetime import datetime, timezone
import tempfile

from src.core.task_manager import BackgroundTaskManager
from src.core.run_registry import RunRegistry
from src.models.run import Run, RunStatus


@pytest.fixture
def registry():
    """Create a temporary RunRegistry for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = Path(f.name)
    
    try:
        reg = RunRegistry(history_file=history_file)
        yield reg
    finally:
        if history_file.exists():
            history_file.unlink()


@pytest.fixture
def task_manager(registry):
    """Create a BackgroundTaskManager instance."""
    return BackgroundTaskManager(registry)


@pytest.fixture
def sample_run():
    """Create a sample Run object for testing."""
    return Run(
        run_id="test_run_1",
        module_id="test_module",
        module_name="Test Module",
        status=RunStatus.QUEUED,
        created_at=datetime.now(timezone.utc),
        parameters={}
    )


class TestBackgroundTaskManagerInitialization:
    """Test BackgroundTaskManager initialization."""
    
    def test_initialization(self, registry):
        """Test that BackgroundTaskManager initializes correctly."""
        manager = BackgroundTaskManager(registry)
        assert manager.registry is registry
        assert isinstance(manager.tasks, dict)
        assert len(manager.tasks) == 0
    
    def test_initial_state(self, task_manager):
        """Test initial state of task manager."""
        assert task_manager.get_active_task_count() == 0
        assert task_manager.get_active_task_ids() == []


class TestTaskExecution:
    """Test task execution functionality."""
    
    @pytest.mark.asyncio
    async def test_start_task_simple(self, task_manager, registry, sample_run):
        """Test starting a simple background task."""
        # Simple async function
        async def simple_task():
            await asyncio.sleep(0.1)
            return "completed"
        
        # Add run to registry
        registry.add_run(sample_run)
        
        # Start task
        task_id = task_manager.start_task(sample_run, simple_task())
        
        assert task_id == sample_run.run_id
        assert task_manager.get_active_task_count() == 1
        assert task_manager.is_task_active(sample_run.run_id)
        
        # Wait for task to complete
        await asyncio.sleep(0.2)
        
        # Task should be completed and removed from active tasks
        assert task_manager.get_active_task_count() == 0
        assert not task_manager.is_task_active(sample_run.run_id)
        
        # Check registry was updated
        updated_run = registry.get_run(sample_run.run_id)
        assert updated_run.status == RunStatus.COMPLETED
        assert updated_run.exit_code == 0
    
    @pytest.mark.asyncio
    async def test_task_failure_handling(self, task_manager, registry, sample_run):
        """Test that task failures are properly handled."""
        error_message = "Task failed intentionally"
        
        async def failing_task():
            await asyncio.sleep(0.05)
            raise ValueError(error_message)
        
        registry.add_run(sample_run)
        task_id = task_manager.start_task(sample_run, failing_task())
        
        # Wait for task to fail
        await asyncio.sleep(0.15)
        
        # Task should be removed from active tasks
        assert task_manager.get_active_task_count() == 0
        
        # Check registry shows failure
        updated_run = registry.get_run(sample_run.run_id)
        assert updated_run.status == RunStatus.FAILED
        assert error_message in updated_run.error_message
    
    @pytest.mark.asyncio
    async def test_immediate_failure(self, task_manager, registry, sample_run):
        """Test task that fails immediately."""
        async def immediate_fail():
            raise RuntimeError("Immediate failure")
        
        registry.add_run(sample_run)
        task_manager.start_task(sample_run, immediate_fail())
        
        # Give task time to fail
        await asyncio.sleep(0.1)
        
        updated_run = registry.get_run(sample_run.run_id)
        assert updated_run.status == RunStatus.FAILED
        assert "Immediate failure" in updated_run.error_message
    
    @pytest.mark.asyncio
    async def test_status_transitions(self, task_manager, registry, sample_run):
        """Test that status transitions happen correctly."""
        status_history = []
        
        async def monitored_task():
            # Check status during execution
            await asyncio.sleep(0.05)
            run = registry.get_run(sample_run.run_id)
            status_history.append(run.status)
            await asyncio.sleep(0.05)
        
        registry.add_run(sample_run)
        initial_status = registry.get_run(sample_run.run_id).status
        
        task_manager.start_task(sample_run, monitored_task())
        
        # Wait for completion
        await asyncio.sleep(0.2)
        
        final_status = registry.get_run(sample_run.run_id).status
        
        # Verify status progression: QUEUED -> RUNNING -> COMPLETED
        assert initial_status == RunStatus.QUEUED
        assert RunStatus.RUNNING in status_history
        assert final_status == RunStatus.COMPLETED


class TestTaskCancellation:
    """Test task cancellation functionality."""
    
    @pytest.mark.asyncio
    async def test_cancel_running_task(self, task_manager, registry, sample_run):
        """Test cancelling a running task."""
        async def long_running_task():
            await asyncio.sleep(10)  # Long task
            return "completed"
        
        registry.add_run(sample_run)
        task_id = task_manager.start_task(sample_run, long_running_task())
        
        # Give task time to start
        await asyncio.sleep(0.05)
        
        # Cancel the task
        result = await task_manager.cancel_task(task_id)
        
        assert result is True
        assert task_manager.get_active_task_count() == 0
        
        # Check registry shows cancellation
        updated_run = registry.get_run(sample_run.run_id)
        assert updated_run.status == RunStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self, task_manager):
        """Test cancelling a task that doesn't exist."""
        result = await task_manager.cancel_task("nonexistent_task")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cancel_completed_task(self, task_manager, registry, sample_run):
        """Test cancelling a task that has already completed."""
        async def quick_task():
            await asyncio.sleep(0.05)
            return "done"
        
        registry.add_run(sample_run)
        task_id = task_manager.start_task(sample_run, quick_task())
        
        # Wait for task to complete
        await asyncio.sleep(0.15)
        
        # Try to cancel completed task
        result = await task_manager.cancel_task(task_id)
        
        assert result is False
        
        # Status should remain COMPLETED
        updated_run = registry.get_run(sample_run.run_id)
        assert updated_run.status == RunStatus.COMPLETED


class TestMultipleTasks:
    """Test managing multiple concurrent tasks."""
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_tasks(self, task_manager, registry):
        """Test running multiple tasks concurrently."""
        task_count = 5
        runs = []
        
        for i in range(task_count):
            run = Run(
                run_id=f"task_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=RunStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            registry.add_run(run)
            runs.append(run)
        
        async def numbered_task(num):
            await asyncio.sleep(0.1)
            return f"Task {num} completed"
        
        # Start all tasks
        for i, run in enumerate(runs):
            task_manager.start_task(run, numbered_task(i))
        
        # All tasks should be active
        assert task_manager.get_active_task_count() == task_count
        
        # Wait for all to complete
        await asyncio.sleep(0.3)
        
        # All tasks should be completed
        assert task_manager.get_active_task_count() == 0
        
        # Check all runs completed successfully
        for run in runs:
            updated_run = registry.get_run(run.run_id)
            assert updated_run.status == RunStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_mixed_success_and_failure(self, task_manager, registry):
        """Test handling mixed successful and failed tasks."""
        async def success_task():
            await asyncio.sleep(0.05)
            return "success"
        
        async def fail_task():
            await asyncio.sleep(0.05)
            raise ValueError("Task failed")
        
        # Create runs
        success_run = Run(
            run_id="success_task",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        fail_run = Run(
            run_id="fail_task",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        registry.add_run(success_run)
        registry.add_run(fail_run)
        
        # Start both tasks
        task_manager.start_task(success_run, success_task())
        task_manager.start_task(fail_run, fail_task())
        
        assert task_manager.get_active_task_count() == 2
        
        # Wait for completion
        await asyncio.sleep(0.2)
        
        # Both should be done
        assert task_manager.get_active_task_count() == 0
        
        # Check statuses
        assert registry.get_run("success_task").status == RunStatus.COMPLETED
        assert registry.get_run("fail_task").status == RunStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_get_active_task_ids(self, task_manager, registry):
        """Test getting list of active task IDs."""
        runs = []
        for i in range(3):
            run = Run(
                run_id=f"task_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=RunStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            registry.add_run(run)
            runs.append(run)
        
        async def slow_task():
            await asyncio.sleep(1)
        
        # Start tasks
        for run in runs:
            task_manager.start_task(run, slow_task())
        
        # Get active task IDs
        active_ids = task_manager.get_active_task_ids()
        
        assert len(active_ids) == 3
        assert "task_0" in active_ids
        assert "task_1" in active_ids
        assert "task_2" in active_ids
        
        # Cancel all tasks
        for task_id in active_ids:
            await task_manager.cancel_task(task_id)


class TestWaitAll:
    """Test wait_all functionality."""
    
    @pytest.mark.asyncio
    async def test_wait_all_empty(self, task_manager):
        """Test wait_all with no active tasks."""
        await task_manager.wait_all()  # Should return immediately
    
    @pytest.mark.asyncio
    async def test_wait_all_with_tasks(self, task_manager, registry):
        """Test wait_all waits for all tasks to complete."""
        completed_tasks = []
        
        async def task_with_id(task_id):
            await asyncio.sleep(0.1)
            completed_tasks.append(task_id)
        
        # Create multiple runs
        for i in range(3):
            run = Run(
                run_id=f"task_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=RunStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            registry.add_run(run)
            task_manager.start_task(run, task_with_id(i))
        
        # Wait for all
        await task_manager.wait_all()
        
        # All tasks should be completed
        assert len(completed_tasks) == 3
        assert task_manager.get_active_task_count() == 0
    
    @pytest.mark.asyncio
    async def test_wait_all_with_failures(self, task_manager, registry):
        """Test wait_all handles failures gracefully."""
        async def success_task():
            await asyncio.sleep(0.05)
        
        async def fail_task():
            await asyncio.sleep(0.05)
            raise ValueError("Task failed")
        
        # Create runs
        success_run = Run(
            run_id="success",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        fail_run = Run(
            run_id="fail",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        registry.add_run(success_run)
        registry.add_run(fail_run)
        
        task_manager.start_task(success_run, success_task())
        task_manager.start_task(fail_run, fail_task())
        
        # wait_all should not raise exception even with failures
        await task_manager.wait_all()
        
        assert task_manager.get_active_task_count() == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_task_with_no_await(self, task_manager, registry, sample_run):
        """Test task that completes synchronously."""
        async def immediate_task():
            return "done"
        
        registry.add_run(sample_run)
        task_manager.start_task(sample_run, immediate_task())
        
        # Give it a moment to complete
        await asyncio.sleep(0.05)
        
        updated_run = registry.get_run(sample_run.run_id)
        assert updated_run.status == RunStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_reusing_run_id(self, task_manager, registry):
        """Test that reusing a run ID replaces the previous entry."""
        async def quick_task():
            await asyncio.sleep(0.05)
        
        run1 = Run(
            run_id="reused_id",
            module_id="module1",
            module_name="Module 1",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        registry.add_run(run1)
        task_manager.start_task(run1, quick_task())
        
        # Wait for first task
        await asyncio.sleep(0.1)
        
        # Start another task with same ID
        run2 = Run(
            run_id="reused_id",
            module_id="module2",
            module_name="Module 2",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        registry.update_run(run2)
        task_manager.start_task(run2, quick_task())
        
        # Wait for second task
        await asyncio.sleep(0.1)
        
        # Should have the second run's data
        final_run = registry.get_run("reused_id")
        assert final_run.module_id == "module2"
    
    @pytest.mark.asyncio
    async def test_exception_in_exception_handler(self, task_manager, registry, sample_run):
        """Test that exceptions during failure handling don't crash."""
        # This is a pathological case, but we should handle it gracefully
        async def bad_task():
            raise ValueError("Original error")
        
        registry.add_run(sample_run)
        task_manager.start_task(sample_run, bad_task())
        
        # Should complete without crashing
        await asyncio.sleep(0.1)
        
        # Task should still be marked as failed
        updated_run = registry.get_run(sample_run.run_id)
        assert updated_run.status == RunStatus.FAILED


class TestIntegrationWithRunRegistry:
    """Test integration between BackgroundTaskManager and RunRegistry."""
    
    @pytest.mark.asyncio
    async def test_registry_persistence(self, registry):
        """Test that task status updates persist in registry."""
        task_manager = BackgroundTaskManager(registry)
        
        async def persisted_task():
            await asyncio.sleep(0.05)
        
        run = Run(
            run_id="persist_test",
            module_id="test_module",
            module_name="Test Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={"test": "value"}
        )
        
        registry.add_run(run)
        task_manager.start_task(run, persisted_task())
        
        # Wait for completion
        await asyncio.sleep(0.15)
        
        # Verify registry has updated data
        persisted_run = registry.get_run("persist_test")
        assert persisted_run.status == RunStatus.COMPLETED
        assert persisted_run.parameters["test"] == "value"
    
    @pytest.mark.asyncio
    async def test_query_active_runs_during_execution(self, task_manager, registry):
        """Test querying active runs while tasks are executing."""
        async def slow_task():
            await asyncio.sleep(0.2)
        
        # Start multiple tasks
        for i in range(3):
            run = Run(
                run_id=f"active_task_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=RunStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            registry.add_run(run)
            task_manager.start_task(run, slow_task())
        
        # Give tasks time to start
        await asyncio.sleep(0.05)
        
        # Query active runs from registry
        active_runs = registry.get_active_runs()
        
        # All should be RUNNING
        assert len(active_runs) == 3
        assert all(run.status == RunStatus.RUNNING for run in active_runs)
        
        # Wait for completion
        await task_manager.wait_all()
        
        # No more active runs
        active_runs = registry.get_active_runs()
        assert len(active_runs) == 0
