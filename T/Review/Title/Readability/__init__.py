"""PrismQ.T.Review.Title.Readability - Title Readability Review Module.

This module implements the title readability review workflow stage (MVP-019).
Reviews titles for voiceover suitability including:
- Clarity and length appropriateness
- Pronunciation difficulty
- Natural rhythm and flow
- Engagement elements

Workflow Position:
    Stage 14: Title Readability Review
    Story (state=PrismQ.T.Review.Title.Readability) → Review → State Transition

Selection Logic:
    Selects the Story that has the Script with the lowest current version number
    (where "current version" is the highest version for a given story_id).
    This ensures stories with less refined scripts are processed first.

State Transitions:
- If review doesn't accept title → 'PrismQ.T.Script.From.Title.Review.Script' (refinement)
- If review accepts title → 'PrismQ.T.Story.Review' (next stage)

Output:
    Review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        score INTEGER CHECK (score >= 0 AND score <= 100),
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )

Usage:
    from T.Review.Title.Readability.src import (
        process_review_title_readability,
        ReviewResult
    )
    
    result = process_review_title_readability(db_connection)
    if result:
        print(f"Score: {result.review.score}")
        print(f"Accepted: {result.accepted}")
        print(f"New state: {result.new_state}")
"""

from .title_readability_review import (
    TitleReadabilityReview,
    ReadabilityIssue,
    ReadabilityIssueType,
    ReadabilitySeverity
)

from .src import (
    ReviewResult,
    process_review_title_readability,
    process_all_pending_reviews,
    get_story_for_review,
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
    # Readability model
    "TitleReadabilityReview",
    "ReadabilityIssue",
    "ReadabilityIssueType",
    "ReadabilitySeverity",
    # Workflow functions
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
