"""PrismQ.T.Database - Database Models, Repositories and Persistence Layer.

This module provides database interfaces and implementations for the PrismQ
workflow, following SOLID principles.

Architecture:
    PrismQ uses two distinct patterns based on data characteristics:
    
    1. INSERT + READ Only (Title, Script, Review, StoryReview):
       - INSERT: Create new records/versions
       - READ: Query existing data
       - UPDATE: Not supported (create new version instead)
       - DELETE: Not supported (data is immutable for history preservation)
    
    2. CRUD with UPDATE (Story):
       - CREATE: Create new story
       - READ: Query story data
       - UPDATE: Update state field (workflow progression)
       - DELETE: Not supported (stories never deleted)

Following SOLID principles:
- Single Responsibility: Each interface has one responsibility
- Open/Closed: Interfaces can be extended without modification
- Liskov Substitution: All implementations are interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions, not concretions

Model Interfaces:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations

Repository Interfaces:
    - IRepository: Interface for Insert + Read data access
    - IVersionedRepository: Extended interface for versioned entities
    - IUpdatableRepository: Extended interface for updatable entities

Repository Implementations:
    - TitleRepository: SQLite implementation for Title entities
    - ScriptRepository: SQLite implementation for Script entities
    - StoryReviewRepository: SQLite implementation for StoryReview entities

Models:
    - Title: Versioned title content with review FK
    - Script: Script model for versioned content storage
    - Review: Simple review model for content review storage
    - StoryReviewModel: Linking table for Story reviews (implements IModel)
    - ReviewType: Enum for review types (grammar, tone, content, etc.)

Design Decisions:
    - No delete operations: Data is immutable or never deleted
    - Version history preserved for Title, Script
    - Story state updated in place (workflow progression)
    - IReadable separate from IModel: Allows read-only consumers to use minimal interface

Example:
    >>> from T.Database import (
    ...     IRepository, IVersionedRepository,
    ...     TitleRepository, ScriptRepository, StoryReviewRepository,
    ...     Title, Script, StoryReviewModel, ReviewType
    ... )
    >>> 
    >>> # Create repositories with SQLite connection
    >>> title_repo = TitleRepository(connection)
    >>> script_repo = ScriptRepository(connection)
    >>> review_repo = StoryReviewRepository(connection)
    >>> 
    >>> # Insert new title and script
    >>> title = Title(story_id=1, version=0, text="My Title")
    >>> script = Script(story_id=1, version=0, text="Once upon a time...")
    >>> saved_title = title_repo.insert(title)
    >>> saved_script = script_repo.insert(script)
    >>> 
    >>> # Link story to review
    >>> story_review = StoryReviewModel(
    ...     story_id=1, review_id=5, version=0, review_type=ReviewType.GRAMMAR
    ... )
    >>> saved_review = review_repo.insert(story_review)
    >>> 
    >>> # Find latest versions
    >>> latest_title = title_repo.find_latest_version(story_id=1)
    >>> latest_script = script_repo.find_latest_version(story_id=1)
"""

__version__ = "0.1.0"

from T.Database.models.base import IReadable, IModel
from T.Database.models.story_review import StoryReviewModel, ReviewType
from T.Database.models.review import Review
from T.Database.models.script import Script
from T.Database.models.title import Title
from T.Database.models.story import Story, StoryState
from T.Database.repositories.base import (
    IRepository,
    IVersionedRepository,
    IUpdatableRepository,
)
from T.Database.repositories.title_repository import TitleRepository
from T.Database.repositories.story_review_repository import StoryReviewRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.review_repository import ReviewRepository

__all__ = [
    # Model interfaces
    "IReadable",
    "IModel",
    # Models
    "Title",
    "Script",
    "Review",
    "Story",
    "StoryState",
    "StoryReviewModel",
    "ReviewType",
    # Repository interfaces
    "IRepository",
    "IVersionedRepository",
    "IUpdatableRepository",
    # Repository implementations
    "TitleRepository",
    "ScriptRepository",
    "StoryReviewRepository",
    "StoryRepository",
    "ReviewRepository",
]
