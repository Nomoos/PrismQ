"""T.Content - Content processing and generation utilities.

This module provides generic functionality for handling content
(processing, validation, transformation, AI generation).

Module Hierarchy:
- This is at PrismQ.T.Content level
- Uses T foundation services (AI from T/src)
- Independent of content origin (Idea, Story, etc.)
"""

import sys
from pathlib import Path

# Add T/src to path for import
T_SRC = Path(__file__).parent.parent.parent / "src"  # T/src
sys.path.insert(0, str(T_SRC))

# Re-export AI config from T foundation level for convenience
from ai_config import (
    AISettings,
    create_ai_config,
    check_ollama_available,
    DEFAULT_AI_MODEL,
    AI_TEMPERATURE_MIN,
    AI_TEMPERATURE_MAX,
)

__all__ = [
    "AISettings",
    "create_ai_config",
    "check_ollama_available",
    "DEFAULT_AI_MODEL",
    "AI_TEMPERATURE_MIN",
    "AI_TEMPERATURE_MAX",
]
