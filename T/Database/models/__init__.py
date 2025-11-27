"""PrismQ.T.Database.models - Database models and interfaces.

This package provides database models and interfaces for the PrismQ text
generation pipeline.

Model Interfaces:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations (extends IReadable)

Models:
    - StoryReviewModel: Linking table for Story reviews with review types
    - ReviewType: Enum for review types (grammar, tone, content, etc.)
    - Title: Versioned title content with review FK

Models follow the Dependency Inversion Principle by depending
on the IModel abstraction rather than concrete database implementations.
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.title import Title

try:
    from .story_review import StoryReviewModel, ReviewType
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    # Interfaces
    "IReadable",
    "IModel",
    # Models
    "StoryReviewModel",
    "ReviewType",
    "Title",
]
