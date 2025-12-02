"""PrismQ.T.Review.Grammar - AI Grammar Review Module

AI-powered grammar and syntax validation for script content.
Stage 14 (MVP-014) in the iterative co-improvement workflow.

DEPRECATED: This module is deprecated. Import from T.Review.Script.Grammar instead:
    from T.Review.Script.Grammar import GrammarReview, GrammarIssue, GrammarIssueType, GrammarSeverity
"""

from T.Review import ReviewSeverity
from T.Review.Script.Grammar import (
    GrammarReview,
    GrammarIssue,
    GrammarIssueType,
    GrammarSeverity
)

# Re-export unified severity for convenience
# GrammarSeverity is kept for backward compatibility, but ReviewSeverity is the unified version
__all__ = [
    "GrammarReview",
    "GrammarIssue",
    "GrammarIssueType",
    "GrammarSeverity",
    "ReviewSeverity",
]
