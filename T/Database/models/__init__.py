"""PrismQ.T.Database.models - Database models and interfaces.

This package provides database models and interfaces for the PrismQ text
generation pipeline.

Model Interfaces:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations (extends IReadable)

Models:
    - IdeaSchema: SQL schema definition for Idea table
    - Title: Versioned title content with review FK
    - Script: Script model for versioned content storage
    - Review: Simple review model for content review storage
    - Story: Story model for content workflow management
    - StoryState: Enum for Story workflow states (imported from T.State.constants.state_names)
    - StoryReviewModel: Linking table for Story reviews with review types
    - ReviewType: Enum for review types (grammar, tone, content, etc.)

Models follow the Dependency Inversion Principle by depending
on the IModel abstraction rather than concrete database implementations.
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.idea import IdeaSchema
from T.Database.models.review import Review
from T.Database.models.script import Script
from T.Database.models.title import Title
from T.Database.models.story import Story
from T.State.constants.state_names import StoryState

try:
    from .story_review import StoryReviewModel, ReviewType
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    # Interfaces
    "IReadable",
    "IModel",
    # Schema definitions
    "IdeaSchema",
    # Models
    "StoryReviewModel",
    "ReviewType",
    "Review",
    "Script",
    "Title",
    "Story",
    "StoryState",
]
