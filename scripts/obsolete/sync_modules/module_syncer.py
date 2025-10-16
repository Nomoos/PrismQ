"""Main ModuleSyncer class orchestrating module synchronization."""

from pathlib import Path
from typing import List, Dict, Optional
import click
from git import Repo

from .module_discovery import (
    discover_modules_from_json,
    get_hardcoded_modules
)
from .git_sync import sync_module, validate_and_set_origin
from .path_utils import derive_remote_name


class ModuleSyncer:
    """Handles PrismQ module synchronization with git subtree."""

    def __init__(self, repo_root: Path):
        """
        Initialize ModuleSyncer.
        
        Args:
            repo_root: Path to the root of the main repository
        """
        self.repo_root = repo_root
        self.repo = Repo(repo_root)
        self.modules: List[Dict[str, str]] = []
        self.sync_errors = 0

    def derive_remote_name(self, remote_url: str) -> str:
        """Derive remote name from repository URL. Delegates to path_utils module."""
        return derive_remote_name(remote_url)

    def discover_modules_from_json(self, recursive: bool = False):
        """Discover modules with module.json files."""
        discovered = discover_modules_from_json(self.repo_root, recursive)
        for module in discovered:
            # Check if module already configured
            already_configured = any(
                m['path'] == module['path'] for m in self.modules
            )
            if not already_configured:
                self.modules.append(module)

    def add_hardcoded_modules(self):
        """Add hardcoded module configurations."""
        hardcoded = get_hardcoded_modules()
        
        for module in hardcoded:
            # Check if module already configured (from discovery)
            already_configured = any(
                m['path'] == module['path'] for m in self.modules
            )
            if not already_configured:
                self.modules.append(module)

    def validate_and_set_origin(self, module_path: Path, remote_url: str):
        """Validate and set origin for a module. Delegates to git_sync module."""
        validate_and_set_origin(module_path, remote_url)

    def sync_module(self, module: Dict[str, str]):
        """Sync a single module using git subtree. Delegates to git_sync module."""
        success = sync_module(module, self.repo_root, self.repo)
        if not success:
            self.sync_errors += 1

    def list_modules(self):
        """List all discovered modules."""
        click.echo()
        click.echo("=" * 56)
        click.echo("Discovered Modules:")
        click.echo("=" * 56)
        
        for module in self.modules:
            click.echo(f"- {module['path']}")
            click.echo(f"  Remote: {module['remote_name']} ({module['remote_url']})")
            click.echo(f"  Branch: {module['branch']}")

    def sync_all(self):
        """Sync all discovered modules."""
        for module in self.modules:
            self.sync_module(module)

    def sync_specific(self, module_path: str):
        """Sync a specific module by path."""
        for module in self.modules:
            if module['path'] == module_path:
                self.sync_module(module)
                return
        
        click.echo(f"Error: Module '{module_path}' not found in discovered modules")
        click.echo("Run with --list-only to see available modules")
