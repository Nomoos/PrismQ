"""Content Editing Review Service - AI-powered review for PrismQ.T.Review.Content.Editing.

Processes stories in REVIEW_CONTENT_EDITING state using local Ollama AI (qwen3:14b).
On PASS → REVIEW_TITLE_READABILITY
On FAIL → CONTENT_FROM_CONTENT_REVIEW_TITLE (step 09 — AI content regeneration)
"""

import json
import logging
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from Model.Database.models.review import Review
from Model.Database.repositories.review_repository import ReviewRepository
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model import StateNames

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).parent.parent / "_meta" / "prompts"

INPUT_STATE = StateNames.REVIEW_CONTENT_EDITING
OUTPUT_STATE_PASS = StateNames.REVIEW_TITLE_READABILITY
OUTPUT_STATE_FAIL = StateNames.CONTENT_FROM_CONTENT_REVIEW_TITLE

_AI_MODEL = os.getenv("PRISMQ_AI_MODEL_REVIEW", "qwen3:14b")
_AI_TEMPERATURE = 0.3
_AI_MAX_TOKENS = 400
_AI_TIMEOUT = 120
_PASS_THRESHOLD = 75
_MAX_CONTENT_PREVIEW_LENGTH = 3000


@dataclass
class EditingReviewResult:
    """Result of editing review processing."""

    success: bool
    story_id: Optional[int] = None
    review_id: Optional[int] = None
    score: Optional[int] = None
    text: Optional[str] = None
    next_state: Optional[str] = None
    passes: Optional[bool] = None
    error: Optional[str] = None


class ScriptEditingReviewService:
    """AI-powered editing review service for PrismQ.T.Review.Content.Editing state.

    Calls local Ollama with qwen3:14b to evaluate wordiness, clarity, flow,
    pacing, and transitions.
    On PASS (score >= 75) → REVIEW_TITLE_READABILITY
    On FAIL (score < 75)  → CONTENT_FROM_CONTENT_REVIEW_TITLE
    """

    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.content_repo = ContentRepository(connection)
        self.review_repo = ReviewRepository(connection)

    def _ai_review(self, content_text: str, title_text: str) -> Tuple[str, int]:
        """Call Ollama for editing review. Returns (feedback, score)."""
        try:
            import requests as _requests
        except ImportError as exc:
            raise RuntimeError("requests library not available; run: pip install requests") from exc

        template = (_PROMPTS_DIR / "review_editing.txt").read_text(encoding="utf-8")
        prompt = template.format(
            title_text=title_text,
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
                    "options": {"temperature": _AI_TEMPERATURE, "num_predict": _AI_MAX_TOKENS},
                },
                timeout=_AI_TIMEOUT,
            )
            response.raise_for_status()
            raw = response.json().get("response", "").strip()
        except _requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Ollama API call failed: {exc}") from exc

        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON in AI response: {raw[:200]}")
        data = json.loads(match.group())
        score = max(0, min(100, int(data.get("overall_score", 50))))
        feedback = str(data.get("feedback", "AI editing review completed."))

        return feedback, score

    def _fetch_story(self) -> Optional[sqlite3.Row]:
        """Fetch the next story to process with priority ordering."""
        cursor = self._conn.execute(
            """
            SELECT
                s.id          AS story_id,
                t.id          AS title_id,
                t.text        AS title_text,
                c.id          AS content_id,
                c.text        AS content_text,
                c.version     AS content_version,
                COALESCE(r.score, 0) AS last_review_score
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
            (INPUT_STATE,),
        )
        return cursor.fetchone()

    def process_oldest_story(self) -> EditingReviewResult:
        """Process the oldest story in REVIEW_CONTENT_EDITING state."""
        row = self._fetch_story()

        if not row:
            return EditingReviewResult(
                success=True, story_id=None, error="No stories found in state"
            )

        result = EditingReviewResult(success=False, story_id=row["story_id"])

        try:
            feedback, score = self._ai_review(
                content_text=row["content_text"],
                title_text=row["title_text"],
            )

            review = Review(text=feedback, score=score, created_at=datetime.now())
            review = self.review_repo.insert(review)
            result.review_id = review.id

            self._conn.execute(
                "UPDATE Content SET review_id = ? WHERE id = ?",
                (review.id, row["content_id"]),
            )
            self._conn.commit()

            result.text = feedback
            result.score = score
            result.passes = score >= _PASS_THRESHOLD
            result.next_state = OUTPUT_STATE_PASS if result.passes else OUTPUT_STATE_FAIL

            story = self.story_repo.find_by_id(row["story_id"])
            story.state = result.next_state
            self.story_repo.update(story)

            result.success = True
            logger.info(
                f"Story {row['story_id']}: editing review complete, "
                f"score={score}, passes={result.passes}"
            )

        except Exception as e:
            result.error = f"Editing review failed: {str(e)}"
            logger.exception(f"Error processing story {row['story_id']}")

        return result

    def count_pending(self) -> int:
        return self.story_repo.count_by_state(INPUT_STATE)


def process_review_content_editing(connection: sqlite3.Connection) -> EditingReviewResult:
    """Process the oldest story in PrismQ.T.Review.Content.Editing state.

    Args:
        connection: SQLite database connection with row_factory = sqlite3.Row

    Returns:
        EditingReviewResult with processing details.
    """
    service = ScriptEditingReviewService(connection)
    return service.process_oldest_story()
