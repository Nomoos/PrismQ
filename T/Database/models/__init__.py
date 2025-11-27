"""Database models module.

This module contains model interfaces and base classes for database operations.

Main Classes:
    - IModel: Base interface for all database models with CRUD operations
"""

from T.Database.models.base import IModel

__all__ = [
    "IModel",
]
