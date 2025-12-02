"""PrismQ.T.Review.Grammar - AI Grammar Review Module

AI-powered grammar and syntax validation for script content.
Stage 14 (MVP-014) in the iterative co-improvement workflow.
"""

from T.Review import ReviewSeverity
from .grammar_review import (
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
