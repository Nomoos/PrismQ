"""
Performance tests for PrismQ Client Backend API.

Tests API response times and resource usage to ensure performance targets are met.
"""

import asyncio
import time
from typing import List
import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.mark.asyncio
async def test_health_endpoint_response_time():
    """Test that health endpoint responds within 100ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_time = time.time()
        response = await client.get("/api/health")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100, f"Response time {response_time_ms:.2f}ms exceeds 100ms target"


@pytest.mark.asyncio
async def test_list_modules_response_time():
    """Test that listing modules responds within 100ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_time = time.time()
        response = await client.get("/api/modules")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100, f"Response time {response_time_ms:.2f}ms exceeds 100ms target"


@pytest.mark.asyncio
async def test_list_runs_response_time():
    """Test that listing runs responds within 100ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_time = time.time()
        response = await client.get("/api/runs")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100, f"Response time {response_time_ms:.2f}ms exceeds 100ms target"


@pytest.mark.asyncio
async def test_get_module_config_response_time():
    """Test that getting module config responds within 100ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_time = time.time()
        response = await client.get("/api/modules/youtube-shorts/config")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100, f"Response time {response_time_ms:.2f}ms exceeds 100ms target"


@pytest.mark.asyncio
async def test_concurrent_requests_performance():
    """Test that API can handle 10 concurrent requests efficiently."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        
        async def make_request():
            start = time.time()
            response = await client.get("/api/modules")
            end = time.time()
            return response, (end - start) * 1000
        
        # Create 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time_ms = (end_time - start_time) * 1000
        
        # All requests should succeed
        for response, response_time in results:
            assert response.status_code == 200
        
        # Average response time should be reasonable
        avg_response_time = sum(rt for _, rt in results) / len(results)
        assert avg_response_time < 150, f"Average response time {avg_response_time:.2f}ms too high"
        
        # Total time for 10 concurrent requests should be much less than 10x sequential
        # (indicating they are truly concurrent)
        assert total_time_ms < 500, f"Total time {total_time_ms:.2f}ms indicates poor concurrency"


@pytest.mark.asyncio
async def test_rapid_sequential_requests():
    """Test rapid sequential API requests (simulating frontend polling)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response_times: List[float] = []
        
        # Make 20 rapid sequential requests
        for _ in range(20):
            start = time.time()
            response = await client.get("/api/runs")
            end = time.time()
            
            assert response.status_code == 200
            response_times.append((end - start) * 1000)
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        # Performance should be consistent
        assert avg_time < 100, f"Average response time {avg_time:.2f}ms exceeds target"
        assert max_time < 200, f"Max response time {max_time:.2f}ms indicates degradation"


@pytest.mark.asyncio
async def test_system_stats_response_time():
    """Test that system stats endpoint responds within 100ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_time = time.time()
        response = await client.get("/api/system/stats")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100, f"Response time {response_time_ms:.2f}ms exceeds 100ms target"


@pytest.mark.asyncio
async def test_module_launch_performance():
    """Test that module launch responds within 500ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_time = time.time()
        response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 10}, "save_config": False}
        )
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 202
        assert response_time_ms < 500, f"Launch time {response_time_ms:.2f}ms exceeds 500ms target"
        
        # Clean up
        run_id = response.json()["run_id"]
        await client.delete(f"/api/runs/{run_id}")


@pytest.mark.asyncio 
async def test_config_save_performance():
    """Test that saving config responds within 100ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start_time = time.time()
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 50, "category": "Gaming"}}
        )
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100, f"Save time {response_time_ms:.2f}ms exceeds 100ms target"


@pytest.mark.asyncio
async def test_get_run_details_performance():
    """Test that getting run details responds within 100ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a run first
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {}, "save_config": False}
        )
        run_id = create_response.json()["run_id"]
        
        # Test performance of getting run details
        start_time = time.time()
        response = await client.get(f"/api/runs/{run_id}")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100, f"Response time {response_time_ms:.2f}ms exceeds 100ms target"
        
        # Clean up
        await client.delete(f"/api/runs/{run_id}")


@pytest.mark.asyncio
async def test_get_logs_performance():
    """Test that getting logs responds within 100ms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a run first
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {}, "save_config": False}
        )
        run_id = create_response.json()["run_id"]
        
        # Test performance of getting logs
        start_time = time.time()
        response = await client.get(f"/api/runs/{run_id}/logs")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100, f"Response time {response_time_ms:.2f}ms exceeds 100ms target"
        
        # Clean up
        await client.delete(f"/api/runs/{run_id}")
