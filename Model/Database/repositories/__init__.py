"""DEPRECATED: Use Model.Repositories instead.

This module re-exports from Model.Repositories for backward compatibility.
"""
from Model.Repositories import (
    IRepository,
    IUpdatableRepository,
    StoryRepository,
    TitleRepository,
    ScriptRepository,
    ReviewRepository,
)

try:
    from Model.Repositories import StoryReviewRepository
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
