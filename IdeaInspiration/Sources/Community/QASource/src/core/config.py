"""Configuration management for QASource."""

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
        """Find the topmost/root parent directory with exact name 'PrismQ'."""
        current_path = Path.cwd().absolute()
        prismq_dir = None
        
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
        """Prompt user for a configuration value."""
        if not self._interactive:
            return default
        
        prompt = f"{description}"
        if default:
            prompt += f" (default: {default})"
        prompt += ": "
        
        try:
            value = input(prompt).strip()
            return value if value else default
        except (EOFError, KeyboardInterrupt):
            return default
    
    def _get_or_prompt(self, key: str, description: str, default: str = "", 
                      required: bool = False) -> str:
        """Get value from environment or prompt user if missing."""
        value = os.getenv(key)
        
        if value is None or value == "":
            if self._interactive and required:
                value = self._prompt_for_value(key, description, default)
                if value:
                    set_key(self.env_file, key, value)
                    load_dotenv(self.env_file, override=True)
            else:
                value = default
        
        return value
    
    def _load_configuration(self):
        """Load all configuration values with interactive prompting."""
        # Database configuration
        database_url = self._get_or_prompt(
            "QA_DATABASE_URL",
            "Database URL for QASource (e.g., sqlite:///qa_source.s3db)",
            f"sqlite:///{Path(self.working_directory) / 'qa_source.s3db'}",
            required=False
        )
        
        self.database_url = database_url
        
        # Extract database_path from SQLite URLs
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            if not Path(db_path).is_absolute():
                self.database_path = str(Path(self.working_directory) / db_path)
            else:
                self.database_path = db_path
        else:
            self.database_path = str(Path(self.working_directory) / "qa_source.s3db")
        
        # StackExchange configuration
        self.stackexchange_key = self._get_or_prompt(
            "STACKEXCHANGE_API_KEY",
            "StackExchange API key (optional, increases rate limit)",
            "",
            required=False
        )
        
        # Sites to query (comma-separated)
        sites = self._get_or_prompt(
            "QA_STACKEXCHANGE_SITES",
            "StackExchange sites to query (comma-separated)",
            "stackoverflow,askubuntu,superuser",
            required=False
        )
        self.stackexchange_sites = [s.strip() for s in sites.split(',') if s.strip()]
        
        # Tags to filter by
        tags = self._get_or_prompt(
            "QA_TAGS",
            "Tags to filter questions by (comma-separated)",
            "python,javascript,programming",
            required=False
        )
        self.filter_tags = [t.strip() for t in tags.split(',') if t.strip()]
        
        # Max questions per query
        max_questions = self._get_or_prompt(
            "QA_MAX_QUESTIONS",
            "Maximum questions to fetch per query",
            "100",
            required=False
        )
        self.max_questions = int(max_questions) if max_questions else 100
