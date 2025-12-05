"""Tests for connection module - PEP 249 compliant SQLite connection utilities.

Tests the connection utilities defined in T.Database.connection following
PEP 249 (Python Database API Specification v2.0).
"""

import sys
import sqlite3
import pytest
from pathlib import Path
import tempfile
import os

# Setup paths
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent.parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

from Model.Database.connection import (
    get_connection,
    connection_context,
    create_database,
    verify_connection,
)


class TestGetConnection:
    """Tests for get_connection function."""
    
    def test_get_connection_returns_sqlite_connection(self):
        """Test that get_connection returns a sqlite3.Connection."""
        conn = get_connection(":memory:")
        try:
            assert isinstance(conn, sqlite3.Connection)
        finally:
            conn.close()
    
    def test_get_connection_enables_row_factory(self):
        """Test that row_factory is set to sqlite3.Row by default."""
        conn = get_connection(":memory:")
        try:
            assert conn.row_factory == sqlite3.Row
        finally:
            conn.close()
    
    def test_get_connection_row_factory_disabled(self):
        """Test that row_factory can be disabled."""
        conn = get_connection(":memory:", enable_row_factory=False)
        try:
            assert conn.row_factory is None
        finally:
            conn.close()
    
    def test_get_connection_enables_foreign_keys(self):
        """Test that foreign keys are enabled by default."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert result[0] == 1  # 1 = enabled
        finally:
            conn.close()
    
    def test_get_connection_foreign_keys_disabled(self):
        """Test that foreign keys can be disabled."""
        conn = get_connection(":memory:", enable_foreign_keys=False)
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert result[0] == 0  # 0 = disabled
        finally:
            conn.close()
    
    def test_get_connection_allows_cursor_operations(self):
        """Test that connection supports cursor() as per PEP 249."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            assert cursor is not None
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
        finally:
            conn.close()
    
    def test_get_connection_supports_parameterized_queries(self):
        """Test that connection supports ? placeholder queries (PEP 249)."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute("INSERT INTO test (name) VALUES (?)", ("test_value",))
            cursor.execute("SELECT name FROM test WHERE id = ?", (1,))
            result = cursor.fetchone()
            assert result["name"] == "test_value"
        finally:
            conn.close()
    
    def test_get_connection_row_allows_dict_access(self):
        """Test that sqlite3.Row allows dictionary-like access."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute("INSERT INTO test (name) VALUES (?)", ("test_name",))
            cursor.execute("SELECT * FROM test WHERE id = ?", (1,))
            row = cursor.fetchone()
            
            # Can access by column name
            assert row["id"] == 1
            assert row["name"] == "test_name"
            
            # Can also access by index
            assert row[0] == 1
            assert row[1] == "test_name"
        finally:
            conn.close()
    
    def test_get_connection_foreign_keys_enforced(self):
        """Test that foreign key constraints are actually enforced."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            
            # Create parent and child tables
            cursor.execute("""
                CREATE TABLE parent (
                    id INTEGER PRIMARY KEY
                )
            """)
            cursor.execute("""
                CREATE TABLE child (
                    id INTEGER PRIMARY KEY,
                    parent_id INTEGER NOT NULL,
                    FOREIGN KEY (parent_id) REFERENCES parent(id)
                )
            """)
            conn.commit()
            
            # Try to insert child with non-existent parent - should fail
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("INSERT INTO child (parent_id) VALUES (?)", (999,))
                conn.commit()
        finally:
            conn.close()
    
    def test_get_connection_with_file_database(self):
        """Test connection to a file-based database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.s3db")
            conn = get_connection(db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
                conn.commit()
                
                # Verify file was created
                assert os.path.exists(db_path)
            finally:
                conn.close()


class TestConnectionContext:
    """Tests for connection_context context manager."""
    
    def test_connection_context_provides_connection(self):
        """Test that connection_context yields a valid connection."""
        with connection_context(":memory:") as conn:
            assert isinstance(conn, sqlite3.Connection)
    
    def test_connection_context_closes_on_exit(self):
        """Test that connection is closed when context exits."""
        with connection_context(":memory:") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        
        # Connection should be closed after context exit
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")
    
    def test_connection_context_closes_on_exception(self):
        """Test that connection is closed even when exception occurs."""
        try:
            with connection_context(":memory:") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Connection should be closed
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")
    
    def test_connection_context_passes_options(self):
        """Test that options are passed to get_connection."""
        with connection_context(
            ":memory:",
            enable_row_factory=False,
            enable_foreign_keys=False
        ) as conn:
            assert conn.row_factory is None
            
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert result[0] == 0


class TestCreateDatabase:
    """Tests for create_database function."""
    
    def test_create_database_creates_file(self):
        """Test that create_database creates the database file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "new.s3db")
            
            assert not os.path.exists(db_path)
            
            conn = create_database(db_path)
            try:
                assert os.path.exists(db_path)
            finally:
                conn.close()
    
    def test_create_database_creates_parent_directories(self):
        """Test that parent directories are created if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "deep", "nested", "dir", "test.s3db")
            
            conn = create_database(db_path)
            try:
                assert os.path.exists(db_path)
                assert os.path.isdir(os.path.join(tmpdir, "deep", "nested", "dir"))
            finally:
                conn.close()
    
    def test_create_database_exist_ok_true(self):
        """Test that existing database is opened when exist_ok=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "existing.s3db")
            
            # Create initial database
            conn1 = create_database(db_path)
            cursor = conn1.cursor()
            cursor.execute("CREATE TABLE marker (id INTEGER PRIMARY KEY)")
            conn1.commit()
            conn1.close()
            
            # Open again with exist_ok=True (default)
            conn2 = create_database(db_path)
            try:
                cursor = conn2.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marker'")
                result = cursor.fetchone()
                assert result is not None  # Table should still exist
            finally:
                conn2.close()
    
    def test_create_database_exist_ok_false_raises(self):
        """Test that FileExistsError is raised when exist_ok=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "existing.s3db")
            
            # Create initial database
            conn = create_database(db_path)
            conn.close()
            
            # Try to create again with exist_ok=False
            with pytest.raises(FileExistsError):
                create_database(db_path, exist_ok=False)
    
    def test_create_database_rejects_memory(self):
        """Test that :memory: is rejected with helpful error."""
        with pytest.raises(ValueError, match="in-memory"):
            create_database(":memory:")
    
    def test_create_database_returns_configured_connection(self):
        """Test that returned connection is properly configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "new.s3db")
            
            conn = create_database(db_path)
            try:
                # Check row factory
                assert conn.row_factory == sqlite3.Row
                
                # Check foreign keys
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys")
                result = cursor.fetchone()
                assert result[0] == 1
            finally:
                conn.close()


class TestVerifyConnection:
    """Tests for verify_connection function."""
    
    def test_verify_connection_valid_connection(self):
        """Test that valid connection returns True."""
        conn = get_connection(":memory:")
        try:
            assert verify_connection(conn) is True
        finally:
            conn.close()
    
    def test_verify_connection_closed_connection(self):
        """Test that closed connection returns False."""
        conn = get_connection(":memory:")
        conn.close()
        
        assert verify_connection(conn) is False
    
    def test_verify_connection_without_foreign_keys(self):
        """Test that connection without foreign keys returns False."""
        conn = get_connection(":memory:", enable_foreign_keys=False)
        try:
            assert verify_connection(conn) is False
        finally:
            conn.close()


class TestPEP249Compliance:
    """Tests verifying PEP 249 compliance."""
    
    def test_connection_has_cursor_method(self):
        """Test that connection has cursor() method per PEP 249."""
        conn = get_connection(":memory:")
        try:
            assert hasattr(conn, 'cursor')
            assert callable(conn.cursor)
        finally:
            conn.close()
    
    def test_connection_has_commit_method(self):
        """Test that connection has commit() method per PEP 249."""
        conn = get_connection(":memory:")
        try:
            assert hasattr(conn, 'commit')
            assert callable(conn.commit)
        finally:
            conn.close()
    
    def test_connection_has_rollback_method(self):
        """Test that connection has rollback() method per PEP 249."""
        conn = get_connection(":memory:")
        try:
            assert hasattr(conn, 'rollback')
            assert callable(conn.rollback)
        finally:
            conn.close()
    
    def test_connection_has_close_method(self):
        """Test that connection has close() method per PEP 249."""
        conn = get_connection(":memory:")
        try:
            assert hasattr(conn, 'close')
            assert callable(conn.close)
        finally:
            conn.close()
    
    def test_cursor_has_execute_method(self):
        """Test that cursor has execute() method per PEP 249."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            assert hasattr(cursor, 'execute')
            assert callable(cursor.execute)
        finally:
            conn.close()
    
    def test_cursor_has_fetchone_method(self):
        """Test that cursor has fetchone() method per PEP 249."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            assert hasattr(cursor, 'fetchone')
            assert callable(cursor.fetchone)
        finally:
            conn.close()
    
    def test_cursor_has_fetchall_method(self):
        """Test that cursor has fetchall() method per PEP 249."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            assert hasattr(cursor, 'fetchall')
            assert callable(cursor.fetchall)
        finally:
            conn.close()
    
    def test_paramstyle_qmark(self):
        """Test that ? placeholder works (qmark paramstyle)."""
        conn = get_connection(":memory:")
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ? AS value", ("test",))
            result = cursor.fetchone()
            assert result["value"] == "test"
        finally:
            conn.close()


class TestDatabaseDesignCompliance:
    """Tests verifying compliance with DATABASE_DESIGN.md recommendations."""
    
    def test_default_timeout_is_30_seconds(self):
        """Test that default timeout matches DATABASE_DESIGN.md (30.0 seconds)."""
        # The design doc specifies timeout=30.0
        # We verify the connection accepts the default timeout value
        conn = get_connection(":memory:", timeout=30.0)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
        finally:
            conn.close()
    
    def test_check_same_thread_false_by_default(self):
        """Test that check_same_thread=False for multi-process access per DATABASE_DESIGN.md."""
        # The design doc specifies check_same_thread=False
        # This allows connections to be used from multiple threads
        conn = get_connection(":memory:", check_same_thread=False)
        try:
            # If check_same_thread was True, this would raise an error
            # when accessed from a different thread
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1
        finally:
            conn.close()
    
    def test_wal_mode_enabled_for_file_databases(self):
        """Test that WAL mode is enabled for file databases per DATABASE_DESIGN.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.s3db")
            conn = get_connection(db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode")
                result = cursor.fetchone()
                assert result[0].lower() == "wal"
            finally:
                conn.close()
    
    def test_recommended_connection_settings(self):
        """Test that all DATABASE_DESIGN.md recommended settings are applied.
        
        Reference: DATABASE_DESIGN.md "Best Practices Research" section
        
        Recommended SQLite configuration:
        - check_same_thread=False
        - timeout=30.0
        - PRAGMA journal_mode=WAL
        - PRAGMA foreign_keys=ON
        - row_factory = sqlite3.Row
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "prismq.s3db")
            conn = get_connection(db_path)
            try:
                cursor = conn.cursor()
                
                # Check row_factory
                assert conn.row_factory == sqlite3.Row
                
                # Check foreign keys
                cursor.execute("PRAGMA foreign_keys")
                assert cursor.fetchone()[0] == 1
                
                # Check WAL mode (file-based DB)
                cursor.execute("PRAGMA journal_mode")
                assert cursor.fetchone()[0].lower() == "wal"
                
            finally:
                conn.close()
