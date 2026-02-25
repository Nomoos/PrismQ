#!/usr/bin/env python3
"""Interactive Idea Creation CLI for PrismQ.

This script provides continuous interactive mode for creating ideas from text
input. It waits for user input, processes it through the idea variant system,
and saves to the database.

**IMPORTANT - Single Shared Database:**
PrismQ uses ONE shared database (db.s3db) for ALL modules (T, A, V, P, M).
All Idea, Story, Title, Content, and other tables are in this single database.
DO NOT create multiple database connections or separate databases.

The database connection is established once at initialization and reused
across all operations for efficiency.

Usage:
    python idea_creation_interactive.py
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Setup paths
_SCRIPT_DIR = Path(__file__).parent.absolute()
_CREATION_ROOT = _SCRIPT_DIR.parent        # T/Idea/Creation
_IDEA_ROOT = _CREATION_ROOT.parent        # T/Idea
_T_ROOT = _IDEA_ROOT.parent               # T
_REPO_ROOT = _T_ROOT.parent               # repo root

# Add repo root for src module imports
sys.path.insert(0, str(_REPO_ROOT))
# Add user module src for generation backend
_USER_SRC = _IDEA_ROOT / "From" / "User" / "src"
sys.path.insert(0, str(_USER_SRC))

logger = logging.getLogger(__name__)

# Try to import Config from shared src module
try:
    from src.config import Config as _Config
except ImportError:
    _Config = None


# =============================================================================
# Public API
# =============================================================================


def get_database_path() -> str:
    """Get the path to the shared PrismQ database (db.s3db).

    Returns the database path from Config if available, otherwise falls back
    to C:/PrismQ/db.s3db.

    Returns:
        Path string to the shared db.s3db database file.
    """
    if _Config is not None:
        config = _Config(interactive=False)
        return config.database_path
    return str(Path("C:/PrismQ") / "db.s3db")


def parse_input_text(
    text: str,
    log: Optional[logging.Logger] = None,
) -> Tuple[str, str, Dict]:
    """Parse input text and extract title, description, and metadata.

    Handles:
    - Plain text short (title/keyword) - returned as title with empty description
    - Plain text long (story snippet) - first sentence as title, full text as description
    - JSON data with story_title, title, theme, tone, etc.

    Args:
        text: Input text (plain text or JSON).
        log: Optional logger for debug output.

    Returns:
        Tuple of (title, description, metadata).
    """
    text = text.strip()
    metadata: Dict = {}

    if log:
        log.info(f"Parsing input text ({len(text)} chars)")

    # Try to parse as JSON
    if text.startswith("{"):
        try:
            data = json.loads(text)

            title = (
                data.get("story_title")
                or data.get("title")
                or data.get("theme")
                or data.get("topic")
                or data.get("keyword")
                or data.get("name")
                or "Untitled Idea"
            )

            desc_parts = []
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

            if data.get("potencial"):
                metadata["potential"] = data["potencial"]

            description = ". ".join(desc_parts) if desc_parts else ""

            if log:
                log.info(f"Extracted title: '{title}'")

            return title, description, metadata

        except json.JSONDecodeError as e:
            if log:
                log.warning(f"JSON parse failed: {e}")

    # Short plain text: use as-is (title only)
    if len(text) <= 100:
        if log:
            log.info(f"Short text, using as title: '{text}'")
        return text, "", metadata

    # Long plain text: first sentence as title, full text as description
    sentences = re.split(r"[.!?]", text)
    first_sentence = sentences[0].strip() if sentences else text[:80]

    if len(first_sentence) > 80:
        title = first_sentence[:77] + "..."
    else:
        title = first_sentence

    if log:
        log.info(f"Extracted title from long text: '{title}'")

    return title, text, metadata


def run_interactive_mode() -> int:
    """Run the continuous interactive idea creation mode.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    logger.info("Starting interactive mode")

    # Delegate to the backend implementation in T/Idea/From/User/src/
    try:
        import importlib.util

        _spec = importlib.util.spec_from_file_location(
            "_user_idea_creation_interactive",
            str(_USER_SRC / "idea_creation_interactive.py"),
        )
        if _spec is None or _spec.loader is None:
            raise ImportError("Could not load user idea_creation_interactive module")

        _module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)  # type: ignore[union-attr]
        return _module.run_interactive_mode()

    except Exception as e:
        logger.error(f"Failed to run interactive mode: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    return run_interactive_mode()


if __name__ == "__main__":
    sys.exit(main())
