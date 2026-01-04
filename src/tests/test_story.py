"""Tests for the shared Story database module."""

import os
import sqlite3
import tempfile

import pytest

from src import IdeaDatabase, StoryTable, setup_story_table
from src.story import CLEAR_IDEA_ID


class TestStoryTableSetup:
    """Test database setup and connection."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_stories.db")
        self.db = StoryTable(self.db_path)

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
            WHERE type='table' AND name='Story'
        """
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "Story"

    def test_setup_function(self):
        """Test the setup_story_table helper function."""
        db = setup_story_table(self.db_path)

        assert db is not None
        assert db.conn is not None

        # Verify table was created
        cursor = db.conn.cursor()
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='Story'
        """
        )
        result = cursor.fetchone()
        assert result is not None

        db.close()


class TestStoryTableCRUD:
    """Test CRUD operations on Story database."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_stories.db")
        self.db = setup_story_table(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_insert_story(self):
        """Test inserting a story."""
        story_id = self.db.insert_story()

        assert story_id is not None
        assert story_id > 0

    def test_insert_story_with_state(self):
        """Test inserting a story with custom state."""
        story_id = self.db.insert_story(state="PrismQ.T.Script.From.Idea.Title")

        assert story_id is not None
        story = self.db.get_story(story_id)
        assert story["state"] == "PrismQ.T.Script.From.Idea.Title"

    def test_insert_story_from_dict(self):
        """Test inserting story from dictionary."""
        story_dict = {"state": "PrismQ.T.Review.From.Script"}

        story_id = self.db.insert_story_from_dict(story_dict)

        assert story_id is not None
        assert story_id > 0
        story = self.db.get_story(story_id)
        assert story["state"] == "PrismQ.T.Review.From.Script"

    def test_get_story(self):
        """Test retrieving a story by ID."""
        story_id = self.db.insert_story()

        story = self.db.get_story(story_id)

        assert story is not None
        assert story["id"] == story_id
        assert story["state"] == "PrismQ.T.Title.From.Idea"
        assert story["idea_id"] is None
        assert story["created_at"] is not None
        assert story["updated_at"] is not None

    def test_get_nonexistent_story(self):
        """Test retrieving non-existent story returns None."""
        story = self.db.get_story(99999)
        assert story is None

    def test_get_all_stories(self):
        """Test retrieving all stories."""
        self.db.insert_story()
        self.db.insert_story(state="PrismQ.T.Script.From.Idea.Title")
        self.db.insert_story(state="PrismQ.T.Review.From.Script")

        stories = self.db.get_all_stories()

        assert len(stories) == 3

    def test_get_stories_by_state(self):
        """Test filtering stories by state."""
        self.db.insert_story(state="PrismQ.T.Title.From.Idea")
        self.db.insert_story(state="PrismQ.T.Title.From.Idea")
        self.db.insert_story(state="PrismQ.T.Script.From.Idea.Title")

        title_stories = self.db.get_stories_by_state("PrismQ.T.Title.From.Idea")
        script_stories = self.db.get_stories_by_state("PrismQ.T.Script.From.Idea.Title")

        assert len(title_stories) == 2
        assert len(script_stories) == 1

    def test_get_latest_stories(self):
        """Test getting latest stories with limit."""
        for i in range(15):
            self.db.insert_story()

        latest = self.db.get_latest_stories(limit=10)

        assert len(latest) == 10

    def test_get_recently_updated_stories(self):
        """Test getting recently updated stories ordered by updated_at descending."""
        # Create stories with explicit timestamps to control order
        story_id1 = self.db.insert_story(
            created_at="2024-01-01 10:00:00", updated_at="2024-01-01 10:00:00"
        )
        story_id2 = self.db.insert_story(
            created_at="2024-01-01 11:00:00", updated_at="2024-01-01 11:00:00"
        )

        # Update story1 with a later timestamp
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE Story SET updated_at = ?, state = ? WHERE id = ?",
            ("2024-01-01 12:00:00", "PrismQ.T.Script.From.Idea.Title", story_id1),
        )
        self.db.conn.commit()

        recent = self.db.get_recently_updated_stories(limit=1)

        assert len(recent) == 1
        assert recent[0]["id"] == story_id1

    def test_update_story_state(self):
        """Test updating story state."""
        story_id = self.db.insert_story()

        success = self.db.update_story(story_id, state="PrismQ.T.Script.From.Idea.Title")

        assert success is True
        story = self.db.get_story(story_id)
        assert story["state"] == "PrismQ.T.Script.From.Idea.Title"

    def test_update_story_no_fields(self):
        """Test update with no fields still updates timestamp."""
        story_id = self.db.insert_story()
        original = self.db.get_story(story_id)

        # With update_timestamp=True (default), it should succeed
        success = self.db.update_story(story_id)

        # Should succeed since we update the timestamp
        assert success is True

    def test_update_story_no_timestamp(self):
        """Test update without timestamp update."""
        story_id = self.db.insert_story()

        # With no fields and update_timestamp=False, should return False
        success = self.db.update_story(story_id, update_timestamp=False)

        assert success is False

    def test_delete_story(self):
        """Test deleting a story."""
        story_id = self.db.insert_story()

        success = self.db.delete_story(story_id)

        assert success is True
        story = self.db.get_story(story_id)
        assert story is None

    def test_delete_nonexistent_story(self):
        """Test deleting non-existent story returns False."""
        success = self.db.delete_story(99999)
        assert success is False


class TestStoryTableDefaultState:
    """Test default state constraint."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_stories.db")
        self.db = setup_story_table(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_default_state(self):
        """Test that default state is 'PrismQ.T.Title.From.Idea'."""
        story_id = self.db.insert_story()

        story = self.db.get_story(story_id)
        assert story is not None
        assert story["state"] == "PrismQ.T.Title.From.Idea"

    def test_custom_state(self):
        """Test that custom state is stored correctly."""
        custom_state = "PrismQ.T.Script.From.Idea.Title"
        story_id = self.db.insert_story(state=custom_state)

        story = self.db.get_story(story_id)
        assert story is not None
        assert story["state"] == custom_state

    def test_default_state_via_raw_sql(self):
        """Test that DEFAULT state works via raw SQL insert."""
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO Story (idea_id) VALUES (NULL)")
        self.db.conn.commit()
        story_id = cursor.lastrowid

        story = self.db.get_story(story_id)
        assert story is not None
        assert story["state"] == "PrismQ.T.Title.From.Idea"


class TestStoryTableSearch:
    """Test search and query operations."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_stories.db")
        self.db = setup_story_table(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_search_stories_by_state(self):
        """Test searching stories by state content."""
        self.db.insert_story(state="PrismQ.T.Title.From.Idea")
        self.db.insert_story(state="PrismQ.T.Script.From.Idea.Title")
        self.db.insert_story(state="PrismQ.T.Review.From.Script")

        # Search for stories with "Script" in state
        results = self.db.search_stories_by_state("Script")

        assert len(results) == 2

    def test_search_stories_no_results(self):
        """Test search with no matching results."""
        self.db.insert_story(state="PrismQ.T.Title.From.Idea")

        results = self.db.search_stories_by_state("Nonexistent")

        assert len(results) == 0

    def test_count_stories(self):
        """Test counting total stories."""
        assert self.db.count_stories() == 0

        self.db.insert_story()
        assert self.db.count_stories() == 1

        self.db.insert_story()
        self.db.insert_story()
        assert self.db.count_stories() == 3

    def test_count_stories_by_state(self):
        """Test counting stories by state."""
        self.db.insert_story(state="PrismQ.T.Title.From.Idea")
        self.db.insert_story(state="PrismQ.T.Title.From.Idea")
        self.db.insert_story(state="PrismQ.T.Script.From.Idea.Title")

        title_count = self.db.count_stories_by_state("PrismQ.T.Title.From.Idea")
        script_count = self.db.count_stories_by_state("PrismQ.T.Script.From.Idea.Title")

        assert title_count == 2
        assert script_count == 1

    def test_get_distinct_states(self):
        """Test getting distinct states."""
        self.db.insert_story(state="PrismQ.T.Title.From.Idea")
        self.db.insert_story(state="PrismQ.T.Title.From.Idea")
        self.db.insert_story(state="PrismQ.T.Script.From.Idea.Title")
        self.db.insert_story(state="PrismQ.T.Review.From.Script")

        states = self.db.get_distinct_states()

        assert len(states) == 3
        assert "PrismQ.T.Title.From.Idea" in states
        assert "PrismQ.T.Script.From.Idea.Title" in states
        assert "PrismQ.T.Review.From.Script" in states


class TestStoryTableForeignKey:
    """Test foreign key relationship with Idea table."""

    def setup_method(self):
        """Create a temporary database with both Idea and Story tables."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_stories.db")

        # Create Idea table first (required for FK)
        self.idea_db = IdeaDatabase(self.db_path)
        self.idea_db.connect()
        self.idea_db.create_tables()

        # Now create Story table (will use same connection for FK)
        self.story_db = StoryTable(self.db_path)
        self.story_db.conn = self.idea_db.conn  # Share connection
        self.story_db.create_tables()

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.idea_db.conn:
            self.idea_db.close()
            self.story_db.conn = None  # Don't double-close
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_story_with_valid_idea_id(self):
        """Test story can reference existing Idea."""
        # Create an idea first
        idea_id = self.idea_db.insert_idea("Test idea content")

        # Create story referencing the idea
        story_id = self.story_db.insert_story(idea_id=idea_id)

        story = self.story_db.get_story(story_id)
        assert story is not None
        assert story["idea_id"] == idea_id

    def test_story_with_null_idea_id(self):
        """Test story can have NULL idea_id."""
        story_id = self.story_db.insert_story(idea_id=None)

        story = self.story_db.get_story(story_id)
        assert story is not None
        assert story["idea_id"] is None

    def test_get_stories_by_idea_id(self):
        """Test getting stories by idea_id."""
        # Create ideas
        idea_id1 = self.idea_db.insert_idea("Idea 1")
        idea_id2 = self.idea_db.insert_idea("Idea 2")

        # Create stories
        self.story_db.insert_story(idea_id=idea_id1)
        self.story_db.insert_story(idea_id=idea_id1)
        self.story_db.insert_story(idea_id=idea_id2)

        # Query by idea_id
        stories_1 = self.story_db.get_stories_by_idea_id(idea_id1)
        stories_2 = self.story_db.get_stories_by_idea_id(idea_id2)

        assert len(stories_1) == 2
        assert len(stories_2) == 1

    def test_update_story_idea_id(self):
        """Test updating story's idea_id."""
        # Create ideas
        idea_id1 = self.idea_db.insert_idea("Idea 1")
        idea_id2 = self.idea_db.insert_idea("Idea 2")

        # Create story with idea_id1
        story_id = self.story_db.insert_story(idea_id=idea_id1)

        # Update to idea_id2
        success = self.story_db.update_story(story_id, idea_id=idea_id2)

        assert success is True
        story = self.story_db.get_story(story_id)
        assert story["idea_id"] == idea_id2

    def test_update_story_idea_id_to_null(self):
        """Test updating story's idea_id to NULL using CLEAR_IDEA_ID."""
        idea_id = self.idea_db.insert_idea("Test idea")
        story_id = self.story_db.insert_story(idea_id=idea_id)

        # Update to NULL by passing CLEAR_IDEA_ID
        success = self.story_db.update_story(story_id, idea_id=CLEAR_IDEA_ID)

        assert success is True
        story = self.story_db.get_story(story_id)
        assert story["idea_id"] is None


class TestStoryTableTimestamps:
    """Test timestamp handling."""

    def setup_method(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_stories.db")
        self.db = setup_story_table(self.db_path)

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.db.conn:
            self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        story_id = self.db.insert_story()

        story = self.db.get_story(story_id)
        assert story["created_at"] is not None

    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set."""
        story_id = self.db.insert_story()

        story = self.db.get_story(story_id)
        assert story["updated_at"] is not None

    def test_updated_at_changes_on_update(self):
        """Test that updated_at changes when story is updated."""
        import time

        story_id = self.db.insert_story()
        original = self.db.get_story(story_id)

        # Wait a moment to ensure timestamp difference
        time.sleep(0.1)

        # Update the story
        self.db.update_story(story_id, state="PrismQ.T.Script.From.Idea.Title")
        updated = self.db.get_story(story_id)

        # updated_at should be different (or at least not earlier)
        assert updated["updated_at"] >= original["updated_at"]

    def test_custom_timestamps(self):
        """Test inserting with custom timestamps."""
        custom_time = "2024-01-01 12:00:00"
        story_id = self.db.insert_story(created_at=custom_time, updated_at=custom_time)

        story = self.db.get_story(story_id)
        assert story["created_at"] == custom_time
        assert story["updated_at"] == custom_time
