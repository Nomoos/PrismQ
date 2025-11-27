"""Database models module.

This module contains model interfaces and base classes for database operations.

Main Classes:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations (extends IReadable)
    - Script: Script model for versioned content storage
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.script import Script

__all__ = [
    "IReadable",
    "IModel",
    "Script",
]
