"""Story Repository - SQLite implementation for Story entities.

This module provides SQLite implementation of the IUpdatableRepository interface
for Story entities, handling all database operations including UPDATE for
state transitions.
"""StoryRepository - SQLite repository for Story entities.

This module provides the SQLite implementation of IUpdatableRepository
for Story entities. Unlike versioned entities (Title, Script), Story
supports UPDATE operations for state transitions.

Usage:
    >>> import sqlite3
    >>> from T.Database.repositories.story_repository import StoryRepository
    >>> from T.Database.models.story import Story
    >>> from T.Database.models.story import Story, StoryState
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> repo = StoryRepository(conn)
    >>> 
    >>> # Insert new story
    >>> story = Story(idea_json='{"title": "Test", "concept": "Test concept"}')
    >>> saved = repo.insert(story)
    >>> 
    >>> # Find stories needing scripts
    >>> stories = repo.find_needing_script()
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

from T.Database.repositories.base import IUpdatableRepository
from T.Database.models.story import Story
from .base import IUpdatableRepository
from ..models.story import Story, StoryState


class StoryRepository(IUpdatableRepository[Story, int]):
    """SQLite implementation of IUpdatableRepository for Story entities.
    
    This repository handles all database operations for Story
    following the CRUD pattern (with UPDATE capability for state changes).
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
        >>> # Create schema
        >>> conn.executescript(Story.get_sql_schema())
        >>> 
        >>> # Insert story
        >>> story = Story(idea_json='{"title": "Test"}')
        >>> saved = repo.insert(story)
        >>> print(saved.id)  # Auto-generated ID
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
            "SELECT id, idea_json, title_id, script_id, state, created_at, updated_at "
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_model(row)
        return self._row_to_story(row)
    
    def find_all(self) -> List[Story]:
        """Find all story records.
        
        Returns:
            List of all Story entities, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_json, title_id, script_id, state, created_at, updated_at "
            "FROM Story ORDER BY id"
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
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
            "INSERT INTO Story (idea_json, title_id, script_id, state, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                entity.idea_json,
                entity.title_id,
                entity.script_id,
                entity.state,
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
    
    # === UPDATE Operation ===
    
    def update(self, entity: Story) -> Story:
        """Update existing story in place.
        
        This method updates an existing story's fields in the database.
        Unlike versioned entities, this modifies the same row.
        
        Args:
            entity: Story to update. Must have a valid ID.
            
        Returns:
            The updated Story (same instance with changes persisted).
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
            raise ValueError("Cannot update story without ID")
            raise ValueError("Cannot update Story without ID")
        
        # Update the updated_at timestamp
        entity.updated_at = datetime.now()
        
        self._conn.execute(
            "UPDATE Story SET idea_json = ?, title_id = ?, script_id = ?, "
            "state = ?, updated_at = ? WHERE id = ?",
            (
                entity.idea_json,
                entity.title_id,
                entity.script_id,
                entity.state,
            "UPDATE Story SET state = ?, updated_at = ? WHERE id = ?",
            (
                entity.state.value,
                entity.updated_at.isoformat(),
                entity.id
            )
        )
        self._conn.commit()
        
        return entity
    
    # === Custom Query Methods ===
    
    def find_by_state(self, state: str) -> List[Story]:
        """Find all stories in a specific state.
        
        Args:
            state: The state to filter by (e.g., 'IDEA', 'TITLE', 'SCRIPT').
            
        Returns:
            List of Story entities in the specified state.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_json, title_id, script_id, state, created_at, updated_at "
            "FROM Story WHERE state = ? ORDER BY id",
            (state,)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def find_needing_script(self) -> List[Story]:
        """Find all stories that need script generation.
        
        A story needs a script if:
        - It has an idea (idea_json IS NOT NULL)
        - It has a title (title_id IS NOT NULL)
        - It does not have a script (script_id IS NULL)
        
        Returns:
            List of Story entities ready for script generation.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_json, title_id, script_id, state, created_at, updated_at "
            "FROM Story "
            "WHERE idea_json IS NOT NULL "
            "AND title_id IS NOT NULL "
            "AND script_id IS NULL "
            "ORDER BY id"
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def find_needing_title(self) -> List[Story]:
        """Find all stories that need title generation.
        
        A story needs a title if:
        - It has an idea (idea_json IS NOT NULL)
        - It does not have a title (title_id IS NULL)
        
        Returns:
            List of Story entities ready for title generation.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_json, title_id, script_id, state, created_at, updated_at "
            "FROM Story "
            "WHERE idea_json IS NOT NULL "
            "AND title_id IS NULL "
            "ORDER BY id"
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def find_with_script(self) -> List[Story]:
        """Find all stories that have a script.
        
        Returns:
            List of Story entities that have script_id set.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_json, title_id, script_id, state, created_at, updated_at "
            "FROM Story "
            "WHERE script_id IS NOT NULL "
            "ORDER BY id"
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def count_by_state(self, state: str) -> int:
        """Count stories in a specific state.
        
        Args:
            state: The state to count.
            
        Returns:
            Number of stories in the specified state.
        """
        cursor = self._conn.execute(
            "SELECT COUNT(*) FROM Story WHERE state = ?",
            (state,)
        )
        return cursor.fetchone()[0]
    
    def count_needing_script(self) -> int:
        """Count stories that need script generation.
        
        Returns:
            Number of stories ready for script generation.
        """
        cursor = self._conn.execute(
            "SELECT COUNT(*) FROM Story "
            "WHERE idea_json IS NOT NULL "
            "AND title_id IS NOT NULL "
            "AND script_id IS NULL"
        )
        return cursor.fetchone()[0]
    
    # === Helper Methods ===
    
    def _row_to_model(self, row: sqlite3.Row) -> Story:
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
        
        return Story(
            id=row["id"],
            idea_json=row["idea_json"],
            title_id=row["title_id"],
            script_id=row["script_id"],
            state=row["state"],
            created_at=created_at,
            updated_at=updated_at
        )
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
