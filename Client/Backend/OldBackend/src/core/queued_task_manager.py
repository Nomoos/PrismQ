"""
QueuedTaskManager: Adapter for BackgroundTaskManager interface using queue system.

This adapter implements Worker 10 Issue #339: Integration layer that allows existing
BackgroundTaskManager code to work with the new SQLite-based queue system.

The adapter pattern enables:
- Backward compatibility with existing code
- Gradual migration to queue system
- Feature parity with BackgroundTaskManager
- Easy rollback if needed
"""

import asyncio
import json
import logging
from typing import Dict, Callable, Awaitable, Optional
from datetime import datetime, timezone

from ..queue import QueueDatabase, TaskHandlerRegistry, Task
from ..models.run import Run, RunStatus
from .run_registry import RunRegistry

logger = logging.getLogger(__name__)


class QueuedTaskManager:
    """
    Adapter that implements BackgroundTaskManager interface using queue system.
    
    This class bridges the gap between the old BackgroundTaskManager interface
    and the new queue-based system, enabling transparent migration.
    
    Key Features:
    - Compatible with BackgroundTaskManager interface
    - Delegates to SQLite queue for persistence
    - Uses TaskHandlerRegistry for handler management
    - Maintains status tracking via RunRegistry
    - Supports task cancellation
    - Graceful shutdown support
    
    Design Pattern: Adapter
    - Target: BackgroundTaskManager interface
    - Adaptee: QueueDatabase and TaskHandlerRegistry
    - Adapter: This class (QueuedTaskManager)
    
    Example:
        ```python
        # Initialize components
        queue = QueueDatabase()
        queue.initialize_schema()
        registry = RunRegistry()
        
        # Create adapter
        manager = QueuedTaskManager(queue, registry)
        
        # Register task handler
        async def cleanup_handler(task_data):
            # Process cleanup task
            pass
        
        await manager.register_task("cleanup_runs", cleanup_handler)
        
        # Schedule task (same API as BackgroundTaskManager)
        run = Run(
            run_id="cleanup-123",
            module_id="cleanup",
            module_name="Cleanup",
            status=RunStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            parameters={"max_age_hours": 24}
        )
        
        task_id = manager.start_task(run, cleanup_handler())
        
        # Task is now queued in SQLite database
        # Can query status, cancel, etc.
        ```
    """
    
    def __init__(self, queue: QueueDatabase, registry: RunRegistry):
        """
        Initialize QueuedTaskManager adapter.
        
        Args:
            queue: QueueDatabase instance for task persistence
            registry: RunRegistry instance for tracking task status
        """
        self.queue = queue
        self.registry = registry
        self.handler_registry = TaskHandlerRegistry()
        self.tasks: Dict[str, int] = {}  # Maps run_id to task_id in queue
        logger.info("QueuedTaskManager initialized with queue backend")
    
    async def register_task(
        self,
        task_type: str,
        handler: Callable,
        description: str = ""
    ) -> None:
        """
        Register a task handler for a specific task type.
        
        This method provides compatibility with the old registration pattern
        while using the new TaskHandlerRegistry internally.
        
        Args:
            task_type: Type of task to handle
            handler: Callable that processes the task
            description: Human-readable description
        """
        self.handler_registry.register_handler(
            task_type=task_type,
            handler=handler,
            description=description
        )
        logger.info(f"Registered handler for task type '{task_type}'")
    
    def start_task(self, run: Run, coro: Awaitable) -> str:
        """
        Start a background task by enqueueing it in the queue system.
        
        This method provides backward compatibility with BackgroundTaskManager.start_task
        but delegates to the queue system for actual task management.
        
        Args:
            run: Run object for tracking (should have status=QUEUED)
            coro: Coroutine to execute (not actually used, as queue workers execute tasks)
            
        Returns:
            Run ID for tracking the task
            
        Note:
            The coroutine parameter is accepted for API compatibility but not used.
            Instead, the task is enqueued in the queue system, and registered
            handlers will process it asynchronously via queue workers.
        """
        # Prepare task data from run parameters
        payload_json = json.dumps(run.parameters)
        compatibility_json = json.dumps({})
        run_after = datetime.now(timezone.utc)
        
        # Enqueue task in database
        try:
            with self.queue.transaction() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO task_queue (
                        type, priority, payload, compatibility,
                        max_attempts, run_after_utc, idempotency_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run.module_id,  # Use module_id as task type
                        100,  # Default priority
                        payload_json,
                        compatibility_json,
                        5,  # Default max attempts
                        run_after.isoformat(),
                        run.run_id,  # Use run_id as idempotency key
                    )
                )
                task_id = cursor.lastrowid
            
            # Store mapping from run_id to task_id
            self.tasks[run.run_id] = task_id
            
            # Update run status to queued in registry
            run.status = RunStatus.QUEUED
            self.registry.update_run(run)
            
            logger.info(
                f"Enqueued task {task_id} for run {run.run_id} "
                f"({len(self.tasks)} active tasks)"
            )
            return run.run_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue task for run {run.run_id}: {e}")
            raise
    
    async def schedule_task(
        self,
        task_type: str,
        payload: dict,
        priority: int = 100,
        run_after: Optional[datetime] = None,
        idempotency_key: Optional[str] = None
    ) -> str:
        """
        Schedule a task for later execution.
        
        This method provides a direct queue-style API for scheduling tasks
        without needing to create a Run object first.
        
        Args:
            task_type: Type of task to schedule
            payload: Task payload data
            priority: Task priority (1-1000, lower = higher priority)
            run_after: Schedule task to run after this time
            idempotency_key: Unique key to prevent duplicate tasks
            
        Returns:
            Task ID in the queue
        """
        payload_json = json.dumps(payload)
        compatibility_json = json.dumps({})
        run_after_dt = run_after or datetime.now(timezone.utc)
        
        try:
            with self.queue.transaction() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO task_queue (
                        type, priority, payload, compatibility,
                        max_attempts, run_after_utc, idempotency_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task_type,
                        priority,
                        payload_json,
                        compatibility_json,
                        5,  # Default max attempts
                        run_after_dt.isoformat(),
                        idempotency_key,
                    )
                )
                task_id = cursor.lastrowid
            
            logger.info(f"Scheduled task {task_id} of type '{task_type}'")
            return str(task_id)
            
        except Exception as e:
            logger.error(f"Failed to schedule task of type {task_type}: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> dict:
        """
        Get the status of a task.
        
        Args:
            task_id: Task ID or run ID to query
            
        Returns:
            Dictionary with task status information
        """
        try:
            # Check if task_id is a run_id in our mapping
            if task_id in self.tasks:
                queue_task_id = self.tasks[task_id]
            else:
                # Assume it's already a queue task ID
                try:
                    queue_task_id = int(task_id)
                except ValueError:
                    # If it's not a number, it might be a run_id not in our mapping
                    # Try to look it up by idempotency_key
                    cursor = self.queue.execute(
                        "SELECT id FROM task_queue WHERE idempotency_key = ?",
                        (task_id,)
                    )
                    row = cursor.fetchone()
                    if not row:
                        return {
                            "status": "not_found",
                            "task_id": task_id,
                            "error": "Task not found"
                        }
                    queue_task_id = dict(row)["id"]
            
            # Query task from queue
            cursor = self.queue.execute(
                """
                SELECT id, type, status, priority, attempts, max_attempts,
                       payload, error_message, created_at_utc, processing_started_utc,
                       finished_at_utc, locked_by
                FROM task_queue WHERE id = ?
                """,
                (queue_task_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return {
                    "status": "not_found",
                    "task_id": task_id,
                    "error": "Task not found"
                }
            
            task_dict = dict(row)
            
            # Map queue status to BackgroundTaskManager status
            status_map = {
                "queued": "queued",
                "processing": "running",
                "completed": "completed",
                "failed": "failed"
            }
            
            return {
                "task_id": task_dict["id"],
                "status": status_map.get(task_dict["status"], task_dict["status"]),
                "type": task_dict["type"],
                "attempts": task_dict["attempts"],
                "max_attempts": task_dict["max_attempts"],
                "error_message": task_dict.get("error_message"),
                "created_at": task_dict.get("created_at_utc"),
                "started_at": task_dict.get("processing_started_utc"),
                "finished_at": task_dict.get("finished_at_utc"),
                "locked_by": task_dict.get("locked_by")
            }
            
        except Exception as e:
            logger.error(f"Failed to get status for task {task_id}: {e}")
            return {
                "status": "error",
                "task_id": task_id,
                "error": str(e)
            }
    
    async def cancel_task(self, run_id: str) -> bool:
        """
        Cancel a running or queued task.
        
        This method provides compatibility with BackgroundTaskManager.cancel_task.
        
        Args:
            run_id: ID of the task to cancel
            
        Returns:
            True if task was successfully cancelled, False otherwise
        """
        try:
            # Get queue task_id from run_id
            if run_id in self.tasks:
                queue_task_id = self.tasks[run_id]
            else:
                # Try to look it up by idempotency_key
                cursor = self.queue.execute(
                    "SELECT id, status FROM task_queue WHERE idempotency_key = ?",
                    (run_id,)
                )
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"Task {run_id} not found")
                    return False
                task_dict = dict(row)
                queue_task_id = task_dict["id"]
                current_status = task_dict["status"]
                
                # Check if already completed
                if current_status in ("completed", "failed"):
                    logger.info(f"Task {run_id} already {current_status}")
                    return False
            
            # Check current status before attempting to cancel
            cursor = self.queue.execute(
                "SELECT status FROM task_queue WHERE id = ?",
                (queue_task_id,)
            )
            row = cursor.fetchone()
            if row:
                current_status = dict(row)["status"]
                if current_status in ("completed", "failed"):
                    logger.info(f"Task {run_id} already {current_status}")
                    return False
            
            # Cancel task in queue
            with self.queue.transaction() as conn:
                cursor = conn.execute(
                    """
                    UPDATE task_queue
                    SET status = 'failed',
                        error_message = 'Cancelled by user',
                        finished_at_utc = datetime('now', 'utc'),
                        updated_at_utc = datetime('now', 'utc')
                    WHERE id = ? AND status NOT IN ('completed', 'failed')
                    """,
                    (queue_task_id,)
                )
                rows_affected = cursor.rowcount
            
            # If no rows were updated, task was already completed
            if rows_affected == 0:
                logger.info(f"Task {run_id} already completed or failed")
                return False
            
            # Update run status in registry if exists
            run = self.registry.get_run(run_id)
            if run:
                run.status = RunStatus.CANCELLED
                self.registry.update_run(run)
            
            # Remove from active tasks
            self.tasks.pop(run_id, None)
            
            logger.info(f"Cancelled task {run_id} (queue task {queue_task_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel task {run_id}: {e}")
            return False
    
    async def wait_all(self) -> None:
        """
        Wait for all background tasks to complete.
        
        This method polls the queue for task completion. Since tasks are
        processed by queue workers, we just need to wait until all our
        tracked tasks are no longer in 'queued' or 'processing' status.
        """
        if not self.tasks:
            logger.debug("No active tasks to wait for")
            return
        
        task_count = len(self.tasks)
        logger.info(f"Waiting for {task_count} queued tasks to complete")
        
        # Poll tasks until all are completed or failed
        remaining_tasks = set(self.tasks.keys())
        
        while remaining_tasks:
            completed_tasks = set()
            
            for run_id in remaining_tasks:
                status = await self.get_task_status(run_id)
                if status["status"] in ("completed", "failed", "not_found", "error"):
                    completed_tasks.add(run_id)
            
            remaining_tasks -= completed_tasks
            
            if remaining_tasks:
                # Wait a bit before polling again
                await asyncio.sleep(0.5)
        
        logger.info(f"All {task_count} queued tasks completed")
    
    def get_active_task_count(self) -> int:
        """
        Get the number of currently active (tracked) tasks.
        
        Returns:
            Number of tasks currently being tracked
        """
        return len(self.tasks)
    
    def get_active_task_ids(self) -> list:
        """
        Get IDs of all active tasks.
        
        Returns:
            List of run IDs for active tasks
        """
        return list(self.tasks.keys())
    
    def is_task_active(self, run_id: str) -> bool:
        """
        Check if a task is currently active (tracked).
        
        Args:
            run_id: Run ID to check
            
        Returns:
            True if task is active, False otherwise
        """
        return run_id in self.tasks
