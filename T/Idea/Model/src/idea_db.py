"""Database setup for Idea model with IdeaInspiration relationship.

This module provides SQLite database schema and utilities for storing Idea
instances and their relationships with IdeaInspiration instances.

Extended with multi-language story translation support following best practices:
- Story translations table with composite key (story_id, language_code)
- Translation feedback loop tracking
- Original language designation in ideas table
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
        # Enable foreign key constraints in SQLite
        self.conn.execute("PRAGMA foreign_keys = ON")
    
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
                synopsis TEXT,
                story_premise TEXT,
                purpose TEXT,
                emotional_quality TEXT,
                target_audience TEXT,
                target_demographics TEXT,  -- JSON string
                target_platforms TEXT,  -- JSON string (list of platforms)
                target_formats TEXT,  -- JSON string (list of formats: text, audio, video)
                genre TEXT,
                style TEXT,
                keywords TEXT,  -- JSON string (list of keywords)
                themes TEXT,  -- JSON string (list of themes)
                character_notes TEXT,
                setting_notes TEXT,
                tone_guidance TEXT,
                length_target TEXT,
                outline TEXT,
                skeleton TEXT,
                original_language TEXT DEFAULT 'en',  -- ISO 639-1 code for original language
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
        
        # Note: target_platforms is JSON text, not ideal for indexing
        # Omit index on target_platforms as it's a JSON field
        
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
        
        # Create story_translations table for multi-language support
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                language_code TEXT NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                iteration_count INTEGER DEFAULT 0,
                max_iterations INTEGER DEFAULT 2,
                translator_id TEXT,
                reviewer_id TEXT,
                feedback_history TEXT,  -- JSON string (list of feedback objects)
                last_feedback TEXT,
                meaning_verified INTEGER DEFAULT 0,  -- Boolean: 0=False, 1=True
                translated_from TEXT DEFAULT 'en',
                version INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT,
                approved_at TEXT,
                published_at TEXT,
                notes TEXT,
                FOREIGN KEY (story_id) REFERENCES ideas(id) ON DELETE CASCADE,
                UNIQUE(story_id, language_code)
            )
        """)
        
        # Create indexes for story_translations
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_translations_story 
            ON story_translations(story_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_translations_language 
            ON story_translations(language_code)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_translations_status 
            ON story_translations(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_translations_composite 
            ON story_translations(story_id, language_code)
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
        target_platforms = json.dumps(idea_dict.get("target_platforms", []))
        target_formats = json.dumps(idea_dict.get("target_formats", []))
        keywords = json.dumps(idea_dict.get("keywords", []))
        themes = json.dumps(idea_dict.get("themes", []))
        potential_scores = json.dumps(idea_dict.get("potential_scores", {}))
        metadata = json.dumps(idea_dict.get("metadata", {}))
        inspiration_ids = idea_dict.get("inspiration_ids", [])
        
        cursor.execute("""
            INSERT INTO ideas (
                title, concept, synopsis, story_premise, purpose, emotional_quality, target_audience,
                target_demographics, target_platforms, target_formats, genre, style, keywords, themes,
                character_notes, setting_notes, tone_guidance, length_target,
                outline, skeleton, original_language, potential_scores, metadata, version, status, notes,
                created_at, updated_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            idea_dict.get("title"),
            idea_dict.get("concept"),
            idea_dict.get("synopsis", ""),
            idea_dict.get("story_premise", ""),
            idea_dict.get("purpose", ""),
            idea_dict.get("emotional_quality", ""),
            idea_dict.get("target_audience", ""),
            target_demographics,
            target_platforms,
            target_formats,
            idea_dict.get("genre", "other"),
            idea_dict.get("style", ""),
            keywords,
            themes,
            idea_dict.get("character_notes", ""),
            idea_dict.get("setting_notes", ""),
            idea_dict.get("tone_guidance", ""),
            idea_dict.get("length_target", ""),
            idea_dict.get("outline", ""),
            idea_dict.get("skeleton", ""),
            idea_dict.get("original_language", "en"),
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
        idea_dict["target_platforms"] = json.loads(idea_dict["target_platforms"])
        idea_dict["target_formats"] = json.loads(idea_dict["target_formats"])
        idea_dict["keywords"] = json.loads(idea_dict["keywords"])
        idea_dict["themes"] = json.loads(idea_dict["themes"])
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
        
        Note: target_platforms is stored as JSON, so this does a LIKE search.
        
        Args:
            platform: Platform to filter by
            
        Returns:
            List of Idea dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        # Use LIKE to search in JSON array string
        cursor.execute("SELECT id FROM ideas WHERE target_platforms LIKE ?", (f'%{platform}%',))
        
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
        target_platforms = json.dumps(idea_dict.get("target_platforms", []))
        target_formats = json.dumps(idea_dict.get("target_formats", []))
        keywords = json.dumps(idea_dict.get("keywords", []))
        themes = json.dumps(idea_dict.get("themes", []))
        potential_scores = json.dumps(idea_dict.get("potential_scores", {}))
        metadata = json.dumps(idea_dict.get("metadata", {}))
        
        cursor.execute("""
            UPDATE ideas SET
                title = ?, concept = ?, synopsis = ?, story_premise = ?,
                purpose = ?, emotional_quality = ?,
                target_audience = ?, target_demographics = ?, target_platforms = ?, target_formats = ?,
                genre = ?, style = ?, keywords = ?, themes = ?,
                character_notes = ?, setting_notes = ?, tone_guidance = ?, length_target = ?,
                outline = ?, skeleton = ?, original_language = ?,
                potential_scores = ?, metadata = ?,
                version = ?, status = ?, notes = ?, updated_at = ?, created_by = ?
            WHERE id = ?
        """, (
            idea_dict.get("title"),
            idea_dict.get("concept"),
            idea_dict.get("synopsis", ""),
            idea_dict.get("story_premise", ""),
            idea_dict.get("purpose", ""),
            idea_dict.get("emotional_quality", ""),
            idea_dict.get("target_audience", ""),
            target_demographics,
            target_platforms,
            target_formats,
            idea_dict.get("genre", "other"),
            idea_dict.get("style", ""),
            keywords,
            themes,
            idea_dict.get("character_notes", ""),
            idea_dict.get("setting_notes", ""),
            idea_dict.get("tone_guidance", ""),
            idea_dict.get("length_target", ""),
            idea_dict.get("outline", ""),
            idea_dict.get("skeleton", ""),
            idea_dict.get("original_language", "en"),
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
    
    # Translation Management Methods
    
    def insert_translation(self, translation_dict: Dict[str, Any]) -> int:
        """Insert a StoryTranslation into the database.
        
        Args:
            translation_dict: Dictionary representation of StoryTranslation
            
        Returns:
            ID of inserted translation
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Serialize complex fields
        feedback_history = json.dumps(translation_dict.get("feedback_history", []))
        meaning_verified = 1 if translation_dict.get("meaning_verified", False) else 0
        
        cursor.execute("""
            INSERT INTO story_translations (
                story_id, language_code, title, text, status,
                iteration_count, max_iterations, translator_id, reviewer_id,
                feedback_history, last_feedback, meaning_verified,
                translated_from, version, created_at, updated_at,
                approved_at, published_at, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            translation_dict.get("story_id"),
            translation_dict.get("language_code"),
            translation_dict.get("title"),
            translation_dict.get("text"),
            translation_dict.get("status", "draft"),
            translation_dict.get("iteration_count", 0),
            translation_dict.get("max_iterations", 2),
            translation_dict.get("translator_id"),
            translation_dict.get("reviewer_id"),
            feedback_history,
            translation_dict.get("last_feedback", ""),
            meaning_verified,
            translation_dict.get("translated_from", "en"),
            translation_dict.get("version", 1),
            translation_dict.get("created_at"),
            translation_dict.get("updated_at"),
            translation_dict.get("approved_at"),
            translation_dict.get("published_at"),
            translation_dict.get("notes", "")
        ))
        
        translation_id = cursor.lastrowid
        self.conn.commit()
        return translation_id
    
    def get_translation(self, story_id: int, language_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve a translation by story ID and language code.
        
        Args:
            story_id: ID of the story
            language_code: ISO 639-1 language code
            
        Returns:
            Dictionary representation of StoryTranslation or None
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM story_translations 
            WHERE story_id = ? AND language_code = ?
        """, (story_id, language_code))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Convert row to dict and deserialize JSON fields
        translation_dict = dict(row)
        translation_dict["feedback_history"] = json.loads(translation_dict["feedback_history"])
        translation_dict["meaning_verified"] = bool(translation_dict["meaning_verified"])
        
        return translation_dict
    
    def get_all_translations(self, story_id: int) -> List[Dict[str, Any]]:
        """Get all translations for a story.
        
        Args:
            story_id: ID of the story
            
        Returns:
            List of translation dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT language_code FROM story_translations
            WHERE story_id = ?
            ORDER BY language_code
        """, (story_id,))
        
        translations = []
        for row in cursor.fetchall():
            translation = self.get_translation(story_id, row[0])
            if translation:
                translations.append(translation)
        
        return translations
    
    def get_translations_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all translations with a specific status.
        
        Args:
            status: Translation status to filter by
            
        Returns:
            List of translation dictionaries
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT story_id, language_code FROM story_translations
            WHERE status = ?
        """, (status,))
        
        translations = []
        for row in cursor.fetchall():
            translation = self.get_translation(row[0], row[1])
            if translation:
                translations.append(translation)
        
        return translations
    
    def update_translation(
        self,
        story_id: int,
        language_code: str,
        translation_dict: Dict[str, Any]
    ) -> bool:
        """Update an existing translation.
        
        Args:
            story_id: ID of the story
            language_code: Language code of translation to update
            translation_dict: Dictionary with updated fields
            
        Returns:
            True if successful, False otherwise
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Serialize complex fields
        feedback_history = json.dumps(translation_dict.get("feedback_history", []))
        meaning_verified = 1 if translation_dict.get("meaning_verified", False) else 0
        
        cursor.execute("""
            UPDATE story_translations SET
                title = ?, text = ?, status = ?,
                iteration_count = ?, max_iterations = ?,
                translator_id = ?, reviewer_id = ?,
                feedback_history = ?, last_feedback = ?,
                meaning_verified = ?, translated_from = ?,
                version = ?, updated_at = ?,
                approved_at = ?, published_at = ?, notes = ?
            WHERE story_id = ? AND language_code = ?
        """, (
            translation_dict.get("title"),
            translation_dict.get("text"),
            translation_dict.get("status"),
            translation_dict.get("iteration_count", 0),
            translation_dict.get("max_iterations", 2),
            translation_dict.get("translator_id"),
            translation_dict.get("reviewer_id"),
            feedback_history,
            translation_dict.get("last_feedback", ""),
            meaning_verified,
            translation_dict.get("translated_from", "en"),
            translation_dict.get("version", 1),
            translation_dict.get("updated_at"),
            translation_dict.get("approved_at"),
            translation_dict.get("published_at"),
            translation_dict.get("notes", ""),
            story_id,
            language_code
        ))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_translation(self, story_id: int, language_code: str) -> bool:
        """Delete a translation.
        
        Args:
            story_id: ID of the story
            language_code: Language code of translation to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM story_translations 
            WHERE story_id = ? AND language_code = ?
        """, (story_id, language_code))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_available_languages(self, story_id: int) -> List[str]:
        """Get list of available language codes for a story.
        
        Args:
            story_id: ID of the story
            
        Returns:
            List of ISO 639-1 language codes
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT language_code FROM story_translations
            WHERE story_id = ?
            ORDER BY language_code
        """, (story_id,))
        
        return [row[0] for row in cursor.fetchall()]


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
