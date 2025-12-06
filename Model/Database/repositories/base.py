"""DEPRECATED: Use Model.repositories.base instead."""
from Model.repositories.base import IRepository, IUpdatableRepository, IVersionedRepository
__all__ = ["IRepository", "IUpdatableRepository", "IVersionedRepository"]
