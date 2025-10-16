#!/usr/bin/env python3
"""Tests for subtree converter modules."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    from .backup_manager import BackupManager
    from .command_runner import CommandResult, SubprocessCommandRunner
    from .exceptions import (
        CommandExecutionError,
        PathResolutionError,
    )
    from .git_operations import GitOperationsImpl
    from .path_resolver import PathResolver
    from .repository_scanner import RepositoryScanner
    from .subtree_manager import SubtreeManager
except ImportError:
    # Fallback for direct execution
    from backup_manager import BackupManager
    from command_runner import CommandResult, SubprocessCommandRunner
    from exceptions import (
        CommandExecutionError,
        PathResolutionError,
    )
    from git_operations import GitOperationsImpl
    from path_resolver import PathResolver
    from repository_scanner import RepositoryScanner
    from subtree_manager import SubtreeManager


class TestCommandRunner:
    """Test suite for command runner."""

    def test_successful_command(self):
        """Test successful command execution."""
        runner = SubprocessCommandRunner()
        result = runner.run(["echo", "hello"], capture=True, check=False)
        assert result.success
        assert "hello" in result.stdout

    def test_failed_command_with_check(self):
        """Test failed command with check=True raises exception."""
        runner = SubprocessCommandRunner()
        with pytest.raises(CommandExecutionError):
            runner.run(["false"], check=True)

    def test_failed_command_without_check(self):
        """Test failed command with check=False returns result."""
        runner = SubprocessCommandRunner()
        result = runner.run(["false"], check=False)
        assert not result.success
        assert result.returncode != 0


class TestPathResolver:
    """Test suite for path resolver."""

    def test_sanitize_remote_name(self):
        """Test remote name sanitization."""
        assert PathResolver.sanitize_remote_name("foo/bar:baz") == "foo_bar_baz"
        assert PathResolver.sanitize_remote_name("normal-name") == "normal-name"
        assert PathResolver.sanitize_remote_name("name@with.dots") == "name_with_dots"

    def test_normalize_path_removes_leading_src(self):
        """Test that leading 'src/' is removed from paths."""
        result = PathResolver.normalize_path_in_module(
            Path("src/Sources"), ["src", "Sources"]
        )
        assert result == Path("Sources")

    def test_normalize_path_keeps_other_paths(self):
        """Test that non-src paths are kept as-is."""
        result = PathResolver.normalize_path_in_module(
            Path("Content/Data"), ["Content", "Data"]
        )
        assert result == Path("Content/Data")

    def test_find_prismq_root_not_found(self):
        """Test error when .git is not found."""
        with patch("pathlib.Path.cwd", return_value=Path("/tmp")):
            with pytest.raises(PathResolutionError):
                PathResolver.find_prismq_root()


class TestBackupManager:
    """Test suite for backup manager."""

    def test_create_backup_nonexistent_directory(self, tmp_path):
        """Test backup creation when directory doesn't exist."""
        target = tmp_path / "nonexistent"
        backup = BackupManager.create_backup(target)
        assert backup is None

    def test_create_backup_existing_directory(self, tmp_path):
        """Test backup creation for existing directory."""
        target = tmp_path / "existing"
        target.mkdir()
        (target / "file.txt").write_text("content")

        backup = BackupManager.create_backup(target)

        assert backup is not None
        assert backup.exists()
        assert not target.exists()
        assert (backup / "file.txt").read_text() == "content"

        # Cleanup
        if backup.exists():
            shutil.rmtree(backup)

    def test_restore_backup(self, tmp_path):
        """Test backup restoration."""
        backup = tmp_path / "backup"
        backup.mkdir()
        (backup / "file.txt").write_text("content")

        target = tmp_path / "target"

        BackupManager.restore_backup(backup, target)

        assert target.exists()
        assert not backup.exists()
        assert (target / "file.txt").read_text() == "content"

    def test_cleanup_backup(self, tmp_path):
        """Test backup cleanup."""
        backup = tmp_path / "backup"
        backup.mkdir()

        BackupManager.cleanup_backup(backup)

        assert not backup.exists()


class TestGitOperations:
    """Test suite for git operations."""

    def test_get_remote_url_success(self):
        """Test getting remote URL successfully."""
        runner = MagicMock()
        runner.run.return_value = CommandResult(0, "https://github.com/test/repo.git", "")
        git_ops = GitOperationsImpl(runner)

        url = git_ops.get_remote_url(Path("/repo"))

        assert url == "https://github.com/test/repo.git"
        runner.run.assert_called_once()

    def test_get_remote_url_not_found(self):
        """Test getting remote URL when not found."""
        runner = MagicMock()
        runner.run.return_value = CommandResult(1, "", "not found")
        git_ops = GitOperationsImpl(runner)

        url = git_ops.get_remote_url(Path("/repo"))

        assert url is None

    def test_get_default_branch_from_symbolic_ref(self):
        """Test getting default branch from symbolic-ref."""
        runner = MagicMock()
        runner.run.side_effect = [
            CommandResult(0, "origin/main", ""),
        ]
        git_ops = GitOperationsImpl(runner)

        branch = git_ops.get_default_branch(Path("/repo"))

        assert branch == "main"

    def test_get_default_branch_fallback(self):
        """Test getting default branch with fallback."""
        runner = MagicMock()
        runner.run.side_effect = [
            CommandResult(1, "", ""),  # symbolic-ref fails
            CommandResult(0, "develop", ""),  # rev-parse succeeds
        ]
        git_ops = GitOperationsImpl(runner)

        branch = git_ops.get_default_branch(Path("/repo"))

        assert branch == "develop"

    def test_ensure_remote_adds_new_remote(self):
        """Test ensuring remote adds it when missing."""
        runner = MagicMock()
        runner.run.side_effect = [
            CommandResult(1, "", "not found"),  # get-url fails
            CommandResult(0, "", ""),  # add succeeds
        ]
        git_ops = GitOperationsImpl(runner)

        git_ops.ensure_remote(Path("/repo"), "origin", "https://github.com/test/repo.git")

        assert runner.run.call_count == 2

    def test_ensure_remote_updates_existing_remote(self):
        """Test ensuring remote updates URL when different."""
        runner = MagicMock()
        runner.run.side_effect = [
            CommandResult(0, "https://old.url", ""),  # get-url succeeds
            CommandResult(0, "", ""),  # set-url succeeds
        ]
        git_ops = GitOperationsImpl(runner)

        git_ops.ensure_remote(Path("/repo"), "origin", "https://new.url")

        assert runner.run.call_count == 2


class TestRepositoryScanner:
    """Test suite for repository scanner."""

    def test_find_nested_repositories(self, tmp_path):
        """Test finding nested repositories."""
        # Create structure: src/Module/.git and src/Module/Nested/.git
        src = tmp_path / "src"
        module = src / "Module"
        nested = module / "Nested"

        module.mkdir(parents=True)
        nested.mkdir(parents=True)
        (module / ".git").mkdir()
        (nested / ".git").mkdir()

        scanner = RepositoryScanner()
        nested_repos = scanner.find_nested_repositories(src)

        # Should find only the nested one, not the module root
        assert len(nested_repos) == 1
        assert nested_repos[0].module_name == "Module"
        assert nested_repos[0].path == nested

    def test_find_module_roots(self, tmp_path):
        """Test finding module root repositories."""
        # Create structure: src/Module1/.git and src/Module2/.git
        src = tmp_path / "src"
        module1 = src / "Module1"
        module2 = src / "Module2"

        module1.mkdir(parents=True)
        module2.mkdir(parents=True)
        (module1 / ".git").mkdir()
        (module2 / ".git").mkdir()

        scanner = RepositoryScanner()
        module_repos = scanner.find_module_roots(src)

        assert len(module_repos) == 2
        assert any(r.module_name == "Module1" for r in module_repos)
        assert any(r.module_name == "Module2" for r in module_repos)


class TestSubtreeManager:
    """Test suite for subtree manager."""

    def test_add_subtree_success(self, tmp_path):
        """Test successful subtree addition without backup."""
        git_ops = MagicMock()
        backup_mgr = MagicMock()
        backup_mgr.create_backup.return_value = None
        path_resolver = PathResolver()

        subtree_mgr = SubtreeManager(git_ops, backup_mgr, path_resolver)

        subtree_mgr.add_subtree(
            tmp_path,
            "prefix",
            "https://github.com/test/repo.git",
            "main",
            "remote_name",
        )

        git_ops.ensure_remote.assert_called_once()
        git_ops.subtree_add.assert_called_once()
        backup_mgr.create_backup.assert_called_once()
        # cleanup_backup is not called when no backup was created
        backup_mgr.cleanup_backup.assert_not_called()

    def test_add_subtree_success_with_backup(self, tmp_path):
        """Test successful subtree addition with backup cleanup."""
        git_ops = MagicMock()
        backup_path = tmp_path / "backup"
        backup_mgr = MagicMock()
        backup_mgr.create_backup.return_value = backup_path
        path_resolver = PathResolver()

        subtree_mgr = SubtreeManager(git_ops, backup_mgr, path_resolver)

        subtree_mgr.add_subtree(
            tmp_path,
            "prefix",
            "https://github.com/test/repo.git",
            "main",
            "remote_name",
        )

        git_ops.ensure_remote.assert_called_once()
        git_ops.subtree_add.assert_called_once()
        backup_mgr.create_backup.assert_called_once()
        backup_mgr.cleanup_backup.assert_called_once_with(backup_path)

    def test_add_subtree_with_backup_restore_on_failure(self, tmp_path):
        """Test subtree addition restores backup on failure."""
        git_ops = MagicMock()
        git_ops.subtree_add.side_effect = CommandExecutionError("Failed")

        backup_path = tmp_path / "backup"
        backup_mgr = MagicMock()
        backup_mgr.create_backup.return_value = backup_path

        path_resolver = PathResolver()
        subtree_mgr = SubtreeManager(git_ops, backup_mgr, path_resolver)

        with pytest.raises(CommandExecutionError):
            subtree_mgr.add_subtree(
                tmp_path,
                "prefix",
                "https://github.com/test/repo.git",
                "main",
                "remote_name",
            )

        backup_mgr.restore_backup.assert_called_once()


class TestCommandResult:
    """Test suite for CommandResult."""

    def test_success_property(self):
        """Test success property."""
        assert CommandResult(0).success
        assert not CommandResult(1).success
        assert not CommandResult(-1).success
