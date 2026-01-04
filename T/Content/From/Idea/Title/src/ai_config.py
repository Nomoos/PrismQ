"""Title-specific AI configuration wrapper.

This module provides AI configuration for the Title workflow.
It imports from T/src level (foundation) because AI is shared across Text domains.

Module Hierarchy:
- src/: Cross-cutting (database, config)
- T/: Text foundation (AI for all Text domains) ← AI CONFIG IS HERE
- T/Content/: Content processing (uses T foundation AI)
- T/Content/From/Idea/Title/: Title-specific logic

This module is just a wrapper for backward compatibility.
For new code, import directly from T.src.ai_config.
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add T/src to path
SCRIPT_DIR = Path(__file__).parent
T_SRC = SCRIPT_DIR.parent.parent.parent.parent.parent / "src"  # T/src
if str(T_SRC) not in sys.path:
    sys.path.insert(0, str(T_SRC))

try:
    # Import from T foundation level (correct hierarchy)
    # Use importlib to avoid circular import with ai_config module name
    import importlib.util
    spec = importlib.util.spec_from_file_location("t_ai_config", T_SRC / "ai_config.py")
    t_ai_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t_ai_config)
    
    # Extract needed items
    DEFAULT_AI_MODEL = t_ai_config.DEFAULT_AI_MODEL
    DEFAULT_AI_API_BASE = t_ai_config.DEFAULT_AI_API_BASE
    AI_TEMPERATURE_MIN = t_ai_config.AI_TEMPERATURE_MIN
    AI_TEMPERATURE_MAX = t_ai_config.AI_TEMPERATURE_MAX
    AISettings = t_ai_config.AISettings
    create_ai_config = t_ai_config.create_ai_config
    check_ollama_available = t_ai_config.check_ollama_available
    
    # Backward compatibility wrapper functions
    def get_local_ai_model() -> str:
        """Get the local AI model name.
        
        DEPRECATED: Import from T.src.ai_config instead.
        """
        return DEFAULT_AI_MODEL
    
    def get_local_ai_api_base() -> str:
        """Get the local AI API base URL.
        
        DEPRECATED: Import from T.src.ai_config instead.
        """
        return DEFAULT_AI_API_BASE
    
    def get_local_ai_temperature() -> float:
        """Get a random AI temperature.
        
        DEPRECATED: Import from T.src.ai_config instead.
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
        
        DEPRECATED: Use create_ai_config() from T.src.ai_config instead.
        
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
