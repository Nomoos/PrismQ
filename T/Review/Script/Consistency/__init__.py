"""PrismQ.T.Review.Script.Consistency - Script Consistency Review Module

AI-powered consistency validation for scripts (Stage 17 / MVP-017).
Comprehensive checking of character names, timeline, locations, and internal
contradictions with detailed issue detection and JSON output.

This module serves as a quality gate in the workflow:
- If PASSES: proceed to Stage 18 (Editing Review / MVP-018)
- If FAILS: return to Script Refinement (Stage 11) with detailed feedback
"""

from .consistency_review import (
    ConsistencyReview,
    ConsistencyIssue,
    ConsistencyIssueType,
    ConsistencySeverity,
    ScriptConsistencyChecker,
    review_script_consistency,
    review_script_consistency_to_json,
    get_consistency_feedback
)

__all__ = [
    "ConsistencyReview",
    "ConsistencyIssue",
    "ConsistencyIssueType",
    "ConsistencySeverity",
    "ScriptConsistencyChecker",
    "review_script_consistency",
    "review_script_consistency_to_json",
    "get_consistency_feedback"
]
