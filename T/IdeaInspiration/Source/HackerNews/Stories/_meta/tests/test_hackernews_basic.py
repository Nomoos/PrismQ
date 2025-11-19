"""Basic tests for HackerNews API Client and Workers."""

import sys
import tempfile
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch

# Add source to path
src_path = Path(__file__).resolve().parents[2] / 'src'
sys.path.insert(0, str(src_path))

from workers import Task, TaskResult, TaskStatus
from client import HackerNewsClient


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
        task_type="story_fetch",
        parameters={"story_type": "top", "limit": 10},
        priority=5,
        status=TaskStatus.QUEUED,
        retry_count=0,
        max_retries=3,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    assert task.id == 1
    assert task.task_type == "story_fetch"
    assert task.parameters["story_type"] == "top"
    assert task.status == TaskStatus.QUEUED
    print("✓ Task dataclass works correctly")


def test_task_result_dataclass():
    """Test TaskResult dataclass creation."""
    result = TaskResult(
        success=True,
        data={"stories": []},
        items_processed=10,
        metrics={"story_type": "top"}
    )
    
    assert result.success is True
    assert result.items_processed == 10
    print("✓ TaskResult dataclass works correctly")


def test_queue_schema():
    """Test that queue schema can be created."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Read schema
        schema_path = Path(__file__).resolve().parents[2] / 'src' / 'workers' / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Create database
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)
        
        # Verify tables exist
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'task_queue' in tables
        assert 'worker_heartbeats' in tables
        assert 'task_history' in tables
        
        conn.close()
        print("✓ Queue schema created successfully with all tables")
        
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_task_insertion_and_retrieval():
    """Test inserting and retrieving tasks from the queue."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Create database with schema
        schema_path = Path(__file__).resolve().parents[2] / 'src' / 'workers' / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)
        
        # Insert a task
        now = datetime.now(timezone.utc).isoformat()
        params = json.dumps({"story_type": "top", "limit": 30})
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO task_queue 
            (task_type, parameters, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("story_fetch", params, 5, "queued", now, now))
        conn.commit()
        
        # Retrieve the task
        cursor.execute("SELECT * FROM task_queue WHERE status = 'queued'")
        row = cursor.fetchone()
        
        assert row is not None
        print("✓ Task insertion and retrieval works")
        
        conn.close()
        
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_hackernews_client_initialization():
    """Test HackerNews client initialization."""
    client = HackerNewsClient()
    
    assert client.API_BASE == "https://hacker-news.firebaseio.com/v0"
    assert client.timeout == 10
    assert client.rate_limit_delay == 0.1
    
    print("✓ HackerNewsClient initialized correctly")


def test_claiming_strategies():
    """Test that claiming strategies can be imported and used."""
    from workers.claiming_strategies import get_strategy
    
    fifo = get_strategy("FIFO")
    assert "created_at ASC" in fifo.get_order_by_clause()
    
    lifo = get_strategy("LIFO")
    assert "created_at DESC" in lifo.get_order_by_clause()
    
    priority = get_strategy("PRIORITY")
    assert "priority DESC" in priority.get_order_by_clause()
    
    print("✓ All claiming strategies work correctly")


def test_hackernews_client_api_methods():
    """Test that HackerNews client has all required API methods."""
    client = HackerNewsClient()
    
    # Check methods exist
    assert hasattr(client, 'get_top_stories')
    assert hasattr(client, 'get_best_stories')
    assert hasattr(client, 'get_new_stories')
    assert hasattr(client, 'get_ask_stories')
    assert hasattr(client, 'get_show_stories')
    assert hasattr(client, 'get_job_stories')
    assert hasattr(client, 'get_item')
    assert hasattr(client, 'get_items')
    assert hasattr(client, 'get_max_item_id')
    assert hasattr(client, 'get_user')
    
    print("✓ HackerNewsClient has all required methods")


def test_hackernews_client_context_manager():
    """Test that HackerNews client works as context manager."""
    with HackerNewsClient() as client:
        assert client is not None
    
    print("✓ HackerNewsClient context manager works")


def run_all_tests():
    """Run all tests."""
    print("\n=== Running HackerNews Tests ===\n")
    
    tests = [
        test_worker_imports,
        test_task_dataclass,
        test_task_result_dataclass,
        test_queue_schema,
        test_task_insertion_and_retrieval,
        test_hackernews_client_initialization,
        test_claiming_strategies,
        test_hackernews_client_api_methods,
        test_hackernews_client_context_manager,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
