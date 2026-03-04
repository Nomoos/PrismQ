#!/usr/bin/env python3
"""Continuous Workflow Runner for PrismQ.T.Review.Content.From.Title [10].

Processes stories in REVIEW_CONTENT_FROM_TITLE state using Ollama AI.
Pre-checks score trend — escalates to [07] if no improvement over last 3 versions.

On PASS     → REVIEW_CONTENT_GRAMMAR [11]
On FAIL     → CONTENT_FROM_TITLE_CONTENT_REVIEW [09]
On ESCALATE → REVIEW_TITLE_FROM_CONTENT [07]

Usage:
    python review_script_from_title_workflow.py

Press Ctrl+C to stop.
"""

import sqlite3
import sys
import time
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
MODULE_ROOT = SCRIPT_DIR.parent
T_ROOT = MODULE_ROOT.parent.parent.parent.parent   # Title→From→Script→Review→T
REPO_ROOT = T_ROOT.parent                          # T→PrismQ (repo root)

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT))

try:
    from src.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from review_script_from_title import ReviewContentFromTitleService
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    IMPORT_ERROR = str(e)


# ANSI Colors
class Colors:
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    GRAY   = "\033[90m"
    END    = "\033[0m"
    BOLD   = "\033[1m"


def print_info(text):    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")
def print_success(text): print(f"{Colors.GREEN}✓ {text}{Colors.END}")
def print_error(text):   print(f"{Colors.RED}✗ {text}{Colors.END}")
def print_warning(text): print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def main() -> int:
    if not SERVICE_AVAILABLE:
        print_error(f"Failed to import service: {IMPORT_ERROR}")
        return 1

    db_path = "C:/PrismQ/db.s3db"
    if CONFIG_AVAILABLE:
        try:
            db_path = Config(interactive=False).database_path
        except Exception:
            pass

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 78}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'PrismQ.T.Review.Content.From.Title'.center(78)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 78}{Colors.END}\n")

    print_info("Processing stories continuously")
    print_info("Waits 30 seconds when no stories to process")
    print_info("Press Ctrl+C to stop")
    print()

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        return 1

    print_info(f"Database: {db_path}")
    print_success("Connected to database")

    service = ReviewContentFromTitleService(conn)

    run_count = 0
    total_processed = 0
    total_errors = 0

    try:
        while True:
            run_count += 1

            if run_count > 1:
                print(f"\n{Colors.CYAN}{'═' * 80}{Colors.END}")
                print(f"{Colors.CYAN}Run #{run_count} - Checking for stories...{Colors.END}")
                print(f"{Colors.CYAN}{'═' * 80}{Colors.END}\n")

            pending = service.count_pending()

            if pending == 0:
                if run_count == 1:
                    print_info(f"No stories in state {service.CURRENT_STATE}")
                print_info("Waiting 30s before next check...")
                time.sleep(30)
                continue

            if run_count == 1:
                print_success(f"Found {pending} stories ready for content review")
            else:
                print_success(f"Found {pending} pending stories")

            result = service.process_oldest_story()

            if result.story_id is None:
                print_warning("No story returned")
                time.sleep(1)
                continue

            if result.success:
                total_processed += 1
                if result.escalated:
                    print_warning(f"Story {result.story_id}: Escalated (no score improvement) → {result.next_state}")
                elif result.passes:
                    print_success(f"Story {result.story_id}: Content ACCEPTED (score: {result.score})")
                else:
                    print_warning(f"Story {result.story_id}: Content REJECTED (score: {result.score})")
                print_info(f"  Next state: {result.next_state}")
            else:
                total_errors += 1
                print_error(f"Story {result.story_id}: Failed - {result.error}")

            print_info("Waiting 1 ms before next story...")
            time.sleep(0.001)

    except KeyboardInterrupt:
        print()
        print_info("Workflow stopped by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()
        print()
        print_info(f"Session: {total_processed} processed, {total_errors} errors")

    return 0


if __name__ == "__main__":
    sys.exit(main())
