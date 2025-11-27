"""Database repositories module.

This module contains repository interfaces and implementations for data access.

Interfaces:
    - IRepository: Base interface for Insert + Read operations
    - IVersionedRepository: Extended interface for versioned entities (Title, Script)
    - IUpdatableRepository: Extended interface for updatable entities (Story)

Implementations:
    - TitleRepository: SQLite implementation for Title entities
    - StoryReviewRepository: SQLite implementation for StoryReview entities
"""

from T.Database.repositories.base import (
    IRepository,
    IVersionedRepository,
    IUpdatableRepository,
)
from T.Database.repositories.title_repository import TitleRepository
from T.Database.repositories.story_review_repository import StoryReviewRepository

__all__ = [
    # Interfaces
    "IRepository",
    "IVersionedRepository",
    "IUpdatableRepository",
    # Implementations
    "TitleRepository",
    "StoryReviewRepository",
]
