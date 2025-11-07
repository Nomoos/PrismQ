"""
Integration tests for QueuedTaskManager adapter.

Tests backward compatibility and integration with the queue system.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from src.core.queued_task_manager import QueuedTaskManager
from src.core.run_registry import RunRegistry
from src.queue import QueueDatabase
from src.models.run import Run, RunStatus


@pytest.fixture
def queue_db():
    """Create a temporary QueueDatabase for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    try:
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        yield db
    finally:
        db.close()
        if db_path.exists():
            db_path.unlink()


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
def task_manager(queue_db, registry):
    """Create a QueuedTaskManager instance."""
    return QueuedTaskManager(queue_db, registry)


@pytest.fixture
def sample_run():
    """Create a sample Run object for testing."""
    return Run(
        run_id="test_run_1",
        module_id="test_module",
        module_name="Test Module",
        status=RunStatus.QUEUED,
        created_at=datetime.now(timezone.utc),
        parameters={"test_param": "test_value"}
    )


class TestQueuedTaskManagerInitialization:
    """Test QueuedTaskManager initialization."""
    
    def test_initialization(self, queue_db, registry):
        """Test that QueuedTaskManager initializes correctly."""
        manager = QueuedTaskManager(queue_db, registry)
        assert manager.queue is queue_db
        assert manager.registry is registry
        assert manager.handler_registry is not None
        assert isinstance(manager.tasks, dict)
        assert len(manager.tasks) == 0
    
    def test_initial_state(self, task_manager):
        """Test initial state of task manager."""
        assert task_manager.get_active_task_count() == 0
        assert task_manager.get_active_task_ids() == []


class TestBackwardCompatibility:
    """Test backward compatibility with BackgroundTaskManager interface."""
    
    def test_start_task_compatibility(self, task_manager, registry, sample_run):
        """Test that start_task works like BackgroundTaskManager."""
        # Register run in registry
        registry.add_run(sample_run)
        
        # Start task (coroutine is ignored, just for API compatibility)
        async def dummy_coro():
            await asyncio.sleep(0.1)
            return "done"
        
        task_id = task_manager.start_task(sample_run, dummy_coro())
        
        # Verify task was enqueued
        assert task_id == sample_run.run_id
        assert task_manager.get_active_task_count() == 1
        assert task_manager.is_task_active(sample_run.run_id)
        
        # Verify task is in queue database
        cursor = task_manager.queue.execute(
            "SELECT id, type, status, payload FROM task_queue WHERE idempotency_key = ?",
            (sample_run.run_id,)
        )
        row = cursor.fetchone()
        assert row is not None
        
        task_dict = dict(row)
        assert task_dict["type"] == sample_run.module_id
        assert task_dict["status"] == "queued"
    
    @pytest.mark.asyncio
    async def test_schedule_task_direct(self, task_manager):
        """Test direct task scheduling without Run object."""
        task_id = await task_manager.schedule_task(
            task_type="cleanup_runs",
            payload={"max_age_hours": 24},
            priority=50
        )
        
        # Verify task was created
        assert task_id is not None
        
        # Query from database
        cursor = task_manager.queue.execute(
            "SELECT id, type, status, payload, priority FROM task_queue WHERE id = ?",
            (int(task_id),)
        )
        row = cursor.fetchone()
        assert row is not None
        
        task_dict = dict(row)
        assert task_dict["type"] == "cleanup_runs"
        assert task_dict["status"] == "queued"
        assert task_dict["priority"] == 50
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, task_manager, registry, sample_run):
        """Test getting task status."""
        # Register and start task
        registry.add_run(sample_run)
        
        async def dummy_coro():
            pass
        
        run_id = task_manager.start_task(sample_run, dummy_coro())
        
        # Get status
        status = await task_manager.get_task_status(run_id)
        
        assert status["status"] == "queued"
        assert status["type"] == sample_run.module_id
        assert "task_id" in status
    
    @pytest.mark.asyncio
    async def test_cancel_task(self, task_manager, registry, sample_run):
        """Test cancelling a task."""
        # Register and start task
        registry.add_run(sample_run)
        
        async def dummy_coro():
            pass
        
        run_id = task_manager.start_task(sample_run, dummy_coro())
        
        # Cancel task
        success = await task_manager.cancel_task(run_id)
        assert success is True
        
        # Verify task is cancelled in queue
        status = await task_manager.get_task_status(run_id)
        assert status["status"] == "failed"
        assert status["error_message"] == "Cancelled by user"
        
        # Verify task removed from active tasks
        assert not task_manager.is_task_active(run_id)
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self, task_manager):
        """Test cancelling a task that doesn't exist."""
        success = await task_manager.cancel_task("nonexistent_task")
        assert success is False


class TestHandlerRegistration:
    """Test task handler registration."""
    
    @pytest.mark.asyncio
    async def test_register_handler(self, task_manager):
        """Test registering a task handler."""
        async def test_handler(task):
            return "processed"
        
        await task_manager.register_task(
            "test_task",
            test_handler,
            "Test task handler"
        )
        
        # Verify handler is registered
        handler = task_manager.handler_registry.get_handler("test_task")
        assert handler is not None
    
    @pytest.mark.asyncio
    async def test_register_multiple_handlers(self, task_manager):
        """Test registering multiple task handlers."""
        async def handler1(task):
            return "handler1"
        
        async def handler2(task):
            return "handler2"
        
        await task_manager.register_task("type1", handler1)
        await task_manager.register_task("type2", handler2)
        
        # Verify both handlers are registered
        h1 = task_manager.handler_registry.get_handler("type1")
        h2 = task_manager.handler_registry.get_handler("type2")
        
        assert h1 is not None
        assert h2 is not None


class TestMultipleTasks:
    """Test managing multiple tasks."""
    
    def test_multiple_tasks_tracked(self, task_manager, registry):
        """Test tracking multiple tasks."""
        async def dummy_coro():
            pass
        
        # Create and start multiple tasks
        runs = []
        for i in range(3):
            run = Run(
                run_id=f"test_run_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=RunStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            registry.add_run(run)
            runs.append(run)
            task_manager.start_task(run, dummy_coro())
        
        # Verify all tasks are tracked
        assert task_manager.get_active_task_count() == 3
        
        task_ids = task_manager.get_active_task_ids()
        assert len(task_ids) == 3
        assert all(run.run_id in task_ids for run in runs)
    
    @pytest.mark.asyncio
    async def test_get_status_multiple_tasks(self, task_manager, registry):
        """Test getting status of multiple tasks."""
        async def dummy_coro():
            pass
        
        # Create multiple tasks
        run_ids = []
        for i in range(3):
            run = Run(
                run_id=f"test_run_{i}",
                module_id="test_module",
                module_name="Test Module",
                status=RunStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            registry.add_run(run)
            run_id = task_manager.start_task(run, dummy_coro())
            run_ids.append(run_id)
        
        # Get status of each task
        for run_id in run_ids:
            status = await task_manager.get_task_status(run_id)
            assert status["status"] == "queued"


class TestIdempotency:
    """Test idempotency key handling."""
    
    def test_idempotency_key_from_run_id(self, task_manager, registry, sample_run):
        """Test that run_id is used as idempotency key."""
        async def dummy_coro():
            pass
        
        registry.add_run(sample_run)
        
        # Start task
        task_manager.start_task(sample_run, dummy_coro())
        
        # Try to start same task again (should use same idempotency key)
        # This would normally fail due to unique constraint on idempotency_key
        # but we're just testing that the key is set correctly
        
        cursor = task_manager.queue.execute(
            "SELECT idempotency_key FROM task_queue WHERE idempotency_key = ?",
            (sample_run.run_id,)
        )
        row = cursor.fetchone()
        assert row is not None
        assert dict(row)["idempotency_key"] == sample_run.run_id
    
    @pytest.mark.asyncio
    async def test_schedule_with_idempotency_key(self, task_manager):
        """Test scheduling with explicit idempotency key."""
        task_id1 = await task_manager.schedule_task(
            task_type="test_task",
            payload={"data": "value"},
            idempotency_key="unique_key_123"
        )
        
        # Try to schedule again with same key (should fail due to unique constraint)
        with pytest.raises(Exception):
            await task_manager.schedule_task(
                task_type="test_task",
                payload={"data": "different_value"},
                idempotency_key="unique_key_123"
            )


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_get_status_invalid_task_id(self, task_manager):
        """Test getting status of invalid task ID."""
        status = await task_manager.get_task_status("invalid_id_999")
        assert status["status"] == "not_found"
        assert "error" in status
    
    @pytest.mark.asyncio
    async def test_cancel_already_completed(self, task_manager, registry, sample_run):
        """Test cancelling already completed task."""
        async def dummy_coro():
            pass
        
        registry.add_run(sample_run)
        run_id = task_manager.start_task(sample_run, dummy_coro())
        
        # Manually mark task as completed in queue
        with task_manager.queue.transaction() as conn:
            conn.execute(
                """
                UPDATE task_queue
                SET status = 'completed',
                    finished_at_utc = datetime('now', 'utc')
                WHERE idempotency_key = ?
                """,
                (run_id,)
            )
        
        # Try to cancel - should return False
        success = await task_manager.cancel_task(run_id)
        assert success is False
    
    @pytest.mark.asyncio
    async def test_wait_all_with_no_tasks(self, task_manager):
        """Test wait_all with no tasks."""
        # Should complete immediately
        await task_manager.wait_all()
        assert task_manager.get_active_task_count() == 0


class TestStatusMapping:
    """Test status mapping between queue and BackgroundTaskManager."""
    
    @pytest.mark.asyncio
    async def test_queue_status_to_manager_status(self, task_manager, registry, sample_run):
        """Test that queue statuses are mapped correctly."""
        async def dummy_coro():
            pass
        
        registry.add_run(sample_run)
        run_id = task_manager.start_task(sample_run, dummy_coro())
        
        # Test queued status
        status = await task_manager.get_task_status(run_id)
        assert status["status"] == "queued"
        
        # Update to processing
        queue_task_id = task_manager.tasks[run_id]
        with task_manager.queue.transaction() as conn:
            conn.execute(
                "UPDATE task_queue SET status = 'processing' WHERE id = ?",
                (queue_task_id,)
            )
        
        status = await task_manager.get_task_status(run_id)
        assert status["status"] == "running"  # Maps to "running"
        
        # Update to completed
        with task_manager.queue.transaction() as conn:
            conn.execute(
                "UPDATE task_queue SET status = 'completed' WHERE id = ?",
                (queue_task_id,)
            )
        
        status = await task_manager.get_task_status(run_id)
        assert status["status"] == "completed"
