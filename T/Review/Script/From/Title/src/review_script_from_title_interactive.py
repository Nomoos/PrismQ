#!/usr/bin/env python3
"""Interactive Content Review CLI for PrismQ.

This script provides an interactive mode for reviewing scripts against titles.
It analyzes script-title alignment and provides improvement recommendations.

Usage:
    python review_content_from_title_interactive.py                    # Interactive mode
    python review_content_from_title_interactive.py --preview          # Preview mode
    python review_content_from_title_interactive.py --preview --debug  # Debug mode

Modes:
    Default: Reviews scripts and saves results to database
    Preview: Reviews scripts for testing without saving (extensive logging)
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
REVIEW_SCRIPT_FROM_TITLE_ROOT = SCRIPT_DIR.parent  # T/Review/Content/From/Title
REVIEW_SCRIPT_FROM_ROOT = REVIEW_SCRIPT_FROM_TITLE_ROOT.parent  # T/Review/Content/From
REVIEW_SCRIPT_ROOT = REVIEW_SCRIPT_FROM_ROOT.parent  # T/Review/Content
REVIEW_ROOT = REVIEW_SCRIPT_ROOT.parent  # T/Review
T_ROOT = REVIEW_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REVIEW_SCRIPT_FROM_TITLE_ROOT))
sys.path.insert(0, str(REVIEW_SCRIPT_ROOT))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model" / "src"))

# Import review modules
try:
    from by_title_v2 import (
        compare_reviews,
        extract_improvements_from_review,
        get_next_steps,
        is_ready_to_proceed,
        review_content_by_title_v2,
    )

    REVIEW_V2_AVAILABLE = True
except ImportError as e:
    REVIEW_V2_AVAILABLE = False
    IMPORT_ERROR_V2 = str(e)

try:
    from script_review_by_title import review_content_by_title

    REVIEW_AVAILABLE = True
except ImportError as e:
    REVIEW_AVAILABLE = False
    IMPORT_ERROR = str(e)

try:
    from script_review import ReviewCategory, ScriptReview

    SCRIPT_REVIEW_AVAILABLE = True
except ImportError:
    SCRIPT_REVIEW_AVAILABLE = False

# Try to import Idea model
try:
    from idea import ContentGenre, Idea

    IDEA_MODEL_AVAILABLE = True
except ImportError:
    IDEA_MODEL_AVAILABLE = False


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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'═' * 78}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(78)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'═' * 78}{Colors.END}\n")


def print_section(text: str) -> None:
    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.END}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.END}")


def print_success(text: str) -> None:
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str) -> None:
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str) -> None:
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str) -> None:
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


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
    - JSON with content_text, title fields
    - Plain text separated by newlines

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
                logger.info(f"Detected JSON input")

            content_text = data.get("content_text") or data.get("script") or ""
            title_text = data.get("title_text") or data.get("title") or ""

            # Create idea if provided
            idea = None
            if IDEA_MODEL_AVAILABLE and (data.get("idea") or data.get("concept")):
                idea_data = data.get("idea", {})
                if isinstance(idea_data, str):
                    idea = Idea(title=title_text, concept=idea_data, genre=ContentGenre.OTHER)
                else:
                    idea = Idea(
                        title=idea_data.get("title", title_text),
                        concept=idea_data.get("concept", ""),
                        genre=ContentGenre.OTHER,
                    )
            elif IDEA_MODEL_AVAILABLE:
                # Create default idea from title
                idea = Idea(title=title_text, concept=title_text, genre=ContentGenre.OTHER)

            return content_text, title_text, idea

        except json.JSONDecodeError as e:
            if logger:
                logger.warning(f"JSON parse failed: {e}")

    # Plain text - split by double newline
    parts = text.split("\n\n", 1)
    if len(parts) >= 2:
        content_text = parts[0].strip()
        title_text = parts[1].strip()
        idea = (
            Idea(title=title_text, concept=title_text, genre=ContentGenre.OTHER)
            if IDEA_MODEL_AVAILABLE
            else None
        )
        return content_text, title_text, idea

    # Single text - treat as script, ask for title
    return text, "", None


# =============================================================================
# Interactive Mode
# =============================================================================


def run_interactive_mode(preview: bool = False, debug: bool = False):
    """Run the interactive script review mode."""
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"review_content_from_title_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler(),
            ],
        )
        logger = logging.getLogger("PrismQ.Review.Content.From.Title")
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")

    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
    print_header(f"PrismQ Review Content From Title - {mode_text}")

    # Check module availability
    if not REVIEW_AVAILABLE and not REVIEW_V2_AVAILABLE:
        print_error(f"Review module not available")
        if logger:
            logger.error(f"Module import failed")
        return 1

    print_success("Content review module loaded")
    if logger:
        logger.info("Review module loaded successfully")

    if preview:
        print_warning("Preview mode - reviews will NOT be saved to database")
        print_info("This mode is for testing and tuning. Check logs for details.")

    # Interactive loop
    print_section("Enter Review Input")
    print("Enter script and title as JSON or separated by blank line:")
    print('JSON: {"content_text": "Content content...", "title": "Title"}')
    print("Or enter script, press Enter twice, then title.")
    print("Type 'quit' to exit.\n")

    while True:
        print(f"{Colors.CYAN}>>> Enter script (or JSON): {Colors.END}", end="")

        try:
            first_line = input().strip()
            if first_line.lower() == "quit":
                print_info("Exiting...")
                return 0

            if not first_line:
                continue

            # If JSON, process immediately
            if first_line.startswith("{"):
                content_text, title_text, idea = parse_review_input(first_line, logger)
            else:
                # Get full script (multiline)
                script_lines = [first_line]
                print(f"{Colors.CYAN}>>> Continue script (blank line to finish): {Colors.END}")
                while True:
                    line = input()
                    if line == "":
                        break
                    script_lines.append(line)
                content_text = "\n".join(script_lines)

                # Get title
                print(f"{Colors.CYAN}>>> Enter title: {Colors.END}", end="")
                title_text = input().strip()
                idea = (
                    Idea(title=title_text, concept=title_text, genre=ContentGenre.OTHER)
                    if IDEA_MODEL_AVAILABLE
                    else None
                )

        except EOFError:
            print_info("Exiting...")
            return 0
        except KeyboardInterrupt:
            print("\n")
            print_info("Interrupted. Type 'quit' to exit.")
            continue

        if not content_text or not title_text:
            print_error("Both script and title are required")
            continue

        if logger:
            logger.info(f"Reviewing script against title: {title_text[:50]}...")

        # Display input
        print_section("Review Input")
        print(f"  Title: {Colors.BOLD}{title_text}{Colors.END}")
        script_preview = content_text[:200] + "..." if len(content_text) > 200 else content_text
        print(f"  Content: {script_preview}")

        # Perform review
        print_section("Analyzing Content-Title Alignment")

        try:
            review = None

            if REVIEW_V2_AVAILABLE and idea:
                review = review_content_by_title_v2(
                    content_text=content_text,
                    title=title_text,
                    idea=idea,
                    script_version="v1",
                    title_version="v1",
                )
            elif REVIEW_AVAILABLE and idea:
                review = review_content_by_title(
                    content_text=content_text, title=title_text, idea=idea
                )

            if review:
                # Display review results
                print_section("Review Results")
                print(f"  Overall Score: {format_score(review.overall_score)}")

                # Get alignment scores from metadata
                title_alignment = int(review.metadata.get("title_alignment_score", 0) or 0)
                idea_alignment = int(review.metadata.get("idea_alignment_score", 0) or 0)

                if title_alignment:
                    print(f"  Title Alignment: {format_score(title_alignment)}")
                if idea_alignment:
                    print(f"  Idea Alignment: {format_score(idea_alignment)}")

                print(f"  Needs Major Revision: {'Yes' if review.needs_major_revision else 'No'}")

                # Category scores
                if review.category_scores:
                    print_section("Category Scores")
                    for cat_score in review.category_scores[:5]:
                        print(f"  {cat_score.category.value}: {format_score(cat_score.score)}")
                        if cat_score.reasoning:
                            print(f"    → {cat_score.reasoning[:80]}...")

                # Improvement points
                if review.improvement_points:
                    print_section("Improvement Recommendations")
                    for i, point in enumerate(review.improvement_points[:5], 1):
                        priority_color = (
                            Colors.RED
                            if point.priority == "high"
                            else (Colors.YELLOW if point.priority == "medium" else Colors.GRAY)
                        )
                        print(
                            f"  {i}. [{priority_color}{point.priority.upper()}{Colors.END}] {point.title}"
                        )
                        print(f"     {point.description[:100]}...")
                        if point.suggested_fix:
                            print(f"     → {Colors.GREEN}{point.suggested_fix[:80]}...{Colors.END}")

                # Overall assessment
                print_section("Assessment")
                if review.overall_score >= 80:
                    print_success("Content is well-aligned with title - Ready to proceed")
                elif review.overall_score >= 60:
                    print_warning("Content needs minor improvements")
                else:
                    print_error("Content needs major revision")

                # Next steps
                if REVIEW_V2_AVAILABLE:
                    steps = get_next_steps(review)
                    if steps:
                        print_section("Next Steps")
                        for step in steps:
                            print(f"  • {step}")
            else:
                print_warning("Could not generate full review - basic analysis only")
                print_info("Ensure Idea model is available for complete review")

            if logger:
                logger.info(
                    f"Review completed - Score: {review.overall_score if review else 'N/A'}"
                )

        except Exception as e:
            print_error(f"Error during review: {e}")
            if logger:
                logger.exception("Review failed")
            continue

        # Output as JSON option
        if review:
            json_choice = (
                input(f"\n{Colors.CYAN}Output as JSON? (y/n) [n]: {Colors.END}").strip().lower()
            )
            if json_choice == "y":
                print_section("JSON Output")
                review_dict = {
                    "overall_score": review.overall_score,
                    "needs_major_revision": review.needs_major_revision,
                    "category_scores": [
                        {
                            "category": cs.category.value,
                            "score": cs.score,
                            "reasoning": cs.reasoning,
                        }
                        for cs in review.category_scores
                    ],
                    "improvement_points": [
                        {
                            "title": p.title,
                            "description": p.description,
                            "priority": p.priority,
                            "suggested_fix": p.suggested_fix,
                        }
                        for p in review.improvement_points
                    ],
                }
                print(json.dumps(review_dict, indent=2, ensure_ascii=False))

        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print("Enter new script/title or type 'quit' to exit.\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive Content Review against Title for PrismQ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python review_content_from_title_interactive.py                    # Interactive mode
  python review_content_from_title_interactive.py --preview          # Preview mode
  python review_content_from_title_interactive.py --preview --debug  # Debug mode
        """,
    )

    parser.add_argument(
        "--preview", "-p", action="store_true", help="Preview mode - do not save to database"
    )
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    return run_interactive_mode(preview=args.preview, debug=args.debug)


if __name__ == "__main__":
    sys.exit(main())
