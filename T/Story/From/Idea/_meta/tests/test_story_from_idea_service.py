"""Tests for Story from Idea service.

This module tests the StoryFromIdeaService that creates Story objects
from Idea objects that don't have Story references yet.
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
import sys


def _find_t_module_dir() -> Path:
    """Find the T module directory by walking up from current file."""
    current = Path(__file__).resolve()
    while current.name != 'T' and current.parent != current:
        current = current.parent
    if current.name == 'T':
        return current
    # Fallback to counting parents (tests -> _meta -> Idea -> From -> Story -> T)
    return Path(__file__).resolve().parent.parent.parent.parent.parent.parent


# Add paths for imports
t_module_dir = _find_t_module_dir()
if str(t_module_dir) not in sys.path:
    sys.path.insert(0, str(t_module_dir))

idea_model_path = t_module_dir / 'Idea' / 'Model' / 'src'
if str(idea_model_path) not in sys.path:
    sys.path.insert(0, str(idea_model_path))

from T.Database.models.story import Story, StoryState
from T.Database.repositories.story_repository import StoryRepository
from simple_idea import SimpleIdea
from simple_idea_db import SimpleIdeaDatabase


class TestStoryFromIdeaService:
    """Tests for StoryFromIdeaService."""
    
    @pytest.fixture
    def story_db(self, tmp_path):
        """Create a temporary Story database."""
        db_path = tmp_path / "story.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        # Create Story table
        conn.executescript(Story.get_sql_schema())
        conn.commit()
        
        yield conn
        
        conn.close()
    
    @pytest.fixture
    def idea_db(self, tmp_path):
        """Create a temporary Idea database with test ideas."""
        db_path = tmp_path / "idea.db"
        db = SimpleIdeaDatabase(str(db_path))
        db.connect()
        db.create_tables()
        
        # Insert test ideas
        db.insert_idea("First test idea about AI", version=1)
        db.insert_idea("Second test idea about quantum computing", version=1)
        db.insert_idea("Third test idea about blockchain", version=1)
        
        yield db
        
        db.close()
    
    @pytest.fixture
    def service(self, story_db, idea_db):
        """Create StoryFromIdeaService with test databases."""
        from T.Story.From.Idea.src.story_from_idea_service import StoryFromIdeaService
        return StoryFromIdeaService(story_db, idea_db)
    
    def test_get_unreferenced_ideas_all_unreferenced(self, service, idea_db):
        """Test that all ideas are returned when none have stories."""
        unreferenced = service.get_unreferenced_ideas()
        
        assert len(unreferenced) == 3
        assert all(isinstance(idea, SimpleIdea) for idea in unreferenced)
    
    def test_get_unreferenced_ideas_some_referenced(self, service, idea_db, story_db):
        """Test that only unreferenced ideas are returned."""
        # Create a story for the first idea
        repo = StoryRepository(story_db)
        story = Story(idea_id="1", state=StoryState.CREATED)
        repo.insert(story)
        
        unreferenced = service.get_unreferenced_ideas()
        
        assert len(unreferenced) == 2
        idea_ids = [idea.id for idea in unreferenced]
        assert 1 not in idea_ids
        assert 2 in idea_ids
        assert 3 in idea_ids
    
    def test_get_unreferenced_ideas_all_referenced(self, service, idea_db, story_db):
        """Test that no ideas are returned when all have stories."""
        # Create stories for all ideas
        repo = StoryRepository(story_db)
        for idea_id in [1, 2, 3]:
            story = Story(idea_id=str(idea_id), state=StoryState.CREATED)
            repo.insert(story)
        
        unreferenced = service.get_unreferenced_ideas()
        
        assert len(unreferenced) == 0
    
    def test_idea_has_stories_false(self, service):
        """Test idea_has_stories returns False for new idea."""
        assert service.idea_has_stories(1) is False
    
    def test_idea_has_stories_true(self, service, story_db):
        """Test idea_has_stories returns True after creating stories."""
        repo = StoryRepository(story_db)
        story = Story(idea_id="1", state=StoryState.CREATED)
        repo.insert(story)
        
        assert service.idea_has_stories(1) is True
    
    def test_create_stories_from_idea_creates_10_stories(self, service):
        """Test that create_stories_from_idea creates exactly 10 stories."""
        result = service.create_stories_from_idea(idea_id=1)
        
        assert result is not None
        assert result.count == 10
        assert len(result.stories) == 10
        assert result.idea_id == 1
    
    def test_create_stories_from_idea_correct_state(self, service):
        """Test that created stories have TITLE_FROM_IDEA state."""
        result = service.create_stories_from_idea(idea_id=1)
        
        for story in result.stories:
            assert story.state == StoryState.TITLE_FROM_IDEA
    
    def test_create_stories_from_idea_correct_idea_reference(self, service):
        """Test that created stories reference the correct idea."""
        result = service.create_stories_from_idea(idea_id=1)
        
        for story in result.stories:
            assert story.idea_id == "1"  # Stored as string in Story
    
    def test_create_stories_from_idea_unique_ids(self, service):
        """Test that all created stories have unique IDs."""
        result = service.create_stories_from_idea(idea_id=1)
        
        story_ids = [story.id for story in result.stories]
        assert len(set(story_ids)) == 10  # All IDs are unique
    
    def test_create_stories_from_idea_skip_if_exists(self, service, story_db):
        """Test that create_stories_from_idea skips if stories already exist."""
        # Create first batch
        result1 = service.create_stories_from_idea(idea_id=1)
        assert result1 is not None
        assert result1.count == 10
        
        # Try to create again - should be skipped
        result2 = service.create_stories_from_idea(idea_id=1, skip_if_exists=True)
        assert result2 is None
    
    def test_create_stories_from_idea_no_skip(self, service, story_db):
        """Test that create_stories_from_idea can create more stories if skip_if_exists=False."""
        # Create first batch
        result1 = service.create_stories_from_idea(idea_id=1)
        assert result1 is not None
        
        # Create again without skipping
        result2 = service.create_stories_from_idea(idea_id=1, skip_if_exists=False)
        assert result2 is not None
        assert result2.count == 10
        
        # Total should be 20 stories for idea 1
        repo = StoryRepository(story_db)
        stories = repo.find_by_idea_id("1")
        assert len(stories) == 20
    
    def test_process_unreferenced_ideas_all(self, service):
        """Test process_unreferenced_ideas creates stories for all ideas."""
        results = service.process_unreferenced_ideas()
        
        assert len(results) == 3
        
        total_stories = sum(r.count for r in results)
        assert total_stories == 30  # 10 stories per 3 ideas
    
    def test_process_unreferenced_ideas_partial(self, service, story_db):
        """Test process_unreferenced_ideas only processes unreferenced ideas."""
        # Create story for first idea
        repo = StoryRepository(story_db)
        story = Story(idea_id="1", state=StoryState.CREATED)
        repo.insert(story)
        
        results = service.process_unreferenced_ideas()
        
        assert len(results) == 2
        
        processed_idea_ids = [r.idea_id for r in results]
        assert 1 not in processed_idea_ids
        assert 2 in processed_idea_ids
        assert 3 in processed_idea_ids
    
    def test_process_unreferenced_ideas_none_unreferenced(self, service, story_db):
        """Test process_unreferenced_ideas returns empty when all referenced."""
        # Create stories for all ideas
        repo = StoryRepository(story_db)
        for idea_id in [1, 2, 3]:
            story = Story(idea_id=str(idea_id), state=StoryState.CREATED)
            repo.insert(story)
        
        results = service.process_unreferenced_ideas()
        
        assert len(results) == 0
    
    def test_get_oldest_unreferenced_idea(self, service):
        """Test get_oldest_unreferenced_idea returns the oldest idea."""
        oldest = service.get_oldest_unreferenced_idea()
        
        # First idea inserted should be the oldest
        assert oldest is not None
        assert oldest.id == 1
    
    def test_get_oldest_unreferenced_idea_with_some_referenced(self, service, story_db):
        """Test get_oldest_unreferenced_idea skips referenced ideas."""
        # Create a story for the first idea (oldest)
        repo = StoryRepository(story_db)
        story = Story(idea_id="1", state=StoryState.CREATED)
        repo.insert(story)
        
        oldest = service.get_oldest_unreferenced_idea()
        
        # Should return idea 2 (the next oldest unreferenced)
        assert oldest is not None
        assert oldest.id == 2
    
    def test_get_oldest_unreferenced_idea_none_available(self, service, story_db):
        """Test get_oldest_unreferenced_idea returns None when all referenced."""
        # Create stories for all ideas
        repo = StoryRepository(story_db)
        for idea_id in [1, 2, 3]:
            story = Story(idea_id=str(idea_id), state=StoryState.CREATED)
            repo.insert(story)
        
        oldest = service.get_oldest_unreferenced_idea()
        
        assert oldest is None
    
    def test_process_oldest_unreferenced_idea(self, service):
        """Test process_oldest_unreferenced_idea creates stories for oldest idea."""
        result = service.process_oldest_unreferenced_idea()
        
        assert result is not None
        assert result.idea_id == 1  # Should be the first (oldest) idea
        assert result.count == 10
    
    def test_process_oldest_unreferenced_idea_with_some_referenced(self, service, story_db):
        """Test process_oldest_unreferenced_idea processes next oldest when some referenced."""
        # Create a story for the first idea (oldest)
        repo = StoryRepository(story_db)
        story = Story(idea_id="1", state=StoryState.CREATED)
        repo.insert(story)
        
        result = service.process_oldest_unreferenced_idea()
        
        assert result is not None
        assert result.idea_id == 2  # Should be the second (next oldest) idea
        assert result.count == 10
    
    def test_process_oldest_unreferenced_idea_none_available(self, service, story_db):
        """Test process_oldest_unreferenced_idea returns None when all referenced."""
        # Create stories for all ideas
        repo = StoryRepository(story_db)
        for idea_id in [1, 2, 3]:
            story = Story(idea_id=str(idea_id), state=StoryState.CREATED)
            repo.insert(story)
        
        result = service.process_oldest_unreferenced_idea()
        
        assert result is None
    
    def test_process_oldest_unreferenced_idea_stories_have_correct_state(self, service):
        """Test that stories created by process_oldest_unreferenced_idea have correct state."""
        result = service.process_oldest_unreferenced_idea()
        
        assert result is not None
        for story in result.stories:
            assert story.state == StoryState.TITLE_FROM_IDEA


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    @pytest.fixture
    def story_db(self, tmp_path):
        """Create a temporary Story database."""
        db_path = tmp_path / "story.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        # Create Story table
        conn.executescript(Story.get_sql_schema())
        conn.commit()
        
        yield conn
        
        conn.close()
    
    @pytest.fixture
    def idea_db(self, tmp_path):
        """Create a temporary Idea database with test ideas."""
        db_path = tmp_path / "idea.db"
        db = SimpleIdeaDatabase(str(db_path))
        db.connect()
        db.create_tables()
        
        # Insert test ideas
        db.insert_idea("Test idea 1", version=1)
        db.insert_idea("Test idea 2", version=1)
        
        yield db
        
        db.close()
    
    def test_create_stories_from_idea_function(self, story_db, idea_db):
        """Test create_stories_from_idea convenience function."""
        from T.Story.From.Idea.src.story_from_idea_service import create_stories_from_idea
        
        result = create_stories_from_idea(story_db, idea_db, idea_id=1)
        
        assert result is not None
        assert result.count == 10
    
    def test_get_unreferenced_ideas_function(self, story_db, idea_db):
        """Test get_unreferenced_ideas convenience function."""
        from T.Story.From.Idea.src.story_from_idea_service import get_unreferenced_ideas
        
        unreferenced = get_unreferenced_ideas(story_db, idea_db)
        
        assert len(unreferenced) == 2
    
    def test_process_oldest_unreferenced_idea_function(self, story_db, idea_db):
        """Test process_oldest_unreferenced_idea convenience function."""
        from T.Story.From.Idea.src.story_from_idea_service import process_oldest_unreferenced_idea
        
        result = process_oldest_unreferenced_idea(story_db, idea_db)
        
        assert result is not None
        assert result.idea_id == 1  # Should process the first (oldest) idea
        assert result.count == 10


class TestStoryCreationResult:
    """Tests for StoryCreationResult dataclass."""
    
    def test_creation_result_count(self):
        """Test StoryCreationResult.count property."""
        from T.Story.From.Idea.src.story_from_idea_service import StoryCreationResult
        
        result = StoryCreationResult(
            idea_id=1,
            stories=[
                Story(idea_id="1", state=StoryState.CREATED),
                Story(idea_id="1", state=StoryState.CREATED),
            ]
        )
        
        assert result.count == 2
    
    def test_creation_result_empty(self):
        """Test StoryCreationResult with no stories."""
        from T.Story.From.Idea.src.story_from_idea_service import StoryCreationResult
        
        result = StoryCreationResult(idea_id=1)
        
        assert result.count == 0
        assert result.stories == []


class TestWaitIntervalFunctions:
    """Tests for the dynamic wait interval functions."""
    
    def test_get_wait_interval_zero_ideas(self):
        """Test that 0 unreferenced ideas returns 30 seconds."""
        from T.Story.From.Idea.src.story_from_idea_interactive import get_wait_interval
        
        assert get_wait_interval(0) == 30.0
    
    def test_get_wait_interval_one_idea(self):
        """Test that 1 unreferenced idea returns ~1 second."""
        from T.Story.From.Idea.src.story_from_idea_interactive import get_wait_interval
        
        assert get_wait_interval(1) == 1.0
    
    def test_get_wait_interval_hundred_ideas(self):
        """Test that 100 unreferenced ideas returns 1 ms."""
        from T.Story.From.Idea.src.story_from_idea_interactive import get_wait_interval
        
        assert get_wait_interval(100) == 0.001
    
    def test_get_wait_interval_many_ideas(self):
        """Test that > 100 unreferenced ideas returns 1 ms."""
        from T.Story.From.Idea.src.story_from_idea_interactive import get_wait_interval
        
        assert get_wait_interval(1000) == 0.001
        assert get_wait_interval(500) == 0.001
    
    def test_get_wait_interval_fifty_ideas(self):
        """Test that 50 unreferenced ideas returns ~0.5 seconds."""
        from T.Story.From.Idea.src.story_from_idea_interactive import get_wait_interval
        
        interval = get_wait_interval(50)
        assert 0.4 < interval < 0.6  # Approximately 0.5 seconds
    
    def test_get_wait_interval_gradual_increase(self):
        """Test that interval increases as count decreases."""
        from T.Story.From.Idea.src.story_from_idea_interactive import get_wait_interval
        
        # Interval should increase as count decreases
        assert get_wait_interval(99) < get_wait_interval(50)
        assert get_wait_interval(50) < get_wait_interval(25)
        assert get_wait_interval(25) < get_wait_interval(1)
    
    def test_format_wait_time_seconds(self):
        """Test format_wait_time for values >= 1 second."""
        from T.Story.From.Idea.src.story_from_idea_interactive import format_wait_time
        
        assert format_wait_time(30.0) == "30.0 second(s)"
        assert format_wait_time(1.0) == "1.0 second(s)"
        assert format_wait_time(5.5) == "5.5 second(s)"
    
    def test_format_wait_time_milliseconds(self):
        """Test format_wait_time for values < 1 second."""
        from T.Story.From.Idea.src.story_from_idea_interactive import format_wait_time
        
        assert format_wait_time(0.001) == "1.0 ms"
        assert format_wait_time(0.5) == "500.0 ms"
        assert format_wait_time(0.1) == "100.0 ms"
