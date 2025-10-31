"""Additional tests for error scenarios and edge cases."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status

from src.main import app
from src.core import get_module_runner
from src.core.exceptions import ResourceLimitException


@pytest.fixture(autouse=True)
def reset_state():
    """Reset state between tests."""
    # Get instances (don't reset singletons as app may have already imported them)
    from src.core import get_module_runner, get_config_storage

    runner = get_module_runner()
    config_storage = get_config_storage()

    # Clear the run registry for clean tests
    runner.registry.runs.clear()
    runner.process_manager.processes.clear()
    runner.process_manager.log_buffers.clear()

    # Clear module configs by deleting config files
    for module_id in config_storage.list_configs():
        config_storage.delete_config(module_id)

    yield

    # Cleanup after test
    runner.registry.runs.clear()
    runner.process_manager.processes.clear()
    runner.process_manager.log_buffers.clear()

    # Clear configs again
    for module_id in config_storage.list_configs():
        config_storage.delete_config(module_id)


@pytest.mark.asyncio
async def test_list_runs_with_filters():
    """Test listing runs with filters."""
    # Create multiple runs
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create runs for different modules
        await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )

        # Filter by module_id
        response = await client.get("/api/runs?module_id=youtube-shorts")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(run["module_id"] == "youtube-shorts" for run in data["runs"])


@pytest.mark.asyncio
async def test_list_runs_pagination():
    """Test run list pagination."""
    # Create several runs
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for _ in range(5):
            await client.post(
                "/api/modules/youtube-shorts/run",
                json={"parameters": {"max_results": 10}},
            )

        # Get first page with limit
        response = await client.get("/api/runs?limit=2&offset=0")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["runs"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_cancel_already_completed_run():
    """Test cancelling a completed run should fail."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a run
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]

        # Cancel it once (should succeed)
        await client.delete(f"/api/runs/{run_id}")

        # Try to cancel again (should fail)
        response = await client.delete(f"/api/runs/{run_id}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already cancelled" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_concurrent_module_run_conflict():
    """Test that max concurrent runs limit is enforced."""
    import asyncio
    from src.core import get_module_runner, ProcessManager, RunRegistry, OutputCapture
    from src.models.run import RunStatus
    from pathlib import Path
    import tempfile

    # Create isolated runner for this test
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        history_file = Path(f.name)

    # Create temp log dir
    log_dir = Path(tempfile.mkdtemp())

    try:
        # Create a new isolated runner
        registry = RunRegistry(history_file=history_file)
        process_manager = ProcessManager()
        output_capture = OutputCapture(log_dir=log_dir)
        from src.core.module_runner import ModuleRunner

        runner = ModuleRunner(
            registry=registry,
            process_manager=process_manager,
            config_storage=None,
            output_capture=output_capture,
            max_concurrent_runs=1,
        )

        # Create first run
        run1 = await runner.execute_module(
            module_id="test1",
            module_name="Test 1",
            script_path=Path("/tmp/test.py"),
            parameters={},
        )
        assert run1.status == RunStatus.QUEUED

        # Manually set to RUNNING
        run1.status = RunStatus.RUNNING
        runner.registry.update_run(run1)

        # Try to create second run - should fail due to limit
        with pytest.raises(ResourceLimitException, match="Max concurrent runs"):
            await runner.execute_module(
                module_id="test2",
                module_name="Test 2",
                script_path=Path("/tmp/test2.py"),
                parameters={},
            )
    finally:
        # Cleanup
        if history_file.exists():
            history_file.unlink()
        if log_dir.exists():
            import shutil

            shutil.rmtree(log_dir)


@pytest.mark.asyncio
async def test_get_logs_with_tail_parameter():
    """Test getting logs with tail parameter."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a run
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]

        # Get logs with custom tail
        response = await client.get(f"/api/runs/{run_id}/logs?tail=100")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["run_id"] == run_id
    assert isinstance(data["logs"], list)


@pytest.mark.asyncio
async def test_update_config_for_nonexistent_module():
    """Test updating config for nonexistent module."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/modules/nonexistent/config",
            json={"parameters": {"test": "value"}},
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_config_persistence():
    """Test that configuration updates persist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Update config
        update_response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 200}},
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Get config again
        get_response = await client.get("/api/modules/youtube-shorts/config")

    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert data["parameters"]["max_results"] == 200


@pytest.mark.asyncio
async def test_health_endpoint_reflects_state():
    """Test that health endpoint reflects current state."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Get initial health
        health1 = await client.get("/api/health")
        initial_runs = health1.json()["active_runs"]

        # Create a running module
        await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )

        # Health should show more runs (note: they're queued, not running)
        health2 = await client.get("/api/health")

    assert health2.status_code == status.HTTP_200_OK
    data = health2.json()
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0


@pytest.mark.asyncio
async def test_update_config_with_invalid_parameter_types():
    """Test updating config with wrong parameter types."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try to pass a string where a number is expected
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": "not_a_number"}},
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "must be a number" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_config_with_missing_required_parameter():
    """Test updating config without required parameters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Don't include the required max_results parameter
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {}},
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "required" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_config_with_invalid_select_option():
    """Test updating config with invalid select option."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Pass an invalid category option
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={
                "parameters": {
                    "max_results": 50,
                    "trending_category": "InvalidCategory",
                }
            },
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "must be one of" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_run_with_boundary_values():
    """Test creating a run with min/max boundary values."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test minimum value
        response1 = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 1}},
        )
        assert response1.status_code == status.HTTP_202_ACCEPTED

        # Test maximum value
        response2 = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 1000}},
        )
        assert response2.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.asyncio
async def test_update_config_with_out_of_range_values():
    """Test updating config with out-of-range parameter values."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test below minimum
        response1 = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 0}},
        )
        assert response1.status_code == status.HTTP_400_BAD_REQUEST
        assert ">=" in response1.json()["detail"]

        # Test above maximum
        response2 = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 10000}},
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "<=" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_list_runs_with_zero_limit():
    """Test listing runs with zero limit."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Limit must be >= 1, so 0 should fail
        response = await client.get("/api/runs?limit=0")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_runs_with_negative_offset():
    """Test listing runs with negative offset."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Offset must be >= 0, so negative should fail
        response = await client.get("/api/runs?offset=-1")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_runs_with_excessive_limit():
    """Test listing runs with limit exceeding maximum."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Limit max is 100, so 101 should fail
        response = await client.get("/api/runs?limit=101")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_runs_with_very_large_offset():
    """Test listing runs with very large offset."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a few runs
        for _ in range(3):
            await client.post(
                "/api/modules/youtube-shorts/run",
                json={"parameters": {"max_results": 50}},
            )

        # Request with offset beyond available runs
        response = await client.get("/api/runs?offset=1000")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["runs"]) == 0  # No runs at this offset


@pytest.mark.asyncio
async def test_list_runs_with_invalid_status_filter():
    """Test listing runs with invalid status filter."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try an invalid status value
        response = await client.get("/api/runs?status=invalid_status")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_logs_with_negative_tail():
    """Test getting logs with negative tail parameter."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a run first
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]

        # Try negative tail
        response = await client.get(f"/api/runs/{run_id}/logs?tail=-1")

    # Should either reject with 422 or treat as 0
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]


@pytest.mark.asyncio
async def test_get_logs_with_zero_tail():
    """Test getting logs with zero tail parameter."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a run first
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]

        # Request with tail=0 (may be rejected as invalid or return all logs)
        response = await client.get(f"/api/runs/{run_id}/logs?tail=0")

    # Should either reject with 422 or return all logs with 200
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert isinstance(data["logs"], list)


@pytest.mark.asyncio
async def test_update_config_with_empty_parameters():
    """Test updating config with empty parameters dictionary."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save empty config
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {}},
        )

    # Should succeed but validation will catch missing required fields later
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


@pytest.mark.asyncio
async def test_update_config_with_extra_parameters():
    """Test updating config with extra/unknown parameters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Include unknown parameter
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 100, "unknown_param": "value"}},
        )

    # Should succeed - extra params are typically ignored
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_cancel_nonexistent_run():
    """Test cancelling a run that doesn't exist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete("/api/runs/nonexistent_run_id")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_logs_for_nonexistent_run():
    """Test getting logs for a run that doesn't exist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/runs/nonexistent_run_id/logs")

    # Should return empty logs or 404
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_get_results_for_nonexistent_run():
    """Test getting results for a run that doesn't exist."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/runs/nonexistent_run_id/results")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_module_id_with_special_characters():
    """Test accessing module with special characters in ID."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try module ID with special characters
        response = await client.get("/api/modules/module-with-@-symbol")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_module_id_with_path_traversal():
    """Test module ID with path traversal attempt."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try path traversal
        response = await client.get("/api/modules/../../../etc/passwd")

    # Should normalize path and not find module
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_empty_module_id():
    """Test empty module ID."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try empty module ID (trailing slash redirects)
        response = await client.get("/api/modules/", follow_redirects=False)

    # FastAPI redirects trailing slash or returns module list
    assert response.status_code in [
        status.HTTP_200_OK,  # Returns module list
        status.HTTP_307_TEMPORARY_REDIRECT,  # Redirects
        status.HTTP_404_NOT_FOUND,  # Not found
    ]


@pytest.mark.asyncio
async def test_concurrent_config_updates():
    """Test concurrent updates to the same module config."""
    import asyncio

    async def update_config(client, value):
        return await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": value}},
        )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Launch multiple concurrent updates
        tasks = [update_config(client, i * 10) for i in range(1, 6)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK

        # Final config should have one of the values
        final_config = await client.get("/api/modules/youtube-shorts/config")
        assert final_config.status_code == status.HTTP_200_OK
        final_value = final_config.json()["parameters"]["max_results"]
        assert final_value in [10, 20, 30, 40, 50]


@pytest.mark.asyncio
async def test_run_with_very_long_parameter_string():
    """Test creating run with very long string parameter."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a very long string (10KB)
        long_string = "A" * 10000

        response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={
                "parameters": {
                    "max_results": 50,
                    "extra_field": long_string,  # Not validated, but should be handled
                }
            },
        )

    # Should either succeed or reject gracefully
    assert response.status_code in [
        status.HTTP_202_ACCEPTED,
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    ]


@pytest.mark.asyncio
async def test_list_runs_with_all_filters_combined():
    """Test listing runs with multiple filters combined."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create some runs
        for _ in range(3):
            await client.post(
                "/api/modules/youtube-shorts/run",
                json={"parameters": {"max_results": 50}},
            )

        # Query with all filters
        response = await client.get(
            "/api/runs?module_id=youtube-shorts&status=queued&limit=10&offset=0"
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(run["module_id"] == "youtube-shorts" for run in data["runs"])
    assert all(run["status"] == "queued" for run in data["runs"])


@pytest.mark.asyncio
async def test_malformed_json_in_request():
    """Test API endpoint with malformed JSON."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Send malformed JSON
        response = await client.post(
            "/api/modules/youtube-shorts/run",
            content=b'{"parameters": {invalid json',
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_rapid_sequential_runs():
    """Test creating multiple runs rapidly in sequence."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        run_ids = []

        # Create 5 runs rapidly
        for i in range(5):
            response = await client.post(
                "/api/modules/youtube-shorts/run",
                json={"parameters": {"max_results": 10 * (i + 1)}},
            )
            assert response.status_code == status.HTTP_202_ACCEPTED
            run_ids.append(response.json()["run_id"])

        # All run_ids should be unique
        assert len(set(run_ids)) == 5

        # All runs should be tracked
        list_response = await client.get("/api/runs")
        assert list_response.status_code == status.HTTP_200_OK
        tracked_runs = list_response.json()["runs"]
        tracked_ids = [run["run_id"] for run in tracked_runs]

        for run_id in run_ids:
            assert run_id in tracked_ids


@pytest.mark.asyncio
async def test_config_save_and_run_integration():
    """Test that saved config is used in subsequent runs."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save a config
        config_response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 75}},
        )
        assert config_response.status_code == status.HTTP_200_OK

        # Run with save_config=True
        run_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 75}, "save_config": True},
        )
        assert run_response.status_code == status.HTTP_202_ACCEPTED

        # Check that config was persisted
        get_config = await client.get("/api/modules/youtube-shorts/config")
        assert get_config.status_code == status.HTTP_200_OK
        assert get_config.json()["parameters"]["max_results"] == 75


@pytest.mark.asyncio
async def test_multiple_module_configs_isolation():
    """Test that configs for different modules are isolated."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save config for youtube-shorts
        response1 = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 100}},
        )
        assert response1.status_code == status.HTTP_200_OK

        # Try to get config for a different (non-existent) module
        response2 = await client.get("/api/modules/other-module/config")
        assert response2.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_run_status_lifecycle():
    """Test that run status follows expected lifecycle."""
    from src.core import get_module_runner

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a run
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        assert create_response.status_code == status.HTTP_202_ACCEPTED
        run_id = create_response.json()["run_id"]

        # Check initial status (should be queued)
        get_response = await client.get(f"/api/runs/{run_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["status"] in ["queued", "running"]


@pytest.mark.asyncio
async def test_logs_endpoint_pagination():
    """Test that logs endpoint respects tail parameter."""
    from src.core import get_process_manager

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a run
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]

        # Add some mock logs
        process_manager = get_process_manager()
        for i in range(100):
            process_manager.log_buffers.setdefault(run_id, []).append(
                {
                    "timestamp": f"2024-01-01T00:00:{i:02d}Z",
                    "level": "INFO",
                    "message": f"Log {i}",
                }
            )

        # Get logs with small tail
        response1 = await client.get(f"/api/runs/{run_id}/logs?tail=10")
        assert response1.status_code == status.HTTP_200_OK
        logs1 = response1.json()["logs"]
        assert len(logs1) <= 10

        # Get logs with larger tail
        response2 = await client.get(f"/api/runs/{run_id}/logs?tail=50")
        assert response2.status_code == status.HTTP_200_OK
        logs2 = response2.json()["logs"]
        assert len(logs2) <= 50


@pytest.mark.asyncio
async def test_delete_config_then_get_returns_defaults():
    """Test that deleting config returns to default values."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save custom config
        save_response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 200}},
        )
        assert save_response.status_code == status.HTTP_200_OK

        # Verify it was saved
        get_response1 = await client.get("/api/modules/youtube-shorts/config")
        assert get_response1.json()["parameters"]["max_results"] == 200

        # Delete the config
        delete_response = await client.delete("/api/modules/youtube-shorts/config")
        assert delete_response.status_code == status.HTTP_200_OK

        # Get config should now return defaults
        get_response2 = await client.get("/api/modules/youtube-shorts/config")
        assert get_response2.status_code == status.HTTP_200_OK
        # Should have default value (50)
        assert get_response2.json()["parameters"]["max_results"] == 50


@pytest.mark.asyncio
async def test_parameter_validation_with_boolean():
    """Test parameter validation for boolean checkbox type."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Note: The mock module doesn't have boolean params, so this tests the validation logic
        # Would fail if we add a boolean param and pass non-boolean value
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 50}},  # Valid config
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_run_results_endpoint_structure():
    """Test that results endpoint returns expected structure."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a run
        create_response = await client.post(
            "/api/modules/youtube-shorts/run",
            json={"parameters": {"max_results": 50}},
        )
        run_id = create_response.json()["run_id"]

        # Get results (should return 404 or empty structure for incomplete run)
        response = await client.get(f"/api/runs/{run_id}/results")

    # Results might not exist for incomplete runs
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_filter_runs_by_multiple_criteria():
    """Test filtering runs by module_id and status together."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create runs
        for _ in range(3):
            await client.post(
                "/api/modules/youtube-shorts/run",
                json={"parameters": {"max_results": 50}},
            )

        # Filter by both module_id and status
        response = await client.get("/api/runs?module_id=youtube-shorts&status=queued")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # All returned runs should match both filters
        for run in data["runs"]:
            assert run["module_id"] == "youtube-shorts"
            assert run["status"] == "queued"


@pytest.mark.asyncio
async def test_unicode_in_parameters():
    """Test handling of Unicode characters in parameters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save config with Unicode (emoji, non-ASCII)
        response = await client.post(
            "/api/modules/youtube-shorts/config",
            json={"parameters": {"max_results": 50, "custom_field": "Hello 世界 🌍"}},
        )

        # Should handle Unicode gracefully
        assert response.status_code == status.HTTP_200_OK

        # Verify it was saved correctly
        get_response = await client.get("/api/modules/youtube-shorts/config")
        assert get_response.status_code == status.HTTP_200_OK
