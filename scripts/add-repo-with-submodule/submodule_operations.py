#!/usr/bin/env python3
"""Git submodule operations."""

import subprocess
from pathlib import Path
from typing import Optional
import importlib.util

try:
    from .exceptions import SubmoduleAddError, SubmoduleCommitError
except ImportError:
    # When running as script, load our local exceptions module
    exceptions_path = Path(__file__).parent / "exceptions.py"
    spec = importlib.util.spec_from_file_location("submodule_exceptions", exceptions_path)
    exceptions_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exceptions_module)
    SubmoduleAddError = exceptions_module.SubmoduleAddError
    SubmoduleCommitError = exceptions_module.SubmoduleCommitError


def add_git_submodule(
    parent_path: Path,
    repo_url: str,
    relative_path: str,
    branch: str = "main"
) -> bool:
    """
    Add repository as git submodule.
    
    Args:
        parent_path: Path to parent repository
        repo_url: URL of repository to add as submodule
        relative_path: Relative path within parent (e.g., 'mod/Module')
        branch: Branch to track (default: 'main')
        
    Returns:
        True if successful
        
    Raises:
        SubmoduleAddError: If git submodule add fails
    """
    try:
        # Run git submodule add
        result = subprocess.run(
            [
                "git", "-C", str(parent_path),
                "submodule", "add",
                "-b", branch,
                repo_url,
                relative_path
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        raise SubmoduleAddError(
            f"Failed to add submodule {repo_url} at {relative_path}: {e.stderr}"
        )
    except FileNotFoundError:
        raise SubmoduleAddError("Git not installed or not on PATH")


def commit_submodule_changes(
    parent_path: Path,
    module_name: str,
    message: Optional[str] = None
) -> bool:
    """
    Commit .gitmodules and submodule changes to parent repository.
    
    Args:
        parent_path: Path to parent repository
        module_name: Name of the module being added
        message: Custom commit message (optional)
        
    Returns:
        True if successful
        
    Raises:
        SubmoduleCommitError: If commit fails
    """
    if message is None:
        message = f"Add {module_name} as submodule"
    
    try:
        # Stage .gitmodules and submodule directory
        subprocess.run(
            ["git", "-C", str(parent_path), "add", ".gitmodules"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        
        # Commit changes
        result = subprocess.run(
            ["git", "-C", str(parent_path), "commit", "-m", message],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        # If nothing to commit, that's okay
        if "nothing to commit" in e.stdout or "nothing to commit" in e.stderr:
            return True
        raise SubmoduleCommitError(
            f"Failed to commit submodule changes: {e.stderr}"
        )
    except FileNotFoundError:
        raise SubmoduleCommitError("Git not installed or not on PATH")


def is_git_repository(path: Path) -> bool:
    """
    Check if path is a git repository.
    
    Args:
        path: Path to check
        
    Returns:
        True if path is a git repository
    """
    return (path / ".git").exists()
