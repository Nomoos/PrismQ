"""Tests for TaskManager integration in BaseWorker."""

import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add source to path
src_path = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(src_path))

from workers import Task, TaskResult, TaskStatus


def test_taskmanager_integration_import():
    """Test that TaskManager integration code imports correctly."""
    from workers.base_worker import BaseWorker, _taskmanager_available

    # Check if import flag exists
    assert hasattr(BaseWorker, "__init__")
    print(f"✓ TaskManager integration imports (available: {_taskmanager_available})")


def test_worker_with_taskmanager_disabled():
    """Test that worker can be initialized with TaskManager disabled."""
    from core.config import Config
    from core.database import Database
    from workers.base_worker import BaseWorker

    # Create a concrete implementation for testing
    class TestWorker(BaseWorker):
        def process_task(self, task: Task) -> TaskResult:
            return TaskResult(success=True, items_processed=1)

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        queue_db = tmp.name

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        results_db_path = tmp.name

    try:
        # Initialize schema
        schema_path = Path(__file__).resolve().parents[2] / "src" / "workers" / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        conn = sqlite3.connect(queue_db)
        conn.executescript(schema_sql)
        conn.close()

        # Create worker with TaskManager disabled
        config = Config(interactive=False)
        results_db = Database(results_db_path)

        worker = TestWorker(
            worker_id="test-worker",
            queue_db_path=queue_db,
            config=config,
            results_db=results_db,
            enable_taskmanager=False,
        )

        assert worker.taskmanager_client is None
        print("✓ Worker can be initialized with TaskManager disabled")

    finally:
        Path(queue_db).unlink(missing_ok=True)
        Path(results_db_path).unlink(missing_ok=True)


def test_worker_update_task_manager_graceful_degradation():
    """Test that _update_task_manager handles missing client gracefully."""
    from core.config import Config
    from core.database import Database
    from workers.base_worker import BaseWorker

    # Create a concrete implementation for testing
    class TestWorker(BaseWorker):
        def process_task(self, task: Task) -> TaskResult:
            return TaskResult(success=True, items_processed=1)

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        queue_db = tmp.name

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        results_db_path = tmp.name

    try:
        # Initialize schema
        schema_path = Path(__file__).resolve().parents[2] / "src" / "workers" / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        conn = sqlite3.connect(queue_db)
        conn.executescript(schema_sql)
        conn.close()

        # Create worker with TaskManager disabled
        config = Config(interactive=False)
        results_db = Database(results_db_path)

        worker = TestWorker(
            worker_id="test-worker",
            queue_db_path=queue_db,
            config=config,
            results_db=results_db,
            enable_taskmanager=False,
        )

        # Create a test task and result
        task = Task(
            id=1,
            task_type="test_task",
            parameters={"subreddit": "python"},
            priority=5,
            status=TaskStatus.CLAIMED,
            retry_count=0,
            max_retries=3,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        result = TaskResult(success=True, data={"posts": []}, items_processed=10)

        # This should not raise an error even though taskmanager_client is None
        worker._update_task_manager(task, result)

        print("✓ _update_task_manager handles missing client gracefully")

    finally:
        Path(queue_db).unlink(missing_ok=True)
        Path(results_db_path).unlink(missing_ok=True)


def test_worker_update_task_manager_with_mock_client():
    """Test that _update_task_manager calls TaskManager API correctly."""
    from core.config import Config
    from core.database import Database
    from workers.base_worker import BaseWorker

    # Create a concrete implementation for testing
    class TestWorker(BaseWorker):
        def process_task(self, task: Task) -> TaskResult:
            return TaskResult(success=True, items_processed=1)

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        queue_db = tmp.name

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        results_db_path = tmp.name

    try:
        # Initialize schema
        schema_path = Path(__file__).resolve().parents[2] / "src" / "workers" / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        conn = sqlite3.connect(queue_db)
        conn.executescript(schema_sql)
        conn.close()

        # Create worker
        config = Config(interactive=False)
        results_db = Database(results_db_path)

        worker = TestWorker(
            worker_id="test-worker",
            queue_db_path=queue_db,
            config=config,
            results_db=results_db,
            enable_taskmanager=False,  # Disabled for this test
        )

        # Mock the TaskManager client
        mock_client = Mock()
        mock_client.complete_task = Mock(return_value={"status": "completed"})
        worker.taskmanager_client = mock_client

        # Create a test task and result
        task = Task(
            id=1,
            task_type="test_task",
            parameters={"subreddit": "python", "sort": "hot"},
            priority=5,
            status=TaskStatus.CLAIMED,
            retry_count=0,
            max_retries=3,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        result = TaskResult(success=True, data={"posts": []}, items_processed=10)

        # Call _update_task_manager
        worker._update_task_manager(task, result)

        # Verify that complete_task was called
        mock_client.complete_task.assert_called_once()
        call_args = mock_client.complete_task.call_args

        assert call_args[1]["task_id"] == 1
        assert call_args[1]["worker_id"] == "test-worker"
        assert call_args[1]["success"] is True
        assert call_args[1]["result"]["items_processed"] == 10
        assert call_args[1]["result"]["subreddit"] == "python"

        print("✓ _update_task_manager calls TaskManager API correctly")

    finally:
        Path(queue_db).unlink(missing_ok=True)
        Path(results_db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    print("\n=== Running TaskManager Integration Tests ===\n")

    test_taskmanager_integration_import()
    test_worker_with_taskmanager_disabled()
    test_worker_update_task_manager_graceful_degradation()
    test_worker_update_task_manager_with_mock_client()

    print("\n=== All Tests Passed! ===\n")
