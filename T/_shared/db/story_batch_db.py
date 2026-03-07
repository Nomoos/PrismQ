"""StoryBatch and StoryBatchItem table management.

StoryBatch  — tracks one OpenAI batch job (review or polish).
StoryBatchItem — links each story to the batch job and stores its result.

Schema is created automatically on first use (CREATE TABLE IF NOT EXISTS).
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_DDL = """
CREATE TABLE IF NOT EXISTS StoryBatch (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    openai_batch_id TEXT NOT NULL UNIQUE,
    step            TEXT NOT NULL,          -- 'review' or 'polish'
    status          TEXT NOT NULL DEFAULT 'pending',
    story_count     INTEGER NOT NULL DEFAULT 0,
    submitted_at    TEXT NOT NULL,
    completed_at    TEXT,
    output_file_id  TEXT,
    error           TEXT
);

CREATE INDEX IF NOT EXISTS idx_storybatch_status ON StoryBatch(status);
CREATE INDEX IF NOT EXISTS idx_storybatch_step   ON StoryBatch(step);

CREATE TABLE IF NOT EXISTS StoryBatchItem (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id    INTEGER NOT NULL,
    story_id    INTEGER NOT NULL,
    custom_id   TEXT NOT NULL UNIQUE,
    result_json TEXT,
    FOREIGN KEY (batch_id) REFERENCES StoryBatch(id),
    FOREIGN KEY (story_id) REFERENCES Story(id)
);

CREATE INDEX IF NOT EXISTS idx_storybatchitem_story ON StoryBatchItem(story_id);
CREATE INDEX IF NOT EXISTS idx_storybatchitem_batch ON StoryBatchItem(batch_id);
"""

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class StoryBatch:
    openai_batch_id: str
    step: str                       # "review" | "polish"
    story_count: int
    submitted_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"         # pending | completed | failed
    completed_at: Optional[datetime] = None
    output_file_id: Optional[str] = None
    error: Optional[str] = None
    id: Optional[int] = None


@dataclass
class StoryBatchItem:
    batch_id: int
    story_id: int
    custom_id: str                  # e.g. "story-123-review"
    result_json: Optional[str] = None
    id: Optional[int] = None


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------

class StoryBatchDB:
    """Manages StoryBatch and StoryBatchItem tables.

    Args:
        connection: Open SQLite connection (must have row_factory = Row).
    """

    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create tables if they don't exist yet."""
        self._conn.executescript(_DDL)
        self._conn.commit()

    # ------------------------------------------------------------------
    # StoryBatch
    # ------------------------------------------------------------------

    def insert_batch(self, batch: StoryBatch) -> StoryBatch:
        """Insert a new StoryBatch record."""
        cursor = self._conn.execute(
            """
            INSERT INTO StoryBatch
                (openai_batch_id, step, status, story_count, submitted_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                batch.openai_batch_id,
                batch.step,
                batch.status,
                batch.story_count,
                batch.submitted_at.isoformat(),
            ),
        )
        self._conn.commit()
        batch.id = cursor.lastrowid
        return batch

    def update_batch_status(
        self,
        batch_db_id: int,
        status: str,
        output_file_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update batch status after polling."""
        completed_at = datetime.now().isoformat() if status in ("completed", "failed") else None
        self._conn.execute(
            """
            UPDATE StoryBatch
            SET status = ?, output_file_id = ?, error = ?, completed_at = ?
            WHERE id = ?
            """,
            (status, output_file_id, error, completed_at, batch_db_id),
        )
        self._conn.commit()

    def find_active_batches(self, step: str) -> List[sqlite3.Row]:
        """Return all pending (not yet completed) batches for a step."""
        cursor = self._conn.execute(
            "SELECT * FROM StoryBatch WHERE step = ? AND status = 'pending'",
            (step,),
        )
        return cursor.fetchall()

    def find_batch_by_openai_id(self, openai_batch_id: str) -> Optional[sqlite3.Row]:
        cursor = self._conn.execute(
            "SELECT * FROM StoryBatch WHERE openai_batch_id = ?",
            (openai_batch_id,),
        )
        return cursor.fetchone()

    # ------------------------------------------------------------------
    # StoryBatchItem
    # ------------------------------------------------------------------

    def insert_items(self, items: List[StoryBatchItem]) -> None:
        """Bulk-insert batch items."""
        self._conn.executemany(
            "INSERT INTO StoryBatchItem (batch_id, story_id, custom_id) VALUES (?, ?, ?)",
            [(item.batch_id, item.story_id, item.custom_id) for item in items],
        )
        self._conn.commit()

    def find_items_by_batch(self, batch_db_id: int) -> List[sqlite3.Row]:
        """Return all items belonging to a batch."""
        cursor = self._conn.execute(
            "SELECT * FROM StoryBatchItem WHERE batch_id = ?",
            (batch_db_id,),
        )
        return cursor.fetchall()

    def update_item_result(self, item_id: int, result_json: str) -> None:
        self._conn.execute(
            "UPDATE StoryBatchItem SET result_json = ? WHERE id = ?",
            (result_json, item_id),
        )
        self._conn.commit()

    def find_item_by_custom_id(self, custom_id: str) -> Optional[sqlite3.Row]:
        cursor = self._conn.execute(
            "SELECT * FROM StoryBatchItem WHERE custom_id = ?",
            (custom_id,),
        )
        return cursor.fetchone()
