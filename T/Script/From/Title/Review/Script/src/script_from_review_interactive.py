#!/usr/bin/env python3
"""Interactive Script Improvement CLI for PrismQ.

This script provides an interactive mode for improving scripts based on review feedback.

Usage:
    python script_from_review_interactive.py                    # Interactive mode
    python script_from_review_interactive.py --preview          # Preview mode
    python script_from_review_interactive.py --preview --debug  # Debug mode
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()
SCRIPT_FROM_REVIEW_ROOT = SCRIPT_DIR.parent  # T/Script/From/Title/Review/Script
T_ROOT = SCRIPT_FROM_REVIEW_ROOT.parent.parent.parent.parent.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_FROM_REVIEW_ROOT))
sys.path.insert(0, str(T_ROOT / "Review" / "Script"))
sys.path.insert(0, str(T_ROOT / "Review" / "Title" / "From" / "Script" / "Idea"))

# Import modules
try:
    from script_improver import ScriptImprover, improve_script_from_reviews, ImprovedScript
    IMPROVER_AVAILABLE = True
except ImportError as e:
    IMPROVER_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import review modules for creating mock reviews
try:
    from script_review import ScriptReview, ReviewCategory, ImprovementPoint, CategoryScore
    SCRIPT_REVIEW_AVAILABLE = True
except ImportError:
    SCRIPT_REVIEW_AVAILABLE = False


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
# Mock Review Creator
# =============================================================================

def create_mock_script_review(script: str, title: str, score: int = 65) -> Optional['ScriptReview']:
    """Create a mock script review for testing."""
    if not SCRIPT_REVIEW_AVAILABLE:
        return None
    
    return ScriptReview(
        script_id=f"script-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        script_text=script,
        script_version="v1",
        overall_score=score,
        category_scores=[
            CategoryScore(
                category=ReviewCategory.STRUCTURE,
                score=score,
                reasoning="Mock review for testing"
            )
        ],
        improvement_points=[
            ImprovementPoint(
                category=ReviewCategory.STRUCTURE,
                title="Improve opening hook",
                description="The opening could be more engaging to match title promise",
                priority="high",
                impact_score=75,
                suggested_fix="Start with a compelling hook that connects to the title"
            ),
            ImprovementPoint(
                category=ReviewCategory.CONTENT,
                title="Strengthen conclusion",
                description="The ending needs more impact",
                priority="medium",
                impact_score=60,
                suggested_fix="Add a memorable closing statement"
            )
        ],
        needs_major_revision=score < 60
    )


# =============================================================================
# Interactive Mode
# =============================================================================

def run_interactive_mode(preview: bool = False, debug: bool = False):
    """Run the interactive script improvement mode."""
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"script_from_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename
        
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler() if debug else logging.NullHandler()
            ]
        )
        logger = logging.getLogger('PrismQ.Script.From.Review')
        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")
    
    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
    print_header(f"PrismQ Script From Title Review - {mode_text}")
    
    # Check module availability
    if not IMPROVER_AVAILABLE:
        print_error(f"Script improver module not available: {IMPORT_ERROR}")
        if logger:
            logger.error(f"Module import failed: {IMPORT_ERROR}")
        return 1
    
    print_success("Script improver module loaded")
    if logger:
        logger.info("Script improver module loaded successfully")
    
    if preview:
        print_warning("Preview mode - results will NOT be saved to database")
        print_info("This mode is for testing and tuning. Check logs for details.")
    
    # Interactive loop
    print_section("Enter Improvement Input")
    print("Enter script text and title as JSON:")
    print('JSON: {"script": "Script content...", "title": "Title", "score": 65}')
    print("Or enter step by step (script, then title).")
    print("Type 'quit' to exit.\n")
    
    while True:
        print(f"{Colors.CYAN}>>> Enter script (or JSON): {Colors.END}", end="")
        
        try:
            first_line = input().strip()
            if first_line.lower() == 'quit':
                print_info("Exiting...")
                return 0
            
            if not first_line:
                continue
            
            # If JSON, process immediately
            if first_line.startswith('{'):
                try:
                    data = json.loads(first_line)
                    original_script = data.get('script', '')
                    title_text = data.get('title', '')
                    mock_score = data.get('score', 65)
                except json.JSONDecodeError:
                    print_error("Invalid JSON format")
                    continue
            else:
                # Get script step by step
                script_lines = [first_line]
                print(f"{Colors.CYAN}>>> Continue script (blank line to finish): {Colors.END}")
                while True:
                    line = input()
                    if line == '':
                        break
                    script_lines.append(line)
                original_script = '\n'.join(script_lines)
                
                print(f"{Colors.CYAN}>>> Enter title: {Colors.END}", end="")
                title_text = input().strip()
                mock_score = 65
            
        except EOFError:
            print_info("Exiting...")
            return 0
        except KeyboardInterrupt:
            print("\n")
            print_info("Interrupted. Type 'quit' to exit.")
            continue
        
        if not original_script or not title_text:
            print_error("Both script and title are required")
            continue
        
        if logger:
            logger.info(f"Improving script for title: {title_text[:50]}...")
        
        # Display input
        print_section("Improvement Input")
        print(f"  Title: {Colors.BOLD}{title_text}{Colors.END}")
        script_preview = original_script[:200] + '...' if len(original_script) > 200 else original_script
        print(f"  Script: {script_preview}")
        
        # Create reviews (mock)
        print_section("Creating Reviews")
        script_review = create_mock_script_review(original_script, title_text, mock_score)
        
        if not script_review:
            print_error("Could not create review - check dependencies")
            continue
        
        print_success(f"Created script review (score: {mock_score}%)")
        
        # Generate improved script
        print_section("Generating Improved Script")
        
        try:
            improver = ScriptImprover()
            result = improver.improve_script(
                original_script=original_script,
                title_text=title_text,
                script_review=script_review,
                original_version_number="v1",
                new_version_number="v2"
            )
            
            # Display results
            print_section("Improvement Results")
            print(f"\n  Original length: {len(original_script)} chars")
            print(f"  Improved length: {len(result.new_version.text)} chars")
            
            print_section("Changes Made")
            print(f"  Rationale:")
            for line in result.rationale.split('\n'):
                print(f"    {line}")
            
            if result.addressed_improvements:
                print_section("Addressed Improvements")
                for imp in result.addressed_improvements:
                    print(f"  • {imp}")
            
            if result.title_alignment_notes:
                print_section("Title Alignment Notes")
                for line in result.title_alignment_notes.split('\n'):
                    print(f"    {line}")
            
            if result.structure_notes:
                print_section("Structure Notes")
                for line in result.structure_notes.split('\n'):
                    print(f"    {line}")
            
            # Show improved script
            show_script = input(f"\n{Colors.CYAN}Show improved script? (y/n) [n]: {Colors.END}").strip().lower()
            if show_script == 'y':
                print_section("Improved Script Text")
                print(result.new_version.text)
            
            if logger:
                logger.info(f"Script improved: {len(original_script)} → {len(result.new_version.text)} chars")
                
        except Exception as e:
            print_error(f"Error during improvement: {e}")
            if logger:
                logger.exception("Improvement failed")
            continue
        
        # Output as JSON option
        json_choice = input(f"\n{Colors.CYAN}Output as JSON? (y/n) [n]: {Colors.END}").strip().lower()
        if json_choice == 'y':
            print_section("JSON Output")
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        
        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.END}")
        print("Enter new script/title or type 'quit' to exit.\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Interactive Script Improvement from Reviews for PrismQ',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script_from_review_interactive.py                    # Interactive mode
  python script_from_review_interactive.py --preview          # Preview mode
  python script_from_review_interactive.py --preview --debug  # Debug mode
        """
    )
    
    parser.add_argument('--preview', '-p', action='store_true',
                       help='Preview mode - do not save to database')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    return run_interactive_mode(preview=args.preview, debug=args.debug)


if __name__ == '__main__':
    sys.exit(main())
