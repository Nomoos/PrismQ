"""Path derivation utilities for PrismQ modules.

This module handles conversion of PrismQ dot-notation module names
into correct nested folder structures, ensuring no repetitive segments.

PEP 257: Module-level docstring
PEP 484: Type hints throughout
"""

from typing import Tuple, List
import re


class PathDerivationError(Exception):
    """Raised when path derivation fails."""
    pass


def derive_module_path(repo_name: str) -> Tuple[str, str]:
    """
    Derive module path from repository name.
    
    Converts repository name like "PrismQ.IdeaInspiration.Sources"
    to module name "IdeaInspiration.Sources" and path "src/IdeaInspiration/src/Sources"
    
    Pattern:
    - PrismQ.RepositoryTemplate → src/RepositoryTemplate
    - PrismQ.IdeaInspiration.Sources → src/IdeaInspiration/src/Sources
    - PrismQ.Module.Nested.Path → src/Module/src/Nested/src/Path
    
    Args:
        repo_name: Repository name (e.g., "PrismQ.ModuleName")
        
    Returns:
        Tuple of (module_name, module_path)
        
    Raises:
        PathDerivationError: If the repo_name is invalid
        
    Examples:
        >>> derive_module_path("PrismQ.RepositoryTemplate")
        ('RepositoryTemplate', 'src/RepositoryTemplate')
        
        >>> derive_module_path("PrismQ.IdeaInspiration.Sources")
        ('IdeaInspiration.Sources', 'src/IdeaInspiration/src/Sources')
    """
    if not repo_name:
        raise PathDerivationError("Repository name cannot be empty")
    
    # Remove "PrismQ." prefix if present
    module_full_name = repo_name.replace('PrismQ.', '', 1)
    
    if not module_full_name:
        raise PathDerivationError("Module name cannot be empty after removing PrismQ prefix")
    
    # Split by dots
    components = module_full_name.split('.')
    
    # Validate components
    for comp in components:
        if not comp or not comp.strip():
            raise PathDerivationError(f"Invalid component in module name: {repo_name}")
    
    if len(components) == 1:
        # Single component: src/Component
        module_path = f"src/{components[0]}"
    else:
        # Multiple components: src/First/src/Second/src/Third...
        path_parts = [f"src/{components[0]}"]
        for component in components[1:]:
            path_parts.append(f"src/{component}")
        module_path = '/'.join(path_parts)
    
    # Validate no repetitive patterns
    _validate_no_repetitive_segments(module_path, components)
    
    return module_full_name, module_path


def _validate_no_repetitive_segments(path: str, components: List[str]) -> None:
    """
    Validate that path does not contain repetitive segments.
    
    Guards against patterns like:
    - src/ModuleName/src/ModuleName/src/ModuleName
    - src/src/Module
    
    Args:
        path: The derived path to validate
        components: The module name components
        
    Raises:
        PathDerivationError: If repetitive patterns are detected
    """
    # Check for consecutive 'src/src'
    if 'src/src' in path:
        raise PathDerivationError(f"Path contains consecutive 'src/src': {path}")
    
    # Check for repetitive module name patterns
    # e.g., ModuleName/src/ModuleName/src/ModuleName
    for component in components:
        # Pattern: component appears multiple times in succession with src/ between them
        pattern = f"{component}/src/{component}"
        if pattern in path:
            raise PathDerivationError(
                f"Path contains repetitive component pattern '{pattern}': {path}"
            )
    
    # Validate path structure: should alternate between src/ and component names
    parts = path.split('/')
    for i, part in enumerate(parts):
        if i % 2 == 0:  # Even indices should be 'src'
            if part != 'src':
                raise PathDerivationError(
                    f"Invalid path structure at position {i}: expected 'src', got '{part}'"
                )
        else:  # Odd indices should be component names
            if part not in components:
                raise PathDerivationError(
                    f"Invalid path structure at position {i}: '{part}' not in components"
                )


def derive_remote_name(remote_url: str) -> str:
    """
    Derive remote name from repository URL.
    
    Converts URL like "https://github.com/Nomoos/PrismQ.RepositoryTemplate.git"
    to "prismq-repositorytemplate"
    
    Args:
        remote_url: GitHub repository URL
        
    Returns:
        Remote name for git operations
        
    Examples:
        >>> derive_remote_name("https://github.com/Nomoos/PrismQ.Test.git")
        'prismq-test'
    """
    # Extract repo name from URL
    url = remote_url.replace('.git', '')
    repo_name = url.split('/')[-1]
    
    # Convert to lowercase and replace dots/underscores with hyphens
    remote_name = repo_name.lower().replace('.', '-').replace('_', '-')
    
    return remote_name


def parse_module_hierarchy(repo_name: str) -> List[str]:
    """
    Parse module hierarchy from repository name.
    
    For PrismQ.IdeaInspiration.Sources.Content, returns:
    ['PrismQ.IdeaInspiration', 'PrismQ.IdeaInspiration.Sources', 
     'PrismQ.IdeaInspiration.Sources.Content']
    
    Args:
        repo_name: Full repository name with PrismQ prefix
        
    Returns:
        List of repository names for each level in the hierarchy
        
    Examples:
        >>> parse_module_hierarchy("PrismQ.IdeaInspiration.Sources")
        ['PrismQ.IdeaInspiration', 'PrismQ.IdeaInspiration.Sources']
    """
    # Remove PrismQ. prefix to get module hierarchy
    hierarchy = repo_name.replace('PrismQ.', '', 1)
    
    # Build array of all hierarchy levels
    levels = []
    components = hierarchy.split('.')
    current_level = ""
    
    for component in components:
        if current_level:
            current_level += f".{component}"
        else:
            current_level = component
        levels.append(f"PrismQ.{current_level}")
    
    return levels
