#!/usr/bin/env python3
"""Interactive Content Generation CLI for PrismQ.

This script provides an interactive mode for generating scripts from ideas and titles.
It waits for user input, processes it through the script generator, and
optionally saves to the database.

Usage:
    python script_from_idea_title_interactive.py                    # Interactive mode with DB save
    python script_from_idea_title_interactive.py --preview          # Preview mode (no DB save)
    python script_from_idea_title_interactive.py --preview --debug  # Debug mode with extensive logging

Modes:
    Default: Creates scripts and saves to database
    Preview: Creates scripts for testing without saving (extensive logging)
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup paths - Now in T/Content/From/Idea/Title/src/
SCRIPT_DIR = Path(__file__).parent.absolute()
SCRIPT_FROM_TITLE_ROOT = SCRIPT_DIR.parent  # T/Content/From/Idea/Title
SCRIPT_FROM_IDEA_ROOT = SCRIPT_FROM_TITLE_ROOT.parent  # T/Content/From/Idea
SCRIPT_FROM_ROOT = SCRIPT_FROM_IDEA_ROOT.parent  # T/Content/From
SCRIPT_ROOT = SCRIPT_FROM_ROOT.parent  # T/Content
T_ROOT = SCRIPT_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))  # Current directory for local imports
sys.path.insert(0, str(T_ROOT / "Idea" / "Model" / "src"))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model"))

# Import script generator
try:
    from script_generator import (
        PlatformTarget,
        ScriptGenerator,
        ScriptGeneratorConfig,
        ScriptSection,
        ScriptStructure,
        ScriptTone,
        ScriptV1,
    )

    SCRIPT_GENERATOR_AVAILABLE = True
except ImportError as e:
    SCRIPT_GENERATOR_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import Idea model
try:
    from idea import ContentGenre, Idea

    IDEA_MODEL_AVAILABLE = True
except ImportError:
    IDEA_MODEL_AVAILABLE = False

# Try to import database
try:
    from Model.Database.repositories.content_repository import ContentRepository

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


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


def parse_input(text: str, logger: Optional[logging.Logger] = None) -> tuple:
    """Parse input text and extract idea and title.

    Handles:
    - JSON with idea and title fields
    - Plain text (treated as title, concept generated)

    Args:
        text: Input text (any format)
        logger: Optional logger for debug output

    Returns:
        Tuple of (Idea, title_text) or (None, None) if parsing fails
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

            # Extract title
            title_text = data.get("title") or data.get("story_title") or "Untitled Story"

            # Create Idea from JSON data
            idea_title = data.get("idea_title") or title_text
            concept = data.get("concept") or data.get("description") or title_text

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
                title=idea_title,
                concept=concept,
                genre=genre,
                themes=data.get("themes", []),
                keywords=data.get("keywords", []),
                hook=data.get("hook", ""),
                premise=data.get("premise", ""),
                synopsis=data.get("synopsis", ""),
            )

            if logger:
                logger.info(f"Created Idea: '{idea_title}' with title: '{title_text}'")

            return idea, title_text

        except json.JSONDecodeError as e:
            if logger:
                logger.warning(f"JSON parse failed: {e}")

    # Plain text handling - treat as title
    if logger:
        logger.info("Processing as plain text")

    title_text = text[:100] if len(text) <= 100 else text[:97] + "..."

    idea = Idea(
        title=title_text,
        concept=text if len(text) > 50 else f"Story about: {text}",
        genre=ContentGenre.OTHER,
    )

    if logger:
        logger.info(f"Created Idea from plain text: '{idea.title}'")

    return idea, title_text


# =============================================================================
# Interactive Mode
# =============================================================================


def run_interactive_mode(preview: bool = False, debug: bool = False):
    """Run the interactive script generation mode.

    Args:
        preview: If True, don't save to database (preview/test mode)
        debug: If True, enable extensive debug logging
    """
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"script_from_idea_title_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler(),
            ],
        )
        logger = logging.getLogger("PrismQ.Content.From.Idea.Title")
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")

    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
    print_header(f"PrismQ Content From Idea+Title - {mode_text}")

    # Check module availability
    if not SCRIPT_GENERATOR_AVAILABLE:
        print_error(f"Content generator module not available: {IMPORT_ERROR}")
        if logger:
            logger.error(f"Module import failed: {IMPORT_ERROR}")
        return 1

    if not IDEA_MODEL_AVAILABLE:
        print_error("Idea model not available")
        return 1

    print_success("Content generator module loaded")
    if logger:
        logger.info("Content generator module loaded successfully")

    if preview:
        print_warning("Preview mode - scripts will NOT be saved to database")
        print_info("This mode is for testing and tuning. Check logs for details.")
    else:
        if DB_AVAILABLE:
            print_success("Database module available")
        else:
            print_warning("Database module not available - will run in preview mode")
            preview = True

    # Show available options
    print_section("Content Generation Options")
    print("  Structure: hook_deliver_cta, three_act, problem_solution, story")
    print("  Tone: engaging, mysterious, educational, dramatic, conversational")
    print("  Platform: youtube_short, youtube_medium, youtube_long, tiktok, instagram_reel")

    # Interactive loop
    print_section("Enter Input")
    print("Enter idea+title (as JSON or plain text for title).")
    print('Example JSON: {"title": "Story Title", "concept": "Story concept", "genre": "horror"}')
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

        # Parse input
        print_section("Processing Input")
        idea, title = parse_input(input_text, logger)

        if not idea or not title:
            print_error("Could not parse input")
            continue

        print(f"  Idea Title: {Colors.BOLD}{idea.title}{Colors.END}")
        print(f"  Content Title: {Colors.BOLD}{title}{Colors.END}")
        if idea.concept:
            concept_preview = (
                idea.concept[:100] + "..." if len(idea.concept) > 100 else idea.concept
            )
            print(f"  Concept: {concept_preview}")
        print(f"  Genre: {idea.genre.value if hasattr(idea.genre, 'value') else idea.genre}")

        # Generate script
        print_section("Generating Content")

        try:
            config = ScriptGeneratorConfig(
                platform_target=PlatformTarget.YOUTUBE_MEDIUM,
                target_duration_seconds=90,
                structure_type=ScriptStructure.HOOK_DELIVER_CTA,
                include_cta=True,
                tone=ScriptTone.ENGAGING,
            )
            generator = ScriptGenerator(config)
            print_info("Generating script with HOOK_DELIVER_CTA structure...")
            if logger:
                logger.info("Generating script")

            script = generator.generate_content_v1(idea, title)

        except Exception as e:
            print_error(f"Error generating script: {e}")
            if logger:
                logger.exception("Content generation failed")
            continue

        # Display results
        print_section(f"Generated Content")

        print(f"\n{Colors.GREEN}{'─' * 60}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}  Content: {script.title}{Colors.END}")
        print(f"{Colors.GREEN}{'─' * 60}{Colors.END}")
        print(f"  ID: {script.content_id}")
        print(f"  Structure: {script.structure_type.value}")
        print(f"  Platform: {script.platform_target.value}")
        print(f"  Duration: {script.total_duration_seconds}s")
        print(f"  Sections: {len(script.sections)}")

        for section in script.sections:
            print(
                f"\n  {Colors.CYAN}[{section.section_type.upper()}]{Colors.END} ({section.estimated_duration_seconds}s)"
            )
            print(f"    Purpose: {section.purpose}")
            # Show first 200 chars of content
            content_preview = (
                section.content[:200] + "..." if len(section.content) > 200 else section.content
            )
            print(f"    Content: {content_preview}")

        if logger:
            logger.info(f"Content generated: {script.content_id}")
            logger.debug(
                f"Content data: {json.dumps(script.to_dict(), indent=2, ensure_ascii=False)}"
            )

        # Save to database (if not preview mode)
        if not preview and DB_AVAILABLE:
            print_section("Database Operations")
            save_choice = (
                input(f"{Colors.CYAN}Save to database? (y/n) [y]: {Colors.END}").strip().lower()
            )
            if save_choice != "n":
                print_info("Saving to database...")
                if logger:
                    logger.info("Saving script to database")
                # TODO: Implement actual DB save
                print_warning(
                    "Database save not yet implemented - script was created but not persisted"
                )
            else:
                print_info("Skipped database save")
                if logger:
                    logger.info("User skipped database save")
        elif preview:
            print_section("Preview Mode - No Database Save")
            print_info("Content created - NOT saved to database")
            if logger:
                logger.info("Preview mode: script created but not saved")

        # Output as JSON option
        json_choice = (
            input(f"\n{Colors.CYAN}Output as JSON? (y/n) [n]: {Colors.END}").strip().lower()
        )
        if json_choice == "y":
            print_section("JSON Output")
            print(json.dumps(script.to_dict(), indent=2, ensure_ascii=False))
            if logger:
                logger.info("User requested JSON output")

        # Output full script text
        full_text_choice = (
            input(f"\n{Colors.CYAN}Show full script text? (y/n) [n]: {Colors.END}").strip().lower()
        )
        if full_text_choice == "y":
            print_section("Full Content Text")
            print(script.full_text)

        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print("Enter new input or type 'quit' to exit.\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive Content Generation from Idea+Title for PrismQ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script_from_idea_title_interactive.py                    # Interactive mode with DB save
  python script_from_idea_title_interactive.py --preview          # Preview mode (no DB save)
  python script_from_idea_title_interactive.py --preview --debug  # Debug mode with extensive logging
        """,
    )

    parser.add_argument(
        "--preview", "-p", action="store_true", help="Preview mode - do not save to database"
    )
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enable debug logging (extensive output)"
    )

    args = parser.parse_args()

    return run_interactive_mode(preview=args.preview, debug=args.debug)


if __name__ == "__main__":
    sys.exit(main())
