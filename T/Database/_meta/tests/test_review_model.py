"""Tests for Review model."""

import pytest
from datetime import datetime
from models.review import Review


class TestReviewBasic:
    """Test basic Review functionality."""
    
    def test_create_basic_review(self):
        """Test creating a basic Review instance."""
        review = Review(
            text="Great story structure, but pacing needs work.",
            score=7.5
        )
        
        assert review.text == "Great story structure, but pacing needs work."
        assert review.score == 7.5
        assert review.id is None
        assert review.created_at is not None
    
    def test_create_with_all_fields(self):
        """Test creating Review with all fields specified."""
        review = Review(
            id=42,
            text="Excellent work on the dialogue.",
            score=9.0,
            created_at="2025-01-15T10:30:00"
        )
        
        assert review.id == 42
        assert review.text == "Excellent work on the dialogue."
        assert review.score == 9.0
        assert review.created_at == "2025-01-15T10:30:00"
    
    def test_timestamps_auto_generated(self):
        """Test that timestamps are automatically generated."""
        review = Review(text="Test review", score=5.0)
        
        assert review.created_at is not None
        
        # Verify ISO format
        try:
            datetime.fromisoformat(review.created_at)
        except ValueError:
            pytest.fail("Timestamp should be in ISO format")
    
    def test_score_can_be_integer(self):
        """Test that score can be an integer value."""
        review = Review(text="Test review", score=8)
        assert review.score == 8
    
    def test_score_can_be_float(self):
        """Test that score can be a float value."""
        review = Review(text="Test review", score=7.5)
        assert review.score == 7.5
    
    def test_score_can_be_zero(self):
        """Test that score can be zero."""
        review = Review(text="Poor content", score=0.0)
        assert review.score == 0.0
    
    def test_score_can_be_ten(self):
        """Test that score can be ten (max rating)."""
        review = Review(text="Perfect!", score=10.0)
        assert review.score == 10.0
    
    def test_invalid_score_type_raises_error(self):
        """Test that non-numeric score raises TypeError."""
        with pytest.raises(TypeError):
            Review(text="Test", score="invalid")


class TestReviewSerialization:
    """Test serialization and deserialization."""
    
    def test_to_dict(self):
        """Test converting Review to dictionary."""
        review = Review(
            id=1,
            text="Good work on the narrative flow.",
            score=8.5,
            created_at="2025-01-15T10:00:00"
        )
        
        data = review.to_dict()
        
        assert isinstance(data, dict)
        assert data["id"] == 1
        assert data["text"] == "Good work on the narrative flow."
        assert data["score"] == 8.5
        assert data["created_at"] == "2025-01-15T10:00:00"
    
    def test_from_dict(self):
        """Test creating Review from dictionary."""
        data = {
            "id": 5,
            "text": "Needs more detail in the character development.",
            "score": 6.0,
            "created_at": "2025-01-15T12:00:00"
        }
        
        review = Review.from_dict(data)
        
        assert review.id == 5
        assert review.text == "Needs more detail in the character development."
        assert review.score == 6.0
        assert review.created_at == "2025-01-15T12:00:00"
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with missing fields uses defaults."""
        data = {"text": "Minimal review"}
        
        review = Review.from_dict(data)
        
        assert review.text == "Minimal review"
        assert review.score == 0.0
        assert review.id is None
        # created_at is set by __post_init__ if None from dict
        assert review.created_at is not None
    
    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = Review(
            text="Comprehensive review with detailed feedback.",
            score=8.0,
        )
        
        # Roundtrip
        data = original.to_dict()
        restored = Review.from_dict(data)
        
        assert restored.text == original.text
        assert restored.score == original.score
        assert restored.created_at == original.created_at


class TestReviewRepresentation:
    """Test string representation."""
    
    def test_repr_short_text(self):
        """Test __repr__ with short text."""
        review = Review(id=1, text="Short review", score=7.0)
        
        repr_str = repr(review)
        
        assert "Review" in repr_str
        assert "id=1" in repr_str
        assert "score=7.0" in repr_str
        assert "Short review" in repr_str
    
    def test_repr_long_text_truncated(self):
        """Test __repr__ truncates long text."""
        long_text = "A" * 100
        review = Review(text=long_text, score=5.5)
        
        repr_str = repr(review)
        
        assert "..." in repr_str
        assert len(repr_str) < 150
