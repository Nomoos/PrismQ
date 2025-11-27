"""Database repositories module.

This module contains repository interfaces and implementations for data access.

Interfaces:
    - IRepository: Base interface for Insert + Read operations
    - IVersionedRepository: Extended interface for versioned entities (Title, Script)
    - IUpdatableRepository: Extended interface for updatable entities (Story)

Implementations:
    - TitleRepository: SQLite implementation for Title entities
    - ScriptRepository: SQLite implementation for Script entities
"""

from T.Database.repositories.base import (
    IRepository,
    IVersionedRepository,
    IUpdatableRepository,
)
from T.Database.repositories.title_repository import TitleRepository
from T.Database.repositories.script_repository import ScriptRepository

__all__ = [
    # Interfaces
    "IRepository",
    "IVersionedRepository",
    "IUpdatableRepository",
    # Implementations
    "TitleRepository",
    "ScriptRepository",
]
