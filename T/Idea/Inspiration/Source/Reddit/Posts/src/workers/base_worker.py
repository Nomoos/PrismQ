"""Base worker implementation using pure TaskManager API pattern.

This worker uses ONLY the TaskManager REST API for task queue management.
No local SQLite queue is used - all task operations go through the external API.

Following SOLID principles:
- Single Responsibility: Manages task lifecycle via TaskManager API
- Dependency Inversion: Depends on abstractions (TaskManagerClient, Config)
- Interface Segregation: Minimal interface for workers
"""

import logging
import time
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from abc import ABC, abstractmethod

# Add parent directory to path for imports
_src_path = Path(__file__).resolve().parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from core.config import Config

# Import TaskManager client
try:
    # Add TaskManager to path
    _taskmanager_path = Path(__file__).resolve().parents[5] / 'TaskManager'
    if str(_taskmanager_path) not in sys.path:
        sys.path.insert(0, str(_taskmanager_path))
    
    from src.client import TaskManagerClient, ResourceNotFoundError
    _taskmanager_available = True
except ImportError:
    _taskmanager_available = False
    TaskManagerClient = None
    ResourceNotFoundError = Exception


logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """Base worker class using TaskManager API for task queue management.
    
    Architecture:
        Worker → TaskManagerClient → External TaskManager API
               ↓
        IdeaInspiration Database (for results only)
    
    Responsibilities:
    - Register task types with TaskManager API
    - Poll API for available tasks
    - Claim tasks using configured policy
    - Process tasks (implemented by subclass)
    - Save results to IdeaInspiration database
    - Report completion to TaskManager API
    
    Does NOT:
    - Manage local task queue (TaskManager API handles this)
    - Store tasks locally (TaskManager API handles this)
    """
    
    def __init__(
        self,
        worker_id: str,
        config: Config,
        claiming_policy: str = "FIFO",
        poll_interval: int = 5,
        max_backoff: int = 60,
        backoff_multiplier: float = 1.5,
    ):
        """Initialize worker with TaskManager API integration.
        
        Args:
            worker_id: Unique worker identifier
            config: Configuration object
            claiming_policy: Task claiming strategy - "FIFO", "LIFO", or "PRIORITY"
            poll_interval: Base polling interval in seconds (default: 5)
            max_backoff: Maximum backoff time in seconds (default: 60)
            backoff_multiplier: Backoff multiplier for exponential backoff (default: 1.5)
            
        Raises:
            RuntimeError: If TaskManager client is not available
        """
        if not _taskmanager_available:
            raise RuntimeError(
                "TaskManager client not available. "
                "Cannot initialize worker without TaskManager API."
            )
        
        self.worker_id = worker_id
        self.config = config
        self.claiming_policy = claiming_policy
        self.poll_interval = poll_interval
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        
        # Initialize TaskManager client
        self.taskmanager_client = TaskManagerClient()
        
        # Task type IDs (populated during registration)
        self.task_type_ids: List[int] = []
        
        # State
        self.running = False
        self.current_task: Optional[Dict] = None
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.start_time = time.time()
        
        # Backoff state
        self._current_backoff = poll_interval
        
        logger.info(
            f"Worker {worker_id} initialized with TaskManager API "
            f"(policy: {claiming_policy}, poll: {poll_interval}s)"
        )
    
    def register_task_types(self) -> None:
        """
        Register task types with TaskManager API.
        
        Subclasses should override this to register their specific task types.
        Each task type should be registered and its ID stored in self.task_type_ids.
        
        Example:
            result = self.taskmanager_client.register_task_type(
                name="PrismQ.Text.Reddit.Post.Subreddit",
                version="1.0.0",
                param_schema={...}
            )
            self.task_type_ids.append(result['id'])
        """
        pass
    
    def claim_task(self) -> Optional[Dict]:
        """
        Claim a task from TaskManager API using configured policy.
        
        Tries to claim tasks from registered task types in order.
        Uses claiming policy to determine sort order.
        
        Returns:
            Claimed task dictionary or None if no tasks available
        """
        # Configure sort parameters based on claiming policy
        if self.claiming_policy == "FIFO":
            sort_by = "created_at"
            sort_order = "ASC"  # Oldest first
        elif self.claiming_policy == "LIFO":
            sort_by = "created_at"
            sort_order = "DESC"  # Newest first
        elif self.claiming_policy == "PRIORITY":
            sort_by = "priority"
            sort_order = "DESC"  # Highest priority first
        else:
            # Default to FIFO
            sort_by = "created_at"
            sort_order = "ASC"
        
        # Try to claim from each registered task type
        for task_type_id in self.task_type_ids:
            try:
                task = self.taskmanager_client.claim_task(
                    worker_id=self.worker_id,
                    task_type_id=task_type_id,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                
                self.current_task = task
                
                # Reset backoff on successful claim
                self._current_backoff = self.poll_interval
                
                logger.info(
                    f"Worker {self.worker_id} claimed task {task['id']} "
                    f"(type: {task.get('type')}, task_type_id: {task_type_id})"
                )
                return task
                
            except ResourceNotFoundError:
                # No tasks available for this type, try next
                continue
            except Exception as e:
                logger.error(f"Error claiming task from type {task_type_id}: {e}")
                continue
        
        # No tasks available from any type
        return None
    
    @abstractmethod
    def process_task(self, task: Dict) -> Dict:
        """
        Process a claimed task - MUST be implemented by subclass.
        
        This is where the actual scraping/processing logic goes.
        Results should be saved to IdeaInspiration database.
        
        Args:
            task: The task to process (from TaskManager API)
            
        Returns:
            Processing result with:
                - success: bool
                - idea_inspiration_id: ID of saved idea (if successful)
                - processed_at: timestamp
                - items_processed: int
                - error: str (if failed)
        
        Example:
            return {
                "success": True,
                "idea_inspiration_id": idea_id,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "items_processed": 1
            }
        """
        pass
    
    def complete_task(self, task: Dict, result: Dict) -> None:
        """
        Report task completion to TaskManager API.
        
        Args:
            task: The task that was processed
            result: Processing result from process_task()
        """
        try:
            if result.get('success'):
                # Success case: include IdeaInspiration ID
                self.taskmanager_client.complete_task(
                    task_id=task['id'],
                    worker_id=self.worker_id,
                    success=True,
                    result={
                        "idea_inspiration_id": result.get('idea_inspiration_id'),
                        "processed_at": result.get('processed_at'),
                        "items_processed": result.get('items_processed', 1)
                    }
                )
                self.tasks_processed += 1
                logger.info(
                    f"Task {task['id']} completed successfully "
                    f"(IdeaInspiration ID: {result.get('idea_inspiration_id')})"
                )
            else:
                # Failure case: include error message
                self.taskmanager_client.complete_task(
                    task_id=task['id'],
                    worker_id=self.worker_id,
                    success=False,
                    error=result.get('error', 'Unknown error')
                )
                self.tasks_failed += 1
                logger.error(
                    f"Task {task['id']} failed: {result.get('error')}"
                )
        
        except Exception as e:
            logger.error(f"Error completing task {task['id']}: {e}")
            raise
    
    def run_once(self) -> bool:
        """
        Execute one iteration of the worker loop.
        
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
            self.complete_task(task, result)
            
            return True
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error processing task {task['id']}: {e}", exc_info=True)
            result = {
                'success': False,
                'error': str(e)
            }
            self.complete_task(task, result)
            return False
        
        finally:
            self.current_task = None
    
    def run(self, max_iterations: Optional[int] = None):
        """
        Run the worker loop with exponential backoff for empty queue.
        
        Steps:
        1. Register task types on startup
        2. Poll for tasks continuously
        3. Process tasks as they become available
        4. Wait with exponential backoff when no tasks available
        
        Args:
            max_iterations: Maximum iterations (None = infinite)
        """
        # Register task types on startup
        self.register_task_types()
        
        if not self.task_type_ids:
            logger.error("No task types registered. Worker cannot run.")
            return
        
        logger.info(
            f"Worker {self.worker_id} started - registered {len(self.task_type_ids)} task types"
        )
        
        self.running = True
        iteration = 0
        
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
                        f"waiting {self._current_backoff:.1f}s"
                    )
                    time.sleep(self._current_backoff)
                    self._increase_backoff()
                
                iteration += 1
                
                # Log progress periodically
                if (self.tasks_processed + self.tasks_failed) % 10 == 0 and (self.tasks_processed + self.tasks_failed) > 0:
                    self._log_statistics()
        
        except KeyboardInterrupt:
            logger.info(f"Worker {self.worker_id} interrupted")
            self._log_statistics()
        
        except Exception as e:
            logger.error(f"Fatal error in worker: {e}", exc_info=True)
            self._log_statistics()
            raise
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the worker gracefully."""
        self.running = False
        self._log_statistics()
        logger.info(f"Worker {self.worker_id} stopped")
    
    def _increase_backoff(self) -> None:
        """Increase backoff time exponentially up to max_backoff."""
        self._current_backoff = min(
            self._current_backoff * self.backoff_multiplier,
            self.max_backoff
        )
    
    def _log_statistics(self) -> None:
        """Log worker statistics."""
        uptime = time.time() - self.start_time
        total_tasks = self.tasks_processed + self.tasks_failed
        success_rate = (
            (self.tasks_processed / total_tasks * 100)
            if total_tasks > 0
            else 0
        )
        
        logger.info(
            f"Worker statistics: "
            f"processed={self.tasks_processed}, "
            f"failed={self.tasks_failed}, "
            f"success_rate={success_rate:.1f}%, "
            f"uptime={uptime:.0f}s"
        )


__all__ = ["BaseWorker"]
