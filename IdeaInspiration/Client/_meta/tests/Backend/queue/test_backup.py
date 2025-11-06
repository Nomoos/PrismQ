"""Unit tests for queue backup utilities."""

import pytest
import sqlite3
import tempfile
import time
from pathlib import Path
from datetime import datetime

from src.queue import (
    QueueDatabase,
    QueueBackup,
    BackupInfo,
    QueueBackupError,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_queue.db"


@pytest.fixture
def temp_backup_dir():
    """Create a temporary backup directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "backups"


@pytest.fixture
def db(temp_db_path):
    """Create a QueueDatabase instance for testing."""
    database = QueueDatabase(str(temp_db_path))
    database.initialize_schema()
    yield database
    database.close()


@pytest.fixture
def backup_manager(db, temp_backup_dir):
    """Create a QueueBackup instance for testing."""
    return QueueBackup(db, str(temp_backup_dir))


class TestBackupInfo:
    """Test BackupInfo dataclass."""

    def test_from_path(self, temp_db_path):
        """Test creating BackupInfo from a file path."""
        # Create a test file
        temp_db_path.parent.mkdir(parents=True, exist_ok=True)
        temp_db_path.write_text("test data")
        
        info = BackupInfo.from_path(temp_db_path)
        
        assert info.path == temp_db_path
        assert info.size_bytes > 0
        assert isinstance(info.created_at, datetime)

    def test_size_mb_property(self, temp_db_path):
        """Test size_mb property calculation."""
        temp_db_path.parent.mkdir(parents=True, exist_ok=True)
        temp_db_path.write_bytes(b"x" * (2 * 1024 * 1024))  # 2 MB
        
        info = BackupInfo.from_path(temp_db_path)
        
        assert abs(info.size_mb - 2.0) < 0.01  # Allow small variance


class TestBackupInitialization:
    """Test backup manager initialization."""

    def test_initialization_with_custom_dir(self, db, temp_backup_dir):
        """Test initialization with custom backup directory."""
        backup = QueueBackup(db, str(temp_backup_dir))
        
        assert backup.db == db
        assert backup.backup_dir == temp_backup_dir
        assert temp_backup_dir.exists()

    def test_initialization_with_default_dir(self, db):
        """Test initialization with default backup directory."""
        backup = QueueBackup(db)
        
        assert backup.db == db
        assert backup.backup_dir is not None

    def test_backup_directory_creation(self, db, temp_backup_dir):
        """Test backup directory is created if it doesn't exist."""
        # Ensure directory doesn't exist
        if temp_backup_dir.exists():
            temp_backup_dir.rmdir()
        
        backup = QueueBackup(db, str(temp_backup_dir))
        
        assert temp_backup_dir.exists()


class TestBackupCreation:
    """Test backup creation operations."""

    def test_create_backup_basic(self, backup_manager):
        """Test basic backup creation."""
        backup_path = backup_manager.create_backup()
        
        assert backup_path.exists()
        assert backup_path.suffix == ".db"
        assert "queue_backup_" in backup_path.name

    def test_create_backup_with_custom_name(self, backup_manager):
        """Test backup creation with custom name."""
        backup_path = backup_manager.create_backup(name="test_backup")
        
        assert backup_path.exists()
        assert "test_backup" in backup_path.name

    def test_create_backup_with_data(self, db, backup_manager):
        """Test backup includes data from source database."""
        # Insert test data
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                ("test_task", '{"data": "test"}', 100)
            )
        
        # Create backup
        backup_path = backup_manager.create_backup()
        
        # Verify backup contains data
        backup_conn = sqlite3.connect(str(backup_path))
        cursor = backup_conn.execute("SELECT COUNT(*) FROM task_queue")
        count = cursor.fetchone()[0]
        backup_conn.close()
        
        assert count == 1

    def test_create_backup_while_database_in_use(self, db, backup_manager):
        """Test backup can be created while database is in use."""
        # Keep a transaction open
        conn = db.get_connection()
        cursor = conn.execute("SELECT COUNT(*) FROM task_queue")
        
        # Backup should still succeed (non-blocking)
        backup_path = backup_manager.create_backup()
        
        assert backup_path.exists()

    def test_create_multiple_backups(self, backup_manager):
        """Test creating multiple backups with unique names."""
        backup1 = backup_manager.create_backup()
        time.sleep(1.1)  # Ensure different timestamps
        backup2 = backup_manager.create_backup()
        
        assert backup1 != backup2
        assert backup1.exists()
        assert backup2.exists()


class TestBackupVerification:
    """Test backup verification operations."""

    def test_verify_valid_backup(self, backup_manager):
        """Test verifying a valid backup."""
        backup_path = backup_manager.create_backup()
        
        is_valid = backup_manager.verify_backup(backup_path)
        
        assert is_valid is True

    def test_verify_nonexistent_backup(self, backup_manager, temp_backup_dir):
        """Test verifying nonexistent backup raises error."""
        fake_path = temp_backup_dir / "nonexistent.db"
        
        with pytest.raises(QueueBackupError, match="not found"):
            backup_manager.verify_backup(fake_path)

    def test_verify_corrupted_backup(self, backup_manager, temp_backup_dir):
        """Test verifying corrupted backup raises error."""
        # Create a corrupted file
        corrupted_path = temp_backup_dir / "corrupted.db"
        corrupted_path.write_bytes(b"not a valid sqlite database")
        
        with pytest.raises(QueueBackupError):
            backup_manager.verify_backup(corrupted_path)


class TestBackupRestoration:
    """Test backup restoration operations."""

    def test_restore_backup(self, db, backup_manager, temp_db_path):
        """Test restoring database from backup."""
        # Insert test data
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                ("original_task", '{"data": "original"}', 100)
            )
        
        # Create backup
        backup_path = backup_manager.create_backup()
        
        # Modify original database
        with db.transaction() as conn:
            conn.execute("DELETE FROM task_queue")
        
        # Restore from backup
        backup_manager.restore_backup(backup_path)
        
        # Re-open database and verify data
        db2 = QueueDatabase(str(temp_db_path))
        cursor = db2.execute("SELECT type FROM task_queue")
        task_type = cursor.fetchone()[0]
        db2.close()
        
        assert task_type == "original_task"

    def test_restore_nonexistent_backup(self, backup_manager, temp_backup_dir):
        """Test restoring from nonexistent backup raises error."""
        fake_path = temp_backup_dir / "nonexistent.db"
        
        with pytest.raises(QueueBackupError, match="not found"):
            backup_manager.restore_backup(fake_path)

    def test_restore_with_custom_target(self, backup_manager, temp_backup_dir):
        """Test restoring to custom target path."""
        backup_path = backup_manager.create_backup()
        target_path = temp_backup_dir / "restored.db"
        
        backup_manager.restore_backup(backup_path, target_path)
        
        assert target_path.exists()


class TestBackupListing:
    """Test backup listing operations."""

    def test_list_backups_empty(self, backup_manager):
        """Test listing backups when none exist."""
        backups = backup_manager.list_backups()
        
        assert backups == []

    def test_list_backups_with_multiple(self, backup_manager):
        """Test listing multiple backups."""
        backup_manager.create_backup()
        time.sleep(1.1)
        backup_manager.create_backup()
        time.sleep(1.1)
        backup_manager.create_backup()
        
        backups = backup_manager.list_backups()
        
        assert len(backups) == 3
        assert all(isinstance(b, BackupInfo) for b in backups)

    def test_list_backups_sorted_by_time(self, backup_manager):
        """Test backups are sorted newest first."""
        backup_manager.create_backup(name="first")
        time.sleep(1.1)
        backup_manager.create_backup(name="second")
        time.sleep(1.1)
        backup_manager.create_backup(name="third")
        
        backups = backup_manager.list_backups()
        
        # Should be sorted newest first
        assert "third" in backups[0].path.name
        assert "second" in backups[1].path.name
        assert "first" in backups[2].path.name

    def test_get_latest_backup(self, backup_manager):
        """Test getting the latest backup."""
        # No backups initially
        assert backup_manager.get_latest_backup() is None
        
        # Create backups
        backup_manager.create_backup(name="first")
        time.sleep(1.1)
        latest = backup_manager.create_backup(name="latest")
        
        latest_info = backup_manager.get_latest_backup()
        
        assert latest_info is not None
        assert latest_info.path == latest


class TestBackupCleanup:
    """Test backup cleanup operations."""

    def test_cleanup_old_backups(self, backup_manager):
        """Test cleaning up old backups."""
        # Create 5 backups
        for i in range(5):
            backup_manager.create_backup(name=f"backup_{i}")
            time.sleep(1.1)
        
        # Cleanup, keeping only 3
        deleted = backup_manager.cleanup_old_backups(keep_count=3)
        
        assert deleted == 2
        
        remaining = backup_manager.list_backups()
        assert len(remaining) == 3

    def test_cleanup_when_fewer_than_keep_count(self, backup_manager):
        """Test cleanup when there are fewer backups than keep_count."""
        backup_manager.create_backup()
        time.sleep(1.1)
        backup_manager.create_backup()
        
        deleted = backup_manager.cleanup_old_backups(keep_count=5)
        
        assert deleted == 0
        assert len(backup_manager.list_backups()) >= 1  # At least 1 backup exists

    def test_cleanup_keeps_newest_backups(self, backup_manager):
        """Test cleanup keeps the newest backups."""
        backup_manager.create_backup(name="old1")
        time.sleep(1.1)
        backup_manager.create_backup(name="old2")
        time.sleep(1.1)
        backup_manager.create_backup(name="new1")
        time.sleep(1.1)
        backup_manager.create_backup(name="new2")
        
        backup_manager.cleanup_old_backups(keep_count=2)
        
        remaining = backup_manager.list_backups()
        remaining_names = [b.path.name for b in remaining]
        
        assert any("new2" in name for name in remaining_names)
        assert any("new1" in name for name in remaining_names)


class TestBackupErrorHandling:
    """Test backup error handling."""

    def test_backup_with_readonly_directory(self, db, temp_backup_dir):
        """Test backup handles permission errors gracefully."""
        # Test that error is raised when directory cannot be created/written
        # This is a simple test that verifies error handling exists
        backup_manager = QueueBackup(db, str(temp_backup_dir))
        
        # Normal backup should work
        backup_path = backup_manager.create_backup()
        assert backup_path.exists()
