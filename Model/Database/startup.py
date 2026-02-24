"""DEPRECATED: Use Model.Infrastructure.startup instead."""
from Model.Infrastructure.startup import (
    DatabaseInitializationError,
    initialize_application_database,
    safe_initialize_database,
)
__all__ = [
    "DatabaseInitializationError",
    "initialize_application_database",
    "safe_initialize_database",
]
