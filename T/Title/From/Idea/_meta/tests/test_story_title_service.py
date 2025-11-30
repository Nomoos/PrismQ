"""Tests for Story and Title creation service from Idea.

This module tests the StoryTitleService functionality which creates
10 Story objects with FK reference to Idea and generates the first
Title (v0) for each Story.
"""

import sys
import os
import pytest
import sqlite3
from pathlib import Path

# Set up paths before any other imports
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent.parent.parent.parent.parent.parent
_idea_model_path = _project_root / 'T' / 'Idea' / 'Model' / 'src'
_src_path = _test_dir.parent.parent / 'src'

# Add all required paths
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_idea_model_path))
sys.path.insert(0, str(_src_path))

from idea import Idea, ContentGenre, IdeaStatus
from title_generator import TitleConfig
from story_title_service import (
    StoryTitleService,
    StoryTitleResult,
    create_stories_from_idea
)

# Import database models
from T.Database.models.story import Story, StoryState
from T.Database.models.title import Title


class TestStoryTitleService:
    """Tests for StoryTitleService class."""
    
    def test_create_10_stories_from_idea(self):
        """Test creating exactly 10 stories from an idea."""
        idea = Idea(
            title="The Future of AI",
            concept="An exploration of artificial intelligence trends",
            status=IdeaStatus.DRAFT
        )
        
        service = StoryTitleService()
        result = service.create_stories_with_titles(idea)
        
        assert result.count == 10
        assert len(result.stories) == 10
        assert len(result.titles) == 10
        assert len(result.title_variants) == 10
    
    def test_stories_reference_idea(self):
        """Test that all stories reference the same idea."""
        idea = Idea(
            title="Digital Privacy",
            concept="Understanding online privacy concerns",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea)
        
        # All stories should have the same idea_id
        idea_ids = [story.idea_id for story in result.stories]
        assert len(set(idea_ids)) == 1  # All same
        assert result.idea_id == idea_ids[0]
    
    def test_explicit_idea_id(self):
        """Test using explicit idea_id."""
        idea = Idea(
            title="Test Idea",
            concept="Test concept",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea, idea_id="custom-idea-123")
        
        assert result.idea_id == "custom-idea-123"
        for story in result.stories:
            assert story.idea_id == "custom-idea-123"
    
    def test_each_story_has_title_v0(self):
        """Test that each story gets a Title v0."""
        idea = Idea(
            title="Machine Learning Basics",
            concept="Introduction to ML concepts",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea)
        
        for story, title in result.get_story_title_pairs():
            assert title.story_id == story.id
            assert title.version == 0
            assert len(title.text) > 0
    
    def test_stories_in_title_v0_state(self):
        """Test that all stories are transitioned to TITLE_V0 state."""
        idea = Idea(
            title="Blockchain Technology",
            concept="Understanding decentralized systems",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea)
        
        for story in result.stories:
            assert story.state == StoryState.TITLE_V0
    
    def test_invalid_idea_none(self):
        """Test error handling with None idea."""
        service = StoryTitleService()
        
        with pytest.raises(ValueError, match="Idea cannot be None"):
            service.create_stories_with_titles(None)
    
    def test_invalid_idea_empty(self):
        """Test error handling with empty idea."""
        idea = Idea(
            title="",
            concept="",
            status=IdeaStatus.DRAFT
        )
        
        service = StoryTitleService()
        
        with pytest.raises(ValueError, match="must have at least a title or concept"):
            service.create_stories_with_titles(idea)
    
    def test_title_variants_diverse(self):
        """Test that 10 different title variants are generated."""
        idea = Idea(
            title="Python Programming",
            concept="Learning Python language",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea)
        
        # Check all variants have different styles
        styles = [v.style for v in result.title_variants]
        expected_styles = {
            'direct', 'question', 'how-to', 'curiosity', 'authoritative',
            'listicle', 'problem-solution', 'comparison', 'ultimate-guide', 'benefit'
        }
        assert set(styles) == expected_styles


class TestStoryTitleServiceWithDatabase:
    """Tests for StoryTitleService with database persistence."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database for testing."""
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()
    
    def test_persistence_to_database(self, db_connection):
        """Test that stories and titles are persisted to database."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()
        
        idea = Idea(
            title="Test Persistence",
            concept="Testing database persistence",
            status=IdeaStatus.DRAFT
        )
        
        result = service.create_stories_with_titles(idea)
        
        # Verify stories in database
        cursor = db_connection.execute('SELECT COUNT(*) FROM Story')
        story_count = cursor.fetchone()[0]
        assert story_count == 10
        
        # Verify titles in database
        cursor = db_connection.execute('SELECT COUNT(*) FROM Title')
        title_count = cursor.fetchone()[0]
        assert title_count == 10
    
    def test_story_title_fk_relationship(self, db_connection):
        """Test FK relationship between Story and Title."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()
        
        idea = Idea(
            title="FK Test",
            concept="Testing foreign key relationship",
            status=IdeaStatus.DRAFT
        )
        
        result = service.create_stories_with_titles(idea)
        
        # Each title should reference its story
        for story, title in result.get_story_title_pairs():
            cursor = db_connection.execute(
                'SELECT story_id FROM Title WHERE id = ?',
                (title.id,)
            )
            row = cursor.fetchone()
            assert row['story_id'] == story.id
    
    def test_story_state_persisted(self, db_connection):
        """Test that story state is correctly persisted."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()
        
        idea = Idea(
            title="State Test",
            concept="Testing state persistence",
            status=IdeaStatus.DRAFT
        )
        
        result = service.create_stories_with_titles(idea)
        
        # All stories should have TITLE_V0 state in database
        cursor = db_connection.execute(
            "SELECT state FROM Story WHERE state = ?",
            (StoryState.TITLE_V0.value,)
        )
        rows = cursor.fetchall()
        assert len(rows) == 10
    
    def test_multiple_ideas_separate_stories(self, db_connection):
        """Test that different ideas create separate story sets."""
        service = StoryTitleService(db_connection)
        service.ensure_tables_exist()
        
        idea1 = Idea(
            title="First Idea",
            concept="First concept",
            status=IdeaStatus.DRAFT
        )
        idea2 = Idea(
            title="Second Idea",
            concept="Second concept",
            status=IdeaStatus.DRAFT
        )
        
        result1 = service.create_stories_with_titles(idea1)
        result2 = service.create_stories_with_titles(idea2)
        
        # Each idea should have its own set of stories
        assert result1.idea_id != result2.idea_id
        
        # Total 20 stories in database
        cursor = db_connection.execute('SELECT COUNT(*) FROM Story')
        total_stories = cursor.fetchone()[0]
        assert total_stories == 20
        
        # 10 stories for each idea
        cursor = db_connection.execute(
            'SELECT COUNT(*) FROM Story WHERE idea_id = ?',
            (result1.idea_id,)
        )
        idea1_stories = cursor.fetchone()[0]
        assert idea1_stories == 10


class TestStoryTitleResult:
    """Tests for StoryTitleResult data class."""
    
    def test_count_property(self):
        """Test count property returns correct number."""
        result = StoryTitleResult(
            idea_id="test-id",
            stories=[Story(idea_id="test-id") for _ in range(5)],
            titles=[Title(story_id=i, version=0, text=f"Title {i}") for i in range(5)]
        )
        
        assert result.count == 5
    
    def test_get_story_title_pairs(self):
        """Test get_story_title_pairs returns correct pairs."""
        stories = [Story(idea_id="test", id=i) for i in range(3)]
        titles = [Title(story_id=i, version=0, text=f"Title {i}") for i in range(3)]
        
        result = StoryTitleResult(
            idea_id="test",
            stories=stories,
            titles=titles
        )
        
        pairs = result.get_story_title_pairs()
        assert len(pairs) == 3
        for i, (story, title) in enumerate(pairs):
            assert story.id == i
            assert title.story_id == i


class TestConvenienceFunction:
    """Tests for create_stories_from_idea convenience function."""
    
    def test_create_stories_from_idea(self):
        """Test convenience function creates stories correctly."""
        idea = Idea(
            title="Cloud Computing",
            concept="Understanding cloud services",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea)
        
        assert result.count == 10
        assert all(isinstance(s, Story) for s in result.stories)
        assert all(isinstance(t, Title) for t in result.titles)
    
    def test_with_custom_config(self):
        """Test convenience function with custom title config."""
        config = TitleConfig(
            num_variants=10,
            max_length=70
        )
        
        idea = Idea(
            title="Test with Config",
            concept="Testing configuration",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea, title_config=config)
        
        assert result.count == 10
        for title in result.titles:
            assert len(title.text) <= 70


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_idea_with_only_concept(self):
        """Test creating stories from idea with only concept."""
        idea = Idea(
            title="",
            concept="A comprehensive exploration of quantum computing",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea)
        
        assert result.count == 10
        # ID should be derived from concept hash
        assert result.idea_id.startswith("idea-")
    
    def test_idea_with_unicode(self):
        """Test creating stories from idea with unicode characters."""
        idea = Idea(
            title="Technology & Innovation",
            concept="Exploring tech trends",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea)
        
        assert result.count == 10
        assert all(s.state == StoryState.TITLE_V0 for s in result.stories)
    
    def test_very_long_title(self):
        """Test with very long idea title."""
        idea = Idea(
            title="A Very Long Title About The Future of Technology and Innovation " * 3,
            concept="Long title test",
            status=IdeaStatus.DRAFT
        )
        
        result = create_stories_from_idea(idea)
        
        assert result.count == 10
        # Idea ID should be truncated
        assert len(result.idea_id) <= 50
