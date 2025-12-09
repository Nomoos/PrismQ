"""PrismQ.Review.Model - Core data models for content reviews.

This package provides pure database/data models for representing
content feedback in the PrismQ content creation workflow.

Models:
- Review: Simple review content (text, score)
- StoryReview: Linking table for Story reviews with review types

For business logic models with validation and workflow methods, use:
- T.Review.Content.Consistency for ConsistencyReview
- T.Review.Content.Content for ContentReview
- T.Review.Content.Editing for EditingReview
"""

try:
    from .review import Review
    from .story_review import ReviewType, StoryReview
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "Review",
    "StoryReview",
    "ReviewType",
]

__version__ = "0.1.0"
