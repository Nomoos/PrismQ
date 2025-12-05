"""TitleRepository - SQLite implementation for Title entities.

This module provides SQLite implementations of the IVersionedRepository interface
for Title entities, handling SQL DML (Data Manipulation Language) operations
only: SELECT, INSERT.

Note:
    This repository does NOT handle schema creation (DDL). Use SchemaManager
    from T.Database.schema_manager for database initialization.

Usage:
    >>> import sqlite3
    >>> from T.Database.schema_manager import initialize_database
    >>> from T.Database.repositories.title_repository import TitleRepository
    >>> from T.Database.models.title import Title
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> initialize_database(conn)  # Creates schema
    >>> 
    >>> repo = TitleRepository(conn)
    >>> title = Title(story_id=1, version=0, text="My Title")
    >>> saved = repo.insert(title)
    >>> 
    >>> # Find latest version
    >>> latest = repo.find_latest_version(story_id=1)
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from .base import IVersionedRepository
from ..models.title import Title


class TitleRepository(IVersionedRepository[Title, int]):
    """SQLite implementation of IVersionedRepository for Title entities.
    
    This repository handles SQL DML (Data Manipulation Language) operations
    for Title entities following the INSERT+READ only pattern. New versions
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
        >>> repo = TitleRepository(conn)
        >>> title = Title(story_id=1, version=0, text="Original Title")
        >>> saved = repo.insert(title)
        >>> 
        >>> # Create new version
        >>> new_version = saved.create_next_version("Improved Title")
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
    
    def find_by_id(self, id: int) -> Optional[Title]:
        """Find title by unique identifier.
        
        Args:
            id: The primary key of the title record.
            
        Returns:
            Title if found, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Title WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_title(row)
    
    def find_all(self) -> List[Title]:
        """Find all title records.
        
        Returns:
            List of all Title entities, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Title ORDER BY id"
        )
        return [self._row_to_title(row) for row in cursor.fetchall()]
    
    def exists(self, id: int) -> bool:
        """Check if title exists by ID.
        
        Args:
            id: The primary key to check.
            
        Returns:
            True if title exists, False otherwise.
        """
        cursor = self._conn.execute(
            "SELECT 1 FROM Title WHERE id = ?",
            (id,)
        )
        return cursor.fetchone() is not None
    
    # === INSERT Operation ===
    
    def insert(self, entity: Title) -> Title:
        """Insert new title (or new version).
        
        Creates a new row in the Title table. For versioned content,
        use create_next_version() to get a new Title instance with
        incremented version, then insert it.
        
        Args:
            entity: Title instance to insert. id will be auto-generated.
            
        Returns:
            The inserted Title with id populated.
        """
        cursor = self._conn.execute(
            "INSERT INTO Title (story_id, version, text, review_id, created_at) "
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
    
    def find_latest_version(self, story_id: int) -> Optional[Title]:
        """Find the most recent version of a title for a story.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            The Title with highest version number, or None if no titles exist.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Title WHERE story_id = ? "
            "ORDER BY version DESC LIMIT 1",
            (story_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_title(row)
    
    def find_versions(self, story_id: int) -> List[Title]:
        """Find all versions of a title for a story.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all Title versions ordered by version number (ascending).
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Title WHERE story_id = ? "
            "ORDER BY version ASC",
            (story_id,)
        )
        return [self._row_to_title(row) for row in cursor.fetchall()]
    
    def find_version(self, story_id: int, version: int) -> Optional[Title]:
        """Find a specific version of a title.
        
        Args:
            story_id: The story identifier.
            version: The version number (0, 1, 2, ...).
            
        Returns:
            The specific Title version, or None if not found.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Title WHERE story_id = ? AND version = ?",
            (story_id, version)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_title(row)
    
    def find_by_story_id(self, story_id: int) -> List[Title]:
        """Find all titles for a specific story.
        
        Alias for find_versions() for semantic clarity when querying
        by story rather than by base entity ID.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all Title versions for the story.
        """
        return self.find_versions(story_id)
    
    # === Current Version Convenience Methods ===
    
    def get_current_title(self, story_id: int) -> Optional[Title]:
        """Get the current (latest) title for a story.
        
        Convenience alias for find_latest_version(). Gets the title with
        the highest version number using ORDER BY version DESC LIMIT 1.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            The current Title for the story, or None if no titles exist.
        """
        return self.find_latest_version(story_id)
    
    # === Helper Methods ===
    
    def _row_to_title(self, row: sqlite3.Row) -> Title:
        """Convert database row to Title instance.
        
        Args:
            row: SQLite Row object with title data.
            
        Returns:
            Title instance populated from row data.
        """
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return Title(
            id=row["id"],
            story_id=row["story_id"],
            version=row["version"],
            text=row["text"],
            review_id=row["review_id"],
            created_at=created_at
        )
    
    def _get_next_version_number(self, story_id: int) -> int:
        """Get the next version number for a story's title.
        
        Private helper method to determine what version number to use
        when creating a new title version.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            Next version number (0 if no titles exist, otherwise max+1).
        """
        cursor = self._conn.execute(
            "SELECT MAX(version) as max_version FROM Title WHERE story_id = ?",
            (story_id,)
        )
        row = cursor.fetchone()
        max_version = row["max_version"] if row["max_version"] is not None else -1
        return max_version + 1
