"""Worker heartbeat and monitoring for queue system."""

import json
from typing import List, Dict, Any
from datetime import datetime

from .database import QueueDatabase
from .models import Worker
from .exceptions import QueueDatabaseError


class WorkerHeartbeat:
    """
    Manages worker heartbeat updates and monitoring.
    
    Detects stale workers and enables worker health monitoring.
    
    Follows SOLID principles:
    - Single Responsibility: Manages worker lifecycle and health
    - Dependency Inversion: Depends on QueueDatabase abstraction
    - Open/Closed: Can be extended without modification
    """

    def __init__(self, db: QueueDatabase, stale_threshold_seconds: int = 300):
        """
        Initialize heartbeat manager.
        
        Args:
            db: QueueDatabase instance
            stale_threshold_seconds: Seconds before worker considered stale (default: 5 minutes)
        """
        self.db = db
        self.stale_threshold_seconds = stale_threshold_seconds

    def update_heartbeat(
        self,
        worker_id: str,
        capabilities: Dict[str, Any],
    ) -> None:
        """
        Update or create worker heartbeat.
        
        Uses UPSERT (INSERT OR REPLACE) to handle both new and existing workers.
        
        Args:
            worker_id: Unique worker identifier
            capabilities: Worker capabilities as dict
            
        Raises:
            QueueDatabaseError: If update fails
        """
        # Convert capabilities to JSON
        try:
            capabilities_json = json.dumps(capabilities)
        except (TypeError, ValueError) as e:
            raise QueueDatabaseError(f"Failed to serialize capabilities: {e}") from e
        
        # UPSERT worker with updated heartbeat
        sql = """
            INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(worker_id) 
            DO UPDATE SET 
                capabilities = excluded.capabilities,
                heartbeat_utc = datetime('now')
        """
        
        try:
            self.db.execute(sql, (worker_id, capabilities_json))
        except Exception as e:
            raise QueueDatabaseError(f"Failed to update worker heartbeat: {e}") from e

    def get_active_workers(self) -> List[Worker]:
        """
        Get list of active workers (recent heartbeat).
        
        Active workers have heartbeat within stale_threshold_seconds.
        
        Returns:
            List of Worker objects with recent heartbeat
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = """
            SELECT worker_id, capabilities, heartbeat_utc
            FROM workers
            WHERE (JULIANDAY('now') - JULIANDAY(heartbeat_utc)) * 86400 <= ?
            ORDER BY heartbeat_utc DESC
        """
        
        try:
            cursor = self.db.execute(sql, (self.stale_threshold_seconds,))
            rows = cursor.fetchall()
            
            # Convert rows to Worker objects
            workers = []
            for row in rows:
                worker_dict = dict(row)
                workers.append(Worker.from_dict(worker_dict))
            
            return workers
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get active workers: {e}") from e

    def get_stale_workers(self) -> List[Worker]:
        """
        Get list of stale workers (no recent heartbeat).
        
        Stale workers have not sent heartbeat within stale_threshold_seconds.
        
        Returns:
            List of Worker objects with stale heartbeat
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = """
            SELECT worker_id, capabilities, heartbeat_utc
            FROM workers
            WHERE (JULIANDAY('now') - JULIANDAY(heartbeat_utc)) * 86400 > ?
            ORDER BY heartbeat_utc ASC
        """
        
        try:
            cursor = self.db.execute(sql, (self.stale_threshold_seconds,))
            rows = cursor.fetchall()
            
            # Convert rows to Worker objects
            workers = []
            for row in rows:
                worker_dict = dict(row)
                workers.append(Worker.from_dict(worker_dict))
            
            return workers
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get stale workers: {e}") from e

    def cleanup_stale_workers(self, force: bool = False) -> int:
        """
        Remove stale workers from registry.
        
        Args:
            force: If True, remove all stale workers. If False, only remove
                  workers with no active tasks (default: False)
            
        Returns:
            Number of workers removed
            
        Raises:
            QueueDatabaseError: If cleanup fails
        """
        if force:
            # Remove all stale workers regardless of active tasks
            sql = """
                DELETE FROM workers
                WHERE (JULIANDAY('now') - JULIANDAY(heartbeat_utc)) * 86400 > ?
            """
            params = (self.stale_threshold_seconds,)
        else:
            # Only remove stale workers with no active tasks
            sql = """
                DELETE FROM workers
                WHERE (JULIANDAY('now') - JULIANDAY(heartbeat_utc)) * 86400 > ?
                AND worker_id NOT IN (
                    SELECT DISTINCT locked_by
                    FROM task_queue
                    WHERE status = 'processing'
                    AND locked_by IS NOT NULL
                )
            """
            params = (self.stale_threshold_seconds,)
        
        try:
            cursor = self.db.execute(sql, params)
            deleted_count = cursor.rowcount
            return deleted_count
        except Exception as e:
            raise QueueDatabaseError(f"Failed to cleanup stale workers: {e}") from e

    def get_worker_stats(self, worker_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific worker.
        
        Args:
            worker_id: Worker identifier
            
        Returns:
            Dict with worker stats including:
            - worker_id
            - capabilities
            - heartbeat_utc
            - seconds_since_heartbeat
            - is_active
            - active_tasks_count
            - total_tasks_processed
            - success_rate
            
        Raises:
            QueueDatabaseError: If query fails
        """
        # Get worker info and heartbeat
        worker_sql = """
            SELECT 
                worker_id,
                capabilities,
                heartbeat_utc,
                ROUND((JULIANDAY('now') - JULIANDAY(heartbeat_utc)) * 86400) as seconds_since_heartbeat
            FROM workers
            WHERE worker_id = ?
        """
        
        # Get task stats
        tasks_sql = """
            SELECT
                COUNT(*) as total_tasks,
                COALESCE(SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END), 0) as active_tasks,
                COALESCE(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END), 0) as completed_tasks,
                COALESCE(SUM(CASE WHEN status IN ('failed', 'dead_letter') THEN 1 ELSE 0 END), 0) as failed_tasks
            FROM task_queue
            WHERE locked_by = ?
        """
        
        try:
            # Get worker info
            cursor = self.db.execute(worker_sql, (worker_id,))
            worker_row = cursor.fetchone()
            
            if not worker_row:
                raise QueueDatabaseError(f"Worker {worker_id} not found")
            
            worker_dict = dict(worker_row)
            
            # Get task stats
            cursor = self.db.execute(tasks_sql, (worker_id,))
            tasks_row = cursor.fetchone()
            tasks_dict = dict(tasks_row) if tasks_row else {}
            
            # Calculate metrics
            total_tasks = tasks_dict.get("total_tasks", 0)
            completed_tasks = tasks_dict.get("completed_tasks", 0)
            failed_tasks = tasks_dict.get("failed_tasks", 0)
            
            success_rate = 0.0
            if total_tasks > 0:
                success_rate = completed_tasks / total_tasks
            
            is_active = (
                worker_dict.get("seconds_since_heartbeat", float("inf"))
                <= self.stale_threshold_seconds
            )
            
            return {
                "worker_id": worker_dict["worker_id"],
                "capabilities": worker_dict["capabilities"],
                "heartbeat_utc": worker_dict["heartbeat_utc"],
                "seconds_since_heartbeat": worker_dict["seconds_since_heartbeat"],
                "is_active": is_active,
                "active_tasks_count": tasks_dict.get("active_tasks", 0),
                "total_tasks_processed": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": round(success_rate, 3),
            }
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get worker stats: {e}") from e

    def get_all_workers_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all workers (active and stale).
        
        Returns:
            List of worker summaries with key metrics
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = """
            SELECT
                w.worker_id,
                w.capabilities,
                w.heartbeat_utc,
                ROUND((JULIANDAY('now') - JULIANDAY(w.heartbeat_utc)) * 86400) as seconds_since_heartbeat,
                COUNT(CASE WHEN t.status = 'processing' THEN 1 END) as active_tasks,
                COUNT(t.id) as total_tasks
            FROM workers w
            LEFT JOIN task_queue t ON t.locked_by = w.worker_id
            GROUP BY w.worker_id, w.capabilities, w.heartbeat_utc
            ORDER BY seconds_since_heartbeat ASC
        """
        
        try:
            cursor = self.db.execute(sql)
            rows = cursor.fetchall()
            
            workers_summary = []
            for row in rows:
                row_dict = dict(row)
                is_active = (
                    row_dict["seconds_since_heartbeat"] <= self.stale_threshold_seconds
                )
                row_dict["is_active"] = is_active
                workers_summary.append(row_dict)
            
            return workers_summary
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get workers summary: {e}") from e

    def reclaim_stale_worker_tasks(self) -> int:
        """
        Reclaim tasks from stale workers.
        
        Resets tasks that are still 'processing' but locked by stale workers.
        This allows tasks to be picked up by active workers.
        
        Returns:
            Number of tasks reclaimed
            
        Raises:
            QueueDatabaseError: If reclaim fails
        """
        sql = """
            UPDATE task_queue
            SET 
                status = 'queued',
                locked_by = NULL,
                lease_until_utc = NULL,
                attempts = attempts + 1
            WHERE status = 'processing'
            AND locked_by IN (
                SELECT worker_id
                FROM workers
                WHERE (JULIANDAY('now') - JULIANDAY(heartbeat_utc)) * 86400 > ?
            )
        """
        
        try:
            cursor = self.db.execute(sql, (self.stale_threshold_seconds,))
            reclaimed_count = cursor.rowcount
            return reclaimed_count
        except Exception as e:
            raise QueueDatabaseError(f"Failed to reclaim stale worker tasks: {e}") from e
