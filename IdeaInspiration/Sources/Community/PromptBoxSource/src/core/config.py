"""Configuration management for PromptBoxSource."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key


class Config:
    """Manages application configuration from environment variables."""

    def __init__(self, env_file: Optional[str] = None, interactive: bool = True):
        """Initialize configuration."""
        if env_file is None:
            prismq_dir = self._find_prismq_directory()
            if prismq_dir.name == "PrismQ":
                working_dir = prismq_dir.parent / "PrismQ_WD"
            else:
                working_dir = prismq_dir
            self.working_directory = str(working_dir)
            env_file = working_dir / ".env"
        else:
            env_path = Path(env_file)
            self.working_directory = str(env_path.parent.absolute())
            env_file = env_path
        
        self.env_file = str(env_file)
        self._interactive = interactive
        
        if not Path(self.env_file).exists():
            Path(self.env_file).parent.mkdir(parents=True, exist_ok=True)
            Path(self.env_file).touch()
        
        load_dotenv(self.env_file)
        self._ensure_working_directory()
        self._load_configuration()
    
    def _find_prismq_directory(self) -> Path:
        """Find the topmost/root parent directory with exact name 'PrismQ'."""
        current_path = Path.cwd().absolute()
        prismq_dir = None
        for path in [current_path] + list(current_path.parents):
            if path.name == "PrismQ":
                prismq_dir = path
        return prismq_dir if prismq_dir else current_path
    
    def _ensure_working_directory(self):
        """Ensure working directory is stored in .env file."""
        current_wd = os.getenv("WORKING_DIRECTORY")
        if current_wd != self.working_directory:
            set_key(self.env_file, "WORKING_DIRECTORY", self.working_directory)
            load_dotenv(self.env_file, override=True)
    
    def _get_or_prompt(self, key: str, description: str, default: str = "", 
                      required: bool = False) -> str:
        """Get value from environment or use default."""
        value = os.getenv(key)
        if value is None or value == "":
            if self._interactive and required:
                try:
                    prompt = f"{description}"
                    if default:
                        prompt += f" (default: {default})"
                    prompt += ": "
                    value = input(prompt).strip()
                    value = value if value else default
                    if value:
                        set_key(self.env_file, key, value)
                        load_dotenv(self.env_file, override=True)
                except (EOFError, KeyboardInterrupt):
                    value = default
            else:
                value = default
        return value
    
    def _load_configuration(self):
        """Load all configuration values."""
        database_url = self._get_or_prompt(
            "PROMPT_BOX_DATABASE_URL",
            "Database URL for PromptBoxSource",
            f"sqlite:///{Path(self.working_directory) / 'prompt_box.s3db'}",
            required=False
        )
        
        self.database_url = database_url
        
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            if not Path(db_path).is_absolute():
                self.database_path = str(Path(self.working_directory) / db_path)
            else:
                self.database_path = db_path
        else:
            self.database_path = str(Path(self.working_directory) / "prompt_box.s3db")
        
        # Form submission settings
        self.form_endpoint = self._get_or_prompt(
            "PROMPT_BOX_FORM_ENDPOINT", "Form submission endpoint URL", "", False)
        
        self.submission_directory = self._get_or_prompt(
            "PROMPT_BOX_SUBMISSION_DIR", "Directory for form submissions",
            str(Path(self.working_directory) / "submissions"), False)
