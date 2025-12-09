"""PrismQ.T.Review.Script.Grammar - Script Grammar Review Module

AI-powered grammar validation for scripts (Stage 14 / MVP-014).
Comprehensive checking of grammar, punctuation, spelling, syntax, and tense
with line-by-line error detection and JSON output.

This module serves as a quality gate in the workflow:
- If PASSES: proceed to Stage 15 (Tone Review / MVP-015)
- If FAILS: return to Script Refinement (Stage 11) with detailed feedback

Usage:
    # For direct grammar checking:
    >>> from T.Review.Script.Grammar import review_script_grammar
    >>> review = review_script_grammar(script_text)
    >>> if review.passes:
    ...     print("Script passes grammar review")

    # For workflow processing:
    >>> from T.Review.Script.Grammar import ScriptGrammarReviewService
    >>> service = ScriptGrammarReviewService(connection)
    >>> result = service.process_oldest_story()
"""

from .grammar_review import (
    GrammarIssue,
    GrammarIssueType,
    GrammarReview,
    GrammarSeverity,
)
from .script_grammar_review import (
    ScriptGrammarChecker,
    get_grammar_feedback,
    review_script_grammar,
    review_script_grammar_to_json,
)
from .script_grammar_service import (
    DEFAULT_PASS_THRESHOLD,
    INPUT_STATE,
    OUTPUT_STATE_FAIL,
    OUTPUT_STATE_PASS,
    GrammarReviewResult,
    ScriptGrammarReviewService,
    process_oldest_grammar_review,
)

__all__ = [
    # Grammar model
    "GrammarReview",
    "GrammarIssue",
    "GrammarIssueType",
    "GrammarSeverity",
    # Grammar checker
    "ScriptGrammarChecker",
    "review_script_grammar",
    "review_script_grammar_to_json",
    "get_grammar_feedback",
    # Workflow service
    "ScriptGrammarReviewService",
    "GrammarReviewResult",
    "process_oldest_grammar_review",
    # Constants
    "INPUT_STATE",
    "OUTPUT_STATE_PASS",
    "OUTPUT_STATE_FAIL",
    "DEFAULT_PASS_THRESHOLD",
]
