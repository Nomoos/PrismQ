#!/usr/bin/env python3
"""
PrismQ Add Module Script - CLI Entry Point

This script interactively creates a new PrismQ module with GitHub integration.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from git import Repo

from .module_creator import ModuleCreator


@click.command()
@click.option('--github-url', help='GitHub repository URL or Owner/RepoName format')
@click.option('--description', default='A PrismQ module', help='Module description')
def main(github_url: Optional[str], description: str):
    """PrismQ Module Creation Script - Create a new PrismQ module with GitHub integration."""
    
    click.echo()
    click.echo("=" * 56)
    click.echo("        PrismQ Module Creation Script")
    click.echo("=" * 56)
    click.echo()
    
    # Check if we're in a git repository
    try:
        repo = Repo('.', search_parent_directories=True)
        repo_root = Path(repo.working_dir)
    except Exception:
        click.echo("Error: Not in a git repository")
        click.echo("Please run this script from the root of the PrismQ repository")
        sys.exit(1)
    
    creator = ModuleCreator(repo_root)
    
    # Always use GitHub URL input method
    if github_url:
        # GitHub URL provided via command line
        github_input = github_url
    else:
        # Interactive mode - prompt for GitHub URL
        github_input = click.prompt("Enter the GitHub repository URL (e.g., https://github.com/Nomoos/PrismQ.RepositoryTemplate.git)")
    
    # Parse GitHub URL
    github_owner, repo_name = creator.parse_github_url(github_input)
    
    if not github_owner or not repo_name:
        click.echo("Error: Failed to parse GitHub URL")
        sys.exit(1)
    
    # Derive module name and path from repository name
    module_name_derived, module_dir_path = creator.derive_module_path(repo_name)
    
    click.echo()
    click.echo("Parsed from GitHub URL:")
    click.echo(f"  Owner: {github_owner}")
    click.echo(f"  Repository: {repo_name}")
    click.echo(f"  Module Name: {module_name_derived}")
    click.echo(f"  Module Path: {module_dir_path}")
    click.echo()
    
    if not description or description == 'A PrismQ module':
        description = click.prompt("Please enter a short description for the module (optional)", 
                                  default="A PrismQ module", show_default=False)
    
    remote_url = f"https://github.com/{github_owner}/{repo_name}.git"
    
    # Derive remote name
    remote_name = creator.derive_remote_name(remote_url)
    
    # Display configuration summary
    click.echo()
    click.echo("=" * 56)
    click.echo("Module Configuration Summary")
    click.echo("=" * 56)
    click.echo(f"Module Name:        {module_name_derived}")
    click.echo(f"Module Directory:   {module_dir_path}")
    click.echo(f"Description:        {description}")
    click.echo(f"Repository Name:    {repo_name}")
    click.echo(f"GitHub Owner:       {github_owner}")
    click.echo(f"Remote URL:         {remote_url}")
    click.echo(f"Remote Name:        {remote_name}")
    click.echo("=" * 56)
    click.echo()
    
    # Confirm creation
    if not click.confirm("Create this module?"):
        click.echo("Module creation cancelled")
        sys.exit(0)
    
    click.echo()
    click.echo("Creating module structure...")
    
    # Create module structure
    module_dir = repo_root / module_dir_path
    if not creator.create_module_structure(
        module_dir,
        module_name_derived,
        repo_name,
        github_owner,
        remote_url,
        description
    ):
        sys.exit(1)
    
    # Initialize git repository
    creator.initialize_git_repo(module_dir, remote_url, module_name_derived)
    
    # Create GitHub repositories and set up hierarchy
    repos = creator.create_github_repositories(repo_name, github_owner)
    
    # Set up nested subtree structure
    creator.setup_nested_subtree(repos, module_dir)
    
    click.echo()
    click.echo("=" * 56)
    click.echo("Module created successfully!")
    click.echo("=" * 56)
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  1. Review the generated files in {module_dir}")
    click.echo("  2. The module has been committed to the parent repository")
    click.echo("  3. Push the parent repository changes:")
    click.echo("     git push")
    click.echo("  4. Use scripts/sync_modules.py (or scripts\\sync-modules.bat on Windows) to sync future updates")
    click.echo("     The module is managed as a git subtree hierarchy")
    click.echo()


if __name__ == '__main__':
    main()
