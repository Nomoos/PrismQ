"""Basic test for Reddit Subreddit Worker."""

import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Add source to path
src_path = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(src_path))

from workers import Task, TaskResult, TaskStatus


def test_worker_imports():
    """Test that worker imports work correctly."""
    assert Task is not None
    assert TaskResult is not None
    assert TaskStatus is not None
    print("✓ All worker imports successful")


def test_task_dataclass():
    """Test Task dataclass creation."""
    task = Task(
        id=1,
        task_type="subreddit_scrape",
        parameters={"subreddit": "python", "limit": 10},
        priority=5,
        status=TaskStatus.QUEUED,
        retry_count=0,
        max_retries=3,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    assert task.id == 1
    assert task.task_type == "subreddit_scrape"
    assert task.parameters["subreddit"] == "python"
    assert task.status == TaskStatus.QUEUED
    print("✓ Task dataclass works correctly")


def test_task_result_dataclass():
    """Test TaskResult dataclass creation."""
    result = TaskResult(
        success=True,
        data={"posts_scraped": 10},
        items_processed=10,
        metrics={"subreddit": "python"},
    )

    assert result.success is True
    assert result.data["posts_scraped"] == 10
    assert result.items_processed == 10
    print("✓ TaskResult dataclass works correctly")


def test_queue_schema():
    """Test that queue schema can be created."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        # Read schema
        schema_path = Path(__file__).resolve().parents[2] / "src" / "workers" / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Create database
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)

        # Verify tables exist
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert "task_queue" in tables
        assert "worker_heartbeats" in tables
        assert "task_logs" in tables

        # Verify views exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = [row[0] for row in cursor.fetchall()]

        assert "v_active_tasks" in views
        assert "v_worker_status" in views
        assert "v_task_stats" in views

        conn.close()
        print("✓ Queue schema created successfully with all tables and views")

    finally:
        Path(db_path).unlink(missing_ok=True)


def test_task_insertion_and_retrieval():
    """Test inserting and retrieving tasks from the queue."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        # Initialize schema
        schema_path = Path(__file__).resolve().parents[2] / "src" / "workers" / "schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)

        # Insert a task
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO task_queue (
                task_type, parameters, priority, status, 
                retry_count, max_retries, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "subreddit_scrape",
                json.dumps({"subreddit": "python", "limit": 50, "sort": "hot"}),
                5,
                "queued",
                0,
                3,
                now,
                now,
            ),
        )
        conn.commit()

        # Retrieve the task
        cursor.execute("SELECT * FROM task_queue WHERE status = 'queued'")
        row = cursor.fetchone()

        assert row is not None

        # Parse JSON parameters
        params = json.loads(row[2])  # parameters column
        assert params["subreddit"] == "python"
        assert params["limit"] == 50
        assert params["sort"] == "hot"

        conn.close()
        print("✓ Task insertion and retrieval works correctly")

    finally:
        Path(db_path).unlink(missing_ok=True)


def test_claiming_strategies():
    """Test that claiming strategies can be imported."""
    from workers.claiming_strategies import get_available_strategies, get_strategy

    strategies = get_available_strategies()
    assert "FIFO" in strategies
    assert "LIFO" in strategies
    assert "PRIORITY" in strategies

    # Test getting a strategy
    fifo = get_strategy("FIFO")
    assert fifo.get_order_by_clause() == "created_at ASC, priority DESC"

    lifo = get_strategy("LIFO")
    assert lifo.get_order_by_clause() == "created_at DESC, priority DESC"

    print("✓ Claiming strategies work correctly")


if __name__ == "__main__":
    print("\n=== Running Reddit Worker Infrastructure Tests ===\n")

    test_worker_imports()
    test_task_dataclass()
    test_task_result_dataclass()
    test_queue_schema()
    test_task_insertion_and_retrieval()
    test_claiming_strategies()

    print("\n=== All Tests Passed! ===\n")
