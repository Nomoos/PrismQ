"""Unit tests for queue logging and observability integration."""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timezone
import logging

from src.queue import (
    QueueDatabase,
    TaskLogger,
    QueueLogger,
    Task,
    TaskLog,
    QueueDatabaseError,
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
    database.initialize_schema()
    yield database
    database.close()


@pytest.fixture
def task_logger(db):
    """Create a TaskLogger instance for testing."""
    return TaskLogger(db)


@pytest.fixture
def queue_logger(db):
    """Create a QueueLogger instance for testing."""
    return QueueLogger(db)


class TestTaskLogger:
    """Test TaskLogger functionality."""

    def test_log_basic_message(self, task_logger, db):
        """Test logging a basic message."""
        # Insert a test task first
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Log a message
        task_logger.log(task_id, "INFO", "Test message")

        # Verify log was created
        logs = task_logger.get_task_logs(task_id)
        assert len(logs) == 1
        assert logs[0].task_id == task_id
        assert logs[0].level == "INFO"
        assert logs[0].message == "Test message"
        assert logs[0].details is None

    def test_log_with_details(self, task_logger, db):
        """Test logging with additional details."""
        # Insert a test task
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Log with details
        details = {"error": "Network timeout", "attempt": 3}
        task_logger.log(task_id, "ERROR", "Task failed", details)

        # Verify log with details
        logs = task_logger.get_task_logs(task_id)
        assert len(logs) == 1
        assert logs[0].level == "ERROR"
        assert logs[0].details is not None
        
        # Parse details
        details_dict = json.loads(logs[0].details)
        assert details_dict["error"] == "Network timeout"
        assert details_dict["attempt"] == 3

    def test_log_level_validation(self, task_logger, db):
        """Test log level validation and normalization."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Test lowercase level
        task_logger.log(task_id, "info", "Test")
        logs = task_logger.get_task_logs(task_id)
        assert logs[0].level == "INFO"

        # Test invalid level defaults to INFO
        task_logger.log(task_id, "INVALID", "Test")
        logs = task_logger.get_task_logs(task_id, limit=10)
        assert any(log.level == "INFO" for log in logs)

    def test_get_task_logs_with_level_filter(self, task_logger, db):
        """Test retrieving logs filtered by level."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Create logs at different levels
        task_logger.log(task_id, "DEBUG", "Debug message")
        task_logger.log(task_id, "INFO", "Info message")
        task_logger.log(task_id, "ERROR", "Error message")

        # Get only ERROR logs
        error_logs = task_logger.get_task_logs(task_id, level="ERROR")
        assert len(error_logs) == 1
        assert error_logs[0].level == "ERROR"
        assert error_logs[0].message == "Error message"

        # Get all logs
        all_logs = task_logger.get_task_logs(task_id, limit=10)
        assert len(all_logs) == 3

    def test_get_task_logs_limit(self, task_logger, db):
        """Test log retrieval with limit."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Create many logs
        for i in range(10):
            task_logger.log(task_id, "INFO", f"Message {i}")

        # Get limited logs
        logs = task_logger.get_task_logs(task_id, limit=5)
        assert len(logs) == 5

        # Verify order (newest first)
        messages = [log.message for log in logs]
        assert "Message 9" in messages[0]  # Most recent

    def test_get_recent_logs(self, task_logger, db):
        """Test getting recent logs across all tasks."""
        # Create multiple tasks with logs
        for i in range(3):
            sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
            cursor = db.execute(sql, (f"task_{i}", "{}"))
            task_id = cursor.lastrowid
            task_logger.log(task_id, "INFO", f"Task {i} message")

        # Get recent logs
        recent_logs = task_logger.get_recent_logs(limit=10)
        assert len(recent_logs) == 3

    def test_delete_old_logs(self, task_logger, db):
        """Test deletion of old logs."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Create some logs
        for i in range(5):
            task_logger.log(task_id, "INFO", f"Message {i}")

        # Delete logs older than 0 days (should delete none as they're recent)
        deleted = task_logger.delete_old_logs(days=0)
        assert deleted == 0

        # Verify logs still exist
        logs = task_logger.get_task_logs(task_id)
        assert len(logs) == 5

    def test_log_with_unserializable_details(self, task_logger, db):
        """Test logging with unserializable details."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Try to log with unserializable details
        class CustomClass:
            pass

        details = {"object": CustomClass()}
        task_logger.log(task_id, "ERROR", "Test", details)

        # Verify error was handled gracefully
        logs = task_logger.get_task_logs(task_id)
        assert len(logs) == 1
        assert logs[0].details is not None


class TestQueueLogger:
    """Test QueueLogger functionality."""

    def test_log_task_event(self, queue_logger, db):
        """Test logging task event to both database and app logger."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Log an event
        queue_logger.log_task_event(task_id, "INFO", "Event occurred")

        # Verify database log
        logs = queue_logger.task_logger.get_task_logs(task_id)
        assert len(logs) == 1
        assert logs[0].message == "Event occurred"

    def test_log_task_transition(self, queue_logger, db):
        """Test logging task status transitions."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Log a transition
        queue_logger.log_task_transition(task_id, "queued", "processing")

        # Verify log
        logs = queue_logger.task_logger.get_task_logs(task_id)
        assert len(logs) == 1
        assert "queued → processing" in logs[0].message
        assert logs[0].level == "DEBUG"

    def test_log_task_transition_to_failed(self, queue_logger, db):
        """Test logging transition to failed status."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Log transition to failed
        queue_logger.log_task_transition(task_id, "processing", "failed")

        # Verify ERROR level
        logs = queue_logger.task_logger.get_task_logs(task_id)
        assert logs[0].level == "ERROR"

    def test_log_task_error(self, queue_logger, db):
        """Test logging task errors."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Log an error
        error = ValueError("Invalid input")
        queue_logger.log_task_error(task_id, error)

        # Verify error log
        logs = queue_logger.task_logger.get_task_logs(task_id)
        assert len(logs) == 1
        assert logs[0].level == "ERROR"
        assert "ValueError" in logs[0].message

        # Check details
        details = json.loads(logs[0].details)
        assert details["error_type"] == "ValueError"
        assert details["error_message"] == "Invalid input"

    def test_log_task_retry(self, queue_logger, db):
        """Test logging task retry attempts."""
        sql = "INSERT INTO task_queue (type, payload) VALUES (?, ?)"
        cursor = db.execute(sql, ("test_task", "{}"))
        task_id = cursor.lastrowid

        # Log a retry
        next_run = datetime.now(timezone.utc)
        queue_logger.log_task_retry(task_id, 2, 5, next_run)

        # Verify retry log
        logs = queue_logger.task_logger.get_task_logs(task_id)
        assert len(logs) == 1
        assert logs[0].level == "WARNING"
        assert "attempt 2/5" in logs[0].message

        # Check details
        details = json.loads(logs[0].details)
        assert details["attempt"] == 2
        assert details["max_attempts"] == 5

    def test_log_with_custom_logger(self, db):
        """Test QueueLogger with custom application logger."""
        # Create custom logger
        custom_logger = logging.getLogger("test.custom")
        
        # Create QueueLogger with custom logger
        queue_logger = QueueLogger(db, custom_logger)
        
        # Verify custom logger is used
        assert queue_logger.app_logger == custom_logger

    def test_database_logging_failure_handling(self, queue_logger, db):
        """Test graceful handling when database logging fails."""
        # Close the database to cause a failure
        db.close()

        # Attempt to log (should not raise exception)
        try:
            queue_logger.log_task_event(999, "INFO", "Test message")
        except Exception:
            pytest.fail("QueueLogger should handle database failures gracefully")


class TestTaskLogModel:
    """Test TaskLog model functionality."""

    def test_task_log_to_dict(self):
        """Test TaskLog to_dict conversion."""
        log = TaskLog(
            log_id=1,
            task_id=123,
            at_utc=datetime(2025, 1, 1, 12, 0, 0),
            level="INFO",
            message="Test message",
            details='{"key": "value"}',
        )

        log_dict = log.to_dict()
        assert log_dict["log_id"] == 1
        assert log_dict["task_id"] == 123
        assert log_dict["level"] == "INFO"
        assert log_dict["message"] == "Test message"
        assert log_dict["details"] == '{"key": "value"}'

    def test_task_log_from_dict(self):
        """Test TaskLog from_dict creation."""
        data = {
            "log_id": 1,
            "task_id": 123,
            "at_utc": "2025-01-01 12:00:00",
            "level": "ERROR",
            "message": "Error occurred",
            "details": '{"error": "timeout"}',
        }

        log = TaskLog.from_dict(data)
        assert log.log_id == 1
        assert log.task_id == 123
        assert log.level == "ERROR"
        assert log.message == "Error occurred"
        assert log.details == '{"error": "timeout"}'
        assert isinstance(log.at_utc, datetime)
