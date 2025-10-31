"""Tests for IdeaInspirationDatabase."""

import pytest
import tempfile
import os
from pathlib import Path

from idea_inspiration import IdeaInspiration, ContentType
from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db(temp_db):
    """Create an IdeaInspirationDatabase instance."""
    return IdeaInspirationDatabase(temp_db, interactive=False)


@pytest.fixture
def sample_idea():
    """Create a sample IdeaInspiration for testing."""
    return IdeaInspiration.from_text(
        title="Test Article",
        description="A test article",
        text_content="This is test content",
        keywords=["test", "article"],
        metadata={"author": "Test Author", "views": "1000"},
        source_id="test-123",
        source_url="https://example.com/test",
        source_created_by="Test Author",
        source_created_at="2025-01-01T00:00:00Z",
        score=85,
        category="technology"
    )


class TestIdeaInspirationDatabase:
    """Tests for IdeaInspirationDatabase class."""
    
    def test_init_creates_database(self, temp_db):
        """Test that initialization creates the database."""
        db = IdeaInspirationDatabase(temp_db, interactive=False)
        assert os.path.exists(temp_db)
    
    def test_init_creates_schema(self, db, temp_db):
        """Test that initialization creates the schema."""
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='IdeaInspiration'
        """)
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_insert_idea(self, db, sample_idea):
        """Test inserting an IdeaInspiration."""
        record_id = db.insert(sample_idea)
        
        assert record_id is not None
        assert isinstance(record_id, int)
        assert record_id > 0
    
    def test_insert_duplicate_source_id(self, db, sample_idea):
        """Test that inserting duplicate source_id is handled gracefully."""
        # First insert should succeed
        record_id1 = db.insert(sample_idea)
        assert record_id1 is not None
        
        # Second insert with same source_id should be handled
        # Note: Without UNIQUE constraint, this will insert a duplicate
        # If we want to prevent duplicates, we need to add UNIQUE constraint
        record_id2 = db.insert(sample_idea)
        # For now, this will succeed (creates duplicate)
        assert record_id2 is not None
    
    def test_get_by_id(self, db, sample_idea):
        """Test retrieving an IdeaInspiration by ID."""
        record_id = db.insert(sample_idea)
        
        retrieved = db.get_by_id(record_id)
        
        assert retrieved is not None
        assert retrieved.title == sample_idea.title
        assert retrieved.description == sample_idea.description
        assert retrieved.content == sample_idea.content
        assert retrieved.keywords == sample_idea.keywords
        assert retrieved.source_id == sample_idea.source_id
        assert retrieved.score == sample_idea.score
    
    def test_get_by_id_not_found(self, db):
        """Test retrieving a non-existent record."""
        retrieved = db.get_by_id(99999)
        assert retrieved is None
    
    def test_get_by_source_id(self, db, sample_idea):
        """Test retrieving an IdeaInspiration by source ID."""
        db.insert(sample_idea)
        
        retrieved = db.get_by_source_id(sample_idea.source_id)
        
        assert retrieved is not None
        assert retrieved.title == sample_idea.title
        assert retrieved.source_id == sample_idea.source_id
    
    def test_get_by_source_id_not_found(self, db):
        """Test retrieving by non-existent source ID."""
        retrieved = db.get_by_source_id("nonexistent")
        assert retrieved is None
    
    def test_get_all(self, db, sample_idea):
        """Test retrieving all IdeaInspiration records."""
        # Insert multiple records
        db.insert(sample_idea)
        
        idea2 = IdeaInspiration.from_text(
            title="Second Article",
            description="Another test",
            text_content="More content",
            keywords=["second"],
            source_id="test-456"
        )
        db.insert(idea2)
        
        all_ideas = db.get_all()
        
        assert len(all_ideas) == 2
        assert all(isinstance(idea, IdeaInspiration) for idea in all_ideas)
    
    def test_get_all_with_limit(self, db, sample_idea):
        """Test retrieving with limit."""
        # Insert 3 records
        for i in range(3):
            idea = IdeaInspiration.from_text(
                title=f"Article {i}",
                text_content=f"Content {i}",
                source_id=f"test-{i}"
            )
            db.insert(idea)
        
        limited = db.get_all(limit=2)
        assert len(limited) == 2
    
    def test_get_all_with_offset(self, db, sample_idea):
        """Test retrieving with offset."""
        # Insert 3 records
        for i in range(3):
            idea = IdeaInspiration.from_text(
                title=f"Article {i}",
                text_content=f"Content {i}",
                source_id=f"test-{i}"
            )
            db.insert(idea)
        
        offset_results = db.get_all(offset=1, limit=2)
        assert len(offset_results) <= 2
    
    def test_get_all_filter_by_source_type(self, db):
        """Test filtering by source type."""
        # Insert text and video ideas
        text_idea = IdeaInspiration.from_text(
            title="Text Article",
            text_content="Text content",
            source_id="text-1"
        )
        video_idea = IdeaInspiration.from_video(
            title="Video Content",
            subtitle_text="Video subtitles",
            source_id="video-1"
        )
        
        db.insert(text_idea)
        db.insert(video_idea)
        
        text_results = db.get_all(source_type="text")
        assert len(text_results) == 1
        assert text_results[0].source_type == ContentType.TEXT
    
    def test_get_all_filter_by_category(self, db):
        """Test filtering by category."""
        tech_idea = IdeaInspiration.from_text(
            title="Tech Article",
            text_content="Tech content",
            source_id="tech-1",
            category="technology"
        )
        sports_idea = IdeaInspiration.from_text(
            title="Sports Article",
            text_content="Sports content",
            source_id="sports-1",
            category="sports"
        )
        
        db.insert(tech_idea)
        db.insert(sports_idea)
        
        tech_results = db.get_all(category="technology")
        assert len(tech_results) == 1
        assert tech_results[0].category == "technology"
    
    def test_count(self, db, sample_idea):
        """Test counting records."""
        assert db.count() == 0
        
        db.insert(sample_idea)
        assert db.count() == 1
        
        idea2 = IdeaInspiration.from_text(
            title="Second",
            text_content="Content",
            source_id="test-2"
        )
        db.insert(idea2)
        assert db.count() == 2
    
    def test_count_with_filters(self, db):
        """Test counting with filters."""
        tech_idea = IdeaInspiration.from_text(
            title="Tech",
            text_content="Content",
            source_id="tech-1",
            category="technology"
        )
        sports_idea = IdeaInspiration.from_text(
            title="Sports",
            text_content="Content",
            source_id="sports-1",
            category="sports"
        )
        
        db.insert(tech_idea)
        db.insert(sports_idea)
        
        assert db.count(category="technology") == 1
        assert db.count(category="sports") == 1
        assert db.count() == 2
    
    def test_insert_batch(self, db):
        """Test batch insertion."""
        ideas = [
            IdeaInspiration.from_text(
                title=f"Article {i}",
                text_content=f"Content {i}",
                source_id=f"batch-{i}"
            )
            for i in range(5)
        ]
        
        inserted_count = db.insert_batch(ideas)
        
        assert inserted_count == 5
        assert db.count() == 5
    
    def test_insert_batch_with_duplicates(self, db):
        """Test batch insertion with some duplicates."""
        # Insert one record first
        first_idea = IdeaInspiration.from_text(
            title="First",
            text_content="Content",
            source_id="dup-1"
        )
        db.insert(first_idea)
        
        # Try to insert batch including duplicate
        ideas = [
            first_idea,  # This is a duplicate
            IdeaInspiration.from_text(
                title="Second",
                text_content="Content",
                source_id="dup-2"
            )
        ]
        
        inserted_count = db.insert_batch(ideas)
        # Should insert both since we don't have UNIQUE constraint yet
        assert inserted_count >= 1
    
    def test_metadata_preservation(self, db, sample_idea):
        """Test that metadata dictionary is preserved."""
        db.insert(sample_idea)
        
        retrieved = db.get_by_source_id(sample_idea.source_id)
        
        assert retrieved.metadata == sample_idea.metadata
        assert retrieved.metadata['author'] == "Test Author"
        assert retrieved.metadata['views'] == "1000"
    
    def test_keywords_preservation(self, db, sample_idea):
        """Test that keywords list is preserved."""
        db.insert(sample_idea)
        
        retrieved = db.get_by_source_id(sample_idea.source_id)
        
        assert retrieved.keywords == sample_idea.keywords
        assert "test" in retrieved.keywords
        assert "article" in retrieved.keywords
    
    def test_subcategory_relevance_preservation(self, db):
        """Test that subcategory_relevance is preserved."""
        idea = IdeaInspiration.from_text(
            title="Test",
            text_content="Content",
            source_id="subcat-1",
            subcategory_relevance={
                "tech": 90,
                "science": 75,
                "innovation": 85
            }
        )
        
        db.insert(idea)
        retrieved = db.get_by_source_id(idea.source_id)
        
        assert retrieved.subcategory_relevance == idea.subcategory_relevance
        assert retrieved.subcategory_relevance['tech'] == 90
    
    def test_contextual_scores_preservation(self, db):
        """Test that contextual category scores are preserved."""
        idea = IdeaInspiration.from_text(
            title="Test",
            text_content="Content",
            source_id="context-1",
            contextual_category_scores={
                "language:english": 145,
                "region:us": 160,
                "age:18-24": 142
            }
        )
        
        db.insert(idea)
        retrieved = db.get_by_source_id(idea.source_id)
        
        assert retrieved.contextual_category_scores == idea.contextual_category_scores
        assert retrieved.contextual_category_scores['language:english'] == 145


class TestGetCentralDatabasePath:
    """Tests for get_central_database_path function."""
    
    def test_returns_string_path(self):
        """Test that function returns a string path."""
        path = get_central_database_path()
        assert isinstance(path, str)
        assert len(path) > 0
    
    def test_path_ends_with_db_extension(self):
        """Test that path ends with .s3db extension."""
        path = get_central_database_path()
        assert path.endswith('.s3db') or path.endswith('.db')
