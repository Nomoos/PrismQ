"""Content-specific AI configuration wrapper.

This module re-exports AI configuration from T/src (foundation level).
It exists for backward compatibility with T/Content code.

For new code, import directly from T.src.ai_config.

Module Hierarchy:
- src/: Cross-cutting (database, config)
- T/: Text foundation (AI for all Text domains)  ← AI CONFIG IS HERE
- T/Content/: Content processing (uses T foundation AI)
- T/Content/From/Idea/Title/: Title-specific logic
"""

import sys
from pathlib import Path

# Add T/src to path for import
T_SRC = Path(__file__).parent.parent.parent / "src"  # T/src
sys.path.insert(0, str(T_SRC))

# Re-export from T foundation level
from ai_config import (
    AISettings,
    create_ai_config,
    check_ollama_available,
    DEFAULT_AI_MODEL,
    DEFAULT_AI_API_BASE,
    AI_TEMPERATURE_MIN,
    AI_TEMPERATURE_MAX,
    DEFAULT_AI_TIMEOUT,
)

__all__ = [
    "AISettings",
    "create_ai_config",
    "check_ollama_available",
    "DEFAULT_AI_MODEL",
    "DEFAULT_AI_API_BASE",
    "AI_TEMPERATURE_MIN",
    "AI_TEMPERATURE_MAX",
    "DEFAULT_AI_TIMEOUT",
]
