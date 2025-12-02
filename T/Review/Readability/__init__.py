"""PrismQ.T.Review.Title.Readability - AI Title Readability Review Module

AI-powered readability validation for title voiceover suitability.
Stage 19 (MVP-019) in the iterative co-improvement workflow.

This is the FINAL review stage for titles - focused 100% on spoken-word
suitability, voiceover flow, natural rhythm, and listening clarity.
"""

from T.Review import ReviewSeverity
from .title_readability_review import (
    TitleReadabilityReview,
    ReadabilityIssue,
    ReadabilityIssueType,
    ReadabilitySeverity
)

# Re-export unified severity for convenience
# ReadabilitySeverity is kept for backward compatibility, but ReviewSeverity is the unified version
__all__ = [
    "TitleReadabilityReview",
    "ReadabilityIssue",
    "ReadabilityIssueType",
    "ReadabilitySeverity",
    "ReviewSeverity",
]
