"""Database models module.

This module exports all database models and interfaces.

Main Classes:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations (extends IReadable)
    - Review: Simple review model for content review storage
    - Script: Script model for versioned content storage
    - Title: Versioned title content with review FK

Models follow the Dependency Inversion Principle by depending
on the IModel abstraction rather than concrete database implementations.
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.review import Review
from T.Database.models.script import Script
from T.Database.models.title import Title

__all__ = [
    "IReadable",
    "IModel",
    "Review",
    "Script",
    "Title",
]
