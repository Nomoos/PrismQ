"""AI configuration for Text domain (PrismQ.T foundation level).

This module provides AI configuration for all Text-related AI operations using Ollama.
It belongs at the T/ level (PrismQ.T foundation) because:
- AI is used across multiple T domains (Content, Publishing, Story, etc.)
- Multiple domains need consistent AI configuration
- Shared foundation for all Text AI operations

According to module hierarchy:
- src/PrismQ: Cross-cutting functionality (database, environment)
- T/PrismQ.T: Text foundation (AI for Text domain - THIS MODULE)
- T/Content/PrismQ.T.Content: Content processing (uses T foundation AI)
- T/Publishing/: Publishing operations (uses T foundation AI)
- T/Story/: Story operations (uses T foundation AI)

Usage:
    from T.src.ai_config import AISettings, create_ai_config
    
    # In your main():
    ai_settings = create_ai_config()
    model = ai_settings.get_model()
    temp = ai_settings.get_random_temperature()
"""

import logging
import os
import random
from dataclasses import dataclass
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Constants - Text foundation level AI configuration
# =============================================================================

DEFAULT_AI_MODEL = "qwen3:32b"
DEFAULT_AI_API_BASE = "http://localhost:11434"
AI_TEMPERATURE_MIN = 0.6
AI_TEMPERATURE_MAX = 0.8
DEFAULT_AI_TIMEOUT = 120

# =============================================================================
# Early-Stage AI Model Configuration (Scripts 01-06)
# =============================================================================

# Choice list of Qwen3 models available for early-stage processing (Scripts 01-06).
# Set the matching PRISMQ_AI_MODEL_STAGE_* env var in your .env to override a stage's model.
EARLY_STAGE_AI_MODELS: Dict[str, str] = {
    "qwen3:8b":  "Fast     – Qwen3 8B  (scripts 03-04)",
    "qwen3:14b": "Balanced – Qwen3 14B (scripts 01, 05-06)",
    "qwen3:32b": "Quality  – Qwen3 32B (scripts 07+ and default main model)",
}

# Per-stage-group model defaults (each overridable via environment variable).
# Script 01  – Idea generation
DEFAULT_AI_MODEL_STAGE_01: str = os.getenv("PRISMQ_AI_MODEL_STAGE_01", "qwen3:14b")
# Scripts 03-04 – Title and Content generation
DEFAULT_AI_MODEL_STAGE_03_04: str = os.getenv("PRISMQ_AI_MODEL_STAGE_03_04", "qwen3:8b")
# Scripts 05-06 – Early reviews (title & content)
DEFAULT_AI_MODEL_STAGE_05_06: str = os.getenv("PRISMQ_AI_MODEL_STAGE_05_06", "qwen3:14b")

# Keep legacy single-variable for backward compatibility (falls back to stage 05-06 default)
DEFAULT_AI_MODEL_EARLY_STAGE: str = os.getenv(
    "PRISMQ_AI_MODEL_EARLY_STAGE",
    DEFAULT_AI_MODEL_STAGE_05_06,
)


# =============================================================================
# AI Settings - Plain data class for content generation
# =============================================================================

@dataclass
class AISettings:
    """AI configuration settings for Text domain operations.
    
    This is at the T/ (PrismQ.T) foundation level because AI is used across
    multiple Text domains (Content, Publishing, Story), not just content processing.
    """
    
    model: str = DEFAULT_AI_MODEL
    api_base: str = DEFAULT_AI_API_BASE
    timeout: int = DEFAULT_AI_TIMEOUT
    
    def get_model(self) -> str:
        """Get the AI model name."""
        return self.model
    
    def get_api_base(self) -> str:
        """Get the API base URL."""
        return self.api_base
    
    def get_random_temperature(self) -> float:
        """Get a random temperature for creative variety.
        
        Returns a random value between 0.6 and 0.8.
        """
        return random.uniform(AI_TEMPERATURE_MIN, AI_TEMPERATURE_MAX)
    
    def get_config_tuple(self) -> Tuple[str, float, str]:
        """Get complete AI configuration as tuple.
        
        Returns:
            Tuple of (model, temperature, api_base)
        """
        return (
            self.model,
            self.get_random_temperature(),
            self.api_base
        )


# =============================================================================
# Factory Function - Create AI configuration
# =============================================================================

def create_ai_config(
    model: str = None,
    api_base: str = None,
    timeout: int = None
) -> AISettings:
    """Factory function to create AI configuration for Text domain operations.
    
    This is at the T foundation level for use across all Text domains.
    
    Args:
        model: Override AI model (default: qwen3:32b)
        api_base: Override API base (default: localhost:11434)
        timeout: Override timeout (default: 120s)
    
    Returns:
        Configured AISettings instance for Text domain
    
    Example:
        # In your main()
        ai_settings = create_ai_config()
        model = ai_settings.get_model()
    """
    return AISettings(
        model=model or DEFAULT_AI_MODEL,
        api_base=api_base or DEFAULT_AI_API_BASE,
        timeout=timeout or DEFAULT_AI_TIMEOUT
    )


def create_early_stage_ai_config(
    model: str = None,
    api_base: str = None,
    timeout: int = None
) -> AISettings:
    """Factory function to create AI configuration for early-stage scripts (01-06).

    Uses the legacy ``PRISMQ_AI_MODEL_EARLY_STAGE`` env var for backward
    compatibility.  Prefer the stage-specific factories below for new code.

    Args:
        model: Override AI model (default: value of PRISMQ_AI_MODEL_EARLY_STAGE)
        api_base: Override API base (default: localhost:11434)
        timeout: Override timeout (default: 120s)

    Returns:
        Configured AISettings instance for early-stage operations
    """
    return AISettings(
        model=model or DEFAULT_AI_MODEL_EARLY_STAGE,
        api_base=api_base or DEFAULT_AI_API_BASE,
        timeout=timeout or DEFAULT_AI_TIMEOUT
    )


def create_stage_01_ai_config(
    model: str = None,
    api_base: str = None,
    timeout: int = None
) -> AISettings:
    """AI config for Script 01 (Idea generation) – default: qwen3:14b.

    Override via ``PRISMQ_AI_MODEL_STAGE_01`` environment variable.
    """
    return AISettings(
        model=model or DEFAULT_AI_MODEL_STAGE_01,
        api_base=api_base or DEFAULT_AI_API_BASE,
        timeout=timeout or DEFAULT_AI_TIMEOUT
    )


def create_stage_03_04_ai_config(
    model: str = None,
    api_base: str = None,
    timeout: int = None
) -> AISettings:
    """AI config for Scripts 03-04 (Title & Content generation) – default: qwen3:8b.

    Override via ``PRISMQ_AI_MODEL_STAGE_03_04`` environment variable.
    """
    return AISettings(
        model=model or DEFAULT_AI_MODEL_STAGE_03_04,
        api_base=api_base or DEFAULT_AI_API_BASE,
        timeout=timeout or DEFAULT_AI_TIMEOUT
    )


def create_stage_05_06_ai_config(
    model: str = None,
    api_base: str = None,
    timeout: int = None
) -> AISettings:
    """AI config for Scripts 05-06 (Early reviews) – default: qwen3:14b.

    Override via ``PRISMQ_AI_MODEL_STAGE_05_06`` environment variable.
    """
    return AISettings(
        model=model or DEFAULT_AI_MODEL_STAGE_05_06,
        api_base=api_base or DEFAULT_AI_API_BASE,
        timeout=timeout or DEFAULT_AI_TIMEOUT
    )


# =============================================================================
# Availability Check
# =============================================================================

def check_ollama_available(
    api_base: str = None,
    model: str = None,
    timeout: int = 5
) -> bool:
    """Check if Ollama is running and model is available.
    
    This does network I/O - call explicitly from composition root.
    
    Args:
        api_base: API base URL
        model: Model name to check
        timeout: Request timeout
    
    Returns:
        True if Ollama is available
    """
    # Lazy import
    try:
        import requests
    except ImportError:
        logger.warning("requests module not available")
        return False
    
    api_base = api_base or DEFAULT_AI_API_BASE
    model = model or DEFAULT_AI_MODEL
    
    try:
        response = requests.get(
            f"{api_base}/api/tags",
            timeout=timeout
        )
        
        if response.status_code != 200:
            logger.warning(f"Ollama API returned status {response.status_code}")
            return False
        
        # Check if model is available
        models_data = response.json()
        available_models = [m.get("name", "") for m in models_data.get("models", [])]
        
        if model not in available_models:
            logger.warning(f"Model '{model}' not found. Available: {available_models}")
            return False
        
        return True
    
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to connect to Ollama: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking Ollama: {e}")
        return False
