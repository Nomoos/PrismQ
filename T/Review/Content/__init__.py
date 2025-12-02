"""PrismQ.T.Review.Content - AI Content Review Module

AI-powered narrative and content validation for script content.
Stage 16 (MVP-016) in the iterative co-improvement workflow.

DEPRECATED: This module is deprecated. Import from T.Review.Model instead:
    from T.Review.Model import ContentReview, ContentIssue, ContentIssueType, ContentSeverity
"""

from T.Review import ReviewSeverity
from T.Review.Model.src.content_review import (
    ContentReview,
    ContentIssue,
    ContentIssueType,
    ContentSeverity
)

# Re-export unified severity for convenience
# ContentSeverity is kept for backward compatibility, but ReviewSeverity is the unified version
__all__ = [
    "ContentReview",
    "ContentIssue",
    "ContentIssueType",
    "ContentSeverity",
    "ReviewSeverity",
]
