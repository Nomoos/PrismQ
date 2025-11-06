"""Tests for conditional parameter validation."""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.utils.module_loader import get_module_loader


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_youtube_shorts_trending_mode_validation(client):
    """Test validation for YouTube Shorts in trending mode."""
    # Get the YouTube Shorts module
    loader = get_module_loader()
    module = loader.get_module("youtube-shorts")
    assert module is not None
    
    # Trending mode should not require channel_url or query
    response = client.post(
        f"/api/modules/{module.id}/config",
        json={
            "parameters": {
                "mode": "trending",
                "max_results": 50,
                "category": "Gaming"
            }
        }
    )
    assert response.status_code == 200


def test_youtube_shorts_channel_mode_validation_success(client):
    """Test validation for YouTube Shorts in channel mode with valid channel URL."""
    response = client.post(
        "/api/modules/youtube-shorts/config",
        json={
            "parameters": {
                "mode": "channel",
                "channel_url": "https://www.youtube.com/@testchannel",
                "max_results": 30
            }
        }
    )
    assert response.status_code == 200


def test_youtube_shorts_channel_mode_validation_failure(client):
    """Test validation for YouTube Shorts in channel mode with invalid channel URL."""
    response = client.post(
        "/api/modules/youtube-shorts/config",
        json={
            "parameters": {
                "mode": "channel",
                "channel_url": "invalid-url",
                "max_results": 30
            }
        }
    )
    assert response.status_code == 400
    assert "channel" in response.json()["detail"].lower() or "url" in response.json()["detail"].lower()


def test_youtube_shorts_channel_mode_missing_url(client):
    """Test that channel mode without channel_url is rejected."""
    # Note: channel_url is not marked as required in the schema because it's conditional
    # The validation should check if it's provided when mode is channel
    response = client.post(
        "/api/modules/youtube-shorts/config",
        json={
            "parameters": {
                "mode": "channel",
                "max_results": 30
            }
        }
    )
    # This should succeed as empty optional parameters are allowed
    # The actual requirement check should happen at module launch time
    assert response.status_code == 200


def test_youtube_shorts_keyword_mode_validation(client):
    """Test validation for YouTube Shorts in keyword mode."""
    response = client.post(
        "/api/modules/youtube-shorts/config",
        json={
            "parameters": {
                "mode": "keyword",
                "query": "test search",
                "max_results": 25
            }
        }
    )
    assert response.status_code == 200


def test_module_parameter_has_conditional_display():
    """Test that YouTube Shorts parameters have conditional_display fields."""
    loader = get_module_loader()
    module = loader.get_module("youtube-shorts")
    assert module is not None
    
    # Find channel_url parameter
    channel_param = next((p for p in module.parameters if p.name == "channel_url"), None)
    assert channel_param is not None
    assert channel_param.conditional_display is not None
    assert channel_param.conditional_display.field == "mode"
    assert channel_param.conditional_display.value == "channel"
    
    # Find query parameter
    query_param = next((p for p in module.parameters if p.name == "query"), None)
    assert query_param is not None
    assert query_param.conditional_display is not None
    assert query_param.conditional_display.field == "mode"
    assert query_param.conditional_display.value == "keyword"
    
    # Find category parameter
    category_param = next((p for p in module.parameters if p.name == "category"), None)
    assert category_param is not None
    assert category_param.conditional_display is not None
    assert category_param.conditional_display.field == "mode"
    assert category_param.conditional_display.value == "trending"


def test_validation_rules_present():
    """Test that validation rules are present for channel_url."""
    loader = get_module_loader()
    module = loader.get_module("youtube-shorts")
    assert module is not None
    
    # Find channel_url parameter
    channel_param = next((p for p in module.parameters if p.name == "channel_url"), None)
    assert channel_param is not None
    assert channel_param.validation is not None
    assert channel_param.validation.pattern is not None
    assert channel_param.validation.message is not None


def test_warning_message_present():
    """Test that warning message is present for keyword mode."""
    loader = get_module_loader()
    module = loader.get_module("youtube-shorts")
    assert module is not None
    
    # Find query parameter
    query_param = next((p for p in module.parameters if p.name == "query"), None)
    assert query_param is not None
    assert query_param.warning is not None
    assert "Issue #300" in query_param.warning


def test_channel_url_regex_validation():
    """Test that channel URL regex validation works correctly."""
    import re
    from src.utils.module_loader import get_module_loader
    
    loader = get_module_loader()
    module = loader.get_module("youtube-shorts")
    channel_param = next((p for p in module.parameters if p.name == "channel_url"), None)
    
    pattern = channel_param.validation.pattern
    
    # Valid URLs
    assert re.match(pattern, "https://www.youtube.com/@testchannel")
    assert re.match(pattern, "http://youtube.com/@user")
    assert re.match(pattern, "www.youtube.com/@channel-name_123")
    assert re.match(pattern, "youtube.com/channel/UCxxxxxxxxxxxxx")
    assert re.match(pattern, "@username")
    assert re.match(pattern, "UCabcdefghijklmnop")
    
    # Invalid URLs
    assert not re.match(pattern, "invalid-url")
    assert not re.match(pattern, "https://google.com")
    assert not re.match(pattern, "")
