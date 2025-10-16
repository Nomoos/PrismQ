#!/usr/bin/env python3
"""Custom exceptions for PrismQ Repository Builder."""


class RepoBuilderError(Exception):
    """Base exception for repository builder errors."""
    pass


class GitHubCLIError(RepoBuilderError):
    """Exception raised when GitHub CLI authentication fails."""
    pass


class ModuleParseError(RepoBuilderError):
    """Exception raised when module name parsing fails."""
    pass
