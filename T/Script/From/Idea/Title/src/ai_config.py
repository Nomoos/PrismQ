"""AI Configuration for Content Generation (Step 04).

This module provides AI configuration functions for the PrismQ.T.Content.From.Idea.Title
workflow. It uses the global AI configuration functions from src.startup to maintain
consistency across the entire PrismQ system.

All AI configuration is centralized through global functions, similar to how database
paths are handled. This ensures that all scripts use the same AI model and configuration.

Usage:
    from ai_config import (
        get_local_ai_model,
        get_local_ai_temperature,
        get_local_ai_api_base,
        get_local_ai_config
    )
    
    # Get individual config values
    model = get_local_ai_model()  # Returns: "qwen3:32b"
    temperature = get_local_ai_temperature()  # Returns: random 0.6-0.8
    api_base = get_local_ai_api_base()  # Returns: "http://localhost:11434"
    
    # Or get complete config
    model, temp, api_base = get_local_ai_config()
"""

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add repo root to path for imports
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent  # Up to repo root
sys.path.insert(0, str(REPO_ROOT))

try:
    from src.startup import (
        check_ollama_available,
        get_local_ai_api_base,
        get_local_ai_config,
        get_local_ai_model,
        get_local_ai_temperature,
    )
except ImportError as e:
    logger.error(f"Failed to import AI config functions from src.startup: {e}")
    raise

# Re-export functions for convenience
__all__ = [
    "get_local_ai_model",
    "get_local_ai_temperature",
    "get_local_ai_api_base",
    "get_local_ai_config",
    "check_ollama_available",
]
