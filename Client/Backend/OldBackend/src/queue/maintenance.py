"""Database maintenance utilities for task queue."""

import sqlite3
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .database import QueueDatabase
from .exceptions import QueueDatabaseError


class QueueMaintenanceError(QueueDatabaseError):
    """Exception raised when maintenance operations fail."""
    pass


class QueueMaintenance:
    """
    Database maintenance utilities.
    
    Handles WAL checkpoints, VACUUM, ANALYZE, and cleanup operations.
    Follows SOLID principles:
    - Single Responsibility: Manages maintenance operations only
    - Dependency Inversion: Depends on QueueDatabase abstraction
    """

    # Valid checkpoint modes
    CHECKPOINT_PASSIVE = "PASSIVE"
    CHECKPOINT_FULL = "FULL"
    CHECKPOINT_RESTART = "RESTART"
    CHECKPOINT_TRUNCATE = "TRUNCATE"

    def __init__(self, db: QueueDatabase):
        """
        Initialize maintenance manager.
        
        Args:
            db: QueueDatabase instance to maintain
        """
        self.db = db

    def checkpoint(self, mode: str = CHECKPOINT_PASSIVE) -> Dict[str, int]:
        """
        Execute WAL checkpoint.
        
        Checkpoint modes:
        - PASSIVE: Don't block, checkpoint what's possible (default)
        - FULL: Block readers until all WAL is checkpointed
        - RESTART: Like FULL, also resets WAL
        - TRUNCATE: Like RESTART, also truncates WAL to 0 bytes
        
        Args:
            mode: Checkpoint mode (PASSIVE, FULL, RESTART, or TRUNCATE)
            
        Returns:
            Dictionary with checkpoint statistics:
            - busy: 1 if checkpoint couldn't complete, 0 if successful
            - log: Number of WAL pages written to database
            - checkpointed: Number of WAL pages successfully checkpointed
            
        Raises:
            QueueMaintenanceError: If checkpoint fails
        """
        valid_modes = {
            self.CHECKPOINT_PASSIVE,
            self.CHECKPOINT_FULL,
            self.CHECKPOINT_RESTART,
            self.CHECKPOINT_TRUNCATE
        }
        
        if mode not in valid_modes:
            raise QueueMaintenanceError(
                f"Invalid checkpoint mode: {mode}. Must be one of {valid_modes}"
            )
        
        try:
            conn = self.db.get_connection()
            cursor = conn.execute(f"PRAGMA wal_checkpoint({mode})")
            result = cursor.fetchone()
            
            # SQLite returns (busy, log, checkpointed)
            return {
                "busy": result[0] if result else 0,
                "log": result[1] if result and len(result) > 1 else 0,
                "checkpointed": result[2] if result and len(result) > 2 else 0,
            }
            
        except sqlite3.Error as e:
            raise QueueMaintenanceError(f"Checkpoint failed: {e}") from e

    def vacuum(self) -> None:
        """
        Reclaim free space and defragment database.
        
        WARNING: VACUUM requires exclusive database lock and can take significant time.
        This operation should be run during maintenance windows or low-traffic periods.
        
        The VACUUM command rebuilds the database file, repacking it into a minimal
        amount of disk space. This removes free pages created by DELETE and UPDATE
        operations.
        
        Raises:
            QueueMaintenanceError: If VACUUM fails
        """
        try:
            conn = self.db.get_connection()
            
            # VACUUM cannot run in a transaction
            # Set isolation_level to None for autocommit mode
            old_isolation = conn.isolation_level
            try:
                conn.isolation_level = None
                conn.execute("VACUUM")
            finally:
                conn.isolation_level = old_isolation
                
        except sqlite3.Error as e:
            raise QueueMaintenanceError(f"VACUUM failed: {e}") from e

    def analyze(self, table: Optional[str] = None) -> None:
        """
        Update query planner statistics.
        
        ANALYZE gathers statistics about the content of indexes and stores them
        in the database. The query planner uses these statistics to make better
        query execution choices.
        
        This operation is non-blocking and relatively fast.
        
        Args:
            table: Optional table name to analyze (default: all tables)
            
        Raises:
            QueueMaintenanceError: If ANALYZE fails
        """
        try:
            conn = self.db.get_connection()
            
            if table:
                conn.execute(f"ANALYZE {table}")
            else:
                conn.execute("ANALYZE")
            
            conn.commit()
            
        except sqlite3.Error as e:
            raise QueueMaintenanceError(f"ANALYZE failed: {e}") from e

    def integrity_check(self) -> List[str]:
        """
        Run database integrity check.
        
        Verifies the integrity of the database file. Returns a list of any
        issues found, or ["ok"] if the database is intact.
        
        Returns:
            List of integrity check messages (["ok"] if no issues)
            
        Raises:
            QueueMaintenanceError: If integrity check fails to run
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.execute("PRAGMA integrity_check")
            
            # Fetch all results (SQLite may return multiple rows for errors)
            results = [row[0] for row in cursor.fetchall()]
            
            return results if results else ["ok"]
            
        except sqlite3.Error as e:
            raise QueueMaintenanceError(f"Integrity check failed: {e}") from e

    def cleanup_stale_leases(self, timeout_seconds: int = 300) -> int:
        """
        Clean up expired task leases and requeue tasks.
        
        Finds tasks with expired leases (lease_until_utc in the past) and
        resets them to 'queued' status so they can be claimed again.
        
        This prevents task starvation when workers crash or lose connectivity
        without properly releasing their leases.
        
        Args:
            timeout_seconds: Lease expiration threshold (default: 300 = 5 minutes)
                           Tasks with leases older than this are considered stale
            
        Returns:
            Number of tasks requeued
            
        Raises:
            QueueMaintenanceError: If cleanup fails
        """
        try:
            conn = self.db.get_connection()
            
            # Calculate cutoff time
            cutoff = datetime.utcnow() - timedelta(seconds=timeout_seconds)
            cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
            
            # Find and requeue stale leases
            # Using BEGIN IMMEDIATE to ensure atomic operation
            with self.db.transaction() as trans_conn:
                cursor = trans_conn.execute(
                    """
                    UPDATE task_queue
                    SET status = 'queued',
                        locked_by = NULL,
                        lease_until_utc = NULL,
                        reserved_at_utc = NULL,
                        updated_at_utc = datetime('now')
                    WHERE status = 'processing'
                      AND lease_until_utc IS NOT NULL
                      AND lease_until_utc < ?
                    """,
                    (cutoff_str,)
                )
                
                requeued_count = cursor.rowcount
            
            return requeued_count
            
        except sqlite3.Error as e:
            raise QueueMaintenanceError(f"Stale lease cleanup failed: {e}") from e

    def get_database_stats(self) -> Dict[str, any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics:
            - page_count: Total pages in database
            - page_size: Size of each page in bytes
            - total_size_mb: Total database size in megabytes
            - freelist_count: Number of free pages
            - wal_mode: Whether WAL mode is enabled
            - wal_size_mb: Size of WAL file in megabytes (if exists)
            
        Raises:
            QueueMaintenanceError: If stats retrieval fails
        """
        try:
            conn = self.db.get_connection()
            stats = {}
            
            # Page count
            cursor = conn.execute("PRAGMA page_count")
            stats["page_count"] = cursor.fetchone()[0]
            
            # Page size
            cursor = conn.execute("PRAGMA page_size")
            stats["page_size"] = cursor.fetchone()[0]
            
            # Calculate total size
            stats["total_size_mb"] = (stats["page_count"] * stats["page_size"]) / (1024 * 1024)
            
            # Freelist count
            cursor = conn.execute("PRAGMA freelist_count")
            stats["freelist_count"] = cursor.fetchone()[0]
            
            # Journal mode
            cursor = conn.execute("PRAGMA journal_mode")
            stats["wal_mode"] = cursor.fetchone()[0].upper() == "WAL"
            
            # WAL file size (if exists)
            wal_path = self.db.db_path.with_suffix(self.db.db_path.suffix + "-wal")
            if wal_path.exists():
                stats["wal_size_mb"] = wal_path.stat().st_size / (1024 * 1024)
            else:
                stats["wal_size_mb"] = 0.0
            
            return stats
            
        except sqlite3.Error as e:
            raise QueueMaintenanceError(f"Failed to get database stats: {e}") from e

    def optimize(self, full: bool = False) -> Dict[str, any]:
        """
        Run optimization operations.
        
        Executes ANALYZE and optionally VACUUM based on database stats.
        
        Args:
            full: If True, run VACUUM (slow, blocks writes)
                 If False, only run ANALYZE (fast, non-blocking)
            
        Returns:
            Dictionary with operation statistics:
            - analyzed: Whether ANALYZE was run
            - vacuumed: Whether VACUUM was run
            - stats_before: Database stats before optimization
            - stats_after: Database stats after optimization
            
        Raises:
            QueueMaintenanceError: If optimization fails
        """
        try:
            # Get stats before optimization
            stats_before = self.get_database_stats()
            
            # Always run ANALYZE
            self.analyze()
            
            # Run VACUUM if requested
            vacuumed = False
            if full:
                self.vacuum()
                vacuumed = True
            
            # Get stats after optimization
            stats_after = self.get_database_stats()
            
            return {
                "analyzed": True,
                "vacuumed": vacuumed,
                "stats_before": stats_before,
                "stats_after": stats_after,
            }
            
        except QueueMaintenanceError:
            # Re-raise our own exceptions
            raise
        except Exception as e:
            raise QueueMaintenanceError(f"Optimization failed: {e}") from e
