"""Core functionality initialization."""

from .config_storage import ConfigStorage
from pathlib import Path

from .module_runner import ModuleRunner
from .output_capture import OutputCapture
from .process_manager import ProcessManager, ProcessResult
from .resource_manager import ResourceManager
from .run_registry import RunRegistry
from .task_manager import BackgroundTaskManager
from .task_orchestrator import TaskOrchestrator, PatternAdvisor, TaskPattern
from .config import settings
from .exceptions import (
    WebClientException,
    ModuleNotFoundException,
    ModuleExecutionException,
    ResourceLimitException,
    ValidationException,
    RunNotFoundException,
    ConfigurationException,
)
from .resource_pool import (
    ResourcePool,
    get_resource_pool,
    initialize_resource_pool,
    initialize_resource_pool_async,
    cleanup_resource_pool,
)

# Global singletons for dependency injection
_config_storage: ConfigStorage = None
_process_manager: ProcessManager = None
_resource_manager: ResourceManager = None
_run_registry: RunRegistry = None
_module_runner: ModuleRunner = None
_output_capture: OutputCapture = None


def get_config_storage() -> ConfigStorage:
    """Get or create the global ConfigStorage instance."""
    global _config_storage
    if _config_storage is None:
        _config_storage = ConfigStorage(settings.get_config_dir())
    return _config_storage


def get_process_manager() -> ProcessManager:
    """Get or create the global ProcessManager instance."""
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
    return _process_manager


def get_run_registry() -> RunRegistry:
    """Get or create the global RunRegistry instance."""
    global _run_registry
    if _run_registry is None:
        _run_registry = RunRegistry()
    return _run_registry


def get_output_capture() -> OutputCapture:
    """Get or create the global OutputCapture instance."""
    global _output_capture
    if _output_capture is None:
        # Create logs directory in Backend/data/logs
        log_dir = Path(__file__).parent.parent.parent / "data" / "logs"
        _output_capture = OutputCapture(log_dir=log_dir)
    return _output_capture


def get_resource_manager() -> ResourceManager:
    """Get or create the global ResourceManager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


def get_module_runner() -> ModuleRunner:
    """Get or create the global ModuleRunner instance."""
    global _module_runner
    if _module_runner is None:
        _module_runner = ModuleRunner(
            registry=get_run_registry(),
            process_manager=get_process_manager(),
            config_storage=get_config_storage(),
            output_capture=get_output_capture(),
            resource_manager=get_resource_manager()
        )
    return _module_runner


def reset_singletons():
    """Reset all singleton instances. For testing only."""
    global _config_storage, _process_manager, _resource_manager, _run_registry, _module_runner, _output_capture
    _config_storage = None
    _process_manager = None
    _resource_manager = None
    _run_registry = None
    _module_runner = None
    _output_capture = None


__all__ = [
    "BackgroundTaskManager",
    "ConfigStorage",
    "ModuleRunner",
    "OutputCapture",
    "PatternAdvisor",
    "ProcessManager",
    "ProcessResult",
    "ResourceManager",
    "ResourcePool",
    "RunRegistry",
    "TaskOrchestrator",
    "TaskPattern",
    "get_config_storage",
    "get_module_runner",
    "get_output_capture",
    "get_process_manager",
    "get_resource_manager",
    "get_resource_pool",
    "get_run_registry",
    "initialize_resource_pool",
    "initialize_resource_pool_async",
    "cleanup_resource_pool",
    "reset_singletons",
    "WebClientException",
    "ModuleNotFoundException",
    "ModuleExecutionException",
    "ResourceLimitException",
    "ValidationException",
    "RunNotFoundException",
    "ConfigurationException",
]
