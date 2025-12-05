"""DEPRECATED: Use Model.entities instead.

This module re-exports from Model.entities for backward compatibility.
"""
from Model.entities import (
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
    from Model.entities import StoryReviewModel, ReviewType
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
