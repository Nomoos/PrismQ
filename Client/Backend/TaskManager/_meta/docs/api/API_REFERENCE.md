# TaskManager API Reference

Complete API documentation for the TaskManager system.

## Base URL

```
https://your-domain.com/api
```

## Response Format

All endpoints return JSON with the following structure:

### Success Response
```json
{
  "success": true,
  "message": "Success message",
  "data": { ... },
  "timestamp": 1699999999
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... },  // Optional
  "timestamp": 1699999999
}
```

## HTTP Headers

All responses include:
```
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Content-Type: application/json
```

## Endpoints

---

## Task Types

### Register Task Type

Register or update a task type with its parameter schema.

**Endpoint**: `POST /task-types/register`

**Request Body**:
```json
{
  "name": "string (required)",
  "version": "string (required)",
  "param_schema": "object (required)"
}
```

**Parameters**:
- `name`: Unique task type identifier (e.g., "PrismQ.Script.Generate")
- `version`: Version string (e.g., "1.0.0")
- `param_schema`: JSON Schema object for validating task parameters

**Example Request**:
```bash
curl -X POST https://your-domain.com/api/task-types/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PrismQ.Script.Generate",
    "version": "1.0.0",
    "param_schema": {
      "type": "object",
      "properties": {
        "topic": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "style": {
          "type": "string",
          "enum": ["formal", "casual", "technical"]
        },
        "length": {
          "type": "integer",
          "minimum": 100,
          "maximum": 5000
        }
      },
      "required": ["topic", "style"]
    }
  }'
```

**Success Response** (201 Created - New):
```json
{
  "success": true,
  "message": "Task type registered successfully",
  "data": {
    "id": 1,
    "name": "PrismQ.Script.Generate",
    "version": "1.0.0",
    "created": true
  },
  "timestamp": 1699999999
}
```

**Success Response** (200 OK - Updated):
```json
{
  "success": true,
  "message": "Task type updated successfully",
  "data": {
    "id": 1,
    "name": "PrismQ.Script.Generate",
    "version": "1.0.1",
    "updated": true
  },
  "timestamp": 1699999999
}
```

**Error Responses**:
- `400 Bad Request`: Missing required fields or invalid schema
- `500 Internal Server Error`: Database error

---

### Get Task Type

Retrieve a specific task type by name.

**Endpoint**: `GET /task-types/{name}`

**Parameters**:
- `name`: Task type name (URL encoded if contains special characters)

**Example Request**:
```bash
curl https://your-domain.com/api/task-types/PrismQ.Script.Generate
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": 1,
    "name": "PrismQ.Script.Generate",
    "version": "1.0.0",
    "param_schema": {
      "type": "object",
      "properties": { ... },
      "required": [ ... ]
    },
    "is_active": true,
    "created_at": "2025-01-01 12:00:00",
    "updated_at": "2025-01-01 12:00:00"
  },
  "timestamp": 1699999999
}
```

**Error Responses**:
- `404 Not Found`: Task type doesn't exist
- `500 Internal Server Error`: Database error

---

### List Task Types

Get a list of all registered task types.

**Endpoint**: `GET /task-types`

**Query Parameters**:
- `active_only` (optional): "true" to only return active task types

**Example Request**:
```bash
curl https://your-domain.com/api/task-types?active_only=true
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "task_types": [
      {
        "id": 1,
        "name": "PrismQ.Script.Generate",
        "version": "1.0.0",
        "is_active": true,
        "created_at": "2025-01-01 12:00:00",
        "updated_at": "2025-01-01 12:00:00"
      },
      {
        "id": 2,
        "name": "PrismQ.IdeaInspiration.Research",
        "version": "1.0.0",
        "is_active": true,
        "created_at": "2025-01-02 10:00:00",
        "updated_at": "2025-01-02 10:00:00"
      }
    ],
    "count": 2
  },
  "timestamp": 1699999999
}
```

---

## Tasks

### Create Task

Create a new task with parameters.

**Endpoint**: `POST /tasks`

**Request Body**:
```json
{
  "type": "string (required)",
  "params": "object (required)"
}
```

**Parameters**:
- `type`: Task type name (must be registered)
- `params`: Task parameters (validated against type's schema)

**Example Request**:
```bash
curl -X POST https://your-domain.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "PrismQ.Script.Generate",
    "params": {
      "topic": "Artificial Intelligence in Healthcare",
      "style": "formal",
      "length": 1500
    }
  }'
```

**Success Response** (201 Created):
```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "id": 123,
    "type": "PrismQ.Script.Generate",
    "status": "pending",
    "dedupe_key": "a1b2c3d4e5f6..."
  },
  "timestamp": 1699999999
}
```

**Success Response** (200 OK - Deduplicated):
```json
{
  "success": true,
  "message": "Task already exists (deduplicated)",
  "data": {
    "id": 123,
    "status": "completed",
    "deduplicated": true
  },
  "timestamp": 1699999999
}
```

**Error Responses**:
- `400 Bad Request`: Missing fields, validation failed, or inactive type
- `404 Not Found`: Task type doesn't exist
- `500 Internal Server Error`: Database error

---

### Claim Task

Claim an available task for processing.

**Endpoint**: `POST /tasks/claim`

**Request Body**:
```json
{
  "worker_id": "string (required)",
  "task_type_id": "integer (required)",
  "type_pattern": "string (optional)",
  "sort_by": "string (optional)",
  "sort_order": "string (optional)"
}
```

**Parameters**:
- `worker_id` (required): Unique identifier for the worker claiming the task
- `task_type_id` (required): Specific task type ID to claim - must be a positive integer matching a registered task type ID. This parameter is mandatory and cannot be omitted.
- `type_pattern` (optional): SQL LIKE pattern to filter tasks by type name (e.g., "PrismQ.Script.%")
- `sort_by` (optional): Field to sort by (allowed values: `created_at`, `priority`, `id`, `attempts`; default: `created_at`)
- `sort_order` (optional): Sort direction (`ASC` or `DESC`; default: `ASC`)

**Example Request**:
```bash
curl -X POST https://your-domain.com/api/tasks/claim \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "worker-001",
    "task_type_id": 1,
    "sort_by": "priority",
    "sort_order": "DESC"
  }'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Task claimed successfully",
  "data": {
    "id": 123,
    "type": "PrismQ.Script.Generate",
    "params": {
      "topic": "Artificial Intelligence in Healthcare",
      "style": "formal",
      "length": 1500
    },
    "attempts": 1,
    "priority": 0
  },
  "timestamp": 1699999999
}
```

**Error Responses**:
- `400 Bad Request`: Missing required fields (worker_id or task_type_id), invalid task_type_id (must be positive integer), or invalid sort_by/sort_order
- `404 Not Found`: No available tasks for the specified task type
- `500 Internal Server Error`: Database error

**Notes**:
- **`task_type_id` is mandatory** - Every claim request must specify which task type to claim by providing its ID
- Tasks in `pending` status are claimable
- Tasks in `claimed` status older than `TASK_CLAIM_TIMEOUT` are also claimable (timeout recovery)
- Only one task is claimed per request
- The `type_pattern` parameter provides additional filtering on top of the required `task_type_id` if needed
- Use `sort_by` and `sort_order` to control claiming behavior:
  - FIFO (First In, First Out): `sort_by=created_at`, `sort_order=ASC` (default)
  - LIFO (Last In, First Out): `sort_by=created_at`, `sort_order=DESC`
  - Highest Priority First: `sort_by=priority`, `sort_order=DESC`

---

### Complete Task

Mark a claimed task as completed or failed.

**Endpoint**: `POST /tasks/{id}/complete`

**URL Parameters**:
- `id`: Task ID

**Request Body** (Success):
```json
{
  "worker_id": "string (required)",
  "success": true,
  "result": "object (optional)"
}
```

**Request Body** (Failure):
```json
{
  "worker_id": "string (required)",
  "success": false,
  "error": "string (optional)"
}
```

**Parameters**:
- `worker_id`: Worker ID (must match the worker that claimed the task)
- `success`: Boolean indicating task success or failure
- `result`: Task result data (for successful completions)
- `error`: Error message (for failed completions)

**Example Request** (Success):
```bash
curl -X POST https://your-domain.com/api/tasks/123/complete \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "worker-001",
    "success": true,
    "result": {
      "output": "Generated script content...",
      "word_count": 1487,
      "generated_at": "2025-01-01T12:00:00Z"
    }
  }'
```

**Example Request** (Failure):
```bash
curl -X POST https://your-domain.com/api/tasks/123/complete \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "worker-001",
    "success": false,
    "error": "API rate limit exceeded. Will retry later."
  }'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Task completed successfully",
  "data": {
    "id": 123,
    "status": "completed"
  },
  "timestamp": 1699999999
}
```

**Success Response** (200 OK - Failed with Retry):
```json
{
  "success": true,
  "message": "Task completed successfully",
  "data": {
    "id": 123,
    "status": "pending (retry)"
  },
  "timestamp": 1699999999
}
```

**Error Responses**:
- `400 Bad Request`: Missing fields or task not in claimed state
- `403 Forbidden`: Worker ID doesn't match the claimer
- `404 Not Found`: Task doesn't exist
- `500 Internal Server Error`: Database error

**Notes**:
- Failed tasks with `attempts < MAX_TASK_ATTEMPTS` are automatically reset to `pending` for retry
- Failed tasks exceeding max attempts remain in `failed` status

---

### Get Task Status

Retrieve detailed information about a specific task.

**Endpoint**: `GET /tasks/{id}`

**URL Parameters**:
- `id`: Task ID

**Example Request**:
```bash
curl https://your-domain.com/api/tasks/123
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": 123,
    "type": "PrismQ.Script.Generate",
    "status": "completed",
    "params": {
      "topic": "Artificial Intelligence in Healthcare",
      "style": "formal",
      "length": 1500
    },
    "result": {
      "output": "Generated script content...",
      "word_count": 1487
    },
    "error_message": null,
    "attempts": 1,
    "claimed_by": "worker-001",
    "claimed_at": "2025-01-01 12:00:00",
    "completed_at": "2025-01-01 12:05:00",
    "created_at": "2025-01-01 11:55:00"
  },
  "timestamp": 1699999999
}
```

**Error Responses**:
- `404 Not Found`: Task doesn't exist
- `500 Internal Server Error`: Database error

---

### List Tasks

Get a paginated list of tasks with optional filters.

**Endpoint**: `GET /tasks`

**Query Parameters**:
- `status` (optional): Filter by status ("pending", "claimed", "completed", "failed")
- `type` (optional): Filter by type (supports SQL LIKE pattern, e.g., "PrismQ.Script.%")
- `limit` (optional): Number of results per page (default: 50, max: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Example Request**:
```bash
curl 'https://your-domain.com/api/tasks?status=pending&type=PrismQ.Script.%&limit=10&offset=0'
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "tasks": [
      {
        "id": 124,
        "type": "PrismQ.Script.Generate",
        "status": "pending",
        "attempts": 0,
        "claimed_by": null,
        "created_at": "2025-01-01 13:00:00",
        "completed_at": null
      },
      {
        "id": 125,
        "type": "PrismQ.Script.Rewrite",
        "status": "pending",
        "attempts": 0,
        "claimed_by": null,
        "created_at": "2025-01-01 13:05:00",
        "completed_at": null
      }
    ],
    "count": 2,
    "limit": 10,
    "offset": 0
  },
  "timestamp": 1699999999
}
```

---

## Health Check

### Health Check Endpoint

Simple health check to verify API is running.

**Endpoint**: `GET /health`

**Example Request**:
```bash
curl https://your-domain.com/api/health
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "status": "healthy",
    "timestamp": 1699999999
  },
  "timestamp": 1699999999
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters or validation failed |
| 401 | Unauthorized - Authentication required (if implemented) |
| 403 | Forbidden - Not authorized to perform action |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Server-side error |

---

## Rate Limiting

Currently not implemented. Consider adding rate limiting for production:
- Per IP: 100 requests/minute
- Per API key: 1000 requests/minute

---

## Authentication

Currently not implemented. For production, consider adding:
- API key authentication via `X-API-Key` header
- JWT tokens for more complex scenarios
- OAuth2 for third-party integrations

---

## JSON Schema Examples

### Simple String Parameter
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100
    }
  },
  "required": ["name"]
}
```

### Enum Values
```json
{
  "type": "object",
  "properties": {
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    }
  },
  "required": ["priority"]
}
```

### Nested Objects
```json
{
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"}
      },
      "required": ["name", "email"]
    }
  },
  "required": ["user"]
}
```

### Arrays
```json
{
  "type": "object",
  "properties": {
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "maxItems": 10
    }
  },
  "required": ["tags"]
}
```

---

## Best Practices

1. **Task Types**: Register task types before creating tasks
2. **Deduplication**: Use consistent parameter ordering for reliable deduplication
3. **Error Handling**: Always check `success` field in responses
4. **Retry Logic**: Implement exponential backoff for claim attempts when no tasks available
5. **Timeouts**: Set appropriate HTTP timeouts in workers (30-60 seconds)
6. **Monitoring**: Track task counts by status regularly
7. **Cleanup**: Periodically archive or delete old completed tasks

---

## Postman Collection

Import the included Postman collection for easy API testing:
`PrismQ_TaskManager.postman_collection.json` (to be created)

---

For more information, see:
- [README.md](../README.md) - Overview and quick start
- [DATA_DRIVEN_ARCHITECTURE.md](DATA_DRIVEN_ARCHITECTURE.md) - Complete guide to data-driven API
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
