"""
Tests for caching optimizations in the PrismQ Client Backend.

These tests verify that caching is working correctly and improving performance.
"""

import asyncio
import time
import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.mark.asyncio
async def test_system_stats_caching():
    """Test that system stats endpoint uses caching effectively."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First call - cache miss
        start1 = time.time()
        response1 = await client.get("/api/system/stats")
        end1 = time.time()
        time1_ms = (end1 - start1) * 1000
        
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second call immediately after - should be cached
        start2 = time.time()
        response2 = await client.get("/api/system/stats")
        end2 = time.time()
        time2_ms = (end2 - start2) * 1000
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Verify cache hit is significantly faster
        assert time2_ms < 20, f"Cached request {time2_ms:.2f}ms should be <20ms"
        assert time2_ms < time1_ms / 5, f"Cached request should be at least 5x faster"
        
        # Data should be identical (from cache)
        assert data1 == data2


@pytest.mark.asyncio
async def test_system_stats_cache_expiration():
    """Test that system stats cache expires after TTL."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First call - cache miss
        response1 = await client.get("/api/system/stats")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second call immediately - should be cached
        start2 = time.time()
        response2 = await client.get("/api/system/stats")
        end2 = time.time()
        time2_ms = (end2 - start2) * 1000
        
        assert response2.status_code == 200
        assert time2_ms < 10, "Should be cached"
        
        # Wait for cache to expire (TTL is 2 seconds)
        await asyncio.sleep(2.5)
        
        # Third call after expiration - cache miss again
        start3 = time.time()
        response3 = await client.get("/api/system/stats")
        end3 = time.time()
        time3_ms = (end3 - start3) * 1000
        
        assert response3.status_code == 200
        # This should be slower than the cached call
        assert time3_ms > 10, f"Expired cache call {time3_ms:.2f}ms should be >10ms"


@pytest.mark.asyncio
async def test_module_loader_singleton():
    """Test that module loader is reused (singleton pattern)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Multiple calls to modules endpoint should reuse the same loader
        times = []
        
        for _ in range(5):
            start = time.time()
            response = await client.get("/api/modules")
            end = time.time()
            
            assert response.status_code == 200
            times.append((end - start) * 1000)
        
        # All calls should be fast (loader is cached)
        avg_time = sum(times) / len(times)
        assert avg_time < 50, f"Average time {avg_time:.2f}ms should be <50ms with cached loader"
        
        # Times should be relatively consistent (no repeated loading)
        max_time = max(times)
        min_time = min(times)
        variance = max_time - min_time
        assert variance < 50, f"Variance {variance:.2f}ms indicates inconsistent performance"


@pytest.mark.asyncio
async def test_concurrent_cached_requests():
    """Test that multiple concurrent requests benefit from caching."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First request to warm up cache
        await client.get("/api/system/stats")
        await asyncio.sleep(0.1)
        
        # Multiple concurrent requests
        async def make_request():
            start = time.time()
            response = await client.get("/api/system/stats")
            end = time.time()
            return response, (end - start) * 1000
        
        # Create 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for response, response_time in results:
            assert response.status_code == 200
        
        # Most should be very fast (cached)
        fast_requests = sum(1 for _, t in results if t < 10)
        assert fast_requests >= 8, f"At least 8/10 requests should hit cache (<10ms), got {fast_requests}"


@pytest.mark.asyncio
async def test_config_endpoint_performance():
    """Test that config endpoints are fast (file I/O is fast)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        module_id = "youtube-shorts"
        
        # Save config
        start_save = time.time()
        save_response = await client.post(
            f"/api/modules/{module_id}/config",
            json={"parameters": {"max_results": 50}}
        )
        end_save = time.time()
        save_time_ms = (end_save - start_save) * 1000
        
        assert save_response.status_code == 200
        assert save_time_ms < 100, f"Config save {save_time_ms:.2f}ms should be <100ms"
        
        # Get config
        start_get = time.time()
        get_response = await client.get(f"/api/modules/{module_id}/config")
        end_get = time.time()
        get_time_ms = (end_get - start_get) * 1000
        
        assert get_response.status_code == 200
        assert get_time_ms < 50, f"Config get {get_time_ms:.2f}ms should be <50ms"
        
        # Verify data
        assert get_response.json()["parameters"]["max_results"] == 50


@pytest.mark.asyncio
async def test_log_retrieval_with_tail():
    """Test that log retrieval with tail parameter is fast."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a run
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {}, "save_config": False}
        )
        run_id = create_response.json()["run_id"]
        
        # Get logs with tail
        start = time.time()
        response = await client.get(f"/api/runs/{run_id}/logs?tail=100")
        end = time.time()
        response_time_ms = (end - start) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 50, f"Log retrieval {response_time_ms:.2f}ms should be <50ms"
        
        # Cleanup
        await client.delete(f"/api/runs/{run_id}")


@pytest.mark.asyncio
async def test_health_check_performance():
    """Test that health check is extremely fast (no expensive operations)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        times = []
        
        # Make multiple health check calls
        for _ in range(10):
            start = time.time()
            response = await client.get("/api/health")
            end = time.time()
            
            assert response.status_code == 200
            times.append((end - start) * 1000)
        
        # All should be very fast
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        assert avg_time < 20, f"Average health check {avg_time:.2f}ms should be <20ms"
        assert max_time < 50, f"Max health check {max_time:.2f}ms should be <50ms"
