"""DEPRECATED: Use Model.repositories instead.

This module re-exports from Model.repositories for backward compatibility.
"""
from Model.repositories import (
    IRepository,
    IUpdatableRepository,
    StoryRepository,
    TitleRepository,
    ScriptRepository,
    ReviewRepository,
)

try:
    from Model.repositories import StoryReviewRepository
except (ImportError, TypeError):
    pass

__all__ = [
    "IRepository",
    "IUpdatableRepository",
    "StoryRepository",
    "TitleRepository",
    "ScriptRepository",
    "ReviewRepository",
]
