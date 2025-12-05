"""Tests for StoryReviewModel in T/Database/models.

Tests cover:
- Model creation and validation
- Version validation (must be >= 0, UINT simulation)
- Review type validation and conversion
- Serialization (to_dict) and deserialization (from_dict)
- SQL schema generation
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add the T/Database/models directory to path (before other paths to avoid conflicts)
database_models_path = str(Path(__file__).parent.parent.parent / "models")
if database_models_path in sys.path:
    sys.path.remove(database_models_path)
sys.path.insert(0, database_models_path)

# Import with explicit module reference to avoid conflicts with T/Review/Model/src/story_review.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "database_story_review", 
    Path(__file__).parent.parent.parent / "models" / "story_review.py"
)
database_story_review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database_story_review)

StoryReviewModel = database_story_review.StoryReviewModel
ReviewType = database_story_review.ReviewType


class TestReviewType:
    """Tests for ReviewType enum."""
    
    def test_all_review_types_exist(self):
        """Test all required review types are defined."""
        expected_types = ["grammar", "tone", "content", "consistency", "editing"]
        
        for type_name in expected_types:
            assert hasattr(ReviewType, type_name.upper())
            assert ReviewType(type_name).value == type_name
    
    def test_review_type_is_string_enum(self):
        """Test ReviewType inherits from str and Enum."""
        assert issubclass(ReviewType, str)
        assert isinstance(ReviewType.GRAMMAR, str)
        assert ReviewType.GRAMMAR == "grammar"


class TestStoryReviewModel:
    """Tests for StoryReviewModel."""
    
    def test_create_story_review(self):
        """Test creating a story review link."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=5,
            version=2,
            review_type=ReviewType.GRAMMAR
        )
        
        assert story_review.story_id == 1
        assert story_review.review_id == 5
        assert story_review.version == 2
        assert story_review.review_type == ReviewType.GRAMMAR
        assert story_review.id is None
        assert isinstance(story_review.created_at, datetime)
    
    def test_create_with_id(self):
        """Test creating with explicit id."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=1,
            review_type=ReviewType.GRAMMAR,
            id=42
        )
        assert story_review.id == 42
    
    def test_version_validation_negative(self):
        """Test version must be non-negative (UINT simulation)."""
        with pytest.raises(ValueError) as exc_info:
            StoryReviewModel(
                story_id=1,
                review_id=1,
                version=-1,
                review_type=ReviewType.GRAMMAR
            )
        assert "Version must be >= 0" in str(exc_info.value)
    
    def test_version_zero_allowed(self):
        """Test version 0 is allowed."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        assert story_review.version == 0
    
    def test_version_large_value(self):
        """Test large version values work."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=999999,
            review_type=ReviewType.GRAMMAR
        )
        assert story_review.version == 999999
    
    def test_review_type_from_string(self):
        """Test review_type can be created from string."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=1,
            review_type="tone"
        )
        assert story_review.review_type == ReviewType.TONE
    
    def test_review_type_invalid_string(self):
        """Test invalid review type string raises error."""
        with pytest.raises(ValueError):
            StoryReviewModel(
                story_id=1,
                review_id=1,
                version=1,
                review_type="invalid_type"
            )
    
    def test_all_review_types_work(self):
        """Test all review types can be used."""
        types = ["grammar", "tone", "content", "consistency", "editing"]
        
        for review_type in types:
            story_review = StoryReviewModel(
                story_id=1,
                review_id=1,
                version=1,
                review_type=review_type
            )
            assert story_review.review_type.value == review_type
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        created_at = datetime(2024, 1, 15, 10, 30, 0)
        story_review = StoryReviewModel(
            story_id=1,
            review_id=5,
            version=2,
            review_type=ReviewType.CONTENT,
            id=10,
            created_at=created_at
        )
        data = story_review.to_dict()
        
        assert data["story_id"] == 1
        assert data["review_id"] == 5
        assert data["version"] == 2
        assert data["review_type"] == "content"
        assert data["id"] == 10
        assert data["created_at"] == "2024-01-15T10:30:00"
    
    def test_to_dict_none_id(self):
        """Test to_dict with None id."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=1,
            review_type=ReviewType.GRAMMAR
        )
        data = story_review.to_dict()
        
        assert data["id"] is None
    
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
        story_review = StoryReviewModel.from_dict(data)
        
        assert story_review.story_id == 2
        assert story_review.review_id == 8
        assert story_review.version == 3
        assert story_review.review_type == ReviewType.EDITING
        assert story_review.id == 15
        assert story_review.created_at == datetime(2024, 1, 15, 10, 30, 0)
    
    def test_from_dict_minimal(self):
        """Test creation from dictionary with only required fields."""
        data = {
            "story_id": 1,
            "review_id": 1,
            "version": 0,
            "review_type": "grammar"
        }
        story_review = StoryReviewModel.from_dict(data)
        
        assert story_review.story_id == 1
        assert story_review.review_id == 1
        assert story_review.version == 0
        assert story_review.review_type == ReviewType.GRAMMAR
        assert story_review.id is None
        assert isinstance(story_review.created_at, datetime)
    
    def test_from_dict_with_enum_review_type(self):
        """Test from_dict handles ReviewType enum directly."""
        data = {
            "story_id": 1,
            "review_id": 1,
            "version": 1,
            "review_type": ReviewType.CONSISTENCY
        }
        story_review = StoryReviewModel.from_dict(data)
        
        assert story_review.review_type == ReviewType.CONSISTENCY
    
    def test_roundtrip_serialization(self):
        """Test to_dict -> from_dict roundtrip."""
        original = StoryReviewModel(
            story_id=5,
            review_id=10,
            version=3,
            review_type=ReviewType.TONE,
            id=100
        )
        
        data = original.to_dict()
        restored = StoryReviewModel.from_dict(data)
        
        assert restored.story_id == original.story_id
        assert restored.review_id == original.review_id
        assert restored.version == original.version
        assert restored.review_type == original.review_type
        assert restored.id == original.id


class TestStoryReviewModelSQL:
    """Tests for SQL schema generation."""
    
    def test_get_sql_schema(self):
        """Test SQL schema generation."""
        schema = StoryReviewModel.get_sql_schema()
        
        # Check table creation
        assert "CREATE TABLE" in schema
        assert "StoryReview" in schema
        
        # Check columns
        assert "id INTEGER PRIMARY KEY AUTOINCREMENT" in schema
        assert "story_id INTEGER NOT NULL" in schema
        assert "review_id INTEGER NOT NULL" in schema
        assert "version INTEGER NOT NULL" in schema
        assert "review_type TEXT NOT NULL" in schema
        assert "created_at TEXT NOT NULL" in schema
    
    def test_sql_schema_has_version_check(self):
        """Test SQL schema includes version >= 0 constraint."""
        schema = StoryReviewModel.get_sql_schema()
        assert "CHECK (version >= 0)" in schema
    
    def test_sql_schema_has_review_type_check(self):
        """Test SQL schema includes review_type CHECK constraint."""
        schema = StoryReviewModel.get_sql_schema()
        assert "grammar" in schema
        assert "tone" in schema
        assert "content" in schema
        assert "consistency" in schema
        assert "editing" in schema
    
    def test_sql_schema_has_foreign_keys(self):
        """Test SQL schema includes foreign key references."""
        schema = StoryReviewModel.get_sql_schema()
        assert "FOREIGN KEY (story_id) REFERENCES Story(id)" in schema
        assert "FOREIGN KEY (review_id) REFERENCES Review(id)" in schema
    
    def test_sql_schema_has_unique_constraint(self):
        """Test SQL schema includes unique constraint on (story_id, version, review_type)."""
        schema = StoryReviewModel.get_sql_schema()
        assert "UNIQUE(story_id, version, review_type)" in schema
    
    def test_sql_schema_has_performance_indexes(self):
        """Test SQL schema includes performance indexes."""
        schema = StoryReviewModel.get_sql_schema()
        assert "idx_storyreview_story_id" in schema
        assert "idx_storyreview_review_id" in schema
        assert "idx_storyreview_story_version" in schema


class TestStoryReviewModelIModel:
    """Tests for IModel interface implementation."""
    
    def test_get_id_returns_none_when_not_persisted(self):
        """Test get_id returns None for new model."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        assert story_review.get_id() is None
    
    def test_get_id_returns_id_when_set(self):
        """Test get_id returns the ID when set."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR,
            id=42
        )
        assert story_review.get_id() == 42
    
    def test_exists_returns_false_when_no_id(self):
        """Test exists returns False when model has no ID."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        assert story_review.exists() is False
    
    def test_exists_returns_true_when_has_id(self):
        """Test exists returns True when model has ID."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR,
            id=42
        )
        assert story_review.exists() is True
    
    def test_get_created_at_returns_datetime(self):
        """Test get_created_at returns datetime."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        assert isinstance(story_review.get_created_at(), datetime)
    
    def test_save_returns_true(self):
        """Test save returns True (actual persistence via repository)."""
        story_review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        assert story_review.save() is True
    
    def test_refresh_returns_exists_status(self):
        """Test refresh returns exists status."""
        # Without ID
        story_review1 = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        assert story_review1.refresh() is False
        
        # With ID
        story_review2 = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR,
            id=42
        )
        assert story_review2.refresh() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
