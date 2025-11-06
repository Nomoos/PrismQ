"""
Tests for QueueWorker - Worker Engine Implementation.

Tests atomic task claiming, worker loop, lease renewal, retry logic,
and dead-letter handling.
"""

import pytest
import time
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "Backend"))

from src.queue import (
    QueueDatabase,
    QueueWorker,
    create_worker,
    Task,
    Worker,
    TaskLog,
    QueueDatabaseError,
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_queue.db"
        yield str(db_path)


@pytest.fixture
def db(temp_db):
    """Create and initialize database."""
    database = QueueDatabase(temp_db)
    database.initialize_schema()
    yield database
    database.close()


@pytest.fixture
def task_results():
    """Shared dictionary to store task execution results."""
    return {"executed": [], "lock": threading.Lock()}


# ==============================================================================
# Test Task Handlers
# ==============================================================================

def success_handler(task: Task) -> bool:
    """Task handler that always succeeds."""
    time.sleep(0.01)  # Simulate work
    return True


def failure_handler(task: Task) -> bool:
    """Task handler that always fails."""
    time.sleep(0.01)
    return False


def exception_handler(task: Task) -> bool:
    """Task handler that raises exception."""
    raise ValueError("Simulated error")


def recording_handler(results: dict):
    """Create a task handler that records execution."""
    def handler(task: Task) -> bool:
        with results["lock"]:
            results["executed"].append(task.id)
        time.sleep(0.05)  # Simulate work
        return True
    return handler


# ==============================================================================
# Test Worker Initialization
# ==============================================================================

class TestWorkerInitialization:
    """Test worker initialization and configuration."""
    
    def test_worker_creation(self, temp_db):
        """Test creating a worker."""
        worker = QueueWorker(
            worker_id="test-worker",
            task_handler=success_handler,
            db_path=temp_db
        )
        
        assert worker.worker_id == "test-worker"
        assert worker.capabilities == {}
        assert worker.lease_duration_seconds == 300
        assert not worker._running
    
    def test_worker_with_capabilities(self, temp_db):
        """Test worker with capabilities."""
        capabilities = {"cpu": 8, "gpu": "RTX5090"}
        worker = QueueWorker(
            worker_id="capable-worker",
            task_handler=success_handler,
            capabilities=capabilities,
            db_path=temp_db
        )
        
        assert worker.capabilities == capabilities
    
    def test_create_worker_helper(self, temp_db):
        """Test create_worker helper function."""
        worker = create_worker(
            "helper-worker",
            success_handler,
            capabilities={"gpu": True},
            db_path=temp_db
        )
        
        assert isinstance(worker, QueueWorker)
        assert worker.worker_id == "helper-worker"
        assert worker.capabilities == {"gpu": True}


# ==============================================================================
# Test Task Claiming
# ==============================================================================

class TestTaskClaiming:
    """Test atomic task claiming."""
    
    def test_claim_single_task(self, db, temp_db, task_results):
        """Test claiming a single task."""
        # Insert a task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                ("test_task", "{}", 100)
            )
        
        # Create worker
        handler = recording_handler(task_results)
        worker = QueueWorker(
            "test-worker",
            handler,
            db_path=temp_db,
            poll_interval_seconds=0.1
        )
        
        # Start worker in thread
        worker_thread = threading.Thread(target=worker.start, daemon=True)
        worker_thread.start()
        
        # Wait for task execution
        time.sleep(0.5)
        worker.stop()
        worker_thread.join(timeout=2)
        
        # Verify task was executed
        with task_results["lock"]:
            assert len(task_results["executed"]) == 1
        
        # Verify task status
        cursor = db.execute("SELECT status FROM task_queue WHERE id = 1")
        row = cursor.fetchone()
        assert row["status"] == "completed"
    
    def test_no_double_claiming(self, db, temp_db, task_results):
        """Test that two workers don't claim the same task."""
        # Insert a task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                ("test_task", "{}", 100)
            )
        
        # Create two workers
        handler = recording_handler(task_results)
        worker1 = QueueWorker("worker1", handler, db_path=temp_db, poll_interval_seconds=0.05)
        worker2 = QueueWorker("worker2", handler, db_path=temp_db, poll_interval_seconds=0.05)
        
        # Start both workers
        thread1 = threading.Thread(target=worker1.start, daemon=True)
        thread2 = threading.Thread(target=worker2.start, daemon=True)
        thread1.start()
        thread2.start()
        
        # Wait for execution
        time.sleep(0.5)
        worker1.stop()
        worker2.stop()
        thread1.join(timeout=2)
        thread2.join(timeout=2)
        
        # Verify task executed exactly once
        with task_results["lock"]:
            assert len(task_results["executed"]) == 1
    
    def test_claim_respects_run_after(self, db, temp_db):
        """Test that tasks with run_after are not claimed prematurely."""
        # Insert task with future run_after
        future_time = (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, run_after_utc)
                VALUES (?, ?, ?, ?)
                """,
                ("future_task", "{}", 100, future_time)
            )
        
        # Create worker
        worker = QueueWorker(
            "test-worker",
            success_handler,
            db_path=temp_db,
            poll_interval_seconds=0.1
        )
        
        # Try to claim task
        task = worker._claim_task()
        
        # Should not claim future task
        assert task is None
    
    def test_claim_respects_max_attempts(self, db, temp_db):
        """Test that tasks at max_attempts are not claimed."""
        # Insert task already at max attempts
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, attempts, max_attempts)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("exhausted_task", "{}", 100, 5, 5)
            )
        
        # Create worker
        worker = QueueWorker(
            "test-worker",
            success_handler,
            db_path=temp_db
        )
        
        # Try to claim task
        task = worker._claim_task()
        
        # Should not claim exhausted task
        assert task is None


# ==============================================================================
# Test Capability Matching
# ==============================================================================

class TestCapabilityMatching:
    """Test capability-based task filtering."""
    
    def test_task_without_requirements(self, temp_db):
        """Test claiming task without capability requirements."""
        db = QueueDatabase(temp_db)
        db.initialize_schema()
        
        # Insert task without compatibility
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
                ("any_task", "{}")
            )
        
        # Worker with capabilities
        worker = QueueWorker(
            "test-worker",
            success_handler,
            capabilities={"gpu": True},
            db_path=temp_db
        )
        
        # Should be able to claim
        task = worker._claim_task()
        assert task is not None
        
        db.close()
    
    def test_matching_capabilities(self, temp_db):
        """Test claiming task with matching capabilities."""
        db = QueueDatabase(temp_db)
        db.initialize_schema()
        
        # Insert task requiring GPU
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, compatibility)
                VALUES (?, ?, ?)
                """,
                ("gpu_task", "{}", '{"gpu": true}')
            )
        
        # Worker with GPU capability
        worker = QueueWorker(
            "gpu-worker",
            success_handler,
            capabilities={"gpu": True},
            db_path=temp_db
        )
        
        # Should claim task
        task = worker._claim_task()
        assert task is not None
        
        db.close()
    
    def test_mismatched_capabilities(self, temp_db):
        """Test not claiming task with mismatched capabilities."""
        db = QueueDatabase(temp_db)
        db.initialize_schema()
        
        # Insert task requiring GPU
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, compatibility)
                VALUES (?, ?, ?)
                """,
                ("gpu_task", "{}", '{"gpu": true}')
            )
        
        # Worker without GPU
        worker = QueueWorker(
            "cpu-worker",
            success_handler,
            capabilities={"gpu": False},
            db_path=temp_db
        )
        
        # Should not claim task
        task = worker._claim_task()
        assert task is None
        
        db.close()


# ==============================================================================
# Test Lease Management
# ==============================================================================

class TestLeaseManagement:
    """Test lease-based task locking."""
    
    def test_lease_set_on_claim(self, db, temp_db):
        """Test that lease is set when task is claimed."""
        # Insert task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
                ("test_task", "{}")
            )
        
        # Claim task
        worker = QueueWorker(
            "test-worker",
            success_handler,
            db_path=temp_db,
            lease_duration_seconds=60
        )
        task = worker._claim_task()
        
        assert task is not None
        assert task.lease_until_utc is not None
        assert task.locked_by == "test-worker"
        
        # Lease should be ~60 seconds in future
        # task.lease_until_utc is already a datetime object
        lease_time = task.lease_until_utc
        now = datetime.now(timezone.utc)
        lease_delta = (lease_time - now).total_seconds()
        
        assert 55 < lease_delta < 65  # Allow some tolerance
    
    def test_expired_lease_reclaimed(self, temp_db):
        """Test that tasks with expired leases can be reclaimed."""
        # Create database and add task
        db = QueueDatabase(temp_db)
        db.initialize_schema()
        
        # Insert task with expired lease
        past_time = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (
                    type, payload, status, locked_by, lease_until_utc, run_after_utc
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("stale_task", "{}", "processing", "old-worker", past_time, past_time)
            )
        db.close()
        
        # New worker should be able to claim
        worker = QueueWorker(
            "new-worker",
            success_handler,
            db_path=temp_db
        )
        
        task = worker._claim_task()
        assert task is not None
        assert task.locked_by == "new-worker"
        worker.db.close()


# ==============================================================================
# Test Retry Logic
# ==============================================================================

class TestRetryLogic:
    """Test retry with exponential backoff."""
    
    def test_task_retry_on_failure(self, db, temp_db):
        """Test that failed tasks are retried."""
        # Insert task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, max_attempts) VALUES (?, ?, ?)",
                ("retry_task", "{}", 3)
            )
        
        # Worker that fails
        worker = QueueWorker(
            "fail-worker",
            failure_handler,
            db_path=temp_db,
            poll_interval_seconds=0.1
        )
        
        # Start worker
        worker_thread = threading.Thread(target=worker.start, daemon=True)
        worker_thread.start()
        
        # Let it fail
        time.sleep(0.3)
        worker.stop()
        worker_thread.join(timeout=2)
        
        # Check task status - should be queued for retry
        cursor = db.execute("SELECT status, attempts FROM task_queue WHERE id = 1")
        row = cursor.fetchone()
        
        assert row["status"] == "queued"  # Retry
        assert row["attempts"] == 1  # First attempt failed
    
    def test_exponential_backoff(self, temp_db):
        """Test that retry delay increases exponentially."""
        # This test verifies the retry delay calculation
        # We'll insert a task, fail it, and check the run_after_utc gets set correctly
        
        db = QueueDatabase(temp_db)
        db.initialize_schema()
        
        worker = QueueWorker("test-worker", failure_handler, db_path=temp_db)
        
        for attempt in range(1, 4):
            # Insert or reset task for each attempt
            if attempt == 1:
                with db.transaction() as conn:
                    conn.execute(
                        "INSERT INTO task_queue (type, payload, max_attempts) VALUES (?, ?, ?)",
                        ("backoff_task", "{}", 5)
                    )
                task_id = 1
            else:
                # For subsequent attempts, update existing task to be claimable
                past_time = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
                with db.transaction() as conn:
                    conn.execute(
                        """
                        UPDATE task_queue 
                        SET run_after_utc = ?, status = 'queued'
                        WHERE id = ?
                        """,
                        (past_time, task_id)
                    )
                db.close()
                # Recreate worker connection
                worker.db.close()
                worker = QueueWorker("test-worker", failure_handler, db_path=temp_db)
                db = QueueDatabase(temp_db)
            
            # Claim and fail the task
            task = worker._claim_task()
            assert task is not None, f"Failed to claim task on attempt {attempt}"
            worker._mark_task_failed(task, f"Attempt {attempt} failed")
            
            # Check run_after delay
            cursor = db.execute(
                "SELECT run_after_utc, attempts FROM task_queue WHERE id = ?",
                (task_id,)
            )
            row = cursor.fetchone()
            
            if row["run_after_utc"]:
                # Parse datetime - could be datetime object or string
                run_after_val = row["run_after_utc"]
                if isinstance(run_after_val, str):
                    run_after = datetime.fromisoformat(
                        run_after_val.replace("Z", "+00:00")
                    )
                else:
                    run_after = run_after_val
                
                now = datetime.now(timezone.utc)
                delay = (run_after - now).total_seconds()
                
                # Delay should roughly match 2^(attempts-1) * 60, max 3600
                expected_delay = min(60 * (2 ** (attempt - 1)), 3600)
                
                # Allow ±20% tolerance for timing variations
                assert expected_delay * 0.8 < delay < expected_delay * 1.2, \
                    f"Attempt {attempt}: expected ~{expected_delay}s, got {delay}s"
        
        db.close()
        worker.db.close()


# ==============================================================================
# Test Dead-Letter Handling
# ==============================================================================

class TestDeadLetterHandling:
    """Test dead-letter queue for permanently failed tasks."""
    
    def test_max_attempts_reached(self, temp_db):
        """Test that tasks move to failed status after max attempts."""
        # Create database and insert task with low max_attempts
        db = QueueDatabase(temp_db)
        db.initialize_schema()
        
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, max_attempts) VALUES (?, ?, ?)",
                ("doomed_task", "{}", 2)
            )
        
        # Worker that always fails
        worker = QueueWorker("fail-worker", failure_handler, db_path=temp_db)
        
        # Fail it twice
        for i in range(2):
            # For second attempt, update task to be claimable
            if i > 0:
                db.close()
                worker.db.close()
                
                # Update via new connection
                temp_db_obj = QueueDatabase(temp_db)
                past_time = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
                with temp_db_obj.transaction() as conn:
                    conn.execute(
                        """
                        UPDATE task_queue 
                        SET run_after_utc = ?, status = 'queued'
                        WHERE id = 1
                        """,
                        (past_time,)
                    )
                temp_db_obj.close()
                
                # Recreate connections
                db = QueueDatabase(temp_db)
                worker = QueueWorker("fail-worker", failure_handler, db_path=temp_db)
            
            task = worker._claim_task()
            assert task is not None, f"Failed to claim task on attempt {i+1}"
            worker._mark_task_failed(task, "Failed")
            time.sleep(0.05)
        
        # Check final status
        cursor = db.execute("SELECT status, attempts FROM task_queue WHERE id = 1")
        row = cursor.fetchone()
        
        assert row["status"] == "failed"  # Dead-letter
        assert row["attempts"] == 2  # Max attempts reached
        
        db.close()
        worker.db.close()
    
    def test_dead_letter_not_reclaimed(self, db, temp_db):
        """Test that failed tasks are not claimed again."""
        # Insert failed task
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (
                    type, payload, status, attempts, max_attempts
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                ("dead_task", "{}", "failed", 3, 3)
            )
        
        # Worker should not claim it
        worker = QueueWorker("test-worker", success_handler, db_path=temp_db)
        task = worker._claim_task()
        
        assert task is None


# ==============================================================================
# Test Task Execution
# ==============================================================================

class TestTaskExecution:
    """Test task execution lifecycle."""
    
    def test_successful_execution(self, db, temp_db):
        """Test successful task execution."""
        # Insert task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
                ("success_task", "{}")
            )
        
        # Execute
        worker = QueueWorker("test-worker", success_handler, db_path=temp_db)
        task = worker._claim_task()
        worker._execute_task(task)
        
        # Verify completion
        cursor = db.execute("SELECT status FROM task_queue WHERE id = 1")
        row = cursor.fetchone()
        assert row["status"] == "completed"
    
    def test_failed_execution(self, db, temp_db):
        """Test failed task execution."""
        # Insert task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, max_attempts) VALUES (?, ?, ?)",
                ("fail_task", "{}", 3)
            )
        
        # Execute
        worker = QueueWorker("test-worker", failure_handler, db_path=temp_db)
        task = worker._claim_task()
        worker._execute_task(task)
        
        # Verify retry queued
        cursor = db.execute("SELECT status FROM task_queue WHERE id = 1")
        row = cursor.fetchone()
        assert row["status"] == "queued"
    
    def test_exception_handling(self, db, temp_db):
        """Test exception handling during execution."""
        # Insert task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, max_attempts) VALUES (?, ?, ?)",
                ("exception_task", "{}", 3)
            )
        
        # Execute
        worker = QueueWorker("test-worker", exception_handler, db_path=temp_db)
        task = worker._claim_task()
        worker._execute_task(task)
        
        # Verify error recorded
        cursor = db.execute("SELECT error_message FROM task_queue WHERE id = 1")
        row = cursor.fetchone()
        assert "Simulated error" in row["error_message"]


# ==============================================================================
# Test Worker Lifecycle
# ==============================================================================

class TestWorkerLifecycle:
    """Test worker start/stop and cleanup."""
    
    def test_worker_registration(self, db, temp_db):
        """Test that worker registers itself."""
        worker = QueueWorker(
            "reg-worker",
            success_handler,
            capabilities={"test": True},
            db_path=temp_db
        )
        
        worker._register_worker()
        
        # Verify registration
        cursor = db.execute("SELECT * FROM workers WHERE worker_id = ?", ("reg-worker",))
        row = cursor.fetchone()
        
        assert row is not None
        assert row["worker_id"] == "reg-worker"
        assert '"test": true' in row["capabilities"].lower()
    
    def test_graceful_shutdown(self, db, temp_db, task_results):
        """Test graceful shutdown."""
        # Insert task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
                ("shutdown_task", "{}")
            )
        
        # Start worker
        handler = recording_handler(task_results)
        worker = QueueWorker(
            "shutdown-worker",
            handler,
            db_path=temp_db,
            poll_interval_seconds=0.1
        )
        
        worker_thread = threading.Thread(target=worker.start, daemon=True)
        worker_thread.start()
        
        # Let it run briefly
        time.sleep(0.3)
        
        # Stop gracefully
        worker.stop()
        worker_thread.join(timeout=2)
        
        # Thread should have exited
        assert not worker_thread.is_alive()


# ==============================================================================
# Test Task Logging
# ==============================================================================

class TestTaskLogging:
    """Test task log creation."""
    
    def test_logs_created(self, db, temp_db):
        """Test that task logs are created during execution."""
        # Insert task
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
                ("logged_task", "{}")
            )
        
        # Execute
        worker = QueueWorker("log-worker", success_handler, db_path=temp_db)
        task = worker._claim_task()
        worker._execute_task(task)
        
        # Check logs
        cursor = db.execute("SELECT COUNT(*) as count FROM task_logs WHERE task_id = 1")
        row = cursor.fetchone()
        
        # Should have at least claimed and completed logs
        assert row["count"] >= 2


# ==============================================================================
# Test Integration
# ==============================================================================

class TestIntegration:
    """Integration tests for complete workflow."""
    
    def test_multiple_tasks_execution(self, db, temp_db, task_results):
        """Test executing multiple tasks."""
        # Insert 5 tasks
        with db.transaction() as conn:
            for i in range(5):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                    (f"task_{i}", "{}", 100)
                )
        
        # Start worker
        handler = recording_handler(task_results)
        worker = QueueWorker(
            "multi-worker",
            handler,
            db_path=temp_db,
            poll_interval_seconds=0.05
        )
        
        worker_thread = threading.Thread(target=worker.start, daemon=True)
        worker_thread.start()
        
        # Wait for all tasks
        time.sleep(1.5)
        worker.stop()
        worker_thread.join(timeout=2)
        
        # All should be executed
        with task_results["lock"]:
            assert len(task_results["executed"]) == 5
    
    def test_concurrent_workers(self, db, temp_db, task_results):
        """Test multiple workers processing tasks concurrently."""
        # Insert 10 tasks
        with db.transaction() as conn:
            for i in range(10):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                    (f"concurrent_task_{i}", "{}", 100)
                )
        
        # Create 3 workers
        handler = recording_handler(task_results)
        workers = []
        threads = []
        
        for i in range(3):
            worker = QueueWorker(
                f"concurrent-worker-{i}",
                handler,
                db_path=temp_db,
                poll_interval_seconds=0.05
            )
            workers.append(worker)
            
            thread = threading.Thread(target=worker.start, daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for all tasks
        time.sleep(2)
        
        # Stop all workers
        for worker in workers:
            worker.stop()
        for thread in threads:
            thread.join(timeout=2)
        
        # All 10 tasks should be executed exactly once
        with task_results["lock"]:
            assert len(task_results["executed"]) == 10
            # No duplicates
            assert len(set(task_results["executed"])) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
