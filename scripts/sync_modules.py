#!/usr/bin/env python3
"""
PrismQ Module Sync Script (Python)
This script syncs first-level modules from their remote repositories using git subtree.
Each module can be maintained in a separate repository and synced to the main PrismQ repo.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import click
from git import Repo, GitCommandError


class ModuleSyncer:
    """Handles PrismQ module synchronization with git subtree."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.repo = Repo(repo_root)
        self.modules: List[Dict[str, str]] = []
        self.sync_errors = 0

    def derive_remote_name(self, remote_url: str) -> str:
        """
        Derive remote name from repository URL.
        
        Converts URL like "https://github.com/Nomoos/PrismQ.RepositoryTemplate.git"
        to "prismq-repositorytemplate"
        """
        # Extract repo name from URL
        url = remote_url.replace('.git', '')
        repo_name = url.split('/')[-1]
        
        # Convert to lowercase and replace dots/underscores with hyphens
        remote_name = repo_name.lower().replace('.', '-').replace('_', '-')
        
        return remote_name

    def discover_modules_from_json(self):
        """Discover modules with module.json files."""
        src_dir = self.repo_root / "src"
        if not src_dir.exists():
            return
        
        for module_dir in src_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            # Check if it's a valid module (has src/ subdirectory)
            if not (module_dir / "src").exists():
                continue
            
            # Check for module.json
            config_file = module_dir / "module.json"
            if not config_file.exists():
                continue
            
            # Read module.json
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                remote_url = config.get('remote', {}).get('url')
                if not remote_url:
                    click.echo(f"WARNING: {config_file} is missing remote URL configuration")
                    continue
                
                # Derive remote name from URL
                remote_name = self.derive_remote_name(remote_url)
                
                # Branch is always main
                branch = "main"
                
                # Get module path relative to repo root
                module_path = module_dir.relative_to(self.repo_root)
                
                # Check if module already configured
                already_configured = any(
                    m['path'] == str(module_path) for m in self.modules
                )
                
                if not already_configured:
                    self.modules.append({
                        'path': str(module_path),
                        'remote_name': remote_name,
                        'remote_url': remote_url,
                        'branch': branch
                    })
                    click.echo(f"Discovered module from module.json: {module_path}")
                    
            except (json.JSONDecodeError, IOError) as e:
                click.echo(f"WARNING: Failed to read {config_file}: {e}")

    def add_hardcoded_modules(self):
        """Add hardcoded module configurations."""
        hardcoded = [
            {
                'path': 'src/RepositoryTemplate',
                'remote_name': 'prismq-repositorytemplate',
                'remote_url': 'https://github.com/Nomoos/PrismQ.RepositoryTemplate.git',
                'branch': 'main'
            },
            {
                'path': 'src/IdeaInspiration',
                'remote_name': 'prismq-ideainspiration',
                'remote_url': 'https://github.com/Nomoos/PrismQ.IdeaInspiration.git',
                'branch': 'main'
            }
        ]
        
        for module in hardcoded:
            # Check if module already configured (from discovery)
            already_configured = any(
                m['path'] == module['path'] for m in self.modules
            )
            if not already_configured:
                self.modules.append(module)

    def validate_and_set_origin(self, module_path: Path, remote_url: str):
        """Validate and set origin for a module if it has a .git directory."""
        if not module_path.exists() or not (module_path / '.git').exists():
            return
        
        try:
            module_repo = Repo(module_path)
            
            # Get current origin URL
            try:
                origin = module_repo.remote('origin')
                current_url = next(origin.urls)
                
                if current_url != remote_url:
                    # Origin exists but different, update it
                    click.echo(f"Updating origin for {module_path} to {remote_url}")
                    origin.set_url(remote_url)
            except ValueError:
                # No origin set, add it
                click.echo(f"Setting origin for {module_path} to {remote_url}")
                module_repo.create_remote('origin', remote_url)
                
        except Exception as e:
            click.echo(f"WARNING: Failed to validate origin for {module_path}: {e}")

    def sync_module(self, module: Dict[str, str]):
        """Sync a single module using git subtree."""
        module_path = module['path']
        remote_name = module['remote_name']
        remote_url = module['remote_url']
        branch = module['branch']
        
        click.echo()
        click.echo("=" * 56)
        click.echo(f"Syncing module: {module_path}")
        click.echo("=" * 56)
        
        module_dir = self.repo_root / module_path
        
        # Check if module directory exists
        if not module_dir.exists():
            click.echo(f"Module directory '{module_path}' does not exist yet")
            click.echo("This module will be added on first sync from remote")
        else:
            # Check for module.json and validate/set origin
            config_file = module_dir / "module.json"
            if config_file.exists():
                self.validate_and_set_origin(module_dir, remote_url)
            else:
                click.echo(f"WARNING: {module_path}/module.json not found")
                click.echo("The module repository may not have proper remote configuration")
        
        # Check if remote exists
        try:
            remote = self.repo.remote(remote_name)
            click.echo(f"Remote '{remote_name}' already exists")
        except ValueError:
            # Remote doesn't exist, add it
            click.echo(f"Adding remote '{remote_name}' -> {remote_url}")
            self.repo.create_remote(remote_name, remote_url)
            remote = self.repo.remote(remote_name)
        
        # Fetch from remote
        click.echo(f"Fetching from {remote_name}...")
        try:
            remote.fetch(branch)
        except GitCommandError as e:
            click.echo(f"Failed to fetch from {remote_name}")
            click.echo(f"Repository may not exist yet: {remote_url}")
            click.echo(f"Error: {e}")
            self.sync_errors += 1
            return
        
        # Pull updates using subtree
        click.echo(f"Pulling updates to {module_path}...")
        try:
            # Use git subtree command directly
            result = subprocess.run(
                ['git', 'subtree', 'pull', f'--prefix={module_path}', remote_name, branch, '--squash'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            click.echo(f"[OK] Successfully synced {module_path}")
        except subprocess.CalledProcessError as e:
            click.echo(f"[ERROR] Failed to sync {module_path}")
            if e.stderr:
                click.echo(f"Error: {e.stderr}")
            self.sync_errors += 1

    def list_modules(self):
        """List all configured modules."""
        click.echo("Configured modules:")
        click.echo()
        
        for module in self.modules:
            click.echo(f"  • {module['path']}")
            click.echo(f"    Remote: {module['remote_name']} ({module['remote_url']})")
            click.echo(f"    Branch: {module['branch']}")
            click.echo()

    def sync_all(self):
        """Sync all configured modules."""
        click.echo("Syncing all configured modules...")
        click.echo()
        
        for module in self.modules:
            self.sync_module(module)

    def sync_specific(self, module_path: str):
        """Sync a specific module by path."""
        # Normalize path (convert backslashes to forward slashes)
        module_path = module_path.replace('\\', '/')
        
        # Find the module
        found = False
        for module in self.modules:
            if module['path'] == module_path:
                found = True
                self.sync_module(module)
                break
        
        if not found:
            click.echo(f"Error: Module '{module_path}' not found in configuration")
            click.echo("Use --list to see configured modules")
            sys.exit(1)


@click.command()
@click.option('--list', '-l', 'list_only', is_flag=True, help='List configured modules')
@click.option('--all', '-a', 'sync_all_flag', is_flag=True, help='Sync all configured modules (default)')
@click.argument('module_path', required=False)
def main(list_only: bool, sync_all_flag: bool, module_path: Optional[str]):
    """
    PrismQ Module Synchronization Script
    
    Syncs first-level modules from their remote repositories using git subtree.
    
    Examples:
    
        # Sync all modules
        python sync_modules.py
        
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
    syncer.discover_modules_from_json()
    
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
