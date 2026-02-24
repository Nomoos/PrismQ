"""Inspiration database model for PrismQ Database Schema.

This module provides the SQL DDL schema definition for the Inspiration table.
It follows the same pattern as other database models in PrismQ, with a
get_sql_schema() method that returns the CREATE TABLE statement.

Note:
    This module contains ONLY DDL (Data Definition Language) operations.
    Business logic and data access are handled by separate modules.

Schema:
    Inspiration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,                             -- Source text / description
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )

The Inspiration table stores inspiration sources for Ideas.
Ideas reference Inspirations via the IdeaInspiration junction table (M:N).
One Inspiration can come from user input, fusion, or other modules.
"""


class InspirationSchema:
    """Schema definition for Inspiration table.

    This class provides the SQL CREATE TABLE statement for the Inspiration table.
    It is designed to be used by SchemaManager for database initialization.

    Note:
        This class contains ONLY DDL operations - no business logic.

    Example:
        >>> schema = InspirationSchema.get_sql_schema()
        >>> print(schema)  # Returns CREATE TABLE IF NOT EXISTS Inspiration (...)
    """

    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for the Inspiration table.

        Returns:
            SQL statement to create the Inspiration table with
            CREATE TABLE IF NOT EXISTS for idempotent operations.
        """
        return """
        CREATE TABLE IF NOT EXISTS Inspiration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_inspiration_created_at ON Inspiration(created_at);
        """


__all__ = [
    "InspirationSchema",
]
