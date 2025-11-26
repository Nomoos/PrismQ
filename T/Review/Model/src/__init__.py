"""PrismQ.Review.Model - Core data models for content reviews.

This package provides the Review and StoryReview models for representing
content feedback in the PrismQ content creation workflow.

Models:
- Review: Simple review content (text, score)
- StoryReview: Linking table for Story reviews with review types
"""

try:
    from .review import Review
    from .story_review import StoryReview, ReviewType
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "Review",
    "StoryReview",
    "ReviewType",
]

__version__ = "0.1.0"
