"""src - Centralized environment and configuration management for PrismQ.

This module provides a standardized way to load and manage environment variables
and configuration across all PrismQ modules (T, A, V, P, M, Client).

Key Features:
- Centralized .env file management
- Standardized working directory at C:/PrismQ (fallback for all platforms)
- Cross-platform path handling
- Interactive and non-interactive configuration modes
- Automatic .env file creation and management
- Shared database (db.s3db) for all content storage
- Shared Story database for tracking story progress through the workflow pipeline

Usage:
    from src import Config

    config = Config()
    print(config.working_directory)
    print(config.database_url)

    # Use shared database (default: db.s3db in working directory)
    from src import IdeaDatabase, setup_idea_database

    db = setup_idea_database()  # Uses db.s3db by default
    idea_id = db.insert_idea("Write a horror story...")
    db.close()

    # Use shared Story database
    from src import StoryDatabase, setup_story_database

    db = setup_story_database()  # Uses db.s3db by default
    story_id = db.insert_story(idea_id=idea_id)
    db.close()
"""

from .config import Config
from .idea import IdeaDatabase, setup_idea_database
from .startup import (
    DatabaseConfig,
    create_database_config,
    get_database_path,  # Backward compatibility (deprecated)
)
from .story import StoryDatabase, setup_story_database

__all__ = [
    "Config",
    "IdeaDatabase",
    "setup_idea_database",
    "StoryDatabase",
    "setup_story_database",
    # Database configuration
    "DatabaseConfig",
    "create_database_config",
    "get_database_path",  # Backward compatibility (deprecated)
]
__version__ = "1.0.0"
