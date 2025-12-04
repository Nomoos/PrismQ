#!/usr/bin/env python3
"""Interactive Story from Idea CLI for PrismQ.

This script provides an interactive mode for creating Story objects from Idea objects.
It selects the oldest unreferenced Idea and creates 10 Story objects for it.

Usage:
    python story_from_idea_interactive.py                    # Interactive mode with DB save
    python story_from_idea_interactive.py --preview          # Preview mode (no DB save)
    python story_from_idea_interactive.py --preview --debug  # Debug mode with extensive logging

Modes:
    Default: Creates stories and saves to database
    Preview: Creates stories for testing without saving (extensive logging)
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


# =============================================================================
# Interactive Mode
# =============================================================================

def run_interactive_mode(preview: bool = False, debug: bool = False):
    """Run the interactive story from idea mode.
    
    Args:
        preview: If True, don't save to database (preview/test mode)
        debug: If True, enable extensive debug logging
    """
    import sqlite3
    
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"story_from_idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        
        # Create logger with DEBUG level to allow all messages through
        # Handler levels control what actually gets logged
        logger = logging.getLogger('PrismQ.Story.From.Idea')
        logger.setLevel(logging.DEBUG)
        
        # File handler - captures all DEBUG messages
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Console handler - only INFO and above
        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(console_handler)
        
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")
    
    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
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
    
    # Interactive loop
    print_section("Story From Idea Workflow")
    print("This workflow selects the oldest Idea without Story references")
    print("and creates 10 Story objects for it.")
    print("\nPress Enter to process the next Idea, or type 'quit' to exit.\n")
    
    while True:
        print(f"{Colors.CYAN}>>> Press Enter to process next Idea (or 'quit' to exit): {Colors.END}", end="")
        
        try:
            line = input().strip()
            if line.lower() == 'quit':
                print_info("Exiting...")
                if logger:
                    logger.info("User requested exit")
                return 0
            
        except EOFError:
            print_info("Exiting...")
            return 0
        except KeyboardInterrupt:
            print("\n")
            print_info("Interrupted. Type 'quit' to exit.")
            continue
        
        # Connect to databases
        print_section("Connecting to Databases")
        
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
            continue
        
        try:
            # Create service
            service = StoryFromIdeaService(story_conn, idea_db)
            
            # Ensure tables exist
            service.ensure_tables_exist()
            
            # Find oldest unreferenced idea
            print_section("Finding Unreferenced Ideas")
            
            oldest_idea = service.get_oldest_unreferenced_idea()
            
            if oldest_idea is None:
                print_warning("No unreferenced Ideas found")
                print_info("All Ideas already have Story references.")
                if logger:
                    logger.info("No unreferenced Ideas found")
                
                # Show stats
                all_ideas = idea_db.get_all_ideas()
                print_info(f"Total Ideas in database: {len(all_ideas)}")
                
                story_conn.close()
                idea_db.close()
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
                print_section("Preview Mode - Simulating Story Creation")
                print_info(f"Would create 10 Stories for Idea ID {oldest_idea.id}")
                print_info("Stories would have state: TITLE_FROM_IDEA (PrismQ.T.Title.From.Idea)")
                print_warning("Preview mode - no changes made to database")
                
                if logger:
                    logger.info(f"Preview: Would create 10 Stories for Idea ID {oldest_idea.id}")
                
                # In preview mode, idea is still unreferenced, so remaining count is same as before
                print_info(f"Remaining unreferenced Ideas (unchanged): {len(unreferenced)}")
                
            else:
                # Run mode - save to database
                print_section("Creating Stories")
                
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
                    print_section(f"Created {result.count} Story Object(s)")
                    
                    for i, story in enumerate(result.stories):
                        print(f"\n{Colors.GREEN}{'─' * 50}{Colors.END}")
                        print(f"{Colors.GREEN}{Colors.BOLD}  Story {i+1}{Colors.END}")
                        print(f"{Colors.GREEN}{'─' * 50}{Colors.END}")
                        print(f"  ID: {story.id}")
                        print(f"  Idea ID: {story.idea_id}")
                        print(f"  State: {story.state.value if hasattr(story.state, 'value') else story.state}")
                        print(f"  Created: {story.created_at}")
                        
                        if logger:
                            logger.info(f"Created Story ID {story.id} for Idea ID {story.idea_id}")
                    
                    if logger:
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
            # Close connections
            try:
                story_conn.close()
                idea_db.close()
            except Exception:
                pass
        
        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print("Press Enter to process next Idea or type 'quit' to exit.\n")


def run_continuous_mode(preview: bool = False, debug: bool = False, interval: float = 1.0):
    """Run story creation from idea continuously until cancelled.
    
    This mode processes ideas repeatedly with a pause between iterations.
    It continues until the user cancels with Ctrl+C or closes the window.
    
    Args:
        preview: If True, don't save to database (preview/test mode)
        debug: If True, enable extensive debug logging
        interval: Pause in seconds between iterations (default: 1.0)
    """
    import sqlite3
    import time
    
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"story_from_idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        
        # Create logger with DEBUG level to allow all messages through
        logger = logging.getLogger('PrismQ.Story.From.Idea')
        logger.setLevel(logging.DEBUG)
        
        # File handler - captures all DEBUG messages
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Console handler - only INFO and above
        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(console_handler)
        
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}, Mode: continuous")
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
                    
                    story_conn.close()
                    idea_db.close()
                    
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
                # Close connections
                try:
                    story_conn.close()
                    idea_db.close()
                except Exception:
                    pass
            
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


def run_single_mode(preview: bool = False, debug: bool = False):
    """Run a single story creation from idea without interactive prompts.
    
    This mode processes one idea automatically and exits.
    
    Args:
        preview: If True, don't save to database (preview/test mode)
        debug: If True, enable extensive debug logging
    """
    import sqlite3
    
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"story_from_idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        
        # Create logger with DEBUG level to allow all messages through
        logger = logging.getLogger('PrismQ.Story.From.Idea')
        logger.setLevel(logging.DEBUG)
        
        # File handler - captures all DEBUG messages
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Console handler - only INFO and above
        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(console_handler)
        
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}, Mode: single")
        print_info(f"Logging to: {log_path}")
    
    # Print header
    mode_text = "PREVIEW MODE" if preview else "RUN MODE"
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
    
    # Connect to databases
    print_section("Connecting to Databases")
    
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
            return 1
        
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
        return 1
    
    try:
        # Create service
        service = StoryFromIdeaService(story_conn, idea_db)
        
        # Ensure tables exist
        service.ensure_tables_exist()
        
        # Find oldest unreferenced idea
        print_section("Finding Unreferenced Ideas")
        
        oldest_idea = service.get_oldest_unreferenced_idea()
        
        if oldest_idea is None:
            print_warning("No unreferenced Ideas found")
            print_info("All Ideas already have Story references.")
            if logger:
                logger.info("No unreferenced Ideas found")
            
            # Show stats
            all_ideas = idea_db.get_all_ideas()
            print_info(f"Total Ideas in database: {len(all_ideas)}")
            
            story_conn.close()
            idea_db.close()
            return 0
        
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
            print_section("Preview Mode - Simulating Story Creation")
            print_info(f"Would create 10 Stories for Idea ID {oldest_idea.id}")
            print_info("Stories would have state: TITLE_FROM_IDEA (PrismQ.T.Title.From.Idea)")
            print_warning("Preview mode - no changes made to database")
            
            if logger:
                logger.info(f"Preview: Would create 10 Stories for Idea ID {oldest_idea.id}")
            
            # In preview mode, idea is still unreferenced, so remaining count is same as before
            print_info(f"Remaining unreferenced Ideas (unchanged): {len(unreferenced)}")
            
        else:
            # Run mode - save to database
            print_section("Creating Stories")
            
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
                print_section(f"Created {result.count} Story Object(s)")
                
                for i, story in enumerate(result.stories):
                    print(f"\n{Colors.GREEN}{'─' * 50}{Colors.END}")
                    print(f"{Colors.GREEN}{Colors.BOLD}  Story {i+1}{Colors.END}")
                    print(f"{Colors.GREEN}{'─' * 50}{Colors.END}")
                    print(f"  ID: {story.id}")
                    print(f"  Idea ID: {story.idea_id}")
                    print(f"  State: {story.state.value if hasattr(story.state, 'value') else story.state}")
                    print(f"  Created: {story.created_at}")
                    
                    if logger:
                        logger.info(f"Created Story ID {story.id} for Idea ID {story.idea_id}")
                
                if logger:
                    logger.info(f"Successfully created {result.count} Stories")
            
            # Get the updated count after processing
            remaining = service.get_unreferenced_ideas()
            remaining_count = len(remaining)
            if remaining_count > 0:
                print_info(f"Remaining unreferenced Ideas: {remaining_count}")
            else:
                print_info("No more unreferenced Ideas remaining")
        
        return 0
        
    except Exception as e:
        print_error(f"Error processing idea: {e}")
        if logger:
            logger.exception("Error processing idea")
        return 1
    
    finally:
        # Close connections
        try:
            story_conn.close()
            idea_db.close()
        except Exception:
            pass


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Interactive Story Creation from Idea for PrismQ',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python story_from_idea_interactive.py                    # Interactive mode with DB save
  python story_from_idea_interactive.py --run              # Run mode - process one idea and exit
  python story_from_idea_interactive.py --continuous       # Continuous mode - run repeatedly until cancelled
  python story_from_idea_interactive.py --preview          # Preview mode (no DB save)
  python story_from_idea_interactive.py --preview --debug  # Debug mode with extensive logging
        """
    )
    
    parser.add_argument('--preview', '-p', action='store_true',
                       help='Preview mode - do not save to database')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug logging (extensive output)')
    parser.add_argument('--run', '-r', action='store_true',
                       help='Run mode - process one idea without interactive prompts and exit')
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Continuous mode - run repeatedly with 1 second pause until cancelled (Ctrl+C or close window)')
    parser.add_argument('--interval', '-i', type=float, default=1.0,
                       help='Interval in seconds between iterations in continuous mode (default: 1.0)')
    
    args = parser.parse_args()
    
    if args.continuous:
        return run_continuous_mode(preview=args.preview, debug=args.debug, interval=args.interval)
    elif args.run:
        return run_single_mode(preview=args.preview, debug=args.debug)
    else:
        return run_interactive_mode(preview=args.preview, debug=args.debug)


if __name__ == '__main__':
    sys.exit(main())
