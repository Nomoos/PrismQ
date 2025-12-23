"""Content-specific AI configuration - uses general startup module.

This module provides AI configuration for the Content.From.Idea.Title workflow.
It re-exports functions from src.startup for convenience and backward compatibility.

For new code, prefer importing directly from src.startup instead.
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add repo root to path for imports
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent  # Up to repo root
sys.path.insert(0, str(REPO_ROOT))

try:
    # Import from top-level general module (RECOMMENDED)
    from src.startup import (
        DEFAULT_AI_MODEL,
        DEFAULT_AI_API_BASE,
        AI_TEMPERATURE_MIN,
        AI_TEMPERATURE_MAX,
        AISettings,
        create_startup_config,
    )
    
    # For backward compatibility, provide wrapper functions
    def get_local_ai_model() -> str:
        """Get the local AI model name.
        
        DEPRECATED: Import from src.startup instead.
        This is a wrapper for backward compatibility.
        """
        return DEFAULT_AI_MODEL
    
    def get_local_ai_api_base() -> str:
        """Get the local AI API base URL.
        
        DEPRECATED: Import from src.startup instead.
        This is a wrapper for backward compatibility.
        """
        return DEFAULT_AI_API_BASE
    
    def get_local_ai_temperature() -> float:
        """Get a random AI temperature.
        
        DEPRECATED: Import from src.startup instead.
        This is a wrapper for backward compatibility.
        """
        # Use AISettings to get temperature
        import random
        return random.uniform(AI_TEMPERATURE_MIN, AI_TEMPERATURE_MAX)
    
    def get_local_ai_timeout() -> int:
        """Get the AI request timeout.
        
        Returns:
            Timeout in seconds (default: 120)
        """
        return 120
    
    def get_local_ai_config():
        """Get complete local AI configuration.
        
        DEPRECATED: Use create_startup_config() from src.startup instead.
        This is a wrapper for backward compatibility.
        
        Returns:
            Tuple of (model, api_base, temperature, timeout)
        """
        return (
            get_local_ai_model(),
            get_local_ai_api_base(),
            get_local_ai_temperature(),
            get_local_ai_timeout(),
        )

except ImportError as e:
    logger.error(f"Failed to import from src.startup: {e}")
    logger.warning("Falling back to local implementation (not recommended)")
    
    # Fallback implementation if src.startup is not available
    import random
    from typing import Tuple
    
    DEFAULT_AI_MODEL = "qwen3:32b"
    DEFAULT_AI_API_BASE = "http://localhost:11434"
    AI_TEMPERATURE_MIN = 0.6
    AI_TEMPERATURE_MAX = 0.8
    
    def get_local_ai_model() -> str:
        return DEFAULT_AI_MODEL
    
    def get_local_ai_api_base() -> str:
        return DEFAULT_AI_API_BASE
    
    def get_local_ai_temperature() -> float:
        return random.uniform(AI_TEMPERATURE_MIN, AI_TEMPERATURE_MAX)
    
    def get_local_ai_timeout() -> int:
        return 120
    
    def get_local_ai_config() -> Tuple[str, str, float, int]:
        return (
            get_local_ai_model(),
            get_local_ai_api_base(),
            get_local_ai_temperature(),
            get_local_ai_timeout(),
        )
