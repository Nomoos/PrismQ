"""Periodic background tasks for scheduled execution.

This module implements Pattern 5 from the Background Tasks Best Practices guide,
providing infrastructure for running maintenance tasks, health checks, and cleanup
operations on a schedule.

Platform: Windows (primary), Linux/macOS (supported)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Awaitable

logger = logging.getLogger(__name__)


class PeriodicTask:
    """Execute a task periodically in the background.
    
    This class provides a robust implementation of periodic task execution with:
    - Configurable intervals using timedelta
    - Graceful start/stop with event signaling
    - Error handling that doesn't stop the scheduler
    - Proper cleanup and resource management
    
    Example:
        ```python
        async def cleanup_task():
            logger.info("Running cleanup")
            # Cleanup logic here
            
        task = PeriodicTask(
            name="cleanup",
            interval=timedelta(hours=1),
            task_func=cleanup_task
        )
        task.start()
        
        # Later...
        await task.stop()
        ```
    """
    
    def __init__(
        self,
        name: str,
        interval: timedelta,
        task_func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ):
        """Initialize a periodic task.
        
        Args:
            name: Human-readable name for the task (used in logging)
            interval: Time between task executions
            task_func: Async function to execute periodically
            *args: Positional arguments to pass to task_func
            **kwargs: Keyword arguments to pass to task_func
        """
        self.name = name
        self.interval = interval
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._run_count = 0
        self._error_count = 0
        self._last_run: Optional[datetime] = None
    
    async def _run_periodic(self):
        """Run the task periodically until stopped.
        
        This method runs in a loop, executing the task function and then
        waiting for the specified interval. Errors in the task function
        are caught and logged, but don't stop the scheduler.
        """
        logger.info(f"Starting periodic task '{self.name}' (interval={self.interval})")
        
        while not self._stop_event.is_set():
            try:
                # Execute the task
                logger.debug(f"Executing periodic task '{self.name}'")
                start_time = datetime.now()
                
                await self.task_func(*self.args, **self.kwargs)
                
                # Update statistics
                self._run_count += 1
                self._last_run = start_time
                
                duration = (datetime.now() - start_time).total_seconds()
                logger.debug(
                    f"Periodic task '{self.name}' completed in {duration:.2f}s "
                    f"(runs: {self._run_count}, errors: {self._error_count})"
                )
                
            except Exception as e:
                self._error_count += 1
                logger.error(
                    f"Error in periodic task '{self.name}': {e}",
                    exc_info=True
                )
            
            # Wait for next interval or stop signal
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.interval.total_seconds()
                )
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue to next iteration
        
        logger.info(
            f"Stopped periodic task '{self.name}' "
            f"(runs: {self._run_count}, errors: {self._error_count})"
        )
    
    def start(self):
        """Start the periodic task.
        
        Creates a background asyncio task that runs the periodic execution loop.
        If the task is already running, logs a warning and does nothing.
        """
        if self._task and not self._task.done():
            logger.warning(f"Periodic task '{self.name}' already running")
            return
        
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_periodic())
        logger.info(f"Periodic task '{self.name}' started")
    
    async def stop(self, timeout: float = 5.0):
        """Stop the periodic task gracefully.
        
        Signals the task to stop and waits for it to complete. If the task
        doesn't stop within the timeout, it is cancelled forcefully.
        
        Args:
            timeout: Maximum time in seconds to wait for graceful shutdown
        """
        if not self._task or self._task.done():
            logger.warning(f"Periodic task '{self.name}' not running")
            return
        
        logger.info(f"Stopping periodic task '{self.name}'")
        self._stop_event.set()
        
        try:
            await asyncio.wait_for(self._task, timeout=timeout)
            logger.info(f"Periodic task '{self.name}' stopped gracefully")
        except asyncio.TimeoutError:
            logger.warning(
                f"Periodic task '{self.name}' did not stop gracefully, "
                f"cancelling..."
            )
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info(f"Periodic task '{self.name}' cancelled")
    
    @property
    def is_running(self) -> bool:
        """Check if the periodic task is currently running.
        
        Returns:
            True if task is running, False otherwise
        """
        return self._task is not None and not self._task.done()
    
    @property
    def statistics(self) -> dict:
        """Get task execution statistics.
        
        Returns:
            Dictionary with run count, error count, and last run time
        """
        return {
            "name": self.name,
            "interval": str(self.interval),
            "is_running": self.is_running,
            "run_count": self._run_count,
            "error_count": self._error_count,
            "last_run": self._last_run.isoformat() if self._last_run else None,
        }


class PeriodicTaskManager:
    """Manager for multiple periodic tasks.
    
    Provides centralized management of periodic tasks with lifecycle control.
    Useful for managing multiple tasks that start/stop together with the application.
    
    Example:
        ```python
        manager = PeriodicTaskManager()
        
        # Register tasks
        manager.register_task(
            name="cleanup",
            interval=timedelta(hours=1),
            task_func=cleanup_old_runs
        )
        manager.register_task(
            name="health_check",
            interval=timedelta(minutes=5),
            task_func=check_system_health
        )
        
        # Start all tasks
        manager.start_all()
        
        # Later... stop all tasks
        await manager.stop_all()
        ```
    """
    
    def __init__(self):
        """Initialize the periodic task manager."""
        self._tasks: dict[str, PeriodicTask] = {}
    
    def register_task(
        self,
        name: str,
        interval: timedelta,
        task_func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> PeriodicTask:
        """Register a new periodic task.
        
        Args:
            name: Unique name for the task
            interval: Time between task executions
            task_func: Async function to execute periodically
            *args: Positional arguments for task_func
            **kwargs: Keyword arguments for task_func
            
        Returns:
            The created PeriodicTask instance
            
        Raises:
            ValueError: If a task with the same name already exists
        """
        if name in self._tasks:
            raise ValueError(f"Task '{name}' already registered")
        
        task = PeriodicTask(name, interval, task_func, *args, **kwargs)
        self._tasks[name] = task
        logger.info(f"Registered periodic task '{name}' with interval {interval}")
        return task
    
    def get_task(self, name: str) -> Optional[PeriodicTask]:
        """Get a periodic task by name.
        
        Args:
            name: Name of the task
            
        Returns:
            The PeriodicTask instance, or None if not found
        """
        return self._tasks.get(name)
    
    def start_all(self):
        """Start all registered periodic tasks."""
        logger.info(f"Starting {len(self._tasks)} periodic tasks")
        for task in self._tasks.values():
            task.start()
    
    async def stop_all(self, timeout: float = 5.0):
        """Stop all periodic tasks gracefully.
        
        Args:
            timeout: Maximum time in seconds to wait for each task
        """
        logger.info(f"Stopping {len(self._tasks)} periodic tasks")
        for task in self._tasks.values():
            await task.stop(timeout=timeout)
    
    def get_all_statistics(self) -> list[dict]:
        """Get statistics for all tasks.
        
        Returns:
            List of statistics dictionaries for all tasks
        """
        return [task.statistics for task in self._tasks.values()]
