#!/usr/bin/env python3
"""CLI interface and main workflow for subtree converter."""

import sys
from pathlib import Path

try:
    from .backup_manager import BackupManager
    from .command_runner import SubprocessCommandRunner
    from .exceptions import RepositoryNotFoundError, SubtreeConverterError
    from .git_operations import GitOperationsImpl
    from .path_resolver import PathResolver
    from .repository_scanner import RepositoryScanner
    from .subtree_manager import SubtreeManager
except ImportError:
    from backup_manager import BackupManager
    from command_runner import SubprocessCommandRunner
    from exceptions import RepositoryNotFoundError, SubtreeConverterError
    from git_operations import GitOperationsImpl
    from path_resolver import PathResolver
    from repository_scanner import RepositoryScanner
    from subtree_manager import SubtreeManager


class SubtreeConverter:
    """Main orchestrator for subtree conversion (Single Responsibility Principle)."""

    def __init__(
        self,
        scanner: RepositoryScanner,
        subtree_mgr: SubtreeManager,
        git_ops: GitOperationsImpl,
        path_resolver: PathResolver,
    ) -> None:
        """Initialize converter with dependencies.

        Args:
            scanner: Repository scanner (Dependency Injection)
            subtree_mgr: Subtree manager (Dependency Injection)
            git_ops: Git operations (Dependency Injection)
            path_resolver: Path resolver (Dependency Injection)
        """
        self._scanner = scanner
        self._subtree_mgr = subtree_mgr
        self._git_ops = git_ops
        self._path_resolver = path_resolver

    def convert_nested_to_subtrees(self, src_root: Path) -> None:
        """Convert nested repositories to subtrees within module roots.

        Args:
            src_root: Root of src directory
        """
        print("\n=== Step 1: Nested repos -> subtree in MODULE ROOT ===")

        nested_repos = self._scanner.find_nested_repositories(src_root)

        for repo in nested_repos:
            url = self._git_ops.get_remote_url(repo.path)
            if not url:
                print(f"[WARN] Skipping (missing remote.origin.url): {repo.path}")
                continue

            branch = self._git_ops.get_default_branch(repo.path)

            # Normalize path - remove leading "src/" if present
            parts = Path(repo.relative_in_module).parts
            rel_in_module = self._path_resolver.normalize_path_in_module(
                Path(repo.relative_in_module), list(parts)
            )

            remote_name = self._path_resolver.sanitize_remote_name(
                f"st_{repo.module_name}_{str(rel_in_module).replace('/', '_')}"
            )

            try:
                self._subtree_mgr.add_subtree(
                    repo.module_root,
                    str(rel_in_module),
                    url,
                    branch,
                    remote_name,
                )
            except SubtreeConverterError:
                print(f"[FAIL] Could not add subtree {rel_in_module} to {repo.module_root}")
                continue

    def convert_modules_to_subtrees(self, prismq_root: Path, src_root: Path) -> None:
        """Convert module roots to subtrees in PrismQ root.

        Args:
            prismq_root: Root of PrismQ repository
            src_root: Root of src directory
        """
        print("\n=== Step 2: Module ROOTS -> subtree in PrismQ under <Module> ===")

        module_repos = self._scanner.find_module_roots(src_root)

        for repo in module_repos:
            url = self._git_ops.get_remote_url(repo.path)
            if not url:
                print(f"[WARN] Skipping (missing remote.origin.url): {repo.path}")
                continue

            branch = self._git_ops.get_default_branch(repo.path)

            # Prefix is just module name without "src/"
            rel_in_prismq = repo.module_name

            remote_name = self._path_resolver.sanitize_remote_name(
                f"st_root_{rel_in_prismq}"
            )

            try:
                self._subtree_mgr.add_subtree(
                    prismq_root,
                    rel_in_prismq,
                    url,
                    branch,
                    remote_name,
                )
            except SubtreeConverterError:
                print(f"[FAIL] Could not add subtree {rel_in_prismq} to PrismQ")
                continue


def main() -> None:
    """Main entry point for CLI."""
    try:
        # Initialize dependencies (Dependency Injection)
        runner = SubprocessCommandRunner()
        git_ops = GitOperationsImpl(runner)
        backup_mgr = BackupManager()
        path_resolver = PathResolver()
        scanner = RepositoryScanner()
        subtree_mgr = SubtreeManager(git_ops, backup_mgr, path_resolver)

        # Find PrismQ root
        prismq_root = path_resolver.find_prismq_root()
        if not (prismq_root / ".git").is_dir():
            raise RepositoryNotFoundError("PrismQ root is not a git repository.")

        src_root = prismq_root / "src"
        if not src_root.is_dir():
            raise RepositoryNotFoundError(f"Source directory not found: {src_root}")

        print(f"PrismQ root : {prismq_root}")
        print(f"SRC root    : {src_root}\n")

        # Create converter and run conversion
        converter = SubtreeConverter(scanner, subtree_mgr, git_ops, path_resolver)
        converter.convert_nested_to_subtrees(src_root)
        converter.convert_modules_to_subtrees(prismq_root, src_root)

        print("\nDone. Commit changes (squash commits from subtree).")
        print("To update later:")
        print("  git subtree pull --prefix=PATH REMOTE BRANCH --squash")
        print("To export changes to upstream:")
        print("  git subtree push --prefix=PATH REMOTE BRANCH")

    except SubtreeConverterError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
