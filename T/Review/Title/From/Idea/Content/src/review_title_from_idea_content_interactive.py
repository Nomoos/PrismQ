#!/usr/bin/env python3
"""Interactive Title Review CLI for PrismQ.T.Review.Title.From.Idea.Content

This script provides AI-powered title review using Ollama with Qwen3:32b.
It evaluates titles based on Idea (intent) and Content (delivery), producing
narrative review text.

Usage:
    python review_title_by_idea_content_interactive.py                    # Interactive mode
    python review_title_by_idea_content_interactive.py --preview          # Preview mode (extensive logging)
    python review_title_by_idea_content_interactive.py --preview --debug  # Debug mode with full logging

Modes:
    Default: Generates reviews (ready for production integration)
    Preview: Testing mode with extensive logging
    Debug: Full diagnostic logging including API requests/responses

Requirements:
    - Ollama running locally (http://localhost:11434)
    - Qwen3:32b model installed (ollama pull qwen3:32b)
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup paths - Now in T/Review/Title/From/Idea/Content/src/
SCRIPT_DIR = Path(__file__).parent.absolute()
MODULE_ROOT = SCRIPT_DIR.parent  # T/Review/Title/From/Idea/Content
TITLE_FROM_ROOT = MODULE_ROOT.parent.parent  # T/Review/Title/From
TITLE_ROOT = TITLE_FROM_ROOT.parent  # T/Review/Title
REVIEW_ROOT = TITLE_ROOT.parent  # T/Review
T_ROOT = REVIEW_ROOT.parent  # T
REPO_ROOT = T_ROOT.parent  # repo root

# Add paths for imports
sys.path.insert(0, str(SCRIPT_DIR))  # Current directory for local imports
sys.path.insert(0, str(REPO_ROOT))  # Add repo root

# Try to import our review module
try:
    from by_idea_and_content import review_title_by_idea_and_content
    from title_review import TitleReview

    REVIEW_MODULE_AVAILABLE = True
except ImportError as e:
    REVIEW_MODULE_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Try to import requests for Ollama API
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


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
# AI Prompt Template (Narrative Format)
# =============================================================================

NARRATIVE_PROMPT_TEMPLATE = """You are a senior title editor and viral content strategist.

Your task is to WRITE A TEXTUAL REVIEW of a TITLE based on:
- the STORY IDEA (original intent and promise)
- the CONTENT (existing / obsolete script or final content)

You are NOT reviewing the content quality.
You are reviewing the TITLE's effectiveness, accuracy, and emotional performance
given what the audience is promised (Idea) and what they actually receive (Content).

---

INPUT:

STORY IDEA:
{idea}

CONTENT:
{content}

CURRENT TITLE:
{title}

---

ANALYSIS RULES (internal, do not output):
- Compare title promise vs idea intent
- Compare title promise vs content delivery
- Detect overpromise, underpromise, or misdirection
- Judge emotional pull in under 1 second
- Consider trust, retention, and replay motivation
- Assume short-form, audio-first, emotion-driven platforms

---

OUTPUT RULES (STRICT):
- Output ONLY a continuous review text (paragraphs allowed)
- Do NOT use headings, lists, or bullet points
- Do NOT quote the prompt or structure
- Do NOT mention scores or labels explicitly
- Do NOT rewrite or summarize the content
- Do NOT suggest content changes
- You MAY suggest title improvements or alternatives naturally within the text
- Tone: professional, precise, critical but constructive

The review should clearly answer:
- Does the title fit the idea?
- Does the title truthfully represent the content?
- Does it create enough emotional tension to earn the click?
- What is the main risk of keeping this title as-is?"""


# =============================================================================
# Ollama Integration
# =============================================================================


def check_ollama_available(logger: Optional[logging.Logger] = None) -> bool:
    """Check if Ollama is running and accessible.

    Args:
        logger: Optional logger for diagnostic output

    Returns:
        True if Ollama is available, False otherwise
    """
    if not REQUESTS_AVAILABLE:
        if logger:
            logger.error("requests library not available")
        return False

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            if logger:
                logger.info("Ollama service is running")
            return True
        else:
            if logger:
                logger.warning(f"Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        if logger:
            logger.error("Cannot connect to Ollama (connection refused)")
        return False
    except requests.exceptions.Timeout:
        if logger:
            logger.error("Ollama connection timeout")
        return False
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error checking Ollama: {e}")
        return False


def check_qwen3_available(logger: Optional[logging.Logger] = None) -> bool:
    """Check if Qwen3:32b model is installed in Ollama.

    Args:
        logger: Optional logger for diagnostic output

    Returns:
        True if Qwen3:32b is available, False otherwise
    """
    if not REQUESTS_AVAILABLE:
        return False

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model.get("name", "") for model in data.get("models", [])]
            
            # Check for qwen3:32b
            qwen3_found = any("qwen3" in model and "32b" in model for model in models)
            
            if logger:
                logger.info(f"Found models: {', '.join(models)}")
                if qwen3_found:
                    logger.info("Qwen3:32b model is available")
                else:
                    logger.warning("Qwen3:32b model not found")
            
            return qwen3_found
        return False
    except Exception as e:
        if logger:
            logger.error(f"Error checking Qwen3 availability: {e}")
        return False


def generate_title_review_with_ai(
    title_text: str,
    idea_summary: str,
    content_text: str,
    logger: Optional[logging.Logger] = None,
) -> str:
    """Generate narrative title review using Ollama + Qwen3:32b.

    Args:
        title_text: The title to review
        idea_summary: Summary of the story idea
        content_text: The content/script text
        logger: Optional logger for diagnostic output

    Returns:
        Narrative review text from AI

    Raises:
        Exception if AI generation fails
    """
    if logger:
        logger.info("Generating AI review with Qwen3:32b")
        logger.debug(f"Title: {title_text}")
        logger.debug(f"Idea length: {len(idea_summary)} chars")
        logger.debug(f"Content length: {len(content_text)} chars")

    # Format the prompt
    prompt = NARRATIVE_PROMPT_TEMPLATE.format(
        title=title_text, idea=idea_summary, content=content_text
    )

    if logger:
        logger.debug(f"Prompt length: {len(prompt)} chars")

    # Ollama parameters optimized for Qwen3:32b narrative format
    params = {
        "temperature": 0.75,
        "top_p": 0.9,
        "top_k": 40,
        "num_predict": 900,
        "repeat_penalty": 1.05,
        "stop": ["INPUT:", "ANALYSIS RULES", "---"],
    }

    try:
        if logger:
            logger.info("Sending request to Ollama...")

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen3:32b", "prompt": prompt, "stream": False, "options": params},
            timeout=120,  # 2 minutes timeout for AI generation
        )

        if logger:
            logger.info(f"Ollama response status: {response.status_code}")

        response.raise_for_status()
        result = response.json()
        review_text = result.get("response", "").strip()

        if logger:
            logger.info(f"Generated review: {len(review_text)} chars")
            logger.debug(f"Review text: {review_text[:200]}...")

        if not review_text:
            raise ValueError("AI returned empty review")

        return review_text

    except requests.exceptions.Timeout:
        error_msg = "AI generation timed out (>2 minutes)"
        if logger:
            logger.error(error_msg)
        raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f"Ollama API request failed: {e}"
        if logger:
            logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"AI generation failed: {e}"
        if logger:
            logger.error(error_msg)
        raise Exception(error_msg)


# =============================================================================
# Main Interactive Loop
# =============================================================================


def main(preview: bool = False, debug: bool = False) -> int:
    """Main interactive loop for title review.

    Args:
        preview: If True, runs in preview mode with extensive logging
        debug: If True, enables debug-level logging

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Setup logging
    logger = None
    if debug or preview:
        log_filename = f"title_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = SCRIPT_DIR / log_filename

        # Create logger
        logger = logging.getLogger("PrismQ.T.Review.Title.From.Idea.Content")
        logger.setLevel(logging.DEBUG)

        # File handler - captures all messages
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)

        # Console handler - only INFO and above
        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            logger.addHandler(console_handler)

        logger.info(f"Session started - Preview: {preview}, Debug: {debug}")
        print_info(f"Logging to: {log_path}")

    # Print header
    mode_text = "PREVIEW MODE" if preview else "INTERACTIVE MODE"
    print_header(f"PrismQ Title Review - {mode_text}")

    # Check module availability
    if not REVIEW_MODULE_AVAILABLE:
        print_error(f"Review module not available: {IMPORT_ERROR}")
        if logger:
            logger.error(f"Module import failed: {IMPORT_ERROR}")
        return 1

    print_success("Review module loaded")
    if logger:
        logger.info("Review module loaded successfully")

    if not REQUESTS_AVAILABLE:
        print_error("requests library not available (pip install requests)")
        if logger:
            logger.error("requests library not available")
        return 1

    print_success("requests library available")

    # Check Ollama availability
    print_section("Checking AI Service")
    
    if not check_ollama_available(logger):
        print_error("Ollama is not running or not accessible")
        print_info("Please start Ollama: ollama serve")
        if logger:
            logger.error("Ollama check failed")
        return 1

    print_success("Ollama service is running")

    if not check_qwen3_available(logger):
        print_error("Qwen3:32b model not found")
        print_info("Please install: ollama pull qwen3:32b")
        if logger:
            logger.error("Qwen3:32b not available")
        return 1

    print_success("Qwen3:32b model available")

    if preview:
        print_warning("Preview mode - for testing AI reviews")
        print_info("Reviews will be displayed but not saved")

    # Main loop
    print_section("Title Review Input")
    print("Enter title review details. Type 'quit' or 'exit' to stop.")
    print("Format: Provide title, idea, and content as prompted\n")

    review_count = 0

    while True:
        try:
            # Get title
            print(f"\n{Colors.BOLD}Title to review:{Colors.END} ", end="")
            title_input = input().strip()

            if title_input.lower() in ["quit", "exit", "q"]:
                break

            if not title_input:
                print_warning("Title cannot be empty")
                continue

            # Get idea
            print(f"{Colors.BOLD}Story idea:{Colors.END} ", end="")
            idea_input = input().strip()

            if not idea_input:
                print_warning("Idea cannot be empty")
                continue

            # Get content
            print(f"{Colors.BOLD}Content (multiline, end with empty line):{Colors.END}")
            content_lines = []
            while True:
                line = input()
                if not line.strip():
                    break
                content_lines.append(line)

            content_input = "\n".join(content_lines).strip()

            if not content_input:
                print_warning("Content cannot be empty")
                continue

            if logger:
                logger.info(f"Review request #{review_count + 1}")
                logger.info(f"Title: {title_input}")
                logger.info(f"Idea: {idea_input[:100]}...")
                logger.info(f"Content: {len(content_input)} chars")

            # Generate AI review
            print_section("Generating Review")
            print_info("Calling Qwen3:32b via Ollama...")

            try:
                review_text = generate_title_review_with_ai(
                    title_text=title_input,
                    idea_summary=idea_input,
                    content_text=content_input,
                    logger=logger,
                )

                review_count += 1

                # Display review
                print_section(f"Review #{review_count}")
                print(f"\n{review_text}\n")

                if logger:
                    logger.info(f"Review #{review_count} generated successfully")
                    logger.info(f"Review text:\n{review_text}")

                print_success(f"Review #{review_count} complete")

            except Exception as e:
                print_error(f"Failed to generate review: {e}")
                if logger:
                    logger.error(f"Review generation failed: {e}", exc_info=True)

        except KeyboardInterrupt:
            print("\n")
            print_warning("Interrupted by user")
            break
        except EOFError:
            print("\n")
            break
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            if logger:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)

    # Summary
    print_section("Session Summary")
    print(f"Total reviews generated: {review_count}")

    if logger:
        logger.info(f"Session ended - Total reviews: {review_count}")

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Interactive Title Review CLI")
    parser.add_argument("--preview", action="store_true", help="Preview mode (extensive logging)")
    parser.add_argument("--debug", action="store_true", help="Debug mode (full diagnostic logging)")

    args = parser.parse_args()

    sys.exit(main(preview=args.preview, debug=args.debug))
