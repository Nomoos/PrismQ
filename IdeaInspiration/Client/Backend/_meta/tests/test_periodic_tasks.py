"""Tests for periodic background tasks."""

import asyncio
import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.periodic_tasks import PeriodicTask, PeriodicTaskManager


class TestPeriodicTask:
    """Test suite for PeriodicTask class."""
    
    @pytest.mark.asyncio
    async def test_periodic_task_creation(self):
        """Test creating a periodic task."""
        async def dummy_task():
            pass
        
        task = PeriodicTask(
            name="test_task",
            interval=timedelta(seconds=1),
            task_func=dummy_task
        )
        
        assert task.name == "test_task"
        assert task.interval == timedelta(seconds=1)
        assert task.is_running is False
        assert task._run_count == 0
        assert task._error_count == 0
    
    @pytest.mark.asyncio
    async def test_periodic_task_start_stop(self):
        """Test starting and stopping a periodic task."""
        call_count = 0
        
        async def counting_task():
            nonlocal call_count
            call_count += 1
        
        task = PeriodicTask(
            name="counting_task",
            interval=timedelta(milliseconds=100),
            task_func=counting_task
        )
        
        # Start the task
        task.start()
        assert task.is_running is True
        
        # Let it run a few times
        await asyncio.sleep(0.35)
        
        # Stop the task
        await task.stop()
        assert task.is_running is False
        
        # Task should have run at least 2-3 times
        assert call_count >= 2
        assert task._run_count >= 2
    
    @pytest.mark.asyncio
    async def test_periodic_task_with_arguments(self):
        """Test periodic task with positional and keyword arguments."""
        result = []
        
        async def task_with_args(a, b, c=None):
            result.append((a, b, c))
        
        task = PeriodicTask(
            "task_with_args",
            timedelta(milliseconds=100),
            task_with_args,
            1, 2, c=3
        )
        
        task.start()
        await asyncio.sleep(0.25)
        await task.stop()
        
        # Should have been called at least twice
        assert len(result) >= 2
        # Check arguments were passed correctly
        assert all(r == (1, 2, 3) for r in result)
    
    @pytest.mark.asyncio
    async def test_periodic_task_error_handling(self):
        """Test that errors in task don't stop the scheduler."""
        call_count = 0
        
        async def failing_task():
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                raise ValueError("Test error")
        
        task = PeriodicTask(
            name="failing_task",
            interval=timedelta(milliseconds=100),
            task_func=failing_task
        )
        
        task.start()
        await asyncio.sleep(0.45)
        await task.stop()
        
        # Task should have run multiple times despite errors
        assert call_count >= 3
        assert task._run_count >= 3
        # Should have recorded errors
        assert task._error_count >= 1
    
    @pytest.mark.asyncio
    async def test_periodic_task_already_running(self):
        """Test starting a task that's already running."""
        async def dummy_task():
            await asyncio.sleep(0.01)
        
        task = PeriodicTask(
            name="test_task",
            interval=timedelta(seconds=1),
            task_func=dummy_task
        )
        
        task.start()
        assert task.is_running is True
        
        # Try starting again - should log warning but not crash
        task.start()
        assert task.is_running is True
        
        await task.stop()
    
    @pytest.mark.asyncio
    async def test_periodic_task_stop_not_running(self):
        """Test stopping a task that's not running."""
        async def dummy_task():
            pass
        
        task = PeriodicTask(
            name="test_task",
            interval=timedelta(seconds=1),
            task_func=dummy_task
        )
        
        # Should not raise error when stopping a non-running task
        await task.stop()
    
    @pytest.mark.asyncio
    async def test_periodic_task_graceful_shutdown(self):
        """Test graceful shutdown waits for current execution."""
        execution_started = asyncio.Event()
        execution_can_finish = asyncio.Event()
        
        async def long_running_task():
            execution_started.set()
            await execution_can_finish.wait()
        
        task = PeriodicTask(
            name="long_task",
            interval=timedelta(seconds=10),  # Long interval
            task_func=long_running_task
        )
        
        task.start()
        
        # Wait for first execution to start
        await asyncio.wait_for(execution_started.wait(), timeout=1.0)
        
        # Stop the task (should wait for current execution)
        stop_task = asyncio.create_task(task.stop(timeout=2.0))
        
        # Give it a moment to try stopping
        await asyncio.sleep(0.1)
        
        # Task should still be running (waiting for execution to finish)
        assert not stop_task.done()
        
        # Allow execution to finish
        execution_can_finish.set()
        
        # Now stop should complete
        await asyncio.wait_for(stop_task, timeout=2.0)
        assert task.is_running is False
    
    @pytest.mark.asyncio
    async def test_periodic_task_forced_cancellation(self):
        """Test that task is cancelled if it doesn't stop gracefully."""
        async def never_ending_task():
            while True:
                await asyncio.sleep(0.1)
        
        task = PeriodicTask(
            name="never_ending",
            interval=timedelta(seconds=10),
            task_func=never_ending_task
        )
        
        task.start()
        await asyncio.sleep(0.2)
        
        # Stop with very short timeout - should force cancellation
        await task.stop(timeout=0.1)
        
        assert task.is_running is False
    
    @pytest.mark.asyncio
    async def test_periodic_task_statistics(self):
        """Test task statistics collection."""
        call_count = 0
        
        async def counting_task():
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise ValueError("Test error")
        
        task = PeriodicTask(
            name="stats_task",
            interval=timedelta(milliseconds=100),
            task_func=counting_task
        )
        
        # Initial statistics
        stats = task.statistics
        assert stats["name"] == "stats_task"
        assert stats["is_running"] is False
        assert stats["run_count"] == 0
        assert stats["error_count"] == 0
        assert stats["last_run"] is None
        
        # Run the task
        task.start()
        await asyncio.sleep(0.35)
        await task.stop()
        
        # Updated statistics
        stats = task.statistics
        assert stats["is_running"] is False
        assert stats["run_count"] >= 3
        assert stats["error_count"] >= 1
        assert stats["last_run"] is not None


class TestPeriodicTaskManager:
    """Test suite for PeriodicTaskManager class."""
    
    @pytest.mark.asyncio
    async def test_manager_creation(self):
        """Test creating a task manager."""
        manager = PeriodicTaskManager()
        assert manager._tasks == {}
    
    @pytest.mark.asyncio
    async def test_register_task(self):
        """Test registering a periodic task."""
        manager = PeriodicTaskManager()
        
        async def dummy_task():
            pass
        
        task = manager.register_task(
            name="test_task",
            interval=timedelta(seconds=1),
            task_func=dummy_task
        )
        
        assert task is not None
        assert task.name == "test_task"
        assert manager.get_task("test_task") is task
    
    @pytest.mark.asyncio
    async def test_register_duplicate_task(self):
        """Test that registering duplicate task name raises error."""
        manager = PeriodicTaskManager()
        
        async def dummy_task():
            pass
        
        manager.register_task(
            name="test_task",
            interval=timedelta(seconds=1),
            task_func=dummy_task
        )
        
        # Should raise ValueError for duplicate name
        with pytest.raises(ValueError, match="already registered"):
            manager.register_task(
                name="test_task",
                interval=timedelta(seconds=1),
                task_func=dummy_task
            )
    
    @pytest.mark.asyncio
    async def test_get_task(self):
        """Test getting a task by name."""
        manager = PeriodicTaskManager()
        
        async def dummy_task():
            pass
        
        task = manager.register_task(
            name="test_task",
            interval=timedelta(seconds=1),
            task_func=dummy_task
        )
        
        # Get existing task
        retrieved = manager.get_task("test_task")
        assert retrieved is task
        
        # Get non-existent task
        assert manager.get_task("nonexistent") is None
    
    @pytest.mark.asyncio
    async def test_start_all(self):
        """Test starting all registered tasks."""
        manager = PeriodicTaskManager()
        call_counts = {"task1": 0, "task2": 0}
        
        async def task1():
            call_counts["task1"] += 1
        
        async def task2():
            call_counts["task2"] += 1
        
        manager.register_task(
            name="task1",
            interval=timedelta(milliseconds=100),
            task_func=task1
        )
        manager.register_task(
            name="task2",
            interval=timedelta(milliseconds=100),
            task_func=task2
        )
        
        # Start all tasks
        manager.start_all()
        
        # Both should be running
        assert manager.get_task("task1").is_running is True
        assert manager.get_task("task2").is_running is True
        
        # Let them run a bit
        await asyncio.sleep(0.35)
        
        # Both should have executed
        assert call_counts["task1"] >= 2
        assert call_counts["task2"] >= 2
        
        # Stop all
        await manager.stop_all()
    
    @pytest.mark.asyncio
    async def test_stop_all(self):
        """Test stopping all registered tasks."""
        manager = PeriodicTaskManager()
        
        async def dummy_task():
            await asyncio.sleep(0.01)
        
        # Register multiple tasks
        for i in range(3):
            manager.register_task(
                name=f"task{i}",
                interval=timedelta(milliseconds=100),
                task_func=dummy_task
            )
        
        # Start all
        manager.start_all()
        
        # All should be running
        for i in range(3):
            assert manager.get_task(f"task{i}").is_running is True
        
        # Stop all
        await manager.stop_all()
        
        # All should be stopped
        for i in range(3):
            assert manager.get_task(f"task{i}").is_running is False
    
    @pytest.mark.asyncio
    async def test_get_all_statistics(self):
        """Test getting statistics for all tasks."""
        manager = PeriodicTaskManager()
        
        async def dummy_task():
            pass
        
        # Register tasks
        manager.register_task(
            name="task1",
            interval=timedelta(seconds=1),
            task_func=dummy_task
        )
        manager.register_task(
            name="task2",
            interval=timedelta(seconds=2),
            task_func=dummy_task
        )
        
        # Get statistics
        all_stats = manager.get_all_statistics()
        
        assert len(all_stats) == 2
        assert all_stats[0]["name"] in ["task1", "task2"]
        assert all_stats[1]["name"] in ["task1", "task2"]
        assert all_stats[0]["name"] != all_stats[1]["name"]
    
    @pytest.mark.asyncio
    async def test_register_task_with_args_kwargs(self):
        """Test registering task with arguments."""
        manager = PeriodicTaskManager()
        result = []
        
        async def task_with_args(a, b, c=None):
            result.append((a, b, c))
        
        manager.register_task(
            "task_with_args",
            timedelta(milliseconds=100),
            task_with_args,
            1, 2, c=3
        )
        
        manager.start_all()
        await asyncio.sleep(0.25)
        await manager.stop_all()
        
        # Should have been called at least twice
        assert len(result) >= 2
        # Check arguments were passed correctly
        assert all(r == (1, 2, 3) for r in result)
