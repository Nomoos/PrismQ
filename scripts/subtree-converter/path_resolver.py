#!/usr/bin/env python3
"""Path resolution utilities (Single Responsibility Principle)."""

from pathlib import Path

try:
    from .exceptions import PathResolutionError
except ImportError:
    from exceptions import PathResolutionError


class PathResolver:
    """Resolves paths for PrismQ repositories."""

    @staticmethod
    def find_prismq_root(start_path: Path | None = None) -> Path:
        """Find PrismQ root directory from current location.

        Args:
            start_path: Starting path to search from (default: current directory)

        Returns:
            Path to PrismQ root directory

        Raises:
            PathResolutionError: If .git directory is not found
        """
        if start_path is None:
            start_path = Path.cwd()

        current = start_path.resolve()
        while True:
            if (current / ".git").is_dir():
                return current
            parent = current.parent
            if parent == current:
                msg = "Could not find .git above current location. Run from PrismQ or its subdirectory."
                raise PathResolutionError(msg)
            current = parent

    @staticmethod
    def sanitize_remote_name(name: str) -> str:
        """Sanitize a string to be used as git remote name.

        Args:
            name: Input name to sanitize

        Returns:
            Sanitized name safe for use as git remote
        """
        bad_chars = "\\/:*?\"<>| @."
        return "".join("_" if ch in bad_chars else ch for ch in name)

    @staticmethod
    def normalize_path_in_module(rel_path: Path, parts: list[str]) -> Path:
        """Normalize path within a module by removing leading 'src/' if present.

        Args:
            rel_path: Relative path within module
            parts: Path components

        Returns:
            Normalized path
        """
        if parts and parts[0].lower() == "src":
            if len(parts) > 1:
                return Path(*parts[1:])
            return Path("src")
        return rel_path
