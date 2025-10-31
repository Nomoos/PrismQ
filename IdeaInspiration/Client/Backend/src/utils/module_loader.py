"""Module loader for loading module definitions from JSON configuration."""

import json
from pathlib import Path
from typing import List, Optional, Dict
from ..models.module import Module, ModuleParameter


class ModuleLoader:
    """Loads and manages module definitions from configuration files."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize module loader.
        
        Args:
            config_path: Path to modules.json file. If None, uses default location.
        """
        if config_path is None:
            # Default to configs/modules.json relative to Backend directory
            backend_dir = Path(__file__).parent.parent.parent
            config_path = backend_dir / "configs" / "modules.json"
        
        self.config_path = config_path
        self._modules: List[Module] = []
        self._modules_by_id: Dict[str, Module] = {}  # O(1) lookup by ID
        self._load_modules()
    
    def _load_modules(self) -> None:
        """Load modules from JSON configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Module configuration not found at {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            module_data = data.get('modules', [])
            self._modules = []
            self._modules_by_id = {}
            
            for idx, mod in enumerate(module_data):
                try:
                    # Convert parameter dictionaries to ModuleParameter objects
                    parameters = [
                        ModuleParameter(**param) for param in mod.get('parameters', [])
                    ]
                    
                    # Create Module object with parameters
                    module = Module(
                        id=mod['id'],
                        name=mod['name'],
                        description=mod['description'],
                        category=mod['category'],
                        script_path=mod['script_path'],
                        parameters=parameters,
                        version=mod.get('version', '1.0.0'),
                        tags=mod.get('tags', []),
                        status=mod.get('status', 'active'),
                        enabled=mod.get('enabled', True),
                    )
                    self._modules.append(module)
                    self._modules_by_id[module.id] = module
                    
                except KeyError as e:
                    raise ValueError(
                        f"Missing required field {e} in module at index {idx} "
                        f"(id: {mod.get('id', 'unknown')})"
                    )
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in module configuration: {e}")
    
    def get_all_modules(self) -> List[Module]:
        """
        Get all loaded modules.
        
        Returns:
            List of Module objects
        """
        return self._modules.copy()
    
    def get_module(self, module_id: str) -> Optional[Module]:
        """
        Get a specific module by ID (O(1) lookup).
        
        Args:
            module_id: Module identifier
            
        Returns:
            Module object if found, None otherwise
        """
        return self._modules_by_id.get(module_id)
    
    def reload(self) -> None:
        """Reload modules from configuration file."""
        self._load_modules()


# Global module loader instance
_module_loader: Optional[ModuleLoader] = None


def get_module_loader() -> ModuleLoader:
    """
    Get the global module loader instance.
    
    Returns:
        ModuleLoader instance
    """
    global _module_loader
    if _module_loader is None:
        _module_loader = ModuleLoader()
    return _module_loader
