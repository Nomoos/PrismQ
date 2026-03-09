"""Step 19 — Story Review: Poll / retrieve results.

Polls ALL three pending tracks simultaneously:

  19.1 STORY_REVIEW_GPT_PENDING    → OpenAI Batch results
  19.2 STORY_REVIEW_CLAUDE_PENDING → Anthropic Batch results
  19.3 STORY_REVIEW_MANUAL_PENDING → user response file

Output states:
  PASS (score >= PASS_THRESHOLD) : PrismQ.T.Story.Polish
  FAIL (score <  PASS_THRESHOLD) : PrismQ.T.Content.From.Content.Review.Title

Manual response file format:
    SCORE: <0-100>
    FEEDBACK: <one sentence>

Environment variables:
    PRISMQ_MANUAL_DIR              path   (default: C:/PrismQ/manual)
    PRISMQ_REVIEW_PASS_THRESHOLD   int    (default: 75)
    OPENAI_API_KEY
    ANTHROPIC_API_KEY
"""

import json
import logging
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_src_dir = Path(__file__).parent
_story_review_dir = _src_dir.parent
_t_dir = _story_review_dir.parent.parent
_repo_root = _t_dir.parent

for _p in [str(_repo_root), str(_t_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from Model.state import StateNames
from T._shared.api.openai_batch_client import OpenAIBatchClient
from T._shared.db.story_batch_db import StoryBatchDB

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
INPUT_STATE_GPT    = StateNames.STORY_REVIEW_GPT_PENDING
INPUT_STATE_CLAUDE = StateNames.STORY_REVIEW_CLAUDE_PENDING
INPUT_STATE_MANUAL = StateNames.STORY_REVIEW_MANUAL_PENDING
OUTPUT_STATE_PASS = StateNames.STORY_POLISH
OUTPUT_STATE_FAIL = StateNames.CONTENT_FROM_CONTENT_REVIEW_TITLE

PASS_THRESHOLD = int(os.getenv("PRISMQ_REVIEW_PASS_THRESHOLD", "75"))
MANUAL_DIR = Path(os.getenv("PRISMQ_MANUAL_DIR", "C:/PrismQ/manual"))


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _update_story_state(conn: sqlite3.Connection, story_id: int, new_state: str) -> None:
    conn.execute(
        "UPDATE Story SET state = ?, updated_at = ? WHERE id = ?",
        (new_state, datetime.now().isoformat(), story_id),
    )


def _insert_review(conn: sqlite3.Connection, story_id: int, content_id: Optional[int],
                   feedback: str, score: int) -> int:
    """Insert Review record and link it to the content, return review.id."""
    cursor = conn.execute(
        "INSERT INTO Review (text, score, created_at) VALUES (?, ?, ?)",
        (feedback, score, datetime.now().isoformat()),
    )
    review_id = cursor.lastrowid
    if content_id:
        conn.execute(
            "UPDATE Content SET review_id = ? WHERE id = ?",
            (review_id, content_id),
        )
    return review_id


def _get_latest_content_id(conn: sqlite3.Connection, story_id: int) -> Optional[int]:
    row = conn.execute(
        "SELECT id FROM Content WHERE story_id = ? ORDER BY version DESC LIMIT 1",
        (story_id,),
    ).fetchone()
    return row[0] if row else None


def _parse_json_response(raw: str) -> Tuple[str, int]:
    """Parse {"overall_score": N, "feedback": "..."} from GPT response.

    Returns (feedback, score).
    """
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in response: {raw[:200]}")
    data = json.loads(match.group())
    score = max(0, min(100, int(data.get("overall_score", 0))))
    feedback = str(data.get("feedback", "Review completed."))
    return feedback, score


def _advance_story(conn: sqlite3.Connection, story_id: int, feedback: str, score: int) -> str:
    """Create Review record, link to content, update story state. Returns next_state."""
    content_id = _get_latest_content_id(conn, story_id)
    _insert_review(conn, story_id, content_id, feedback, score)
    next_state = OUTPUT_STATE_PASS if score >= PASS_THRESHOLD else OUTPUT_STATE_FAIL
    _update_story_state(conn, story_id, next_state)
    conn.commit()
    return next_state


# ---------------------------------------------------------------------------
# Batch mode poll
# ---------------------------------------------------------------------------

def _poll_gpt_batch(conn: sqlite3.Connection) -> dict:
    """Check all pending OpenAI batches and process completed ones."""
    batch_db = StoryBatchDB(conn)
    active_batches = batch_db.find_active_batches("review-gpt")

    if not active_batches:
        return {"mode": "batch", "batches_checked": 0}

    client = OpenAIBatchClient()
    processed_stories = 0
    batches_completed = 0

    for batch_row in active_batches:
        batch_db_id = batch_row["id"]
        openai_batch_id = batch_row["openai_batch_id"]

        try:
            status_data = client.get_status(openai_batch_id)
            status = status_data.get("status", "")
        except Exception as exc:
            logger.warning(f"Failed to poll batch {openai_batch_id}: {exc}")
            continue

        if client.is_active(status):
            counts = status_data.get("request_counts", {})
            logger.info(
                f"Batch {openai_batch_id}: {status} "
                f"({counts.get('completed', 0)}/{counts.get('total', 0)} done)"
            )
            continue

        if client.is_failed(status):
            batch_db.update_batch_status(
                batch_db_id, "failed", error=f"OpenAI batch status: {status}"
            )
            # Move stories back to STORY_REVIEW for re-submit
            items = batch_db.find_items_by_batch(batch_db_id)
            for item in items:
                _update_story_state(conn, item["story_id"], StateNames.STORY_REVIEW)
            conn.commit()
            logger.warning(f"Batch {openai_batch_id} failed, stories reset to STORY_REVIEW")
            continue

        if client.is_done(status):
            output_file_id = status_data.get("output_file_id")
            if not output_file_id:
                logger.warning(f"Batch {openai_batch_id} completed but no output_file_id")
                continue

            results = client.retrieve_results(output_file_id)
            items = batch_db.find_items_by_batch(batch_db_id)

            for item in items:
                custom_id = item["custom_id"]
                story_id = item["story_id"]
                raw = results.get(custom_id)

                if raw is None:
                    # Request failed — reset story for retry
                    _update_story_state(conn, story_id, StateNames.STORY_REVIEW)
                    logger.warning(f"Story {story_id}: no result in batch, reset to STORY_REVIEW")
                    continue

                try:
                    feedback, score = _parse_json_response(raw)
                    next_state = _advance_story(conn, story_id, feedback, score)
                    batch_db.update_item_result(item["id"], raw)
                    processed_stories += 1
                    logger.info(f"Story {story_id}: score={score} → {next_state}")
                except Exception as exc:
                    logger.error(f"Story {story_id}: failed to process result: {exc}")
                    _update_story_state(conn, story_id, StateNames.STORY_REVIEW)
                    conn.commit()

            batch_db.update_batch_status(batch_db_id, "completed", output_file_id=output_file_id)
            batches_completed += 1

    return {
        "mode": "gpt_batch",
        "batches_checked": len(active_batches),
        "batches_completed": batches_completed,
        "stories_processed": processed_stories,
    }


# ---------------------------------------------------------------------------
# Manual mode poll
# ---------------------------------------------------------------------------

def _poll_claude_batch(conn: sqlite3.Connection) -> dict:
    """Check all pending Anthropic batches and process completed ones."""
    batch_db = StoryBatchDB(conn)
    active_batches = batch_db.find_active_batches("review-claude")

    if not active_batches:
        return {"mode": "claude_batch", "batches_checked": 0}

    try:
        from T._shared.api.claude_batch_client import ClaudeBatchClient
        client = ClaudeBatchClient()
    except Exception as exc:
        return {"mode": "claude_batch", "error": str(exc)}

    processed_stories = 0
    batches_completed = 0

    for batch_row in active_batches:
        batch_db_id = batch_row["id"]
        anthropic_batch_id = batch_row["openai_batch_id"]

        try:
            status_data = client.get_status(anthropic_batch_id)
            status = status_data.get("processing_status", "")
        except Exception as exc:
            logger.warning(f"Failed to poll Claude batch {anthropic_batch_id}: {exc}")
            continue

        if status in ("in_progress", "validating"):
            logger.info(f"Claude batch {anthropic_batch_id}: {status}")
            continue

        if status in ("errored", "expired", "canceled"):
            batch_db.update_batch_status(batch_db_id, "failed", error=f"status: {status}")
            items = batch_db.find_items_by_batch(batch_db_id)
            for item in items:
                _update_story_state(conn, item["story_id"], StateNames.STORY_REVIEW)
            conn.commit()
            logger.warning(f"Claude batch {anthropic_batch_id} {status}, stories reset")
            continue

        if status == "ended":
            results = client.retrieve_results(anthropic_batch_id)
            items = batch_db.find_items_by_batch(batch_db_id)

            for item in items:
                custom_id = item["custom_id"]
                story_id = item["story_id"]
                raw = results.get(custom_id)

                if raw is None:
                    _update_story_state(conn, story_id, StateNames.STORY_REVIEW)
                    logger.warning(f"Story {story_id}: no Claude result, reset to STORY_REVIEW")
                    continue

                try:
                    feedback, score = _parse_json_response(raw)
                    next_state = _advance_story(conn, story_id, feedback, score)
                    batch_db.update_item_result(item["id"], raw)
                    processed_stories += 1
                    logger.info(f"Story {story_id}: Claude score={score} → {next_state}")
                except Exception as exc:
                    logger.error(f"Story {story_id}: Claude result parse failed: {exc}")
                    _update_story_state(conn, story_id, StateNames.STORY_REVIEW)
                    conn.commit()

            batch_db.update_batch_status(batch_db_id, "completed")
            batches_completed += 1

    return {
        "mode": "claude_batch",
        "batches_checked": len(active_batches),
        "batches_completed": batches_completed,
        "stories_processed": processed_stories,
    }


def _poll_manual(conn: sqlite3.Connection) -> dict:
    """Check for completed manual review files."""
    cursor = conn.execute(
        "SELECT id FROM Story WHERE state = ?",
        (INPUT_STATE_MANUAL,),
    )
    stories = cursor.fetchall()
    if not stories:
        return {"mode": "manual", "stories_checked": 0}

    processed = 0
    pending = 0

    for row in stories:
        story_id = row[0]
        done_file = MANUAL_DIR / f"{story_id}_review_done.txt"

        if not done_file.exists():
            pending += 1
            continue

        try:
            text = done_file.read_text(encoding="utf-8").strip()
            # Parse: SCORE: 85 / FEEDBACK: one sentence
            score_match = re.search(r"SCORE\s*:\s*(\d+)", text, re.IGNORECASE)
            feedback_match = re.search(r"FEEDBACK\s*:\s*(.+)", text, re.IGNORECASE)

            if not score_match:
                raise ValueError("SCORE not found in response file")

            score = max(0, min(100, int(score_match.group(1))))
            feedback = feedback_match.group(1).strip() if feedback_match else "Manual review."

            next_state = _advance_story(conn, story_id, feedback, score)
            done_file.rename(done_file.with_suffix(".processed.txt"))
            processed += 1
            logger.info(f"Story {story_id}: manual review score={score} → {next_state}")

        except Exception as exc:
            logger.error(f"Story {story_id}: failed to parse manual response: {exc}")

    return {
        "mode": "manual",
        "stories_checked": len(stories),
        "stories_processed": processed,
        "stories_pending": pending,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(conn: sqlite3.Connection) -> dict:
    """Poll all pending tracks: GPT batch, Claude batch, manual files."""
    return {
        "gpt": _poll_gpt_batch(conn),
        "claude": _poll_claude_batch(conn),
        "manual": _poll_manual(conn),
    }


if __name__ == "__main__":
    import sqlite3 as _sqlite3

    logging.basicConfig(level=logging.INFO)
    db_path = os.getenv("PRISMQ_DB_PATH", "C:/PrismQ/db.s3db")
    conn = _sqlite3.connect(db_path)
    conn.row_factory = _sqlite3.Row
    result = run(conn)
    conn.close()
    print(json.dumps(result, indent=2, default=str))
