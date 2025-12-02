"""PrismQ.T.Review.Consistency - Script consistency validation module.

This module provides AI-powered consistency review for script content, checking:
- Character name consistency
- Timeline alignment
- Location continuity
- Contradiction detection
- Repeated detail matching

Stage 17 (MVP-017): Consistency Review

DEPRECATED: This module is deprecated. Import from T.Review.Model instead:
    from T.Review.Model import ConsistencyReview, ConsistencyIssue, ConsistencyIssueType, ConsistencySeverity
"""

from T.Review import ReviewSeverity
from T.Review.Model.src.consistency_review import (
    ConsistencyReview,
    ConsistencyIssue,
    ConsistencyIssueType,
    ConsistencySeverity
)

# Re-export unified severity for convenience
# ConsistencySeverity is kept for backward compatibility, but ReviewSeverity is the unified version
__all__ = [
    "ConsistencyReview",
    "ConsistencyIssue",
    "ConsistencyIssueType",
    "ConsistencySeverity",
    "ReviewSeverity",
]
