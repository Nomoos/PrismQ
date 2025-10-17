#!/usr/bin/env python3
"""
Git Commit All - Recursive Commit Script

Commits all changes in all repositories with a single commit message.
Recursively processes all mod/ directories.
"""

import sys
from pathlib import Path
import subprocess
from typing import List, Tuple


def is_git_repository(path: Path) -> bool:
    """Check if a path is a git repository."""
    return (path / ".git").exists()


def has_changes(repo_path: Path) -> bool:
    """Check if a repository has uncommitted changes."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    return len(result.stdout.strip()) > 0


def commit_changes(repo_path: Path, commit_message: str) -> Tuple[bool, str]:
    """
    Commit all changes in a repository.
    
    Args:
        repo_path: Path to the repository
        commit_message: Commit message to use
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Add all changes
        result = subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False, f"Failed to add changes: {result.stderr.strip()}"
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, "Committed successfully"
        else:
            # Check if it's "nothing to commit"
            if "nothing to commit" in result.stdout.lower():
                return True, "Nothing to commit (clean)"
            return False, f"Commit failed: {result.stderr.strip()}"
            
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
    
    # Sort by depth (deepest first) to commit children before parents
    repos.sort(key=lambda p: len(p.parts), reverse=True)
    
    return repos


def main():
    """Main entry point."""
    print("=" * 70)
    print("💾 Git Commit All - Recursive Commit")
    print("=" * 70)
    print()
    
    # Get commit message
    if len(sys.argv) < 2:
        print("Usage: git-commit-all <commit_message>")
        print()
        print("Example:")
        print("  git-commit-all \"Update all repositories\"")
        return 1
    
    commit_message = " ".join(sys.argv[1:])
    print(f"📝 Commit message: {commit_message}")
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
    
    committed_count = 0
    clean_count = 0
    failed_count = 0
    
    for repo in repos:
        rel_path = repo.relative_to(workspace) if repo != workspace else Path(".")
        print(f"📁 {rel_path}")
        
        if not has_changes(repo):
            print(f"   ✅ Clean (no changes)")
            clean_count += 1
        else:
            success, message = commit_changes(repo, commit_message)
            if success:
                if "clean" in message.lower():
                    print(f"   ✅ {message}")
                    clean_count += 1
                else:
                    print(f"   ✅ {message}")
                    committed_count += 1
            else:
                print(f"   ❌ {message}")
                failed_count += 1
        
        print()
    
    print("=" * 70)
    print(f"Summary: Committed {committed_count}, Clean {clean_count}, Failed {failed_count}")
    
    if committed_count > 0:
        print("\n💡 Next steps:")
        print("   • Run 'git-push-all' to push changes to remote")
        print("   • Run 'check-submodules' to verify submodule state")
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
