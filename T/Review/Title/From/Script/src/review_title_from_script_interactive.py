#!/usr/bin/env python3
"""Interactive Title Review CLI for PrismQ.

This script provides an interactive mode for reviewing titles against scripts.
It analyzes title-script alignment and provides improvement recommendations.

Usage:
    python review_title_from_content_interactive.py                    # Interactive mode
    python review_title_from_content_interactive.py --preview          # Preview mode (no DB save)
    python review_title_from_content_interactive.py --preview --debug  # Debug mode

Modes:
    Default: Reviews titles and saves results to database
    Preview: Reviews titles for testing without saving (extensive logging)
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
REVIEW_TITLE_FROM_SCRIPT_ROOT = SCRIPT_DIR.parent  # T/Review/Title/From/Script
REVIEW_TITLE_FROM_ROOT = REVIEW_TITLE_FROM_SCRIPT_ROOT.parent  # T/Review/Title/From
REVIEW_TITLE_ROOT = REVIEW_TITLE_FROM_ROOT.parent  # T/Review/Title
REVIEW_ROOT = REVIEW_TITLE_ROOT.parent  # T/Review
T_ROOT = REVIEW_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REVIEW_TITLE_FROM_SCRIPT_ROOT))
sys.path.insert(0, str(REVIEW_TITLE_FROM_SCRIPT_ROOT / "Idea"))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model" / "src"))

# Import review modules
try:
    from by_content_v2 import (
        compare_reviews,
        get_improvement_summary,
        review_title_by_content_v2,
    )

    REVIEW_V2_AVAILABLE = True
except ImportError as e:
    REVIEW_V2_AVAILABLE = False
    IMPORT_ERROR_V2 = str(e)

try:
    from Idea.by_content_and_idea import (
        analyze_engagement,
        analyze_seo,
        analyze_title_content_alignment,
        extract_keywords,
        review_title_by_content_and_idea,
    )
    from Idea.title_review import TitleReview, TitleReviewCategory

    REVIEW_AVAILABLE = True
except ImportError as e:
    REVIEW_AVAILABLE = False
    IMPORT_ERROR = str(e)

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
    """Parse input text for title review.

    Handles:
    - JSON with title_text, content_text fields
    - Plain text separated by newlines

    Returns:
        Tuple of (title_text, content_text, idea) or (None, None, None)
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

            title_text = data.get("title_text") or data.get("title") or ""
            content_text = data.get("content_text") or data.get("script") or ""

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

            return title_text, content_text, idea

        except json.JSONDecodeError as e:
            if logger:
                logger.warning(f"JSON parse failed: {e}")

    # Plain text - split by double newline
    parts = text.split("\n\n", 1)
    if len(parts) >= 2:
        title_text = parts[0].strip()
        content_text = parts[1].strip()
        return title_text, content_text, None

    # Single line - treat as title, ask for script
    return text, "", None


# =============================================================================
# Interactive Mode
# =============================================================================


def run_interactive_mode(preview: bool = False, debug: bool = False):
    """Run the interactive title review mode."""
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"review_title_from_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler(),
            ],
        )
        logger = logging.getLogger("PrismQ.Review.Title.From.Content")
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")

    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
    print_header(f"PrismQ Review Title From Content - {mode_text}")

    # Check module availability
    if not REVIEW_AVAILABLE:
        print_error(f"Review module not available: {IMPORT_ERROR}")
        if logger:
            logger.error(f"Module import failed: {IMPORT_ERROR}")
        return 1

    print_success("Title review module loaded")
    if logger:
        logger.info("Review module loaded successfully")

    if preview:
        print_warning("Preview mode - reviews will NOT be saved to database")
        print_info("This mode is for testing and tuning. Check logs for details.")

    # Interactive loop
    print_section("Enter Review Input")
    print("Enter title and script as JSON or separated by blank line:")
    print('JSON: {"title_text": "Title", "content_text": "Content content..."}')
    print("Or enter title, press Enter twice, then script.")
    print("Type 'quit' to exit.\n")

    while True:
        print(f"{Colors.CYAN}>>> Enter title (or JSON): {Colors.END}", end="")

        try:
            first_line = input().strip()
            if first_line.lower() == "quit":
                print_info("Exiting...")
                return 0

            if not first_line:
                continue

            # If JSON, process immediately
            if first_line.startswith("{"):
                title_text, content_text, idea = parse_review_input(first_line, logger)
            else:
                # Get script text
                title_text = first_line
                print(f"{Colors.CYAN}>>> Enter script text (end with blank line): {Colors.END}")
                script_lines = []
                while True:
                    line = input()
                    if line == "":
                        break
                    script_lines.append(line)
                content_text = "\n".join(script_lines)
                idea = None

        except EOFError:
            print_info("Exiting...")
            return 0
        except KeyboardInterrupt:
            print("\n")
            print_info("Interrupted. Type 'quit' to exit.")
            continue

        if not title_text or not content_text:
            print_error("Both title and script are required")
            continue

        if logger:
            logger.info(f"Reviewing title: {title_text[:50]}...")

        # Display input
        print_section("Review Input")
        print(f"  Title: {Colors.BOLD}{title_text}{Colors.END}")
        script_preview = content_text[:200] + "..." if len(content_text) > 200 else content_text
        print(f"  Content: {script_preview}")

        # Perform review
        print_section("Analyzing Title-Content Alignment")

        try:
            # Use basic review if idea not available
            review = (
                review_title_by_content_v2(
                    title_text=title_text,
                    content_text=content_text,
                    title_version="v1",
                    script_version="v1",
                )
                if REVIEW_V2_AVAILABLE
                else None
            )

            if not review and REVIEW_AVAILABLE:
                # Use direct analysis functions
                alignment = analyze_title_content_alignment(title_text, content_text)
                engagement = analyze_engagement(title_text)
                keywords = extract_keywords(content_text)
                seo = analyze_seo(title_text, keywords)

                # Display results directly
                print_section("Review Results")
                print(f"  Content Alignment: {format_score(alignment.score)}")
                print(f"  Engagement Score: {format_score(engagement['engagement_score'])}")
                print(f"  SEO Score: {format_score(seo['seo_score'])}")
                print(f"  Length Score: {format_score(seo['length_score'])}")

                print_section("Alignment Details")
                print(
                    f"  Matches: {', '.join(alignment.matches[:5]) if alignment.matches else 'None'}"
                )
                print(
                    f"  Mismatches: {', '.join(alignment.mismatches[:5]) if alignment.mismatches else 'None'}"
                )
                print(
                    f"  Key Elements: {', '.join(alignment.key_elements[:5]) if alignment.key_elements else 'None'}"
                )

                print_section("Recommendations")
                if alignment.score < 70:
                    print_warning("Title needs better alignment with script content")
                if engagement["engagement_score"] < 70:
                    print_warning("Consider adding more engaging language")
                if seo["seo_score"] < 70:
                    print_warning("SEO optimization needed")
                    if seo["suggested_keywords"]:
                        print_info(
                            f"Suggested keywords: {', '.join(seo['suggested_keywords'][:5])}"
                        )

            elif review:
                # Display review results
                print_section("Review Results")
                print(f"  Overall Score: {format_score(review.overall_score)}")
                print(f"  Content Alignment: {format_score(review.script_alignment_score)}")
                print(f"  Engagement Score: {format_score(review.engagement_score)}")
                print(f"  SEO Score: {format_score(review.seo_score)}")
                print(f"  Length Score: {format_score(review.length_score)}")

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
                        print(f"     {point.description}")
                        if point.suggested_fix:
                            print(f"     → {Colors.GREEN}{point.suggested_fix}{Colors.END}")

                # Overall assessment
                print_section("Assessment")
                if review.overall_score >= 80:
                    print_success("Title is well-aligned with script - Ready to proceed")
                elif review.overall_score >= 60:
                    print_warning("Title needs minor improvements")
                else:
                    print_error("Title needs major revision")

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
                # Convert review to dict
                review_dict = {
                    "title_text": review.title_text,
                    "overall_score": review.overall_score,
                    "script_alignment_score": review.script_alignment_score,
                    "engagement_score": review.engagement_score,
                    "seo_score": review.seo_score,
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
        print("Enter new title/script or type 'quit' to exit.\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive Title Review against Content for PrismQ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python review_title_from_content_interactive.py                    # Interactive mode
  python review_title_from_content_interactive.py --preview          # Preview mode
  python review_title_from_content_interactive.py --preview --debug  # Debug mode
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
