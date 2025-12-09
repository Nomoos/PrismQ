#!/usr/bin/env python3
"""
Shared module discovery library for PrismQ.IdeaInspiration.

This library provides a single source of truth for discovering modules in the repository.
It's used by:
- Environment setup scripts (setup_all_envs, clean_all_envs, etc.)
- CI/CD pipelines
- Other automation tools

The discovery logic is centralized here to avoid duplication and ensure consistency.

Note: The Client module has been moved to a separate repository. References to it
in this file are preserved for backwards compatibility but are no longer active.
"""

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ModuleInfo:
    """Information about a discovered module."""

    name: str  # Relative path from repo root (e.g., "Classification", "Sources/Content/YouTube")
    path: Path  # Absolute path to module directory
    has_requirements: bool  # Has requirements.txt
    has_setup_py: bool  # Has setup.py
    has_pyproject_toml: bool  # Has pyproject.toml
    is_python_project: bool  # Is a Python project (has any of the above)
    depth: int  # Depth from repository root

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "path": str(self.path),
            "has_requirements": self.has_requirements,
            "has_setup_py": self.has_setup_py,
            "has_pyproject_toml": self.has_pyproject_toml,
            "is_python_project": self.is_python_project,
            "depth": self.depth,
        }


class ModuleDiscovery:
    """Discovers modules in the PrismQ.IdeaInspiration repository."""

    # Directories to exclude from discovery
    EXCLUDED_DIRS = {
        "_meta",
        ".git",
        ".idea",
        "venv",
        "node_modules",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        "egg-info",
        ".tox",
        ".nox",
    }

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize module discovery.

        Args:
            repo_root: Path to repository root. If None, auto-detects from script location.
        """
        if repo_root is None:
            # Auto-detect repo root (this script is in _meta/scripts/)
            repo_root = Path(__file__).parent.parent.parent

        self.repo_root = repo_root.resolve()

    def _is_excluded(self, path: Path) -> bool:
        """Check if a path should be excluded from discovery."""
        # Check if any part of the path is in excluded directories
        parts = path.relative_to(self.repo_root).parts
        return any(part in self.EXCLUDED_DIRS or part.startswith(".") for part in parts)

    def _find_requirements_files(self, max_depth: int = 3) -> List[Path]:
        """
        Find all requirements.txt files up to max_depth.

        Args:
            max_depth: Maximum depth to search from repo root

        Returns:
            List of paths to requirements.txt files
        """
        requirements_files = []

        for depth in range(1, max_depth + 1):
            pattern = "/".join(["*"] * depth) + "/requirements.txt"
            for req_file in self.repo_root.glob(pattern):
                if not self._is_excluded(req_file.parent):
                    requirements_files.append(req_file)

        return sorted(requirements_files)

    def discover_all(self, max_depth: int = 3) -> List[ModuleInfo]:
        """
        Discover all modules in the repository.

        Args:
            max_depth: Maximum depth to search from repo root

        Returns:
            List of ModuleInfo objects for all discovered modules
        """
        modules = []
        requirements_files = self._find_requirements_files(max_depth)

        for req_file in requirements_files:
            module_dir = req_file.parent
            rel_path = module_dir.relative_to(self.repo_root)
            depth = len(rel_path.parts)

            module_info = ModuleInfo(
                name=str(rel_path),
                path=module_dir,
                has_requirements=True,
                has_setup_py=(module_dir / "setup.py").exists(),
                has_pyproject_toml=(module_dir / "pyproject.toml").exists(),
                is_python_project=True,
                depth=depth,
            )
            modules.append(module_info)

        return modules

    def discover_for_env_setup(self, max_depth: int = 3) -> List[ModuleInfo]:
        """
        Discover modules for environment setup (only top-level, non-nested).

        This filters out nested modules where both parent and child have requirements.txt.
        For example, if both "Sources" and "Sources/Content" have requirements.txt,
        only "Sources" is returned.

        Args:
            max_depth: Maximum depth to search from repo root

        Returns:
            List of ModuleInfo objects for environment setup
        """
        all_modules = self.discover_all(max_depth)
        module_names = {m.name for m in all_modules}

        # Filter out nested modules
        filtered = []
        for module in all_modules:
            # Check if any other module is a parent of this one
            is_nested = False
            for other_name in module_names:
                if other_name != module.name and module.name.startswith(other_name + "/"):
                    is_nested = True
                    break

            if not is_nested:
                filtered.append(module)

        return sorted(filtered, key=lambda m: m.name)

    def discover_for_client(self, max_depth: int = 3) -> List[ModuleInfo]:
        """
        Discover modules that could be registered in external automation tools.

        This returns modules that have executable scripts (sources, processors, etc.)
        and excludes infrastructure modules like ConfigLoad, Model.

        Note: This method name is preserved for backwards compatibility. The Client
        module has been moved to a separate repository. This method now supports
        discovery for any external management or automation systems.

        Args:
            max_depth: Maximum depth to search from repo root

        Returns:
            List of ModuleInfo objects suitable for external tool registration
        """
        all_modules = self.discover_all(max_depth)

        # Exclude infrastructure modules
        infrastructure = {"EnvLoad", "Model"}

        client_modules = [m for m in all_modules if m.name not in infrastructure]

        return sorted(client_modules, key=lambda m: m.name)


def main():
    """Command-line interface for module discovery."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Discover modules in PrismQ.IdeaInspiration repository"
    )
    parser.add_argument(
        "--format",
        choices=["list", "json", "names"],
        default="list",
        help="Output format (default: list)",
    )
    parser.add_argument(
        "--filter",
        choices=["all", "env-setup", "client"],
        default="env-setup",
        help="Filter modules by purpose (default: env-setup)",
    )
    parser.add_argument(
        "--max-depth", type=int, default=3, help="Maximum search depth from repo root (default: 3)"
    )
    parser.add_argument(
        "--repo-root", type=Path, help="Repository root path (default: auto-detect)"
    )

    args = parser.parse_args()

    discovery = ModuleDiscovery(repo_root=args.repo_root)

    # Get modules based on filter
    if args.filter == "all":
        modules = discovery.discover_all(max_depth=args.max_depth)
    elif args.filter == "env-setup":
        modules = discovery.discover_for_env_setup(max_depth=args.max_depth)
    else:  # client
        modules = discovery.discover_for_client(max_depth=args.max_depth)

    # Output in requested format
    if args.format == "names":
        for module in modules:
            print(module.name)
    elif args.format == "json":
        output = [m.to_dict() for m in modules]
        print(json.dumps(output, indent=2))
    else:  # list
        print(f"Found {len(modules)} module(s):")
        for module in modules:
            markers = []
            if module.has_setup_py:
                markers.append("setup.py")
            if module.has_pyproject_toml:
                markers.append("pyproject.toml")
            marker_str = f" ({', '.join(markers)})" if markers else ""
            print(f"  - {module.name}{marker_str}")


if __name__ == "__main__":
    main()
