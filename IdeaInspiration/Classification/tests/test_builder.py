"""Tests for IdeaInspirationBuilder."""

import pytest
from datetime import datetime
from prismq.idea.classification import IdeaInspirationBuilder, IdeaInspiration


class TestIdeaInspirationBuilder:
    """Test IdeaInspirationBuilder functionality."""
    
    def test_initialization(self):
        """Test builder initialization."""
        builder = IdeaInspirationBuilder()
        assert builder is not None
    
    def test_build_minimal(self):
        """Test building with minimal fields."""
        builder = IdeaInspirationBuilder()
        inspiration = builder.set_title("Test Title").build()
        
        assert inspiration.title == "Test Title"
        assert inspiration.description == ""
        assert inspiration.content == ""
    
    def test_build_full(self):
        """Test building with all fields."""
        builder = IdeaInspirationBuilder()
        created_at = datetime(2025, 10, 13, 12, 0, 0)
        
        inspiration = (builder
            .set_title("Full Title")
            .set_description("Full description")
            .set_content("Full content")
            .add_keyword("key1")
            .add_keyword("key2")
            .set_source_type("video")
            .add_metadata("test", "value")
            .set_created_at(created_at)
            .build())
        
        assert inspiration.title == "Full Title"
        assert inspiration.description == "Full description"
        assert inspiration.content == "Full content"
        assert "key1" in inspiration.keywords
        assert "key2" in inspiration.keywords
        assert inspiration.source_type == "video"
        assert inspiration.metadata["test"] == "value"
        assert inspiration.created_at == created_at
    
    def test_chainable_methods(self):
        """Test that methods are chainable."""
        builder = IdeaInspirationBuilder()
        result = (builder
            .set_title("Test")
            .set_description("Desc")
            .set_content("Content"))
        
        assert result is builder
    
    def test_set_keywords_replaces(self):
        """Test set_keywords replaces existing keywords."""
        builder = IdeaInspirationBuilder()
        builder.set_title("Test")
        builder.add_keyword("old")
        builder.set_keywords(["new1", "new2"])
        
        inspiration = builder.build()
        assert "old" not in inspiration.keywords
        assert "new1" in inspiration.keywords
        assert "new2" in inspiration.keywords
    
    def test_add_keywords_no_duplicates(self):
        """Test add_keyword avoids duplicates."""
        builder = IdeaInspirationBuilder()
        builder.set_title("Test")
        builder.add_keyword("test")
        builder.add_keyword("test")
        
        inspiration = builder.build()
        assert inspiration.keywords.count("test") == 1
    
    def test_add_keywords_multiple(self):
        """Test add_keywords adds multiple keywords."""
        builder = IdeaInspirationBuilder()
        builder.set_title("Test")
        builder.add_keywords(["key1", "key2", "key3"])
        
        inspiration = builder.build()
        assert "key1" in inspiration.keywords
        assert "key2" in inspiration.keywords
        assert "key3" in inspiration.keywords
    
    def test_extract_keywords_from_content(self):
        """Test automatic keyword extraction."""
        builder = IdeaInspirationBuilder()
        builder.set_title("Story about programming")
        builder.set_description("Learn Python coding")
        builder.set_content("This is content about software development")
        builder.extract_keywords_from_content(max_keywords=5)
        
        inspiration = builder.build()
        assert len(inspiration.keywords) > 0
    
    def test_extract_keywords_merge(self):
        """Test keyword extraction merges with existing."""
        builder = IdeaInspirationBuilder()
        builder.add_keyword("existing")
        builder.set_title("Story about programming")
        builder.extract_keywords_from_content(merge_with_existing=True)
        
        inspiration = builder.build()
        assert "existing" in inspiration.keywords
    
    def test_extract_keywords_replace(self):
        """Test keyword extraction replaces existing."""
        builder = IdeaInspirationBuilder()
        builder.add_keyword("existing")
        builder.set_title("Story about programming")
        builder.extract_keywords_from_content(merge_with_existing=False)
        
        inspiration = builder.build()
        assert "existing" not in inspiration.keywords
    
    def test_from_metadata_dict_basic(self):
        """Test building from metadata dictionary."""
        builder = IdeaInspirationBuilder()
        metadata = {
            'title': 'Meta Title',
            'description': 'Meta description',
            'content': 'Meta content',
            'tags': ['tag1', 'tag2']
        }
        
        inspiration = builder.from_metadata_dict(metadata).build()
        
        assert inspiration.title == "Meta Title"
        assert inspiration.description == "Meta description"
        assert inspiration.content == "Meta content"
        assert "tag1" in inspiration.keywords
        assert "tag2" in inspiration.keywords
    
    def test_from_metadata_dict_video(self):
        """Test metadata dict detects video type."""
        builder = IdeaInspirationBuilder()
        metadata = {
            'title': 'Video',
            'subtitle_text': 'Subtitles',
            'tags': ['video']
        }
        
        inspiration = builder.from_metadata_dict(metadata).build()
        
        assert inspiration.source_type == "video"
        assert inspiration.content == "Subtitles"
    
    def test_from_metadata_dict_audio(self):
        """Test metadata dict detects audio type."""
        builder = IdeaInspirationBuilder()
        metadata = {
            'title': 'Audio',
            'transcription': 'Transcript',
            'tags': ['audio']
        }
        
        inspiration = builder.from_metadata_dict(metadata).build()
        
        assert inspiration.source_type == "audio"
        assert inspiration.content == "Transcript"
    
    def test_validate_success(self):
        """Test validation succeeds with content."""
        builder = IdeaInspirationBuilder()
        builder.set_title("Test")
        
        assert builder.validate() is True
    
    def test_validate_failure(self):
        """Test validation fails without content."""
        builder = IdeaInspirationBuilder()
        
        assert builder.validate() is False
    
    def test_build_validation_error(self):
        """Test build raises error on invalid content."""
        builder = IdeaInspirationBuilder()
        
        with pytest.raises(ValueError):
            builder.build()
    
    def test_reset(self):
        """Test reset clears all fields."""
        builder = IdeaInspirationBuilder()
        builder.set_title("Test").set_description("Desc").add_keyword("key")
        builder.reset()
        
        # After reset, should fail validation
        assert builder.validate() is False
    
    def test_multiple_builds(self):
        """Test builder can be used for multiple builds."""
        builder = IdeaInspirationBuilder()
        
        # First build
        inspiration1 = builder.set_title("First").build()
        assert inspiration1.title == "First"
        
        # Reset and build again
        inspiration2 = builder.reset().set_title("Second").build()
        assert inspiration2.title == "Second"
        
        # First inspiration should be unchanged
        assert inspiration1.title == "First"
