"""Idea database model for PrismQ Database Schema.

This module provides the SQL DDL schema definition for the Idea table.
It follows the same pattern as other database models in PrismQ, with a
get_sql_schema() method that returns the CREATE TABLE statement.

Note:
    This module contains ONLY DDL (Data Definition Language) operations.
    Business logic and data access are handled by separate modules.
    
Schema:
    Idea (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,                                      -- Prompt-like text describing the idea
        version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),  -- Version tracking (UINT simulation)
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )

The Idea table stores simple prompt-based idea data for content generation.
Story references Idea via FK in Story.idea_id.
"""


class IdeaSchema:
    """Schema definition for Idea table.
    
    This class provides the SQL CREATE TABLE statement for the Idea table.
    It is designed to be used by SchemaManager for database initialization.
    
    The Idea table stores simple prompt-based idea data that serves as
    input for the PrismQ content generation pipeline. Story entities
    reference Ideas via foreign key (Story.idea_id).
    
    Note:
        This class contains ONLY DDL operations - no business logic.
        Version uses INTEGER with CHECK >= 0 to simulate unsigned integer.
    
    Attributes:
        None - this is a schema-only class
    
    Example:
        >>> schema = IdeaSchema.get_sql_schema()
        >>> print(schema)  # Returns CREATE TABLE IF NOT EXISTS Idea (...)
    """
    
    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for the Idea table.
        
        Returns:
            SQL statement to create the Idea table with all constraints
            and performance indexes using CREATE TABLE IF NOT EXISTS
            for idempotent operations.
        
        Note:
            - The table is a base table with no foreign key dependencies
            - version uses INTEGER with CHECK >= 0 to simulate unsigned integer
            - Story references this table via Story.idea_id FK
        """
        return """
        CREATE TABLE IF NOT EXISTS Idea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        
        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_idea_created_at ON Idea(created_at);
        """


__all__ = [
    "IdeaSchema",
]
