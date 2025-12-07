"""DEPRECATED: Use Model.Entities instead.

This module re-exports from Model.Entities for backward compatibility.
"""
from Model.Entities import (
    IReadable,
    IModel,
    IdeaSchema,
    Review,
    Script,
    Title,
    Story,
)
from Model.state import StoryState

try:
    from Model.Entities import StoryReviewModel, ReviewType
except (ImportError, TypeError):
    pass

__all__ = [
    "IReadable",
    "IModel",
    "IdeaSchema",
    "Review",
    "Script",
    "Title",
    "Story",
    "StoryState",
]
