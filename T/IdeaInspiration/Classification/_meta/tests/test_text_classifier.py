"""Tests for TextClassifier."""

import pytest
from src.classification import (
    TextClassifier,
    IdeaInspiration,
    IdeaInspirationBuilder,
    PrimaryCategory
)


class TestTextClassifier:
    """Test TextClassifier functionality."""
    
    def test_initialization(self):
        """Test classifier initialization."""
        classifier = TextClassifier()
        assert classifier is not None
        assert classifier.category_classifier is not None
        assert classifier.story_detector is not None
    
    def test_classify_story_content(self):
        """Test classification of story content."""
        classifier = TextClassifier()
        
        inspiration = IdeaInspiration(
            title="My AITA Story - Was I Wrong?",
            description="This is my true story about what happened",
            content="Let me tell you about my experience...",
            keywords=["story", "aita", "confession"]
        )
        
        result = classifier.classify(inspiration)
        
        assert result.category == PrimaryCategory.STORYTELLING
        assert result.is_story is True
        assert result.story_confidence > 0.0
        assert len(result.indicators) > 0
    
    def test_classify_entertainment_content(self):
        """Test classification of entertainment content."""
        classifier = TextClassifier()
        
        inspiration = IdeaInspiration(
            title="Funniest Meme Compilation",
            description="Hilarious memes that will make you laugh",
            keywords=["comedy", "funny", "memes"]
        )
        
        result = classifier.classify(inspiration)
        
        assert result.category == PrimaryCategory.ENTERTAINMENT
        assert result.combined_score > 0.0
    
    def test_classify_education_content(self):
        """Test classification of educational content."""
        classifier = TextClassifier()
        
        inspiration = IdeaInspiration(
            title="How to Learn Python Programming",
            description="Tutorial for beginners on Python coding",
            keywords=["tutorial", "education", "programming"]
        )
        
        result = classifier.classify(inspiration)
        
        assert result.category == PrimaryCategory.EDUCATION
    
    def test_classify_text_fields_directly(self):
        """Test classification without creating IdeaInspiration."""
        classifier = TextClassifier()
        
        result = classifier.classify_text_fields(
            title="Gaming Highlights",
            description="Epic gameplay moments",
            keywords=["gaming", "fortnite", "gameplay"]
        )
        
        assert result.category == PrimaryCategory.GAMING
    
    def test_classify_batch(self):
        """Test batch classification."""
        classifier = TextClassifier()
        
        inspirations = [
            IdeaInspiration(title="Story Time", keywords=["story"]),
            IdeaInspiration(title="Funny Meme", keywords=["comedy"]),
            IdeaInspiration(title="Tutorial", keywords=["tutorial"])
        ]
        
        results = classifier.classify_batch(inspirations)
        
        assert len(results) == 3
        assert results[0].category == PrimaryCategory.STORYTELLING
        assert results[1].category == PrimaryCategory.ENTERTAINMENT
        assert results[2].category == PrimaryCategory.EDUCATION
    
    def test_field_scores(self):
        """Test field scoring functionality."""
        classifier = TextClassifier()
        
        inspiration = IdeaInspiration(
            title="Long Title With Many Words",
            description="This is a longer description with more content",
            content="Even more content in the body text here",
            keywords=["key1", "key2", "key3"]
        )
        
        result = classifier.classify(inspiration)
        
        assert 'title' in result.field_scores
        assert 'description' in result.field_scores
        assert 'content' in result.field_scores
        assert 'keywords' in result.field_scores
        
        # All scores should be between 0 and 1
        for score in result.field_scores.values():
            assert 0.0 <= score <= 1.0
    
    def test_combined_score(self):
        """Test combined score calculation."""
        classifier = TextClassifier()
        
        inspiration = IdeaInspiration(
            title="Quality Content Title",
            description="Quality description text",
            content="Quality body content",
            keywords=["quality", "content"]
        )
        
        result = classifier.classify(inspiration)
        
        assert 0.0 <= result.combined_score <= 1.0
    
    def test_classify_video_source(self):
        """Test classification of video source type."""
        classifier = TextClassifier()
        
        inspiration = IdeaInspiration(
            title="Video Title",
            description="Video description",
            content="This is subtitle text from video",
            source_type="video",
            keywords=["video"]
        )
        
        result = classifier.classify(inspiration)
        
        # Should still classify correctly
        assert result.category is not None
        assert result.combined_score > 0.0
    
    def test_classify_audio_source(self):
        """Test classification of audio source type."""
        classifier = TextClassifier()
        
        inspiration = IdeaInspiration(
            title="Podcast Episode",
            description="Podcast description",
            content="This is the transcription from audio",
            source_type="audio",
            keywords=["podcast"]
        )
        
        result = classifier.classify(inspiration)
        
        assert result.category is not None
        assert result.combined_score > 0.0
    
    def test_classification_result_attributes(self):
        """Test all TextClassificationResult attributes are present."""
        classifier = TextClassifier()
        
        inspiration = IdeaInspiration(
            title="Test",
            keywords=["test"]
        )
        
        result = classifier.classify(inspiration)
        
        # Check all expected attributes exist
        assert hasattr(result, 'category')
        assert hasattr(result, 'is_story')
        assert hasattr(result, 'story_confidence')
        assert hasattr(result, 'field_scores')
        assert hasattr(result, 'combined_score')
        assert hasattr(result, 'indicators')
        
        assert isinstance(result.category, PrimaryCategory)
        assert isinstance(result.is_story, bool)
        assert isinstance(result.story_confidence, float)
        assert isinstance(result.field_scores, dict)
        assert isinstance(result.combined_score, float)
        assert isinstance(result.indicators, list)
