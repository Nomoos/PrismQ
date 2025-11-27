"""Tests for Script model.

Tests cover:
- Script creation with required and optional fields
- Version validation (non-negative INTEGER)
- Serialization to/from dictionary
- Data transfer methods (to_dict/from_dict)
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add models to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "models"))

from script import Script


class TestScript:
    """Tests for Script model."""
    
    def test_create_script(self):
        """Test creating a basic script."""
        script = Script(
            story_id=1,
            version=0,
            text="Once upon a time..."
        )
        
        assert script.story_id == 1
        assert script.version == 0
        assert script.text == "Once upon a time..."
        assert script.review_id is None
        assert script.id is None
        assert isinstance(script.created_at, datetime)
    
    def test_create_script_with_review(self):
        """Test creating a script with review reference."""
        script = Script(
            story_id=1,
            version=1,
            text="Revised content...",
            review_id=5
        )
        
        assert script.story_id == 1
        assert script.version == 1
        assert script.text == "Revised content..."
        assert script.review_id == 5
    
    def test_create_script_with_id(self):
        """Test creating a script with explicit ID."""
        script = Script(
            story_id=1,
            version=0,
            text="Content",
            id=42
        )
        
        assert script.id == 42
    
    def test_version_validation_negative(self):
        """Test version must be non-negative (UINT simulation)."""
        with pytest.raises(ValueError, match="Version must be >= 0"):
            Script(story_id=1, version=-1, text="Invalid")
    
    def test_version_zero_allowed(self):
        """Test version 0 is allowed (initial version)."""
        script = Script(story_id=1, version=0, text="First version")
        assert script.version == 0
    
    def test_version_large_number(self):
        """Test large version numbers are allowed."""
        script = Script(story_id=1, version=999, text="Many revisions")
        assert script.version == 999
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        script = Script(
            story_id=1,
            version=2,
            text="Script content",
            review_id=5,
            id=10
        )
        data = script.to_dict()
        
        assert data["story_id"] == 1
        assert data["version"] == 2
        assert data["text"] == "Script content"
        assert data["review_id"] == 5
        assert data["id"] == 10
        assert "created_at" in data
    
    def test_to_dict_without_optional_fields(self):
        """Test to_dict with None optional fields."""
        script = Script(story_id=1, version=0, text="Content")
        data = script.to_dict()
        
        assert data["id"] is None
        assert data["review_id"] is None
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "story_id": 2,
            "version": 3,
            "text": "From dictionary",
            "review_id": 8,
            "id": 15,
            "created_at": "2024-01-15T10:30:00"
        }
        script = Script.from_dict(data)
        
        assert script.story_id == 2
        assert script.version == 3
        assert script.text == "From dictionary"
        assert script.review_id == 8
        assert script.id == 15
        assert script.created_at == datetime.fromisoformat("2024-01-15T10:30:00")
    
    def test_from_dict_minimal(self):
        """Test from_dict with only required fields."""
        data = {
            "story_id": 1,
            "version": 0,
            "text": "Minimal data"
        }
        script = Script.from_dict(data)
        
        assert script.story_id == 1
        assert script.version == 0
        assert script.text == "Minimal data"
        assert script.review_id is None
        assert script.id is None
    
    def test_roundtrip_serialization(self):
        """Test to_dict and from_dict roundtrip preserves data."""
        original = Script(
            story_id=5,
            version=10,
            text="Roundtrip test content",
            review_id=42,
            id=100
        )
        
        data = original.to_dict()
        restored = Script.from_dict(data)
        
        assert restored.story_id == original.story_id
        assert restored.version == original.version
        assert restored.text == original.text
        assert restored.review_id == original.review_id
        assert restored.id == original.id


class TestScriptDataTransferMethods:
    """Tests for Script data transfer methods (to_dict/from_dict)."""
    
    def test_script_has_id_attribute(self):
        """Test Script has id attribute for persistence."""
        script = Script(story_id=1, version=0, text="Test")
        assert hasattr(script, "id")
    
    def test_script_has_to_dict_method(self):
        """Test Script has to_dict method for serialization."""
        script = Script(story_id=1, version=0, text="Test")
        assert hasattr(script, "to_dict")
        assert callable(script.to_dict)
    
    def test_script_has_from_dict_method(self):
        """Test Script has from_dict classmethod for deserialization."""
        assert hasattr(Script, "from_dict")
        assert callable(Script.from_dict)
    
    def test_script_has_created_at_attribute(self):
        """Test Script has created_at attribute for timestamp tracking."""
        script = Script(story_id=1, version=0, text="Test")
        assert hasattr(script, "created_at")
        assert isinstance(script.created_at, datetime)


class TestScriptEdgeCases:
    """Edge case tests for Script model."""
    
    def test_empty_text(self):
        """Test script with empty text is allowed."""
        script = Script(story_id=1, version=0, text="")
        assert script.text == ""
    
    def test_long_text(self):
        """Test script with very long text."""
        long_text = "x" * 100000  # 100KB text
        script = Script(story_id=1, version=0, text=long_text)
        assert len(script.text) == 100000
    
    def test_unicode_text(self):
        """Test script with unicode characters."""
        unicode_text = "日本語テスト 🎬 émojis änd spëcial characters"
        script = Script(story_id=1, version=0, text=unicode_text)
        assert script.text == unicode_text
    
    def test_multiline_text(self):
        """Test script with multiline content."""
        multiline = """Scene 1:
        Character enters.
        
        Scene 2:
        Dialog begins."""
        script = Script(story_id=1, version=0, text=multiline)
        assert "Scene 1:" in script.text
        assert "Scene 2:" in script.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
