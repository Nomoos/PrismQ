"""PrismQ.T.Database - Database Models and Persistence Layer.

This module provides database model interfaces and implementations for the PrismQ
workflow, following SOLID principles.

Following SOLID principles:
- Single Responsibility: Each model has one responsibility
- Open/Closed: Models can be extended without modification
- Liskov Substitution: All model implementations are interchangeable
- Interface Segregation: Small, focused interfaces (IReadable, IModel)
- Dependency Inversion: Depend on abstractions, not concretions

Main Classes:
    - IReadable: Interface for read-only model operations
    - IModel: Interface for full persistence operations

Design Decisions:
    - No delete operations: Data is immutable; new versions are created instead
    - Only created_at timestamp: Due to versioning, updated_at is not needed
    - IReadable separate from IModel: Allows read-only consumers to use minimal interface

Example:
    >>> from T.Database.models.base import IReadable, IModel
    >>> # Implement IReadable for read-only access
    >>> # Implement IModel for full persistence operations
"""

from T.Database.models.base import IReadable, IModel

__all__ = [
    "IReadable",
    "IModel",
]
