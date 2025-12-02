"""PrismQ.T.Review.Title.Readability source module.

This module provides the title readability review workflow stage:
- Selects the oldest Story with state 'PrismQ.T.Review.Title.Readability'
- Evaluates the title for voiceover readability
- Outputs a Review model (text, score, created_at)
- Updates the Story state based on review acceptance

State Transitions:
- If review doesn't accept title → 'PrismQ.T.Script.From.Title.Review.Script'
- If review accepts title → 'PrismQ.T.Story.Review'
"""

from .review_title_readability import (
    ReviewResult,
    process_review_title_readability,
    process_all_pending_reviews,
    get_oldest_story_for_review,
    determine_next_state,
    create_review,
    evaluate_title_readability,
    ACCEPTANCE_THRESHOLD,
    STATE_REVIEW_TITLE_READABILITY,
    STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT,
    STATE_STORY_REVIEW,
)

__all__ = [
    "ReviewResult",
    "process_review_title_readability",
    "process_all_pending_reviews",
    "get_oldest_story_for_review",
    "determine_next_state",
    "create_review",
    "evaluate_title_readability",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_TITLE_READABILITY",
    "STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT",
    "STATE_STORY_REVIEW",
]
