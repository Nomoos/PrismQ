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
    depth: int  # Nesting depth (0 = top-level mod/, 1 = mod/Module/mod/, etc.)


@dataclass
class ModuleRepository:
    """Represents a module root repository."""

    path: Path
    module_name: str
    parent_module: Path | None  # Parent module path if nested, None if top-level
    depth: int  # Nesting depth (0 = top-level mod/, 1 = mod/Module/mod/, etc.)


class RepositoryScanner:
    """Scans directory tree for git repositories."""

    @staticmethod
    def _calculate_depth(path: Path, root: Path) -> int:
        """Calculate nesting depth by counting 'mod' directories in path.

        Args:
            path: Repository path
            root: Base root path to calculate relative depth from

        Returns:
            Depth level (0 = top-level mod/, 1 = mod/Module/mod/, etc.)
        """
        try:
            rel_path = path.relative_to(root)
        except ValueError:
            return 0

        parts = rel_path.parts
        # Count how many times "mod" appears in the path
        return sum(1 for part in parts if part == "mod")

    @staticmethod
    def _find_parent_module(repo_path: Path, prismq_root: Path) -> Path | None:
        """Find the parent module directory for a repository.

        Args:
            repo_path: Repository path
            prismq_root: PrismQ root path

        Returns:
            Parent module path or None if top-level
        """
        current = repo_path.parent
        while current != prismq_root and current.parent != prismq_root:
            # Check if parent contains a .git directory
            if (current / ".git").is_dir():
                return current
            # Check if we're at a mod/ directory's parent
            if current.name == "mod" and (current.parent / ".git").is_dir():
                return current.parent
            current = current.parent
        return None

    @staticmethod
    def _find_parent_module_for_repo(repo_path: Path, mod_root: Path) -> Path:
        """Find the immediate parent module directory for a repository.

        Args:
            repo_path: Repository path
            mod_root: Root mod directory

        Returns:
            Parent module path (the closest module containing this repo)
        """
        current = repo_path.parent
        prismq_root = mod_root.parent

        # Walk up the directory tree looking for a parent with .git
        while current != mod_root.parent:
            # If this directory has .git, it's a module
            if (current / ".git").is_dir() and current != repo_path:
                return current
            
            parent = current.parent
            if parent == prismq_root or parent == current:
                break
            current = parent
        
        # If we didn't find a parent module, check if we're directly under a top-level module
        rel_to_mod = repo_path.relative_to(mod_root)
        parts = rel_to_mod.parts
        if parts:
            # Return the first-level module
            return mod_root / parts[0]
        
        return mod_root

    @staticmethod
    def find_nested_repositories(mod_root: Path) -> list[NestedRepository]:
        """Find all nested git repositories within mod directory.

        Args:
            mod_root: Root mod directory to scan

        Returns:
            List of nested repositories found, sorted by depth (deepest first)
        """
        nested_repos: list[NestedRepository] = []
        module_roots: set[Path] = set()

        for root, dirs, _files in os.walk(mod_root):
            if ".git" not in dirs:
                continue

            abs_repo = Path(root).resolve()
            
            # Check if this is a module root at its level
            # A module root is right under a mod/ directory
            is_module_root = False
            if abs_repo.parent.name == "mod" or abs_repo.parent == mod_root:
                is_module_root = True
                module_roots.add(abs_repo)

            if is_module_root:
                continue

            # This is a nested repo within a module
            # Find the immediate parent module
            module_root = RepositoryScanner._find_parent_module_for_repo(abs_repo, mod_root)
            
            # Calculate relative paths
            rel_to_mod = abs_repo.relative_to(mod_root)
            rel_in_module = abs_repo.relative_to(module_root)
            
            # Module name is the name of the module root directory
            module_name = module_root.name

            # Calculate depth
            depth = RepositoryScanner._calculate_depth(abs_repo, mod_root)

            nested_repos.append(
                NestedRepository(
                    path=abs_repo,
                    relative_to_mod=str(rel_to_mod),
                    module_root=module_root,
                    module_name=module_name,
                    relative_in_module=str(rel_in_module),
                    depth=depth,
                )
            )

        # Sort by depth (deepest first) so we process inner modules before outer ones
        return sorted(nested_repos, key=lambda x: x.depth, reverse=True)

    @staticmethod
    def find_module_roots(mod_root: Path) -> list[ModuleRepository]:
        """Find all module root repositories, including nested ones.

        Args:
            mod_root: Root mod directory to scan

        Returns:
            List of module root repositories, sorted by depth (deepest first)
        """
        module_repos: list[ModuleRepository] = []
        prismq_root = mod_root.parent

        for root, dirs, _files in os.walk(mod_root):
            if ".git" not in dirs:
                continue

            abs_repo = Path(root).resolve()
            
            # Check if this is a module root (directly under a mod/ directory)
            is_module_root = False
            if abs_repo.parent.name == "mod" or abs_repo.parent == mod_root:
                is_module_root = True

            if not is_module_root:
                continue

            # Extract module name (last component of path)
            module_name = abs_repo.name
            
            # Calculate depth
            depth = RepositoryScanner._calculate_depth(abs_repo, mod_root)
            
            # Find parent module if this is nested
            parent_module = RepositoryScanner._find_parent_module(abs_repo, prismq_root)

            module_repos.append(
                ModuleRepository(
                    path=abs_repo,
                    module_name=module_name,
                    parent_module=parent_module,
                    depth=depth,
                )
            )

        # Sort by depth (deepest first) so we process inner modules before outer ones
        return sorted(module_repos, key=lambda x: x.depth, reverse=True)
