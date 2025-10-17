#!/usr/bin/env python3
"""Custom exception classes for add-repo-with-submodule."""


class SubmoduleError(Exception):
    """Base exception for submodule operations."""
    pass


class SubmoduleAddError(SubmoduleError):
    """Error when adding a submodule fails."""
    pass


class SubmoduleCommitError(SubmoduleError):
    """Error when committing submodule changes fails."""
    pass


class ParentNotFoundError(SubmoduleError):
    """Error when parent repository is not found."""
    pass
