"""GitHub URL parsing utilities."""

from typing import Optional, Tuple


def parse_github_url(github_input: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse GitHub URL to extract owner and repository name.
    
    Supports formats:
    - https://github.com/Owner/RepoName.git
    - https://github.com/Owner/RepoName
    - git@github.com:Owner/RepoName.git
    - Owner/RepoName
    
    Args:
        github_input: GitHub URL or Owner/RepoName string
        
    Returns:
        Tuple of (owner, repository_name) or (None, None) if parsing fails
    """
    # Remove .git suffix if present
    url = github_input.replace('.git', '')
    
    # Handle different URL formats
    if 'github.com/' in url or 'github.com:' in url:
        # Full URL format
        url = url.replace('https://github.com/', '')
        url = url.replace('http://github.com/', '')
        url = url.replace('git@github.com:', '')
    
    # Extract owner and repo from "Owner/RepoName" format
    parts = url.split('/')
    if len(parts) >= 2:
        return parts[0], parts[1]
    
    return None, None
