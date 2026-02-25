#!/usr/bin/env python3
"""Entry point for PrismQ.T.Story.From.Idea continuous processing.

This script delegates to src/story_from_idea_interactive.py which implements
the full continuous-mode workflow for creating Story objects from Idea objects.

Workflow:
    1. Connect to database
    2. Find Ideas without Story references (oldest first)
    3. Create 10 Story objects per Idea with state PrismQ.T.Title.From.Idea
    4. Save Stories to DB, commit transaction
    5. Loop continuously; wait 30s when no Ideas are pending, 1ms otherwise

Usage:
    python run.py                   # Continuous mode (default)
    python run.py --preview         # Preview mode (no DB changes)
    python run.py --debug           # Preview mode with debug output

Requirements:
    - Idea records must exist in the database (created by module 01)
    - Shared database (db.s3db) must be accessible
"""

import sys
from pathlib import Path

# Add src directory to path so story_from_idea_interactive can be imported
SCRIPT_DIR = Path(__file__).parent.absolute()
SRC_DIR = SCRIPT_DIR.parent.parent / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from story_from_idea_interactive import main

if __name__ == "__main__":
    sys.exit(main())
