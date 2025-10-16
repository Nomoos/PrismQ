#!/usr/bin/env python3
"""CLI interface and main workflow for submodule converter."""

import sys
from pathlib import Path

try:
    from .backup_manager import BackupManager
    from .command_runner import SubprocessCommandRunner
    from .exceptions import RepositoryNotFoundError, SubtreeConverterError
    from .git_operations import GitOperationsImpl
    from .path_resolver import PathResolver
    from .repository_scanner import RepositoryScanner
    from .submodule_manager import SubmoduleManager
except ImportError:
    from backup_manager import BackupManager
    from command_runner import SubprocessCommandRunner
    from exceptions import RepositoryNotFoundError, SubtreeConverterError
    from git_operations import GitOperationsImpl
    from path_resolver import PathResolver
    from repository_scanner import RepositoryScanner
    from submodule_manager import SubmoduleManager


class SubmoduleConverter:
    """Main orchestrator for submodule conversion (Single Responsibility Principle)."""

    def __init__(
        self,
        scanner: RepositoryScanner,
        submodule_mgr: SubmoduleManager,
        git_ops: GitOperationsImpl,
        path_resolver: PathResolver,
    ) -> None:
        """Initialize converter with dependencies.

        Args:
            scanner: Repository scanner (Dependency Injection)
            submodule_mgr: Submodule manager (Dependency Injection)
            git_ops: Git operations (Dependency Injection)
            path_resolver: Path resolver (Dependency Injection)
        """
        self._scanner = scanner
        self._submodule_mgr = submodule_mgr
        self._git_ops = git_ops
        self._path_resolver = path_resolver

    def convert_nested_to_submodules(self, mod_root: Path) -> None:
        """Convert nested repositories to submodules within module roots.

        Args:
            mod_root: Root of mod directory
        """
        print("\n=== Step 1: Nested repos -> submodule in MODULE ROOT ===")

        nested_repos = self._scanner.find_nested_repositories(mod_root)

        for repo in nested_repos:
            url = self._git_ops.get_remote_url(repo.path)
            if not url:
                print(f"[WARN] Skipping (missing remote.origin.url): {repo.path}")
                continue

            branch = self._git_ops.get_default_branch(repo.path)

            # Normalize path - remove leading "mod/" if present
            parts = Path(repo.relative_in_module).parts
            rel_in_module = self._path_resolver.normalize_path_in_module(
                Path(repo.relative_in_module), list(parts)
            )

            try:
                self._submodule_mgr.add_submodule(
                    repo.module_root,
                    str(rel_in_module),
                    url,
                    branch,
                )
            except SubtreeConverterError:
                print(f"[FAIL] Could not add submodule {rel_in_module} to {repo.module_root}")
                continue

    def convert_modules_to_submodules(self, prismq_root: Path, mod_root: Path) -> None:
        """Convert module roots to submodules in their parent context.

        This handles both top-level modules (under PrismQ/mod/) and nested modules
        (under Module/mod/). Processes deepest modules first.

        Args:
            prismq_root: Root of PrismQ repository
            mod_root: Root of mod directory
        """
        print("\n=== Step 2: Module ROOTS -> submodule in parent context ===")

        module_repos = self._scanner.find_module_roots(mod_root)

        for repo in module_repos:
            url = self._git_ops.get_remote_url(repo.path)
            if not url:
                print(f"[WARN] Skipping (missing remote.origin.url): {repo.path}")
                continue

            branch = self._git_ops.get_default_branch(repo.path)

            # Determine the parent repository and relative path
            if repo.parent_module is None:
                # Top-level module: add to PrismQ root
                parent_repo = prismq_root
                rel_in_parent = f"mod/{repo.module_name}"
            else:
                # Nested module: add to parent module
                parent_repo = repo.parent_module
                rel_in_parent = f"mod/{repo.module_name}"

            try:
                self._submodule_mgr.add_submodule(
                    parent_repo,
                    rel_in_parent,
                    url,
                    branch,
                )
            except SubtreeConverterError:
                print(f"[FAIL] Could not add submodule {rel_in_parent} to {parent_repo}")
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
        submodule_mgr = SubmoduleManager(git_ops, backup_mgr, path_resolver)

        # Find PrismQ root
        prismq_root = path_resolver.find_prismq_root()
        if not (prismq_root / ".git").is_dir():
            raise RepositoryNotFoundError("PrismQ root is not a git repository.")

        mod_root = prismq_root / "mod"
        if not mod_root.is_dir():
            raise RepositoryNotFoundError(f"Module directory not found: {mod_root}")

        print(f"PrismQ root : {prismq_root}")
        print(f"MOD root    : {mod_root}\n")

        # Create converter and run conversion
        converter = SubmoduleConverter(scanner, submodule_mgr, git_ops, path_resolver)
        converter.convert_nested_to_submodules(mod_root)
        converter.convert_modules_to_submodules(prismq_root, mod_root)

        print("\nDone. Commit changes and initialize submodules.")
        print("To initialize submodules after cloning:")
        print("  git submodule update --init --recursive")
        print("To update all submodules:")
        print("  git submodule update --remote --recursive")

    except SubtreeConverterError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
