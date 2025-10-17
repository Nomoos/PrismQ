#!/usr/bin/env python3
"""
Add Repository with Submodule Package

A tool that creates GitHub repositories and registers them as git submodules.
Uses repo-builder for repository creation and adds submodule registration.
"""

__version__ = "1.0.0"

# Export main functions
try:
    from .add_repo_submodule import main, add_chain_as_submodules
    from .submodule_operations import (
        add_git_submodule,
        commit_submodule_changes,
        is_git_repository
    )
    from .exceptions import (
        SubmoduleError,
        SubmoduleAddError,
        SubmoduleCommitError,
        ParentNotFoundError
    )
    from .cli import cli_main
except ImportError:
    from add_repo_submodule import main, add_chain_as_submodules
    from submodule_operations import (
        add_git_submodule,
        commit_submodule_changes,
        is_git_repository
    )
    from exceptions import (
        SubmoduleError,
        SubmoduleAddError,
        SubmoduleCommitError,
        ParentNotFoundError
    )
    from cli import cli_main

__all__ = [
    'main',
    'add_chain_as_submodules',
    'add_git_submodule',
    'commit_submodule_changes',
    'is_git_repository',
    'SubmoduleError',
    'SubmoduleAddError',
    'SubmoduleCommitError',
    'ParentNotFoundError',
    'cli_main',
]
