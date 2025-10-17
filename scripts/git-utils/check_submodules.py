#!/usr/bin/env python3
"""
Check Submodules - Validation Script

Validates if each folder in any mod/ folder is mapped in the nearest parent's .gitmodules.
Inspired by git_pull_all.bat structure for recursive traversal.
"""

import sys
from pathlib import Path
import subprocess
from typing import List, Tuple, Optional


def is_git_repository(path: Path) -> bool:
    """Check if a path is a git repository."""
    return (path / ".git").exists()


def get_gitmodules_entries(repo_path: Path) -> dict:
    """
    Get all submodule entries from .gitmodules in a repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary mapping submodule paths to their URLs
    """
    gitmodules_path = repo_path / ".gitmodules"
    entries = {}
    
    if not gitmodules_path.exists():
        return entries
    
    result = subprocess.run(
        ["git", "config", "--file", str(gitmodules_path), "--get-regexp", "path"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if line:
                # Format: submodule.path.path <path>
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    submodule_path = parts[1]
                    entries[submodule_path] = True
    
    return entries


def find_mod_directories(root_path: Path) -> List[Tuple[Path, Path]]:
    """
    Recursively find all mod/ directories and their parent repositories.
    
    Args:
        root_path: Root path to search from
        
    Returns:
        List of tuples (parent_repo_path, mod_directory_path)
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
            if parent_repo:
                results.append((parent_repo, mod_dir))
    
    return results


def check_submodule_mapping(parent_repo: Path, mod_dir: Path) -> List[Tuple[Path, bool, str]]:
    """
    Check if all subdirectories in mod_dir are mapped in parent's .gitmodules.
    
    Args:
        parent_repo: Parent repository path
        mod_dir: The mod/ directory to check
        
    Returns:
        List of tuples (subdir_path, is_mapped, message)
    """
    results = []
    gitmodules_entries = get_gitmodules_entries(parent_repo)
    
    # Check each subdirectory in mod/
    for subdir in mod_dir.iterdir():
        if subdir.is_dir() and subdir.name != ".git":
            # Calculate relative path from parent repo
            try:
                rel_path = subdir.relative_to(parent_repo)
                rel_path_str = str(rel_path).replace('\\', '/')
                
                is_mapped = rel_path_str in gitmodules_entries
                
                if is_mapped:
                    results.append((subdir, True, "✅ Mapped"))
                else:
                    # Check if it's a git repository
                    if is_git_repository(subdir):
                        results.append((subdir, False, "⚠️  NOT mapped (is git repo)"))
                    else:
                        results.append((subdir, False, "ℹ️  NOT mapped (not git repo)"))
            except ValueError:
                results.append((subdir, False, "❌ Error: Path calculation failed"))
    
    return results


def main():
    """Main entry point."""
    print("=" * 70)
    print("🔍 Check Submodules - Validation Report")
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
    
    # Find all mod/ directories
    mod_dirs = find_mod_directories(workspace)
    
    if not mod_dirs:
        print("ℹ️  No mod/ directories found")
        return 0
    
    print(f"Found {len(mod_dirs)} mod/ director{'y' if len(mod_dirs) == 1 else 'ies'}")
    print()
    
    all_mapped = True
    total_checked = 0
    total_unmapped = 0
    
    for parent_repo, mod_dir in mod_dirs:
        print(f"📁 {mod_dir.relative_to(workspace)}")
        print(f"   Parent: {parent_repo.relative_to(workspace)}")
        
        results = check_submodule_mapping(parent_repo, mod_dir)
        
        if results:
            for subdir, is_mapped, message in results:
                total_checked += 1
                print(f"   {message} {subdir.name}")
                if not is_mapped:
                    all_mapped = False
                    total_unmapped += 1
        else:
            print(f"   ℹ️  Empty directory")
        
        print()
    
    print("=" * 70)
    print(f"Summary: Checked {total_checked} subdirectories")
    
    if all_mapped:
        print("✅ All mod/ subdirectories are properly mapped in .gitmodules")
        return 0
    else:
        print(f"⚠️  {total_unmapped} subdirectories are NOT mapped in .gitmodules")
        print("\n💡 Next steps:")
        print("   • Run 'map-submodules' to automatically map unmapped directories")
        return 1


if __name__ == "__main__":
    sys.exit(main())
