"""PrismQ.T.Review.Script.Readability - Script Readability Review Module

AI-powered voiceover readability validation for scripts (Stage 20 / MVP-020).
Comprehensive checking of natural flow, pronunciation, pacing, and spoken-word
suitability with detailed issue detection and JSON output.

This module serves as the final script quality gate in the workflow:
- If PASSES: proceed to Stage 21 (Expert Review / MVP-021)
- If FAILS: return to Script Refinement (Stage 11) with voiceover-focused feedback
"""

from .script_readability_review import (
    ReadabilityIssue,
    ReadabilityIssueType,
    ReadabilityReview,
    ReadabilitySeverity,
    ScriptReadabilityChecker,
    get_readability_feedback,
    review_script_readability,
    review_script_readability_to_json,
)

__all__ = [
    "ReadabilityReview",
    "ReadabilityIssue",
    "ReadabilityIssueType",
    "ReadabilitySeverity",
    "ScriptReadabilityChecker",
    "review_script_readability",
    "review_script_readability_to_json",
    "get_readability_feedback",
]
