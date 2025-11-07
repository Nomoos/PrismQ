# API Module Documentation

## Overview

The API module provides a separated, standalone API for task type registration and task list management in the PrismQ Client Backend. This module is designed to allow microservices to register task types they can handle and manage task instances.

## Architecture

The API module is organized as follows:

```
Backend/API/
├── __init__.py              # Module initialization
├── database.py              # Database operations
├── models/                  # Pydantic models
│   ├── __init__.py
│   ├── task_type.py         # TaskType models
│   └── task_list.py         # TaskList models
└── endpoints/               # API endpoints
    ├── __init__.py
    ├── task_types.py        # TaskType CRUD endpoints
    └── task_list.py         # TaskList CRUD endpoints
```

## Key Concepts

### TaskType

A **TaskType** represents a registration of task types that microservices can perform. It's essentially a registry entry that describes:

- What type of task exists (e.g., "video_processing", "data_analysis")
- What parameters the task accepts (via JSON schema)
- Metadata about the task type

**Important**: TaskType is NOT tied to any specific worker implementation. It's just a declaration that "this type of task exists in the system."

### TaskList (Task)

A **Task** (in the task_list table) represents an actual instance of a task that needs to be executed. Each task:

- References a TaskType
- Contains specific parameters for this execution
- Tracks status (pending, running, completed, failed, cancelled)
- Stores results or error messages

## Database Schema

### task_types Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique identifier |
| name | TEXT UNIQUE | Task type name |
| description | TEXT | Description of the task type |
| parameters_schema | TEXT (JSON) | JSON schema for parameters |
| metadata | TEXT (JSON) | Additional metadata |
| is_active | INTEGER | Active flag (1=active, 0=inactive) |
| created_at | TEXT (ISO) | Creation timestamp |
| updated_at | TEXT (ISO) | Last update timestamp |

### task_list Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique identifier |
| task_type_id | INTEGER | Foreign key to task_types |
| status | TEXT | Task status (pending/running/completed/failed/cancelled) |
| parameters | TEXT (JSON) | Task parameters |
| priority | INTEGER | Priority (1-1000, lower = higher priority) |
| metadata | TEXT (JSON) | Additional metadata |
| result | TEXT (JSON) | Task result data |
| error_message | TEXT | Error message if failed |
| created_at | TEXT (ISO) | Creation timestamp |
| updated_at | TEXT (ISO) | Last update timestamp |
| started_at | TEXT (ISO) | Execution start timestamp |
| completed_at | TEXT (ISO) | Completion timestamp |

## API Endpoints

### TaskType Endpoints

#### POST /api/task-types

Create a new task type.

**Request Body:**
```json
{
  "name": "video_processing",
  "description": "Process video files with different parameters",
  "parameters_schema": {
    "type": "object",
    "properties": {
      "format": {"type": "string", "enum": ["mp4", "webm"]},
      "resolution": {"type": "string", "enum": ["720p", "1080p", "4k"]}
    },
    "required": ["format"]
  },
  "metadata": {
    "category": "media",
    "estimated_duration": "5m"
  }
}
```

**Response:** 201 Created
```json
{
  "id": 1,
  "name": "video_processing",
  "description": "Process video files with different parameters",
  "parameters_schema": { ... },
  "metadata": { ... },
  "is_active": true,
  "created_at": "2025-11-06T22:00:00Z",
  "updated_at": null
}
```

#### GET /api/task-types

List all task types.

**Query Parameters:**
- `include_inactive` (boolean, default: false) - Include inactive task types

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "name": "video_processing",
    ...
  }
]
```

#### GET /api/task-types/{task_type_id}

Get a specific task type by ID.

**Response:** 200 OK or 404 Not Found

#### PUT /api/task-types/{task_type_id}

Update a task type.

**Request Body:** (all fields optional)
```json
{
  "description": "Updated description",
  "parameters_schema": { ... },
  "metadata": { ... },
  "is_active": true
}
```

**Response:** 200 OK or 404 Not Found

#### DELETE /api/task-types/{task_type_id}

Delete (soft delete) a task type. Marks it as inactive.

**Response:** 204 No Content or 404 Not Found

### TaskList Endpoints

#### POST /api/tasks

Create a new task.

**Request Body:**
```json
{
  "task_type_id": 1,
  "parameters": {
    "format": "mp4",
    "resolution": "1080p",
    "input_file": "video.raw"
  },
  "priority": 50,
  "metadata": {
    "user_id": "user123",
    "request_id": "req-456"
  }
}
```

**Response:** 201 Created
```json
{
  "id": 1,
  "task_type_id": 1,
  "status": "pending",
  "parameters": { ... },
  "priority": 50,
  "metadata": { ... },
  "result": null,
  "error_message": null,
  "created_at": "2025-11-06T22:00:00Z",
  "updated_at": null,
  "started_at": null,
  "completed_at": null
}
```

#### GET /api/tasks

List tasks with optional filtering.

**Query Parameters:**
- `task_type_id` (integer) - Filter by task type
- `status` (string) - Filter by status (pending/running/completed/failed/cancelled)
- `limit` (integer, default: 100, max: 1000) - Maximum number of tasks

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "task_type_id": 1,
    "status": "pending",
    ...
  }
]
```

#### GET /api/tasks/{task_id}

Get a specific task by ID.

**Response:** 200 OK or 404 Not Found

#### PUT /api/tasks/{task_id}

Update a task.

**Request Body:** (all fields optional)
```json
{
  "status": "completed",
  "priority": 25,
  "parameters": { ... },
  "metadata": { ... },
  "result": {
    "output_file": "video_processed.mp4",
    "duration": "5m 23s"
  },
  "error_message": "Error details if failed"
}
```

**Response:** 200 OK or 404 Not Found

**Note:** When updating status:
- Setting to "running" automatically sets `started_at`
- Setting to "completed", "failed", or "cancelled" automatically sets `completed_at`

#### DELETE /api/tasks/{task_id}

Delete a task (permanent deletion).

**Response:** 204 No Content or 404 Not Found

## Usage Examples

### Example 1: Register a Task Type

```bash
# Register a new task type
curl -X POST http://localhost:8000/api/task-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "data_analysis",
    "description": "Analyze datasets with various algorithms",
    "parameters_schema": {
      "type": "object",
      "properties": {
        "algorithm": {"type": "string", "enum": ["kmeans", "dbscan"]},
        "dataset_path": {"type": "string"}
      },
      "required": ["algorithm", "dataset_path"]
    }
  }'
```

### Example 2: Create and Execute a Task

```bash
# 1. Create the task
TASK_ID=$(curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type_id": 1,
    "parameters": {
      "algorithm": "kmeans",
      "dataset_path": "/data/dataset.csv"
    },
    "priority": 10
  }' | jq -r '.id')

# 2. Mark as running
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "running"}'

# 3. Mark as completed with result
curl -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "result": {
      "clusters": 5,
      "output_path": "/results/clusters.json"
    }
  }'
```

### Example 3: Query Tasks

```bash
# List all pending tasks
curl http://localhost:8000/api/tasks?status=pending

# List all tasks for a specific type
curl http://localhost:8000/api/tasks?task_type_id=1

# Get recent tasks (limit to 10)
curl http://localhost:8000/api/tasks?limit=10
```

## Error Handling

All endpoints follow standard HTTP status codes:

- **200 OK** - Successful GET/PUT request
- **201 Created** - Successful POST request
- **204 No Content** - Successful DELETE request
- **400 Bad Request** - Invalid input (e.g., inactive task type)
- **404 Not Found** - Resource not found
- **409 Conflict** - Duplicate resource (e.g., task type name)
- **422 Unprocessable Entity** - Validation error
- **500 Internal Server Error** - Server error

Error responses include details:
```json
{
  "detail": "Task type 999 not found"
}
```

## Testing

Run the test suite:

```bash
# Run all API tests
pytest _meta/tests/api/ -v

# Run specific test file
pytest _meta/tests/api/test_task_types.py -v
pytest _meta/tests/api/test_task_list.py -v

# Run with coverage
pytest _meta/tests/api/ --cov=API --cov-report=html
```

## Integration with Main Application

The API module is integrated into the main FastAPI application in `src/main.py`:

```python
from API.endpoints import task_types_router, task_list_router

app.include_router(task_types_router, prefix="/api", tags=["TaskTypes"])
app.include_router(task_list_router, prefix="/api", tags=["TaskList"])
```

## Database Location

By default, the API database is stored at:
- **Windows**: `C:\Data\PrismQ\api\api.db`
- **Linux/macOS**: `/tmp/prismq/api/api.db`

This can be overridden by providing a custom path when initializing `APIDatabase`.

## Future Enhancements

Potential future improvements:

1. **Validation**: Validate task parameters against the task type's parameters_schema
2. **Webhooks**: Notify external services when tasks complete
3. **Pagination**: Add cursor-based pagination for large result sets
4. **Search**: Full-text search for task types and tasks
5. **Metrics**: Track task execution metrics and statistics
6. **Retry Logic**: Automatic retry for failed tasks
7. **Scheduling**: Support for scheduled task execution
8. **Dependencies**: Support task dependencies (task A must complete before task B)

## See Also

- [Main Backend README](../README.md)
- [API Reference](../../docs/API.md)
- [Queue System Documentation](../src/queue/README.md)
