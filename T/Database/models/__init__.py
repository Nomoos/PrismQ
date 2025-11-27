"""Database models for PrismQ.

This package contains the database model implementations following
the Dependency Inversion Principle - depending on abstractions (IModel)
rather than concrete implementations.
"""

from .base import IModel
from .script import Script

__all__ = ["IModel", "Script"]
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
