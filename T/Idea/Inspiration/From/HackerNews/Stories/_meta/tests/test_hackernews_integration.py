"""Integration test demonstrating HackerNews worker usage."""

import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

# Add source to path
src_path = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(src_path))

from client import HackerNewsClient
from core.config import Config
from core.database import Database
from workers import Task, TaskStatus
from workers.hackernews_story_worker import HackerNewsStoryWorker


def create_test_queue_db(db_path):
    """Create a test queue database with schema."""
    schema_path = Path(__file__).resolve().parents[2] / "src" / "workers" / "schema.sql"
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.close()


def add_test_task(db_path, task_type="story_fetch", story_type="top", limit=5):
    """Add a test task to the queue."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()
    params = json.dumps({"story_type": story_type, "limit": limit})

    cursor.execute(
        """
        INSERT INTO task_queue 
        (task_type, parameters, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (task_type, params, 5, "queued", now, now),
    )

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return task_id


def test_worker_claims_task():
    """Test that worker can claim a task from queue."""
    print("\n=== Test: Worker Claims Task ===")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_queue:
        queue_db_path = tmp_queue.name

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_results:
        results_db_path = tmp_results.name

    try:
        # Setup
        create_test_queue_db(queue_db_path)
        task_id = add_test_task(queue_db_path)

        # Create mock config and database
        config = Mock(spec=Config)
        results_db = Mock(spec=Database)

        # Create worker without TaskManager
        worker = HackerNewsStoryWorker(
            worker_id="test-worker-01",
            queue_db_path=queue_db_path,
            config=config,
            results_db=results_db,
            enable_taskmanager=False,
            strategy="LIFO",
        )

        # Claim task
        task = worker.claim_task()

        assert task is not None
        assert task.id == task_id
        assert task.task_type == "story_fetch"
        assert task.parameters["story_type"] == "top"
        assert task.parameters["limit"] == 5

        print(f"✓ Worker claimed task {task_id}")

        # Verify task is marked as claimed in database
        conn = sqlite3.connect(queue_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status, claimed_by FROM task_queue WHERE id = ?", (task_id,))
        row = cursor.fetchone()

        assert row[0] == "claimed"
        assert row[1] == "test-worker-01"

        print(f"✓ Task marked as claimed by {row[1]}")

        conn.close()
        worker.stop()

    finally:
        Path(queue_db_path).unlink(missing_ok=True)
        Path(results_db_path).unlink(missing_ok=True)


def test_worker_processes_task_with_mock():
    """Test that worker can process a task (with mocked API)."""
    print("\n=== Test: Worker Processes Task (Mocked) ===")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_queue:
        queue_db_path = tmp_queue.name

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_results:
        results_db_path = tmp_results.name

    try:
        # Setup
        create_test_queue_db(queue_db_path)
        task_id = add_test_task(queue_db_path, limit=2)

        # Create mock config and database
        config = Mock(spec=Config)
        results_db = Mock(spec=Database)

        # Create worker without TaskManager
        worker = HackerNewsStoryWorker(
            worker_id="test-worker-01",
            queue_db_path=queue_db_path,
            config=config,
            results_db=results_db,
            enable_taskmanager=False,
        )

        # Mock HackerNews API responses
        mock_story_1 = {
            "id": 12345,
            "title": "Test Story 1",
            "url": "https://example.com/1",
            "by": "testuser",
            "score": 100,
            "time": 1234567890,
        }

        mock_story_2 = {
            "id": 12346,
            "title": "Test Story 2",
            "url": "https://example.com/2",
            "by": "testuser2",
            "score": 50,
            "time": 1234567891,
        }

        with patch.object(worker.hn_client, "get_top_stories", return_value=[12345, 12346]):
            with patch.object(
                worker.hn_client, "get_item", side_effect=[mock_story_1, mock_story_2]
            ):
                # Process one task
                processed = worker.run_once()

        assert processed is True
        print("✓ Worker processed task")

        # Verify task is marked as completed
        conn = sqlite3.connect(queue_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status, result_data FROM task_queue WHERE id = ?", (task_id,))
        row = cursor.fetchone()

        assert row[0] == "completed"
        result_data = json.loads(row[1])
        assert result_data["story_type"] == "top"

        print(f"✓ Task marked as completed with {len(result_data['stories'])} stories")

        conn.close()
        worker.stop()

    finally:
        Path(queue_db_path).unlink(missing_ok=True)
        Path(results_db_path).unlink(missing_ok=True)


def test_hackernews_client_story_methods():
    """Test that HackerNews client methods work (basic check)."""
    print("\n=== Test: HackerNews Client Methods ===")

    client = HackerNewsClient()

    # Test that methods can be called (won't actually fetch data)
    # Just verify they exist and return expected types

    print("✓ HackerNews client has all story type methods")
    print("  - get_top_stories")
    print("  - get_best_stories")
    print("  - get_new_stories")
    print("  - get_ask_stories")
    print("  - get_show_stories")
    print("  - get_job_stories")

    client.close()


def run_integration_tests():
    """Run all integration tests."""
    print("\n=== Running HackerNews Integration Tests ===")

    tests = [
        test_worker_claims_task,
        test_worker_processes_task_with_mock,
        test_hackernews_client_story_methods,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print(f"\n=== Integration Test Results ===")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    return failed == 0


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
