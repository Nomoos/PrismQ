"""Title-specific AI configuration wrapper.

This module provides AI configuration for the Title workflow.
It imports from T.Content level (not src level) because AI is content-specific.

Module Hierarchy:
- src/: Cross-cutting (database, config)
- T/Content/: Content processing (AI for content)
- T/Content/From/Idea/Title/: Title-specific logic

This module is just a wrapper for backward compatibility.
For new code, import directly from T.Content.src.ai_config.
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add T/Content/src to path
SCRIPT_DIR = Path(__file__).parent
T_CONTENT_SRC = SCRIPT_DIR.parent.parent.parent.parent / "src"  # T/Content/src
sys.path.insert(0, str(T_CONTENT_SRC))

try:
    # Import from T/Content level (correct hierarchy)
    from ai_config import (
        DEFAULT_AI_MODEL,
        DEFAULT_AI_API_BASE,
        AI_TEMPERATURE_MIN,
        AI_TEMPERATURE_MAX,
        AISettings,
        create_ai_config,
        check_ollama_available,
    )
    
    # Backward compatibility wrapper functions
    def get_local_ai_model() -> str:
        """Get the local AI model name.
        
        DEPRECATED: Import from T.Content.src.ai_config instead.
        """
        return DEFAULT_AI_MODEL
    
    def get_local_ai_api_base() -> str:
        """Get the local AI API base URL.
        
        DEPRECATED: Import from T.Content.src.ai_config instead.
        """
        return DEFAULT_AI_API_BASE
    
    def get_local_ai_temperature() -> float:
        """Get a random AI temperature.
        
        DEPRECATED: Import from T.Content.src.ai_config instead.
        """
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
        
        DEPRECATED: Use create_ai_config() from T.Content.src.ai_config instead.
        
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
    logger.error(f"Failed to import from T.Content.src.ai_config: {e}")
    logger.warning("Falling back to local implementation")
    
    # Fallback implementation
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
