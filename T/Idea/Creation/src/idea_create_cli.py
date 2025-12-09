#!/usr/bin/env python3
"""Interactive CLI client for creating AI-generated Ideas.

Usage:
    idea create "<prompt>" [--count N] [--preview] [--no-save] [--debug] [--validate]

This CLI tool generates Ideas from a single text prompt using AI, validates them,
and optionally saves them to the database with user confirmation.

Features:
    - Single text input parameter (prompt)
    - Default 10 ideas generation (configurable with --count)
    - AI-powered generation with template fallback
    - Interactive confirmation before DB save
    - Preview, debug, and validation modes
    - Clear error messages for CLI users
"""

import argparse
import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

# Add parent directories to path for imports
# Note: This pattern is established in the codebase (see idea_cli.py example)
# and is necessary for the module's position in the directory structure
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = current_dir
model_dir = os.path.join(current_dir, "../../Model/src")
model_base = os.path.join(current_dir, "../../Model")
repo_root = os.path.join(current_dir, "../../../../")

sys.path.insert(0, src_dir)
sys.path.insert(0, model_dir)
sys.path.insert(0, model_base)
sys.path.insert(0, repo_root)

from creation import CreationConfig, IdeaCreator
from idea_db import IdeaDatabase

from idea import ContentGenre, Idea, IdeaStatus

# Try to import Config for database path
try:
    from src import Config

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


def get_default_db_path() -> str:
    """Get the default database path from Config or fallback.

    Returns:
        Path to the database file (db.s3db in working directory)
    """
    if CONFIG_AVAILABLE:
        config = Config(interactive=False)
        return config.database_path
    else:
        # Fallback to C:/PrismQ/db.s3db
        return os.path.join("C:/PrismQ", "db.s3db")


# Module constants
DEFAULT_COUNT = 10
DEFAULT_MODEL = "qwen3:32b"
DEFAULT_TEMPERATURE = 0.8
MAX_COUNT = 100
MIN_COUNT = 1

# Required fields for database insertion
REQUIRED_DB_FIELDS = ["title", "concept"]

# UI Messages (Czech localization)
MSG_SAVE_PROMPT = "💾 Uložit do databáze?"
MSG_YES_NO = "[Y] Ano  /  [N] Ne"
MSG_INVALID_INPUT = "❌ Neplatná odpověď. Zadejte Y nebo N."
MSG_CANCELLED = "\n⚠️  Operace zrušena."
MSG_DB_ERROR = "Chyba při ukládání do databáze"
MSG_INVALID_INPUT_ERROR = "Neplatný vstup"
MSG_GENERATION_ERROR = "Chyba při generování nápadů"


class ValidationError(Exception):
    """Raised when idea validation fails."""

    pass


class CLIError(Exception):
    """Raised for CLI-specific errors with user-friendly messages."""

    pass


@dataclass
class CLIOptions:
    """Options for the CLI tool."""

    prompt: str
    count: int = DEFAULT_COUNT
    preview: bool = False
    no_save: bool = False
    debug: bool = False
    validate: bool = False
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    db_path: Optional[str] = None


def validate_idea(idea: Idea) -> List[str]:
    """Validate an idea has all required fields for database insertion.

    Args:
        idea: The Idea instance to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required fields
    if not idea.title or not idea.title.strip():
        errors.append("Missing required field: title")

    if not idea.concept or not idea.concept.strip():
        errors.append("Missing required field: concept")

    # Check field types
    if not isinstance(idea.title, str):
        errors.append(f"Invalid type for 'title': expected str, got {type(idea.title).__name__}")

    if not isinstance(idea.concept, str):
        errors.append(
            f"Invalid type for 'concept': expected str, got {type(idea.concept).__name__}"
        )

    if not isinstance(idea.keywords, list):
        errors.append(
            f"Invalid type for 'keywords': expected list, got {type(idea.keywords).__name__}"
        )

    if not isinstance(idea.themes, list):
        errors.append(f"Invalid type for 'themes': expected list, got {type(idea.themes).__name__}")

    if not isinstance(idea.target_platforms, list):
        errors.append(
            f"Invalid type for 'target_platforms': expected list, got {type(idea.target_platforms).__name__}"
        )

    if not isinstance(idea.target_formats, list):
        errors.append(
            f"Invalid type for 'target_formats': expected list, got {type(idea.target_formats).__name__}"
        )

    # Validate status is valid enum
    if not isinstance(idea.status, IdeaStatus):
        errors.append(
            f"Invalid type for 'status': expected IdeaStatus, got {type(idea.status).__name__}"
        )

    # Validate genre is valid enum
    if not isinstance(idea.genre, ContentGenre):
        errors.append(
            f"Invalid type for 'genre': expected ContentGenre, got {type(idea.genre).__name__}"
        )

    return errors


def format_idea_row(idea: Idea, index: int, verbose: bool = False) -> str:
    """Format an idea as a single row for CLI output.

    Args:
        idea: The Idea to format
        index: The idea index (1-based)
        verbose: Whether to show detailed information

    Returns:
        Formatted string representation
    """
    lines = []

    # Header
    lines.append(f"\n{'─'*80}")
    lines.append(f"💡 Idea {index}: {idea.title}")
    lines.append(f"{'─'*80}")

    # Core fields
    lines.append(f"📝 Concept: {idea.concept}")

    if verbose or idea.premise:
        if idea.premise:
            lines.append(f"📋 Premise: {idea.premise}")

    if verbose or idea.logline:
        if idea.logline:
            lines.append(f"🎬 Logline: {idea.logline}")

    if verbose or idea.hook:
        if idea.hook:
            lines.append(f"🪝 Hook: {idea.hook}")

    if verbose and idea.synopsis:
        lines.append(
            f"📖 Synopsis: {idea.synopsis[:200]}..."
            if len(idea.synopsis) > 200
            else f"📖 Synopsis: {idea.synopsis}"
        )

    # Metadata
    if idea.keywords:
        keywords_str = ", ".join(idea.keywords[:8])
        if len(idea.keywords) > 8:
            keywords_str += f" (+{len(idea.keywords) - 8} more)"
        lines.append(f"🏷️  Keywords: {keywords_str}")

    if idea.themes:
        lines.append(f"🎯 Themes: {', '.join(idea.themes)}")

    lines.append(f"🎭 Genre: {idea.genre.value}")

    if idea.target_platforms:
        lines.append(f"📺 Platforms: {', '.join(idea.target_platforms)}")

    if idea.target_formats:
        lines.append(f"📄 Formats: {', '.join(idea.target_formats)}")

    lines.append(f"📊 Status: {idea.status.value}")

    return "\n".join(lines)


def format_idea_db_row(idea: Idea) -> Dict[str, Any]:
    """Format an idea for database insertion.

    Args:
        idea: The Idea to format

    Returns:
        Dictionary suitable for database insertion
    """
    return idea.to_dict()


def print_header(prompt: str, count: int, options: CLIOptions):
    """Print CLI header with configuration info."""
    print(f"\n{'='*80}")
    print("🌟 PrismQ Idea Creation CLI")
    print(f"{'='*80}")
    print(f"📝 Prompt: {prompt}")
    print(f"🔢 Count: {count} ideas")

    flags = []
    if options.preview:
        flags.append("--preview")
    if options.no_save:
        flags.append("--no-save")
    if options.debug:
        flags.append("--debug")
    if options.validate:
        flags.append("--validate")

    if flags:
        print(f"🚀 Flags: {' '.join(flags)}")
    print(f"{'='*80}\n")


def prompt_user_confirmation(message: str = MSG_SAVE_PROMPT) -> bool:
    """Prompt user for Y/N confirmation.

    Args:
        message: The confirmation message to display

    Returns:
        True if user confirms (Y), False otherwise (N)
    """
    print(f"\n{message}")
    print(MSG_YES_NO)

    while True:
        try:
            response = input("> ").strip().upper()
            if response in ("Y", "ANO", "YES", "1"):
                return True
            elif response in ("N", "NE", "NO", "0", ""):
                return False
            else:
                print(MSG_INVALID_INPUT)
        except (EOFError, KeyboardInterrupt):
            print(MSG_CANCELLED)
            return False


def save_idea_to_db(idea: Idea, db_path: Optional[str] = None) -> int:
    """Save an idea to the database.

    Args:
        idea: The Idea to save
        db_path: Optional path to the database file

    Returns:
        The database ID of the saved idea

    Raises:
        CLIError: If database save fails
    """
    try:
        db = IdeaDatabase(db_path or get_default_db_path())
        db.connect()
        db.create_tables()

        idea_dict = format_idea_db_row(idea)
        idea_id = db.insert_idea(idea_dict)

        db.close()
        return idea_id
    except Exception as e:
        raise CLIError(f"{MSG_DB_ERROR}: {e}")


def generate_ideas(options: CLIOptions) -> List[Idea]:
    """Generate ideas from the prompt using AI.

    Args:
        options: CLI options

    Returns:
        List of generated Idea instances

    Raises:
        CLIError: If generation fails
    """
    try:
        config = CreationConfig(
            use_ai=True,
            ai_model=options.model,
            ai_temperature=options.temperature,
            default_num_ideas=options.count,
        )

        creator = IdeaCreator(config)

        # AI determines the best interpretation of the prompt
        # (title, description, keyword, script snippet, etc.)
        # The prompt is treated as a flexible input seed
        ideas = creator.create_from_description(description=options.prompt, num_ideas=options.count)

        return ideas

    except ValueError as e:
        raise CLIError(f"{MSG_INVALID_INPUT_ERROR}: {e}")
    except Exception as e:
        raise CLIError(f"{MSG_GENERATION_ERROR}: {e}")


def run_cli(options: CLIOptions) -> int:
    """Run the CLI with the given options.

    Args:
        options: CLI options

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Print header
        print_header(options.prompt, options.count, options)

        # Generate ideas
        print("🔄 Generuji nápady pomocí AI...")
        ideas = generate_ideas(options)

        if not ideas:
            print("❌ Nepodařilo se vygenerovat žádné nápady.")
            return 1

        print(f"✅ Vygenerováno {len(ideas)} nápadů\n")

        # Validate if requested
        if options.validate:
            print("🔍 Validace nápadů...")
            all_valid = True
            for i, idea in enumerate(ideas, 1):
                errors = validate_idea(idea)
                if errors:
                    all_valid = False
                    print(f"❌ Idea {i} validace selhala:")
                    for error in errors:
                        print(f"   - {error}")
                else:
                    print(f"✅ Idea {i}: OK")

            if not all_valid:
                print("\n⚠️  Některé nápady nesplňují validaci.")
                if not options.preview and not options.no_save:
                    return 1
            else:
                print("\n✅ Všechny nápady prošly validací.")

        # Process each idea
        saved_count = 0
        skipped_count = 0

        for i, idea in enumerate(ideas, 1):
            # Display idea
            verbose = options.debug or options.validate
            print(format_idea_row(idea, i, verbose=verbose))

            # Handle save logic based on flags
            if options.preview:
                # Preview mode: just show, don't save
                print(f"\n📋 [Preview režim - idea nebude uložena]")
                continue

            if options.no_save:
                # No-save mode: skip confirmation and don't save
                continue

            # Debug or normal mode: ask for confirmation
            if options.debug:
                print(f"\n🐛 [Debug režim]")

            if prompt_user_confirmation():
                try:
                    idea_id = save_idea_to_db(idea, options.db_path)
                    print(f"✅ Idea uložena do databáze (ID: {idea_id})")
                    saved_count += 1
                except CLIError as e:
                    print(f"❌ {e}")
                    skipped_count += 1
            else:
                print("⏭️  Idea přeskočena")
                skipped_count += 1

        # Summary
        print(f"\n{'='*80}")
        print("📊 Souhrn:")
        print(f"   Vygenerováno: {len(ideas)} nápadů")
        if not options.preview and not options.no_save:
            print(f"   Uloženo: {saved_count}")
            print(f"   Přeskočeno: {skipped_count}")
        elif options.preview:
            print(f"   Režim: Preview (žádné uložení)")
        elif options.no_save:
            print(f"   Režim: No-save (žádné uložení)")
        print(f"{'='*80}\n")

        return 0

    except CLIError as e:
        print(f"\n❌ Chyba: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Operace přerušena uživatelem.")
        return 130


def parse_args(args: Optional[List[str]] = None) -> CLIOptions:
    """Parse command line arguments.

    Args:
        args: Optional list of arguments (defaults to sys.argv)

    Returns:
        Parsed CLIOptions
    """
    parser = argparse.ArgumentParser(
        prog="idea create",
        description="Generate AI-powered ideas from a text prompt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  idea create "Zombie kočky útočí v supermarketu"
  idea create "AI v medicíně" --count 5
  idea create "Horror příběh" --preview
  idea create "Sci-fi koncept" --debug
  idea create "Technologie budoucnosti" --validate --no-save
        """,
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Text prompt for idea generation (title, description, keyword, script snippet, etc.)",
    )

    parser.add_argument(
        "--count", type=int, default=10, help="Number of ideas to generate (default: 10)"
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview mode: display ideas without saving to database",
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        dest="no_save",
        help="Generate ideas without confirmation prompt and without saving",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: display detailed idea info and wait for Y/N confirmation",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate all required fields and types before displaying",
    )

    parser.add_argument(
        "--model",
        default="qwen3:32b",
        help="AI model to use (default: qwen3:32b)",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help="AI temperature for creativity (0.0-2.0, default: 0.8)",
    )

    parser.add_argument(
        "--db-path",
        dest="db_path",
        help="Path to the database file (default: db.s3db in working directory)",
    )

    parsed = parser.parse_args(args)

    # Validate prompt
    if not parsed.prompt:
        parser.print_help()
        sys.exit(1)

    # Validate count
    if parsed.count < MIN_COUNT:
        parser.error(f"--count must be at least {MIN_COUNT}")

    if parsed.count > MAX_COUNT:
        parser.error(f"--count cannot exceed {MAX_COUNT}")

    # Validate temperature
    if parsed.temperature < 0.0 or parsed.temperature > 2.0:
        parser.error("--temperature must be between 0.0 and 2.0")

    return CLIOptions(
        prompt=parsed.prompt,
        count=parsed.count,
        preview=parsed.preview,
        no_save=parsed.no_save,
        debug=parsed.debug,
        validate=parsed.validate,
        model=parsed.model,
        temperature=parsed.temperature,
        db_path=parsed.db_path,
    )


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Optional list of arguments (defaults to sys.argv)

    Returns:
        Exit code
    """
    options = parse_args(args)
    return run_cli(options)


if __name__ == "__main__":
    sys.exit(main())
