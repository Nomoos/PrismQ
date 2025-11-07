"""Queue metrics and statistics collection for observability."""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from .database import QueueDatabase
from .exceptions import QueueDatabaseError


class QueueMetrics:
    """
    Provides real-time queue metrics and statistics.
    
    Follows SOLID principles:
    - Single Responsibility: Aggregates queue metrics
    - Dependency Inversion: Depends on QueueDatabase abstraction
    - Open/Closed: Can be extended with new metrics without modification
    
    Efficient SQL queries using indexes for performance.
    """

    def __init__(self, db: QueueDatabase):
        """
        Initialize with database connection.
        
        Args:
            db: QueueDatabase instance for metrics queries
        """
        self.db = db

    def get_queue_depth(
        self,
        task_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Get number of tasks in queue.
        
        Uses indexed queries for performance.
        
        Args:
            task_type: Filter by task type (optional)
            status: Filter by status (optional)
            
        Returns:
            Count of matching tasks
            
        Raises:
            QueueDatabaseError: If query fails
        """
        # Build query with optional filters
        if task_type and status:
            sql = "SELECT COUNT(*) FROM task_queue WHERE type = ? AND status = ?"
            params = (task_type, status)
        elif task_type:
            sql = "SELECT COUNT(*) FROM task_queue WHERE type = ?"
            params = (task_type,)
        elif status:
            sql = "SELECT COUNT(*) FROM task_queue WHERE status = ?"
            params = (status,)
        else:
            sql = "SELECT COUNT(*) FROM task_queue"
            params = ()
        
        try:
            cursor = self.db.execute(sql, params)
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get queue depth: {e}") from e

    def get_queue_depth_by_status(self) -> Dict[str, int]:
        """
        Get task counts grouped by status.
        
        Uses the v_queue_status_summary view for efficient aggregation.
        
        Returns:
            Dict mapping status -> count
            Example: {'queued': 50, 'processing': 5, 'completed': 200}
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = "SELECT status, task_count FROM v_queue_status_summary"
        
        try:
            cursor = self.db.execute(sql)
            rows = cursor.fetchall()
            
            return {row["status"]: row["task_count"] for row in rows}
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get queue depth by status: {e}") from e

    def get_queue_depth_by_type(self) -> Dict[str, int]:
        """
        Get task counts grouped by type.
        
        Returns:
            Dict mapping task type -> count
            Example: {'classify': 100, 'score': 50}
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = """
            SELECT type, COUNT(*) as count
            FROM task_queue
            GROUP BY type
        """
        
        try:
            cursor = self.db.execute(sql)
            rows = cursor.fetchall()
            
            return {row["type"]: row["count"] for row in rows}
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get queue depth by type: {e}") from e

    def get_oldest_queued_task_age(self) -> Optional[int]:
        """
        Get age in seconds of the oldest queued task.
        
        Indicates queue backlog and processing lag.
        
        Returns:
            Age in seconds, or None if queue is empty
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = """
            SELECT ROUND((JULIANDAY('now') - JULIANDAY(created_at_utc)) * 86400) as age_seconds
            FROM task_queue
            WHERE status = 'queued'
            ORDER BY created_at_utc ASC
            LIMIT 1
        """
        
        try:
            cursor = self.db.execute(sql)
            result = cursor.fetchone()
            return int(result["age_seconds"]) if result else None
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get oldest queued task age: {e}") from e

    def get_success_failure_rates(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate success/failure rates over time period.
        
        Args:
            hours: Time period in hours (default: 24)
            
        Returns:
            Dict with success_count, failure_count, total_count,
            success_rate, failure_rate
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = """
            SELECT
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status IN ('failed', 'dead_letter') THEN 1 ELSE 0 END) as failure_count,
                COUNT(*) as total_count
            FROM task_queue
            WHERE finished_at_utc >= datetime('now', ?)
        """
        
        try:
            cursor = self.db.execute(sql, (f"-{hours} hours",))
            result = cursor.fetchone()
            
            if not result:
                return {
                    "success_count": 0,
                    "failure_count": 0,
                    "total_count": 0,
                    "success_rate": 0.0,
                    "failure_rate": 0.0,
                }
            
            success_count = result["success_count"] or 0
            failure_count = result["failure_count"] or 0
            total_count = result["total_count"] or 0
            
            success_rate = (success_count / total_count) if total_count > 0 else 0.0
            failure_rate = (failure_count / total_count) if total_count > 0 else 0.0
            
            return {
                "success_count": success_count,
                "failure_count": failure_count,
                "total_count": total_count,
                "success_rate": success_rate,
                "failure_rate": failure_rate,
            }
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get success/failure rates: {e}") from e

    def get_worker_activity(self) -> List[Dict[str, Any]]:
        """
        Get current worker activity and heartbeats.
        
        Uses the v_worker_status view for efficient querying.
        
        Returns:
            List of worker info with capabilities, heartbeat, active tasks,
            and seconds since last heartbeat
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = "SELECT * FROM v_worker_status ORDER BY active_tasks DESC"
        
        try:
            cursor = self.db.execute(sql)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get worker activity: {e}") from e

    def get_throughput_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """
        Calculate throughput metrics.
        
        Args:
            hours: Time period in hours (default: 1)
            
        Returns:
            Dict with tasks_completed, tasks_per_minute, avg_processing_time_seconds
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = """
            SELECT
                COUNT(*) as tasks_completed,
                ROUND(AVG(JULIANDAY(finished_at_utc) - JULIANDAY(processing_started_utc)) * 86400, 2) as avg_processing_seconds
            FROM task_queue
            WHERE status = 'completed'
            AND finished_at_utc >= datetime('now', ?)
        """
        
        try:
            cursor = self.db.execute(sql, (f"-{hours} hours",))
            result = cursor.fetchone()
            
            if not result:
                return {
                    "tasks_completed": 0,
                    "tasks_per_minute": 0.0,
                    "avg_processing_time_seconds": 0.0,
                }
            
            tasks_completed = result["tasks_completed"] or 0
            avg_processing_seconds = result["avg_processing_seconds"] or 0.0
            
            # Calculate tasks per minute
            minutes = hours * 60
            tasks_per_minute = (tasks_completed / minutes) if minutes > 0 else 0.0
            
            return {
                "tasks_completed": tasks_completed,
                "tasks_per_minute": round(tasks_per_minute, 2),
                "avg_processing_time_seconds": avg_processing_seconds,
            }
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get throughput metrics: {e}") from e

    def get_retry_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate retry-related metrics.
        
        Args:
            hours: Time period in hours (default: 24)
            
        Returns:
            Dict with total_tasks, tasks_with_retries, retry_rate,
            avg_attempts, max_attempts_reached
            
        Raises:
            QueueDatabaseError: If query fails
        """
        sql = """
            SELECT
                COUNT(*) as total_tasks,
                SUM(CASE WHEN attempts > 1 THEN 1 ELSE 0 END) as tasks_with_retries,
                SUM(CASE WHEN status = 'dead_letter' THEN 1 ELSE 0 END) as max_attempts_reached,
                ROUND(AVG(attempts), 2) as avg_attempts
            FROM task_queue
            WHERE finished_at_utc >= datetime('now', ?)
            OR status IN ('queued', 'processing')
        """
        
        try:
            cursor = self.db.execute(sql, (f"-{hours} hours",))
            result = cursor.fetchone()
            
            if not result:
                return {
                    "total_tasks": 0,
                    "tasks_with_retries": 0,
                    "retry_rate": 0.0,
                    "avg_attempts": 0.0,
                    "max_attempts_reached": 0,
                }
            
            total_tasks = result["total_tasks"] or 0
            tasks_with_retries = result["tasks_with_retries"] or 0
            max_attempts_reached = result["max_attempts_reached"] or 0
            avg_attempts = result["avg_attempts"] or 0.0
            
            retry_rate = (tasks_with_retries / total_tasks) if total_tasks > 0 else 0.0
            
            return {
                "total_tasks": total_tasks,
                "tasks_with_retries": tasks_with_retries,
                "retry_rate": retry_rate,
                "avg_attempts": avg_attempts,
                "max_attempts_reached": max_attempts_reached,
            }
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get retry metrics: {e}") from e

    def get_processing_time_percentiles(
        self,
        hours: int = 24,
        task_type: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Calculate processing time percentiles (p50, p95, p99).
        
        Args:
            hours: Time period in hours (default: 24)
            task_type: Filter by task type (optional)
            
        Returns:
            Dict with p50, p95, p99 processing times in seconds
            
        Raises:
            QueueDatabaseError: If query fails
        """
        # Build query with optional task type filter
        if task_type:
            sql = """
                SELECT
                    ROUND((JULIANDAY(finished_at_utc) - JULIANDAY(processing_started_utc)) * 86400, 2) as processing_seconds
                FROM task_queue
                WHERE status = 'completed'
                AND finished_at_utc >= datetime('now', ?)
                AND type = ?
                ORDER BY processing_seconds
            """
            params = (f"-{hours} hours", task_type)
        else:
            sql = """
                SELECT
                    ROUND((JULIANDAY(finished_at_utc) - JULIANDAY(processing_started_utc)) * 86400, 2) as processing_seconds
                FROM task_queue
                WHERE status = 'completed'
                AND finished_at_utc >= datetime('now', ?)
                ORDER BY processing_seconds
            """
            params = (f"-{hours} hours",)
        
        try:
            cursor = self.db.execute(sql, params)
            times = [row["processing_seconds"] for row in cursor.fetchall()]
            
            if not times:
                return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
            
            # Calculate percentiles
            def percentile(data: List[float], p: float) -> float:
                """Calculate percentile from sorted data."""
                if not data:
                    return 0.0
                k = (len(data) - 1) * p
                f = int(k)
                c = k - f
                if f + 1 < len(data):
                    return data[f] + c * (data[f + 1] - data[f])
                else:
                    return data[f]
            
            return {
                "p50": percentile(times, 0.50),
                "p95": percentile(times, 0.95),
                "p99": percentile(times, 0.99),
            }
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get processing time percentiles: {e}") from e

    def get_queue_health_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive queue health summary.
        
        Combines multiple metrics into a single health report.
        
        Returns:
            Dict with comprehensive health metrics including:
            - Queue depths by status
            - Oldest task age
            - Success/failure rates (24h)
            - Throughput (1h)
            - Active workers
            - Retry metrics
            
        Raises:
            QueueDatabaseError: If query fails
        """
        try:
            return {
                "queue_depth": self.get_queue_depth_by_status(),
                "oldest_queued_task_age_seconds": self.get_oldest_queued_task_age(),
                "success_failure_rates_24h": self.get_success_failure_rates(hours=24),
                "throughput_1h": self.get_throughput_metrics(hours=1),
                "active_workers": len(self.get_worker_activity()),
                "retry_metrics_24h": self.get_retry_metrics(hours=24),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            raise QueueDatabaseError(f"Failed to get queue health summary: {e}") from e
