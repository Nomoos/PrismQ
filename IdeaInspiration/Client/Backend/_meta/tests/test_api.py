"""Tests for API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status

from src.main import app
from src.core import get_module_runner


@pytest.fixture(autouse=True)
def clear_run_history():
    """Clear run history before each test."""
    runner = get_module_runner()
    runner.registry.runs.clear()
    runner.process_manager.log_buffers.clear()
    yield


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data
    assert "active_runs" in data
    assert "total_modules" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_list_modules():
    """Test listing modules."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/modules")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "modules" in data
    assert "total" in data
    assert data["total"] >= 0


@pytest.mark.asyncio
async def test_get_module():
    """Test getting module details."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/modules/youtube-shorts")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "youtube-shorts"
    assert "name" in data
    assert "description" in data
    assert "parameters" in data


@pytest.mark.asyncio
async def test_get_nonexistent_module():
    """Test getting nonexistent module."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/modules/nonexistent")
        
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_module_config():
    """Test getting module configuration."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/modules/youtube-shorts/config")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["module_id"] == "youtube-shorts"
    assert "parameters" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_update_module_config():
    """Test updating module configuration."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 100, "trending_category": "Gaming"}},
        )
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["module_id"] == "youtube-shorts"
    assert data["parameters"]["max_results"] == 100
    assert data["parameters"]["trending_category"] == "Gaming"


@pytest.mark.asyncio
async def test_create_run():
    """Test creating a new run."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}, "save_config": True},
        )
        
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert "run_id" in data
    assert data["module_id"] == "youtube-shorts"
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_list_runs():
    """Test listing runs."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/runs")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "runs" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


@pytest.mark.asyncio
async def test_get_run():
    """Test getting run details."""
    # First create a run
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]
        
        # Now get the run
        response = await client.get(f"/api/runs/{run_id}")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["run_id"] == run_id


@pytest.mark.asyncio
async def test_get_nonexistent_run():
    """Test getting nonexistent run."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/runs/nonexistent")
        
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_cancel_run():
    """Test cancelling a run."""
    # First create a run
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]
        
        # Now cancel the run
        response = await client.delete(f"/api/runs/{run_id}")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_get_run_logs():
    """Test getting run logs."""
    # First create a run
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]
        
        # Now get the logs
        response = await client.get(f"/api/runs/{run_id}/logs")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["run_id"] == run_id
    assert "logs" in data
    assert "total_lines" in data
    assert "truncated" in data


@pytest.mark.asyncio
async def test_get_run_results():
    """Test getting run results."""
    # First create a run
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]
        
        # Now get the results
        response = await client.get(f"/api/runs/{run_id}/results")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["run_id"] == run_id
    assert "status" in data
    assert "summary" in data
    assert "output_files" in data


@pytest.mark.asyncio
async def test_system_stats():
    """Test getting system statistics."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/system/stats")
        
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "runs" in data
    assert "modules" in data
    assert "system" in data
