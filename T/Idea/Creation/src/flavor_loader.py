"""Flavor Loader Service - SOLID Design.

This module implements the Flavor Loader following SOLID principles:
- Single Responsibility: Only loads and manages flavor definitions
- Open/Closed: Extended through configuration, not code modification
- Dependency Inversion: Depends on abstract file loading, not specifics
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class FlavorLoader:
    """Loads flavor definitions from external JSON configuration.
    
    This class is responsible for:
    - Loading flavor definitions from JSON files
    - Validating flavor structure
    - Providing access to flavor data
    
    Following Single Responsibility Principle: Does ONE thing only.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize flavor loader.
        
        Args:
            config_path: Optional path to flavors.json file.
                        If None, uses default location.
        """
        if config_path is None:
            # Default: data/flavors.json relative to this file
            current_dir = Path(__file__).parent
            config_path = current_dir.parent / "data" / "flavors.json"
        
        self.config_path = Path(config_path)
        self._data = None
        self._flavors = None
        self._default_fields = None
    
    def load(self) -> None:
        """Load flavor definitions from JSON file.
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If required sections are missing
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Flavor config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._data = json.load(f)
        
        # Validate structure
        if 'flavors' not in self._data:
            raise ValueError("Missing 'flavors' section in config")
        if 'default_fields' not in self._data:
            raise ValueError("Missing 'default_fields' section in config")
        
        self._flavors = self._data['flavors']
        self._default_fields = self._data['default_fields']
    
    def ensure_loaded(self) -> None:
        """Ensure flavors are loaded (lazy loading)."""
        if self._flavors is None:
            self.load()
    
    def get_all_flavors(self) -> Dict[str, Dict[str, Any]]:
        """Get all flavor definitions.
        
        Returns:
            Dictionary mapping flavor names to their definitions
        """
        self.ensure_loaded()
        return self._flavors.copy()
    
    def get_flavor(self, name: str) -> Dict[str, Any]:
        """Get a specific flavor definition.
        
        Args:
            name: Flavor name
            
        Returns:
            Flavor definition dictionary
            
        Raises:
            KeyError: If flavor not found
        """
        self.ensure_loaded()
        if name not in self._flavors:
            raise KeyError(f"Flavor not found: {name}")
        return self._flavors[name].copy()
    
    def list_flavor_names(self) -> List[str]:
        """Get list of all flavor names.
        
        Returns:
            Sorted list of flavor names
        """
        self.ensure_loaded()
        return sorted(self._flavors.keys())
    
    def get_default_fields(self) -> Dict[str, str]:
        """Get default field definitions.
        
        Returns:
            Dictionary of field names to descriptions
        """
        self.ensure_loaded()
        return self._default_fields.copy()
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get configuration metadata.
        
        Returns:
            Metadata dictionary
        """
        self.ensure_loaded()
        return self._data.get('metadata', {}).copy()
    
    def get_flavors_by_audience(self, audience: str) -> List[str]:
        """Get flavors filtered by target audience.
        
        Args:
            audience: Audience filter string
            
        Returns:
            List of matching flavor names
        """
        self.ensure_loaded()
        audience_lower = audience.lower()
        matching = []
        
        for name, flavor in self._flavors.items():
            if 'audience' in flavor and audience_lower in flavor['audience'].lower():
                matching.append(name)
        
        return sorted(matching)
    
    def get_flavor_count(self) -> int:
        """Get total number of flavors.
        
        Returns:
            Number of flavors
        """
        self.ensure_loaded()
        return len(self._flavors)
    
    def get_weights(self) -> Dict[str, int]:
        """Get flavor weights for weighted selection.
        
        Returns:
            Dictionary mapping flavor names to weights
        """
        self.ensure_loaded()
        weights = {}
        for name, flavor in self._flavors.items():
            weights[name] = flavor.get('weight', 50)  # Default weight: 50
        return weights


# Singleton instance for easy access
_loader_instance = None


def get_flavor_loader(config_path: Optional[Path] = None) -> FlavorLoader:
    """Get the global flavor loader instance.
    
    This implements a simple singleton pattern for convenient access.
    
    Args:
        config_path: Optional custom config path
        
    Returns:
        FlavorLoader instance
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = FlavorLoader(config_path)
    return _loader_instance


__all__ = [
    'FlavorLoader',
    'get_flavor_loader',
]
