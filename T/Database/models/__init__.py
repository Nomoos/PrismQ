"""Database models module.

This module exports all database models and interfaces.

Main Classes:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations (extends IReadable)
    - Review: Simple review model for content review storage
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.review import Review

__all__ = [
    "IReadable",
    "IModel",
    "Review",
]
