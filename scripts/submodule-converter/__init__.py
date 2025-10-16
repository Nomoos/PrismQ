#!/usr/bin/env python3
"""PrismQ Submodule Converter.

A modular tool for converting nested git repositories to git submodules,
following SOLID principles with proper separation of concerns.

Modules:
- exceptions.py: Custom exception classes
- command_runner.py: Command execution abstraction (SRP, DIP)
- git_operations.py: Git-specific operations (SRP)
- repository_scanner.py: Repository discovery logic (SRP)
- submodule_manager.py: Submodule add operations (SRP)
- backup_manager.py: Backup/restore functionality (SRP)
- path_resolver.py: Path resolution logic (SRP)
- cli.py: CLI interface and main workflow (SRP)

Usage:
    python -m submodule-converter
    python cli.py
"""

try:
    from .backup_manager import BackupManager
    from .cli import SubmoduleConverter, main
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
    from .submodule_manager import SubmoduleManager
except ImportError:
    from backup_manager import BackupManager
    from cli import SubmoduleConverter, main
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
    from submodule_manager import SubmoduleManager

__all__ = [
    # Main
    "main",
    "SubmoduleConverter",
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
    # Submodule management
    "SubmoduleManager",
    # Backup management
    "BackupManager",
    # Path utilities
    "PathResolver",
]
