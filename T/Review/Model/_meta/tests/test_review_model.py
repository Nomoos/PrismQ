"""Tests for Review and StoryReview models."""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from review import Review
from story_review import StoryReview, ReviewType


class TestReview:
    """Tests for Review model."""
    
    def test_create_review(self):
        """Test creating a basic review."""
        review = Review(text="Great title!", score=85)
        
        assert review.text == "Great title!"
        assert review.score == 85
        assert review.id is None
        assert isinstance(review.created_at, datetime)
    
    def test_review_without_score(self):
        """Test review without score."""
        review = Review(text="Needs improvement")
        
        assert review.text == "Needs improvement"
        assert review.score is None
    
    def test_review_score_validation(self):
        """Test score must be 0-100."""
        with pytest.raises(ValueError):
            Review(text="Invalid", score=101)
        
        with pytest.raises(ValueError):
            Review(text="Invalid", score=-1)
    
    def test_review_to_dict(self):
        """Test conversion to dictionary."""
        review = Review(text="Good", score=75, id=1)
        data = review.to_dict()
        
        assert data["text"] == "Good"
        assert data["score"] == 75
        assert data["id"] == 1
        assert "created_at" in data
    
    def test_review_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "text": "Excellent",
            "score": 95,
            "id": 5,
            "created_at": "2024-01-15T10:30:00"
        }
        review = Review.from_dict(data)
        
        assert review.text == "Excellent"
        assert review.score == 95
        assert review.id == 5


class TestStoryReview:
    """Tests for StoryReview model."""
    
    def test_create_story_review(self):
        """Test creating a story review link."""
        story_review = StoryReview(
            story_id=1,
            review_id=5,
            version=2,
            review_type=ReviewType.GRAMMAR
        )
        
        assert story_review.story_id == 1
        assert story_review.review_id == 5
        assert story_review.version == 2
        assert story_review.review_type == ReviewType.GRAMMAR
    
    def test_version_validation(self):
        """Test version must be non-negative (UINT simulation)."""
        with pytest.raises(ValueError):
            StoryReview(story_id=1, review_id=1, version=-1, review_type=ReviewType.GRAMMAR)
    
    def test_version_zero_allowed(self):
        """Test version 0 is allowed."""
        story_review = StoryReview(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        assert story_review.version == 0
    
    def test_review_type_from_string(self):
        """Test review_type can be created from string."""
        story_review = StoryReview(
            story_id=1,
            review_id=1,
            version=1,
            review_type="tone"
        )
        assert story_review.review_type == ReviewType.TONE
    
    def test_all_review_types(self):
        """Test all review types are valid."""
        types = ["grammar", "tone", "content", "consistency", "editing"]
        
        for review_type in types:
            story_review = StoryReview(
                story_id=1,
                review_id=1,
                version=1,
                review_type=review_type
            )
            assert story_review.review_type.value == review_type
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        story_review = StoryReview(
            story_id=1,
            review_id=5,
            version=2,
            review_type=ReviewType.CONTENT,
            id=10
        )
        data = story_review.to_dict()
        
        assert data["story_id"] == 1
        assert data["review_id"] == 5
        assert data["version"] == 2
        assert data["review_type"] == "content"
        assert data["id"] == 10
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "story_id": 2,
            "review_id": 8,
            "version": 3,
            "review_type": "editing",
            "id": 15,
            "created_at": "2024-01-15T10:30:00"
        }
        story_review = StoryReview.from_dict(data)
        
        assert story_review.story_id == 2
        assert story_review.review_id == 8
        assert story_review.version == 3
        assert story_review.review_type == ReviewType.EDITING
        assert story_review.id == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
