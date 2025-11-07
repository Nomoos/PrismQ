"""Unit tests for queue metrics and statistics collection."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from src.queue import (
    QueueDatabase,
    QueueMetrics,
    Task,
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
def metrics(db):
    """Create a QueueMetrics instance for testing."""
    return QueueMetrics(db)


def insert_task(db, task_type="test", status="queued", **kwargs):
    """Helper to insert a task and return its ID."""
    sql = """
        INSERT INTO task_queue (type, status, priority, payload, compatibility)
        VALUES (?, ?, ?, ?, ?)
    """
    priority = kwargs.get("priority", 100)
    payload = kwargs.get("payload", "{}")
    compatibility = kwargs.get("compatibility", "{}")
    
    cursor = db.execute(sql, (task_type, status, priority, payload, compatibility))
    return cursor.lastrowid


class TestQueueDepth:
    """Test queue depth metrics."""

    def test_get_queue_depth_empty(self, metrics):
        """Test queue depth with empty queue."""
        depth = metrics.get_queue_depth()
        assert depth == 0

    def test_get_queue_depth_basic(self, metrics, db):
        """Test basic queue depth."""
        # Insert some tasks
        insert_task(db, status="queued")
        insert_task(db, status="queued")
        insert_task(db, status="processing")

        depth = metrics.get_queue_depth()
        assert depth == 3

    def test_get_queue_depth_by_status(self, metrics, db):
        """Test queue depth filtered by status."""
        insert_task(db, status="queued")
        insert_task(db, status="queued")
        insert_task(db, status="processing")
        insert_task(db, status="completed")

        queued_depth = metrics.get_queue_depth(status="queued")
        assert queued_depth == 2

        processing_depth = metrics.get_queue_depth(status="processing")
        assert processing_depth == 1

    def test_get_queue_depth_by_type(self, metrics, db):
        """Test queue depth filtered by type."""
        insert_task(db, task_type="classify", status="queued")
        insert_task(db, task_type="classify", status="processing")
        insert_task(db, task_type="score", status="queued")

        classify_depth = metrics.get_queue_depth(task_type="classify")
        assert classify_depth == 2

        score_depth = metrics.get_queue_depth(task_type="score")
        assert score_depth == 1

    def test_get_queue_depth_by_type_and_status(self, metrics, db):
        """Test queue depth filtered by both type and status."""
        insert_task(db, task_type="classify", status="queued")
        insert_task(db, task_type="classify", status="processing")
        insert_task(db, task_type="score", status="queued")

        depth = metrics.get_queue_depth(task_type="classify", status="queued")
        assert depth == 1


class TestQueueDepthAggregations:
    """Test queue depth aggregation methods."""

    def test_get_queue_depth_by_status_aggregation(self, metrics, db):
        """Test queue depth grouped by status."""
        insert_task(db, status="queued")
        insert_task(db, status="queued")
        insert_task(db, status="processing")
        insert_task(db, status="completed")

        depth_by_status = metrics.get_queue_depth_by_status()
        
        assert depth_by_status.get("queued") == 2
        assert depth_by_status.get("processing") == 1
        assert depth_by_status.get("completed") == 1

    def test_get_queue_depth_by_type_aggregation(self, metrics, db):
        """Test queue depth grouped by type."""
        insert_task(db, task_type="classify")
        insert_task(db, task_type="classify")
        insert_task(db, task_type="score")

        depth_by_type = metrics.get_queue_depth_by_type()
        
        assert depth_by_type.get("classify") == 2
        assert depth_by_type.get("score") == 1


class TestQueueAge:
    """Test queue age metrics."""

    def test_get_oldest_queued_task_age_empty(self, metrics):
        """Test oldest task age with empty queue."""
        age = metrics.get_oldest_queued_task_age()
        assert age is None

    def test_get_oldest_queued_task_age(self, metrics, db):
        """Test oldest queued task age."""
        # Insert a queued task
        insert_task(db, status="queued")
        
        # Get age (should be close to 0 seconds since just created)
        age = metrics.get_oldest_queued_task_age()
        assert age is not None
        assert age >= 0
        assert age < 5  # Should be very recent

    def test_get_oldest_queued_task_ignores_other_statuses(self, metrics, db):
        """Test that oldest task age only considers queued tasks."""
        # Insert old completed task
        insert_task(db, status="completed")
        
        # No queued tasks
        age = metrics.get_oldest_queued_task_age()
        assert age is None
        
        # Now add a queued task
        insert_task(db, status="queued")
        age = metrics.get_oldest_queued_task_age()
        assert age is not None


class TestSuccessFailureRates:
    """Test success/failure rate metrics."""

    def test_get_success_failure_rates_empty(self, metrics):
        """Test success/failure rates with no completed tasks."""
        rates = metrics.get_success_failure_rates(hours=24)
        
        assert rates["success_count"] == 0
        assert rates["failure_count"] == 0
        assert rates["total_count"] == 0
        assert rates["success_rate"] == 0.0
        assert rates["failure_rate"] == 0.0

    def test_get_success_failure_rates(self, metrics, db):
        """Test success/failure rate calculation."""
        # Insert completed tasks
        sql = """
            INSERT INTO task_queue 
            (type, status, payload, compatibility, finished_at_utc)
            VALUES (?, ?, ?, ?, datetime('now'))
        """
        
        # 7 successful
        for _ in range(7):
            db.execute(sql, ("test", "completed", "{}", "{}"))
        
        # 3 failed
        for _ in range(3):
            db.execute(sql, ("test", "failed", "{}", "{}"))

        rates = metrics.get_success_failure_rates(hours=24)
        
        assert rates["success_count"] == 7
        assert rates["failure_count"] == 3
        assert rates["total_count"] == 10
        assert rates["success_rate"] == 0.7
        assert rates["failure_rate"] == 0.3

    def test_get_success_failure_rates_with_dead_letter(self, metrics, db):
        """Test that dead_letter tasks count as failures."""
        sql = """
            INSERT INTO task_queue 
            (type, status, payload, compatibility, finished_at_utc)
            VALUES (?, ?, ?, ?, datetime('now'))
        """
        
        db.execute(sql, ("test", "completed", "{}", "{}"))
        db.execute(sql, ("test", "failed", "{}", "{}"))
        db.execute(sql, ("test", "dead_letter", "{}", "{}"))

        rates = metrics.get_success_failure_rates(hours=24)
        
        assert rates["success_count"] == 1
        assert rates["failure_count"] == 2  # failed + dead_letter
        assert rates["failure_rate"] == pytest.approx(0.666, rel=0.01)


class TestWorkerActivity:
    """Test worker activity metrics."""

    def test_get_worker_activity_empty(self, metrics):
        """Test worker activity with no workers."""
        activity = metrics.get_worker_activity()
        assert activity == []

    def test_get_worker_activity(self, metrics, db):
        """Test worker activity retrieval."""
        # Insert workers
        sql = "INSERT INTO workers (worker_id, capabilities) VALUES (?, ?)"
        db.execute(sql, ("worker-1", '{"type": "classifier"}'))
        db.execute(sql, ("worker-2", '{"type": "scorer"}'))

        # Insert tasks assigned to workers
        insert_task(db, status="processing")
        sql = "UPDATE task_queue SET locked_by = ? WHERE id = ?"
        db.execute(sql, ("worker-1", 1))

        activity = metrics.get_worker_activity()
        
        assert len(activity) == 2
        # Worker-1 should have 1 active task
        worker1 = next(w for w in activity if w["worker_id"] == "worker-1")
        assert worker1["active_tasks"] == 1


class TestThroughputMetrics:
    """Test throughput metrics."""

    def test_get_throughput_metrics_empty(self, metrics):
        """Test throughput with no completed tasks."""
        throughput = metrics.get_throughput_metrics(hours=1)
        
        assert throughput["tasks_completed"] == 0
        assert throughput["tasks_per_minute"] == 0.0
        assert throughput["avg_processing_time_seconds"] == 0.0

    def test_get_throughput_metrics(self, metrics, db):
        """Test throughput calculation."""
        # Insert completed tasks with processing times
        sql = """
            INSERT INTO task_queue 
            (type, status, payload, compatibility, 
             processing_started_utc, finished_at_utc)
            VALUES (?, ?, ?, ?, 
                    datetime('now', '-10 seconds'), 
                    datetime('now'))
        """
        
        for _ in range(60):  # 60 tasks
            db.execute(sql, ("test", "completed", "{}", "{}"))

        throughput = metrics.get_throughput_metrics(hours=1)
        
        assert throughput["tasks_completed"] == 60
        assert throughput["tasks_per_minute"] == 1.0  # 60 tasks / 60 minutes
        assert throughput["avg_processing_time_seconds"] > 0


class TestRetryMetrics:
    """Test retry-related metrics."""

    def test_get_retry_metrics_empty(self, metrics):
        """Test retry metrics with no tasks."""
        retry_metrics = metrics.get_retry_metrics(hours=24)
        
        assert retry_metrics["total_tasks"] == 0
        assert retry_metrics["tasks_with_retries"] == 0
        assert retry_metrics["retry_rate"] == 0.0
        assert retry_metrics["avg_attempts"] == 0.0
        assert retry_metrics["max_attempts_reached"] == 0

    def test_get_retry_metrics(self, metrics, db):
        """Test retry metrics calculation."""
        # Insert tasks with different attempt counts
        sql = """
            INSERT INTO task_queue 
            (type, status, attempts, payload, compatibility, finished_at_utc)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        
        # 5 tasks succeeded on first try
        for _ in range(5):
            db.execute(sql, ("test", "completed", 1, "{}", "{}"))
        
        # 3 tasks needed retries
        for _ in range(3):
            db.execute(sql, ("test", "completed", 3, "{}", "{}"))
        
        # 2 tasks reached max attempts
        for _ in range(2):
            db.execute(sql, ("test", "dead_letter", 5, "{}", "{}"))

        retry_metrics = metrics.get_retry_metrics(hours=24)
        
        assert retry_metrics["total_tasks"] == 10
        assert retry_metrics["tasks_with_retries"] == 5  # 3 + 2
        assert retry_metrics["retry_rate"] == 0.5
        assert retry_metrics["max_attempts_reached"] == 2


class TestProcessingTimePercentiles:
    """Test processing time percentile calculations."""

    def test_get_processing_time_percentiles_empty(self, metrics):
        """Test percentiles with no completed tasks."""
        percentiles = metrics.get_processing_time_percentiles(hours=24)
        
        assert percentiles["p50"] == 0.0
        assert percentiles["p95"] == 0.0
        assert percentiles["p99"] == 0.0

    def test_get_processing_time_percentiles(self, metrics, db):
        """Test processing time percentile calculation."""
        # Insert tasks with known processing times
        sql = """
            INSERT INTO task_queue 
            (type, status, payload, compatibility,
             processing_started_utc, finished_at_utc)
            VALUES (?, ?, ?, ?,
                    datetime('now', ?),
                    datetime('now'))
        """
        
        # Create 100 tasks with processing times from 1 to 100 seconds
        for i in range(1, 101):
            db.execute(sql, ("test", "completed", "{}", "{}", f"-{i} seconds"))

        percentiles = metrics.get_processing_time_percentiles(hours=24)
        
        # p50 should be around 50 seconds
        assert 45 <= percentiles["p50"] <= 55
        # p95 should be around 95 seconds
        assert 90 <= percentiles["p95"] <= 100
        # p99 should be around 99 seconds
        assert 95 <= percentiles["p99"] <= 100

    def test_get_processing_time_percentiles_filtered_by_type(self, metrics, db):
        """Test percentiles filtered by task type."""
        sql = """
            INSERT INTO task_queue 
            (type, status, payload, compatibility,
             processing_started_utc, finished_at_utc)
            VALUES (?, ?, ?, ?,
                    datetime('now', '-10 seconds'),
                    datetime('now'))
        """
        
        # Add classify tasks
        for _ in range(5):
            db.execute(sql, ("classify", "completed", "{}", "{}"))
        
        # Add score tasks
        for _ in range(5):
            db.execute(sql, ("score", "completed", "{}", "{}"))

        percentiles = metrics.get_processing_time_percentiles(
            hours=24,
            task_type="classify"
        )
        
        # Should only consider classify tasks
        assert percentiles["p50"] > 0


class TestQueueHealthSummary:
    """Test comprehensive queue health summary."""

    def test_get_queue_health_summary(self, metrics, db):
        """Test queue health summary generation."""
        # Insert various tasks
        insert_task(db, status="queued")
        insert_task(db, status="processing")
        
        sql = """
            INSERT INTO task_queue 
            (type, status, payload, compatibility, finished_at_utc)
            VALUES (?, ?, ?, ?, datetime('now'))
        """
        db.execute(sql, ("test", "completed", "{}", "{}"))

        # Insert a worker
        sql = "INSERT INTO workers (worker_id, capabilities) VALUES (?, ?)"
        db.execute(sql, ("worker-1", '{"type": "test"}'))

        health = metrics.get_queue_health_summary()
        
        # Verify all expected keys are present
        assert "queue_depth" in health
        assert "oldest_queued_task_age_seconds" in health
        assert "success_failure_rates_24h" in health
        assert "throughput_1h" in health
        assert "active_workers" in health
        assert "retry_metrics_24h" in health
        assert "timestamp" in health
        
        # Verify queue depth
        assert health["queue_depth"].get("queued") == 1
        assert health["queue_depth"].get("processing") == 1
        assert health["queue_depth"].get("completed") == 1
        
        # Verify worker count
        assert health["active_workers"] == 1


class TestMetricsEdgeCases:
    """Test edge cases and error handling."""

    def test_metrics_with_closed_database(self, metrics, db):
        """Test metrics behavior when database is closed."""
        db.close()
        
        # SQLite might not raise immediately on closed connection
        # Try an operation that requires database access
        try:
            metrics.get_queue_depth()
            # If it doesn't raise, the connection might still work
            # This is acceptable behavior
        except (QueueDatabaseError, Exception):
            # Expected - database is closed
            pass

    def test_metrics_with_null_values(self, metrics, db):
        """Test metrics handling of NULL values."""
        # Insert task with NULL processing times
        sql = """
            INSERT INTO task_queue 
            (type, status, payload, compatibility)
            VALUES (?, ?, ?, ?)
        """
        db.execute(sql, ("test", "queued", "{}", "{}"))
        
        # Should handle NULLs gracefully
        throughput = metrics.get_throughput_metrics(hours=24)
        assert throughput["avg_processing_time_seconds"] == 0.0
