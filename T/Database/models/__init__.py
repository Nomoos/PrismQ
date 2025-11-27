"""Database models for PrismQ.

This module exports all database models.
"""

from .review import Review

__all__ = [
    "Review",
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
