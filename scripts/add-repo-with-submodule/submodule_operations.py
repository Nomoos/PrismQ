#!/usr/bin/env python3
"""Git submodule operations."""

import importlib.util
import shutil
import subprocess
from pathlib import Path

try:
    from .exceptions import SubmoduleAddError, SubmoduleCommitError
except ImportError:
    # When running as script, load our local exceptions module
    import sys

    # Check if already loaded by another module to ensure we use the same exception classes
    if "submodule_exceptions" in sys.modules:
        exceptions_module = sys.modules["submodule_exceptions"]
    else:
        exceptions_path = Path(__file__).parent / "exceptions.py"
        spec = importlib.util.spec_from_file_location("submodule_exceptions", exceptions_path)
        exceptions_module = importlib.util.module_from_spec(spec)
        sys.modules["submodule_exceptions"] = exceptions_module
        spec.loader.exec_module(exceptions_module)

    SubmoduleAddError = exceptions_module.SubmoduleAddError
    SubmoduleCommitError = exceptions_module.SubmoduleCommitError


def log_git_status(parent_path: Path, context: str) -> None:
    """Log current git repository status for debugging.

    Args:
        parent_path: Path to parent repository
        context: Context message for the log
    """
    print(f"   🔍 Git Status ({context}):")
    try:
        result = subprocess.run(
            ["git", "-C", str(parent_path), "status", "--short"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        status_output = result.stdout.strip()
        if status_output:
            for line in status_output.split('\n'):
                print(f"      {line}")
        else:
            print("      (clean working tree)")
    except Exception as e:
        print(f"      Failed to get status: {e}")


def log_submodule_index_state(parent_path: Path, relative_path: str) -> None:
    """Log git index state for a submodule path.

    Args:
        parent_path: Path to parent repository
        relative_path: Relative path of the submodule
    """
    print(f"   🔍 Index state for '{relative_path}':")
    try:
        result = subprocess.run(
            ["git", "-C", str(parent_path), "ls-files", "--stage", relative_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        index_output = result.stdout.strip()
        if index_output:
            print(f"      {index_output}")
        else:
            print("      (not in index)")
    except Exception as e:
        print(f"      Failed to check index: {e}")


def log_gitmodules_config(parent_path: Path, relative_path: str) -> None:
    """Log .gitmodules configuration for a submodule.

    Args:
        parent_path: Path to parent repository
        relative_path: Relative path of the submodule
    """
    print(f"   🔍 .gitmodules config for '{relative_path}':")
    try:
        result = subprocess.run(
            ["git", "-C", str(parent_path), "config", "--file", ".gitmodules", "--get-regexp", f"submodule.{relative_path}.*"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        config_output = result.stdout.strip()
        if config_output:
            for line in config_output.split('\n'):
                print(f"      {line}")
        else:
            print("      (no configuration found)")
    except subprocess.CalledProcessError:
        print("      (no configuration found)")
    except Exception as e:
        print(f"      Failed to check config: {e}")


def log_submodule_git_config(parent_path: Path, relative_path: str) -> None:
    """Log git config for a submodule.

    Args:
        parent_path: Path to parent repository
        relative_path: Relative path of the submodule
    """
    print(f"   🔍 Git config for 'submodule.{relative_path}':")
    try:
        result = subprocess.run(
            ["git", "-C", str(parent_path), "config", "--get-regexp", f"submodule.{relative_path}.*"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        config_output = result.stdout.strip()
        if config_output:
            for line in config_output.split('\n'):
                print(f"      {line}")
        else:
            print("      (no configuration found)")
    except subprocess.CalledProcessError:
        print("      (no configuration found)")
    except Exception as e:
        print(f"      Failed to check config: {e}")


def log_submodule_directory_state(parent_path: Path, relative_path: str) -> None:
    """Log filesystem state of submodule directory.

    Args:
        parent_path: Path to parent repository
        relative_path: Relative path of the submodule
    """
    submodule_path = parent_path / relative_path
    modules_path = parent_path / ".git" / "modules" / relative_path

    print("   🔍 Filesystem state:")
    print(f"      Submodule directory exists: {submodule_path.exists()}")
    if submodule_path.exists():
        print(f"      Is directory: {submodule_path.is_dir()}")
        if submodule_path.is_dir():
            try:
                # Count items efficiently without creating a full list
                item_count = sum(1 for _ in submodule_path.iterdir())
                print(f"      Contents: {item_count} items")
            except Exception as e:
                print(f"      Failed to list contents: {e}")
    print(f"      .git/modules entry exists: {modules_path.exists()}")


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

        # Log detailed state before removal
        log_submodule_index_state(parent_path, relative_path)
        log_gitmodules_config(parent_path, relative_path)
        log_submodule_directory_state(parent_path, relative_path)

        print("   🔄 Removing old submodule...")

        try:
            remove_git_submodule(parent_path, relative_path)
            print("   ✅ Old submodule removed")
        except SubmoduleAddError as e:
            print(f"   ⚠️  Warning during removal: {e}")
            # Log state after failed removal
            log_submodule_index_state(parent_path, relative_path)
            log_gitmodules_config(parent_path, relative_path)
            log_submodule_directory_state(parent_path, relative_path)

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
        # Log detailed state on error
        print("   ❌ Failed to add submodule")
        print(f"   Error output: {e.stderr}")
        log_git_status(parent_path, "after failed add")
        log_submodule_index_state(parent_path, relative_path)
        log_gitmodules_config(parent_path, relative_path)
        log_submodule_directory_state(parent_path, relative_path)

        raise SubmoduleAddError(
            f"Failed to add submodule {repo_url} at {relative_path}: {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise SubmoduleAddError("Git not installed or not on PATH") from e


def commit_submodule_changes(
    parent_path: Path,
    module_name: str,
    message: str | None = None
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

    # Log git status before committing
    log_git_status(parent_path, "before commit")

    try:
        # First, check if there are any modified or new commits in the submodule
        # In such cases, we need to stage the submodule explicitly
        status_result = subprocess.run(
            ["git", "-C", str(parent_path), "status", "--short"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        
        # Look for lines like " M mod/Submodule" (modified in working tree)
        # or "M  mod/Submodule" (modified in index) or "MM mod/Submodule" (both)
        # Git status --short format: XY filename where X=index, Y=working tree
        # For submodules: " M" (modified content), "M " (new commits staged), "MM" (both)
        status_lines = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
        needs_staging = False
        for line in status_lines:
            # Check if line indicates modified or unstaged changes
            # Check first two characters for status codes
            if len(line) >= 2:
                status_code = line[:2]
                # ' M' = modified in working tree (not staged)
                # 'M ' = modified in index but also modified in working tree
                # 'MM' = modified in both
                if status_code in {' M', 'M ', 'MM'}:
                    needs_staging = True
                    break
        
        if needs_staging:
            print(f"   📍 Staging submodule changes...")
            # Stage all changes including .gitmodules and the submodule gitlink
            subprocess.run(
                ["git", "-C", str(parent_path), "add", "-A"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                check=True
            )
            print("   ✅ Changes staged")
        
        # Commit all staged changes (git submodule add already stages both .gitmodules and the submodule entry)
        # Note: For new submodules, git submodule add stages them automatically
        # For existing submodules with changes, we stage them above
        result = subprocess.run(
            ["git", "-C", str(parent_path), "commit", "-m", message],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        print(f"   🔍 Commit output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        # If nothing to commit, that's okay
        # This covers both "nothing to commit" (clean tree) and "nothing added to commit" (untracked files present)
        git_output = (e.stdout or '') + (e.stderr or '')
        if "nothing to commit" in git_output or "nothing added to commit" in git_output:
            print("   ℹ️  Nothing to commit (already committed or clean tree)")
            return True

        # Log detailed state on error
        print("   ❌ Failed to commit")
        print(f"   Error output: {e.stderr}")
        print(f"   Stdout: {e.stdout}")
        log_git_status(parent_path, "after failed commit")

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


def get_submodule_url(parent_path: Path, relative_path: str) -> str | None:
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
    print("   🔍 Starting submodule removal process...")
    log_submodule_index_state(parent_path, relative_path)
    log_gitmodules_config(parent_path, relative_path)
    log_submodule_git_config(parent_path, relative_path)
    log_submodule_directory_state(parent_path, relative_path)

    try:
        # Step 1: Deinitialize the submodule
        print("   📍 Step 1: Deinitializing submodule...")
        result = subprocess.run(
            [
                "git", "-C", str(parent_path),
                "submodule", "deinit", "-f", relative_path
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False  # May fail if not initialized, that's ok
        )
        if result.returncode == 0:
            print("   ✅ Deinitialize succeeded")
        else:
            print(f"   ⚠️  Deinitialize failed (may not have been initialized): {result.stderr.strip()}")

        # Step 2: Remove from git index and working tree
        print("   📍 Step 2: Removing from git index and working tree...")
        # Use --cached to remove from index without requiring .gitmodules configuration
        # This is necessary when a gitlink exists in the index but is not properly registered
        result = subprocess.run(
            [
                "git", "-C", str(parent_path),
                "rm", "--cached", "-r", relative_path
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        print(f"   ✅ Removed from git index: {result.stdout.strip()}")
        
        # Also remove from working directory if it exists
        submodule_path = parent_path / relative_path
        if submodule_path.exists():
            print(f"   📍 Removing from working directory: {relative_path}")
            shutil.rmtree(submodule_path)
            print("   ✅ Removed from working directory")

        # Step 3: Remove submodule config from .gitmodules
        print("   📍 Step 3: Removing from .gitmodules...")
        result = subprocess.run(
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
        if result.returncode == 0:
            print("   ✅ Removed from .gitmodules")
        else:
            print(f"   ⚠️  .gitmodules removal skipped (may not exist): {result.stderr.strip()}")

        # Step 4: Remove submodule-specific git config
        print("   📍 Step 4: Removing from git config...")
        result = subprocess.run(
            [
                "git", "-C", str(parent_path),
                "config", "--remove-section", f"submodule.{relative_path}"
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False  # May fail if doesn't exist, that's ok
        )
        if result.returncode == 0:
            print("   ✅ Removed from git config")
        else:
            print(f"   ⚠️  Git config removal skipped (may not exist): {result.stderr.strip()}")

        # Step 5: Remove .git/modules/<path> directory
        print("   📍 Step 5: Removing .git/modules directory...")
        modules_path = parent_path / ".git" / "modules" / relative_path
        if modules_path.exists():
            shutil.rmtree(modules_path)
            print(f"   ✅ Removed .git/modules/{relative_path}")
        else:
            print(f"   ⚠️  .git/modules/{relative_path} does not exist, skipping")

        # Log final state
        print("   🔍 Final state after removal:")
        log_submodule_index_state(parent_path, relative_path)
        log_gitmodules_config(parent_path, relative_path)
        log_submodule_directory_state(parent_path, relative_path)

        return True
    except subprocess.CalledProcessError as e:
        print("   ❌ Removal failed at step")
        print(f"   Error output: {e.stderr}")
        log_git_status(parent_path, "after failed removal")
        log_submodule_index_state(parent_path, relative_path)
        log_gitmodules_config(parent_path, relative_path)
        log_submodule_directory_state(parent_path, relative_path)

        raise SubmoduleAddError(
            f"Failed to remove submodule {relative_path}: {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise SubmoduleAddError("Git not installed or not on PATH") from e
    except Exception as e:
        print(f"   ❌ Unexpected error during removal: {str(e)}")
        log_git_status(parent_path, "after unexpected error")
        log_submodule_index_state(parent_path, relative_path)
        log_submodule_directory_state(parent_path, relative_path)

        raise SubmoduleAddError(
            f"Failed to remove submodule {relative_path}: {str(e)}"
        ) from e
