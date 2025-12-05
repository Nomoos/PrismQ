"""ScriptRepository - SQLite implementation for Script entities.

This module provides the SQLite implementation of IVersionedRepository
for Script entities, handling SQL DML (Data Manipulation Language) operations
only: SELECT, INSERT, UPDATE (limited to review_id FK).

Note:
    This repository does NOT handle schema creation (DDL). Use SchemaManager
    from T.Database.schema_manager for database initialization.

Usage:
    >>> import sqlite3
    >>> from T.Database.schema_manager import initialize_database
    >>> from T.Database.repositories.script_repository import ScriptRepository
    >>> from T.Database.models.script import Script
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> initialize_database(conn)  # Creates schema
    >>> 
    >>> repo = ScriptRepository(conn)
    >>> script = Script(story_id=1, version=0, text="Once upon a time...")
    >>> saved = repo.insert(script)
    >>> 
    >>> # Find latest version
    >>> latest = repo.find_latest_version(story_id=1)
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from .base import IVersionedRepository
from ..models.script import Script


class ScriptRepository(IVersionedRepository[Script, int]):
    """SQLite implementation of IVersionedRepository for Script entities.
    
    This repository handles SQL DML (Data Manipulation Language) operations
    for Script entities following the INSERT+READ only pattern. New versions
    are created instead of updating existing rows.
    
    Note:
        This repository does NOT create database tables. Schema initialization
        must be performed separately using SchemaManager.initialize_schema()
        before using this repository.
    
    Attributes:
        _conn: SQLite database connection with Row factory enabled.
    
    Example:
        >>> import sqlite3
        >>> from T.Database.schema_manager import initialize_database
        >>> 
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> initialize_database(conn)  # Create schema first
        >>> 
        >>> repo = ScriptRepository(conn)
        >>> script = Script(story_id=1, version=0, text="Original content")
        >>> saved = repo.insert(script)
        >>> 
        >>> # Create new version
        >>> new_version = saved.create_next_version("Improved content")
        >>> repo.insert(new_version)
        >>> 
        >>> # Get latest
        >>> latest = repo.find_latest_version(story_id=1)
        >>> print(latest.version)  # 1
    """
    
    def __init__(self, connection: sqlite3.Connection):
        """Initialize repository with database connection.
        
        Args:
            connection: SQLite connection with row_factory = sqlite3.Row
                recommended for dictionary-like row access.
                
        Note:
            The database schema must be initialized before using this
            repository. Use SchemaManager.initialize_schema() to create
            the required tables.
        """
        self._conn = connection
    
    # === READ Operations ===
    
    def find_by_id(self, id: int) -> Optional[Script]:
        """Find script by unique identifier.
        
        Args:
            id: The primary key of the script record.
            
        Returns:
            Script if found, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Script WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_script(row)
    
    def find_all(self) -> List[Script]:
        """Find all script records.
        
        Returns:
            List of all Script entities, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Script ORDER BY id"
        )
        return [self._row_to_script(row) for row in cursor.fetchall()]
    
    def exists(self, id: int) -> bool:
        """Check if script exists by ID.
        
        Args:
            id: The primary key to check.
            
        Returns:
            True if script exists, False otherwise.
        """
        cursor = self._conn.execute(
            "SELECT 1 FROM Script WHERE id = ?",
            (id,)
        )
        return cursor.fetchone() is not None
    
    # === INSERT Operation ===
    
    def insert(self, entity: Script) -> Script:
        """Insert new script (or new version).
        
        Creates a new row in the Script table. For versioned content,
        use create_next_version() to get a new Script instance with
        incremented version, then insert it.
        
        Args:
            entity: Script instance to insert. id will be auto-generated.
            
        Returns:
            The inserted Script with id populated.
        """
        cursor = self._conn.execute(
            "INSERT INTO Script (story_id, version, text, review_id, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                entity.story_id,
                entity.version,
                entity.text,
                entity.review_id,
                entity.created_at.isoformat()
            )
        )
        self._conn.commit()
        
        # Update entity with generated ID
        entity.id = cursor.lastrowid
        return entity
    
    # === IVersionedRepository Operations ===
    
    def find_latest_version(self, story_id: int) -> Optional[Script]:
        """Find the most recent version of a script for a story.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            The Script with highest version number, or None if no scripts exist.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Script WHERE story_id = ? "
            "ORDER BY version DESC LIMIT 1",
            (story_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_script(row)
    
    def find_versions(self, story_id: int) -> List[Script]:
        """Find all versions of a script for a story.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all Script versions ordered by version number (ascending).
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Script WHERE story_id = ? "
            "ORDER BY version ASC",
            (story_id,)
        )
        return [self._row_to_script(row) for row in cursor.fetchall()]
    
    def find_version(self, story_id: int, version: int) -> Optional[Script]:
        """Find a specific version of a script.
        
        Args:
            story_id: The story identifier.
            version: The version number (0, 1, 2, ...).
            
        Returns:
            The specific Script version, or None if not found.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Script WHERE story_id = ? AND version = ?",
            (story_id, version)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_script(row)
    
    def find_by_story_id(self, story_id: int) -> List[Script]:
        """Find all scripts for a specific story.
        
        Alias for find_versions() for semantic clarity when querying
        by story rather than by base entity ID.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all Script versions for the story.
        """
        return self.find_versions(story_id)
    
    # === UPDATE Operation (for review_id only) ===
    
    def update_review_id(self, script_id: int, review_id: int) -> bool:
        """Update the review_id FK on a Script.
        
        This is a limited update operation specifically for linking
        a Review to a Script after grammar/quality review is performed.
        
        Note:
            This is an exception to the INSERT+READ only pattern,
            allowed because review_id is a reference field, not content.
        
        Args:
            script_id: The script's primary key.
            review_id: The review to link (FK to Review table).
            
        Returns:
            True if the script was updated, False if not found.
        """
        cursor = self._conn.execute(
            "UPDATE Script SET review_id = ? WHERE id = ?",
            (review_id, script_id)
        )
        self._conn.commit()
        return cursor.rowcount > 0
    
    # === Helper Methods ===
    
    def _row_to_script(self, row: sqlite3.Row) -> Script:
        """Convert database row to Script instance.
        
        Args:
            row: SQLite Row object with script data.
            
        Returns:
            Script instance populated from row data.
        """
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return Script(
            id=row["id"],
            story_id=row["story_id"],
            version=row["version"],
            text=row["text"],
            review_id=row["review_id"],
            created_at=created_at
        )
    
    def _get_next_version_number(self, story_id: int) -> int:
        """Get the next version number for a story's script.
        
        Private helper method to determine what version number to use
        when creating a new script version.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            Next version number (0 if no scripts exist, otherwise max+1).
        """
        cursor = self._conn.execute(
            "SELECT MAX(version) as max_version FROM Script WHERE story_id = ?",
            (story_id,)
        )
        row = cursor.fetchone()
        max_version = row["max_version"] if row["max_version"] is not None else -1
        return max_version + 1
    
    def update_review_id(self, script_id: int, review_id: int) -> bool:
        """Update the review_id FK on an existing script.
        
        This is the only UPDATE operation allowed on Script, specifically
        for linking a Review to a Script after the review is created.
        
        Args:
            script_id: The ID of the script to update.
            review_id: The ID of the review to link.
            
        Returns:
            True if the update was successful, False if script not found.
            
        Example:
            >>> repo.update_review_id(script_id=5, review_id=10)
            True
        """
        cursor = self._conn.execute(
            "UPDATE Script SET review_id = ? WHERE id = ?",
            (review_id, script_id)
        )
        self._conn.commit()
        return cursor.rowcount > 0
