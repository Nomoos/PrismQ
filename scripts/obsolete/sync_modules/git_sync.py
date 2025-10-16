"""Git synchronization operations for modules."""

import subprocess
from pathlib import Path
from typing import Dict
import click
from git import Repo, GitCommandError


def validate_and_set_origin(module_path: Path, remote_url: str):
    """
    Validate and set origin for a module if it has a .git directory.
    
    Args:
        module_path: Path to the module directory
        remote_url: Expected remote URL
    """
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


def sync_module(module: Dict[str, str], repo_root: Path, repo: Repo) -> bool:
    """
    Sync a single module using git subtree.
    
    Args:
        module: Module configuration dict
        repo_root: Root of the main repository
        repo: Git repository object
        
    Returns:
        True if successful, False otherwise
    """
    module_path = module['path']
    remote_name = module['remote_name']
    remote_url = module['remote_url']
    branch = module['branch']
    
    click.echo()
    click.echo("=" * 56)
    click.echo(f"Syncing module: {module_path}")
    click.echo("=" * 56)
    
    module_dir = repo_root / module_path
    
    # Check if module directory exists
    if not module_dir.exists():
        click.echo(f"Module directory '{module_path}' does not exist yet")
        click.echo("This module will be added on first sync from remote")
    else:
        # Check for module.json and validate/set origin
        config_file = module_dir / "module.json"
        if config_file.exists():
            validate_and_set_origin(module_dir, remote_url)
        else:
            click.echo(f"WARNING: {module_path}/module.json not found")
            click.echo("The module repository may not have proper remote configuration")
    
    # Check if remote exists
    try:
        remote = repo.remote(remote_name)
        click.echo(f"Remote '{remote_name}' already exists")
    except ValueError:
        # Remote doesn't exist, add it
        click.echo(f"Adding remote '{remote_name}' -> {remote_url}")
        repo.create_remote(remote_name, remote_url)
        remote = repo.remote(remote_name)
    
    # Fetch from remote
    click.echo(f"Fetching from {remote_name}...")
    try:
        # Explicitly fetch the main branch from the remote
        remote.fetch(refspec='refs/heads/main:refs/remotes/{}/{}'.format(remote_name, branch))
    except GitCommandError as e:
        click.echo(f"Failed to fetch from {remote_name}")
        click.echo(f"Repository may not exist yet: {remote_url}")
        click.echo(f"Error: {e}")
        return False
    
    # Pull updates using subtree
    click.echo(f"Pulling updates to {module_path}...")
    try:
        # Use git subtree command directly
        result = subprocess.run(
            ['git', 'subtree', 'pull', f'--prefix={module_path}', remote_name, branch, '--squash'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        click.echo(f"[OK] Successfully synced {module_path}")
        return True
    except subprocess.CalledProcessError as e:
        click.echo(f"[ERROR] Failed to sync {module_path}")
        if e.stderr:
            click.echo(f"Error: {e.stderr}")
        return False
