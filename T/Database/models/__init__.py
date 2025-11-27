"""PrismQ.T.Database.models - Database models.

This package provides database models for the PrismQ text generation pipeline.
"""

try:
    from .story_review import StoryReviewModel, ReviewType
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "StoryReviewModel",
    "ReviewType",
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
