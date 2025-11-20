"""Database operations for Story model.

This module provides database CRUD operations for Story objects,
including state machine tracking and query capabilities.
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any

try:
    from .story import Story, StoryState, StoryStatus
except ImportError:
    from story import Story, StoryState, StoryStatus


class StoryDatabase:
    """Database manager for Story objects.
    
    Provides persistence for Story objects with support for:
    - CRUD operations
    - State-based queries
    - State history tracking
    - Idea linking
    
    Example:
        >>> db = StoryDatabase("stories.db")
        >>> db.connect()
        >>> 
        >>> # Save story
        >>> story_id = db.insert_story(story.to_dict())
        >>> 
        >>> # Query by state
        >>> drafts = db.get_stories_by_state(StoryState.SCRIPT_DRAFT)
        >>> 
        >>> # Get stories for an idea
        >>> stories = db.get_stories_by_idea("idea_123")
        >>> 
        >>> db.close()
    """
    
    def __init__(self, db_path: str):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self) -> None:
        """Establish database connection and create tables if needed."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _create_tables(self) -> None:
        """Create Story table if it doesn't exist."""
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        
        # Create Story table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                idea_id TEXT NOT NULL,
                state TEXT NOT NULL,
                status TEXT NOT NULL,
                script_id TEXT,
                script_text TEXT,
                script_title TEXT,
                published_text_url TEXT,
                published_audio_url TEXT,
                published_video_url TEXT,
                metadata TEXT,
                tags TEXT,
                target_platforms TEXT,
                target_formats TEXT,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT,
                state_history TEXT,
                notes TEXT
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stories_idea_id 
            ON stories(idea_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stories_state 
            ON stories(state)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stories_status 
            ON stories(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stories_created_at 
            ON stories(created_at)
        """)
        
        self.conn.commit()
    
    def insert_story(self, story_dict: Dict[str, Any]) -> int:
        """Insert a new Story into the database.
        
        Args:
            story_dict: Story data as dictionary (from Story.to_dict())
            
        Returns:
            ID of inserted story
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO stories (
                title, idea_id, state, status,
                script_id, script_text, script_title,
                published_text_url, published_audio_url, published_video_url,
                metadata, tags, target_platforms, target_formats,
                created_at, updated_at, created_by,
                state_history, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            story_dict["title"],
            story_dict["idea_id"],
            story_dict["state"],
            story_dict["status"],
            story_dict.get("script_id"),
            story_dict.get("script_text", ""),
            story_dict.get("script_title", ""),
            story_dict.get("published_text_url"),
            story_dict.get("published_audio_url"),
            story_dict.get("published_video_url"),
            json.dumps(story_dict.get("metadata", {})),
            json.dumps(story_dict.get("tags", [])),
            json.dumps(story_dict.get("target_platforms", [])),
            json.dumps(story_dict.get("target_formats", [])),
            story_dict.get("created_at"),
            story_dict.get("updated_at"),
            story_dict.get("created_by"),
            json.dumps(story_dict.get("state_history", [])),
            story_dict.get("notes", "")
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def update_story(self, story_id: int, story_dict: Dict[str, Any]) -> None:
        """Update an existing Story in the database.
        
        Args:
            story_id: ID of story to update
            story_dict: Updated story data
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE stories SET
                title = ?,
                idea_id = ?,
                state = ?,
                status = ?,
                script_id = ?,
                script_text = ?,
                script_title = ?,
                published_text_url = ?,
                published_audio_url = ?,
                published_video_url = ?,
                metadata = ?,
                tags = ?,
                target_platforms = ?,
                target_formats = ?,
                updated_at = ?,
                created_by = ?,
                state_history = ?,
                notes = ?
            WHERE id = ?
        """, (
            story_dict["title"],
            story_dict["idea_id"],
            story_dict["state"],
            story_dict["status"],
            story_dict.get("script_id"),
            story_dict.get("script_text", ""),
            story_dict.get("script_title", ""),
            story_dict.get("published_text_url"),
            story_dict.get("published_audio_url"),
            story_dict.get("published_video_url"),
            json.dumps(story_dict.get("metadata", {})),
            json.dumps(story_dict.get("tags", [])),
            json.dumps(story_dict.get("target_platforms", [])),
            json.dumps(story_dict.get("target_formats", [])),
            story_dict.get("updated_at"),
            story_dict.get("created_by"),
            json.dumps(story_dict.get("state_history", [])),
            story_dict.get("notes", ""),
            story_id
        ))
        
        self.conn.commit()
    
    def get_story(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a Story by ID.
        
        Args:
            story_id: ID of story to retrieve
            
        Returns:
            Story data as dictionary, or None if not found
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_stories_by_idea(self, idea_id: str) -> List[Dict[str, Any]]:
        """Get all Stories for a specific Idea.
        
        Args:
            idea_id: ID of the Idea
            
        Returns:
            List of Story dictionaries
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM stories WHERE idea_id = ?", (idea_id,))
        rows = cursor.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_stories_by_state(self, state: StoryState) -> List[Dict[str, Any]]:
        """Get all Stories in a specific state.
        
        Args:
            state: The state to query for
            
        Returns:
            List of Story dictionaries
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM stories WHERE state = ?", (state.value,))
        rows = cursor.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_stories_by_status(self, status: StoryStatus) -> List[Dict[str, Any]]:
        """Get all Stories with a specific status.
        
        Args:
            status: The status to query for
            
        Returns:
            List of Story dictionaries
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM stories WHERE status = ?", (status.value,))
        rows = cursor.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    def delete_story(self, story_id: int) -> None:
        """Delete a Story from the database.
        
        Args:
            story_id: ID of story to delete
        """
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM stories WHERE id = ?", (story_id,))
        self.conn.commit()
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to dictionary.
        
        Args:
            row: Database row
            
        Returns:
            Dictionary representation
        """
        return {
            "id": row["id"],
            "title": row["title"],
            "idea_id": row["idea_id"],
            "state": row["state"],
            "status": row["status"],
            "script_id": row["script_id"],
            "script_text": row["script_text"],
            "script_title": row["script_title"],
            "published_text_url": row["published_text_url"],
            "published_audio_url": row["published_audio_url"],
            "published_video_url": row["published_video_url"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            "tags": json.loads(row["tags"]) if row["tags"] else [],
            "target_platforms": json.loads(row["target_platforms"]) if row["target_platforms"] else [],
            "target_formats": json.loads(row["target_formats"]) if row["target_formats"] else [],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "created_by": row["created_by"],
            "state_history": json.loads(row["state_history"]) if row["state_history"] else [],
            "notes": row["notes"],
        }
