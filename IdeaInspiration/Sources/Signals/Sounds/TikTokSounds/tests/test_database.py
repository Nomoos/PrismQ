"""Tests for database operations."""

import pytest
import tempfile
from pathlib import Path
from src.core.database import Database


@pytest.fixture
def db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    database = Database(db_path, interactive=False)
    yield database
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


def test_database_initialization(db):
    """Test that database is initialized correctly."""
    assert Path(db.database_path).exists()


def test_insert_signal(db):
    """Test inserting a signal."""
    success = db.insert_signal(
        source='google_trends',
        source_id='test_query_US_20250101',
        signal_type='trend',
        name='Test Query',
        description='A test trending query',
        tags='google,search,trend',
        metrics={'volume': 100, 'velocity': 10.5},
        temporal={'first_seen': '2025-01-01T00:00:00Z', 'current_status': 'rising'}
    )
    
    assert success is True


def test_duplicate_signal(db):
    """Test that duplicate signals are rejected."""
    # Insert first signal
    db.insert_signal(
        source='google_trends',
        source_id='test_query_US_20250101',
        signal_type='trend',
        name='Test Query'
    )
    
    # Try to insert duplicate
    success = db.insert_signal(
        source='google_trends',
        source_id='test_query_US_20250101',
        signal_type='trend',
        name='Test Query Duplicate'
    )
    
    assert success is False


def test_get_all_signals(db):
    """Test retrieving all signals."""
    # Insert multiple signals
    for i in range(3):
        db.insert_signal(
            source='google_trends',
            source_id=f'query_{i}_US_20250101',
            signal_type='trend',
            name=f'Query {i}'
        )
    
    signals = db.get_all_signals()
    assert len(signals) == 3


def test_get_signals_by_type(db):
    """Test filtering signals by type."""
    # Insert signals of different types
    db.insert_signal(
        source='google_trends',
        source_id='trend_1',
        signal_type='trend',
        name='Trend 1'
    )
    db.insert_signal(
        source='google_trends',
        source_id='hashtag_1',
        signal_type='hashtag',
        name='Hashtag 1'
    )
    
    trends = db.get_signals_by_type('trend')
    hashtags = db.get_signals_by_type('hashtag')
    
    assert len(trends) == 1
    assert len(hashtags) == 1
    assert trends[0]['signal_type'] == 'trend'


def test_get_signal_count(db):
    """Test getting signal count."""
    # Initially empty
    assert db.get_signal_count() == 0
    
    # Insert signals
    for i in range(5):
        db.insert_signal(
            source='google_trends',
            source_id=f'query_{i}',
            signal_type='trend',
            name=f'Query {i}'
        )
    
    assert db.get_signal_count() == 5


def test_metrics_serialization(db):
    """Test that metrics are properly serialized/deserialized."""
    metrics = {
        'volume': 100,
        'velocity': 15.5,
        'acceleration': 2.3,
        'geographic_spread': ['US', 'UK', 'CA']
    }
    
    db.insert_signal(
        source='google_trends',
        source_id='test_metrics',
        signal_type='trend',
        name='Test Metrics',
        metrics=metrics
    )
    
    signals = db.get_all_signals()
    assert len(signals) == 1
    
    retrieved_metrics = signals[0]['metrics']
    assert retrieved_metrics['volume'] == 100
    assert retrieved_metrics['velocity'] == 15.5
    assert isinstance(retrieved_metrics['geographic_spread'], list)
    assert len(retrieved_metrics['geographic_spread']) == 3
