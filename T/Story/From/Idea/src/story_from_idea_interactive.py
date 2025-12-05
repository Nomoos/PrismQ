#!/usr/bin/env python3
"""Story from Idea CLI for PrismQ.

This script runs continuously, creating Story objects from Idea objects.
It selects the oldest unreferenced Idea and creates 10 Story objects for it,
then waits 1 second before processing the next one.

Usage:
    python story_from_idea_interactive.py           # Run continuously with DB save
    python story_from_idea_interactive.py --preview # Preview mode (no DB save)

Modes:
    Default: Runs continuously, creates stories and saves to database
    Preview: Runs continuously but doesn't save to database (for testing)
    
Press Ctrl+C or close the window to stop.
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup paths - Now in T/Story/From/Idea/src/
SCRIPT_DIR = Path(__file__).parent.absolute()
STORY_FROM_IDEA_ROOT = SCRIPT_DIR.parent  # T/Story/From/Idea
STORY_FROM_ROOT = STORY_FROM_IDEA_ROOT.parent  # T/Story/From
STORY_ROOT = STORY_FROM_ROOT.parent  # T/Story
T_ROOT = STORY_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))  # Current directory for local imports
sys.path.insert(0, str(T_ROOT / "Idea" / "Model" / "src"))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model"))
sys.path.insert(0, str(REPO_ROOT))  # Add repo root for src module import

# Import story from idea service
try:
    from story_from_idea_service import (
        StoryFromIdeaService,
        StoryCreationResult,
    )
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import SimpleIdea model and database
try:
    from simple_idea import SimpleIdea
    from simple_idea_db import SimpleIdeaDatabase
    IDEA_MODEL_AVAILABLE = True
except ImportError:
    IDEA_MODEL_AVAILABLE = False

# Try to import database connection
try:
    from src.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


# =============================================================================
# ANSI Colors for Terminal Output
# =============================================================================

class Colors:
    """ANSI color codes for terminal styling."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'═' * 78}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(78)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 78}{Colors.END}\n")


def print_section(text: str) -> None:
    """Print a styled section header."""
    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.END}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.END}")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_debug(text: str, logger: Optional[logging.Logger] = None) -> None:
    """Print a debug message."""
    print(f"{Colors.GRAY}  [DEBUG] {text}{Colors.END}")
    if logger:
        logger.debug(text)


def get_database_paths() -> tuple:
    """Get the database paths for Story and Idea databases.
    
    Returns database paths from Config if available, otherwise falls back
    to C:/PrismQ/db.s3db for both.
    
    Returns:
        Tuple of (story_db_path, idea_db_path)
    """
    if CONFIG_AVAILABLE:
        config = Config(interactive=False)
        # Both Story and Idea use the same database file
        return config.database_path, config.database_path
    else:
        # Fallback to C:/PrismQ/db.s3db
        default_path = str(Path("C:/PrismQ") / "db.s3db")
        return default_path, default_path



def run_continuous_mode(preview: bool = False):
    """Run story creation from idea continuously until cancelled.
    
    This mode processes ideas repeatedly with a 1 second pause between iterations.
    It continues until the user cancels with Ctrl+C or closes the window.
    
    Args:
        preview: If True, don't save to database (preview/test mode)
    """
    import sqlite3
    import time
    
    interval = 1.0  # Fixed 1 second pause between iterations
    
    # Setup logging for preview mode
    logger = None
    if preview:
        log_filename = f"story_from_idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        
        # Create logger with DEBUG level to allow all messages through
        logger = logging.getLogger('PrismQ.Story.From.Idea')
        logger.setLevel(logging.DEBUG)
        
        # File handler - captures all DEBUG messages
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        logger.info(f"Session started - Preview: {preview}, Mode: continuous")
        print_info(f"Logging to: {log_path}")
    
    # Print header
    mode_text = "PREVIEW MODE" if preview else "CONTINUOUS MODE"
    print_header(f"PrismQ Story From Idea - {mode_text}")
    
    # Check module availability
    if not SERVICE_AVAILABLE:
        print_error(f"Story from idea service not available: {IMPORT_ERROR}")
        if logger:
            logger.error(f"Module import failed: {IMPORT_ERROR}")
        return 1
    
    if not IDEA_MODEL_AVAILABLE:
        print_error("Idea model not available")
        if logger:
            logger.error("Idea model import failed")
        return 1
    
    print_success("Story from idea service loaded")
    if logger:
        logger.info("Story from idea service loaded successfully")
    
    if preview:
        print_warning("Preview mode - stories will NOT be saved to database")
        print_info("This mode is for testing. Check logs for details.")
    
    # Get database paths
    story_db_path, idea_db_path = get_database_paths()
    print_info(f"Story database: {story_db_path}")
    print_info(f"Idea database: {idea_db_path}")
    
    if logger:
        logger.info(f"Story database path: {story_db_path}")
        logger.info(f"Idea database path: {idea_db_path}")
    
    print_section("Continuous Mode")
    print(f"Processing ideas continuously with {interval} second pause between iterations.")
    print("Press Ctrl+C or close the window to stop.\n")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
            print(f"{Colors.CYAN}{Colors.BOLD}  Iteration {iteration}{Colors.END}")
            print(f"{Colors.CYAN}{'─' * 60}{Colors.END}")
            
            # Connect to databases
            try:
                # Check if database files exist
                story_path = Path(story_db_path)
                idea_path = Path(idea_db_path)
                
                if not story_path.exists():
                    print_warning(f"Story database not found: {story_db_path}")
                    if logger:
                        logger.warning(f"Story database not found: {story_db_path}")
                    print_info("Creating new database...")
                
                if not idea_path.exists():
                    print_error(f"Idea database not found: {idea_db_path}")
                    if logger:
                        logger.error(f"Idea database not found: {idea_db_path}")
                    print_info(f"Waiting {interval} second(s) before retry...")
                    time.sleep(interval)
                    continue
                
                # Connect to Story database
                story_conn = sqlite3.connect(story_db_path)
                story_conn.row_factory = sqlite3.Row
                
                # Connect to Idea database
                idea_db = SimpleIdeaDatabase(idea_db_path)
                idea_db.connect()
                
                print_success("Connected to databases")
                if logger:
                    logger.info("Connected to both databases")
                
            except Exception as e:
                print_error(f"Failed to connect to databases: {e}")
                if logger:
                    logger.exception("Database connection failed")
                print_info(f"Waiting {interval} second(s) before retry...")
                time.sleep(interval)
                continue
            
            try:
                # Create service
                service = StoryFromIdeaService(story_conn, idea_db)
                
                # Ensure tables exist
                service.ensure_tables_exist()
                
                # Find oldest unreferenced idea
                oldest_idea = service.get_oldest_unreferenced_idea()
                
                if oldest_idea is None:
                    print_warning("No unreferenced Ideas found")
                    print_info("All Ideas already have Story references.")
                    if logger:
                        logger.info("No unreferenced Ideas found")
                    
                    # Show stats
                    all_ideas = idea_db.get_all_ideas()
                    print_info(f"Total Ideas in database: {len(all_ideas)}")
                    
                    # Close connections with error handling
                    try:
                        story_conn.close()
                    except Exception as close_error:
                        if logger:
                            logger.warning(f"Error closing story connection: {close_error}")
                    try:
                        idea_db.close()
                    except Exception as close_error:
                        if logger:
                            logger.warning(f"Error closing idea database: {close_error}")
                    
                    print_info(f"Waiting {interval} second(s) before checking for new ideas...")
                    time.sleep(interval)
                    continue
                
                # Display idea info
                print_success(f"Found oldest unreferenced Idea: ID {oldest_idea.id}")
                print(f"  Text: {oldest_idea.text[:100]}..." if len(oldest_idea.text) > 100 else f"  Text: {oldest_idea.text}")
                print(f"  Version: {oldest_idea.version}")
                print(f"  Created: {oldest_idea.created_at}")
                
                if logger:
                    logger.info(f"Processing Idea ID {oldest_idea.id}")
                    logger.debug(f"Idea text: {oldest_idea.text}")
                
                # Show unreferenced count
                unreferenced = service.get_unreferenced_ideas()
                print_info(f"Total unreferenced Ideas: {len(unreferenced)}")
                
                if preview:
                    # Preview mode - don't save
                    print_info(f"Would create 10 Stories for Idea ID {oldest_idea.id}")
                    print_info("Stories would have state: TITLE_FROM_IDEA (PrismQ.T.Title.From.Idea)")
                    print_warning("Preview mode - no changes made to database")
                    
                    if logger:
                        logger.info(f"Preview: Would create 10 Stories for Idea ID {oldest_idea.id}")
                    
                    print_info(f"Remaining unreferenced Ideas (unchanged): {len(unreferenced)}")
                    
                else:
                    # Run mode - save to database
                    result = service.create_stories_from_idea(
                        idea_id=oldest_idea.id,
                        skip_if_exists=True
                    )
                    
                    if result is None:
                        print_warning(f"Idea ID {oldest_idea.id} already has Stories")
                        if logger:
                            logger.info(f"Idea ID {oldest_idea.id} already has Stories - skipped")
                    else:
                        print_success(f"Created {result.count} Stories for Idea ID {result.idea_id}")
                        
                        # Display created stories
                        for i, story in enumerate(result.stories):
                            print(f"  Story {i+1}: ID {story.id}, State: {story.state.value if hasattr(story.state, 'value') else story.state}")
                        
                        if logger:
                            for story in result.stories:
                                logger.info(f"Created Story ID {story.id} for Idea ID {story.idea_id}")
                            logger.info(f"Successfully created {result.count} Stories")
                    
                    # Get the updated count after processing
                    remaining = service.get_unreferenced_ideas()
                    remaining_count = len(remaining)
                    if remaining_count > 0:
                        print_info(f"Remaining unreferenced Ideas: {remaining_count}")
                    else:
                        print_info("No more unreferenced Ideas remaining")
                
            except Exception as e:
                print_error(f"Error processing idea: {e}")
                if logger:
                    logger.exception("Error processing idea")
            
            finally:
                # Close connections - log errors but don't fail
                try:
                    if 'story_conn' in locals() and story_conn:
                        story_conn.close()
                except Exception as close_error:
                    if logger:
                        logger.warning(f"Error closing story connection: {close_error}")
                try:
                    if 'idea_db' in locals() and idea_db:
                        idea_db.close()
                except Exception as close_error:
                    if logger:
                        logger.warning(f"Error closing idea database: {close_error}")
            
            # Wait before next iteration
            print_info(f"Waiting {interval} second(s) before next iteration...")
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print_info("Interrupted by user. Exiting...")
        if logger:
            logger.info(f"User interrupted after {iteration} iterations")
        return 0
    
    return 0



def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Story Creation from Idea for PrismQ - runs continuously with 1 second pause',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python story_from_idea_interactive.py           # Run continuously with DB save
  python story_from_idea_interactive.py --preview # Preview mode (no DB save)

Press Ctrl+C or close the window to stop.
        """
    )
    
    parser.add_argument('--preview', '-p', action='store_true',
                       help='Preview mode - do not save to database')
    
    args = parser.parse_args()
    
    return run_continuous_mode(preview=args.preview)


if __name__ == '__main__':
    sys.exit(main())
