"""PrismQ repository implementations.

This module provides repository pattern implementations for data persistence.
All repositories follow the IRepository interface for consistent data access.

Repositories:
    - StoryRepository: CRUD operations for Story entities (supports UPDATE)
    - TitleRepository: Insert-only versioned Title persistence
    - ScriptRepository: Insert-only versioned Script persistence
    - ReviewRepository: Insert-only Review persistence
    - StoryReviewRepository: Story review linking table operations

Interfaces:
    - IRepository: Base repository interface (read + insert)
    - IUpdatableRepository: Extended interface with update capability

Example:
    >>> from Model.Repositories import StoryRepository
    >>> repo = StoryRepository(connection)
    >>> story = repo.find_by_id(1)
"""

from Model.Repositories.base import IRepository, IUpdatableRepository
from Model.Repositories.story_repository import StoryRepository
from Model.Repositories.title_repository import TitleRepository
from Model.Repositories.script_repository import ScriptRepository
from Model.Repositories.review_repository import ReviewRepository

try:
    from Model.Repositories.story_review_repository import StoryReviewRepository
except ImportError:
    StoryReviewRepository = None

__all__ = [
    # Interfaces
    "IRepository",
    "IUpdatableRepository",
    # Repositories
    "StoryRepository",
    "TitleRepository",
    "ScriptRepository",
    "ReviewRepository",
    "StoryReviewRepository",
]
