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

# Choice list of faster models suitable for early-stage processing (Scripts 01-06).
# These models trade some quality for speed compared to the default qwen3:32b.
# Set PRISMQ_AI_MODEL_EARLY_STAGE in your .env or environment to select one.
EARLY_STAGE_AI_MODELS: Dict[str, str] = {
    "qwen2.5:3b":           "Fastest  – very lightweight, minimal VRAM",
    "qwen2.5:7b":           "Very fast – good quality, low VRAM",
    "qwen2.5:14b":          "Fast     – better quality (recommended default)",
    "qwen2.5:14b-instruct": "Fast     – instruction-tuned 14 B variant",
    "qwen3:8b":             "Fast     – Qwen3 smaller variant",
    "llama3.2:3b":          "Fastest  – Meta Llama 3.2 3B",
    "llama3.1:8b":          "Fast     – Meta Llama 3.1 8B",
    "gemma2:9b":            "Fast     – Google Gemma 2 9B",
    "mistral:7b":           "Fast     – Mistral 7B v0.3",
}

# Active early-stage model (override via PRISMQ_AI_MODEL_EARLY_STAGE env var).
# Defaults to qwen2.5:14b – a good balance of speed and quality for early stages.
DEFAULT_AI_MODEL_EARLY_STAGE: str = os.getenv(
    "PRISMQ_AI_MODEL_EARLY_STAGE",
    "qwen2.5:14b",
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

    Uses a faster model suited for initial processing steps.  The active model
    is selected via the ``PRISMQ_AI_MODEL_EARLY_STAGE`` environment variable
    (default: ``qwen2.5:14b``).  See ``EARLY_STAGE_AI_MODELS`` for the full
    list of supported choices.

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
