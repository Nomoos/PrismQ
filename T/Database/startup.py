"""Startup - Safe database schema initialization for PrismQ application startup.

This module provides a safe database schema initialization function
that should ONLY be called during application startup, not during normal
repository or business logic operations.

The module ensures:
- Schema initialization with proper error handling and logging
- Idempotent initialization (safe to call multiple times)
- Clear separation between startup initialization and runtime operations

Usage:
    This module should ONLY be used during:
    - Application bootstrapping (main entry point)
    - CLI tool initialization
    - Framework startup hooks (e.g., FastAPI lifespan, Flask before_first_request)
    
    It should NOT be called from:
    - Repository methods
    - Business logic/service layers
    - Individual request handlers

Example:
    >>> import sqlite3
    >>> import logging
    >>> from T.Database.startup import initialize_application_database
    >>> 
    >>> # Configure logging
    >>> logging.basicConfig(level=logging.INFO)
    >>> 
    >>> # Initialize database at application startup
    >>> conn = sqlite3.connect("prismq.db")
    >>> success = initialize_application_database(conn)
    >>> if success:
    ...     print("Database ready")
    ... else:
    ...     print("Database initialization failed - check logs")
"""

import sqlite3
import logging
from typing import Optional

from T.Database.schema_manager import SchemaManager

# Module logger
logger = logging.getLogger(__name__)


class DatabaseInitializationError(Exception):
    """Exception raised when database initialization fails.
    
    This exception wraps underlying database errors and provides
    context about the initialization failure for logging and
    error handling purposes.
    
    Attributes:
        message: Human-readable error message
        original_error: The original exception that caused the failure
    """
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            original_error: The original exception that caused the failure
        """
        self.message = message
        self.original_error = original_error
        super().__init__(message)


def initialize_application_database(
    connection: sqlite3.Connection,
    verify: bool = True
) -> bool:
    """Initialize the database schema safely during application startup.
    
    This function performs database schema initialization with proper
    error handling and logging. If any step fails, the error is logged
    and the function returns False.
    
    This function should ONLY be called during application startup:
    - Main entry point initialization
    - CLI tool initialization  
    - Framework startup hooks
    
    It should NOT be called from repository methods or business logic.
    
    Args:
        connection: SQLite database connection
        verify: If True (default), verify schema after initialization
        
    Returns:
        True if initialization succeeded, False if it failed.
        Errors are logged via the module logger.
    
    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> if initialize_application_database(conn):
        ...     print("Database initialized successfully")
        ... else:
        ...     print("Initialization failed - check logs")
    """
    logger.info("Starting database schema initialization")
    
    try:
        # Create schema manager
        schema_manager = SchemaManager(connection)
        
        # Check if schema already exists (for idempotency)
        if schema_manager.verify_schema():
            logger.info("Database schema already exists - skipping initialization")
            return True
        
        # Log missing tables for visibility
        missing_tables = schema_manager.get_missing_tables()
        if missing_tables:
            logger.info(f"Missing tables to create: {', '.join(missing_tables)}")
        
        # Initialize schema
        # Note: SchemaManager.initialize_schema() uses executescript() which
        # auto-commits each script and calls commit() at the end. If an error
        # occurs mid-way, partial tables may have been created (which is safe
        # since CREATE TABLE IF NOT EXISTS is idempotent).
        schema_manager.initialize_schema()
        
        # Verify schema if requested
        if verify:
            if not schema_manager.verify_schema():
                logger.error("Schema verification failed after initialization")
                return False
            logger.info("Schema verification passed")
        
        logger.info("Database schema initialization completed successfully")
        return True
        
    except sqlite3.Error as e:
        # Handle SQLite-specific errors
        logger.error(f"Database error during schema initialization: {e}")
        
        # Attempt rollback for any uncommitted changes
        # Note: Due to executescript auto-commit behavior, this may not
        # have any effect, but is included for completeness
        try:
            connection.rollback()
        except sqlite3.Error:
            pass  # Rollback failure is expected if nothing to rollback
        
        return False
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during schema initialization: {e}")
        
        # Attempt rollback for any uncommitted changes
        try:
            connection.rollback()
        except Exception:
            pass  # Rollback failure is expected if nothing to rollback
        
        return False


def safe_initialize_database(
    connection: sqlite3.Connection,
    raise_on_error: bool = False
) -> bool:
    """Safe wrapper for database initialization with enhanced error handling.
    
    This is an alternative entry point that provides more control over
    error handling behavior. It can either return a boolean status or
    raise an exception depending on caller preference.
    
    Args:
        connection: SQLite database connection
        raise_on_error: If True, raises DatabaseInitializationError on failure.
                       If False (default), returns False on failure.
                       
    Returns:
        True if initialization succeeded, False if it failed
        (when raise_on_error=False).
        
    Raises:
        DatabaseInitializationError: If initialization fails and 
            raise_on_error=True.
    
    Example:
        >>> # Silent failure mode (returns False)
        >>> success = safe_initialize_database(conn)
        >>> 
        >>> # Exception mode (raises on failure)
        >>> try:
        ...     safe_initialize_database(conn, raise_on_error=True)
        ... except DatabaseInitializationError as e:
        ...     print(f"Failed: {e.message}")
    """
    try:
        success = initialize_application_database(connection, verify=True)
        
        if not success and raise_on_error:
            raise DatabaseInitializationError(
                "Database schema initialization failed - check logs for details"
            )
        
        return success
        
    except DatabaseInitializationError:
        # Re-raise our custom exception
        raise
        
    except Exception as e:
        if raise_on_error:
            raise DatabaseInitializationError(
                f"Unexpected error during initialization: {e}",
                original_error=e
            )
        return False


__all__ = [
    "DatabaseInitializationError",
    "initialize_application_database",
    "safe_initialize_database",
]
