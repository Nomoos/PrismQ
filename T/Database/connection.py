"""PrismQ Database Connection Module - PEP 249 Compliant SQLite Connection.

This module provides database connection utilities following PEP 249 (Python
Database API Specification v2.0) for SQLite databases, including .s3db files.

Configuration follows the recommendations in T/_meta/docs/DATABASE_DESIGN.md
"Best Practices Research" section for SQLite (S3DB) specific considerations.

Features:
    - PEP 249 compliant connection interface
    - PRAGMA foreign_keys=ON for referential integrity
    - PRAGMA journal_mode=WAL for better concurrency
    - sqlite3.Row factory for dictionary-like row access
    - check_same_thread=False for multi-process access
    - timeout=30.0 for busy database handling
    - Parameterized queries with ? placeholder (sqlite3 standard)
    - Context manager support for automatic resource cleanup

Usage:
    >>> from T.Database.connection import get_connection, connection_context
    >>> 
    >>> # Recommended: Use context manager for automatic cleanup
    >>> with connection_context("prismq.s3db") as conn:
    ...     cursor = conn.cursor()
    ...     cursor.execute("SELECT * FROM Story WHERE id = ?", (1,))
    ...     row = cursor.fetchone()
    ...     print(dict(row))  # sqlite3.Row allows dict conversion
    >>> 
    >>> # Alternative: Manual connection management (remember to close!)
    >>> conn = get_connection("prismq.s3db")
    >>> try:
    ...     cursor = conn.cursor()
    ...     cursor.execute("SELECT * FROM Story WHERE id = ?", (1,))
    ...     row = cursor.fetchone()
    ...     print(dict(row))
    ... finally:
    ...     conn.close()
    >>> 
    >>> # In-memory database for testing
    >>> with connection_context(":memory:") as conn:
    ...     cursor = conn.cursor()
    ...     cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    ...     conn.commit()

PRAGMA Settings:
    The following PRAGMA statements are executed on connection:
    - PRAGMA foreign_keys=ON: Enforce foreign key constraints
    - PRAGMA journal_mode=WAL: Write-ahead logging for better concurrency
      (only for file-based databases, not :memory:)

Note:
    This module uses sqlite3.connect() directly following PEP 249.
    All SQL queries should use ? as the parameter placeholder per SQLite
    conventions (not %s or :name which are also valid but less common).

Reference:
    See T/_meta/docs/DATABASE_DESIGN.md for full database design documentation.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator


def get_connection(
    db_path: str,
    enable_row_factory: bool = True,
    enable_foreign_keys: bool = True,
    enable_wal_mode: bool = True,
    check_same_thread: bool = False,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """Get a SQLite database connection following PEP 249.
    
    Creates a new connection to the specified SQLite database file.
    The connection is configured with recommended settings for the
    PrismQ application as specified in DATABASE_DESIGN.md.
    
    Args:
        db_path: Path to the SQLite database file (.s3db, .db, .sqlite)
                 or ":memory:" for an in-memory database.
        enable_row_factory: If True (default), sets row_factory to
                           sqlite3.Row for dictionary-like row access.
        enable_foreign_keys: If True (default), executes
                            PRAGMA foreign_keys = ON.
        enable_wal_mode: If True (default), enables WAL journal mode
                        for better concurrency (file-based DBs only).
        check_same_thread: If False (default), allows multi-process access.
                          SQLite objects can be shared across threads.
        timeout: Time in seconds to wait for database lock (default: 30.0).
    
    Returns:
        sqlite3.Connection: A configured database connection.
        
    Raises:
        sqlite3.Error: If the connection cannot be established.
    
    Example:
        >>> conn = get_connection("prismq.s3db")
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT * FROM Story WHERE id = ?", (1,))
        >>> row = cursor.fetchone()
        >>> if row:
        ...     print(row["state"])  # Access by column name
        >>> conn.close()
    
    Note:
        The caller is responsible for closing the connection when done.
        Consider using the connection_context() context manager for
        automatic cleanup.
        
    Reference:
        Configuration follows DATABASE_DESIGN.md "Best Practices Research"
        section for SQLite (S3DB) specific considerations.
    """
    # Create connection using sqlite3.connect (PEP 249)
    # check_same_thread=False allows multi-process access
    # timeout specifies time to wait for database lock
    conn = sqlite3.connect(
        db_path,
        check_same_thread=check_same_thread,
        timeout=timeout,
    )
    
    # Enable sqlite3.Row for dictionary-like access
    if enable_row_factory:
        conn.row_factory = sqlite3.Row
    
    # Enable foreign key constraints (SQLite has them disabled by default)
    if enable_foreign_keys:
        conn.execute("PRAGMA foreign_keys=ON")
    
    # Enable WAL mode for better concurrency (not for in-memory databases)
    if enable_wal_mode and db_path != ":memory:":
        conn.execute("PRAGMA journal_mode=WAL")
    
    return conn


@contextmanager
def connection_context(
    db_path: str,
    enable_row_factory: bool = True,
    enable_foreign_keys: bool = True,
    enable_wal_mode: bool = True,
    check_same_thread: bool = False,
    timeout: float = 30.0,
) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with automatic cleanup.
    
    Provides a context manager that automatically closes the connection
    when the context exits, even if an exception occurs.
    
    Args:
        db_path: Path to the SQLite database file (.s3db, .db, .sqlite)
                 or ":memory:" for an in-memory database.
        enable_row_factory: If True (default), sets row_factory to
                           sqlite3.Row for dictionary-like row access.
        enable_foreign_keys: If True (default), executes
                            PRAGMA foreign_keys = ON.
        enable_wal_mode: If True (default), enables WAL journal mode
                        for better concurrency (file-based DBs only).
        check_same_thread: If False (default), allows multi-process access.
        timeout: Time in seconds to wait for database lock (default: 30.0).
    
    Yields:
        sqlite3.Connection: A configured database connection.
    
    Example:
        >>> with connection_context("prismq.s3db") as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("INSERT INTO Story (state) VALUES (?)", ("IDEA",))
        ...     conn.commit()
        ...     print(f"Inserted story with id {cursor.lastrowid}")
        >>> # Connection is automatically closed here
    
    Note:
        The connection is NOT committed before closing. Call conn.commit()
        explicitly if you want to persist changes.
    """
    conn = get_connection(
        db_path,
        enable_row_factory=enable_row_factory,
        enable_foreign_keys=enable_foreign_keys,
        enable_wal_mode=enable_wal_mode,
        check_same_thread=check_same_thread,
        timeout=timeout,
    )
    try:
        yield conn
    finally:
        conn.close()


def create_database(
    db_path: str,
    exist_ok: bool = True,
) -> sqlite3.Connection:
    """Create a new SQLite database file and return a connection.
    
    Creates the database file and any parent directories if they don't
    exist. Returns a connection to the newly created database.
    
    Args:
        db_path: Path to the SQLite database file to create.
                 Supports .s3db, .db, .sqlite extensions.
        exist_ok: If True (default), existing database is opened.
                 If False, raises FileExistsError if file exists.
    
    Returns:
        sqlite3.Connection: A configured connection to the database.
        
    Raises:
        FileExistsError: If db_path exists and exist_ok is False.
        ValueError: If db_path is ":memory:" (use get_connection instead).
    
    Example:
        >>> conn = create_database("data/prismq.s3db")
        >>> # Database file and data/ directory are created if needed
        >>> conn.close()
    """
    if db_path == ":memory:":
        raise ValueError(
            "Use get_connection(':memory:') for in-memory databases"
        )
    
    path = Path(db_path)
    
    if not exist_ok and path.exists():
        raise FileExistsError(f"Database already exists: {db_path}")
    
    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create and return connection (file is created by sqlite3.connect)
    return get_connection(db_path)


def verify_connection(conn: sqlite3.Connection) -> bool:
    """Verify that a connection is valid and functional.
    
    Executes a simple query to verify the connection is working.
    Also checks that foreign key support is enabled.
    
    Args:
        conn: The connection to verify.
        
    Returns:
        bool: True if connection is valid, False otherwise.
    
    Example:
        >>> conn = get_connection("prismq.s3db")
        >>> if verify_connection(conn):
        ...     print("Connection OK")
        >>> conn.close()
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result is None or result[0] != 1:
            return False
        
        # Verify foreign keys are enabled
        cursor.execute("PRAGMA foreign_keys")
        fk_result = cursor.fetchone()
        
        return fk_result is not None and fk_result[0] == 1
    except sqlite3.Error:
        return False


__all__ = [
    "get_connection",
    "connection_context",
    "create_database",
    "verify_connection",
]
