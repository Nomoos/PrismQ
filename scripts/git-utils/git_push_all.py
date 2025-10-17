#!/usr/bin/env python3
"""
Git Push All - Recursive Push Script

Pushes all repositories to their remotes recursively.
Processes all git repositories found in the workspace.
"""

import sys
from pathlib import Path
import subprocess
from typing import List, Tuple


def is_git_repository(path: Path) -> bool:
    """Check if a path is a git repository."""
    return (path / ".git").exists()


def has_remote(repo_path: Path) -> bool:
    """Check if a repository has a remote configured."""
    result = subprocess.run(
        ["git", "remote"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    return len(result.stdout.strip()) > 0


def get_current_branch(repo_path: Path) -> str:
    """Get the current branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def push_repository(repo_path: Path) -> Tuple[bool, str]:
    """
    Push a repository to its remote.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Check if there's a remote
        if not has_remote(repo_path):
            return True, "No remote configured (skipped)"
        
        # Get current branch
        branch = get_current_branch(repo_path)
        
        # Push to remote
        result = subprocess.run(
            ["git", "push", "origin", branch],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Check if already up to date
            if "up to date" in result.stderr.lower() or "up-to-date" in result.stderr.lower():
                return True, "Already up to date"
            return True, "Pushed successfully"
        else:
            return False, f"Push failed: {result.stderr.strip()}"
            
    except Exception as e:
        return False, f"Error: {e}"


def find_all_repositories(root_path: Path) -> List[Path]:
    """
    Find all git repositories recursively.
    
    Args:
        root_path: Root path to search from
        
    Returns:
        List of repository paths, sorted by depth (deepest first)
    """
    repos = []
    
    # Find all .git directories recursively
    for git_dir in root_path.rglob(".git"):
        if git_dir.is_dir():
            repo_path = git_dir.parent
            repos.append(repo_path)
    
    # Sort by depth (deepest first) to push children before parents
    repos.sort(key=lambda p: len(p.parts), reverse=True)
    
    return repos


def main():
    """Main entry point."""
    print("=" * 70)
    print("🚀 Git Push All - Recursive Push")
    print("=" * 70)
    print()
    
    # Find workspace root
    workspace = Path.cwd()
    while workspace.name != "PrismQ" and workspace != workspace.parent:
        workspace = workspace.parent
    
    if not is_git_repository(workspace):
        print(f"❌ Error: {workspace} is not a git repository")
        return 1
    
    print(f"📂 Workspace: {workspace}")
    print()
    
    # Find all repositories
    repos = find_all_repositories(workspace)
    
    if not repos:
        print("ℹ️  No git repositories found")
        return 0
    
    print(f"Found {len(repos)} repositor{'y' if len(repos) == 1 else 'ies'}")
    print()
    
    pushed_count = 0
    skipped_count = 0
    failed_count = 0
    
    for repo in repos:
        rel_path = repo.relative_to(workspace) if repo != workspace else Path(".")
        branch = get_current_branch(repo)
        print(f"📁 {rel_path} ({branch})")
        
        success, message = push_repository(repo)
        if success:
            if "skipped" in message.lower() or "up to date" in message.lower():
                print(f"   ✅ {message}")
                skipped_count += 1
            else:
                print(f"   ✅ {message}")
                pushed_count += 1
        else:
            print(f"   ❌ {message}")
            failed_count += 1
        
        print()
    
    print("=" * 70)
    print(f"Summary: Pushed {pushed_count}, Up to date {skipped_count}, Failed {failed_count}")
    
    if failed_count > 0:
        print("\n⚠️  Some repositories failed to push. Check the errors above.")
        return 1
    
    if pushed_count > 0:
        print("\n✅ All changes pushed successfully!")
    else:
        print("\n✅ All repositories are up to date!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
