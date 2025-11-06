"""SQLite database connection manager for task queue."""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from typing import List, ContextManager, Optional, Tuple, Any
import threading

from .exceptions import QueueDatabaseError, QueueBusyError, QueueSchemaError
from .schema import PRAGMAS, SCHEMA_STATEMENTS


class QueueDatabase:
    """
    SQLite database connection manager for task queue.
    
    Follows SOLID principles:
    - Single Responsibility: Manages DB connection lifecycle
    - Dependency Inversion: Uses Protocol for extensibility
    - Open/Closed: Can be extended without modification
    
    Thread-safe connection management with proper transaction support.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to database file. If None, uses default path.
                    Default: C:\\Data\\PrismQ\\queue\\queue.db (Windows)
                            or /tmp/prismq/queue/queue.db (Linux/macOS)
        """
        if db_path is None:
            db_path = os.environ.get("PRISMQ_QUEUE_DB_PATH")
            if db_path is None:
                # Default path based on OS
                if os.name == "nt":  # Windows
                    db_path = r"C:\Data\PrismQ\queue\queue.db"
                else:  # Linux/macOS
                    db_path = "/tmp/prismq/queue/queue.db"

        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Create database directory if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _apply_pragmas(self, conn: sqlite3.Connection) -> None:
        """
        Apply Windows-optimized PRAGMA settings to connection.
        
        Args:
            conn: SQLite connection to configure
        """
        for pragma, value in PRAGMAS.items():
            conn.execute(f"PRAGMA {pragma} = {value}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get the active connection, creating it if necessary.
        
        Returns:
            Active SQLite connection with PRAGMAs applied
            
        Raises:
            QueueDatabaseError: If connection cannot be established
        """
        with self._lock:
            if self._connection is None:
                try:
                    self._connection = sqlite3.connect(
                        str(self.db_path),
                        check_same_thread=False,  # Allow multi-threaded access
                        timeout=5.0,  # 5 second timeout for lock acquisition
                    )
                    # Enable row factory for dict-like access
                    self._connection.row_factory = sqlite3.Row
                    # Apply PRAGMAs
                    self._apply_pragmas(self._connection)
                except sqlite3.Error as e:
                    raise QueueDatabaseError(f"Failed to connect to database: {e}") from e

            return self._connection

    def initialize_schema(self) -> None:
        """
        Create tables and indexes if they don't exist.
        
        Raises:
            QueueSchemaError: If schema creation fails
        """
        conn = self.get_connection()
        try:
            with self._lock:
                for statement in SCHEMA_STATEMENTS:
                    conn.execute(statement)
                conn.commit()
        except sqlite3.Error as e:
            raise QueueSchemaError(f"Failed to initialize schema: {e}") from e

    def execute(
        self, sql: str, params: Tuple[Any, ...] = ()
    ) -> sqlite3.Cursor:
        """
        Execute a single SQL statement.
        
        Args:
            sql: SQL statement to execute
            params: Parameters for the SQL statement
            
        Returns:
            Cursor with query results
            
        Raises:
            QueueBusyError: If database is locked
            QueueDatabaseError: For other database errors
        """
        conn = self.get_connection()
        try:
            with self._lock:
                return conn.execute(sql, params)
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower() or "busy" in str(e).lower():
                raise QueueBusyError(f"Database is busy: {e}") from e
            raise QueueDatabaseError(f"Database error: {e}") from e
        except sqlite3.Error as e:
            raise QueueDatabaseError(f"Database error: {e}") from e

    def execute_many(self, sql: str, param_list: List[Tuple[Any, ...]]) -> None:
        """
        Execute SQL with multiple parameter sets.
        
        Args:
            sql: SQL statement to execute
            param_list: List of parameter tuples
            
        Raises:
            QueueBusyError: If database is locked
            QueueDatabaseError: For other database errors
        """
        conn = self.get_connection()
        try:
            with self._lock:
                conn.executemany(sql, param_list)
                conn.commit()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower() or "busy" in str(e).lower():
                raise QueueBusyError(f"Database is busy: {e}") from e
            raise QueueDatabaseError(f"Database error: {e}") from e
        except sqlite3.Error as e:
            raise QueueDatabaseError(f"Database error: {e}") from e

    @contextmanager
    def connection(self) -> ContextManager[sqlite3.Connection]:
        """
        Context manager for read-only database operations.
        
        Provides a connection without starting a transaction.
        Useful for SELECT queries and operations that don't modify data.
        
        Yields:
            SQLite connection
            
        Raises:
            QueueDatabaseError: If connection fails
            
        Example:
            with db.connection() as conn:
                cursor = conn.execute("SELECT * FROM task_queue")
                rows = cursor.fetchall()
        """
        conn = self.get_connection()
        try:
            yield conn
        except sqlite3.Error as e:
            raise QueueDatabaseError(f"Database error: {e}") from e
    
    @contextmanager
    def transaction(self) -> ContextManager[sqlite3.Connection]:
        """
        Context manager for transactions with IMMEDIATE isolation.
        
        Ensures atomic operations for task claiming.
        
        Yields:
            SQLite connection within transaction context
            
        Raises:
            QueueBusyError: If database is locked
            QueueDatabaseError: For other database errors
        """
        conn = self.get_connection()
        try:
            with self._lock:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.commit()
        except sqlite3.OperationalError as e:
            conn.rollback()
            if "database is locked" in str(e).lower() or "busy" in str(e).lower():
                raise QueueBusyError(f"Database is busy: {e}") from e
            raise QueueDatabaseError(f"Database error: {e}") from e
        except Exception as e:
            conn.rollback()
            raise

    def close(self) -> None:
        """Close database connection."""
        with self._lock:
            if self._connection is not None:
                try:
                    self._connection.close()
                except sqlite3.Error:
                    pass  # Ignore errors during close
                finally:
                    self._connection = None

    def __enter__(self) -> "QueueDatabase":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
