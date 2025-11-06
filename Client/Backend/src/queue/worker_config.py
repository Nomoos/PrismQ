"""
Worker configuration loading and management.

Provides functionality to load worker configuration from files (JSON, YAML, TOML)
and environment variables for queue workers.

Part of Issue #328: Worker Strategy Configuration

Design Principles:
- Single Responsibility: Manages worker configuration loading only
- Open/Closed: Extensible for new configuration formats
- Dependency Inversion: Uses Protocol for configuration loaders
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Protocol

from .models import WorkerConfig, SchedulingStrategy

# Set up logger for configuration warnings
logger = logging.getLogger(__name__)


class ConfigLoader(Protocol):
    """
    Protocol for configuration file loaders.
    
    Follows SOLID Interface Segregation principle.
    """
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        ...


class JSONConfigLoader:
    """Load configuration from JSON files."""
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}") from e


class YAMLConfigLoader:
    """Load configuration from YAML files."""
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML configuration. "
                "Install with: pip install pyyaml"
            )
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}") from e


class TOMLConfigLoader:
    """Load configuration from TOML files."""
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        try:
            import tomli
        except ImportError:
            raise ImportError(
                "tomli is required for TOML configuration. "
                "Install with: pip install tomli"
            )
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(path, 'rb') as f:
                return tomli.load(f)
        except Exception as e:
            raise ValueError(f"Invalid TOML in {file_path}: {e}") from e


class WorkerConfigurationManager:
    """
    Manages worker configuration loading from various sources.
    
    Supports:
    - JSON, YAML, TOML configuration files
    - Environment variable overrides
    - Configuration validation
    - Default values
    
    Follows SOLID principles:
    - Single Responsibility: Configuration loading only
    - Open/Closed: Extensible for new formats via loader registration
    - Dependency Inversion: Depends on ConfigLoader protocol
    """
    
    def __init__(self):
        """Initialize configuration manager with default loaders."""
        self._loaders: Dict[str, ConfigLoader] = {
            '.json': JSONConfigLoader(),
            '.yaml': YAMLConfigLoader(),
            '.yml': YAMLConfigLoader(),
            '.toml': TOMLConfigLoader(),
        }
    
    def register_loader(self, extension: str, loader: ConfigLoader) -> None:
        """
        Register a custom configuration loader.
        
        Args:
            extension: File extension (e.g., '.json')
            loader: ConfigLoader instance
        """
        self._loaders[extension] = loader
    
    def load_from_file(
        self,
        file_path: str,
        apply_env_overrides: bool = True
    ) -> WorkerConfig:
        """
        Load worker configuration from file.
        
        Args:
            file_path: Path to configuration file
            apply_env_overrides: Whether to apply environment variable overrides
            
        Returns:
            WorkerConfig instance
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If configuration is invalid
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in self._loaders:
            raise ValueError(
                f"Unsupported configuration file format: {extension}. "
                f"Supported formats: {', '.join(self._loaders.keys())}"
            )
        
        loader = self._loaders[extension]
        config_dict = loader.load(file_path)
        
        # Apply environment variable overrides
        if apply_env_overrides:
            config_dict = self._apply_env_overrides(config_dict)
        
        # Validate and create WorkerConfig
        return self._create_worker_config(config_dict)
    
    def load_from_dict(
        self,
        config_dict: Dict[str, Any],
        apply_env_overrides: bool = True
    ) -> WorkerConfig:
        """
        Load worker configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            apply_env_overrides: Whether to apply environment variable overrides
            
        Returns:
            WorkerConfig instance
            
        Raises:
            ValueError: If configuration is invalid
        """
        if apply_env_overrides:
            config_dict = self._apply_env_overrides(config_dict)
        
        return self._create_worker_config(config_dict)
    
    def load_from_env(self, prefix: str = "PRISMQ_WORKER_") -> WorkerConfig:
        """
        Load worker configuration from environment variables.
        
        Environment variables:
        - PRISMQ_WORKER_ID: Worker ID
        - PRISMQ_WORKER_SCHEDULING_STRATEGY: Scheduling strategy
        - PRISMQ_WORKER_LEASE_DURATION_SECONDS: Lease duration
        - PRISMQ_WORKER_POLL_INTERVAL_SECONDS: Poll interval
        - PRISMQ_WORKER_MAX_RETRIES: Maximum retries
        - PRISMQ_WORKER_CAPABILITIES: JSON string of capabilities
        
        Args:
            prefix: Environment variable prefix
            
        Returns:
            WorkerConfig instance
        """
        config_dict = {}
        
        # Map environment variables to config keys
        env_mappings = {
            f"{prefix}ID": "worker_id",
            f"{prefix}SCHEDULING_STRATEGY": "scheduling_strategy",
            f"{prefix}LEASE_DURATION_SECONDS": "lease_duration_seconds",
            f"{prefix}POLL_INTERVAL_SECONDS": "poll_interval_seconds",
            f"{prefix}MAX_RETRIES": "max_retries",
            f"{prefix}CAPABILITIES": "capabilities",
        }
        
        for env_key, config_key in env_mappings.items():
            value = os.getenv(env_key)
            if value is not None:
                # Parse JSON for capabilities
                if config_key == "capabilities":
                    try:
                        config_dict[config_key] = json.loads(value)
                    except json.JSONDecodeError:
                        raise ValueError(
                            f"Invalid JSON in {env_key}: {value}"
                        )
                # Parse integers
                elif config_key in [
                    "lease_duration_seconds",
                    "poll_interval_seconds",
                    "max_retries"
                ]:
                    try:
                        config_dict[config_key] = int(value)
                    except ValueError:
                        raise ValueError(
                            f"Invalid integer value for {env_key}: {value}"
                        )
                else:
                    config_dict[config_key] = value
        
        return self._create_worker_config(config_dict)
    
    def _apply_env_overrides(
        self,
        config_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.
        
        Environment variables take precedence over file configuration.
        
        Args:
            config_dict: Base configuration dictionary
            
        Returns:
            Updated configuration dictionary
        """
        # Create a copy to avoid modifying original
        config = config_dict.copy()
        
        # Check for environment variable overrides
        prefix = "PRISMQ_WORKER_"
        env_mappings = {
            f"{prefix}ID": "worker_id",
            f"{prefix}SCHEDULING_STRATEGY": "scheduling_strategy",
            f"{prefix}LEASE_DURATION_SECONDS": "lease_duration_seconds",
            f"{prefix}POLL_INTERVAL_SECONDS": "poll_interval_seconds",
            f"{prefix}MAX_RETRIES": "max_retries",
            f"{prefix}CAPABILITIES": "capabilities",
        }
        
        for env_key, config_key in env_mappings.items():
            value = os.getenv(env_key)
            if value is not None:
                # Parse JSON for capabilities
                if config_key == "capabilities":
                    try:
                        config[config_key] = json.loads(value)
                    except json.JSONDecodeError as e:
                        # Log warning but don't fail - keep file config value
                        logger.warning(
                            f"Invalid JSON in environment variable {env_key}: {e}. "
                            f"Ignoring override and using file configuration."
                        )
                # Parse integers
                elif config_key in [
                    "lease_duration_seconds",
                    "poll_interval_seconds",
                    "max_retries"
                ]:
                    try:
                        config[config_key] = int(value)
                    except ValueError as e:
                        # Log warning but don't fail - keep file config value
                        logger.warning(
                            f"Invalid integer in environment variable {env_key}='{value}': {e}. "
                            f"Ignoring override and using file configuration."
                        )
                else:
                    config[config_key] = value
        
        return config
    
    def _create_worker_config(
        self,
        config_dict: Dict[str, Any]
    ) -> WorkerConfig:
        """
        Create WorkerConfig from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            WorkerConfig instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        if "worker_id" not in config_dict:
            raise ValueError("worker_id is required in configuration")
        
        # Parse scheduling strategy
        strategy_str = config_dict.get("scheduling_strategy", "priority")
        try:
            if isinstance(strategy_str, SchedulingStrategy):
                strategy = strategy_str
            else:
                strategy = SchedulingStrategy(strategy_str.lower())
        except ValueError:
            valid_strategies = [s.value for s in SchedulingStrategy]
            raise ValueError(
                f"Invalid scheduling strategy: {strategy_str}. "
                f"Valid strategies: {', '.join(valid_strategies)}"
            )
        
        # Create WorkerConfig
        return WorkerConfig(
            worker_id=config_dict["worker_id"],
            capabilities=config_dict.get("capabilities", {}),
            scheduling_strategy=strategy,
            lease_duration_seconds=config_dict.get("lease_duration_seconds", 60),
            poll_interval_seconds=config_dict.get("poll_interval_seconds", 1),
            max_retries=config_dict.get("max_retries", 3),
        )
    
    def save_to_file(
        self,
        config: WorkerConfig,
        file_path: str,
        indent: int = 2
    ) -> None:
        """
        Save worker configuration to file.
        
        Args:
            config: WorkerConfig instance
            file_path: Path to save configuration
            indent: JSON indentation level
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Convert WorkerConfig to dictionary
        config_dict = {
            "worker_id": config.worker_id,
            "capabilities": config.capabilities,
            "scheduling_strategy": config.scheduling_strategy.value,
            "lease_duration_seconds": config.lease_duration_seconds,
            "poll_interval_seconds": config.poll_interval_seconds,
            "max_retries": config.max_retries,
        }
        
        # Save based on format
        if extension == '.json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=indent)
        elif extension in ['.yaml', '.yml']:
            try:
                import yaml
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config_dict, f, default_flow_style=False)
            except ImportError:
                raise ImportError(
                    "PyYAML is required for YAML configuration. "
                    "Install with: pip install pyyaml"
                )
        elif extension == '.toml':
            try:
                import tomli_w
                with open(path, 'wb') as f:
                    tomli_w.dump(config_dict, f)
            except ImportError:
                raise ImportError(
                    "tomli-w is required for TOML writing. "
                    "Install with: pip install tomli-w"
                )
        else:
            raise ValueError(
                f"Unsupported configuration file format: {extension}"
            )


def load_worker_config(
    file_path: Optional[str] = None,
    apply_env_overrides: bool = True
) -> WorkerConfig:
    """
    Convenience function to load worker configuration.
    
    Args:
        file_path: Path to configuration file (if None, loads from env only)
        apply_env_overrides: Whether to apply environment variable overrides
        
    Returns:
        WorkerConfig instance
        
    Example:
        # Load from file
        config = load_worker_config("worker.json")
        
        # Load from environment only
        config = load_worker_config()
        
        # Load from file without env overrides
        config = load_worker_config("worker.json", apply_env_overrides=False)
    """
    manager = WorkerConfigurationManager()
    
    if file_path is None:
        return manager.load_from_env()
    else:
        return manager.load_from_file(file_path, apply_env_overrides)
