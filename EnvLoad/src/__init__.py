"""EnvLoad - Centralized environment and configuration management for PrismQ.

This module provides a standardized way to load and manage environment variables
and configuration across all PrismQ modules (T, A, V, P, M, Client).

Key Features:
- Centralized .env file management
- Standardized working directory at C:\\PrismQ (Windows) or ~/PrismQ (Unix-like)
- Cross-platform path handling
- Interactive and non-interactive configuration modes
- Automatic .env file creation and management

Usage:
    from EnvLoad.src import Config
    
    config = Config()
    print(config.working_directory)
    print(config.database_url)
"""

from .config import Config

__all__ = ['Config']
__version__ = '1.0.0'
