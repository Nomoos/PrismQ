"""Step 18 — Story Review: Submit.

Reads all STORY_REVIEW stories and routes them to one of three review tracks:

  18.1 GPT    → STORY_REVIEW_GPT_PENDING    (OpenAI Batch)
  18.2 Claude → STORY_REVIEW_CLAUDE_PENDING (Anthropic Batch)
  18.3 Manual → STORY_REVIEW_MANUAL_PENDING (file-based, user fills in)

Only ONE mode is active per run (set via PRISMQ_REVIEW_MODE env var).
Default: gpt

Manual response file format (for step 19.3 poll):
    SCORE: <0-100>
    FEEDBACK: <one sentence>

Environment variables:
    PRISMQ_REVIEW_MODE   gpt | claude | manual   (default: gpt)
    PRISMQ_GPT_MODEL     model ID                (default: o4-mini)
    PRISMQ_MANUAL_DIR    path                    (default: C:/PrismQ/manual)
    OPENAI_API_KEY
    ANTHROPIC_API_KEY
"""

import json
import logging
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List

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
from T._shared.api.api_config import MAX_TOKENS_REVIEW, MAX_CONTENT_LENGTH
from T._shared.api.openai_batch_client import OpenAIBatchClient
from T._shared.db.story_batch_db import StoryBatch, StoryBatchDB, StoryBatchItem

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
INPUT_STATE = StateNames.STORY_REVIEW
OUTPUT_STATE_GPT    = StateNames.STORY_REVIEW_GPT_PENDING
OUTPUT_STATE_CLAUDE = StateNames.STORY_REVIEW_CLAUDE_PENDING
OUTPUT_STATE_MANUAL = StateNames.STORY_REVIEW_MANUAL_PENDING

REVIEW_MODE = os.getenv("PRISMQ_REVIEW_MODE", "gpt").lower()
MANUAL_DIR  = Path(os.getenv("PRISMQ_MANUAL_DIR", "C:/PrismQ/manual"))

_PROMPTS_DIR = _story_review_dir / "_meta" / "prompts"


def _load_prompt() -> str:
    return (_PROMPTS_DIR / "review_story_gpt.txt").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Fetch helper
# ---------------------------------------------------------------------------

def _fetch_review_stories(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    cursor = conn.execute(
        """
        SELECT
            s.id   AS story_id,
            t.text AS title_text,
            c.text AS content_text
        FROM Story s
        INNER JOIN Title t
            ON t.story_id = s.id
            AND t.version = (SELECT MAX(t2.version) FROM Title t2 WHERE t2.story_id = s.id)
        INNER JOIN Content c
            ON c.story_id = s.id
            AND c.version = (SELECT MAX(c2.version) FROM Content c2 WHERE c2.story_id = s.id)
        WHERE s.state = ?
        ORDER BY s.created_at ASC
        """,
        (INPUT_STATE,),
    )
    return cursor.fetchall()


def _update_story_state(conn: sqlite3.Connection, story_id: int, new_state: str) -> None:
    conn.execute(
        "UPDATE Story SET state = ?, updated_at = ? WHERE id = ?",
        (new_state, datetime.now().isoformat(), story_id),
    )


# ---------------------------------------------------------------------------
# 18.1 — GPT Batch submit
# ---------------------------------------------------------------------------

def submit_gpt(conn: sqlite3.Connection) -> dict:
    """Submit all STORY_REVIEW stories to OpenAI Batch API."""
    stories = _fetch_review_stories(conn)
    if not stories:
        return {"submitted": 0, "mode": "gpt", "skipped": "no stories in STORY_REVIEW state"}

    template = _load_prompt()
    client = OpenAIBatchClient()

    requests = []
    for row in stories:
        prompt = template.format(
            title_text=row["title_text"],
            content_text=(row["content_text"] or "")[:MAX_CONTENT_LENGTH],
        )
        requests.append(
            client.build_request(
                custom_id=f"story-{row['story_id']}-review",
                prompt=prompt,
                max_tokens=MAX_TOKENS_REVIEW,
            )
        )

    openai_batch_id = client.submit_batch(requests)

    batch_db = StoryBatchDB(conn)
    batch_record = batch_db.insert_batch(
        StoryBatch(
            openai_batch_id=openai_batch_id,
            step="review-gpt",
            story_count=len(stories),
            submitted_at=datetime.now(),
        )
    )
    batch_db.insert_items([
        StoryBatchItem(
            batch_id=batch_record.id,
            story_id=row["story_id"],
            custom_id=f"story-{row['story_id']}-review",
        )
        for row in stories
    ])

    for row in stories:
        _update_story_state(conn, row["story_id"], OUTPUT_STATE_GPT)
    conn.commit()

    return {"mode": "gpt", "submitted": len(stories), "openai_batch_id": openai_batch_id}


# ---------------------------------------------------------------------------
# 18.2 — Claude Batch submit
# ---------------------------------------------------------------------------

def submit_claude(conn: sqlite3.Connection) -> dict:
    """Submit all STORY_REVIEW stories to Anthropic Batch API."""
    try:
        from T._shared.api.claude_batch_client import ClaudeBatchClient
    except ImportError as exc:
        raise RuntimeError(f"ClaudeBatchClient not available: {exc}") from exc

    stories = _fetch_review_stories(conn)
    if not stories:
        return {"submitted": 0, "mode": "claude", "skipped": "no stories in STORY_REVIEW state"}

    template = _load_prompt()
    client = ClaudeBatchClient()

    requests = []
    for row in stories:
        prompt = template.format(
            title_text=row["title_text"],
            content_text=(row["content_text"] or "")[:MAX_CONTENT_LENGTH],
        )
        requests.append(
            client.build_request(
                custom_id=f"story-{row['story_id']}-review",
                prompt=prompt,
                max_tokens=MAX_TOKENS_REVIEW,
            )
        )

    anthropic_batch_id = client.submit_batch(requests)

    batch_db = StoryBatchDB(conn)
    batch_record = batch_db.insert_batch(
        StoryBatch(
            openai_batch_id=anthropic_batch_id,   # reusing field for anthropic ID
            step="review-claude",
            story_count=len(stories),
            submitted_at=datetime.now(),
        )
    )
    batch_db.insert_items([
        StoryBatchItem(
            batch_id=batch_record.id,
            story_id=row["story_id"],
            custom_id=f"story-{row['story_id']}-review",
        )
        for row in stories
    ])

    for row in stories:
        _update_story_state(conn, row["story_id"], OUTPUT_STATE_CLAUDE)
    conn.commit()

    return {"mode": "claude", "submitted": len(stories), "anthropic_batch_id": anthropic_batch_id}


# ---------------------------------------------------------------------------
# 18.3 — Manual file submit
# ---------------------------------------------------------------------------

def submit_manual(conn: sqlite3.Connection) -> dict:
    """Write review prompt files for all STORY_REVIEW stories."""
    stories = _fetch_review_stories(conn)
    if not stories:
        return {"submitted": 0, "mode": "manual", "skipped": "no stories in STORY_REVIEW state"}

    MANUAL_DIR.mkdir(parents=True, exist_ok=True)
    template = _load_prompt()
    written = 0

    for row in stories:
        input_file = MANUAL_DIR / f"{row['story_id']}_review.txt"
        if not input_file.exists():
            prompt = template.format(
                title_text=row["title_text"],
                content_text=(row["content_text"] or "")[:MAX_CONTENT_LENGTH],
            )
            header = (
                f"=== MANUAL REVIEW REQUEST — Story {row['story_id']} ===\n"
                f"Created: {datetime.now().isoformat()}\n\n"
                f"Review the story below, then create the response file:\n"
                f"  {MANUAL_DIR}/{row['story_id']}_review_done.txt\n\n"
                f"Response file format:\n"
                f"  SCORE: <integer 0-100>\n"
                f"  FEEDBACK: <one sentence summary>\n\n"
                f"{'=' * 60}\n\n"
            )
            input_file.write_text(header + prompt, encoding="utf-8")
            written += 1

        _update_story_state(conn, row["story_id"], OUTPUT_STATE_MANUAL)

    conn.commit()
    return {
        "mode": "manual",
        "submitted": len(stories),
        "files_written": written,
        "manual_dir": str(MANUAL_DIR),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(conn: sqlite3.Connection) -> dict:
    """Route to the active model based on PRISMQ_REVIEW_MODE env var."""
    if REVIEW_MODE == "claude":
        return submit_claude(conn)
    if REVIEW_MODE == "manual":
        return submit_manual(conn)
    return submit_gpt(conn)   # default


if __name__ == "__main__":
    import sqlite3 as _sqlite3
    logging.basicConfig(level=logging.INFO)
    db_path = os.getenv("PRISMQ_DB_PATH", "C:/PrismQ/db.s3db")
    conn = _sqlite3.connect(db_path)
    conn.row_factory = _sqlite3.Row
    result = run(conn)
    conn.close()
    print(json.dumps(result, indent=2))
