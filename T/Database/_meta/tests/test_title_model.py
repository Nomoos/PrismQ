"""Tests for Title model.

Tests the Title model implementation against the IModel interface,
including validation, serialization, and field requirements.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from T.Database.models.title import Title


class TestTitle:
    """Tests for Title model."""
    
    def test_create_title(self):
        """Test creating a basic title."""
        title = Title(
            story_id=1,
            version=0,
            text="10 Tips for Better Python Code"
        )
        
        assert title.story_id == 1
        assert title.version == 0
        assert title.text == "10 Tips for Better Python Code"
        assert title.review_id is None
        assert title.id is None
        assert isinstance(title.created_at, datetime)
    
    def test_title_with_review_id(self):
        """Test title with review reference."""
        title = Title(
            story_id=1,
            version=1,
            text="Improved Title",
            review_id=5
        )
        
        assert title.review_id == 5
    
    def test_version_validation(self):
        """Test version must be non-negative (UINT simulation)."""
        with pytest.raises(ValueError) as exc_info:
            Title(story_id=1, version=-1, text="Invalid")
        
        assert "Version must be >= 0" in str(exc_info.value)
    
    def test_version_zero_allowed(self):
        """Test version 0 is allowed (first version)."""
        title = Title(story_id=1, version=0, text="First Version")
        assert title.version == 0
    
    def test_empty_text_validation(self):
        """Test text cannot be empty."""
        with pytest.raises(ValueError) as exc_info:
            Title(story_id=1, version=0, text="")
        
        assert "Title text cannot be empty" in str(exc_info.value)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        title = Title(
            story_id=1,
            version=2,
            text="Great Title",
            review_id=10,
            id=5
        )
        data = title.to_dict()
        
        assert data["id"] == 5
        assert data["story_id"] == 1
        assert data["version"] == 2
        assert data["text"] == "Great Title"
        assert data["review_id"] == 10
        assert "created_at" in data
    
    def test_to_dict_without_optional_fields(self):
        """Test conversion to dictionary without optional fields."""
        title = Title(story_id=1, version=0, text="Minimal Title")
        data = title.to_dict()
        
        assert data["id"] is None
        assert data["review_id"] is None
        assert data["story_id"] == 1
        assert data["version"] == 0
        assert data["text"] == "Minimal Title"
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "id": 5,
            "story_id": 2,
            "version": 3,
            "text": "Dictionary Title",
            "review_id": 15,
            "created_at": "2024-01-15T10:30:00"
        }
        title = Title.from_dict(data)
        
        assert title.id == 5
        assert title.story_id == 2
        assert title.version == 3
        assert title.text == "Dictionary Title"
        assert title.review_id == 15
    
    def test_from_dict_minimal(self):
        """Test creation from dictionary with minimal fields."""
        data = {
            "story_id": 1,
            "version": 0,
            "text": "Minimal Title"
        }
        title = Title.from_dict(data)
        
        assert title.id is None
        assert title.story_id == 1
        assert title.version == 0
        assert title.text == "Minimal Title"
        assert title.review_id is None
    
    def test_from_dict_datetime_parsing(self):
        """Test datetime parsing from ISO format string."""
        data = {
            "story_id": 1,
            "version": 0,
            "text": "Test",
            "created_at": "2024-06-15T14:30:00"
        }
        title = Title.from_dict(data)
        
        assert isinstance(title.created_at, datetime)
        assert title.created_at.year == 2024
        assert title.created_at.month == 6
        assert title.created_at.day == 15
    
    def test_roundtrip_dict(self):
        """Test to_dict and from_dict roundtrip."""
        original = Title(
            story_id=3,
            version=5,
            text="Roundtrip Title",
            review_id=20,
            id=100
        )
        
        data = original.to_dict()
        reconstructed = Title.from_dict(data)
        
        assert reconstructed.id == original.id
        assert reconstructed.story_id == original.story_id
        assert reconstructed.version == original.version
        assert reconstructed.text == original.text
        assert reconstructed.review_id == original.review_id
    
    def test_multiple_versions_same_story(self):
        """Test multiple title versions for same story."""
        titles = [
            Title(story_id=1, version=0, text="First Draft"),
            Title(story_id=1, version=1, text="Second Draft", review_id=1),
            Title(story_id=1, version=2, text="Final Title", review_id=2),
        ]
        
        assert len(titles) == 3
        assert all(t.story_id == 1 for t in titles)
        assert [t.version for t in titles] == [0, 1, 2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
