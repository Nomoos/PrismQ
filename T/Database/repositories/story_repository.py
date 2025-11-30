"""StoryRepository - SQLite repository for Story entities.

This module provides the SQLite implementation of IUpdatableRepository
for Story entities. Unlike versioned entities (Title, Script), Story
supports UPDATE operations for state transitions.

Usage:
    >>> import sqlite3
    >>> from T.Database.repositories.story_repository import StoryRepository
    >>> from T.Database.models.story import Story, StoryState
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> repo = StoryRepository(conn)
    >>> 
    >>> # Create new story
    >>> story = Story(idea_id="idea-123")
    >>> saved = repo.insert(story)
    >>> 
    >>> # Update state
    >>> saved.transition_to(StoryState.TITLE_V0)
    >>> repo.update(saved)
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from .base import IUpdatableRepository
from ..models.story import Story, StoryState


class StoryRepository(IUpdatableRepository[Story, int]):
    """SQLite implementation of IUpdatableRepository for Story entities.
    
    This repository handles all database operations for Story entities.
    Unlike versioned repositories, StoryRepository supports UPDATE
    operations for state transitions.
    
    Attributes:
        _conn: SQLite database connection with Row factory enabled.
    
    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> repo = StoryRepository(conn)
        >>> 
        >>> # Create story
        >>> story = Story(idea_id="idea-123")
        >>> saved = repo.insert(story)
        >>> 
        >>> # Update state
        >>> saved.transition_to(StoryState.TITLE_V0)
        >>> updated = repo.update(saved)
        >>> print(updated.state.value)
        title_v0
    """
    
    def __init__(self, connection: sqlite3.Connection):
        """Initialize repository with database connection.
        
        Args:
            connection: SQLite connection with row_factory = sqlite3.Row
                recommended for dictionary-like row access.
        """
        self._conn = connection
    
    # === READ Operations ===
    
    def find_by_id(self, id: int) -> Optional[Story]:
        """Find story by unique identifier.
        
        Args:
            id: The primary key of the story record.
            
        Returns:
            Story if found, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_story(row)
    
    def find_all(self) -> List[Story]:
        """Find all story records.
        
        Returns:
            List of all Story entities, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story ORDER BY id"
        )
        return [self._row_to_story(row) for row in cursor.fetchall()]
    
    def exists(self, id: int) -> bool:
        """Check if story exists by ID.
        
        Args:
            id: The primary key to check.
            
        Returns:
            True if story exists, False otherwise.
        """
        cursor = self._conn.execute(
            "SELECT 1 FROM Story WHERE id = ?",
            (id,)
        )
        return cursor.fetchone() is not None
    
    # === INSERT Operation ===
    
    def insert(self, entity: Story) -> Story:
        """Insert new story.
        
        Creates a new row in the Story table.
        
        Args:
            entity: Story instance to insert. id will be auto-generated.
            
        Returns:
            The inserted Story with id populated.
        """
        cursor = self._conn.execute(
            "INSERT INTO Story (idea_id, state, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (
                entity.idea_id,
                entity.state.value,
                entity.created_at.isoformat(),
                entity.updated_at.isoformat()
            )
        )
        self._conn.commit()
        
        # Update entity with generated ID
        entity.id = cursor.lastrowid
        return entity
    
    # === UPDATE Operation (IUpdatableRepository) ===
    
    def update(self, entity: Story) -> Story:
        """Update existing story.
        
        Updates the state and updated_at fields for an existing story.
        
        Args:
            entity: Story instance to update. Must have a valid ID.
            
        Returns:
            The updated Story.
            
        Raises:
            ValueError: If entity has no ID (not yet persisted).
        """
        if entity.id is None:
            raise ValueError("Cannot update Story without ID")
        
        # Update the updated_at timestamp
        entity.updated_at = datetime.now()
        
        self._conn.execute(
            "UPDATE Story SET state = ?, updated_at = ? WHERE id = ?",
            (
                entity.state.value,
                entity.updated_at.isoformat(),
                entity.id
            )
        )
        self._conn.commit()
        
        return entity
    
    # === Additional Query Methods ===
    
    def find_by_idea_id(self, idea_id: str) -> List[Story]:
        """Find all stories for a specific idea.
        
        Args:
            idea_id: The idea identifier.
            
        Returns:
            List of all Story entities for the idea, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story WHERE idea_id = ? ORDER BY id",
            (idea_id,)
        )
        return [self._row_to_story(row) for row in cursor.fetchall()]
    
    def find_by_state(self, state: StoryState) -> List[Story]:
        """Find all stories in a specific state.
        
        Args:
            state: The StoryState to filter by.
            
        Returns:
            List of all Story entities in that state, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story WHERE state = ? ORDER BY id",
            (state.value,)
        )
        return [self._row_to_story(row) for row in cursor.fetchall()]
    
    def count_by_idea_id(self, idea_id: str) -> int:
        """Count stories for a specific idea.
        
        Args:
            idea_id: The idea identifier.
            
        Returns:
            Number of stories for the idea.
        """
        cursor = self._conn.execute(
            "SELECT COUNT(*) as count FROM Story WHERE idea_id = ?",
            (idea_id,)
        )
        row = cursor.fetchone()
        return row["count"] if row else 0
    
    # === Helper Methods ===
    
    def _row_to_story(self, row: sqlite3.Row) -> Story:
        """Convert database row to Story instance.
        
        Args:
            row: SQLite Row object with story data.
            
        Returns:
            Story instance populated from row data.
        """
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = row["updated_at"]
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        state = row["state"]
        if isinstance(state, str):
            state = StoryState(state)
        
        return Story(
            id=row["id"],
            idea_id=row["idea_id"],
            state=state,
            created_at=created_at,
            updated_at=updated_at
        )
    
    def create_table(self) -> None:
        """Create the Story table if it doesn't exist.
        
        This is a convenience method for setting up the database schema.
        """
        self._conn.executescript(Story.get_sql_schema())
        self._conn.commit()
