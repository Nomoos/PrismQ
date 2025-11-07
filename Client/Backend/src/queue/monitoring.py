"""Queue monitoring and observability functions.

This module provides worker heartbeat management and queue metrics for
monitoring the SQLite queue system.

Implements issue #330: Worker Heartbeat and Monitoring
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from .database import QueueDatabase
from .models import Worker
from .exceptions import QueueDatabaseError


class QueueMonitoring:
    """
    Queue monitoring and observability manager.
    
    Provides functions for:
    - Worker registration and heartbeat updates
    - Stale worker detection
    - Queue metrics and statistics
    
    Follows SOLID principles:
    - Single Responsibility: Handles monitoring and observability only
    - Dependency Inversion: Depends on QueueDatabase abstraction
    - Open/Closed: Can be extended without modification
    """

    def __init__(self, db: QueueDatabase):
        """
        Initialize monitoring manager.
        
        Args:
            db: QueueDatabase instance for database operations
        """
        self.db = db

    def register_worker(
        self,
        worker_id: str,
        capabilities: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register or update a worker in the registry.
        
        Uses UPSERT pattern (INSERT OR REPLACE) to handle both new workers
        and heartbeat updates for existing workers.
        
        Args:
            worker_id: Unique identifier for the worker
            capabilities: Worker capabilities dict (default: empty dict)
            
        Raises:
            QueueDatabaseError: If registration fails
        """
        if capabilities is None:
            capabilities = {}
        
        capabilities_json = json.dumps(capabilities)
        
        try:
            self.db.execute(
                """
                INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(worker_id) DO UPDATE SET
                    capabilities = excluded.capabilities,
                    heartbeat_utc = datetime('now')
                """,
                (worker_id, capabilities_json)
            )
            self.db.get_connection().commit()
        except Exception as e:
            raise QueueDatabaseError(f"Failed to register worker: {e}") from e

    def update_heartbeat(self, worker_id: str) -> bool:
        """
        Update worker heartbeat timestamp.
        
        Args:
            worker_id: Unique identifier for the worker
            
        Returns:
            True if heartbeat was updated, False if worker not found
            
        Raises:
            QueueDatabaseError: If update fails
        """
        try:
            cursor = self.db.execute(
                """
                UPDATE workers 
                SET heartbeat_utc = datetime('now')
                WHERE worker_id = ?
                """,
                (worker_id,)
            )
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            raise QueueDatabaseError(f"Failed to update heartbeat: {e}") from e

    def get_worker(self, worker_id: str) -> Optional[Worker]:
        """
        Get worker information by ID.
        
        Args:
            worker_id: Unique identifier for the worker
            
        Returns:
            Worker object if found, None otherwise
            
        Raises:
            QueueDatabaseError: If query fails
        """
        try:
            cursor = self.db.execute(
                "SELECT * FROM workers WHERE worker_id = ?",
                (worker_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Worker.from_dict(dict(row))
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get worker: {e}") from e

    def get_all_workers(self) -> List[Worker]:
        """
        Get all registered workers.
        
        Returns:
            List of Worker objects
            
        Raises:
            QueueDatabaseError: If query fails
        """
        try:
            cursor = self.db.execute("SELECT * FROM workers ORDER BY worker_id")
            return [Worker.from_dict(dict(row)) for row in cursor.fetchall()]
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get workers: {e}") from e

    def get_stale_workers(
        self, 
        stale_threshold_seconds: int = 300
    ) -> List[Worker]:
        """
        Get workers that haven't sent heartbeat recently.
        
        A worker is considered stale if its last heartbeat is older than
        the threshold. Default threshold is 5 minutes (300 seconds).
        
        Args:
            stale_threshold_seconds: Seconds since last heartbeat to consider stale
            
        Returns:
            List of stale Worker objects
            
        Raises:
            QueueDatabaseError: If query fails
        """
        try:
            cursor = self.db.execute(
                """
                SELECT * FROM workers
                WHERE heartbeat_utc < datetime('now', ?)
                ORDER BY heartbeat_utc ASC
                """,
                (f'-{stale_threshold_seconds} seconds',)
            )
            return [Worker.from_dict(dict(row)) for row in cursor.fetchall()]
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get stale workers: {e}") from e

    def get_active_workers(
        self,
        active_threshold_seconds: int = 60
    ) -> List[Worker]:
        """
        Get workers that have sent heartbeat recently.
        
        A worker is considered active if its last heartbeat is within
        the threshold. Default threshold is 60 seconds.
        
        Args:
            active_threshold_seconds: Seconds since last heartbeat to consider active
            
        Returns:
            List of active Worker objects
            
        Raises:
            QueueDatabaseError: If query fails
        """
        try:
            cursor = self.db.execute(
                """
                SELECT * FROM workers
                WHERE heartbeat_utc >= datetime('now', ?)
                ORDER BY heartbeat_utc DESC
                """,
                (f'-{active_threshold_seconds} seconds',)
            )
            return [Worker.from_dict(dict(row)) for row in cursor.fetchall()]
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get active workers: {e}") from e

    def remove_worker(self, worker_id: str) -> bool:
        """
        Remove a worker from the registry.
        
        Useful for cleanup of permanently offline workers.
        
        Args:
            worker_id: Unique identifier for the worker
            
        Returns:
            True if worker was removed, False if not found
            
        Raises:
            QueueDatabaseError: If removal fails
        """
        try:
            cursor = self.db.execute(
                "DELETE FROM workers WHERE worker_id = ?",
                (worker_id,)
            )
            self.db.get_connection().commit()
            return cursor.rowcount > 0
        except Exception as e:
            raise QueueDatabaseError(f"Failed to remove worker: {e}") from e

    def get_queue_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive queue metrics for monitoring.
        
        Returns dict with:
        - queue_depth_by_status: Count of tasks by status
        - queue_depth_by_type: Count of tasks by type
        - oldest_queued_task_age_seconds: Age of oldest queued task
        - task_statistics: Success/failure rates
        - worker_statistics: Active/stale worker counts
        
        Returns:
            Dictionary with queue metrics
            
        Raises:
            QueueDatabaseError: If queries fail
        """
        metrics = {}
        
        try:
            # Queue depth by status
            cursor = self.db.execute(
                """
                SELECT status, COUNT(*) as count
                FROM task_queue
                GROUP BY status
                """
            )
            metrics['queue_depth_by_status'] = {
                row['status']: row['count'] for row in cursor.fetchall()
            }
            
            # Queue depth by type
            cursor = self.db.execute(
                """
                SELECT type, COUNT(*) as count
                FROM task_queue
                WHERE status = 'queued'
                GROUP BY type
                """
            )
            metrics['queue_depth_by_type'] = {
                row['type']: row['count'] for row in cursor.fetchall()
            }
            
            # Age of oldest queued task
            cursor = self.db.execute(
                """
                SELECT 
                    CAST((julianday('now') - julianday(created_at_utc)) * 86400 AS INTEGER) as age_seconds
                FROM task_queue
                WHERE status = 'queued'
                ORDER BY created_at_utc ASC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            metrics['oldest_queued_task_age_seconds'] = row['age_seconds'] if row else None
            
            # Task statistics
            cursor = self.db.execute(
                """
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(attempts) as avg_attempts
                FROM task_queue
                WHERE status IN ('completed', 'failed')
                GROUP BY status
                """
            )
            task_stats = {row['status']: dict(row) for row in cursor.fetchall()}
            metrics['task_statistics'] = task_stats
            
            # Calculate success/failure rates
            total_completed = task_stats.get('completed', {}).get('count', 0)
            total_failed = task_stats.get('failed', {}).get('count', 0)
            total_finished = total_completed + total_failed
            
            if total_finished > 0:
                metrics['success_rate'] = total_completed / total_finished
                metrics['failure_rate'] = total_failed / total_finished
            else:
                metrics['success_rate'] = None
                metrics['failure_rate'] = None
            
            # Worker statistics
            cursor = self.db.execute("SELECT COUNT(*) as count FROM workers")
            metrics['total_workers'] = cursor.fetchone()['count']
            
            active_workers = self.get_active_workers(active_threshold_seconds=60)
            metrics['active_workers'] = len(active_workers)
            
            stale_workers = self.get_stale_workers(stale_threshold_seconds=300)
            metrics['stale_workers'] = len(stale_workers)
            
            return metrics
            
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get queue metrics: {e}") from e

    def get_worker_activity(self) -> List[Dict[str, Any]]:
        """
        Get worker activity summary.
        
        Returns list of dicts with worker ID, capabilities, last heartbeat,
        and time since last heartbeat.
        
        Returns:
            List of worker activity dicts
            
        Raises:
            QueueDatabaseError: If query fails
        """
        try:
            cursor = self.db.execute(
                """
                SELECT 
                    worker_id,
                    capabilities,
                    heartbeat_utc,
                    CAST((julianday('now') - julianday(heartbeat_utc)) * 86400 AS INTEGER) as seconds_since_heartbeat
                FROM workers
                ORDER BY heartbeat_utc DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get worker activity: {e}") from e
