"""Tests for Story model and state machine."""

import pytest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from story import Story, StoryState, StoryStatus, VALID_TRANSITIONS
from story_db import StoryDatabase


class TestStoryStateTransitions:
    """Test state machine transitions."""
    
    def test_initial_state(self):
        """Test that Story starts in IDEA state."""
        story = Story(title="Test Story", idea_id="idea_1")
        assert story.state == StoryState.IDEA
        assert story.status == StoryStatus.DRAFT
    
    def test_valid_transition(self):
        """Test valid state transition."""
        story = Story(title="Test Story", idea_id="idea_1")
        
        # Valid transition: IDEA -> IDEA_REVIEW
        result = story.transition_to(StoryState.IDEA_REVIEW)
        assert result is True
        assert story.state == StoryState.IDEA_REVIEW
        assert len(story.state_history) == 2
    
    def test_invalid_transition(self):
        """Test that invalid transitions raise ValueError."""
        story = Story(title="Test Story", idea_id="idea_1")
        
        # Invalid: Can't go directly from IDEA to SCRIPT_DRAFT
        with pytest.raises(ValueError, match="Invalid state transition"):
            story.transition_to(StoryState.SCRIPT_DRAFT)
    
    def test_full_workflow_text_only(self):
        """Test complete workflow through all review stages."""
        story = Story(title="Quality Story", idea_id="idea_quality_1")
        
        # Progress through Idea phase
        story.transition_to(StoryState.IDEA_REVIEW)
        story.transition_to(StoryState.OUTLINE)
        story.transition_to(StoryState.TITLE_DRAFT)
        
        # Progress through Script phase
        story.transition_to(StoryState.SCRIPT_DRAFT)
        story.script_text = "Once upon a time..."
        story.transition_to(StoryState.CONTENT_REVIEW)
        story.transition_to(StoryState.EDITING)
        
        # Progress through Quality Review Pipeline
        story.transition_to(StoryState.GRAMMAR_REVIEW)
        story.transition_to(StoryState.CONSISTENCY_CHECK)
        story.transition_to(StoryState.TONE_CHECK)
        story.transition_to(StoryState.READABILITY_REVIEW)
        
        # Finalize and publish
        story.transition_to(StoryState.FINALIZATION)
        story.transition_to(StoryState.TITLE_OPTIMIZATION)
        story.transition_to(StoryState.PUBLISHING)
        
        # Archive
        story.transition_to(StoryState.ARCHIVED)
        
        assert story.state == StoryState.ARCHIVED
        assert story.status == StoryStatus.ARCHIVED
        assert len(story.state_history) == 15  # 1 initial + 14 transitions
    
    def test_workflow_with_improvements(self):
        """Test workflow with script improvements loop."""
        story = Story(title="Story with Improvements", idea_id="idea_improve_1")
        
        # Progress through initial phases
        story.transition_to(StoryState.IDEA_REVIEW)
        story.transition_to(StoryState.OUTLINE)
        story.transition_to(StoryState.TITLE_DRAFT)
        story.transition_to(StoryState.SCRIPT_DRAFT)
        story.transition_to(StoryState.CONTENT_REVIEW)
        story.transition_to(StoryState.EDITING)
        story.transition_to(StoryState.GRAMMAR_REVIEW)
        
        # Found language issues - go to improvements
        story.transition_to(StoryState.SCRIPT_IMPROVEMENTS, notes="Grammar issues found")
        
        # Loop back to editing
        story.transition_to(StoryState.EDITING)
        story.transition_to(StoryState.GRAMMAR_REVIEW)
        story.transition_to(StoryState.CONSISTENCY_CHECK)
        story.transition_to(StoryState.TONE_CHECK)
        story.transition_to(StoryState.READABILITY_REVIEW)
        
        # Complete workflow
        story.transition_to(StoryState.FINALIZATION)
        story.transition_to(StoryState.TITLE_OPTIMIZATION)
        story.transition_to(StoryState.PUBLISHING)
        story.transition_to(StoryState.ARCHIVED)
        
        assert story.state == StoryState.ARCHIVED
        assert len(story.state_history) == 18  # 1 initial + 17 transitions
    
    def test_backward_transition_script_revision(self):
        """Test backward transition using improvements hub."""
        story = Story(title="Story", idea_id="idea_1")
        
        # Progress to tone check
        story.transition_to(StoryState.IDEA_REVIEW)
        story.transition_to(StoryState.OUTLINE)
        story.transition_to(StoryState.TITLE_DRAFT)
        story.transition_to(StoryState.SCRIPT_DRAFT)
        story.transition_to(StoryState.CONTENT_REVIEW)
        story.transition_to(StoryState.EDITING)
        story.transition_to(StoryState.GRAMMAR_REVIEW)
        story.transition_to(StoryState.CONSISTENCY_CHECK)
        story.transition_to(StoryState.TONE_CHECK)
        
        # Go to improvements for tone mismatch
        story.transition_to(StoryState.SCRIPT_IMPROVEMENTS, notes="Tone mismatch")
        assert story.state == StoryState.SCRIPT_IMPROVEMENTS
        
        # Verify state history
        assert len(story.state_history) == 11
        assert story.state_history[-1]["notes"] == "Tone mismatch"
    
    def test_early_archive(self):
        """Test that stories can be archived from any state."""
        story = Story(title="Story", idea_id="idea_1")
        
        # Archive from initial state
        story.transition_to(StoryState.ARCHIVED)
        assert story.state == StoryState.ARCHIVED
        assert story.status == StoryStatus.ARCHIVED


class TestStoryOperations:
    """Test Story operations and methods."""
    
    def test_from_idea(self):
        """Test creating Story from Idea."""
        # Mock Idea object
        class MockIdea:
            id = "idea_123"
            title = "Test Idea"
            target_platforms = ["reddit", "medium"]
            target_formats = ["text"]
            keywords = ["horror", "nosleep"]
        
        idea = MockIdea()
        story = Story.from_idea(idea, created_by="writer_1")
        
        assert story.idea_id == "idea_123"
        assert story.title == "Test Idea"
        assert story.target_platforms == ["reddit", "medium"]
        assert story.target_formats == ["text"]
        assert story.tags == ["horror", "nosleep"]
        assert story.created_by == "writer_1"
    
    def test_get_valid_transitions(self):
        """Test getting valid transitions for current state."""
        story = Story(title="Story", idea_id="idea_1")
        
        # From IDEA
        valid = story.get_valid_transitions()
        assert StoryState.IDEA_REVIEW in valid
        assert StoryState.ARCHIVED in valid
        assert StoryState.SCRIPT_DRAFT not in valid
    
    def test_can_transition_to(self):
        """Test checking if transition is valid."""
        story = Story(title="Story", idea_id="idea_1")
        
        assert story.can_transition_to(StoryState.IDEA_REVIEW) is True
        assert story.can_transition_to(StoryState.SCRIPT_DRAFT) is False
    
    def test_status_updates(self):
        """Test that status updates correctly with state changes."""
        story = Story(title="Story", idea_id="idea_1")
        
        # Draft phase
        assert story.status == StoryStatus.DRAFT
        
        # Development phase
        story.transition_to(StoryState.IDEA_REVIEW)
        story.transition_to(StoryState.OUTLINE)
        story.transition_to(StoryState.TITLE_DRAFT)
        story.transition_to(StoryState.SCRIPT_DRAFT)
        assert story.status == StoryStatus.IN_DEVELOPMENT
        
        # Ready for review
        story.transition_to(StoryState.CONTENT_REVIEW)
        story.transition_to(StoryState.EDITING)
        story.transition_to(StoryState.GRAMMAR_REVIEW)
        assert story.status == StoryStatus.READY_FOR_REVIEW
        
        # Approved/finalization
        story.transition_to(StoryState.CONSISTENCY_CHECK)
        story.transition_to(StoryState.TONE_CHECK)
        story.transition_to(StoryState.READABILITY_REVIEW)
        story.transition_to(StoryState.FINALIZATION)
        assert story.status == StoryStatus.APPROVED
        
        # In production
        story.transition_to(StoryState.TITLE_OPTIMIZATION)
        story.transition_to(StoryState.PUBLISHING)
        assert story.status == StoryStatus.IN_PRODUCTION
    
    def test_to_dict_from_dict(self):
        """Test serialization and deserialization."""
        story = Story(
            title="Test Story",
            idea_id="idea_1",
            script_text="Script content",
            tags=["horror", "story"],
            target_platforms=["reddit"]
        )
        
        # Convert to dict
        story_dict = story.to_dict()
        assert story_dict["title"] == "Test Story"
        assert story_dict["state"] == "idea"
        
        # Convert back
        story2 = Story.from_dict(story_dict)
        assert story2.title == story.title
        assert story2.state == story.state
        assert story2.tags == story.tags


class TestStoryDatabase:
    """Test Story database operations."""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create temporary database for testing."""
        db_path = tmp_path / "test_stories.db"
        db = StoryDatabase(str(db_path))
        db.connect()
        yield db
        db.close()
    
    def test_insert_and_retrieve(self, db):
        """Test inserting and retrieving story."""
        story = Story(title="Test Story", idea_id="idea_1")
        
        # Insert
        story_id = db.insert_story(story.to_dict())
        assert story_id > 0
        
        # Retrieve
        retrieved = db.get_story(story_id)
        assert retrieved is not None
        assert retrieved["title"] == "Test Story"
        assert retrieved["idea_id"] == "idea_1"
    
    def test_update_story(self, db):
        """Test updating story."""
        story = Story(title="Original Title", idea_id="idea_1")
        story_id = db.insert_story(story.to_dict())
        
        # Update
        story.title = "Updated Title"
        story.transition_to(StoryState.IDEA_REVIEW)
        db.update_story(story_id, story.to_dict())
        
        # Retrieve and verify
        retrieved = db.get_story(story_id)
        assert retrieved["title"] == "Updated Title"
        assert retrieved["state"] == "idea_review"
    
    def test_get_stories_by_idea(self, db):
        """Test retrieving stories by idea ID."""
        story1 = Story(title="Story 1", idea_id="idea_1")
        story2 = Story(title="Story 2", idea_id="idea_1")
        story3 = Story(title="Story 3", idea_id="idea_2")
        
        db.insert_story(story1.to_dict())
        db.insert_story(story2.to_dict())
        db.insert_story(story3.to_dict())
        
        # Query for idea_1
        stories = db.get_stories_by_idea("idea_1")
        assert len(stories) == 2
        assert all(s["idea_id"] == "idea_1" for s in stories)
    
    def test_get_stories_by_state(self, db):
        """Test retrieving stories by state."""
        story1 = Story(title="Story 1", idea_id="idea_1")
        story2 = Story(title="Story 2", idea_id="idea_2")
        story2.transition_to(StoryState.IDEA_REVIEW)
        
        db.insert_story(story1.to_dict())
        db.insert_story(story2.to_dict())
        
        # Query for IDEA state
        stories = db.get_stories_by_state(StoryState.IDEA)
        assert len(stories) == 1
        assert stories[0]["title"] == "Story 1"
    
    def test_get_stories_by_status(self, db):
        """Test retrieving stories by status."""
        story1 = Story(title="Story 1", idea_id="idea_1")
        story2 = Story(title="Story 2", idea_id="idea_2")
        story2.transition_to(StoryState.IDEA_REVIEW)
        story2.transition_to(StoryState.OUTLINE)
        story2.transition_to(StoryState.TITLE_DRAFT)
        story2.transition_to(StoryState.SCRIPT_DRAFT)
        
        db.insert_story(story1.to_dict())
        db.insert_story(story2.to_dict())
        
        # Query for DRAFT status
        drafts = db.get_stories_by_status(StoryStatus.DRAFT)
        assert len(drafts) == 1
        
        # Query for IN_DEVELOPMENT status
        in_dev = db.get_stories_by_status(StoryStatus.IN_DEVELOPMENT)
        assert len(in_dev) == 1
    
    def test_delete_story(self, db):
        """Test deleting story."""
        story = Story(title="Story to Delete", idea_id="idea_1")
        story_id = db.insert_story(story.to_dict())
        
        # Verify it exists
        assert db.get_story(story_id) is not None
        
        # Delete
        db.delete_story(story_id)
        
        # Verify it's gone
        assert db.get_story(story_id) is None


class TestValidTransitions:
    """Test the VALID_TRANSITIONS dictionary."""
    
    def test_all_states_have_transitions(self):
        """Test that all states (except terminal) have defined transitions."""
        for state in StoryState:
            assert state in VALID_TRANSITIONS
    
    def test_archived_has_no_exits(self):
        """Test that ARCHIVED state has no exit transitions."""
        assert VALID_TRANSITIONS[StoryState.ARCHIVED] == []
    
    def test_all_states_can_archive(self):
        """Test that all non-terminal states can transition to ARCHIVED."""
        for state in StoryState:
            if state != StoryState.ARCHIVED:
                transitions = VALID_TRANSITIONS[state]
                assert StoryState.ARCHIVED in transitions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
