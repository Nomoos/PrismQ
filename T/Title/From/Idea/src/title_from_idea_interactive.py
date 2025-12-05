#!/usr/bin/env python3
"""Title Generation CLI for PrismQ (AI-powered).

This script provides title generation from ideas using local AI (Ollama).
AI is REQUIRED - no template-based fallback is available.

Usage:
    python title_from_idea_interactive.py                    # Continuous mode (default)
    python title_from_idea_interactive.py --preview          # Preview mode (no DB save)
    python title_from_idea_interactive.py --interactive      # Interactive mode (manual input)

Modes:
    Default (Continuous): Auto-processes Stories from database without user input
    Interactive: Manual input mode for testing single ideas
    Preview: Creates titles for testing without saving (extensive logging)

Requirements:
    - Ollama must be running with qwen2.5:14b-instruct model
    - AI is required - script will fail if Ollama is unavailable
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Setup paths - Now in T/Title/From/Idea/src/
SCRIPT_DIR = Path(__file__).parent.absolute()
TITLE_FROM_IDEA_ROOT = SCRIPT_DIR.parent  # T/Title/From/Idea
TITLE_FROM_ROOT = TITLE_FROM_IDEA_ROOT.parent  # T/Title/From
TITLE_ROOT = TITLE_FROM_ROOT.parent  # T/Title
T_ROOT = TITLE_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(REPO_ROOT))  # Repository root for T.Database, T.State imports
sys.path.insert(0, str(SCRIPT_DIR))  # Current directory for local imports
sys.path.insert(0, str(T_ROOT / "Idea" / "Model" / "src"))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model"))

# Import title generator
try:
    from title_generator import (
        TitleGenerator,
        TitleConfig,
        TitleVariant,
        generate_titles_from_idea,
    )
    TITLE_GENERATOR_AVAILABLE = True
except ImportError as e:
    TITLE_GENERATOR_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import Idea model
try:
    from idea import Idea, ContentGenre
    IDEA_MODEL_AVAILABLE = True
except ImportError:
    IDEA_MODEL_AVAILABLE = False

# Try to import database
try:
    from Model.Database.repositories.title_repository import TitleRepository
    from Model.Database.repositories.story_repository import StoryRepository
    from Model.Database.models.story import Story
    from Model.State.constants.state_names import StoryState
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Try to import StoryTitleService for state-based workflow
try:
    from story_title_service import StoryTitleService, process_stories_without_titles, AIUnavailableError
    SERVICE_AVAILABLE = True
except ImportError:
    SERVICE_AVAILABLE = False
    # Define a placeholder exception if import fails
    class AIUnavailableError(Exception):
        pass

# Try to import AI title generator for local Ollama-based generation
try:
    from ai_title_generator import AITitleGenerator, AITitleConfig, generate_ai_titles_from_idea, AIUnavailableError as AIGenUnavailableError
    AI_TITLE_GENERATOR_AVAILABLE = True
except ImportError:
    AI_TITLE_GENERATOR_AVAILABLE = False
    # Define a placeholder exception if import fails
    class AIGenUnavailableError(Exception):
        pass

# Try to import SimpleIdeaDatabase for fetching Idea content
try:
    from simple_idea_db import SimpleIdeaDatabase
    SIMPLE_IDEA_DB_AVAILABLE = True
except ImportError:
    SIMPLE_IDEA_DB_AVAILABLE = False

# Try to import Config for database path management
try:
    from src.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


def get_database_paths() -> tuple:
    """Get the database paths for Title and Story databases.
    
    Returns database paths from Config if available, otherwise falls back
    to C:/PrismQ/db.s3db for both.
    
    Returns:
        Tuple of (title_db_path, story_db_path)
    """
    if CONFIG_AVAILABLE:
        config = Config(interactive=False)
        # Both Title and Story use the same database file
        return config.database_path, config.database_path
    else:
        # Fallback to C:/PrismQ/db.s3db
        default_path = str(Path("C:/PrismQ") / "db.s3db")
        return default_path, default_path


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


# =============================================================================
# Input Parsing
# =============================================================================

def parse_idea_input(text: str, logger: Optional[logging.Logger] = None) -> Optional[Idea]:
    """Parse input text and create an Idea object.
    
    Handles:
    - Plain text (treated as title/concept)
    - JSON data with idea fields
    
    Args:
        text: Input text (any format)
        logger: Optional logger for debug output
        
    Returns:
        Idea object or None if parsing fails
    """
    text = text.strip()
    
    if logger:
        logger.info(f"Parsing input text ({len(text)} chars)")
    
    # Try to parse as JSON
    if text.startswith('{'):
        try:
            data = json.loads(text)
            if logger:
                logger.info(f"Detected JSON input with {len(data)} fields")
                logger.debug(f"JSON fields: {list(data.keys())}")
            
            # Create Idea from JSON data
            title = data.get('title') or data.get('story_title') or 'Untitled'
            concept = data.get('concept') or data.get('description') or ''
            
            # Try to parse genre
            genre = ContentGenre.OTHER
            genre_str = data.get('genre', '').lower()
            if genre_str:
                genre_map = {
                    'horror': ContentGenre.HORROR,
                    'educational': ContentGenre.EDUCATIONAL,
                    'entertainment': ContentGenre.ENTERTAINMENT,
                    'mystery': ContentGenre.MYSTERY,
                    'drama': ContentGenre.DRAMA,
                    'sci-fi': ContentGenre.SCI_FI,
                    'science fiction': ContentGenre.SCI_FI,
                    'fantasy': ContentGenre.FANTASY,
                    'romance': ContentGenre.ROMANCE,
                    'thriller': ContentGenre.THRILLER,
                    'comedy': ContentGenre.COMEDY,
                }
                genre = genre_map.get(genre_str, ContentGenre.OTHER)
            
            idea = Idea(
                title=title,
                concept=concept,
                genre=genre,
                themes=data.get('themes', []),
                keywords=data.get('keywords', []),
            )
            
            if logger:
                logger.info(f"Created Idea: '{title}'")
            
            return idea
            
        except json.JSONDecodeError as e:
            if logger:
                logger.warning(f"JSON parse failed: {e}")
    
    # Plain text handling - treat as title/concept
    if logger:
        logger.info("Processing as plain text")
    
    idea = Idea(
        title=text[:100] if len(text) <= 100 else text[:97] + "...",
        concept=text if len(text) > 100 else "",
        genre=ContentGenre.OTHER,
    )
    
    if logger:
        logger.info(f"Created Idea from plain text: '{idea.title}'")
    
    return idea


# =============================================================================
# Interactive Mode
# =============================================================================

def run_interactive_mode(preview: bool = False, debug: bool = False):
    """Run the interactive title generation mode.
    
    Args:
        preview: If True, don't save to database (preview/test mode)
        debug: If True, enable extensive debug logging
    """
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"title_from_idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler()
            ]
        )
        logger = logging.getLogger('PrismQ.Title.From.Idea')
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")
    
    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
    print_header(f"PrismQ Title From Idea - {mode_text}")
    
    # Check module availability
    if not TITLE_GENERATOR_AVAILABLE:
        print_error(f"Title generator module not available: {IMPORT_ERROR}")
        if logger:
            logger.error(f"Module import failed: {IMPORT_ERROR}")
        return 1
    
    if not IDEA_MODEL_AVAILABLE:
        print_error("Idea model not available")
        return 1
    
    print_success("Title generator module loaded")
    if logger:
        logger.info("Title generator module loaded successfully")
    
    if preview:
        print_warning("Preview mode - titles will NOT be saved to database")
        print_info("This mode is for testing and tuning. Check logs for details.")
    else:
        if DB_AVAILABLE:
            print_success("Database module available")
        else:
            print_warning("Database module not available - will run in preview mode")
            preview = True
    
    # Interactive loop
    print_section("Enter Idea Input")
    print("Type or paste your idea (text, JSON, or title/concept).")
    print("Press Enter to submit, or type 'quit' to exit.\n")
    
    while True:
        print(f"{Colors.CYAN}>>> {Colors.END}", end="")
        
        try:
            line = input().strip()
            if line.lower() == 'quit':
                print_info("Exiting...")
                if logger:
                    logger.info("User requested exit")
                return 0
            
            if not line:
                continue
            
            input_text = line
            
        except EOFError:
            print_info("Exiting...")
            return 0
        except KeyboardInterrupt:
            print("\n")
            print_info("Interrupted. Type 'quit' to exit.")
            continue
        
        if logger:
            logger.info(f"Received input: {len(input_text)} chars")
            logger.debug(f"Input text:\n{input_text[:500]}...")
        
        # Parse input to create Idea
        print_section("Processing Input")
        idea = parse_idea_input(input_text, logger)
        
        if not idea:
            print_error("Could not parse input as idea")
            continue
        
        print(f"  Title: {Colors.BOLD}{idea.title}{Colors.END}")
        if idea.concept:
            concept_preview = idea.concept[:100] + '...' if len(idea.concept) > 100 else idea.concept
            print(f"  Concept: {concept_preview}")
        print(f"  Genre: {idea.genre.value if hasattr(idea.genre, 'value') else idea.genre}")
        
        # Generate title variants using AI (required - no fallback)
        print_section("Generating Title Variants")
        
        titles = []
        ai_generator = None
        
        # AI title generator is required - no fallback to template-based generation
        if not AI_TITLE_GENERATOR_AVAILABLE:
            print_error("AI title generator module not available")
            print_error("AI generation is required - no fallback available")
            if logger:
                logger.error("AI title generator module not imported - cannot proceed")
            raise AIGenUnavailableError("AI title generator module not available")
        
        try:
            ai_generator = AITitleGenerator()
            if not ai_generator.is_available():
                print_error("AI (Ollama) not available")
                print_error("Please ensure Ollama is running with the required model")
                print_info("  1. Start Ollama: ollama serve")
                print_info("  2. Pull model: ollama pull qwen2.5:14b-instruct")
                if logger:
                    logger.error("Ollama not available - cannot proceed")
                raise AIGenUnavailableError("Ollama not available - AI is required for title generation")
            
            print_success("AI title generation available (Ollama)")
            if logger:
                logger.info("AI title generation available via Ollama")
                
        except AIGenUnavailableError:
            raise  # Re-raise AIGenUnavailableError
        except Exception as e:
            print_error(f"AI generator init failed: {e}")
            if logger:
                logger.error(f"AI generator initialization failed: {e}")
            raise AIGenUnavailableError(f"AI generator initialization failed: {e}") from e
        
        try:
            print_info(f"Creating 10 title variants...")
            if logger:
                logger.info("Creating 10 title variants")
            
            # Use AI-powered title generation via Ollama (required)
            print_info("Using local AI (Ollama) for title generation...")
            if logger:
                logger.info("Generating titles using AI (Ollama)")
            titles = ai_generator.generate_from_idea(idea, num_variants=10)
                
        except AIGenUnavailableError as ai_err:
            print_error(f"AI generation failed: {ai_err}")
            print_error("AI is required - no fallback available")
            if logger:
                logger.error(f"AI generation failed: {ai_err}")
            raise
        except Exception as e:
            print_error(f"Error creating title variants: {e}")
            if logger:
                logger.exception("Title variant creation failed")
            continue
        
        # Display results
        print_section(f"Generated {len(titles)} Title Variant(s)")
        
        for i, title_variant in enumerate(titles):
            print(f"\n{Colors.GREEN}{'─' * 50}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}  Variant {i+1}: {title_variant.style}{Colors.END}")
            print(f"{Colors.GREEN}{'─' * 50}{Colors.END}")
            print(f"  Title: {title_variant.text}")
            print(f"  Length: {title_variant.length} chars")
            print(f"  Score: {title_variant.score:.2f}")
            print(f"  Keywords: {', '.join(title_variant.keywords[:5])}")
            
            if logger:
                logger.info(f"Variant {i+1}: {title_variant.style}")
                logger.debug(f"Variant {i+1} data: {title_variant.to_dict()}")
        
        # Save to database (if not preview mode)
        if not preview and DB_AVAILABLE:
            print_section("Database Operations")
            save_choice = input(f"{Colors.CYAN}Save to database? (y/n) [y]: {Colors.END}").strip().lower()
            if save_choice != 'n':
                print_info("Saving to database...")
                if logger:
                    logger.info(f"Saving {len(titles)} titles to database")
                # TODO: Implement actual DB save when TitleRepository is properly integrated
                print_warning("Database save not yet implemented - titles were created but not persisted")
            else:
                print_info("Skipped database save")
                if logger:
                    logger.info("User skipped database save")
        elif preview:
            print_section("Preview Mode - No Database Save")
            print_info(f"Created {len(titles)} title variant(s) - NOT saved to database")
            if logger:
                logger.info(f"Preview mode: {len(titles)} titles created but not saved")
        
        # Output as JSON option
        json_choice = input(f"\n{Colors.CYAN}Output as JSON? (y/n) [n]: {Colors.END}").strip().lower()
        if json_choice == 'y':
            print_section("JSON Output")
            titles_json = [t.to_dict() for t in titles]
            print(json.dumps(titles_json, indent=2, ensure_ascii=False))
            if logger:
                logger.info("User requested JSON output")
        
        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print("Enter new idea or type 'quit' to exit.\n")


def run_state_workflow_mode(db_path: Optional[str] = None, preview: bool = False, debug: bool = False):
    """Run the state-based workflow mode for title generation.
    
    This mode automatically processes Stories with state PrismQ.T.Title.From.Idea,
    generates titles using AI with similarity checking, and transitions to the next state.
    
    IMPORTANT: This mode requires AI (Ollama) to be running. If AI is unavailable,
    the script will raise an error and stop - no fallback titles will be generated.
    
    Args:
        db_path: Path to the SQLite database file. If None, uses default from
                 Config (C:/PrismQ/db.s3db).
        preview: If True, don't save to database (preview/test mode).
        debug: If True, enable extensive debug logging.
        
    Raises:
        AIUnavailableError: If AI (Ollama) is not available for title generation.
    """
    import sqlite3
    
    # Use default database paths if not provided
    if db_path is None:
        title_db_path, story_db_path = get_database_paths()
        db_path = title_db_path  # Both use the same database
    
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"title_from_idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler()
            ]
        )
        logger = logging.getLogger('PrismQ.Title.From.Idea')
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")
    
    # Print header - RUN MODE as specified in problem statement
    print_header("PrismQ.T.Title.From.Idea - RUN MODE")
    
    # Check module availability
    if not TITLE_GENERATOR_AVAILABLE:
        print_error(f"Title generator module not available: {IMPORT_ERROR}")
        return 1
    
    if not SERVICE_AVAILABLE:
        print_error("StoryTitleService not available")
        return 1
    
    if not DB_AVAILABLE:
        print_error("Database modules not available")
        return 1
    
    if not SIMPLE_IDEA_DB_AVAILABLE:
        print_error("SimpleIdeaDatabase not available - cannot fetch Idea content")
        return 1
    
    print_success("All modules loaded successfully")
    
    # Connect to database
    print_section("Environment Setup")
    print_info(f"Database path: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print_success(f"Connected to database: {db_path}")
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        return 1
    
    # Initialize service and check AI availability
    service = StoryTitleService(conn)
    
    # Check AI availability - fail fast if AI is not available
    print_section("Checking AI Availability")
    if not service.is_ai_available():
        print_error("AI title generation is NOT available!")
        print_error("Ollama must be running with the required model (qwen2.5:14b-instruct)")
        print_info("Please start Ollama and ensure the model is loaded:")
        print_info("  1. Start Ollama: ollama serve")
        print_info("  2. Pull model: ollama pull qwen2.5:14b-instruct")
        print_info("  3. Re-run this script")
        conn.close()
        raise AIUnavailableError(
            "AI title generation unavailable. Ollama must be running with qwen2.5:14b-instruct model. "
            "No fallback titles will be generated."
        )
    print_success("AI title generation is available")
    
    # Connect to Idea database to fetch Idea content
    # Use the same database path for Idea table (it's in the same database)
    idea_db = SimpleIdeaDatabase(db_path)
    idea_db.connect()
    print_success("Connected to Idea database")
    
    # Find Stories with state TITLE_FROM_IDEA
    print_section("Finding Stories for Title Generation")
    stories_to_process = service.get_stories_without_titles()
    
    if not stories_to_process:
        print_info("No Stories found with state PrismQ.T.Title.From.Idea")
        print_info("Make sure Stories are created using PrismQ.T.Story.From.Idea first")
        idea_db.close()
        conn.close()
        return 0
    
    print_success(f"Found {len(stories_to_process)} Stories ready for title generation")
    
    # Track processing results
    processed_count = 0
    error_count = 0
    
    # Process each story
    for i, story in enumerate(stories_to_process, 1):
        print_section(f"Processing Story {i}/{len(stories_to_process)} (ID: {story.id})")
        print(f"  Idea ID: {story.idea_id}")
        
        # Get sibling stories for context
        siblings = service.get_sibling_stories(story)
        sibling_titles = service.get_sibling_titles(story)
        
        print(f"  Sibling Stories: {len(siblings)}")
        print(f"  Existing Sibling Titles: {len(sibling_titles)}")
        
        if sibling_titles:
            print(f"\n  {Colors.GRAY}Existing titles from same Idea:{Colors.END}")
            for st in sibling_titles[:5]:  # Show up to 5
                print(f"    - {st.text[:60]}{'...' if len(st.text) > 60 else ''}")
            if len(sibling_titles) > 5:
                print(f"    ... and {len(sibling_titles) - 5} more")
        
        # Get Idea from story.idea_json first, then fall back to fetching from Idea database
        idea = None
        if story.idea_json:
            try:
                idea_data = json.loads(story.idea_json)
                if IDEA_MODEL_AVAILABLE:
                    idea = Idea.from_dict(idea_data)
                    print_info(f"Using embedded idea_json data")
            except (json.JSONDecodeError, Exception) as e:
                if logger:
                    logger.warning(f"Failed to parse idea_json: {e}")
        
        # If no idea_json, fetch from Idea database using story.idea_id
        if idea is None and story.idea_id is not None:
            try:
                idea_id = int(story.idea_id)
                idea_dict = idea_db.get_idea(idea_id)
                if idea_dict:
                    # Create Idea object from SimpleIdea data
                    idea_text = idea_dict.get('text', '')
                    if idea_text and IDEA_MODEL_AVAILABLE:
                        # Truncate title to reasonable length (max 100 chars)
                        MAX_TITLE_LENGTH = 100
                        if len(idea_text) <= MAX_TITLE_LENGTH:
                            title = idea_text
                        else:
                            title = idea_text[:MAX_TITLE_LENGTH - 3] + "..."
                        idea = Idea(
                            title=title,
                            concept=idea_text,
                            genre=ContentGenre.OTHER
                        )
                        print_info(f"Fetched Idea from database (ID: {idea_id})")
                        if logger:
                            logger.info(f"Created Idea from database: {idea_text[:50]}...")
                    else:
                        print_warning(f"Idea {idea_id} has no text content")
                else:
                    print_warning(f"Idea {idea_id} not found in database")
            except (ValueError, TypeError) as e:
                print_warning(f"Invalid idea_id format: {story.idea_id}")
                if logger:
                    logger.warning(f"Failed to parse idea_id: {e}")
        
        # AI title generation requires an Idea - no fallback
        if idea is None:
            print_error(f"Cannot generate title: No Idea data available for Story {story.id}")
            print_error("Ensure the Idea exists in the database with valid text content")
            error_count += 1
            continue
        
        # Generate title variants using AI
        print_section("Generating AI Title Variants")
        
        try:
            # Use service constant for number of variants
            num_variants = StoryTitleService.NUM_VARIANTS
            
            print_info(f"Generating {num_variants} variants from Idea: '{idea.title[:50]}...'")
            
            # Generate variants using AI through the service
            variants = service.generate_title_variants(idea, num_variants=num_variants)
            
            if not variants:
                raise AIUnavailableError("AI returned no title variants")
            
            # Select best title using similarity check
            print_section("Selecting Best Title (with Similarity Check)")
            best_variant, similar_titles = service.select_best_title(variants, story)
            
            # Display all variants
            print(f"\n  {Colors.CYAN}Generated {len(variants)} AI Title Variants:{Colors.END}")
            for j, v in enumerate(variants, 1):
                is_best = v.text == best_variant.text
                marker = f"{Colors.GREEN}★{Colors.END}" if is_best else " "
                print(f"  {marker} {j}. [{v.style}] {v.text}")
                print(f"       Length: {v.length} chars | Score: {v.score:.2f}")
            
            # Show similarity warnings
            if similar_titles:
                print(f"\n  {Colors.YELLOW}⚠ Similarity warnings:{Colors.END}")
                for sim_title, sim_score in similar_titles:
                    print(f"    - {sim_score:.0%} similar to: '{sim_title[:50]}...'")
            
            # Show selected best
            print(f"\n  {Colors.GREEN}Selected Best Title:{Colors.END}")
            print(f"    {best_variant.text}")
            print(f"    Style: {best_variant.style} | Score: {best_variant.score:.2f}")
            
            if preview:
                print_warning("PREVIEW MODE - Title NOT saved to database")
                print_info(f"Would transition state: TITLE_FROM_IDEA → SCRIPT_FROM_IDEA_TITLE")
                processed_count += 1
            else:
                # Save title and update state
                print_section("Database Operations")
                try:
                    title = service.generate_title_for_story(story, idea)
                    if title:
                        print_success(f"Title saved with ID: {title.id}")
                        print_success(f"State changed to: PrismQ.T.Script.From.Idea.Title")
                        processed_count += 1
                    else:
                        print_warning("Story already has a title, skipped")
                except Exception as e:
                    print_error(f"Failed to save title: {e}")
                    if logger:
                        logger.exception("Database save failed")
                    error_count += 1
                    
        except AIUnavailableError as e:
            print_error(f"AI title generation failed: {e}")
            print_error("Stopping processing - AI is required for title generation")
            if logger:
                logger.error(f"AI unavailable: {e}")
            idea_db.close()
            conn.close()
            raise  # Re-raise to stop processing
    
    # Summary
    print_section("Processing Summary")
    print(f"  Total Stories found: {len(stories_to_process)}")
    print(f"  Successfully processed: {processed_count}")
    print(f"  Errors: {error_count}")
    print(f"  Mode: {'PREVIEW (no changes saved)' if preview else 'RUN (changes saved)'}")
    print(f"  Next state: PrismQ.T.Script.From.Idea.Title")
    
    idea_db.close()
    conn.close()
    print_success("Processing complete!")
    return 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Title Generation from Idea for PrismQ (AI-powered)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Continuous mode (default - automatic processing without user input)
  python title_from_idea_interactive.py                    # Process Stories from default DB
  python title_from_idea_interactive.py --db /path/to/db.s3db  # Use custom DB
  python title_from_idea_interactive.py --preview          # Preview without saving
  
  # Interactive mode (manual input)
  python title_from_idea_interactive.py --interactive      # Interactive mode with DB save
  python title_from_idea_interactive.py --interactive --preview  # Preview mode (no DB save)
  python title_from_idea_interactive.py --interactive --debug    # Debug mode with extensive logging

Note: AI (Ollama) is REQUIRED for title generation. No template fallback available.
        """
    )
    
    parser.add_argument('--preview', '-p', action='store_true',
                       help='Preview mode - do not save to database')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug logging (extensive output)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive mode (manual input instead of continuous)')
    parser.add_argument('--db', type=str, default=None,
                       help='Path to SQLite database (default: from Config or C:/PrismQ/db.s3db)')
    
    args = parser.parse_args()
    
    if args.interactive:
        return run_interactive_mode(preview=args.preview, debug=args.debug)
    else:
        # Default: continuous mode (auto-process Stories without user input)
        return run_state_workflow_mode(args.db, preview=args.preview, debug=args.debug)


if __name__ == '__main__':
    sys.exit(main())
