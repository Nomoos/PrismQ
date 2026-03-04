"""PrismQ.T.Title.From.Title.Review.Content Service Module.

This module provides the service to process stories in the
PrismQ.T.Title.From.Title.Review.Content state by:
1. Selecting the oldest Story in this state
2. Loading current title and content versions
3. Loading review data (from Review table via title/content review_id)
4. Generating an improved title using TitleImprover
5. Saving the new title version
6. Updating the Story state to the next workflow state

State Transitions:
    PrismQ.T.Title.From.Title.Review.Content -> PrismQ.T.Content.From.Content.Review.Title
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
_module_root = os.path.dirname(_current_dir)  # T/Title/From/Title/Review/Script
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

# Try to import TitleImprover
try:
    from title_improver import TitleImprover, ImprovedTitle
    IMPROVER_AVAILABLE = True
except ImportError:
    IMPROVER_AVAILABLE = False

# Try to import review model classes for creating mock reviews
_review_title_path = os.path.join(_t_root, "Review", "Title", "From", "Content", "Idea")
_review_content_path = os.path.join(_t_root, "Review", "Content")
_idea_model_path = os.path.join(_t_root, "Idea", "Model", "src")

if _review_title_path not in sys.path:
    sys.path.insert(0, _review_title_path)
if _review_content_path not in sys.path:
    sys.path.insert(0, _review_content_path)
if _idea_model_path not in sys.path:
    sys.path.insert(0, _idea_model_path)

try:
    from title_review import (
        TitleCategoryScore,
        TitleImprovementPoint,
        TitleReview,
        TitleReviewCategory,
    )
    TITLE_REVIEW_AVAILABLE = True
except ImportError:
    TITLE_REVIEW_AVAILABLE = False

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
class TitleImprovementResult:
    """Result of processing a story's title improvement.

    Attributes:
        success: Whether the improvement was processed successfully
        story_id: ID of the processed story
        new_title_version: Version number of the new title
        new_state: The new state the story was transitioned to
        error: Error message if processing failed
    """

    success: bool
    story_id: Optional[int] = None
    new_title_version: Optional[int] = None
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


def _create_mock_title_review(title: str, content: str, score: int = 65) -> Optional[object]:
    """Create a mock TitleReview from simplified data."""
    if not TITLE_REVIEW_AVAILABLE:
        return None

    return TitleReview(
        title_id=f"title-db",
        title_text=title,
        title_version="v1",
        overall_score=score,
        category_scores=[
            TitleCategoryScore(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                score=score,
                reasoning="Review from database",
            )
        ],
        improvement_points=[
            TitleImprovementPoint(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                title="Improve script alignment",
                description="Title could better match script content",
                priority="medium",
                impact_score=score,
                suggested_fix="Align title more closely with content themes",
            )
        ],
        script_alignment_score=score,
        engagement_score=score,
        seo_score=score,
        length_score=80,
        key_content_elements=[],
        suggested_keywords=[],
    )


def _create_mock_script_review(content: str, title: str, score: int = 65) -> Optional[object]:
    """Create a mock ScriptReview from simplified data."""
    if not SCRIPT_REVIEW_AVAILABLE:
        return None

    return ScriptReview(
        content_id=f"content-db",
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
                description="Content structure could be improved",
                priority="medium",
                impact_score=score,
                suggested_fix="Improve opening and structure to match title",
            )
        ],
        needs_major_revision=score < 60,
    )


class TitleFromReviewService:
    """Service for processing stories in the PrismQ.T.Title.From.Title.Review.Content state.

    This service improves titles based on review feedback:
    1. Finds the oldest story in TITLE_FROM_TITLE_REVIEW_CONTENT state
    2. Loads the current title and content versions
    3. Retrieves review scores from Review table
    4. Generates an improved title using TitleImprover
    5. Saves the new title version
    6. Updates the story state to CONTENT_FROM_CONTENT_REVIEW_TITLE
    """

    INPUT_STATE = StateNames.TITLE_FROM_TITLE_REVIEW_CONTENT
    OUTPUT_STATE = StateNames.CONTENT_FROM_CONTENT_REVIEW_TITLE

    def __init__(self, connection: sqlite3.Connection):
        """Initialize the service with database connection.

        Args:
            connection: SQLite database connection
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.title_repo = TitleRepository(connection)
        self.content_repo = ContentRepository(connection)

    def _fetch_next_story(self):
        """Fetch the next story to process using priority ordering.

        Selection priority:
          1. Lowest title version (ASC) — fewest regen cycles first
          2. Highest last title review score (DESC) — pick story closest to threshold
          3. Oldest story (created_at ASC) as tiebreaker

        Returns:
            sqlite3.Row with story_id field, or None
        """
        cursor = self._conn.execute(
            """
            SELECT
                s.id          AS story_id,
                t.id          AS title_id,
                t.version     AS title_version,
                t.review_id   AS title_review_id,
                COALESCE(r.score, 0) AS last_title_review_score
            FROM Story s
            INNER JOIN Title t
                ON t.story_id = s.id
                AND t.version = (SELECT MAX(t2.version) FROM Title t2 WHERE t2.story_id = s.id)
            LEFT JOIN Review r ON r.id = t.review_id
            WHERE s.state = ?
            ORDER BY t.version ASC, COALESCE(r.score, 0) DESC, s.created_at ASC
            LIMIT 1
            """,
            (self.INPUT_STATE,),
        )
        return cursor.fetchone()

    def process_oldest_story(self) -> TitleImprovementResult:
        """Process the next story in TITLE_FROM_TITLE_REVIEW_CONTENT state.

        Uses priority ordering: lowest title version ASC, highest title
        review score DESC, oldest story ASC.

        Returns:
            TitleImprovementResult with processing details
        """
        row = self._fetch_next_story()

        if not row:
            return TitleImprovementResult(
                success=True,
                story_id=None,
                error="No stories found in state",
            )

        story = self.story_repo.find_by_id(row["story_id"])
        return self._process_story(story)

    def _process_story(self, story: Story) -> TitleImprovementResult:
        """Process a single story: improve title and update state.

        Args:
            story: The Story to process

        Returns:
            TitleImprovementResult with processing outcome
        """
        logger.info(f"Processing story {story.id} in state {story.state}")
        result = TitleImprovementResult(success=False, story_id=story.id)

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
                result.error = "TitleImprover not available"
                return result

            if not TITLE_REVIEW_AVAILABLE or not SCRIPT_REVIEW_AVAILABLE:
                result.error = "Review model classes not available"
                return result

            # Get review scores from Review table (via review_id on title/content)
            title_score = _get_review_score(self._conn, title.review_id) or 65
            content_score = _get_review_score(self._conn, content.review_id) or 65

            # Create review objects from stored data
            title_review = _create_mock_title_review(title.text, content.text, title_score)
            script_review = _create_mock_script_review(content.text, title.text, content_score)

            if not title_review or not script_review:
                result.error = "Could not create review objects"
                return result

            # Generate improved title
            improver = TitleImprover()
            improved = improver.improve_title(
                original_title=title.text,
                content_text=content.text,
                title_review=title_review,
                script_review=script_review,
                original_version_number=f"v{title.version}",
                new_version_number=f"v{title.version + 1}",
            )

            new_version_num = title.version + 1
            logger.info(
                f"Story {story.id}: Title improved from v{title.version} to v{new_version_num}"
            )

            # Save new title version
            new_title = Title(
                story_id=story.id,
                version=new_version_num,
                text=improved.new_version.text,
                created_at=datetime.now(),
            )
            self.title_repo.insert(new_title)

            # Update story state
            story.state = self.OUTPUT_STATE
            self.story_repo.update(story)
            logger.info(f"Story {story.id}: State updated to {self.OUTPUT_STATE}")

            result.success = True
            result.new_title_version = new_version_num
            result.new_state = self.OUTPUT_STATE
            return result

        except Exception as e:
            result.error = f"Unexpected error: {e}"
            logger.exception(f"Story {story.id}: {result.error}")
            return result
