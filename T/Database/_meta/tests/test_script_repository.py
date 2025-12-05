"""Tests for ScriptRepository.

Tests cover:
- CRUD operations (Insert + Read only)
- Version management (find_latest_version, find_versions, find_version)
- Integration with Script model
"""

import pytest
import sqlite3
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for proper imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from T.Database.models.script import Script
from T.Database.repositories.script_repository import ScriptRepository


@pytest.fixture
def db_connection():
    """Create in-memory SQLite database with Script table."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Create Script table
    conn.execute("""
        CREATE TABLE Script (
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
    """Create ScriptRepository instance."""
    return ScriptRepository(db_connection)


class TestScriptRepositoryIntegration:
    """Integration tests for ScriptRepository."""
    
    def test_insert_script(self, repo):
        """Test inserting a new script."""
        script = Script(story_id=1, version=0, text="Once upon a time...")
        saved = repo.insert(script)
        
        assert saved.id is not None
        assert saved.id > 0
        assert saved.story_id == 1
        assert saved.version == 0
        assert saved.text == "Once upon a time..."
    
    def test_insert_script_with_review_id(self, repo):
        """Test inserting a script with review reference."""
        script = Script(story_id=1, version=0, text="Content", review_id=5)
        saved = repo.insert(script)
        
        assert saved.review_id == 5
    
    def test_insert_multiple_versions(self, repo):
        """Test inserting multiple versions of a script."""
        script_v0 = Script(story_id=1, version=0, text="Version 0")
        script_v1 = Script(story_id=1, version=1, text="Version 1")
        script_v2 = Script(story_id=1, version=2, text="Version 2")
        
        saved_v0 = repo.insert(script_v0)
        saved_v1 = repo.insert(script_v1)
        saved_v2 = repo.insert(script_v2)
        
        assert saved_v0.id < saved_v1.id < saved_v2.id
    
    def test_find_by_id_existing(self, repo):
        """Test finding existing script by ID."""
        script = Script(story_id=1, version=0, text="Test content")
        saved = repo.insert(script)
        
        found = repo.find_by_id(saved.id)
        
        assert found is not None
        assert found.id == saved.id
        assert found.text == "Test content"
    
    def test_find_by_id_not_found(self, repo):
        """Test finding non-existent script by ID."""
        found = repo.find_by_id(999)
        assert found is None
    
    def test_find_all_empty(self, repo):
        """Test find_all on empty database."""
        scripts = repo.find_all()
        assert scripts == []
    
    def test_find_all_multiple(self, repo):
        """Test find_all with multiple scripts."""
        repo.insert(Script(story_id=1, version=0, text="Script 1"))
        repo.insert(Script(story_id=2, version=0, text="Script 2"))
        repo.insert(Script(story_id=1, version=1, text="Script 1 v1"))
        
        scripts = repo.find_all()
        
        assert len(scripts) == 3
    
    def test_exists_true(self, repo):
        """Test exists returns True for existing script."""
        script = Script(story_id=1, version=0, text="Test")
        saved = repo.insert(script)
        
        assert repo.exists(saved.id) is True
    
    def test_exists_false(self, repo):
        """Test exists returns False for non-existent script."""
        assert repo.exists(999) is False
    
    def test_find_latest_version(self, repo):
        """Test finding the latest version of a script."""
        repo.insert(Script(story_id=1, version=0, text="v0"))
        repo.insert(Script(story_id=1, version=1, text="v1"))
        repo.insert(Script(story_id=1, version=2, text="v2"))
        
        latest = repo.find_latest_version(story_id=1)
        
        assert latest is not None
        assert latest.version == 2
        assert latest.text == "v2"
    
    def test_find_latest_version_single(self, repo):
        """Test find_latest_version with only one version."""
        repo.insert(Script(story_id=1, version=0, text="Only version"))
        
        latest = repo.find_latest_version(story_id=1)
        
        assert latest is not None
        assert latest.version == 0
    
    def test_find_latest_version_no_scripts(self, repo):
        """Test find_latest_version when no scripts exist."""
        latest = repo.find_latest_version(story_id=999)
        assert latest is None
    
    def test_find_versions(self, repo):
        """Test finding all versions of a script."""
        repo.insert(Script(story_id=1, version=0, text="v0"))
        repo.insert(Script(story_id=1, version=1, text="v1"))
        repo.insert(Script(story_id=1, version=2, text="v2"))
        
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
        repo.insert(Script(story_id=1, version=0, text="Story 1"))
        repo.insert(Script(story_id=2, version=0, text="Story 2"))
        repo.insert(Script(story_id=1, version=1, text="Story 1 v1"))
        
        versions_story1 = repo.find_versions(story_id=1)
        versions_story2 = repo.find_versions(story_id=2)
        
        assert len(versions_story1) == 2
        assert len(versions_story2) == 1
    
    def test_find_version_specific(self, repo):
        """Test finding a specific version."""
        repo.insert(Script(story_id=1, version=0, text="v0"))
        repo.insert(Script(story_id=1, version=1, text="v1"))
        repo.insert(Script(story_id=1, version=2, text="v2"))
        
        v1 = repo.find_version(story_id=1, version=1)
        
        assert v1 is not None
        assert v1.version == 1
        assert v1.text == "v1"
    
    def test_find_version_not_found(self, repo):
        """Test find_version for non-existent version."""
        repo.insert(Script(story_id=1, version=0, text="v0"))
        
        not_found = repo.find_version(story_id=1, version=5)
        assert not_found is None
    
    def test_find_by_story_id(self, repo):
        """Test find_by_story_id alias."""
        repo.insert(Script(story_id=1, version=0, text="v0"))
        repo.insert(Script(story_id=1, version=1, text="v1"))
        
        scripts = repo.find_by_story_id(story_id=1)
        
        assert len(scripts) == 2
    
    def test_get_next_version_number_empty(self, repo):
        """Test _get_next_version_number when no scripts exist."""
        next_version = repo._get_next_version_number(story_id=1)
        assert next_version == 0
    
    def test_get_next_version_number_existing(self, repo):
        """Test _get_next_version_number with existing scripts."""
        repo.insert(Script(story_id=1, version=0, text="v0"))
        repo.insert(Script(story_id=1, version=1, text="v1"))
        
        next_version = repo._get_next_version_number(story_id=1)
        assert next_version == 2
    
    def test_version_workflow(self, repo):
        """Test complete version workflow with create_next_version."""
        # Create initial script
        script_v0 = Script(story_id=1, version=0, text="Original content")
        saved_v0 = repo.insert(script_v0)
        
        # Create next version using model method
        script_v1 = saved_v0.create_next_version("Improved content", review_id=5)
        saved_v1 = repo.insert(script_v1)
        
        # Verify
        assert saved_v1.version == 1
        assert saved_v1.text == "Improved content"
        assert saved_v1.review_id == 5
        
        # Verify latest
        latest = repo.find_latest_version(story_id=1)
        assert latest.version == 1
    
    def test_datetime_persistence(self, repo):
        """Test datetime is persisted and restored correctly."""
        script = Script(story_id=1, version=0, text="Test")
        saved = repo.insert(script)
        
        found = repo.find_by_id(saved.id)
        
        assert isinstance(found.created_at, datetime)
        # Allow small time difference due to serialization
        assert abs((found.created_at - saved.created_at).total_seconds()) < 1
    
    # === GET_CURRENT_SCRIPT Tests ===
    
    def test_get_current_script(self, repo):
        """Test get_current_script returns latest version."""
        repo.insert(Script(story_id=1, version=0, text="Version 0"))
        repo.insert(Script(story_id=1, version=1, text="Version 1"))
        repo.insert(Script(story_id=1, version=2, text="Version 2"))
        
        current = repo.get_current_script(story_id=1)
        
        assert current is not None
        assert current.version == 2
        assert current.text == "Version 2"
    
    def test_get_current_script_no_scripts(self, repo):
        """Test get_current_script when no scripts exist."""
        current = repo.get_current_script(story_id=9999)
        
        assert current is None
    
    def test_get_current_script_single(self, repo):
        """Test get_current_script with only one version."""
        repo.insert(Script(story_id=1, version=0, text="Only Script"))
        
        current = repo.get_current_script(story_id=1)
        
        assert current is not None
        assert current.version == 0
        assert current.text == "Only Script"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
