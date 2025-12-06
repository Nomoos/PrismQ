"""PrismQ domain entities.

This module provides the core domain entities for the PrismQ workflow system.
All entities implement the IModel interface for persistence operations.

Entities:
    - Story: Content workflow management with state tracking
    - Title: Versioned title content with review FK
    - Script: Versioned script content with review FK
    - Review: Content review scores and feedback
    - IdeaSchema: SQL schema definition for Idea table
    - StoryReviewModel: Linking table for Story reviews

Interfaces:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations

Example:
    >>> from Model.Entities import Story, Title, Script
    >>> story = Story(idea_id="1", state="CREATED")
"""

from Model.Entities.base import IReadable, IModel
from Model.Entities.story import Story
from Model.Entities.title import Title
from Model.Entities.script import Script
from Model.Entities.review import Review
from Model.Entities.idea import IdeaSchema

try:
    from Model.Entities.story_review import StoryReviewModel, ReviewType
except ImportError:
    StoryReviewModel = None
    ReviewType = None

__all__ = [
    # Interfaces
    "IReadable",
    "IModel",
    # Entities
    "Story",
    "Title",
    "Script",
    "Review",
    "IdeaSchema",
    "StoryReviewModel",
    "ReviewType",
]
