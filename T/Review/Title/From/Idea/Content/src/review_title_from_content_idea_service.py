"""PrismQ.T.Review.Title.From.Content.Idea Service Module.

This module provides the service to process stories in the
PrismQ.T.Review.Title.From.Content.Idea state by:
1. Selecting the oldest Story in this state
2. Loading the associated Title, Content, and Idea objects
3. Running AI review of the title against content and idea context
4. Creating a Review record with text and score
5. Updating the Story state based on review result

State Transitions:
    - If review accepts title (score >= threshold) -> PrismQ.T.Review.Content.From.Title.Idea
    - If review does not accept title (score < threshold) -> PrismQ.T.Title.From.Title.Review.Content
"""

import logging
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

# Setup logging
logger = logging.getLogger(__name__)

# Setup paths for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_module_root = os.path.dirname(_current_dir)  # T/Review/Title/From/Idea/Content
_t_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_module_root)))))  # T
_repo_root = os.path.dirname(_t_root)

if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _t_root not in sys.path:
    sys.path.insert(0, _t_root)

from Model.Database.models.review import Review
from Model.Database.models.story import Story
from Model.Database.repositories.review_repository import ReviewRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.State.constants.state_names import StateNames

# Import the AI-powered title review function (always required — no algorithmic fallback)
try:
    from T.Review.Title.From.Content.Idea.review_title_from_content_idea import (
        review_title_from_content_idea,
    )
    REVIEW_AVAILABLE = True
except ImportError:
    REVIEW_AVAILABLE = False


# Score threshold for title acceptance
TITLE_ACCEPTANCE_THRESHOLD = 70  # Titles with score >= 70 are accepted
MAX_REVIEW_TEXT_LENGTH = 500  # Maximum characters stored in the Review table


@dataclass
class ReviewTitleFromContentIdeaResult:
    """Result of processing a story's title review with idea context.

    Attributes:
        success: Whether the review was processed successfully
        story_id: ID of the processed story
        review_id: ID of the created Review record
        score: Score assigned to the title
        text: Review feedback text
        next_state: The new state the story was transitioned to
        accepted: Whether the title was accepted
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
    title_text: Optional[str] = None


class ReviewTitleFromContentIdeaService:
    """Service for processing stories in the PrismQ.T.Review.Title.From.Content.Idea state.

    This service reviews titles against both content AND the original idea,
    providing more comprehensive evaluation than step 07 alone.
    """

    INPUT_STATE = StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA
    OUTPUT_STATE_PASS = StateNames.REVIEW_CONTENT_FROM_TITLE_IDEA
    OUTPUT_STATE_FAIL = StateNames.TITLE_FROM_TITLE_REVIEW_CONTENT

    def __init__(self, connection: sqlite3.Connection):
        """Initialize the service with database connection.

        Args:
            connection: SQLite database connection
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.review_repo = ReviewRepository(connection)

    def _fetch_story_with_content(self):
        """Fetch the oldest pending story with its latest title, content, and idea in one query.

        Uses a single SQL JOIN to select the oldest story in INPUT_STATE that
        already has both a Title and a Content record, avoiding follow-up round
        trips and skipping stories that are not yet ready to process.

        Returns:
            A sqlite3.Row with columns:
              story_id, idea_id, title_id, title_text, title_version,
              content_id, content_text, content_version, idea_text
            or None if no eligible story exists.
        """
        cursor = self._conn.execute(
            """
            SELECT
                s.id          AS story_id,
                s.idea_id     AS idea_id,
                t.id          AS title_id,
                t.text        AS title_text,
                t.version     AS title_version,
                c.id          AS content_id,
                c.text        AS content_text,
                c.version     AS content_version,
                COALESCE(i.text, '') AS idea_text
            FROM Story s
            INNER JOIN Title t
                ON t.story_id = s.id
                AND t.version = (
                    SELECT MAX(t2.version) FROM Title t2 WHERE t2.story_id = s.id
                )
            INNER JOIN Content c
                ON c.story_id = s.id
                AND c.version = (
                    SELECT MAX(c2.version) FROM Content c2 WHERE c2.story_id = s.id
                )
            LEFT JOIN Idea i ON i.id = s.idea_id
            WHERE s.state = ?
            ORDER BY s.created_at ASC
            LIMIT 1
            """,
            (self.INPUT_STATE,),
        )
        return cursor.fetchone()

    def _generate_review(
        self,
        title_text: str,
        content_text: str,
        idea_text: str,
        title_id: Optional[int] = None,
        content_id: Optional[int] = None,
    ) -> Tuple[str, int]:
        """Generate AI review text and score for a title against content and idea.

        Always calls the AI model (Ollama).  The active model is selected via
        the PRISMQ_AI_MODEL_EARLY_STAGE environment variable.  Raises
        RuntimeError if the review module or Ollama is unavailable — no
        algorithmic fallback is used.

        Args:
            title_text: The title to review
            content_text: The script/content text
            idea_text: The original idea text
            title_id: Optional title database ID
            content_id: Optional content database ID

        Returns:
            Tuple of (review_text, review_score)

        Raises:
            RuntimeError: If AI review is unavailable
        """
        if not REVIEW_AVAILABLE:
            raise RuntimeError(
                "AI title review module is not available. "
                "Ensure the T/Review/Title/From/Content/Idea package is installed."
            )

        review_result = review_title_from_content_idea(
            title_text=title_text,
            content_text=content_text,
            idea_summary=idea_text,
            title_id=str(title_id) if title_id is not None else None,
            content_id=str(content_id) if content_id is not None else None,
        )

        review_text = review_result.primary_concern or review_result.notes or "No review text"
        return review_text, review_result.overall_score

    def process_oldest_story(self) -> ReviewTitleFromContentIdeaResult:
        """Process the oldest story in PrismQ.T.Review.Title.From.Content.Idea state.

        Returns:
            ReviewTitleFromContentIdeaResult with processing details
        """
        row = self._fetch_story_with_content()

        if not row:
            return ReviewTitleFromContentIdeaResult(
                success=True,
                story_id=None,
                error="No stories found in state",
            )

        story_id = row["story_id"]
        result = ReviewTitleFromContentIdeaResult(success=False, story_id=story_id, title_text=row["title_text"])

        try:
            logger.info(
                f"Story {story_id}: reviewing title v{row['title_version']} "
                f"against content v{row['content_version']} and idea"
            )

            # Generate review using title + content + idea (all from the JOIN row)
            review_text, review_score = self._generate_review(
                title_text=row["title_text"],
                content_text=row["content_text"],
                idea_text=row["idea_text"],
                title_id=row["title_id"],
                content_id=row["content_id"],
            )

            result.text = review_text
            result.score = review_score

            # Save review record to database
            review = Review(
                text=review_text[:MAX_REVIEW_TEXT_LENGTH] if len(review_text) > MAX_REVIEW_TEXT_LENGTH else review_text,
                score=review_score,
                created_at=datetime.now(),
            )
            review = self.review_repo.insert(review)
            result.review_id = review.id

            # Determine next state based on score
            if review_score >= TITLE_ACCEPTANCE_THRESHOLD:
                result.accepted = True
                result.next_state = self.OUTPUT_STATE_PASS
            else:
                result.accepted = False
                result.next_state = self.OUTPUT_STATE_FAIL

            # Update story state
            story = Story(id=story_id, idea_id=row["idea_id"], state=self.INPUT_STATE)
            story.state = result.next_state
            self.story_repo.update(story)

            result.success = True
            logger.info(
                f"Story {story_id}: title review complete, "
                f"score={review_score}, accepted={result.accepted}, "
                f"next_state={result.next_state}"
            )

        except Exception as e:
            result.error = f"Processing failed: {str(e)}"
            logger.exception(f"Error processing story {story_id}")

        return result


__all__ = [
    "ReviewTitleFromContentIdeaService",
    "ReviewTitleFromContentIdeaResult",
    "TITLE_ACCEPTANCE_THRESHOLD",
]
