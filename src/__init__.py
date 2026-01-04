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
- Table managers for Idea and Story tables in the shared database

IMPORTANT: PrismQ uses ONE shared database (db.s3db) for ALL modules.
IdeaTable and StoryTable manage their respective tables in this shared database,
not separate databases.

Usage:
    from src.config import Config

    config = Config()
    print(config.working_directory)
    print(config.database_url)

    # Use shared database table managers (default: db.s3db in working directory)
    from src.idea import IdeaTable, setup_idea_table

    db = setup_idea_table()  # Uses db.s3db by default
    idea_id = db.insert_idea("Write a horror story...")
    db.close()

    # Use shared Story table manager
    from src.story import StoryTable, setup_story_table

    db = setup_story_table()  # Uses db.s3db by default
    story_id = db.insert_story(idea_id=idea_id)
    db.close()
"""

from .config import Config
from .idea import IdeaTable, setup_idea_table
from .startup import (
    DatabaseConfig,
    create_database_config,
    get_database_path,  # Backward compatibility (deprecated)
)
from .story import StoryTable, setup_story_table

__all__ = [
    "Config",
    "IdeaTable",
    "setup_idea_table",
    "StoryTable",
    "setup_story_table",
    # Database configuration
    "DatabaseConfig",
    "create_database_config",
    "get_database_path",  # Backward compatibility (deprecated)
]
__version__ = "1.0.0"
