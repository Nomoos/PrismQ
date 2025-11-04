"""Database utilities for IdeaInspiration model.

This module provides database operations for storing and retrieving
IdeaInspiration objects. It is designed to be used by all Source modules
to save their output to a central database while maintaining their
own source-specific tables.

Design Pattern:
    - Dual-save approach: Sources maintain their own detailed tables
      AND save normalized IdeaInspiration records to central database
    - This enables unified cross-source queries while preserving
      domain-specific data structures (SOLID: Single Responsibility)
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from idea_inspiration import IdeaInspiration


class IdeaInspirationDatabase:
    """Manages database operations for IdeaInspiration records.
    
    This class provides a simple interface for Source modules to save
    IdeaInspiration objects to a central database for unified access.
    
    Example:
        >>> from idea_inspiration_db import IdeaInspirationDatabase
        >>> db = IdeaInspirationDatabase("db.s3db")
        >>> idea = IdeaInspiration.from_text(title="Test", text_content="Content")
        >>> db.insert(idea)
    """

    def __init__(self, database_path: str, interactive: bool = True):
        """Initialize database connection.
        
        Args:
            database_path: Path to SQLite database file
            interactive: Whether to prompt for confirmation before creating database
        """
        self.database_path = database_path
        self._interactive = interactive
        
        # Ensure database directory exists
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema for IdeaInspiration table."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create IdeaInspiration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS IdeaInspiration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                keywords TEXT,
                source_type TEXT,
                metadata TEXT,
                source_id TEXT,
                source_url TEXT,
                source_platform TEXT,
                source_created_by TEXT,
                source_created_at TEXT,
                score INTEGER,
                category TEXT,
                subcategory_relevance TEXT,
                contextual_category_scores TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migrate existing databases by adding source_platform column if it doesn't exist
        try:
            cursor.execute("PRAGMA table_info(IdeaInspiration)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'source_platform' not in columns:
                cursor.execute("""
                    ALTER TABLE IdeaInspiration 
                    ADD COLUMN source_platform TEXT
                """)
        except sqlite3.OperationalError as e:
            # Ignore if column already exists from a concurrent migration
            # or if table doesn't exist yet (will be created below)
            error_msg = str(e).lower()
            if 'duplicate column' not in error_msg and 'no such table' not in error_msg:
                # Log unexpected operational errors but don't fail
                # Schema creation below will handle most cases
                print(f"Warning during migration: {e}")
        except Exception as e:
            # Log unexpected errors but don't fail initialization
            print(f"Warning during schema migration: {e}")
        
        # Create index on source_id for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_id 
            ON IdeaInspiration(source_id)
        """)
        
        # Create index on source_type for filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_type 
            ON IdeaInspiration(source_type)
        """)
        
        # Create index on source_platform for filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_platform 
            ON IdeaInspiration(source_platform)
        """)
        
        # Create index on category for filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON IdeaInspiration(category)
        """)
        
        conn.commit()
        conn.close()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection context manager.
        
        Yields:
            sqlite3.Connection object
        """
        conn = sqlite3.connect(self.database_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def insert(self, idea: IdeaInspiration) -> Optional[int]:
        """Insert an IdeaInspiration object into the database.
        
        Args:
            idea: IdeaInspiration object to insert
            
        Returns:
            Database ID of the inserted record, or None if duplicate
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert idea to dict for easier handling
            data = idea.to_dict()
            
            # Serialize complex fields to JSON
            keywords_json = json.dumps(data['keywords'])
            metadata_json = json.dumps(data['metadata'])
            subcategory_relevance_json = json.dumps(data['subcategory_relevance'])
            contextual_scores_json = json.dumps(data['contextual_category_scores'])
            
            try:
                cursor.execute("""
                    INSERT INTO IdeaInspiration (
                        title, description, content, keywords, source_type,
                        metadata, source_id, source_url, source_platform,
                        source_created_by, source_created_at, score, category, 
                        subcategory_relevance, contextual_category_scores
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['title'],
                    data['description'],
                    data['content'],
                    keywords_json,
                    data['source_type'],
                    metadata_json,
                    data['source_id'],
                    data['source_url'],
                    data['source_platform'],
                    data['source_created_by'],
                    data['source_created_at'],
                    data['score'],
                    data['category'],
                    subcategory_relevance_json,
                    contextual_scores_json
                ))
                
                conn.commit()
                return cursor.lastrowid
                
            except sqlite3.IntegrityError:
                # Handle duplicate entries gracefully
                return None
    
    def insert_batch(self, ideas: List[IdeaInspiration]) -> int:
        """Insert multiple IdeaInspiration objects in a batch.
        
        Args:
            ideas: List of IdeaInspiration objects to insert
            
        Returns:
            Number of records successfully inserted
        """
        inserted_count = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for idea in ideas:
                data = idea.to_dict()
                
                # Serialize complex fields
                keywords_json = json.dumps(data['keywords'])
                metadata_json = json.dumps(data['metadata'])
                subcategory_relevance_json = json.dumps(data['subcategory_relevance'])
                contextual_scores_json = json.dumps(data['contextual_category_scores'])
                
                try:
                    cursor.execute("""
                        INSERT INTO IdeaInspiration (
                            title, description, content, keywords, source_type,
                            metadata, source_id, source_url, source_platform,
                            source_created_by, source_created_at, score, category, 
                            subcategory_relevance, contextual_category_scores
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data['title'],
                        data['description'],
                        data['content'],
                        keywords_json,
                        data['source_type'],
                        metadata_json,
                        data['source_id'],
                        data['source_url'],
                        data['source_platform'],
                        data['source_created_by'],
                        data['source_created_at'],
                        data['score'],
                        data['category'],
                        subcategory_relevance_json,
                        contextual_scores_json
                    ))
                    inserted_count += 1
                    
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    continue
            
            conn.commit()
        
        return inserted_count
    
    def get_by_id(self, record_id: int) -> Optional[IdeaInspiration]:
        """Retrieve an IdeaInspiration by database ID.
        
        Args:
            record_id: Database ID of the record
            
        Returns:
            IdeaInspiration object or None if not found
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM IdeaInspiration WHERE id = ?
            """, (record_id,))
            
            row = cursor.fetchone()
            
            if row:
                return self._row_to_idea(dict(row))
            return None
    
    def get_by_source_id(self, source_id: str) -> Optional[IdeaInspiration]:
        """Retrieve an IdeaInspiration by source ID.
        
        Args:
            source_id: Source identifier
            
        Returns:
            IdeaInspiration object or None if not found
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM IdeaInspiration WHERE source_id = ?
            """, (source_id,))
            
            row = cursor.fetchone()
            
            if row:
                return self._row_to_idea(dict(row))
            return None
    
    def get_all(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        source_type: Optional[str] = None,
        source_platform: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[IdeaInspiration]:
        """Retrieve IdeaInspiration records with optional filtering.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            source_type: Filter by source type (text, video, audio)
            source_platform: Filter by source platform (e.g., "youtube", "google_trends")
            category: Filter by category
            
        Returns:
            List of IdeaInspiration objects
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM IdeaInspiration WHERE 1=1"
            params = []
            
            if source_type:
                query += " AND source_type = ?"
                params.append(source_type)
            
            if source_platform:
                query += " AND source_platform = ?"
                params.append(source_platform)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            if offset:
                query += " OFFSET ?"
                params.append(offset)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_idea(dict(row)) for row in rows]
    
    def count(
        self,
        source_type: Optional[str] = None,
        source_platform: Optional[str] = None,
        category: Optional[str] = None
    ) -> int:
        """Count IdeaInspiration records with optional filtering.
        
        Args:
            source_type: Filter by source type
            source_platform: Filter by source platform
            category: Filter by category
            
        Returns:
            Count of matching records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM IdeaInspiration WHERE 1=1"
            params = []
            
            if source_type:
                query += " AND source_type = ?"
                params.append(source_type)
            
            if source_platform:
                query += " AND source_platform = ?"
                params.append(source_platform)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    def _row_to_idea(self, row: Dict[str, Any]) -> IdeaInspiration:
        """Convert database row to IdeaInspiration object.
        
        Args:
            row: Database row as dictionary
            
        Returns:
            IdeaInspiration object
        """
        # Parse JSON fields
        keywords = json.loads(row['keywords']) if row['keywords'] else []
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        subcategory_relevance = json.loads(row['subcategory_relevance']) if row['subcategory_relevance'] else {}
        contextual_scores = json.loads(row['contextual_category_scores']) if row['contextual_category_scores'] else {}
        
        # Create IdeaInspiration from dict
        return IdeaInspiration.from_dict({
            'title': row['title'],
            'description': row['description'] or '',
            'content': row['content'] or '',
            'keywords': keywords,
            'source_type': row['source_type'],
            'metadata': metadata,
            'source_id': row['source_id'],
            'source_url': row['source_url'],
            'source_platform': row.get('source_platform'),
            'source_created_by': row['source_created_by'],
            'source_created_at': row['source_created_at'],
            'score': row['score'],
            'category': row['category'],
            'subcategory_relevance': subcategory_relevance,
            'contextual_category_scores': contextual_scores
        })


def get_central_database_path() -> str:
    """Get the path to the central IdeaInspiration database.
    
    This function uses the config_manager to determine the working
    directory and returns the standard database path.
    
    Returns:
        Path to the central database file
    """
    try:
        from config_manager import setup_working_directory
        config = setup_working_directory('PrismQ.IdeaInspiration', quiet=True)
        working_dir = Path(config.working_dir)
        return str(working_dir / 'db.s3db')
    except (ImportError, AttributeError, FileNotFoundError) as e:
        # Fallback to a default path if config manager is not available
        # This allows the module to work in isolated test environments
        return 'db.s3db'
