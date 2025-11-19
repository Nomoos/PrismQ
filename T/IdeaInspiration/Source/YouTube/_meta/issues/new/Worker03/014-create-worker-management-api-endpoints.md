# Issue #014: Create Worker Management API Endpoints

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 03 - Full Stack Developer  
**Language**: Python 3.10+ (FastAPI/Flask)  
**Status**: New  
**Priority**: High  
**Duration**: 2 days  
**Dependencies**: #002 (Worker Base), #004 (Database Schema), #013 (Parameter Registration)

---

## Objective

Create REST API endpoints for managing workers, tasks, and monitoring the YouTube scraping system. Provides programmatic interface for task submission, status checking, and worker management.

---

## SOLID Principles Analysis

**SRP** ✅ - API layer only handles HTTP requests/responses  
**OCP** ✅ - New endpoints can be added without modifying existing  
**LSP** ✅ - All endpoints follow REST conventions  
**ISP** ✅ - Endpoints grouped by resource type  
**DIP** ✅ - Depends on service layer abstractions

---

## Proposed Solution

### API Endpoints

**File**: `Sources/Content/Shorts/YouTube/src/api/worker_api.py` (NEW)

```python
"""Worker management REST API.

Provides endpoints for task and worker management.
"""

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..workers.queue_database import QueueDatabase
from ..core.parameter_schema import ParameterRegistry


app = FastAPI(
    title="YouTube Worker API",
    version="1.0.0",
    description="API for managing YouTube scraping workers and tasks"
)


# Pydantic models
class TaskCreate(BaseModel):
    """Model for creating a new task."""
    task_type: str
    parameters: dict
    priority: int = 5


class TaskResponse(BaseModel):
    """Model for task response."""
    id: int
    task_type: str
    status: str
    created_at: str
    claimed_by: Optional[str] = None


class WorkerStatusResponse(BaseModel):
    """Model for worker status."""
    worker_id: str
    last_heartbeat: str
    tasks_processed: int
    tasks_failed: int
    current_task_id: Optional[int] = None


# Database connection (configured on startup)
queue_db: Optional[QueueDatabase] = None


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    global queue_db
    queue_db = QueueDatabase("data/worker_queue.db")


# ===== Task Endpoints =====

@app.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate):
    """Create a new task.
    
    Args:
        task: Task creation request
        
    Returns:
        Created task
    """
    # Validate parameters
    registry = ParameterRegistry.get_instance()
    is_valid, prepared_params, errors = registry.validate_and_prepare(
        task.task_type,
        task.parameters
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Insert task into queue
    conn = queue_db.get_connection()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO task_queue
        (task_type, parameters, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, 'queued', ?, ?)
    """, (task.task_type, str(prepared_params), task.priority, now, now))
    
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return TaskResponse(
        id=task_id,
        task_type=task.task_type,
        status="queued",
        created_at=now
    )


@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
):
    """List tasks with optional filtering.
    
    Args:
        status: Filter by status
        limit: Maximum number of tasks to return
        
    Returns:
        List of tasks
    """
    conn = queue_db.get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, task_type, status, created_at, claimed_by FROM task_queue"
    params = []
    
    if status:
        query += " WHERE status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [
        TaskResponse(
            id=row['id'],
            task_type=row['task_type'],
            status=row['status'],
            created_at=row['created_at'],
            claimed_by=row['claimed_by']
        )
        for row in rows
    ]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """Get task by ID.
    
    Args:
        task_id: Task ID
        
    Returns:
        Task details
    """
    conn = queue_db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, task_type, status, created_at, claimed_by
        FROM task_queue
        WHERE id = ?
    """, (task_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        id=row['id'],
        task_type=row['task_type'],
        status=row['status'],
        created_at=row['created_at'],
        claimed_by=row['claimed_by']
    )


@app.delete("/tasks/{task_id}", status_code=204)
async def cancel_task(task_id: int):
    """Cancel a task.
    
    Args:
        task_id: Task ID to cancel
    """
    conn = queue_db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE task_queue
        SET status = 'cancelled', updated_at = ?
        WHERE id = ? AND status IN ('queued', 'claimed')
    """, (datetime.utcnow().isoformat(), task_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Task not found or cannot be cancelled"
        )
    
    conn.commit()
    conn.close()


# ===== Worker Endpoints =====

@app.get("/workers", response_model=List[WorkerStatusResponse])
async def list_workers():
    """List all workers and their status.
    
    Returns:
        List of worker statuses
    """
    conn = queue_db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT worker_id, last_heartbeat, tasks_processed,
               tasks_failed, current_task_id
        FROM worker_heartbeats
        ORDER BY last_heartbeat DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        WorkerStatusResponse(
            worker_id=row['worker_id'],
            last_heartbeat=row['last_heartbeat'],
            tasks_processed=row['tasks_processed'],
            tasks_failed=row['tasks_failed'],
            current_task_id=row['current_task_id']
        )
        for row in rows
    ]


# ===== Schema Endpoints =====

@app.get("/schemas")
async def list_schemas():
    """List all parameter schemas.
    
    Returns:
        List of available task types and their schemas
    """
    registry = ParameterRegistry.get_instance()
    schemas = registry.list_schemas()
    
    return {
        'schemas': [schema.to_dict() for schema in schemas]
    }


@app.get("/schemas/{task_type}")
async def get_schema(task_type: str):
    """Get parameter schema for task type.
    
    Args:
        task_type: Task type identifier
        
    Returns:
        Parameter schema
    """
    registry = ParameterRegistry.get_instance()
    schema = registry.get_schema(task_type)
    
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    
    return schema.to_dict()


# ===== Statistics Endpoints =====

@app.get("/statistics")
async def get_statistics():
    """Get system statistics.
    
    Returns:
        Statistics about tasks and workers
    """
    stats = queue_db.get_stats()
    return stats
```

---

## Implementation Plan

### Day 1: Core Endpoints
- Setup FastAPI application
- Implement task endpoints (CRUD)
- Implement worker list endpoint

### Day 2: Testing & Documentation
- Add statistics endpoints
- Write API tests
- Generate OpenAPI documentation
- Add authentication (if needed)

---

## Acceptance Criteria

- [ ] All endpoints implemented and working
- [ ] Request/response validation with Pydantic
- [ ] Error handling comprehensive
- [ ] OpenAPI documentation generated
- [ ] Integration tests passing
- [ ] Test coverage >80%

---

## API Endpoints Summary

**Tasks**:
- `POST /tasks` - Create task
- `GET /tasks` - List tasks
- `GET /tasks/{id}` - Get task
- `DELETE /tasks/{id}` - Cancel task

**Workers**:
- `GET /workers` - List workers

**Schemas**:
- `GET /schemas` - List all schemas
- `GET /schemas/{type}` - Get schema

**Statistics**:
- `GET /statistics` - Get system stats

---

## API Usage Examples

### cURL Examples

#### Create a Task

```bash
# Create a channel scraping task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "channel_scrape",
    "parameters": {
      "channel_url": "https://youtube.com/@TechChannel",
      "top_n": 50,
      "max_age_days": 30
    },
    "priority": 5
  }'

# Response:
# {
#   "id": 123,
#   "task_type": "channel_scrape",
#   "status": "queued",
#   "created_at": "2024-11-13T08:00:00Z"
# }

# Create a trending scrape task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "trending_scrape",
    "parameters": {
      "country": "US",
      "category": "gaming",
      "top_n": 100
    },
    "priority": 7
  }'

# Create a keyword search task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "keyword_search",
    "parameters": {
      "query": "python tutorials",
      "top_n": 75,
      "date_filter": "month",
      "sort_by": "views"
    },
    "priority": 6
  }'
```

#### List Tasks

```bash
# List all tasks
curl http://localhost:8000/tasks

# List only queued tasks
curl http://localhost:8000/tasks?status=queued

# List completed tasks with limit
curl http://localhost:8000/tasks?status=completed&limit=50

# List failed tasks
curl http://localhost:8000/tasks?status=failed&limit=25
```

#### Get Task Details

```bash
# Get specific task
curl http://localhost:8000/tasks/123

# Response:
# {
#   "id": 123,
#   "task_type": "channel_scrape",
#   "status": "completed",
#   "created_at": "2024-11-13T08:00:00Z",
#   "claimed_by": "worker-001"
# }
```

#### Cancel a Task

```bash
# Cancel a queued or claimed task
curl -X DELETE http://localhost:8000/tasks/123

# Response: HTTP 204 No Content (success)
```

#### List Workers

```bash
# List all workers
curl http://localhost:8000/workers

# Response:
# [
#   {
#     "worker_id": "worker-001",
#     "last_heartbeat": "2024-11-13T08:05:00Z",
#     "tasks_processed": 25,
#     "tasks_failed": 2,
#     "current_task_id": 124
#   },
#   {
#     "worker_id": "worker-002",
#     "last_heartbeat": "2024-11-13T08:04:50Z",
#     "tasks_processed": 18,
#     "tasks_failed": 0,
#     "current_task_id": null
#   }
# ]
```

#### Get Parameter Schemas

```bash
# List all available task types
curl http://localhost:8000/schemas

# Get schema for specific task type
curl http://localhost:8000/schemas/channel_scrape

# Response:
# {
#   "task_type": "channel_scrape",
#   "description": "Scrape videos from YouTube channel",
#   "parameters": [
#     {
#       "name": "channel_url",
#       "type": "string",
#       "required": true,
#       "description": "YouTube channel URL",
#       "constraints": {...}
#     },
#     ...
#   ],
#   "examples": [...]
# }
```

#### Get Statistics

```bash
# Get system statistics
curl http://localhost:8000/statistics

# Response:
# {
#   "status_counts": {
#     "queued": 45,
#     "claimed": 5,
#     "completed": 1234,
#     "failed": 23
#   },
#   "active_workers": 3,
#   "db_size_mb": 125.5
# }
```

### Python Client Examples

#### Basic Usage

```python
import requests
import json

API_BASE = "http://localhost:8000"

# Create a task
def create_task(task_type: str, params: dict, priority: int = 5):
    response = requests.post(
        f"{API_BASE}/tasks",
        json={
            "task_type": task_type,
            "parameters": params,
            "priority": priority
        }
    )
    response.raise_for_status()
    return response.json()

# Example: Create channel scrape
task = create_task(
    "channel_scrape",
    {
        "channel_url": "https://youtube.com/@TechReviews",
        "top_n": 100,
        "max_age_days": 30
    },
    priority=7
)
print(f"Created task {task['id']}")

# List tasks
def list_tasks(status: str = None, limit: int = 100):
    params = {"limit": limit}
    if status:
        params["status"] = status
    
    response = requests.get(f"{API_BASE}/tasks", params=params)
    response.raise_for_status()
    return response.json()

# Get queued tasks
queued = list_tasks(status="queued")
print(f"Found {len(queued)} queued tasks")

# Get task details
def get_task(task_id: int):
    response = requests.get(f"{API_BASE}/tasks/{task_id}")
    response.raise_for_status()
    return response.json()

task_details = get_task(123)
print(f"Task status: {task_details['status']}")

# Cancel task
def cancel_task(task_id: int):
    response = requests.delete(f"{API_BASE}/tasks/{task_id}")
    response.raise_for_status()

cancel_task(125)
print("Task cancelled")
```

#### Advanced Client with Error Handling

```python
import requests
from typing import Optional, Dict, List
from dataclasses import dataclass

@dataclass
class APIResponse:
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None

class YouTubeWorkerClient:
    """Python client for YouTube Worker API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def create_task(
        self,
        task_type: str,
        parameters: Dict,
        priority: int = 5
    ) -> APIResponse:
        """Create a new scraping task."""
        try:
            response = requests.post(
                f"{self.base_url}/tasks",
                json={
                    "task_type": task_type,
                    "parameters": parameters,
                    "priority": priority
                },
                timeout=10
            )
            
            if response.status_code == 201:
                return APIResponse(success=True, data=response.json())
            elif response.status_code == 400:
                errors = response.json().get('detail', {}).get('errors', [])
                return APIResponse(
                    success=False,
                    error=f"Validation errors: {', '.join(errors)}"
                )
            else:
                return APIResponse(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        except requests.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 100
    ) -> APIResponse:
        """List tasks with optional filtering."""
        try:
            params = {"limit": limit}
            if status:
                params["status"] = status
            
            response = requests.get(
                f"{self.base_url}/tasks",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            return APIResponse(success=True, data=response.json())
        except requests.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def get_task(self, task_id: int) -> APIResponse:
        """Get details for a specific task."""
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                timeout=10
            )
            
            if response.status_code == 404:
                return APIResponse(
                    success=False,
                    error=f"Task {task_id} not found"
                )
            
            response.raise_for_status()
            return APIResponse(success=True, data=response.json())
        except requests.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def cancel_task(self, task_id: int) -> APIResponse:
        """Cancel a task."""
        try:
            response = requests.delete(
                f"{self.base_url}/tasks/{task_id}",
                timeout=10
            )
            
            if response.status_code == 204:
                return APIResponse(success=True)
            elif response.status_code == 404:
                return APIResponse(
                    success=False,
                    error="Task not found or cannot be cancelled"
                )
            
            response.raise_for_status()
            return APIResponse(success=True)
        except requests.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def list_workers(self) -> APIResponse:
        """List all workers."""
        try:
            response = requests.get(
                f"{self.base_url}/workers",
                timeout=10
            )
            response.raise_for_status()
            return APIResponse(success=True, data=response.json())
        except requests.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def get_statistics(self) -> APIResponse:
        """Get system statistics."""
        try:
            response = requests.get(
                f"{self.base_url}/statistics",
                timeout=10
            )
            response.raise_for_status()
            return APIResponse(success=True, data=response.json())
        except requests.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def get_schema(self, task_type: str) -> APIResponse:
        """Get parameter schema for task type."""
        try:
            response = requests.get(
                f"{self.base_url}/schemas/{task_type}",
                timeout=10
            )
            
            if response.status_code == 404:
                return APIResponse(
                    success=False,
                    error=f"Schema for '{task_type}' not found"
                )
            
            response.raise_for_status()
            return APIResponse(success=True, data=response.json())
        except requests.RequestException as e:
            return APIResponse(success=False, error=str(e))

# Usage example
client = YouTubeWorkerClient()

# Create task with error handling
result = client.create_task(
    "channel_scrape",
    {
        "channel_url": "https://youtube.com/@TechChannel",
        "top_n": 50
    }
)

if result.success:
    print(f"Task created: {result.data['id']}")
else:
    print(f"Error: {result.error}")

# Monitor task progress
import time

def wait_for_task(client: YouTubeWorkerClient, task_id: int, timeout: int = 300):
    """Wait for task to complete."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        result = client.get_task(task_id)
        
        if not result.success:
            return None
        
        status = result.data['status']
        
        if status == 'completed':
            return result.data
        elif status == 'failed':
            raise Exception(f"Task {task_id} failed")
        
        time.sleep(5)
    
    raise TimeoutError(f"Task {task_id} did not complete in {timeout}s")

# Use it
task_result = result.data
completed_task = wait_for_task(client, task_result['id'])
print(f"Task completed: {completed_task}")
```

#### Batch Operations

```python
def create_multiple_tasks(client: YouTubeWorkerClient, tasks: List[Dict]) -> Dict:
    """Create multiple tasks and track results."""
    results = {
        'created': [],
        'failed': []
    }
    
    for task in tasks:
        result = client.create_task(
            task['type'],
            task['params'],
            task.get('priority', 5)
        )
        
        if result.success:
            results['created'].append(result.data)
        else:
            results['failed'].append({
                'task': task,
                'error': result.error
            })
    
    return results

# Example: Create batch of tasks
tasks_to_create = [
    {
        'type': 'channel_scrape',
        'params': {'channel_url': 'https://youtube.com/@Channel1', 'top_n': 50}
    },
    {
        'type': 'trending_scrape',
        'params': {'country': 'US', 'category': 'gaming', 'top_n': 100}
    },
    {
        'type': 'keyword_search',
        'params': {'query': 'tech reviews', 'top_n': 75}
    }
]

batch_results = create_multiple_tasks(client, tasks_to_create)
print(f"Created: {len(batch_results['created'])}")
print(f"Failed: {len(batch_results['failed'])}")
```

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/src/api/__init__.py` - NEW
2. `Sources/Content/Shorts/YouTube/src/api/worker_api.py` - NEW
3. `Sources/Content/Shorts/YouTube/_meta/tests/test_worker_api.py` - NEW

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker03 - Full Stack Developer  
**Estimated Start**: Week 2, Day 5  
**Estimated Completion**: Week 3, Day 1
