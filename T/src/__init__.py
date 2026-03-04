"""PrismQ.T (Text) foundation module.

This module provides foundation-level functionality shared across all Text domains.

Exports:
- AI configuration (used by Content, Publishing, Story, etc.)
- Prompt utilities (template variable substitution for all AI modules)
"""

from .ai_config import (
    AISettings,
    create_ai_config,
    create_early_stage_ai_config,
    create_qwen3_14b_ai_config,
    create_qwen3_8b_ai_config,
    create_stage_01_ai_config,
    create_stage_03_04_ai_config,
    create_stage_05_06_ai_config,
    check_ollama_available,
    DEFAULT_AI_MODEL,
    DEFAULT_AI_MODEL_EARLY_STAGE,
    DEFAULT_AI_MODEL_STAGE_01,
    DEFAULT_AI_MODEL_STAGE_03_04,
    DEFAULT_AI_MODEL_STAGE_05_06,
    EARLY_STAGE_AI_MODELS,
    DEFAULT_AI_API_BASE,
    AI_TEMPERATURE_MIN,
    AI_TEMPERATURE_MAX,
)
from .prompt_utils import apply_template

__all__ = [
    "AISettings",
    "create_ai_config",
    "create_early_stage_ai_config",
    "create_qwen3_14b_ai_config",
    "create_qwen3_8b_ai_config",
    "create_stage_01_ai_config",
    "create_stage_03_04_ai_config",
    "create_stage_05_06_ai_config",
    "check_ollama_available",
    "DEFAULT_AI_MODEL",
    "DEFAULT_AI_MODEL_EARLY_STAGE",
    "DEFAULT_AI_MODEL_STAGE_01",
    "DEFAULT_AI_MODEL_STAGE_03_04",
    "DEFAULT_AI_MODEL_STAGE_05_06",
    "EARLY_STAGE_AI_MODELS",
    "DEFAULT_AI_API_BASE",
    "AI_TEMPERATURE_MIN",
    "AI_TEMPERATURE_MAX",
    "apply_template",
]
