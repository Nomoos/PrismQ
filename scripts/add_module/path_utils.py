"""Path and naming utilities for modules."""

from typing import Tuple


def derive_module_path(repo_name: str) -> Tuple[str, str]:
    """
    Derive module path from repository name.
    
    Converts repository name like "PrismQ.IdeaInspiration.Sources"
    to module name "IdeaInspiration.Sources" and path "src/IdeaInspiration/src/Sources"
    
    Args:
        repo_name: Repository name (e.g., "PrismQ.ModuleName")
        
    Returns:
        Tuple of (module_name, module_path)
    """
    # Remove "PrismQ." prefix if present
    module_full_name = repo_name.replace('PrismQ.', '', 1)
    
    # Split by dots
    components = module_full_name.split('.')
    
    if len(components) == 1:
        # Single component: src/Component
        return components[0], f"src/{components[0]}"
    else:
        # Multiple components: src/First/src/Second/src/Third...
        path_parts = [f"src/{components[0]}"]
        for component in components[1:]:
            path_parts.append(f"src/{component}")
        module_path = '/'.join(path_parts)
        return module_full_name, module_path


def derive_remote_name(remote_url: str) -> str:
    """
    Derive remote name from repository URL.
    
    Converts URL like "https://github.com/Nomoos/PrismQ.RepositoryTemplate.git"
    to "prismq-repositorytemplate"
    
    Args:
        remote_url: GitHub repository URL
        
    Returns:
        Remote name for git operations
    """
    # Extract repo name from URL
    url = remote_url.replace('.git', '')
    repo_name = url.split('/')[-1]
    
    # Convert to lowercase and replace dots/underscores with hyphens
    remote_name = repo_name.lower().replace('.', '-').replace('_', '-')
    
    return remote_name
