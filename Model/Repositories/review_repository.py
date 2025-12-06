"""Review Repository - SQLite implementation for Review entities.

This module provides SQLite implementation of the IRepository interface
for Review entities, handling SQL DML (Data Manipulation Language) operations
only: SELECT, INSERT.

Note:
    This repository does NOT handle schema creation (DDL). Use SchemaManager
    from Model.Database.schema_manager for database initialization.

Usage:
    >>> import sqlite3
    >>> from Model.Database.schema_manager import initialize_database
    >>> from Model.Database.repositories.review_repository import ReviewRepository
    >>> from Model.Entities.review import Review
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> initialize_database(conn)  # Creates schema
    >>> 
    >>> repo = ReviewRepository(conn)
    >>> review = Review(text="Great script!", score=85)
    >>> saved = repo.insert(review)
    >>> print(saved.id)
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from Model.Repositories.base import IRepository
from Model.Entities.review import Review


class ReviewRepository(IRepository[Review, int]):
    """SQLite implementation of IRepository for Review entities.
    
    This repository handles SQL DML (Data Manipulation Language) operations
    for Review entities following the INSERT+READ only pattern.
    
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
        >>> repo = ReviewRepository(conn)
        >>> review = Review(text="Good quality script", score=80)
        >>> saved = repo.insert(review)
        >>> print(saved.id)
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
    
    def find_by_id(self, id: int) -> Optional[Review]:
        """Find review by unique identifier.
        
        Args:
            id: The primary key of the review record.
            
        Returns:
            Review if found, None otherwise.
        """
        cursor = self._conn.execute(
            "SELECT id, text, score, created_at FROM Review WHERE id = ?",
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
            "SELECT id, text, score, created_at FROM Review ORDER BY id"
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
            "INSERT INTO Review (text, score, created_at) VALUES (?, ?, ?)",
            (
                entity.text,
                entity.score,
                entity.created_at.isoformat() if entity.created_at else datetime.now().isoformat()
            )
        )
        self._conn.commit()
        
        # Update entity with generated ID
        entity.id = cursor.lastrowid
        return entity
    
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
