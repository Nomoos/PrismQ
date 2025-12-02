"""Tests for database save functionality in idea_creation_interactive module."""

import sys
import os
import pytest
import tempfile
import sqlite3
from pathlib import Path

# Add paths for imports
TESTS_DIR = Path(__file__).parent.absolute()
CREATION_ROOT = TESTS_DIR.parent.parent  # T/Idea/Creation
CREATION_SRC = CREATION_ROOT / "src"
REPO_ROOT = CREATION_ROOT.parent.parent.parent  # Repository root

sys.path.insert(0, str(CREATION_SRC))
sys.path.insert(0, str(REPO_ROOT))

# Import shared database module
from src import IdeaDatabase, setup_idea_database


class TestDatabaseSaveIntegration:
    """Test the database save functionality for idea variants."""
    
    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ideas.db")
    
    def teardown_method(self):
        """Clean up the temporary database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_setup_database_creates_idea_table(self):
        """Test that setup_idea_database creates the Idea table."""
        db = setup_idea_database(self.db_path)
        
        # Verify table exists
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='Idea'
        """)
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == "Idea"
        
        db.close()
    
    def test_idea_table_has_correct_schema(self):
        """Test that the Idea table has the schema from the problem statement."""
        db = setup_idea_database(self.db_path)
        
        # Verify table columns
        cursor = db.conn.cursor()
        cursor.execute("PRAGMA table_info(Idea)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        # Schema: id, text, version, created_at
        assert "id" in columns
        assert "text" in columns
        assert "version" in columns
        assert "created_at" in columns
        
        assert columns["id"] == "INTEGER"
        assert columns["text"] == "TEXT"
        assert columns["version"] == "INTEGER"
        assert columns["created_at"] == "TEXT"
        
        db.close()
    
    def test_insert_idea_text(self):
        """Test inserting idea text into the database."""
        db = setup_idea_database(self.db_path)
        
        idea_text = "My online family around can 2000s fashion help you escape social exclusion"
        idea_id = db.insert_idea(text=idea_text, version=1)
        
        assert idea_id is not None
        assert idea_id > 0
        
        # Retrieve and verify
        idea = db.get_idea(idea_id)
        assert idea is not None
        assert idea["text"] == idea_text
        assert idea["version"] == 1
        assert idea["created_at"] is not None
        
        db.close()
    
    def test_insert_multiple_ideas(self):
        """Test inserting multiple ideas like variant generation does."""
        db = setup_idea_database(self.db_path)
        
        # Simulate saving 10 variants
        variant_texts = [
            "Variant 1: Chosen Family + Online Connection Blend",
            "Variant 2: A community that became a family",
            "Variant 3: A fandom/interest that became so much more",
            "Variant 4: Unconditional support, 2am check-ins, inside jokes that span years",
            "Variant 5: What's missing in offline relationships",
            "Variant 6: My journey to belonging",
            "Variant 7: Escape social exclusion",
            "Variant 8: 2000s fashion help",
            "Variant 9: Online family around",
            "Variant 10: Finding connection in digital spaces",
        ]
        
        saved_ids = []
        for text in variant_texts:
            idea_id = db.insert_idea(text=text, version=1)
            saved_ids.append(idea_id)
        
        assert len(saved_ids) == 10
        assert len(set(saved_ids)) == 10  # All unique IDs
        assert all(id > 0 for id in saved_ids)
        
        # Verify count
        assert db.count_ideas() == 10
        
        db.close()
    
    def test_version_constraint_enforced(self):
        """Test that the version CHECK constraint is enforced."""
        db = setup_idea_database(self.db_path)
        
        # Negative version should fail due to CHECK constraint
        with pytest.raises(sqlite3.IntegrityError):
            db.insert_idea(text="Test idea", version=-1)
        
        # Zero version should work
        idea_id = db.insert_idea(text="Zero version idea", version=0)
        idea = db.get_idea(idea_id)
        assert idea["version"] == 0
        
        db.close()
    
    def test_default_version_is_one(self):
        """Test that version defaults to 1 when using raw SQL insert."""
        db = setup_idea_database(self.db_path)
        
        # Insert using raw SQL without version
        cursor = db.conn.cursor()
        cursor.execute("INSERT INTO Idea (text) VALUES (?)", ("Test with default version",))
        db.conn.commit()
        idea_id = cursor.lastrowid
        
        idea = db.get_idea(idea_id)
        assert idea["version"] == 1
        
        db.close()
    
    def test_created_at_auto_generated(self):
        """Test that created_at is auto-generated."""
        db = setup_idea_database(self.db_path)
        
        idea_id = db.insert_idea(text="Auto timestamp test", version=1)
        idea = db.get_idea(idea_id)
        
        assert idea["created_at"] is not None
        assert len(idea["created_at"]) > 0
        # Should be in datetime format
        assert "-" in idea["created_at"]  # Date separator
        
        db.close()


class TestDatabaseSaveWithFormatIdeaAsText:
    """Test database save using format_idea_as_text output."""
    
    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ideas.db")
    
    def teardown_method(self):
        """Clean up the temporary database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_save_formatted_idea_text(self):
        """Test saving a formatted idea text like the interactive script does."""
        db = setup_idea_database(self.db_path)
        
        # Simulated output from format_idea_as_text
        formatted_text = """Variant 10: Chosen Family + Online Connection Blend
My online family around can 2000s fashion help you escape social exclusion my journey to belonging — A community that became a family
A fandom/interest that became so much more
Unconditional support, 2am check-ins, inside jokes that span years
What's missing in offline relationships"""
        
        idea_id = db.insert_idea(text=formatted_text, version=1)
        
        # Retrieve and verify
        idea = db.get_idea(idea_id)
        assert idea is not None
        assert idea["text"] == formatted_text
        assert "Chosen Family" in idea["text"]
        assert "Online Connection" in idea["text"]
        
        db.close()
    
    def test_save_long_text(self):
        """Test saving longer formatted idea text."""
        db = setup_idea_database(self.db_path)
        
        # A longer text that might come from format_idea_as_text
        long_text = """This is a story about finding belonging in unexpected places.
In the digital age, connections form across continents.
The confession that started it all: I've been hiding my online friendships.
The discovery that changed everything: These people know me better than anyone IRL.
The emotional core: Unconditional acceptance without judgment.
The journey: From isolation to community.
The resolution: Chosen family is still family."""
        
        idea_id = db.insert_idea(text=long_text, version=1)
        idea = db.get_idea(idea_id)
        
        assert idea["text"] == long_text
        assert len(idea["text"]) > 100  # Minimum text length
        
        db.close()


class TestDatabaseSearchAndRetrieve:
    """Test search and retrieval operations on saved ideas."""
    
    def setup_method(self):
        """Create a temporary database with test data."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ideas.db")
        self.db = setup_idea_database(self.db_path)
        
        # Insert test ideas
        self.db.insert_idea("Online community story about gaming", version=1)
        self.db.insert_idea("Family drama with online elements", version=1)
        self.db.insert_idea("Chosen family finding belonging", version=2)
    
    def teardown_method(self):
        """Clean up the temporary database."""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_search_ideas_by_keyword(self):
        """Test searching ideas by keyword in text."""
        results = self.db.search_ideas("online")
        assert len(results) == 2
        assert all("online" in r["text"].lower() for r in results)
    
    def test_search_ideas_no_results(self):
        """Test search with no matches."""
        results = self.db.search_ideas("nonexistent")
        assert len(results) == 0
    
    def test_get_ideas_by_version(self):
        """Test filtering ideas by version."""
        v1_ideas = self.db.get_ideas_by_version(1)
        v2_ideas = self.db.get_ideas_by_version(2)
        
        assert len(v1_ideas) == 2
        assert len(v2_ideas) == 1
    
    def test_get_all_ideas(self):
        """Test retrieving all ideas."""
        all_ideas = self.db.get_all_ideas()
        assert len(all_ideas) == 3
    
    def test_count_ideas(self):
        """Test counting ideas."""
        assert self.db.count_ideas() == 3
