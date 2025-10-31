"""Configuration management for PrismQ.IdeaInspiration.Sources.Events.SportsHighlights."""

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
        self._load_configuration()
    
    def _find_prismq_directory(self) -> Path:
        """Find the topmost/root parent directory with exact name 'PrismQ'.
        
        Returns:
            Path to the topmost PrismQ directory, or current directory if none found
        """
        current_path = Path.cwd().absolute()
        prismq_dir = None
        
        # Check current directory and all parents
        for path in [current_path] + list(current_path.parents):
            if path.name == "PrismQ":
                prismq_dir = path
        
        return prismq_dir if prismq_dir else current_path
    
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
    
    def _prompt_for_value(self, key: str, description: str, default: str = "") -> str:
        """Prompt user for a configuration value.
        
        Args:
            key: Environment variable key
            description: Human-readable description
            default: Default value
            
        Returns:
            The value entered by the user or the default
        """
        if not self._interactive:
            return default
        
        try:
            prompt = f"{description}"
            if default:
                prompt += f" (default: {default})"
            prompt += ": "
            
            value = input(prompt).strip()
            return value if value else default
        except (EOFError, KeyboardInterrupt):
            return default
    
    def _load_configuration(self):
        """Load configuration from environment variables."""
        # Database path
        default_db = str(Path(self.working_directory) / "data" / "sports_highlights.db")
        self.database_path = os.getenv("SPORTS_HIGHLIGHTS_DB_PATH")
        
        if not self.database_path:
            self.database_path = self._prompt_for_value(
                "SPORTS_HIGHLIGHTS_DB_PATH",
                "Path to sports highlights database",
                default_db
            )
            if self.database_path:
                set_key(self.env_file, "SPORTS_HIGHLIGHTS_DB_PATH", self.database_path)
                load_dotenv(self.env_file, override=True)
        
        # TheSportsDB API key (optional - free tier available)
        self.thesportsdb_api_key = os.getenv("THESPORTSDB_API_KEY", "3")  # 3 is the test key
        
        # Default sport
        self.default_sport = os.getenv("SPORTS_DEFAULT_SPORT", "Soccer")
        
        # Default league
        self.default_league = os.getenv("SPORTS_DEFAULT_LEAGUE", "English Premier League")
        
        # Max events to fetch
        self.max_events = int(os.getenv("SPORTS_MAX_EVENTS", "50"))
