#!/usr/bin/env python3
"""Git-specific operations (Single Responsibility Principle)."""

from pathlib import Path
from typing import Protocol

try:
    from .command_runner import CommandRunner
except ImportError:
    from command_runner import CommandRunner


class GitOperations(Protocol):
    """Protocol for git operations (Interface Segregation Principle)."""

    def get_remote_url(self, repo_path: Path, remote: str = "origin") -> str | None:
        """Get remote URL for a repository.

        Args:
            repo_path: Path to git repository
            remote: Remote name (default: origin)

        Returns:
            Remote URL or None if not found
        """
        ...

    def get_default_branch(self, repo_path: Path) -> str:
        """Get default branch for a repository.

        Args:
            repo_path: Path to git repository

        Returns:
            Default branch name
        """
        ...

    def ensure_remote(self, repo_path: Path, name: str, url: str) -> None:
        """Ensure remote exists with correct URL.

        Args:
            repo_path: Path to git repository
            name: Remote name
            url: Remote URL
        """
        ...

    def subtree_add(
        self,
        repo_path: Path,
        prefix: str,
        remote_name: str,
        branch: str,
    ) -> None:
        """Add a subtree to repository.

        Args:
            repo_path: Path to git repository
            prefix: Prefix path for subtree
            remote_name: Remote name
            branch: Branch to add
        """
        ...


class GitOperationsImpl:
    """Concrete implementation of git operations."""

    def __init__(self, runner: CommandRunner) -> None:
        """Initialize git operations with command runner.

        Args:
            runner: Command runner implementation (Dependency Injection)
        """
        self._runner = runner

    def get_remote_url(self, repo_path: Path, remote: str = "origin") -> str | None:
        """Get remote URL for a repository.

        Args:
            repo_path: Path to git repository
            remote: Remote name (default: origin)

        Returns:
            Remote URL or None if not found
        """
        result = self._runner.run(
            ["git", "config", "--get", f"remote.{remote}.url"],
            cwd=repo_path,
            check=False,
            capture=True,
        )
        if result.success:
            return result.stdout.strip()
        return None

    def get_default_branch(self, repo_path: Path) -> str:
        """Get default branch for a repository.

        Args:
            repo_path: Path to git repository

        Returns:
            Default branch name
        """
        # Try symbolic-ref for remote HEAD
        result = self._runner.run(
            ["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
            cwd=repo_path,
            check=False,
            capture=True,
        )
        if result.success:
            ref = result.stdout.strip()  # "origin/main"
            if "/" in ref:
                return ref.split("/", 1)[1]

        # Try current branch
        result = self._runner.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            check=False,
            capture=True,
        )
        if result.success:
            branch = result.stdout.strip()
            if branch and branch != "HEAD":
                return branch

        # Default fallback
        return "main"

    def ensure_remote(self, repo_path: Path, name: str, url: str) -> None:
        """Ensure remote exists with correct URL.

        Args:
            repo_path: Path to git repository
            name: Remote name
            url: Remote URL
        """
        result = self._runner.run(
            ["git", "remote", "get-url", name],
            cwd=repo_path,
            check=False,
            capture=True,
        )

        if not result.success:
            # Remote doesn't exist, add it
            self._runner.run(
                ["git", "remote", "add", name, url],
                cwd=repo_path,
                check=True,
            )
        else:
            # Remote exists, update URL if different
            current_url = result.stdout.strip()
            if current_url != url:
                self._runner.run(
                    ["git", "remote", "set-url", name, url],
                    cwd=repo_path,
                    check=True,
                )

    def subtree_add(
        self,
        repo_path: Path,
        prefix: str,
        remote_name: str,
        branch: str,
    ) -> None:
        """Add a subtree to repository.

        Args:
            repo_path: Path to git repository
            prefix: Prefix path for subtree
            remote_name: Remote name
            branch: Branch to add
        """
        self._runner.run(
            ["git", "subtree", "add", "--prefix", prefix, remote_name, branch, "--squash"],
            cwd=repo_path,
            check=True,
        )
