"""Story Repository - SQLite implementation for Story entities.

This module provides SQLite implementation of the IUpdatableRepository interface
for Story entities, handling SQL DML (Data Manipulation Language) operations
only: SELECT, INSERT, UPDATE.

Note:
    This repository does NOT handle schema creation (DDL). Use SchemaManager
    from Model.Database.schema_manager for database initialization.

Usage:
    >>> import sqlite3
    >>> from Model.Database.schema_manager import initialize_database
    >>> from Model.Database.repositories.story_repository import StoryRepository
    >>> from Model.Database.models.story import Story
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> initialize_database(conn)  # Creates schema
    >>> 
    >>> repo = StoryRepository(conn)
    >>> story = Story(idea_id=1, state="PrismQ.T.Title.From.Idea")
    >>> saved = repo.insert(story)
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from Model.Database.repositories.base import IUpdatableRepository
from Model.Database.models.story import Story
from Model.State.validators.transition_validator import TransitionValidator
from Model.Database.exceptions import (
    EntityNotFoundError,
    ForeignKeyViolationError,
    ConstraintViolationError,
    InvalidStateTransitionError,
    map_sqlite_error,
)


class StoryRepository(IUpdatableRepository[Story, int]):
    """SQLite implementation of IUpdatableRepository for Story entities.
    
    This repository handles SQL DML (Data Manipulation Language) operations
    for Story entities following the CRUD pattern (with UPDATE capability
    for state changes).
    
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
        >>> repo = StoryRepository(conn)
        >>> story = Story(idea_id=1)
        >>> saved = repo.insert(story)
        >>> print(saved.id)  # Auto-generated ID
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
        self._transition_validator = TransitionValidator()
    
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
        
        return self._row_to_model(row)
    
    def find_all(self) -> List[Story]:
        """Find all story records.
        
        Returns:
            List of all Story entities, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story ORDER BY id"
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
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
            
        Raises:
            ForeignKeyViolationError: If idea_id references non-existent Idea.
            ConstraintViolationError: If any constraint is violated.
        """
        try:
            cursor = self._conn.execute(
                "INSERT INTO Story (idea_id, state, created_at, updated_at) "
                "VALUES (?, ?, ?, ?)",
                (
                    entity.idea_id,
                    entity.state,
                    entity.created_at.isoformat(),
                    entity.updated_at.isoformat()
                )
            )
            self._conn.commit()
            
            # Update entity with generated ID
            entity.id = cursor.lastrowid
            return entity
        except sqlite3.IntegrityError as e:
            raise map_sqlite_error(e, {
                "entity_type": "Story",
                "column": "idea_id",
                "value": entity.idea_id,
                "table": "Idea"
            })
    
    # === UPDATE Operation ===
    
    def update(self, entity: Story) -> Story:
        """Update existing story in place.
        
        This method updates an existing story's fields in the database.
        Unlike versioned entities, this modifies the same row.
        
        State transitions are validated using TransitionValidator before saving.
        Invalid transitions will print a detailed error message for debugging.
        
        Args:
            entity: Story to update. Must have a valid ID.
            
        Returns:
            The updated Story (same instance with changes persisted).
            
        Raises:
            EntityNotFoundError: If entity has no ID or is not found.
            InvalidStateTransitionError: If state transition is invalid.
            ForeignKeyViolationError: If foreign key constraint is violated.
        """
        if entity.id is None:
            raise EntityNotFoundError("Story", None, None)
        
        # Get current state from database to validate transition
        current_story = self.find_by_id(entity.id)
        if current_story is None:
            raise EntityNotFoundError("Story", entity.id, None)
        
        current_state = current_story.state
        new_state = entity.state
        
        # Validate state transition if state is changing
        if current_state != new_state:
            validation_result = self._transition_validator.validate(current_state, new_state)
            
            if not validation_result.is_valid:
                # Print detailed error message for debugging (copilot-friendly format)
                error_msg = (
                    f"\n"
                    f"╔══════════════════════════════════════════════════════════════════╗\n"
                    f"║  INVALID STATE TRANSITION                                        ║\n"
                    f"╠══════════════════════════════════════════════════════════════════╣\n"
                    f"║  Story ID: {entity.id}\n"
                    f"║  From State: {current_state}\n"
                    f"║  To State: {new_state}\n"
                    f"║  Error: {validation_result.error_message}\n"
                    f"╠══════════════════════════════════════════════════════════════════╣\n"
                    f"║  Valid transitions from '{current_state}':\n"
                )
                valid_next = self._transition_validator.get_valid_next_states(current_state)
                for valid_state in valid_next:
                    error_msg += f"║    - {valid_state}\n"
                if not valid_next:
                    error_msg += f"║    (none - terminal state)\n"
                error_msg += (
                    f"╚══════════════════════════════════════════════════════════════════╝\n"
                )
                print(error_msg)
                raise InvalidStateTransitionError(
                    from_state=current_state,
                    to_state=new_state,
                    entity_id=entity.id
                )
        
        # Update the updated_at timestamp
        entity.updated_at = datetime.now()
        
        try:
            self._conn.execute(
                "UPDATE Story SET idea_id = ?, state = ?, updated_at = ? WHERE id = ?",
                (
                    entity.idea_id,
                    entity.state,
                    entity.updated_at.isoformat(),
                    entity.id
                )
            )
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            raise map_sqlite_error(e, {
                "entity_type": "Story",
                "entity_id": entity.id,
                "column": "idea_id",
                "value": entity.idea_id,
                "table": "Idea"
            })
        
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
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story WHERE state = ? ORDER BY id",
            (state,)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def find_by_idea_id(self, idea_id: str) -> List[Story]:
        """Find all stories for a specific idea.
        
        Args:
            idea_id: The idea ID to filter by (TEXT in database).
            
        Returns:
            List of Story entities for the specified idea.
        """
        cursor = self._conn.execute(
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story WHERE idea_id = ? ORDER BY id",
            (idea_id,)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def count_by_idea_id(self, idea_id: str) -> int:
        """Count stories for a specific idea.
        
        Args:
            idea_id: The idea ID to count stories for.
            
        Returns:
            Number of stories for the specified idea.
        """
        cursor = self._conn.execute(
            "SELECT COUNT(*) FROM Story WHERE idea_id = ?",
            (idea_id,)
        )
        return cursor.fetchone()[0]
    
    def find_by_state_ordered_by_created(self, state: str, ascending: bool = True) -> List[Story]:
        """Find all stories in a specific state, ordered by creation date.
        
        This method is useful for processing stories in the order they were created,
        particularly for workflow states like 'PrismQ.T.Script.From.Idea.Title'.
        
        Args:
            state: The state to filter by (e.g., 'PrismQ.T.Script.From.Idea.Title').
            ascending: If True, oldest first (ASC). If False, newest first (DESC).
            
        Returns:
            List of Story entities in the specified state, ordered by created_at.
            
        Example:
            >>> # Find stories ready for script generation, oldest first
            >>> stories = repo.find_by_state_ordered_by_created(
            ...     'PrismQ.T.Script.From.Idea.Title',
            ...     ascending=True
            ... )
        """
        order = "ASC" if ascending else "DESC"
        cursor = self._conn.execute(
            f"SELECT id, idea_id, state, created_at, updated_at "
            f"FROM Story WHERE state = ? ORDER BY created_at {order}",
            (state,)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def find_oldest_by_state(self, state: str) -> Optional[Story]:
        """Find the oldest story in a specific state.
        
        This method is useful for processing stories in FIFO order,
        particularly for workflow states like 'PrismQ.T.Script.From.Idea.Title'.
        
        Args:
            state: The state to filter by (e.g., 'PrismQ.T.Script.From.Idea.Title').
            
        Returns:
            The oldest Story entity in the specified state, or None if no stories found.
            
        Example:
            >>> # Find oldest story ready for script generation
            >>> story = repo.find_oldest_by_state('PrismQ.T.Script.From.Idea.Title')
            >>> if story:
            ...     print(f"Processing story {story.id}")
        """
        cursor = self._conn.execute(
            "SELECT id, idea_id, state, created_at, updated_at "
            "FROM Story WHERE state = ? ORDER BY created_at ASC LIMIT 1",
            (state,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_model(row)
    
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
    
    def find_next_for_processing(self, state: str) -> Optional[Story]:
        """Find the next story to process for a given state/module.
        
        Selection criteria in order:
        1. Story must have the specified state (full module name)
        2. Select by lowest version (based on module type - see below)
        3. Select by highest Story score (AVG of Script and Title review scores)
        4. Select oldest story by created_at timestamp
        
        Args:
            state: The full module name to filter by
                   (e.g., 'PrismQ.T.Script.From.Idea.Title').
                   
        Returns:
            The next Story to process, or None if no matching stories found.
            
        Note:
            Version selection by module type (PrismQ.T.<Type>.*):
            - PrismQ.T.Script.*: Uses max Script version
            - PrismQ.T.Title.*: Uses max Title version
            - PrismQ.T.Review.Script.*: Uses max Script version (reviewing scripts)
            - PrismQ.T.Review.Title.*: Uses max Title version (reviewing titles)
            - PrismQ.T.Story.*: Uses max of both Script and Title versions
            
            Story score is the average of Script and Title review scores (0 if no reviews)
            
        Example:
            >>> # Find next story for script generation
            >>> story = repo.find_next_for_processing('PrismQ.T.Script.From.Idea.Title')
            >>> if story:
            ...     print(f"Processing story {story.id}")
            >>> 
            >>> # Find next story for script review
            >>> story = repo.find_next_for_processing('PrismQ.T.Review.Script.Grammar')
        """
        # Determine module type from state pattern
        # Patterns: PrismQ.T.<Type>.* where Type is Script, Title, Review, or Story
        module_type = self._get_module_type(state)
        
        # Build the query with subqueries for version and score calculation
        # For version: get MAX version from relevant table based on module type
        # For score: get AVG of latest Script and Title review scores
        
        version_subquery = self._get_version_subquery(module_type)
        
        # Story score is average of latest script and title review scores
        # Latest script/title is determined by MAX version
        # Review score comes from Review table via review_id FK
        # Note: Missing reviews are treated as 0 score per the requirement:
        # "AVG between Script and Title review score" - this means sum/2 always
        # This favors stories with both reviews over those with only one
        score_subquery = """
            (
                COALESCE(
                    (SELECT r1.score FROM Review r1
                     INNER JOIN Script s ON s.review_id = r1.id
                     WHERE s.story_id = Story.id
                     ORDER BY s.version DESC LIMIT 1),
                    0
                ) +
                COALESCE(
                    (SELECT r2.score FROM Review r2
                     INNER JOIN Title t ON t.review_id = r2.id
                     WHERE t.story_id = Story.id
                     ORDER BY t.version DESC LIMIT 1),
                    0
                )
            ) / 2.0
        """
        
        # Build query with parameterized state value
        # The version and score subqueries are constructed from internal logic only
        # and do not include any user-provided input
        query = f"""
            SELECT id, idea_id, state, created_at, updated_at
            FROM Story
            WHERE state = ?
            ORDER BY
                {version_subquery} ASC,
                {score_subquery} DESC,
                created_at ASC
            LIMIT 1
        """
        
        cursor = self._conn.execute(query, (state,))
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_model(row)
    
    # === Helper Methods ===
    
    def _get_module_type(self, state: str) -> str:
        """Determine the module type from the state pattern.
        
        Module types:
        - 'script': PrismQ.T.Script.* modules
        - 'title': PrismQ.T.Title.* modules
        - 'review_script': PrismQ.T.Review.Script.* modules
        - 'review_title': PrismQ.T.Review.Title.* modules
        - 'story': PrismQ.T.Story.* modules
        
        Args:
            state: The full module name (e.g., 'PrismQ.T.Script.From.Idea.Title')
            
        Returns:
            The module type string
        """
        if not state.startswith("PrismQ.T."):
            return "unknown"
        
        rest = state[len("PrismQ.T."):]
        
        # Check more specific patterns first before general patterns
        if rest.startswith("Review.Script"):
            return "review_script"
        elif rest.startswith("Review.Title"):
            return "review_title"
        elif rest.startswith("Script"):
            return "script"
        elif rest.startswith("Title"):
            return "title"
        elif rest.startswith("Story"):
            return "story"
        else:
            return "unknown"
    
    def _get_version_subquery(self, module_type: str) -> str:
        """Get the SQL subquery for version calculation based on module type.
        
        Args:
            module_type: The module type from _get_module_type
            
        Returns:
            SQL subquery string for version calculation
        """
        script_version = """
            COALESCE(
                (SELECT MAX(s.version) FROM Script s WHERE s.story_id = Story.id),
                0
            )
        """
        
        title_version = """
            COALESCE(
                (SELECT MAX(t.version) FROM Title t WHERE t.story_id = Story.id),
                0
            )
        """
        
        # For story modules, use the maximum of both versions
        combined_version = (
            "MAX("
            + script_version.strip()
            + ", "
            + title_version.strip()
            + ")"
        )
        
        if module_type == "script":
            return script_version
        elif module_type == "title":
            return title_version
        elif module_type == "review_script":
            return script_version
        elif module_type == "review_title":
            return title_version
        elif module_type == "story":
            return combined_version
        else:
            # Default to combined version for unknown types
            return combined_version
    
    def preview_next_for_processing(self, state: str, wait_for_confirm: bool = True) -> Optional[Story]:
        """Preview the next story to process and optionally wait for confirmation.
        
        This method displays the selected story details in a formatted way
        and waits for user confirmation before returning the story for processing.
        
        Args:
            state: The full module name to filter by
                   (e.g., 'PrismQ.T.Script.From.Idea.Title').
            wait_for_confirm: If True, wait for user keystroke before returning.
                              If False, just display and return immediately.
                   
        Returns:
            The selected Story if found and confirmed, None otherwise.
            
        Example:
            >>> # Preview next story for script generation
            >>> story = repo.preview_next_for_processing('PrismQ.T.Script.From.Idea.Title')
            >>> if story:
            ...     # Process the story
            ...     pass
        """
        story = self.find_next_for_processing(state)
        
        if story is None:
            print(f"\n{'═' * 70}")
            print(f"  Module: {state}")
            print(f"{'═' * 70}")
            print(f"  No stories found for processing in state: {state}")
            print(f"{'═' * 70}\n")
            return None
        
        # Display story details
        print(f"\n{'═' * 70}")
        print(f"  SELECTED STORY FOR PROCESSING")
        print(f"  Module: {state}")
        print(f"{'═' * 70}")
        print(f"  Story ID: {story.id}")
        print(f"  State: {story.state}")
        print(f"  Idea ID: {story.idea_id}")
        print(f"  Created: {story.created_at}")
        print(f"  Updated: {story.updated_at}")
        print(f"{'═' * 70}")
        
        if wait_for_confirm:
            try:
                input("  Press ENTER to continue processing or Ctrl+C to cancel...")
                print(f"{'═' * 70}\n")
                return story
            except KeyboardInterrupt:
                print(f"\n  Processing cancelled by user.")
                print(f"{'═' * 70}\n")
                return None
        else:
            print(f"{'═' * 70}\n")
            return story
    
    def _row_to_model(self, row: sqlite3.Row) -> Story:
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
            idea_id=row["idea_id"],
            state=row["state"],
            created_at=created_at,
            updated_at=updated_at
        )
