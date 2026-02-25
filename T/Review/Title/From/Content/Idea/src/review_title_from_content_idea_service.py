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
    - If review rejects title (score < threshold) -> PrismQ.T.Title.From.Title.Review.Content
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
_module_root = os.path.dirname(_current_dir)  # T/Review/Title/From/Content/Idea
_t_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_module_root))))
)  # T
_repo_root = os.path.dirname(_t_root)

if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _t_root not in sys.path:
    sys.path.insert(0, _t_root)

from Model.Database.models.review import Review
from Model.Database.models.story import Story
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.review_repository import ReviewRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model.State.constants.state_names import StateNames

# Try to import the review function
try:
    from T.Review.Title.From.Content.Idea.by_content_and_idea import (
        review_title_by_content_and_idea,
    )

    REVIEW_AVAILABLE = True
except ImportError:
    REVIEW_AVAILABLE = False


# Score threshold for title acceptance
TITLE_ACCEPTANCE_THRESHOLD = 70  # Titles with score >= 70 are accepted


@dataclass
class ReviewTitleFromContentIdeaResult:
    """Result of processing a story's title review with content and idea context.

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


class ReviewTitleFromContentIdeaService:
    """Service for processing stories in the PrismQ.T.Review.Title.From.Content.Idea state.

    This service reviews the title against both the generated content (script)
    AND the original idea, providing comprehensive evaluation of title quality
    across the title-content-idea triad.

    Workflow position:
        Title v1 (from Idea) + Content v1 (from Idea+Title) + Idea
            -> AI Review (title vs content + idea)
            -> Pass: PrismQ.T.Review.Content.From.Title.Idea
            -> Fail: PrismQ.T.Title.From.Title.Review.Content
    """

    INPUT_STATE = StateNames.REVIEW_TITLE_FROM_CONTENT_IDEA
    OUTPUT_STATE_PASS = StateNames.REVIEW_CONTENT_FROM_TITLE_IDEA
    OUTPUT_STATE_FAIL = StateNames.TITLE_FROM_TITLE_REVIEW_CONTENT

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

    def _fetch_idea_text(self, idea_id: Optional[str]) -> str:
        """Fetch idea text from the shared database.

        Args:
            idea_id: The idea ID to look up

        Returns:
            Idea text, or empty string if not found
        """
        if not idea_id:
            return ""

        try:
            cursor = self._conn.execute(
                "SELECT text FROM Idea WHERE id = ?", (idea_id,)
            )
            row = cursor.fetchone()
            if row:
                return row[0] or ""
        except Exception as e:
            logger.warning(f"Could not fetch idea {idea_id}: {e}")

        return ""

    def _generate_review(
        self, title_text: str, content_text: str, idea_text: str,
        title_id: Optional[int] = None, content_id: Optional[int] = None,
        idea_id: Optional[str] = None,
    ) -> Tuple[str, int]:
        """Generate review text and score for a title against content and idea.

        Adds the title, content, and idea to the AI prompt template and
        evaluates the title based on all three inputs.

        Args:
            title_text: The title to review
            content_text: The script/content text
            idea_text: The original idea text
            title_id: Optional title database ID
            content_id: Optional content database ID
            idea_id: Optional idea database ID

        Returns:
            Tuple of (review_text, review_score)
        """
        if not REVIEW_AVAILABLE:
            return self._simple_review(title_text, content_text, idea_text)

        review_result = review_title_by_content_and_idea(
            title_text=title_text,
            content_text=content_text,
            idea_summary=idea_text,
            title_id=str(title_id) if title_id else None,
            content_id=str(content_id) if content_id else None,
            idea_id=str(idea_id) if idea_id else None,
        )

        review_text = self._format_review_text(review_result)
        return review_text, review_result.overall_score

    def _format_review_text(self, review_result) -> str:
        """Format review result into text feedback.

        Args:
            review_result: TitleReview object from the review module

        Returns:
            Formatted review text
        """
        parts = []

        if review_result.overall_score >= 80:
            parts.append("Title is well-aligned with content and idea.")
        elif review_result.overall_score >= 60:
            parts.append(
                "Title shows fair alignment with content and idea but has room for improvement."
            )
        else:
            parts.append("Title needs significant improvements to align with content and idea.")

        if review_result.script_alignment_score:
            parts.append(f"Content alignment: {review_result.script_alignment_score}%")

        if review_result.idea_alignment_score:
            parts.append(f"Idea alignment: {review_result.idea_alignment_score}%")

        if review_result.engagement_score:
            parts.append(f"Engagement score: {review_result.engagement_score}%")

        if hasattr(review_result, "improvement_points") and review_result.improvement_points:
            high_priority = [p for p in review_result.improvement_points if p.priority == "high"]
            if high_priority:
                parts.append("High priority improvements:")
                for point in high_priority[:3]:
                    parts.append(f"- {point.title}: {point.description}")

        return " ".join(parts)

    def _simple_review(
        self, title_text: str, content_text: str, idea_text: str
    ) -> Tuple[str, int]:
        """Simple fallback review when full module is not available.

        Args:
            title_text: Title text to review
            content_text: Content text to review against
            idea_text: Idea text for additional context

        Returns:
            Tuple of (review_text, review_score)
        """
        title_lower = title_text.lower()
        content_lower = content_text.lower()
        idea_lower = idea_text.lower()

        title_words = set(
            word for word in title_lower.split() if len(word) > 3 and word.isalpha()
        )

        content_matches = sum(1 for word in title_words if word in content_lower)
        idea_matches = sum(1 for word in title_words if word in idea_lower)

        if title_words:
            content_pct = (content_matches / len(title_words)) * 100
            idea_pct = (idea_matches / len(title_words)) * 100
        else:
            content_pct = 50
            idea_pct = 50

        score = int(min(100, 40 + content_pct * 0.4 + idea_pct * 0.2))

        if score >= 80:
            review_text = (
                f"Title aligns well with content and idea. "
                f"Content matches: {content_matches}/{len(title_words)}, "
                f"Idea matches: {idea_matches}/{len(title_words)}."
            )
        elif score >= 60:
            review_text = (
                f"Fair title alignment. "
                f"Content matches: {content_matches}/{len(title_words)}, "
                f"Idea matches: {idea_matches}/{len(title_words)}."
            )
        else:
            review_text = (
                f"Title needs improvement. "
                f"Content matches: {content_matches}/{len(title_words)}, "
                f"Idea matches: {idea_matches}/{len(title_words)}."
            )

        return review_text, score

    def process_oldest_story(self) -> ReviewTitleFromContentIdeaResult:
        """Process the oldest story in PrismQ.T.Review.Title.From.Content.Idea state.

        Returns:
            ReviewTitleFromContentIdeaResult with processing details
        """
        story = self.story_repo.find_oldest_by_state(self.INPUT_STATE)

        if not story:
            return ReviewTitleFromContentIdeaResult(
                success=True,
                story_id=None,
                error="No stories found in state",
            )

        result = ReviewTitleFromContentIdeaResult(success=False, story_id=story.id)

        try:
            # Load the latest title for this story
            title = self.title_repo.find_latest_version(story.id)
            if not title:
                result.error = f"No title found for story {story.id}"
                logger.error(result.error)
                return result

            # Load the latest content for this story
            content = self.content_repo.find_latest_version(story.id)
            if not content:
                result.error = f"No content found for story {story.id}"
                logger.error(result.error)
                return result

            # Load idea text from the shared database
            idea_text = self._fetch_idea_text(story.idea_id)

            logger.info(
                f"Story {story.id}: reviewing title v{title.version} "
                f"against content v{content.version} and idea"
            )

            # Generate AI review using title + content + idea prompt template
            review_text, review_score = self._generate_review(
                title_text=title.text,
                content_text=content.text,
                idea_text=idea_text,
                title_id=title.id,
                content_id=content.id,
                idea_id=story.idea_id,
            )

            result.text = review_text
            result.score = review_score

            # Save review record to database
            if not self._preview_mode:
                review = Review(
                    text=review_text[:500] if len(review_text) > 500 else review_text,
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
            if not self._preview_mode:
                story.state = result.next_state
                self.story_repo.update(story)

            result.success = True
            logger.info(
                f"Story {story.id}: title review complete, "
                f"score={review_score}, accepted={result.accepted}, "
                f"next_state={result.next_state}"
            )

        except Exception as e:
            result.error = f"Processing failed: {str(e)}"
            logger.exception(f"Error processing story {story.id}")

        return result


__all__ = [
    "ReviewTitleFromContentIdeaService",
    "ReviewTitleFromContentIdeaResult",
    "TITLE_ACCEPTANCE_THRESHOLD",
]
