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

Models:
    - Script: Script model for versioned content storage

Design Decisions:
    - No delete operations: Data is immutable or never deleted
    - Version history preserved for Title, Script
    - Story state updated in place (workflow progression)
    - IReadable separate from IModel: Allows read-only consumers to use minimal interface

Models:
    - Title: Versioned title content with review FK

Example:
    >>> from T.Database import IReadable, IModel, IRepository, IVersionedRepository, Script
    >>> # Implement IModel for entity persistence
    >>> # Implement IVersionedRepository for versioned data access
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.script import Script
from T.Database.repositories.base import IRepository, IVersionedRepository
    >>> from T.Database import IRepository, IVersionedRepository, TitleRepository
    >>> from T.Database.models import Title
    >>> 
    >>> # Create repository with SQLite connection
    >>> repo = TitleRepository(connection)
    >>> 
    >>> # Insert new title
    >>> title = Title(story_id=1, version=0, text="My Title")
    >>> saved = repo.insert(title)
    >>> 
    >>> # Find latest version
    >>> latest = repo.find_latest_version(story_id=1)
"""

from T.Database.models.base import IReadable, IModel
from T.Database.models.title import Title
from T.Database.repositories.base import (
    IRepository,
    IVersionedRepository,
    IUpdatableRepository,
)
from T.Database.repositories.title_repository import TitleRepository

__all__ = [
    # Model interfaces
    "IReadable",
    "IModel",
    # Repository interfaces
    "IRepository",
    "IVersionedRepository",
    # Models
    "Script",
    "IUpdatableRepository",
    # Repository implementations
    "TitleRepository",
    # Models
    "Title",
]
