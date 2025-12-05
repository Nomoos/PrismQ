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
        title TEXT NOT NULL,
        concept TEXT NOT NULL,
        synopsis TEXT,
        story_premise TEXT,
        purpose TEXT,
        emotional_quality TEXT,
        target_audience TEXT,
        target_demographics TEXT,  -- JSON string
        target_platforms TEXT,     -- JSON string (list of platforms)
        target_formats TEXT,       -- JSON string (list of formats)
        genre TEXT,
        style TEXT,
        keywords TEXT,             -- JSON string (list of keywords)
        themes TEXT,               -- JSON string (list of themes)
        character_notes TEXT,
        setting_notes TEXT,
        tone_guidance TEXT,
        length_target TEXT,
        outline TEXT,
        skeleton TEXT,
        original_language TEXT DEFAULT 'en',
        potential_scores TEXT,     -- JSON string
        metadata TEXT,             -- JSON string
        version INTEGER DEFAULT 1,
        status TEXT DEFAULT 'draft',
        notes TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        created_by TEXT
    )
"""


class IdeaSchema:
    """Schema definition for Idea table.
    
    This class provides the SQL CREATE TABLE statement for the Idea table.
    It is designed to be used by SchemaManager for database initialization.
    
    The Idea table stores creative content ideas that serve as the foundation
    for the PrismQ content generation pipeline.
    
    Note:
        This class contains ONLY DDL operations - no business logic.
        For the full Idea data model with business logic, see 
        T/Idea/Model/src/idea.py
    
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
            - The table uses TEXT type for JSON-serialized complex fields
            - No foreign keys in this table (Idea is a base table)
            - Includes indexes for common query patterns
        """
        return """
        CREATE TABLE IF NOT EXISTS Idea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            concept TEXT NOT NULL,
            synopsis TEXT,
            story_premise TEXT,
            purpose TEXT,
            emotional_quality TEXT,
            target_audience TEXT,
            target_demographics TEXT,
            target_platforms TEXT,
            target_formats TEXT,
            genre TEXT,
            style TEXT,
            keywords TEXT,
            themes TEXT,
            character_notes TEXT,
            setting_notes TEXT,
            tone_guidance TEXT,
            length_target TEXT,
            outline TEXT,
            skeleton TEXT,
            original_language TEXT DEFAULT 'en',
            potential_scores TEXT,
            metadata TEXT,
            version INTEGER DEFAULT 1,
            status TEXT DEFAULT 'draft',
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            created_by TEXT
        );
        
        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_idea_status ON Idea(status);
        CREATE INDEX IF NOT EXISTS idx_idea_genre ON Idea(genre);
        CREATE INDEX IF NOT EXISTS idx_idea_created_at ON Idea(created_at);
        """


__all__ = [
    "IdeaSchema",
]
