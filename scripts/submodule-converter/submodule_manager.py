#!/usr/bin/env python3
"""Submodule management operations (Single Responsibility Principle)."""

from pathlib import Path

try:
    from .backup_manager import BackupManager
    from .exceptions import CommandExecutionError
    from .git_operations import GitOperations
    from .path_resolver import PathResolver
except ImportError:
    from backup_manager import BackupManager
    from exceptions import CommandExecutionError
    from git_operations import GitOperations
    from path_resolver import PathResolver


class SubmoduleManager:
    """Manages git submodule operations."""

    def __init__(
        self,
        git_ops: GitOperations,
        backup_mgr: BackupManager,
        path_resolver: PathResolver,
    ) -> None:
        """Initialize submodule manager with dependencies.

        Args:
            git_ops: Git operations implementation (Dependency Injection)
            backup_mgr: Backup manager implementation (Dependency Injection)
            path_resolver: Path resolver implementation (Dependency Injection)
        """
        self._git_ops = git_ops
        self._backup_mgr = backup_mgr
        self._path_resolver = path_resolver

    def add_submodule(
        self,
        superproj: Path,
        path_rel: str,
        remote_url: str,
        branch: str,
    ) -> None:
        """Add a submodule to a repository.

        Args:
            superproj: Path to superproject repository
            path_rel: Relative path for submodule
            remote_url: Remote URL for submodule
            branch: Branch to track

        Raises:
            CommandExecutionError: If submodule add fails
        """
        # Prepare target path and backup if exists
        target = (superproj / path_rel).resolve()
        backup = self._backup_mgr.create_backup(target)

        try:
            print(
                f"[DO] git -C {superproj} submodule add "
                f'-b {branch} {remote_url} "{path_rel}"'
            )
            self._git_ops.submodule_add(superproj, remote_url, path_rel, branch)

            # Success - cleanup backup
            if backup:
                self._backup_mgr.cleanup_backup(backup)

        except CommandExecutionError as e:
            print(f"[ERROR] submodule add failed for {path_rel}: {e}")
            # Restore backup on failure
            if backup:
                self._backup_mgr.restore_backup(backup, target)
            raise
