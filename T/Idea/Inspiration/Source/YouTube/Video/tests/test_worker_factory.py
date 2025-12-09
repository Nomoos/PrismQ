"""Tests for worker factory.

This module tests the WorkerFactory implementation, ensuring:
- SOLID principles compliance (Open/Closed)
- Worker registration and creation
- Error handling for unknown task types
"""

import os
import tempfile
from unittest.mock import MagicMock, Mock

import pytest

from src.core.config import Config
from src.core.database import Database
from src.workers.base_worker import BaseWorker
from src.workers.factory import WorkerFactory, worker_factory


class TestWorkerFactoryInitialization:
    """Test factory initialization and default registrations."""

    def test_factory_initialization(self):
        """Test that factory initializes."""
        factory = WorkerFactory()
        assert factory is not None

        # Should be able to get list of supported types
        supported_types = factory.get_supported_types()
        assert isinstance(supported_types, list)

    def test_global_factory_instance(self):
        """Test that global factory instance exists."""
        assert worker_factory is not None
        assert isinstance(worker_factory, WorkerFactory)


class TestWorkerFactoryRegistration:
    """Test worker registration (Open/Closed Principle)."""

    def test_register_new_worker_type(self):
        """Test registering a new worker type."""
        factory = WorkerFactory()

        # Create a mock worker class
        class CustomWorker(BaseWorker):
            def process_task(self, task):
                return None

        # Register custom worker
        factory.register("custom_task", CustomWorker)

        # Verify registration
        assert "custom_task" in factory.get_supported_types()

    def test_register_overwrites_existing(self):
        """Test that registration can overwrite existing worker types."""
        factory = WorkerFactory()

        class NewVideoWorker(BaseWorker):
            def process_task(self, task):
                return None

        # Overwrite existing registration
        factory.register("youtube_video_single", NewVideoWorker)

        # Verify it's still registered
        assert "youtube_video_single" in factory.get_supported_types()


class TestWorkerFactoryCreation:
    """Test worker instance creation."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for worker creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_db_path = os.path.join(tmpdir, "queue.db")
            results_db_path = os.path.join(tmpdir, "results.db")

            # Create mock config
            config = Mock(spec=Config)
            config.youtube_api_key = "test_api_key"
            config.database_path = results_db_path
            config.youtube_quota_db_path = os.path.join(tmpdir, "quota.db")
            config.youtube_daily_quota_limit = 10000

            # Create mock results database
            results_db = Mock(spec=Database)

            yield {"queue_db_path": queue_db_path, "config": config, "results_db": results_db}

    def test_create_with_custom_worker(self, mock_dependencies):
        """Test creating a custom worker."""
        factory = WorkerFactory()

        # Register a custom test worker
        class TestWorker(BaseWorker):
            def process_task(self, task):
                return None

        factory.register("test_task", TestWorker)

        worker = factory.create(
            task_type="test_task", worker_id="test-worker-1", **mock_dependencies
        )

        assert worker is not None
        assert isinstance(worker, TestWorker)
        assert worker.worker_id == "test-worker-1"

    def test_create_with_unknown_task_type(self, mock_dependencies):
        """Test that creating worker with unknown task type raises error."""
        factory = WorkerFactory()

        with pytest.raises(ValueError) as exc_info:
            factory.create(
                task_type="unknown_task_type", worker_id="test-worker", **mock_dependencies
            )

        assert "Unknown task type" in str(exc_info.value)
        assert "unknown_task_type" in str(exc_info.value)

    def test_create_with_additional_kwargs(self, mock_dependencies):
        """Test creating worker with additional keyword arguments."""
        factory = WorkerFactory()

        class TestWorker(BaseWorker):
            def process_task(self, task):
                return None

        factory.register("test_task", TestWorker)

        worker = factory.create(
            task_type="test_task",
            worker_id="test-worker",
            strategy="FIFO",
            heartbeat_interval=60,
            **mock_dependencies
        )

        assert worker.strategy == "FIFO"
        assert worker.heartbeat_interval == 60


class TestWorkerFactoryListSupported:
    """Test listing supported task types."""

    def test_get_supported_types_returns_list(self):
        """Test that get_supported_types returns a list."""
        factory = WorkerFactory()
        supported = factory.get_supported_types()

        assert isinstance(supported, list)

    def test_get_supported_types_after_registration(self):
        """Test that supported types updates after new registration."""
        factory = WorkerFactory()

        class CustomWorker(BaseWorker):
            def process_task(self, task):
                return None

        # Initial count
        initial_count = len(factory.get_supported_types())

        # Register new worker
        factory.register("custom_new_task", CustomWorker)

        # Verify count increased
        new_count = len(factory.get_supported_types())
        assert new_count == initial_count + 1
        assert "custom_new_task" in factory.get_supported_types()


class TestWorkerFactorySOLIDCompliance:
    """Test SOLID principles compliance."""

    def test_open_closed_principle(self):
        """Test that factory follows Open/Closed Principle.

        Should be open for extension (new workers can be registered)
        but closed for modification (factory logic unchanged).
        """
        factory = WorkerFactory()

        # Define a completely new worker type
        class SocialMediaWorker(BaseWorker):
            def process_task(self, task):
                return None

        # Extend factory without modifying its code
        factory.register("social_media_scrape", SocialMediaWorker)

        # Verify extension works
        assert "social_media_scrape" in factory.get_supported_types()

    def test_dependency_injection(self):
        """Test that factory uses dependency injection correctly."""
        factory = WorkerFactory()

        # Mock all dependencies
        mock_config = Mock(spec=Config)
        mock_results_db = Mock(spec=Database)

        # Create a custom test worker
        class TestWorker(BaseWorker):
            def process_task(self, task):
                return None

        factory.register("test_task", TestWorker)

        with tempfile.TemporaryDirectory() as tmpdir:
            queue_db_path = os.path.join(tmpdir, "queue.db")

            # Dependencies are injected, not created internally
            worker = factory.create(
                task_type="test_task",
                worker_id="test-worker",
                queue_db_path=queue_db_path,
                config=mock_config,
                results_db=mock_results_db,
            )

            # Worker should use injected dependencies
            assert worker.config is mock_config
            assert worker.results_db is mock_results_db
