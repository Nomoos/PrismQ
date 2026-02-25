"""PrismQ.T.Review.Content.From.Title.Idea Service Module.

This module provides the service to process stories in the
PrismQ.T.Review.Content.From.Title.Idea state by:
1. Selecting the oldest Story in this state
2. Reviewing the content against the title AND the original idea
3. Creating a Review record with text and score
4. Updating the Story state based on review result

This is similar to step 10 (Review.Content.From.Title) but with additional
Idea context for more comprehensive review.

State Transitions:
    - If review accepts content (score >= threshold) -> PrismQ.T.Review.Title.From.Content
    - If review does not accept content (score < threshold) -> PrismQ.T.Content.From.Content.Review.Title
"""

import logging
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

# Setup logging
logger = logging.getLogger(__name__)

# Setup paths for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_module_root = os.path.dirname(_current_dir)  # T/Review/Content/From/Title/Idea
_t_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_module_root)))))  # T
_repo_root = os.path.dirname(_t_root)
_review_content_dir = os.path.join(_t_root, "Review", "Content")

if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _t_root not in sys.path:
    sys.path.insert(0, _t_root)
if _review_content_dir not in sys.path:
    sys.path.insert(0, _review_content_dir)

from Model.Database.models.review import Review
from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.Database.models.title import Title
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model.State.constants.state_names import StateNames

# Try to import Idea database for fetching idea context
try:
    sys.path.insert(0, os.path.join(_repo_root, "src"))
    from idea import IdeaTable
    IDEA_DB_AVAILABLE = True
except ImportError:
    IDEA_DB_AVAILABLE = False

# Try to import the review function (direct import from T/Review/Content directory)
try:
    from T.Review.Content.review_content_from_title_idea import review_content_from_title_idea
    REVIEW_AVAILABLE = True
except ImportError:
    REVIEW_AVAILABLE = False


# Score threshold for content acceptance
CONTENT_ACCEPTANCE_THRESHOLD = 70  # Content with score >= 70 is accepted


@dataclass
class ReviewContentFromTitleIdeaResult:
    """Result of processing a story's content review with idea context.

    Attributes:
        success: Whether the review was processed successfully
        story_id: ID of the processed story
        review_id: ID of the created Review record
        score: Score assigned to the content
        text: Review feedback text
        next_state: The new state the story was transitioned to
        accepted: Whether the content was accepted
        error: Error message if processing failed
    """

    success: bool
    story_id: Optional[int] = None
    review_id: Optional[int] = None
    score: Optional[int] = None
    text: Optional[str] = None
    next_state: Optional[str] = None
    accepted: Optional[bool] = None
    error: Optional[str] = None


class ReviewRepository:
    """SQLite repository for Review entities."""

    def __init__(self, connection: sqlite3.Connection):
        """Initialize with database connection."""
        self._conn = connection

    def insert(self, review: Review) -> Review:
        """Insert a new Review into the database."""
        cursor = self._conn.execute(
            "INSERT INTO Review (text, score, created_at) VALUES (?, ?, ?)",
            (review.text, review.score, review.created_at.isoformat()),
        )
        self._conn.commit()
        review.id = cursor.lastrowid
        return review


class ReviewContentFromTitleIdeaService:
    """Service for processing stories in the PrismQ.T.Review.Content.From.Title.Idea state.

    This service reviews content against both title AND the original idea,
    providing more comprehensive evaluation than step 10 alone.
    """

    INPUT_STATE = "PrismQ.T.Review.Content.From.Title.Idea"
    OUTPUT_STATE_PASS = "PrismQ.T.Review.Title.From.Content"  # Step 06 pass
    OUTPUT_STATE_FAIL = "PrismQ.T.Content.From.Content.Review.Title"  # Step 06 fail -> regenerate content

    def __init__(self, connection: sqlite3.Connection, preview_mode: bool = False):
        """Initialize the service with database connection.

        Args:
            connection: SQLite database connection
            preview_mode: If True, don't save changes to database
        """
        self._conn = connection
        self._preview_mode = preview_mode
        self.story_repo = StoryRepository(connection)
        self.title_repo = TitleRepository(connection)
        self.content_repo = ContentRepository(connection)
        self.review_repo = ReviewRepository(connection)

    def process_oldest_story(self) -> ReviewContentFromTitleIdeaResult:
        """Process the oldest story in PrismQ.T.Review.Content.From.Title.Idea state.

        Returns:
            ReviewContentFromTitleIdeaResult with processing details
        """
        # Find oldest story in this state
        stories = self.story_repo.find_by_state_ordered_by_created(
            self.INPUT_STATE, ascending=True
        )

        if not stories:
            return ReviewContentFromTitleIdeaResult(
                success=True,
                story_id=None,
                error="No stories found in state"
            )

        story = stories[0]
        result = ReviewContentFromTitleIdeaResult(success=False, story_id=story.id)

        try:
            # Get latest title for the story
            title = self.title_repo.find_latest_version(story.id)
            if not title:
                result.error = "No title found for story"
                return result

            # Get latest content for the story
            content = self.content_repo.find_latest_version(story.id)
            if not content:
                result.error = "No content found for story"
                return result

            # Get idea context
            idea_text = ""
            if story.idea_id and IDEA_DB_AVAILABLE:
                try:
                    cursor = self._conn.execute("PRAGMA database_list")
                    db_file = cursor.fetchone()[2]

                    idea_db = IdeaTable(db_file)
                    idea_db.connect()
                    idea_data = idea_db.get_idea(story.idea_id)
                    if idea_data:
                        idea_text = idea_data.get("text", "")
                    idea_db.close()
                except Exception as e:
                    logger.warning(f"Could not fetch idea {story.idea_id}: {e}")

            # Perform review with title, content, and idea context
            if not REVIEW_AVAILABLE:
                result.error = "Review function not available"
                return result

            # Create a context object compatible with review_content_from_title_idea
            class _GenreContext:
                def __init__(self):
                    self.value = "other"

            class _IdeaContext:
                def __init__(self, text):
                    self.concept = text
                    self.title = text[:100] if text else ""
                    self.premise = text
                    self.hook = None
                    self.genre = _GenreContext()
                    self.target_audience = None
                    self.target_platforms = []
                    self.length_target = None
                    self.version = 1

            idea_obj = _IdeaContext(idea_text)

            # Review content against title and idea
            review_result = review_content_from_title_idea(
                content_text=content.text,
                title=title.text,
                idea=idea_obj,
                content_id=str(content.id) if content.id else None,
            )

            review_score = review_result.overall_score
            # Format review as human-readable text
            review_text = _format_review_text(review_result, title.text)

            # Create Review record
            if not self._preview_mode:
                review = Review(
                    text=review_text,
                    score=review_score,
                    created_at=datetime.now()
                )
                review = self.review_repo.insert(review)
                result.review_id = review.id

            result.text = review_text
            result.score = review_score

            # Determine next state based on score
            if review_score >= CONTENT_ACCEPTANCE_THRESHOLD:
                result.accepted = True
                result.next_state = self.OUTPUT_STATE_PASS
            else:
                result.accepted = False
                result.next_state = self.OUTPUT_STATE_FAIL

            # Update story state
            if not self._preview_mode:
                story.state = result.next_state
                self.story_repo.update(story)

            result.success = True
            logger.info(
                f"Story {story.id}: Content review complete, "
                f"score={review_score}, accepted={result.accepted}"
            )

        except Exception as e:
            result.error = f"Processing failed: {str(e)}"
            logger.exception(f"Error processing story {story.id}")

        return result


def _format_review_text(review_result, title: str) -> str:
    """Format a ScriptReview result as human-readable text.

    Args:
        review_result: ScriptReview object from review_content_from_title_idea
        title: The title being reviewed against

    Returns:
        Formatted review text suitable for database storage
    """
    lines = [
        f"CONTENT REVIEW: {title}",
        "=" * 60,
        f"OVERALL SCORE: {review_result.overall_score}%",
    ]

    if hasattr(review_result, "metadata") and review_result.metadata:
        if "title_alignment_score" in review_result.metadata:
            lines.append(f"Title Alignment: {review_result.metadata['title_alignment_score']}%")
        if "idea_alignment_score" in review_result.metadata:
            lines.append(f"Idea Alignment: {review_result.metadata['idea_alignment_score']}%")

    lines.append("")

    if review_result.overall_score >= CONTENT_ACCEPTANCE_THRESHOLD:
        lines.append("STATUS: Content accepted")
    else:
        lines.append("STATUS: Content needs revision")

    if hasattr(review_result, "primary_concern") and review_result.primary_concern:
        lines.append(f"PRIMARY CONCERN: {review_result.primary_concern}")

    if hasattr(review_result, "improvement_points") and review_result.improvement_points:
        lines.append("")
        lines.append("TOP IMPROVEMENTS:")
        for point in review_result.improvement_points[:3]:
            lines.append(f"  [{point.priority.upper()}] {point.title}: {point.description}")

    return "\n".join(lines)
