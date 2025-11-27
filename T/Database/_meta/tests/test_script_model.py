"""Tests for Script model.

Tests cover:
- Script creation with required and optional fields
- Version validation (non-negative INTEGER)
- Serialization to/from dictionary
- IModel interface implementation (get_id, exists, save, refresh)
- Version management (create_next_version)
- Data transfer methods (to_dict/from_dict)
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from T.Database.models.script import Script
from T.Database.models.base import IModel, IReadable


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


class TestScriptIModelInterface:
    """Tests for Script IModel interface implementation."""
    
    def test_script_is_imodel(self):
        """Test Script is an IModel."""
        script = Script(story_id=1, version=0, text="Test")
        assert isinstance(script, IModel)
    
    def test_script_is_ireadable(self):
        """Test Script is an IReadable."""
        script = Script(story_id=1, version=0, text="Test")
        assert isinstance(script, IReadable)
    
    def test_get_id_returns_none_when_not_persisted(self):
        """Test get_id returns None for new script."""
        script = Script(story_id=1, version=0, text="Test")
        assert script.get_id() is None
    
    def test_get_id_returns_id_when_set(self):
        """Test get_id returns ID when script has one."""
        script = Script(story_id=1, version=0, text="Test", id=42)
        assert script.get_id() == 42
    
    def test_exists_returns_false_when_not_persisted(self):
        """Test exists returns False for new script."""
        script = Script(story_id=1, version=0, text="Test")
        assert script.exists() is False
    
    def test_exists_returns_true_when_has_id(self):
        """Test exists returns True when script has ID."""
        script = Script(story_id=1, version=0, text="Test", id=42)
        assert script.exists() is True
    
    def test_get_created_at_returns_datetime(self):
        """Test get_created_at returns the creation timestamp."""
        script = Script(story_id=1, version=0, text="Test")
        assert isinstance(script.get_created_at(), datetime)
    
    def test_save_returns_true(self):
        """Test save returns True (placeholder for repository)."""
        script = Script(story_id=1, version=0, text="Test")
        assert script.save() is True
    
    def test_refresh_returns_exists_status(self):
        """Test refresh returns whether script exists."""
        script_new = Script(story_id=1, version=0, text="Test")
        assert script_new.refresh() is False
        
        script_existing = Script(story_id=1, version=0, text="Test", id=42)
        assert script_existing.refresh() is True


class TestScriptVersionManagement:
    """Tests for Script version management."""
    
    def test_create_next_version_increments_version(self):
        """Test create_next_version increments version number."""
        script_v0 = Script(story_id=1, version=0, text="Original")
        script_v1 = script_v0.create_next_version("Improved")
        
        assert script_v1.version == 1
    
    def test_create_next_version_updates_text(self):
        """Test create_next_version uses new text."""
        script_v0 = Script(story_id=1, version=0, text="Original")
        script_v1 = script_v0.create_next_version("New content")
        
        assert script_v1.text == "New content"
    
    def test_create_next_version_with_review_id(self):
        """Test create_next_version can set review_id."""
        script_v0 = Script(story_id=1, version=0, text="Original")
        script_v1 = script_v0.create_next_version("Reviewed content", review_id=5)
        
        assert script_v1.review_id == 5
    
    def test_create_next_version_preserves_story_id(self):
        """Test create_next_version preserves story_id."""
        script_v0 = Script(story_id=42, version=0, text="Original")
        script_v1 = script_v0.create_next_version("New content")
        
        assert script_v1.story_id == 42
    
    def test_create_next_version_chain(self):
        """Test creating multiple versions in sequence."""
        script_v0 = Script(story_id=1, version=0, text="v0")
        script_v1 = script_v0.create_next_version("v1")
        script_v2 = script_v1.create_next_version("v2")
        script_v3 = script_v2.create_next_version("v3")
        
        assert script_v3.version == 3
        assert script_v3.text == "v3"
    
    def test_create_next_version_is_new_instance(self):
        """Test create_next_version creates a new Script instance."""
        script_v0 = Script(story_id=1, version=0, text="Original")
        script_v1 = script_v0.create_next_version("New content")
        
        assert script_v0 is not script_v1
        assert script_v0.text == "Original"  # Original unchanged
    
    def test_get_version_info(self):
        """Test get_version_info returns formatted string."""
        script = Script(story_id=42, version=5, text="Content")
        info = script.get_version_info()
        
        assert info == "v5 (story_id=42)"
    
    def test_get_version_info_initial_version(self):
        """Test get_version_info for initial version."""
        script = Script(story_id=1, version=0, text="Content")
        info = script.get_version_info()
        
        assert info == "v0 (story_id=1)"


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
