#!/usr/bin/env python3
"""Title Generation CLI for PrismQ (AI-powered).

This script provides title generation from ideas using local AI (Ollama).
AI is REQUIRED - no template-based fallback is available.

Usage:
    python title_from_idea_interactive.py                    # Process Stories from default DB
    python title_from_idea_interactive.py --db /path/db.s3db # Custom database path

Requirements:
    - Ollama must be running with qwen3:32b model
    - AI is required - script will fail if Ollama is unavailable

Note: This module does NOT support manual/interactive modes in production workflow.
      Manual mode is only for development/debugging purposes.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup paths - Now in T/Title/From/Idea/src/
SCRIPT_DIR = Path(__file__).parent.absolute()
TITLE_FROM_IDEA_ROOT = SCRIPT_DIR.parent  # T/Title/From/Idea
TITLE_FROM_ROOT = TITLE_FROM_IDEA_ROOT.parent  # T/Title/From
TITLE_ROOT = TITLE_FROM_ROOT.parent  # T/Title
T_ROOT = TITLE_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root
_WORKFLOW_JSON = (
    REPO_ROOT / "_meta" / "scripts" / "03_PrismQ.T.Title.From.Idea" / "workflow.json"
)


def _load_worker_count() -> int:
    """Read worker_count from workflow.json. Returns 1 if file missing or invalid."""
    import json as _json
    try:
        data = _json.loads(_WORKFLOW_JSON.read_text(encoding="utf-8"))
        val = int(data.get("worker_count", 1))
        return max(1, val)
    except Exception:
        return 1


# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))  # Current directory for local imports
sys.path.insert(0, str(T_ROOT / "Idea" / "Model" / "src"))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model"))
sys.path.insert(0, str(REPO_ROOT))  # Repository root for T.Database, T.State imports

# Import Config and IdeaTable from shared src module - same pattern as Script 01
# Must be imported here, before other imports (story_title_service, ai_title_generator)
# that insert T at sys.path[0], which would shadow REPO_ROOT/src with T/src
# (a different package that does not contain IdeaTable).
try:
    from src.config import Config
    from src.idea import IdeaTable, setup_idea_table

    IDEA_TABLE_AVAILABLE = True
    CONFIG_AVAILABLE = True
except ImportError:
    IDEA_TABLE_AVAILABLE = False
    CONFIG_AVAILABLE = False

# Import title generator
try:
    from title_generator import (
        TitleConfig,
        TitleGenerator,
        TitleVariant,
        generate_titles_from_idea,
    )

    TITLE_GENERATOR_AVAILABLE = True
except ImportError as e:
    TITLE_GENERATOR_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import Idea model
try:
    from idea import ContentGenre, Idea

    IDEA_MODEL_AVAILABLE = True
except ImportError:
    IDEA_MODEL_AVAILABLE = False

# Try to import database
try:
    from Model.Database.models.story import Story
    from Model.Database.repositories.story_repository import StoryRepository
    from Model.Database.repositories.title_repository import TitleRepository
    from Model.State.constants.state_names import StoryState, StateNames

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Try to import StoryTitleService for state-based workflow
try:
    from story_title_service import (
        AIUnavailableError,
        StoryTitleService,
        process_stories_without_titles,
    )

    SERVICE_AVAILABLE = True
except ImportError:
    SERVICE_AVAILABLE = False

    # Define a placeholder exception if import fails
    class AIUnavailableError(Exception):
        pass


# Try to import AI title generator for local Ollama-based generation
try:
    from ai_title_generator import (
        AITitleConfig,
        AITitleGenerator,
    )
    from ai_title_generator import AIUnavailableError as AIGenUnavailableError
    from ai_title_generator import (
        generate_ai_titles_from_idea,
    )

    AI_TITLE_GENERATOR_AVAILABLE = True
except ImportError:
    AI_TITLE_GENERATOR_AVAILABLE = False

    # Define a placeholder exception if import fails
    class AIGenUnavailableError(Exception):
        pass


# Number of parallel threads — should match OLLAMA_NUM_PARALLEL
PARALLEL_WORKERS = int(os.getenv("PRISMQ_PARALLEL_WORKERS", "4"))


def _worker_process_story(story, db_path: str) -> tuple:
    """Process one story in a dedicated thread with its own database connection.

    Returns:
        (success, story_id, title_text_or_None, error_or_None)
        On AI unavailability, error starts with "AI_UNAVAILABLE:" prefix.
    """
    import sqlite3 as _sqlite3

    conn = _sqlite3.connect(db_path, timeout=30)
    conn.row_factory = _sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    idea_db_local = None
    try:
        service = StoryTitleService(conn, auto_create_schema=False)
        idea_db_local = setup_idea_table(db_path)

        # Fetch Idea content from DB
        idea = None
        if story.idea_id is not None:
            try:
                idea_id = int(story.idea_id)
                idea_dict = idea_db_local.get_idea(idea_id)
                if idea_dict:
                    idea_text = idea_dict.get("text", "")
                    if idea_text and IDEA_MODEL_AVAILABLE:
                        title_text = (
                            idea_text if len(idea_text) <= 100 else idea_text[:97] + "..."
                        )
                        idea = Idea(title=title_text, concept=idea_text, genre=ContentGenre.OTHER)
            except (ValueError, TypeError):
                pass

        if idea is None:
            return (False, story.id, None, "No idea data available")

        # Generate title via AI — I/O bound, releases GIL while waiting for Ollama
        try:
            variant = service.generate_title(idea)
        except AIUnavailableError as e:
            return (False, story.id, None, f"AI_UNAVAILABLE:{e}")

        if not variant:
            return (False, story.id, None, "AI returned no title")

        # Save to DB and transition state
        title_obj = service.generate_title_for_story(story, idea, variant)
        if title_obj:
            return (True, story.id, variant.text, None)
        else:
            return (False, story.id, None, "Story already has a title")

    except Exception as e:
        return (False, story.id, None, str(e))
    finally:
        conn.close()
        if idea_db_local:
            try:
                idea_db_local.close()
            except Exception:
                pass


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

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


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
    if text.startswith("{"):
        try:
            data = json.loads(text)
            if logger:
                logger.info(f"Detected JSON input with {len(data)} fields")
                logger.debug(f"JSON fields: {list(data.keys())}")

            # Create Idea from JSON data
            title = data.get("title") or data.get("story_title") or "Untitled"
            concept = data.get("concept") or data.get("description") or ""

            # Try to parse genre
            genre = ContentGenre.OTHER
            genre_str = data.get("genre", "").lower()
            if genre_str:
                genre_map = {
                    "horror": ContentGenre.HORROR,
                    "educational": ContentGenre.EDUCATIONAL,
                    "entertainment": ContentGenre.ENTERTAINMENT,
                    "mystery": ContentGenre.MYSTERY,
                    "drama": ContentGenre.DRAMA,
                    "sci-fi": ContentGenre.SCI_FI,
                    "science fiction": ContentGenre.SCI_FI,
                    "fantasy": ContentGenre.FANTASY,
                    "romance": ContentGenre.ROMANCE,
                    "thriller": ContentGenre.THRILLER,
                    "comedy": ContentGenre.COMEDY,
                }
                genre = genre_map.get(genre_str, ContentGenre.OTHER)

            idea = Idea(
                title=title,
                concept=concept,
                genre=genre,
                themes=data.get("themes", []),
                keywords=data.get("keywords", []),
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


def run_interactive_mode(preview: bool = False, debug: bool = False, manual: bool = False):
    """Run the interactive title generation mode.

    Args:
        preview: If True, don't save to database (preview/test mode)
        debug: If True, enable extensive debug logging
        manual: If True, enables manual mode where prompts are shown
               and responses are entered by the user
    """
    # Setup logging
    logger = None
    if debug or preview or manual:
        log_filename = f"title_from_idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler(),
            ],
        )
        logger = logging.getLogger("PrismQ.Title.From.Idea")
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}, Manual: {manual}")
        print_info(f"Logging to: {log_path}")

    # Print header
    if manual:
        mode_text = "MANUAL MODE"
    elif preview:
        mode_text = "PREVIEW MODE"
    else:
        mode_text = "INTERACTIVE MODE"
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
            if line.lower() == "quit":
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
            concept_preview = (
                idea.concept[:100] + "..." if len(idea.concept) > 100 else idea.concept
            )
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
            ai_generator = AITitleGenerator(manual_mode=manual)
            if not ai_generator.is_available() and not manual:
                print_error("AI (Ollama) not available")
                print_error("Please ensure Ollama is running with the required model")
                print_info("  1. Start Ollama: ollama serve")
                print_info("  2. Pull model: ollama pull qwen3:32b")
                if logger:
                    logger.error("Ollama not available - cannot proceed")
                raise AIGenUnavailableError(
                    "Ollama not available - AI is required for title generation"
                )

            if manual:
                print_warning("Manual mode - you will provide AI responses manually")
                print_info("Prompts will be displayed and you'll paste responses")
            else:
                print_success("AI title generation available (Ollama)")
            if logger:
                logger.info(f"AI title generation - Manual mode: {manual}")

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
            save_choice = (
                input(f"{Colors.CYAN}Save to database? (y/n) [y]: {Colors.END}").strip().lower()
            )
            if save_choice != "n":
                print_info("Saving to database...")
                if logger:
                    logger.info(f"Saving {len(titles)} titles to database")
                # TODO: Implement actual DB save when TitleRepository is properly integrated
                print_warning(
                    "Database save not yet implemented - titles were created but not persisted"
                )
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
        json_choice = (
            input(f"\n{Colors.CYAN}Output as JSON? (y/n) [n]: {Colors.END}").strip().lower()
        )
        if json_choice == "y":
            print_section("JSON Output")
            titles_json = [t.to_dict() for t in titles]
            print(json.dumps(titles_json, indent=2, ensure_ascii=False))
            if logger:
                logger.info("User requested JSON output")

        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print("Enter new idea or type 'quit' to exit.\n")


def run_state_workflow_mode(
    db_path: Optional[str] = None, debug: bool = False, worker_id: int = 0
):
    """Run the state-based workflow mode for title generation in continuous mode.

    This mode automatically and continuously processes Stories with state PrismQ.T.Title.From.Idea,
    generates titles using AI with similarity checking, and transitions to the next state.
    
    Runs continuously with 1ms wait between iterations when processing items,
    and 30-second wait when no stories are found. Press Ctrl+C to stop.

    IMPORTANT: This mode requires AI (Ollama) to be running. If AI is unavailable,
    the script will raise an error and stop - no fallback titles will be generated.

    Args:
        db_path: Path to the SQLite database file. If None, uses default from
                 Config (C:/PrismQ/db.s3db).
        debug: If True, enable extensive debug logging.

    Raises:
        AIUnavailableError: If AI (Ollama) is not available for title generation.
    """
    import sqlite3
    import time

    # Use default database paths if not provided
    if db_path is None:
        title_db_path, story_db_path = get_database_paths()
        db_path = title_db_path  # Both use the same database

    # Setup logging
    logger = None
    if debug:
        log_filename = f"title_from_idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler(),
            ],
        )
        logger = logging.getLogger("PrismQ.Title.From.Idea")
        logger.info(f"Session started - Debug: {debug}")
        print_info(f"Logging to: {log_path}")

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

    if not IDEA_TABLE_AVAILABLE:
        print_error("IdeaTable not available - cannot fetch Idea content")
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
        print_error("Ollama must be running with the required model (qwen3:32b)")
        print_info("Please start Ollama and ensure the model is loaded:")
        print_info("  1. Start Ollama: ollama serve")
        print_info("  2. Pull model: ollama pull qwen3:32b")
        print_info("  3. Re-run this script")
        conn.close()
        raise AIUnavailableError(
            "AI title generation unavailable. Ollama must be running with qwen3:32b model. "
            "No fallback titles will be generated."
        )
    print_success("AI title generation is available")

    # Worker sharding configuration (only used when --worker-id >= 0)
    worker_count = _load_worker_count()
    if worker_id >= 0 and worker_count > 1:
        print_info(f"Worker sharding: worker {worker_id} of {worker_count} (stories where id % {worker_count} == {worker_id})")
    elif worker_id < 0:
        print_info(f"Threading: {PARALLEL_WORKERS} parallel threads (internal, no sharding)")
    else:
        print_info("Single worker mode (worker_count=1)")

    # Connect to Idea database to fetch Idea content
    # Use the same database path for Idea table (it's in the same database)
    idea_db = setup_idea_table(db_path)
    print_success("Connected to Idea database")

    run_count = 0
    total_processed = 0
    total_errors = 0
    
    try:
        while True:
            run_count += 1
            
            # Show run header for subsequent runs
            if run_count > 1:
                print(f"\n{Colors.CYAN}{'═' * 80}{Colors.END}")
                print(f"{Colors.CYAN}Run #{run_count} - Checking for new stories...{Colors.END}")
                print(f"{Colors.CYAN}{'═' * 80}{Colors.END}\n")

            # Find Stories with state TITLE_FROM_IDEA
            if run_count == 1:
                print_section("Finding Stories for Title Generation")
            
            stories_to_process = service.get_stories_without_titles()
            if worker_id >= 0 and worker_count > 1:
                stories_to_process = [s for s in stories_to_process if s.id % worker_count == worker_id]

            if not stories_to_process:
                if run_count == 1:
                    print_info("No Stories found with state PrismQ.T.Title.From.Idea")
                    print_info("Make sure Stories are created using PrismQ.T.Story.From.Idea first")
                    print_info("Waiting 30 seconds before checking again...")
                # Wait 30 seconds and check again
                time.sleep(30)
                continue

            if run_count == 1:
                print_success(f"Found {len(stories_to_process)} Stories ready for title generation")
            else:
                print_success(f"Found {len(stories_to_process)} new Stories")

            # Track processing results for this run
            processed_count = 0
            error_count = 0
            ai_unavailable_error = None
            total = len(stories_to_process)

            use_parallel = worker_id < 0

            if use_parallel:
                # Parallel mode: ThreadPoolExecutor — 4 Ollama calls in flight simultaneously
                print_info(f"Processing {total} stories with {PARALLEL_WORKERS} parallel threads...")
                with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
                    future_map = {
                        executor.submit(_worker_process_story, story, db_path): (i, story)
                        for i, story in enumerate(stories_to_process, 1)
                    }
                    for future in as_completed(future_map):
                        i, story = future_map[future]
                        success, sid, title_text, err = future.result()
                        if success:
                            print_success(f"[{i}/{total}] Story {sid}: \"{title_text}\"")
                            if logger:
                                logger.info(f"Story {sid}: '{title_text}'")
                            processed_count += 1
                        elif err and err.startswith("AI_UNAVAILABLE:"):
                            actual_err = err[len("AI_UNAVAILABLE:"):]
                            print_error(f"Story {sid}: AI unavailable — {actual_err}")
                            ai_unavailable_error = actual_err
                            for f in future_map:
                                f.cancel()
                            break
                        else:
                            print_warning(f"[{i}/{total}] Story {sid}: {err}")
                            if logger:
                                logger.warning(f"Story {sid}: {err}")
                            error_count += 1
            else:
                # Sequential mode: used when --worker-id is explicitly set (multiple bat windows)
                for i, story in enumerate(stories_to_process, 1):
                    success, sid, title_text, err = _worker_process_story(story, db_path)
                    if success:
                        print_success(f"[{i}/{total}] Story {sid}: \"{title_text}\"")
                        if logger:
                            logger.info(f"Story {sid}: '{title_text}'")
                        processed_count += 1
                    elif err and err.startswith("AI_UNAVAILABLE:"):
                        actual_err = err[len("AI_UNAVAILABLE:"):]
                        print_error(f"Story {sid}: AI unavailable — {actual_err}")
                        ai_unavailable_error = actual_err
                        break
                    else:
                        print_warning(f"[{i}/{total}] Story {sid}: {err}")
                        if logger:
                            logger.warning(f"Story {sid}: {err}")
                        error_count += 1

            if ai_unavailable_error:
                idea_db.close()
                conn.close()
                raise AIUnavailableError(f"AI unavailable: {ai_unavailable_error}")

            # Summary for this run
            total_processed += processed_count
            total_errors += error_count
            
            if processed_count > 0 or error_count > 0:
                print_section(f"Run #{run_count} Summary")
                print(f"  Stories processed in this run: {processed_count}")
                print(f"  Errors in this run: {error_count}")
                print(f"  Next state: {StateNames.CONTENT_FROM_IDEA_TITLE}")
            
            # Wait 1ms before next check
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print(f"\n\n{Colors.YELLOW}{'═' * 80}{Colors.END}")
        print(f"{Colors.YELLOW}Interrupted by user (Ctrl+C){Colors.END}")
        print(f"{Colors.YELLOW}{'═' * 80}{Colors.END}\n")
        print_section("Final Summary")
        print(f"  Total runs completed: {run_count}")
        print(f"  Total stories processed: {total_processed}")
        print(f"  Total errors: {total_errors}")
        print_success("Processing stopped gracefully")
        idea_db.close()
        conn.close()
        return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Title Generation from Idea for PrismQ (AI-powered)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python title_from_idea_interactive.py                    # Process Stories from default DB
  python title_from_idea_interactive.py --db /path/to/db.s3db  # Use custom DB
  
Note: 
  - AI (Ollama) is REQUIRED for title generation. No template fallback available.
        """,
    )

    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enable debug logging (extensive output)"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="[DEBUG ONLY] Run interactive mode - not for production workflow",
    )
    parser.add_argument(
        "--manual",
        "-m",
        action="store_true",
        help="[DEBUG ONLY] Manual mode - not for production workflow",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Path to SQLite database (default: from Config or C:/PrismQ/db.s3db)",
    )
    parser.add_argument(
        "--worker-id",
        type=int,
        default=-1,
        help=(
            "Worker shard index (0-based). Default -1 = internal multithreading (recommended). "
            "Set to 0,1,2... when running multiple separate bat windows with sharding."
        ),
    )

    args = parser.parse_args()

    if args.interactive or args.manual:
        return run_interactive_mode(debug=args.debug, manual=args.manual)
    else:
        return run_state_workflow_mode(args.db, debug=args.debug, worker_id=args.worker_id)


if __name__ == "__main__":
    sys.exit(main())
