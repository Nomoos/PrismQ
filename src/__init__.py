"""src - Centralized environment and configuration management for PrismQ.

This module provides a standardized way to load and manage environment variables
and configuration across all PrismQ modules (T, A, V, P, M, Client).

Key Features:
- Centralized .env file management
- Standardized working directory at C:\\PrismQ (Windows) or ~/PrismQ (Unix-like)
- Cross-platform path handling
- Interactive and non-interactive configuration modes
- Automatic .env file creation and management
- Shared Idea database for prompt-based idea storage
- Shared Story database for tracking story progress through the workflow pipeline

Usage:
    from src import Config
    
    config = Config()
    print(config.working_directory)
    print(config.database_url)
    
    # Use shared Idea database
    from src import IdeaDatabase, setup_idea_database
    
    db = setup_idea_database("ideas.db")
    idea_id = db.insert_idea("Write a horror story...")
    db.close()
    
    # Use shared Story database
    from src import StoryDatabase, setup_story_database
    
    db = setup_story_database("stories.db")
    story_id = db.insert_story(idea_id=idea_id)
    db.close()
"""

from .config import Config
from .idea import IdeaDatabase, setup_idea_database
from .story import StoryDatabase, setup_story_database

__all__ = [
    'Config',
    'IdeaDatabase',
    'setup_idea_database',
    'StoryDatabase',
    'setup_story_database',
]
__version__ = '1.0.0'
