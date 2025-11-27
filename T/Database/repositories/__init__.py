"""Database repositories module.

This module contains repository interfaces for data access operations.

Main Classes:
    - IRepository: Base interface for Insert + Read operations
    - IVersionedRepository: Extended interface for versioned entities (Title, Script)
"""

from T.Database.repositories.base import IRepository, IVersionedRepository

__all__ = [
    "IRepository",
    "IVersionedRepository",
]
