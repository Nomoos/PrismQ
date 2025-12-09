"""PrismQ.T.Review.Content.Consistency - Content Consistency Review Module

AI-powered consistency validation for scripts (Stage 17 / MVP-017).
Comprehensive checking of character names, timeline, locations, and internal
contradictions with detailed issue detection and JSON output.

This module serves as a quality gate in the workflow:
- If PASSES: proceed to PrismQ.T.Review.Content.Content
- If FAILS: return to PrismQ.T.Content.From.Title.Review.Content with detailed feedback

Service Module (in src/):
- ScriptConsistencyReviewService: Process stories in PrismQ.T.Review.Content.Consistency state
- process_oldest_consistency_review: Process single oldest story
- process_all_consistency_reviews: Process all pending stories
"""

from T.Review.Content.Consistency.consistency_review import (
    ConsistencyIssue,
    ConsistencyIssueType,
    ConsistencyReview,
    ConsistencySeverity,
    ScriptConsistencyChecker,
    get_consistency_feedback,
    review_content_consistency,
    review_content_consistency_to_json,
)

__all__ = [
    # Review model and checker
    "ConsistencyReview",
    "ConsistencyIssue",
    "ConsistencyIssueType",
    "ConsistencySeverity",
    "ScriptConsistencyChecker",
    "review_content_consistency",
    "review_content_consistency_to_json",
    "get_consistency_feedback",
]
