#!/usr/bin/env python3
"""Step 18+19 — Story Review: Combined submit + poll runner.

Continuously:
  1. Submits all STORY_REVIEW stories to the active track (GPT / Claude / Manual)
  2. Polls all pending review batches / manual files and processes completed results

Environment variables:
    PRISMQ_REVIEW_MODE   gpt | claude | manual   (default: gpt)
    PRISMQ_DB_PATH       path to SQLite DB        (default: C:/PrismQ/db.s3db)
    OPENAI_API_KEY
    ANTHROPIC_API_KEY

Press Ctrl+C to stop.
"""

import logging
import os
import sqlite3
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_src_dir = Path(__file__).parent.absolute()
_story_review_dir = _src_dir.parent           # T/Story/Review
_t_dir = _story_review_dir.parent.parent      # T
_repo_root = _t_dir.parent                    # repo root

for _p in [str(_repo_root), str(_t_dir), str(_src_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import story_review_batch_submit as _submit
import story_review_batch_poll as _poll

from Model.state import StateNames

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------


class Colors:
    HEADER = "\033[95m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    END    = "\033[0m"
    BOLD   = "\033[1m"


def _header(text: str) -> None:
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'═' * 78}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(78)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 78}{Colors.END}\n")


def _info(text: str) -> None:
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def _ok(text: str) -> None:
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def _warn(text: str) -> None:
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def _err(text: str) -> None:
    print(f"{Colors.RED}✗ {text}{Colors.END}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PENDING_STATES = (
    StateNames.STORY_REVIEW,
    StateNames.STORY_REVIEW_GPT_PENDING,
    StateNames.STORY_REVIEW_CLAUDE_PENDING,
    StateNames.STORY_REVIEW_MANUAL_PENDING,
)

POLL_INTERVAL_IDLE   = 30.0   # seconds — nothing in the review pipeline
POLL_INTERVAL_ACTIVE = 15.0   # seconds — batches are in flight


def _count_pending(conn: sqlite3.Connection) -> int:
    placeholders = ",".join("?" * len(_PENDING_STATES))
    row = conn.execute(
        f"SELECT COUNT(*) FROM Story WHERE state IN ({placeholders})",
        _PENDING_STATES,
    ).fetchone()
    return row[0] if row else 0


def _print_poll(result: dict, run: int) -> None:
    for track, data in result.items():
        if not isinstance(data, dict):
            continue
        processed = data.get("stories_processed", 0)
        pending   = data.get("stories_pending", 0)
        checked   = data.get("batches_checked", data.get("stories_checked", 0))
        error     = data.get("error")
        if error:
            _warn(f"[{run}] {track}: {error}")
        elif processed > 0:
            _ok(f"[{run}] {track}: {processed} stories resolved")
        elif checked > 0:
            _info(f"[{run}] {track}: {checked} checked, {pending} still pending")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    db_path     = os.getenv("PRISMQ_DB_PATH", "C:/PrismQ/db.s3db")
    review_mode = os.getenv("PRISMQ_REVIEW_MODE", "gpt").lower()

    _header("PrismQ.T.Story.Review")
    _info(f"Database:     {db_path}")
    _info(f"Review mode:  {review_mode}")
    _info("Press Ctrl+C to stop")
    print()

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        _ok("Connected to database")
    except Exception as exc:
        _err(f"Failed to connect to database: {exc}")
        return 1

    run = 0
    try:
        while True:
            run += 1

            # 1. Submit stories that are waiting in STORY_REVIEW state
            try:
                submit_result = _submit.run(conn)
                submitted = submit_result.get("submitted", 0)
                if submitted > 0:
                    mode = submit_result.get("mode", review_mode)
                    _ok(f"[{run}] Submitted {submitted} stories for review ({mode})")
                    if "openai_batch_id" in submit_result:
                        _info(f"  Batch ID: {submit_result['openai_batch_id']}")
                    elif "anthropic_batch_id" in submit_result:
                        _info(f"  Batch ID: {submit_result['anthropic_batch_id']}")
                    elif "manual_dir" in submit_result:
                        _info(f"  Review files written to: {submit_result['manual_dir']}")
            except Exception as exc:
                _err(f"[{run}] Submit error: {exc}")

            # 2. Poll all pending tracks (GPT, Claude, manual)
            try:
                poll_result = _poll.run(conn)
                _print_poll(poll_result, run)
            except Exception as exc:
                _err(f"[{run}] Poll error: {exc}")

            # 3. Sleep based on pipeline activity
            pending = _count_pending(conn)
            wait = POLL_INTERVAL_ACTIVE if pending > 0 else POLL_INTERVAL_IDLE
            if pending == 0:
                _info(f"No stories in review pipeline. Waiting {wait:.0f}s before next check...")
            else:
                _info(f"{pending} stories still in pipeline. Next poll in {wait:.0f}s...")
            time.sleep(wait)

    except KeyboardInterrupt:
        print()
        _info("Stopped by user")
    except Exception as exc:
        _err(f"Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
