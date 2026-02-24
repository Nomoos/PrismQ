"""Idea table manager for PrismQ's shared database.

This module provides the IdeaTable class for managing the Idea and
IdeaInspiration tables in PrismQ's shared database (db.s3db).

IMPORTANT: PrismQ uses ONE shared database (db.s3db) for ALL modules.

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

Usage:
    from src.idea import IdeaTable, setup_idea_table

    db = setup_idea_table()
    idea_id = db.insert_idea("Write a horror story about...")
    db.add_inspiration(idea_id, "user-input-1")
    db.close()
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class IdeaTable:
    """Table manager for the Idea table in PrismQ's shared database.

    Provides CRUD operations for the Idea table that stores
    prompt-like text content with versioning support.

    IMPORTANT: This manages the Idea table in the shared database (db.s3db),
    not a separate database. PrismQ uses ONE shared database for all tables.

    The Idea table is designed to be referenced by Story via foreign key.

    Example:
        >>> db = IdeaTable("db.s3db")
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

    def __init__(self, db_path: str = "db.s3db"):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file (default: db.s3db)
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
        """Create Idea and IdeaInspiration tables."""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Create Review table first (required for Idea FK constraint)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Review (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """
        )

        # Create Idea table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Idea (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
                review_id INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (review_id) REFERENCES Review(id)
            )
        """
        )

        # Create IdeaInspiration junction table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS IdeaInspiration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER NOT NULL,
                inspiration_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (idea_id) REFERENCES Idea(id) ON DELETE CASCADE,
                UNIQUE(idea_id, inspiration_id)
            )
        """
        )

        # Indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_idea_version ON Idea(version)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_idea_created_at ON Idea(created_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_idea_review_id ON Idea(review_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_idea_inspiration_idea_id ON IdeaInspiration(idea_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_idea_inspiration_inspiration_id ON IdeaInspiration(inspiration_id)"
        )

        self.conn.commit()

    def insert_idea(
        self,
        text: str,
        version: int = 1,
        review_id: Optional[int] = None,
        created_at: Optional[str] = None,
    ) -> int:
        """Insert a new Idea into the database.

        Args:
            text: Prompt-like text content for content generation
            version: Version number (default: 1, must be >= 0)
            review_id: Optional FK to Review table for idea quality assessment
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
            cursor.execute(
                """
                INSERT INTO Idea (text, version, review_id, created_at)
                VALUES (?, ?, ?, ?)
            """,
                (text, version, review_id, created_at),
            )
        else:
            cursor.execute(
                """
                INSERT INTO Idea (text, version, review_id)
                VALUES (?, ?, ?)
            """,
                (text, version, review_id),
            )

        idea_id = cursor.lastrowid
        self.conn.commit()

        return idea_id

    def insert_idea_from_dict(self, idea_dict: Dict[str, Any]) -> int:
        """Insert an Idea from dictionary representation.

        Args:
            idea_dict: Dictionary with the following keys:
                - text (str): Prompt-like text content (required, defaults to "" if missing)
                - version (int): Version number (optional, defaults to 1 if missing)
                - review_id (int): Optional FK to Review table (optional)
                - created_at (str): Optional timestamp (auto-generated if not provided)

        Returns:
            ID of inserted idea
        """
        return self.insert_idea(
            text=idea_dict.get("text", ""),
            version=idea_dict.get("version", 1),
            review_id=idea_dict.get("review_id"),
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
        cursor.execute("SELECT * FROM Idea WHERE version = ? ORDER BY created_at DESC", (version,))

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
        cursor.execute("SELECT * FROM Idea ORDER BY created_at DESC LIMIT ?", (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def update_idea(
        self,
        idea_id: int,
        text: Optional[str] = None,
        version: Optional[int] = None,
        review_id: Optional[int] = None,
    ) -> bool:
        """Update an existing Idea.

        Args:
            idea_id: ID of the idea to update
            text: New text content (optional, not updated if None)
            version: New version number (optional, must be >= 0, not updated if None)
            review_id: New review_id FK to Review table (optional, not updated if None)

        Returns:
            True if successful, False otherwise

        Raises:
            sqlite3.IntegrityError: If version is negative (CHECK constraint violation)
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Build update query dynamically using parameterized queries
        # Note: Column names are hardcoded strings, not user input - safe from SQL injection
        updates = []
        params = []

        if text is not None:
            updates.append("text = ?")
            params.append(text)

        if version is not None:
            updates.append("version = ?")
            params.append(version)

        if review_id is not None:
            updates.append("review_id = ?")
            params.append(review_id)
            params.append(version)

        if not updates:
            return False

        params.append(idea_id)
        # Query construction is safe: updates list contains only hardcoded column placeholders
        query = f"UPDATE Idea SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, params)
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
            "SELECT * FROM Idea WHERE text LIKE ? ORDER BY created_at DESC", (f"%{query}%",)
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

    # =========================================================================
    # IdeaInspiration CRUD
    # =========================================================================

    def add_inspiration(self, idea_id: int, inspiration_id: str) -> bool:
        """Link an inspiration source to an Idea.

        Args:
            idea_id: ID of the Idea
            inspiration_id: Text identifier of the inspiration source

        Returns:
            True if added, False if already exists
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO IdeaInspiration (idea_id, inspiration_id) VALUES (?, ?)",
                (idea_id, inspiration_id),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_inspirations(self, idea_id: int) -> List[str]:
        """Get all inspiration IDs linked to an Idea.

        Args:
            idea_id: ID of the Idea

        Returns:
            List of inspiration ID strings (empty if none)
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT inspiration_id FROM IdeaInspiration WHERE idea_id = ?",
            (idea_id,),
        )
        return [row[0] for row in cursor.fetchall()]

    def get_ideas_by_inspiration(self, inspiration_id: str) -> List[Dict[str, Any]]:
        """Get all Ideas linked to a specific inspiration source.

        Args:
            inspiration_id: Text identifier of the inspiration source

        Returns:
            List of Idea dictionaries
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT DISTINCT idea_id FROM IdeaInspiration WHERE inspiration_id = ?",
            (inspiration_id,),
        )
        return [self.get_idea(row[0]) for row in cursor.fetchall()]

    def remove_inspiration(self, idea_id: int, inspiration_id: str) -> bool:
        """Remove an inspiration link from an Idea.

        Args:
            idea_id: ID of the Idea
            inspiration_id: Text identifier of the inspiration source

        Returns:
            True if removed, False if not found
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM IdeaInspiration WHERE idea_id = ? AND inspiration_id = ?",
            (idea_id, inspiration_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0


def setup_idea_table(db_path: str = "db.s3db") -> IdeaTable:
    """Setup and initialize the Idea table manager for the shared database.

    Creates a table manager, connects to the shared database, and ensures
    the Idea table exists with proper schema and indexes.

    IMPORTANT: This manages the Idea table in the shared database (db.s3db),
    not a separate database. All PrismQ modules use this same database.

    Args:
        db_path: Path to shared SQLite database file (default: db.s3db)

    Returns:
        Connected and initialized IdeaTable instance

    Example:
        >>> db = setup_idea_table()
        >>> idea_id = db.insert_idea("Write a story about...")
        >>> db.close()
    """
    db = IdeaTable(db_path)
    db.connect()
    db.create_tables()
    return db


__all__ = [
    "IdeaTable",
    "setup_idea_table",
]
