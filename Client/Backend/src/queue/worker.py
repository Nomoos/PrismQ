"""
Worker engine with retry logic and dead-letter handling.

Implements Issue #326: Retry Logic and Dead-Letter Handling
Provides task execution lifecycle including:
- Task completion and failure handling
- Exponential backoff retry logic
- max_attempts enforcement
- Dead-letter handling
- Error message capture
- Lease renewal
"""

import time
import math
import random
from typing import Optional, Callable, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass

from .database import QueueDatabase
from .models import Task, SchedulingStrategy
from .scheduling import TaskClaimerFactory
from .exceptions import QueueDatabaseError


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.
    
    Follows SOLID principles:
    - Single Responsibility: Represents retry configuration
    """
    
    initial_delay_seconds: float = 1.0  # Initial delay before first retry
    max_delay_seconds: float = 300.0    # Maximum delay (5 minutes)
    backoff_multiplier: float = 2.0      # Exponential backoff multiplier
    jitter_factor: float = 0.1           # Add randomness to prevent thundering herd


class TaskExecutor:
    """
    Handles task lifecycle operations including retry logic.
    
    Follows SOLID principles:
    - Single Responsibility: Manages task execution lifecycle
    - Dependency Inversion: Depends on QueueDatabase abstraction
    - Interface Segregation: Focused interface for task operations
    """
    
    def __init__(self, db: QueueDatabase):
        """
        Initialize task executor.
        
        Args:
            db: QueueDatabase instance for database operations
        """
        self.db = db
    
    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task as completed successfully.
        
        Args:
            task_id: ID of the task to complete
            
        Returns:
            True if task was completed, False if task not found or already finished
            
        Raises:
            QueueDatabaseError: If database operation fails
        """
        sql = """
        UPDATE task_queue
        SET status = 'completed',
            finished_at_utc = datetime('now'),
            updated_at_utc = datetime('now')
        WHERE id = ?
            AND status = 'leased'
        """
        
        try:
            with self.db.transaction() as conn:
                cursor = conn.execute(sql, (task_id,))
                return cursor.rowcount > 0
        except Exception as e:
            raise QueueDatabaseError(f"Failed to complete task: {e}") from e
    
    def fail_task(
        self,
        task_id: int,
        error_message: str,
        retry: bool = True
    ) -> bool:
        """
        Mark a task as failed with retry logic.
        
        Implements exponential backoff retry and dead-letter handling:
        - If attempts < max_attempts and retry=True: requeue with exponential backoff
        - If attempts >= max_attempts: mark as 'failed' (dead-letter)
        
        Args:
            task_id: ID of the task that failed
            error_message: Error description
            retry: Whether to retry (if False, immediately moves to failed status)
            
        Returns:
            True if task was updated, False if task not found
            
        Raises:
            QueueDatabaseError: If database operation fails
        """
        try:
            with self.db.transaction() as conn:
                # Fetch current task state
                cursor = conn.execute(
                    """
                    SELECT attempts, max_attempts, priority
                    FROM task_queue
                    WHERE id = ? AND status = 'leased'
                    """,
                    (task_id,)
                )
                row = cursor.fetchone()
                
                if row is None:
                    return False
                
                attempts = row['attempts']
                max_attempts = row['max_attempts']
                priority = row['priority']
                
                # Increment attempts
                new_attempts = attempts + 1
                
                # Determine if we should retry or move to dead-letter
                if retry and new_attempts < max_attempts:
                    # Calculate exponential backoff delay
                    retry_config = RetryConfig()
                    delay_seconds = self._calculate_backoff_delay(
                        new_attempts,
                        retry_config
                    )
                    
                    # Requeue task with exponential backoff
                    conn.execute(
                        """
                        UPDATE task_queue
                        SET status = 'queued',
                            attempts = ?,
                            error_message = ?,
                            run_after_utc = datetime('now', printf('+%d seconds', ?)),
                            lease_until_utc = NULL,
                            locked_by = NULL,
                            updated_at_utc = datetime('now')
                        WHERE id = ?
                        """,
                        (new_attempts, error_message, int(delay_seconds), task_id)
                    )
                else:
                    # Dead-letter: max attempts reached or retry=False
                    conn.execute(
                        """
                        UPDATE task_queue
                        SET status = 'failed',
                            attempts = ?,
                            error_message = ?,
                            finished_at_utc = datetime('now'),
                            updated_at_utc = datetime('now')
                        WHERE id = ?
                        """,
                        (new_attempts, error_message, task_id)
                    )
                
                return True
                
        except Exception as e:
            raise QueueDatabaseError(f"Failed to update task status: {e}") from e
    
    def renew_lease(self, task_id: int, lease_seconds: int) -> bool:
        """
        Renew the lease on a task to prevent timeout during long operations.
        
        Args:
            task_id: ID of the task
            lease_seconds: Additional seconds to add to lease
            
        Returns:
            True if lease was renewed, False if task not found or not leased
            
        Raises:
            QueueDatabaseError: If database operation fails
        """
        sql = """
        UPDATE task_queue
        SET lease_until_utc = datetime('now', printf('+%d seconds', ?)),
            updated_at_utc = datetime('now')
        WHERE id = ?
            AND status = 'leased'
        """
        
        try:
            with self.db.transaction() as conn:
                cursor = conn.execute(sql, (lease_seconds, task_id))
                return cursor.rowcount > 0
        except Exception as e:
            raise QueueDatabaseError(f"Failed to renew lease: {e}") from e
    
    def _calculate_backoff_delay(
        self,
        attempt: int,
        config: RetryConfig
    ) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Formula: min(initial_delay * (backoff_multiplier ^ attempt), max_delay)
        Jitter: +/- (jitter_factor * delay) for randomization
        
        Args:
            attempt: Current attempt number (1-indexed)
            config: Retry configuration
            
        Returns:
            Delay in seconds before next retry
        """
        # Exponential backoff
        delay = config.initial_delay_seconds * (config.backoff_multiplier ** (attempt - 1))
        
        # Cap at max delay
        delay = min(delay, config.max_delay_seconds)
        
        # Add jitter to prevent thundering herd
        # Simple jitter: multiply by factor between (1 - jitter) and (1 + jitter)
        jitter_range = config.jitter_factor
        jitter_multiplier = 1.0 + random.uniform(-jitter_range, jitter_range)
        delay *= jitter_multiplier
        
        return max(0.0, delay)


class WorkerEngine:
    """
    Worker engine that claims and processes tasks with retry support.
    
    Follows SOLID principles:
    - Single Responsibility: Coordinates task claiming and execution
    - Dependency Inversion: Depends on abstractions (QueueDatabase, TaskExecutor)
    - Open/Closed: Can be extended with custom task handlers
    """
    
    def __init__(
        self,
        db: QueueDatabase,
        worker_id: str,
        capabilities: Dict[str, Any] = None,
        scheduling_strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY,
        lease_seconds: int = 60,
        poll_interval_seconds: float = 1.0
    ):
        """
        Initialize worker engine.
        
        Args:
            db: QueueDatabase instance
            worker_id: Unique identifier for this worker
            capabilities: Worker capabilities for task filtering
            scheduling_strategy: Strategy for claiming tasks
            lease_seconds: Duration to lease tasks
            poll_interval_seconds: Time to wait between polls when queue is empty
        """
        self.db = db
        self.worker_id = worker_id
        self.capabilities = capabilities or {}
        self.scheduling_strategy = scheduling_strategy
        self.lease_seconds = lease_seconds
        self.poll_interval_seconds = poll_interval_seconds
        
        # Create task claimer and executor
        self.claimer = TaskClaimerFactory.create(scheduling_strategy, db)
        self.executor = TaskExecutor(db)
        
        self._running = False
    
    def claim_and_process(
        self,
        task_handler: Callable[[Task], None]
    ) -> bool:
        """
        Claim a single task and process it with retry support.
        
        Args:
            task_handler: Function that processes the task.
                         Should raise exception on failure.
                         
        Returns:
            True if a task was claimed and processed, False if no task available
            
        Raises:
            QueueDatabaseError: If database operation fails
        """
        # Claim a task
        task = self.claimer.claim_task(
            self.worker_id,
            self.capabilities,
            self.lease_seconds
        )
        
        if task is None:
            return False
        
        # Mark as processing
        try:
            with self.db.transaction() as conn:
                conn.execute(
                    """
                    UPDATE task_queue
                    SET processing_started_utc = datetime('now'),
                        updated_at_utc = datetime('now')
                    WHERE id = ?
                    """,
                    (task.id,)
                )
        except Exception as e:
            raise QueueDatabaseError(f"Failed to mark task as processing: {e}") from e
        
        # Execute task
        try:
            task_handler(task)
            # Task succeeded - complete it
            self.executor.complete_task(task.id)
            return True
            
        except Exception as e:
            # Task failed - apply retry logic
            error_message = f"{type(e).__name__}: {str(e)}"
            self.executor.fail_task(task.id, error_message, retry=True)
            return True
    
    def run_loop(
        self,
        task_handler: Callable[[Task], None],
        max_iterations: Optional[int] = None
    ) -> None:
        """
        Run worker loop that continuously claims and processes tasks.
        
        Args:
            task_handler: Function that processes tasks
            max_iterations: Maximum number of iterations (None = infinite)
        """
        self._running = True
        iteration = 0
        
        while self._running:
            if max_iterations is not None and iteration >= max_iterations:
                break
            
            # Claim and process one task
            processed = self.claim_and_process(task_handler)
            
            # If no task was available, wait before polling again
            if not processed:
                time.sleep(self.poll_interval_seconds)
            
            iteration += 1
    
    def stop(self) -> None:
        """Stop the worker loop."""
        self._running = False
