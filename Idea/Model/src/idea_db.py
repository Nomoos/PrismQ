"""Database setup for Idea model with IdeaInspiration relationship.

This module provides SQLite database schema and utilities for storing Idea
instances and their relationships with IdeaInspiration instances.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
import json


class IdeaDatabase:
    """Database manager for Idea model with M:N IdeaInspiration relationship."""
    
    def __init__(self, db_path: str = "idea.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create database schema for Idea and relationships."""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Create ideas table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                concept TEXT NOT NULL,
                purpose TEXT,
                emotional_quality TEXT,
                target_audience TEXT,
                target_demographics TEXT,  -- JSON string
                target_platform TEXT,
                genre TEXT,
                style TEXT,
                keywords TEXT,  -- JSON string (list of keywords)
                outline TEXT,
                skeleton TEXT,
                potential_scores TEXT,  -- JSON string
                metadata TEXT,  -- JSON string
                version INTEGER DEFAULT 1,
                status TEXT DEFAULT 'draft',
                notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT
            )
        """)
        
        # Create junction table for Idea-IdeaInspiration M:N relationship
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS idea_inspirations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER NOT NULL,
                inspiration_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
                UNIQUE(idea_id, inspiration_id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ideas_status 
            ON ideas(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ideas_platform 
            ON ideas(target_platform)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ideas_genre 
            ON ideas(genre)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_idea_inspirations_idea 
            ON idea_inspirations(idea_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_idea_inspirations_inspiration 
            ON idea_inspirations(inspiration_id)
        """)
        
        self.conn.commit()
        
    def insert_idea(self, idea_dict: Dict[str, Any]) -> int:
        """Insert an Idea into the database.
        
        Args:
            idea_dict: Dictionary representation of Idea
            
        Returns:
            ID of inserted idea
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Extract and serialize complex fields
        target_demographics = json.dumps(idea_dict.get("target_demographics", {}))
        keywords = json.dumps(idea_dict.get("keywords", []))
        potential_scores = json.dumps(idea_dict.get("potential_scores", {}))
        metadata = json.dumps(idea_dict.get("metadata", {}))
        inspiration_ids = idea_dict.get("inspiration_ids", [])
        
        cursor.execute("""
            INSERT INTO ideas (
                title, concept, purpose, emotional_quality, target_audience,
                target_demographics, target_platform, genre, style, keywords,
                outline, skeleton, potential_scores, metadata, version, status, notes,
                created_at, updated_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            idea_dict.get("title"),
            idea_dict.get("concept"),
            idea_dict.get("purpose", ""),
            idea_dict.get("emotional_quality", ""),
            idea_dict.get("target_audience", ""),
            target_demographics,
            idea_dict.get("target_platform", ""),
            idea_dict.get("genre", "other"),
            idea_dict.get("style", ""),
            keywords,
            idea_dict.get("outline", ""),
            idea_dict.get("skeleton", ""),
            potential_scores,
            metadata,
            idea_dict.get("version", 1),
            idea_dict.get("status", "draft"),
            idea_dict.get("notes", ""),
            idea_dict.get("created_at"),
            idea_dict.get("updated_at"),
            idea_dict.get("created_by")
        ))
        
        idea_id = cursor.lastrowid
        
        # Insert inspiration relationships
        for inspiration_id in inspiration_ids:
            cursor.execute("""
                INSERT OR IGNORE INTO idea_inspirations (idea_id, inspiration_id)
                VALUES (?, ?)
            """, (idea_id, inspiration_id))
        
        self.conn.commit()
        return idea_id
    
    def get_idea(self, idea_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve an Idea by ID.
        
        Args:
            idea_id: ID of the idea
            
        Returns:
            Dictionary representation of Idea or None
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convert row to dict and deserialize JSON fields
        idea_dict = dict(row)
        idea_dict["target_demographics"] = json.loads(idea_dict["target_demographics"])
        idea_dict["keywords"] = json.loads(idea_dict["keywords"])
        idea_dict["potential_scores"] = json.loads(idea_dict["potential_scores"])
        idea_dict["metadata"] = json.loads(idea_dict["metadata"])
        
        # Fetch linked inspirations
        cursor.execute("""
            SELECT inspiration_id FROM idea_inspirations
            WHERE idea_id = ?
        """, (idea_id,))
        idea_dict["inspiration_ids"] = [row[0] for row in cursor.fetchall()]
        
        return idea_dict
    
    def get_ideas_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Retrieve all Ideas with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of Idea dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM ideas WHERE status = ?", (status,))
        
        return [self.get_idea(row[0]) for row in cursor.fetchall()]
    
    def get_ideas_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        """Retrieve all Ideas for a specific platform.
        
        Args:
            platform: Platform to filter by
            
        Returns:
            List of Idea dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM ideas WHERE target_platform = ?", (platform,))
        
        return [self.get_idea(row[0]) for row in cursor.fetchall()]
    
    def get_ideas_from_inspiration(self, inspiration_id: str) -> List[Dict[str, Any]]:
        """Get all Ideas that were derived from a specific IdeaInspiration.
        
        Args:
            inspiration_id: ID of the inspiration
            
        Returns:
            List of Idea dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT idea_id FROM idea_inspirations
            WHERE inspiration_id = ?
        """, (inspiration_id,))
        
        return [self.get_idea(row[0]) for row in cursor.fetchall()]
    
    def update_idea(self, idea_id: int, idea_dict: Dict[str, Any]) -> bool:
        """Update an existing Idea.
        
        Args:
            idea_id: ID of the idea to update
            idea_dict: Dictionary with updated fields
            
        Returns:
            True if successful, False otherwise
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Serialize complex fields
        target_demographics = json.dumps(idea_dict.get("target_demographics", {}))
        keywords = json.dumps(idea_dict.get("keywords", []))
        potential_scores = json.dumps(idea_dict.get("potential_scores", {}))
        metadata = json.dumps(idea_dict.get("metadata", {}))
        
        cursor.execute("""
            UPDATE ideas SET
                title = ?, concept = ?, purpose = ?, emotional_quality = ?,
                target_audience = ?, target_demographics = ?, target_platform = ?,
                genre = ?, style = ?, keywords = ?, outline = ?, skeleton = ?,
                potential_scores = ?, metadata = ?,
                version = ?, status = ?, notes = ?, updated_at = ?, created_by = ?
            WHERE id = ?
        """, (
            idea_dict.get("title"),
            idea_dict.get("concept"),
            idea_dict.get("purpose", ""),
            idea_dict.get("emotional_quality", ""),
            idea_dict.get("target_audience", ""),
            target_demographics,
            idea_dict.get("target_platform", ""),
            idea_dict.get("genre", "other"),
            idea_dict.get("style", ""),
            keywords,
            idea_dict.get("outline", ""),
            idea_dict.get("skeleton", ""),
            idea_dict.get("genre", "other"),
            idea_dict.get("style", ""),
            potential_scores,
            metadata,
            idea_dict.get("version", 1),
            idea_dict.get("status", "draft"),
            idea_dict.get("notes", ""),
            idea_dict.get("updated_at"),
            idea_dict.get("created_by"),
            idea_id
        ))
        
        # Update inspiration relationships if provided
        if "inspiration_ids" in idea_dict:
            # Remove old relationships
            cursor.execute("DELETE FROM idea_inspirations WHERE idea_id = ?", (idea_id,))
            
            # Add new relationships
            for inspiration_id in idea_dict["inspiration_ids"]:
                cursor.execute("""
                    INSERT OR IGNORE INTO idea_inspirations (idea_id, inspiration_id)
                    VALUES (?, ?)
                """, (idea_id, inspiration_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_idea(self, idea_id: int) -> bool:
        """Delete an Idea and its relationships.
        
        Args:
            idea_id: ID of the idea to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ideas WHERE id = ?", (idea_id,))
        self.conn.commit()
        
        return cursor.rowcount > 0


def setup_database(db_path: str = "idea.db") -> IdeaDatabase:
    """Initialize and setup the Idea database.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        Configured IdeaDatabase instance
    """
    db = IdeaDatabase(db_path)
    db.connect()
    db.create_tables()
    return db


if __name__ == "__main__":
    # Example usage
    print("Setting up Idea database...")
    db = setup_database()
    print(f"Database created at: {db.db_path}")
    db.close()
    print("Setup complete!")
