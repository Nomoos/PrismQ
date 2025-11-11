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

## Files to Create

1. `Sources/Content/Shorts/YouTube/src/api/__init__.py` - NEW
2. `Sources/Content/Shorts/YouTube/src/api/worker_api.py` - NEW
3. `Sources/Content/Shorts/YouTube/_meta/tests/test_worker_api.py` - NEW

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker03 - Full Stack Developer  
**Estimated Start**: Week 2, Day 5  
**Estimated Completion**: Week 3, Day 1
