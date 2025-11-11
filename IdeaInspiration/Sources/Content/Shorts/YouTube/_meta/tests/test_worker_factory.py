"""Tests for WorkerFactory implementation."""

import pytest
from unittest.mock import Mock

from src.workers import Task, TaskResult
from src.workers.base_worker import BaseWorker
from src.workers.factory import WorkerFactory, worker_factory


class MockWorker1(BaseWorker):
    """Mock worker for testing."""
    
    def process_task(self, task: Task) -> TaskResult:
        return TaskResult(success=True, data={"worker": "1"})


class MockWorker2(BaseWorker):
    """Another mock worker for testing."""
    
    def process_task(self, task: Task) -> TaskResult:
        return TaskResult(success=True, data={"worker": "2"})


@pytest.fixture
def factory():
    """Create a fresh factory instance for testing."""
    return WorkerFactory()


@pytest.fixture
def mock_config():
    """Create a mock config object."""
    return Mock()


@pytest.fixture
def mock_results_db():
    """Create a mock results database."""
    return Mock()


class TestWorkerFactory:
    """Test WorkerFactory functionality."""
    
    def test_factory_initializes_empty(self, factory):
        """Test factory initializes with no registered workers."""
        assert len(factory.get_supported_types()) == 0
    
    def test_register_worker_type(self, factory):
        """Test registering a worker type."""
        factory.register("task_type_1", MockWorker1)
        
        assert "task_type_1" in factory.get_supported_types()
        assert len(factory.get_supported_types()) == 1
    
    def test_register_multiple_worker_types(self, factory):
        """Test registering multiple worker types."""
        factory.register("task_type_1", MockWorker1)
        factory.register("task_type_2", MockWorker2)
        
        supported = factory.get_supported_types()
        assert len(supported) == 2
        assert "task_type_1" in supported
        assert "task_type_2" in supported
    
    def test_create_worker_instance(self, factory, mock_config, mock_results_db):
        """Test creating a worker instance."""
        factory.register("test_task", MockWorker1)
        
        worker = factory.create(
            task_type="test_task",
            worker_id="worker-1",
            queue_db_path=":memory:",
            config=mock_config,
            results_db=mock_results_db
        )
        
        assert isinstance(worker, MockWorker1)
        assert worker.worker_id == "worker-1"
    
    def test_create_different_worker_types(self, factory, mock_config, mock_results_db):
        """Test creating different worker types."""
        factory.register("type1", MockWorker1)
        factory.register("type2", MockWorker2)
        
        worker1 = factory.create(
            task_type="type1",
            worker_id="worker-1",
            queue_db_path=":memory:",
            config=mock_config,
            results_db=mock_results_db
        )
        
        worker2 = factory.create(
            task_type="type2",
            worker_id="worker-2",
            queue_db_path=":memory:",
            config=mock_config,
            results_db=mock_results_db
        )
        
        assert isinstance(worker1, MockWorker1)
        assert isinstance(worker2, MockWorker2)
    
    def test_create_unknown_type_raises_error(self, factory, mock_config, mock_results_db):
        """Test creating worker with unknown type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown task type"):
            factory.create(
                task_type="unknown",
                worker_id="worker-1",
                queue_db_path=":memory:",
                config=mock_config,
                results_db=mock_results_db
            )
    
    def test_create_with_kwargs(self, factory, mock_config, mock_results_db):
        """Test creating worker with additional kwargs."""
        factory.register("test_task", MockWorker1)
        
        worker = factory.create(
            task_type="test_task",
            worker_id="worker-1",
            queue_db_path=":memory:",
            config=mock_config,
            results_db=mock_results_db,
            strategy="FIFO",
            heartbeat_interval=60
        )
        
        assert worker.strategy == "FIFO"
        assert worker.heartbeat_interval == 60
    
    def test_overwrite_registration(self, factory):
        """Test that re-registering a type overwrites the previous one."""
        factory.register("task_type", MockWorker1)
        factory.register("task_type", MockWorker2)
        
        # Should have only one entry
        assert len(factory.get_supported_types()) == 1
        
        # Should use the last registered worker
        worker = factory.create(
            task_type="task_type",
            worker_id="worker-1",
            queue_db_path=":memory:",
            config=Mock(),
            results_db=Mock()
        )
        
        assert isinstance(worker, MockWorker2)


class TestGlobalFactoryInstance:
    """Test global worker_factory instance."""
    
    def test_global_factory_exists(self):
        """Test that global factory instance exists."""
        assert worker_factory is not None
        assert isinstance(worker_factory, WorkerFactory)
    
    def test_global_factory_is_usable(self):
        """Test that global factory can be used for registration."""
        # Note: This test modifies the global factory
        # In production, we'd want to clear it after the test
        initial_count = len(worker_factory.get_supported_types())
        
        worker_factory.register("global_test", MockWorker1)
        
        assert len(worker_factory.get_supported_types()) == initial_count + 1
        assert "global_test" in worker_factory.get_supported_types()
        
        # Cleanup
        worker_factory._worker_types.pop("global_test", None)


class TestFactoryOpenClosedPrinciple:
    """Test that factory follows Open/Closed Principle."""
    
    def test_adding_new_worker_doesnt_modify_factory(self, factory):
        """Test that adding new worker types doesn't require modifying factory code."""
        # Create a new worker type at runtime
        class DynamicWorker(BaseWorker):
            def process_task(self, task: Task) -> TaskResult:
                return TaskResult(success=True, data={"dynamic": True})
        
        # Should be able to register without modifying factory
        factory.register("dynamic_task", DynamicWorker)
        
        # Should be able to create instances
        worker = factory.create(
            task_type="dynamic_task",
            worker_id="dynamic-worker",
            queue_db_path=":memory:",
            config=Mock(),
            results_db=Mock()
        )
        
        assert isinstance(worker, DynamicWorker)
    
    def test_factory_extensible_via_registration(self, factory):
        """Test that factory is extensible via registration mechanism."""
        # Factory starts empty
        assert len(factory.get_supported_types()) == 0
        
        # Can be extended by registering workers
        factory.register("type1", MockWorker1)
        assert len(factory.get_supported_types()) == 1
        
        factory.register("type2", MockWorker2)
        assert len(factory.get_supported_types()) == 2
        
        # No modification to factory code was needed
