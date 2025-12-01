"""Tests for Story model and StoryScriptService.

These tests verify:
1. Story model functionality
2. StoryRepository database operations
3. StoryScriptService script generation workflow
"""

import json
import pytest
import sqlite3
from datetime import datetime

from T.Database.models.story import Story
from T.Database.models.script import Script
from T.Database.models.title import Title
from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.Database.repositories.title_repository import TitleRepository
from T.Script.From.Idea.Title.src.story_script_service import (
    StoryScriptService,
    ScriptGenerationResult,
    process_all_pending_stories
)
from T.State.constants.state_names import StateNames

# Import Idea for test data
import sys
from pathlib import Path
_t_module_dir = Path(__file__).parent.parent / 'T' / 'Idea' / 'Model' / 'src'
sys.path.insert(0, str(_t_module_dir))
from idea import Idea, ContentGenre


@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database with all required tables."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create tables in correct order (dependencies first)
    # Title table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Title (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(story_id, version)
        )
    """)
    
    # Script table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Script (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(story_id, version)
        )
    """)
    
    # Story table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_json TEXT NULL,
            title_id INTEGER NULL,
            script_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (title_id) REFERENCES Title(id),
            FOREIGN KEY (script_id) REFERENCES Script(id)
        )
    """)
    
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def sample_idea():
    """Create a sample Idea for testing."""
    return Idea(
        title="The Mystery of the Abandoned House",
        concept="A girl discovers a time-loop in an abandoned house",
        premise="When Maya explores an abandoned house, she discovers she's trapped in a time loop, reliving the same terrifying night.",
        hook="Every night at midnight, she returns to the same moment.",
        synopsis="Maya enters an abandoned house looking for her lost cat. Inside, she finds herself trapped in a repeating nightmare.",
        genre=ContentGenre.HORROR,
        target_audience="Horror enthusiasts aged 14-29"
    )


class TestStoryModel:
    """Tests for Story model functionality."""
    
    def test_create_story(self):
        """Test creating a Story instance."""
        story = Story(
            idea_json='{"title": "Test", "concept": "Test concept"}',
            state='IDEA'
        )
        
        assert story.idea_json is not None
        assert story.state == 'IDEA'
        assert story.title_id is None
        assert story.script_id is None
        assert story.id is None  # Not persisted yet
    
    def test_has_idea(self):
        """Test has_idea() method."""
        story_with_idea = Story(idea_json='{"title": "Test"}')
        story_without_idea = Story()
        
        assert story_with_idea.has_idea() is True
        assert story_without_idea.has_idea() is False
    
    def test_has_title(self):
        """Test has_title() method."""
        story_with_title = Story(title_id=1)
        story_without_title = Story()
        
        assert story_with_title.has_title() is True
        assert story_without_title.has_title() is False
    
    def test_has_script(self):
        """Test has_script() method."""
        story_with_script = Story(script_id=1)
        story_without_script = Story()
        
        assert story_with_script.has_script() is True
        assert story_without_script.has_script() is False
    
    def test_needs_script(self):
        """Test needs_script() method."""
        # Story that needs script (has idea and title, no script)
        story_needs_script = Story(
            idea_json='{"title": "Test"}',
            title_id=1,
            script_id=None
        )
        
        # Story that doesn't need script (already has script)
        story_has_script = Story(
            idea_json='{"title": "Test"}',
            title_id=1,
            script_id=1
        )
        
        # Story that can't have script (no idea)
        story_no_idea = Story(title_id=1)
        
        # Story that can't have script (no title)
        story_no_title = Story(idea_json='{"title": "Test"}')
        
        assert story_needs_script.needs_script() is True
        assert story_has_script.needs_script() is False
        assert story_no_idea.needs_script() is False
        assert story_no_title.needs_script() is False
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        story = Story(
            idea_json='{"title": "Test"}',
            title_id=1,
            state='TITLE'
        )
        
        story_dict = story.to_dict()
        restored = Story.from_dict(story_dict)
        
        assert restored.idea_json == story.idea_json
        assert restored.title_id == story.title_id
        assert restored.state == story.state
    
    def test_update_state(self):
        """Test updating story state."""
        story = Story(state='CREATED')
        old_updated_at = story.updated_at
        
        story.update_state('IDEA')
        
        assert story.state == 'IDEA'
        assert story.updated_at >= old_updated_at
    
    def test_set_script(self):
        """Test setting script reference."""
        story = Story(state='TITLE')
        
        story.set_script(5)
        
        assert story.script_id == 5
        assert story.state == 'SCRIPT'


class TestStoryRepository:
    """Tests for StoryRepository database operations."""
    
    def test_insert_and_find(self, db_connection):
        """Test inserting and finding a story."""
        repo = StoryRepository(db_connection)
        
        story = Story(
            idea_json='{"title": "Test"}',
            state='IDEA'
        )
        
        saved = repo.insert(story)
        
        assert saved.id is not None
        
        found = repo.find_by_id(saved.id)
        assert found is not None
        assert found.idea_json == '{"title": "Test"}'
        assert found.state == 'IDEA'
    
    def test_update(self, db_connection):
        """Test updating a story."""
        repo = StoryRepository(db_connection)
        
        story = repo.insert(Story(state='CREATED'))
        story.state = 'IDEA'
        story.idea_json = '{"title": "Updated"}'
        
        updated = repo.update(story)
        
        found = repo.find_by_id(updated.id)
        assert found.state == 'IDEA'
        assert found.idea_json == '{"title": "Updated"}'
    
    def test_find_needing_script(self, db_connection):
        """Test finding stories that need scripts."""
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create a title first
        title = Title(story_id=1, version=0, text="Test Title")
        saved_title = title_repo.insert(title)
        
        # Create stories in different states
        # Story that needs script
        story1 = story_repo.insert(Story(
            idea_json='{"title": "Test1"}',
            title_id=saved_title.id,
            state='TITLE'
        ))
        
        # Story that already has script
        story2 = story_repo.insert(Story(
            idea_json='{"title": "Test2"}',
            title_id=saved_title.id,
            script_id=1,  # Has script
            state='SCRIPT'
        ))
        
        # Story without title
        story3 = story_repo.insert(Story(
            idea_json='{"title": "Test3"}',
            state='IDEA'
        ))
        
        # Story without idea
        story4 = story_repo.insert(Story(
            title_id=saved_title.id,
            state='TITLE'
        ))
        
        needing = story_repo.find_needing_script()
        
        assert len(needing) == 1
        assert needing[0].id == story1.id
    
    def test_count_needing_script(self, db_connection):
        """Test counting stories that need scripts."""
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create titles
        title = title_repo.insert(Title(story_id=1, version=0, text="Title"))
        
        # Create 3 stories that need scripts
        for i in range(3):
            story_repo.insert(Story(
                idea_json=f'{{"title": "Test{i}"}}',
                title_id=title.id,
                state='TITLE'
            ))
        
        # Create 1 story that has script
        story_repo.insert(Story(
            idea_json='{"title": "HasScript"}',
            title_id=title.id,
            script_id=1,
            state='SCRIPT'
        ))
        
        count = story_repo.count_needing_script()
        assert count == 3
    
    def test_find_by_state_ordered_by_created(self, db_connection):
        """Test finding stories by state ordered by creation date."""
        import time
        story_repo = StoryRepository(db_connection)
        
        # Create stories with different creation times
        # Using different created_at values to ensure ordering
        from datetime import datetime, timedelta
        
        base_time = datetime.now()
        
        # Create story 1 (oldest)
        story1 = Story(
            idea_json='{"title": "First"}',
            state='PrismQ.T.Script.From.Idea.Title',
            created_at=base_time - timedelta(hours=2)
        )
        story_repo.insert(story1)
        
        # Create story 2 (newest)
        story2 = Story(
            idea_json='{"title": "Second"}',
            state='PrismQ.T.Script.From.Idea.Title',
            created_at=base_time
        )
        story_repo.insert(story2)
        
        # Create story 3 (middle)
        story3 = Story(
            idea_json='{"title": "Third"}',
            state='PrismQ.T.Script.From.Idea.Title',
            created_at=base_time - timedelta(hours=1)
        )
        story_repo.insert(story3)
        
        # Create story with different state (should not be included)
        story4 = Story(
            idea_json='{"title": "Different State"}',
            state='CREATED',
            created_at=base_time - timedelta(hours=3)
        )
        story_repo.insert(story4)
        
        # Test ascending order (oldest first)
        stories_asc = story_repo.find_by_state_ordered_by_created(
            'PrismQ.T.Script.From.Idea.Title',
            ascending=True
        )
        
        assert len(stories_asc) == 3
        assert stories_asc[0].id == story1.id  # Oldest
        assert stories_asc[1].id == story3.id  # Middle
        assert stories_asc[2].id == story2.id  # Newest
        
        # Test descending order (newest first)
        stories_desc = story_repo.find_by_state_ordered_by_created(
            'PrismQ.T.Script.From.Idea.Title',
            ascending=False
        )
        
        assert len(stories_desc) == 3
        assert stories_desc[0].id == story2.id  # Newest
        assert stories_desc[1].id == story3.id  # Middle
        assert stories_desc[2].id == story1.id  # Oldest


class TestStoryScriptService:
    """Tests for StoryScriptService."""
    
    def test_count_stories_needing_scripts(self, db_connection):
        """Test counting stories needing scripts."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Initially no stories
        assert service.count_stories_needing_scripts() == 0
        
        # Add a story with idea and title
        title = title_repo.insert(Title(story_id=1, version=0, text="Title"))
        story_repo.insert(Story(
            idea_json='{"title": "Test", "concept": "Test"}',
            title_id=title.id,
            state='TITLE'
        ))
        
        assert service.count_stories_needing_scripts() == 1
    
    def test_generate_script_for_story(self, db_connection, sample_idea):
        """Test generating a script for a single story."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create a story with idea and title
        story = story_repo.insert(Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state='IDEA'
        ))
        
        title = title_repo.insert(Title(
            story_id=story.id,
            version=0,
            text="The Mystery of the Abandoned House"
        ))
        
        # Update story with title reference
        story.title_id = title.id
        story.state = 'TITLE'
        story_repo.update(story)
        
        # Generate script
        result = service.generate_script_for_story(story)
        
        assert result.success is True
        assert result.script_id is not None
        assert result.script_v1 is not None
        assert result.error is None
        
        # Verify story was updated
        updated_story = story_repo.find_by_id(story.id)
        assert updated_story.script_id == result.script_id
        assert updated_story.state == 'SCRIPT'
    
    def test_generate_script_missing_title(self, db_connection, sample_idea):
        """Test that script generation fails when title is missing."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        # Create story without title
        story = story_repo.insert(Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state='IDEA'
        ))
        
        result = service.generate_script_for_story(story)
        
        assert result.success is False
        assert result.error is not None
        assert "does not need script" in result.error
    
    def test_process_stories_needing_scripts(self, db_connection, sample_idea):
        """Test processing multiple stories."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create multiple stories with ideas and titles
        for i in range(3):
            story = story_repo.insert(Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state='IDEA'
            ))
            
            title = title_repo.insert(Title(
                story_id=story.id,
                version=0,
                text=f"Test Title {i}"
            ))
            
            story.title_id = title.id
            story.state = 'TITLE'
            story_repo.update(story)
        
        # Process all
        results = service.process_stories_needing_scripts()
        
        assert len(results) == 3
        assert all(r.success for r in results)
        
        # Verify summary
        summary = service.get_processing_summary(results)
        assert summary['total_processed'] == 3
        assert summary['successful'] == 3
        assert summary['failed'] == 0
        assert summary['success_rate'] == 1.0
    
    def test_process_with_limit(self, db_connection, sample_idea):
        """Test processing with a limit."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create 5 stories
        for i in range(5):
            story = story_repo.insert(Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state='IDEA'
            ))
            title = title_repo.insert(Title(
                story_id=story.id,
                version=0,
                text=f"Title {i}"
            ))
            story.title_id = title.id
            story.state = 'TITLE'
            story_repo.update(story)
        
        # Process only 2
        results = service.process_stories_needing_scripts(limit=2)
        
        assert len(results) == 2
        
        # Verify only 2 were processed
        remaining = service.count_stories_needing_scripts()
        assert remaining == 3


class TestProcessAllPendingStories:
    """Tests for the convenience function."""
    
    def test_process_all_pending_stories(self, db_connection, sample_idea):
        """Test the convenience function."""
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create stories
        for i in range(2):
            story = story_repo.insert(Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state='IDEA'
            ))
            title = title_repo.insert(Title(
                story_id=story.id,
                version=0,
                text=f"Title {i}"
            ))
            story.title_id = title.id
            story.state = 'TITLE'
            story_repo.update(story)
        
        # Use convenience function
        summary = process_all_pending_stories(db_connection)
        
        assert summary['total_processed'] == 2
        assert summary['successful'] == 2
        assert summary['success_rate'] == 1.0


class TestStoryScriptServiceStateBased:
    """Tests for the state-based workflow (primary workflow).
    
    Tests the new methods:
    - get_oldest_story_by_state()
    - count_stories_by_state()
    - process_oldest_story()
    """
    
    def test_get_oldest_story_by_state_no_stories(self, db_connection):
        """Test get_oldest_story_by_state when no stories exist."""
        service = StoryScriptService(db_connection)
        
        result = service.get_oldest_story_by_state()
        
        assert result is None
    
    def test_get_oldest_story_by_state_returns_oldest(self, db_connection, sample_idea):
        """Test that get_oldest_story_by_state returns the oldest story."""
        from datetime import timedelta
        
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        base_time = datetime.now()
        
        # Create oldest story (2 hours ago)
        story1 = Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=StateNames.SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time - timedelta(hours=2)
        )
        story_repo.insert(story1)
        title1 = title_repo.insert(Title(story_id=story1.id, version=0, text="Title 1"))
        story1.title_id = title1.id
        story_repo.update(story1)
        
        # Create newer story (1 hour ago)
        story2 = Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=StateNames.SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time - timedelta(hours=1)
        )
        story_repo.insert(story2)
        title2 = title_repo.insert(Title(story_id=story2.id, version=0, text="Title 2"))
        story2.title_id = title2.id
        story_repo.update(story2)
        
        # Create newest story
        story3 = Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=StateNames.SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time
        )
        story_repo.insert(story3)
        title3 = title_repo.insert(Title(story_id=story3.id, version=0, text="Title 3"))
        story3.title_id = title3.id
        story_repo.update(story3)
        
        # Should return the oldest
        result = service.get_oldest_story_by_state()
        
        assert result is not None
        assert result.id == story1.id
    
    def test_get_oldest_story_by_state_filters_by_state(self, db_connection, sample_idea):
        """Test that get_oldest_story_by_state only returns stories with correct state."""
        from datetime import timedelta
        
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        base_time = datetime.now()
        
        # Create story with wrong state (oldest)
        story1 = Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state='CREATED',  # Wrong state
            created_at=base_time - timedelta(hours=2)
        )
        story_repo.insert(story1)
        
        # Create story with correct state (newer)
        story2 = Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=StateNames.SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time - timedelta(hours=1)
        )
        story_repo.insert(story2)
        
        result = service.get_oldest_story_by_state()
        
        assert result is not None
        assert result.id == story2.id
        assert result.state == StateNames.SCRIPT_FROM_IDEA_TITLE
    
    def test_count_stories_by_state(self, db_connection, sample_idea):
        """Test counting stories with the correct state."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        # Initially should be 0
        assert service.count_stories_by_state() == 0
        
        # Add stories with correct state
        for i in range(3):
            story = Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state=StateNames.SCRIPT_FROM_IDEA_TITLE
            )
            story_repo.insert(story)
        
        # Add story with different state
        story_other = Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state='CREATED'
        )
        story_repo.insert(story_other)
        
        assert service.count_stories_by_state() == 3
    
    def test_process_oldest_story_no_stories(self, db_connection):
        """Test process_oldest_story returns None when no stories exist."""
        service = StoryScriptService(db_connection)
        
        result = service.process_oldest_story()
        
        assert result is None
    
    def test_process_oldest_story_success(self, db_connection, sample_idea):
        """Test successful processing of the oldest story."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create story with correct state
        story = Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=StateNames.SCRIPT_FROM_IDEA_TITLE
        )
        story_repo.insert(story)
        
        title = title_repo.insert(Title(
            story_id=story.id,
            version=0,
            text="The Mystery of the Abandoned House"
        ))
        story.title_id = title.id
        story_repo.update(story)
        
        # Process
        result = service.process_oldest_story()
        
        assert result is not None
        assert result.success is True
        assert result.script_id is not None
        assert result.script_v1 is not None
        assert result.error is None
        
        # Verify state changed
        updated_story = story_repo.find_by_id(story.id)
        assert updated_story.state == StateNames.REVIEW_TITLE_FROM_SCRIPT
        assert updated_story.script_id == result.script_id
    
    def test_process_oldest_story_missing_idea(self, db_connection):
        """Test process_oldest_story fails when story has no idea."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        # Create story without idea_json
        story = Story(
            state=StateNames.SCRIPT_FROM_IDEA_TITLE
        )
        story_repo.insert(story)
        
        result = service.process_oldest_story()
        
        assert result is not None
        assert result.success is False
        assert "idea_json" in result.error
    
    def test_process_oldest_story_missing_title(self, db_connection, sample_idea):
        """Test process_oldest_story fails when story has no title."""
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        # Create story without title_id
        story = Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=StateNames.SCRIPT_FROM_IDEA_TITLE
        )
        story_repo.insert(story)
        
        result = service.process_oldest_story()
        
        assert result is not None
        assert result.success is False
        assert "title_id" in result.error
    
    def test_process_oldest_story_processes_in_order(self, db_connection, sample_idea):
        """Test that process_oldest_story processes stories in creation order."""
        from datetime import timedelta
        
        service = StoryScriptService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        base_time = datetime.now()
        
        # Create multiple stories in different orders
        stories = []
        for i, offset in enumerate([2, 1, 3]):  # Creating out of order
            story = Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state=StateNames.SCRIPT_FROM_IDEA_TITLE,
                created_at=base_time - timedelta(hours=offset)
            )
            story_repo.insert(story)
            title = title_repo.insert(Title(
                story_id=story.id,
                version=0,
                text=f"Title {i}"
            ))
            story.title_id = title.id
            story_repo.update(story)
            stories.append(story)
        
        # Process first - should be the oldest (3 hours ago)
        result1 = service.process_oldest_story()
        assert result1.success is True
        
        # Process second - should be 2 hours ago
        result2 = service.process_oldest_story()
        assert result2.success is True
        
        # Process third - should be 1 hour ago
        result3 = service.process_oldest_story()
        assert result3.success is True
        
        # No more stories to process
        result4 = service.process_oldest_story()
        assert result4 is None
        
        # Verify all states changed
        for story in stories:
            updated = story_repo.find_by_id(story.id)
            assert updated.state == StateNames.REVIEW_TITLE_FROM_SCRIPT
