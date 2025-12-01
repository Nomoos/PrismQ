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
"""

from .config import Config
from .idea import IdeaDatabase, setup_idea_database

__all__ = ['Config', 'IdeaDatabase', 'setup_idea_database']
__version__ = '1.0.0'
