#!/usr/bin/env python3
"""Interactive Idea Creation CLI for PrismQ.

This script provides an interactive mode for creating ideas from text input.
It waits for user input, processes it through the idea variant system, and
optionally saves to the database.

Usage:
    python idea_creation_interactive.py                    # Interactive mode with DB save
    python idea_creation_interactive.py --preview          # Preview mode (no DB save)
    python idea_creation_interactive.py --preview --debug  # Debug mode with extensive logging

Modes:
    Default: Creates ideas and saves to database
    Preview: Creates ideas for testing without saving (extensive logging)
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Setup paths - Now in T/Idea/Creation/src/
SCRIPT_DIR = Path(__file__).parent.absolute()
CREATION_ROOT = SCRIPT_DIR.parent  # T/Idea/Creation
IDEA_ROOT = CREATION_ROOT.parent  # T/Idea
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
        create_idea_variant,
        create_all_variants,
        create_multiple_of_same_variant,
        create_ideas_from_input,
        list_templates,
        get_template,
        format_idea_as_text,
        VARIANT_TEMPLATES,
        DEFAULT_IDEA_COUNT,
    )
    VARIANTS_AVAILABLE = True
except ImportError as e:
    VARIANTS_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import Idea model
try:
    from idea import Idea, IdeaStatus, ContentGenre
    IDEA_MODEL_AVAILABLE = True
except ImportError:
    IDEA_MODEL_AVAILABLE = False

# Try to import database from shared src module
try:
    from src import IdeaDatabase, setup_idea_database, Config
    DB_AVAILABLE = True
except ImportError:
    # Fallback: try local simple_idea_db
    try:
        from simple_idea_db import SimpleIdeaDatabase as IdeaDatabase
        from simple_idea_db import setup_simple_idea_database as setup_idea_database
        Config = None
        DB_AVAILABLE = True
    except ImportError:
        DB_AVAILABLE = False
        Config = None


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
# Input Parsing
# =============================================================================

def parse_input_text(text: str, logger: Optional[logging.Logger] = None) -> tuple:
    """Parse input text and extract title and description.
    
    Handles:
    - Plain text (title, description, story snippet, keyword)
    - JSON data with story_title, title, theme, etc.
    
    Args:
        text: Input text (any format)
        logger: Optional logger for debug output
        
    Returns:
        Tuple of (title, description, metadata)
    """
    import re
    
    text = text.strip()
    metadata = {}
    
    if logger:
        logger.info(f"Parsing input text ({len(text)} chars)")
    
    # Try to parse as JSON
    if text.startswith('{'):
        try:
            data = json.loads(text)
            if logger:
                logger.info(f"Detected JSON input with {len(data)} fields")
                logger.debug(f"JSON fields: {list(data.keys())}")
            
            # Extract title from various JSON fields
            title = (
                data.get('story_title') or 
                data.get('title') or 
                data.get('theme') or 
                data.get('topic') or
                data.get('keyword') or
                data.get('name') or
                'Untitled Idea'
            )
            
            # Build description from other fields
            desc_parts = []
            
            if data.get('narrator_gender'):
                desc_parts.append(f"Narrator: {data['narrator_gender']}")
            if data.get('tone'):
                desc_parts.append(f"Tone: {data['tone']}")
            if data.get('theme'):
                desc_parts.append(f"Theme: {data['theme']}")
            if data.get('character_arc'):
                desc_parts.append(f"Character arc: {data['character_arc']}")
            if data.get('outcome'):
                desc_parts.append(f"Outcome: {data['outcome']}")
            if data.get('emotional_core'):
                desc_parts.append(f"Emotional core: {data['emotional_core']}")
            
            # Store potential info in metadata
            if data.get('potencial'):
                metadata['potential'] = data['potencial']
                if logger:
                    logger.debug(f"Found potential data: {data['potencial']}")
            
            description = '. '.join(desc_parts) if desc_parts else ''
            
            if logger:
                logger.info(f"Extracted title: '{title}'")
                logger.info(f"Extracted description: '{description[:100]}...' ({len(description)} chars)")
            
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
        return text, '', metadata
    
    # For longer text (story snippet, description), extract a title
    sentences = re.split(r'[.!?]', text)
    first_sentence = sentences[0].strip() if sentences else text[:100]
    
    # Truncate title if too long
    if len(first_sentence) > 80:
        title = first_sentence[:77] + '...'
    else:
        title = first_sentence
    
    if logger:
        logger.info(f"Extracted title from long text: '{title}'")
        logger.info(f"Full text used as description ({len(text)} chars)")
    
    return title, text, metadata


# =============================================================================
# Interactive Mode
# =============================================================================

def run_interactive_mode(preview: bool = False, debug: bool = False):
    """Run the interactive idea creation mode.
    
    Args:
        preview: If True, don't save to database (preview/test mode)
        debug: If True, enable extensive debug logging
    """
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"idea_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        
        # Create logger with DEBUG level to allow all messages through
        # Handler levels control what actually gets logged
        logger = logging.getLogger('PrismQ.Idea.Creation')
        logger.setLevel(logging.DEBUG)
        
        # File handler - captures all DEBUG messages (including JSON data)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Console handler - only INFO and above (no JSON dumps to console)
        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(console_handler)
        
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")
    
    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
    print_header(f"PrismQ Idea Creation - {mode_text}")
    
    # Check module availability
    if not VARIANTS_AVAILABLE:
        print_error(f"Idea variants module not available: {IMPORT_ERROR}")
        if logger:
            logger.error(f"Module import failed: {IMPORT_ERROR}")
        return 1
    
    print_success("Idea variants module loaded")
    if logger:
        logger.info("Idea variants module loaded successfully")
    
    if preview:
        print_warning("Preview mode - ideas will NOT be saved to database")
        print_info("This mode is for testing and tuning. Check logs for details.")
    else:
        if DB_AVAILABLE:
            print_success("Database module available")
        else:
            print_warning("Database module not available - will run in preview mode")
            preview = True
    
    # Show available templates
    print_section("Available Variant Templates")
    templates = list_templates()
    for i, name in enumerate(templates, 1):
        template = get_template(name)
        print(f"  {i:2}. {Colors.BOLD}{name:15}{Colors.END} - {template['name']}")
    
    if logger:
        logger.info(f"Available templates: {templates}")
    
    # Interactive loop
    print_section("Enter Text Input")
    print("Type or paste your text (title, description, story snippet, or JSON).")
    print("Press Enter to submit, or type 'quit' to exit.\n")
    
    while True:
        # Collect single-line input (or multi-line for JSON)
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
        
        # Parse input
        print_section("Processing Input")
        title, description, metadata = parse_input_text(input_text, logger)
        
        print(f"  Title: {Colors.BOLD}{title}{Colors.END}")
        if description:
            desc_preview = description[:100] + '...' if len(description) > 100 else description
            print(f"  Description: {desc_preview}")
        if metadata:
            print(f"  Metadata: {json.dumps(metadata, indent=2)[:200]}...")
        
        # Generate variants with random template selection
        print_section("Generating Variants")
        
        variants = []
        try:
            # Generate 10 variants with randomly selected templates (weighted)
            print_info(f"Creating {DEFAULT_IDEA_COUNT} variants with randomly selected templates...")
            if logger:
                logger.info(f"Creating {DEFAULT_IDEA_COUNT} variants with weighted random template selection")
            variants = create_ideas_from_input(title, count=DEFAULT_IDEA_COUNT, description=description)
                
        except Exception as e:
            print_error(f"Error creating variants: {e}")
            if logger:
                logger.exception("Variant creation failed")
            continue
        
        # Display results
        print_section(f"Generated {len(variants)} Variant(s)")
        
        for i, variant in enumerate(variants):
            print(f"\n{Colors.GREEN}{'─' * 50}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}  Variant {i+1}: {variant.get('variant_name', 'Unknown')}{Colors.END}")
            print(f"{Colors.GREEN}{'─' * 50}{Colors.END}")
            
            # Print clean text representation of the idea
            idea_text = format_idea_as_text(variant)
            for line in idea_text.split('\n'):
                print(f"  {line}")
            
            if logger:
                logger.info(f"Variant {i+1}: {variant.get('variant_name')}")
                logger.debug(f"Variant {i+1} data: {json.dumps(variant, indent=2, ensure_ascii=False)}")
        
        # Save to database automatically (if not preview mode)
        if not preview and DB_AVAILABLE:
            print_section("Database Operations")
            print_info("Saving to database...")
            if logger:
                logger.info(f"Saving {len(variants)} variants to database")
            
            try:
                # Get database path using helper function
                db_path = get_database_path()
                
                # Setup and connect to database
                db = setup_idea_database(db_path)
                
                # Save each variant to the database
                saved_ids = []
                for i, variant in enumerate(variants):
                    # Convert variant to text using format_idea_as_text
                    idea_text = format_idea_as_text(variant)
                    
                    # Insert into database with version=1 (new ideas always start at version 1)
                    idea_id = db.insert_idea(text=idea_text, version=1)
                    saved_ids.append(idea_id)
                    
                    if logger:
                        logger.info(f"Saved variant {i+1} with ID: {idea_id}")
                
                db.close()
                
                print_success(f"Successfully saved {len(saved_ids)} variant(s) to database")
                print_info(f"Database: {db_path}")
                print_info(f"Saved IDs: {saved_ids}")
                
                if logger:
                    logger.info(f"Saved {len(saved_ids)} variants to {db_path}: IDs={saved_ids}")
                    
            except Exception as e:
                print_error(f"Failed to save to database: {e}")
                if logger:
                    logger.exception("Database save failed")
        elif preview:
            print_section("Preview Mode - No Database Save")
            print_info(f"Created {len(variants)} variant(s) - NOT saved to database")
            if logger:
                logger.info(f"Preview mode: {len(variants)} variants created but not saved")
        
        # Output as JSON option
        json_choice = input(f"\n{Colors.CYAN}Output as JSON? (y/n) [n]: {Colors.END}").strip().lower()
        if json_choice == 'y':
            print_section("JSON Output")
            print(json.dumps(variants, indent=2, ensure_ascii=False))
            if logger:
                logger.info("User requested JSON output")
        
        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print("Enter new text or type 'quit' to exit.\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Interactive Idea Creation for PrismQ',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python idea_creation_interactive.py                    # Interactive mode with DB save
  python idea_creation_interactive.py --preview          # Preview mode (no DB save)
  python idea_creation_interactive.py --preview --debug  # Debug mode with extensive logging
        """
    )
    
    parser.add_argument('--preview', '-p', action='store_true',
                       help='Preview mode - do not save to database')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug logging (extensive output)')
    
    args = parser.parse_args()
    
    return run_interactive_mode(preview=args.preview, debug=args.debug)


if __name__ == '__main__':
    sys.exit(main())
