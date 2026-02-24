"""Inspiration database model for PrismQ Database Schema.

This module provides the SQL DDL schema definition for the Inspiration table,
which serves as the central registry for all inspiration sources.

Note:
    This module contains ONLY DDL (Data Definition Language) operations.

Schema:
    Inspiration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        source_id TEXT NOT NULL,
        title TEXT,
        url TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(source, source_id)
    )

Best Practice:
    Every inspiration — regardless of origin (user input, YouTube, Reddit, etc.)
    — is registered in this table first. IdeaInspiration then references
    Inspiration(id) as an INTEGER FK, giving full referential integrity while
    keeping the source details in one place.

    Source conventions:
        - 'user'        : direct user-provided inspiration (source_id = any unique label)
        - 'youtube'     : YouTube video (source_id = video ID)
        - 'reddit'      : Reddit post (source_id = post ID)
        - 'hackernews'  : HackerNews story (source_id = item ID)
"""


class InspirationSchema:
    """Schema definition for the Inspiration table.

    Note:
        This class contains ONLY DDL operations - no business logic.

    Example:
        >>> schema = InspirationSchema.get_sql_schema()
    """

    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for Inspiration."""
        return """
        CREATE TABLE IF NOT EXISTS Inspiration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            title TEXT,
            url TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(source, source_id)
        );

        CREATE INDEX IF NOT EXISTS idx_inspiration_source ON Inspiration(source);
        CREATE INDEX IF NOT EXISTS idx_inspiration_source_id ON Inspiration(source_id);
        """


__all__ = [
    "InspirationSchema",
]
