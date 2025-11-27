"""Database models module.

This module contains model interfaces and base classes for database operations.

Main Classes:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations (extends IReadable)
    - Script: Script model for versioned content storage
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.script import Script
    - Title: Versioned title content with review FK

Models follow the Dependency Inversion Principle by depending
on the IModel abstraction rather than concrete database implementations.
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.title import Title

__all__ = [
    "IReadable",
    "IModel",
    "Script",
    "Title",
]
