"""PrismQ.T.Review.Script.Tone module.

This module provides script tone review functionality for the PrismQ workflow.
Stage 15 (MVP-015) in the iterative co-improvement workflow.

The ToneReview model enables:
- Emotional intensity evaluation
- Style alignment checking (dark, suspense, dramatic, etc.)
- Voice and POV consistency validation
- Tone appropriateness for content type
- Audience-specific tone tuning
- Feedback for script refinement
"""

from .tone_review import (
    ToneReview,
    ToneIssue,
    ToneIssueType,
    ToneSeverity
)

from T.Review.Script.Tone.src.review_script_tone import (
    ReviewResult,
    process_review_script_tone,
    process_all_pending_reviews,
    get_story_with_lowest_script_version,
    get_script_for_story,
    save_review,
    update_script_review_id,
    determine_next_state,
    create_review,
    evaluate_tone,
    ACCEPTANCE_THRESHOLD,
    STATE_REVIEW_SCRIPT_TONE,
    STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT,
    STATE_REVIEW_SCRIPT_EDITING,
)

__all__ = [
    # Tone model
    "ToneReview",
    "ToneIssue",
    "ToneIssueType",
    "ToneSeverity",
    # Workflow functions
    "ReviewResult",
    "process_review_script_tone",
    "process_all_pending_reviews",
    "get_story_with_lowest_script_version",
    "get_script_for_story",
    "save_review",
    "update_script_review_id",
    "determine_next_state",
    "create_review",
    "evaluate_tone",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_SCRIPT_TONE",
    "STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT",
    "STATE_REVIEW_SCRIPT_EDITING",
]
