"""Startup - Safe database schema initialization for PrismQ application startup.

This module provides a safe, transaction-based database schema initialization
that should ONLY be called during application startup, not during normal
repository or business logic operations.

The module ensures:
- Schema initialization runs in a single transaction
- Database errors are caught and logged appropriately
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
    
    This function performs database schema initialization within a single
    transaction. If any step fails, the transaction is rolled back and
    the error is logged.
    
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
        
    Raises:
        DatabaseInitializationError: If initialization fails and caller
            prefers exception handling over boolean return value.
            Only raised if error is not recoverable (e.g., connection closed).
    
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
        
        # Log missing tables
        missing_tables = schema_manager.get_missing_tables()
        if missing_tables:
            logger.info(f"Missing tables to create: {', '.join(missing_tables)}")
        
        # Initialize schema within transaction
        # Note: SchemaManager.initialize_schema() handles the transaction
        # and commits on success
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
        
        # Attempt rollback if possible
        try:
            connection.rollback()
            logger.info("Transaction rolled back successfully")
        except sqlite3.Error as rollback_error:
            logger.warning(f"Rollback failed: {rollback_error}")
        
        return False
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during schema initialization: {e}")
        
        # Attempt rollback if possible
        try:
            connection.rollback()
            logger.info("Transaction rolled back successfully")
        except Exception as rollback_error:
            logger.warning(f"Rollback failed: {rollback_error}")
        
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
