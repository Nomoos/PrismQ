"""Step 21 — Story Polish: Poll / retrieve results.

Input states:
  PrismQ.T.Story.Polish.GPT.Pending    (OpenAI Batch)
  PrismQ.T.Story.Polish.Claude.Pending (Anthropic Batch — future)
  PrismQ.T.Story.Polish.Manual.Pending (user response file)

Output state (all paths):
  PUBLISHING — always advances on success (or on GPT failure, with original content)

For batch mode: queries OpenAI Batch API, downloads results when ready.
                Saves new Title + Content versions from GPT polish.

For manual mode: checks for {story_id}_polish_done.txt file in MANUAL_DIR.

Manual response file format:
    TITLE: <improved title>
    CONTENT:
    <improved content — everything after the CONTENT: line>

Environment variables:
    PRISMQ_MANUAL_DIR   path   (default: C:/PrismQ/manual)
    OPENAI_API_KEY
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
_story_polish_dir = _src_dir.parent
_t_dir = _story_polish_dir.parent.parent
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
INPUT_STATE_GPT = StateNames.STORY_POLISH_GPT_PENDING
INPUT_STATE_MANUAL = StateNames.STORY_POLISH_MANUAL_PENDING
OUTPUT_STATE = StateNames.PUBLISHING

MANUAL_DIR = Path(os.getenv("PRISMQ_MANUAL_DIR", "C:/PrismQ/manual"))


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _update_story_state(conn: sqlite3.Connection, story_id: int, new_state: str) -> None:
    conn.execute(
        "UPDATE Story SET state = ?, updated_at = ? WHERE id = ?",
        (new_state, datetime.now().isoformat(), story_id),
    )


def _get_next_version(conn: sqlite3.Connection, table: str, story_id: int) -> int:
    row = conn.execute(
        f"SELECT COALESCE(MAX(version), 0) FROM {table} WHERE story_id = ?",
        (story_id,),
    ).fetchone()
    return (row[0] or 0) + 1


def _save_polished_title(conn: sqlite3.Connection, story_id: int, title_text: str) -> None:
    """Insert a new Title version with the polished text."""
    version = _get_next_version(conn, "Title", story_id)
    conn.execute(
        "INSERT INTO Title (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
        (story_id, title_text, version, datetime.now().isoformat()),
    )


def _save_polished_content(conn: sqlite3.Connection, story_id: int, content_text: str) -> None:
    """Insert a new Content version with the polished text."""
    version = _get_next_version(conn, "Content", story_id)
    conn.execute(
        "INSERT INTO Content (story_id, text, version, created_at) VALUES (?, ?, ?, ?)",
        (story_id, content_text, version, datetime.now().isoformat()),
    )


def _parse_polish_response(raw: str) -> Tuple[str, str, str]:
    """Parse {"title": ..., "content": ..., "changes": ...} from GPT response.

    Returns (title, content, changes).
    """
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in response: {raw[:200]}")
    data = json.loads(match.group())
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()
    changes = str(data.get("changes", "")).strip()
    if not title or not content:
        raise ValueError(f"title or content missing in response: {data}")
    return title, content, changes


def _advance_story(
    conn: sqlite3.Connection,
    story_id: int,
    title_text: str,
    content_text: str,
) -> None:
    """Save polished versions and advance to PUBLISHING."""
    _save_polished_title(conn, story_id, title_text)
    _save_polished_content(conn, story_id, content_text)
    _update_story_state(conn, story_id, OUTPUT_STATE)
    conn.commit()


# ---------------------------------------------------------------------------
# GPT batch poll
# ---------------------------------------------------------------------------

def _poll_gpt_batch(conn: sqlite3.Connection) -> dict:
    batch_db = StoryBatchDB(conn)
    active_batches = batch_db.find_active_batches("polish")

    if not active_batches:
        return {"mode": "gpt_batch", "batches_checked": 0}

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
                f"Polish batch {openai_batch_id}: {status} "
                f"({counts.get('completed', 0)}/{counts.get('total', 0)} done)"
            )
            continue

        if client.is_failed(status):
            # On polish batch failure, advance to PUBLISHING with original content
            items = batch_db.find_items_by_batch(batch_db_id)
            for item in items:
                _update_story_state(conn, item["story_id"], OUTPUT_STATE)
            conn.commit()
            batch_db.update_batch_status(
                batch_db_id, "failed",
                error=f"OpenAI batch status: {status} — stories advanced to PUBLISHING with original content"
            )
            logger.warning(
                f"Polish batch {openai_batch_id} failed, "
                f"stories advanced to PUBLISHING with original content"
            )
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
                    # Request failed — advance with original content
                    _update_story_state(conn, story_id, OUTPUT_STATE)
                    conn.commit()
                    logger.warning(f"Story {story_id}: no polish result, advanced with original content")
                    continue

                try:
                    title, content, changes = _parse_polish_response(raw)
                    _advance_story(conn, story_id, title, content)
                    batch_db.update_item_result(item["id"], raw)
                    processed_stories += 1
                    logger.info(f"Story {story_id}: polished → PUBLISHING. Changes: {changes}")
                except Exception as exc:
                    # Parse error — advance with original content
                    logger.error(f"Story {story_id}: polish parse failed: {exc}, advancing with original")
                    _update_story_state(conn, story_id, OUTPUT_STATE)
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
# Manual poll
# ---------------------------------------------------------------------------

def _poll_manual(conn: sqlite3.Connection) -> dict:
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
        done_file = MANUAL_DIR / f"{story_id}_polish_done.txt"

        if not done_file.exists():
            pending += 1
            continue

        try:
            text = done_file.read_text(encoding="utf-8").strip()

            title_match = re.search(r"TITLE\s*:\s*(.+)", text, re.IGNORECASE)
            content_match = re.search(r"CONTENT\s*:\s*\n(.*)", text, re.IGNORECASE | re.DOTALL)

            if not title_match:
                raise ValueError("TITLE not found in response file")
            if not content_match:
                raise ValueError("CONTENT not found in response file")

            title = title_match.group(1).strip()
            content = content_match.group(1).strip()

            _advance_story(conn, story_id, title, content)
            done_file.rename(done_file.with_suffix(".processed.txt"))
            processed += 1
            logger.info(f"Story {story_id}: manual polish → PUBLISHING")

        except Exception as exc:
            logger.error(f"Story {story_id}: failed to parse manual polish: {exc}")

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
    gpt_result = _poll_gpt_batch(conn)
    manual_result = _poll_manual(conn)
    return {"gpt_batch": gpt_result, "manual": manual_result}


if __name__ == "__main__":
    import sqlite3 as _sqlite3

    logging.basicConfig(level=logging.INFO)
    db_path = os.getenv("PRISMQ_DB_PATH", "C:/PrismQ/db.s3db")
    conn = _sqlite3.connect(db_path)
    conn.row_factory = _sqlite3.Row
    result = run(conn)
    conn.close()
    print(json.dumps(result, indent=2, default=str))
