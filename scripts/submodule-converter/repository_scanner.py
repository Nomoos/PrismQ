#!/usr/bin/env python3
"""Repository discovery and scanning (Single Responsibility Principle)."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NestedRepository:
    """Represents a nested git repository."""

    path: Path
    relative_to_mod: str
    module_root: Path
    module_name: str
    relative_in_module: str


@dataclass
class ModuleRepository:
    """Represents a module root repository."""

    path: Path
    module_name: str


class RepositoryScanner:
    """Scans directory tree for git repositories."""

    @staticmethod
    def find_nested_repositories(mod_root: Path) -> list[NestedRepository]:
        """Find all nested git repositories within mod directory.

        Args:
            mod_root: Root mod directory to scan

        Returns:
            List of nested repositories found
        """
        nested_repos: list[NestedRepository] = []
        module_roots: set[Path] = set()

        for root, dirs, _files in os.walk(mod_root):
            if ".git" not in dirs:
                continue

            abs_repo = Path(root).resolve()
            rel_to_mod = abs_repo.relative_to(mod_root)
            module_name = str(rel_to_mod).split(os.sep, 1)[0]
            module_root = mod_root / module_name

            # Skip if this is a module root
            if abs_repo.resolve() == module_root.resolve():
                module_roots.add(module_root)
                continue

            # This is a nested repo within a module
            rel_in_module = abs_repo.relative_to(module_root)

            nested_repos.append(
                NestedRepository(
                    path=abs_repo,
                    relative_to_mod=str(rel_to_mod),
                    module_root=module_root,
                    module_name=module_name,
                    relative_in_module=str(rel_in_module),
                )
            )

        return nested_repos

    @staticmethod
    def find_module_roots(mod_root: Path) -> list[ModuleRepository]:
        """Find all module root repositories.

        Args:
            mod_root: Root mod directory to scan

        Returns:
            List of module root repositories
        """
        module_repos: list[ModuleRepository] = []

        for root, dirs, _files in os.walk(mod_root):
            if ".git" not in dirs:
                continue

            abs_repo = Path(root).resolve()
            rel_to_mod = abs_repo.relative_to(mod_root)
            module_name = str(rel_to_mod).split(os.sep, 1)[0]
            module_root = mod_root / module_name

            # Only include module roots
            if abs_repo.resolve() == module_root.resolve():
                module_repos.append(
                    ModuleRepository(
                        path=module_root,
                        module_name=module_name,
                    )
                )

        return sorted(module_repos, key=lambda x: str(x.path))
