#!/usr/bin/env python3
"""Interactive Script Review by Title and Idea CLI for PrismQ.

This script provides an interactive mode for reviewing scripts against both
title and the originating idea. It evaluates title-script alignment,
idea-script alignment, and provides comprehensive improvement recommendations.

Usage:
    python review_script_by_title_idea_interactive.py                    # Interactive mode
    python review_script_by_title_idea_interactive.py --preview          # Preview mode
    python review_script_by_title_idea_interactive.py --preview --debug  # Debug mode

Modes:
    Default: Reviews scripts and saves results to database
    Preview: Reviews scripts for testing without saving (extensive logging)
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup paths - We're in T/Review/Content/From/Title/Idea/src/
SCRIPT_DIR = Path(__file__).parent.absolute()
FROM_TITLE_IDEA_ROOT = SCRIPT_DIR.parent  # T/Review/Content/From/Title/Idea
FROM_TITLE_ROOT = FROM_TITLE_IDEA_ROOT.parent  # T/Review/Content/From/Title
FROM_ROOT = FROM_TITLE_ROOT.parent  # T/Review/Content/From
REVIEW_CONTENT_ROOT = FROM_ROOT.parent  # T/Review/Content
REVIEW_ROOT = REVIEW_CONTENT_ROOT.parent  # T/Review
T_ROOT = REVIEW_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(FROM_TITLE_IDEA_ROOT))
sys.path.insert(0, str(REVIEW_CONTENT_ROOT))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model" / "src"))
sys.path.insert(0, str(REPO_ROOT))

# Import review modules
try:
    from by_title_and_idea import review_content_by_title_and_idea
    REVIEW_AVAILABLE = True
except ImportError as e:
    REVIEW_AVAILABLE = False
    IMPORT_ERROR = str(e)

try:
    from script_review import ReviewCategory, ScriptReview
    SCRIPT_REVIEW_AVAILABLE = True
except ImportError as e:
    SCRIPT_REVIEW_AVAILABLE = False
    SCRIPT_REVIEW_ERROR = str(e)

# Try to import Idea model
try:
    from idea import ContentGenre, Idea
    IDEA_MODEL_AVAILABLE = True
except ImportError as e:
    IDEA_MODEL_AVAILABLE = False
    IDEA_ERROR = str(e)

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


def format_score(score: int) -> str:
    """Format score with color based on value."""
    if score >= 80:
        return f"{Colors.GREEN}{score}%{Colors.END}"
    elif score >= 60:
        return f"{Colors.YELLOW}{score}%{Colors.END}"
    else:
        return f"{Colors.RED}{score}%{Colors.END}"


# =============================================================================
# Input Parsing
# =============================================================================


def parse_review_input(text: str, logger: Optional[logging.Logger] = None) -> tuple:
    """Parse input text for script review.

    Handles:
    - JSON with content_text, title, idea fields
    - Plain text (requires manual input)

    Returns:
        Tuple of (content_text, title_text, idea) or (None, None, None)
    """
    text = text.strip()

    if logger:
        logger.info(f"Parsing input text ({len(text)} chars)")

    # Try to parse as JSON
    if text.startswith("{"):
        try:
            data = json.loads(text)
            if logger:
                logger.info("Detected JSON input")

            content_text = data.get("content_text") or data.get("script") or ""
            title_text = data.get("title_text") or data.get("title") or ""

            # Create idea from JSON data
            idea = None
            if IDEA_MODEL_AVAILABLE:
                idea_data = data.get("idea", {})
                if isinstance(idea_data, dict):
                    idea = Idea(
                        title=idea_data.get("title", title_text),
                        concept=idea_data.get("concept", ""),
                        premise=idea_data.get("premise", ""),
                        hook=idea_data.get("hook", ""),
                        genre=ContentGenre[idea_data.get("genre", "OTHER").upper()],
                        target_audience=idea_data.get("target_audience"),
                        target_platforms=idea_data.get("target_platforms", []),
                        length_target=idea_data.get("length_target"),
                    )
                elif idea_data:
                    # Simple string concept
                    idea = Idea(title=title_text, concept=str(idea_data), genre=ContentGenre.OTHER)
                else:
                    # No idea data - create minimal idea
                    idea = Idea(title=title_text, concept=title_text, genre=ContentGenre.OTHER)

            return content_text, title_text, idea

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            if logger:
                logger.warning(f"JSON parse failed: {e}")

    # If not JSON or parsing failed, return None to prompt for manual input
    return None, None, None


def get_manual_input(logger: Optional[logging.Logger] = None) -> tuple:
    """Get review inputs manually from user.

    Returns:
        Tuple of (content_text, title_text, idea)
    """
    print_section("Manual Input Mode")
    print_info("Please provide the following information:")
    print()

    try:
        # Get title
        title_text = input(f"{Colors.CYAN}Title: {Colors.END}").strip()
        
        # Get script content
        print(f"\n{Colors.CYAN}Script content (paste text, then press Enter twice):{Colors.END}")
        lines = []
        empty_count = 0
        while empty_count < 2:
            try:
                line = input()
                if not line:
                    empty_count += 1
                else:
                    empty_count = 0
                    lines.append(line)
            except EOFError:
                # Handle Ctrl+D / EOF gracefully
                break
        content_text = "\n".join(lines).strip()

        # Get idea information
        print(f"\n{Colors.CYAN}Idea concept:{Colors.END}")
        concept = input().strip()

        print(f"\n{Colors.CYAN}Idea premise (optional):{Colors.END}")
        premise = input().strip()

        print(f"\n{Colors.CYAN}Genre (horror/mystery/science_fiction/educational/other):{Colors.END}")
        genre_input = input().strip().upper() or "OTHER"
        try:
            genre = ContentGenre[genre_input]
        except KeyError:
            genre = ContentGenre.OTHER
            print_warning(f"Unknown genre '{genre_input}', using OTHER")

        # Create idea
        idea = None
        if IDEA_MODEL_AVAILABLE:
            idea = Idea(
                title=title_text,
                concept=concept,
                premise=premise or concept,
                genre=genre,
            )

        return content_text, title_text, idea
    
    except EOFError:
        # User pressed Ctrl+D, return empty values
        if logger:
            logger.info("User cancelled input (EOF)")
        return None, None, None


# =============================================================================
# Review Display
# =============================================================================


def display_review(review: ScriptReview, logger: Optional[logging.Logger] = None) -> None:
    """Display review results in formatted output."""
    print_section(f"Review Results: {review.script_title}")

    # Overall score
    print(f"\n{Colors.BOLD}Overall Score:{Colors.END} {format_score(review.overall_score)}")
    
    # Title and Idea alignment
    if "title_alignment_score" in review.metadata:
        title_score = int(review.metadata["title_alignment_score"])
        print(f"{Colors.BOLD}Title Alignment:{Colors.END} {format_score(title_score)}")
    
    if "idea_alignment_score" in review.metadata:
        idea_score = int(review.metadata["idea_alignment_score"])
        print(f"{Colors.BOLD}Idea Alignment:{Colors.END} {format_score(idea_score)}")

    # Length information
    print(f"\n{Colors.BOLD}Content Length:{Colors.END}")
    print(f"  Current: {review.current_length_seconds}s")
    if review.optimal_length_seconds:
        print(f"  Target:  {review.optimal_length_seconds}s")
    print(f"  Category: {review.target_length.value}")

    # Category scores
    if review.category_scores:
        print(f"\n{Colors.BOLD}Category Scores:{Colors.END}")
        for cat_score in review.category_scores:
            score_str = format_score(cat_score.score)
            print(f"  {cat_score.category.value.capitalize():<20} {score_str}")
            if cat_score.strengths:
                for strength in cat_score.strengths:
                    print(f"    {Colors.GREEN}+ {strength}{Colors.END}")
            if cat_score.weaknesses:
                for weakness in cat_score.weaknesses:
                    print(f"    {Colors.RED}- {weakness}{Colors.END}")

    # Primary concern and quick wins
    if review.primary_concern:
        print(f"\n{Colors.BOLD}{Colors.RED}Primary Concern:{Colors.END}")
        print(f"  {review.primary_concern}")

    if review.quick_wins:
        print(f"\n{Colors.BOLD}{Colors.GREEN}Quick Wins:{Colors.END}")
        for win in review.quick_wins:
            print(f"  • {win}")

    # Improvement points
    if review.improvement_points:
        print(f"\n{Colors.BOLD}Improvement Recommendations:{Colors.END}")
        for i, point in enumerate(review.improvement_points[:5], 1):  # Top 5
            priority_color = Colors.RED if point.priority == "high" else Colors.YELLOW
            print(f"\n  {i}. {priority_color}[{point.priority.upper()}]{Colors.END} {point.title}")
            print(f"     {point.description}")
            if point.suggested_fix:
                print(f"     {Colors.CYAN}→ {point.suggested_fix}{Colors.END}")
            print(f"     {Colors.GRAY}Impact: +{point.impact_score}%{Colors.END}")

    # Major revision flag
    if review.needs_major_revision:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠ Major revision recommended{Colors.END}")
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Ready to proceed with minor improvements{Colors.END}")


# =============================================================================
# Database Operations
# =============================================================================


def save_review_to_database(
    review: ScriptReview,
    preview_mode: bool = False,
    logger: Optional[logging.Logger] = None
) -> bool:
    """Save review results to database.

    Args:
        review: ScriptReview object to save
        preview_mode: If True, don't actually save
        logger: Logger instance

    Returns:
        True if saved successfully or in preview mode, False otherwise
    """
    if preview_mode:
        print_warning("Preview mode - review NOT saved to database")
        if logger:
            logger.info("Preview mode - skipping database save")
        return True  # Return True in preview mode (operation successful, just skipped)

    try:
        # Import database dependencies
        from Model.Infrastructure.connection import connection_context
        from Model.Entities.review import Review
        from Model.Repositories.review_repository import ReviewRepository
        
        # Import config to get database path
        if not CONFIG_AVAILABLE:
            print_error("Database configuration not available")
            if logger:
                logger.error("Cannot save review: Config module not available")
            return False
        
        # Get database path from config
        config = Config(interactive=False)
        db_path = config.database_path
        
        if logger:
            logger.info(f"Saving review to database: {db_path}")
        
        # Serialize the review to JSON for storage
        review_json = json.dumps(review.to_dict(), indent=2)
        
        # Create Review entity
        review_entity = Review(
            text=review_json,
            score=review.overall_score
        )
        
        # Save to database
        with connection_context(db_path) as conn:
            repo = ReviewRepository(conn)
            saved_review = repo.insert(review_entity)
            conn.commit()
            
            if logger:
                logger.info(f"Review saved successfully with ID: {saved_review.id}")
            
            print_success(f"Review saved to database with ID: {saved_review.id}")
            return True
            
    except ImportError as e:
        print_error(f"Database module import failed: {e}")
        if logger:
            logger.error(f"Cannot save review: Import error - {e}")
        return False
    except Exception as e:
        print_error(f"Failed to save review to database: {e}")
        if logger:
            logger.error(f"Database save failed: {e}", exc_info=True)
        return False


# =============================================================================
# Logging Setup
# =============================================================================


def setup_logging(debug: bool = False) -> logging.Logger:
    """Setup logging configuration.

    Args:
        debug: Enable debug level logging

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = FROM_TITLE_IDEA_ROOT / "_meta" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("review_script_by_title_idea")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Clear existing handlers
    logger.handlers = []

    # File handler
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"review_{timestamp}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (warnings and errors by default, debug if enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.WARNING)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized - log file: {log_file}")
    return logger


# =============================================================================
# Main Interactive Loop
# =============================================================================


def run_interactive_mode(preview_mode: bool = False, debug: bool = False) -> None:
    """Run the interactive review mode.

    Args:
        preview_mode: If True, don't save to database
        debug: Enable debug logging
    """
    logger = setup_logging(debug)
    
    mode_name = "PREVIEW" if preview_mode else "RUN"
    print_header(f"Script Review by Title and Idea - {mode_name} MODE")

    # Check dependencies
    if not REVIEW_AVAILABLE:
        print_error(f"Review module not available: {IMPORT_ERROR}")
        logger.error(f"Review module import failed: {IMPORT_ERROR}")
        sys.exit(1)

    if not IDEA_MODEL_AVAILABLE:
        print_error(f"Idea model not available: {IDEA_ERROR}")
        logger.error(f"Idea model import failed: {IDEA_ERROR}")
        sys.exit(1)

    if preview_mode:
        print_warning("Preview mode - reviews will NOT be saved to database")
    else:
        print_info("Run mode - reviews will be saved to database")

    logger.info(f"Starting interactive mode (preview={preview_mode}, debug={debug})")

    # Main interactive loop
    while True:
        print_section("New Review")
        print_info("Enter review data (JSON or press Enter for manual input):")
        print_info("Press Ctrl+C to exit")
        print()

        try:
            # Get input
            user_input = input(f"{Colors.CYAN}> {Colors.END}").strip()

            # Parse input
            content_text, title_text, idea = parse_review_input(user_input, logger)

            # If parsing failed, get manual input
            if not content_text or not title_text or not idea:
                content_text, title_text, idea = get_manual_input(logger)

            # Validate inputs
            if not content_text:
                print_error("Content text is required")
                continue
            
            if not title_text:
                print_error("Title is required")
                continue

            if not idea:
                print_error("Idea information is required")
                continue

            # Log review attempt
            logger.info(f"Reviewing script: '{title_text}' ({len(content_text)} chars)")

            # Perform review
            print_info("Analyzing script...")
            review = review_content_by_title_and_idea(
                content_text=content_text,
                title=title_text,
                idea=idea,
            )

            # Display results
            display_review(review, logger)

            # Save to database
            if not preview_mode:
                print_info("\nSaving review to database...")
                saved = save_review_to_database(review, preview_mode, logger)
                if saved:
                    print_success("Review saved successfully")
                else:
                    print_warning("Review not saved")

            # Log completion
            logger.info(f"Review completed: score={review.overall_score}%")

            print()

        except KeyboardInterrupt:
            print("\n")
            print_info("Exiting...")
            logger.info("User interrupted")
            break
        except Exception as e:
            print_error(f"Error during review: {e}")
            logger.exception(f"Error during review: {e}")
            print()


# =============================================================================
# Main Entry Point
# =============================================================================


def main():
    """Main entry point for the interactive script."""
    parser = argparse.ArgumentParser(
        description="Interactive Script Review by Title and Idea CLI for PrismQ"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview mode - don't save reviews to database"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    try:
        run_interactive_mode(preview_mode=args.preview, debug=args.debug)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
