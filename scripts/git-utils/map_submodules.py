#!/usr/bin/env python3
"""
Map Submodules - Auto-registration Script

Checks mod/ directories and adds any git repositories to .gitmodules if not already present.
Uses standard git submodule add workflow.
"""

import sys
from pathlib import Path
import subprocess
from typing import List, Tuple, Optional


def is_git_repository(path: Path) -> bool:
    """Check if a path is a git repository."""
    return (path / ".git").exists()


def get_git_remote_url(repo_path: Path) -> Optional[str]:
    """Get the remote URL of a git repository."""
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def is_submodule_mapped(parent_repo: Path, submodule_path: str) -> bool:
    """Check if a submodule is already mapped in .gitmodules."""
    result = subprocess.run(
        ["git", "config", "--file", ".gitmodules", "--get", f"submodule.{submodule_path}.path"],
        cwd=parent_repo,
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def add_submodule(parent_repo: Path, submodule_path: str, repo_url: str) -> bool:
    """
    Add a submodule using git submodule add.
    
    Args:
        parent_repo: Parent repository path
        submodule_path: Relative path to the submodule
        repo_url: URL of the submodule repository
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if already mapped
        if is_submodule_mapped(parent_repo, submodule_path):
            print(f"   ℹ️  Already mapped: {submodule_path}")
            return True
        
        # Use git submodule add
        result = subprocess.run(
            ["git", "submodule", "add", "--force", repo_url, submodule_path],
            cwd=parent_repo,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"   ✅ Added: {submodule_path}")
            return True
        else:
            print(f"   ⚠️  Failed to add {submodule_path}: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error adding {submodule_path}: {e}")
        return False


def find_unmapped_repos(root_path: Path) -> List[Tuple[Path, Path, str]]:
    """
    Find all git repositories in mod/ directories that are not mapped.
    
    Args:
        root_path: Root path to search from
        
    Returns:
        List of tuples (parent_repo, submodule_path, repo_url)
    """
    results = []
    
    def find_parent_repo(path: Path) -> Optional[Path]:
        """Find the nearest parent directory that is a git repository."""
        current = path.parent
        while current != current.parent:
            if is_git_repository(current):
                return current
            current = current.parent
        return None
    
    # Find all directories named "mod" recursively
    for mod_dir in root_path.rglob("mod"):
        if mod_dir.is_dir():
            parent_repo = find_parent_repo(mod_dir)
            if not parent_repo:
                continue
            
            # Check each subdirectory in mod/
            for subdir in mod_dir.iterdir():
                if subdir.is_dir() and subdir.name != ".git":
                    # Only process if it's a git repository
                    if is_git_repository(subdir):
                        # Calculate relative path from parent repo
                        try:
                            rel_path = subdir.relative_to(parent_repo)
                            rel_path_str = str(rel_path).replace('\\', '/')
                            
                            # Check if already mapped
                            if not is_submodule_mapped(parent_repo, rel_path_str):
                                # Get remote URL
                                repo_url = get_git_remote_url(subdir)
                                if repo_url:
                                    results.append((parent_repo, rel_path_str, repo_url))
                        except ValueError:
                            pass
    
    return results


def main():
    """Main entry point."""
    print("=" * 70)
    print("🔗 Map Submodules - Auto-registration")
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
    
    # Find all unmapped repositories
    unmapped = find_unmapped_repos(workspace)
    
    if not unmapped:
        print("✅ All repositories in mod/ directories are already mapped")
        return 0
    
    print(f"Found {len(unmapped)} unmapped repositor{'y' if len(unmapped) == 1 else 'ies'}")
    print()
    
    # Sort by depth (deepest first) to avoid "modified content" errors
    unmapped_sorted = sorted(unmapped, key=lambda x: x[1].count('/'), reverse=True)
    
    added_count = 0
    failed_count = 0
    
    for parent_repo, submodule_path, repo_url in unmapped_sorted:
        print(f"📁 {submodule_path}")
        print(f"   Parent: {parent_repo.relative_to(workspace)}")
        print(f"   URL: {repo_url}")
        
        if add_submodule(parent_repo, submodule_path, repo_url):
            added_count += 1
        else:
            failed_count += 1
        
        print()
    
    print("=" * 70)
    print(f"Summary: Added {added_count}, Failed {failed_count}")
    
    if added_count > 0:
        print("\n💡 Next steps:")
        print("   • Run 'git-commit-all' to commit the changes")
        print("   • Run 'git-push-all' to push to remote")
        print("   • Run 'check-submodules' to verify the mapping")
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
