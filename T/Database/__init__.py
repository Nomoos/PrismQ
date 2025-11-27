"""Database module for PrismQ.

This module contains database models and interfaces following SOLID principles:
- Single Responsibility: Each model handles only its own data
- Interface Segregation: Small, focused IModel interface
- Dependency Inversion: Depend on abstractions (IModel) not implementations
"""

from .models import IModel, Script

__all__ = ["IModel", "Script"]
"""PrismQ.T.Database - Database Models, Repositories and Persistence Layer.

This module provides database interfaces and implementations for the PrismQ
workflow, following SOLID principles.

Architecture: INSERT + READ Only
    All database tables follow an Insert+Read only pattern:
    - INSERT: Create new records/versions
    - READ: Query existing data
    - UPDATE: Not supported (create new version instead)
    - DELETE: Not supported (data is immutable for history preservation)

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

Design Decisions:
    - No delete operations: Data is immutable; new versions are created instead
    - Only created_at timestamp: Due to versioning, updated_at is not needed
    - IReadable separate from IModel: Allows read-only consumers to use minimal interface
    - IVersionedRepository: For tables like Title, Script that maintain version history

Example:
    >>> from T.Database import IReadable, IModel, IRepository, IVersionedRepository
    >>> # Implement IModel for entity persistence
    >>> # Implement IVersionedRepository for versioned data access
"""

from T.Database.models.base import IReadable, IModel
from T.Database.repositories.base import IRepository, IVersionedRepository

__all__ = [
    # Model interfaces
    "IReadable",
    "IModel",
    # Repository interfaces
    "IRepository",
    "IVersionedRepository",
]
