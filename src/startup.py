"""General startup utilities for PrismQ scripts.

This module provides reusable functions for database connection and Ollama local AI
configuration that can be used across all scripts in the PrismQ system.

Key Features:
- Database path configuration (reusable across all scripts)
- Local AI model configuration (Ollama integration)
- AI availability checking
- Random temperature generation for creative variety

Usage:
    from src.startup import (
        get_database_path,
        get_local_ai_model,
        get_local_ai_temperature,
        get_local_ai_api_base,
        get_local_ai_config,
        check_ollama_available
    )
    
    # Get database path
    db_path = get_database_path()
    
    # Get AI configuration
    model = get_local_ai_model()
    temperature = get_local_ai_temperature()
    api_base = get_local_ai_api_base()
    
    # Or get complete config
    model, temperature, api_base = get_local_ai_config()
    
    # Check if Ollama is available
    if check_ollama_available():
        print("Ollama is ready!")
"""

import logging
import random
from pathlib import Path
from typing import Optional, Tuple

import requests

from .config import Config

logger = logging.getLogger(__name__)


# =============================================================================
# Database Configuration
# =============================================================================


def get_database_path(config: Optional[Config] = None) -> str:
    """Get the database path for PrismQ.
    
    This function provides a centralized way to get the database path that can
    be reused across all scripts in the PrismQ system.
    
    Args:
        config: Optional Config instance. If not provided, a new one will be created.
    
    Returns:
        Absolute path to the database file (db.s3db)
    
    Example:
        >>> db_path = get_database_path()
        >>> print(db_path)
        C:/PrismQ/db.s3db
    """
    if config is None:
        config = Config(interactive=False)
    
    return config.database_path


# =============================================================================
# Local AI Configuration (Ollama)
# =============================================================================


def get_local_ai_model() -> str:
    """Get the local AI model name for content generation.
    
    Returns the fixed model name used for local AI operations via Ollama.
    Currently configured to use Qwen3:32b model.
    
    Returns:
        Model name string (e.g., "qwen3:32b")
    
    Example:
        >>> model = get_local_ai_model()
        >>> print(model)
        qwen3:32b
    """
    return "qwen3:32b"


def get_local_ai_temperature() -> float:
    """Get a random temperature value for AI generation.
    
    Returns a random temperature between 0.6 and 0.8 for creative variety
    while maintaining coherent output. Each call returns a different random
    value within this range.
    
    Returns:
        Random float between 0.6 and 0.8
    
    Example:
        >>> temp1 = get_local_ai_temperature()
        >>> temp2 = get_local_ai_temperature()
        >>> print(f"{temp1:.2f}, {temp2:.2f}")
        0.67, 0.74
    """
    return random.uniform(0.6, 0.8)


def get_local_ai_api_base() -> str:
    """Get the Ollama API base URL.
    
    Returns the base URL for Ollama API calls. Default is localhost:11434.
    
    Returns:
        API base URL string
    
    Example:
        >>> api_base = get_local_ai_api_base()
        >>> print(api_base)
        http://localhost:11434
    """
    return "http://localhost:11434"


def get_local_ai_config() -> Tuple[str, float, str]:
    """Get complete local AI configuration as a tuple.
    
    Convenience function that returns all AI configuration parameters in one call.
    
    Returns:
        Tuple of (model_name, temperature, api_base_url)
    
    Example:
        >>> model, temp, api_base = get_local_ai_config()
        >>> print(f"Model: {model}, Temp: {temp:.2f}, API: {api_base}")
        Model: qwen3:32b, Temp: 0.72, API: http://localhost:11434
    """
    return (
        get_local_ai_model(),
        get_local_ai_temperature(),
        get_local_ai_api_base()
    )


# =============================================================================
# Ollama Availability Check
# =============================================================================


def check_ollama_available(
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 5
) -> bool:
    """Check if Ollama is running and the specified model is available.
    
    Sends a GET request to Ollama's /api/tags endpoint to verify that:
    1. Ollama server is running
    2. The specified model is available (if model is provided)
    
    Args:
        api_base: Ollama API base URL. If None, uses get_local_ai_api_base()
        model: Model name to check. If None, uses get_local_ai_model()
        timeout: Request timeout in seconds (default: 5)
    
    Returns:
        True if Ollama is available (and model exists if specified), False otherwise
    
    Example:
        >>> if check_ollama_available():
        ...     print("Ollama is ready!")
        ... else:
        ...     print("Ollama is not available")
        Ollama is ready!
    """
    if api_base is None:
        api_base = get_local_ai_api_base()
    
    if model is None:
        model = get_local_ai_model()
    
    try:
        # Check if Ollama is running
        response = requests.get(
            f"{api_base}/api/tags",
            timeout=timeout
        )
        
        if response.status_code != 200:
            logger.warning(f"Ollama API returned status {response.status_code}")
            return False
        
        # Check if model is available (if specified)
        if model:
            models_data = response.json()
            available_models = [m.get("name", "") for m in models_data.get("models", [])]
            
            if model not in available_models:
                logger.warning(f"Model '{model}' not found in Ollama. Available: {available_models}")
                return False
        
        return True
    
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to connect to Ollama: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking Ollama: {e}")
        return False


# =============================================================================
# Startup Initialization
# =============================================================================


def initialize_environment(
    check_ai: bool = True,
    interactive: bool = False
) -> Tuple[Config, bool]:
    """Initialize the PrismQ environment with database and AI checks.
    
    This is a convenience function that:
    1. Loads configuration
    2. Checks Ollama availability (if requested)
    3. Returns ready-to-use config and AI status
    
    Args:
        check_ai: Whether to check Ollama availability (default: True)
        interactive: Whether to run Config in interactive mode (default: False)
    
    Returns:
        Tuple of (Config instance, AI available boolean)
    
    Example:
        >>> config, ai_available = initialize_environment()
        >>> if not ai_available:
        ...     print("Warning: Ollama not available!")
        >>> db_path = config.database_path
    """
    # Load configuration
    config = Config(interactive=interactive)
    
    # Check AI availability if requested
    ai_available = check_ollama_available() if check_ai else False
    
    return config, ai_available
