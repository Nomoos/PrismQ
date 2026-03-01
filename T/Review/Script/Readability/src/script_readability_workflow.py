#!/usr/bin/env python3
"""Continuous Workflow Runner for PrismQ.T.Review.Content.Readability

This script runs continuously, processing Story objects that need script readability review.
It waits with dynamic intervals when no stories are available:
- 30 seconds when 0 stories to process
- 1 ms between iterations when stories are available

Usage:
    python script_readability_workflow.py           # Run continuously with DB save
    python script_readability_workflow.py --preview # Preview mode (no DB save)

Press Ctrl+C or close the window to stop.
"""

import sqlite3
import sys
import time
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
# T/Review/Script/Readability/src/ -> T/Review/Script/Readability/ -> T/Review/Script/ -> T/Review/ -> T/ -> repo root
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent

sys.path.insert(0, str(REPO_ROOT))

INPUT_STATE = "PrismQ.T.Review.Content.Readability"

try:
    from src.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from T.Review.Script.Readability.src.review_script_readability_service import (
        process_review_content_readability,
    )
    SERVICE_AVAILABLE = True
except Exception as e:
    SERVICE_AVAILABLE = False
    IMPORT_ERROR = str(e)


class Colors:
    HEADER = "\033[95m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'═' * 78}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(78)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 78}{Colors.END}\n")


def print_info(text: str) -> None:
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def print_success(text: str) -> None:
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str) -> None:
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str) -> None:
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def get_wait_interval(pending_count: int) -> float:
    """Return wait interval: 30s when idle, 1ms when processing."""
    return 30.0 if pending_count == 0 else 0.001


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Continuous Script Readability Workflow for PrismQ"
    )
    parser.add_argument("--preview", "-p", action="store_true",
                        help="Preview mode - do not save to database")
    parser.add_argument("--debug", "-d", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    print_header("PrismQ.T.Review.Content.Readability - CONTINUOUS MODE")
    print_info("Processing stories continuously")
    print_info("Waits 30 seconds when no stories to process")
    print_info("Press Ctrl+C to stop")
    print()

    if not SERVICE_AVAILABLE:
        print_error(f"Service module not available: {IMPORT_ERROR}")
        return 1

    db_path = "C:/PrismQ/db.s3db"
    if CONFIG_AVAILABLE:
        try:
            config = Config()
            db_path = config.database_path
        except Exception:
            pass

    print_info(f"Database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print_success("Connected to database")
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        return 1

    if args.preview:
        print_warning("PREVIEW MODE - Changes will not be saved to database")

    run_count = 0
    total_processed = 0
    total_accepted = 0
    total_rejected = 0

    try:
        while True:
            run_count += 1

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Story WHERE state = ?", (INPUT_STATE,))
            pending_count = cursor.fetchone()[0]

            if pending_count == 0:
                if run_count == 1:
                    print_info(f"No stories found with state {INPUT_STATE}")
                    print_info("Waiting for stories from previous steps...")
                wait = get_wait_interval(0)
                print_info(f"Waiting {wait:.0f}s before checking again...")
                time.sleep(wait)
                continue

            print_success(f"Found {pending_count} stories ready for script readability review")

            result = process_review_content_readability(connection=conn)

            if result is None:
                print_warning("No story found to process")
                time.sleep(1.0)
                continue

            total_processed += 1
            if result.accepted:
                print_success(
                    f"Story {result.story.id}: ACCEPTED script readability review"
                )
                print_info(f"  Next state: {result.new_state}")
                total_accepted += 1
            else:
                print_warning(
                    f"Story {result.story.id}: REJECTED script readability review"
                )
                print_info(f"  Next state: {result.new_state}")
                total_rejected += 1

            if total_processed % 10 == 0:
                print_info(
                    f"Progress: {total_accepted} accepted, {total_rejected} rejected"
                )

            remaining = pending_count - 1
            time.sleep(get_wait_interval(remaining))

    except KeyboardInterrupt:
        print()
        print_info("Workflow interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        conn.close()
        print()
        print_info(
            f"Session complete: {total_accepted} accepted, {total_rejected} rejected"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
