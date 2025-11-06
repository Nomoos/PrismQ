"""SQLite online backup implementation for task queue."""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, NamedTuple
from dataclasses import dataclass

from .database import QueueDatabase
from .exceptions import QueueDatabaseError


class QueueBackupError(QueueDatabaseError):
    """Exception raised when backup operations fail."""
    pass


@dataclass
class BackupInfo:
    """Information about a backup file."""
    
    path: Path
    size_bytes: int
    created_at: datetime
    
    @property
    def size_mb(self) -> float:
        """Get backup size in megabytes."""
        return self.size_bytes / (1024 * 1024)
    
    @classmethod
    def from_path(cls, path: Path) -> "BackupInfo":
        """Create BackupInfo from a backup file path."""
        stat = path.stat()
        return cls(
            path=path,
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_mtime)
        )


class QueueBackup:
    """
    SQLite online backup implementation.
    
    Uses SQLite backup API for non-blocking backup while database is in use.
    Follows SOLID principles:
    - Single Responsibility: Manages backup operations only
    - Dependency Inversion: Depends on QueueDatabase abstraction
    """

    def __init__(self, db: QueueDatabase, backup_dir: Optional[str] = None):
        """
        Initialize backup manager.
        
        Args:
            db: QueueDatabase instance to backup
            backup_dir: Directory for backup files. If None, uses default.
                       Default Windows: C:\\Data\\PrismQ\\queue\\backups
                       Default Linux/macOS: /tmp/prismq/queue/backups
        """
        self.db = db
        
        if backup_dir is None:
            import os
            if os.name == "nt":  # Windows
                backup_dir = r"C:\Data\PrismQ\queue\backups"
            else:  # Linux/macOS
                backup_dir = "/tmp/prismq/queue/backups"
        
        self.backup_dir = Path(backup_dir)
        self._ensure_backup_dir_exists()

    def _ensure_backup_dir_exists(self) -> None:
        """Create backup directory if it doesn't exist."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _generate_backup_name(self, name: Optional[str] = None) -> str:
        """
        Generate backup filename.
        
        Args:
            name: Optional custom name
            
        Returns:
            Backup filename with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if name:
            return f"queue_backup_{name}_{timestamp}.db"
        return f"queue_backup_{timestamp}.db"

    def create_backup(self, name: Optional[str] = None) -> Path:
        """
        Create a backup of the queue database.
        
        Uses SQLite online backup API which allows backup while database is in use.
        The backup is performed page-by-page to minimize locking.
        
        Args:
            name: Optional backup name (default: timestamp-based)
            
        Returns:
            Path to created backup file
            
        Raises:
            QueueBackupError: If backup fails
        """
        backup_filename = self._generate_backup_name(name)
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Get source connection
            source_conn = self.db.get_connection()
            
            # Create backup connection
            backup_conn = sqlite3.connect(str(backup_path))
            
            try:
                # Perform online backup using SQLite backup API
                # This copies pages incrementally to avoid blocking
                source_conn.backup(backup_conn, pages=100, sleep=0.1)
                
                # Ensure all changes are written
                backup_conn.commit()
                
            finally:
                backup_conn.close()
            
            # Verify backup was created
            if not backup_path.exists():
                raise QueueBackupError(f"Backup file not created: {backup_path}")
            
            return backup_path
            
        except sqlite3.Error as e:
            # Clean up failed backup
            if backup_path.exists():
                backup_path.unlink()
            raise QueueBackupError(f"Backup failed: {e}") from e

    def verify_backup(self, backup_path: Path) -> bool:
        """
        Verify backup integrity.
        
        Opens backup database and runs integrity check.
        
        Args:
            backup_path: Path to backup file to verify
            
        Returns:
            True if backup is valid and intact
            
        Raises:
            QueueBackupError: If backup verification fails
        """
        if not backup_path.exists():
            raise QueueBackupError(f"Backup file not found: {backup_path}")
        
        try:
            conn = sqlite3.connect(str(backup_path), timeout=5.0)
            try:
                # Run integrity check
                cursor = conn.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                # SQLite returns "ok" if database is intact
                is_valid = result and result[0] == "ok"
                
                if not is_valid:
                    # Get all integrity check messages
                    cursor = conn.execute("PRAGMA integrity_check")
                    errors = [row[0] for row in cursor.fetchall()]
                    raise QueueBackupError(
                        f"Backup integrity check failed: {', '.join(errors)}"
                    )
                
                return True
                
            finally:
                conn.close()
                
        except sqlite3.Error as e:
            raise QueueBackupError(f"Failed to verify backup: {e}") from e

    def restore_backup(self, backup_path: Path, target_path: Optional[Path] = None) -> None:
        """
        Restore database from backup.
        
        WARNING: This will overwrite the target database.
        The current database should be closed before restoring.
        
        Args:
            backup_path: Path to backup file
            target_path: Path to restore to (default: current database path)
            
        Raises:
            QueueBackupError: If restore fails
        """
        if not backup_path.exists():
            raise QueueBackupError(f"Backup file not found: {backup_path}")
        
        # Verify backup before restoring
        self.verify_backup(backup_path)
        
        if target_path is None:
            target_path = self.db.db_path
        
        try:
            # Close existing connection if any
            self.db.close()
            
            # Copy backup to target location
            import shutil
            shutil.copy2(backup_path, target_path)
            
        except (OSError, IOError) as e:
            raise QueueBackupError(f"Failed to restore backup: {e}") from e

    def list_backups(self) -> List[BackupInfo]:
        """
        List available backups with metadata.
        
        Returns:
            List of BackupInfo objects sorted by creation time (newest first)
        """
        backup_files = self.backup_dir.glob("queue_backup_*.db")
        backups = [BackupInfo.from_path(f) for f in backup_files]
        
        # Sort by creation time, newest first
        backups.sort(key=lambda b: b.created_at, reverse=True)
        
        return backups

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Remove old backups, keeping most recent N.
        
        Args:
            keep_count: Number of recent backups to keep (default: 10)
            
        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()
        
        # Skip if we don't have more than keep_count
        if len(backups) <= keep_count:
            return 0
        
        # Delete old backups
        backups_to_delete = backups[keep_count:]
        deleted_count = 0
        
        for backup in backups_to_delete:
            try:
                backup.path.unlink()
                deleted_count += 1
            except OSError:
                # Continue even if delete fails
                pass
        
        return deleted_count

    def get_latest_backup(self) -> Optional[BackupInfo]:
        """
        Get the most recent backup.
        
        Returns:
            BackupInfo for latest backup, or None if no backups exist
        """
        backups = self.list_backups()
        return backups[0] if backups else None
