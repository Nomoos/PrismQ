"""
Task Handler Configuration Loader.

Supports loading task handler registrations from configuration files.
Part of Worker 10 Issue #339: Ensure Client takes only registered task handlers.

Supported formats:
- JSON (.json)
- YAML (.yaml, .yml)
- TOML (.toml)
"""

import json
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from .task_handler_registry import TaskHandlerRegistry

logger = logging.getLogger(__name__)


class HandlerConfigError(Exception):
    """Raised when handler configuration is invalid."""
    pass


class TaskHandlerConfigLoader:
    """
    Loads task handler configurations from files.
    
    Configuration file format (JSON/YAML/TOML):
    {
        "handlers": [
            {
                "task_type": "send_email",
                "module": "myapp.handlers.email",
                "function": "handle_send_email",
                "description": "Sends email notifications",
                "version": "1.0.0"
            },
            {
                "task_type": "generate_report",
                "module": "myapp.handlers.reports",
                "function": "handle_generate_report",
                "description": "Generates reports",
                "version": "1.0.0"
            }
        ]
    }
    
    Example usage:
        >>> loader = TaskHandlerConfigLoader()
        >>> registry = TaskHandlerRegistry()
        >>> loader.load_from_file("config/handlers.json", registry)
    """
    
    def __init__(self):
        """Initialize the config loader."""
        pass
    
    def load_from_file(
        self,
        config_path: Path | str,
        registry: TaskHandlerRegistry,
        allow_override: bool = False
    ) -> int:
        """
        Load handler configurations from a file.
        
        Args:
            config_path: Path to configuration file
            registry: TaskHandlerRegistry to register handlers in
            allow_override: Whether to allow overriding existing handlers
            
        Returns:
            Number of handlers successfully registered
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            HandlerConfigError: If configuration is invalid
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Handler configuration not found: {config_path}")
        
        # Load based on file extension
        suffix = config_path.suffix.lower()
        
        if suffix == '.json':
            config_data = self._load_json(config_path)
        elif suffix in ('.yaml', '.yml'):
            config_data = self._load_yaml(config_path)
        elif suffix == '.toml':
            config_data = self._load_toml(config_path)
        else:
            raise HandlerConfigError(
                f"Unsupported configuration format: {suffix}. "
                f"Supported: .json, .yaml, .yml, .toml"
            )
        
        # Register handlers
        return self._register_handlers(config_data, registry, allow_override)
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise HandlerConfigError(f"Invalid JSON in {path}: {e}")
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            raise HandlerConfigError(
                "PyYAML is required for YAML configuration files. "
                "Install with: pip install pyyaml"
            )
        except Exception as e:
            raise HandlerConfigError(f"Invalid YAML in {path}: {e}")
    
    def _load_toml(self, path: Path) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        try:
            import tomli
            with open(path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            # Try tomllib (Python 3.11+)
            try:
                import tomllib
                with open(path, 'rb') as f:
                    return tomllib.load(f)
            except ImportError:
                raise HandlerConfigError(
                    "tomli is required for TOML configuration files. "
                    "Install with: pip install tomli"
                )
        except Exception as e:
            raise HandlerConfigError(f"Invalid TOML in {path}: {e}")
    
    def _register_handlers(
        self,
        config_data: Dict[str, Any],
        registry: TaskHandlerRegistry,
        allow_override: bool
    ) -> int:
        """
        Register handlers from configuration data.
        
        Args:
            config_data: Parsed configuration dictionary
            registry: TaskHandlerRegistry to register in
            allow_override: Whether to allow overriding existing handlers
            
        Returns:
            Number of handlers successfully registered
        """
        if 'handlers' not in config_data:
            raise HandlerConfigError("Configuration must contain 'handlers' key")
        
        handlers_config = config_data['handlers']
        
        if not isinstance(handlers_config, list):
            raise HandlerConfigError("'handlers' must be a list")
        
        registered_count = 0
        
        for idx, handler_config in enumerate(handlers_config):
            try:
                self._register_single_handler(
                    handler_config,
                    registry,
                    allow_override
                )
                registered_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to register handler at index {idx}: {e}"
                )
                raise HandlerConfigError(
                    f"Failed to register handler at index {idx}: {e}"
                )
        
        logger.info(f"Registered {registered_count} handlers from configuration")
        return registered_count
    
    def _register_single_handler(
        self,
        handler_config: Dict[str, Any],
        registry: TaskHandlerRegistry,
        allow_override: bool
    ) -> None:
        """
        Register a single handler from configuration.
        
        Args:
            handler_config: Handler configuration dictionary
            registry: TaskHandlerRegistry to register in
            allow_override: Whether to allow overriding existing handlers
        """
        # Validate required fields
        required_fields = ['task_type', 'module', 'function']
        for field in required_fields:
            if field not in handler_config:
                raise HandlerConfigError(
                    f"Handler configuration missing required field: {field}"
                )
        
        task_type = handler_config['task_type']
        module_name = handler_config['module']
        function_name = handler_config['function']
        description = handler_config.get('description', '')
        version = handler_config.get('version', '1.0.0')
        
        # Import the handler function
        try:
            module = importlib.import_module(module_name)
            handler_func = getattr(module, function_name)
        except ImportError as e:
            raise HandlerConfigError(
                f"Cannot import module '{module_name}': {e}"
            )
        except AttributeError:
            raise HandlerConfigError(
                f"Module '{module_name}' has no function '{function_name}'"
            )
        
        # Verify it's callable
        if not callable(handler_func):
            raise HandlerConfigError(
                f"{module_name}.{function_name} is not callable"
            )
        
        # Register the handler
        registry.register_handler(
            task_type=task_type,
            handler=handler_func,
            description=description,
            version=version,
            allow_override=allow_override
        )
        
        logger.info(
            f"Registered handler '{task_type}' -> {module_name}.{function_name} "
            f"(v{version})"
        )


def load_handlers_from_config(
    config_path: Path | str,
    registry: Optional[TaskHandlerRegistry] = None,
    allow_override: bool = False
) -> TaskHandlerRegistry:
    """
    Convenience function to load handlers from a configuration file.
    
    Args:
        config_path: Path to configuration file
        registry: Optional existing registry. If None, creates new one.
        allow_override: Whether to allow overriding existing handlers
        
    Returns:
        TaskHandlerRegistry with loaded handlers
        
    Example:
        >>> registry = load_handlers_from_config("config/handlers.json")
        >>> worker = WorkerEngine(db, "worker-01", handler_registry=registry)
    """
    if registry is None:
        registry = TaskHandlerRegistry()
    
    loader = TaskHandlerConfigLoader()
    loader.load_from_file(config_path, registry, allow_override)
    
    return registry
