"""PrismQ.Review.Model - Core data models for content reviews.

This package provides the Review and StoryReview models for representing
content feedback in the PrismQ content creation workflow.

Models:
- Review: Simple review content (text, score)
- StoryReview: Linking table for Story reviews with review types
- ConsistencyReview: Script consistency validation model
- ContentReview: Script content validation model
- EditingReview: Script editing validation model
"""

try:
    from .review import Review
    from .story_review import StoryReview, ReviewType
    from .consistency_review import (
        ConsistencyReview,
        ConsistencyIssue,
        ConsistencyIssueType,
        ConsistencySeverity
    )
    from .content_review import (
        ContentReview,
        ContentIssue,
        ContentIssueType,
        ContentSeverity
    )
    from .editing_review import (
        EditingReview,
        EditingIssue,
        EditingIssueType,
        EditingSeverity
    )
except ImportError:
    # Allow importing when not installed as package
    pass

__all__ = [
    "Review",
    "StoryReview",
    "ReviewType",
    # Consistency Review
    "ConsistencyReview",
    "ConsistencyIssue",
    "ConsistencyIssueType",
    "ConsistencySeverity",
    # Content Review
    "ContentReview",
    "ContentIssue",
    "ContentIssueType",
    "ContentSeverity",
    # Editing Review
    "EditingReview",
    "EditingIssue",
    "EditingIssueType",
    "EditingSeverity",
]

__version__ = "0.1.0"
