"""PrismQ.T.Review.Script.Editing.src - Script Editing Review Service Module.

This module implements the script editing review workflow service that:
1. Selects the oldest Story with state 'PrismQ.T.Review.Script.Editing'
2. Reviews the script for editing quality (clarity, flow, redundancy)
3. Creates a Review model with text and score
4. Updates the Story state based on review acceptance:
   - If review accepts → 'PrismQ.T.Review.Title.Readability'
   - If review doesn't accept → 'PrismQ.T.Script.From.Title.Review.Script'
"""

from .review_script_editing_service import (
    ReviewResult,
    process_review_script_editing,
    process_all_pending_reviews,
    get_oldest_story_for_review,
    determine_next_state,
    create_review,
    evaluate_script,
    ACCEPTANCE_THRESHOLD,
    STATE_REVIEW_SCRIPT_EDITING,
    STATE_SCRIPT_REFINEMENT,
    STATE_REVIEW_TITLE_READABILITY,
)

__all__ = [
    "ReviewResult",
    "process_review_script_editing",
    "process_all_pending_reviews",
    "get_oldest_story_for_review",
    "determine_next_state",
    "create_review",
    "evaluate_script",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_SCRIPT_EDITING",
    "STATE_SCRIPT_REFINEMENT",
    "STATE_REVIEW_TITLE_READABILITY",
]
