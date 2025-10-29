"""Configuration manager for PrismQ modules.

This module handles .env file management for PrismQ packages, ensuring
that configuration values are persisted and retrieved from the working
directory's .env file.

Design Principles:
- Single Responsibility: Manages .env configuration only
- DRY: Centralized configuration management
- KISS: Simple, focused API for config operations
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """Manages configuration through .env files in the working directory.
    
    This class handles reading, writing, and updating configuration values
    stored in .env files. It ensures that configuration is persisted per
    package in the working directory.
    
    Attributes:
        working_dir: Path to the working directory containing .env file
        env_file: Path to the .env file
        config: Dictionary of configuration key-value pairs
    """

    def __init__(self, working_dir: Optional[str] = None):
        """Initialize ConfigManager with a working directory.
        
        Args:
            working_dir: Path to working directory. If None, uses current directory.
        """
        if working_dir is None:
            working_dir = os.getcwd()
        
        self.working_dir = Path(working_dir).resolve()
        self.env_file = self.working_dir / ".env"
        self.config: Dict[str, str] = {}
        
        # Load existing configuration if .env exists
        if self.env_file.exists():
            self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from .env file into memory."""
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        self.config[key] = value
        except Exception as e:
            print(f"[WARNING] Failed to load .env file: {e}", file=sys.stderr)
    
    def _save_config(self) -> None:
        """Save current configuration to .env file."""
        try:
            # Ensure working directory exists
            self.working_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write("# PrismQ Module Configuration\n")
                f.write("# This file stores package-specific configuration\n")
                f.write("# Auto-generated - do not edit manually unless necessary\n\n")
                
                for key, value in sorted(self.config.items()):
                    f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"[ERROR] Failed to save .env file: {e}", file=sys.stderr)
            raise
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: str) -> None:
        """Set a configuration value and save to .env file.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self._save_config()
    
    def update(self, values: Dict[str, str]) -> None:
        """Update multiple configuration values at once.
        
        Args:
            values: Dictionary of key-value pairs to update
        """
        self.config.update(values)
        self._save_config()
    
    def has(self, key: str) -> bool:
        """Check if a configuration key exists.
        
        Args:
            key: Configuration key
            
        Returns:
            True if key exists, False otherwise
        """
        return key in self.config
    
    def ensure_exists(self) -> None:
        """Ensure .env file exists in working directory.
        
        Creates the .env file with default values if it doesn't exist.
        """
        if not self.env_file.exists():
            self._save_config()
    
    def prompt_if_missing(self, key: str, prompt_message: str, 
                         default: Optional[str] = None) -> str:
        """Prompt user for a configuration value if not set.
        
        Args:
            key: Configuration key
            prompt_message: Message to display to user
            default: Default value to use if provided
            
        Returns:
            Configuration value (existing or newly set)
        """
        if self.has(key):
            return self.get(key)
        
        # Check if running in interactive mode
        if not sys.stdin.isatty():
            # Non-interactive mode (CI/testing)
            if default is not None:
                self.set(key, default)
                return default
            else:
                # Cannot prompt in non-interactive mode
                print(f"[WARNING] Configuration key '{key}' not set and running in non-interactive mode", 
                      file=sys.stderr)
                return ""
        
        # Interactive mode - prompt user
        user_input = input(f"{prompt_message}: ")
        if not user_input and default is not None:
            user_input = default
        
        if user_input:
            self.set(key, user_input)
        
        return user_input


def find_prismq_directory() -> Optional[Path]:
    """Find the nearest parent directory with 'PrismQ' in its name.
    
    Walks up the directory tree from current directory to find a directory
    whose name contains 'PrismQ' (case-insensitive).
    
    Returns:
        Path to the nearest PrismQ directory or None if not found
    """
    current = Path.cwd().resolve()
    
    # Check current directory first
    if 'prismq' in current.name.lower():
        return current
    
    # Walk up the directory tree
    for parent in current.parents:
        if 'prismq' in parent.name.lower():
            return parent
    
    return None


def get_working_directory_from_env() -> Optional[str]:
    """Get the working directory from environment or config.
    
    Checks in order:
    1. PRISMQ_WORKING_DIR environment variable
    2. .env file in nearest PrismQ directory
    3. .env file in current directory
    
    Returns:
        Working directory path or None if not configured
    """
    # Check environment variable first
    work_dir = os.environ.get('PRISMQ_WORKING_DIR')
    if work_dir:
        return work_dir
    
    # Check for .env in nearest PrismQ directory
    prismq_dir = find_prismq_directory()
    if prismq_dir:
        env_file = prismq_dir / ".env"
        if env_file.exists():
            config = ConfigManager(str(prismq_dir))
            work_dir = config.get('WORKING_DIR')
            if work_dir:
                return work_dir
    
    # Fallback: Check for .env in current directory
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        config = ConfigManager()
        work_dir = config.get('WORKING_DIR')
        if work_dir:
            return work_dir
    
    return None


def setup_working_directory(package_name: str = "PrismQ.IdeaInspiration.Model", 
                           quiet: bool = False) -> ConfigManager:
    """Set up working directory configuration for a package.
    
    This function ensures that:
    1. Working directory is configured (asks user if not set)
    2. .env file exists in nearest PrismQ directory (or working directory if not found)
    3. Package configuration is saved
    
    The .env file is stored in the nearest parent directory with 'PrismQ' in its name,
    allowing configuration to be shared across all PrismQ modules in that directory tree.
    If PRISMQ_WORKING_DIR environment variable is set, the .env is stored there instead.
    
    Args:
        package_name: Name of the package
        quiet: If True, suppress informational messages (for scripting)
        
    Returns:
        ConfigManager instance for the working directory
    """
    # Try to get existing working directory
    work_dir = get_working_directory_from_env()
    
    if not work_dir:
        # Need to ask user for working directory
        if sys.stdin.isatty():
            # Interactive mode
            current_dir = os.getcwd()
            if not quiet:
                print(f"[INFO] Working directory not configured.", file=sys.stderr)
                print(f"[INFO] Current directory: {current_dir}", file=sys.stderr)
            
            use_current = input(f"Use current directory '{current_dir}' as working directory? (Y/N): ")
            if use_current.strip().upper() == 'Y':
                work_dir = current_dir
            else:
                work_dir = input("Enter the working directory path: ")
                if not work_dir:
                    work_dir = current_dir
        else:
            # Non-interactive mode - use current directory
            work_dir = os.getcwd()
            if not quiet:
                print(f"[INFO] Using current directory as working directory: {work_dir}", file=sys.stderr)
    
    # Determine where to store the .env file
    # Priority: PRISMQ_WORKING_DIR env var > nearest PrismQ directory > working directory
    env_location = None
    if os.environ.get('PRISMQ_WORKING_DIR'):
        # If environment variable is set, use that location for .env
        env_location = os.environ.get('PRISMQ_WORKING_DIR')
    else:
        # Find the nearest PrismQ directory to store .env file
        prismq_dir = find_prismq_directory()
        if prismq_dir:
            env_location = str(prismq_dir)
        else:
            # Fallback to working directory if no PrismQ directory found
            env_location = work_dir
    
    # Create config manager for the .env file location
    config = ConfigManager(env_location)
    
    # Ensure .env exists
    config.ensure_exists()
    
    # Set package-specific configuration
    if not config.has('APP_NAME'):
        config.set('APP_NAME', package_name)
    
    if not config.has('WORKING_DIR'):
        config.set('WORKING_DIR', work_dir)
    
    return config
