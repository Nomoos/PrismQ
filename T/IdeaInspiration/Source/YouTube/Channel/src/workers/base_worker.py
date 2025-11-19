"""Base worker implementation following SOLID principles."""

import logging
import time
from typing import Optional
from datetime import datetime, timezone
from abc import ABC, abstractmethod

from ..core.config import Config
from ..core.database import Database
from . import Task, TaskResult, TaskStatus, WorkerProtocol

# Import TaskManager API Client for centralized task coordination
try:
    from TaskManager import TaskManagerClient
    _taskmanager_available = True
except ImportError:
    _taskmanager_available = False


logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """Base worker class providing common functionality.
    
    Follows Single Responsibility Principle (SRP):
    - Manages task lifecycle
    - Handles polling and claiming
    - Reports results
    
    Does NOT handle:
    - Specific scraping logic (abstract method)
    - Queue implementation (injected dependency)
    - API integration (separate responsibility)
    
    Follows Dependency Inversion Principle (DIP):
    - Depends on abstractions (Config, Database)
    - Dependencies injected via constructor
    """
    
    def __init__(
        self,
        worker_id: str,
        config: Config,
        results_db: Database,
        task_type_ids: list,
        strategy: str = "LIFO",
        heartbeat_interval: int = 30,
        poll_interval: int = 5,
        max_backoff: int = 60,
        backoff_multiplier: float = 1.5,
    ):
        """Initialize worker with injected dependencies (DIP).
        
        Args:
            worker_id: Unique worker identifier
            config: Configuration object
            results_db: Database for storing results
            task_type_ids: List of task type IDs to claim from TaskManager API (required)
            strategy: Task claiming strategy (FIFO, LIFO, PRIORITY)
            heartbeat_interval: Seconds between heartbeats
            poll_interval: Base polling interval in seconds (default 5)
            max_backoff: Maximum backoff time in seconds (default 60)
            backoff_multiplier: Backoff multiplier for exponential backoff (default 1.5)
        """
        self.worker_id = worker_id
        self.config = config
        self.results_db = results_db
        self.strategy = strategy
        self.heartbeat_interval = heartbeat_interval
        self.poll_interval = poll_interval
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self.task_type_ids = task_type_ids
        
        # State
        self.running = False
        self.current_task: Optional[Task] = None
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.last_heartbeat = time.time()
        
        # Backoff state
        self._current_backoff = poll_interval
        
        # TaskManager API client (only mode)
        if not _taskmanager_available:
            raise ImportError(
                "TaskManager module is required. "
                "Install with: pip install -e Source/TaskManager"
            )
        if not task_type_ids:
            raise ValueError(
                "task_type_ids is required. "
                "Register task types and provide their IDs."
            )
        
        try:
            self.taskmanager_client = TaskManagerClient()
            logger.info(f"TaskManager API client initialized for worker {worker_id}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize TaskManager client: {e}. "
                "Check TASKMANAGER_API_URL and TASKMANAGER_API_KEY configuration."
            ) from e
        
        logger.info(
            f"Worker {self.worker_id} initialized "
            f"(strategy: {self.strategy}, poll_interval: {poll_interval}s, "
            f"max_backoff: {max_backoff}s)"
        )
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from TaskManager API.
        
        Returns:
            Task if available and claimed, None otherwise
        """
        try:
            # Configure sort parameters based on claiming policy
            if self.strategy == "FIFO":
                sort_by = "created_at"
                sort_order = "ASC"  # Oldest first
            elif self.strategy == "LIFO":
                sort_by = "created_at"
                sort_order = "DESC"  # Newest first
            elif self.strategy == "PRIORITY":
                sort_by = "priority"
                sort_order = "DESC"  # Highest priority first
            else:
                # Default to LIFO
                logger.warning(f"Unknown strategy '{self.strategy}', falling back to LIFO")
                sort_by = "created_at"
                sort_order = "DESC"
            
            # Try to claim from each registered task type
            from TaskManager import ResourceNotFoundError
            
            for task_type_id in self.task_type_ids:
                try:
                    claimed_task = self.taskmanager_client.claim_task(
                        worker_id=self.worker_id,
                        task_type_id=task_type_id,
                        sort_by=sort_by,
                        sort_order=sort_order
                    )
                    
                    # Convert API response to Task object
                    task = Task(
                        id=claimed_task['id'],
                        task_type=claimed_task['type'],
                        parameters=claimed_task.get('params', {}),
                        priority=claimed_task.get('priority', 5),
                        status=TaskStatus.CLAIMED,
                        retry_count=claimed_task.get('attempts', 0),
                        max_retries=claimed_task.get('max_attempts', 3),
                        created_at=claimed_task.get('created_at', ''),
                        claimed_at=claimed_task.get('claimed_at', '')
                    )
                    
                    self.current_task = task
                    
                    # Reset backoff on successful claim
                    self._current_backoff = self.poll_interval
                    
                    logger.info(
                        f"Worker {self.worker_id} claimed task {task.id} from TaskManager API "
                        f"(type: {task.task_type}, task_type_id: {task_type_id})"
                    )
                    return task
                    
                except ResourceNotFoundError:
                    # No tasks available for this type, try next
                    continue
                except Exception as e:
                    logger.error(f"Error claiming task from TaskManager API (type_id {task_type_id}): {e}")
                    continue
            
            # No tasks available from any type
            return None
            
        except Exception as e:
            logger.error(f"Error claiming task from TaskManager API: {e}")
            return None
    
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        """Process a claimed task - MUST be implemented by subclass.
        
        This is where the actual scraping logic goes.
        Subclasses implement specific scraping behavior.
        
        Args:
            task: The task to process
            
        Returns:
            TaskResult with success status and data
        """
        pass
    
    def report_result(self, task: Task, result: TaskResult) -> None:
        """Report task result to TaskManager API and save data to IdeaInspiration.
        
        Updates:
        1. TaskManager API with completion status
        2. Results database (IdeaInspiration)
        
        Args:
            task: The completed task
            result: The execution result
        """
        try:
            # Update statistics
            if result.success:
                self.tasks_processed += 1
            else:
                self.tasks_failed += 1
            
            # Report to TaskManager API
            self._update_task_manager(task, result)
            
            # Save results to IdeaInspiration database if successful
            if result.success and result.data:
                self._save_results(task, result)
            
            status = "completed" if result.success else "failed"
            logger.info(
                f"Worker {self.worker_id} completed task {task.id} via TaskManager API "
                f"(status: {status}, items: {result.items_processed})"
            )
            
        except Exception as e:
            logger.error(f"Error reporting result: {e}")
    
    def _save_results(self, task: Task, result: TaskResult) -> None:
        """Save results to IdeaInspiration database - to be customized by subclass."""
        # Default implementation - can be overridden
        pass
    
    def _update_task_manager(self, task: Task, result: TaskResult) -> None:
        """Update TaskManager API with task completion status.
        
        Args:
            task: The completed task
            result: The execution result
        """
        try:
            # Prepare result data for TaskManager API
            result_data = None
            if result.success and result.data:
                result_data = {
                    "items_processed": result.items_processed,
                    "data_summary": {
                        # Include key metrics but not full data payload
                        "total_items": result.items_processed,
                        "processed_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            
            # Report completion to TaskManager API
            self.taskmanager_client.complete_task(
                task_id=task.id,
                worker_id=self.worker_id,
                success=result.success,
                result=result_data,
                error=result.error
            )
            
            logger.debug(
                f"Task {task.id} status reported to TaskManager API "
                f"(success: {result.success})"
            )
            
        except Exception as e:
            # Log error but don't fail the task - TaskManager reporting is optional
            logger.warning(
                f"Failed to report task {task.id} to TaskManager API: {e}. "
                "Task completed locally but not synced to central system."
            )
    
    def run_once(self) -> bool:
        """Execute one iteration of the worker loop.
        
        Returns:
            True if a task was processed, False otherwise
        """
        # Try to claim a task
        task = self.claim_task()
        if not task:
            return False
        
        try:
            # Process the task
            result = self.process_task(task)
            
            # Report the result
            self.report_result(task, result)
            
            return True
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing task {task.id}: {e}")
            result = TaskResult(
                success=False,
                error=str(e)
            )
            self.report_result(task, result)
            return False
        
        finally:
            self.current_task = None
    
    def run(self, poll_interval: int = None, max_iterations: Optional[int] = None):
        """Run the worker loop with exponential backoff for empty queue.
        
        Args:
            poll_interval: Seconds to wait between polls (defaults to self.poll_interval)
            max_iterations: Maximum iterations (None = infinite)
        """
        # Use instance poll_interval if not overridden
        if poll_interval is None:
            poll_interval = self.poll_interval
            
        self.running = True
        iteration = 0
        
        logger.info(f"Worker {self.worker_id} starting...")
        
        try:
            while self.running:
                # Check iteration limit
                if max_iterations and iteration >= max_iterations:
                    break
                
                # Process one task
                processed = self.run_once()
                
                # Wait if no task was available with exponential backoff
                if not processed:
                    logger.debug(
                        f"Worker {self.worker_id} no task available, "
                        f"backing off for {self._current_backoff}s"
                    )
                    time.sleep(self._current_backoff)
                    self._increase_backoff()
                
                iteration += 1
                
        except KeyboardInterrupt:
            logger.info(f"Worker {self.worker_id} interrupted")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the worker gracefully."""
        self.running = False
        logger.info(
            f"Worker {self.worker_id} stopped "
            f"(processed: {self.tasks_processed}, failed: {self.tasks_failed})"
        )
    
    def _increase_backoff(self) -> None:
        """Increase backoff time exponentially up to max_backoff.
        
        This implements exponential backoff to reduce CPU usage when
        the queue is empty. The backoff time starts at poll_interval
        and increases by backoff_multiplier each time, capped at max_backoff.
        """
        self._current_backoff = min(
            self._current_backoff * self.backoff_multiplier,
            self.max_backoff
        )
        logger.debug(
            f"Worker {self.worker_id} increased backoff to {self._current_backoff:.1f}s "
            f"(max: {self.max_backoff}s)"
        )


__all__ = ["BaseWorker"]
