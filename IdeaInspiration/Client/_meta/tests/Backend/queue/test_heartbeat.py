"""Unit tests for worker heartbeat and monitoring."""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import time

from src.queue import (
    QueueDatabase,
    WorkerHeartbeat,
    Worker,
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
def heartbeat(db):
    """Create a WorkerHeartbeat instance for testing."""
    return WorkerHeartbeat(db, stale_threshold_seconds=300)


class TestHeartbeatUpdate:
    """Test worker heartbeat updates."""

    def test_update_heartbeat_new_worker(self, heartbeat, db):
        """Test creating a new worker with heartbeat."""
        capabilities = {"type": "classifier", "version": "1.0"}
        heartbeat.update_heartbeat("worker-1", capabilities)

        # Verify worker was created
        sql = "SELECT * FROM workers WHERE worker_id = ?"
        cursor = db.execute(sql, ("worker-1",))
        row = cursor.fetchone()

        assert row is not None
        assert row["worker_id"] == "worker-1"
        assert row["capabilities"] == json.dumps(capabilities)
        assert row["heartbeat_utc"] is not None

    def test_update_heartbeat_existing_worker(self, heartbeat, db):
        """Test updating heartbeat for existing worker."""
        # Create initial worker
        capabilities1 = {"type": "classifier"}
        heartbeat.update_heartbeat("worker-1", capabilities1)

        # Get initial heartbeat
        sql = "SELECT heartbeat_utc FROM workers WHERE worker_id = ?"
        cursor = db.execute(sql, ("worker-1",))
        initial_heartbeat = cursor.fetchone()["heartbeat_utc"]

        # Wait a moment and update
        time.sleep(0.1)
        
        # Update with new capabilities
        capabilities2 = {"type": "classifier", "version": "2.0"}
        heartbeat.update_heartbeat("worker-1", capabilities2)

        # Verify heartbeat was updated
        cursor = db.execute(sql, ("worker-1",))
        updated_heartbeat = cursor.fetchone()["heartbeat_utc"]

        # Heartbeat should be different (more recent)
        assert updated_heartbeat >= initial_heartbeat

    def test_update_heartbeat_invalid_capabilities(self, heartbeat):
        """Test updating heartbeat with unserializable capabilities."""
        class CustomClass:
            pass

        capabilities = {"object": CustomClass()}
        
        with pytest.raises(QueueDatabaseError):
            heartbeat.update_heartbeat("worker-1", capabilities)


class TestActiveWorkers:
    """Test active worker detection."""

    def test_get_active_workers_empty(self, heartbeat):
        """Test getting active workers with no workers."""
        workers = heartbeat.get_active_workers()
        assert workers == []

    def test_get_active_workers(self, heartbeat, db):
        """Test getting active workers."""
        # Create workers with recent heartbeat
        heartbeat.update_heartbeat("worker-1", {"type": "classifier"})
        heartbeat.update_heartbeat("worker-2", {"type": "scorer"})

        workers = heartbeat.get_active_workers()
        
        assert len(workers) == 2
        worker_ids = [w.worker_id for w in workers]
        assert "worker-1" in worker_ids
        assert "worker-2" in worker_ids

    def test_get_active_workers_excludes_stale(self, heartbeat, db):
        """Test that stale workers are excluded from active workers."""
        # Create a stale worker (old heartbeat)
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        # Create an active worker
        heartbeat.update_heartbeat("active-worker", {"type": "test"})

        workers = heartbeat.get_active_workers()
        
        # Should only get active worker
        assert len(workers) == 1
        assert workers[0].worker_id == "active-worker"


class TestStaleWorkers:
    """Test stale worker detection."""

    def test_get_stale_workers_empty(self, heartbeat):
        """Test getting stale workers with no workers."""
        workers = heartbeat.get_stale_workers()
        assert workers == []

    def test_get_stale_workers(self, heartbeat, db):
        """Test getting stale workers."""
        # Create a stale worker
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        # Create an active worker
        heartbeat.update_heartbeat("active-worker", {"type": "test"})

        stale_workers = heartbeat.get_stale_workers()
        
        # Should only get stale worker
        assert len(stale_workers) == 1
        assert stale_workers[0].worker_id == "stale-worker"

    def test_custom_stale_threshold(self, db):
        """Test custom stale threshold."""
        # Create heartbeat with very short threshold
        short_heartbeat = WorkerHeartbeat(db, stale_threshold_seconds=1)

        # Create a worker
        short_heartbeat.update_heartbeat("worker-1", {"type": "test"})

        # Worker should be active initially
        active = short_heartbeat.get_active_workers()
        assert len(active) == 1

        # Wait for threshold to pass
        time.sleep(1.5)

        # Worker should now be stale
        stale = short_heartbeat.get_stale_workers()
        assert len(stale) == 1
        assert stale[0].worker_id == "worker-1"


class TestCleanupStaleWorkers:
    """Test stale worker cleanup."""

    def test_cleanup_stale_workers_empty(self, heartbeat):
        """Test cleanup with no workers."""
        deleted = heartbeat.cleanup_stale_workers()
        assert deleted == 0

    def test_cleanup_stale_workers_no_active_tasks(self, heartbeat, db):
        """Test cleanup of stale workers with no active tasks."""
        # Create stale workers
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker-1", '{"type": "test"}'))
        db.execute(sql, ("stale-worker-2", '{"type": "test"}'))

        # Cleanup
        deleted = heartbeat.cleanup_stale_workers()
        assert deleted == 2

        # Verify workers were deleted
        sql = "SELECT COUNT(*) FROM workers"
        cursor = db.execute(sql)
        assert cursor.fetchone()[0] == 0

    def test_cleanup_preserves_workers_with_active_tasks(self, heartbeat, db):
        """Test that stale workers with active tasks are preserved."""
        # Create stale worker
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        # Create active task for this worker
        sql = """
            INSERT INTO task_queue (type, status, locked_by, payload, compatibility)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute(sql, ("test", "processing", "stale-worker", "{}", "{}"))

        # Cleanup (non-force)
        deleted = heartbeat.cleanup_stale_workers(force=False)
        assert deleted == 0

        # Verify worker still exists
        sql = "SELECT COUNT(*) FROM workers"
        cursor = db.execute(sql)
        assert cursor.fetchone()[0] == 1

    def test_cleanup_force_removes_all_stale(self, heartbeat, db):
        """Test force cleanup removes all stale workers."""
        # Create stale worker
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        # Create active task for this worker
        sql = """
            INSERT INTO task_queue (type, status, locked_by, payload, compatibility)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute(sql, ("test", "processing", "stale-worker", "{}", "{}"))

        # Force cleanup
        deleted = heartbeat.cleanup_stale_workers(force=True)
        assert deleted == 1

        # Verify worker was deleted
        sql = "SELECT COUNT(*) FROM workers"
        cursor = db.execute(sql)
        assert cursor.fetchone()[0] == 0

    def test_cleanup_preserves_active_workers(self, heartbeat, db):
        """Test that active workers are not cleaned up."""
        # Create active worker
        heartbeat.update_heartbeat("active-worker", {"type": "test"})

        # Create stale worker
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        # Cleanup
        deleted = heartbeat.cleanup_stale_workers()
        assert deleted == 1

        # Verify active worker still exists
        workers = heartbeat.get_active_workers()
        assert len(workers) == 1
        assert workers[0].worker_id == "active-worker"


class TestWorkerStats:
    """Test worker statistics retrieval."""

    def test_get_worker_stats_basic(self, heartbeat, db):
        """Test getting basic worker stats."""
        # Create worker
        heartbeat.update_heartbeat("worker-1", {"type": "classifier"})

        stats = heartbeat.get_worker_stats("worker-1")
        
        assert stats["worker_id"] == "worker-1"
        assert "classifier" in stats["capabilities"]
        assert stats["is_active"] is True
        assert stats["active_tasks_count"] == 0
        assert stats["total_tasks_processed"] == 0

    def test_get_worker_stats_with_tasks(self, heartbeat, db):
        """Test worker stats with tasks."""
        # Create worker
        heartbeat.update_heartbeat("worker-1", {"type": "test"})

        # Create tasks for this worker
        sql = """
            INSERT INTO task_queue (type, status, locked_by, payload, compatibility)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute(sql, ("test", "processing", "worker-1", "{}", "{}"))
        db.execute(sql, ("test", "completed", "worker-1", "{}", "{}"))
        db.execute(sql, ("test", "completed", "worker-1", "{}", "{}"))
        db.execute(sql, ("test", "failed", "worker-1", "{}", "{}"))

        stats = heartbeat.get_worker_stats("worker-1")
        
        assert stats["active_tasks_count"] == 1  # processing
        assert stats["total_tasks_processed"] == 4
        assert stats["completed_tasks"] == 2
        assert stats["failed_tasks"] == 1
        assert stats["success_rate"] == 0.5  # 2 out of 4

    def test_get_worker_stats_stale_worker(self, heartbeat, db):
        """Test stats for stale worker."""
        # Create stale worker
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        stats = heartbeat.get_worker_stats("stale-worker")
        
        assert stats["worker_id"] == "stale-worker"
        assert stats["is_active"] is False
        assert stats["seconds_since_heartbeat"] > 3000  # More than 1 hour

    def test_get_worker_stats_nonexistent(self, heartbeat):
        """Test getting stats for nonexistent worker."""
        with pytest.raises(QueueDatabaseError):
            heartbeat.get_worker_stats("nonexistent")


class TestWorkersummary:
    """Test all workers summary."""

    def test_get_all_workers_summary_empty(self, heartbeat):
        """Test summary with no workers."""
        summary = heartbeat.get_all_workers_summary()
        assert summary == []

    def test_get_all_workers_summary(self, heartbeat, db):
        """Test getting summary of all workers."""
        # Create active worker
        heartbeat.update_heartbeat("active-worker", {"type": "test"})

        # Create stale worker
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        # Create tasks
        sql = """
            INSERT INTO task_queue (type, status, locked_by, payload, compatibility)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute(sql, ("test", "processing", "active-worker", "{}", "{}"))

        summary = heartbeat.get_all_workers_summary()
        
        assert len(summary) == 2
        
        # Find active worker in summary
        active = next(w for w in summary if w["worker_id"] == "active-worker")
        assert active["is_active"] is True
        assert active["active_tasks"] == 1
        
        # Find stale worker in summary
        stale = next(w for w in summary if w["worker_id"] == "stale-worker")
        assert stale["is_active"] is False


class TestReclaimStaleTasks:
    """Test reclaiming tasks from stale workers."""

    def test_reclaim_stale_worker_tasks_empty(self, heartbeat):
        """Test reclaim with no stale tasks."""
        reclaimed = heartbeat.reclaim_stale_worker_tasks()
        assert reclaimed == 0

    def test_reclaim_stale_worker_tasks(self, heartbeat, db):
        """Test reclaiming tasks from stale workers."""
        # Create stale worker
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        # Create tasks locked by stale worker
        sql = """
            INSERT INTO task_queue (type, status, locked_by, payload, compatibility)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute(sql, ("test", "processing", "stale-worker", "{}", "{}"))
        db.execute(sql, ("test", "processing", "stale-worker", "{}", "{}"))

        # Reclaim tasks
        reclaimed = heartbeat.reclaim_stale_worker_tasks()
        assert reclaimed == 2

        # Verify tasks are now queued and unlocked
        sql = """
            SELECT COUNT(*) FROM task_queue 
            WHERE status = 'queued' AND locked_by IS NULL
        """
        cursor = db.execute(sql)
        assert cursor.fetchone()[0] == 2

    def test_reclaim_increments_attempts(self, heartbeat, db):
        """Test that reclaiming increments attempt counter."""
        # Create stale worker
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now', '-1 hour'))
        """
        db.execute(sql, ("stale-worker", '{"type": "test"}'))

        # Create task with 1 attempt
        sql = """
            INSERT INTO task_queue 
            (type, status, locked_by, attempts, payload, compatibility)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute(sql, ("test", "processing", "stale-worker", 1, "{}", "{}"))

        # Reclaim
        heartbeat.reclaim_stale_worker_tasks()

        # Verify attempts incremented
        sql = "SELECT attempts FROM task_queue WHERE id = 1"
        cursor = db.execute(sql)
        assert cursor.fetchone()[0] == 2

    def test_reclaim_preserves_active_worker_tasks(self, heartbeat, db):
        """Test that tasks from active workers are not reclaimed."""
        # Create active worker
        heartbeat.update_heartbeat("active-worker", {"type": "test"})

        # Create task locked by active worker
        sql = """
            INSERT INTO task_queue (type, status, locked_by, payload, compatibility)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute(sql, ("test", "processing", "active-worker", "{}", "{}"))

        # Reclaim (should not affect active worker's task)
        reclaimed = heartbeat.reclaim_stale_worker_tasks()
        assert reclaimed == 0

        # Verify task still processing
        sql = "SELECT status, locked_by FROM task_queue WHERE id = 1"
        cursor = db.execute(sql)
        row = cursor.fetchone()
        assert row["status"] == "processing"
        assert row["locked_by"] == "active-worker"


class TestWorkerModel:
    """Test Worker model functionality."""

    def test_worker_to_dict(self):
        """Test Worker to_dict conversion."""
        worker = Worker(
            worker_id="worker-1",
            capabilities='{"type": "classifier"}',
            heartbeat_utc=datetime(2025, 1, 1, 12, 0, 0),
        )

        worker_dict = worker.to_dict()
        assert worker_dict["worker_id"] == "worker-1"
        assert worker_dict["capabilities"] == '{"type": "classifier"}'
        assert worker_dict["heartbeat_utc"] is not None

    def test_worker_from_dict(self):
        """Test Worker from_dict creation."""
        data = {
            "worker_id": "worker-1",
            "capabilities": '{"type": "scorer"}',
            "heartbeat_utc": "2025-01-01 12:00:00",
        }

        worker = Worker.from_dict(data)
        assert worker.worker_id == "worker-1"
        assert worker.capabilities == '{"type": "scorer"}'
        assert isinstance(worker.heartbeat_utc, datetime)

    def test_worker_get_capabilities_dict(self):
        """Test parsing capabilities JSON."""
        worker = Worker(
            worker_id="worker-1",
            capabilities='{"type": "classifier", "version": "1.0"}',
        )

        caps = worker.get_capabilities_dict()
        assert caps["type"] == "classifier"
        assert caps["version"] == "1.0"
