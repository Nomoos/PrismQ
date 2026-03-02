#!/usr/bin/env python3
"""Continuous Workflow Runner for PrismQ.T.Content.From.Content.Review.Title

This script runs continuously, processing Story objects that need content improvement
based on review feedback.

Wait strategy:
- 1ms between iterations when there are items to process
- 30 seconds when idle (no items to process)

Usage:
    python script_from_review_workflow.py           # Run continuously with DB save
    python script_from_review_workflow.py --preview # Preview mode (no DB save)

Press Ctrl+C or close the window to stop.
"""

import logging
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
MODULE_ROOT = SCRIPT_DIR.parent
T_ROOT = MODULE_ROOT.parent.parent.parent.parent.parent
REPO_ROOT = T_ROOT.parent

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT))

# Import Config before service
try:
    from src.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from script_from_review_service import ScriptFromReviewService
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    IMPORT_ERROR = str(e)


# ANSI Colors
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
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
    """Calculate wait interval based on pending stories count.

    Returns:
        30.0 seconds when 0 stories, 0.001 seconds when > 0 stories
    """
    if pending_count == 0:
        return 30.0
    else:
        return 0.001


def format_wait_time(interval: float) -> str:
    """Format wait interval for display."""
    if interval >= 1.0:
        return f"{interval:.1f} seconds"
    else:
        return f"{interval * 1000:.0f} ms"


def main():
    """Main continuous workflow runner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Continuous Content Improvement Workflow for PrismQ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script_from_review_workflow.py           # Run continuously with DB save
  python script_from_review_workflow.py --preview # Preview mode (no DB save)
        """,
    )

    parser.add_argument(
        "--preview", "-p", action="store_true",
        help="Preview mode - do not save to database"
    )
    parser.add_argument(
        "--debug", "-d", action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Setup logging
    if args.debug:
        log_filename = f"script_from_review_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(),
            ],
        )
        logger = logging.getLogger("PrismQ.Content.From.Review")
        logger.info("Workflow started")
        print_info(f"Logging to: {log_path}")

    # Print header
    print_header("PrismQ.T.Content.From.Content.Review.Title")
    print_info("Processing stories continuously")
    print_info("Waits 30 seconds when no stories to process")
    print_info("Press Ctrl+C to stop")
    print()

    # Check module availability
    if not SERVICE_AVAILABLE:
        print_error(f"Service module not available: {IMPORT_ERROR}")
        return 1

    # Get database path
    db_path = "C:/PrismQ/db.s3db"
    if CONFIG_AVAILABLE:
        try:
            config = Config()
            db_path = config.database_path
        except Exception:
            pass

    print_info(f"Database: {db_path}")

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print_success("Connected to database")
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        return 1

    # Initialize service
    service = ScriptFromReviewService(conn, preview_mode=args.preview)

    if args.preview:
        print_warning("PREVIEW MODE - Changes will not be saved to database")

    # Continuous processing loop
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

            # Get count of pending stories
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM Story WHERE state = ?",
                (service.INPUT_STATE,)
            )
            pending_count = cursor.fetchone()[0]

            if pending_count == 0:
                if run_count == 1:
                    print_info(f"No stories found with state {service.INPUT_STATE}")
                    print_info("Waiting for stories to be created by previous steps...")

                wait_interval = get_wait_interval(0)
                print_info(f"Waiting {format_wait_time(wait_interval)} before checking again...")
                time.sleep(wait_interval)
                continue

            if run_count == 1:
                print_success(f"Found {pending_count} stories ready for content improvement")
            else:
                print_success(f"Found {pending_count} pending stories")

            # Process oldest story
            result = service.process_oldest_story()

            if result.story_id is None:
                print_warning("No story found to process")
                time.sleep(1.0)
                continue

            # Display result
            if result.success:
                total_processed += 1
                print_success(
                    f"Story {result.story_id}: Content improved to v{result.new_content_version}"
                )
                print_info(f"  Next state: {result.new_state}")
            else:
                print_error(f"Story {result.story_id}: Failed - {result.error}")
                total_errors += 1

            # Show summary periodically
            if (total_processed + total_errors) > 0 and (total_processed + total_errors) % 10 == 0:
                print()
                print_info(f"Progress: {total_processed} improved, {total_errors} errors")

            # Dynamic wait based on remaining count
            remaining = pending_count - 1
            wait_interval = get_wait_interval(remaining)

            if remaining > 0:
                print_info(f"Waiting {format_wait_time(wait_interval)} before next story...")
                time.sleep(wait_interval)

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
        print_info(f"Session complete: {total_processed} improved, {total_errors} errors")

    return 0


if __name__ == "__main__":
    sys.exit(main())
