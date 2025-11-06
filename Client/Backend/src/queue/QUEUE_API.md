# Queue API Documentation

## Overview

The Queue API provides RESTful endpoints for managing tasks in the SQLite-based task queue system. This API supports task enqueueing, status polling, cancellation, and queue statistics.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API does not require authentication. This should be added in production environments.

## Endpoints

### 1. Enqueue Task

Create a new task in the queue.

**Endpoint:** `POST /queue/enqueue`

**Request Body:**

```json
{
  "type": "video_processing",
  "priority": 50,
  "payload": {
    "format": "mp4",
    "resolution": "1080p"
  },
  "compatibility": {
    "region": "us-west"
  },
  "max_attempts": 3,
  "run_after_utc": "2025-11-06T10:00:00Z",
  "idempotency_key": "video-123-process"
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| type | string | Yes | - | Task type identifier |
| priority | integer | No | 100 | Task priority (1-1000, lower = higher priority) |
| payload | object | No | {} | Task-specific data |
| compatibility | object | No | {} | Worker compatibility requirements |
| max_attempts | integer | No | 5 | Maximum retry attempts (1-10) |
| run_after_utc | datetime | No | now | Schedule task to run after this time |
| idempotency_key | string | No | null | Unique key to prevent duplicate task creation |

**Response (201 Created):**

```json
{
  "task_id": 1,
  "status": "queued",
  "created_at_utc": "2025-11-05T19:35:00Z",
  "message": "Task enqueued successfully"
}
```

**Idempotency:**

If an `idempotency_key` is provided and a task with that key already exists, the API returns the existing task instead of creating a duplicate:

```json
{
  "task_id": 1,
  "status": "queued",
  "created_at_utc": "2025-11-05T19:35:00Z",
  "message": "Task already exists (idempotency key match)"
}
```

**Error Responses:**

- `422 Unprocessable Entity`: Invalid request data
- `503 Service Unavailable`: Queue database is busy
- `500 Internal Server Error`: Database error

---

### 2. Get Task Status

Retrieve the current status and details of a specific task.

**Endpoint:** `GET /queue/tasks/{task_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | integer | Unique task identifier |

**Response (200 OK):**

```json
{
  "task_id": 1,
  "type": "video_processing",
  "status": "processing",
  "priority": 50,
  "attempts": 1,
  "max_attempts": 3,
  "payload": {
    "format": "mp4",
    "resolution": "1080p"
  },
  "compatibility": {
    "region": "us-west"
  },
  "error_message": null,
  "created_at_utc": "2025-11-05T19:35:00Z",
  "processing_started_utc": "2025-11-05T19:36:00Z",
  "finished_at_utc": null,
  "locked_by": "worker-001"
}
```

**Task Statuses:**

- `queued`: Task is waiting to be processed
- `processing`: Task is currently being processed by a worker
- `completed`: Task completed successfully
- `failed`: Task failed or was cancelled

**Error Responses:**

- `404 Not Found`: Task does not exist
- `500 Internal Server Error`: Database error

---

### 3. Cancel Task

Cancel a queued or processing task.

**Endpoint:** `POST /queue/tasks/{task_id}/cancel`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | integer | Unique task identifier |

**Response (200 OK):**

```json
{
  "task_id": 1,
  "status": "failed",
  "message": "Task cancelled successfully"
}
```

**Notes:**

- Only tasks with status `queued` or `processing` can be cancelled
- Cancelled tasks are marked as `failed` with error message "Cancelled by user"
- Already completed or failed tasks cannot be cancelled

**Response for already completed task:**

```json
{
  "task_id": 1,
  "status": "completed",
  "message": "Task already completed, cannot cancel"
}
```

**Error Responses:**

- `404 Not Found`: Task does not exist
- `500 Internal Server Error`: Database error

---

### 4. List Tasks

Retrieve a list of tasks with optional filtering.

**Endpoint:** `GET /queue/tasks`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| status | string | No | - | Filter by status (queued, processing, completed, failed) |
| type | string | No | - | Filter by task type |
| limit | integer | No | 100 | Maximum number of tasks to return (1-1000) |

**Examples:**

```
GET /queue/tasks
GET /queue/tasks?status=queued
GET /queue/tasks?type=video_processing
GET /queue/tasks?status=queued&type=video_processing&limit=50
```

**Response (200 OK):**

```json
[
  {
    "task_id": 1,
    "type": "video_processing",
    "status": "queued",
    "priority": 50,
    "attempts": 0,
    "max_attempts": 3,
    "payload": {...},
    "compatibility": {...},
    "error_message": null,
    "created_at_utc": "2025-11-05T19:35:00Z",
    "processing_started_utc": null,
    "finished_at_utc": null,
    "locked_by": null
  },
  ...
]
```

**Error Responses:**

- `500 Internal Server Error`: Database error

---

### 5. Get Queue Statistics

Retrieve aggregate statistics about the task queue.

**Endpoint:** `GET /queue/stats`

**Response (200 OK):**

```json
{
  "total_tasks": 150,
  "queued_tasks": 45,
  "processing_tasks": 5,
  "completed_tasks": 90,
  "failed_tasks": 10,
  "oldest_queued_age_seconds": 120.5
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| total_tasks | integer | Total number of tasks in the queue |
| queued_tasks | integer | Number of tasks waiting to be processed |
| processing_tasks | integer | Number of tasks currently being processed |
| completed_tasks | integer | Number of successfully completed tasks |
| failed_tasks | integer | Number of failed tasks |
| oldest_queued_age_seconds | float/null | Age in seconds of the oldest queued task, or null if no queued tasks |

**Error Responses:**

- `500 Internal Server Error`: Database error

---

## Error Handling

All API endpoints return errors in a consistent format:

```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-11-05T19:35:00Z"
}
```

### Common Error Codes

- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid request data
- `503 Service Unavailable`: Service temporarily unavailable
- `500 Internal Server Error`: Internal server error

---

## Examples

### Python Example

```python
import requests

# Enqueue a task
response = requests.post(
    "http://localhost:8000/api/queue/enqueue",
    json={
        "type": "video_processing",
        "priority": 50,
        "payload": {"format": "mp4"},
        "idempotency_key": "video-123",
    }
)
task_id = response.json()["task_id"]

# Poll task status
response = requests.get(
    f"http://localhost:8000/api/queue/tasks/{task_id}"
)
status = response.json()["status"]

# Cancel task if needed
if status in ("queued", "processing"):
    response = requests.post(
        f"http://localhost:8000/api/queue/tasks/{task_id}/cancel"
    )
```

### cURL Examples

```bash
# Enqueue a task
curl -X POST http://localhost:8000/api/queue/enqueue \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email_notification",
    "payload": {"recipient": "user@example.com"},
    "idempotency_key": "email-456"
  }'

# Get task status
curl http://localhost:8000/api/queue/tasks/1

# Cancel task
curl -X POST http://localhost:8000/api/queue/tasks/1/cancel

# Get queue stats
curl http://localhost:8000/api/queue/stats

# List queued tasks
curl http://localhost:8000/api/queue/tasks?status=queued&limit=10
```

---

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces provide:
- Complete API schema
- Interactive request testing
- Request/response examples
- Parameter validation

---

## Best Practices

### 1. Use Idempotency Keys

Always use idempotency keys for critical operations to prevent duplicate task creation:

```python
response = requests.post(
    "/api/queue/enqueue",
    json={
        "type": "payment_processing",
        "idempotency_key": f"payment-{order_id}",
        "payload": {...}
    }
)
```

### 2. Poll Responsibly

When polling task status, use reasonable intervals to avoid overwhelming the API:

```python
import time

while True:
    response = requests.get(f"/api/queue/tasks/{task_id}")
    status = response.json()["status"]
    
    if status in ("completed", "failed"):
        break
    
    time.sleep(5)  # Poll every 5 seconds
```

### 3. Handle Errors Gracefully

Always handle potential errors:

```python
try:
    response = requests.post("/api/queue/enqueue", json=task_data)
    response.raise_for_status()
    task_id = response.json()["task_id"]
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 503:
        # Queue is busy, retry later
        time.sleep(1)
        retry()
    else:
        # Handle other errors
        log_error(e)
```

### 4. Use Appropriate Priorities

Set task priorities based on business importance:

- **1-50**: High priority (urgent tasks)
- **51-100**: Normal priority (default)
- **101-1000**: Low priority (background tasks)

### 5. Monitor Queue Statistics

Regularly check queue statistics to detect issues:

```python
response = requests.get("/api/queue/stats")
stats = response.json()

# Alert if queue is backing up
if stats["queued_tasks"] > 1000:
    send_alert("Queue backup detected")

# Alert if old tasks are stuck
if stats["oldest_queued_age_seconds"] > 3600:  # 1 hour
    send_alert("Tasks are stuck in queue")
```

---

## Rate Limiting

Currently, no rate limiting is enforced. In production:

- Implement rate limiting per client/IP
- Use exponential backoff for retries
- Monitor and alert on abnormal usage patterns

---

## Security Considerations

**Current Implementation:**

- No authentication required
- No authorization checks
- All endpoints are publicly accessible

**Production Recommendations:**

1. Add API key authentication
2. Implement role-based access control
3. Use HTTPS for all connections
4. Validate and sanitize all input data
5. Rate limit API requests
6. Log all API access for audit trails

---

## Performance

**Throughput:**

- Enqueue: ~100-1000 tasks/minute
- Status polling: <10ms per request
- Queue stats: <50ms (cached for 2 seconds)

**Optimization Tips:**

1. Batch multiple enqueue operations when possible
2. Use queue statistics endpoint instead of counting tasks manually
3. Cache task status locally when polling frequently
4. Use appropriate limit values when listing tasks

---

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
