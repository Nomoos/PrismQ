"""Task logging and observability integration for queue system."""

import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from .database import QueueDatabase
from .models import TaskLog
from .exceptions import QueueDatabaseError


class TaskLogger:
    """
    Manages task-level logging to the task_logs table.
    
    Follows SOLID principles:
    - Single Responsibility: Handles task log persistence
    - Dependency Inversion: Depends on QueueDatabase abstraction
    - Open/Closed: Extensible without modification
    
    Thread-safe logging operations with minimal performance overhead.
    """

    def __init__(self, db: QueueDatabase):
        """
        Initialize with database connection.
        
        Args:
            db: QueueDatabase instance for log persistence
        """
        self.db = db

    def log(
        self,
        task_id: int,
        level: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a task event to task_logs table.
        
        Args:
            task_id: ID of the task
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            details: Optional additional details as JSON
            
        Raises:
            QueueDatabaseError: If log insertion fails
        """
        # Validate log level
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if level.upper() not in valid_levels:
            level = "INFO"
        
        # Convert details to JSON string
        details_json = None
        if details is not None:
            try:
                details_json = json.dumps(details)
            except (TypeError, ValueError) as e:
                # If details can't be serialized, log the error
                details_json = json.dumps({"error": f"Failed to serialize details: {e}"})
        
        # Insert log entry
        sql = """
            INSERT INTO task_logs (task_id, level, message, details)
            VALUES (?, ?, ?, ?)
        """
        
        try:
            self.db.execute(sql, (task_id, level.upper(), message, details_json))
        except Exception as e:
            raise QueueDatabaseError(f"Failed to insert task log: {e}") from e

    def get_task_logs(
        self,
        task_id: int,
        level: Optional[str] = None,
        limit: int = 100,
    ) -> List[TaskLog]:
        """
        Retrieve logs for a specific task.
        
        Args:
            task_id: ID of the task
            level: Filter by log level (optional)
            limit: Maximum number of logs to retrieve (default: 100)
            
        Returns:
            List of TaskLog objects ordered by timestamp (newest first)
            
        Raises:
            QueueDatabaseError: If query fails
        """
        # Build query with optional level filter
        if level:
            sql = """
                SELECT log_id, task_id, at_utc, level, message, details
                FROM task_logs
                WHERE task_id = ? AND level = ?
                ORDER BY at_utc DESC
                LIMIT ?
            """
            params = (task_id, level.upper(), limit)
        else:
            sql = """
                SELECT log_id, task_id, at_utc, level, message, details
                FROM task_logs
                WHERE task_id = ?
                ORDER BY at_utc DESC
                LIMIT ?
            """
            params = (task_id, limit)
        
        try:
            cursor = self.db.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert rows to TaskLog objects
            logs = []
            for row in rows:
                log_dict = dict(row)
                logs.append(TaskLog.from_dict(log_dict))
            
            return logs
        except Exception as e:
            raise QueueDatabaseError(f"Failed to retrieve task logs: {e}") from e

    def get_recent_logs(
        self,
        limit: int = 100,
        level: Optional[str] = None,
    ) -> List[TaskLog]:
        """
        Retrieve recent logs across all tasks.
        
        Args:
            limit: Maximum number of logs to retrieve (default: 100)
            level: Filter by log level (optional)
            
        Returns:
            List of TaskLog objects ordered by timestamp (newest first)
            
        Raises:
            QueueDatabaseError: If query fails
        """
        # Build query with optional level filter
        if level:
            sql = """
                SELECT log_id, task_id, at_utc, level, message, details
                FROM task_logs
                WHERE level = ?
                ORDER BY at_utc DESC
                LIMIT ?
            """
            params = (level.upper(), limit)
        else:
            sql = """
                SELECT log_id, task_id, at_utc, level, message, details
                FROM task_logs
                ORDER BY at_utc DESC
                LIMIT ?
            """
            params = (limit,)
        
        try:
            cursor = self.db.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert rows to TaskLog objects
            logs = []
            for row in rows:
                log_dict = dict(row)
                logs.append(TaskLog.from_dict(log_dict))
            
            return logs
        except Exception as e:
            raise QueueDatabaseError(f"Failed to retrieve recent logs: {e}") from e

    def delete_old_logs(self, days: int = 30) -> int:
        """
        Delete logs older than specified number of days.
        
        Useful for log rotation and cleanup.
        
        Args:
            days: Delete logs older than this many days (default: 30)
            
        Returns:
            Number of logs deleted
            
        Raises:
            QueueDatabaseError: If deletion fails
        """
        sql = """
            DELETE FROM task_logs
            WHERE at_utc < datetime('now', ?)
        """
        
        try:
            cursor = self.db.execute(sql, (f"-{days} days",))
            deleted_count = cursor.rowcount
            return deleted_count
        except Exception as e:
            raise QueueDatabaseError(f"Failed to delete old logs: {e}") from e


class QueueLogger:
    """
    Integrates queue logging with application logging.
    
    Bridges task_logs database persistence with standard Python logging.
    Provides unified logging interface for queue events.
    
    Follows SOLID principles:
    - Single Responsibility: Coordinates logging to multiple destinations
    - Dependency Inversion: Depends on abstractions (TaskLogger, logging.Logger)
    """

    def __init__(
        self,
        db: QueueDatabase,
        app_logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize with database and optional application logger.
        
        Args:
            db: QueueDatabase instance
            app_logger: Optional logger, defaults to queue logger
        """
        self.task_logger = TaskLogger(db)
        self.app_logger = app_logger or logging.getLogger("prismq.queue")

    def log_task_event(
        self,
        task_id: int,
        level: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log task event to both database and application logs.
        
        Args:
            task_id: Task ID
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            details: Optional details dict
        """
        # Log to database
        try:
            self.task_logger.log(task_id, level, message, details)
        except Exception as e:
            # If database logging fails, at least log to app logger
            self.app_logger.error(
                f"Failed to log task {task_id} to database: {e}",
                exc_info=True,
            )
        
        # Log to application logger
        log_method = getattr(
            self.app_logger,
            level.lower(),
            self.app_logger.info,
        )
        
        # Format message with context
        context_msg = f"Task {task_id}: {message}"
        
        # Include details in extra if provided
        extra = {"task_id": task_id}
        if details:
            extra["details"] = details
        
        log_method(context_msg, extra=extra)

    def log_task_transition(
        self,
        task_id: int,
        from_status: str,
        to_status: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log task status transition.
        
        Args:
            task_id: Task ID
            from_status: Previous status
            to_status: New status
            details: Optional details dict
        """
        message = f"Status transition: {from_status} → {to_status}"
        
        # Determine log level based on transition
        if to_status in ("failed", "dead_letter"):
            level = "ERROR"
        elif to_status == "completed":
            level = "INFO"
        else:
            level = "DEBUG"
        
        transition_details = {"from_status": from_status, "to_status": to_status}
        if details:
            transition_details.update(details)
        
        self.log_task_event(task_id, level, message, transition_details)

    def log_task_error(
        self,
        task_id: int,
        error: Exception,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log task error with exception details.
        
        Args:
            task_id: Task ID
            error: Exception that occurred
            details: Optional additional details
        """
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        if details:
            error_details.update(details)
        
        message = f"Task error: {type(error).__name__}: {error}"
        self.log_task_event(task_id, "ERROR", message, error_details)

    def log_task_retry(
        self,
        task_id: int,
        attempt: int,
        max_attempts: int,
        next_run_after: datetime,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log task retry attempt.
        
        Args:
            task_id: Task ID
            attempt: Current attempt number
            max_attempts: Maximum allowed attempts
            next_run_after: When task will be retried
            details: Optional additional details
        """
        retry_details = {
            "attempt": attempt,
            "max_attempts": max_attempts,
            "next_run_after": next_run_after.isoformat() if next_run_after else None,
        }
        if details:
            retry_details.update(details)
        
        message = f"Retry scheduled: attempt {attempt}/{max_attempts}"
        self.log_task_event(task_id, "WARNING", message, retry_details)
