"""PrismQ.T.Review.Script.Editing.src - Script Editing Review Service Module.

This module implements the script editing review workflow service that:
1. Selects the Story with state 'PrismQ.T.Review.Script.Editing' that has
   the Script with the lowest current version number
2. Gets the Script associated with the Story
3. Reviews the Script for editing quality (clarity, flow, redundancy)
4. Creates a Review model and links it to the Script via review_id FK
5. Updates the Story state based on review acceptance:
   - If review accepts → 'PrismQ.T.Review.Title.Readability'
   - If review doesn't accept → 'PrismQ.T.Script.From.Title.Review.Script'

Selection Logic:
- Prioritizes Stories whose Scripts have fewer iterations (lowest max version)
- Stories with version 0 scripts are processed before those with version 1, etc.

The Review is linked to the Script via the Script.review_id FK field,
allowing tracking of which review was created for which script version.
"""

from .review_script_editing_service import (
    ACCEPTANCE_THRESHOLD,
    STATE_REVIEW_SCRIPT_EDITING,
    STATE_REVIEW_TITLE_READABILITY,
    STATE_SCRIPT_REFINEMENT,
    ReviewResult,
    create_review,
    determine_next_state,
    evaluate_script,
    get_oldest_story_for_review,
    get_story_with_lowest_script_version,
    process_all_pending_reviews,
    process_review_script_editing,
)

__all__ = [
    "ReviewResult",
    "process_review_script_editing",
    "process_all_pending_reviews",
    "get_oldest_story_for_review",
    "get_story_with_lowest_script_version",
    "determine_next_state",
    "create_review",
    "evaluate_script",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_SCRIPT_EDITING",
    "STATE_SCRIPT_REFINEMENT",
    "STATE_REVIEW_TITLE_READABILITY",
]
