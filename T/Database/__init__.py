"""PrismQ.T.Database - Database Models and Persistence Layer.

This module provides database model interfaces and implementations for the PrismQ
workflow, following SOLID principles.

Following SOLID principles:
- Single Responsibility: Each model has one responsibility
- Open/Closed: Models can be extended without modification
- Liskov Substitution: All model implementations are interchangeable
- Interface Segregation: Small, focused interfaces (IModel defines only CRUD)
- Dependency Inversion: Depend on abstractions, not concretions

Main Classes:
    - IModel: Interface defining base model CRUD operations

Example:
    >>> from T.Database.models.base import IModel
    >>> # Implement IModel for your specific entity
"""

from T.Database.models.base import IModel

__all__ = [
    "IModel",
]
