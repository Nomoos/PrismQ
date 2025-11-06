"""Background task manager for fire-and-forget task execution with tracking."""

import asyncio
import logging
from typing import Dict, List, Awaitable, Optional

from ..models.run import Run, RunStatus
from .run_registry import RunRegistry

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """
    Manage fire-and-forget background tasks with status tracking.
    
    This class implements Pattern 4 from BACKGROUND_TASKS_BEST_PRACTICES.md,
    providing a clean interface for launching background tasks without waiting
    for completion while maintaining automatic status tracking via RunRegistry.
    
    Key Features:
    - Fire-and-forget task execution
    - Automatic status updates (queued -> running -> completed/failed/cancelled)
    - Task cancellation support
    - Graceful shutdown with wait_all
    - Exception handling with status propagation
    
    This class follows SOLID principles:
    - Single Responsibility: Manages background task lifecycle only
    - Open/Closed: Can be extended with hooks for monitoring
    - Liskov Substitution: Could be swapped with alternative implementations
    - Interface Segregation: Provides focused, minimal interface
    - Dependency Inversion: Depends on RunRegistry abstraction
    
    Example:
        ```python
        # Initialize
        registry = RunRegistry()
        task_manager = BackgroundTaskManager(registry)
        
        # Create a run object
        run = Run(
            run_id="unique-id",
            module_id="my-module",
            module_name="My Module",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={}
        )
        
        # Start background task
        async def my_task():
            await asyncio.sleep(5)
            return "result"
        
        task_id = task_manager.start_task(run, my_task())
        
        # Task runs in background, status automatically tracked
        # Can cancel if needed
        await task_manager.cancel_task(task_id)
        
        # Wait for all tasks before shutdown
        await task_manager.wait_all()
        ```
    """
    
    def __init__(self, registry: RunRegistry):
        """
        Initialize background task manager.
        
        Args:
            registry: RunRegistry instance for tracking task status
        """
        self.registry = registry
        self.tasks: Dict[str, asyncio.Task] = {}
        logger.info("BackgroundTaskManager initialized")
    
    async def _execute_task(self, run: Run, coro: Awaitable) -> None:
        """
        Execute task and update status in registry.
        
        This is the core execution wrapper that handles:
        - Status transitions (running -> completed/failed/cancelled)
        - Exception handling and logging
        - Registry updates
        - Task cleanup
        
        Args:
            run: Run object for tracking
            coro: Coroutine to execute
        """
        try:
            # Update status to running
            run.status = RunStatus.RUNNING
            self.registry.update_run(run)
            logger.info(f"Task {run.run_id} started")
            
            # Execute the actual task
            result = await coro
            
            # Update status to completed
            run.status = RunStatus.COMPLETED
            run.exit_code = 0
            self.registry.update_run(run)
            
            logger.info(f"Task {run.run_id} completed successfully")
            
        except asyncio.CancelledError:
            # Handle cancellation
            run.status = RunStatus.CANCELLED
            self.registry.update_run(run)
            logger.warning(f"Task {run.run_id} was cancelled")
            raise
            
        except Exception as e:
            # Handle failures
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            self.registry.update_run(run)
            logger.exception(f"Task {run.run_id} failed: {e}")
            
        finally:
            # Always cleanup - remove from active tasks
            self.tasks.pop(run.run_id, None)
            logger.debug(f"Task {run.run_id} cleaned up from active tasks")
    
    def start_task(self, run: Run, coro: Awaitable) -> str:
        """
        Start a background task without waiting for completion.
        
        This method immediately returns after creating the task, allowing
        the caller to continue without blocking. The task status is
        automatically tracked in the RunRegistry.
        
        Args:
            run: Run object for tracking (should have status=QUEUED)
            coro: Coroutine to execute in the background
            
        Returns:
            Run ID for tracking the task
            
        Example:
            ```python
            run = Run(
                run_id="task-123",
                module_id="my-module",
                module_name="My Module",
                status=RunStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                parameters={}
            )
            
            async def my_work():
                await asyncio.sleep(10)
                return "done"
            
            task_id = task_manager.start_task(run, my_work())
            # Returns immediately, task runs in background
            ```
        """
        # Create and store task
        task = asyncio.create_task(self._execute_task(run, coro))
        self.tasks[run.run_id] = task
        
        logger.info(f"Started background task {run.run_id} ({len(self.tasks)} active tasks)")
        return run.run_id
    
    async def cancel_task(self, run_id: str) -> bool:
        """
        Cancel a running background task.
        
        Attempts to cancel the specified task. If the task has already
        completed or doesn't exist, returns False.
        
        Args:
            run_id: ID of the task to cancel
            
        Returns:
            True if task was successfully cancelled, False otherwise
            
        Example:
            ```python
            # Cancel a task
            success = await task_manager.cancel_task("task-123")
            if success:
                print("Task cancelled")
            else:
                print("Task not found or already completed")
            ```
        """
        task = self.tasks.get(run_id)
        if not task:
            logger.warning(f"Task {run_id} not found in active tasks")
            return False
        
        if task.done():
            logger.info(f"Task {run_id} already completed")
            return False
        
        logger.info(f"Cancelling task {run_id}")
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            # Expected when cancelling
            pass
        
        return True
    
    async def wait_all(self) -> None:
        """
        Wait for all background tasks to complete.
        
        This method is useful for graceful shutdown - it waits for all
        active tasks to finish before returning. Exceptions are caught
        and logged but don't propagate.
        
        Example:
            ```python
            # Before shutdown
            await task_manager.wait_all()
            print("All background tasks completed")
            ```
        """
        if not self.tasks:
            logger.debug("No active tasks to wait for")
            return
        
        task_count = len(self.tasks)
        logger.info(f"Waiting for {task_count} background tasks to complete")
        
        # Gather all tasks, catching exceptions
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)
        
        logger.info(f"All {task_count} background tasks completed")
    
    def get_active_task_count(self) -> int:
        """
        Get the number of currently active tasks.
        
        Returns:
            Number of tasks currently running
        """
        return len(self.tasks)
    
    def get_active_task_ids(self) -> List[str]:
        """
        Get IDs of all active tasks.
        
        Returns:
            List of run IDs for active tasks
        """
        return list(self.tasks.keys())
    
    def is_task_active(self, run_id: str) -> bool:
        """
        Check if a task is currently active.
        
        Args:
            run_id: Run ID to check
            
        Returns:
            True if task is active, False otherwise
        """
        return run_id in self.tasks
