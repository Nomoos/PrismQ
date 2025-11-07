"""
Worker Database Module

Encapsulates worker-specific database operations and definitions.
Separates worker concerns from the general queue API.

Part of PrismQ.Client.Worker.Model - Worker 10 Issue #339
"""

from typing import Optional, Dict, Any
import logging

from ..queue.database import QueueDatabase
from ..queue.models import Task, Worker, WorkerConfig
from ..queue.scheduling import TaskClaimerFactory, SchedulingStrategy
from ..queue.worker import WorkerEngine, TaskExecutor
from ..queue.task_handler_registry import TaskHandlerRegistry
from ..queue.heartbeat import WorkerHeartbeat

logger = logging.getLogger(__name__)


class WorkerDatabase:
    """
    Worker-specific database operations.
    
    Provides a focused interface for worker processes to interact with
    the queue database without exposing the full API surface.
    
    This class is designed for use by worker processes and separates
    worker concerns from the API layer.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize worker database.
        
        Args:
            db_path: Path to SQLite database. If None, uses default path.
        """
        self.db = QueueDatabase(db_path)
        self.db.initialize_schema()
        logger.info(f"Worker database initialized: {db_path or 'default'}")
    
    def create_worker(
        self,
        worker_id: str,
        config: Optional[WorkerConfig] = None,
        handler_registry: Optional[TaskHandlerRegistry] = None
    ) -> WorkerEngine:
        """
        Create a worker engine instance.
        
        Args:
            worker_id: Unique identifier for this worker
            config: Optional worker configuration
            handler_registry: Optional task handler registry
            
        Returns:
            Configured WorkerEngine instance
        """
        if config is None:
            config = WorkerConfig(worker_id=worker_id)
        
        worker = WorkerEngine(
            db=self.db,
            worker_id=worker_id,
            capabilities=config.capabilities,
            scheduling_strategy=config.scheduling_strategy,
            lease_seconds=config.lease_duration_seconds,
            poll_interval_seconds=config.poll_interval_seconds,
            handler_registry=handler_registry
        )
        
        logger.info(
            f"Created worker '{worker_id}' with strategy {config.scheduling_strategy}"
        )
        
        return worker
    
    def register_worker_heartbeat(
        self,
        worker_id: str,
        capabilities: Dict[str, Any] = None
    ) -> None:
        """
        Register worker with heartbeat system.
        
        Args:
            worker_id: Worker identifier
            capabilities: Worker capabilities dict
        """
        heartbeat = WorkerHeartbeat(self.db)
        heartbeat.update_heartbeat(worker_id, capabilities or {})
        logger.info(f"Registered heartbeat for worker '{worker_id}'")
    
    def claim_task(
        self,
        worker_id: str,
        capabilities: Dict[str, Any],
        lease_seconds: int,
        strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY
    ) -> Optional[Task]:
        """
        Claim a task using specified strategy.
        
        Args:
            worker_id: Worker identifier
            capabilities: Worker capabilities for task matching
            lease_seconds: Duration to lease the task
            strategy: Scheduling strategy to use
            
        Returns:
            Claimed Task or None if no tasks available
        """
        claimer = TaskClaimerFactory.create(strategy, self.db)
        task = claimer.claim_task(worker_id, capabilities, lease_seconds)
        
        if task:
            logger.info(
                f"Worker '{worker_id}' claimed task #{task.id} "
                f"(type: {task.type}, strategy: {strategy})"
            )
        
        return task
    
    def get_executor(self) -> TaskExecutor:
        """
        Get a task executor for completing/failing tasks.
        
        Returns:
            TaskExecutor instance
        """
        return TaskExecutor(self.db)
    
    def get_worker_stats(self, worker_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific worker.
        
        Args:
            worker_id: Worker identifier
            
        Returns:
            Dictionary with worker statistics
        """
        cursor = self.db.execute(
            """
            SELECT
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'leased' THEN 1 ELSE 0 END) as in_progress
            FROM task_queue
            WHERE locked_by = ?
            """,
            (worker_id,)
        )
        
        row = cursor.fetchone()
        stats = dict(row) if row else {}
        
        return {
            "worker_id": worker_id,
            "total_tasks": stats.get("total_tasks", 0),
            "completed_tasks": stats.get("completed", 0),
            "failed_tasks": stats.get("failed", 0),
            "in_progress_tasks": stats.get("in_progress", 0),
        }
    
    def close(self) -> None:
        """Close the database connection."""
        self.db.close()
        logger.info("Worker database closed")


def create_worker_from_config(
    worker_id: str,
    config_path: str,
    handler_registry: Optional[TaskHandlerRegistry] = None,
    db_path: Optional[str] = None
) -> WorkerEngine:
    """
    Create a worker from configuration file.
    
    Convenience function to create a fully configured worker from
    a configuration file.
    
    Args:
        worker_id: Unique worker identifier
        config_path: Path to worker configuration file (JSON/YAML/TOML)
        handler_registry: Optional task handler registry
        db_path: Optional database path
        
    Returns:
        Configured WorkerEngine instance
        
    Example:
        >>> worker = create_worker_from_config(
        ...     "worker-01",
        ...     "config/worker.json",
        ...     handler_registry=registry
        ... )
        >>> worker.run_loop()
    """
    from ..queue.worker_config import load_worker_config
    
    # Load configuration
    config = load_worker_config(config_path)
    
    # Create worker database
    worker_db = WorkerDatabase(db_path)
    
    # Create and return worker
    return worker_db.create_worker(worker_id, config, handler_registry)
