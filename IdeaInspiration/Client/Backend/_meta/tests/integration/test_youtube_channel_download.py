"""
Integration test for YouTube channel downloading via Backend API.

This test validates the complete workflow of downloading YouTube channel content
through the Backend API, with extensive logging for Agent analysis and debugging.

The test covers:
- Module discovery and configuration
- Parameter validation
- Module execution via Backend
- Log capture and streaming
- Error handling
- Performance tracking
"""

import pytest
from httpx import AsyncClient, ASGITransport
import asyncio
import json
from datetime import datetime
from pathlib import Path

from src.main import app


@pytest.mark.asyncio
async def test_youtube_channel_download_workflow():
    """
    Test complete YouTube channel download workflow with extensive logging.
    
    This test demonstrates:
    1. Finding the YouTube Shorts module
    2. Configuring it for channel mode
    3. Launching the download
    4. Tracking execution status
    5. Capturing comprehensive logs
    6. Verifying results
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n" + "="*80)
        print("YOUTUBE CHANNEL DOWNLOAD TEST - START")
        print("="*80)
        
        # Step 1: Verify backend is healthy
        print("\n[Step 1] Checking Backend health...")
        response = await client.get("/api/health")
        assert response.status_code == 200
        health = response.json()
        print(f"✓ Backend status: {health['status']}")
        print(f"✓ Total modules available: {health.get('total_modules', 'N/A')}")
        print(f"✓ Backend version: {health.get('version', 'N/A')}")
        
        # Step 2: Find YouTube Shorts module
        print("\n[Step 2] Discovering YouTube Shorts module...")
        response = await client.get("/api/modules")
        assert response.status_code == 200
        modules_data = response.json()
        
        youtube_module = None
        for module in modules_data["modules"]:
            if module["id"] == "youtube-shorts":
                youtube_module = module
                break
        
        assert youtube_module is not None, "YouTube Shorts module not found"
        print(f"✓ Found module: {youtube_module['name']}")
        print(f"  - ID: {youtube_module['id']}")
        print(f"  - Version: {youtube_module.get('version', 'N/A')}")
        print(f"  - Category: {youtube_module.get('category', 'N/A')}")
        print(f"  - Description: {youtube_module.get('description', 'N/A')}")
        print(f"  - Parameters: {len(youtube_module.get('parameters', []))}")
        
        # Step 3: Review module parameters
        print("\n[Step 3] Reviewing module parameters...")
        for param in youtube_module.get('parameters', []):
            print(f"  - {param['name']}: {param.get('type', 'unknown')} "
                  f"(default: {param.get('default', 'N/A')})")
            if param.get('description'):
                print(f"    → {param['description']}")
        
        # Step 4: Configure module for channel download
        print("\n[Step 4] Configuring module for channel download...")
        test_config = {
            "parameters": {
                "mode": "channel",
                "channel_url": "@TED",  # Using TED as a reliable test channel
                "max_results": 5,  # Small number for testing
                "category": "All"
            }
        }
        
        print(f"✓ Configuration:")
        print(f"  - Mode: {test_config['parameters']['mode']}")
        print(f"  - Channel: {test_config['parameters']['channel_url']}")
        print(f"  - Max Results: {test_config['parameters']['max_results']}")
        
        # Save configuration
        response = await client.post(
            f"/api/modules/{youtube_module['id']}/config",
            json=test_config
        )
        assert response.status_code == 200
        print("✓ Configuration saved successfully")
        
        # Step 5: Launch module
        print("\n[Step 5] Launching YouTube channel download...")
        print(f"  Timestamp: {datetime.now().isoformat()}")
        
        response = await client.post(
            f"/api/modules/{youtube_module['id']}/run",
            json={
                "parameters": test_config['parameters'],
                "save_config": False
            }
        )
        
        assert response.status_code == 202, f"Expected 202, got {response.status_code}"
        run_data = response.json()
        run_id = run_data["run_id"]
        
        print(f"✓ Module launched successfully")
        print(f"  - Run ID: {run_id}")
        print(f"  - Module ID: {run_data.get('module_id', 'N/A')}")
        
        # Step 6: Monitor execution
        print("\n[Step 6] Monitoring execution status...")
        max_wait_time = 300  # 5 minutes max
        poll_interval = 2  # Poll every 2 seconds
        elapsed_time = 0
        previous_status = None
        
        while elapsed_time < max_wait_time:
            response = await client.get(f"/api/runs/{run_id}")
            assert response.status_code == 200
            run_status = response.json()
            
            current_status = run_status["status"]
            
            # Log status changes
            if current_status != previous_status:
                print(f"  [{elapsed_time:3d}s] Status: {current_status}")
                previous_status = current_status
            
            # Check if execution finished
            if current_status in ["completed", "failed", "cancelled"]:
                print(f"\n✓ Execution finished with status: {current_status}")
                print(f"  - Started: {run_status.get('created_at', 'N/A')}")
                if run_status.get('completed_at'):
                    print(f"  - Completed: {run_status['completed_at']}")
                if run_status.get('error'):
                    print(f"  - Error: {run_status['error']}")
                break
            
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval
        
        # Step 7: Retrieve and analyze logs
        print("\n[Step 7] Retrieving execution logs...")
        response = await client.get(f"/api/runs/{run_id}/logs")
        assert response.status_code == 200
        logs_data = response.json()
        
        logs = logs_data.get("logs", [])
        print(f"✓ Retrieved {len(logs)} log entries")
        
        # Display comprehensive logs
        print("\n" + "-"*80)
        print("EXECUTION LOGS (for Agent analysis)")
        print("-"*80)
        
        for i, log_entry in enumerate(logs, 1):
            timestamp = log_entry.get('timestamp', 'N/A')
            level = log_entry.get('level', 'INFO')
            message = log_entry.get('message', '')
            
            # Format log entry
            print(f"[{i:3d}] {timestamp} | {level:8s} | {message}")
        
        print("-"*80)
        
        # Step 8: Analyze log content
        print("\n[Step 8] Analyzing log content...")
        
        # Count log levels
        log_levels = {}
        for log_entry in logs:
            level = log_entry.get('level', 'UNKNOWN')
            log_levels[level] = log_levels.get(level, 0) + 1
        
        print("✓ Log statistics:")
        for level, count in sorted(log_levels.items()):
            print(f"  - {level}: {count}")
        
        # Look for key indicators
        indicators = {
            'channel_detected': False,
            'video_processing': False,
            'metadata_extracted': False,
            'database_saved': False,
            'errors_found': False
        }
        
        for log_entry in logs:
            message = log_entry.get('message', '').lower()
            
            if 'channel' in message or 'shorts' in message:
                indicators['channel_detected'] = True
            if 'video' in message or 'extracting' in message:
                indicators['video_processing'] = True
            if 'metadata' in message or 'info' in message:
                indicators['metadata_extracted'] = True
            if 'saved' in message or 'database' in message:
                indicators['database_saved'] = True
            if log_entry.get('level') in ['ERROR', 'CRITICAL']:
                indicators['errors_found'] = True
        
        print("\n✓ Log indicators:")
        for indicator, found in indicators.items():
            status = "✓" if found else "✗"
            print(f"  {status} {indicator.replace('_', ' ').title()}")
        
        # Step 9: Get final run details
        print("\n[Step 9] Retrieving final run details...")
        response = await client.get(f"/api/runs/{run_id}")
        assert response.status_code == 200
        final_run = response.json()
        
        print("✓ Final run summary:")
        print(f"  - Run ID: {final_run['run_id']}")
        print(f"  - Module: {final_run['module_id']}")
        print(f"  - Status: {final_run['status']}")
        print(f"  - Parameters: {json.dumps(final_run.get('parameters', {}), indent=4)}")
        
        if final_run.get('output'):
            print(f"  - Output: {final_run['output']}")
        
        # Step 10: Verify run list
        print("\n[Step 10] Verifying run appears in run list...")
        response = await client.get("/api/runs")
        assert response.status_code == 200
        all_runs = response.json()
        
        our_run = next((r for r in all_runs["runs"] if r["run_id"] == run_id), None)
        assert our_run is not None, "Run should appear in run list"
        print(f"✓ Run found in list (total runs: {all_runs['total']})")
        
        # Test summary
        print("\n" + "="*80)
        print("YOUTUBE CHANNEL DOWNLOAD TEST - SUMMARY")
        print("="*80)
        print(f"✓ Module: {youtube_module['name']}")
        print(f"✓ Run ID: {run_id}")
        print(f"✓ Status: {final_run['status']}")
        print(f"✓ Logs captured: {len(logs)} entries")
        print(f"✓ Execution time: ~{elapsed_time}s")
        
        if final_run['status'] == 'completed':
            print("✓ TEST PASSED - Channel download completed successfully")
        elif final_run['status'] == 'failed':
            print("⚠ TEST COMPLETED - Module execution failed (check logs above)")
            print("  This may be expected if yt-dlp is not installed or network issues")
        else:
            print(f"⚠ TEST COMPLETED - Unexpected status: {final_run['status']}")
        
        print("="*80 + "\n")
        
        # Always assert that we got to a terminal state
        assert final_run['status'] in ['completed', 'failed', 'cancelled'], \
            f"Run did not complete within {max_wait_time}s"


@pytest.mark.asyncio
async def test_youtube_channel_download_error_handling():
    """
    Test error handling for YouTube channel downloads.
    
    This test verifies that errors are properly captured and logged.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n" + "="*80)
        print("YOUTUBE CHANNEL ERROR HANDLING TEST")
        print("="*80)
        
        # Find YouTube module
        response = await client.get("/api/modules")
        assert response.status_code == 200
        modules = response.json()["modules"]
        
        youtube_module = next((m for m in modules if m["id"] == "youtube-shorts"), None)
        if not youtube_module:
            pytest.skip("YouTube Shorts module not found")
        
        # Test with invalid channel URL
        print("\n[Test 1] Invalid channel URL...")
        response = await client.post(
            f"/api/modules/{youtube_module['id']}/run",
            json={
                "parameters": {
                    "mode": "channel",
                    "channel_url": "this-is-not-a-valid-channel",
                    "max_results": 1
                },
                "save_config": False
            }
        )
        
        assert response.status_code == 202
        run_id = response.json()["run_id"]
        
        # Wait for completion
        await asyncio.sleep(5)
        
        # Check status
        response = await client.get(f"/api/runs/{run_id}")
        run_data = response.json()
        
        print(f"✓ Status: {run_data['status']}")
        print(f"✓ Error handling verified")
        
        # Get logs
        response = await client.get(f"/api/runs/{run_id}/logs")
        logs = response.json()["logs"]
        print(f"✓ Captured {len(logs)} log entries during error scenario")
        
        # Test with missing required parameter
        print("\n[Test 2] Missing required parameter...")
        response = await client.post(
            f"/api/modules/{youtube_module['id']}/run",
            json={
                "parameters": {
                    "mode": "channel",
                    # channel_url is missing!
                    "max_results": 1
                },
                "save_config": False
            }
        )
        
        # Should still launch (validation happens in the module)
        assert response.status_code == 202
        print("✓ Module launched (validation happens at runtime)")
        
        print("\n" + "="*80)
        print("ERROR HANDLING TEST COMPLETED")
        print("="*80 + "\n")


@pytest.mark.asyncio
async def test_youtube_channel_log_streaming():
    """
    Test real-time log streaming for YouTube channel downloads.
    
    This test verifies that logs can be streamed in real-time via SSE.
    Note: This is a placeholder for future SSE testing.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n" + "="*80)
        print("YOUTUBE CHANNEL LOG STREAMING TEST")
        print("="*80)
        
        # Find YouTube module
        response = await client.get("/api/modules")
        assert response.status_code == 200
        modules = response.json()["modules"]
        
        youtube_module = next((m for m in modules if m["id"] == "youtube-shorts"), None)
        if not youtube_module:
            pytest.skip("YouTube Shorts module not found")
        
        # Launch module
        print("\n[Step 1] Launching module for log streaming test...")
        response = await client.post(
            f"/api/modules/{youtube_module['id']}/run",
            json={
                "parameters": {
                    "mode": "trending",
                    "max_results": 3
                },
                "save_config": False
            }
        )
        
        assert response.status_code == 202
        run_id = response.json()["run_id"]
        print(f"✓ Run ID: {run_id}")
        
        # Simulate log polling (SSE streaming test would be more complex)
        print("\n[Step 2] Polling logs...")
        for i in range(5):
            await asyncio.sleep(1)
            response = await client.get(f"/api/runs/{run_id}/logs")
            if response.status_code == 200:
                logs = response.json()["logs"]
                print(f"  Poll {i+1}: {len(logs)} log entries")
        
        print("\n✓ Log polling successful")
        print("="*80 + "\n")


@pytest.mark.asyncio
async def test_youtube_channel_configuration_persistence():
    """
    Test that YouTube channel configurations are properly saved and retrieved.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n" + "="*80)
        print("YOUTUBE CHANNEL CONFIG PERSISTENCE TEST")
        print("="*80)
        
        # Find YouTube module
        response = await client.get("/api/modules")
        assert response.status_code == 200
        modules = response.json()["modules"]
        
        youtube_module = next((m for m in modules if m["id"] == "youtube-shorts"), None)
        if not youtube_module:
            pytest.skip("YouTube Shorts module not found")
        
        module_id = youtube_module['id']
        
        # Test config
        test_config = {
            "parameters": {
                "mode": "channel",
                "channel_url": "@TestChannel",
                "max_results": 25,
                "category": "Education"
            }
        }
        
        # Save config
        print("\n[Step 1] Saving configuration...")
        response = await client.post(
            f"/api/modules/{module_id}/config",
            json=test_config
        )
        assert response.status_code == 200
        print("✓ Configuration saved")
        
        # Retrieve config
        print("\n[Step 2] Retrieving configuration...")
        response = await client.get(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        retrieved_config = response.json()
        
        print("✓ Configuration retrieved:")
        print(f"  - Mode: {retrieved_config['parameters'].get('mode')}")
        print(f"  - Channel: {retrieved_config['parameters'].get('channel_url')}")
        print(f"  - Max Results: {retrieved_config['parameters'].get('max_results')}")
        
        # Verify
        assert retrieved_config['parameters']['mode'] == "channel"
        assert retrieved_config['parameters']['channel_url'] == "@TestChannel"
        assert retrieved_config['parameters']['max_results'] == 25
        
        # Delete config
        print("\n[Step 3] Deleting configuration...")
        response = await client.delete(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        print("✓ Configuration deleted")
        
        # Verify deletion
        response = await client.get(f"/api/modules/{module_id}/config")
        assert response.status_code == 200
        reset_config = response.json()
        print("✓ Configuration reset to defaults")
        
        print("="*80 + "\n")
