"""Configuration management for PrismQ modules.

This module provides centralized .env file loading and configuration management
based on the pattern from PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeShortsSource.

Design Principles:
- Single Responsibility: Manages .env configuration only
- DRY: Centralized configuration management
- KISS: Simple, focused API for config operations
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key


class Config:
    """Manages application configuration from environment variables.
    
    This class handles:
    - Finding the topmost PrismQ directory
    - Creating and managing .env files in PrismQ_WD directory
    - Loading environment variables from .env files
    - Interactive prompting for missing configuration values
    """

    def __init__(self, env_file: Optional[str] = None, interactive: bool = True):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file (default: .env in topmost PrismQ_WD directory)
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
    
    def _create_env_file(self):
        """Create a new .env file with default values."""
        Path(self.env_file).parent.mkdir(parents=True, exist_ok=True)
        Path(self.env_file).touch()
    
    def _ensure_working_directory(self):
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
    
    def get_or_prompt(
        self, 
        key: str, 
        description: str, 
        default: str = "", 
        required: bool = False
    ) -> str:
        """Get value from environment or prompt user if missing.
        
        This is a public method that can be used by modules to get configuration
        values with optional interactive prompting.
        
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
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value from environment.
        
        Args:
            key: Environment variable key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return os.getenv(key, default)
    
    def set(self, key: str, value: str) -> None:
        """Set a configuration value and save to .env file.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        set_key(self.env_file, key, value)
        # Reload to pick up the change
        load_dotenv(self.env_file, override=True)


def find_prismq_directory() -> Optional[Path]:
    """Find the topmost parent directory with exact name 'PrismQ'.
    
    This is a standalone utility function for finding the PrismQ root directory.
    
    Returns:
        Path to the topmost PrismQ directory, or None if not found
    """
    current_path = Path.cwd().absolute()
    prismq_dir = None
    
    # Check current directory and all parents, continuing to find the topmost match
    for path in [current_path] + list(current_path.parents):
        if path.name == "PrismQ":
            prismq_dir = path
            # Continue searching - don't break early
    
    return prismq_dir
