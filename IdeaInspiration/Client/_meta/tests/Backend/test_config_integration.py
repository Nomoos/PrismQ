"""Integration tests for configuration persistence API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status

from src.main import app
from src.core import get_config_storage


@pytest.fixture(autouse=True)
def cleanup_configs():
    """Clean up config files before and after each test."""
    storage = get_config_storage()
    
    # Clean before test
    for module_id in storage.list_configs():
        storage.delete_config(module_id)
    
    yield
    
    # Clean after test
    for module_id in storage.list_configs():
        storage.delete_config(module_id)


@pytest.mark.asyncio
async def test_get_config_with_no_saved_config():
    """Test getting config when no config is saved returns defaults."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/modules/youtube-shorts/config")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["module_id"] == "youtube-shorts"
    assert "parameters" in data
    # Should have defaults from module definition
    assert data["parameters"]["max_results"] == 50
    assert data["parameters"]["trending_category"] == "All"


@pytest.mark.asyncio
async def test_save_and_get_config():
    """Test saving a config and retrieving it."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save config
        save_response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 100, "trending_category": "Gaming"}},
        )
        
        assert save_response.status_code == status.HTTP_200_OK
        save_data = save_response.json()
        assert save_data["parameters"]["max_results"] == 100
        assert save_data["parameters"]["trending_category"] == "Gaming"
        
        # Get config
        get_response = await client.get("/api/modules/youtube-shorts/config")
        
        assert get_response.status_code == status.HTTP_200_OK
        get_data = get_response.json()
        assert get_data["parameters"]["max_results"] == 100
        assert get_data["parameters"]["trending_category"] == "Gaming"


@pytest.mark.asyncio
async def test_save_config_validation():
    """Test that invalid parameters are rejected."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test invalid number type
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": "not a number"}},
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid parameters" in response.json()["detail"]


@pytest.mark.asyncio
async def test_save_config_validates_min_max():
    """Test that min/max constraints are enforced."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test value below min
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 0}},
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must be >=" in response.json()["detail"]
        
        # Test value above max
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 2000}},
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must be <=" in response.json()["detail"]


@pytest.mark.asyncio
async def test_save_config_validates_select_options():
    """Test that select parameters validate against allowed options."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"trending_category": "InvalidCategory"}},
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must be one of" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_config():
    """Test deleting a saved configuration."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save config
        await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 100}},
        )
        
        # Delete config
        delete_response = await client.delete("/api/modules/youtube-shorts/config")
        
        assert delete_response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in delete_response.json()["message"]
        
        # Verify config is gone (defaults returned)
        get_response = await client.get("/api/modules/youtube-shorts/config")
        assert get_response.json()["parameters"]["max_results"] == 50  # Default


@pytest.mark.asyncio
async def test_delete_nonexistent_config():
    """Test deleting a config that doesn't exist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete("/api/modules/youtube-shorts/config")
        
        assert response.status_code == status.HTTP_200_OK
        assert "No configuration to delete" in response.json()["message"]


@pytest.mark.asyncio
async def test_save_config_for_nonexistent_module():
    """Test saving config for a module that doesn't exist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/modules/nonexistent-module/config",
            json={"parameters": {"some_param": "value"}},
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_config_for_nonexistent_module():
    """Test getting config for a module that doesn't exist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/modules/nonexistent-module/config")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_config_persistence_across_runs():
    """Test that saved config persists and is used for module runs."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save config
        await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 200, "trending_category": "Music"}},
        )
        
        # Create run with save_config=True (default)
        run_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 200, "trending_category": "Music"}},
        )
        
        assert run_response.status_code == status.HTTP_202_ACCEPTED
        
        # Verify config is still saved
        get_response = await client.get("/api/modules/youtube-shorts/config")
        assert get_response.json()["parameters"]["max_results"] == 200
        assert get_response.json()["parameters"]["trending_category"] == "Music"


@pytest.mark.asyncio
async def test_run_with_save_config_false():
    """Test that save_config=False doesn't save parameters."""
    storage = get_config_storage()
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create run with save_config=False
        await client.post(
            "/api/modules/youtube-shorts/run",
            json={
                "parameters": {"max_results": 300},
                "save_config": False
            },
        )
        
        # Verify config was not saved
        assert "youtube-shorts" not in storage.list_configs()


@pytest.mark.asyncio
async def test_partial_config_save():
    """Test saving partial parameters merges with defaults."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save only one parameter
        await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 150}},
        )
        
        # Get config should return saved param + defaults for others
        get_response = await client.get("/api/modules/youtube-shorts/config")
        data = get_response.json()
        
        assert data["parameters"]["max_results"] == 150  # Saved
        assert data["parameters"]["trending_category"] == "All"  # Default


@pytest.mark.asyncio
async def test_config_file_structure():
    """Test that config files have correct JSON structure."""
    storage = get_config_storage()
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 100}},
        )
        
    # Verify file exists with correct structure
    import json
    config_file = storage.config_dir / "youtube-shorts.json"
    assert config_file.exists()
    
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    assert data["module_id"] == "youtube-shorts"
    assert data["parameters"]["max_results"] == 100
    assert "updated_at" in data
