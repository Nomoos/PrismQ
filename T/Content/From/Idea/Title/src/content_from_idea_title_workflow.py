#!/usr/bin/env python3
"""Continuous Workflow Runner for PrismQ.T.Content.From.Idea.Title

This script runs continuously, processing Story objects that need content generation.
It waits with dynamic intervals when no stories are available:
- 30 seconds when 0 stories to process
- Gradually decreasing wait time as more stories become available

Usage:
    python content_from_idea_title_workflow.py           # Run continuously with DB save
    python content_from_idea_title_workflow.py --preview # Preview mode (no DB save)

Press Ctrl+C or close the window to stop.
"""

import logging
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
CONTENT_FROM_IDEA_TITLE_ROOT = SCRIPT_DIR.parent
T_ROOT = CONTENT_FROM_IDEA_TITLE_ROOT.parent.parent.parent
REPO_ROOT = T_ROOT.parent

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT))

try:
    from story_content_service import StateBasedContentService
    from src.config import Config
    
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
    
    Args:
        pending_count: Number of stories pending processing
        
    Returns:
        Wait interval in seconds:
        - 30.0 seconds when 0 stories (wait for new items)
        - 0.001 (1 ms) when > 0 stories (between iterations)
    """
    if pending_count == 0:
        return 30.0  # 30 seconds when nothing to process
    else:
        return 0.001  # 1 ms between iterations


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
        description="Continuous Content Generation Workflow for PrismQ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python content_from_idea_title_workflow.py           # Run continuously with DB save
  python content_from_idea_title_workflow.py --preview # Preview mode (no DB save)
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
        log_filename = f"content_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(),
            ],
        )
        logger = logging.getLogger("PrismQ.Content.From.Idea.Title")
        logger.info("Workflow started")
        print_info(f"Logging to: {log_path}")

    # Print header
    print_header("PrismQ.T.Content.From.Idea.Title - CONTINUOUS MODE")
    print_info("Processing stories continuously")
    print_info("Waits 30 seconds when no stories to process")
    print_info("Press Ctrl+C to stop")
    print()

    # Check module availability
    if not SERVICE_AVAILABLE:
        print_error(f"Service module not available: {IMPORT_ERROR}")
        return 1

    # Get database path
    try:
        db_path = Config.get_database_path()
    except:
        db_path = "C:/PrismQ/db.s3db"
    
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
    service = StateBasedContentService(conn, preview_mode=args.preview)
    
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
                print_success(f"Found {pending_count} stories ready for content generation")
            else:
                print_success(f"Found {pending_count} pending stories")
            
            # Process oldest story
            result = service.process_oldest_story()
            
            if result.story_id is None:
                # Should not happen but handle it
                print_warning("No story found to process")
                time.sleep(1.0)
                continue
            
            # Display result
            if result.success:
                print_success(f"Story {result.story_id}: Content generated successfully")
                if result.word_count:
                    print(f"  Word count: {result.word_count}")
                if result.duration:
                    print(f"  Duration: {result.duration:.1f}s")
                total_processed += 1
            else:
                print_error(f"Story {result.story_id}: Failed - {result.error}")
                total_errors += 1
            
            # Show summary periodically
            if total_processed + total_errors > 0 and (total_processed + total_errors) % 10 == 0:
                print()
                print_info(f"Progress: {total_processed} successful, {total_errors} errors")
            
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
        print_info(f"Session complete: {total_processed} processed, {total_errors} errors")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
