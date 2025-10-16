#!/usr/bin/env python3
"""Tests for submodule converter modules."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    from .backup_manager import BackupManager
    from .cli import SubmoduleConverter
    from .command_runner import CommandResult, SubprocessCommandRunner
    from .exceptions import (
        CommandExecutionError,
        PathResolutionError,
    )
    from .git_operations import GitOperationsImpl
    from .path_resolver import PathResolver
    from .repository_scanner import RepositoryScanner
    from .submodule_manager import SubmoduleManager
except ImportError:
    # Fallback for direct execution
    from backup_manager import BackupManager
    from cli import SubmoduleConverter
    from command_runner import CommandResult, SubprocessCommandRunner
    from exceptions import (
        CommandExecutionError,
        PathResolutionError,
    )
    from git_operations import GitOperationsImpl
    from path_resolver import PathResolver
    from repository_scanner import RepositoryScanner
    from submodule_manager import SubmoduleManager


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

    def test_normalize_path_removes_leading_mod(self):
        """Test that leading 'mod/' is removed from paths."""
        result = PathResolver.normalize_path_in_module(
            Path("mod/Sources"), ["mod", "Sources"]
        )
        assert result == Path("Sources")

    def test_normalize_path_keeps_other_paths(self):
        """Test that non-mod paths are kept as-is."""
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

    def test_get_default_branch_ultimate_fallback(self):
        """Test getting default branch with ultimate fallback to main."""
        runner = MagicMock()
        runner.run.side_effect = [
            CommandResult(1, "", ""),  # symbolic-ref fails
            CommandResult(1, "", ""),  # rev-parse fails
        ]
        git_ops = GitOperationsImpl(runner)

        branch = git_ops.get_default_branch(Path("/repo"))

        assert branch == "main"

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

    def test_path_exists_in_index_returns_true(self):
        """Test checking if path exists in index returns True."""
        runner = MagicMock()
        runner.run.return_value = CommandResult(0, "mod/IdeaInspiration/file.txt", "")
        git_ops = GitOperationsImpl(runner)

        exists = git_ops.path_exists_in_index(Path("/repo"), "mod/IdeaInspiration")

        assert exists is True
        runner.run.assert_called_once()

    def test_path_exists_in_index_returns_false(self):
        """Test checking if path exists in index returns False."""
        runner = MagicMock()
        runner.run.return_value = CommandResult(0, "", "")
        git_ops = GitOperationsImpl(runner)

        exists = git_ops.path_exists_in_index(Path("/repo"), "mod/NonExistent")

        assert exists is False

    def test_remove_from_index(self):
        """Test removing path from git index."""
        runner = MagicMock()
        runner.run.return_value = CommandResult(0, "", "")
        git_ops = GitOperationsImpl(runner)

        git_ops.remove_from_index(Path("/repo"), "mod/IdeaInspiration")

        runner.run.assert_called_once()
        call_args = runner.run.call_args
        assert "git" in call_args[0][0]
        assert "rm" in call_args[0][0]
        assert "--cached" in call_args[0][0]
        assert "mod/IdeaInspiration" in call_args[0][0]


class TestRepositoryScanner:
    """Test suite for repository scanner."""

    def test_find_nested_repositories(self, tmp_path):
        """Test finding nested repositories."""
        # Create structure: mod/Module/.git and mod/Module/Nested/.git
        mod = tmp_path / "mod"
        module = mod / "Module"
        nested = module / "Nested"

        module.mkdir(parents=True)
        nested.mkdir(parents=True)
        (module / ".git").mkdir()
        (nested / ".git").mkdir()

        scanner = RepositoryScanner()
        nested_repos = scanner.find_nested_repositories(mod)

        # Should find only the nested one, not the module root
        assert len(nested_repos) == 1
        assert nested_repos[0].module_name == "Module"
        assert nested_repos[0].path == nested
        assert nested_repos[0].depth == 0  # No nested mod/ directories

    def test_find_module_roots(self, tmp_path):
        """Test finding module root repositories."""
        # Create structure: mod/Module1/.git and mod/Module2/.git
        mod = tmp_path / "mod"
        module1 = mod / "Module1"
        module2 = mod / "Module2"

        module1.mkdir(parents=True)
        module2.mkdir(parents=True)
        (module1 / ".git").mkdir()
        (module2 / ".git").mkdir()

        scanner = RepositoryScanner()
        module_repos = scanner.find_module_roots(mod)

        assert len(module_repos) == 2
        assert any(r.module_name == "Module1" for r in module_repos)
        assert any(r.module_name == "Module2" for r in module_repos)
        # Both should be top-level (depth 0, no parent_module)
        assert all(r.depth == 0 for r in module_repos)
        assert all(r.parent_module is None for r in module_repos)

    def test_find_nested_module_hierarchy(self, tmp_path):
        """Test finding deeply nested module hierarchy.
        
        Structure:
        mod/
          IdeaInspiration/.git          <- module root, depth 0
            mod/
              Classification/.git       <- nested module root, depth 1
                mod/
                  DeepModule/.git       <- deeply nested module root, depth 2
        """
        mod = tmp_path / "mod"
        idea = mod / "IdeaInspiration"
        idea_mod = idea / "mod"
        classification = idea_mod / "Classification"
        classification_mod = classification / "mod"
        deep = classification_mod / "DeepModule"

        # Create directories
        idea.mkdir(parents=True)
        (idea / ".git").mkdir()
        idea_mod.mkdir()
        classification.mkdir(parents=True)
        (classification / ".git").mkdir()
        classification_mod.mkdir()
        deep.mkdir(parents=True)
        (deep / ".git").mkdir()

        scanner = RepositoryScanner()
        module_repos = scanner.find_module_roots(mod)

        # Should find all three module roots
        assert len(module_repos) == 3
        
        # Check they're sorted by depth (deepest first)
        assert module_repos[0].depth == 2  # DeepModule
        assert module_repos[1].depth == 1  # Classification
        assert module_repos[2].depth == 0  # IdeaInspiration
        
        # Verify the deepest module
        deep_module = module_repos[0]
        assert deep_module.module_name == "DeepModule"
        assert deep_module.path == deep
        assert deep_module.parent_module == classification
        
        # Verify the middle module
        middle_module = module_repos[1]
        assert middle_module.module_name == "Classification"
        assert middle_module.path == classification
        assert middle_module.parent_module == idea
        
        # Verify the top-level module
        top_module = module_repos[2]
        assert top_module.module_name == "IdeaInspiration"
        assert top_module.path == idea
        assert top_module.parent_module is None

    def test_find_nested_repos_in_hierarchy(self, tmp_path):
        """Test finding nested repos within a hierarchical module structure.
        
        Structure:
        mod/
          IdeaInspiration/.git          <- module root
            mod/
              Classification/.git       <- nested module root
                SomeRepo/.git           <- nested repo (not a module)
        """
        mod = tmp_path / "mod"
        idea = mod / "IdeaInspiration"
        idea_mod = idea / "mod"
        classification = idea_mod / "Classification"
        some_repo = classification / "SomeRepo"

        # Create directories
        idea.mkdir(parents=True)
        (idea / ".git").mkdir()
        idea_mod.mkdir()
        classification.mkdir(parents=True)
        (classification / ".git").mkdir()
        some_repo.mkdir(parents=True)
        (some_repo / ".git").mkdir()

        scanner = RepositoryScanner()
        nested_repos = scanner.find_nested_repositories(mod)

        # Should find the nested repo (SomeRepo) but not the module roots
        assert len(nested_repos) == 1
        assert nested_repos[0].path == some_repo
        assert nested_repos[0].module_root == classification
        assert nested_repos[0].module_name == "Classification"


class TestSubmoduleManager:
    """Test suite for submodule manager."""

    def test_add_submodule_success(self, tmp_path):
        """Test successful submodule addition without backup."""
        git_ops = MagicMock()
        backup_mgr = MagicMock()
        backup_mgr.create_backup.return_value = None
        path_resolver = PathResolver()

        submodule_mgr = SubmoduleManager(git_ops, backup_mgr, path_resolver)

        submodule_mgr.add_submodule(
            tmp_path,
            "prefix",
            "https://github.com/test/repo.git",
            "main",
        )

        git_ops.submodule_add.assert_called_once()
        backup_mgr.create_backup.assert_called_once()
        # cleanup_backup is not called when no backup was created
        backup_mgr.cleanup_backup.assert_not_called()

    def test_add_submodule_success_with_backup(self, tmp_path):
        """Test successful submodule addition with backup cleanup."""
        git_ops = MagicMock()
        backup_path = tmp_path / "backup"
        backup_mgr = MagicMock()
        backup_mgr.create_backup.return_value = backup_path
        path_resolver = PathResolver()

        submodule_mgr = SubmoduleManager(git_ops, backup_mgr, path_resolver)

        submodule_mgr.add_submodule(
            tmp_path,
            "prefix",
            "https://github.com/test/repo.git",
            "main",
        )

        git_ops.submodule_add.assert_called_once()
        backup_mgr.create_backup.assert_called_once()
        backup_mgr.cleanup_backup.assert_called_once_with(backup_path)

    def test_add_submodule_with_backup_restore_on_failure(self, tmp_path):
        """Test submodule addition restores backup on failure."""
        git_ops = MagicMock()
        git_ops.path_exists_in_index.return_value = False
        git_ops.submodule_add.side_effect = CommandExecutionError("Failed")

        backup_path = tmp_path / "backup"
        backup_mgr = MagicMock()
        backup_mgr.create_backup.return_value = backup_path

        path_resolver = PathResolver()
        submodule_mgr = SubmoduleManager(git_ops, backup_mgr, path_resolver)

        with pytest.raises(CommandExecutionError):
            submodule_mgr.add_submodule(
                tmp_path,
                "prefix",
                "https://github.com/test/repo.git",
                "main",
            )

        backup_mgr.restore_backup.assert_called_once()

    def test_add_submodule_removes_index_entries_when_present(self, tmp_path):
        """Test submodule addition removes index entries when they exist."""
        git_ops = MagicMock()
        git_ops.path_exists_in_index.return_value = True
        backup_mgr = MagicMock()
        backup_mgr.create_backup.return_value = None
        path_resolver = PathResolver()

        submodule_mgr = SubmoduleManager(git_ops, backup_mgr, path_resolver)

        submodule_mgr.add_submodule(
            tmp_path,
            "mod/IdeaInspiration",
            "https://github.com/test/repo.git",
            "main",
        )

        git_ops.path_exists_in_index.assert_called_once_with(tmp_path, "mod/IdeaInspiration")
        git_ops.remove_from_index.assert_called_once_with(tmp_path, "mod/IdeaInspiration")
        git_ops.submodule_add.assert_called_once()


class TestCommandResult:
    """Test suite for CommandResult."""

    def test_success_property(self):
        """Test success property."""
        assert CommandResult(0).success
        assert not CommandResult(1).success
        assert not CommandResult(-1).success


class TestSubmoduleConverter:
    """Test suite for SubmoduleConverter."""

    def test_convert_nested_repos_preserves_mod_prefix(self, tmp_path):
        """Test that nested repositories preserve mod/ directory structure.
        
        This tests the fix for the bug where Classification should be added at
        PrismQ/mod/IdeaInspiration/mod/Classification, not at
        PrismQ/mod/IdeaInspiration/Classification.
        """
        # Setup mocks
        scanner = MagicMock()
        
        # Create mock nested repo: IdeaInspiration/mod/Classification
        nested_repo = MagicMock()
        nested_repo.path = tmp_path / "mod" / "IdeaInspiration" / "mod" / "Classification"
        nested_repo.module_root = tmp_path / "mod" / "IdeaInspiration"
        nested_repo.module_name = "IdeaInspiration"
        nested_repo.relative_in_module = "mod/Classification"
        nested_repo.depth = 1
        
        scanner.find_nested_repositories.return_value = [nested_repo]
        
        submodule_mgr = MagicMock()
        git_ops = MagicMock()
        git_ops.get_remote_url.return_value = "https://github.com/test/Classification.git"
        git_ops.get_default_branch.return_value = "main"
        
        path_resolver = PathResolver()
        
        # Create converter
        converter = SubmoduleConverter(scanner, submodule_mgr, git_ops, path_resolver)
        
        # Convert nested repos
        mod_root = tmp_path / "mod"
        converter.convert_nested_to_submodules(mod_root)
        
        # Verify submodule was added with "mod/Classification" path (preserving mod/ prefix)
        submodule_mgr.add_submodule.assert_called_once_with(
            tmp_path / "mod" / "IdeaInspiration",
            "mod/Classification",
            "https://github.com/test/Classification.git",
            "main",
        )

    def test_convert_modules_uses_mod_prefix(self, tmp_path):
        """Test that module roots are added with mod/ prefix."""
        # Setup mocks
        scanner = MagicMock()
        module_repo = MagicMock()
        module_repo.module_name = "TestModule"
        module_repo.path = tmp_path / "mod" / "TestModule"
        module_repo.parent_module = None  # Top-level module
        scanner.find_module_roots.return_value = [module_repo]
        
        submodule_mgr = MagicMock()
        git_ops = MagicMock()
        git_ops.get_remote_url.return_value = "https://github.com/test/repo.git"
        git_ops.get_default_branch.return_value = "main"
        
        path_resolver = PathResolver()
        
        # Create converter
        converter = SubmoduleConverter(scanner, submodule_mgr, git_ops, path_resolver)
        
        # Convert modules
        prismq_root = tmp_path
        mod_root = tmp_path / "mod"
        converter.convert_modules_to_submodules(prismq_root, mod_root)
        
        # Verify submodule was added with "mod/TestModule" path
        submodule_mgr.add_submodule.assert_called_once_with(
            prismq_root,
            "mod/TestModule",
            "https://github.com/test/repo.git",
            "main",
        )

    def test_convert_nested_modules_in_depth_order(self, tmp_path):
        """Test that nested modules are converted in correct order (deepest first)."""
        # Setup mocks
        scanner = MagicMock()
        
        # Create mock repos: IdeaInspiration (depth 0) and Classification (depth 1)
        idea_repo = MagicMock()
        idea_repo.module_name = "IdeaInspiration"
        idea_repo.path = tmp_path / "mod" / "IdeaInspiration"
        idea_repo.parent_module = None
        idea_repo.depth = 0
        
        classification_repo = MagicMock()
        classification_repo.module_name = "Classification"
        classification_repo.path = tmp_path / "mod" / "IdeaInspiration" / "mod" / "Classification"
        classification_repo.parent_module = idea_repo.path
        classification_repo.depth = 1
        
        # Scanner returns them in depth order (deepest first)
        scanner.find_module_roots.return_value = [classification_repo, idea_repo]
        
        submodule_mgr = MagicMock()
        git_ops = MagicMock()
        git_ops.get_remote_url.return_value = "https://github.com/test/repo.git"
        git_ops.get_default_branch.return_value = "main"
        
        path_resolver = PathResolver()
        
        # Create converter
        converter = SubmoduleConverter(scanner, submodule_mgr, git_ops, path_resolver)
        
        # Convert modules
        prismq_root = tmp_path
        mod_root = tmp_path / "mod"
        converter.convert_modules_to_submodules(prismq_root, mod_root)
        
        # Verify both submodules were added
        assert submodule_mgr.add_submodule.call_count == 2
        
        # First call should be for Classification (deeper, added to IdeaInspiration)
        first_call = submodule_mgr.add_submodule.call_args_list[0]
        assert first_call[0][0] == classification_repo.parent_module  # Parent is IdeaInspiration
        assert first_call[0][1] == "mod/Classification"
        
        # Second call should be for IdeaInspiration (top-level, added to PrismQ)
        second_call = submodule_mgr.add_submodule.call_args_list[1]
        assert second_call[0][0] == prismq_root
        assert second_call[0][1] == "mod/IdeaInspiration"
