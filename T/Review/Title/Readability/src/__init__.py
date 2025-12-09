"""PrismQ.T.Review.Title.Readability source module.

This module provides the title readability review workflow stage:
- Selects the Story with state 'PrismQ.T.Review.Title.Readability' that has
  the Content with the lowest current version number
- Evaluates the title for voiceover readability
- Outputs a Review model (text, score, created_at)
- Updates the Story state based on review acceptance

State Transitions:
- If review doesn't accept title → 'PrismQ.T.Content.From.Title.Review.Content'
- If review accepts title → 'PrismQ.T.Story.Review'
"""

from .review_title_readability import (
    ACCEPTANCE_THRESHOLD,
    STATE_REVIEW_TITLE_READABILITY,
    STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT,
    STATE_STORY_REVIEW,
    ReviewResult,
    create_review,
    determine_next_state,
    evaluate_title_readability,
    get_oldest_story_for_review,
    get_story_for_review,
    process_all_pending_reviews,
    process_review_title_readability,
)

__all__ = [
    "ReviewResult",
    "process_review_title_readability",
    "process_all_pending_reviews",
    "get_story_for_review",
    "get_oldest_story_for_review",
    "determine_next_state",
    "create_review",
    "evaluate_title_readability",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_TITLE_READABILITY",
    "STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT",
    "STATE_STORY_REVIEW",
]
