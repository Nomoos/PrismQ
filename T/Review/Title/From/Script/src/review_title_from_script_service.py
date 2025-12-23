"""PrismQ.T.Review.Title.From.Content Service Module.

This module provides the service to process stories in the
PrismQ.T.Review.Title.From.Content state by:
1. Selecting the oldest Story in this state
2. Reviewing the title against the script
3. Creating a Review record with text and score
4. Updating the Story state based on review result

State Transitions:
    - If review accepts title (score >= threshold) -> PrismQ.T.Review.Content.From.Title
    - If review does not accept title (score < threshold) -> PrismQ.T.Title.From.Content.Review.Title
"""

import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

# Setup paths for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_module_root = os.path.dirname(_current_dir)  # T/Review/Title/From/Content
_t_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_module_root))))  # T
_repo_root = os.path.dirname(_t_root)

if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _t_root not in sys.path:
    sys.path.insert(0, _t_root)

from Model.Database.models.review import Review
from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.Database.models.title import Title
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model.State.constants.state_names import StateNames

# Try to import the review function
try:
    from T.Review.Title.From.Script.by_script_v2 import (
        SCORE_THRESHOLD_HIGH,
        review_title_by_content_v2,
    )

    REVIEW_AVAILABLE = True
except ImportError:
    REVIEW_AVAILABLE = False
    SCORE_THRESHOLD_HIGH = 80  # Default fallback


# Score threshold for title acceptance
TITLE_ACCEPTANCE_THRESHOLD = 70  # Titles with score >= 70 are accepted


@dataclass
class ReviewTitleFromScriptResult:
    """Result of processing a story's title review.

    Attributes:
        success: Whether the review was processed successfully
        story_id: ID of the processed story
        review_id: ID of the created Review record
        review_score: Score assigned to the title
        review_text: Review feedback text
        new_state: The new state the story was transitioned to
        title_accepted: Whether the title was accepted
        error_message: Error message if processing failed
    """

    success: bool
    story_id: Optional[int] = None
    review_id: Optional[int] = None
    review_score: Optional[int] = None
    review_text: Optional[str] = None
    new_state: Optional[str] = None
    title_accepted: Optional[bool] = None
    error_message: Optional[str] = None


class ReviewRepository:
    """SQLite repository for Review entities.

    Simple repository for inserting and retrieving Review records.
    """

    def __init__(self, connection: sqlite3.Connection):
        """Initialize with database connection."""
        self._conn = connection

    def insert(self, review: Review) -> Review:
        """Insert a new Review into the database.

        Args:
            review: Review entity to insert

        Returns:
            Review with populated id
        """
        cursor = self._conn.execute(
            "INSERT INTO Review (text, score, created_at) VALUES (?, ?, ?)",
            (review.text, review.score, review.created_at.isoformat()),
        )
        self._conn.commit()
        review.id = cursor.lastrowid
        return review

    def find_by_id(self, review_id: int) -> Optional[Review]:
        """Find a Review by ID.

        Args:
            review_id: The ID to search for

        Returns:
            Review if found, None otherwise
        """
        cursor = self._conn.execute(
            "SELECT id, text, score, created_at FROM Review WHERE id = ?", (review_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None

        created_at = row[3]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return Review(id=row[0], text=row[1], score=row[2], created_at=created_at)


class ReviewTitleFromScriptService:
    """Service for processing stories in the PrismQ.T.Review.Title.From.Content state.

    This service implements the workflow logic for reviewing titles against scripts:
    1. Finds the oldest story in the Review.Title.From.Content state
    2. Loads the associated title and script
    3. Performs title review analysis
    4. Creates a Review record
    5. Updates the story state based on review result

    Attributes:
        story_repo: Repository for Story operations
        title_repo: Repository for Title operations
        content_repo: Repository for Content operations
        review_repo: Repository for Review operations
    """

    # State names for transitions
    CURRENT_STATE = StateNames.REVIEW_TITLE_FROM_SCRIPT
    STATE_ON_ACCEPT = StateNames.REVIEW_SCRIPT_FROM_TITLE
    STATE_ON_REJECT = StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE

    def __init__(
        self,
        story_repo: StoryRepository,
        title_repo: TitleRepository,
        content_repo: ContentRepository,
        review_repo: ReviewRepository,
        acceptance_threshold: int = TITLE_ACCEPTANCE_THRESHOLD,
    ):
        """Initialize the service with repositories.

        Args:
            story_repo: Repository for Story operations
            title_repo: Repository for Title operations
            content_repo: Repository for Content operations
            review_repo: Repository for Review operations
            acceptance_threshold: Score threshold for accepting titles (default: 70)
        """
        self.story_repo = story_repo
        self.title_repo = title_repo
        self.content_repo = content_repo
        self.review_repo = review_repo
        self.acceptance_threshold = acceptance_threshold

    def find_oldest_story_to_process(self) -> Optional[Story]:
        """Find the oldest story in the Review.Title.From.Content state.

        Returns:
            Oldest Story in the current state, or None if none found
        """
        stories = self.story_repo.find_by_state_ordered_by_created(
            self.CURRENT_STATE, ascending=True
        )
        return stories[0] if stories else None

    def count_stories_to_process(self) -> int:
        """Count stories in the Review.Title.From.Content state.

        Returns:
            Number of stories waiting to be processed
        """
        return self.story_repo.count_by_state(self.CURRENT_STATE)

    def _generate_review(self, title: Title, script: Content) -> Tuple[str, int]:
        """Generate review text and score for a title against a script.

        Args:
            title: The Title to review
            script: The Content to review against

        Returns:
            Tuple of (review_text, review_score)
        """
        if REVIEW_AVAILABLE:
            # Use the full review module
            review_result = review_title_by_content_v2(
                title_text=title.text,
                content_text=script.text,
                title_id=str(title.id),
                content_id=str(script.id),
                title_version=f"v{title.version}",
                script_version=f"v{script.version}",
            )

            # Generate review text from the review result
            review_text = self._format_review_text(review_result)
            return review_text, review_result.overall_score
        else:
            # Fallback: simple keyword-based analysis
            return self._simple_review(title.text, script.text)

    def _format_review_text(self, review_result) -> str:
        """Format review result into text feedback.

        Args:
            review_result: TitleReview object from the review module

        Returns:
            Formatted review text
        """
        parts = []

        # Overall assessment
        if review_result.overall_score >= 80:
            parts.append("Title is well-aligned with the script content.")
        elif review_result.overall_score >= 60:
            parts.append("Title shows fair alignment with script but has room for improvement.")
        else:
            parts.append("Title needs significant improvements to align with script content.")

        # Add specific feedback
        if review_result.script_alignment_score:
            parts.append(f"Content alignment: {review_result.script_alignment_score}%")

        if review_result.engagement_score:
            parts.append(f"Engagement score: {review_result.engagement_score}%")

        # Add improvement recommendations if any
        if hasattr(review_result, "improvement_points") and review_result.improvement_points:
            high_priority = [p for p in review_result.improvement_points if p.priority == "high"]
            if high_priority:
                parts.append("High priority improvements:")
                for point in high_priority[:3]:
                    parts.append(f"- {point.title}: {point.description}")

        return " ".join(parts)

    def _simple_review(self, title_text: str, content_text: str) -> Tuple[str, int]:
        """Simple fallback review when full module is not available.

        Args:
            title_text: Title text to review
            content_text: Content text to review against

        Returns:
            Tuple of (review_text, review_score)
        """
        # Simple keyword matching
        title_lower = title_text.lower()
        script_lower = content_text.lower()

        # Extract simple keywords from title
        title_words = set(word for word in title_lower.split() if len(word) > 3 and word.isalpha())

        # Count how many title words appear in script
        matches = sum(1 for word in title_words if word in script_lower)

        # Calculate simple score
        if title_words:
            match_percentage = (matches / len(title_words)) * 100
        else:
            match_percentage = 50  # Default for empty title

        # Base score from matching
        score = int(min(100, 50 + match_percentage * 0.5))

        # Generate review text
        if score >= 80:
            review_text = (
                f"Title aligns well with script. {matches}/{len(title_words)} keywords match."
            )
        elif score >= 60:
            review_text = (
                f"Fair title-script alignment. {matches}/{len(title_words)} keywords found."
            )
        else:
            review_text = (
                f"Title needs improvement. Only {matches}/{len(title_words)} keywords match script."
            )

        return review_text, score

    def process_story(self, story: Story) -> ReviewTitleFromScriptResult:
        """Process a single story: review its title and update state.

        Args:
            story: The Story to process

        Returns:
            ReviewTitleFromScriptResult with processing outcome
        """
        # Validate story is in correct state
        if story.state != self.CURRENT_STATE:
            return ReviewTitleFromScriptResult(
                success=False,
                story_id=story.id,
                error_message=f"Story is in state '{story.state}', expected '{self.CURRENT_STATE}'",
            )

        # Get the latest title for the story
        title = self.title_repo.find_latest_version(story.id)
        if not title:
            return ReviewTitleFromScriptResult(
                success=False, story_id=story.id, error_message="No title found for story"
            )

        # Get the latest script for the story
        script = self.content_repo.find_latest_version(story.id)
        if not script:
            return ReviewTitleFromScriptResult(
                success=False, story_id=story.id, error_message="No script found for story"
            )

        # Generate the review
        review_text, review_score = self._generate_review(title, script)

        # Create and save the Review record
        review = Review(text=review_text, score=review_score, created_at=datetime.now())
        saved_review = self.review_repo.insert(review)

        # Determine next state based on score
        title_accepted = review_score >= self.acceptance_threshold
        new_state = self.STATE_ON_ACCEPT if title_accepted else self.STATE_ON_REJECT

        # Update story state
        story.state = new_state
        story.updated_at = datetime.now()
        self.story_repo.update(story)

        # Note: The review_id could be linked to Title via FK but Title uses
        # INSERT-only pattern (create new version instead of update). The review
        # result is stored separately and the story state tracks progression.
        # The StoryReview linking table could be used for formal linking if needed.

        return ReviewTitleFromScriptResult(
            success=True,
            story_id=story.id,
            review_id=saved_review.id,
            review_score=review_score,
            review_text=review_text,
            new_state=new_state,
            title_accepted=title_accepted,
        )

    def process_oldest_story(self) -> ReviewTitleFromScriptResult:
        """Process the oldest story in the Review.Title.From.Content state.

        Returns:
            ReviewTitleFromScriptResult with processing outcome
        """
        story = self.find_oldest_story_to_process()
        if not story:
            return ReviewTitleFromScriptResult(
                success=False, error_message=f"No stories found in state '{self.CURRENT_STATE}'"
            )

        return self.process_story(story)

    def process_all_stories(self, limit: Optional[int] = None) -> List[ReviewTitleFromScriptResult]:
        """Process all stories in the Review.Title.From.Content state.

        Args:
            limit: Optional maximum number of stories to process

        Returns:
            List of ReviewTitleFromScriptResult for each processed story
        """
        results = []
        stories = self.story_repo.find_by_state_ordered_by_created(
            self.CURRENT_STATE, ascending=True
        )

        if limit:
            stories = stories[:limit]

        for story in stories:
            result = self.process_story(story)
            results.append(result)

        return results


def create_review_table_sql() -> str:
    """Get SQL to create the Review table if it doesn't exist.

    Returns:
        SQL CREATE TABLE statement for Review
    """
    return """
    CREATE TABLE IF NOT EXISTS Review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    
    CREATE INDEX IF NOT EXISTS idx_review_score ON Review(score);
    """


__all__ = [
    "ReviewTitleFromScriptService",
    "ReviewTitleFromScriptResult",
    "ReviewRepository",
    "create_review_table_sql",
    "TITLE_ACCEPTANCE_THRESHOLD",
]
