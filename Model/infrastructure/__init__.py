"""PrismQ database infrastructure.

This module provides database infrastructure components including
connection management, schema management, and exception handling.

Components:
    - connection: Database connection utilities
    - schema: Schema creation and initialization
    - exceptions: Custom database exception types
    - startup: Application startup utilities

Example:
    >>> from Model.infrastructure import get_connection, initialize_database
    >>> conn = get_connection("prismq.db")
    >>> initialize_database(conn)
"""

from Model.infrastructure.connection import get_connection, connection_context
from Model.infrastructure.schema import initialize_database, SchemaManager
from Model.infrastructure.exceptions import (
    DatabaseException,
    EntityNotFoundError,
    DuplicateEntityError,
    ForeignKeyViolationError,
    ConstraintViolationError,
    DatabaseConnectionError,
    DataIntegrityError,
    InvalidStateTransitionError,
    map_sqlite_error,
)

__all__ = [
    # Connection
    "get_connection",
    "connection_context",
    # Schema
    "initialize_database",
    "SchemaManager",
    # Exceptions
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
