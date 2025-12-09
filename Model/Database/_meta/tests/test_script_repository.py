"""Tests for ContentRepository.

Tests cover:
- CRUD operations (Insert + Read only)
- Version management (find_latest_version, find_versions, find_version)
- Integration with Content model
"""

import pytest
import sqlite3
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from Model.Database.models.content import Content
from Model.Database.repositories.content_repository import ContentRepository


@pytest.fixture
def db_connection():
    """Create in-memory SQLite database with Content table."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create Content table
    conn.execute("""
        CREATE TABLE Content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL,
            UNIQUE(story_id, version)
        )
    """)
    conn.commit()
    
    yield conn
    conn.close()


@pytest.fixture
def repo(db_connection):
    """Create ContentRepository instance."""
    return ContentRepository(db_connection)


class TestContentRepositoryIntegration:
    """Integration tests for ContentRepository."""
    
    def test_insert_content(self, repo):
        """Test inserting a new content."""
        content = Content(story_id=1, version=0, text="Once upon a time...")
        saved = repo.insert(content)
        
        assert saved.id is not None
        assert saved.id > 0
        assert saved.story_id == 1
        assert saved.version == 0
        assert saved.text == "Once upon a time..."
    
    def test_insert_content_with_review_id(self, repo):
        """Test inserting a content with review reference."""
        content = Content(story_id=1, version=0, text="Content", review_id=5)
        saved = repo.insert(content)
        
        assert saved.review_id == 5
    
    def test_insert_multiple_versions(self, repo):
        """Test inserting multiple versions of a content."""
        content_v0 = Content(story_id=1, version=0, text="Version 0")
        content_v1 = Content(story_id=1, version=1, text="Version 1")
        content_v2 = Content(story_id=1, version=2, text="Version 2")
        
        saved_v0 = repo.insert(content_v0)
        saved_v1 = repo.insert(content_v1)
        saved_v2 = repo.insert(content_v2)
        
        assert saved_v0.id < saved_v1.id < saved_v2.id
    
    def test_find_by_id_existing(self, repo):
        """Test finding existing content by ID."""
        content = Content(story_id=1, version=0, text="Test content")
        saved = repo.insert(content)
        
        found = repo.find_by_id(saved.id)
        
        assert found is not None
        assert found.id == saved.id
        assert found.text == "Test content"
    
    def test_find_by_id_not_found(self, repo):
        """Test finding non-existent content by ID."""
        found = repo.find_by_id(999)
        assert found is None
    
    def test_find_all_empty(self, repo):
        """Test find_all on empty database."""
        contents = repo.find_all()
        assert contents == []
    
    def test_find_all_multiple(self, repo):
        """Test find_all with multiple contents."""
        repo.insert(Content(story_id=1, version=0, text="Content 1"))
        repo.insert(Content(story_id=2, version=0, text="Content 2"))
        repo.insert(Content(story_id=1, version=1, text="Content 1 v1"))
        
        contents = repo.find_all()
        
        assert len(contents) == 3
    
    def test_exists_true(self, repo):
        """Test exists returns True for existing content."""
        content = Content(story_id=1, version=0, text="Test")
        saved = repo.insert(content)
        
        assert repo.exists(saved.id) is True
    
    def test_exists_false(self, repo):
        """Test exists returns False for non-existent content."""
        assert repo.exists(999) is False
    
    def test_find_latest_version(self, repo):
        """Test finding the latest version of a content."""
        repo.insert(Content(story_id=1, version=0, text="v0"))
        repo.insert(Content(story_id=1, version=1, text="v1"))
        repo.insert(Content(story_id=1, version=2, text="v2"))
        
        latest = repo.find_latest_version(story_id=1)
        
        assert latest is not None
        assert latest.version == 2
        assert latest.text == "v2"
    
    def test_find_latest_version_single(self, repo):
        """Test find_latest_version with only one version."""
        repo.insert(Content(story_id=1, version=0, text="Only version"))
        
        latest = repo.find_latest_version(story_id=1)
        
        assert latest is not None
        assert latest.version == 0
    
    def test_find_latest_version_no_contents(self, repo):
        """Test find_latest_version when no contents exist."""
        latest = repo.find_latest_version(story_id=999)
        assert latest is None
    
    def test_find_versions(self, repo):
        """Test finding all versions of a content."""
        repo.insert(Content(story_id=1, version=0, text="v0"))
        repo.insert(Content(story_id=1, version=1, text="v1"))
        repo.insert(Content(story_id=1, version=2, text="v2"))
        
        versions = repo.find_versions(story_id=1)
        
        assert len(versions) == 3
        assert versions[0].version == 0
        assert versions[1].version == 1
        assert versions[2].version == 2
    
    def test_find_versions_empty(self, repo):
        """Test find_versions when no versions exist."""
        versions = repo.find_versions(story_id=999)
        assert versions == []
    
    def test_find_versions_different_stories(self, repo):
        """Test find_versions returns only versions for specified story."""
        repo.insert(Content(story_id=1, version=0, text="Story 1"))
        repo.insert(Content(story_id=2, version=0, text="Story 2"))
        repo.insert(Content(story_id=1, version=1, text="Story 1 v1"))
        
        versions_story1 = repo.find_versions(story_id=1)
        versions_story2 = repo.find_versions(story_id=2)
        
        assert len(versions_story1) == 2
        assert len(versions_story2) == 1
    
    def test_find_version_specific(self, repo):
        """Test finding a specific version."""
        repo.insert(Content(story_id=1, version=0, text="v0"))
        repo.insert(Content(story_id=1, version=1, text="v1"))
        repo.insert(Content(story_id=1, version=2, text="v2"))
        
        v1 = repo.find_version(story_id=1, version=1)
        
        assert v1 is not None
        assert v1.version == 1
        assert v1.text == "v1"
    
    def test_find_version_not_found(self, repo):
        """Test find_version for non-existent version."""
        repo.insert(Content(story_id=1, version=0, text="v0"))
        
        not_found = repo.find_version(story_id=1, version=5)
        assert not_found is None
    
    def test_find_by_story_id(self, repo):
        """Test find_by_story_id alias."""
        repo.insert(Content(story_id=1, version=0, text="v0"))
        repo.insert(Content(story_id=1, version=1, text="v1"))
        
        contents = repo.find_by_story_id(story_id=1)
        
        assert len(contents) == 2
    
    def test_get_next_version_number_empty(self, repo):
        """Test _get_next_version_number when no contents exist."""
        next_version = repo._get_next_version_number(story_id=1)
        assert next_version == 0
    
    def test_get_next_version_number_existing(self, repo):
        """Test _get_next_version_number with existing contents."""
        repo.insert(Content(story_id=1, version=0, text="v0"))
        repo.insert(Content(story_id=1, version=1, text="v1"))
        
        next_version = repo._get_next_version_number(story_id=1)
        assert next_version == 2
    
    def test_version_workflow(self, repo):
        """Test complete version workflow with create_next_version."""
        # Create initial content
        content_v0 = Content(story_id=1, version=0, text="Original content")
        saved_v0 = repo.insert(content_v0)
        
        # Create next version using model method
        content_v1 = saved_v0.create_next_version("Improved content", review_id=5)
        saved_v1 = repo.insert(content_v1)
        
        # Verify
        assert saved_v1.version == 1
        assert saved_v1.text == "Improved content"
        assert saved_v1.review_id == 5
        
        # Verify latest
        latest = repo.find_latest_version(story_id=1)
        assert latest.version == 1
    
    def test_datetime_persistence(self, repo):
        """Test datetime is persisted and restored correctly."""
        content = Content(story_id=1, version=0, text="Test")
        saved = repo.insert(content)
        
        found = repo.find_by_id(saved.id)
        
        assert isinstance(found.created_at, datetime)
        # Allow small time difference due to serialization
        assert abs((found.created_at - saved.created_at).total_seconds()) < 1
    
    # === GET_CURRENT_SCRIPT Tests ===
    
    def test_get_current_content(self, repo):
        """Test get_current_content returns latest version."""
        repo.insert(Content(story_id=1, version=0, text="Version 0"))
        repo.insert(Content(story_id=1, version=1, text="Version 1"))
        repo.insert(Content(story_id=1, version=2, text="Version 2"))
        
        current = repo.get_current_content(story_id=1)
        
        assert current is not None
        assert current.version == 2
        assert current.text == "Version 2"
    
    def test_get_current_content_no_contents(self, repo):
        """Test get_current_content when no contents exist."""
        current = repo.get_current_content(story_id=9999)
        
        assert current is None
    
    def test_get_current_content_single(self, repo):
        """Test get_current_content with only one version."""
        repo.insert(Content(story_id=1, version=0, text="Only Content"))
        
        current = repo.get_current_content(story_id=1)
        
        assert current is not None
        assert current.version == 0
        assert current.text == "Only Content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
