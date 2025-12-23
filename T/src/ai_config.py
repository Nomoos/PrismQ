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
import random
from dataclasses import dataclass
from typing import Tuple

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
