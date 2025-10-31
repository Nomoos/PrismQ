"""Tests for database module."""

import pytest
import tempfile
import os
from pathlib import Path
from src.core.database import Database, init_database, insert_resource, get_all_resources, count_resources


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.s3db') as f:
        db_path = f.name
    
    database_url = f"sqlite:///{db_path}"
    init_database(database_url)
    
    yield database_url, db_path
    
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_database_init(temp_db):
    """Test database initialization."""
    database_url, db_path = temp_db
    
    assert os.path.exists(db_path)
    
    # Verify we can connect
    db = Database(db_path, interactive=False)
    assert db.database_url == database_url


def test_insert_resource(temp_db):
    """Test inserting a resource."""
    database_url, db_path = temp_db
    
    success = insert_resource(
        database_url,
        source='genius',
        source_id='test_123',
        title='Test Song - Artist',
        content='Test visual resource',
        tags='test,lyrics',
        score=8.5,
        score_dictionary='{"emotional_impact": 8.5}'
    )
    
    assert success is True
    assert count_resources(database_url) == 1


def test_insert_duplicate(temp_db):
    """Test inserting duplicate resource (should update)."""
    database_url, db_path = temp_db
    
    # Insert first time
    success1 = insert_resource(
        database_url,
        source='genius',
        source_id='test_123',
        title='Test Song',
        content='Test lyrics',
        score=7.0
    )
    
    # Insert duplicate (should update)
    success2 = insert_resource(
        database_url,
        source='genius',
        source_id='test_123',
        title='Test Song Updated',
        content='Updated lyrics',
        score=8.0
    )
    
    assert success1 is True
    assert success2 is False  # False means updated, not inserted
    assert count_resources(database_url) == 1


def test_get_all_resources(temp_db):
    """Test retrieving all resources."""
    database_url, db_path = temp_db
    
    # Insert some resources
    insert_resource(database_url, 'genius', 'id1', 'Song 1', 'Lyrics 1', score=9.0)
    insert_resource(database_url, 'genius', 'id2', 'Song 2', 'Lyrics 2', score=7.0)
    insert_resource(database_url, 'manual', 'id3', 'Song 3', 'Lyrics 3', score=8.0)
    
    resources = get_all_resources(database_url, limit=10)
    
    assert len(resources) == 3
    # Should be ordered by score descending
    assert resources[0]['score'] == 9.0
    assert resources[1]['score'] == 8.0
    assert resources[2]['score'] == 7.0


def test_database_class_interface(temp_db):
    """Test Database class interface."""
    database_url, db_path = temp_db
    
    db = Database(db_path, interactive=False)
    
    # Insert
    success = db.insert_resource(
        source='manual',
        source_id='test_id',
        title='Test',
        content='Content',
        score=5.0
    )
    
    assert success is True
    assert db.count_resources() == 1
    
    # Get all
    resources = db.get_all_resources(limit=10)
    assert len(resources) == 1
    assert resources[0]['title'] == 'Test'
