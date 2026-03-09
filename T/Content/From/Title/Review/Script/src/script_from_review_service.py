"""PrismQ.T.Content.From.Content.Review.Title Service Module.

This module provides the service to process stories in the
PrismQ.T.Content.From.Content.Review.Title state by:
1. Selecting the next Story in this state (lowest version first, highest review score first)
2. Loading current title and content versions
3. Loading review data (score + feedback text) from the Review table
4. Generating improved content using local AI (Ollama)
5. Saving the new content version
6. Updating the Story state to the next workflow state

State Transitions:
    PrismQ.T.Content.From.Content.Review.Title -> PrismQ.T.Review.Content.From.Title
"""

import json
import logging
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Setup logging
logger = logging.getLogger(__name__)

# Prompt template directory
_PROMPTS_DIR = Path(__file__).parent.parent / "_meta" / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    return (_PROMPTS_DIR / filename).read_text(encoding="utf-8")

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

from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model.State.constants.state_names import StateNames

# AI model for content improvement — qwen3:32b for generation quality
_AI_MODEL = os.getenv("PRISMQ_AI_MODEL_CONTENT_IMPROVE", "qwen3:32b")
_AI_TEMPERATURE = 0.7
_AI_MAX_TOKENS = 2000
_AI_TIMEOUT = 180  # seconds — larger model needs more time
_MAX_CONTENT_PREVIEW_LENGTH = 3000


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


class ScriptFromReviewService:
    """Service for processing stories in the PrismQ.T.Content.From.Content.Review.Title state.

    Uses local AI (Ollama) to improve content based on review feedback:
    1. Finds the next story by priority (lowest content version, highest review score)
    2. Loads the current title, content, and review data
    3. Calls local AI to generate improved content addressing the review feedback
    4. Saves the new content version
    5. Updates the story state to REVIEW_CONTENT_FROM_TITLE
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

    def _ai_improve_content(
        self,
        content_text: str,
        title_text: str,
        review_text: str,
        review_score: int,
    ) -> str:
        """Improve content using local AI based on review feedback.

        Always calls AI — no algorithmic fallback.

        Args:
            content_text: The original script to improve
            title_text: The title
            review_text: Feedback from the previous review
            review_score: Score from the previous review (0-100)

        Returns:
            Improved content text

        Raises:
            RuntimeError: If Ollama is not available or the API call fails
        """
        try:
            import requests as _requests
        except ImportError as exc:
            raise RuntimeError("requests library not available; run: pip install requests") from exc

        template = _load_prompt("content_improvement.txt")
        prompt = template.format(
            title_text=title_text,
            review_score=review_score,
            review_text=review_text or "No specific feedback provided.",
            content_text=content_text[:_MAX_CONTENT_PREVIEW_LENGTH],
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
                    "options": {"temperature": _AI_TEMPERATURE, "num_predict": _AI_MAX_TOKENS, "num_ctx": 4096},
                },
                timeout=_AI_TIMEOUT,
            )
            response.raise_for_status()
            raw = response.json().get("response", "").strip()
        except _requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Ollama API call failed: {exc}") from exc

        # Strip <think>...</think> blocks (Qwen3 thinking mode)
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

        if not raw:
            raise RuntimeError("Ollama returned empty response")

        # Remove common prefixes that the model might add
        for prefix in ["SCRIPT:", "Script:", "Improved script:", "Improved Script:"]:
            if raw.lower().startswith(prefix.lower()):
                raw = raw[len(prefix):].strip()

        return raw

    def _fetch_next_story(self):
        """Fetch the next story to process using priority ordering.

        Selection priority:
          1. Lowest content version (ASC) — fewest regen cycles first
          2. Highest last content review score (DESC) — pick story closest to threshold
          3. Oldest story (created_at ASC) as tiebreaker

        Returns:
            sqlite3.Row with story/title/content/review fields, or None
        """
        cursor = self._conn.execute(
            """
            SELECT
                s.id          AS story_id,
                t.id          AS title_id,
                t.text        AS title_text,
                t.version     AS title_version,
                c.id          AS content_id,
                c.text        AS content_text,
                c.version     AS content_version,
                c.review_id   AS content_review_id,
                COALESCE(r.score, 0)  AS last_content_review_score,
                COALESCE(r.text, '')  AS last_content_review_text
            FROM Story s
            INNER JOIN Title t
                ON t.story_id = s.id
                AND t.version = (SELECT MAX(t2.version) FROM Title t2 WHERE t2.story_id = s.id)
            INNER JOIN Content c
                ON c.story_id = s.id
                AND c.version = (SELECT MAX(c2.version) FROM Content c2 WHERE c2.story_id = s.id)
            LEFT JOIN Review r ON r.id = c.review_id
            WHERE s.state = ?
            ORDER BY c.version ASC, COALESCE(r.score, 0) DESC, s.created_at ASC
            LIMIT 1
            """,
            (self.INPUT_STATE,),
        )
        return cursor.fetchone()

    def process_oldest_story(self) -> ContentImprovementResult:
        """Process the next story in CONTENT_FROM_CONTENT_REVIEW_TITLE state.

        Uses priority ordering: lowest content version ASC, highest content
        review score DESC, oldest story ASC.

        Returns:
            ContentImprovementResult with processing details
        """
        row = self._fetch_next_story()

        if not row:
            return ContentImprovementResult(
                success=True,
                story_id=None,
                error="No stories found in state",
            )

        result = ContentImprovementResult(success=False, story_id=row["story_id"])

        try:
            review_text = row["last_content_review_text"]
            review_score = row["last_content_review_score"]

            logger.info(
                f"Story {row['story_id']}: Improving content v{row['content_version']} "
                f"(review score={review_score})"
            )

            # Generate improved content using local AI
            improved_text = self._ai_improve_content(
                content_text=row["content_text"],
                title_text=row["title_text"],
                review_text=review_text,
                review_score=review_score,
            )

            new_version_num = row["content_version"] + 1

            # Save new content version
            new_content = Content(
                story_id=row["story_id"],
                version=new_version_num,
                text=improved_text,
                created_at=datetime.now(),
            )
            self.content_repo.insert(new_content)

            logger.info(
                f"Story {row['story_id']}: Content improved from "
                f"v{row['content_version']} to v{new_version_num}"
            )

            # Update story state
            story = self.story_repo.find_by_id(row["story_id"])
            story.state = self.OUTPUT_STATE
            self.story_repo.update(story)

            logger.info(f"Story {row['story_id']}: State updated to {self.OUTPUT_STATE}")

            result.success = True
            result.new_content_version = new_version_num
            result.new_state = self.OUTPUT_STATE

        except Exception as e:
            result.error = f"Unexpected error: {e}"
            logger.exception(f"Story {row['story_id']}: {result.error}")

        return result
