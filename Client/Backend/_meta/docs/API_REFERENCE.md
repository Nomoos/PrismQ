# PrismQ Web Client REST API

**Version:** 1.0.0  
**Base URL:** `http://127.0.0.1:8000`  
**Documentation:** `http://127.0.0.1:8000/docs` (Swagger UI)

## Overview

The PrismQ Web Client Backend provides a comprehensive REST API for discovering, configuring, and running PrismQ data collection modules. The API follows RESTful principles and provides automatic OpenAPI/Swagger documentation.

## Authentication

**None required** - This API is designed for localhost-only access (127.0.0.1).

## API Endpoints

### Module Discovery

#### `GET /api/modules`
Get list of all available PrismQ modules.

**Response:** `200 OK`
```json
{
  "modules": [...],
  "total": 15
}
```

#### `GET /api/modules/{module_id}`
Get detailed information about a specific module.

**Response:** `200 OK` | `404 Not Found`

---

### Module Configuration

Configuration persistence allows module parameters to be saved and automatically loaded for future runs.

#### `GET /api/modules/{module_id}/config`
Retrieve saved configuration for a module. Returns saved parameters merged with module defaults.

**Response:** `200 OK`
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming"
  },
  "updated_at": "2025-10-30T15:45:23.123456Z"
}
```

**Error Responses:**
- `404 Not Found` - Module doesn't exist

---

#### `POST /api/modules/{module_id}/config`
Save configuration for a module. Parameters are validated against the module's parameter schema.

**Request Body:**
```json
{
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming"
  }
}
```

**Response:** `200 OK`
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming"
  },
  "updated_at": "2025-10-30T15:45:23.123456Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameters (type mismatch, out of range, invalid option)
- `404 Not Found` - Module doesn't exist
- `500 Internal Server Error` - Failed to save configuration

**Validation:**
- Type checking (number, text, select, checkbox, password)
- Range validation (min/max for numbers)
- Option validation (allowed values for select)
- Required parameter enforcement

---

#### `DELETE /api/modules/{module_id}/config`
Delete saved configuration for a module, reverting to defaults.

**Response:** `200 OK`
```json
{
  "message": "Configuration deleted successfully"
}
```

**Error Responses:**
- `404 Not Found` - Module doesn't exist

---

### Module Execution

#### `POST /api/modules/{module_id}/run`
Launch a module with specified parameters.

**Request Body:**
```json
{
  "parameters": {
    "max_results": 50
  },
  "save_config": true
}
```

**Response:** `202 Accepted` | `400 Bad Request` | `409 Conflict`

---

### Run Management

#### `GET /api/runs`
List all runs with optional filtering and pagination.

**Query Parameters:**
- `module_id` (optional): Filter by module
- `status` (optional): Filter by status (queued, running, completed, failed, cancelled)
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`

#### `GET /api/runs/{run_id}`
Get detailed status of a specific run.

**Response:** `200 OK` | `404 Not Found`

#### `DELETE /api/runs/{run_id}`
Cancel a running module execution.

**Response:** `200 OK` | `400 Bad Request` | `404 Not Found`

---

### Log Streaming

#### `GET /api/runs/{run_id}/logs`
Retrieve logs for a specific run with advanced filtering options.

**Query Parameters:**
- `tail` (optional): Number of recent lines (default: 500, max: 10000)
- `since` (optional): ISO 8601 timestamp to get logs after (e.g., "2025-10-31T12:00:00Z")

**Response:** `200 OK` | `404 Not Found`
```json
{
  "run_id": "run_20251031_120000_youtube_abc123",
  "logs": [
    {
      "timestamp": "2025-10-31T12:00:01.123456Z",
      "level": "INFO",
      "message": "Starting data collection..."
    },
    {
      "timestamp": "2025-10-31T12:00:02.456789Z",
      "level": "WARNING",
      "message": "Rate limit approaching"
    }
  ],
  "total_lines": 150,
  "truncated": true
}
```

#### `GET /api/runs/{run_id}/logs/stream`
Stream logs in real-time using Server-Sent Events (SSE).

This endpoint keeps the connection open and streams new log entries as they arrive from the running module. The client receives events in real-time until the run completes or the connection is closed.

**Response:** `text/event-stream` | `404 Not Found`

**Event Types:**
- `log`: New log entry
- `complete`: Run completed
- `error`: Error occurred

**Example SSE Stream:**
```
event: log
data: {"timestamp":"2025-10-31T12:00:01.123456Z","level":"INFO","message":"Processing item 1/50"}

event: log
data: {"timestamp":"2025-10-31T12:00:02.456789Z","level":"INFO","message":"Processing item 2/50"}

event: complete
data: {"status":"completed"}
```

**Client Example (JavaScript):**
```javascript
const eventSource = new EventSource('/api/runs/run_123/logs/stream');

eventSource.addEventListener('log', (event) => {
  const log = JSON.parse(event.data);
  console.log(`[${log.level}] ${log.message}`);
});

eventSource.addEventListener('complete', () => {
  console.log('Run completed');
  eventSource.close();
});

eventSource.addEventListener('error', (event) => {
  console.error('SSE error:', event);
});
```

#### `GET /api/runs/{run_id}/logs/download`
Download complete log file for a run.

Returns the entire log file as a plain text download, suitable for saving to disk or viewing in a text editor.

**Response:** `200 OK` (plain text) | `404 Not Found`

**Response Headers:**
- `Content-Type`: text/plain
- `Content-Disposition`: attachment; filename={run_id}.log

**Example Response:**
```
[2025-10-31T12:00:00.123456Z] [INFO] [stdout] Starting module execution...
[2025-10-31T12:00:01.234567Z] [INFO] [stdout] Processing item 1/50
[2025-10-31T12:00:02.345678Z] [WARNING] [stdout] Rate limit approaching
[2025-10-31T12:00:03.456789Z] [ERROR] [stderr] Connection timeout
[2025-10-31T12:00:04.567890Z] [INFO] [stdout] Retrying...
```

---

### Results & Artifacts

#### `GET /api/runs/{run_id}/results`
Get execution results and output artifacts.

**Response:** `200 OK` | `404 Not Found`

---

### System Health

#### `GET /api/health`
Health check endpoint with server status.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "active_runs": 2,
  "total_modules": 15
}
```

#### `GET /api/system/stats`
System statistics and metrics.

**Response:** `200 OK`

---

## Data Models

### Module
- `id`: Unique identifier
- `name`: Human-readable name
- `description`: Module description
- `category`: Module category
- `version`: Module version
- `script_path`: Path to executable script
- `parameters`: List of parameter definitions
- `tags`: Module tags
- `status`: Module status (active, inactive, maintenance)
- `last_run`: Last run timestamp
- `total_runs`: Total number of runs
- `success_rate`: Success rate percentage

### ModuleParameter
- `name`: Parameter name
- `type`: Parameter type (text, number, select, checkbox, password)
- `default`: Default value
- `options`: Available options (for select type)
- `required`: Whether parameter is required
- `description`: Parameter description
- `min`: Minimum value (for number type)
- `max`: Maximum value (for number type)

### Run
- `run_id`: Unique run identifier
- `module_id`: Module identifier
- `module_name`: Module name
- `status`: Run status (queued, running, completed, failed, cancelled)
- `created_at`: Creation timestamp
- `started_at`: Start timestamp
- `completed_at`: Completion timestamp
- `duration_seconds`: Run duration
- `progress_percent`: Progress percentage (0-100)
- `items_processed`: Number of items processed
- `items_total`: Total number of items
- `exit_code`: Process exit code
- `error_message`: Error message if failed
- `parameters`: Run parameters

### LogEntry
- `timestamp`: Log timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `message`: Log message

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message",
  "error_code": "optional_code",
  "timestamp": "2025-10-30T15:30:00Z"
}
```

### HTTP Status Codes
- `200 OK`: Successful request
- `202 Accepted`: Request accepted (async operation started)
- `400 Bad Request`: Invalid parameters or request
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., module already running)
- `500 Internal Server Error`: Server error

---

## Interactive Documentation

Visit `http://127.0.0.1:8000/docs` for interactive Swagger UI documentation with:
- Full API schema
- Request/response examples
- Try-it-out functionality
- Model schemas

Visit `http://127.0.0.1:8000/redoc` for alternative ReDoc documentation.

---

## Development

### Running the Server
```bash
cd Client/Backend
pip install -r requirements.txt
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### Running Tests
```bash
cd Client/Backend
pytest ../_meta/tests/Backend/ -v
```

### Test Coverage
- 23 comprehensive tests covering all endpoints
- Edge cases and error scenarios tested
- Pagination and filtering tested
- Configuration persistence tested

---

## Notes

- All endpoints use JSON for request/response bodies
- All timestamps are in UTC using ISO 8601 format
- The API is fully async-compatible
- Mock data is used for initial implementation
- SSE (Server-Sent Events) is used for real-time log streaming
- CORS is configured for localhost Vue frontend (ports 5173)
