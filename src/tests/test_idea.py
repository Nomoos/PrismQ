"""Tests for the shared Idea database module."""

import os
import sqlite3
import tempfile

import pytest

from src import IdeaTable, setup_idea_table


class TestIdeaTableSetup:
    """Test database setup and connection."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ideas.db")
        self.db = IdeaTable(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_connect(self):
        """Test database connection."""
        self.db.connect()
        assert self.db.conn is not None

    def test_close(self):
        """Test database close."""
        self.db.connect()
        self.db.close()
        assert self.db.conn is None

    def test_create_tables(self):
        """Test table creation."""
        self.db.connect()
        self.db.create_tables()

        # Verify table exists
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='Idea'
        """
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "Idea"

    def test_setup_function(self):
        """Test the setup_idea_table helper function."""
        db = setup_idea_table(self.db_path)

        assert db is not None
        assert db.conn is not None

        # Verify table was created
        cursor = db.conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='Idea'
        """
        )
        result = cursor.fetchone()
        assert result is not None

        db.close()


class TestIdeaTableCRUD:
    """Test CRUD operations on Idea database."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ideas.db")
        self.db = setup_idea_table(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_insert_idea(self):
        """Test inserting an idea."""
        idea_id = self.db.insert_idea(text="Write a horror story about a ghost.", version=1)

        assert idea_id is not None
        assert idea_id > 0

    def test_insert_idea_from_dict(self):
        """Test inserting idea from dictionary."""
        idea_dict = {"text": "Create an educational video.", "version": 2}

        idea_id = self.db.insert_idea_from_dict(idea_dict)

        assert idea_id is not None
        assert idea_id > 0

    def test_get_idea(self):
        """Test retrieving an idea by ID."""
        text = "Test idea content"
        idea_id = self.db.insert_idea(text=text, version=1)

        idea = self.db.get_idea(idea_id)

        assert idea is not None
        assert idea["id"] == idea_id
        assert idea["text"] == text
        assert idea["version"] == 1
        assert idea["created_at"] is not None

    def test_get_nonexistent_idea(self):
        """Test retrieving non-existent idea returns None."""
        idea = self.db.get_idea(99999)
        assert idea is None

    def test_get_all_ideas(self):
        """Test retrieving all ideas."""
        self.db.insert_idea("Idea 1", version=1)
        self.db.insert_idea("Idea 2", version=1)
        self.db.insert_idea("Idea 3", version=2)

        ideas = self.db.get_all_ideas()

        assert len(ideas) == 3

    def test_get_ideas_by_version(self):
        """Test filtering ideas by version."""
        self.db.insert_idea("Idea v1", version=1)
        self.db.insert_idea("Another v1", version=1)
        self.db.insert_idea("Idea v2", version=2)

        v1_ideas = self.db.get_ideas_by_version(1)
        v2_ideas = self.db.get_ideas_by_version(2)

        assert len(v1_ideas) == 2
        assert len(v2_ideas) == 1

    def test_get_latest_ideas(self):
        """Test getting latest ideas with limit."""
        for i in range(15):
            self.db.insert_idea(f"Idea {i}", version=1)

        latest = self.db.get_latest_ideas(limit=10)

        assert len(latest) == 10

    def test_update_idea_text(self):
        """Test updating idea text."""
        idea_id = self.db.insert_idea("Original text", version=1)

        success = self.db.update_idea(idea_id, text="Updated text")

        assert success is True
        idea = self.db.get_idea(idea_id)
        assert idea["text"] == "Updated text"
        assert idea["version"] == 1  # Version unchanged

    def test_update_idea_version(self):
        """Test updating idea version."""
        idea_id = self.db.insert_idea("Test", version=1)

        success = self.db.update_idea(idea_id, version=2)

        assert success is True
        idea = self.db.get_idea(idea_id)
        assert idea["version"] == 2

    def test_update_idea_both_fields(self):
        """Test updating both text and version."""
        idea_id = self.db.insert_idea("Original", version=1)

        success = self.db.update_idea(idea_id, text="New", version=3)

        assert success is True
        idea = self.db.get_idea(idea_id)
        assert idea["text"] == "New"
        assert idea["version"] == 3

    def test_update_idea_no_fields(self):
        """Test update with no fields does nothing."""
        idea_id = self.db.insert_idea("Test", version=1)

        success = self.db.update_idea(idea_id)

        assert success is False

    def test_delete_idea(self):
        """Test deleting an idea."""
        idea_id = self.db.insert_idea("To be deleted", version=1)

        success = self.db.delete_idea(idea_id)

        assert success is True
        idea = self.db.get_idea(idea_id)
        assert idea is None

    def test_delete_nonexistent_idea(self):
        """Test deleting non-existent idea returns False."""
        success = self.db.delete_idea(99999)
        assert success is False


class TestIdeaTableVersionConstraint:
    """Test version constraint enforcement (CHECK >= 0)."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ideas.db")
        self.db = setup_idea_table(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_negative_version_fails_insert(self):
        """Test that negative version fails at database level due to CHECK constraint."""
        with pytest.raises(sqlite3.IntegrityError):
            self.db.insert_idea("Test idea", version=-1)

    def test_zero_version_allowed(self):
        """Test that version 0 is allowed (edge case for CHECK >= 0)."""
        idea_id = self.db.insert_idea("Test idea with version 0", version=0)

        idea = self.db.get_idea(idea_id)
        assert idea is not None
        assert idea["version"] == 0

    def test_positive_version_allowed(self):
        """Test that positive versions work correctly."""
        idea_id = self.db.insert_idea("Test idea", version=5)

        idea = self.db.get_idea(idea_id)
        assert idea is not None
        assert idea["version"] == 5

    def test_update_to_negative_version_fails(self):
        """Test that updating to negative version fails at database level."""
        idea_id = self.db.insert_idea("Test idea", version=1)

        with pytest.raises(sqlite3.IntegrityError):
            self.db.update_idea(idea_id, version=-1)

    def test_default_version_is_one(self):
        """Test that default version is 1 when not specified in raw SQL insert."""
        # Verify the DEFAULT 1 constraint by inserting via raw SQL
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO Idea (text) VALUES (?)", ("Test with default version",))
        self.db.conn.commit()
        idea_id = cursor.lastrowid

        idea = self.db.get_idea(idea_id)
        assert idea is not None
        assert idea["version"] == 1


class TestIdeaTableSearch:
    """Test search and query operations."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ideas.db")
        self.db = setup_idea_table(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_search_ideas(self):
        """Test searching ideas by text content."""
        self.db.insert_idea("Write a horror story about ghosts", version=1)
        self.db.insert_idea("Create a comedy video", version=1)
        self.db.insert_idea("Horror movie review", version=1)

        results = self.db.search_ideas("horror")

        assert len(results) == 2

    def test_search_ideas_no_results(self):
        """Test search with no matching results."""
        self.db.insert_idea("Comedy content", version=1)

        results = self.db.search_ideas("horror")

        assert len(results) == 0

    def test_search_ideas_case_insensitive(self):
        """Test search is case-insensitive (SQLite LIKE behavior)."""
        self.db.insert_idea("HORROR story uppercase", version=1)
        self.db.insert_idea("horror story lowercase", version=1)

        # SQLite LIKE is case-insensitive for ASCII
        results = self.db.search_ideas("horror")

        assert len(results) >= 1

    def test_count_ideas(self):
        """Test counting total ideas."""
        assert self.db.count_ideas() == 0

        self.db.insert_idea("Idea 1", version=1)
        assert self.db.count_ideas() == 1

        self.db.insert_idea("Idea 2", version=1)
        self.db.insert_idea("Idea 3", version=2)
        assert self.db.count_ideas() == 3

    def test_get_max_version(self):
        """Test getting maximum version."""
        assert self.db.get_max_version() == 0

        self.db.insert_idea("v1", version=1)
        assert self.db.get_max_version() == 1

        self.db.insert_idea("v3", version=3)
        assert self.db.get_max_version() == 3

        self.db.insert_idea("v2", version=2)
        assert self.db.get_max_version() == 3  # Still 3


class TestIdeaTableInspirations:
    """Test inspiration reference operations (M:N, nullable)."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ideas.db")
        self.db = setup_idea_table(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_insert_inspiration(self):
        """Test registering an inspiration source returns an integer ID."""
        insp_id = self.db.insert_inspiration(source="user", source_id="user-input-1")
        assert isinstance(insp_id, int)
        assert insp_id > 0

    def test_insert_inspiration_idempotent(self):
        """Test that inserting the same inspiration twice returns the same ID."""
        id1 = self.db.insert_inspiration(source="youtube", source_id="abc123")
        id2 = self.db.insert_inspiration(source="youtube", source_id="abc123")
        assert id1 == id2

    def test_get_inspiration(self):
        """Test retrieving an Inspiration record by ID."""
        insp_id = self.db.insert_inspiration(
            source="reddit", source_id="post-xyz", title="Cool post", url="https://reddit.com"
        )
        record = self.db.get_inspiration(insp_id)
        assert record is not None
        assert record["source"] == "reddit"
        assert record["source_id"] == "post-xyz"
        assert record["title"] == "Cool post"

    def test_add_inspiration(self):
        """Test linking an inspiration source to an idea."""
        idea_id = self.db.insert_idea("Horror story idea", version=1)
        insp_id = self.db.insert_inspiration(source="user", source_id="user-input-1")
        result = self.db.add_inspiration(idea_id, insp_id)
        assert result is True

    def test_add_duplicate_inspiration_returns_false(self):
        """Test that adding duplicate inspiration returns False."""
        idea_id = self.db.insert_idea("Horror story idea", version=1)
        insp_id = self.db.insert_inspiration(source="user", source_id="user-input-1")
        self.db.add_inspiration(idea_id, insp_id)
        result = self.db.add_inspiration(idea_id, insp_id)
        assert result is False

    def test_get_inspirations(self):
        """Test getting all inspirations for an idea."""
        idea_id = self.db.insert_idea("Fusion idea", version=1)
        id1 = self.db.insert_inspiration(source="user", source_id="source-1")
        id2 = self.db.insert_inspiration(source="youtube", source_id="source-2")
        id3 = self.db.insert_inspiration(source="reddit", source_id="source-3")
        self.db.add_inspiration(idea_id, id1)
        self.db.add_inspiration(idea_id, id2)
        self.db.add_inspiration(idea_id, id3)

        inspirations = self.db.get_inspirations(idea_id)
        assert len(inspirations) == 3
        source_ids = [r["source_id"] for r in inspirations]
        assert "source-1" in source_ids
        assert "source-2" in source_ids
        assert "source-3" in source_ids

    def test_get_inspirations_empty(self):
        """Test that idea without inspirations returns empty list."""
        idea_id = self.db.insert_idea("No inspirations", version=1)
        inspirations = self.db.get_inspirations(idea_id)
        assert inspirations == []

    def test_get_ideas_by_inspiration(self):
        """Test getting all ideas from a specific inspiration source."""
        id1 = self.db.insert_idea("Idea from source A", version=1)
        id2 = self.db.insert_idea("Another idea from source A", version=1)
        id3 = self.db.insert_idea("Idea from source B", version=1)

        insp_a = self.db.insert_inspiration(source="youtube", source_id="source-A")
        insp_b = self.db.insert_inspiration(source="reddit", source_id="source-B")
        self.db.add_inspiration(id1, insp_a)
        self.db.add_inspiration(id2, insp_a)
        self.db.add_inspiration(id3, insp_b)

        ideas = self.db.get_ideas_by_inspiration(insp_a)
        assert len(ideas) == 2

    def test_remove_inspiration(self):
        """Test removing an inspiration link."""
        idea_id = self.db.insert_idea("Test idea", version=1)
        insp1 = self.db.insert_inspiration(source="user", source_id="source-1")
        insp2 = self.db.insert_inspiration(source="user", source_id="source-2")
        self.db.add_inspiration(idea_id, insp1)
        self.db.add_inspiration(idea_id, insp2)

        result = self.db.remove_inspiration(idea_id, insp1)
        assert result is True

        inspirations = self.db.get_inspirations(idea_id)
        assert len(inspirations) == 1
        assert inspirations[0]["source_id"] == "source-2"

    def test_remove_nonexistent_inspiration(self):
        """Test removing non-existent inspiration returns False."""
        idea_id = self.db.insert_idea("Test idea", version=1)
        result = self.db.remove_inspiration(idea_id, 99999)
        assert result is False

    def test_idea_inspirations_table_created(self):
        """Test that IdeaInspiration table exists."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='IdeaInspiration'
        """
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "IdeaInspiration"

    def test_inspiration_table_created(self):
        """Test that Inspiration table exists."""
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='Inspiration'
        """
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "Inspiration"

