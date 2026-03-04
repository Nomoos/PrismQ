"""PrismQ.T.Review.Title.From.Content Service Module [07].

Processes stories in REVIEW_TITLE_FROM_CONTENT state using local Ollama AI (qwen3:14b).

On PASS  → REVIEW_CONTENT_FROM_TITLE [10]
On FAIL  → TITLE_FROM_TITLE_REVIEW_CONTENT [08] (soft title improvement)

Priority: c.version ASC, COALESCE(r.score,0) DESC, s.created_at ASC
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

# Setup paths for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_module_root = os.path.dirname(_current_dir)
_t_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_module_root))))
_repo_root = os.path.dirname(_t_root)

if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _t_root not in sys.path:
    sys.path.insert(0, _t_root)

from Model.Database.models.review import Review
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.review_repository import ReviewRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model import StateNames

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).parent.parent / "_meta" / "prompts"

INPUT_STATE       = StateNames.REVIEW_TITLE_FROM_CONTENT
OUTPUT_STATE_PASS = StateNames.REVIEW_CONTENT_FROM_TITLE        # → [10]
OUTPUT_STATE_FAIL = StateNames.TITLE_FROM_TITLE_REVIEW_CONTENT  # → [08]

_AI_MODEL       = os.getenv("PRISMQ_AI_MODEL_REVIEW", "qwen3:14b")
_AI_TEMPERATURE = 0.3
_AI_MAX_TOKENS  = 400
_AI_TIMEOUT     = 120
_PASS_THRESHOLD = 70
_MAX_CONTENT_PREVIEW_LENGTH = 3000

# Keep for external callers that check this constant
TITLE_ACCEPTANCE_THRESHOLD = _PASS_THRESHOLD


@dataclass
class ReviewTitleFromScriptResult:
    """Result of processing a story's title review."""

    success: bool
    story_id: Optional[int] = None
    review_id: Optional[int] = None
    review_score: Optional[int] = None
    review_text: Optional[str] = None
    new_state: Optional[str] = None
    title_accepted: Optional[bool] = None
    error_message: Optional[str] = None


from Model.Database.repositories.review_repository import ReviewRepository as ReviewRepository_impl


class ReviewTitleFromScriptService:
    """AI quality gate for PrismQ.T.Review.Title.From.Content [07].

    Calls Ollama to review the title against the content.
    PASS (score >= 70) → [10] REVIEW_CONTENT_FROM_TITLE
    FAIL              → [08] TITLE_FROM_TITLE_REVIEW_CONTENT
    """

    CURRENT_STATE  = INPUT_STATE
    STATE_ON_ACCEPT = OUTPUT_STATE_PASS
    STATE_ON_REJECT = OUTPUT_STATE_FAIL

    def __init__(self, connection: sqlite3.Connection, acceptance_threshold: int = _PASS_THRESHOLD):
        self._conn = connection
        self.story_repo   = StoryRepository(connection)
        self.title_repo   = TitleRepository(connection)
        self.content_repo = ContentRepository(connection)
        self.review_repo  = ReviewRepository_impl(connection)
        self.acceptance_threshold = acceptance_threshold

    # ── AI review ────────────────────────────────────────────────────────────

    def _ai_review(self, title_text: str, content_text: str) -> Tuple[str, int]:
        """Call Ollama for title quality review. Returns (feedback, score)."""
        try:
            import requests as _requests
        except ImportError as exc:
            raise RuntimeError("requests library not available; run: pip install requests") from exc

        template = (_PROMPTS_DIR / "review_title_from_content.txt").read_text(encoding="utf-8")
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
        feedback = str(data.get("feedback", "AI title review completed."))

        return feedback, score

    # ── story fetch ───────────────────────────────────────────────────────────

    def _fetch_story_with_content(self):
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
                COALESCE(r.score, 0) AS last_content_review_score
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

    # ── public API ────────────────────────────────────────────────────────────

    def count_stories_to_process(self) -> int:
        return self.story_repo.count_by_state(INPUT_STATE)

    def process_oldest_story(self) -> ReviewTitleFromScriptResult:
        """Process the next story in REVIEW_TITLE_FROM_CONTENT state."""
        row = self._fetch_story_with_content()
        if not row:
            return ReviewTitleFromScriptResult(
                success=False, error_message=f"No stories found in state '{INPUT_STATE}'"
            )

        story_id = row["story_id"]
        result = ReviewTitleFromScriptResult(success=False, story_id=story_id)

        try:
            feedback, score = self._ai_review(
                title_text=row["title_text"],
                content_text=row["content_text"],
            )

            review = Review(text=feedback, score=score, created_at=datetime.now())
            review = self.review_repo.insert(review)
            result.review_id = review.id

            self._conn.execute(
                "UPDATE Title SET review_id = ? WHERE id = ?",
                (review.id, row["title_id"]),
            )
            self._conn.commit()

            title_accepted = score >= self.acceptance_threshold
            new_state = OUTPUT_STATE_PASS if title_accepted else OUTPUT_STATE_FAIL

            story = self.story_repo.find_by_id(story_id)
            story.state = new_state
            self.story_repo.update(story)

            result.review_score  = score
            result.review_text   = feedback
            result.title_accepted = title_accepted
            result.new_state     = new_state
            result.success       = True

            logger.info(
                f"Story {story_id}: title review complete, "
                f"score={score}, accepted={title_accepted}, next={new_state}"
            )

        except Exception as e:
            result.error_message = f"Title review failed: {str(e)}"
            logger.exception(f"Error processing story {story_id}")

        return result


__all__ = [
    "ReviewTitleFromScriptService",
    "ReviewTitleFromScriptResult",
    "TITLE_ACCEPTANCE_THRESHOLD",
]
