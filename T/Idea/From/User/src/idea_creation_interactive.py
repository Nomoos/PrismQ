#!/usr/bin/env python3
"""Interactive Idea Creation CLI for PrismQ.

This script provides continuous interactive mode for creating ideas from text input.
It waits for user input, processes it through the idea variant system, and
saves to the database.

**IMPORTANT - Single Shared Database:**
PrismQ uses ONE shared database (db.s3db) for ALL modules (T, A, V, P, M).
All Idea, Story, Title, Content, and other tables are in this single database.
DO NOT create multiple database connections or separate databases.

The database connection is established once at initialization and reused
across all operations for efficiency.

Usage:
    python idea_creation_interactive.py    # Continuous mode - creates and saves ideas

The tool runs in continuous mode, accepting multiple inputs until 'quit' is entered.
Database connection is required - the tool will exit with error if database is unavailable.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup paths - Now in T/Idea/From/User/src/
SCRIPT_DIR = Path(__file__).parent.absolute()
CREATION_ROOT = SCRIPT_DIR.parent  # T/Idea/From/User
FROM_ROOT = CREATION_ROOT.parent  # T/Idea/From
IDEA_ROOT = FROM_ROOT.parent  # T/Idea
T_ROOT = IDEA_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))  # Current directory for local imports
sys.path.insert(0, str(IDEA_ROOT / "Model" / "src"))
sys.path.insert(0, str(IDEA_ROOT / "Model"))
sys.path.insert(0, str(REPO_ROOT))  # Add repo root for src module import

# Import idea variants module
try:
    from idea_variants import (
        DEFAULT_IDEA_COUNT,
        create_ideas_from_input,
        get_flavor,
        list_flavors,
        get_flavor_count,
        IdeaGenerator,
        FlavorSelector,
    )
    # Backward compatibility
    get_template = get_flavor
    list_templates = list_flavors

    VARIANTS_AVAILABLE = True
except ImportError as e:
    VARIANTS_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import Idea model
try:
    from idea import ContentGenre, Idea, IdeaStatus

    IDEA_MODEL_AVAILABLE = True
except ImportError:
    IDEA_MODEL_AVAILABLE = False

# Import database from shared src module - REQUIRED
try:
    from src.config import Config
    from src.idea import IdeaTable, setup_idea_table

    DB_AVAILABLE = True
except ImportError as e:
    DB_AVAILABLE = False
    DB_IMPORT_ERROR = str(e)


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


def get_database_path() -> str:
    """Get the database path for saving ideas.

    Returns database path from Config if available, otherwise falls back
    to C:/PrismQ/db.s3db.

    Returns:
        Path to the database file (db.s3db in working directory)
    """
    if Config is not None:
        config = Config(interactive=False)
        return config.database_path
    else:
        # Fallback to C:/PrismQ/db.s3db
        return str(Path("C:/PrismQ") / "db.s3db")


# =============================================================================
# Input Parsing (DEPRECATED - Kept for backward compatibility only)
# =============================================================================


def parse_input_text(text: str, logger: Optional[logging.Logger] = None) -> tuple:
    """Parse input text and extract title and description.
    
    DEPRECATED: This function is no longer used in the module.
    Input text now flows directly to the AI template without parsing.
    This function is kept for backward compatibility only.

    Handles:
    - Plain text (title, description, story snippet, keyword)
    - JSON data with story_title, title, theme, etc.

    Args:
        text: Input text (any format)
        logger: Optional logger for debug output

    Returns:
        Tuple of (title, description, metadata)
    """
    import warnings
    warnings.warn(
        "parse_input_text is deprecated. Input text now flows directly to AI without parsing.",
        DeprecationWarning,
        stacklevel=2
    )
    
    import re

    text = text.strip()
    metadata = {}

    if logger:
        logger.info(f"Parsing input text ({len(text)} chars)")

    # Try to parse as JSON
    if text.startswith("{"):
        try:
            data = json.loads(text)
            if logger:
                logger.info(f"Detected JSON input with {len(data)} fields")
                logger.debug(f"JSON fields: {list(data.keys())}")

            # Extract title from various JSON fields
            title = (
                data.get("story_title")
                or data.get("title")
                or data.get("theme")
                or data.get("topic")
                or data.get("keyword")
                or data.get("name")
                or "Untitled Idea"
            )

            # Build description from other fields
            desc_parts = []

            if data.get("narrator_gender"):
                desc_parts.append(f"Narrator: {data['narrator_gender']}")
            if data.get("tone"):
                desc_parts.append(f"Tone: {data['tone']}")
            if data.get("theme"):
                desc_parts.append(f"Theme: {data['theme']}")
            if data.get("character_arc"):
                desc_parts.append(f"Character arc: {data['character_arc']}")
            if data.get("outcome"):
                desc_parts.append(f"Outcome: {data['outcome']}")
            if data.get("emotional_core"):
                desc_parts.append(f"Emotional core: {data['emotional_core']}")

            # Store potential info in metadata
            if data.get("potencial"):
                metadata["potential"] = data["potencial"]
                if logger:
                    logger.debug(f"Found potential data: {data['potencial']}")

            description = ". ".join(desc_parts) if desc_parts else ""

            if logger:
                logger.info(f"Extracted title: '{title}'")
                logger.info(
                    f"Extracted description: '{description[:100]}...' ({len(description)} chars)"
                )

            return title, description, metadata

        except json.JSONDecodeError as e:
            if logger:
                logger.warning(f"JSON parse failed: {e}")

    # Plain text handling
    if logger:
        logger.info("Processing as plain text")

    # If it's a short text (likely a title/keyword), use as-is
    if len(text) <= 100:
        if logger:
            logger.info(f"Short text detected, using as title: '{text}'")
        return text, "", metadata

    # For longer text (story snippet, description), extract a title
    sentences = re.split(r"[.!?]", text)
    first_sentence = sentences[0].strip() if sentences else text[:100]

    # Truncate title if too long
    if len(first_sentence) > 80:
        title = first_sentence[:77] + "..."
    else:
        title = first_sentence

    if logger:
        logger.info(f"Extracted title from long text: '{title}'")
        logger.info(f"Full text used as description ({len(text)} chars)")

    return title, text, metadata


# =============================================================================
# Interactive Mode
# =============================================================================


def run_interactive_mode():
    """Run the continuous interactive idea creation mode.
    
    This mode continuously accepts user input and saves ideas to the database.
    Database connection is required - exits with error if unavailable.
    """
    # Print header
    print_header(f"PrismQ Idea Creation - Continuous Mode")

    # Check module availability
    if not VARIANTS_AVAILABLE:
        print_error(f"Idea variants module not available: {IMPORT_ERROR}")
        return 1

    print_success("Idea variants module loaded")

    # Check database availability - REQUIRED for operation
    if not DB_AVAILABLE:
        print_error(f"Database module not available: {DB_IMPORT_ERROR}")
        print_error("Database connection is required for operation.")
        print_info("Please ensure python-dotenv is installed: pip install python-dotenv")
        return 1

    # Setup database connection once at initialization
    # IMPORTANT: PrismQ uses a SINGLE SHARED DATABASE (db.s3db) for all modules
    # This connection is reused across all inputs for better performance
    db = None
    db_path = None
    
    try:
        db_path = get_database_path()
        db = setup_idea_table(db_path)
        print_success("Database connected")
        print_info(f"Database: {db_path}")
        print_info("NOTE: PrismQ uses ONE shared database (db.s3db) for all modules")
    except Exception as e:
        print_error(f"Failed to setup database: {e}")
        print_error("Database connection is required for operation.")
        return 1

    # Show available flavors
    print_section("Available Flavors")
    
    # Import flavor functions
    try:
        from flavors import list_flavor_categories, get_flavor_count
        
        total_flavors = get_flavor_count()
        print(f"  Total available flavors: {Colors.BOLD}{total_flavors}{Colors.END}")
        print(f"  Flavors are automatically selected using weighted random selection")
        print(f"  optimized for the primary audience (13-17 young women in US/Canada)")
        
        categories = list_flavor_categories()
        print(f"\n  Sample flavor categories:")
        for cat_name in list(categories.keys())[:5]:
            flavors_in_cat = categories[cat_name]
            print(f"    • {Colors.CYAN}{cat_name}{Colors.END}: {len(flavors_in_cat)} flavors")
    except ImportError:
        # Fallback to showing templates if flavors not available
        print_warning("Flavor module not available, showing variant templates")
        templates = list_templates()
        for i, name in enumerate(templates[:10], 1):
            template = get_template(name)
            print(f"  {i:2}. {Colors.BOLD}{name:15}{Colors.END} - {template['name']}")
        print(f"  ... and {len(templates) - 10} more")

    # Interactive loop
    print_section("Enter Text Input")
    print("Type or paste your text (title, description, story snippet, or JSON).")
    print("Press Enter to submit, or type 'quit' to exit.\n")

    try:
        while True:
            # Collect single-line input (or multi-line for JSON)
            print(f"{Colors.CYAN}>>> {Colors.END}", end="")

            try:
                line = input().strip()
                if line.lower() == "quit":
                    print_info("Exiting...")
                    break

                if not line:
                    continue

                input_text = line

            except EOFError:
                print_info("Exiting...")
                break
            except KeyboardInterrupt:
                print("\n")
                print_info("Interrupted. Type 'quit' to exit.")
                continue

            # Display input (no parsing or processing)
            print_section("Processing Input")
            
            # Show input preview
            input_preview = input_text[:100] + "..." if len(input_text) > 100 else input_text
            print(f"  Input: {Colors.BOLD}{input_preview}{Colors.END}")
            print(f"  Length: {len(input_text)} characters")

            # Generate variants with random template selection
            print_section("Generating Variants")

            variants = []
            saved_ids = []
            try:
                # Generate 10 variants with randomly selected templates (weighted)
                print_info(f"Creating {DEFAULT_IDEA_COUNT} variants and saving to database...")
                
                # Create generator and selector instances
                generator = IdeaGenerator()
                selector = FlavorSelector()
                
                # Select flavors upfront
                selected_flavors = selector.select_multiple(DEFAULT_IDEA_COUNT)
                
                # Generate variants one at a time with progress feedback
                for i, flavor_name in enumerate(selected_flavors):
                    try:
                        # Show progress
                        print_info(f"  [{i+1}/{DEFAULT_IDEA_COUNT}] Generating with flavor: {flavor_name}...")
                        
                        # Generate the variant using raw input text
                        # Pass database connection for direct save
                        idea = generator.generate_from_flavor(
                            flavor_name=flavor_name,
                            input_text=input_text,
                            variation_index=i,
                            db=db,
                            logger=None,
                        )
                        
                        # Track saved ID if returned
                        if idea.get('idea_id'):
                            saved_ids.append(idea['idea_id'])
                        
                        variants.append(idea)
                    
                    except Exception as e:
                        print_warning(f"  [{i+1}/{DEFAULT_IDEA_COUNT}] Failed with flavor {flavor_name}: {e}")
                        continue

            except Exception as e:
                print_error(f"Error creating variants: {e}")
                continue

            # Display results
            print_section(f"Generated {len(variants)} Variant(s)")

            for i, variant in enumerate(variants):
                print(f"\n{Colors.GREEN}{'─' * 50}{Colors.END}")
                print(
                    f"{Colors.GREEN}{Colors.BOLD}  Variant {i+1}: {variant.get('variant_name', 'Unknown')}{Colors.END}"
                )
                print(f"{Colors.GREEN}{'─' * 50}{Colors.END}")

                # Print the generated text
                idea_text = variant.get('text', '')
                print(f"  {idea_text}")

            # Show summary
            print_section("Database Summary")
            print_success(f"Successfully saved {len(saved_ids)} variant(s) to database")
            if db_path:
                print_info(f"Database: {db_path}")
            print_info(f"Saved IDs: {saved_ids}")

            print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
            print("Enter new text or type 'quit' to exit.\n")
    
    finally:
        # Close database connection when exiting (reusable connection cleanup)
        if db:
            db.close()
    
    return 0


def main():
    """Main entry point."""
    return run_interactive_mode()


if __name__ == "__main__":
    sys.exit(main())
