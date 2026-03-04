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

import json
import logging
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

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

# Active AI model for Script 06 – qwen3:14b (override via PRISMQ_AI_MODEL_STAGE_05_06)
_AI_MODEL = os.getenv("PRISMQ_AI_MODEL_STAGE_05_06", "qwen3:14b")
_AI_TEMPERATURE = 0.3
_AI_MAX_TOKENS = 800
_AI_TIMEOUT = 120  # seconds
_MAX_CONTENT_PREVIEW_LENGTH = 3000  # Chars sent to AI; keeps prompt within token budget


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

    def __init__(self, connection: sqlite3.Connection):
        """Initialize the service with database connection.

        Args:
            connection: SQLite database connection
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.title_repo = TitleRepository(connection)
        self.content_repo = ContentRepository(connection)
        self.review_repo = ReviewRepository(connection)

    def _ai_review_content(
        self,
        content_text: str,
        title_text: str,
        idea_text: str,
    ) -> Tuple[str, int]:
        """Review content against title and idea using the AI model (Ollama).

        Always calls AI — no algorithmic fallback.  The model is selected
        via the PRISMQ_AI_MODEL_EARLY_STAGE environment variable.

        Args:
            content_text: The script/content to review
            title_text: The title to evaluate alignment against
            idea_text: The original idea for context

        Returns:
            Tuple of (review_text, review_score 0-100)

        Raises:
            RuntimeError: If Ollama is not available or the API call fails
        """
        try:
            import requests as _requests
        except ImportError as exc:
            raise RuntimeError("requests library not available; run: pip install requests") from exc

        prompt = (
            "You are a professional content reviewer for short-form storytelling video scripts.\n"
            "Review the following script on two criteria:\n"
            "1. How well it aligns with its title and the original idea (0-100)\n"
            "2. Whether it ends with a forced engagement prompt (comment below, swipe up, tag someone, "
            "hit subscribe, share this, let's build something, etc.)\n\n"
            f"TITLE: {title_text}\n\n"
            f"IDEA: {idea_text or 'Not provided'}\n\n"
            f"SCRIPT:\n{content_text[:_MAX_CONTENT_PREVIEW_LENGTH]}\n\n"
            "Scoring rules:\n"
            "- Start from alignment score (0-100)\n"
            "- If the script ends with ANY forced engagement prompt (calls to comment, swipe, tag, subscribe, share, "
            "or any instruction to the viewer to interact), subtract 40 points\n"
            "- The script should end with a natural story resolution — a reflection, truth, or quiet revelation\n\n"
            "Respond with a JSON object containing:\n"
            '  "overall_score": integer 0-100,\n'
            '  "feedback": one concise sentence of feedback\n'
            "JSON only, no other text."
        )

        try:
            check = _requests.get("http://localhost:11434/api/tags", timeout=5)
            if check.status_code != 200:
                raise RuntimeError(f"Ollama not available (status {check.status_code})")
        except _requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Ollama not reachable: {exc}") from exc

        try:
            response = _requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": _AI_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "think": False,
                    "options": {"temperature": _AI_TEMPERATURE, "num_predict": _AI_MAX_TOKENS},
                },
                timeout=_AI_TIMEOUT,
            )
            response.raise_for_status()
            raw = response.json().get("response", "").strip()
        except _requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Ollama API call failed: {exc}") from exc

        # Strip <think>...</think> blocks (Qwen3 thinking mode)
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

        # Parse JSON response
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError("No JSON in AI response")
            data = json.loads(match.group())
            score = max(0, min(100, int(data.get("overall_score", 50))))
            feedback = str(data.get("feedback", "AI review completed."))
        except Exception as exc:
            logger.warning(f"Failed to parse AI content review response: {exc}")
            raise RuntimeError(f"Could not parse AI review response: {exc}") from exc

        return feedback, score

    def _fetch_story_with_content(self):
        """Fetch the next story to process using priority ordering.

        Selection priority:
          1. Lowest title version (ASC) — fewest regen cycles first
          2. Highest last title review score (DESC) — pick story closest to threshold
          3. Oldest story (created_at ASC) as tiebreaker

        Returns:
            sqlite3.Row with story/title/content/idea fields, or None
        """
        cursor = self._conn.execute(
            """
            SELECT
                s.id          AS story_id,
                s.idea_id     AS idea_id,
                t.id          AS title_id,
                t.text        AS title_text,
                t.version     AS title_version,
                t.review_id   AS title_review_id,
                c.id          AS content_id,
                c.text        AS content_text,
                c.version     AS content_version,
                COALESCE(i.text, '') AS idea_text,
                COALESCE(r.score, 0) AS last_title_review_score
            FROM Story s
            INNER JOIN Title t
                ON t.story_id = s.id
                AND t.version = (SELECT MAX(t2.version) FROM Title t2 WHERE t2.story_id = s.id)
            INNER JOIN Content c
                ON c.story_id = s.id
                AND c.version = (SELECT MAX(c2.version) FROM Content c2 WHERE c2.story_id = s.id)
            LEFT JOIN Idea i ON i.id = s.idea_id
            LEFT JOIN Review r ON r.id = t.review_id
            WHERE s.state = ?
            ORDER BY t.version ASC, COALESCE(r.score, 0) DESC, s.created_at ASC
            LIMIT 1
            """,
            (self.INPUT_STATE,),
        )
        return cursor.fetchone()

    def process_oldest_story(self) -> ReviewContentFromTitleIdeaResult:
        """Process the oldest story in PrismQ.T.Review.Content.From.Title.Idea state.

        Returns:
            ReviewContentFromTitleIdeaResult with processing details
        """
        row = self._fetch_story_with_content()

        if not row:
            return ReviewContentFromTitleIdeaResult(
                success=True,
                story_id=None,
                error="No stories found in state"
            )

        result = ReviewContentFromTitleIdeaResult(success=False, story_id=row["story_id"])

        try:
            idea_text = row["idea_text"]

            # Perform AI review with title, content, and idea context (always AI — no fallback)
            review_text, review_score = self._ai_review_content(
                content_text=row["content_text"],
                title_text=row["title_text"],
                idea_text=idea_text,
            )

            # Create Review record
            review = Review(
                text=review_text,
                score=review_score,
                created_at=datetime.now()
            )
            review = self.review_repo.insert(review)
            result.review_id = review.id

            # Link review back to the content that was reviewed
            self._conn.execute(
                "UPDATE Content SET review_id = ? WHERE id = ?",
                (review.id, row["content_id"])
            )
            self._conn.commit()

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
            story = self.story_repo.find_by_id(row["story_id"])
            story.state = result.next_state
            self.story_repo.update(story)

            result.success = True
            logger.info(
                f"Story {row['story_id']}: Content review complete, "
                f"score={review_score}, accepted={result.accepted}"
            )

        except Exception as e:
            result.error = f"Processing failed: {str(e)}"
            logger.exception(f"Error processing story {row['story_id']}")

        return result
