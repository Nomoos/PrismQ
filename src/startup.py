"""General startup utilities for PrismQ (cross-cutting concerns).

This module provides configuration for cross-cutting functionality used across
the entire PrismQ project, regardless of content type or source.

According to module hierarchy:
- src/PrismQ: Cross-cutting functionality (database, environment, config)
- NOT for content-specific concerns (AI generation is at T/Content level)

Design Principles:
- No work at import time (lazy loading)
- Pure functions and classes (no side effects)
- Explicit dependency injection
- Clear composition root pattern
- Deterministic and testable

Usage:
    from src.startup import DatabaseConfig, create_database_config
    
    # In your main() or composition root:
    db_config = create_database_config()
    db_path = db_config.get_database_path()
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Database Configuration - Cross-cutting concern
# =============================================================================

@dataclass
class DatabaseConfig:
    """Database configuration for PrismQ.
    
    This is at the src/ level because database is a cross-cutting concern
    used by all modules (content, idea, story, etc.).
    """
    
    database_path: str
    
    def get_database_path(self) -> str:
        """Get the database path.
        
        Returns:
            Absolute path to the database file
        """
        return self.database_path


# =============================================================================
# Factory Function - Create database configuration
# =============================================================================

def create_database_config(
    database_path: Optional[str] = None,
    interactive: bool = False
) -> DatabaseConfig:
    """Factory function to create database configuration.
    
    This is the composition root entry point for database configuration.
    Call this from your main() function, not at module import time.
    
    Args:
        database_path: Override database path (default: from Config)
        interactive: Whether Config should prompt for missing values
    
    Returns:
        Configured DatabaseConfig instance
    
    Example:
        def main():
            # Create config at startup
            db_config = create_database_config()
            db_path = db_config.get_database_path()
    """
    # Lazy import Config - only when factory is called
    from .config import Config
    
    # Determine database path
    if database_path is None:
        cfg = Config(interactive=interactive)
        database_path = cfg.database_path
    
    return DatabaseConfig(database_path=database_path)


# =============================================================================
# Backward Compatibility - Deprecated functions
# =============================================================================

def get_database_path(config: Optional['Config'] = None) -> str:
    """Get the database path for PrismQ.
    
    DEPRECATED: Use create_database_config().get_database_path() instead.
    
    Args:
        config: Optional Config instance
    
    Returns:
        Absolute path to the database file
    """
    if config is None:
        from .config import Config
        config = Config(interactive=False)
    
    return config.database_path
