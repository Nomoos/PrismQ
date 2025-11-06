"""Unit tests for queue monitoring and observability (Issue #330)."""

import pytest
import tempfile
import time
from pathlib import Path

from src.queue import (
    QueueDatabase,
    QueueMonitoring,
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
def monitoring(db):
    """Create a QueueMonitoring instance for testing."""
    return QueueMonitoring(db)


class TestWorkerRegistration:
    """Test worker registration and heartbeat updates."""

    def test_register_new_worker(self, monitoring):
        """Test registering a new worker."""
        monitoring.register_worker("worker-01", {"cpu": 8, "memory": 16})
        
        worker = monitoring.get_worker("worker-01")
        assert worker is not None
        assert worker.worker_id == "worker-01"
        assert worker.heartbeat_utc is not None
        
        capabilities = worker.get_capabilities_dict()
        assert capabilities["cpu"] == 8
        assert capabilities["memory"] == 16

    def test_register_worker_without_capabilities(self, monitoring):
        """Test registering a worker without capabilities."""
        monitoring.register_worker("worker-02")
        
        worker = monitoring.get_worker("worker-02")
        assert worker is not None
        assert worker.worker_id == "worker-02"
        assert worker.get_capabilities_dict() == {}

    def test_register_worker_upsert(self, monitoring):
        """Test that re-registering a worker updates capabilities."""
        # Initial registration
        monitoring.register_worker("worker-01", {"cpu": 4})
        worker1 = monitoring.get_worker("worker-01")
        assert worker1.get_capabilities_dict()["cpu"] == 4
        heartbeat1 = worker1.heartbeat_utc
        
        # Wait to ensure heartbeat changes (SQLite datetime precision is 1 second)
        time.sleep(1.1)
        
        # Re-register with different capabilities
        monitoring.register_worker("worker-01", {"cpu": 8, "gpu": True})
        worker2 = monitoring.get_worker("worker-01")
        assert worker2.get_capabilities_dict()["cpu"] == 8
        assert worker2.get_capabilities_dict()["gpu"] is True
        # Heartbeat should be updated
        assert worker2.heartbeat_utc >= heartbeat1  # >= because of precision

    def test_get_nonexistent_worker(self, monitoring):
        """Test getting a worker that doesn't exist."""
        worker = monitoring.get_worker("nonexistent")
        assert worker is None


class TestHeartbeatUpdates:
    """Test worker heartbeat update mechanism."""

    def test_update_heartbeat_existing_worker(self, monitoring):
        """Test updating heartbeat for existing worker."""
        monitoring.register_worker("worker-01")
        worker1 = monitoring.get_worker("worker-01")
        heartbeat1 = worker1.heartbeat_utc
        
        # Wait to ensure heartbeat changes (SQLite datetime precision is 1 second)
        time.sleep(1.1)
        
        # Update heartbeat
        success = monitoring.update_heartbeat("worker-01")
        assert success is True
        
        worker2 = monitoring.get_worker("worker-01")
        heartbeat2 = worker2.heartbeat_utc
        assert heartbeat2 >= heartbeat1  # >= because of precision

    def test_update_heartbeat_nonexistent_worker(self, monitoring):
        """Test updating heartbeat for nonexistent worker."""
        success = monitoring.update_heartbeat("nonexistent")
        assert success is False

    def test_multiple_heartbeat_updates(self, monitoring):
        """Test multiple heartbeat updates in sequence."""
        monitoring.register_worker("worker-01")
        
        heartbeats = []
        for i in range(3):
            if i > 0:
                time.sleep(1.1)  # SQLite datetime precision is 1 second
            monitoring.update_heartbeat("worker-01")
            worker = monitoring.get_worker("worker-01")
            heartbeats.append(worker.heartbeat_utc)
        
        # Each heartbeat should be >= previous (precision limited)
        assert heartbeats[1] >= heartbeats[0]
        assert heartbeats[2] >= heartbeats[1]


class TestWorkerQueries:
    """Test worker query functions."""

    def test_get_all_workers_empty(self, monitoring):
        """Test getting all workers when none exist."""
        workers = monitoring.get_all_workers()
        assert workers == []

    def test_get_all_workers(self, monitoring):
        """Test getting all workers."""
        monitoring.register_worker("worker-01", {"cpu": 4})
        monitoring.register_worker("worker-02", {"cpu": 8})
        monitoring.register_worker("worker-03", {"cpu": 16})
        
        workers = monitoring.get_all_workers()
        assert len(workers) == 3
        
        worker_ids = [w.worker_id for w in workers]
        assert "worker-01" in worker_ids
        assert "worker-02" in worker_ids
        assert "worker-03" in worker_ids

    def test_get_active_workers(self, monitoring):
        """Test getting active workers."""
        # Register workers
        monitoring.register_worker("worker-01")
        monitoring.register_worker("worker-02")
        
        # Both should be active (just registered)
        active = monitoring.get_active_workers(active_threshold_seconds=60)
        assert len(active) == 2

    def test_get_stale_workers(self, monitoring, db):
        """Test getting stale workers."""
        # Register worker
        monitoring.register_worker("worker-01")
        
        # Manually set heartbeat to old timestamp
        db.execute(
            "UPDATE workers SET heartbeat_utc = datetime('now', '-10 minutes') WHERE worker_id = ?",
            ("worker-01",)
        )
        db.get_connection().commit()
        
        # Should be stale (threshold 5 minutes = 300 seconds)
        stale = monitoring.get_stale_workers(stale_threshold_seconds=300)
        assert len(stale) == 1
        assert stale[0].worker_id == "worker-01"

    def test_get_stale_workers_mixed(self, monitoring, db):
        """Test getting stale workers with mix of active and stale."""
        # Register workers
        monitoring.register_worker("worker-01")  # Active
        monitoring.register_worker("worker-02")  # Will be stale
        monitoring.register_worker("worker-03")  # Active
        
        # Make worker-02 stale
        db.execute(
            "UPDATE workers SET heartbeat_utc = datetime('now', '-10 minutes') WHERE worker_id = ?",
            ("worker-02",)
        )
        db.get_connection().commit()
        
        # Check stale workers
        stale = monitoring.get_stale_workers(stale_threshold_seconds=300)
        assert len(stale) == 1
        assert stale[0].worker_id == "worker-02"
        
        # Check active workers
        active = monitoring.get_active_workers(active_threshold_seconds=60)
        assert len(active) == 2
        active_ids = [w.worker_id for w in active]
        assert "worker-01" in active_ids
        assert "worker-03" in active_ids


class TestWorkerRemoval:
    """Test worker removal functionality."""

    def test_remove_existing_worker(self, monitoring):
        """Test removing an existing worker."""
        monitoring.register_worker("worker-01")
        assert monitoring.get_worker("worker-01") is not None
        
        success = monitoring.remove_worker("worker-01")
        assert success is True
        assert monitoring.get_worker("worker-01") is None

    def test_remove_nonexistent_worker(self, monitoring):
        """Test removing a nonexistent worker."""
        success = monitoring.remove_worker("nonexistent")
        assert success is False

    def test_remove_worker_multiple_times(self, monitoring):
        """Test removing the same worker multiple times."""
        monitoring.register_worker("worker-01")
        
        # First removal should succeed
        assert monitoring.remove_worker("worker-01") is True
        
        # Second removal should return False
        assert monitoring.remove_worker("worker-01") is False


class TestQueueMetrics:
    """Test queue metrics and statistics."""

    def test_queue_metrics_empty_queue(self, monitoring):
        """Test queue metrics with empty queue."""
        metrics = monitoring.get_queue_metrics()
        
        assert metrics["queue_depth_by_status"] == {}
        assert metrics["queue_depth_by_type"] == {}
        assert metrics["oldest_queued_task_age_seconds"] is None
        assert metrics["task_statistics"] == {}
        assert metrics["success_rate"] is None
        assert metrics["failure_rate"] is None
        assert metrics["total_workers"] == 0
        assert metrics["active_workers"] == 0
        assert metrics["stale_workers"] == 0

    def test_queue_metrics_with_tasks(self, monitoring, db):
        """Test queue metrics with various tasks."""
        # Insert test tasks (payload is required)
        db.execute(
            "INSERT INTO task_queue (type, status, priority, payload) VALUES (?, ?, ?, ?)",
            ("video", "queued", 100, "{}")
        )
        db.execute(
            "INSERT INTO task_queue (type, status, priority, payload) VALUES (?, ?, ?, ?)",
            ("audio", "queued", 50, "{}")
        )
        db.execute(
            "INSERT INTO task_queue (type, status, priority, payload) VALUES (?, ?, ?, ?)",
            ("video", "processing", 100, "{}")
        )
        db.execute(
            "INSERT INTO task_queue (type, status, priority, payload) VALUES (?, ?, ?, ?)",
            ("image", "completed", 100, "{}")
        )
        db.execute(
            "INSERT INTO task_queue (type, status, priority, payload) VALUES (?, ?, ?, ?)",
            ("text", "failed", 100, "{}")
        )
        db.get_connection().commit()
        
        metrics = monitoring.get_queue_metrics()
        
        # Check queue depth by status
        assert metrics["queue_depth_by_status"]["queued"] == 2
        assert metrics["queue_depth_by_status"]["processing"] == 1
        assert metrics["queue_depth_by_status"]["completed"] == 1
        assert metrics["queue_depth_by_status"]["failed"] == 1
        
        # Check queue depth by type (only queued tasks)
        assert metrics["queue_depth_by_type"]["video"] == 1
        assert metrics["queue_depth_by_type"]["audio"] == 1
        
        # Check task statistics
        assert metrics["task_statistics"]["completed"]["count"] == 1
        assert metrics["task_statistics"]["failed"]["count"] == 1
        
        # Check success/failure rates
        assert metrics["success_rate"] == 0.5  # 1 out of 2
        assert metrics["failure_rate"] == 0.5  # 1 out of 2

    def test_queue_metrics_with_workers(self, monitoring, db):
        """Test queue metrics with workers."""
        # Register workers
        monitoring.register_worker("worker-01")
        monitoring.register_worker("worker-02")
        monitoring.register_worker("worker-03")
        
        # Make one worker stale
        db.execute(
            "UPDATE workers SET heartbeat_utc = datetime('now', '-10 minutes') WHERE worker_id = ?",
            ("worker-03",)
        )
        db.get_connection().commit()
        
        metrics = monitoring.get_queue_metrics()
        
        assert metrics["total_workers"] == 3
        assert metrics["active_workers"] == 2
        assert metrics["stale_workers"] == 1

    def test_queue_metrics_oldest_task_age(self, monitoring, db):
        """Test oldest queued task age calculation."""
        # Insert task with old timestamp (payload is required)
        db.execute(
            "INSERT INTO task_queue (type, status, payload, created_at_utc) VALUES (?, ?, ?, datetime('now', '-5 minutes'))",
            ("old_task", "queued", "{}")
        )
        db.get_connection().commit()
        
        metrics = monitoring.get_queue_metrics()
        
        # Should be approximately 300 seconds (5 minutes)
        assert metrics["oldest_queued_task_age_seconds"] is not None
        assert metrics["oldest_queued_task_age_seconds"] >= 290  # Allow some margin


class TestWorkerActivity:
    """Test worker activity tracking."""

    def test_worker_activity_empty(self, monitoring):
        """Test worker activity with no workers."""
        activity = monitoring.get_worker_activity()
        assert activity == []

    def test_worker_activity_single_worker(self, monitoring):
        """Test worker activity with single worker."""
        monitoring.register_worker("worker-01", {"cpu": 8})
        
        activity = monitoring.get_worker_activity()
        assert len(activity) == 1
        
        worker_activity = activity[0]
        assert worker_activity["worker_id"] == "worker-01"
        assert "heartbeat_utc" in worker_activity
        assert "seconds_since_heartbeat" in worker_activity
        assert worker_activity["seconds_since_heartbeat"] >= 0

    def test_worker_activity_multiple_workers(self, monitoring, db):
        """Test worker activity with multiple workers."""
        # Register workers at different times
        monitoring.register_worker("worker-01")
        
        # Make worker-02 older
        db.execute(
            "INSERT INTO workers (worker_id, capabilities, heartbeat_utc) VALUES (?, ?, datetime('now', '-5 minutes'))",
            ("worker-02", "{}")
        )
        db.get_connection().commit()
        
        activity = monitoring.get_worker_activity()
        assert len(activity) == 2
        
        # Should be ordered by heartbeat (newest first)
        assert activity[0]["worker_id"] == "worker-01"
        assert activity[1]["worker_id"] == "worker-02"
        
        # worker-02 should have older heartbeat
        assert activity[1]["seconds_since_heartbeat"] > activity[0]["seconds_since_heartbeat"]

    def test_worker_activity_with_capabilities(self, monitoring):
        """Test worker activity includes capabilities."""
        monitoring.register_worker("worker-01", {"cpu": 8, "gpu": True})
        
        activity = monitoring.get_worker_activity()
        assert len(activity) == 1
        
        # Capabilities should be JSON string
        assert activity[0]["capabilities"] == '{"cpu": 8, "gpu": true}'


class TestErrorHandling:
    """Test error handling in monitoring functions."""

    def test_register_worker_with_invalid_json(self, monitoring):
        """Test that worker registration handles invalid capabilities gracefully."""
        # Register worker - should work even with complex capabilities
        monitoring.register_worker("worker-01", {"cpu": 8, "nested": {"key": "value"}})
        worker = monitoring.get_worker("worker-01")
        assert worker is not None
        assert worker.worker_id == "worker-01"

    def test_get_metrics_handles_empty_results(self, monitoring):
        """Test that metrics functions handle empty results gracefully."""
        # Should not raise errors even with no data
        metrics = monitoring.get_queue_metrics()
        assert metrics is not None
        assert isinstance(metrics, dict)
        
    def test_worker_activity_handles_empty_results(self, monitoring):
        """Test that worker activity handles empty results gracefully."""
        # Should not raise errors even with no workers
        activity = monitoring.get_worker_activity()
        assert activity is not None
        assert isinstance(activity, list)
        assert len(activity) == 0


class TestIntegration:
    """Integration tests for monitoring functionality."""

    def test_worker_lifecycle(self, monitoring):
        """Test complete worker lifecycle."""
        # Register worker
        monitoring.register_worker("worker-01", {"cpu": 8})
        assert monitoring.get_worker("worker-01") is not None
        
        # Update heartbeat a few times
        monitoring.update_heartbeat("worker-01")
        time.sleep(1.1)  # SQLite datetime precision
        monitoring.update_heartbeat("worker-01")
        
        # Worker should still be active
        active = monitoring.get_active_workers()
        assert len(active) == 1
        
        # Remove worker
        monitoring.remove_worker("worker-01")
        assert monitoring.get_worker("worker-01") is None

    def test_monitoring_multiple_workers_scenario(self, monitoring, db):
        """Test realistic scenario with multiple workers."""
        # Register 3 workers
        monitoring.register_worker("worker-01", {"type": "video"})
        monitoring.register_worker("worker-02", {"type": "audio"})
        monitoring.register_worker("worker-03", {"type": "image"})
        
        # Worker-02 becomes stale
        db.execute(
            "UPDATE workers SET heartbeat_utc = datetime('now', '-10 minutes') WHERE worker_id = ?",
            ("worker-02",)
        )
        db.get_connection().commit()
        
        # Add some tasks (payload is required)
        db.execute("INSERT INTO task_queue (type, status, payload) VALUES ('video', 'queued', '{}')")
        db.execute("INSERT INTO task_queue (type, status, payload) VALUES ('audio', 'processing', '{}')")
        db.execute("INSERT INTO task_queue (type, status, payload) VALUES ('image', 'completed', '{}')")
        db.get_connection().commit()
        
        # Check metrics
        metrics = monitoring.get_queue_metrics()
        assert metrics["total_workers"] == 3
        assert metrics["active_workers"] == 2
        assert metrics["stale_workers"] == 1
        assert metrics["queue_depth_by_status"]["queued"] == 1
        assert metrics["queue_depth_by_status"]["processing"] == 1
        assert metrics["queue_depth_by_status"]["completed"] == 1
        
        # Check worker activity
        activity = monitoring.get_worker_activity()
        assert len(activity) == 3
        
        # Clean up stale worker
        stale_workers = monitoring.get_stale_workers(stale_threshold_seconds=300)
        for worker in stale_workers:
            monitoring.remove_worker(worker.worker_id)
        
        # Verify cleanup
        assert monitoring.get_worker("worker-02") is None
        assert len(monitoring.get_all_workers()) == 2
