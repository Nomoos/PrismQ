"""PrismQ.T.Review.Editing - AI Editing Review Module

AI-powered editing and clarity validation for script content.
Stage 18 (MVP-018) in the iterative co-improvement workflow.

DEPRECATED: This module is deprecated. Import from T.Review.Model instead:
    from T.Review.Model import EditingReview, EditingIssue, EditingIssueType, EditingSeverity
"""

from T.Review import ReviewSeverity
from T.Review.Model.src.editing_review import (
    EditingReview,
    EditingIssue,
    EditingIssueType,
    EditingSeverity
)

# Re-export unified severity for convenience
# EditingSeverity is kept for backward compatibility, but ReviewSeverity is the unified version
__all__ = [
    "EditingReview",
    "EditingIssue",
    "EditingIssueType",
    "EditingSeverity",
    "ReviewSeverity",
]
