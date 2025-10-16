#!/usr/bin/env python3
"""Custom exceptions for PrismQ Subtree Converter."""


class SubtreeConverterError(Exception):
    """Base exception for subtree converter errors."""

    pass


class CommandExecutionError(SubtreeConverterError):
    """Exception raised when a command execution fails."""

    pass


class RepositoryNotFoundError(SubtreeConverterError):
    """Exception raised when a git repository is not found."""

    pass


class BackupError(SubtreeConverterError):
    """Exception raised when backup operations fail."""

    pass


class PathResolutionError(SubtreeConverterError):
    """Exception raised when path resolution fails."""

    pass
