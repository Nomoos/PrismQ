#!/usr/bin/env python3
"""Subtree management operations (Single Responsibility Principle)."""

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


class SubtreeManager:
    """Manages git subtree operations."""

    def __init__(
        self,
        git_ops: GitOperations,
        backup_mgr: BackupManager,
        path_resolver: PathResolver,
    ) -> None:
        """Initialize subtree manager with dependencies.

        Args:
            git_ops: Git operations implementation (Dependency Injection)
            backup_mgr: Backup manager implementation (Dependency Injection)
            path_resolver: Path resolver implementation (Dependency Injection)
        """
        self._git_ops = git_ops
        self._backup_mgr = backup_mgr
        self._path_resolver = path_resolver

    def add_subtree(
        self,
        superproj: Path,
        prefix_rel: str,
        remote_url: str,
        branch: str,
        remote_name: str,
    ) -> None:
        """Add a subtree to a repository.

        Args:
            superproj: Path to superproject repository
            prefix_rel: Relative prefix path for subtree
            remote_url: Remote URL for subtree
            branch: Branch to add
            remote_name: Name for remote

        Raises:
            CommandExecutionError: If subtree add fails
        """
        # Ensure remote is set up
        self._git_ops.ensure_remote(superproj, remote_name, remote_url)

        # Prepare target path and backup if exists
        target = (superproj / prefix_rel).resolve()
        backup = self._backup_mgr.create_backup(target)

        try:
            print(
                f"[DO] git -C {superproj} subtree add "
                f'--prefix="{prefix_rel}" {remote_name} {branch} --squash'
            )
            self._git_ops.subtree_add(superproj, prefix_rel, remote_name, branch)

            # Success - cleanup backup
            if backup:
                self._backup_mgr.cleanup_backup(backup)

        except CommandExecutionError as e:
            print(f"[ERROR] subtree add failed for {prefix_rel}: {e}")
            # Restore backup on failure
            if backup:
                self._backup_mgr.restore_backup(backup, target)
            raise
