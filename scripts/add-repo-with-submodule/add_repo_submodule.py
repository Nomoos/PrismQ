#!/usr/bin/env python3
"""
Add Repository with Submodule - Main Script

Creates GitHub repositories and registers them as git submodules using
repo-builder functionality with additional submodule registration.
"""

import sys
from pathlib import Path
from typing import List

# Import from repo-builder
repo_builder_path = str(Path(__file__).parent.parent / "repo-builder")
if repo_builder_path not in sys.path:
    sys.path.insert(0, repo_builder_path)

# Import from local package
try:
    from .exceptions import SubmoduleError, ParentNotFoundError
    from .submodule_operations import (
        add_git_submodule,
        commit_submodule_changes,
        push_submodule_changes,
        is_git_repository
    )
except ImportError:
    # When running as script, import directly with unique names to avoid conflicts
    import importlib.util
    
    # Load our local exceptions module and register it in sys.modules
    # This ensures submodule_operations will use the same exception classes
    exceptions_path = Path(__file__).parent / "exceptions.py"
    spec = importlib.util.spec_from_file_location("submodule_exceptions", exceptions_path)
    exceptions_module = importlib.util.module_from_spec(spec)
    sys.modules["submodule_exceptions"] = exceptions_module  # Register for shared use
    spec.loader.exec_module(exceptions_module)
    SubmoduleError = exceptions_module.SubmoduleError
    ParentNotFoundError = exceptions_module.ParentNotFoundError
    
    # Load submodule_operations normally - it will now use our registered exceptions module
    from submodule_operations import (
        add_git_submodule,
        commit_submodule_changes,
        push_submodule_changes,
        is_git_repository
    )

# Import from repo-builder
from parsing import derive_module_chain
from repository import create_git_chain, get_repository_path
from validation import validate_github_cli


def get_parent_module(module_name: str) -> str:
    """
    Get parent module name from a dotted module name.
    
    Args:
        module_name: Module name (e.g., 'PrismQ.A.B')
        
    Returns:
        Parent module name (e.g., 'PrismQ.A')
        None if no parent (i.e., module_name is 'PrismQ')
    """
    parts = module_name.split('.')
    if len(parts) <= 1:
        return None
    return '.'.join(parts[:-1])


def get_relative_path(module_name: str) -> str:
    """
    Get relative path for submodule within parent.
    
    Args:
        module_name: Module name (e.g., 'PrismQ.A.B')
        
    Returns:
        Relative path (e.g., 'mod/B')
    """
    parts = module_name.split('.')
    if len(parts) <= 1:
        return None
    
    last_segment = parts[-1]
    return f"mod/{last_segment}"


def add_chain_as_submodules(chain: List[str], workspace: Path) -> None:
    """
    Add each repository in chain as submodule in its parent.
    
    Args:
        chain: List of module names from root to deepest
        workspace: Workspace root path
    """
    print("\n📦 Registering repositories as submodules...")
    print("=" * 50)
    
    # Skip PrismQ root (first in chain)
    # Process in reverse order (deepest to shallowest) to avoid "modified content" errors
    # This ensures child submodules are committed before parent tries to register them
    for module_name in reversed(chain[1:]):
        parent_name = get_parent_module(module_name)
        parent_path = get_repository_path(parent_name, workspace)
        
        # Check if parent is a git repository
        if not is_git_repository(parent_path):
            print(f"   ⚠️  Warning: Parent repository not found or not a git repo: {parent_path}")
            print(f"   Skipping {module_name}...")
            continue
        
        # Get relative path for submodule
        relative_path = get_relative_path(module_name)
        
        # Get repository URL
        repo_url = f"https://github.com/Nomoos/{module_name}.git"
        
        print(f"\n🔗 Adding {module_name} as submodule in {parent_name}...")
        print(f"   URL: {repo_url}")
        print(f"   Path: {relative_path}")
        
        try:
            # Add as submodule
            add_git_submodule(
                parent_path=parent_path,
                repo_url=repo_url,
                relative_path=relative_path,
                branch="main"
            )
            print(f"   ✅ Added as submodule")
        except SubmoduleError as e:
            print(f"   ⚠️  Warning during add: {e}")
            print(f"   Continuing with next submodule...")
            continue
        
        try:
            # Commit changes
            commit_submodule_changes(
                parent_path=parent_path,
                module_name=module_name
            )
            print(f"   ✅ Committed to parent")
        except SubmoduleError as e:
            print(f"   ⚠️  Warning during commit: {e}")
            print(f"   Continuing with next submodule...")
            continue
        
        try:
            # Push changes
            push_submodule_changes(
                parent_path=parent_path
            )
            print(f"   ✅ Pushed to remote")
        except SubmoduleError as e:
            print(f"   ⚠️  Warning during push: {e}")
            print(f"   Continuing with next submodule...")
            continue


def main(module_input: str) -> None:
    """
    Main workflow for creating repositories and adding as submodules.
    
    Args:
        module_input: Module name or GitHub URL
    """
    try:
        print("\n🚀 Add Repository with Submodule")
        print("=" * 50)
        
        # Step 1: Validate GitHub CLI
        validate_github_cli()
        
        # Step 2: Find workspace
        workspace = Path.cwd()
        while workspace.name != "PrismQ" and workspace != workspace.parent:
            workspace = workspace.parent
        print(f"📂 Working directory: {workspace}")
        
        # Step 3: Derive module chain
        print(f"\n🔍 Processing input: {module_input}")
        chain = derive_module_chain(module_input)
        
        # Step 4: Create/clone repositories (using repo-builder)
        print(f"\n📦 Creating/cloning repositories...")
        create_git_chain(chain, workspace)
        
        # Step 5: Add as submodules
        add_chain_as_submodules(chain, workspace)
        
        print("\n" + "=" * 50)
        print("✅ All operations complete!")
        print("\n💡 Next steps:")
        print("   • Review changes with: git status")
        print("   • Changes have been pushed to remote")
        print("   • Initialize submodules in other clones with:")
        print("     git submodule update --init --recursive")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
