"""Tests for database domain exceptions.

Tests cover:
- Exception hierarchy
- Exception attributes
- map_sqlite_error helper function
"""

import pytest
import sqlite3
from T.Database.exceptions import (
    DatabaseException,
    EntityNotFoundError,
    DuplicateEntityError,
    ForeignKeyViolationError,
    ConstraintViolationError,
    DatabaseConnectionError,
    DataIntegrityError,
    InvalidStateTransitionError,
    map_sqlite_error,
)


class TestDatabaseException:
    """Tests for base DatabaseException."""
    
    def test_create_with_message(self):
        """Test creating exception with message."""
        exc = DatabaseException("Test error")
        assert exc.message == "Test error"
        assert str(exc) == "Test error"
    
    def test_create_with_original_error(self):
        """Test creating exception with original error."""
        original = ValueError("Original error")
        exc = DatabaseException("Wrapped error", original_error=original)
        assert exc.original_error is original
    
    def test_is_exception(self):
        """Test that DatabaseException is an Exception."""
        exc = DatabaseException("Test")
        assert isinstance(exc, Exception)


class TestEntityNotFoundError:
    """Tests for EntityNotFoundError."""
    
    def test_create_with_entity_type_and_id(self):
        """Test creating exception with entity type and id."""
        exc = EntityNotFoundError("Story", 123)
        assert exc.entity_type == "Story"
        assert exc.entity_id == 123
        assert "Story" in str(exc)
        assert "123" in str(exc)
    
    def test_message_format(self):
        """Test message format."""
        exc = EntityNotFoundError("Title", 456)
        assert str(exc) == "Title with id 456 not found"
    
    def test_inherits_from_database_exception(self):
        """Test that it inherits from DatabaseException."""
        exc = EntityNotFoundError("Script", 1)
        assert isinstance(exc, DatabaseException)


class TestDuplicateEntityError:
    """Tests for DuplicateEntityError."""
    
    def test_create_with_constraint(self):
        """Test creating exception with constraint info."""
        exc = DuplicateEntityError("Title", constraint="story_id, version")
        assert exc.entity_type == "Title"
        assert exc.constraint == "story_id, version"
        assert "unique constraint" in str(exc).lower()
    
    def test_create_with_entity_id(self):
        """Test creating exception with entity id."""
        exc = DuplicateEntityError("Story", entity_id=123)
        assert exc.entity_id == 123
        assert "123" in str(exc)
    
    def test_create_without_details(self):
        """Test creating exception without details."""
        exc = DuplicateEntityError("Review")
        assert exc.entity_type == "Review"
        assert "unique constraint violated" in str(exc).lower()
    
    def test_inherits_from_database_exception(self):
        """Test that it inherits from DatabaseException."""
        exc = DuplicateEntityError("Title")
        assert isinstance(exc, DatabaseException)


class TestForeignKeyViolationError:
    """Tests for ForeignKeyViolationError."""
    
    def test_create_with_column_and_value(self):
        """Test creating exception with column and value."""
        exc = ForeignKeyViolationError("story_id", 999)
        assert exc.column == "story_id"
        assert exc.value == 999
    
    def test_create_with_referenced_table(self):
        """Test creating exception with referenced table."""
        exc = ForeignKeyViolationError("story_id", 999, referenced_table="Story")
        assert exc.referenced_table == "Story"
        assert "Story" in str(exc)
        assert "not found" in str(exc)
    
    def test_message_format(self):
        """Test message format."""
        exc = ForeignKeyViolationError("idea_id", 123, referenced_table="Idea")
        assert "idea_id=123" in str(exc)
        assert "Idea not found" in str(exc)
    
    def test_inherits_from_database_exception(self):
        """Test that it inherits from DatabaseException."""
        exc = ForeignKeyViolationError("id", 1)
        assert isinstance(exc, DatabaseException)


class TestConstraintViolationError:
    """Tests for ConstraintViolationError."""
    
    def test_create_with_constraint(self):
        """Test creating exception with constraint description."""
        exc = ConstraintViolationError("score must be 0-100")
        assert exc.constraint == "score must be 0-100"
        assert "score must be 0-100" in str(exc)
    
    def test_create_with_column_and_value(self):
        """Test creating exception with column and value."""
        exc = ConstraintViolationError("score must be 0-100", column="score", value=150)
        assert exc.column == "score"
        assert exc.value == 150
        assert "score=150" in str(exc)
    
    def test_inherits_from_database_exception(self):
        """Test that it inherits from DatabaseException."""
        exc = ConstraintViolationError("test")
        assert isinstance(exc, DatabaseException)


class TestDatabaseConnectionError:
    """Tests for DatabaseConnectionError."""
    
    def test_create_with_path(self):
        """Test creating exception with database path."""
        exc = DatabaseConnectionError("/path/to/db.s3db")
        assert exc.db_path == "/path/to/db.s3db"
        assert "/path/to/db.s3db" in str(exc)
    
    def test_create_with_reason(self):
        """Test creating exception with reason."""
        exc = DatabaseConnectionError("/path/to/db.s3db", reason="database is locked")
        assert exc.reason == "database is locked"
        assert "database is locked" in str(exc)
    
    def test_inherits_from_database_exception(self):
        """Test that it inherits from DatabaseException."""
        exc = DatabaseConnectionError("/path")
        assert isinstance(exc, DatabaseException)


class TestDataIntegrityError:
    """Tests for DataIntegrityError."""
    
    def test_create_with_description(self):
        """Test creating exception with description."""
        exc = DataIntegrityError("Version sequence is not contiguous")
        assert exc.description == "Version sequence is not contiguous"
        assert "Version sequence is not contiguous" in str(exc)
    
    def test_message_format(self):
        """Test message format."""
        exc = DataIntegrityError("Invalid data")
        assert "Data integrity error:" in str(exc)
    
    def test_inherits_from_database_exception(self):
        """Test that it inherits from DatabaseException."""
        exc = DataIntegrityError("test")
        assert isinstance(exc, DatabaseException)


class TestInvalidStateTransitionError:
    """Tests for InvalidStateTransitionError."""
    
    def test_create_with_states(self):
        """Test creating exception with state info."""
        exc = InvalidStateTransitionError("CREATED", "PUBLISHED")
        assert exc.from_state == "CREATED"
        assert exc.to_state == "PUBLISHED"
        assert "CREATED" in str(exc)
        assert "PUBLISHED" in str(exc)
    
    def test_create_with_entity_id(self):
        """Test creating exception with entity id."""
        exc = InvalidStateTransitionError("CREATED", "PUBLISHED", entity_id=123)
        assert exc.entity_id == 123
        assert "Story 123" in str(exc)
    
    def test_message_format(self):
        """Test message format."""
        exc = InvalidStateTransitionError("A", "B", entity_id=1)
        assert "Invalid state transition" in str(exc)
    
    def test_inherits_from_database_exception(self):
        """Test that it inherits from DatabaseException."""
        exc = InvalidStateTransitionError("A", "B")
        assert isinstance(exc, DatabaseException)


class TestMapSqliteError:
    """Tests for map_sqlite_error helper function."""
    
    def test_map_foreign_key_error(self):
        """Test mapping foreign key error."""
        error = sqlite3.IntegrityError("FOREIGN KEY constraint failed")
        result = map_sqlite_error(error, {"column": "story_id", "value": 999})
        assert isinstance(result, ForeignKeyViolationError)
        assert result.column == "story_id"
        assert result.value == 999
    
    def test_map_unique_error(self):
        """Test mapping unique constraint error."""
        error = sqlite3.IntegrityError("UNIQUE constraint failed: Title.story_id, Title.version")
        result = map_sqlite_error(error, {"entity_type": "Title"})
        assert isinstance(result, DuplicateEntityError)
        assert result.entity_type == "Title"
    
    def test_map_check_error(self):
        """Test mapping check constraint error."""
        error = sqlite3.IntegrityError("CHECK constraint failed: score")
        result = map_sqlite_error(error, {"column": "score", "value": 150})
        assert isinstance(result, ConstraintViolationError)
    
    def test_map_locked_error(self):
        """Test mapping database locked error."""
        error = sqlite3.OperationalError("database is locked")
        result = map_sqlite_error(error, {"db_path": "/path/db.s3db"})
        assert isinstance(result, DatabaseConnectionError)
        assert "locked" in str(result)
    
    def test_map_generic_error(self):
        """Test mapping generic error."""
        error = sqlite3.Error("Unknown error")
        result = map_sqlite_error(error)
        assert isinstance(result, DatabaseException)
        assert "Unknown error" in str(result)
    
    def test_preserves_original_error(self):
        """Test that original error is preserved."""
        original = sqlite3.IntegrityError("UNIQUE constraint failed")
        result = map_sqlite_error(original)
        assert result.original_error is original


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""
    
    def test_all_exceptions_inherit_from_database_exception(self):
        """Test that all exceptions inherit from DatabaseException."""
        exceptions = [
            EntityNotFoundError("Story", 1),
            DuplicateEntityError("Story"),
            ForeignKeyViolationError("id", 1),
            ConstraintViolationError("test"),
            DatabaseConnectionError("/path"),
            DataIntegrityError("test"),
            InvalidStateTransitionError("A", "B"),
        ]
        for exc in exceptions:
            assert isinstance(exc, DatabaseException)
            assert isinstance(exc, Exception)
    
    def test_can_catch_all_with_database_exception(self):
        """Test that all exceptions can be caught with DatabaseException."""
        exceptions = [
            EntityNotFoundError("Story", 1),
            DuplicateEntityError("Story"),
            ForeignKeyViolationError("id", 1),
            ConstraintViolationError("test"),
            DatabaseConnectionError("/path"),
            DataIntegrityError("test"),
            InvalidStateTransitionError("A", "B"),
        ]
        for exc in exceptions:
            try:
                raise exc
            except DatabaseException as caught:
                assert caught is exc
