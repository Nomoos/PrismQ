#!/usr/bin/env python3
"""PrismQ Subtree Converter.

A modular tool for converting nested git repositories to git subtrees,
following SOLID principles with proper separation of concerns.

Modules:
- exceptions.py: Custom exception classes
- command_runner.py: Command execution abstraction (SRP, DIP)
- git_operations.py: Git-specific operations (SRP)
- repository_scanner.py: Repository discovery logic (SRP)
- subtree_manager.py: Subtree add/merge operations (SRP)
- backup_manager.py: Backup/restore functionality (SRP)
- path_resolver.py: Path resolution logic (SRP)
- cli.py: CLI interface and main workflow (SRP)

Usage:
    python -m subtree-converter
    python cli.py
"""

try:
    from .backup_manager import BackupManager
    from .cli import SubtreeConverter, main
    from .command_runner import CommandRunner, SubprocessCommandRunner
    from .exceptions import (
        BackupError,
        CommandExecutionError,
        PathResolutionError,
        RepositoryNotFoundError,
        SubtreeConverterError,
    )
    from .git_operations import GitOperations, GitOperationsImpl
    from .path_resolver import PathResolver
    from .repository_scanner import (
        ModuleRepository,
        NestedRepository,
        RepositoryScanner,
    )
    from .subtree_manager import SubtreeManager
except ImportError:
    from backup_manager import BackupManager
    from cli import SubtreeConverter, main
    from command_runner import CommandRunner, SubprocessCommandRunner
    from exceptions import (
        BackupError,
        CommandExecutionError,
        PathResolutionError,
        RepositoryNotFoundError,
        SubtreeConverterError,
    )
    from git_operations import GitOperations, GitOperationsImpl
    from path_resolver import PathResolver
    from repository_scanner import (
        ModuleRepository,
        NestedRepository,
        RepositoryScanner,
    )
    from subtree_manager import SubtreeManager

__all__ = [
    # Main
    "main",
    "SubtreeConverter",
    # Exceptions
    "SubtreeConverterError",
    "CommandExecutionError",
    "RepositoryNotFoundError",
    "BackupError",
    "PathResolutionError",
    # Command execution
    "CommandRunner",
    "SubprocessCommandRunner",
    # Git operations
    "GitOperations",
    "GitOperationsImpl",
    # Repository scanning
    "RepositoryScanner",
    "NestedRepository",
    "ModuleRepository",
    # Subtree management
    "SubtreeManager",
    # Backup management
    "BackupManager",
    # Path utilities
    "PathResolver",
]
