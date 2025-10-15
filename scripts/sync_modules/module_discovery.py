"""Module discovery functionality."""

import json
from pathlib import Path
from typing import List, Dict
import click

from .path_utils import derive_remote_name


def discover_modules_from_json(repo_root: Path, recursive: bool = False) -> List[Dict[str, str]]:
    """
    Discover modules with module.json files.
    
    Args:
        repo_root: Root of the repository
        recursive: If True, recursively find all module.json files
        
    Returns:
        List of module configurations
    """
    modules = []
    src_dir = repo_root / "src"
    if not src_dir.exists():
        return modules
    
    if recursive:
        modules = _discover_modules_recursive(src_dir, repo_root)
    else:
        modules = _discover_first_level_modules(src_dir, repo_root)
    
    return modules


def _discover_first_level_modules(src_dir: Path, repo_root: Path) -> List[Dict[str, str]]:
    """Discover first-level modules only."""
    modules = []
    
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
        
        module_config = _add_module_from_config(config_file, module_dir, repo_root)
        if module_config:
            modules.append(module_config)
    
    return modules


def _discover_modules_recursive(base_dir: Path, repo_root: Path) -> List[Dict[str, str]]:
    """Recursively discover all modules with module.json files."""
    modules = []
    
    for item in base_dir.rglob("module.json"):
        module_dir = item.parent
        
        # Check if it's a valid module (has src/ subdirectory)
        if not (module_dir / "src").exists():
            continue
        
        module_config = _add_module_from_config(item, module_dir, repo_root)
        if module_config:
            modules.append(module_config)
    
    return modules


def _add_module_from_config(config_file: Path, module_dir: Path, repo_root: Path) -> Dict[str, str]:
    """
    Add a module from its module.json configuration.
    
    Returns:
        Module configuration dict or None if failed
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        remote_url = config.get('remote', {}).get('url')
        if not remote_url:
            click.echo(f"WARNING: {config_file} is missing remote URL configuration")
            return None
        
        # Derive remote name from URL
        remote_name = derive_remote_name(remote_url)
        
        # Branch is always main
        branch = "main"
        
        # Get module path relative to repo root
        module_path = module_dir.relative_to(repo_root)
        
        click.echo(f"Discovered module from module.json: {module_path}")
        
        return {
            'path': str(module_path),
            'remote_name': remote_name,
            'remote_url': remote_url,
            'branch': branch
        }
            
    except (json.JSONDecodeError, IOError) as e:
        click.echo(f"WARNING: Failed to read {config_file}: {e}")
        return None


def get_hardcoded_modules() -> List[Dict[str, str]]:
    """Get list of hardcoded module configurations."""
    return [
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
