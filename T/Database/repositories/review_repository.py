"""Review Repository - SQLite implementation for Review entities.

This module provides SQLite implementation of the IRepository interface
for Review entities, handling all database operations.

Usage:
    >>> import sqlite3
    >>> from T.Database.repositories.review_repository import ReviewRepository
    >>> from T.Database.models.review import Review
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> repo = ReviewRepository(conn)
    >>> 
    >>> # Insert new review
    >>> review = Review(text="Great script!", score=85)
    >>> saved = repo.insert(review)
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from T.Database.repositories.base import IRepository
from T.Database.models.review import Review


class ReviewRepository(IRepository[Review, int]):
    """SQLite implementation of IRepository for Review entities.
    
    This repository handles all database operations for Review
    following the INSERT+READ only pattern.
    
    Attributes:
        _conn: SQLite database connection with Row factory enabled.
    
    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> repo = ReviewRepository(conn)
        >>> 
        >>> # Create schema
        >>> conn.executescript(ReviewRepository.get_sql_schema())
        >>> 
        >>> # Insert review
        >>> review = Review(text="Great script!", score=85)
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
    
    def find_by_id(self, id: int) -> Optional[Review]:
        """Find review by unique identifier.
        
        Args:
            id: The primary key of the review record.
            
        Returns:
            Review if found, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT id, text, score, created_at "
            "FROM Review WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_model(row)
    
    def find_all(self) -> List[Review]:
        """Find all review records.
        
        Returns:
            List of all Review entities, ordered by id.
        """
        cursor = self._conn.execute(
            "SELECT id, text, score, created_at "
            "FROM Review ORDER BY id"
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def exists(self, id: int) -> bool:
        """Check if review exists by ID.
        
        Args:
            id: The primary key to check.
            
        Returns:
            True if review exists, False otherwise.
        """
        cursor = self._conn.execute(
            "SELECT 1 FROM Review WHERE id = ?",
            (id,)
        )
        return cursor.fetchone() is not None
    
    # === INSERT Operation ===
    
    def insert(self, entity: Review) -> Review:
        """Insert new review.
        
        Creates a new row in the Review table.
        
        Args:
            entity: Review instance to insert. id will be auto-generated.
            
        Returns:
            The inserted Review with id populated.
        """
        cursor = self._conn.execute(
            "INSERT INTO Review (text, score, created_at) "
            "VALUES (?, ?, ?)",
            (
                entity.text,
                entity.score,
                entity.created_at.isoformat()
            )
        )
        self._conn.commit()
        
        # Update entity with generated ID
        entity.id = cursor.lastrowid
        return entity
    
    # === Custom Query Methods ===
    
    def find_by_score_range(self, min_score: int, max_score: int) -> List[Review]:
        """Find all reviews within a score range.
        
        Args:
            min_score: Minimum score (inclusive).
            max_score: Maximum score (inclusive).
            
        Returns:
            List of Review entities within the score range.
        """
        cursor = self._conn.execute(
            "SELECT id, text, score, created_at "
            "FROM Review WHERE score >= ? AND score <= ? "
            "ORDER BY score DESC",
            (min_score, max_score)
        )
        return [self._row_to_model(row) for row in cursor.fetchall()]
    
    def count_all(self) -> int:
        """Count all reviews.
        
        Returns:
            Total number of reviews.
        """
        cursor = self._conn.execute("SELECT COUNT(*) FROM Review")
        return cursor.fetchone()[0]
    
    # === Helper Methods ===
    
    def _row_to_model(self, row: sqlite3.Row) -> Review:
        """Convert database row to Review instance.
        
        Args:
            row: SQLite Row object with review data.
            
        Returns:
            Review instance populated from row data.
        """
        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return Review(
            id=row["id"],
            text=row["text"],
            score=row["score"],
            created_at=created_at
        )
    
    @staticmethod
    def get_sql_schema() -> str:
        """Get the SQL CREATE TABLE statement for Review.
        
        Returns:
            SQL statement to create the Review table.
        """
        return """
        CREATE TABLE IF NOT EXISTS Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
