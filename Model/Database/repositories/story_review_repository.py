"""StoryReview Repository - SQLite implementation for StoryReview entities.

This module provides SQLite implementation of the IRepository interface
for StoryReviewModel entities, handling all database operations for the
StoryReview linking table.

Usage:
    >>> import sqlite3
    >>> from Model.Database.repositories.story_review_repository import StoryReviewRepository
    >>> from Model.Database.models.story_review import StoryReviewModel, ReviewType
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> repo = StoryReviewRepository(conn)
    >>> 
    >>> # Insert new story review
    >>> review = StoryReviewModel(
    ...     story_id=1, review_id=5, version=0, review_type=ReviewType.GRAMMAR
    ... )
    >>> saved = repo.insert(review)
    >>> 
    >>> # Find reviews for a story
    >>> reviews = repo.find_by_story_id(1)
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from Model.Database.repositories.base import IRepository
from Model.Database.models.story_review import StoryReviewModel, ReviewType


class StoryReviewRepository(IRepository[StoryReviewModel, int]):
    """SQLite implementation of IRepository for StoryReview entities.
    
    This repository handles all database operations for StoryReviewModel
    following the INSERT+READ only pattern. The StoryReview table acts as
    a linking table between Story and Review, with additional metadata
    (version, review_type).
    
    Attributes:
        _conn: SQLite database connection with Row factory enabled.
    
    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> repo = StoryReviewRepository(conn)
        >>> 
        >>> # Create schema
        >>> conn.executescript(StoryReviewModel.get_sql_schema())
        >>> 
        >>> # Insert review link
        >>> review = StoryReviewModel(
        ...     story_id=1, review_id=5, version=0, review_type=ReviewType.GRAMMAR
        ... )
        >>> saved = repo.insert(review)
        >>> print(saved.id)  # Auto-generated ID
    """
    
    def __init__(self, connection: sqlite3.Connection):
        """Initialize repository with database connection.
        
        Args:
            connection: SQLite connection with row_factory = sqlite3.Row
                recommended for dictionary-like row access.
        """
        self._conn = connection
    
    # === READ Operations ===
    
    def find_by_id(self, id: int) -> Optional[StoryReviewModel]:
        """Find story review by unique identifier.
        
        Args:
            id: The primary key of the story review record.
            
        Returns:
            StoryReviewModel if found, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, review_id, version, review_type, created_at "
            "FROM StoryReview WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_model(row)
    
    def find_all(self) -> List[StoryReviewModel]:
        """Find all story review records.
        
        Returns:
            List of all StoryReviewModel entities, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, review_id, version, review_type, created_at "
            "FROM StoryReview ORDER BY id"
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def exists(self, id: int) -> bool:
        """Check if story review exists by ID.
        
        Args:
            id: The primary key to check.
            
        Returns:
            True if story review exists, False otherwise.
        """
        cursor = self._conn.execute(
            "SELECT 1 FROM StoryReview WHERE id = ?",
            (id,)
        )
        return cursor.fetchone() is not None
    
    # === INSERT Operation ===
    
    def insert(self, entity: StoryReviewModel) -> StoryReviewModel:
        """Insert new story review link.
        
        Creates a new row in the StoryReview table linking a Story
        to a Review with additional metadata (version, review_type).
        
        Args:
            entity: StoryReviewModel instance to insert. id will be auto-generated.
            
        Returns:
            The inserted StoryReviewModel with id populated.
            
        Note:
            UNIQUE(story_id, version, review_type) constraint prevents
            duplicate reviews of the same type for the same story version.
        """
        cursor = self._conn.execute(
            "INSERT INTO StoryReview (story_id, review_id, version, review_type, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                entity.story_id,
                entity.review_id,
                entity.version,
                entity.review_type.value,
                entity.created_at.isoformat()
            )
        )
        self._conn.commit()
        
        # Update entity with generated ID
        entity.id = cursor.lastrowid
        return entity
    
    # === Custom Query Methods ===
    
    def find_latest_version(self, story_id: int) -> Optional[int]:
        """Find the latest (highest) version number for a story's reviews.
        
        Determines the current version by querying with ORDER BY version DESC LIMIT 1.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            The highest version number if reviews exist, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT version FROM StoryReview WHERE story_id = ? "
            "ORDER BY version DESC LIMIT 1",
            (story_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return row["version"]
    
    def find_latest_reviews(self, story_id: int) -> List[StoryReviewModel]:
        """Find all reviews for the latest version of a story.
        
        Gets the current version using ORDER BY version DESC LIMIT 1,
        then returns all reviews for that version.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all StoryReviewModel entities for the latest story version,
            ordered by review_type. Returns empty list if no reviews exist.
        """
        latest_version = self.find_latest_version(story_id)
        
        if latest_version is None:
            return []
        
        return self.find_by_story_and_version(story_id, latest_version)
    
    def find_latest_review_by_type(
        self, story_id: int, review_type: ReviewType
    ) -> Optional[StoryReviewModel]:
        """Find the latest review of a specific type for a story.
        
        Gets the current version for the given review type using 
        ORDER BY version DESC LIMIT 1.
        
        Args:
            story_id: The story identifier.
            review_type: The type of review (grammar, tone, content, etc.).
            
        Returns:
            The latest StoryReviewModel of the specified type, or None if not found.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, review_id, version, review_type, created_at "
            "FROM StoryReview WHERE story_id = ? AND review_type = ? "
            "ORDER BY version DESC LIMIT 1",
            (story_id, review_type.value)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_model(row)
    
    def find_by_story_id(self, story_id: int) -> List[StoryReviewModel]:
        """Find all reviews for a specific story.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all StoryReviewModel entities for the story,
            ordered by version and review_type.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, review_id, version, review_type, created_at "
            "FROM StoryReview WHERE story_id = ? "
            "ORDER BY version, review_type",
            (story_id,)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def find_by_story_and_version(
        self, story_id: int, version: int
    ) -> List[StoryReviewModel]:
        """Find all reviews for a specific story version.
        
        Args:
            story_id: The story identifier.
            version: The story version number.
            
        Returns:
            List of all StoryReviewModel entities for the story version,
            ordered by review_type.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, review_id, version, review_type, created_at "
            "FROM StoryReview WHERE story_id = ? AND version = ? "
            "ORDER BY review_type",
            (story_id, version)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def find_by_story_version_type(
        self, story_id: int, version: int, review_type: ReviewType
    ) -> Optional[StoryReviewModel]:
        """Find a specific review by story, version, and type.
        
        This uses the UNIQUE constraint (story_id, version, review_type)
        to find exactly one record.
        
        Args:
            story_id: The story identifier.
            version: The story version number.
            review_type: The type of review (grammar, tone, etc.).
            
        Returns:
            The specific StoryReviewModel if found, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, review_id, version, review_type, created_at "
            "FROM StoryReview WHERE story_id = ? AND version = ? AND review_type = ?",
            (story_id, version, review_type.value)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_model(row)
    
    def find_by_review_id(self, review_id: int) -> List[StoryReviewModel]:
        """Find all story reviews linked to a specific review.
        
        Args:
            review_id: The review identifier (FK to Review table).
            
        Returns:
            List of all StoryReviewModel entities linked to the review.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, review_id, version, review_type, created_at "
            "FROM StoryReview WHERE review_id = ? "
            "ORDER BY story_id, version",
            (review_id,)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def find_by_review_type(self, review_type: ReviewType) -> List[StoryReviewModel]:
        """Find all story reviews of a specific type.
        
        Args:
            review_type: The type of review (grammar, tone, etc.).
            
        Returns:
            List of all StoryReviewModel entities of the specified type,
            ordered by story_id and version.
        """
        cursor = self._conn.execute(
            "SELECT id, story_id, review_id, version, review_type, created_at "
            "FROM StoryReview WHERE review_type = ? "
            "ORDER BY story_id, version",
            (review_type.value,)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    # === Current Version Convenience Methods ===
    
    def get_current_story_reviews(self, story_id: int) -> List[StoryReviewModel]:
        """Get all reviews for the current (latest) version of a story.
        
        Convenience alias for find_latest_reviews(). Uses 
        ORDER BY version DESC LIMIT 1 to determine the current version.
        
        Args:
            story_id: The story identifier.
            
        Returns:
            List of all StoryReviewModel entities for the current story version,
            ordered by review_type. Returns empty list if no reviews exist.
        """
        return self.find_latest_reviews(story_id)
    
    def get_current_story_review(
        self, story_id: int, review_type: ReviewType
    ) -> Optional[StoryReviewModel]:
        """Get the current (latest) review of a specific type for a story.
        
        Convenience alias for find_latest_review_by_type(). Uses 
        ORDER BY version DESC LIMIT 1 to find the most recent review.
        
        Args:
            story_id: The story identifier.
            review_type: The type of review (grammar, tone, content, etc.).
            
        Returns:
            The current StoryReviewModel of the specified type, or None if not found.
        """
        return self.find_latest_review_by_type(story_id, review_type)
    
    # === Helper Methods ===
    
    def _row_to_model(self, row: sqlite3.Row) -> StoryReviewModel:
        """Convert database row to StoryReviewModel instance.
        
        Args:
            row: SQLite Row object with story review data.
            
        Returns:
            StoryReviewModel instance populated from row data.
        """
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return StoryReviewModel(
            id=row["id"],
            story_id=row["story_id"],
            review_id=row["review_id"],
            version=row["version"],
            review_type=ReviewType(row["review_type"]),
            created_at=created_at
        )
