"""Task polling mechanism for workers.

This module provides the TaskPoller class that manages continuous polling
of the task queue, applying claiming strategies and handling edge cases.

Following SOLID principles:
- Single Responsibility: Task polling and claiming coordination only
- Dependency Inversion: Depends on abstractions (ClaimingStrategy protocol)
- Interface Segregation: Minimal, focused interface
"""

import logging
import time
import sqlite3
import json
from typing import Optional, Callable
from datetime import datetime, timezone

from . import Task, TaskStatus
from .claiming_strategies import get_strategy, BaseClaimStrategy


logger = logging.getLogger(__name__)


class TaskPoller:
    """Manages task polling for workers.
    
    Follows Single Responsibility Principle (SRP):
    - Polls queue for available tasks
    - Applies claiming strategy
    - Manages polling lifecycle
    - Tracks polling statistics
    
    Does NOT handle:
    - Task execution (worker's responsibility)
    - Database schema (QueueDatabase's responsibility)
    - Result reporting (worker's responsibility)
    
    Follows Dependency Inversion Principle (DIP):
    - Depends on ClaimingStrategy protocol (abstraction)
    - Queue connection injected via constructor
    """
    
    def __init__(
        self,
        queue_conn: sqlite3.Connection,
        worker_id: str,
        strategy: str = "LIFO",
        poll_interval: float = 5.0,
        max_idle_polls: int = 12,  # 1 minute at 5s interval
    ):
        """Initialize task poller.
        
        Args:
            queue_conn: SQLite connection to queue database
            worker_id: Unique worker identifier
            strategy: Claiming strategy name (FIFO, LIFO, PRIORITY, WEIGHTED_RANDOM)
            poll_interval: Seconds between polls when idle
            max_idle_polls: Max consecutive empty polls before applying backoff
        """
        self.queue_conn = queue_conn
        self.worker_id = worker_id
        self.strategy_name = strategy.upper()
        self.strategy = get_strategy(self.strategy_name)
        self.poll_interval = poll_interval
        self.max_idle_polls = max_idle_polls
        
        # Polling state
        self.running = False
        self.polls_total = 0
        self.polls_successful = 0
        self.polls_empty = 0
        self.consecutive_empty = 0
        
        logger.info(
            f"TaskPoller initialized for worker {worker_id} "
            f"(strategy: {self.strategy_name}, interval: {poll_interval}s)"
        )
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from the queue using configured strategy.
        
        Uses IMMEDIATE transaction for atomic claiming to prevent
        SQLITE_BUSY errors and double-claiming.
        
        Returns:
            Task if available and claimed, None otherwise
            
        Performance:
            Target: <10ms (P95) for claiming operation
        """
        self.polls_total += 1
        
        try:
            cursor = self.queue_conn.cursor()
            
            # Begin IMMEDIATE transaction (locks database immediately)
            # This prevents SQLITE_BUSY and ensures atomic claiming
            cursor.execute("BEGIN IMMEDIATE")
            
            try:
                # Build query with strategy's ORDER BY clause
                order_by = self.strategy.get_order_by_clause()
                now_utc = datetime.now(timezone.utc).isoformat()
                
                # Find available task using strategy
                query = f"""
                    SELECT id, task_type, parameters, priority, 
                           status, retry_count, max_retries, created_at
                    FROM task_queue
                    WHERE status = 'queued'
                      AND (run_after_utc IS NULL OR run_after_utc <= ?)
                    ORDER BY {order_by}
                    LIMIT 1
                """
                
                cursor.execute(query, (now_utc,))
                row = cursor.fetchone()
                
                if not row:
                    # No tasks available
                    cursor.execute("ROLLBACK")
                    self.polls_empty += 1
                    self.consecutive_empty += 1
                    return None
                
                # Claim the task atomically
                task_id = row['id']
                
                update_query = """
                    UPDATE task_queue
                    SET status = 'claimed',
                        claimed_at = ?,
                        claimed_by = ?,
                        updated_at = ?
                    WHERE id = ?
                """
                
                cursor.execute(update_query, (
                    now_utc,
                    self.worker_id,
                    now_utc,
                    task_id
                ))
                
                # Commit transaction
                cursor.execute("COMMIT")
                
                # Log the claim event
                try:
                    cursor.execute("""
                        INSERT INTO task_logs 
                        (task_id, worker_id, event_type, message, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        task_id,
                        self.worker_id,
                        'claimed',
                        f'Task claimed by {self.worker_id} using {self.strategy_name}',
                        now_utc
                    ))
                    self.queue_conn.commit()
                except Exception as log_error:
                    # Don't fail the claim if logging fails
                    logger.warning(f"Failed to log claim event: {log_error}")
                
                # Parse parameters (stored as JSON string in SQLite)
                parameters_raw = row['parameters']
                if isinstance(parameters_raw, str):
                    try:
                        parameters = json.loads(parameters_raw)
                    except json.JSONDecodeError:
                        # Fallback to eval for backward compatibility
                        # (only safe because data comes from our own DB)
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
                    claimed_at=now_utc
                )
                
                # Update statistics
                self.polls_successful += 1
                self.consecutive_empty = 0
                
                logger.info(
                    f"Worker {self.worker_id} claimed task {task_id} "
                    f"(type: {task.task_type}, strategy: {self.strategy_name})"
                )
                
                return task
                
            except Exception as e:
                # Rollback on any error
                cursor.execute("ROLLBACK")
                raise
                
        except sqlite3.OperationalError as e:
            # Handle SQLITE_BUSY gracefully
            if "database is locked" in str(e) or "database is busy" in str(e):
                logger.warning(f"Database busy during claim (will retry): {e}")
                self.polls_empty += 1
                self.consecutive_empty += 1
                return None
            else:
                logger.error(f"Operational error claiming task: {e}")
                self.polls_empty += 1
                self.consecutive_empty += 1
                return None
                
        except Exception as e:
            logger.error(f"Error claiming task: {e}", exc_info=True)
            self.polls_empty += 1
            self.consecutive_empty += 1
            return None
    
    def poll_once(
        self,
        on_task: Callable[[Task], None],
        on_idle: Optional[Callable[[], None]] = None
    ) -> bool:
        """Execute one polling iteration.
        
        Args:
            on_task: Callback function invoked when task is claimed
            on_idle: Optional callback function when no task available
            
        Returns:
            True if task was claimed and processed, False otherwise
        """
        # Try to claim a task
        task = self.claim_task()
        
        if task:
            # Task claimed - invoke callback
            try:
                on_task(task)
                return True
            except Exception as e:
                logger.error(
                    f"Error in on_task callback for task {task.id}: {e}",
                    exc_info=True
                )
                return False
        else:
            # No task available - invoke idle callback
            if on_idle:
                try:
                    on_idle()
                except Exception as e:
                    logger.warning(f"Error in on_idle callback: {e}")
            
            # Apply backoff if many consecutive empty polls
            if self.consecutive_empty >= self.max_idle_polls:
                # Exponential backoff up to 60 seconds
                backoff_interval = min(
                    self.poll_interval * 2,
                    60.0  # Max 1 minute backoff
                )
                logger.debug(
                    f"Applying backoff: {backoff_interval}s "
                    f"({self.consecutive_empty} consecutive empty polls)"
                )
                time.sleep(backoff_interval)
            else:
                # Normal polling interval
                time.sleep(self.poll_interval)
            
            return False
    
    def run(
        self,
        on_task: Callable[[Task], None],
        on_idle: Optional[Callable[[], None]] = None,
        max_iterations: Optional[int] = None
    ):
        """Run the polling loop continuously.
        
        Args:
            on_task: Callback function invoked when task is claimed
            on_idle: Optional callback function when no task available
            max_iterations: Maximum iterations to run (None = infinite)
            
        Example:
            >>> def process_task(task):
            ...     print(f"Processing {task.id}")
            >>> def on_idle():
            ...     print("No tasks, waiting...")
            >>> poller = TaskPoller(conn, "worker-1")
            >>> poller.run(process_task, on_idle, max_iterations=10)
        """
        self.running = True
        iteration = 0
        
        logger.info(
            f"TaskPoller starting for worker {self.worker_id} "
            f"(strategy: {self.strategy_name})"
        )
        
        try:
            while self.running:
                # Check iteration limit
                if max_iterations and iteration >= max_iterations:
                    logger.info(f"Max iterations ({max_iterations}) reached, stopping")
                    break
                
                # Poll once
                self.poll_once(on_task, on_idle)
                
                iteration += 1
                
        except KeyboardInterrupt:
            logger.info("Polling interrupted by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"Fatal error in polling loop: {e}", exc_info=True)
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop the polling loop gracefully."""
        self.running = False
        logger.info(
            f"TaskPoller stopped for worker {self.worker_id} "
            f"(polls: {self.polls_total}, "
            f"successful: {self.polls_successful}, "
            f"empty: {self.polls_empty})"
        )
    
    def get_stats(self) -> dict:
        """Get polling statistics.
        
        Returns:
            Dictionary with polling metrics including:
            - worker_id: Worker identifier
            - strategy: Claiming strategy name
            - polls_total: Total poll attempts
            - polls_successful: Successful claims
            - polls_empty: Empty poll results
            - success_rate: Ratio of successful claims
            - consecutive_empty: Current streak of empty polls
            - running: Whether poller is currently running
            
        Example:
            >>> stats = poller.get_stats()
            >>> print(f"Success rate: {stats['success_rate']:.1%}")
        """
        return {
            'worker_id': self.worker_id,
            'strategy': self.strategy_name,
            'polls_total': self.polls_total,
            'polls_successful': self.polls_successful,
            'polls_empty': self.polls_empty,
            'success_rate': (
                self.polls_successful / self.polls_total 
                if self.polls_total > 0 else 0.0
            ),
            'consecutive_empty': self.consecutive_empty,
            'running': self.running
        }


__all__ = ['TaskPoller']
