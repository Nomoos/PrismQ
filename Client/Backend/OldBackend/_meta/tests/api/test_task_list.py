"""Tests for TaskList API endpoints."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import sys

# Add Backend directory to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.main import app
from API.database import APIDatabase
from API.models.task_type import TaskTypeCreate


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    db = APIDatabase(db_path=db_path)
    db.initialize_schema()
    
    yield db
    
    db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def client(test_db, monkeypatch):
    """Create test client with test database."""
    # Monkey patch the database instance for both routers
    from API.endpoints import task_types, task_list
    monkeypatch.setattr(task_types, "_db_instance", test_db)
    monkeypatch.setattr(task_list, "_db_instance", test_db)
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_task_type(client):
    """Create a sample task type for testing."""
    response = client.post(
        "/api/task-types",
        json={
            "name": "sample_task",
            "description": "Sample task for testing",
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                }
            }
        }
    )
    return response.json()


def test_create_task(client, sample_task_type):
    """Test creating a new task."""
    response = client.post(
        "/api/tasks",
        json={
            "task_type_id": sample_task_type["id"],
            "parameters": {"input": "test.txt"},
            "priority": 50,
            "metadata": {"user": "test_user"}
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["task_type_id"] == sample_task_type["id"]
    assert data["parameters"]["input"] == "test.txt"
    assert data["priority"] == 50
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data


def test_create_task_with_nonexistent_type(client):
    """Test creating a task with non-existent task type fails."""
    response = client.post(
        "/api/tasks",
        json={
            "task_type_id": 999,
            "parameters": {"input": "test.txt"}
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_create_task_with_inactive_type(client, test_db):
    """Test creating a task with inactive task type fails."""
    # Create and deactivate a task type
    task_type = test_db.create_task_type(
        TaskTypeCreate(name="inactive", description="Inactive task type")
    )
    test_db.delete_task_type(task_type.id)
    
    response = client.post(
        "/api/tasks",
        json={
            "task_type_id": task_type.id,
            "parameters": {"input": "test.txt"}
        }
    )
    
    assert response.status_code == 400
    assert "not active" in response.json()["detail"]


def test_list_tasks(client, sample_task_type):
    """Test listing all tasks."""
    # Create some tasks
    for i in range(3):
        client.post(
            "/api/tasks",
            json={
                "task_type_id": sample_task_type["id"],
                "parameters": {"input": f"test{i}.txt"}
            }
        )
    
    response = client.get("/api/tasks")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_tasks_filtered_by_type(client):
    """Test listing tasks filtered by task type."""
    # Create two task types
    type1 = client.post("/api/task-types", json={"name": "type1"}).json()
    type2 = client.post("/api/task-types", json={"name": "type2"}).json()
    
    # Create tasks for each type
    client.post("/api/tasks", json={"task_type_id": type1["id"], "parameters": {}})
    client.post("/api/tasks", json={"task_type_id": type1["id"], "parameters": {}})
    client.post("/api/tasks", json={"task_type_id": type2["id"], "parameters": {}})
    
    # Filter by type1
    response = client.get(f"/api/tasks?task_type_id={type1['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_tasks_filtered_by_status(client, sample_task_type, test_db):
    """Test listing tasks filtered by status."""
    # Create tasks with different statuses
    task1_id = client.post(
        "/api/tasks",
        json={"task_type_id": sample_task_type["id"], "parameters": {}}
    ).json()["id"]
    
    task2_id = client.post(
        "/api/tasks",
        json={"task_type_id": sample_task_type["id"], "parameters": {}}
    ).json()["id"]
    
    # Update one to completed
    from API.models.task_list import TaskListUpdate, TaskStatus
    test_db.update_task(task1_id, TaskListUpdate(status=TaskStatus.COMPLETED))
    
    # Filter by completed
    response = client.get("/api/tasks?status=completed")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "completed"


def test_list_tasks_with_limit(client, sample_task_type):
    """Test listing tasks with limit."""
    # Create 5 tasks
    for i in range(5):
        client.post(
            "/api/tasks",
            json={"task_type_id": sample_task_type["id"], "parameters": {}}
        )
    
    # Request with limit=3
    response = client.get("/api/tasks?limit=3")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_task(client, sample_task_type):
    """Test getting a specific task."""
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={
            "task_type_id": sample_task_type["id"],
            "parameters": {"input": "test.txt"},
            "priority": 75
        }
    )
    task_id = create_response.json()["id"]
    
    # Get the task
    response = client.get(f"/api/tasks/{task_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["parameters"]["input"] == "test.txt"
    assert data["priority"] == 75


def test_get_nonexistent_task(client):
    """Test getting a non-existent task returns 404."""
    response = client.get("/api/tasks/999")
    assert response.status_code == 404


def test_update_task_status(client, sample_task_type):
    """Test updating task status."""
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"task_type_id": sample_task_type["id"], "parameters": {}}
    )
    task_id = create_response.json()["id"]
    
    # Update to running
    response = client.put(
        f"/api/tasks/{task_id}",
        json={"status": "running"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["started_at"] is not None


def test_update_task_with_result(client, sample_task_type):
    """Test updating task with result."""
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"task_type_id": sample_task_type["id"], "parameters": {}}
    )
    task_id = create_response.json()["id"]
    
    # Update with result
    response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "status": "completed",
            "result": {"output": "success.txt", "duration": "5s"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["result"]["output"] == "success.txt"
    assert data["completed_at"] is not None


def test_update_task_with_error(client, sample_task_type):
    """Test updating task with error."""
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"task_type_id": sample_task_type["id"], "parameters": {}}
    )
    task_id = create_response.json()["id"]
    
    # Update with error
    response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "status": "failed",
            "error_message": "File not found"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error_message"] == "File not found"


def test_update_nonexistent_task(client):
    """Test updating a non-existent task returns 404."""
    response = client.put(
        "/api/tasks/999",
        json={"status": "completed"}
    )
    assert response.status_code == 404


def test_delete_task(client, sample_task_type):
    """Test deleting a task."""
    # Create a task
    create_response = client.post(
        "/api/tasks",
        json={"task_type_id": sample_task_type["id"], "parameters": {}}
    )
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 404


def test_delete_nonexistent_task(client):
    """Test deleting a non-existent task returns 404."""
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404


def test_task_lifecycle(client, sample_task_type):
    """Test complete task lifecycle: create, update status, complete."""
    # Create task
    create_response = client.post(
        "/api/tasks",
        json={
            "task_type_id": sample_task_type["id"],
            "parameters": {"input": "lifecycle_test.txt"},
            "priority": 10
        }
    )
    task_id = create_response.json()["id"]
    assert create_response.json()["status"] == "pending"
    
    # Start processing
    update_response = client.put(
        f"/api/tasks/{task_id}",
        json={"status": "running"}
    )
    assert update_response.json()["status"] == "running"
    assert update_response.json()["started_at"] is not None
    
    # Complete task
    complete_response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "status": "completed",
            "result": {"output": "processed.txt"}
        }
    )
    data = complete_response.json()
    assert data["status"] == "completed"
    assert data["result"]["output"] == "processed.txt"
    assert data["completed_at"] is not None
