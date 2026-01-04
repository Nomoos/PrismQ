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
if str(T_SRC) not in sys.path:
    sys.path.insert(0, str(T_SRC))

# Re-export from T foundation level using absolute import to avoid circular import
# Import as 't_ai_config' to avoid name collision with this module
import importlib.util
spec = importlib.util.spec_from_file_location("t_ai_config", T_SRC / "ai_config.py")
t_ai_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t_ai_config)

# Re-export all needed items
AISettings = t_ai_config.AISettings
create_ai_config = t_ai_config.create_ai_config
check_ollama_available = t_ai_config.check_ollama_available
DEFAULT_AI_MODEL = t_ai_config.DEFAULT_AI_MODEL
DEFAULT_AI_API_BASE = t_ai_config.DEFAULT_AI_API_BASE
AI_TEMPERATURE_MIN = t_ai_config.AI_TEMPERATURE_MIN
AI_TEMPERATURE_MAX = t_ai_config.AI_TEMPERATURE_MAX
DEFAULT_AI_TIMEOUT = t_ai_config.DEFAULT_AI_TIMEOUT

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
