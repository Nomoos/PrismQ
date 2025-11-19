"""Tests for IdeaInspirationExtractor."""

import pytest
from src.classification import IdeaInspirationExtractor, IdeaInspiration


class TestIdeaInspirationExtractor:
    """Test IdeaInspirationExtractor functionality."""
    
    def test_initialization(self):
        """Test extractor initialization."""
        extractor = IdeaInspirationExtractor()
        assert extractor is not None
    
    def test_extract_from_text(self):
        """Test extraction from text content."""
        extractor = IdeaInspirationExtractor()
        
        inspiration = extractor.extract_from_text(
            title="Article Title",
            description="Article description",
            body="This is the full article body text.",
            tags=["#article", "blog", "content"]
        )
        
        assert inspiration.title == "Article Title"
        assert inspiration.description == "Article description"
        assert inspiration.content == "This is the full article body text."
        assert inspiration.source_type == "text"
        assert "article" in inspiration.keywords
        assert "blog" in inspiration.keywords
        assert "content" in inspiration.keywords
    
    def test_extract_from_video(self):
        """Test extraction from video content."""
        extractor = IdeaInspirationExtractor()
        
        inspiration = extractor.extract_from_video(
            title="Video Title",
            description="Video description",
            subtitle_text="This is the subtitle text from the video.",
            tags=["video", "shorts", "entertainment"]
        )
        
        assert inspiration.title == "Video Title"
        assert inspiration.description == "Video description"
        assert inspiration.content == "This is the subtitle text from the video."
        assert inspiration.source_type == "video"
        assert "video" in inspiration.keywords
        assert "shorts" in inspiration.keywords
    
    def test_extract_from_audio(self):
        """Test extraction from audio content."""
        extractor = IdeaInspirationExtractor()
        
        inspiration = extractor.extract_from_audio(
            title="Podcast Episode",
            description="Episode description",
            transcription="This is the transcribed audio text.",
            tags=["podcast", "audio", "interview"]
        )
        
        assert inspiration.title == "Podcast Episode"
        assert inspiration.description == "Episode description"
        assert inspiration.content == "This is the transcribed audio text."
        assert inspiration.source_type == "audio"
        assert "podcast" in inspiration.keywords
        assert "audio" in inspiration.keywords
    
    def test_extract_from_metadata_video(self):
        """Test auto-detection and extraction from video metadata."""
        extractor = IdeaInspirationExtractor()
        
        metadata = {
            'title': 'Auto Video',
            'description': 'Auto detected video',
            'subtitle_text': 'Video subtitles here',
            'tags': ['auto', 'video']
        }
        
        inspiration = extractor.extract_from_metadata(metadata)
        
        assert inspiration.title == "Auto Video"
        assert inspiration.content == "Video subtitles here"
        assert inspiration.source_type == "video"
    
    def test_extract_from_metadata_audio(self):
        """Test auto-detection and extraction from audio metadata."""
        extractor = IdeaInspirationExtractor()
        
        metadata = {
            'title': 'Auto Audio',
            'description': 'Auto detected audio',
            'transcription': 'Audio transcription here',
            'tags': ['auto', 'audio']
        }
        
        inspiration = extractor.extract_from_metadata(metadata)
        
        assert inspiration.title == "Auto Audio"
        assert inspiration.content == "Audio transcription here"
        assert inspiration.source_type == "audio"
    
    def test_extract_from_metadata_text_default(self):
        """Test default text extraction from metadata."""
        extractor = IdeaInspirationExtractor()
        
        metadata = {
            'title': 'Text Content',
            'description': 'Text description',
            'body': 'Body text here',
            'tags': ['text']
        }
        
        inspiration = extractor.extract_from_metadata(metadata)
        
        assert inspiration.title == "Text Content"
        assert inspiration.content == "Body text here"
        assert inspiration.source_type == "text"
    
    def test_extract_keywords_from_tags(self):
        """Test keyword extraction from tags."""
        extractor = IdeaInspirationExtractor()
        
        tags = ["#hashtag", "normal", "  spaces  ", "#", "a"]
        keywords = extractor._extract_keywords_from_tags(tags)
        
        assert "hashtag" in keywords
        assert "normal" in keywords
        assert "spaces" in keywords
        assert "#" not in keywords  # Too short
        assert "a" not in keywords  # Too short
    
    def test_extract_keywords_from_text(self):
        """Test keyword extraction from text."""
        extractor = IdeaInspirationExtractor()
        
        text = "This is a story about coding and programming with Python and JavaScript"
        keywords = extractor.extract_keywords_from_text(text, max_keywords=5)
        
        assert len(keywords) <= 5
        # Should exclude stop words like "this", "is", "a", "about", "and", "with"
        assert "this" not in keywords
        assert "story" in keywords or "coding" in keywords or "programming" in keywords
    
    def test_extract_keywords_from_empty_text(self):
        """Test keyword extraction from empty text."""
        extractor = IdeaInspirationExtractor()
        
        keywords = extractor.extract_keywords_from_text("")
        assert keywords == []
    
    def test_extract_keywords_min_length(self):
        """Test keyword extraction respects min_length."""
        extractor = IdeaInspirationExtractor()
        
        text = "a ab abc abcd abcde"
        keywords = extractor.extract_keywords_from_text(text, min_length=4)
        
        assert "a" not in keywords
        assert "ab" not in keywords
        assert "abc" not in keywords
        assert "abcd" in keywords
        assert "abcde" in keywords
