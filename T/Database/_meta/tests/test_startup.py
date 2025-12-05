"""Tests for startup module - safe database schema initialization."""

import sys
import sqlite3
import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

# Setup paths
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent.parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

from T.Database.startup import (
    DatabaseInitializationError,
    initialize_application_database,
    safe_initialize_database,
)
from T.Database.schema_manager import SchemaManager


class TestDatabaseInitializationError:
    """Tests for DatabaseInitializationError exception."""
    
    def test_error_with_message_only(self):
        """Test exception with message only."""
        error = DatabaseInitializationError("Test error message")
        
        assert error.message == "Test error message"
        assert error.original_error is None
        assert str(error) == "Test error message"
    
    def test_error_with_original_exception(self):
        """Test exception wrapping an original error."""
        original = ValueError("Original error")
        error = DatabaseInitializationError("Wrapped error", original)
        
        assert error.message == "Wrapped error"
        assert error.original_error is original
        assert str(error) == "Wrapped error"


class TestInitializeApplicationDatabase:
    """Tests for initialize_application_database function."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    
    @pytest.fixture
    def caplog_at_info(self, caplog):
        """Configure caplog to capture INFO level logs."""
        caplog.set_level(logging.INFO)
        return caplog
    
    def test_initializes_schema_successfully(self, db_connection, caplog_at_info):
        """Test successful schema initialization."""
        result = initialize_application_database(db_connection)
        
        assert result is True
        
        # Verify schema was created
        manager = SchemaManager(db_connection)
        assert manager.verify_schema() is True
    
    def test_logs_initialization_start(self, db_connection, caplog_at_info):
        """Test that initialization start is logged."""
        initialize_application_database(db_connection)
        
        assert "Starting database schema initialization" in caplog_at_info.text
    
    def test_logs_success_on_completion(self, db_connection, caplog_at_info):
        """Test that successful completion is logged."""
        initialize_application_database(db_connection)
        
        assert "completed successfully" in caplog_at_info.text
    
    def test_skips_if_schema_exists(self, db_connection, caplog_at_info):
        """Test that initialization is skipped if schema already exists."""
        # Initialize schema first
        manager = SchemaManager(db_connection)
        manager.initialize_schema()
        
        # Try to initialize again
        result = initialize_application_database(db_connection)
        
        assert result is True
        assert "already exists" in caplog_at_info.text
    
    def test_logs_missing_tables(self, db_connection, caplog_at_info):
        """Test that missing tables are logged before creation."""
        initialize_application_database(db_connection)
        
        assert "Missing tables to create" in caplog_at_info.text
    
    def test_is_idempotent(self, db_connection):
        """Test that multiple initializations are safe."""
        result1 = initialize_application_database(db_connection)
        result2 = initialize_application_database(db_connection)
        result3 = initialize_application_database(db_connection)
        
        assert result1 is True
        assert result2 is True
        assert result3 is True
        
        # Schema should still be valid
        manager = SchemaManager(db_connection)
        assert manager.verify_schema() is True
    
    def test_verify_parameter_false_skips_verification(self, db_connection, caplog_at_info):
        """Test that verify=False skips schema verification."""
        result = initialize_application_database(db_connection, verify=False)
        
        assert result is True
        assert "verification passed" not in caplog_at_info.text
    
    def test_handles_sqlite_error(self, db_connection, caplog_at_info):
        """Test handling of SQLite errors during initialization."""
        # Close connection to simulate error
        db_connection.close()
        
        # Should not raise, but return False
        result = initialize_application_database(db_connection)
        
        assert result is False
        assert "Database error" in caplog_at_info.text or "error" in caplog_at_info.text.lower()
    
    def test_attempts_rollback_on_error(self, caplog_at_info):
        """Test that rollback is attempted on error."""
        # Create a mock connection that fails on executescript
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_conn.execute.side_effect = sqlite3.Error("Mock error")
        
        # Create a mock SchemaManager that fails
        with patch('T.Database.startup.SchemaManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.verify_schema.return_value = False
            mock_manager.get_missing_tables.return_value = ["Table1"]
            mock_manager.initialize_schema.side_effect = sqlite3.Error("Init failed")
            mock_manager_class.return_value = mock_manager
            
            result = initialize_application_database(mock_conn)
            
            assert result is False
            # Rollback should have been attempted
            mock_conn.rollback.assert_called()


class TestSafeInitializeDatabase:
    """Tests for safe_initialize_database function."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    
    def test_returns_true_on_success(self, db_connection):
        """Test that True is returned on success."""
        result = safe_initialize_database(db_connection)
        
        assert result is True
    
    def test_returns_false_on_failure_default(self, db_connection):
        """Test that False is returned on failure by default."""
        # Close connection to cause error
        db_connection.close()
        
        result = safe_initialize_database(db_connection)
        
        assert result is False
    
    def test_raises_on_failure_when_requested(self):
        """Test that exception is raised when raise_on_error=True."""
        # Create closed connection
        conn = sqlite3.connect(':memory:')
        conn.close()
        
        with pytest.raises(DatabaseInitializationError):
            safe_initialize_database(conn, raise_on_error=True)
    
    def test_exception_contains_message(self):
        """Test that raised exception contains useful message."""
        conn = sqlite3.connect(':memory:')
        conn.close()
        
        with pytest.raises(DatabaseInitializationError) as exc_info:
            safe_initialize_database(conn, raise_on_error=True)
        
        assert "failed" in exc_info.value.message.lower() or "error" in exc_info.value.message.lower()


class TestIntegrationWithSchemaManager:
    """Integration tests with SchemaManager."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    
    def test_creates_all_required_tables(self, db_connection):
        """Test that all required tables are created."""
        initialize_application_database(db_connection)
        
        # Verify using SchemaManager
        manager = SchemaManager(db_connection)
        assert manager.verify_schema() is True
        
        # Check individual tables
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        expected = ["Review", "Script", "Story", "StoryReview", "Title"]
        for table in expected:
            assert table in tables
    
    def test_tables_have_correct_structure(self, db_connection):
        """Test that created tables have correct column structure."""
        initialize_application_database(db_connection)
        
        manager = SchemaManager(db_connection)
        
        # Check Title table columns
        title_info = manager.get_table_info("Title")
        title_columns = [row[1] for row in title_info]
        assert "id" in title_columns
        assert "story_id" in title_columns
        assert "version" in title_columns
        assert "text" in title_columns
    
    def test_configures_sqlite_pragmas(self, db_connection):
        """Test that SQLite is configured per DATABASE_DESIGN.md.
        
        Per T/_meta/docs/DATABASE_DESIGN.md, initialization should:
        - Enable WAL mode for better concurrency
        - Enable foreign key constraints
        """
        initialize_application_database(db_connection)
        
        # Check foreign keys are enabled
        cursor = db_connection.execute("PRAGMA foreign_keys")
        fk_result = cursor.fetchone()
        assert fk_result[0] == 1, "Foreign keys should be enabled"


class TestStartupOnlyUsage:
    """Tests verifying startup-only usage pattern."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    
    def test_function_signature_is_simple(self):
        """Test that the function has a simple, startup-friendly signature."""
        import inspect
        sig = inspect.signature(initialize_application_database)
        
        # Should have minimal required parameters
        params = list(sig.parameters.keys())
        assert "connection" in params
        
        # All other parameters should have defaults
        for param_name, param in sig.parameters.items():
            if param_name != "connection":
                assert param.default is not inspect.Parameter.empty
    
    def test_returns_boolean_for_easy_startup_checks(self, db_connection):
        """Test that return value is boolean for simple startup checks."""
        result = initialize_application_database(db_connection)
        
        assert isinstance(result, bool)
    
    def test_does_not_require_external_state(self, db_connection):
        """Test that function doesn't require external state setup."""
        # Should work with just a connection - no other setup needed
        result = initialize_application_database(db_connection)
        
        assert result is True
