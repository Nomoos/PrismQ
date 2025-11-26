"""PrismQ.Review.Model

Core data model for content reviews in the PrismQ ecosystem.

This module provides the Review data model which represents feedback
for Title, Script, and Story content. Reviews support:
- Direct FK relationship from Title/Script for 1:1 reviews
- StoryReview linking table for multiple reviews per Story

Workflow position:
    Idea → Title/Script → Review → Polish → Publishing

Example:
    >>> from T.Review.Model.src.review import Review
    >>> 
    >>> review = Review(
    ...     text="Great title! Clear and engaging.",
    ...     score=85
    ... )
"""

try:
    from .src.review import Review
    from .src.story_review import StoryReview, ReviewType
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "Review",
    "StoryReview",
    "ReviewType",
]

__version__ = "0.1.0"
