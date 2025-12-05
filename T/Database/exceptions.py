"""Database domain exceptions for PrismQ.

This module defines domain-specific exceptions for database operations,
abstracting away SQLite-specific error codes from the business logic layer.

Exception Hierarchy:
    DatabaseException (base)
    ├── EntityNotFoundError - Entity lookup failed
    ├── DuplicateEntityError - UNIQUE constraint violation
    ├── ForeignKeyViolationError - FK constraint violation
    ├── ConstraintViolationError - CHECK or other constraint violation
    ├── DatabaseConnectionError - Connection issues
    └── DataIntegrityError - Data integrity issues

Usage:
    >>> from T.Database.exceptions import (
    ...     EntityNotFoundError,
    ...     DuplicateEntityError,
    ...     ForeignKeyViolationError,
    ... )
    >>> 
    >>> # In repository code
    >>> try:
    ...     cursor.execute("INSERT INTO Story ...")
    ... except sqlite3.IntegrityError as e:
    ...     if "FOREIGN KEY" in str(e):
    ...         raise ForeignKeyViolationError("idea_id", idea_id) from e
    ...     elif "UNIQUE" in str(e):
    ...         raise DuplicateEntityError("Story", story_id) from e
    ...     raise ConstraintViolationError(str(e)) from e

Note:
    Business logic should catch these domain exceptions rather than
    sqlite3.Error or other database-specific exceptions.
"""

from typing import Optional, Any


class DatabaseException(Exception):
    """Base exception for all database-related errors.
    
    This is the base class for all domain exceptions in the database layer.
    Business logic can catch this to handle any database error generically.
    
    Attributes:
        message: Human-readable error description.
        original_error: The underlying exception that caused this error.
    """
    
    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None
    ):
        """Initialize database exception.
        
        Args:
            message: Human-readable error description.
            original_error: The underlying exception (e.g., sqlite3.Error).
        """
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class EntityNotFoundError(DatabaseException):
    """Exception raised when an entity is not found in the database.
    
    Attributes:
        entity_type: The type/name of the entity (e.g., "Story", "Title").
        entity_id: The ID that was not found.
    
    Example:
        >>> raise EntityNotFoundError("Story", 123)
        EntityNotFoundError: Story with id 123 not found
    """
    
    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        original_error: Optional[Exception] = None
    ):
        """Initialize entity not found error.
        
        Args:
            entity_type: The type/name of the entity.
            entity_id: The ID that was not found.
            original_error: The underlying exception.
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        message = f"{entity_type} with id {entity_id} not found"
        super().__init__(message, original_error)


class DuplicateEntityError(DatabaseException):
    """Exception raised when attempting to insert a duplicate entity.
    
    This typically occurs when a UNIQUE constraint is violated.
    
    Attributes:
        entity_type: The type/name of the entity.
        entity_id: The duplicate ID or identifying information.
        constraint: Optional name of the violated constraint.
    
    Example:
        >>> raise DuplicateEntityError("Title", constraint="story_id, version")
        DuplicateEntityError: Duplicate Title: violates unique constraint on (story_id, version)
    """
    
    def __init__(
        self,
        entity_type: str,
        entity_id: Optional[Any] = None,
        constraint: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize duplicate entity error.
        
        Args:
            entity_type: The type/name of the entity.
            entity_id: The duplicate ID or identifying information.
            constraint: Name of the violated unique constraint.
            original_error: The underlying exception.
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.constraint = constraint
        
        if constraint:
            message = f"Duplicate {entity_type}: violates unique constraint on ({constraint})"
        elif entity_id:
            message = f"Duplicate {entity_type} with id {entity_id}"
        else:
            message = f"Duplicate {entity_type}: unique constraint violated"
        
        super().__init__(message, original_error)


class ForeignKeyViolationError(DatabaseException):
    """Exception raised when a foreign key constraint is violated.
    
    This typically occurs when:
    - Inserting a record with a non-existent foreign key reference
    - Deleting a record that is still referenced by other records
    
    Attributes:
        column: The FK column name (e.g., "idea_id", "story_id").
        value: The invalid FK value.
        referenced_table: Optional name of the referenced table.
    
    Example:
        >>> raise ForeignKeyViolationError("story_id", 999, "Story")
        ForeignKeyViolationError: Foreign key violation on story_id=999: referenced Story not found
    """
    
    def __init__(
        self,
        column: str,
        value: Any,
        referenced_table: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize foreign key violation error.
        
        Args:
            column: The FK column name.
            value: The invalid FK value.
            referenced_table: Name of the referenced table.
            original_error: The underlying exception.
        """
        self.column = column
        self.value = value
        self.referenced_table = referenced_table
        
        if referenced_table:
            message = f"Foreign key violation on {column}={value}: referenced {referenced_table} not found"
        else:
            message = f"Foreign key violation on {column}={value}"
        
        super().__init__(message, original_error)


class ConstraintViolationError(DatabaseException):
    """Exception raised when a CHECK or other constraint is violated.
    
    This covers constraint violations that are not FK or UNIQUE,
    such as CHECK constraints (e.g., score must be 0-100).
    
    Attributes:
        constraint: Description or name of the violated constraint.
        column: Optional column name.
        value: Optional invalid value.
    
    Example:
        >>> raise ConstraintViolationError("score must be 0-100", "score", 150)
        ConstraintViolationError: Constraint violation: score must be 0-100 (score=150)
    """
    
    def __init__(
        self,
        constraint: str,
        column: Optional[str] = None,
        value: Optional[Any] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize constraint violation error.
        
        Args:
            constraint: Description or name of the violated constraint.
            column: Column name if applicable.
            value: Invalid value if applicable.
            original_error: The underlying exception.
        """
        self.constraint = constraint
        self.column = column
        self.value = value
        
        if column and value is not None:
            message = f"Constraint violation: {constraint} ({column}={value})"
        else:
            message = f"Constraint violation: {constraint}"
        
        super().__init__(message, original_error)


class DatabaseConnectionError(DatabaseException):
    """Exception raised when database connection fails.
    
    This covers connection issues like:
    - Database file not found
    - Permission denied
    - Database locked
    
    Attributes:
        db_path: Path to the database file.
    
    Example:
        >>> raise DatabaseConnectionError("/path/to/db.s3db", "database is locked")
        DatabaseConnectionError: Failed to connect to /path/to/db.s3db: database is locked
    """
    
    def __init__(
        self,
        db_path: str,
        reason: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize database connection error.
        
        Args:
            db_path: Path to the database file.
            reason: Description of why connection failed.
            original_error: The underlying exception.
        """
        self.db_path = db_path
        self.reason = reason
        
        if reason:
            message = f"Failed to connect to {db_path}: {reason}"
        else:
            message = f"Failed to connect to {db_path}"
        
        super().__init__(message, original_error)


class DataIntegrityError(DatabaseException):
    """Exception raised when data integrity is compromised.
    
    This covers general data integrity issues that don't fit
    other specific categories.
    
    Example:
        >>> raise DataIntegrityError("Version sequence is not contiguous")
        DataIntegrityError: Data integrity error: Version sequence is not contiguous
    """
    
    def __init__(
        self,
        description: str,
        original_error: Optional[Exception] = None
    ):
        """Initialize data integrity error.
        
        Args:
            description: Description of the integrity issue.
            original_error: The underlying exception.
        """
        self.description = description
        message = f"Data integrity error: {description}"
        super().__init__(message, original_error)


class InvalidStateTransitionError(DatabaseException):
    """Exception raised when an invalid state transition is attempted.
    
    Attributes:
        from_state: The current state.
        to_state: The attempted target state.
        entity_id: Optional entity ID.
    
    Example:
        >>> raise InvalidStateTransitionError("CREATED", "PUBLISHED", story_id=1)
        InvalidStateTransitionError: Invalid state transition from 'CREATED' to 'PUBLISHED' for Story 1
    """
    
    def __init__(
        self,
        from_state: str,
        to_state: str,
        entity_id: Optional[Any] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize invalid state transition error.
        
        Args:
            from_state: The current state.
            to_state: The attempted target state.
            entity_id: Entity ID if applicable.
            original_error: The underlying exception.
        """
        self.from_state = from_state
        self.to_state = to_state
        self.entity_id = entity_id
        
        if entity_id is not None:
            message = f"Invalid state transition from '{from_state}' to '{to_state}' for Story {entity_id}"
        else:
            message = f"Invalid state transition from '{from_state}' to '{to_state}'"
        
        super().__init__(message, original_error)


def map_sqlite_error(error: Exception, context: Optional[dict] = None) -> DatabaseException:
    """Map a SQLite error to the appropriate domain exception.
    
    This helper function analyzes SQLite error messages and maps them
    to the appropriate domain exception type.
    
    Args:
        error: The SQLite exception (sqlite3.Error subclass).
        context: Optional context dict with keys like 'entity_type', 'entity_id',
                 'column', 'value', 'table'.
    
    Returns:
        The appropriate domain exception.
    
    Example:
        >>> try:
        ...     cursor.execute("INSERT INTO Title ...")
        ... except sqlite3.IntegrityError as e:
        ...     raise map_sqlite_error(e, {'entity_type': 'Title'})
    """
    context = context or {}
    error_str = str(error).lower()
    
    # Foreign key violation
    if "foreign key" in error_str:
        return ForeignKeyViolationError(
            column=context.get("column", "unknown"),
            value=context.get("value"),
            referenced_table=context.get("table"),
            original_error=error
        )
    
    # Unique constraint violation
    if "unique" in error_str:
        return DuplicateEntityError(
            entity_type=context.get("entity_type", "Entity"),
            entity_id=context.get("entity_id"),
            constraint=context.get("constraint"),
            original_error=error
        )
    
    # Check constraint violation
    if "check" in error_str or "constraint" in error_str:
        return ConstraintViolationError(
            constraint=str(error),
            column=context.get("column"),
            value=context.get("value"),
            original_error=error
        )
    
    # Database locked or busy
    if "locked" in error_str or "busy" in error_str:
        return DatabaseConnectionError(
            db_path=context.get("db_path", "unknown"),
            reason="database is locked",
            original_error=error
        )
    
    # Default to generic database exception
    return DatabaseException(str(error), original_error=error)


__all__ = [
    "DatabaseException",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "ForeignKeyViolationError",
    "ConstraintViolationError",
    "DatabaseConnectionError",
    "DataIntegrityError",
    "InvalidStateTransitionError",
    "map_sqlite_error",
]
