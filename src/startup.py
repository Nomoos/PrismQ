"""General startup utilities for PrismQ scripts.

This module provides reusable configuration and dependency injection patterns
for database connection and Ollama local AI that can be used across all scripts.

Design Principles:
- No work at import time (lazy loading)
- Pure functions and classes (no side effects)
- Explicit dependency injection
- Clear composition root pattern
- Deterministic and testable

Usage:
    from src.startup import StartupConfig, create_startup_config
    
    # In your main() or composition root:
    config = create_startup_config()
    
    db_path = config.get_database_path()
    ai_settings = config.get_ai_settings()
    
    if config.check_ollama_available():
        print("Ollama is ready!")
"""

import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Constants - Define at module level, no side effects
# =============================================================================

DEFAULT_AI_MODEL = "qwen3:32b"
DEFAULT_AI_API_BASE = "http://localhost:11434"
AI_TEMPERATURE_MIN = 0.6
AI_TEMPERATURE_MAX = 0.8
DEFAULT_AI_TIMEOUT = 5


# =============================================================================
# AI Settings - Plain data class (no side effects)
# =============================================================================

@dataclass
class AISettings:
    """AI configuration settings - plain data, no behavior."""
    
    model: str = DEFAULT_AI_MODEL
    api_base: str = DEFAULT_AI_API_BASE
    temperature: float = 0.7  # Will be randomized when requested
    timeout: int = 120
    
    def get_random_temperature(self) -> float:
        """Get a random temperature within defined limits.
        
        Returns a random value between 0.6 and 0.8 for creative variety
        while maintaining coherent output.
        
        Returns:
            Random float between 0.6 and 0.8
        """
        return random.uniform(AI_TEMPERATURE_MIN, AI_TEMPERATURE_MAX)


# =============================================================================
# Startup Configuration - Composition root helper
# =============================================================================

@dataclass
class StartupConfig:
    """Startup configuration container - inject dependencies explicitly.
    
    This class provides a composition root pattern for PrismQ scripts.
    All dependencies are injected via constructor, no global state.
    
    Example:
        # In your main() function:
        config = StartupConfig(
            database_path="/path/to/db.s3db",
            ai_settings=AISettings()
        )
        
        # Or use factory:
        config = create_startup_config()
    """
    
    database_path: str
    ai_settings: AISettings = field(default_factory=AISettings)
    _ollama_available: Optional[bool] = field(default=None, init=False, repr=False)
    
    def get_database_path(self) -> str:
        """Get the database path.
        
        Returns:
            Absolute path to the database file
        """
        return self.database_path
    
    def get_ai_settings(self) -> AISettings:
        """Get AI settings object.
        
        Returns:
            AISettings instance
        """
        return self.ai_settings
    
    def get_ai_config(self) -> Tuple[str, float, str]:
        """Get complete AI configuration tuple.
        
        Returns:
            Tuple of (model_name, temperature, api_base_url)
        """
        return (
            self.ai_settings.model,
            self.ai_settings.get_random_temperature(),
            self.ai_settings.api_base
        )
    
    def check_ollama_available(self, force_recheck: bool = False) -> bool:
        """Check if Ollama is running (lazy, cached).
        
        This method does network I/O - call explicitly from composition root,
        not at import time.
        
        Args:
            force_recheck: If True, bypass cache and check again
        
        Returns:
            True if Ollama is available, False otherwise
        """
        if self._ollama_available is not None and not force_recheck:
            return self._ollama_available
        
        # Lazy import - only load when actually checking
        try:
            import requests
        except ImportError:
            logger.warning("requests module not available, cannot check Ollama")
            self._ollama_available = False
            return False
        
        try:
            response = requests.get(
                f"{self.ai_settings.api_base}/api/tags",
                timeout=DEFAULT_AI_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.warning(f"Ollama API returned status {response.status_code}")
                self._ollama_available = False
                return False
            
            # Check if model is available
            models_data = response.json()
            available_models = [m.get("name", "") for m in models_data.get("models", [])]
            
            if self.ai_settings.model not in available_models:
                logger.warning(
                    f"Model '{self.ai_settings.model}' not found. "
                    f"Available: {available_models}"
                )
                self._ollama_available = False
                return False
            
            self._ollama_available = True
            return True
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to connect to Ollama: {e}")
            self._ollama_available = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking Ollama: {e}")
            self._ollama_available = False
            return False


# =============================================================================
# Factory Functions - Create configured instances
# =============================================================================

def create_startup_config(
    database_path: Optional[str] = None,
    ai_model: Optional[str] = None,
    ai_api_base: Optional[str] = None,
    interactive: bool = False
) -> StartupConfig:
    """Factory function to create StartupConfig with defaults.
    
    This is the recommended composition root entry point.
    Call this from your main() function, not at module import time.
    
    Args:
        database_path: Override database path (default: from Config)
        ai_model: Override AI model (default: qwen3:32b)
        ai_api_base: Override API base (default: localhost:11434)
        interactive: Whether Config should prompt for missing values
    
    Returns:
        Configured StartupConfig instance
    
    Example:
        def main():
            # Create config at startup
            config = create_startup_config()
            
            # Use it
            db_path = config.get_database_path()
            if config.check_ollama_available():
                process_with_ai(config)
    """
    # Lazy import Config - only when factory is called
    from .config import Config
    
    # Determine database path
    if database_path is None:
        # Create Config instance to get database path
        cfg = Config(interactive=interactive)
        database_path = cfg.database_path
    
    # Create AI settings
    ai_settings = AISettings(
        model=ai_model or DEFAULT_AI_MODEL,
        api_base=ai_api_base or DEFAULT_AI_API_BASE
    )
    
    # Return configured instance
    return StartupConfig(
        database_path=database_path,
        ai_settings=ai_settings
    )


# =============================================================================
# Backward Compatibility Functions (deprecated, use StartupConfig instead)
# =============================================================================

def get_database_path(config: Optional['Config'] = None) -> str:
    """Get the database path for PrismQ.
    
    DEPRECATED: Use create_startup_config().get_database_path() instead.
    
    This function is provided for backward compatibility but violates
    best practices by potentially doing work at import time.
    
    Args:
        config: Optional Config instance
    
    Returns:
        Absolute path to the database file
    """
    if config is None:
        from .config import Config
        config = Config(interactive=False)
    
    return config.database_path


def get_local_ai_model() -> str:
    """Get the local AI model name.
    
    DEPRECATED: Use create_startup_config().get_ai_settings().model instead.
    
    Returns:
        Model name string (e.g., "qwen3:32b")
    """
    return DEFAULT_AI_MODEL


def get_local_ai_temperature() -> float:
    """Get a random temperature value for AI generation.
    
    DEPRECATED: Use create_startup_config().get_ai_settings().get_random_temperature() instead.
    
    Returns:
        Random float between 0.6 and 0.8
    """
    return random.uniform(AI_TEMPERATURE_MIN, AI_TEMPERATURE_MAX)


def get_local_ai_api_base() -> str:
    """Get the Ollama API base URL.
    
    DEPRECATED: Use create_startup_config().get_ai_settings().api_base instead.
    
    Returns:
        API base URL string
    """
    return DEFAULT_AI_API_BASE


def get_local_ai_config() -> Tuple[str, float, str]:
    """Get complete local AI configuration as a tuple.
    
    DEPRECATED: Use create_startup_config().get_ai_config() instead.
    
    Returns:
        Tuple of (model_name, temperature, api_base_url)
    """
    return (
        DEFAULT_AI_MODEL,
        get_local_ai_temperature(),
        DEFAULT_AI_API_BASE
    )


def check_ollama_available(
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 5
) -> bool:
    """Check if Ollama is running.
    
    DEPRECATED: Use create_startup_config().check_ollama_available() instead.
    
    This function does network I/O and should not be called at import time.
    
    Args:
        api_base: Ollama API base URL
        model: Model name to check
        timeout: Request timeout in seconds
    
    Returns:
        True if Ollama is available, False otherwise
    """
    # Create temporary config for checking
    config = StartupConfig(
        database_path="",  # Not needed for this check
        ai_settings=AISettings(
            model=model or DEFAULT_AI_MODEL,
            api_base=api_base or DEFAULT_AI_API_BASE
        )
    )
    return config.check_ollama_available()


def initialize_environment(
    check_ai: bool = True,
    interactive: bool = False
) -> Tuple['Config', bool]:
    """Initialize the PrismQ environment.
    
    DEPRECATED: Use create_startup_config() in your main() function instead.
    
    This function violates best practices by doing work that should be
    in a composition root.
    
    Args:
        check_ai: Whether to check Ollama availability
        interactive: Whether to run Config in interactive mode
    
    Returns:
        Tuple of (Config instance, AI available boolean)
    """
    from .config import Config
    
    # Load configuration
    config = Config(interactive=interactive)
    
    # Check AI availability if requested
    ai_available = False
    if check_ai:
        startup_config = StartupConfig(
            database_path=config.database_path,
            ai_settings=AISettings()
        )
        ai_available = startup_config.check_ollama_available()
    
    return config, ai_available
