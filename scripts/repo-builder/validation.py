#!/usr/bin/env python3
"""GitHub CLI validation functions."""

import subprocess

try:
    from .exceptions import GitHubCLIError
except ImportError:
    from exceptions import GitHubCLIError


def validate_github_cli() -> bool:
    """
    Validate that GitHub CLI is installed and authenticated.
    
    Returns:
        True if GitHub CLI is authenticated
        
    Raises:
        GitHubCLIError: If GitHub CLI is not installed or not authenticated
    """
    print("🔍 Validating GitHub CLI authentication...")
    
    # Check if gh CLI is installed
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise GitHubCLIError("GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/")
    except FileNotFoundError:
        raise GitHubCLIError("GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/")
    
    # Check if authenticated
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise GitHubCLIError("GitHub CLI is not authenticated. Please run 'gh auth login'")
        
        print("✅ GitHub CLI is authenticated")
        return True
        
    except FileNotFoundError:
        raise GitHubCLIError("GitHub CLI (gh) is not installed")
