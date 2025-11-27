"""PrismQ.Database.models - Database model implementations.

This package provides:
- IModel: Base interface for all database models
- Title: Versioned title content with review FK

Models follow the Dependency Inversion Principle by depending
on the IModel abstraction rather than concrete database implementations.
"""

try:
    from .base import IModel
    from .title import Title
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "IModel",
    "Title",
"""Database models module.

This module contains model interfaces and base classes for database operations.

Main Classes:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations (extends IReadable)
"""

from T.Database.models.base import IReadable, IModel

__all__ = [
    "IReadable",
    "IModel",
]
