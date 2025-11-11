"""Queue database management.

This module provides the QueueDatabase class for managing the worker task queue database.
It follows SOLID principles:
- Single Responsibility: Database setup and configuration only
- Open/Closed: Extensible via views and indexes without schema changes
- Dependency Inversion: Provides standard SQL interface
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class QueueDatabase:
    """Manages the worker queue database.
    
    This class is responsible for:
    - Initializing the database schema
    - Configuring PRAGMA settings for Windows optimization
    - Providing connection management
    - Offering maintenance operations (vacuum, checkpoint)
    - Providing database statistics
    
    It follows the Single Responsibility Principle by focusing only on
    database setup and configuration, not on task operations or worker logic.
    """
    
    def __init__(self, db_path: str):
        """Initialize queue database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize on first use
        self._initialize()
    
    def _initialize(self):
        """Initialize database with schema and PRAGMA settings."""
        conn = self.get_connection()
        
        try:
            # Set PRAGMA settings (Windows optimized)
            # Enable Write-Ahead Logging for concurrent access
            conn.execute("PRAGMA journal_mode = WAL")
            
            # Handle SQLITE_BUSY gracefully (5 seconds)
            conn.execute("PRAGMA busy_timeout = 5000")
            
            # Optimize for Windows SSD (balance safety and speed)
            conn.execute("PRAGMA synchronous = NORMAL")
            
            # Cache size (10MB for better performance)
            conn.execute("PRAGMA cache_size = -10000")
            
            # Memory-mapped I/O (faster on Windows, 30GB limit for RTX 5090 system)
            conn.execute("PRAGMA mmap_size = 30000000000")
            
            # Auto-vacuum for maintenance
            conn.execute("PRAGMA auto_vacuum = INCREMENTAL")
            
            # Temp store in memory for better performance
            conn.execute("PRAGMA temp_store = MEMORY")
            
            # Load and execute schema
            schema_file = Path(__file__).parent / "schema.sql"
            if schema_file.exists():
                with open(schema_file) as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                logger.info(f"Schema loaded from {schema_file}")
            else:
                # Inline schema if file not found (fallback)
                logger.warning(f"Schema file not found: {schema_file}, using inline schema")
                self._create_schema_inline(conn)
            
            conn.commit()
            logger.info(f"Queue database initialized: {self.db_path}")
            
        finally:
            conn.close()
    
    def _create_schema_inline(self, conn: sqlite3.Connection):
        """Create schema inline (fallback if schema.sql not found).
        
        This provides a basic schema as a fallback. For production,
        the schema.sql file should be used.
        """
        # Create main task_queue table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                parameters TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 5,
                run_after_utc TEXT,
                status TEXT NOT NULL DEFAULT 'queued',
                claimed_by TEXT,
                claimed_at TEXT,
                retry_count INTEGER NOT NULL DEFAULT 0,
                max_retries INTEGER NOT NULL DEFAULT 3,
                result_data TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                CHECK (priority BETWEEN 1 AND 10),
                CHECK (retry_count <= max_retries),
                CHECK (status IN ('queued', 'claimed', 'running', 
                                 'completed', 'failed', 'cancelled'))
            )
        """)
        
        # Create critical index for fast claiming
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_queue_claiming 
            ON task_queue(status, priority DESC, created_at DESC)
            WHERE status = 'queued'
        """)
        
        # Create worker_heartbeats table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS worker_heartbeats (
                worker_id TEXT PRIMARY KEY,
                last_heartbeat TEXT NOT NULL,
                tasks_processed INTEGER NOT NULL DEFAULT 0,
                tasks_failed INTEGER NOT NULL DEFAULT 0,
                current_task_id INTEGER,
                strategy TEXT NOT NULL DEFAULT 'LIFO',
                started_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (current_task_id) REFERENCES task_queue(id)
            )
        """)
        
        # Create task_logs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                worker_id TEXT,
                event_type TEXT NOT NULL,
                message TEXT,
                details TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES task_queue(id),
                FOREIGN KEY (worker_id) REFERENCES worker_heartbeats(worker_id)
            )
        """)
        
        logger.info("Inline schema created")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection.
        
        Each worker should have its own connection to avoid threading issues.
        
        Returns:
            SQLite connection with row factory for dict-like access
        """
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def vacuum(self):
        """Perform VACUUM to reclaim space.
        
        This should be run periodically to maintain database performance.
        """
        conn = self.get_connection()
        try:
            conn.execute("VACUUM")
            logger.info("Database vacuumed")
        finally:
            conn.close()
    
    def checkpoint(self):
        """Perform WAL checkpoint.
        
        This flushes the Write-Ahead Log to the main database file.
        Should be called periodically for maintenance.
        """
        conn = self.get_connection()
        try:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            logger.info("WAL checkpoint completed")
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics including:
            - status_counts: Count of tasks by status
            - active_workers: Number of active workers
            - db_size_bytes: Database size in bytes
            - db_size_mb: Database size in megabytes
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Total tasks by status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM task_queue
                GROUP BY status
            """)
            status_counts = {row['status']: row['count'] 
                           for row in cursor.fetchall()}
            
            # Active workers (heartbeat within last 3 minutes)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM worker_heartbeats
                WHERE julianday('now') - julianday(last_heartbeat) < 0.0021
            """)  # 0.0021 days = ~3 minutes
            result = cursor.fetchone()
            active_workers = result['count'] if result else 0
            
            # Database size
            cursor.execute("""
                SELECT page_count * page_size as size 
                FROM pragma_page_count(), pragma_page_size()
            """)
            result = cursor.fetchone()
            db_size = result['size'] if result else 0
            
            return {
                'status_counts': status_counts,
                'active_workers': active_workers,
                'db_size_bytes': db_size,
                'db_size_mb': round(db_size / (1024 * 1024), 2)
            }
            
        finally:
            conn.close()
    
    def get_pragma_info(self) -> Dict[str, Any]:
        """Get current PRAGMA settings.
        
        Returns:
            Dictionary with PRAGMA settings
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            pragma_settings = {}
            
            # Journal mode
            cursor.execute("PRAGMA journal_mode")
            pragma_settings['journal_mode'] = cursor.fetchone()[0]
            
            # Busy timeout
            cursor.execute("PRAGMA busy_timeout")
            pragma_settings['busy_timeout'] = cursor.fetchone()[0]
            
            # Synchronous mode
            cursor.execute("PRAGMA synchronous")
            pragma_settings['synchronous'] = cursor.fetchone()[0]
            
            # Cache size
            cursor.execute("PRAGMA cache_size")
            pragma_settings['cache_size'] = cursor.fetchone()[0]
            
            return pragma_settings
            
        finally:
            conn.close()
