"""Unit tests for retry logic and worker engine (Issue #326)."""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime

from src.queue import (
    QueueDatabase,
    Task,
    TaskExecutor,
    WorkerEngine,
    RetryConfig,
    SchedulingStrategy,
    QueueDatabaseError,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_retry_queue.db"


@pytest.fixture
def db(temp_db_path):
    """Create a QueueDatabase instance for testing."""
    database = QueueDatabase(str(temp_db_path))
    database.initialize_schema()
    yield database
    database.close()


@pytest.fixture
def executor(db):
    """Create a TaskExecutor instance for testing."""
    return TaskExecutor(db)


class TestTaskExecutor:
    """Test TaskExecutor task lifecycle operations."""

    def test_complete_task_success(self, db, executor):
        """Test successfully completing a task."""
        # Insert and claim a task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, status, locked_by)
                VALUES (?, ?, 'leased', ?)
                """,
                ("test_task", "{}", "worker-1")
            )
            cursor = conn.execute("SELECT id FROM task_queue WHERE type = ?", ("test_task",))
            task_id = cursor.fetchone()['id']
        
        # Complete the task
        result = executor.complete_task(task_id)
        assert result is True
        
        # Verify task is completed
        cursor = db.execute("SELECT status, finished_at_utc FROM task_queue WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        assert row['status'] == 'completed'
        assert row['finished_at_utc'] is not None

    def test_complete_task_not_found(self, executor):
        """Test completing a non-existent task."""
        result = executor.complete_task(99999)
        assert result is False

    def test_complete_task_already_completed(self, db, executor):
        """Test completing an already completed task."""
        # Insert a completed task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, status)
                VALUES (?, ?, 'completed')
                """,
                ("test_task", "{}")
            )
            cursor = conn.execute("SELECT id FROM task_queue WHERE type = ?", ("test_task",))
            task_id = cursor.fetchone()['id']
        
        # Try to complete it again
        result = executor.complete_task(task_id)
        assert result is False

    def test_fail_task_with_retry(self, db, executor):
        """Test failing a task with retry (requeue with backoff)."""
        # Insert and claim a task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, status, locked_by, attempts, max_attempts)
                VALUES (?, ?, 'leased', ?, 0, 3)
                """,
                ("test_task", "{}", "worker-1")
            )
            cursor = conn.execute("SELECT id FROM task_queue WHERE type = ?", ("test_task",))
            task_id = cursor.fetchone()['id']
        
        # Fail the task with retry
        error_msg = "Test error message"
        result = executor.fail_task(task_id, error_msg, retry=True)
        assert result is True
        
        # Verify task is requeued
        cursor = db.execute(
            "SELECT status, attempts, error_message, run_after_utc FROM task_queue WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        assert row['status'] == 'queued'
        assert row['attempts'] == 1
        assert row['error_message'] == error_msg
        assert row['run_after_utc'] is not None

    def test_fail_task_max_attempts_reached(self, db, executor):
        """Test failing a task when max attempts reached (dead-letter)."""
        # Insert a task that's already at max attempts
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, status, locked_by, attempts, max_attempts)
                VALUES (?, ?, 'leased', ?, 2, 3)
                """,
                ("test_task", "{}", "worker-1")
            )
            cursor = conn.execute("SELECT id FROM task_queue WHERE type = ?", ("test_task",))
            task_id = cursor.fetchone()['id']
        
        # Fail the task - should move to dead-letter
        error_msg = "Final failure"
        result = executor.fail_task(task_id, error_msg, retry=True)
        assert result is True
        
        # Verify task is in dead-letter (failed status)
        cursor = db.execute(
            "SELECT status, attempts, error_message, finished_at_utc FROM task_queue WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        assert row['status'] == 'failed'
        assert row['attempts'] == 3
        assert row['error_message'] == error_msg
        assert row['finished_at_utc'] is not None

    def test_fail_task_no_retry(self, db, executor):
        """Test failing a task without retry (immediate dead-letter)."""
        # Insert and claim a task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, status, locked_by, attempts, max_attempts)
                VALUES (?, ?, 'leased', ?, 0, 3)
                """,
                ("test_task", "{}", "worker-1")
            )
            cursor = conn.execute("SELECT id FROM task_queue WHERE type = ?", ("test_task",))
            task_id = cursor.fetchone()['id']
        
        # Fail the task without retry
        error_msg = "Non-retryable error"
        result = executor.fail_task(task_id, error_msg, retry=False)
        assert result is True
        
        # Verify task is immediately failed
        cursor = db.execute(
            "SELECT status, attempts, error_message FROM task_queue WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        assert row['status'] == 'failed'
        assert row['attempts'] == 1
        assert row['error_message'] == error_msg

    def test_renew_lease_success(self, db, executor):
        """Test successfully renewing a task lease."""
        # Insert a leased task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, status, locked_by)
                VALUES (?, ?, 'leased', ?)
                """,
                ("test_task", "{}", "worker-1")
            )
            cursor = conn.execute("SELECT id FROM task_queue WHERE type = ?", ("test_task",))
            task_id = cursor.fetchone()['id']
        
        # Renew lease
        result = executor.renew_lease(task_id, 120)
        assert result is True
        
        # Verify lease was updated
        cursor = db.execute("SELECT lease_until_utc FROM task_queue WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        assert row['lease_until_utc'] is not None

    def test_renew_lease_not_leased(self, db, executor):
        """Test renewing lease on a non-leased task."""
        # Insert a queued task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, status)
                VALUES (?, ?, 'queued')
                """,
                ("test_task", "{}")
            )
            cursor = conn.execute("SELECT id FROM task_queue WHERE type = ?", ("test_task",))
            task_id = cursor.fetchone()['id']
        
        # Try to renew lease
        result = executor.renew_lease(task_id, 120)
        assert result is False

    def test_exponential_backoff_calculation(self, executor):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(
            initial_delay_seconds=1.0,
            max_delay_seconds=60.0,
            backoff_multiplier=2.0,
            jitter_factor=0.0  # Disable jitter for predictable testing
        )
        
        # Test backoff progression
        delay_1 = executor._calculate_backoff_delay(1, config)
        delay_2 = executor._calculate_backoff_delay(2, config)
        delay_3 = executor._calculate_backoff_delay(3, config)
        
        # Should double each time (no jitter)
        assert 0.9 <= delay_1 <= 1.1  # ~1 second
        assert 1.8 <= delay_2 <= 2.2  # ~2 seconds
        assert 3.6 <= delay_3 <= 4.4  # ~4 seconds

    def test_exponential_backoff_max_cap(self, executor):
        """Test that backoff is capped at max_delay."""
        config = RetryConfig(
            initial_delay_seconds=10.0,
            max_delay_seconds=30.0,
            backoff_multiplier=2.0,
            jitter_factor=0.0
        )
        
        # High attempt number should be capped
        delay = executor._calculate_backoff_delay(10, config)
        assert delay <= 30.0


class TestWorkerEngine:
    """Test WorkerEngine task processing with retry."""

    def test_claim_and_process_success(self, db):
        """Test claiming and successfully processing a task."""
        # Insert a task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority)
                VALUES (?, ?, ?)
                """,
                ("test_task", '{"data": "test"}', 100)
            )
        
        # Create worker engine
        worker = WorkerEngine(
            db=db,
            worker_id="test-worker",
            scheduling_strategy=SchedulingStrategy.FIFO
        )
        
        # Track task execution
        executed_tasks = []
        
        def task_handler(task: Task):
            executed_tasks.append(task)
        
        # Claim and process
        result = worker.claim_and_process(task_handler)
        assert result is True
        assert len(executed_tasks) == 1
        
        # Verify task is completed
        cursor = db.execute("SELECT status FROM task_queue WHERE type = ?", ("test_task",))
        row = cursor.fetchone()
        assert row['status'] == 'completed'

    def test_claim_and_process_failure_with_retry(self, db):
        """Test claiming and processing a task that fails with retry."""
        # Insert a task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, 3)
                """,
                ("test_task", '{"data": "test"}', 100)
            )
        
        # Create worker engine
        worker = WorkerEngine(
            db=db,
            worker_id="test-worker",
            scheduling_strategy=SchedulingStrategy.FIFO
        )
        
        # Task handler that always fails
        def failing_handler(task: Task):
            raise ValueError("Task processing failed")
        
        # Claim and process - should fail and requeue
        result = worker.claim_and_process(failing_handler)
        assert result is True
        
        # Verify task is requeued
        cursor = db.execute(
            "SELECT status, attempts, error_message FROM task_queue WHERE type = ?",
            ("test_task",)
        )
        row = cursor.fetchone()
        assert row['status'] == 'queued'
        assert row['attempts'] == 1
        assert 'ValueError' in row['error_message']

    def test_claim_and_process_no_tasks(self, db):
        """Test claiming when no tasks are available."""
        worker = WorkerEngine(
            db=db,
            worker_id="test-worker",
            scheduling_strategy=SchedulingStrategy.FIFO
        )
        
        def task_handler(task: Task):
            pass
        
        # Should return False when no tasks available
        result = worker.claim_and_process(task_handler)
        assert result is False

    def test_run_loop_with_max_iterations(self, db):
        """Test worker loop with maximum iterations."""
        # Insert multiple tasks
        with db.transaction() as conn:
            for i in range(5):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                    (f"task_{i}", "{}", 100)
                )
        
        worker = WorkerEngine(
            db=db,
            worker_id="test-worker",
            scheduling_strategy=SchedulingStrategy.FIFO,
            poll_interval_seconds=0.01  # Fast polling for testing
        )
        
        executed_tasks = []
        
        def task_handler(task: Task):
            executed_tasks.append(task)
        
        # Run loop for max 3 iterations
        worker.run_loop(task_handler, max_iterations=3)
        
        # Should have processed 3 tasks
        assert len(executed_tasks) == 3
        
        # Verify 3 tasks are completed
        cursor = db.execute("SELECT COUNT(*) as count FROM task_queue WHERE status = 'completed'")
        count = cursor.fetchone()['count']
        assert count == 3

    def test_worker_stop(self, db):
        """Test stopping worker loop."""
        worker = WorkerEngine(
            db=db,
            worker_id="test-worker",
            poll_interval_seconds=0.1
        )
        
        def task_handler(task: Task):
            pass
        
        # Start worker in separate thread and stop after short delay
        import threading
        
        def run_worker():
            worker.run_loop(task_handler)
        
        thread = threading.Thread(target=run_worker)
        thread.start()
        
        # Stop worker after short delay
        time.sleep(0.2)
        worker.stop()
        thread.join(timeout=1.0)
        
        # Thread should have stopped
        assert not thread.is_alive()


class TestRetryIntegration:
    """Integration tests for retry logic."""

    def test_task_retry_progression(self, db):
        """Test full retry progression from queued to dead-letter."""
        # Insert a task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, 3)
                """,
                ("retry_test", "{}", 100)
            )
        
        worker = WorkerEngine(
            db=db,
            worker_id="retry-worker",
            scheduling_strategy=SchedulingStrategy.FIFO
        )
        
        # Task handler that always fails
        def failing_handler(task: Task):
            raise RuntimeError("Simulated failure")
        
        # First attempt
        result = worker.claim_and_process(failing_handler)
        assert result is True
        
        cursor = db.execute("SELECT status, attempts FROM task_queue WHERE type = ?", ("retry_test",))
        row = cursor.fetchone()
        assert row['status'] == 'queued'
        assert row['attempts'] == 1
        
        # Second attempt (need to wait for run_after_utc to pass)
        # For testing, we'll manually update run_after_utc
        with db.transaction() as conn:
            conn.execute(
                "UPDATE task_queue SET run_after_utc = datetime('now', '-1 seconds') WHERE type = ?",
                ("retry_test",)
            )
        
        result = worker.claim_and_process(failing_handler)
        assert result is True
        
        cursor = db.execute("SELECT status, attempts FROM task_queue WHERE type = ?", ("retry_test",))
        row = cursor.fetchone()
        assert row['status'] == 'queued'
        assert row['attempts'] == 2
        
        # Third attempt - should move to dead-letter
        with db.transaction() as conn:
            conn.execute(
                "UPDATE task_queue SET run_after_utc = datetime('now', '-1 seconds') WHERE type = ?",
                ("retry_test",)
            )
        
        result = worker.claim_and_process(failing_handler)
        assert result is True
        
        cursor = db.execute("SELECT status, attempts FROM task_queue WHERE type = ?", ("retry_test",))
        row = cursor.fetchone()
        assert row['status'] == 'failed'  # Dead-letter
        assert row['attempts'] == 3

    def test_mixed_success_and_failure(self, db):
        """Test processing mix of successful and failing tasks."""
        # Insert successful and failing tasks
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                ("success_task", '{"will_succeed": true}', 100)
            )
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                ("fail_task", '{"will_succeed": false}', 100)
            )
        
        worker = WorkerEngine(
            db=db,
            worker_id="mixed-worker",
            scheduling_strategy=SchedulingStrategy.FIFO
        )
        
        def conditional_handler(task: Task):
            import json
            payload = json.loads(task.payload)
            if not payload.get('will_succeed', True):
                raise ValueError("Task configured to fail")
        
        # Process both tasks
        worker.claim_and_process(conditional_handler)
        worker.claim_and_process(conditional_handler)
        
        # Check statuses
        cursor = db.execute("SELECT type, status FROM task_queue ORDER BY type")
        results = {row['type']: row['status'] for row in cursor}
        
        assert results['success_task'] == 'completed'
        assert results['fail_task'] == 'queued'  # Requeued for retry
