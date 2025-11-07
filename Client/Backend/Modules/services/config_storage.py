"""Configuration storage service for PrismQ modules.

This module provides persistent storage of module configurations using JSON files.
Each module's parameters are saved to a separate JSON file in the configs/parameters directory.

This service follows SOLID principles:
- Single Responsibility: Manages only configuration file I/O
- Open/Closed: Can be extended with different storage backends
- Liskov Substitution: Could implement a storage interface
- Interface Segregation: Provides minimal, focused methods
- Dependency Inversion: Depends on abstractions (Path)
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ConfigStorage:
    """
    Manages persistent storage of module configurations.
    
    Responsibilities:
    - Save module parameters to JSON files
    - Load saved parameters
    - Provide default values
    - Handle config validation
    """
    
    def __init__(self, config_dir: Path):
        """
        Initialize configuration storage.
        
        Args:
            config_dir: Base configuration directory
        """
        self.config_dir = config_dir / "parameters"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ConfigStorage initialized with directory: {self.config_dir}")
    
    def get_config(self, module_id: str) -> Dict:
        """
        Get saved configuration for a module.
        
        Args:
            module_id: Module identifier
            
        Returns:
            Dictionary of saved parameters, or empty dict if not found
        """
        config_file = self.config_dir / f"{module_id}.json"
        
        if not config_file.exists():
            logger.debug(f"No saved config found for {module_id}")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded config for {module_id}")
                return data.get("parameters", {})
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file for {module_id}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading config for {module_id}: {e}")
            return {}
    
    def save_config(self, module_id: str, parameters: Dict) -> bool:
        """
        Save configuration for a module.
        
        Args:
            module_id: Module identifier
            parameters: Dictionary of parameters to save
            
        Returns:
            True if successful, False otherwise
        """
        config_file = self.config_dir / f"{module_id}.json"
        
        try:
            data = {
                "module_id": module_id,
                "parameters": parameters,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Write atomically by writing to temp file first
            temp_file = config_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Rename to final location (atomic on most systems)
            temp_file.replace(config_file)
            
            logger.info(f"Saved config for {module_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving config for {module_id}: {e}")
            return False
    
    def delete_config(self, module_id: str) -> bool:
        """
        Delete saved configuration for a module.
        
        Args:
            module_id: Module identifier
            
        Returns:
            True if config was deleted, False if not found
        """
        config_file = self.config_dir / f"{module_id}.json"
        
        if config_file.exists():
            try:
                config_file.unlink()
                logger.info(f"Deleted config for {module_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting config for {module_id}: {e}")
                return False
        
        logger.debug(f"No config to delete for {module_id}")
        return False
    
    def list_configs(self) -> List[str]:
        """
        List all modules with saved configurations.
        
        Returns:
            List of module IDs with saved configs
        """
        try:
            return [f.stem for f in self.config_dir.glob("*.json")]
        except Exception as e:
            logger.error(f"Error listing configs: {e}")
            return []
