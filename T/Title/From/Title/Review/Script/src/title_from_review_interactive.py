#!/usr/bin/env python3
"""Interactive Title Improvement CLI for PrismQ.

This script provides an interactive mode for improving titles based on review feedback.
It takes original title, script, and reviews to generate improved title versions.

Usage:
    python title_from_review_interactive.py                    # Interactive mode
    python title_from_review_interactive.py --preview          # Preview mode
    python title_from_review_interactive.py --preview --debug  # Debug mode

Modes:
    Default: Improves titles and saves results to database
    Preview: Improves titles for testing without saving (extensive logging)
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
TITLE_FROM_REVIEW_ROOT = SCRIPT_DIR.parent  # T/Title/From/Title/Review/Script
T_TITLE_ROOT = TITLE_FROM_REVIEW_ROOT.parent.parent.parent  # T/Title
T_ROOT = T_TITLE_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(TITLE_FROM_REVIEW_ROOT))
sys.path.insert(0, str(T_ROOT / "Idea" / "Model" / "src"))
sys.path.insert(0, str(T_ROOT / "Review" / "Title" / "From" / "Script" / "Idea"))
sys.path.insert(0, str(T_ROOT / "Review" / "Script"))

# Import modules
try:
    from title_improver import (
        ImprovedTitle,
        TitleImprover,
        TitleVersion,
        improve_title_from_reviews,
    )

    IMPROVER_AVAILABLE = True
except ImportError as e:
    IMPROVER_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import review modules for creating mock reviews
try:
    from title_review import (
        TitleCategoryScore,
        TitleImprovementPoint,
        TitleReview,
        TitleReviewCategory,
    )

    TITLE_REVIEW_AVAILABLE = True
except ImportError:
    TITLE_REVIEW_AVAILABLE = False

try:
    from script_review import (
        CategoryScore,
        ImprovementPoint,
        ReviewCategory,
        ScriptReview,
    )

    SCRIPT_REVIEW_AVAILABLE = True
except ImportError:
    SCRIPT_REVIEW_AVAILABLE = False

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
# Mock Review Creator (for testing without full review)
# =============================================================================


def create_mock_title_review(title: str, script: str, score: int = 70) -> Optional["TitleReview"]:
    """Create a mock title review for testing."""
    if not TITLE_REVIEW_AVAILABLE:
        return None

    return TitleReview(
        title_id=f"title-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        title_text=title,
        title_version="v1",
        overall_score=score,
        category_scores=[
            TitleCategoryScore(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                score=score,
                reasoning="Mock review for testing",
            )
        ],
        improvement_points=[
            TitleImprovementPoint(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                title="Improve script alignment",
                description="Title could better match script content",
                priority="medium",
                impact_score=70,
                suggested_fix="Include key script elements in title",
            )
        ],
        script_alignment_score=score,
        engagement_score=score,
        seo_score=score,
        length_score=80,
        key_script_elements=["story", "mystery", "discovery"],
        suggested_keywords=["untold", "hidden", "revealed"],
    )


def create_mock_script_review(script: str, title: str, score: int = 70) -> Optional["ScriptReview"]:
    """Create a mock script review for testing."""
    if not SCRIPT_REVIEW_AVAILABLE:
        return None

    return ScriptReview(
        script_id=f"script-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        script_text=script,
        script_version="v1",
        overall_score=score,
        category_scores=[],
        improvement_points=[
            ImprovementPoint(
                category=ReviewCategory.STRUCTURE,
                title="Improve title alignment",
                description="Script opening could better match title promise",
                priority="medium",
                impact_score=65,
                suggested_fix="Enhance opening to match title expectations",
            )
        ],
        needs_major_revision=score < 60,
    )


# =============================================================================
# Interactive Mode
# =============================================================================


def run_interactive_mode(preview: bool = False, debug: bool = False):
    """Run the interactive title improvement mode."""
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"title_from_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename

        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler(),
            ],
        )
        logger = logging.getLogger("PrismQ.Title.From.Review")
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")

    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
    print_header(f"PrismQ Title From Script Review - {mode_text}")

    # Check module availability
    if not IMPROVER_AVAILABLE:
        print_error(f"Title improver module not available: {IMPORT_ERROR}")
        if logger:
            logger.error(f"Module import failed: {IMPORT_ERROR}")
        return 1

    print_success("Title improver module loaded")
    if logger:
        logger.info("Title improver module loaded successfully")

    if preview:
        print_warning("Preview mode - results will NOT be saved to database")
        print_info("This mode is for testing and tuning. Check logs for details.")

    # Interactive loop
    print_section("Enter Improvement Input")
    print("Enter original title, script, and optionally reviews as JSON:")
    print('JSON: {"title": "Original Title", "script": "Script content...", "score": 65}')
    print("Or enter step by step (title, then script).")
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
                try:
                    data = json.loads(first_line)
                    original_title = data.get("title", "")
                    script_text = data.get("script", "")
                    mock_score = data.get("score", 65)
                except json.JSONDecodeError:
                    print_error("Invalid JSON format")
                    continue
            else:
                # Get title and script step by step
                original_title = first_line
                print(f"{Colors.CYAN}>>> Enter script text (blank line to finish): {Colors.END}")
                script_lines = []
                while True:
                    line = input()
                    if line == "":
                        break
                    script_lines.append(line)
                script_text = "\n".join(script_lines)
                mock_score = 65

        except EOFError:
            print_info("Exiting...")
            return 0
        except KeyboardInterrupt:
            print("\n")
            print_info("Interrupted. Type 'quit' to exit.")
            continue

        if not original_title or not script_text:
            print_error("Both title and script are required")
            continue

        if logger:
            logger.info(f"Improving title: {original_title[:50]}...")

        # Display input
        print_section("Improvement Input")
        print(f"  Original Title: {Colors.BOLD}{original_title}{Colors.END}")
        script_preview = script_text[:200] + "..." if len(script_text) > 200 else script_text
        print(f"  Script: {script_preview}")

        # Create reviews (mock or real)
        print_section("Creating Reviews")
        title_review = create_mock_title_review(original_title, script_text, mock_score)
        script_review = create_mock_script_review(script_text, original_title, mock_score)

        if not title_review or not script_review:
            print_error("Could not create reviews - check dependencies")
            continue

        print_success(f"Created title review (score: {mock_score}%)")
        print_success(f"Created script review (score: {mock_score}%)")

        # Generate improved title
        print_section("Generating Improved Title")

        try:
            improver = TitleImprover()
            result = improver.improve_title(
                original_title=original_title,
                script_text=script_text,
                title_review=title_review,
                script_review=script_review,
                original_version_number="v1",
                new_version_number="v2",
            )

            # Display results
            print_section("Improvement Results")
            print(f"\n  {Colors.RED}Original (v1): {original_title}{Colors.END}")
            print(f"  {Colors.GREEN}Improved (v2): {result.new_version.text}{Colors.END}")

            print_section("Changes Made")
            print(f"  Rationale:")
            for line in result.rationale.split("\n"):
                print(f"    {line}")

            if result.addressed_improvements:
                print_section("Addressed Improvements")
                for imp in result.addressed_improvements:
                    print(f"  • {imp}")

            if result.script_alignment_notes:
                print_section("Script Alignment Notes")
                for line in result.script_alignment_notes.split("\n"):
                    print(f"    {line}")

            if result.engagement_notes:
                print_section("Engagement Notes")
                for line in result.engagement_notes.split("\n"):
                    print(f"    {line}")

            if logger:
                logger.info(f"Title improved: {original_title} → {result.new_version.text}")

        except Exception as e:
            print_error(f"Error during improvement: {e}")
            if logger:
                logger.exception("Improvement failed")
            continue

        # Output as JSON option
        json_choice = (
            input(f"\n{Colors.CYAN}Output as JSON? (y/n) [n]: {Colors.END}").strip().lower()
        )
        if json_choice == "y":
            print_section("JSON Output")
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print("Enter new title/script or type 'quit' to exit.\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive Title Improvement from Reviews for PrismQ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python title_from_review_interactive.py                    # Interactive mode
  python title_from_review_interactive.py --preview          # Preview mode
  python title_from_review_interactive.py --preview --debug  # Debug mode
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
