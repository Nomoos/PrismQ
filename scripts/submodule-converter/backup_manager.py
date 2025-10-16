#!/usr/bin/env python3
"""Backup management for subtree operations (Single Responsibility Principle)."""

import shutil
import time
from pathlib import Path

try:
    from .exceptions import BackupError
except ImportError:
    from exceptions import BackupError


class BackupManager:
    """Manages backup and restore operations for directories."""

    @staticmethod
    def create_backup(target: Path) -> Path | None:
        """Create a backup of a directory if it exists.

        Args:
            target: Path to directory to backup

        Returns:
            Path to backup location, or None if directory doesn't exist

        Raises:
            BackupError: If backup creation fails
        """
        if not target.exists():
            return None

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = Path(f"{target}.pre_subtree.{timestamp}")

        try:
            print(f"[INFO] Backing up existing path: {target} -> {backup_path}")
            shutil.move(str(target), str(backup_path))
            return backup_path
        except (OSError, shutil.Error) as e:
            raise BackupError(f"Failed to create backup: {e}") from e

    @staticmethod
    def restore_backup(backup: Path, target: Path) -> None:
        """Restore a directory from backup.

        Args:
            backup: Path to backup location
            target: Path to restore to

        Raises:
            BackupError: If restore fails
        """
        if not backup.exists():
            return

        try:
            print(f"[INFO] Restoring backup: {backup} -> {target}")
            shutil.move(str(backup), str(target))
        except (OSError, shutil.Error) as e:
            raise BackupError(f"Failed to restore backup: {e}") from e

    @staticmethod
    def cleanup_backup(backup: Path) -> None:
        """Remove a backup directory.

        Args:
            backup: Path to backup to remove
        """
        if not backup.exists():
            return

        try:
            print(f"[CLEAN] Removing backup: {backup}")
            shutil.rmtree(backup, ignore_errors=True)
        except OSError as e:
            print(f"[WARN] Could not remove backup {backup}: {e}")
