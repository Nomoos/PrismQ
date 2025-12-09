"""PrismQ.T.Review.Script.Editing - Script Editing Review Module

AI-powered editing validation for scripts (Stage 18 / MVP-018).
Comprehensive checking of clarity, flow, redundancy, structure, and transitions
with line-by-line improvement suggestions and JSON output.

This module serves as a quality gate in the workflow:
- If PASSES: proceed to Stage 19 (Title Readability / MVP-019)
- If FAILS: return to Script Refinement (Stage 11) with detailed feedback
"""

from .editing_review import (
    EditingIssue,
    EditingIssueType,
    EditingReview,
    EditingSeverity,
)
from .script_editing_review import (
    ScriptEditingChecker,
    get_editing_feedback,
    review_script_editing,
    review_script_editing_to_json,
)

__all__ = [
    # Editing Review Model
    "EditingReview",
    "EditingIssue",
    "EditingIssueType",
    "EditingSeverity",
    # Service
    "ScriptEditingChecker",
    "review_script_editing",
    "review_script_editing_to_json",
    "get_editing_feedback",
]
