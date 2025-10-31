"""Configuration management for PrismQ.IdeaInspiration.Sources.Internal.ManualBacklog."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key


class Config:
    """Manages application configuration from environment variables."""

    def __init__(self, env_file: Optional[str] = None, interactive: bool = True):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file (default: .env in topmost PrismQ directory)
            interactive: Whether to prompt for missing values (default: True)
        """
        # Determine working directory and .env file path
        if env_file is None:
            # Find topmost parent directory with exact name "PrismQ"
            prismq_dir = self._find_prismq_directory()
            # Only add _WD suffix if we found a PrismQ directory
            if prismq_dir.name == "PrismQ":
                working_dir = prismq_dir.parent / "PrismQ_WD"
            else:
                # If no PrismQ found, use current directory as-is
                working_dir = prismq_dir
            self.working_directory = str(working_dir)
            env_file = working_dir / ".env"
        else:
            # Use the directory of the provided env_file as working directory
            env_path = Path(env_file)
            self.working_directory = str(env_path.parent.absolute())
            env_file = env_path
        
        self.env_file = str(env_file)
        self._interactive = interactive
        
        # Create .env file if it doesn't exist
        if not Path(self.env_file).exists():
            self._create_env_file()
        
        # Load environment variables from .env file
        load_dotenv(self.env_file)
        
        # Store/update working directory in .env
        self._ensure_working_directory()
        
        # Load configuration with interactive prompting for missing values
        self._load_config()
    
    def _find_prismq_directory(self) -> Path:
        """Find the topmost parent directory with exact name 'PrismQ'.
        
        Returns:
            Path to PrismQ directory, or current directory if not found
        """
        current = Path.cwd()
        prismq_dir = current
        
        # Walk up the directory tree
        for parent in [current, *current.parents]:
            if parent.name == "PrismQ":
                prismq_dir = parent
                break
        
        return prismq_dir
    
    def _create_env_file(self):
        """Create .env file if it doesn't exist."""
        env_path = Path(self.env_file)
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.touch()
    
    def _ensure_working_directory(self):
        """Ensure WORKING_DIRECTORY is set in .env file."""
        if not os.getenv('WORKING_DIRECTORY'):
            set_key(self.env_file, 'WORKING_DIRECTORY', self.working_directory)
        else:
            # Update to current value
            set_key(self.env_file, 'WORKING_DIRECTORY', self.working_directory)
    
    def _load_config(self):
        """Load configuration from environment variables."""
        # Database path
        self.database_path = self._get_config_value(
            'MANUAL_BACKLOG_DATABASE_PATH',
            os.path.join(self.working_directory, 'Sources', 'Internal', 'ManualBacklog', 'manual_backlog.db'),
            'Path to SQLite database for manual backlog data'
        )
        
        # Default values for new ideas
        self.default_priority = os.getenv('MANUAL_BACKLOG_DEFAULT_PRIORITY', 'medium')
        self.default_status = os.getenv('MANUAL_BACKLOG_DEFAULT_STATUS', 'new')
        self.default_category = os.getenv('MANUAL_BACKLOG_DEFAULT_CATEGORY', 'general')
        
        # Default user (for created_by)
        self.default_user = os.getenv('MANUAL_BACKLOG_DEFAULT_USER', os.getenv('USER', 'unknown'))
    
    def _get_config_value(self, key: str, default: str, description: str) -> str:
        """Get configuration value from environment or prompt user.
        
        Args:
            key: Environment variable key
            default: Default value
            description: Description for prompting
            
        Returns:
            Configuration value
        """
        value = os.getenv(key)
        
        if value:
            return value
        
        if self._interactive:
            print(f"\n{description}")
            print(f"Default: {default}")
            user_input = input("Enter value (or press Enter for default): ").strip()
            value = user_input if user_input else default
            
            # Save to .env file
            set_key(self.env_file, key, value)
        else:
            value = default
            # Save to .env file
            set_key(self.env_file, key, value)
        
        return value
    
    def get_database_url(self) -> str:
        """Get database URL for db_utils.
        
        Returns:
            Database URL string
        """
        return f"sqlite:///{self.database_path}"
