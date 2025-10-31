# Issue #102: Design REST API Endpoints

**Type**: Feature  
**Priority**: High  
**Status**: Done  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1 week  
**Dependencies**: None  
**Can be parallelized with**: #101 (Project Structure)  
**Completed**: 2025-10-30

---

## Description

Define a comprehensive REST API contract for communication between the Vue frontend and FastAPI backend. This API will enable the web client to discover modules, execute them with parameters, monitor their status, retrieve logs, and manage configurations. The design follows RESTful principles and is optimized for localhost-only access.

## API Design Principles

- **RESTful**: Use standard HTTP methods (GET, POST, PUT, DELETE)
- **Stateless**: Each request contains all necessary information
- **JSON**: All request/response bodies use JSON format
- **Localhost Only**: No authentication required (runs on 127.0.0.1)
- **Async**: All endpoints are async-compatible
- **OpenAPI**: Auto-generated documentation via FastAPI

## API Endpoints

### 1. Module Discovery

#### GET `/api/modules`
Get list of all available PrismQ modules.

**Response**: `200 OK`
```json
{
  "modules": [
    {
      "id": "youtube-shorts",
      "name": "YouTube Shorts Source",
      "description": "Collect trending YouTube Shorts",
      "category": "Content/Shorts",
      "version": "1.0.0",
      "parameters": [
        {
          "name": "max_results",
          "type": "number",
          "default": 50,
          "min": 1,
          "max": 1000,
          "required": true,
          "description": "Maximum number of shorts to collect"
        },
        {
          "name": "trending_category",
          "type": "select",
          "options": ["All", "Gaming", "Music", "Entertainment"],
          "default": "All",
          "required": false,
          "description": "Category to filter by"
        }
      ],
      "tags": ["content", "youtube", "shorts"],
      "status": "active"
    }
  ],
  "total": 15
}
```

#### GET `/api/modules/{module_id}`
Get detailed information about a specific module.

**Parameters**:
- `module_id` (path): Module identifier

**Response**: `200 OK`
```json
{
  "id": "youtube-shorts",
  "name": "YouTube Shorts Source",
  "description": "Collect trending YouTube Shorts from YouTube API",
  "category": "Content/Shorts",
  "version": "1.0.0",
  "script_path": "../../Sources/Content/Shorts/YouTubeShorts/src/main.py",
  "parameters": [...],
  "tags": ["content", "youtube", "shorts"],
  "status": "active",
  "last_run": "2025-10-30T15:30:00Z",
  "total_runs": 42,
  "success_rate": 95.2
}
```

**Error Response**: `404 Not Found`
```json
{
  "detail": "Module not found"
}
```

---

### 2. Module Configuration

#### GET `/api/modules/{module_id}/config`
Retrieve saved configuration for a module.

**Parameters**:
- `module_id` (path): Module identifier

**Response**: `200 OK`
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming",
    "api_key": "***",
    "output_format": "json"
  },
  "updated_at": "2025-10-30T14:20:00Z"
}
```

#### POST `/api/modules/{module_id}/config`
Update saved configuration for a module.

**Parameters**:
- `module_id` (path): Module identifier

**Request Body**:
```json
{
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming",
    "api_key": "your-api-key-here",
    "output_format": "json"
  }
}
```

**Response**: `200 OK`
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming",
    "api_key": "***",
    "output_format": "json"
  },
  "updated_at": "2025-10-30T15:45:00Z",
  "message": "Configuration saved successfully"
}
```

**Error Response**: `400 Bad Request`
```json
{
  "detail": "Invalid parameter: max_results must be between 1 and 1000"
}
```

---

### 3. Module Execution

#### POST `/api/modules/{module_id}/run`
Launch a module with specified parameters.

**Parameters**:
- `module_id` (path): Module identifier

**Request Body**:
```json
{
  "parameters": {
    "max_results": 50,
    "trending_category": "All"
  },
  "save_config": true
}
```

**Response**: `202 Accepted`
```json
{
  "run_id": "run_20251030_154523_abc123",
  "module_id": "youtube-shorts",
  "status": "queued",
  "created_at": "2025-10-30T15:45:23Z",
  "parameters": {
    "max_results": 50,
    "trending_category": "All"
  },
  "message": "Module execution started"
}
```

**Error Response**: `400 Bad Request`
```json
{
  "detail": "Missing required parameter: api_key"
}
```

**Error Response**: `409 Conflict`
```json
{
  "detail": "Module is already running (run_id: run_20251030_154500_xyz789)"
}
```

---

### 4. Run Management

#### GET `/api/runs`
List all runs (current and historical).

**Query Parameters**:
- `module_id` (optional): Filter by module
- `status` (optional): Filter by status (queued, running, completed, failed)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**: `200 OK`
```json
{
  "runs": [
    {
      "run_id": "run_20251030_154523_abc123",
      "module_id": "youtube-shorts",
      "module_name": "YouTube Shorts Source",
      "status": "running",
      "created_at": "2025-10-30T15:45:23Z",
      "started_at": "2025-10-30T15:45:25Z",
      "duration_seconds": 45,
      "progress_percent": 60
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### GET `/api/runs/{run_id}`
Get detailed status of a specific run.

**Parameters**:
- `run_id` (path): Run identifier

**Response**: `200 OK`
```json
{
  "run_id": "run_20251030_154523_abc123",
  "module_id": "youtube-shorts",
  "module_name": "YouTube Shorts Source",
  "status": "running",
  "created_at": "2025-10-30T15:45:23Z",
  "started_at": "2025-10-30T15:45:25Z",
  "completed_at": null,
  "duration_seconds": 120,
  "progress_percent": 75,
  "items_processed": 38,
  "items_total": 50,
  "exit_code": null,
  "error_message": null,
  "parameters": {
    "max_results": 50,
    "trending_category": "All"
  }
}
```

**Error Response**: `404 Not Found`
```json
{
  "detail": "Run not found"
}
```

#### DELETE `/api/runs/{run_id}`
Cancel a running module execution.

**Parameters**:
- `run_id` (path): Run identifier

**Response**: `200 OK`
```json
{
  "run_id": "run_20251030_154523_abc123",
  "status": "cancelled",
  "message": "Run cancelled successfully"
}
```

**Error Response**: `400 Bad Request`
```json
{
  "detail": "Cannot cancel run: already completed"
}
```

---

### 5. Log Streaming

#### GET `/api/runs/{run_id}/logs`
Retrieve logs for a specific run.

**Parameters**:
- `run_id` (path): Run identifier

**Query Parameters**:
- `tail` (optional): Number of recent lines (default: 500)
- `follow` (optional): Stream logs in real-time (default: false)

**Response**: `200 OK`
```json
{
  "run_id": "run_20251030_154523_abc123",
  "logs": [
    {
      "timestamp": "2025-10-30T15:45:25Z",
      "level": "INFO",
      "message": "Starting YouTube Shorts collection..."
    },
    {
      "timestamp": "2025-10-30T15:45:26Z",
      "level": "INFO",
      "message": "Connecting to YouTube API..."
    },
    {
      "timestamp": "2025-10-30T15:45:28Z",
      "level": "INFO",
      "message": "Processing video 1/50..."
    }
  ],
  "total_lines": 145,
  "truncated": false
}
```

#### GET `/api/runs/{run_id}/logs/stream` (SSE)
Stream logs in real-time using Server-Sent Events.

**Parameters**:
- `run_id` (path): Run identifier

**Response**: `200 OK` (text/event-stream)
```
data: {"timestamp": "2025-10-30T15:45:25Z", "level": "INFO", "message": "Starting..."}

data: {"timestamp": "2025-10-30T15:45:26Z", "level": "INFO", "message": "Processing..."}

data: {"timestamp": "2025-10-30T15:45:28Z", "level": "INFO", "message": "Completed!"}
```

---

### 6. Results & Artifacts

#### GET `/api/runs/{run_id}/results`
Get execution results and output artifacts.

**Parameters**:
- `run_id` (path): Run identifier

**Response**: `200 OK`
```json
{
  "run_id": "run_20251030_154523_abc123",
  "status": "completed",
  "summary": {
    "items_collected": 50,
    "items_saved": 48,
    "errors": 2,
    "duration_seconds": 180
  },
  "output_files": [
    {
      "filename": "youtube_shorts_20251030.json",
      "path": "/outputs/youtube_shorts_20251030.json",
      "size_bytes": 245680,
      "created_at": "2025-10-30T15:48:23Z"
    }
  ],
  "metrics": {
    "avg_views": 125000,
    "avg_engagement_rate": 4.5,
    "top_category": "Gaming"
  }
}
```

---

### 7. System Health

#### GET `/api/health`
Health check endpoint.

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "active_runs": 2,
  "total_modules": 15
}
```

#### GET `/api/system/stats`
System statistics and metrics.

**Response**: `200 OK`
```json
{
  "runs": {
    "total": 1500,
    "successful": 1425,
    "failed": 75,
    "success_rate": 95.0
  },
  "modules": {
    "total": 15,
    "active": 2,
    "idle": 13
  },
  "system": {
    "cpu_percent": 15.5,
    "memory_percent": 42.3,
    "disk_free_gb": 512.5
  }
}
```

---

## Pydantic Models

### Module Model
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class ModuleParameter(BaseModel):
    name: str
    type: Literal["text", "number", "select", "checkbox", "password"]
    default: Optional[str | int | bool] = None
    options: Optional[List[str]] = None
    required: bool = False
    description: str = ""
    min: Optional[int] = None
    max: Optional[int] = None

class Module(BaseModel):
    id: str
    name: str
    description: str
    category: str
    version: str = "1.0.0"
    script_path: str
    parameters: List[ModuleParameter]
    tags: List[str] = []
    status: Literal["active", "inactive", "maintenance"] = "active"
    last_run: Optional[datetime] = None
    total_runs: int = 0
    success_rate: float = 0.0
```

### Run Model
```python
class RunCreate(BaseModel):
    parameters: dict
    save_config: bool = True

class Run(BaseModel):
    run_id: str
    module_id: str
    module_name: str
    status: Literal["queued", "running", "completed", "failed", "cancelled"]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    progress_percent: Optional[int] = None
    items_processed: Optional[int] = None
    items_total: Optional[int] = None
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    parameters: dict
```

### Log Model
```python
class LogEntry(BaseModel):
    timestamp: datetime
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    message: str

class LogResponse(BaseModel):
    run_id: str
    logs: List[LogEntry]
    total_lines: int
    truncated: bool
```

---

## Error Handling

### Standard Error Response
```python
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created
- `202 Accepted`: Request accepted (async operation started)
- `400 Bad Request`: Invalid parameters or request
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., already running)
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

---

## Tasks

- [ ] Document all endpoint specifications in OpenAPI/Swagger format
- [ ] Create Pydantic models for all request/response bodies
- [ ] Define error handling standards and response formats
- [ ] Create API versioning strategy (e.g., `/api/v1/`)
- [ ] Document rate limiting (if any)
- [ ] Create example request/response for each endpoint
- [ ] Set up automatic API documentation generation
- [ ] Define CORS policy for localhost development

## Acceptance Criteria

- [x] All endpoints documented with request/response examples
- [x] Pydantic models defined for type safety
- [x] Error handling standards established
- [x] OpenAPI/Swagger documentation auto-generated
- [x] API supports all required operations (CRUD, execution, monitoring)
- [x] Real-time log streaming approach defined (SSE)

## Testing

- [ ] Create Postman/Insomnia collection for API testing
- [ ] Write API contract tests
- [ ] Validate all error scenarios
- [ ] Test concurrent request handling

## Related Issues

- **Parallel**: #101 (Project Structure)
- **Next**: #103 (Backend Module Runner) - Implements these endpoints
- **Next**: #105 (Frontend UI) - Consumes these endpoints

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [REST API Best Practices](https://restfulapi.net/)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
