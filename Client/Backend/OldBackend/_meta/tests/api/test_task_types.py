"""Tests for TaskType API endpoints."""

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
    # Monkey patch the database instance
    from API.endpoints import task_types
    monkeypatch.setattr(task_types, "_db_instance", test_db)
    
    with TestClient(app) as client:
        yield client


def test_create_task_type(client):
    """Test creating a new task type."""
    response = client.post(
        "/api/task-types",
        json={
            "name": "video_processing",
            "description": "Process video files",
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "format": {"type": "string"},
                    "resolution": {"type": "string"}
                }
            },
            "metadata": {"category": "media"}
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "video_processing"
    assert data["description"] == "Process video files"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_task_type(client):
    """Test creating a task type with duplicate name fails."""
    # Create first task type
    client.post(
        "/api/task-types",
        json={"name": "duplicate_test", "description": "Test"}
    )
    
    # Try to create duplicate
    response = client.post(
        "/api/task-types",
        json={"name": "duplicate_test", "description": "Another test"}
    )
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_list_task_types(client):
    """Test listing all task types."""
    # Create some task types
    client.post("/api/task-types", json={"name": "type1", "description": "Type 1"})
    client.post("/api/task-types", json={"name": "type2", "description": "Type 2"})
    
    response = client.get("/api/task-types")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "type1"
    assert data[1]["name"] == "type2"


def test_list_task_types_with_inactive(client, test_db):
    """Test listing task types including inactive ones."""
    from API.models.task_type import TaskTypeCreate
    
    # Create and deactivate a task type
    result = test_db.create_task_type(
        TaskTypeCreate(
            name="inactive_type",
            description="Inactive",
            parameters_schema={},
            metadata={}
        )
    )
    test_db.delete_task_type(result.id)
    
    # Create an active task type
    client.post("/api/task-types", json={"name": "active_type", "description": "Active"})
    
    # List without inactive
    response = client.get("/api/task-types")
    assert response.status_code == 200
    assert len(response.json()) == 1
    
    # List with inactive
    response = client.get("/api/task-types?include_inactive=true")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_task_type(client):
    """Test getting a specific task type."""
    # Create a task type
    create_response = client.post(
        "/api/task-types",
        json={"name": "get_test", "description": "Get test"}
    )
    task_type_id = create_response.json()["id"]
    
    # Get the task type
    response = client.get(f"/api/task-types/{task_type_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_type_id
    assert data["name"] == "get_test"


def test_get_nonexistent_task_type(client):
    """Test getting a non-existent task type returns 404."""
    response = client.get("/api/task-types/999")
    assert response.status_code == 404


def test_update_task_type(client):
    """Test updating a task type."""
    # Create a task type
    create_response = client.post(
        "/api/task-types",
        json={"name": "update_test", "description": "Original description"}
    )
    task_type_id = create_response.json()["id"]
    
    # Update the task type
    response = client.put(
        f"/api/task-types/{task_type_id}",
        json={
            "description": "Updated description",
            "metadata": {"updated": True}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["metadata"]["updated"] is True
    assert data["name"] == "update_test"  # Name should not change


def test_update_nonexistent_task_type(client):
    """Test updating a non-existent task type returns 404."""
    response = client.put(
        "/api/task-types/999",
        json={"description": "New description"}
    )
    assert response.status_code == 404


def test_delete_task_type(client):
    """Test deleting (deactivating) a task type."""
    # Create a task type
    create_response = client.post(
        "/api/task-types",
        json={"name": "delete_test", "description": "To be deleted"}
    )
    task_type_id = create_response.json()["id"]
    
    # Delete the task type
    response = client.delete(f"/api/task-types/{task_type_id}")
    assert response.status_code == 204
    
    # Verify it's marked as inactive
    response = client.get(f"/api/task-types/{task_type_id}")
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_delete_nonexistent_task_type(client):
    """Test deleting a non-existent task type returns 404."""
    response = client.delete("/api/task-types/999")
    assert response.status_code == 404


def test_task_type_with_complex_schema(client):
    """Test creating a task type with complex parameters schema."""
    response = client.post(
        "/api/task-types",
        json={
            "name": "complex_task",
            "description": "Task with complex schema",
            "parameters_schema": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "format": {"type": "string", "enum": ["json", "xml"]}
                        },
                        "required": ["file"]
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["input"]
            }
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "input" in data["parameters_schema"]["properties"]
    assert "options" in data["parameters_schema"]["properties"]
