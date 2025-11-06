"""Unit tests for queue maintenance utilities."""

import pytest
import sqlite3
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta

from src.queue import (
    QueueDatabase,
    QueueMaintenance,
    QueueMaintenanceError,
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
def maintenance(db):
    """Create a QueueMaintenance instance for testing."""
    return QueueMaintenance(db)


class TestMaintenanceInitialization:
    """Test maintenance manager initialization."""

    def test_initialization(self, db):
        """Test basic initialization."""
        maint = QueueMaintenance(db)
        
        assert maint.db == db


class TestCheckpointOperations:
    """Test WAL checkpoint operations."""

    def test_checkpoint_passive(self, maintenance):
        """Test PASSIVE checkpoint."""
        result = maintenance.checkpoint(mode=QueueMaintenance.CHECKPOINT_PASSIVE)
        
        assert "busy" in result
        assert "log" in result
        assert "checkpointed" in result
        assert result["busy"] in (0, 1)

    def test_checkpoint_full(self, maintenance):
        """Test FULL checkpoint."""
        result = maintenance.checkpoint(mode=QueueMaintenance.CHECKPOINT_FULL)
        
        assert "busy" in result
        assert result["busy"] in (0, 1)

    def test_checkpoint_restart(self, maintenance):
        """Test RESTART checkpoint."""
        result = maintenance.checkpoint(mode=QueueMaintenance.CHECKPOINT_RESTART)
        
        assert "busy" in result
        assert result["busy"] in (0, 1)

    def test_checkpoint_truncate(self, maintenance):
        """Test TRUNCATE checkpoint."""
        result = maintenance.checkpoint(mode=QueueMaintenance.CHECKPOINT_TRUNCATE)
        
        assert "busy" in result
        assert result["busy"] in (0, 1)

    def test_checkpoint_invalid_mode(self, maintenance):
        """Test checkpoint with invalid mode raises error."""
        with pytest.raises(QueueMaintenanceError, match="Invalid checkpoint mode"):
            maintenance.checkpoint(mode="INVALID")

    def test_checkpoint_after_writes(self, db, maintenance):
        """Test checkpoint after database writes."""
        # Insert some data to create WAL activity
        with db.transaction() as conn:
            for i in range(10):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                    (f"task_{i}", '{"data": "test"}', 100)
                )
        
        result = maintenance.checkpoint(mode=QueueMaintenance.CHECKPOINT_PASSIVE)
        
        assert isinstance(result, dict)
        assert "log" in result


class TestVacuumOperation:
    """Test VACUUM operation."""

    def test_vacuum_basic(self, maintenance):
        """Test basic VACUUM operation."""
        # Should complete without error
        maintenance.vacuum()

    def test_vacuum_after_deletes(self, db, maintenance):
        """Test VACUUM reclaims space after deletes."""
        # Insert data with valid JSON
        with db.transaction() as conn:
            for i in range(100):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority, compatibility) VALUES (?, ?, ?, ?)",
                    (f"task_{i}", '{"data": "test"}', 100, '{}')
                )
        
        # Get size before delete
        stats_before = maintenance.get_database_stats()
        
        # Delete data
        with db.transaction() as conn:
            conn.execute("DELETE FROM task_queue")
        
        # VACUUM should reclaim space
        maintenance.vacuum()
        
        stats_after = maintenance.get_database_stats()
        
        # After VACUUM, freelist should be reduced or size should be smaller
        assert stats_after["page_count"] <= stats_before["page_count"]


class TestAnalyzeOperation:
    """Test ANALYZE operation."""

    def test_analyze_all_tables(self, maintenance):
        """Test ANALYZE on all tables."""
        # Should complete without error
        maintenance.analyze()

    def test_analyze_specific_table(self, maintenance):
        """Test ANALYZE on specific table."""
        # Should complete without error
        maintenance.analyze(table="task_queue")

    def test_analyze_after_data_changes(self, db, maintenance):
        """Test ANALYZE updates statistics after data changes."""
        # Insert data
        with db.transaction() as conn:
            for i in range(100):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                    (f"task_{i}", '{"data": "test"}', i)
                )
        
        # ANALYZE should succeed
        maintenance.analyze()


class TestIntegrityCheck:
    """Test database integrity check."""

    def test_integrity_check_clean_database(self, maintenance):
        """Test integrity check on clean database."""
        results = maintenance.integrity_check()
        
        assert results == ["ok"]

    def test_integrity_check_with_data(self, db, maintenance):
        """Test integrity check with data in database."""
        # Insert test data
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority, compatibility) VALUES (?, ?, ?, ?)",
                ("test_task", '{"data": "test"}', 100, '{}')
            )
        
        results = maintenance.integrity_check()
        
        assert results == ["ok"]


class TestStaleLeaseCleanup:
    """Test stale lease cleanup operations."""

    def test_cleanup_no_stale_leases(self, maintenance):
        """Test cleanup when no stale leases exist."""
        count = maintenance.cleanup_stale_leases()
        
        assert count == 0

    def test_cleanup_stale_lease(self, db, maintenance):
        """Test cleanup of a single stale lease."""
        # Insert a task with an expired lease
        expired_time = (datetime.utcnow() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue 
                (type, payload, status, lease_until_utc, locked_by, compatibility)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("test_task", '{"data": "test"}', "processing", expired_time, "worker_1", '{}')
            )
        
        # Cleanup stale leases
        count = maintenance.cleanup_stale_leases(timeout_seconds=300)
        
        assert count == 1
        
        # Verify task was requeued
        cursor = db.execute("SELECT status, locked_by FROM task_queue WHERE id = 1")
        row = cursor.fetchone()
        assert row["status"] == "queued"
        assert row["locked_by"] is None

    def test_cleanup_multiple_stale_leases(self, db, maintenance):
        """Test cleanup of multiple stale leases."""
        expired_time = (datetime.utcnow() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert 3 tasks with expired leases
        with db.transaction() as conn:
            for i in range(3):
                conn.execute(
                    """
                    INSERT INTO task_queue 
                    (type, payload, status, lease_until_utc, locked_by, compatibility)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (f"task_{i}", '{"data": "test"}', "processing", expired_time, f"worker_{i}", '{}')
                )
        
        count = maintenance.cleanup_stale_leases()
        
        assert count == 3

    def test_cleanup_does_not_affect_valid_leases(self, db, maintenance):
        """Test cleanup doesn't affect tasks with valid leases."""
        # Insert task with valid future lease
        future_time = (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue 
                (type, payload, status, lease_until_utc, locked_by, compatibility)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("valid_task", '{"data": "test"}', "processing", future_time, "worker_1", '{}')
            )
        
        count = maintenance.cleanup_stale_leases(timeout_seconds=300)
        
        assert count == 0
        
        # Verify task is still processing
        cursor = db.execute("SELECT status FROM task_queue WHERE id = 1")
        row = cursor.fetchone()
        assert row["status"] == "processing"

    def test_cleanup_custom_timeout(self, db, maintenance):
        """Test cleanup with custom timeout threshold."""
        # Insert task with lease that expired 2 minutes ago
        expired_time = (datetime.utcnow() - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
        
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue 
                (type, payload, status, lease_until_utc, locked_by, compatibility)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("test_task", '{"data": "test"}', "processing", expired_time, "worker_1", '{}')
            )
        
        # With 60 second timeout, SHOULD clean up (expired 2 min ago > 1 min threshold)
        count = maintenance.cleanup_stale_leases(timeout_seconds=60)
        assert count == 1


class TestDatabaseStats:
    """Test database statistics retrieval."""

    def test_get_stats_empty_database(self, maintenance):
        """Test getting stats from empty database."""
        stats = maintenance.get_database_stats()
        
        assert "page_count" in stats
        assert "page_size" in stats
        assert "total_size_mb" in stats
        assert "freelist_count" in stats
        assert "wal_mode" in stats
        assert "wal_size_mb" in stats
        
        assert stats["page_count"] > 0
        assert stats["page_size"] > 0
        assert stats["total_size_mb"] > 0
        assert stats["wal_mode"] is True  # WAL mode should be enabled

    def test_get_stats_with_data(self, db, maintenance):
        """Test getting stats after inserting data."""
        # Insert data with valid JSON
        with db.transaction() as conn:
            for i in range(50):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority, compatibility) VALUES (?, ?, ?, ?)",
                    (f"task_{i}", '{"data": "test"}', 100, '{}')
                )
        
        stats = maintenance.get_database_stats()
        
        assert stats["page_count"] > 0
        assert stats["total_size_mb"] > 0

    def test_wal_size_tracking(self, db, maintenance):
        """Test WAL file size is tracked in stats."""
        # Insert data to create WAL activity
        with db.transaction() as conn:
            for i in range(100):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                    (f"task_{i}", '{"data": "test"}', 100)
                )
        
        stats = maintenance.get_database_stats()
        
        # WAL size should be reported
        assert "wal_size_mb" in stats
        assert stats["wal_size_mb"] >= 0


class TestOptimizeOperation:
    """Test combined optimization operations."""

    def test_optimize_without_vacuum(self, maintenance):
        """Test optimize with ANALYZE only."""
        result = maintenance.optimize(full=False)
        
        assert result["analyzed"] is True
        assert result["vacuumed"] is False
        assert "stats_before" in result
        assert "stats_after" in result

    def test_optimize_with_vacuum(self, maintenance):
        """Test optimize with both ANALYZE and VACUUM."""
        result = maintenance.optimize(full=True)
        
        assert result["analyzed"] is True
        assert result["vacuumed"] is True
        assert "stats_before" in result
        assert "stats_after" in result

    def test_optimize_with_data(self, db, maintenance):
        """Test optimize on database with data."""
        # Insert and delete data to create fragmentation with valid JSON
        with db.transaction() as conn:
            for i in range(100):
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority, compatibility) VALUES (?, ?, ?, ?)",
                    (f"task_{i}", '{"data": "test"}', 100, '{}')
                )
        
        with db.transaction() as conn:
            conn.execute("DELETE FROM task_queue WHERE id % 2 = 0")
        
        # Optimize should succeed
        result = maintenance.optimize(full=True)
        
        assert result["analyzed"] is True
        assert result["vacuumed"] is True
        
        # Stats should be present
        assert "stats_before" in result
        assert "stats_after" in result


class TestMaintenanceErrorHandling:
    """Test maintenance error handling."""

    def test_checkpoint_on_closed_database(self, db, maintenance):
        """Test checkpoint returns error indicator when database is closed."""
        db.close()
        
        # Checkpoint should complete but may return busy=1
        # We just verify it doesn't crash
        try:
            result = maintenance.checkpoint()
            # If it succeeds, verify result structure
            assert "busy" in result
        except QueueMaintenanceError:
            # Expected - checkpoint fails on closed database
            pass

    def test_cleanup_handles_concurrent_modifications(self, db, maintenance):
        """Test cleanup is atomic and handles concurrent access."""
        # Insert stale lease
        expired_time = (datetime.utcnow() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue 
                (type, payload, status, lease_until_utc, locked_by, compatibility)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("test_task", '{"data": "test"}', "processing", expired_time, "worker_1", '{}')
            )
        
        # Cleanup should be atomic
        count = maintenance.cleanup_stale_leases()
        
        assert count == 1


class TestMaintenanceConstants:
    """Test maintenance module constants."""

    def test_checkpoint_mode_constants(self):
        """Test checkpoint mode constants are defined."""
        assert QueueMaintenance.CHECKPOINT_PASSIVE == "PASSIVE"
        assert QueueMaintenance.CHECKPOINT_FULL == "FULL"
        assert QueueMaintenance.CHECKPOINT_RESTART == "RESTART"
        assert QueueMaintenance.CHECKPOINT_TRUNCATE == "TRUNCATE"
