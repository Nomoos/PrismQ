"""
PrismQ.Client.Worker.Model

Worker model components for PrismQ task queue system.
This module contains worker-related database definitions and worker engine functionality.

Part of the separation of concerns for:
- Frontend: Vue 3 UI
- Backend.API: FastAPI REST endpoints  
- Backend.Worker.Model: Worker processes and database operations

Worker 10 - Issue #339: Move worker DB definition into Worker.Model
"""

__version__ = "1.0.0"

# Re-export worker components for convenience
from ..queue.worker import (
    RetryConfig,
    TaskExecutor,
    WorkerEngine,
)

from ..queue.task_handler_registry import (
    TaskHandlerRegistry,
    TaskHandlerInfo,
    TaskHandlerNotRegisteredError,
    TaskHandlerAlreadyRegisteredError,
    get_global_registry,
    reset_global_registry,
)

from ..queue.task_handler_config import (
    TaskHandlerConfigLoader,
    HandlerConfigError,
    load_handlers_from_config,
)

from ..queue.worker_config import (
    WorkerConfigurationManager,
    load_worker_config,
    JSONConfigLoader,
    YAMLConfigLoader,
    TOMLConfigLoader,
)

from ..queue.models import (
    Worker,
    WorkerConfig,
)

from ..queue.database import QueueDatabase
from ..queue.scheduling import TaskClaimerFactory, SchedulingStrategy
from ..queue.heartbeat import WorkerHeartbeat
from ..queue.monitoring import QueueMonitoring

# Worker database module
from .worker_db import (
    WorkerDatabase,
    create_worker_from_config,
)

__all__ = [
    # Worker database
    "WorkerDatabase",
    "create_worker_from_config",
    # Worker engine components
    "RetryConfig",
    "TaskExecutor",
    "WorkerEngine",
    # Task handler registry
    "TaskHandlerRegistry",
    "TaskHandlerInfo",
    "TaskHandlerNotRegisteredError",
    "TaskHandlerAlreadyRegisteredError",
    "get_global_registry",
    "reset_global_registry",
    # Task handler configuration
    "TaskHandlerConfigLoader",
    "HandlerConfigError",
    "load_handlers_from_config",
    # Worker configuration
    "WorkerConfigurationManager",
    "load_worker_config",
    "JSONConfigLoader",
    "YAMLConfigLoader",
    "TOMLConfigLoader",
    # Models
    "Worker",
    "WorkerConfig",
    # Database
    "QueueDatabase",
    # Scheduling
    "TaskClaimerFactory",
    "SchedulingStrategy",
    # Monitoring
    "WorkerHeartbeat",
    "QueueMonitoring",
]
