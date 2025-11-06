"""Custom exceptions for queue database operations."""


class QueueDatabaseError(Exception):
    """Base exception for queue database errors."""

    pass


class QueueBusyError(QueueDatabaseError):
    """Raised when database is locked (SQLITE_BUSY)."""

    pass


class QueueSchemaError(QueueDatabaseError):
    """Raised when schema operation fails."""

    pass
