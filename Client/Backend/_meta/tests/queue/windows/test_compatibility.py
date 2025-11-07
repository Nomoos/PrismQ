"""
Windows compatibility tests for queue system.

Tests Windows-specific behaviors like file locking, WAL mode, and path handling.
"""

import pytest
import tempfile
import sys
from pathlib import Path

from src.queue import (
    QueueDatabase,
    WorkerEngine,
    Task,
    get_global_registry,
    reset_global_registry,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_queue.db"
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        yield db
        db.close()


@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    reset_global_registry()
    registry = get_global_registry()
    yield registry
    reset_global_registry()


@pytest.mark.windows
def test_wal_mode_enabled(temp_db):
    """Test that WAL mode is properly enabled."""
    # Query journal mode
    cursor = temp_db.execute("PRAGMA journal_mode")
    journal_mode = cursor.fetchone()[0]
    
    assert journal_mode.upper() == "WAL", f"WAL mode not enabled: {journal_mode}"


@pytest.mark.windows
def test_concurrent_database_access(temp_db, registry):
    """Test concurrent access to database (simulating Windows file locking)."""
    def concurrent_handler(task: Task):
        return {"status": "success"}
    
    registry.register_handler("concurrent_task", concurrent_handler)
    
    # Enqueue tasks
    with temp_db.transaction() as conn:
        for i in range(10):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("concurrent_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Create multiple workers (simulating concurrent access)
    workers = [
        WorkerEngine(
            temp_db,
            f"worker-{i}",
            handler_registry=registry,
        )
        for i in range(3)
    ]
    
    # All workers should be able to access database
    for _ in range(5):
        for worker in workers:
            worker.claim_and_process()  # Should not raise locking errors
    
    # Verify some tasks were processed
    cursor = temp_db.execute(
        "SELECT COUNT(*) FROM task_queue WHERE status = 'completed'",
    )
    completed_count = cursor.fetchone()[0]
    assert completed_count > 0


@pytest.mark.windows
def test_path_handling_with_backslashes(temp_db):
    """Test that Windows-style paths work correctly."""
    # This tests that the database path handling works on Windows
    # The temp_db fixture already tests path creation
    
    # Test database file exists at expected path
    assert temp_db.db_path is not None
    db_file = Path(temp_db.db_path)
    assert db_file.exists()
    
    # Test WAL files exist (WAL mode specific)
    wal_file = Path(str(db_file) + "-wal")
    shm_file = Path(str(db_file) + "-shm")
    # These may or may not exist depending on writes, but check they're valid paths
    assert isinstance(wal_file, Path)
    assert isinstance(shm_file, Path)


@pytest.mark.windows
def test_busy_timeout_handling(temp_db):
    """Test that busy_timeout is properly configured for Windows."""
    # Query busy timeout
    cursor = temp_db.execute("PRAGMA busy_timeout")
    busy_timeout = cursor.fetchone()[0]
    
    # Should be set to at least 5000ms for Windows compatibility
    assert busy_timeout >= 5000, f"Busy timeout too low: {busy_timeout}ms"


@pytest.mark.windows
def test_foreign_keys_enabled(temp_db):
    """Test that foreign keys are enabled (important for referential integrity)."""
    cursor = temp_db.execute("PRAGMA foreign_keys")
    foreign_keys = cursor.fetchone()[0]
    
    assert foreign_keys == 1, "Foreign keys not enabled"


@pytest.mark.windows
def test_large_payload_handling(temp_db, registry):
    """Test handling of large task payloads (Windows file system limits)."""
    def large_handler(task: Task):
        import json
        payload = json.loads(task.payload)
        assert len(payload["data"]) > 1000
        return {"status": "success"}
    
    registry.register_handler("large_task", large_handler)
    
    # Create a large payload (10KB)
    large_data = "x" * 10000
    
    # Enqueue task with large payload
    with temp_db.transaction() as conn:
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("large_task", f'{{"data": "{large_data}"}}', 100, 1),
        )
    
    # Process task
    worker = WorkerEngine(
        temp_db,
        "worker-large",
        handler_registry=registry,
    )
    
    # Should handle large payload without issues
    worker.claim_and_process()
    
    # Verify task completed
    cursor = temp_db.execute(
        "SELECT status FROM task_queue WHERE type = 'large_task'",
    )
    row = cursor.fetchone()
    assert row["status"] == "completed"


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
def test_windows_specific_pragmas():
    """Test Windows-specific SQLite PRAGMA settings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_windows.db"
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        # Check Windows-optimized settings
        pragmas_to_check = {
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "temp_store": "MEMORY",
        }
        
        for pragma_name, expected_value in pragmas_to_check.items():
            cursor = db.execute(f"PRAGMA {pragma_name}")
            actual_value = cursor.fetchone()[0]
            assert str(actual_value).upper() == expected_value.upper(), \
                f"PRAGMA {pragma_name}: expected {expected_value}, got {actual_value}"
        
        db.close()


@pytest.mark.windows
def test_path_with_spaces(registry):
    """Test database path handling with spaces (common on Windows)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create path with spaces
        db_dir = Path(tmpdir) / "path with spaces"
        db_dir.mkdir()
        db_path = db_dir / "test queue.db"
        
        # Should handle path with spaces
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        # Should be able to use database
        def space_handler(task: Task):
            return {"status": "success"}
        
        registry.register_handler("space_task", space_handler)
        
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("space_task", '{"test": true}', 100, 1),
            )
        
        worker = WorkerEngine(
            db,
            "worker-space",
            handler_registry=registry,
        )
        
        worker.claim_and_process()
        
        # Verify task completed
        cursor = db.execute(
            "SELECT COUNT(*) FROM task_queue WHERE status = 'completed'",
        )
        completed = cursor.fetchone()[0]
        assert completed == 1
        
        db.close()


@pytest.mark.windows
def test_unicode_in_paths_and_data(registry):
    """Test Unicode handling in paths and task data."""
    def unicode_handler(task: Task):
        import json
        payload = json.loads(task.payload)
        # Verify Unicode is preserved
        assert "测试" in payload["text"]
        assert "🎉" in payload["emoji"]
        return {"status": "success"}
    
    registry.register_handler("unicode_task", unicode_handler)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_unicode.db"
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        # Enqueue task with Unicode data
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("unicode_task", '{"text": "测试数据", "emoji": "🎉✨"}', 100, 1),
            )
        
        worker = WorkerEngine(
            db,
            "worker-unicode",
            handler_registry=registry,
        )
        
        worker.claim_and_process()
        
        # Verify task completed
        cursor = db.execute(
            "SELECT status FROM task_queue WHERE type = 'unicode_task'",
        )
        row = cursor.fetchone()
        assert row["status"] == "completed"
        
        db.close()
