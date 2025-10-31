"""Tests for exception handling."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status

from src.main import app
from src.core import get_module_runner
from src.core.exceptions import (
    ModuleNotFoundException,
    RunNotFoundException,
    ResourceLimitException,
    ValidationException,
)


@pytest.fixture(autouse=True)
def clear_run_history():
    """Clear run history before each test."""
    runner = get_module_runner()
    runner.registry.runs.clear()
    runner.process_manager.log_buffers.clear()
    yield


@pytest.mark.asyncio
async def test_module_not_found_exception():
    """Test that ModuleNotFoundException returns 404."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/modules/nonexistent-module")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "error_code" in data
    assert data["error_code"] == "MODULE_NOT_FOUND"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_run_not_found_exception():
    """Test that RunNotFoundException returns 404."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/runs/nonexistent-run")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert "error_code" in data
    assert data["error_code"] == "RUN_NOT_FOUND"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_validation_exception_in_run_create():
    """Test that ValidationException from pydantic validation returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create run with too many parameters (>100)
        parameters = {f"param_{i}": i for i in range(101)}
        response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": parameters, "save_config": True}
        )
    
    # Pydantic validation error should return 422
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_validation_exception_forbidden_parameter():
    """Test that forbidden parameter names are rejected."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try to use forbidden parameter name
        response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"__internal__": "value"}, "save_config": True}
        )
    
    # Pydantic validation error should return 422
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_error_response_structure():
    """Test that error responses have consistent structure."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/modules/nonexistent")
    
    data = response.json()
    # Check required fields are present
    assert "detail" in data
    assert "error_code" in data
    assert "timestamp" in data
    
    # Check timestamp is ISO format
    from datetime import datetime
    datetime.fromisoformat(data["timestamp"])  # Should not raise


@pytest.mark.asyncio
async def test_concurrent_runs_limit():
    """Test that exceeding concurrent run limit returns 409."""
    # This would require setting max_concurrent_runs to a low value
    # and creating multiple runs. For now, we just test the concept.
    # In a real scenario, we'd set max_concurrent_runs=1 and create 2 runs
    pass  # TODO: Implement once we can configure max_concurrent_runs in tests
