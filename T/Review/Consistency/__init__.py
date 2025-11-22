"""PrismQ.T.Review.Consistency - Script consistency validation module.

This module provides AI-powered consistency review for script content, checking:
- Character name consistency
- Timeline alignment
- Location continuity
- Contradiction detection
- Repeated detail matching

Stage 17 (MVP-017): Consistency Review
"""

from .consistency_review import (
    ConsistencyReview,
    ConsistencyIssue,
    ConsistencyIssueType,
    ConsistencySeverity
)

__all__ = [
    "ConsistencyReview",
    "ConsistencyIssue",
    "ConsistencyIssueType",
    "ConsistencySeverity"
]
