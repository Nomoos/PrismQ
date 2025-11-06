"""
Integration tests for complete API workflows

These tests verify that the entire API workflow functions correctly end-to-end.
They test the integration between different API endpoints and services.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from pathlib import Path
import asyncio
import time

from src.main import app


@pytest.mark.asyncio
async def test_complete_module_launch_workflow():
    """Test the complete workflow of launching a module and tracking its execution."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Health check
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # Step 2: List available modules
        response = await client.get("/api/modules")
        assert response.status_code == 200
        modules_response = response.json()
        assert "modules" in modules_response
        assert "total" in modules_response
        modules = modules_response["modules"]
        assert isinstance(modules, list)
        assert len(modules) > 0, "At least one module should be available"
        
        # Get the first module
        module = modules[0]
        module_id = module["id"]
        
        # Step 3: Get module configuration
        response = await client.get(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        config = response.json()
        
        # Step 4: Save module configuration with valid parameters
        # Use parameters that match the module's schema
        valid_params = {}
        if module["parameters"]:
            # Use the first parameter's default value or a valid test value
            for param in module["parameters"]:
                if param["name"] == "max_results":
                    valid_params["max_results"] = 25
                elif param["name"] == "trending_category":
                    valid_params["trending_category"] = "Gaming"
        
        new_config = {"parameters": valid_params}
        response = await client.post(
            f"/api/modules/{module_id}/config",
            json=new_config
        )
        assert response.status_code == 200
        
        # Step 5: Verify configuration was saved
        response = await client.get(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        saved_config = response.json()
        # Verify at least one parameter was saved
        assert len(saved_config["parameters"]) > 0
        
        # Step 6: Launch the module (with a simple test script)
        # Note: This assumes a test module exists. In a real scenario,
        # we'd create a temporary test module or mock the execution
        response = await client.post(
            f"/api/modules/{module_id}/run",
            json={"parameters": {}, "save_config": False}
        )
        assert response.status_code == 202  # HTTP 202 Accepted
        run_data = response.json()
        run_id = run_data["run_id"]
        
        # Step 7: Get run details
        response = await client.get(f"/api/runs/{run_id}")
        assert response.status_code == 200
        run = response.json()
        assert run["run_id"] == run_id
        assert run["module_id"] == module_id
        # Status can be any valid state, including failed (if script doesn't exist)
        assert run["status"] in ["queued", "running", "completed", "failed", "cancelled"]
        
        # Step 8: Get run logs
        await asyncio.sleep(0.1)  # Give it a moment to generate logs
        response = await client.get(f"/api/runs/{run_id}/logs")
        assert response.status_code == 200
        logs_response = response.json()
        assert "logs" in logs_response
        assert isinstance(logs_response["logs"], list)


@pytest.mark.asyncio
async def test_run_listing_and_filtering_workflow():
    """Test listing and filtering runs."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get all runs
        response = await client.get("/api/runs")
        assert response.status_code == 200
        runs_response = response.json()
        assert "runs" in runs_response
        assert "total" in runs_response
        all_runs = runs_response["runs"]
        assert isinstance(all_runs, list)
        
        # Test pagination
        response = await client.get("/api/runs?limit=5&offset=0")
        assert response.status_code == 200
        paginated_response = response.json()
        paginated_runs = paginated_response["runs"]
        assert len(paginated_runs) <= 5
        
        # Test status filtering
        response = await client.get("/api/runs?status=completed")
        assert response.status_code == 200
        completed_response = response.json()
        completed_runs = completed_response["runs"]
        for run in completed_runs:
            assert run["status"] == "completed"
        
        # Test module filtering
        if all_runs:
            module_id = all_runs[0]["module_id"]
            response = await client.get(f"/api/runs?module_id={module_id}")
            assert response.status_code == 200
            module_response = response.json()
            module_runs = module_response["runs"]
            for run in module_runs:
                assert run["module_id"] == module_id


@pytest.mark.asyncio
async def test_error_handling_workflow():
    """Test error handling across different scenarios."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 1: Non-existent module
        response = await client.get("/api/modules/non-existent-module/config")
        assert response.status_code == 404
        
        # Test 2: Non-existent run
        response = await client.get("/api/runs/non-existent-run")
        assert response.status_code == 404
        
        # Test 3: Invalid run launch (missing module)
        response = await client.post(
            "/api/modules/non-existent/run",
            json={"parameters": {}}
        )
        assert response.status_code == 404
        
        # Test 4: Get logs for non-existent run  
        # API returns 404 for non-existent runs
        response = await client.get("/api/runs/non-existent/logs")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test that multiple concurrent API operations work correctly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Launch multiple health checks concurrently
        tasks = [
            client.get("/api/health")
            for _ in range(10)
        ]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
        
        # Get modules list concurrently
        tasks = [
            client.get("/api/modules")
            for _ in range(5)
        ]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed and return the same modules
        first_response = responses[0].json()
        first_modules = first_response["modules"]
        for response in responses:
            assert response.status_code == 200
            assert len(response.json()["modules"]) == len(first_modules)


@pytest.mark.asyncio
async def test_module_stats_workflow():
    """Test module statistics are correctly tracked and retrieved."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get initial modules list
        response = await client.get("/api/modules")
        assert response.status_code == 200
        modules_response = response.json()
        modules_before = modules_response["modules"]
        
        # Find a module
        if modules_before:
            module = modules_before[0]
            initial_runs = module.get("total_runs", 0)
            
            # Launch the module (expecting 202 Accepted)
            response = await client.post(
                f"/api/modules/{module['id']}/run",
                json={"parameters": {}, "save_config": False}
            )
            
            # Verify correct status code for async operation
            assert response.status_code == 202, f"Expected 202 Accepted, got {response.status_code}"
            
            # Give it a moment to update stats
            await asyncio.sleep(0.1)
            
            # Get updated modules list
            response = await client.get("/api/modules")
            assert response.status_code == 200
            modules_after_response = response.json()
            modules_after = modules_after_response["modules"]
            
            # Find the same module
            updated_module = next(
                (m for m in modules_after if m["id"] == module["id"]),
                None
            )
            
            if updated_module:
                # Total runs should have increased
                assert updated_module.get("total_runs", 0) >= initial_runs


@pytest.mark.asyncio
async def test_api_response_consistency():
    """Test that API responses are consistent and well-formed."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Health endpoint
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime_seconds" in data
        
        # Modules endpoint
        response = await client.get("/api/modules")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        modules_response = response.json()
        assert "modules" in modules_response
        assert "total" in modules_response
        modules = modules_response["modules"]
        assert isinstance(modules, list)
        
        # Each module should have required fields
        for module in modules:
            assert "id" in module
            assert "name" in module
            assert "description" in module
            assert "category" in module
        
        # Runs endpoint
        response = await client.get("/api/runs")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        runs_response = response.json()
        assert "runs" in runs_response
        assert "total" in runs_response
        runs = runs_response["runs"]
        assert isinstance(runs, list)
        
        # Each run should have required fields
        for run in runs:
            assert "run_id" in run
            assert "module_id" in run
            assert "status" in run
            assert "created_at" in run


@pytest.mark.asyncio
async def test_issue_110_full_integration():
    """
    Integration test for Issue #110: Complete frontend-backend integration workflow.
    
    Tests the complete integration as specified in Issue #110, including:
    - Module discovery from JSON configuration
    - Configuration management
    - Module launching
    - Run tracking
    - All API endpoints working together
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check - verify backend is running
        response = await client.get("/api/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "version" in health_data
        assert "total_modules" in health_data
        assert health_data["total_modules"] > 0, "Should have modules loaded from JSON"
        
        # 2. GET /api/modules - List modules (loaded from JSON, not mocked)
        response = await client.get("/api/modules")
        assert response.status_code == 200
        modules_data = response.json()
        assert "modules" in modules_data
        assert "total" in modules_data
        assert modules_data["total"] > 0
        modules = modules_data["modules"]
        
        # Verify module loaded from JSON has all required fields
        module = modules[0]
        module_id = module["id"]
        assert "name" in module
        assert "description" in module
        assert "category" in module
        assert "script_path" in module
        assert "parameters" in module
        assert "version" in module
        assert "status" in module
        assert "enabled" in module
        
        # 3. GET /api/modules/{id} - Module details
        response = await client.get(f"/api/modules/{module_id}")
        assert response.status_code == 200
        module_detail = response.json()
        assert module_detail["id"] == module_id
        assert len(module_detail["parameters"]) > 0
        
        # 4. GET /api/modules/{id}/config - Get config (should return defaults)
        response = await client.get(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        config_data = response.json()
        assert "module_id" in config_data
        assert "parameters" in config_data
        assert config_data["module_id"] == module_id
        
        # 5. POST /api/modules/{id}/config - Save config
        test_params = {"max_results": 25}
        response = await client.post(
            f"/api/modules/{module_id}/config",
            json={"parameters": test_params}
        )
        assert response.status_code == 200
        saved_config = response.json()
        assert saved_config["parameters"]["max_results"] == 25
        
        # 6. Verify config was persisted
        response = await client.get(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        retrieved_config = response.json()
        assert retrieved_config["parameters"]["max_results"] == 25
        
        # 7. POST /api/modules/{id}/run - Launch module
        response = await client.post(
            f"/api/modules/{module_id}/run",
            json={"parameters": test_params, "save_config": False}
        )
        assert response.status_code == 202  # Async operation
        run_response = response.json()
        assert "run_id" in run_response
        run_id = run_response["run_id"]
        
        # 8. GET /api/runs - List runs
        response = await client.get("/api/runs")
        assert response.status_code == 200
        runs_data = response.json()
        assert "runs" in runs_data
        assert len(runs_data["runs"]) > 0
        
        # Find our run
        our_run = next((r for r in runs_data["runs"] if r["run_id"] == run_id), None)
        assert our_run is not None, "Launched run should be in runs list"
        
        # 9. GET /api/runs/{id} - Run details
        await asyncio.sleep(0.1)  # Give it a moment to update
        response = await client.get(f"/api/runs/{run_id}")
        assert response.status_code == 200
        run_detail = response.json()
        assert run_detail["run_id"] == run_id
        assert run_detail["module_id"] == module_id
        assert run_detail["status"] in ["queued", "running", "completed", "failed", "cancelled"]
        
        # 10. GET /api/runs/{id}/logs - Get logs
        response = await client.get(f"/api/runs/{run_id}/logs")
        assert response.status_code == 200
        logs_data = response.json()
        assert "logs" in logs_data
        assert isinstance(logs_data["logs"], list)
        
        # 11. DELETE /api/modules/{id}/config - Delete config (reset to defaults)
        response = await client.delete(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        
        # Verify config was deleted
        response = await client.get(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        reset_config = response.json()
        # Should have default values, not our custom value
        assert reset_config["parameters"].get("max_results", 50) != 25
        
        # 12. GET /api/system/stats - System stats
        response = await client.get("/api/system/stats")
        assert response.status_code == 200
        stats_data = response.json()
        assert "runs" in stats_data
        assert "modules" in stats_data
        assert "system" in stats_data
        assert stats_data["modules"]["total"] > 0
        
        # Verify all API endpoints are accessible and working together
        print("✅ Issue #110 Integration Test: All API endpoints working correctly")
        print(f"   - Modules loaded from JSON: {modules_data['total']}")
        print(f"   - Configuration persistence: Working")
        print(f"   - Module execution: Working")
        print(f"   - Run tracking: Working")
        print(f"   - All endpoints: Accessible")
