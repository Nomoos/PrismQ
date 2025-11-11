"""Base worker implementation following SOLID principles."""

import logging
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from abc import ABC, abstractmethod

from ..core.config import Config
from ..core.database import Database
from . import Task, TaskResult, TaskStatus, WorkerProtocol
from .claiming_strategies import get_strategy


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
        queue_db_path: str,
        config: Config,
        results_db: Database,
        strategy: str = "LIFO",
        heartbeat_interval: int = 30,
        poll_interval: int = 5,
        max_backoff: int = 60,
        backoff_multiplier: float = 1.5,
    ):
        """Initialize worker with injected dependencies (DIP).
        
        Args:
            worker_id: Unique worker identifier
            queue_db_path: Path to SQLite queue database
            config: Configuration object
            results_db: Database for storing results
            strategy: Task claiming strategy (FIFO, LIFO, PRIORITY)
            heartbeat_interval: Seconds between heartbeats
            poll_interval: Base polling interval in seconds (default 5)
            max_backoff: Maximum backoff time in seconds (default 60)
            backoff_multiplier: Backoff multiplier for exponential backoff (default 1.5)
        """
        self.worker_id = worker_id
        self.queue_db_path = queue_db_path
        self.config = config
        self.results_db = results_db
        self.strategy = strategy
        self.heartbeat_interval = heartbeat_interval
        self.poll_interval = poll_interval
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        
        # State
        self.running = False
        self.current_task: Optional[Task] = None
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.last_heartbeat = time.time()
        
        # Backoff state
        self._current_backoff = poll_interval
        
        # Queue connection (lazy initialization)
        self._queue_conn = None
        
        logger.info(
            f"Worker {self.worker_id} initialized "
            f"(strategy: {self.strategy}, poll_interval: {poll_interval}s, "
            f"max_backoff: {max_backoff}s)"
        )
    
    @property
    def queue_conn(self):
        """Lazy queue connection (one per worker)."""
        if self._queue_conn is None:
            import sqlite3
            self._queue_conn = sqlite3.connect(
                self.queue_db_path,
                check_same_thread=False
            )
            self._queue_conn.row_factory = sqlite3.Row
            # Enable WAL mode for concurrent access
            self._queue_conn.execute("PRAGMA journal_mode=WAL")
            self._queue_conn.execute("PRAGMA busy_timeout=5000")
        return self._queue_conn
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from queue using configured strategy.
        
        Implements atomic claiming with IMMEDIATE transaction.
        Uses Strategy pattern for flexible claiming behavior.
        
        Returns:
            Task if available and claimed, None otherwise
        """
        try:
            # Get ORDER BY clause from strategy
            try:
                strategy_obj = get_strategy(self.strategy)
                order_by = strategy_obj.get_order_by_clause()
            except ValueError:
                # Fallback to LIFO if strategy unknown
                logger.warning(f"Unknown strategy '{self.strategy}', falling back to LIFO")
                order_by = "created_at DESC, priority DESC"
            
            # Atomic claim with IMMEDIATE transaction
            cursor = self.queue_conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            
            try:
                # Find available task
                cursor.execute(f"""
                    SELECT id, task_type, parameters, priority, 
                           status, retry_count, max_retries, created_at
                    FROM task_queue
                    WHERE status = 'queued'
                      AND (run_after_utc IS NULL OR run_after_utc <= ?)
                    ORDER BY {order_by}
                    LIMIT 1
                """, (datetime.now(timezone.utc).isoformat(),))
                
                row = cursor.fetchone()
                if not row:
                    cursor.execute("ROLLBACK")
                    return None
                
                # Claim the task
                task_id = row['id']
                now = datetime.now(timezone.utc).isoformat()
                
                cursor.execute("""
                    UPDATE task_queue
                    SET status = 'claimed',
                        claimed_at = ?,
                        claimed_by = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (now, self.worker_id, now, task_id))
                
                cursor.execute("COMMIT")
                
                # Parse parameters (stored as JSON string in SQLite)
                parameters_raw = row['parameters']
                if isinstance(parameters_raw, str):
                    try:
                        parameters = json.loads(parameters_raw)
                    except json.JSONDecodeError:
                        # Fallback to eval for backward compatibility
                        parameters = eval(parameters_raw)
                else:
                    parameters = parameters_raw or {}
                
                # Create Task object
                task = Task(
                    id=task_id,
                    task_type=row['task_type'],
                    parameters=parameters,
                    priority=row['priority'],
                    status=TaskStatus.CLAIMED,
                    retry_count=row['retry_count'],
                    max_retries=row['max_retries'],
                    created_at=row['created_at'],
                    claimed_at=now
                )
                
                self.current_task = task
                
                # Reset backoff on successful claim
                self._current_backoff = self.poll_interval
                
                logger.info(
                    f"Worker {self.worker_id} claimed task {task_id} "
                    f"(type: {task.task_type})"
                )
                return task
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise
                
        except Exception as e:
            logger.error(f"Error claiming task: {e}")
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
        """Report task result to queue and save data.
        
        Updates:
        1. Queue task status
        2. Results database
        3. TaskManager API (if configured)
        
        Args:
            task: The completed task
            result: The execution result
        """
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            # Update queue status
            if result.success:
                new_status = "completed"
                self.tasks_processed += 1
            else:
                new_status = "failed"
                self.tasks_failed += 1
            
            cursor = self.queue_conn.cursor()
            cursor.execute("""
                UPDATE task_queue
                SET status = ?,
                    completed_at = ?,
                    result_data = ?,
                    error_message = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                new_status,
                now,
                json.dumps(result.data) if result.data else None,
                result.error,
                now,
                task.id
            ))
            self.queue_conn.commit()
            
            # Save results to database if successful
            if result.success and result.data:
                self._save_results(task, result)
            
            # Update TaskManager API (if configured)
            self._update_task_manager(task, result)
            
            logger.info(
                f"Worker {self.worker_id} completed task {task.id} "
                f"(status: {new_status}, items: {result.items_processed})"
            )
            
        except Exception as e:
            logger.error(f"Error reporting result: {e}")
    
    def _save_results(self, task: Task, result: TaskResult) -> None:
        """Save results to database - to be customized by subclass."""
        # Default implementation - can be overridden
        pass
    
    def _update_task_manager(self, task: Task, result: TaskResult) -> None:
        """Update TaskManager API - to be implemented with API client."""
        # Placeholder for TaskManager API integration
        # Will be implemented in Issue #016
        pass
    
    def run_once(self) -> bool:
        """Execute one iteration of the worker loop.
        
        Returns:
            True if a task was processed, False otherwise
        """
        # Send heartbeat if needed
        self._send_heartbeat()
        
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
        if self._queue_conn:
            self._queue_conn.close()
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
    
    def _send_heartbeat(self):
        """Send heartbeat to queue."""
        now = time.time()
        if now - self.last_heartbeat >= self.heartbeat_interval:
            try:
                cursor = self.queue_conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO worker_heartbeats
                    (worker_id, last_heartbeat, tasks_processed, tasks_failed)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.worker_id,
                    datetime.now(timezone.utc).isoformat(),
                    self.tasks_processed,
                    self.tasks_failed
                ))
                self.queue_conn.commit()
                self.last_heartbeat = now
            except Exception as e:
                logger.warning(f"Failed to send heartbeat: {e}")


__all__ = ["BaseWorker"]
