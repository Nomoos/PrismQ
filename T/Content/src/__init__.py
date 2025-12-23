"""T.Content - Content processing and generation utilities.

This module provides generic functionality for handling content
(processing, validation, transformation, AI generation).

Module Hierarchy:
- This is at PrismQ.T.Content level
- Contains content-specific utilities (AI config, processing helpers)
- Independent of content origin (Idea, Story, etc.)
"""

from .ai_config import (
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
