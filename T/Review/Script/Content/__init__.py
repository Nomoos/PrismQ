"""PrismQ.T.Review.Script.Content - Script Content Review Service Module

AI-powered content review for scripts (Stage 12 in quality reviews).
Comprehensive checking of narrative coherence, plot logic, character motivation,
and pacing with detailed issue detection and JSON output.

This module serves as a quality gate in the workflow:
- If PASSES: proceed to PrismQ.T.Review.Script.Tone
- If FAILS: return to PrismQ.T.Script.From.Title.Review.Script

The service:
1. Selects the oldest Story where state is PrismQ.T.Review.Script.Content
2. Generates content review using ContentReview model
3. Creates Review record and links via StoryReview
4. Updates Story state based on review result
"""

from .content_review import (
    ContentIssue,
    ContentIssueType,
    ContentReview,
    ContentSeverity,
)
from .script_content_review import (
    ContentReviewResult,
    ScriptContentReviewer,
    review_oldest_story_content,
)

__all__ = [
    # Content Review Model
    "ContentReview",
    "ContentIssue",
    "ContentIssueType",
    "ContentSeverity",
    # Service
    "ScriptContentReviewer",
    "ContentReviewResult",
    "review_oldest_story_content",
]
