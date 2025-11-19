"""Tests for IdeaInspiration data model."""

import pytest
from datetime import datetime
from src.classification import IdeaInspiration


class TestIdeaInspiration:
    """Test IdeaInspiration data model."""
    
    def test_initialization_minimal(self):
        """Test initialization with minimal fields."""
        inspiration = IdeaInspiration(title="Test Title")
        
        assert inspiration.title == "Test Title"
        assert inspiration.description == ""
        assert inspiration.content == ""
        assert inspiration.keywords == []
        assert inspiration.source_type == "text"
        assert isinstance(inspiration.metadata, dict)
        assert isinstance(inspiration.created_at, datetime)
    
    def test_initialization_full(self):
        """Test initialization with all fields."""
        keywords = ["test", "example"]
        metadata = {"source": "youtube", "duration": 60}
        created_at = datetime(2025, 10, 13, 12, 0, 0)
        
        inspiration = IdeaInspiration(
            title="Full Test",
            description="Test description",
            content="Test content text",
            keywords=keywords,
            source_type="video",
            metadata=metadata,
            created_at=created_at
        )
        
        assert inspiration.title == "Full Test"
        assert inspiration.description == "Test description"
        assert inspiration.content == "Test content text"
        assert inspiration.keywords == ["test", "example"]
        assert inspiration.source_type == "video"
        assert inspiration.metadata == {"source": "youtube", "duration": 60}
        assert inspiration.created_at == created_at
    
    def test_all_text_property(self):
        """Test all_text property combines all text fields."""
        inspiration = IdeaInspiration(
            title="Title",
            description="Description",
            content="Content",
            keywords=["key1", "key2"]
        )
        
        all_text = inspiration.all_text
        assert "Title" in all_text
        assert "Description" in all_text
        assert "Content" in all_text
        assert "key1" in all_text
        assert "key2" in all_text
    
    def test_has_content_property(self):
        """Test has_content property."""
        # Empty inspiration
        empty = IdeaInspiration(title="")
        assert not empty.has_content
        
        # With title
        with_title = IdeaInspiration(title="Title")
        assert with_title.has_content
        
        # With description
        with_desc = IdeaInspiration(title="", description="Description")
        assert with_desc.has_content
        
        # With content
        with_content = IdeaInspiration(title="", content="Content")
        assert with_content.has_content
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        inspiration = IdeaInspiration(
            title="Test",
            description="Desc",
            content="Content",
            keywords=["key1"],
            source_type="video"
        )
        
        data = inspiration.to_dict()
        
        assert data['title'] == "Test"
        assert data['description'] == "Desc"
        assert data['content'] == "Content"
        assert data['keywords'] == ["key1"]
        assert data['source_type'] == "video"
        assert 'metadata' in data
        assert 'created_at' in data
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'title': 'Dict Test',
            'description': 'Dict description',
            'content': 'Dict content',
            'keywords': ['key1', 'key2'],
            'source_type': 'audio',
            'metadata': {'test': 'value'}
        }
        
        inspiration = IdeaInspiration.from_dict(data)
        
        assert inspiration.title == 'Dict Test'
        assert inspiration.description == 'Dict description'
        assert inspiration.content == 'Dict content'
        assert inspiration.keywords == ['key1', 'key2']
        assert inspiration.source_type == 'audio'
        assert inspiration.metadata == {'test': 'value'}
    
    def test_from_dict_with_datetime_string(self):
        """Test from_dict with datetime string."""
        data = {
            'title': 'Test',
            'created_at': '2025-10-13T12:00:00'
        }
        
        inspiration = IdeaInspiration.from_dict(data)
        
        assert inspiration.title == 'Test'
        assert isinstance(inspiration.created_at, datetime)
    
    def test_post_init_validation(self):
        """Test post_init validation handles invalid types."""
        # This should not raise an error
        inspiration = IdeaInspiration(title="Test")
        assert isinstance(inspiration.keywords, list)
        assert isinstance(inspiration.metadata, dict)
