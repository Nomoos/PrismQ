"""Idea model and database support for PrismQ.

This module provides the shared Idea model for storing prompt-based idea data
that can be created by PrismQ.T.Idea.Creation or PrismQ.Idea.Fusion.

The Idea table is designed to be referenced by Story via foreign key (Story.idea_id).

Schema:
    -- Idea: Simple prompt-based idea data (Story references Idea via FK in Story.idea_id)
    -- Text field contains prompt-like content for content generation
    -- Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer
    Idea (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,                                      -- Prompt-like text describing the idea
        version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),  -- Version tracking (UINT simulation)
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )

Usage:
    from src import IdeaDatabase, setup_idea_database
    
    # Setup database
    db = setup_idea_database("ideas.db")
    
    # Insert an idea
    idea_id = db.insert_idea("Write a horror story about...")
    
    # Retrieve it
    idea = db.get_idea(idea_id)
    print(idea["text"])
    
    db.close()
"""

import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime


class IdeaDatabase:
    """Database manager for Idea model.
    
    Provides CRUD operations for the Idea table that stores
    prompt-like text content with versioning support.
    
    The Idea table is designed to be referenced by Story via foreign key.
    This is shared database logic used across all PrismQ modules.
    
    Example:
        >>> db = IdeaDatabase("ideas.db")
        >>> db.connect()
        >>> db.create_tables()
        >>> 
        >>> # Insert an idea
        >>> idea_id = db.insert_idea("Write a horror story about...")
        >>> 
        >>> # Retrieve it
        >>> idea = db.get_idea(idea_id)
        >>> print(idea["text"])
        >>> 
        >>> db.close()
    """
    
    def __init__(self, db_path: str = "idea.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self) -> None:
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        # Enable foreign key constraints in SQLite
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_tables(self) -> None:
        """Create database schema for Idea.
        
        Creates the Idea table with the schema:
            - id: INTEGER PRIMARY KEY AUTOINCREMENT
            - text: TEXT (prompt-like content for content generation)
            - version: INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0)
            - created_at: TEXT NOT NULL DEFAULT (datetime('now'))
        
        Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer.
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Create Idea table
        # Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Idea (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Create index on version for efficient queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_idea_version 
            ON Idea(version)
        """)
        
        # Create index on created_at for chronological queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_idea_created_at 
            ON Idea(created_at)
        """)
        
        self.conn.commit()
    
    def insert_idea(
        self,
        text: str,
        version: int = 1,
        created_at: Optional[str] = None
    ) -> int:
        """Insert a new Idea into the database.
        
        Args:
            text: Prompt-like text content for content generation
            version: Version number (default: 1, must be >= 0)
            created_at: Optional timestamp (auto-generated if not provided)
            
        Returns:
            ID of inserted idea
            
        Raises:
            sqlite3.IntegrityError: If version is negative (CHECK constraint violation)
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        if created_at:
            cursor.execute("""
                INSERT INTO Idea (text, version, created_at)
                VALUES (?, ?, ?)
            """, (text, version, created_at))
        else:
            cursor.execute("""
                INSERT INTO Idea (text, version)
                VALUES (?, ?)
            """, (text, version))
        
        idea_id = cursor.lastrowid
        self.conn.commit()
        
        return idea_id
    
    def insert_idea_from_dict(self, idea_dict: Dict[str, Any]) -> int:
        """Insert an Idea from dictionary representation.
        
        Args:
            idea_dict: Dictionary with text, version, and optional created_at
            
        Returns:
            ID of inserted idea
        """
        return self.insert_idea(
            text=idea_dict.get("text", ""),
            version=idea_dict.get("version", 1),
            created_at=idea_dict.get("created_at"),
        )
    
    def get_idea(self, idea_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve an Idea by ID.
        
        Args:
            idea_id: ID of the idea
            
        Returns:
            Dictionary representation of Idea or None if not found
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Idea WHERE id = ?", (idea_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return dict(row)
    
    def get_all_ideas(self) -> List[Dict[str, Any]]:
        """Retrieve all Ideas.
        
        Returns:
            List of Idea dictionaries ordered by created_at descending
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Idea ORDER BY created_at DESC")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_ideas_by_version(self, version: int) -> List[Dict[str, Any]]:
        """Retrieve all Ideas with a specific version.
        
        Args:
            version: Version number to filter by
            
        Returns:
            List of Idea dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Idea WHERE version = ? ORDER BY created_at DESC",
            (version,)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_latest_ideas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve the most recent Ideas.
        
        Args:
            limit: Maximum number of ideas to return
            
        Returns:
            List of Idea dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Idea ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_idea(
        self,
        idea_id: int,
        text: Optional[str] = None,
        version: Optional[int] = None
    ) -> bool:
        """Update an existing Idea.
        
        Args:
            idea_id: ID of the idea to update
            text: New text content (optional)
            version: New version number (optional, must be >= 0)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            sqlite3.IntegrityError: If version is negative (CHECK constraint violation)
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        if text is not None and version is not None:
            cursor.execute(
                "UPDATE Idea SET text = ?, version = ? WHERE id = ?",
                (text, version, idea_id)
            )
        elif text is not None:
            cursor.execute(
                "UPDATE Idea SET text = ? WHERE id = ?",
                (text, idea_id)
            )
        elif version is not None:
            cursor.execute(
                "UPDATE Idea SET version = ? WHERE id = ?",
                (version, idea_id)
            )
        else:
            return False
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_idea(self, idea_id: int) -> bool:
        """Delete an Idea.
        
        Args:
            idea_id: ID of the idea to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Idea WHERE id = ?", (idea_id,))
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def search_ideas(self, query: str) -> List[Dict[str, Any]]:
        """Search Ideas by text content.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching Idea dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Idea WHERE text LIKE ? ORDER BY created_at DESC",
            (f"%{query}%",)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def count_ideas(self) -> int:
        """Get total count of Ideas.
        
        Returns:
            Number of ideas in database
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Idea")
        
        return cursor.fetchone()[0]
    
    def get_max_version(self) -> int:
        """Get the maximum version number across all Ideas.
        
        Returns:
            Maximum version number, or 0 if no ideas exist
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(version) FROM Idea")
        result = cursor.fetchone()[0]
        
        return result if result is not None else 0


def setup_idea_database(db_path: str = "idea.db") -> IdeaDatabase:
    """Initialize and setup the Idea database.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        Configured IdeaDatabase instance with tables created
    """
    db = IdeaDatabase(db_path)
    db.connect()
    db.create_tables()
    return db


__all__ = [
    "IdeaDatabase",
    "setup_idea_database",
]
