"""Tests for StoryReviewRepository.

Tests cover:
- Insert operations
- Find operations (by id, story_id, version, type)
- Database constraint enforcement
- Query performance with indexes
"""

import pytest
import sqlite3
from datetime import datetime
import sys
from pathlib import Path

# Add the repository to path
repo_path = str(Path(__file__).parent.parent.parent.parent.parent)
if repo_path not in sys.path:
    sys.path.insert(0, repo_path)

from Model.Database.repositories.story_review_repository import StoryReviewRepository
from Model.Database.models.story_review import StoryReviewModel, ReviewType


@pytest.fixture
def connection():
    """Create in-memory SQLite database with StoryReview table."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create the StoryReview table using the model's schema
    conn.executescript(StoryReviewModel.get_sql_schema())
    
    yield conn
    conn.close()


@pytest.fixture
def repo(connection):
    """Create StoryReviewRepository with test database."""
    return StoryReviewRepository(connection)


class TestStoryReviewRepositoryInsert:
    """Tests for insert operations."""
    
    def test_insert_returns_entity_with_id(self, repo):
        """Test insert generates and returns ID."""
        review = StoryReviewModel(
            story_id=1,
            review_id=5,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        
        saved = repo.insert(review)
        
        assert saved.id is not None
        assert saved.id > 0
    
    def test_insert_preserves_fields(self, repo):
        """Test insert preserves all fields."""
        review = StoryReviewModel(
            story_id=1,
            review_id=5,
            version=2,
            review_type=ReviewType.TONE
        )
        
        saved = repo.insert(review)
        
        assert saved.story_id == 1
        assert saved.review_id == 5
        assert saved.version == 2
        assert saved.review_type == ReviewType.TONE
    
    def test_insert_sets_created_at(self, repo):
        """Test insert includes created_at timestamp."""
        review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.CONTENT
        )
        
        saved = repo.insert(review)
        
        assert saved.created_at is not None
        assert isinstance(saved.created_at, datetime)
    
    def test_insert_multiple_review_types(self, repo):
        """Test inserting multiple review types for same story/version."""
        story_id = 1
        version = 0
        
        for review_type in ReviewType:
            review = StoryReviewModel(
                story_id=story_id,
                review_id=review_type.value.__hash__() % 100,  # Fake review_id
                version=version,
                review_type=review_type
            )
            saved = repo.insert(review)
            assert saved.id is not None
        
        # Should have 5 reviews (one per type)
        reviews = repo.find_by_story_id(story_id)
        assert len(reviews) == 5
    
    def test_insert_unique_constraint_violation(self, repo, connection):
        """Test UNIQUE constraint prevents duplicate (story_id, version, review_type)."""
        review1 = StoryReviewModel(
            story_id=1,
            review_id=5,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        repo.insert(review1)
        
        # Try to insert duplicate
        review2 = StoryReviewModel(
            story_id=1,
            review_id=10,  # Different review_id
            version=0,
            review_type=ReviewType.GRAMMAR  # Same type
        )
        
        with pytest.raises(sqlite3.IntegrityError):
            repo.insert(review2)


class TestStoryReviewRepositoryFind:
    """Tests for find operations."""
    
    def test_find_by_id_existing(self, repo):
        """Test find_by_id returns entity when found."""
        review = StoryReviewModel(
            story_id=1,
            review_id=5,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        saved = repo.insert(review)
        
        found = repo.find_by_id(saved.id)
        
        assert found is not None
        assert found.id == saved.id
        assert found.story_id == 1
        assert found.review_type == ReviewType.GRAMMAR
    
    def test_find_by_id_not_found(self, repo):
        """Test find_by_id returns None when not found."""
        found = repo.find_by_id(999)
        assert found is None
    
    def test_find_all_empty(self, repo):
        """Test find_all returns empty list when no records."""
        found = repo.find_all()
        assert found == []
    
    def test_find_all_multiple(self, repo):
        """Test find_all returns all records."""
        for i in range(3):
            review = StoryReviewModel(
                story_id=i + 1,
                review_id=i + 1,
                version=0,
                review_type=ReviewType.GRAMMAR
            )
            repo.insert(review)
        
        found = repo.find_all()
        assert len(found) == 3
    
    def test_exists_true(self, repo):
        """Test exists returns True for existing record."""
        review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        saved = repo.insert(review)
        
        assert repo.exists(saved.id) is True
    
    def test_exists_false(self, repo):
        """Test exists returns False for non-existing record."""
        assert repo.exists(999) is False


class TestStoryReviewRepositoryCustomQueries:
    """Tests for custom query methods."""
    
    def test_find_by_story_id(self, repo):
        """Test find_by_story_id returns all reviews for story."""
        # Insert reviews for story 1
        for review_type in [ReviewType.GRAMMAR, ReviewType.TONE]:
            review = StoryReviewModel(
                story_id=1,
                review_id=1,
                version=0,
                review_type=review_type
            )
            repo.insert(review)
        
        # Insert review for story 2
        review = StoryReviewModel(
            story_id=2,
            review_id=2,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        repo.insert(review)
        
        found = repo.find_by_story_id(1)
        assert len(found) == 2
        assert all(r.story_id == 1 for r in found)
    
    def test_find_by_story_and_version(self, repo):
        """Test find_by_story_and_version returns specific version reviews."""
        # Insert version 0 reviews
        for review_type in [ReviewType.GRAMMAR, ReviewType.TONE]:
            review = StoryReviewModel(
                story_id=1,
                review_id=1,
                version=0,
                review_type=review_type
            )
            repo.insert(review)
        
        # Insert version 1 review
        review = StoryReviewModel(
            story_id=1,
            review_id=2,
            version=1,
            review_type=ReviewType.GRAMMAR
        )
        repo.insert(review)
        
        found = repo.find_by_story_and_version(1, 0)
        assert len(found) == 2
        assert all(r.version == 0 for r in found)
    
    def test_find_by_story_version_type(self, repo):
        """Test find_by_story_version_type returns exact match."""
        review = StoryReviewModel(
            story_id=1,
            review_id=5,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        repo.insert(review)
        
        found = repo.find_by_story_version_type(1, 0, ReviewType.GRAMMAR)
        
        assert found is not None
        assert found.review_type == ReviewType.GRAMMAR
    
    def test_find_by_story_version_type_not_found(self, repo):
        """Test find_by_story_version_type returns None when not found."""
        found = repo.find_by_story_version_type(1, 0, ReviewType.GRAMMAR)
        assert found is None
    
    def test_find_by_review_id(self, repo):
        """Test find_by_review_id returns all linked story reviews."""
        # Link review_id=5 to multiple stories
        for story_id in [1, 2, 3]:
            review = StoryReviewModel(
                story_id=story_id,
                review_id=5,
                version=0,
                review_type=ReviewType.GRAMMAR
            )
            repo.insert(review)
        
        found = repo.find_by_review_id(5)
        assert len(found) == 3
        assert all(r.review_id == 5 for r in found)
    
    def test_find_by_review_type(self, repo):
        """Test find_by_review_type returns all reviews of type."""
        # Insert grammar reviews for multiple stories
        for story_id in [1, 2]:
            review = StoryReviewModel(
                story_id=story_id,
                review_id=story_id,
                version=0,
                review_type=ReviewType.GRAMMAR
            )
            repo.insert(review)
        
        # Insert tone review
        review = StoryReviewModel(
            story_id=3,
            review_id=3,
            version=0,
            review_type=ReviewType.TONE
        )
        repo.insert(review)
        
        found = repo.find_by_review_type(ReviewType.GRAMMAR)
        assert len(found) == 2
        assert all(r.review_type == ReviewType.GRAMMAR for r in found)


class TestStoryReviewRepositoryDatetimePersistence:
    """Tests for datetime handling."""
    
    def test_datetime_roundtrip(self, repo):
        """Test datetime is preserved through insert/find."""
        created_at = datetime(2024, 1, 15, 10, 30, 0)
        review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR,
            created_at=created_at
        )
        
        saved = repo.insert(review)
        found = repo.find_by_id(saved.id)
        
        assert found.created_at == created_at


class TestStoryReviewRepositoryVersionMethods:
    """Tests for version-related methods."""
    
    def test_find_latest_version(self, repo):
        """Test find_latest_version returns highest version number."""
        # Insert reviews for different versions
        for version in [0, 1, 2]:
            review = StoryReviewModel(
                story_id=1,
                review_id=version + 1,
                version=version,
                review_type=ReviewType.GRAMMAR
            )
            repo.insert(review)
        
        latest_version = repo.find_latest_version(1)
        
        assert latest_version == 2
    
    def test_find_latest_version_no_reviews(self, repo):
        """Test find_latest_version returns None when no reviews exist."""
        latest_version = repo.find_latest_version(999)
        assert latest_version is None
    
    def test_find_latest_reviews(self, repo):
        """Test find_latest_reviews returns all reviews for latest version."""
        # Insert reviews for version 0
        for review_type in [ReviewType.GRAMMAR, ReviewType.TONE]:
            review = StoryReviewModel(
                story_id=1,
                review_id=1,
                version=0,
                review_type=review_type
            )
            repo.insert(review)
        
        # Insert reviews for version 1 (latest)
        for review_type in [ReviewType.GRAMMAR, ReviewType.CONTENT]:
            review = StoryReviewModel(
                story_id=1,
                review_id=2,
                version=1,
                review_type=review_type
            )
            repo.insert(review)
        
        latest = repo.find_latest_reviews(1)
        
        assert len(latest) == 2
        assert all(r.version == 1 for r in latest)
    
    def test_find_latest_reviews_empty(self, repo):
        """Test find_latest_reviews returns empty list when no reviews exist."""
        latest = repo.find_latest_reviews(999)
        assert latest == []
    
    def test_find_latest_review_by_type(self, repo):
        """Test find_latest_review_by_type returns latest review of given type."""
        # Insert grammar reviews for different versions
        for version in [0, 1, 2]:
            review = StoryReviewModel(
                story_id=1,
                review_id=version + 1,
                version=version,
                review_type=ReviewType.GRAMMAR
            )
            repo.insert(review)
        
        latest_grammar = repo.find_latest_review_by_type(1, ReviewType.GRAMMAR)
        
        assert latest_grammar is not None
        assert latest_grammar.version == 2
        assert latest_grammar.review_type == ReviewType.GRAMMAR
    
    def test_find_latest_review_by_type_not_found(self, repo):
        """Test find_latest_review_by_type returns None when type not found."""
        # Insert only grammar review
        review = StoryReviewModel(
            story_id=1,
            review_id=1,
            version=0,
            review_type=ReviewType.GRAMMAR
        )
        repo.insert(review)
        
        # Look for tone review
        latest_tone = repo.find_latest_review_by_type(1, ReviewType.TONE)
        assert latest_tone is None


class TestStoryReviewRepositoryConvenienceMethods:
    """Tests for convenience alias methods."""
    
    def test_get_current_story_reviews(self, repo):
        """Test get_current_story_reviews returns reviews for latest version."""
        # Insert reviews for version 0 and 1
        for version in [0, 1]:
            for review_type in [ReviewType.GRAMMAR, ReviewType.TONE]:
                review = StoryReviewModel(
                    story_id=1,
                    review_id=version + 1,
                    version=version,
                    review_type=review_type
                )
                repo.insert(review)
        
        current = repo.get_current_story_reviews(1)
        
        assert len(current) == 2
        assert all(r.version == 1 for r in current)
    
    def test_get_current_story_reviews_empty(self, repo):
        """Test get_current_story_reviews returns empty list when no reviews."""
        current = repo.get_current_story_reviews(999)
        assert current == []
    
    def test_get_current_story_review(self, repo):
        """Test get_current_story_review returns latest review of given type."""
        # Insert grammar reviews for versions 0, 1, 2
        for version in [0, 1, 2]:
            review = StoryReviewModel(
                story_id=1,
                review_id=version + 1,
                version=version,
                review_type=ReviewType.GRAMMAR
            )
            repo.insert(review)
        
        current = repo.get_current_story_review(1, ReviewType.GRAMMAR)
        
        assert current is not None
        assert current.version == 2
        assert current.review_type == ReviewType.GRAMMAR
    
    def test_get_current_story_review_not_found(self, repo):
        """Test get_current_story_review returns None when not found."""
        current = repo.get_current_story_review(999, ReviewType.GRAMMAR)
        assert current is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
