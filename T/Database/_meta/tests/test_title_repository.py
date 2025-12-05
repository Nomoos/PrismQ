"""Integration tests for TitleRepository.

Tests the TitleRepository with a real SQLite in-memory database
to verify actual database operations work correctly.
"""

import pytest
import sqlite3
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from T.Database.repositories.title_repository import TitleRepository
from T.Database.models.title import Title


# SQL schema for Title table
TITLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS Title (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 0),
    text TEXT NOT NULL,
    review_id INTEGER NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(story_id, version)
);
"""


class TestTitleRepositoryIntegration:
    """Integration tests with real SQLite database."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory SQLite database with Title schema."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript(TITLE_SCHEMA)
        yield conn
        conn.close()
    
    @pytest.fixture
    def repo(self, db_connection):
        """Create TitleRepository with database connection."""
        return TitleRepository(db_connection)
    
    # === INSERT Tests ===
    
    def test_insert_title(self, repo):
        """Test inserting a new title."""
        title = Title(story_id=1, version=0, text="Test Title")
        
        saved = repo.insert(title)
        
        assert saved.id is not None
        assert saved.id > 0
        assert saved.story_id == 1
        assert saved.version == 0
        assert saved.text == "Test Title"
    
    def test_insert_title_with_review_id(self, repo):
        """Test inserting title with review reference."""
        title = Title(story_id=1, version=0, text="Reviewed Title", review_id=5)
        
        saved = repo.insert(title)
        
        assert saved.review_id == 5
    
    def test_insert_multiple_versions(self, repo):
        """Test inserting multiple versions for same story."""
        titles = [
            Title(story_id=1, version=0, text="Version 0"),
            Title(story_id=1, version=1, text="Version 1"),
            Title(story_id=1, version=2, text="Version 2"),
        ]
        
        saved_titles = [repo.insert(t) for t in titles]
        
        assert len(saved_titles) == 3
        assert all(t.id is not None for t in saved_titles)
        assert [t.version for t in saved_titles] == [0, 1, 2]
    
    # === FIND_BY_ID Tests ===
    
    def test_find_by_id_existing(self, repo):
        """Test finding existing title by ID."""
        title = Title(story_id=1, version=0, text="Find Me")
        saved = repo.insert(title)
        
        found = repo.find_by_id(saved.id)
        
        assert found is not None
        assert found.id == saved.id
        assert found.text == "Find Me"
    
    def test_find_by_id_not_found(self, repo):
        """Test finding non-existent title returns None."""
        found = repo.find_by_id(9999)
        
        assert found is None
    
    # === FIND_ALL Tests ===
    
    def test_find_all_empty(self, repo):
        """Test find_all on empty table."""
        result = repo.find_all()
        
        assert result == []
    
    def test_find_all_multiple(self, repo):
        """Test find_all returns all titles."""
        repo.insert(Title(story_id=1, version=0, text="Title 1"))
        repo.insert(Title(story_id=2, version=0, text="Title 2"))
        repo.insert(Title(story_id=1, version=1, text="Title 1 v2"))
        
        result = repo.find_all()
        
        assert len(result) == 3
    
    # === EXISTS Tests ===
    
    def test_exists_true(self, repo):
        """Test exists returns True for existing ID."""
        saved = repo.insert(Title(story_id=1, version=0, text="Exists"))
        
        assert repo.exists(saved.id) is True
    
    def test_exists_false(self, repo):
        """Test exists returns False for non-existent ID."""
        assert repo.exists(9999) is False
    
    # === FIND_LATEST_VERSION Tests ===
    
    def test_find_latest_version(self, repo):
        """Test finding latest version of a title."""
        repo.insert(Title(story_id=1, version=0, text="Version 0"))
        repo.insert(Title(story_id=1, version=1, text="Version 1"))
        repo.insert(Title(story_id=1, version=2, text="Version 2"))
        
        latest = repo.find_latest_version(story_id=1)
        
        assert latest is not None
        assert latest.version == 2
        assert latest.text == "Version 2"
    
    def test_find_latest_version_single(self, repo):
        """Test finding latest when only one version exists."""
        repo.insert(Title(story_id=1, version=0, text="Only Version"))
        
        latest = repo.find_latest_version(story_id=1)
        
        assert latest is not None
        assert latest.version == 0
    
    def test_find_latest_version_no_titles(self, repo):
        """Test finding latest version when no titles exist."""
        latest = repo.find_latest_version(story_id=9999)
        
        assert latest is None
    
    # === FIND_VERSIONS Tests ===
    
    def test_find_versions(self, repo):
        """Test finding all versions of a title."""
        repo.insert(Title(story_id=1, version=0, text="v0"))
        repo.insert(Title(story_id=1, version=1, text="v1"))
        repo.insert(Title(story_id=1, version=2, text="v2"))
        
        versions = repo.find_versions(story_id=1)
        
        assert len(versions) == 3
        assert [v.version for v in versions] == [0, 1, 2]  # Ascending order
    
    def test_find_versions_empty(self, repo):
        """Test finding versions for non-existent story."""
        versions = repo.find_versions(story_id=9999)
        
        assert versions == []
    
    def test_find_versions_different_stories(self, repo):
        """Test versions are scoped to specific story."""
        repo.insert(Title(story_id=1, version=0, text="Story 1 v0"))
        repo.insert(Title(story_id=1, version=1, text="Story 1 v1"))
        repo.insert(Title(story_id=2, version=0, text="Story 2 v0"))
        
        story1_versions = repo.find_versions(story_id=1)
        story2_versions = repo.find_versions(story_id=2)
        
        assert len(story1_versions) == 2
        assert len(story2_versions) == 1
    
    # === FIND_VERSION Tests ===
    
    def test_find_version_specific(self, repo):
        """Test finding specific version."""
        repo.insert(Title(story_id=1, version=0, text="v0"))
        repo.insert(Title(story_id=1, version=1, text="v1"))
        repo.insert(Title(story_id=1, version=2, text="v2"))
        
        v1 = repo.find_version(story_id=1, version=1)
        
        assert v1 is not None
        assert v1.version == 1
        assert v1.text == "v1"
    
    def test_find_version_not_found(self, repo):
        """Test finding non-existent version."""
        repo.insert(Title(story_id=1, version=0, text="v0"))
        
        v5 = repo.find_version(story_id=1, version=5)
        
        assert v5 is None
    
    # === FIND_BY_STORY_ID Tests ===
    
    def test_find_by_story_id(self, repo):
        """Test find_by_story_id returns all versions."""
        repo.insert(Title(story_id=1, version=0, text="v0"))
        repo.insert(Title(story_id=1, version=1, text="v1"))
        
        titles = repo.find_by_story_id(story_id=1)
        
        assert len(titles) == 2
    
    # === GET_NEXT_VERSION_NUMBER Tests ===
    
    def test_get_next_version_number_empty(self, repo):
        """Test next version for story with no titles is 0."""
        next_version = repo._get_next_version_number(story_id=1)
        
        assert next_version == 0
    
    def test_get_next_version_number_existing(self, repo):
        """Test next version number after existing versions."""
        repo.insert(Title(story_id=1, version=0, text="v0"))
        repo.insert(Title(story_id=1, version=1, text="v1"))
        
        next_version = repo._get_next_version_number(story_id=1)
        
        assert next_version == 2
    
    # === Workflow Integration Tests ===
    
    def test_version_workflow(self, repo):
        """Test complete version workflow: create, update via new version, find."""
        # Create initial version
        initial = Title(story_id=1, version=0, text="Draft Title")
        saved_initial = repo.insert(initial)
        
        # Create new version (simulating "update")
        new_version = saved_initial.create_next_version(
            "Improved Title", review_id=10
        )
        saved_new = repo.insert(new_version)
        
        # Verify both exist
        all_versions = repo.find_versions(story_id=1)
        latest = repo.find_latest_version(story_id=1)
        
        assert len(all_versions) == 2
        assert latest.version == 1
        assert latest.text == "Improved Title"
        assert latest.review_id == 10
    
    def test_datetime_persistence(self, repo):
        """Test datetime is correctly stored and retrieved."""
        title = Title(story_id=1, version=0, text="Test")
        saved = repo.insert(title)
        
        found = repo.find_by_id(saved.id)
        
        assert isinstance(found.created_at, datetime)
        # Compare down to second (microseconds may differ due to ISO format)
        assert found.created_at.date() == saved.created_at.date()
    
    # === GET_CURRENT_TITLE Tests ===
    
    def test_get_current_title(self, repo):
        """Test get_current_title returns latest version."""
        repo.insert(Title(story_id=1, version=0, text="Version 0"))
        repo.insert(Title(story_id=1, version=1, text="Version 1"))
        repo.insert(Title(story_id=1, version=2, text="Version 2"))
        
        current = repo.get_current_title(story_id=1)
        
        assert current is not None
        assert current.version == 2
        assert current.text == "Version 2"
    
    def test_get_current_title_no_titles(self, repo):
        """Test get_current_title when no titles exist."""
        current = repo.get_current_title(story_id=9999)
        
        assert current is None
    
    def test_get_current_title_single(self, repo):
        """Test get_current_title with only one version."""
        repo.insert(Title(story_id=1, version=0, text="Only Title"))
        
        current = repo.get_current_title(story_id=1)
        
        assert current is not None
        assert current.version == 0
        assert current.text == "Only Title"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
