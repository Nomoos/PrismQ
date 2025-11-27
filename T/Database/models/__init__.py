"""PrismQ.T.Database.models - Database models.

This package provides database models for the PrismQ text generation pipeline.
"""

try:
    from .story_review import StoryReviewModel, ReviewType
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "StoryReviewModel",
    "ReviewType",
]
