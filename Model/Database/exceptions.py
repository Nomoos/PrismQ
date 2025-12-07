"""DEPRECATED: Use Model.Infrastructure.exceptions instead."""
from Model.Infrastructure.exceptions import (
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
