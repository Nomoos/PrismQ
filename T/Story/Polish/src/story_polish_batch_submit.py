"""Step 20 — Story Polish: Submit.

Reads all STORY_POLISH stories and routes them to one of three polish tracks:

  20.1 GPT    → STORY_POLISH_GPT_PENDING    (OpenAI Batch)
  20.2 Claude → STORY_POLISH_CLAUDE_PENDING (Anthropic Batch)
  20.3 Manual → STORY_POLISH_MANUAL_PENDING (file-based, user writes improved story)

Only ONE mode is active per run (PRISMQ_REVIEW_MODE env var). Default: gpt

Manual response file format (for step 21.3 poll):
    TITLE: <improved title>
    CONTENT:
    <improved content — all text after the CONTENT: line>

Environment variables:
    PRISMQ_REVIEW_MODE   gpt | claude | manual   (default: gpt)
    PRISMQ_GPT_MODEL
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
_story_polish_dir = _src_dir.parent
_t_dir = _story_polish_dir.parent.parent
_repo_root = _t_dir.parent

for _p in [str(_repo_root), str(_t_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from Model.state import StateNames
from T._shared.api.api_config import MAX_TOKENS_POLISH, MAX_CONTENT_LENGTH
from T._shared.api.openai_batch_client import OpenAIBatchClient
from T._shared.db.story_batch_db import StoryBatch, StoryBatchDB, StoryBatchItem

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
INPUT_STATE = StateNames.STORY_POLISH
OUTPUT_STATE_GPT    = StateNames.STORY_POLISH_GPT_PENDING
OUTPUT_STATE_CLAUDE = StateNames.STORY_POLISH_CLAUDE_PENDING
OUTPUT_STATE_MANUAL = StateNames.STORY_POLISH_MANUAL_PENDING

REVIEW_MODE = os.getenv("PRISMQ_REVIEW_MODE", "gpt").lower()
MANUAL_DIR  = Path(os.getenv("PRISMQ_MANUAL_DIR", "C:/PrismQ/manual"))

_PROMPTS_DIR = _story_polish_dir / "_meta" / "prompts"


def _load_prompt() -> str:
    return (_PROMPTS_DIR / "polish_story_gpt.txt").read_text(encoding="utf-8")


def _fetch_polish_stories(conn: sqlite3.Connection) -> List[sqlite3.Row]:
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
# 20.1 — GPT Batch submit
# ---------------------------------------------------------------------------

def submit_gpt(conn: sqlite3.Connection) -> dict:
    stories = _fetch_polish_stories(conn)
    if not stories:
        return {"submitted": 0, "mode": "gpt", "skipped": "no stories in STORY_POLISH state"}

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
                custom_id=f"story-{row['story_id']}-polish",
                prompt=prompt,
                max_tokens=MAX_TOKENS_POLISH,
            )
        )

    openai_batch_id = client.submit_batch(requests)

    batch_db = StoryBatchDB(conn)
    batch_record = batch_db.insert_batch(
        StoryBatch(
            openai_batch_id=openai_batch_id,
            step="polish-gpt",
            story_count=len(stories),
            submitted_at=datetime.now(),
        )
    )
    batch_db.insert_items([
        StoryBatchItem(
            batch_id=batch_record.id,
            story_id=row["story_id"],
            custom_id=f"story-{row['story_id']}-polish",
        )
        for row in stories
    ])

    for row in stories:
        _update_story_state(conn, row["story_id"], OUTPUT_STATE_GPT)
    conn.commit()

    return {"mode": "gpt", "submitted": len(stories), "openai_batch_id": openai_batch_id}


# ---------------------------------------------------------------------------
# 20.2 — Claude Batch submit
# ---------------------------------------------------------------------------

def submit_claude(conn: sqlite3.Connection) -> dict:
    try:
        from T._shared.api.claude_batch_client import ClaudeBatchClient
    except ImportError as exc:
        raise RuntimeError(f"ClaudeBatchClient not available: {exc}") from exc

    stories = _fetch_polish_stories(conn)
    if not stories:
        return {"submitted": 0, "mode": "claude", "skipped": "no stories in STORY_POLISH state"}

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
                custom_id=f"story-{row['story_id']}-polish",
                prompt=prompt,
                max_tokens=MAX_TOKENS_POLISH,
            )
        )

    anthropic_batch_id = client.submit_batch(requests)

    batch_db = StoryBatchDB(conn)
    batch_record = batch_db.insert_batch(
        StoryBatch(
            openai_batch_id=anthropic_batch_id,
            step="polish-claude",
            story_count=len(stories),
            submitted_at=datetime.now(),
        )
    )
    batch_db.insert_items([
        StoryBatchItem(
            batch_id=batch_record.id,
            story_id=row["story_id"],
            custom_id=f"story-{row['story_id']}-polish",
        )
        for row in stories
    ])

    for row in stories:
        _update_story_state(conn, row["story_id"], OUTPUT_STATE_CLAUDE)
    conn.commit()

    return {"mode": "claude", "submitted": len(stories), "anthropic_batch_id": anthropic_batch_id}


# ---------------------------------------------------------------------------
# 20.3 — Manual file submit
# ---------------------------------------------------------------------------

def submit_manual(conn: sqlite3.Connection) -> dict:
    stories = _fetch_polish_stories(conn)
    if not stories:
        return {"submitted": 0, "mode": "manual", "skipped": "no stories in STORY_POLISH state"}

    MANUAL_DIR.mkdir(parents=True, exist_ok=True)
    template = _load_prompt()
    written = 0

    for row in stories:
        input_file = MANUAL_DIR / f"{row['story_id']}_polish.txt"
        if not input_file.exists():
            prompt = template.format(
                title_text=row["title_text"],
                content_text=(row["content_text"] or "")[:MAX_CONTENT_LENGTH],
            )
            header = (
                f"=== MANUAL POLISH REQUEST — Story {row['story_id']} ===\n"
                f"Created: {datetime.now().isoformat()}\n\n"
                f"Polish the story below, then create the response file:\n"
                f"  {MANUAL_DIR}/{row['story_id']}_polish_done.txt\n\n"
                f"Response file format:\n"
                f"  TITLE: <improved title>\n"
                f"  CONTENT:\n"
                f"  <improved content — everything after the CONTENT: line>\n\n"
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
    if REVIEW_MODE == "claude":
        return submit_claude(conn)
    if REVIEW_MODE == "manual":
        return submit_manual(conn)
    return submit_gpt(conn)


if __name__ == "__main__":
    import sqlite3 as _sqlite3
    logging.basicConfig(level=logging.INFO)
    db_path = os.getenv("PRISMQ_DB_PATH", "C:/PrismQ/db.s3db")
    conn = _sqlite3.connect(db_path)
    conn.row_factory = _sqlite3.Row
    result = run(conn)
    conn.close()
    print(json.dumps(result, indent=2))
