#!/usr/bin/env python3
"""Git submodule operations."""

import importlib.util
import shutil
import subprocess
from pathlib import Path
from typing import Optional

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
    """Add repository as git submodule.

    Checks if submodule already exists:
    - If exists with correct URL: skips adding (returns True)
    - If exists with wrong URL: removes old one and adds new one
    - If doesn't exist: adds normally

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
    # Check if submodule already exists
    existing_url = get_submodule_url(parent_path, relative_path)
    exists_in_index = submodule_exists_in_index(parent_path, relative_path)

    if existing_url or exists_in_index:
        # Submodule exists - check if URL is correct
        if existing_url == repo_url:
            # Correct URL, nothing to do
            print("   ℹ️  Submodule already exists with correct URL")
            return True
        # Wrong URL or partial state - remove and re-add
        print("   ⚠️  Submodule exists with different URL or incomplete state")
        print(f"      Existing: {existing_url or 'not in .gitmodules'}")
        print(f"      Expected: {repo_url}")
        print("   🔄 Removing old submodule...")

        try:
            remove_git_submodule(parent_path, relative_path)
            print("   ✅ Old submodule removed")
        except SubmoduleAddError as e:
            print(f"   ⚠️  Warning during removal: {e}")

    # Add the submodule
    try:
        # Run git submodule add
        subprocess.run(
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
        ) from e
    except FileNotFoundError as e:
        raise SubmoduleAddError("Git not installed or not on PATH") from e


def commit_submodule_changes(
    parent_path: Path,
    module_name: str,
    message: Optional[str] = None
) -> bool:
    """Commit .gitmodules and submodule changes to parent repository.

    Note: git submodule add already stages both .gitmodules and the submodule entry
    (as a gitlink), so we just commit those staged changes. We don't use 'git add'
    on the submodule path as this would treat it as an embedded repository instead
    of a proper submodule, causing Git warnings.

    Args:
        parent_path: Path to parent repository
        module_name: Name of the module being added (e.g., 'PrismQ.IdeaInspiration')
        message: Custom commit message (optional)

    Returns:
        True if successful

    Raises:
        SubmoduleCommitError: If commit fails
    """
    if message is None:
        message = f"Add {module_name} as submodule"

    try:
        # Commit all staged changes (git submodule add already stages both .gitmodules and the submodule entry)
        # Note: We don't use 'git add' on the submodule path as this would treat it as an embedded repository
        # instead of a proper submodule, causing Git warnings.
        subprocess.run(
            ["git", "-C", str(parent_path), "commit", "-m", message],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        # If nothing to commit, that's okay (covers both "nothing to commit" and "nothing added to commit")
        if ("nothing to commit" in e.stdout or "nothing to commit" in e.stderr or
            "nothing added to commit" in e.stdout or "nothing added to commit" in e.stderr):
            return True
        raise SubmoduleCommitError(
            f"Failed to commit submodule changes: {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise SubmoduleCommitError("Git not installed or not on PATH") from e


def push_submodule_changes(
    parent_path: Path,
    remote: str = "origin",
    branch: str = "main"
) -> bool:
    """Push committed changes to remote repository.

    Args:
        parent_path: Path to parent repository
        remote: Remote name (default: 'origin')
        branch: Branch name (default: 'main')

    Returns:
        True if successful

    Raises:
        SubmoduleCommitError: If push fails
    """
    try:
        # Push changes to remote
        subprocess.run(
            ["git", "-C", str(parent_path), "push", remote, branch],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        raise SubmoduleCommitError(
            f"Failed to push changes to {remote}/{branch}: {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise SubmoduleCommitError("Git not installed or not on PATH") from e


def is_git_repository(path: Path) -> bool:
    """Check if path is a git repository.

    Args:
        path: Path to check

    Returns:
        True if path is a git repository
    """
    return (path / ".git").exists()


def get_submodule_url(parent_path: Path, relative_path: str) -> Optional[str]:
    """Get the URL of an existing submodule.

    Args:
        parent_path: Path to parent repository
        relative_path: Relative path of the submodule

    Returns:
        Submodule URL if it exists, None otherwise
    """
    try:
        result = subprocess.run(
            [
                "git", "-C", str(parent_path),
                "config", "--file", ".gitmodules",
                "--get", f"submodule.{relative_path}.url"
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None


def submodule_exists_in_index(parent_path: Path, relative_path: str) -> bool:
    """Check if submodule exists in git index.

    Args:
        parent_path: Path to parent repository
        relative_path: Relative path of the submodule

    Returns:
        True if submodule exists in index
    """
    try:
        result = subprocess.run(
            [
                "git", "-C", str(parent_path),
                "ls-files", "--stage", relative_path
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        # Check if output contains a git link (mode 160000)
        return "160000" in result.stdout
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def remove_git_submodule(parent_path: Path, relative_path: str) -> bool:
    """Remove an existing git submodule.

    Args:
        parent_path: Path to parent repository
        relative_path: Relative path of the submodule to remove

    Returns:
        True if successful

    Raises:
        SubmoduleAddError: If removal fails
    """
    try:
        # Step 1: Deinitialize the submodule
        subprocess.run(
            [
                "git", "-C", str(parent_path),
                "submodule", "deinit", "-f", relative_path
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False  # May fail if not initialized, that's ok
        )

        # Step 2: Remove from git index and working tree
        subprocess.run(
            [
                "git", "-C", str(parent_path),
                "rm", "-f", relative_path
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )

        # Step 3: Remove submodule config from .gitmodules
        subprocess.run(
            [
                "git", "-C", str(parent_path),
                "config", "--file", ".gitmodules",
                "--remove-section", f"submodule.{relative_path}"
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False  # May fail if already removed, that's ok
        )

        # Step 4: Remove submodule-specific git config
        subprocess.run(
            [
                "git", "-C", str(parent_path),
                "config", "--remove-section", f"submodule.{relative_path}"
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False  # May fail if doesn't exist, that's ok
        )

        # Step 5: Remove .git/modules/<path> directory
        modules_path = parent_path / ".git" / "modules" / relative_path
        if modules_path.exists():
            shutil.rmtree(modules_path)

        return True
    except subprocess.CalledProcessError as e:
        raise SubmoduleAddError(
            f"Failed to remove submodule {relative_path}: {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise SubmoduleAddError("Git not installed or not on PATH") from e
    except Exception as e:
        raise SubmoduleAddError(
            f"Failed to remove submodule {relative_path}: {str(e)}"
        ) from e
