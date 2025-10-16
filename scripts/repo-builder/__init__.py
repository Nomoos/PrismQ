#!/usr/bin/env python3
"""
PrismQ Nested Repository Builder & Checker Package

This package provides tools for validating GitHub CLI authentication and 
deriving the full module chain from root to deepest, given a PrismQ dotted 
name or GitHub URL.
"""

# Re-export all public functions and classes for backward compatibility
try:
    from .exceptions import RepoBuilderError, GitHubCLIError, ModuleParseError
    from .validation import validate_github_cli
    from .parsing import parse_github_url, derive_module_chain
    from .display import display_module_chain
    from .repository import repository_exists, get_repository_path, create_git_chain
    from .cli import get_module_input_interactive, run_git_creation, main
except ImportError:
    from exceptions import RepoBuilderError, GitHubCLIError, ModuleParseError
    from validation import validate_github_cli
    from parsing import parse_github_url, derive_module_chain
    from display import display_module_chain
    from repository import repository_exists, get_repository_path, create_git_chain
    from cli import get_module_input_interactive, run_git_creation, main

__all__ = [
    # Exceptions
    'RepoBuilderError',
    'GitHubCLIError',
    'ModuleParseError',
    # Validation
    'validate_github_cli',
    # Parsing
    'parse_github_url',
    'derive_module_chain',
    # Display
    'display_module_chain',
    # Repository
    'repository_exists',
    'get_repository_path',
    'create_git_chain',
    # CLI
    'get_module_input_interactive',
    'run_git_creation',
    'main',
]
