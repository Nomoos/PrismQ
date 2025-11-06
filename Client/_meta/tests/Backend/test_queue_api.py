"""Tests for queue API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from datetime import datetime, timezone, timedelta
import tempfile
import os

from src.main import app
from src.queue import QueueDatabase
from src.api import queue as queue_module


@pytest.fixture(autouse=True)
def reset_queue_singleton():
    """Reset the queue database singleton between tests."""
    # Reset singleton before test
    queue_module._db_instance = None
    yield
    # Reset singleton after test
    if queue_module._db_instance is not None:
        queue_module._db_instance.close()
        queue_module._db_instance = None


@pytest.fixture
def temp_queue_db(reset_queue_singleton):
    """Create a temporary queue database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_queue.db")
        # Set environment variable for test database
        os.environ["PRISMQ_QUEUE_DB_PATH"] = db_path
        
        # Initialize schema
        db = QueueDatabase(db_path)
        db.initialize_schema()
        db.close()
        
        yield db_path
        
        # Cleanup
        if "PRISMQ_QUEUE_DB_PATH" in os.environ:
            del os.environ["PRISMQ_QUEUE_DB_PATH"]


@pytest.mark.asyncio
async def test_enqueue_task(temp_queue_db):
    """Test enqueueing a new task."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/queue/enqueue",
            json={
                "type": "video_processing",
                "priority": 50,
                "payload": {"format": "mp4", "resolution": "1080p"},
                "compatibility": {"region": "us-west"},
                "max_attempts": 3,
            },
        )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "queued"
    assert "created_at_utc" in data
    assert data["message"] == "Task enqueued successfully"


@pytest.mark.asyncio
async def test_enqueue_task_with_idempotency_key(temp_queue_db):
    """Test idempotency key prevents duplicate task creation."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First request
        response1 = await client.post(
            "/api/queue/enqueue",
            json={
                "type": "email_notification",
                "idempotency_key": "email-123-send",
                "payload": {"recipient": "user@example.com"},
            },
        )

        assert response1.status_code == status.HTTP_201_CREATED
        data1 = response1.json()
        task_id_1 = data1["task_id"]

        # Second request with same idempotency key
        response2 = await client.post(
            "/api/queue/enqueue",
            json={
                "type": "email_notification",
                "idempotency_key": "email-123-send",
                "payload": {"recipient": "user@example.com"},
            },
        )

        assert response2.status_code == status.HTTP_201_CREATED
        data2 = response2.json()
        task_id_2 = data2["task_id"]

        # Should return the same task
        assert task_id_1 == task_id_2
        assert "already exists" in data2["message"].lower()


@pytest.mark.asyncio
async def test_enqueue_task_validation_error(temp_queue_db):
    """Test validation errors for invalid task data."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Empty task type
        response = await client.post(
            "/api/queue/enqueue",
            json={
                "type": "",
                "payload": {},
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_task_status(temp_queue_db):
    """Test getting task status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # First enqueue a task
        enqueue_response = await client.post(
            "/api/queue/enqueue",
            json={
                "type": "data_sync",
                "priority": 100,
                "payload": {"source": "db1", "dest": "db2"},
            },
        )

        task_id = enqueue_response.json()["task_id"]

        # Get task status
        response = await client.get(f"/api/queue/tasks/{task_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == task_id
        assert data["type"] == "data_sync"
        assert data["status"] == "queued"
        assert data["priority"] == 100
        assert data["payload"] == {"source": "db1", "dest": "db2"}
        assert data["attempts"] == 0


@pytest.mark.asyncio
async def test_get_task_status_not_found(temp_queue_db):
    """Test getting status of non-existent task."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/queue/tasks/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_task(temp_queue_db):
    """Test cancelling a queued task."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Enqueue a task
        enqueue_response = await client.post(
            "/api/queue/enqueue",
            json={
                "type": "backup",
                "payload": {"target": "/data"},
            },
        )

        task_id = enqueue_response.json()["task_id"]

        # Cancel the task
        response = await client.post(f"/api/queue/tasks/{task_id}/cancel")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] == "failed"
        assert "cancelled" in data["message"].lower()

        # Verify task status is updated
        status_response = await client.get(f"/api/queue/tasks/{task_id}")
        status_data = status_response.json()
        assert status_data["status"] == "failed"
        assert "cancelled" in status_data["error_message"].lower()


@pytest.mark.asyncio
async def test_cancel_completed_task(temp_queue_db):
    """Test that completed tasks cannot be cancelled."""
    db = QueueDatabase(temp_queue_db)
    
    # Insert a completed task directly
    with db.transaction() as conn:
        cursor = conn.execute(
            """
            INSERT INTO task_queue (type, status, payload, finished_at_utc)
            VALUES (?, ?, ?, ?)
            """,
            ("completed_job", "completed", "{}", datetime.now(timezone.utc).isoformat()),
        )
        task_id = cursor.lastrowid
    db.close()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try to cancel completed task
        response = await client.post(f"/api/queue/tasks/{task_id}/cancel")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert "cannot cancel" in data["message"].lower()


@pytest.mark.asyncio
async def test_cancel_task_not_found(temp_queue_db):
    """Test cancelling non-existent task."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/queue/tasks/99999/cancel")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_queue_stats(temp_queue_db):
    """Test getting queue statistics."""
    db = QueueDatabase(temp_queue_db)
    
    # Insert tasks in different states
    with db.transaction() as conn:
        conn.execute(
            "INSERT INTO task_queue (type, status, payload) VALUES (?, ?, ?)",
            ("job1", "queued", "{}"),
        )
        conn.execute(
            "INSERT INTO task_queue (type, status, payload) VALUES (?, ?, ?)",
            ("job2", "queued", "{}"),
        )
        conn.execute(
            "INSERT INTO task_queue (type, status, payload) VALUES (?, ?, ?)",
            ("job3", "processing", "{}"),
        )
        conn.execute(
            "INSERT INTO task_queue (type, status, payload) VALUES (?, ?, ?)",
            ("job4", "completed", "{}"),
        )
        conn.execute(
            "INSERT INTO task_queue (type, status, payload) VALUES (?, ?, ?)",
            ("job5", "failed", "{}"),
        )
    db.close()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/queue/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_tasks"] == 5
        assert data["queued_tasks"] == 2
        assert data["processing_tasks"] == 1
        assert data["completed_tasks"] == 1
        assert data["failed_tasks"] == 1
        assert "oldest_queued_age_seconds" in data


@pytest.mark.asyncio
async def test_list_tasks(temp_queue_db):
    """Test listing tasks."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Enqueue multiple tasks
        for i in range(5):
            await client.post(
                "/api/queue/enqueue",
                json={
                    "type": "batch_job",
                    "priority": 100 + i,
                    "payload": {"index": i},
                },
            )

        # List all tasks
        response = await client.get("/api/queue/tasks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5


@pytest.mark.asyncio
async def test_list_tasks_with_filters(temp_queue_db):
    """Test listing tasks with status and type filters."""
    db = QueueDatabase(temp_queue_db)
    
    # Insert tasks with different types and statuses
    with db.transaction() as conn:
        conn.execute(
            "INSERT INTO task_queue (type, status, payload) VALUES (?, ?, ?)",
            ("type_a", "queued", "{}"),
        )
        conn.execute(
            "INSERT INTO task_queue (type, status, payload) VALUES (?, ?, ?)",
            ("type_a", "completed", "{}"),
        )
        conn.execute(
            "INSERT INTO task_queue (type, status, payload) VALUES (?, ?, ?)",
            ("type_b", "queued", "{}"),
        )
    db.close()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Filter by status
        response = await client.get("/api/queue/tasks?status=queued")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(task["status"] == "queued" for task in data)

        # Filter by type
        response = await client.get("/api/queue/tasks?type=type_a")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert all(task["type"] == "type_a" for task in data)

        # Filter by both
        response = await client.get("/api/queue/tasks?status=queued&type=type_a")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "type_a"
        assert data[0]["status"] == "queued"


@pytest.mark.asyncio
async def test_list_tasks_with_limit(temp_queue_db):
    """Test listing tasks with limit parameter."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Enqueue multiple tasks
        for i in range(10):
            await client.post(
                "/api/queue/enqueue",
                json={
                    "type": "test_job",
                    "payload": {"index": i},
                },
            )

        # List with limit
        response = await client.get("/api/queue/tasks?limit=5")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5


@pytest.mark.asyncio
async def test_enqueue_task_with_schedule(temp_queue_db):
    """Test enqueueing a task with future run time."""
    future_time = datetime.now(timezone.utc) + timedelta(hours=1)
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/queue/enqueue",
            json={
                "type": "scheduled_job",
                "payload": {"action": "cleanup"},
                "run_after_utc": future_time.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        task_id = response.json()["task_id"]

        # Verify task was created with correct run_after time
        # Note: The task won't be claimed until run_after_utc is reached
        status_response = await client.get(f"/api/queue/tasks/{task_id}")
        assert status_response.status_code == status.HTTP_200_OK
