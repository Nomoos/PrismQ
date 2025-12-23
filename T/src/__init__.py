"""PrismQ.T (Text) foundation module.

This module provides foundation-level functionality shared across all Text domains.

Exports:
- AI configuration (used by Content, Publishing, Story, etc.)
"""

from .ai_config import (
    AISettings,
    create_ai_config,
    check_ollama_available,
    DEFAULT_AI_MODEL,
    DEFAULT_AI_API_BASE,
    AI_TEMPERATURE_MIN,
    AI_TEMPERATURE_MAX,
)

__all__ = [
    "AISettings",
    "create_ai_config",
    "check_ollama_available",
    "DEFAULT_AI_MODEL",
    "DEFAULT_AI_API_BASE",
    "AI_TEMPERATURE_MIN",
    "AI_TEMPERATURE_MAX",
]
