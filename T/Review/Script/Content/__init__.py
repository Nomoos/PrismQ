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

# Direct imports to avoid circular import issue in parent package
import importlib.util
import os

# Load the module directly to avoid T.Review.Script package circular import
_current_dir = os.path.dirname(os.path.abspath(__file__))
_module_path = os.path.join(_current_dir, 'script_content_review.py')
_spec = importlib.util.spec_from_file_location('script_content_review', _module_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

# Export the classes and functions
ScriptContentReviewer = _module.ScriptContentReviewer
ContentReviewResult = _module.ContentReviewResult
review_oldest_story_content = _module.review_oldest_story_content

__all__ = [
    "ScriptContentReviewer",
    "ContentReviewResult",
    "review_oldest_story_content",
]
