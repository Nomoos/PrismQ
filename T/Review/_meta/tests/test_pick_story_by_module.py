"""Tests for pick_story_by_module function in PrismQ.T.Review.

These tests verify the consolidated story picking function that selects
Stories based on their state matching a module name.
"""

import sqlite3
import pytest
from datetime import datetime, timedelta

from T.Review import pick_story_by_module, count_stories_by_module
from Model.Database.models.story import Story
from Model.Database.repositories.story_repository import StoryRepository


@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database with Story table."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create Story table
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT,
            idea_json TEXT,
            title_id INTEGER,
            script_id INTEGER,
            state TEXT NOT NULL DEFAULT 'PrismQ.T.Idea.Creation',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)
    conn.commit()
    
    yield conn
    conn.close()


@pytest.fixture
def story_repository(db_connection):
    """Create a StoryRepository instance."""
    return StoryRepository(db_connection)


class TestPickStoryByModule:
    """Tests for pick_story_by_module function."""
    
    def test_returns_none_when_no_stories(self, db_connection):
        """Test that None is returned when no stories exist."""
        story = pick_story_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Readability"
        )
        assert story is None
    
    def test_returns_none_when_no_stories_in_state(self, db_connection, story_repository):
        """Test that None is returned when no stories match the module state."""
        # Create a story in a different state
        story = Story(
            idea_json='{"title": "Test"}',
            state="PrismQ.T.Review.Script.Tone"
        )
        story_repository.insert(story)
        
        # Try to pick a story for a different module
        result = pick_story_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Readability"
        )
        assert result is None
    
    def test_returns_story_matching_module_state(self, db_connection, story_repository):
        """Test that a story matching the module state is returned."""
        # Create a story in the target state
        story = Story(
            idea_json='{"title": "Test Story"}',
            state="PrismQ.T.Review.Script.Readability"
        )
        saved = story_repository.insert(story)
        
        # Pick the story
        result = pick_story_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Readability"
        )
        
        assert result is not None
        assert result.id == saved.id
        assert result.state == "PrismQ.T.Review.Script.Readability"
    
    def test_returns_oldest_story_when_multiple(self, db_connection, story_repository):
        """Test that the oldest story is returned when multiple match."""
        base_time = datetime.now()
        
        # Create older story first
        older_story = Story(
            idea_json='{"title": "Older Story"}',
            state="PrismQ.T.Review.Script.Readability",
            created_at=base_time - timedelta(hours=2)
        )
        saved_older = story_repository.insert(older_story)
        
        # Create newer story
        newer_story = Story(
            idea_json='{"title": "Newer Story"}',
            state="PrismQ.T.Review.Script.Readability",
            created_at=base_time - timedelta(hours=1)
        )
        story_repository.insert(newer_story)
        
        # Pick should return the older story
        result = pick_story_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Readability"
        )
        
        assert result is not None
        assert result.id == saved_older.id
    
    def test_accepts_custom_repository(self, db_connection, story_repository):
        """Test that a custom repository can be provided."""
        # Create a story
        story = Story(
            idea_json='{"title": "Test"}',
            state="PrismQ.T.Review.Script.Tone"
        )
        story_repository.insert(story)
        
        # Pick using custom repository
        result = pick_story_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Tone",
            story_repository=story_repository
        )
        
        assert result is not None
        assert result.state == "PrismQ.T.Review.Script.Tone"
    
    def test_works_with_various_module_names(self, db_connection, story_repository):
        """Test picking stories for various module names."""
        module_names = [
            "PrismQ.T.Review.Script.Grammar",
            "PrismQ.T.Review.Script.Tone",
            "PrismQ.T.Review.Script.Content",
            "PrismQ.T.Review.Script.Consistency",
            "PrismQ.T.Review.Script.Editing",
            "PrismQ.T.Review.Script.Readability",
        ]
        
        # Create a story for each module state
        for module_name in module_names:
            story = Story(
                idea_json=f'{{"title": "Story for {module_name}"}}',
                state=module_name
            )
            story_repository.insert(story)
        
        # Verify each module can pick its story
        for module_name in module_names:
            result = pick_story_by_module(
                connection=db_connection,
                module_name=module_name
            )
            assert result is not None
            assert result.state == module_name


class TestCountStoriesByModule:
    """Tests for count_stories_by_module function."""
    
    def test_returns_zero_when_no_stories(self, db_connection):
        """Test that 0 is returned when no stories exist."""
        count = count_stories_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Readability"
        )
        assert count == 0
    
    def test_returns_zero_when_no_stories_in_state(self, db_connection, story_repository):
        """Test that 0 is returned when no stories match the module state."""
        # Create a story in a different state
        story = Story(
            idea_json='{"title": "Test"}',
            state="PrismQ.T.Review.Script.Tone"
        )
        story_repository.insert(story)
        
        count = count_stories_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Readability"
        )
        assert count == 0
    
    def test_counts_stories_correctly(self, db_connection, story_repository):
        """Test that stories are counted correctly."""
        # Create multiple stories in the target state
        for i in range(5):
            story = Story(
                idea_json=f'{{"title": "Story {i}"}}',
                state="PrismQ.T.Review.Script.Editing"
            )
            story_repository.insert(story)
        
        count = count_stories_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Editing"
        )
        assert count == 5
    
    def test_counts_only_matching_state(self, db_connection, story_repository):
        """Test that only stories with matching state are counted."""
        # Create stories in different states
        for state in ["PrismQ.T.Review.Script.Tone", "PrismQ.T.Review.Script.Editing"]:
            for i in range(3):
                story = Story(
                    idea_json=f'{{"title": "Story {state} {i}"}}',
                    state=state
                )
                story_repository.insert(story)
        
        # Count for one specific state
        count = count_stories_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Tone"
        )
        assert count == 3
    
    def test_accepts_custom_repository(self, db_connection, story_repository):
        """Test that a custom repository can be provided."""
        story = Story(
            idea_json='{"title": "Test"}',
            state="PrismQ.T.Review.Script.Grammar"
        )
        story_repository.insert(story)
        
        count = count_stories_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Grammar",
            story_repository=story_repository
        )
        assert count == 1


class TestIntegration:
    """Integration tests for story picking workflow."""
    
    def test_pick_and_process_workflow(self, db_connection, story_repository):
        """Test a typical pick-and-process workflow."""
        # Create stories to process
        for i in range(3):
            story = Story(
                idea_json=f'{{"title": "Story {i}"}}',
                state="PrismQ.T.Review.Script.Readability"
            )
            story_repository.insert(story)
        
        # Verify initial count
        initial_count = count_stories_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Readability"
        )
        assert initial_count == 3
        
        # Pick and "process" each story
        processed = []
        while True:
            story = pick_story_by_module(
                connection=db_connection,
                module_name="PrismQ.T.Review.Script.Readability"
            )
            if story is None:
                break
            
            # Update state to simulate processing
            story.state = "PrismQ.T.Review.Title.Readability"
            story_repository.update(story)
            processed.append(story.id)
        
        assert len(processed) == 3
        
        # Verify no more stories in original state
        final_count = count_stories_by_module(
            connection=db_connection,
            module_name="PrismQ.T.Review.Script.Readability"
        )
        assert final_count == 0
