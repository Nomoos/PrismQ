"""Idea table manager for PrismQ's shared database.

This module provides the IdeaTable class for managing the Inspiration,
Idea, and IdeaInspiration tables in PrismQ's shared database (db.s3db).

IMPORTANT: PrismQ uses ONE shared database (db.s3db) for ALL modules.

Best Practice — Inspiration references:
    IdeaInspiration.inspiration_id is an INTEGER FK to Inspiration(id).
    Every inspiration source (user input, YouTube, Reddit, etc.) must first be
    registered in the Inspiration table. IdeaInspiration then links an Idea to
    one or more Inspiration records via integer keys, giving full referential
    integrity. Use the `source` + `source_id` unique pair in Inspiration to
    avoid duplicates across calls.

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
        inspiration_id INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (idea_id) REFERENCES Idea(id) ON DELETE CASCADE,
        FOREIGN KEY (inspiration_id) REFERENCES Inspiration(id),
        UNIQUE(idea_id, inspiration_id)
    )

Usage:
    from src.idea import IdeaTable, setup_idea_table

    db = setup_idea_table()
    insp_id = db.insert_inspiration(source="user", source_id="user-input-1")
    idea_id = db.insert_idea("Write a horror story about...")
    db.add_inspiration(idea_id, insp_id)
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
        """Create Inspiration, Idea, and IdeaInspiration tables."""
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

        # Create Inspiration table (registry for all inspiration sources)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Inspiration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                title TEXT,
                url TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(source, source_id)
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
        # inspiration_id is an INTEGER FK to Inspiration(id) — register an
        # Inspiration record first, then link it here.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS IdeaInspiration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER NOT NULL,
                inspiration_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (idea_id) REFERENCES Idea(id) ON DELETE CASCADE,
                FOREIGN KEY (inspiration_id) REFERENCES Inspiration(id),
                UNIQUE(idea_id, inspiration_id)
            )
        """
        )

        # Indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_inspiration_source ON Inspiration(source)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_inspiration_source_id ON Inspiration(source_id)"
        )
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
    # Inspiration CRUD
    # =========================================================================

    def insert_inspiration(
        self,
        source: str,
        source_id: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
    ) -> int:
        """Register an inspiration source, returning its integer ID.

        Uses INSERT OR IGNORE so calling this multiple times with the same
        (source, source_id) pair is safe — the existing record's ID is
        returned on duplicates.

        Args:
            source: Origin platform (e.g. 'user', 'youtube', 'reddit')
            source_id: Unique identifier within that platform
            title: Optional human-readable label
            url: Optional URL to the source content

        Returns:
            ID of the (new or existing) Inspiration record
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO Inspiration (source, source_id, title, url)
            VALUES (?, ?, ?, ?)
            """,
            (source, source_id, title, url),
        )
        self.conn.commit()

        # Fetch the ID whether just inserted or already existed
        cursor.execute(
            "SELECT id FROM Inspiration WHERE source = ? AND source_id = ?",
            (source, source_id),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(
                f"Failed to retrieve Inspiration after insert for source={source!r}, "
                f"source_id={source_id!r}"
            )
        return row[0]

    def get_inspiration(self, inspiration_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve an Inspiration record by ID.

        Args:
            inspiration_id: Primary key of the Inspiration record

        Returns:
            Dictionary representation or None if not found
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Inspiration WHERE id = ?", (inspiration_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # =========================================================================
    # IdeaInspiration CRUD
    # =========================================================================

    def add_inspiration(self, idea_id: int, inspiration_id: int) -> bool:
        """Link an Inspiration record to an Idea.

        Best practice: call insert_inspiration() first to obtain the integer
        inspiration_id, then pass it here.

        Args:
            idea_id: ID of the Idea
            inspiration_id: Integer ID of an existing Inspiration record

        Returns:
            True if added, False if the link already exists
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

    def get_inspirations(self, idea_id: int) -> List[Dict[str, Any]]:
        """Get all Inspiration records linked to an Idea.

        Args:
            idea_id: ID of the Idea

        Returns:
            List of Inspiration dictionaries (empty if none)
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT i.* FROM Inspiration i
            JOIN IdeaInspiration ii ON ii.inspiration_id = i.id
            WHERE ii.idea_id = ?
            """,
            (idea_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_ideas_by_inspiration(self, inspiration_id: int) -> List[Dict[str, Any]]:
        """Get all Ideas linked to a specific Inspiration record.

        Args:
            inspiration_id: Integer ID of the Inspiration record

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

    def remove_inspiration(self, idea_id: int, inspiration_id: int) -> bool:
        """Remove an inspiration link from an Idea.

        Args:
            idea_id: ID of the Idea
            inspiration_id: Integer ID of the Inspiration record

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
    """Setup and initialize the Inspiration/Idea table managers for the shared database.

    Creates a table manager, connects to the shared database, and ensures
    the Inspiration, Idea, and IdeaInspiration tables exist with proper schema
    and indexes.

    IMPORTANT: This manages tables in the shared database (db.s3db),
    not a separate database. All PrismQ modules use this same database.

    Args:
        db_path: Path to shared SQLite database file (default: db.s3db)

    Returns:
        Connected and initialized IdeaTable instance

    Example:
        >>> db = setup_idea_table()
        >>> insp_id = db.insert_inspiration(source="user", source_id="my-input-1")
        >>> idea_id = db.insert_idea("Write a story about...")
        >>> db.add_inspiration(idea_id, insp_id)
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
