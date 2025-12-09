"""ContentRepository - SQLite implementation for Content entities.

This module provides the SQLite implementation of IVersionedRepository
for Content entities, handling SQL DML (Data Manipulation Language) operations
only: SELECT, INSERT, UPDATE (limited to review_id FK).

Note:
    This repository does NOT handle schema creation (DDL). Use SchemaManager
    from Model.Database.schema_manager for database initialization.

Usage:
    >>> import sqlite3
    >>> from Model.Database.schema_manager import initialize_database
    >>> from Model.Database.repositories.content_repository import ContentRepository
    >>> from Model.Entities.content import Content
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> initialize_database(conn)  # Creates schema
    >>> 
    >>> repo = ContentRepository(conn)
    >>> content = Content(story_id=1, version=0, text="Once upon a time...")
    >>> saved = repo.insert(content)
    >>> 
    >>> # Find latest version
    >>> latest = repo.find_latest_version(story_id=1)
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from .base import IVersionedRepository
from Model.Entities.content import Content
from Model.Infrastructure.exceptions import (
    DuplicateEntityError,
    ForeignKeyViolationError,
    EntityNotFoundError,
    map_sqlite_error,
)


class ContentRepository(IVersionedRepository[Content, int]):
    """SQLite implementation of IVersionedRepository for Content entities.
    
    This repository handles SQL DML (Data Manipulation Language) operations
    for Content entities following the INSERT+READ only pattern. New versions
    are created instead of updating existing rows.
    
    Note:
        This repository does NOT create database tables. Schema initialization
        must be performed separately using SchemaManager.initialize_schema()
        before using this repository.
    
    Attributes:
        _conn: SQLite database connection with Row factory enabled.
    
    Example:
        >>> import sqlite3
        >>> from Model.Database.schema_manager import initialize_database
        >>> 
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> initialize_database(conn)  # Create schema first
        >>> 
        >>> repo = ContentRepository(conn)
        >>> content = Content(story_id=1, version=0, text="Original content")
        >>> saved = repo.insert(content)
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
    
    def find_by_id(self, id: int) -> Optional[Content]:
        """Find content by unique identifier.
        
        Args:
            id: The primary key of the content record.
            
        Returns:
            Content if found, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Content WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_content(row)
    
    def find_all(self) -> List[Content]:
        """Find all content records.
        
        Returns:
            List of all Content entities, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Content ORDER BY id"
        )
        return [self._row_to_content(row) for row in cursor.fetchall()]
    
    def exists(self, id: int) -> bool:
        """Check if content exists by ID.
        
        Args:
            id: The primary key to check.
            
        Returns:
            True if content exists, False otherwise.
        """
        cursor = self._conn.execute(
            "SELECT 1 FROM Content WHERE id = ?",
            (id,)
        )
        return cursor.fetchone() is not None
    
    # === INSERT Operation ===
    
    def insert(self, entity: Content) -> Content:
        """Insert new content (or new version).
        
        Creates a new row in the Content table. For versioned content,
        use create_next_version() to get a new Content instance with
        incremented version, then insert it.
        
        Args:
            entity: Content instance to insert. id will be auto-generated.
            
        Returns:
            The inserted Content with id populated.
            
        Raises:
            DuplicateEntityError: If (story_id, version) already exists.
            ForeignKeyViolationError: If story_id or review_id references non-existent entity.
        """
        try:
            cursor = self._conn.execute(
                "INSERT INTO Content (story_id, version, text, review_id, created_at) "
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
        except sqlite3.IntegrityError as e:
            raise map_sqlite_error(e, {
                "entity_type": "Content",
                "column": "story_id",
                "value": entity.story_id,
                "table": "Story",
                "constraint": "story_id, version"
            })
    
    # === IVersionedRepository Operations ===
    
    def find_latest_version(self, story_id: int) -> Optional[Content]:
        """Find the most recent version of a content for a story.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            The Content with highest version number, or None if no contents exist.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Content WHERE story_id = ? "
            "ORDER BY version DESC LIMIT 1",
            (story_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_content(row)
    
    def find_versions(self, story_id: int) -> List[Content]:
        """Find all versions of a content for a story.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all Content versions ordered by version number (ascending).
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Content WHERE story_id = ? "
            "ORDER BY version ASC",
            (story_id,)
        )
        return [self._row_to_content(row) for row in cursor.fetchall()]
    
    def find_version(self, story_id: int, version: int) -> Optional[Content]:
        """Find a specific version of a content.
        
        Args:
            story_id: The story identifier.
            version: The version number (0, 1, 2, ...).
            
        Returns:
            The specific Content version, or None if not found.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, version, text, review_id, created_at "
            "FROM Content WHERE story_id = ? AND version = ?",
            (story_id, version)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_content(row)
    
    def find_by_story_id(self, story_id: int) -> List[Content]:
        """Find all contents for a specific story.
        
        Alias for find_versions() for semantic clarity when querying
        by story rather than by base entity ID.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all Content versions for the story.
        """
        return self.find_versions(story_id)
    
    # === Current Version Convenience Methods ===
    
    def get_current_content(self, story_id: int) -> Optional[Content]:
        """Get the current (latest) content for a story.
        
        Convenience alias for find_latest_version(). Gets the content with
        the highest version number using ORDER BY version DESC LIMIT 1.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            The current Content for the story, or None if no contents exist.
        """
        return self.find_latest_version(story_id)
    
    # === UPDATE Operation (for review_id only) ===
    
    def update_review_id(self, content_id: int, review_id: int) -> bool:
        """Update the review_id FK on a Content.
        
        This is a limited update operation specifically for linking
        a Review to a Content after grammar/quality review is performed.
        
        Note:
            This is an exception to the INSERT+READ only pattern,
            allowed because review_id is a reference field, not content.
        
        Args:
            content_id: The content's primary key.
            review_id: The review to link (FK to Review table).
            
        Returns:
            True if the content was updated, False if not found.
            
        Raises:
            ForeignKeyViolationError: If review_id references non-existent Review.
            EntityNotFoundError: If content_id is not found.
        """
        try:
            cursor = self._conn.execute(
                "UPDATE Content SET review_id = ? WHERE id = ?",
                (review_id, content_id)
            )
            self._conn.commit()
            
            if cursor.rowcount == 0:
                raise EntityNotFoundError("Content", content_id)
            
            return True
        except sqlite3.IntegrityError as e:
            raise map_sqlite_error(e, {
                "entity_type": "Content",
                "entity_id": content_id,
                "column": "review_id",
                "value": review_id,
                "table": "Review"
            })
    
    # === Helper Methods ===
    
    def _row_to_content(self, row: sqlite3.Row) -> Content:
        """Convert database row to Content instance.
        
        Args:
            row: SQLite Row object with content data.
            
        Returns:
            Content instance populated from row data.
        """
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return Content(
            id=row["id"],
            story_id=row["story_id"],
            version=row["version"],
            text=row["text"],
            review_id=row["review_id"],
            created_at=created_at
        )
    
    def _get_next_version_number(self, story_id: int) -> int:
        """Get the next version number for a story's content.
        
        Private helper method to determine what version number to use
        when creating a new content version.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            Next version number (0 if no contents exist, otherwise max+1).
        """
        cursor = self._conn.execute(
            "SELECT MAX(version) as max_version FROM Content WHERE story_id = ?",
            (story_id,)
        )
        row = cursor.fetchone()
        max_version = row["max_version"] if row["max_version"] is not None else -1
        return max_version + 1
