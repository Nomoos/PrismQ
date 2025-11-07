"""
SQLite Queue Module

Production-ready SQLite-based task queue for PrismQ.IdeaInspiration.

Provides foundational database infrastructure for PrismQ task queue
with Windows-optimized configuration and performance settings based on
comprehensive benchmarking (Issue #337).

Main Components:
- QueueDatabase: Connection manager with PRAGMA optimization
- Task, Worker, TaskLog: Data models
- SchedulingStrategy: Enum for task scheduling strategies (Issue #327)
- TaskClaimer classes: FIFO, LIFO, Priority, Weighted Random (Issue #327)
- WorkerConfigurationManager: Configuration loading from files/env (Issue #328)
- QueueMonitoring: Worker heartbeat and observability (Issue #330)
- Custom exceptions for error handling
- Production configuration: Optimized PRAGMA settings from benchmarking
- Observability: TaskLogger, QueueMetrics, WorkerHeartbeat (Issue #329)

Usage:
    # Using the high-level QueueDatabase class
    from Client.Backend.src.queue import QueueDatabase
    
    db = QueueDatabase("C:/Data/PrismQ/queue/queue.db")
    db.initialize_schema()
    
    # Using observability features
    from Client.Backend.src.queue import TaskLogger, QueueMetrics, WorkerHeartbeat
    # Using scheduling strategies
    from Client.Backend.src.queue import (
        SchedulingStrategy,
        TaskClaimerFactory,
    )
    
    claimer = TaskClaimerFactory.create(SchedulingStrategy.PRIORITY, db)
    task = claimer.claim_task("worker-1", {}, 60)
    
    # Or using low-level configuration
    from Client.Backend.src.queue.config import (
        get_default_db_path,
        apply_pragmas,
        MAX_CONCURRENT_WORKERS,
    )
    
    logger = TaskLogger(db)
    logger.log(task_id=123, level="INFO", message="Task started")
    
    metrics = QueueMetrics(db)
    health = metrics.get_queue_health_summary()
    
    heartbeat = WorkerHeartbeat(db)
    heartbeat.update_heartbeat("worker-1", {"type": "classifier"})
"""

# Core infrastructure (Issue #321)
from .database import QueueDatabase
from .models import Task, Worker, TaskLog, SchedulingStrategy, WorkerConfig
from .exceptions import QueueDatabaseError, QueueBusyError, QueueSchemaError
from .schema import PRAGMAS, SCHEMA_STATEMENTS

# Production configuration (Issue #337)
from .config import (
    PRODUCTION_PRAGMAS,
    MAX_CONCURRENT_WORKERS,
    get_default_db_path,
    ensure_db_directory,
    apply_pragmas,
    validate_config,
)

# Observability (Issue #329)
from .logger import TaskLogger, QueueLogger
from .metrics import QueueMetrics
from .heartbeat import WorkerHeartbeat
# Maintenance utilities (Issue #331)
from .backup import QueueBackup, BackupInfo, QueueBackupError
from .maintenance import QueueMaintenance, QueueMaintenanceError
# Scheduling strategies (Issue #327)
from .scheduling import (
    TaskClaimer,
    FIFOTaskClaimer,
    LIFOTaskClaimer,
    PriorityTaskClaimer,
    WeightedRandomTaskClaimer,
    TaskClaimerFactory,
)

# Worker configuration (Issue #328)
from .worker_config import (
    WorkerConfigurationManager,
    load_worker_config,
    JSONConfigLoader,
    YAMLConfigLoader,
    TOMLConfigLoader,
)

# Monitoring and observability (Issue #330)
from .monitoring import QueueMonitoring

# Retry logic and worker engine (Issue #326)
from .worker import (
    RetryConfig,
    TaskExecutor,
    WorkerEngine,
)

# Task handler registry (Worker 10 - Issue #339)
from .task_handler_registry import (
    TaskHandlerRegistry,
    TaskHandlerInfo,
    TaskHandlerNotRegisteredError,
    TaskHandlerAlreadyRegisteredError,
    get_global_registry,
    reset_global_registry,
)

# Task handler configuration loader (Worker 10 - Issue #339)
from .task_handler_config import (
    TaskHandlerConfigLoader,
    HandlerConfigError,
    load_handlers_from_config,
)

# Validation and support tools (Worker 01 Phase 2)
from .validation import (
    QueueValidator,
    quick_validate,
    validate_worker_integration,
)

# Integration utilities (Worker 10 - Issue #339)
from .integration import (
    create_queue_database,
    get_or_create_queue_database,
    create_queued_task_manager,
    migrate_to_queue_system,
    validate_queue_integration,
    ensure_queue_ready,
    QueueIntegrationError,
)

__all__ = [
    # Core infrastructure
    "QueueDatabase",
    "Task",
    "Worker",
    "TaskLog",
    "SchedulingStrategy",
    "WorkerConfig",
    "QueueDatabaseError",
    "QueueBusyError",
    "QueueSchemaError",
    "PRAGMAS",
    "SCHEMA_STATEMENTS",
    # Production configuration
    "PRODUCTION_PRAGMAS",
    "MAX_CONCURRENT_WORKERS",
    "get_default_db_path",
    "ensure_db_directory",
    "apply_pragmas",
    "validate_config",
    # Observability
    "TaskLogger",
    "QueueLogger",
    "QueueMetrics",
    "WorkerHeartbeat",
    # Maintenance utilities
    "QueueBackup",
    "BackupInfo",
    "QueueBackupError",
    "QueueMaintenance",
    "QueueMaintenanceError",
    # Scheduling strategies
    "TaskClaimer",
    "FIFOTaskClaimer",
    "LIFOTaskClaimer",
    "PriorityTaskClaimer",
    "WeightedRandomTaskClaimer",
    "TaskClaimerFactory",
    # Worker configuration
    "WorkerConfigurationManager",
    "load_worker_config",
    "JSONConfigLoader",
    "YAMLConfigLoader",
    "TOMLConfigLoader",
    # Monitoring and observability
    "QueueMonitoring",
    # Retry logic and worker engine
    "RetryConfig",
    "TaskExecutor",
    "WorkerEngine",
    # Task handler registry (Worker 10 - Issue #339)
    "TaskHandlerRegistry",
    "TaskHandlerInfo",
    "TaskHandlerNotRegisteredError",
    "TaskHandlerAlreadyRegisteredError",
    "get_global_registry",
    "reset_global_registry",
    # Task handler configuration (Worker 10 - Issue #339)
    "TaskHandlerConfigLoader",
    "HandlerConfigError",
    "load_handlers_from_config",
    # Validation and support tools
    "QueueValidator",
    "quick_validate",
    "validate_worker_integration",
    # Integration utilities (Worker 10 - Issue #339)
    "create_queue_database",
    "get_or_create_queue_database",
    "create_queued_task_manager",
    "migrate_to_queue_system",
    "validate_queue_integration",
    "ensure_queue_ready",
    "QueueIntegrationError",
]

__version__ = '1.1.0'
