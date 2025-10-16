#!/usr/bin/env python3
"""URL and module name parsing functions."""

import re
from typing import List

try:
    from .exceptions import ModuleParseError
except ImportError:
    from exceptions import ModuleParseError


def parse_github_url(url: str) -> str:
    """
    Extract module name from GitHub URL.
    
    Args:
        url: GitHub URL (e.g., https://github.com/Nomoos/PrismQ.IdeaInspiration)
        
    Returns:
        Module name in dotted notation (e.g., PrismQ.IdeaInspiration)
        
    Raises:
        ModuleParseError: If URL format is invalid or doesn't meet requirements
    """
    # Match GitHub URL patterns with organization capture
    patterns = [
        r'https?://github\.com/([^/]+)/([^/\.]+(?:\.[^/\.]+)*)',
        r'git@github\.com:([^/]+)/([^/\.]+(?:\.[^/\.]+)*)\.git',
        r'git@github\.com:([^/]+)/([^/\.]+(?:\.[^/\.]+)*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            org_name = match.group(1)
            repo_name = match.group(2)
            # Replace any remaining .git suffix
            repo_name = re.sub(r'\.git$', '', repo_name)
            
            # Validate organization is Nomoos
            if org_name != "Nomoos":
                raise ModuleParseError(
                    f"GitHub URL must be from Nomoos organization, got: {org_name}"
                )
            
            # Validate repo starts with PrismQ. or is exactly PrismQ
            if not repo_name.startswith("PrismQ"):
                raise ModuleParseError(
                    f"Repository name must start with PrismQ., got: {repo_name}"
                )
            
            # Validate at least one segment after PrismQ
            parts = repo_name.split('.')
            if len(parts) < 2:
                raise ModuleParseError(
                    f"Repository name must have at least one segment after PrismQ, got: {repo_name}"
                )
            
            return repo_name
    
    raise ModuleParseError(f"Invalid GitHub URL format: {url}")


def derive_module_chain(module_input: str) -> List[str]:
    """
    Derive the full module chain from root to deepest.
    
    Args:
        module_input: Either a dotted module name (e.g., PrismQ.IdeaInspiration.SubModule)
                     or a GitHub URL
                     
    Returns:
        List of module names from root to deepest
        Example: ['PrismQ', 'PrismQ.IdeaInspiration', 'PrismQ.IdeaInspiration.SubModule']
        
    Raises:
        ModuleParseError: If module name format is invalid
    """
    # Check if input is a URL
    if module_input.startswith('http://') or module_input.startswith('https://') or module_input.startswith('git@'):
        module_name = parse_github_url(module_input)
    else:
        module_name = module_input
    
    # Validate module name format - must start with PrismQ. and have only alphanumeric segments
    if not re.match(r'^[A-Za-z][A-Za-z0-9]*(\.[A-Za-z][A-Za-z0-9]*)*$', module_name):
        raise ModuleParseError(
            f"Invalid module name format: {module_name}\n"
            "Module names must have only alphanumeric segments separated by dots"
        )
    
    # Validate starts with PrismQ.
    if not module_name.startswith("PrismQ.") and module_name != "PrismQ":
        raise ModuleParseError(
            f"Module name must start with PrismQ., got: {module_name}"
        )
    
    # Split into parts
    parts = module_name.split('.')
    
    # Validate at least one segment after PrismQ
    if len(parts) < 2:
        raise ModuleParseError(
            f"Module name must have at least one segment after PrismQ, got: {module_name}"
        )
    
    # Build chain from root to deepest
    chain = []
    for i in range(1, len(parts) + 1):
        chain.append('.'.join(parts[:i]))
    
    return chain
