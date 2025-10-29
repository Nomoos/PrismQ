"""Configuration management for the PrismQ module."""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv, set_key


class Config:
    """Configuration class for the PrismQ module.

    Automatically detects the topmost parent directory with exact name 'PrismQ'
    and stores configuration in a .env file in a PrismQ_WD sibling directory.
    """

    def __init__(self, env_file: Optional[str] = None, interactive: bool = True) -> None:
        """Initialize configuration from environment variables and .env file.

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
            env_file_path = working_dir / ".env"
        else:
            # Use the directory of the provided env_file as working directory
            env_path = Path(env_file)
            self.working_directory = str(env_path.parent.absolute())
            env_file_path = env_path

        self.env_file = str(env_file_path)
        self._interactive = interactive

        # Create .env file if it doesn't exist
        if not Path(self.env_file).exists():
            self._create_env_file()

        # Load environment variables from .env file
        load_dotenv(self.env_file)

        # Store/update working directory in .env
        self._ensure_working_directory()

        # Load configuration
        self.app_name: str = os.getenv("APP_NAME", "PrismQ.ModuleName")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        # Python Configuration
        self.python_executable: str = os.getenv("PYTHON_EXECUTABLE", "python")

        # Paths
        self.input_dir: Path = Path(os.getenv("INPUT_DIR", "./input"))
        self.output_dir: Path = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.cache_dir: Path = Path(os.getenv("CACHE_DIR", "./cache"))

        # Create directories if they don't exist
        self._create_directories()

    def _find_prismq_directory(self) -> Path:
        """Find the topmost/root parent directory with exact name 'PrismQ'.

        This searches upward from the current directory and returns the highest-level
        directory with the exact name 'PrismQ'. This ensures that .env files are
        centralized at the root PrismQ directory, not in subdirectories or modules.

        Returns:
            Path to the topmost PrismQ directory, or current directory if none found
        """
        current_path = Path.cwd().absolute()
        prismq_dir = None

        # Check current directory and all parents, continuing to find the topmost match
        for path in [current_path] + list(current_path.parents):
            if path.name == "PrismQ":
                prismq_dir = path
                # Continue searching - don't break early

        # Return the topmost PrismQ directory found, or current directory as fallback
        return prismq_dir if prismq_dir else current_path

    def _create_env_file(self) -> None:
        """Create a new .env file with default values."""
        env_path = Path(self.env_file)
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.touch()

    def _ensure_working_directory(self) -> None:
        """Ensure working directory is stored in .env file."""
        current_wd = os.getenv("WORKING_DIRECTORY")

        if current_wd != self.working_directory:
            # Update or add working directory to .env
            set_key(self.env_file, "WORKING_DIRECTORY", self.working_directory)
            # Reload to pick up the change
            load_dotenv(self.env_file, override=True)

    def _prompt_for_value(self, key: str, description: str, default: str = "") -> str:
        """Prompt user for a configuration value.

        Args:
            key: Environment variable key
            description: Human-readable description of the value
            default: Default value to suggest

        Returns:
            The value entered by the user or the default
        """
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
            # In non-interactive environments, return default
            return default

    def _get_or_prompt(
        self, key: str, description: str, default: str = "", required: bool = False
    ) -> str:
        """Get value from environment or prompt user if missing.

        Args:
            key: Environment variable key
            description: Human-readable description of the value
            default: Default value
            required: Whether this value is required

        Returns:
            The configuration value
        """
        value = os.getenv(key)

        if value is None or value == "":
            # Value is missing, prompt user if interactive
            if self._interactive and required:
                value = self._prompt_for_value(key, description, default)
                # Save the value to .env file
                if value:
                    set_key(self.env_file, key, value)
                    # Reload to pick up the change
                    load_dotenv(self.env_file, override=True)
            else:
                value = default

        return value

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [self.input_dir, self.output_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_api_key(self, service: str) -> str | None:
        """Get API key for a service.

        Args:
            service: Name of the service (e.g., 'openai', 'anthropic')

        Returns:
            API key or None if not found
        """
        env_var = f"{service.upper()}_API_KEY"
        return os.getenv(env_var)


# Global config instance
config = Config()
