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


# =============================================================================
# Tests for ScriptFromIdeaTitleService (PrismQ.T.Script.From.Idea.Title)
# =============================================================================

from T.Script.From.Idea.Title.src.story_script_service import (
    ScriptFromIdeaTitleService,
    StateBasedScriptResult,
    process_oldest_from_idea_title,
    STATE_SCRIPT_FROM_IDEA_TITLE,
    STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA
)


class TestStoryRepositoryFindOldestByState:
    """Tests for the find_oldest_by_state method."""
    
    def test_find_oldest_by_state_returns_oldest(self, db_connection):
        """Test that find_oldest_by_state returns the oldest story."""
        from datetime import timedelta
        story_repo = StoryRepository(db_connection)
        
        base_time = datetime.now()
        
        # Create stories with different creation times
        story_oldest = Story(
            idea_json='{"title": "Oldest"}',
            state=STATE_SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time - timedelta(hours=3)
        )
        story_repo.insert(story_oldest)
        
        story_middle = Story(
            idea_json='{"title": "Middle"}',
            state=STATE_SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time - timedelta(hours=1)
        )
        story_repo.insert(story_middle)
        
        story_newest = Story(
            idea_json='{"title": "Newest"}',
            state=STATE_SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time
        )
        story_repo.insert(story_newest)
        
        # Find oldest
        oldest = story_repo.find_oldest_by_state(STATE_SCRIPT_FROM_IDEA_TITLE)
        
        assert oldest is not None
        assert oldest.id == story_oldest.id
        assert oldest.idea_json == '{"title": "Oldest"}'
    
    def test_find_oldest_by_state_returns_none_when_empty(self, db_connection):
        """Test that find_oldest_by_state returns None when no stories match."""
        story_repo = StoryRepository(db_connection)
        
        # Create story with different state
        story_repo.insert(Story(
            idea_json='{"title": "Different State"}',
            state='DIFFERENT_STATE'
        ))
        
        # Find oldest in target state
        oldest = story_repo.find_oldest_by_state(STATE_SCRIPT_FROM_IDEA_TITLE)
        
        assert oldest is None
    
    def test_find_oldest_by_state_ignores_other_states(self, db_connection):
        """Test that find_oldest_by_state only considers the specified state."""
        from datetime import timedelta
        story_repo = StoryRepository(db_connection)
        
        base_time = datetime.now()
        
        # Create very old story in different state
        story_different = Story(
            idea_json='{"title": "Very Old Different State"}',
            state='DIFFERENT_STATE',
            created_at=base_time - timedelta(hours=10)
        )
        story_repo.insert(story_different)
        
        # Create newer story in target state
        story_target = Story(
            idea_json='{"title": "Target State"}',
            state=STATE_SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time
        )
        story_repo.insert(story_target)
        
        # Find oldest in target state
        oldest = story_repo.find_oldest_by_state(STATE_SCRIPT_FROM_IDEA_TITLE)
        
        assert oldest is not None
        assert oldest.id == story_target.id


class TestScriptFromIdeaTitleService:
    """Tests for ScriptFromIdeaTitleService."""
    
    def test_count_pending(self, db_connection, sample_idea):
        """Test counting pending stories."""
        service = ScriptFromIdeaTitleService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Initially no pending stories
        assert service.count_pending() == 0
        
        # Add stories in the target state
        for i in range(3):
            story = story_repo.insert(Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state=STATE_SCRIPT_FROM_IDEA_TITLE
            ))
            title = title_repo.insert(Title(
                story_id=story.id,
                version=0,
                text=f"Test Title {i}"
            ))
            story.title_id = title.id
            story_repo.update(story)
        
        assert service.count_pending() == 3
    
    def test_get_oldest_story(self, db_connection, sample_idea):
        """Test getting the oldest pending story."""
        from datetime import timedelta
        service = ScriptFromIdeaTitleService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        base_time = datetime.now()
        
        # Create stories with different creation times
        story1 = story_repo.insert(Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=STATE_SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time - timedelta(hours=2)
        ))
        title1 = title_repo.insert(Title(
            story_id=story1.id,
            version=0,
            text="First Title"
        ))
        story1.title_id = title1.id
        story_repo.update(story1)
        
        story2 = story_repo.insert(Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=STATE_SCRIPT_FROM_IDEA_TITLE,
            created_at=base_time
        ))
        title2 = title_repo.insert(Title(
            story_id=story2.id,
            version=0,
            text="Second Title"
        ))
        story2.title_id = title2.id
        story_repo.update(story2)
        
        # Get oldest
        oldest = service.get_oldest_story()
        
        assert oldest is not None
        assert oldest.id == story1.id
    
    def test_process_oldest_story_success(self, db_connection, sample_idea):
        """Test successfully processing the oldest story."""
        service = ScriptFromIdeaTitleService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create a story in the target state
        story = story_repo.insert(Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=STATE_SCRIPT_FROM_IDEA_TITLE
        ))
        title = title_repo.insert(Title(
            story_id=story.id,
            version=0,
            text="The Mystery of the Abandoned House"
        ))
        story.title_id = title.id
        story_repo.update(story)
        
        # Process the story
        result = service.process_oldest_story()
        
        assert result.success is True
        assert result.story_id == story.id
        assert result.script_id is not None
        assert result.previous_state == STATE_SCRIPT_FROM_IDEA_TITLE
        assert result.new_state == STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA
        assert result.script_v1 is not None
        assert result.error is None
        
        # Verify story state was updated
        updated_story = story_repo.find_by_id(story.id)
        assert updated_story.state == STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA
        assert updated_story.script_id == result.script_id
    
    def test_process_oldest_story_no_stories(self, db_connection):
        """Test processing when no stories are pending."""
        service = ScriptFromIdeaTitleService(db_connection)
        
        result = service.process_oldest_story()
        
        assert result.success is False
        assert result.story_id is None
        assert result.error is not None
        assert "No stories found" in result.error
    
    def test_process_oldest_story_missing_title(self, db_connection, sample_idea):
        """Test processing a story without a title."""
        service = ScriptFromIdeaTitleService(db_connection)
        story_repo = StoryRepository(db_connection)
        
        # Create a story without title_id
        story = story_repo.insert(Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=STATE_SCRIPT_FROM_IDEA_TITLE
        ))
        
        result = service.process_oldest_story()
        
        assert result.success is False
        assert result.story_id == story.id
        assert result.error is not None
        assert "no title_id" in result.error
    
    def test_process_oldest_story_missing_idea(self, db_connection):
        """Test processing a story without idea_json."""
        service = ScriptFromIdeaTitleService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create a story without idea_json
        story = story_repo.insert(Story(
            idea_json=None,
            state=STATE_SCRIPT_FROM_IDEA_TITLE
        ))
        title = title_repo.insert(Title(
            story_id=story.id,
            version=0,
            text="Test Title"
        ))
        story.title_id = title.id
        story_repo.update(story)
        
        result = service.process_oldest_story()
        
        assert result.success is False
        assert result.story_id == story.id
        assert result.error is not None
        assert "no idea_json" in result.error
    
    def test_process_all_pending(self, db_connection, sample_idea):
        """Test processing all pending stories."""
        service = ScriptFromIdeaTitleService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create 3 stories in the target state
        for i in range(3):
            story = story_repo.insert(Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state=STATE_SCRIPT_FROM_IDEA_TITLE
            ))
            title = title_repo.insert(Title(
                story_id=story.id,
                version=0,
                text=f"Test Title {i}"
            ))
            story.title_id = title.id
            story_repo.update(story)
        
        # Process all
        results = service.process_all_pending()
        
        assert len(results) == 3
        assert all(r.success for r in results)
        
        # Verify all stories have new state
        assert service.count_pending() == 0
    
    def test_process_all_pending_with_limit(self, db_connection, sample_idea):
        """Test processing with a limit."""
        service = ScriptFromIdeaTitleService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create 5 stories
        for i in range(5):
            story = story_repo.insert(Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state=STATE_SCRIPT_FROM_IDEA_TITLE
            ))
            title = title_repo.insert(Title(
                story_id=story.id,
                version=0,
                text=f"Test Title {i}"
            ))
            story.title_id = title.id
            story_repo.update(story)
        
        # Process only 2
        results = service.process_all_pending(limit=2)
        
        assert len(results) == 2
        assert service.count_pending() == 3
    
    def test_get_processing_summary(self, db_connection, sample_idea):
        """Test getting processing summary."""
        service = ScriptFromIdeaTitleService(db_connection)
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create stories
        for i in range(2):
            story = story_repo.insert(Story(
                idea_json=json.dumps(sample_idea.to_dict()),
                state=STATE_SCRIPT_FROM_IDEA_TITLE
            ))
            title = title_repo.insert(Title(
                story_id=story.id,
                version=0,
                text=f"Test Title {i}"
            ))
            story.title_id = title.id
            story_repo.update(story)
        
        results = service.process_all_pending()
        summary = service.get_processing_summary(results)
        
        assert summary['total_processed'] == 2
        assert summary['successful'] == 2
        assert summary['failed'] == 0
        assert summary['success_rate'] == 1.0
        assert summary['input_state'] == STATE_SCRIPT_FROM_IDEA_TITLE
        assert summary['output_state'] == STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA


class TestProcessOldestFromIdeaTitle:
    """Tests for the convenience function."""
    
    def test_process_oldest_from_idea_title(self, db_connection, sample_idea):
        """Test the convenience function."""
        story_repo = StoryRepository(db_connection)
        title_repo = TitleRepository(db_connection)
        
        # Create a story
        story = story_repo.insert(Story(
            idea_json=json.dumps(sample_idea.to_dict()),
            state=STATE_SCRIPT_FROM_IDEA_TITLE
        ))
        title = title_repo.insert(Title(
            story_id=story.id,
            version=0,
            text="Test Title"
        ))
        story.title_id = title.id
        story_repo.update(story)
        
        # Use convenience function
        result = process_oldest_from_idea_title(db_connection)
        
        assert result.success is True
        assert result.story_id == story.id
        assert result.new_state == STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA
    
    def test_process_oldest_from_idea_title_empty(self, db_connection):
        """Test the convenience function when no stories are pending."""
        result = process_oldest_from_idea_title(db_connection)
        
        assert result.success is False
        assert result.error is not None
