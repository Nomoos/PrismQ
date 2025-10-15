"""Path and naming utilities for module synchronization."""


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
