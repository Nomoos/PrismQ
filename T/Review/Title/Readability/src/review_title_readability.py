"""Title Readability Review Service - AI-powered review for PrismQ.T.Review.Title.Readability.

Processes stories in REVIEW_TITLE_READABILITY state using local Ollama AI (qwen3:14b).
Reviews the TITLE (not the content) for clarity, catchiness, length, memorability.
On PASS → REVIEW_CONTENT_READABILITY
On FAIL → TITLE_FROM_TITLE_REVIEW_CONTENT (module 08 — soft title improvement)
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
from Model.Database.repositories.story_repository import StoryRepository
from Model import StateNames

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).parent.parent / "_meta" / "prompts"

INPUT_STATE = StateNames.REVIEW_TITLE_READABILITY
OUTPUT_STATE_PASS = StateNames.REVIEW_CONTENT_READABILITY
OUTPUT_STATE_FAIL = StateNames.TITLE_FROM_TITLE_REVIEW_CONTENT     # → modul 08 (soft title improvement)

_AI_MODEL = os.getenv("PRISMQ_AI_MODEL_REVIEW", "qwen3:14b")
_AI_TEMPERATURE = 0.3
_AI_MAX_TOKENS = 400
_AI_TIMEOUT = 120
_PASS_THRESHOLD = 90  # high bar — title must be visually compelling AND speakable


@dataclass
class TitleReadabilityResult:
    """Result of title readability review processing."""

    success: bool
    story_id: Optional[int] = None
    review_id: Optional[int] = None
    score: Optional[int] = None
    text: Optional[str] = None
    next_state: Optional[str] = None
    passes: Optional[bool] = None
    error: Optional[str] = None


class TitleReadabilityReviewService:
    """AI-powered title readability review service for PrismQ.T.Review.Title.Readability state.

    Calls local Ollama with qwen3:14b to evaluate title clarity, catchiness,
    appropriate length, memorability, and engagement.
    Review is linked to Title via Title.review_id FK.
    On PASS (score >= 75) → REVIEW_CONTENT_READABILITY
    On FAIL (score < 75)  → CONTENT_FROM_CONTENT_REVIEW_TITLE
    """

    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.review_repo = ReviewRepository(connection)

    def _ai_review(self, title_text: str) -> Tuple[str, int]:
        """Call Ollama for title readability review. Returns (feedback, score)."""
        try:
            import requests as _requests
        except ImportError as exc:
            raise RuntimeError("requests library not available; run: pip install requests") from exc

        template = (_PROMPTS_DIR / "review_title_readability.txt").read_text(encoding="utf-8")
        prompt = template.format(title_text=title_text)

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
        feedback = str(data.get("feedback", "AI title readability review completed."))

        return feedback, score

    def _fetch_story(self) -> Optional[sqlite3.Row]:
        """Fetch the next story to process with priority ordering (by title version)."""
        cursor = self._conn.execute(
            """
            SELECT
                s.id          AS story_id,
                t.id          AS title_id,
                t.text        AS title_text,
                t.version     AS title_version,
                COALESCE(r.score, 0) AS last_review_score
            FROM Story s
            INNER JOIN Title t
                ON t.story_id = s.id
                AND t.version = (SELECT MAX(t2.version) FROM Title t2 WHERE t2.story_id = s.id)
            LEFT JOIN Review r ON r.id = t.review_id
            WHERE s.state = ?
            ORDER BY t.version ASC, COALESCE(r.score, 0) DESC, s.created_at ASC
            LIMIT 1
            """,
            (INPUT_STATE,),
        )
        return cursor.fetchone()

    def process_oldest_story(self) -> TitleReadabilityResult:
        """Process the oldest story in REVIEW_TITLE_READABILITY state."""
        row = self._fetch_story()

        if not row:
            return TitleReadabilityResult(
                success=True, story_id=None, error="No stories found in state"
            )

        result = TitleReadabilityResult(success=False, story_id=row["story_id"])

        try:
            feedback, score = self._ai_review(title_text=row["title_text"])

            review = Review(text=feedback, score=score, created_at=datetime.now())
            review = self.review_repo.insert(review)
            result.review_id = review.id

            # Link review to Title via Title.review_id FK
            self._conn.execute(
                "UPDATE Title SET review_id = ? WHERE id = ?",
                (review.id, row["title_id"]),
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
                f"Story {row['story_id']}: title readability review complete, "
                f"score={score}, passes={result.passes}"
            )

        except Exception as e:
            result.error = f"Title readability review failed: {str(e)}"
            logger.exception(f"Error processing story {row['story_id']}")

        return result

    def count_pending(self) -> int:
        return self.story_repo.count_by_state(INPUT_STATE)


def process_review_title_readability(connection: sqlite3.Connection) -> TitleReadabilityResult:
    """Process the oldest story in PrismQ.T.Review.Title.Readability state.

    Args:
        connection: SQLite database connection with row_factory = sqlite3.Row

    Returns:
        TitleReadabilityResult with processing details.
    """
    service = TitleReadabilityReviewService(connection)
    return service.process_oldest_story()
