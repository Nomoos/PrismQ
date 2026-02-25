#!/usr/bin/env python3
"""Entry point for PrismQ.T.Title.From.Idea continuous processing.

This script delegates to src/title_from_idea_interactive.py which implements
the full continuous-mode workflow for generating AI titles for Stories.

Workflow:
    1. Connect to database
    2. Find Stories with state PrismQ.T.Title.From.Idea (created by module 02)
    3. For each Story, generate 10 AI title variants (Ollama, temperature 0.6-0.8)
    4. Score each variant: rule-based (length) + AI scoring (title_scoring.txt)
    5. Select best variant (combined score, Jaccard similarity check vs siblings)
    6. Save Title to DB, update Story state to PrismQ.T.Content.From.Idea.Title
    7. Loop continuously; wait 30s when no Stories are pending

Usage:
    python run.py                   # Continuous mode (default)
    python run.py --preview         # Preview mode (no DB changes)
    python run.py --db PATH         # Custom database path
    python run.py --debug           # Enable debug logging

Requirements:
    - Ollama must be running with qwen3:32b model
    - Stories with state PrismQ.T.Title.From.Idea must exist (created by module 02)
"""

import sys
from pathlib import Path

# Add src directory to path so title_from_idea_interactive can be imported
SCRIPT_DIR = Path(__file__).parent.absolute()
SRC_DIR = SCRIPT_DIR.parent.parent / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from title_from_idea_interactive import main

if __name__ == "__main__":
    sys.exit(main())
