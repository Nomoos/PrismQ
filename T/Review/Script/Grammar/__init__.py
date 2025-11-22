"""PrismQ.T.Review.Script.Grammar - Script Grammar Review Module

AI-powered grammar validation for scripts (Stage 14 / MVP-014).
Comprehensive checking of grammar, punctuation, spelling, syntax, and tense
with line-by-line error detection and JSON output.

This module serves as a quality gate in the workflow:
- If PASSES: proceed to Stage 15 (Tone Review / MVP-015)
- If FAILS: return to Script Refinement (Stage 11) with detailed feedback
"""

from .script_grammar_review import (
    ScriptGrammarChecker,
    review_script_grammar,
    review_script_grammar_to_json,
    get_grammar_feedback
)

__all__ = [
    "ScriptGrammarChecker",
    "review_script_grammar",
    "review_script_grammar_to_json",
    "get_grammar_feedback"
]
