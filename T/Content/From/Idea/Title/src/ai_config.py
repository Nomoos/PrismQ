"""Global AI configuration for content generation.

This module provides global AI configuration functions used across all content generation modules.
Similar to how database path is obtained globally, AI model and temperature are configured here.
"""

import random
from typing import Tuple


def get_local_ai_model() -> str:
    """Get the local AI model name for content generation.
    
    Returns fixed model name for local AI inference via Ollama.
    
    Returns:
        Model name string (e.g., "qwen3:32b")
    """
    return "qwen3:32b"


def get_local_ai_api_base() -> str:
    """Get the local AI API base URL.
    
    Returns:
        API base URL for Ollama (default: http://localhost:11434)
    """
    return "http://localhost:11434"


def get_local_ai_temperature() -> float:
    """Get a random AI temperature within defined limits.
    
    Temperature controls creativity/randomness of AI generation.
    Returns a random value between configured min and max limits.
    
    Returns:
        Random temperature value between 0.6 and 0.8
    """
    # Temperature limits for content generation
    MIN_TEMPERATURE = 0.6
    MAX_TEMPERATURE = 0.8
    
    # Return random temperature within limits
    return random.uniform(MIN_TEMPERATURE, MAX_TEMPERATURE)


def get_local_ai_timeout() -> int:
    """Get the AI request timeout in seconds.
    
    Returns:
        Timeout in seconds (default: 120)
    """
    return 120


def get_local_ai_config() -> Tuple[str, str, float, int]:
    """Get complete local AI configuration.
    
    Returns:
        Tuple of (model, api_base, temperature, timeout)
    """
    return (
        get_local_ai_model(),
        get_local_ai_api_base(),
        get_local_ai_temperature(),
        get_local_ai_timeout(),
    )
