"""Idea database model for PrismQ Database Schema.

This module provides the SQL DDL schema definition for the Idea table
and IdeaInspiration junction table.

Note:
    This module contains ONLY DDL (Data Definition Language) operations.
    Business logic and data access are handled by src/idea.py (IdeaTable).
    
Schema:
    Idea (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
        review_id INTEGER,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (review_id) REFERENCES Review(id)
    )

    IdeaInspiration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id INTEGER NOT NULL,
        inspiration_id TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (idea_id) REFERENCES Idea(id) ON DELETE CASCADE,
        UNIQUE(idea_id, inspiration_id)
    )

The Idea table stores simple prompt-based idea data for content generation.
Story references Idea via FK in Story.idea_id.
IdeaInspiration links Ideas to their inspiration sources (M:N).
"""


class IdeaSchema:
    """Schema definition for Idea and IdeaInspiration tables.
    
    Note:
        This class contains ONLY DDL operations - no business logic.
        For CRUD operations use src/idea.py (IdeaTable).
    
    Example:
        >>> schema = IdeaSchema.get_sql_schema()
    """
    
    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statements for Idea and IdeaInspiration."""
        return """
        CREATE TABLE IF NOT EXISTS Idea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
            review_id INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (review_id) REFERENCES Review(id)
        );
        
        CREATE TABLE IF NOT EXISTS IdeaInspiration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NOT NULL,
            inspiration_id TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (idea_id) REFERENCES Idea(id) ON DELETE CASCADE,
            UNIQUE(idea_id, inspiration_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_idea_created_at ON Idea(created_at);
        CREATE INDEX IF NOT EXISTS idx_idea_review_id ON Idea(review_id);
        CREATE INDEX IF NOT EXISTS idx_idea_inspiration_idea_id ON IdeaInspiration(idea_id);
        CREATE INDEX IF NOT EXISTS idx_idea_inspiration_inspiration_id ON IdeaInspiration(inspiration_id);
        """


__all__ = [
    "IdeaSchema",
]
