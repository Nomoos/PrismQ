"""Tests for Review model."""

import sys
from pathlib import Path
from datetime import datetime


def _find_project_root() -> Path:
    """Find project root by looking for pytest.ini marker file."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / 'pytest.ini').exists():
            return parent
    # Fallback to parents[5] for compatibility
    return Path(__file__).resolve().parents[5]


# Add project root to path
project_root = _find_project_root()
sys.path.insert(0, str(project_root))

import pytest
from T.Database.models.review import Review, MIN_SCORE, MAX_SCORE
from T.Database.models.base import IModel, IReadable


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
        created_at = datetime.fromisoformat("2025-01-15T10:30:00")
        review = Review(
            id=42,
            text="Excellent work on the dialogue.",
            score=9.0,
            created_at=created_at
        )
        
        assert review.id == 42
        assert review.text == "Excellent work on the dialogue."
        assert review.score == 9.0
        assert review.created_at == created_at
    
    def test_timestamps_auto_generated(self):
        """Test that timestamps are automatically generated."""
        review = Review(text="Test review", score=5.0)
        
        assert review.created_at is not None
        assert isinstance(review.created_at, datetime)
    
    def test_score_can_be_integer(self):
        """Test that score can be an integer value."""
        review = Review(text="Test review", score=8)
        assert review.score == 8
    
    def test_score_can_be_float(self):
        """Test that score can be a float value."""
        review = Review(text="Test review", score=7.5)
        assert review.score == 7.5
    
    def test_score_can_be_zero(self):
        """Test that score can be zero (min rating)."""
        review = Review(text="Poor content", score=0.0)
        assert review.score == MIN_SCORE
    
    def test_score_can_be_ten(self):
        """Test that score can be ten (max rating)."""
        review = Review(text="Perfect!", score=10.0)
        assert review.score == MAX_SCORE
    
    def test_invalid_score_type_raises_error(self):
        """Test that non-numeric score raises TypeError."""
        with pytest.raises(TypeError):
            Review(text="Test", score="invalid")
    
    def test_score_below_min_raises_error(self):
        """Test that score below MIN_SCORE raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            Review(text="Test", score=-1.0)
        assert "score must be between" in str(exc_info.value)
    
    def test_score_above_max_raises_error(self):
        """Test that score above MAX_SCORE raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            Review(text="Test", score=11.0)
        assert "score must be between" in str(exc_info.value)


class TestReviewIModelInterface:
    """Test IModel interface implementation."""
    
    def test_review_is_imodel(self):
        """Test that Review implements IModel."""
        review = Review(text="Test", score=5.0)
        assert isinstance(review, IModel)
    
    def test_review_is_ireadable(self):
        """Test that Review implements IReadable."""
        review = Review(text="Test", score=5.0)
        assert isinstance(review, IReadable)
    
    def test_get_id_returns_none_when_not_persisted(self):
        """Test get_id returns None for new review."""
        review = Review(text="Test", score=5.0)
        assert review.get_id() is None
    
    def test_get_id_returns_id_when_set(self):
        """Test get_id returns ID when set."""
        review = Review(id=42, text="Test", score=5.0)
        assert review.get_id() == 42
    
    def test_exists_returns_false_when_not_persisted(self):
        """Test exists returns False for new review."""
        review = Review(text="Test", score=5.0)
        assert review.exists() is False
    
    def test_exists_returns_true_when_has_id(self):
        """Test exists returns True when review has ID."""
        review = Review(id=1, text="Test", score=5.0)
        assert review.exists() is True
    
    def test_get_created_at_returns_datetime(self):
        """Test get_created_at returns datetime."""
        review = Review(text="Test", score=5.0)
        assert isinstance(review.get_created_at(), datetime)
    
    def test_save_returns_true(self):
        """Test save returns True (placeholder)."""
        review = Review(text="Test", score=5.0)
        assert review.save() is True
    
    def test_refresh_returns_exists_status(self):
        """Test refresh returns exists status."""
        review_new = Review(text="Test", score=5.0)
        assert review_new.refresh() is False
        
        review_existing = Review(id=1, text="Test", score=5.0)
        assert review_existing.refresh() is True


class TestReviewSerialization:
    """Test serialization and deserialization."""
    
    def test_to_dict(self):
        """Test converting Review to dictionary."""
        created_at = datetime.fromisoformat("2025-01-15T10:00:00")
        review = Review(
            id=1,
            text="Good work on the narrative flow.",
            score=8.5,
            created_at=created_at
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
        assert isinstance(review.created_at, datetime)
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with missing fields uses defaults."""
        data = {"text": "Minimal review"}
        
        review = Review.from_dict(data)
        
        assert review.text == "Minimal review"
        assert review.score == 0.0
        assert review.id is None
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
        # Compare ISO strings for datetime comparison
        assert restored.to_dict()["created_at"] == original.to_dict()["created_at"]


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
