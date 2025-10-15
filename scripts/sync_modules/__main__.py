#!/usr/bin/env python3
"""
PrismQ Module Sync Script - CLI Entry Point

This script syncs modules from their remote repositories using git subtree.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from git import Repo

from .module_syncer import ModuleSyncer


@click.command()
@click.option('--list-only', '-l', 'list_only', is_flag=True, 
             help='List configured modules without syncing')
@click.option('--sync-all', 'sync_all_flag', is_flag=True,
             help='Sync all modules (default behavior)')
@click.option('--recursive', '-r', is_flag=True,
             help='Recursively discover all modules (not just first-level)')
@click.argument('module_path', required=False)
def main(list_only: bool, sync_all_flag: bool, recursive: bool, module_path: Optional[str]):
    """
    PrismQ Module Synchronization Script
    
    Syncs first-level modules from their remote repositories using git subtree.
    
    Examples:
    
        # Sync all first-level modules
        python sync_modules.py
        
        # Recursively sync all modules (including nested)
        python sync_modules.py --recursive
        
        # List configured modules
        python sync_modules.py --list
        
        # Sync only RepositoryTemplate module
        python sync_modules.py src/RepositoryTemplate
    """
    
    click.echo()
    click.echo("        PrismQ Module Synchronization Script")
    click.echo()
    click.echo()
    
    # Check if we're in a git repository
    try:
        repo = Repo('.', search_parent_directories=True)
        repo_root = Path(repo.working_dir)
    except Exception:
        click.echo("Error: Not in a git repository")
        sys.exit(1)
    
    syncer = ModuleSyncer(repo_root)
    
    # Discover modules from module.json files
    syncer.discover_modules_from_json(recursive=recursive)
    
    # Add hardcoded modules
    syncer.add_hardcoded_modules()
    
    # Handle list mode
    if list_only:
        syncer.list_modules()
        sys.exit(0)
    
    # Determine operation mode
    if module_path:
        # Sync specific module
        syncer.sync_specific(module_path)
    else:
        # Sync all modules (default)
        syncer.sync_all()
    
    # Report results
    click.echo()
    click.echo("=" * 56)
    if syncer.sync_errors == 0:
        click.echo("[OK] All modules synced successfully")
        sys.exit(0)
    else:
        click.echo(f"[ERROR] {syncer.sync_errors} module(s) failed to sync")
        click.echo("Note: Some modules may not have remote repositories yet")
        sys.exit(1)


if __name__ == '__main__':
    main()
