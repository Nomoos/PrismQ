"""GitHub client management."""

import subprocess
from typing import Optional
import click
from github import Github


def get_github_client() -> Github:
    """
    Get authenticated GitHub client.
    
    Attempts to authenticate using gh CLI token. Falls back to
    unauthenticated client if authentication fails.
    
    Returns:
        Authenticated or unauthenticated Github client instance
    """
    try:
        # Try to get token from gh CLI
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        token = result.stdout.strip()
        from github import Auth
        auth = Auth.Token(token)
        return Github(auth=auth)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("Warning: GitHub CLI not authenticated. Repository operations may fail.")
        click.echo("Please run: gh auth login")
        return Github()  # Unauthenticated client
