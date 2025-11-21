"""Base worker implementation following SOLID principles and Template Method pattern.

This module provides the foundational worker class that all source workers inherit from.
It implements the Template Method pattern where the algorithm structure is defined here,
but specific steps are implemented by subclasses.

Design Pattern: Template Method Pattern
Reference: https://refactoring.guru/design-patterns/template-method

Hierarchy:
    BaseWorker (this class)
      ↓
    BaseSourceWorker (for specific source types: Text, Video, Audio)
      ↓
    Platform-Specific Workers (YouTube, Reddit, etc.)
      ↓
    Endpoint-Specific Workers (YouTubeVideo, RedditPosts, etc.)

Follows SOLID principles:
- Single Responsibility: Manages task lifecycle and worker state
- Open/Closed: Open for extension via inheritance, closed for modification
- Liskov Substitution: All workers can substitute this base class
- Interface Segregation: Focused interface for worker operations
- Dependency Inversion: Depends on abstractions (TaskManagerClient)
"""

import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from abc import ABC, abstractmethod

# Import TaskManager API Client for centralized task coordination
try:
    from TaskManager import TaskManagerClient
    _taskmanager_available = True
except ImportError:
    _taskmanager_available = False


logger = logging.getLogger(__name__)


class Task:
    """Represents a task to be processed by a worker."""
    
    def __init__(
        self,
        id: str,
        task_type: str,
        parameters: Dict[str, Any],
        priority: int = 5,
        status: str = "pending",
        retry_count: int = 0,
        max_retries: int = 3,
        created_at: str = "",
        claimed_at: str = ""
    ):
        self.id = id
        self.task_type = task_type
        self.parameters = parameters
        self.priority = priority
        self.status = status
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.created_at = created_at
        self.claimed_at = claimed_at


class TaskResult:
    """Represents the result of processing a task."""
    
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        items_processed: int = 0,
        metrics: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data
        self.error = error
        self.items_processed = items_processed
        self.metrics = metrics or {}


class BaseWorker(ABC):
    """Base worker class providing common functionality for all workers.
    
    This class implements the Template Method pattern where the overall
    algorithm for task processing is defined here, but specific steps
    are left abstract for subclasses to implement.
    
    Template Methods (define the algorithm):
    - run(): Main worker loop
    - run_once(): Single task processing iteration
    - claim_task(): Task claiming logic
    - report_result(): Result reporting logic
    
    Hook Methods (can be overridden):
    - _save_results(): Custom result storage
    - _update_task_manager(): TaskManager updates
    - _increase_backoff(): Backoff strategy
    
    Abstract Methods (must be implemented):
    - process_task(): Actual task processing logic
    
    Attributes:
        worker_id: Unique worker identifier
        task_type_ids: List of task type IDs this worker can handle
        strategy: Task claiming strategy (FIFO, LIFO, PRIORITY)
        poll_interval: Seconds between polls for new tasks
        max_backoff: Maximum backoff time in seconds
        backoff_multiplier: Multiplier for exponential backoff
        running: Whether worker is currently running
        tasks_processed: Count of successfully processed tasks
        tasks_failed: Count of failed tasks
    
    Example:
        >>> class MyWorker(BaseWorker):
        ...     def process_task(self, task: Task) -> TaskResult:
        ...         # Process the task
        ...         return TaskResult(success=True, items_processed=1)
        >>> 
        >>> worker = MyWorker(
        ...     worker_id="my-worker-01",
        ...     task_type_ids=["my-task-type"]
        ... )
        >>> worker.run(max_iterations=1)
    """
    
    def __init__(
        self,
        worker_id: str,
        task_type_ids: list,
        strategy: str = "LIFO",
        heartbeat_interval: int = 30,
        poll_interval: int = 5,
        max_backoff: int = 60,
        backoff_multiplier: float = 1.5,
        **kwargs
    ):
        """Initialize base worker with common configuration.
        
        Args:
            worker_id: Unique worker identifier
            task_type_ids: List of task type IDs to claim from TaskManager API
            strategy: Task claiming strategy (FIFO, LIFO, PRIORITY)
            heartbeat_interval: Seconds between heartbeats
            poll_interval: Base polling interval in seconds
            max_backoff: Maximum backoff time in seconds
            backoff_multiplier: Backoff multiplier for exponential backoff
            **kwargs: Additional configuration for subclasses
        """
        self.worker_id = worker_id
        self.task_type_ids = task_type_ids
        self.strategy = strategy
        self.heartbeat_interval = heartbeat_interval
        self.poll_interval = poll_interval
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        
        # Store additional kwargs for subclasses
        self._kwargs = kwargs
        
        # State
        self.running = False
        self.current_task: Optional[Task] = None
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.last_heartbeat = time.time()
        
        # Backoff state
        self._current_backoff = poll_interval
        
        # TaskManager API client
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
        """Claim a task from TaskManager API using configured strategy.
        
        This is a template method that defines the task claiming algorithm.
        Subclasses can override specific parts if needed.
        
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
                        status="claimed",
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
        
        This is the core abstract method that subclasses must implement.
        This is where the actual work happens (scraping, processing, etc.).
        
        Args:
            task: The task to process
            
        Returns:
            TaskResult with success status and data
            
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        pass
    
    def report_result(self, task: Task, result: TaskResult) -> None:
        """Report task result to TaskManager API and save data.
        
        This is a template method that orchestrates result reporting.
        It calls hook methods that subclasses can override.
        
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
            
            # Save results if successful
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
        """Save results to storage - Hook method for subclasses.
        
        Subclasses can override this to implement custom result storage.
        Default implementation does nothing.
        
        Args:
            task: The completed task
            result: The task execution result
        """
        # Default implementation - subclasses can override
        pass
    
    def _update_task_manager(self, task: Task, result: TaskResult) -> None:
        """Update TaskManager API with task completion status - Hook method.
        
        Subclasses can override this to customize TaskManager updates.
        
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
            # Log error but don't fail the task
            logger.warning(
                f"Failed to report task {task.id} to TaskManager API: {e}. "
                "Task completed locally but not synced to central system."
            )
    
    def run_once(self) -> bool:
        """Execute one iteration of the worker loop - Template Method.
        
        This method defines the algorithm for processing a single task:
        1. Claim a task
        2. Process it
        3. Report results
        
        Returns:
            True if a task was processed, False otherwise
        """
        # Try to claim a task
        task = self.claim_task()
        if not task:
            return False
        
        try:
            # Process the task (calls abstract method)
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
        """Run the worker loop with exponential backoff - Template Method.
        
        This is the main entry point for running the worker. It implements
        the overall algorithm for continuous task processing with backoff.
        
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
    
    def _increase_backoff(self):
        """Increase the backoff time exponentially - Hook method."""
        self._current_backoff = min(
            self._current_backoff * self.backoff_multiplier,
            self.max_backoff
        )
        logger.debug(
            f"Worker {self.worker_id} increased backoff to {self._current_backoff:.1f}s "
            f"(max: {self.max_backoff}s)"
        )


__all__ = ["BaseWorker", "Task", "TaskResult"]
