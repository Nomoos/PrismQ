"""PrismQ.Review.Model

Core data model for content reviews in the PrismQ ecosystem.

This module provides pure database/data models:
- Review: Simple review feedback model (text, score)
- StoryReview: Linking table for multiple reviews per Story

For business logic models with validation and workflow methods, use:
- T.Review.Content.Consistency for ConsistencyReview
- T.Review.Content.Content for ContentReview
- T.Review.Content.Editing for EditingReview

Workflow position:
    Idea → Title/Content → Review → Polish → Publishing

Example:
    >>> from T.Review.Model import Review
    >>>
    >>> review = Review(
    ...     text="Great title! Clear and engaging.",
    ...     score=85
    ... )
"""

try:
    from .src.review import Review
    from .src.story_review import ReviewType, StoryReview
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "Review",
    "StoryReview",
    "ReviewType",
]

__version__ = "0.1.0"
