"""Tests for SchemaManager - centralized database schema management."""

import sys
import sqlite3
import pytest
from pathlib import Path

# Setup paths
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent.parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

from T.Database.schema_manager import SchemaManager, initialize_database


class TestSchemaManager:
    """Tests for SchemaManager class."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    
    def test_initialize_schema_creates_all_tables(self, db_connection):
        """Test that initialize_schema creates all required tables."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        # Verify all tables exist
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ["Review", "Script", "Story", "StoryReview", "Title"]
        for table in expected_tables:
            assert table in tables, f"Table {table} should exist"
    
    def test_verify_schema_returns_true_after_init(self, db_connection):
        """Test that verify_schema returns True after initialization."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        assert manager.verify_schema() is True
    
    def test_verify_schema_returns_false_before_init(self, db_connection):
        """Test that verify_schema returns False before initialization."""
        manager = SchemaManager(db_connection)
        
        assert manager.verify_schema() is False
    
    def test_get_missing_tables_empty_db(self, db_connection):
        """Test get_missing_tables on empty database."""
        manager = SchemaManager(db_connection)
        
        missing = manager.get_missing_tables()
        
        assert set(missing) == {"Review", "Story", "Title", "Script", "StoryReview"}
    
    def test_get_missing_tables_after_init(self, db_connection):
        """Test get_missing_tables returns empty after initialization."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        missing = manager.get_missing_tables()
        
        assert missing == []
    
    def test_initialize_schema_is_idempotent(self, db_connection):
        """Test that initialize_schema can be called multiple times safely."""
        manager = SchemaManager(db_connection)
        
        # Call multiple times
        manager.initialize_schema()
        manager.initialize_schema()
        manager.initialize_schema()
        
        # Should still work correctly
        assert manager.verify_schema() is True
    
    def test_get_table_info_validates_table_name(self, db_connection):
        """Test that get_table_info rejects unknown table names."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        with pytest.raises(ValueError, match="Unknown table"):
            manager.get_table_info("NonExistentTable")
    
    def test_get_table_info(self, db_connection):
        """Test get_table_info returns column information."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        info = manager.get_table_info("Title")
        columns = [row[1] for row in info]
        
        expected_columns = ["id", "story_id", "version", "text", "review_id", "created_at"]
        assert columns == expected_columns
    
    def test_table_order_constant(self):
        """Test that TABLE_ORDER contains all expected tables."""
        expected = ["Review", "Story", "Title", "Script", "StoryReview"]
        assert SchemaManager.TABLE_ORDER == expected


class TestInitializeDatabaseFunction:
    """Tests for initialize_database convenience function."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    
    def test_initialize_database_creates_schema(self, db_connection):
        """Test that initialize_database creates all tables."""
        manager = initialize_database(db_connection)
        
        assert manager.verify_schema() is True
    
    def test_initialize_database_returns_manager(self, db_connection):
        """Test that initialize_database returns a SchemaManager instance."""
        manager = initialize_database(db_connection)
        
        assert isinstance(manager, SchemaManager)


class TestTableSchemas:
    """Tests for individual table schemas."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    
    def test_review_table_schema(self, db_connection):
        """Test Review table has correct columns."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        info = manager.get_table_info("Review")
        columns = [row[1] for row in info]
        
        assert "id" in columns
        assert "text" in columns
        assert "score" in columns
        assert "created_at" in columns
    
    def test_story_table_schema(self, db_connection):
        """Test Story table has correct columns."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        info = manager.get_table_info("Story")
        columns = [row[1] for row in info]
        
        assert "id" in columns
        assert "idea_id" in columns
        assert "title_id" in columns
        assert "script_id" in columns
        assert "state" in columns
    
    def test_script_table_schema(self, db_connection):
        """Test Script table has correct columns."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        info = manager.get_table_info("Script")
        columns = [row[1] for row in info]
        
        assert "id" in columns
        assert "story_id" in columns
        assert "version" in columns
        assert "text" in columns
        assert "review_id" in columns
    
    def test_story_review_table_schema(self, db_connection):
        """Test StoryReview table has correct columns."""
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        info = manager.get_table_info("StoryReview")
        columns = [row[1] for row in info]
        
        assert "id" in columns
        assert "story_id" in columns
        assert "review_id" in columns
        assert "version" in columns
        assert "review_type" in columns
