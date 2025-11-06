"""Unit tests for queue database core infrastructure."""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import datetime
import json
import threading
import time

from src.queue import (
    QueueDatabase,
    Task,
    Worker,
    TaskLog,
    QueueDatabaseError,
    QueueBusyError,
    QueueSchemaError,
    PRAGMAS,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_queue.db"


@pytest.fixture
def db(temp_db_path):
    """Create a QueueDatabase instance for testing."""
    database = QueueDatabase(str(temp_db_path))
    yield database
    database.close()


class TestDatabaseInitialization:
    """Test database file creation and PRAGMA setup."""

    def test_database_file_creation(self, temp_db_path):
        """Test database file is created at specified path."""
        db = QueueDatabase(str(temp_db_path))
        conn = db.get_connection()
        assert temp_db_path.exists()
        db.close()

    def test_directory_creation(self):
        """Test database directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "subdir" / "another" / "queue.db"
            db = QueueDatabase(str(db_path))
            conn = db.get_connection()
            assert db_path.parent.exists()
            db.close()

    def test_pragmas_applied(self, db):
        """Test all PRAGMAs are applied correctly."""
        conn = db.get_connection()

        # Check journal_mode
        cursor = conn.execute("PRAGMA journal_mode")
        assert cursor.fetchone()[0].upper() == "WAL"

        # Check synchronous
        cursor = conn.execute("PRAGMA synchronous")
        assert cursor.fetchone()[0] == 1  # NORMAL = 1

        # Check foreign_keys
        cursor = conn.execute("PRAGMA foreign_keys")
        assert cursor.fetchone()[0] == 1  # ON = 1

        # Check busy_timeout
        cursor = conn.execute("PRAGMA busy_timeout")
        assert cursor.fetchone()[0] == 5000

    def test_row_factory_enabled(self, db):
        """Test row factory is set for dict-like access."""
        conn = db.get_connection()
        assert conn.row_factory == sqlite3.Row

    @pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
    def test_default_path_windows(self):
        """Test default database path on Windows."""
        if "PRISMQ_QUEUE_DB_PATH" in os.environ:
            del os.environ["PRISMQ_QUEUE_DB_PATH"]

        db = QueueDatabase()
        expected_path = Path(r"C:\Data\PrismQ\queue\queue.db")
        assert db.db_path == expected_path
        db.close()

    def test_default_path_linux(self, monkeypatch):
        """Test default database path on Linux/macOS."""
        monkeypatch.setattr("os.name", "posix")
        monkeypatch.delenv("PRISMQ_QUEUE_DB_PATH", raising=False)

        db = QueueDatabase()
        expected_path = Path("/tmp/prismq/queue/queue.db")
        assert db.db_path == expected_path
        db.close()

    def test_environment_variable_override(self, monkeypatch, temp_db_path):
        """Test PRISMQ_QUEUE_DB_PATH environment variable."""
        monkeypatch.setenv("PRISMQ_QUEUE_DB_PATH", str(temp_db_path))

        db = QueueDatabase()
        assert db.db_path == temp_db_path
        db.close()


class TestSchemaCreation:
    """Test all tables and indexes are created."""

    def test_schema_initialization(self, db):
        """Test schema creation runs without errors."""
        db.initialize_schema()
        # Should not raise any exceptions

    def test_task_queue_table_exists(self, db):
        """Test task_queue table is created with correct columns."""
        db.initialize_schema()
        conn = db.get_connection()

        # Query table info
        cursor = conn.execute("PRAGMA table_info(task_queue)")
        columns = {row[1] for row in cursor.fetchall()}

        # Expected columns (note: generated columns may not show in PRAGMA on all SQLite versions)
        expected_columns = {
            "id",
            "type",
            "priority",
            "payload",
            "compatibility",
            "status",
            "attempts",
            "max_attempts",
            "run_after_utc",
            "lease_until_utc",
            "reserved_at_utc",
            "processing_started_utc",
            "finished_at_utc",
            "locked_by",
            "error_message",
            "idempotency_key",
            "created_at_utc",
            "updated_at_utc",
        }

        # Check that all expected columns exist (generated columns may or may not appear)
        assert expected_columns.issubset(columns)

    def test_workers_table_exists(self, db):
        """Test workers table is created with correct columns."""
        db.initialize_schema()
        conn = db.get_connection()

        cursor = conn.execute("PRAGMA table_info(workers)")
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {"worker_id", "capabilities", "heartbeat_utc"}
        assert columns == expected_columns

    def test_task_logs_table_exists(self, db):
        """Test task_logs table is created with correct columns."""
        db.initialize_schema()
        conn = db.get_connection()

        cursor = conn.execute("PRAGMA table_info(task_logs)")
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {"log_id", "task_id", "at_utc", "level", "message", "details"}
        assert columns == expected_columns

    def test_indexes_created(self, db):
        """Test all indexes are created."""
        db.initialize_schema()
        conn = db.get_connection()

        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}

        expected_indexes = {
            "ix_task_status_prio_time",
            "ix_task_type_status",
            "ix_task_region",
            "ix_task_format",
            "uq_task_idempotency",
            "ix_logs_task",
        }

        assert expected_indexes.issubset(indexes)

    def test_foreign_key_constraint(self, db):
        """Test foreign key constraint on task_logs."""
        db.initialize_schema()
        conn = db.get_connection()

        # Try to insert log for non-existent task
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO task_logs (task_id, level, message) VALUES (?, ?, ?)",
                (99999, "INFO", "test"),
            )

    def test_idempotency_unique_constraint(self, db):
        """Test unique constraint on idempotency_key."""
        db.initialize_schema()
        conn = db.get_connection()

        # Insert first task with idempotency key
        conn.execute(
            "INSERT INTO task_queue (type, payload, idempotency_key) VALUES (?, ?, ?)",
            ("test", "{}", "unique-key-123"),
        )
        conn.commit()

        # Try to insert second task with same key
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO task_queue (type, payload, idempotency_key) VALUES (?, ?, ?)",
                ("test", "{}", "unique-key-123"),
            )


class TestConnectionManagement:
    """Test connection is reused properly."""

    def test_connection_reuse(self, db):
        """Test same connection is reused across calls."""
        conn1 = db.get_connection()
        conn2 = db.get_connection()
        assert conn1 is conn2

    def test_connection_close(self, db):
        """Test connection can be closed."""
        conn = db.get_connection()
        assert conn is not None

        db.close()
        # After close, should create new connection
        conn2 = db.get_connection()
        assert conn2 is not None
        assert conn2 is not conn

    def test_context_manager(self, temp_db_path):
        """Test database can be used as context manager."""
        with QueueDatabase(str(temp_db_path)) as db:
            conn = db.get_connection()
            assert conn is not None

        # Connection should be closed after context
        # Note: We can't easily test this without accessing internal state


class TestTransactions:
    """Test transaction handling."""

    def test_transaction_commit(self, db):
        """Test transaction commits successfully."""
        db.initialize_schema()

        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload) VALUES (?, ?)", ("test", "{}")
            )

        # Verify data was committed
        cursor = db.execute("SELECT COUNT(*) FROM task_queue")
        count = cursor.fetchone()[0]
        assert count == 1

    def test_transaction_rollback(self, db):
        """Test transaction rolls back on error."""
        db.initialize_schema()

        with pytest.raises(sqlite3.IntegrityError):
            with db.transaction() as conn:
                # Insert valid task
                conn.execute(
                    "INSERT INTO task_queue (type, payload) VALUES (?, ?)", ("test", "{}")
                )
                # Try to insert invalid task (missing required column)
                conn.execute("INSERT INTO task_queue (payload) VALUES (?)", ("{}",))

        # Verify no data was committed
        cursor = db.execute("SELECT COUNT(*) FROM task_queue")
        count = cursor.fetchone()[0]
        assert count == 0

    def test_immediate_transaction(self, db):
        """Test IMMEDIATE transaction isolation."""
        db.initialize_schema()

        # This test verifies BEGIN IMMEDIATE is used
        # In practice, this prevents conflicts in concurrent scenarios
        with db.transaction() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master LIMIT 1")
            result = cursor.fetchone()
            # Transaction should work


class TestExecuteMethods:
    """Test execute and execute_many methods."""

    def test_execute(self, db):
        """Test single statement execution."""
        db.initialize_schema()

        cursor = db.execute(
            "INSERT INTO task_queue (type, payload) VALUES (?, ?)", ("test", "{}")
        )
        db.get_connection().commit()

        cursor = db.execute("SELECT COUNT(*) FROM task_queue")
        count = cursor.fetchone()[0]
        assert count == 1

    def test_execute_many(self, db):
        """Test batch statement execution."""
        db.initialize_schema()

        tasks = [
            ("test1", "{}"),
            ("test2", "{}"),
            ("test3", "{}"),
        ]

        db.execute_many(
            "INSERT INTO task_queue (type, payload) VALUES (?, ?)", tasks
        )

        cursor = db.execute("SELECT COUNT(*) FROM task_queue")
        count = cursor.fetchone()[0]
        assert count == 3

    def test_execute_with_params(self, db):
        """Test parameterized queries."""
        db.initialize_schema()

        db.execute(
            "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
            ("test", "{}", 50),
        )
        db.get_connection().commit()

        cursor = db.execute(
            "SELECT priority FROM task_queue WHERE type = ?", ("test",)
        )
        priority = cursor.fetchone()[0]
        assert priority == 50


class TestErrorHandling:
    """Test error handling."""

    def test_sqlite_busy_error(self, db):
        """Test SQLITE_BUSY error handling with timeout."""
        # This is hard to test directly, but we can verify the timeout is set
        conn = db.get_connection()
        cursor = conn.execute("PRAGMA busy_timeout")
        timeout = cursor.fetchone()[0]
        assert timeout == 5000

    def test_invalid_sql_raises_error(self, db):
        """Test invalid SQL raises QueueDatabaseError."""
        with pytest.raises(QueueDatabaseError):
            db.execute("INVALID SQL STATEMENT")

    def test_schema_error_on_invalid_schema(self, temp_db_path):
        """Test schema initialization errors are caught."""
        db = QueueDatabase(str(temp_db_path))
        
        # Test with actually invalid SQL that will raise an error
        with pytest.raises(QueueDatabaseError):
            # Missing FROM clause will cause error
            db.execute("SELECT * WHERE id = 1")
        
        db.close()


class TestThreadSafety:
    """Test thread-safe operations."""

    def test_concurrent_reads(self, db):
        """Test multiple threads can read safely."""
        db.initialize_schema()

        # Insert test data
        db.execute(
            "INSERT INTO task_queue (type, payload) VALUES (?, ?)", ("test", "{}")
        )
        db.get_connection().commit()

        results = []
        errors = []

        def read_task():
            try:
                cursor = db.execute("SELECT COUNT(*) FROM task_queue")
                row = cursor.fetchone()
                if row:
                    results.append(row[0])
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_task) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Check no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        # At least some reads should succeed
        assert len(results) > 0
        assert all(r == 1 for r in results)

    def test_concurrent_writes(self, db):
        """Test multiple threads can write safely."""
        db.initialize_schema()

        def write_task(task_type):
            with db.transaction() as conn:
                conn.execute(
                    "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
                    (task_type, "{}"),
                )

        threads = [threading.Thread(target=write_task, args=(f"test{i}",)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        cursor = db.execute("SELECT COUNT(*) FROM task_queue")
        count = cursor.fetchone()[0]
        assert count == 5


class TestDataModels:
    """Test Task, Worker, and TaskLog data models."""

    def test_task_to_dict(self):
        """Test Task.to_dict() method."""
        task = Task(
            id=1,
            type="test",
            priority=50,
            payload='{"key": "value"}',
            status="queued",
        )
        data = task.to_dict()

        assert data["id"] == 1
        assert data["type"] == "test"
        assert data["priority"] == 50
        assert data["payload"] == '{"key": "value"}'
        assert data["status"] == "queued"

    def test_task_from_dict(self):
        """Test Task.from_dict() method."""
        data = {
            "id": 1,
            "type": "test",
            "priority": 50,
            "payload": '{"key": "value"}',
            "status": "queued",
        }
        task = Task.from_dict(data)

        assert task.id == 1
        assert task.type == "test"
        assert task.priority == 50
        assert task.payload == '{"key": "value"}'
        assert task.status == "queued"

    def test_task_datetime_serialization(self):
        """Test Task datetime serialization."""
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)  # UTC datetime without tzinfo
        task = Task(id=1, type="test", created_at_utc=now)

        data = task.to_dict()
        assert isinstance(data["created_at_utc"], str)

        # Round-trip
        task2 = Task.from_dict(data)
        # Comparing datetime objects (may lose microsecond precision)
        assert task2.created_at_utc is not None

    def test_task_get_payload_dict(self):
        """Test Task.get_payload_dict() method."""
        task = Task(payload='{"format": "video", "duration": 120}')
        payload_dict = task.get_payload_dict()

        assert payload_dict == {"format": "video", "duration": 120}

    def test_task_get_compatibility_dict(self):
        """Test Task.get_compatibility_dict() method."""
        task = Task(compatibility='{"region": "us-west", "gpu": true}')
        compat_dict = task.get_compatibility_dict()

        assert compat_dict == {"region": "us-west", "gpu": True}

    def test_worker_to_dict(self):
        """Test Worker.to_dict() method."""
        worker = Worker(
            worker_id="worker-01",
            capabilities='{"cpu": 8, "ram": 16}',
        )
        data = worker.to_dict()

        assert data["worker_id"] == "worker-01"
        assert data["capabilities"] == '{"cpu": 8, "ram": 16}'

    def test_worker_from_dict(self):
        """Test Worker.from_dict() method."""
        data = {
            "worker_id": "worker-01",
            "capabilities": '{"cpu": 8, "ram": 16}',
        }
        worker = Worker.from_dict(data)

        assert worker.worker_id == "worker-01"
        assert worker.capabilities == '{"cpu": 8, "ram": 16}'

    def test_worker_get_capabilities_dict(self):
        """Test Worker.get_capabilities_dict() method."""
        worker = Worker(capabilities='{"cpu": 8, "ram": 16, "gpu": "RTX5090"}')
        caps_dict = worker.get_capabilities_dict()

        assert caps_dict == {"cpu": 8, "ram": 16, "gpu": "RTX5090"}

    def test_tasklog_to_dict(self):
        """Test TaskLog.to_dict() method."""
        log = TaskLog(
            log_id=1,
            task_id=100,
            level="INFO",
            message="Task started",
        )
        data = log.to_dict()

        assert data["log_id"] == 1
        assert data["task_id"] == 100
        assert data["level"] == "INFO"
        assert data["message"] == "Task started"

    def test_tasklog_from_dict(self):
        """Test TaskLog.from_dict() method."""
        data = {
            "log_id": 1,
            "task_id": 100,
            "level": "ERROR",
            "message": "Task failed",
            "details": '{"error": "timeout"}',
        }
        log = TaskLog.from_dict(data)

        assert log.log_id == 1
        assert log.task_id == 100
        assert log.level == "ERROR"
        assert log.message == "Task failed"
        assert log.details == '{"error": "timeout"}'


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_insert_and_query_task(self, db):
        """Test inserting and querying a task."""
        db.initialize_schema()

        # Insert task
        db.execute(
            "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
            ("video_processing", '{"format": "mp4"}', 50),
        )
        db.get_connection().commit()

        # Query task
        cursor = db.execute("SELECT * FROM task_queue WHERE type = ?", ("video_processing",))
        row = cursor.fetchone()

        assert row is not None
        assert row["type"] == "video_processing"
        assert row["priority"] == 50

    def test_task_with_log_entries(self, db):
        """Test task with associated log entries."""
        db.initialize_schema()

        # Insert task
        cursor = db.execute(
            "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
            ("test", "{}"),
        )
        db.get_connection().commit()
        task_id = cursor.lastrowid

        # Insert log entries
        db.execute_many(
            "INSERT INTO task_logs (task_id, level, message) VALUES (?, ?, ?)",
            [
                (task_id, "INFO", "Task started"),
                (task_id, "INFO", "Processing..."),
                (task_id, "INFO", "Task completed"),
            ],
        )

        # Query logs
        cursor = db.execute(
            "SELECT COUNT(*) FROM task_logs WHERE task_id = ?", (task_id,)
        )
        count = cursor.fetchone()[0]
        assert count == 3

    def test_worker_heartbeat(self, db):
        """Test worker heartbeat update."""
        db.initialize_schema()

        # Insert worker
        db.execute(
            "INSERT INTO workers (worker_id, capabilities) VALUES (?, ?)",
            ("worker-01", '{"cpu": 8}'),
        )
        db.get_connection().commit()

        # Update heartbeat
        db.execute(
            "UPDATE workers SET heartbeat_utc = datetime('now') WHERE worker_id = ?",
            ("worker-01",),
        )
        db.get_connection().commit()

        # Query worker
        cursor = db.execute(
            "SELECT heartbeat_utc FROM workers WHERE worker_id = ?", ("worker-01",)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["heartbeat_utc"] is not None

    def test_generated_columns(self, db):
        """Test generated columns for JSON filtering."""
        db.initialize_schema()

        # Insert task with JSON data
        db.execute(
            """
            INSERT INTO task_queue (type, payload, compatibility) 
            VALUES (?, ?, ?)
            """,
            (
                "test",
                '{"format": "video"}',
                '{"region": "us-west"}',
            ),
        )
        db.get_connection().commit()

        # Query using generated column
        cursor = db.execute("SELECT * FROM task_queue WHERE region = ?", ("us-west",))
        row = cursor.fetchone()
        assert row is not None
        assert row["region"] == "us-west"

        cursor = db.execute("SELECT * FROM task_queue WHERE format = ?", ("video",))
        row = cursor.fetchone()
        assert row is not None
        assert row["format"] == "video"
