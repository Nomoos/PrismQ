"""Configuration management for GoogleTrendsSource."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key


class Config:
    """Manages application configuration from environment variables."""

    def __init__(self, env_file: Optional[str] = None, interactive: bool = True):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file (default: .env in working directory)
            interactive: Whether to prompt for missing values (default: True)
        """
        # Determine working directory and .env file path
        if env_file is None:
            working_dir = Path.cwd()
            self.working_directory = str(working_dir)
            env_file = working_dir / ".env"
        else:
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
        
        # Load configuration
        self._load_configuration()
    
    def _create_env_file(self):
        """Create a new .env file with default values."""
        Path(self.env_file).parent.mkdir(parents=True, exist_ok=True)
        Path(self.env_file).touch()
    
    def _ensure_working_directory(self):
        """Ensure working directory is stored in .env file."""
        current_wd = os.getenv("WORKING_DIRECTORY")
        
        if current_wd != self.working_directory:
            set_key(self.env_file, "WORKING_DIRECTORY", self.working_directory)
            load_dotenv(self.env_file, override=True)
    
    def _get_or_default(self, key: str, default: str = "") -> str:
        """Get value from environment or use default.
        
        Args:
            key: Environment variable key
            default: Default value
            
        Returns:
            The configuration value
        """
        value = os.getenv(key)
        return value if value is not None and value != "" else default
    
    def _load_configuration(self):
        """Load all configuration values."""
        # Database configuration
        database_url = self._get_or_default(
            "DATABASE_URL",
            f"sqlite:///{Path(self.working_directory) / 'tik_tok_hashtag.db'}"
        )
        
        self.database_url = database_url
        
        # Extract database_path from SQLite URLs for backward compatibility
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            if not Path(db_path).is_absolute():
                self.database_path = str(Path(self.working_directory) / db_path)
            else:
                self.database_path = db_path
        else:
            self.database_path = str(Path(self.working_directory) / "tik_tok_hashtag.db")
        
        # Google Trends configuration
        self.tik_tok_hashtag_region = self._get_or_default("GOOGLE_TRENDS_REGION", "US")
        self.tik_tok_hashtag_language = self._get_or_default("GOOGLE_TRENDS_LANGUAGE", "en-US")
        self.tik_tok_hashtag_timeframe = self._get_or_default("GOOGLE_TRENDS_TIMEFRAME", "now 7-d")
        
        max_results = self._get_or_default("GOOGLE_TRENDS_MAX_RESULTS", "25")
        self.tik_tok_hashtag_max_results = int(max_results) if max_results else 25
        
        # Scraping configuration
        max_retry = self._get_or_default("MAX_RETRY_ATTEMPTS", "3")
        self.max_retry_attempts = int(max_retry) if max_retry else 3
        
        retry_delay = self._get_or_default("RETRY_DELAY_SECONDS", "5")
        self.retry_delay_seconds = int(retry_delay) if retry_delay else 5
