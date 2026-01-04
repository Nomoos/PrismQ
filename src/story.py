"""Story table manager for PrismQ's shared database.

This module provides the StoryTable class for managing the Story table in PrismQ's
shared database (db.s3db). The Story table tracks story progress through the
PrismQ workflow pipeline.

IMPORTANT: PrismQ uses ONE shared database (db.s3db) for ALL modules.
The Story table is one of many tables in this shared database.

The Story table tracks the state of a story as it moves through different
processing steps. State is stored as a string following the pattern:
PrismQ.T.<Output>.From.<Input1>.<Input2>...

The Story table references Idea via foreign key (idea_id).

Schema:
    -- Main Story table with state (next process name) and idea_id FK
    -- State is stored as a string following the pattern: PrismQ.T.<Output>.From.<Input1>.<Input2>...
    -- Note: current_title_version_id and current_script_version_id are removed
    -- Current versions are now implicit - determined by highest version integer
    -- in Title/Script tables via ORDER BY version DESC LIMIT 1
    Story (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        idea_id INTEGER FK NULL REFERENCES Idea(id),  -- Reference to Idea
        state TEXT NOT NULL DEFAULT 'PrismQ.T.Title.From.Idea',  -- Next process name
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (idea_id) REFERENCES Idea(id)
    )

Usage:
    from src.story import StoryTable, setup_story_table

    # Setup table manager for shared database
    db = setup_story_table("db.s3db")

    # Insert a story
    story_id = db.insert_story(idea_id=1)

    # Retrieve it
    story = db.get_story(story_id)
    print(story["state"])

    # Update state
    db.update_story(story_id, state="PrismQ.T.Script.From.Idea.Title")

    db.close()
"""

import sqlite3
from typing import Any, Dict, List, Optional

# Sentinel value to indicate setting idea_id to NULL in update_story
CLEAR_IDEA_ID = -1


class StoryTable:
    """Table manager for the Story table in PrismQ's shared database.

    Provides CRUD operations for the Story table that tracks
    story progress through the PrismQ workflow pipeline.

    IMPORTANT: This manages the Story table in the shared database (db.s3db),
    not a separate database. PrismQ uses ONE shared database for all tables.

    The Story table references Idea via foreign key.
    State tracks the next process to be applied to the story.

    Example:
        >>> db = StoryTable("db.s3db")
        >>> db.connect()
        >>> db.create_tables()
        >>>
        >>> # Insert a story
        >>> story_id = db.insert_story(idea_id=1)
        >>>
        >>> # Retrieve it
        >>> story = db.get_story(story_id)
        >>> print(story["state"])
        >>>
        >>> db.close()
    """

    def __init__(self, db_path: str = "story.db"):
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
        """Create database schema for Story.

        Creates the Story table with the schema:
            - id: INTEGER PRIMARY KEY AUTOINCREMENT
            - idea_id: INTEGER FK NULL REFERENCES Idea(id)
            - state: TEXT NOT NULL DEFAULT 'PrismQ.T.Title.From.Idea'
            - created_at: TEXT NOT NULL DEFAULT (datetime('now'))
            - updated_at: TEXT NOT NULL DEFAULT (datetime('now'))

        Also creates the Idea table if it doesn't exist (required for FK constraint).

        Note: Foreign key constraints require PRAGMA foreign_keys = ON.
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Create Idea table first (required for Story FK constraint)
        # Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer
        # Note: score uses INTEGER with CHECK >= 0 and <= 100 for Local AI scoring
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Idea (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),
                score INTEGER CHECK (score >= 0 AND score <= 100),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """
        )

        # Create Story table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Story (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER NULL,
                state TEXT NOT NULL DEFAULT 'PrismQ.T.Title.From.Idea',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (idea_id) REFERENCES Idea(id)
            )
        """
        )

        # Create index on idea_id for efficient FK lookups
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_story_idea_id 
            ON Story(idea_id)
        """
        )

        # Create index on state for efficient state-based queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_story_state 
            ON Story(state)
        """
        )

        # Create index on created_at for chronological queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_story_created_at 
            ON Story(created_at)
        """
        )

        # Create index on updated_at for recent activity queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_story_updated_at 
            ON Story(updated_at)
        """
        )

        self.conn.commit()

    def insert_story(
        self,
        idea_id: Optional[int] = None,
        state: str = "PrismQ.T.Title.From.Idea",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> int:
        """Insert a new Story into the database.

        Args:
            idea_id: Optional reference to Idea table (can be NULL)
            state: Next process name (default: 'PrismQ.T.Title.From.Idea')
            created_at: Optional timestamp (auto-generated if not provided)
            updated_at: Optional timestamp (auto-generated if not provided)

        Returns:
            ID of inserted story

        Raises:
            sqlite3.IntegrityError: If idea_id references non-existent Idea (FK constraint)
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Build column and value lists dynamically
        columns = ["idea_id", "state"]
        values = [idea_id, state]

        if created_at:
            columns.append("created_at")
            values.append(created_at)
            # If created_at is set but updated_at is not, use created_at for both
            if not updated_at:
                columns.append("updated_at")
                values.append(created_at)

        if updated_at:
            columns.append("updated_at")
            values.append(updated_at)

        placeholders = ", ".join(["?"] * len(values))
        column_names = ", ".join(columns)

        cursor.execute(f"INSERT INTO Story ({column_names}) VALUES ({placeholders})", values)

        story_id = cursor.lastrowid
        self.conn.commit()

        return story_id

    def insert_story_from_dict(self, story_dict: Dict[str, Any]) -> int:
        """Insert a Story from dictionary representation.

        Args:
            story_dict: Dictionary with idea_id, state, and optional timestamps

        Returns:
            ID of inserted story
        """
        return self.insert_story(
            idea_id=story_dict.get("idea_id"),
            state=story_dict.get("state", "PrismQ.T.Title.From.Idea"),
            created_at=story_dict.get("created_at"),
            updated_at=story_dict.get("updated_at"),
        )

    def get_story(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a Story by ID.

        Args:
            story_id: ID of the story

        Returns:
            Dictionary representation of Story or None if not found
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Story WHERE id = ?", (story_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return dict(row)

    def get_all_stories(self) -> List[Dict[str, Any]]:
        """Retrieve all Stories.

        Returns:
            List of Story dictionaries ordered by created_at descending
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Story ORDER BY created_at DESC")

        return [dict(row) for row in cursor.fetchall()]

    def get_stories_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Retrieve all Stories with a specific state.

        Args:
            state: State string to filter by (e.g., 'PrismQ.T.Title.From.Idea')

        Returns:
            List of Story dictionaries
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Story WHERE state = ? ORDER BY created_at DESC", (state,))

        return [dict(row) for row in cursor.fetchall()]

    def get_stories_by_idea_id(self, idea_id: int) -> List[Dict[str, Any]]:
        """Retrieve all Stories referencing a specific Idea.

        Args:
            idea_id: ID of the Idea to filter by

        Returns:
            List of Story dictionaries
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Story WHERE idea_id = ? ORDER BY created_at DESC", (idea_id,))

        return [dict(row) for row in cursor.fetchall()]

    def get_latest_stories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve the most recent Stories.

        Args:
            limit: Maximum number of stories to return

        Returns:
            List of Story dictionaries
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Story ORDER BY created_at DESC LIMIT ?", (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_recently_updated_stories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve the most recently updated Stories.

        Args:
            limit: Maximum number of stories to return

        Returns:
            List of Story dictionaries ordered by updated_at descending
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Story ORDER BY updated_at DESC LIMIT ?", (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def update_story(
        self,
        story_id: int,
        idea_id: Optional[int] = None,
        state: Optional[str] = None,
        update_timestamp: bool = True,
    ) -> bool:
        """Update an existing Story.

        Args:
            story_id: ID of the story to update
            idea_id: New idea_id (optional, use CLEAR_IDEA_ID to set to NULL)
            state: New state string (optional)
            update_timestamp: Whether to update updated_at (default: True)

        Returns:
            True if successful, False otherwise

        Raises:
            sqlite3.IntegrityError: If idea_id references non-existent Idea (FK constraint)
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # Build the update query dynamically
        updates = []
        params = []

        if idea_id is not None:
            if idea_id == CLEAR_IDEA_ID:
                updates.append("idea_id = NULL")
            else:
                updates.append("idea_id = ?")
                params.append(idea_id)

        if state is not None:
            updates.append("state = ?")
            params.append(state)

        if update_timestamp:
            updates.append("updated_at = datetime('now')")

        if not updates:
            return False

        params.append(story_id)
        query = f"UPDATE Story SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, params)
        self.conn.commit()

        return cursor.rowcount > 0

    def delete_story(self, story_id: int) -> bool:
        """Delete a Story.

        Args:
            story_id: ID of the story to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Story WHERE id = ?", (story_id,))
        self.conn.commit()

        return cursor.rowcount > 0

    def search_stories_by_state(self, query: str) -> List[Dict[str, Any]]:
        """Search Stories by state content.

        Args:
            query: Search query string

        Returns:
            List of matching Story dictionaries
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM Story WHERE state LIKE ? ORDER BY created_at DESC", (f"%{query}%",)
        )

        return [dict(row) for row in cursor.fetchall()]

    def count_stories(self) -> int:
        """Get total count of Stories.

        Returns:
            Number of stories in database
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Story")

        return cursor.fetchone()[0]

    def count_stories_by_state(self, state: str) -> int:
        """Get count of Stories with a specific state.

        Args:
            state: State string to filter by

        Returns:
            Number of stories with that state
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Story WHERE state = ?", (state,))

        return cursor.fetchone()[0]

    def get_distinct_states(self) -> List[str]:
        """Get all distinct state values.

        Returns:
            List of unique state strings
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT state FROM Story ORDER BY state")

        return [row[0] for row in cursor.fetchall()]


def setup_story_table(db_path: str = "db.s3db") -> StoryTable:
    """Setup and initialize the Story table manager for the shared database.

    Creates a table manager, connects to the shared database, and ensures
    the Story table exists with proper schema and indexes.

    IMPORTANT: This manages the Story table in the shared database (db.s3db),
    not a separate database. All PrismQ modules use this same database.

    Args:
        db_path: Path to shared SQLite database file (default: db.s3db)

    Returns:
        Connected and initialized StoryTable instance

    Example:
        >>> db = setup_story_table()
        >>> story_id = db.insert_story(idea_id=1)
        >>> db.close()
    """
    db = StoryTable(db_path)
    db.connect()
    db.create_tables()
    return db


# Backward compatibility aliases - DEPRECATED
StoryDatabase = StoryTable
setup_story_database = setup_story_table


__all__ = [
    "CLEAR_IDEA_ID",
    "StoryDatabase",
    "setup_story_database",
]
