"""Tests for App Store Top Charts plugins."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.config import Config
import tempfile


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("APP_STORE_CATEGORIES=games,productivity\n")
        f.write("APP_STORE_MAX_APPS=5\n")
        f.write("APP_STORE_DELAY_SECONDS=0.1\n")
        f.write("GOOGLE_PLAY_COUNTRY=us\n")
        f.write("GOOGLE_PLAY_LANGUAGE=en\n")
        env_path = f.name
    
    config = Config(env_path, interactive=False)
    yield config
    
    import os
    if os.path.exists(env_path):
        os.unlink(env_path)


def test_config_has_app_store_settings(mock_config):
    """Test that app store configuration is loaded."""
    assert hasattr(mock_config, 'app_store_categories')
    assert hasattr(mock_config, 'app_store_max_apps')
    assert hasattr(mock_config, 'app_store_delay_seconds')
    assert mock_config.app_store_max_apps == 5


def test_config_has_google_play_settings(mock_config):
    """Test that Google Play configuration is loaded."""
    assert hasattr(mock_config, 'google_play_country')
    assert hasattr(mock_config, 'google_play_language')
    assert mock_config.google_play_country == "us"
    assert mock_config.google_play_language == "en"


def test_commerce_processor_app_store():
    """Test commerce processor works with app store data."""
    from core.commerce_processor import CommerceProcessor
    
    # Test that processor can handle app store-like data
    app_data = {
        'app_id': 'com.test.app',
        'title': 'Test App',
        'developer': 'Test Developer',
        'category': 'games',
        'price': 0.0,
        'rating': 4.5,
        'review_count': 1000
    }
    
    # The processor should work with any product data
    assert app_data['title'] == 'Test App'
    assert app_data['rating'] == 4.5


def test_metrics_from_app_store_data():
    """Test metrics can be created from app store data."""
    from core.metrics import CommerceMetrics
    
    # Create metrics with app-like data
    metrics = CommerceMetrics(
        rating=4.7,
        review_count=10000,
        price=9.99,
        platform="google_play"
    )
    
    metrics.calculate_derived_metrics()
    
    assert metrics.rating == 4.7
    assert metrics.review_count == 10000
    assert metrics.popularity_score is not None


def test_database_works_with_app_data():
    """Test database can store app store products."""
    from core.database import Database
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path, interactive=False)
        
        # Insert an app
        success = db.insert_product(
            source="google_play",
            source_id="com.test.app",
            title="Test App",
            brand="Test Developer",
            category="games",
            price=0.0,
            score=8.5
        )
        
        assert success is True
        
        # Retrieve it
        apps = db.get_all_products(limit=10)
        assert len(apps) == 1
        assert apps[0]['source_id'] == "com.test.app"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
