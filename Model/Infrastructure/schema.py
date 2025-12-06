"""SchemaManager - Centralized database schema management for PrismQ.

This module provides a single point of responsibility for database schema
initialization and management, following SOLID principles:

- Single Responsibility: Only handles schema DDL operations
- Open/Closed: Schema definitions come from models, manager orchestrates
- Dependency Inversion: Depends on model abstractions (get_sql_schema())

Usage:
    This module should ONLY be used during:
    - Application bootstrapping
    - Test environment setup
    - Database initialization scripts

    It should NOT be called from runtime business logic.

Example:
    >>> import sqlite3
    >>> from Model.Database.schema_manager import SchemaManager
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> schema_manager = SchemaManager(conn)
    >>> schema_manager.initialize_schema()  # Creates all tables
    >>> 
    >>> # For testing
    >>> schema_manager.verify_schema()  # Returns True if all tables exist
"""

import sqlite3
from typing import List, Tuple

from Model.Entities.idea import IdeaSchema
from Model.Entities.review import Review
from Model.Entities.story import Story
from Model.Entities.title import Title
from Model.Entities.script import Script

try:
    from Model.Entities.story_review import StoryReviewModel
except ImportError:
    StoryReviewModel = None


class SchemaManager:
    """Centralized manager for database schema initialization.
    
    This class isolates all DDL (Data Definition Language) operations
    from business logic, ensuring clean separation of concerns.
    
    The schema manager:
    - Creates tables in correct dependency order
    - Uses CREATE TABLE IF NOT EXISTS for idempotency
    - Validates schema consistency with models
    - Is only intended for bootstrapping, not runtime use
    
    Attributes:
        _conn: SQLite database connection
    
    Table Creation Order (respecting FK dependencies):
        1. Idea - base table (no FK dependencies)
        2. Review - base table (no FK dependencies)
        3. Story - references Idea via idea_id (FK)
        4. Title - depends on Story and Review
        5. Script - depends on Story and Review
        6. StoryReview - depends on Story and Review
    
    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> manager = SchemaManager(conn)
        >>> manager.initialize_schema()
        >>> assert manager.verify_schema()
    """
    
    # Table names in creation order (respecting FK dependencies)
    TABLE_ORDER: List[str] = ["Idea", "Review", "Story", "Title", "Script", "StoryReview"]
    
    def __init__(self, connection: sqlite3.Connection):
        """Initialize schema manager with database connection.
        
        Args:
            connection: SQLite database connection.
        """
        self._conn = connection
    
    def initialize_schema(self) -> None:
        """Create all required database tables.
        
        Creates tables in the correct order to respect foreign key
        dependencies. Uses CREATE TABLE IF NOT EXISTS for idempotency.
        
        Note:
            SQLite does not enforce FK constraints by default
            (PRAGMA foreign_keys = OFF), so circular dependencies
            between Story<->Title/Script are handled correctly.
        """
        # Create tables in dependency order
        # 1. Idea table (no FK dependencies)
        self._conn.executescript(IdeaSchema.get_sql_schema())
        
        # 2. Review table (no FK dependencies)
        self._conn.executescript(Review.get_sql_schema())
        
        # 3. Story table (FK to Title/Script are nullable)
        self._conn.executescript(Story.get_sql_schema())
        
        # 4. Title table (depends on Story and Review)
        self._conn.executescript(Title.get_sql_schema())
        
        # 5. Script table (depends on Story and Review)
        self._conn.executescript(Script.get_sql_schema())
        
        # 6. StoryReview linking table (depends on Story and Review)
        self._conn.executescript(StoryReviewModel.get_sql_schema())
        
        self._conn.commit()
    
    def verify_schema(self) -> bool:
        """Verify that all required tables exist.
        
        Returns:
            True if all tables exist, False otherwise.
        """
        existing_tables = self._get_existing_tables()
        return all(table in existing_tables for table in self.TABLE_ORDER)
    
    def get_missing_tables(self) -> List[str]:
        """Get list of tables that don't exist.
        
        Returns:
            List of table names that are missing.
        """
        existing_tables = self._get_existing_tables()
        return [table for table in self.TABLE_ORDER if table not in existing_tables]
    
    def get_table_info(self, table_name: str) -> List[Tuple]:
        """Get column information for a table.
        
        Args:
            table_name: Name of the table. Must be one of the known tables
                        in TABLE_ORDER to prevent SQL injection.
            
        Returns:
            List of tuples with column info from PRAGMA table_info.
            
        Raises:
            ValueError: If table_name is not in the allowed TABLE_ORDER list.
        """
        # Validate table_name against whitelist to prevent SQL injection
        if table_name not in self.TABLE_ORDER:
            raise ValueError(
                f"Unknown table: {table_name}. "
                f"Valid tables: {', '.join(self.TABLE_ORDER)}"
            )
        
        cursor = self._conn.execute(f"PRAGMA table_info({table_name})")
        return cursor.fetchall()
    
    def _get_existing_tables(self) -> List[str]:
        """Get list of existing table names.
        
        Returns:
            List of table names in the database.
        """
        cursor = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        return [row[0] for row in cursor.fetchall()]


def initialize_database(connection: sqlite3.Connection) -> SchemaManager:
    """Convenience function to initialize database schema.
    
    This is the recommended entry point for database bootstrapping.
    It creates all required tables and returns the schema manager
    for verification if needed.
    
    Args:
        connection: SQLite database connection.
        
    Returns:
        SchemaManager instance for further operations if needed.
    
    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> manager = initialize_database(conn)
        >>> print(f"Tables created: {manager.verify_schema()}")
    """
    manager = SchemaManager(connection)
    manager.initialize_schema()
    return manager


__all__ = [
    "SchemaManager",
    "initialize_database",
]
