"""PrismQ.T.Content.From.Content.Review.Title Service Module.

This module provides the service to process stories in the
PrismQ.T.Content.From.Content.Review.Title state by:
1. Selecting the oldest Story in this state
2. Loading current title and content versions
3. Loading review data (from Review table via title/content review_id)
4. Generating improved content using ScriptImprover
5. Saving the new content version
6. Updating the Story state to the next workflow state

State Transitions:
    PrismQ.T.Content.From.Content.Review.Title -> PrismQ.T.Review.Content.From.Title
"""

import logging
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Setup logging
logger = logging.getLogger(__name__)

# Setup paths for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_module_root = os.path.dirname(_current_dir)  # T/Content/From/Title/Review/Script
_t_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_module_root))))
)  # T
_repo_root = os.path.dirname(_t_root)

if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _t_root not in sys.path:
    sys.path.insert(0, _t_root)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.Database.models.title import Title
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model.State.constants.state_names import StateNames

# Try to import ScriptImprover
try:
    from script_improver import ScriptImprover, ImprovedScript
    IMPROVER_AVAILABLE = True
except ImportError:
    IMPROVER_AVAILABLE = False

# Try to import review model classes for creating mock reviews
_review_content_path = os.path.join(_t_root, "Review", "Content")
_review_title_path = os.path.join(_t_root, "Review", "Title", "From", "Content", "Idea")

if _review_content_path not in sys.path:
    sys.path.insert(0, _review_content_path)
if _review_title_path not in sys.path:
    sys.path.insert(0, _review_title_path)

try:
    from script_review import (
        CategoryScore,
        ImprovementPoint,
        ReviewCategory,
        ScriptReview,
    )
    SCRIPT_REVIEW_AVAILABLE = True
except ImportError:
    SCRIPT_REVIEW_AVAILABLE = False


@dataclass
class ContentImprovementResult:
    """Result of processing a story's content improvement.

    Attributes:
        success: Whether the improvement was processed successfully
        story_id: ID of the processed story
        new_content_version: Version number of the new content
        new_state: The new state the story was transitioned to
        error: Error message if processing failed
    """

    success: bool
    story_id: Optional[int] = None
    new_content_version: Optional[int] = None
    new_state: Optional[str] = None
    error: Optional[str] = None


def _get_review_score(conn: sqlite3.Connection, review_id: Optional[int]) -> Optional[int]:
    """Get review score from Review table by review_id."""
    if review_id is None:
        return None
    try:
        cursor = conn.execute("SELECT score FROM Review WHERE id = ?", (review_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception:
        return None


def _create_mock_script_review(content: str, title: str, score: int = 65) -> Optional[object]:
    """Create a mock ScriptReview from simplified data."""
    if not SCRIPT_REVIEW_AVAILABLE:
        return None

    return ScriptReview(
        content_id="content-db",
        content_text=content,
        script_version="v1",
        overall_score=score,
        category_scores=[
            CategoryScore(
                category=ReviewCategory.STRUCTURE,
                score=score,
                reasoning="Review from database",
            )
        ],
        improvement_points=[
            ImprovementPoint(
                category=ReviewCategory.STRUCTURE,
                title="Improve structure",
                description="Content structure could better align with title",
                priority="medium",
                impact_score=score,
                suggested_fix="Improve opening to match title expectations",
            ),
            ImprovementPoint(
                category=ReviewCategory.CONTENT,
                title="Strengthen conclusion",
                description="The ending could be more impactful",
                priority="medium",
                impact_score=score,
                suggested_fix="Add a memorable closing statement",
            ),
        ],
        needs_major_revision=score < 60,
    )


class ScriptFromReviewService:
    """Service for processing stories in the PrismQ.T.Content.From.Content.Review.Title state.

    This service improves content based on review feedback:
    1. Finds the oldest story in CONTENT_FROM_CONTENT_REVIEW_TITLE state
    2. Loads the current title and content versions
    3. Retrieves review scores from Review table
    4. Generates improved content using ScriptImprover
    5. Saves the new content version
    6. Updates the story state to REVIEW_CONTENT_FROM_TITLE
    """

    INPUT_STATE = StateNames.CONTENT_FROM_CONTENT_REVIEW_TITLE
    OUTPUT_STATE = StateNames.REVIEW_CONTENT_FROM_TITLE

    def __init__(self, connection: sqlite3.Connection):
        """Initialize the service with database connection.

        Args:
            connection: SQLite database connection
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.title_repo = TitleRepository(connection)
        self.content_repo = ContentRepository(connection)

    def process_oldest_story(self) -> ContentImprovementResult:
        """Process the oldest story in CONTENT_FROM_CONTENT_REVIEW_TITLE state.

        Returns:
            ContentImprovementResult with processing details
        """
        stories = self.story_repo.find_by_state_ordered_by_created(
            self.INPUT_STATE, ascending=True
        )

        if not stories:
            return ContentImprovementResult(
                success=True,
                story_id=None,
                error="No stories found in state",
            )

        story = stories[0]
        return self._process_story(story)

    def _process_story(self, story: Story) -> ContentImprovementResult:
        """Process a single story: improve content and update state.

        Args:
            story: The Story to process

        Returns:
            ContentImprovementResult with processing outcome
        """
        logger.info(f"Processing story {story.id} in state {story.state}")
        result = ContentImprovementResult(success=False, story_id=story.id)

        try:
            # Get latest title
            title = self.title_repo.find_latest_version(story.id)
            if not title:
                result.error = "No title found for story"
                return result

            # Get latest content
            content = self.content_repo.find_latest_version(story.id)
            if not content:
                result.error = "No content found for story"
                return result

            if not IMPROVER_AVAILABLE:
                result.error = "ScriptImprover not available"
                return result

            if not SCRIPT_REVIEW_AVAILABLE:
                result.error = "Review model classes not available"
                return result

            # Get review score from Review table (via content review_id)
            content_score = _get_review_score(self._conn, content.review_id) or 65

            # Create review object from stored data
            script_review = _create_mock_script_review(content.text, title.text, content_score)

            if not script_review:
                result.error = "Could not create review object"
                return result

            # Generate improved content
            improver = ScriptImprover()
            improved = improver.improve_content(
                original_content=content.text,
                title_text=title.text,
                script_review=script_review,
                original_version_number=f"v{content.version}",
                new_version_number=f"v{content.version + 1}",
            )

            new_version_num = content.version + 1
            logger.info(
                f"Story {story.id}: Content improved from v{content.version} to v{new_version_num}"
            )

            # Save new content version
            new_content = Content(
                story_id=story.id,
                version=new_version_num,
                text=improved.new_version.text,
                created_at=datetime.now(),
            )
            self.content_repo.insert(new_content)

            # Update story state
            story.state = self.OUTPUT_STATE
            self.story_repo.update(story)
            logger.info(f"Story {story.id}: State updated to {self.OUTPUT_STATE}")

            result.success = True
            result.new_content_version = new_version_num
            result.new_state = self.OUTPUT_STATE
            return result

        except Exception as e:
            result.error = f"Unexpected error: {e}"
            logger.exception(f"Story {story.id}: {result.error}")
            return result
