# PrismQ Web Client - API Reference

Complete REST API documentation for the PrismQ Web Client backend.

**Version:** 1.0.0  
**Base URL:** `http://127.0.0.1:8000`  
**Interactive Documentation:** `http://127.0.0.1:8000/docs` (Swagger UI)

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Module Endpoints](#module-endpoints)
- [Run Management](#run-management)
- [Log Streaming](#log-streaming)
- [System Endpoints](#system-endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Overview

The PrismQ Web Client Backend provides a comprehensive REST API for discovering, configuring, and running PrismQ data collection modules. The API follows RESTful principles and provides automatic OpenAPI/Swagger documentation.

### Key Features

- **Module Discovery**: Browse and search available modules
- **Configuration Persistence**: Save and load module configurations
- **Module Execution**: Launch modules with parameters
- **Real-Time Monitoring**: Stream logs via Server-Sent Events (SSE)
- **Run Management**: Track and control module executions

### Base URL

All API endpoints are relative to the base URL:
```
http://127.0.0.1:8000
```

For production, this would be your server's domain.

## Authentication

**None required** - This API is designed for localhost-only access (127.0.0.1).

**Security Note**: The API should only be exposed on localhost. For remote access, implement proper authentication and authorization.

## Module Endpoints

### List All Modules

Get a list of all available PrismQ modules.

**Endpoint:** `GET /api/modules`

**Response:** `200 OK`
```json
{
  "modules": [
    {
      "id": "youtube-shorts",
      "name": "YouTube Shorts Source",
      "description": "Collect trending YouTube Shorts videos",
      "category": "Sources/Content/Shorts",
      "script_path": "../../Sources/Content/Shorts/YouTubeShorts/src/main.py",
      "parameters": [...],
      "tags": ["youtube", "shorts", "video"],
      "version": "1.0.0",
      "last_run": "2025-10-31T10:30:00Z",
      "total_runs": 42,
      "success_rate": 95.2
    }
  ],
  "total": 15
}
```

**Example:**
```bash
curl http://localhost:8000/api/modules
```

### Get Module Details

Get detailed information about a specific module.

**Endpoint:** `GET /api/modules/{module_id}`

**Path Parameters:**
- `module_id` (string): Unique module identifier

**Response:** `200 OK`
```json
{
  "id": "youtube-shorts",
  "name": "YouTube Shorts Source",
  "description": "Collect trending YouTube Shorts videos",
  "category": "Sources/Content/Shorts",
  "script_path": "../../Sources/Content/Shorts/YouTubeShorts/src/main.py",
  "parameters": [
    {
      "name": "max_results",
      "type": "number",
      "default": 50,
      "required": true,
      "description": "Maximum number of videos to collect",
      "min": 1,
      "max": 500
    }
  ],
  "tags": ["youtube", "shorts", "video"],
  "version": "1.0.0"
}
```

**Error Responses:**
- `404 Not Found` - Module doesn't exist

**Example:**
```bash
curl http://localhost:8000/api/modules/youtube-shorts
```

### Get Module Configuration

Retrieve saved configuration for a module.

**Endpoint:** `GET /api/modules/{module_id}/config`

**Path Parameters:**
- `module_id` (string): Unique module identifier

**Response:** `200 OK`
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 100,
    "trending_category": "Gaming"
  },
  "updated_at": "2025-10-31T10:15:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Module doesn't exist or no configuration saved

**Example:**
```bash
curl http://localhost:8000/api/modules/youtube-shorts/config
```

### Save Module Configuration

Save configuration for a module.

**Endpoint:** `POST /api/modules/{module_id}/config`

**Path Parameters:**
- `module_id` (string): Unique module identifier

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
  "updated_at": "2025-10-31T10:15:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameters
  - Type mismatch (e.g., string instead of number)
  - Out of range (e.g., value exceeds max)
  - Invalid option (e.g., not in options list)
  - Missing required parameter
- `404 Not Found` - Module doesn't exist
- `500 Internal Server Error` - Failed to save configuration

**Example:**
```bash
curl -X POST http://localhost:8000/api/modules/youtube-shorts/config \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"max_results": 100, "trending_category": "Gaming"}}'
```

### Delete Module Configuration

Delete saved configuration for a module.

**Endpoint:** `DELETE /api/modules/{module_id}/config`

**Path Parameters:**
- `module_id` (string): Unique module identifier

**Response:** `200 OK`
```json
{
  "message": "Configuration deleted successfully"
}
```

**Error Responses:**
- `404 Not Found` - Module doesn't exist

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/modules/youtube-shorts/config
```

## Run Management

### List All Runs

List all runs with optional filtering and pagination.

**Endpoint:** `GET /api/runs`

**Query Parameters:**
- `module_id` (optional): Filter by module ID
- `status` (optional): Filter by status (queued, running, completed, failed, cancelled)
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "runs": [
    {
      "run_id": "run_20251031_120000_youtube_abc123",
      "module_id": "youtube-shorts",
      "module_name": "YouTube Shorts Source",
      "status": "running",
      "created_at": "2025-10-31T12:00:00Z",
      "started_at": "2025-10-31T12:00:01Z",
      "completed_at": null,
      "duration_seconds": 45,
      "progress_percent": 60,
      "items_processed": 30,
      "items_total": 50,
      "parameters": {
        "max_results": 50
      }
    }
  ],
  "total": 128,
  "limit": 50,
  "offset": 0
}
```

**Examples:**
```bash
# All runs
curl http://localhost:8000/api/runs

# Only running modules
curl http://localhost:8000/api/runs?status=running

# Runs for specific module
curl http://localhost:8000/api/runs?module_id=youtube-shorts

# Paginated results
curl http://localhost:8000/api/runs?limit=20&offset=40
```

### Get Run Details

Get detailed status of a specific run.

**Endpoint:** `GET /api/runs/{run_id}`

**Path Parameters:**
- `run_id` (string): Unique run identifier

**Response:** `200 OK`
```json
{
  "run_id": "run_20251031_120000_youtube_abc123",
  "module_id": "youtube-shorts",
  "module_name": "YouTube Shorts Source",
  "status": "completed",
  "created_at": "2025-10-31T12:00:00Z",
  "started_at": "2025-10-31T12:00:01Z",
  "completed_at": "2025-10-31T12:05:23Z",
  "duration_seconds": 322,
  "progress_percent": 100,
  "items_processed": 50,
  "items_total": 50,
  "exit_code": 0,
  "parameters": {
    "max_results": 50,
    "trending_category": "Gaming"
  }
}
```

**Error Responses:**
- `404 Not Found` - Run doesn't exist

**Example:**
```bash
curl http://localhost:8000/api/runs/run_20251031_120000_youtube_abc123
```

### Launch Module

Launch a module with specified parameters.

**Endpoint:** `POST /api/runs`

**Request Body:**
```json
{
  "module_id": "youtube-shorts",
  "parameters": {
    "max_results": 50,
    "trending_category": "Gaming"
  },
  "save_config": true
}
```

**Response:** `202 Accepted`
```json
{
  "run_id": "run_20251031_120000_youtube_abc123",
  "module_id": "youtube-shorts",
  "status": "queued",
  "created_at": "2025-10-31T12:00:00Z",
  "parameters": {
    "max_results": 50,
    "trending_category": "Gaming"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid parameters or module not found
- `409 Conflict` - Maximum concurrent runs reached

**Example:**
```bash
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{
    "module_id": "youtube-shorts",
    "parameters": {"max_results": 50},
    "save_config": true
  }'
```

### Cancel Run

Cancel a running module execution.

**Endpoint:** `DELETE /api/runs/{run_id}`

**Path Parameters:**
- `run_id` (string): Unique run identifier

**Response:** `200 OK`
```json
{
  "run_id": "run_20251031_120000_youtube_abc123",
  "status": "cancelled",
  "message": "Run cancelled successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Run already completed or can't be cancelled
- `404 Not Found` - Run doesn't exist

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/runs/run_20251031_120000_youtube_abc123
```

## Log Streaming

### Get Logs (Snapshot)

Retrieve logs for a specific run with filtering options.

**Endpoint:** `GET /api/runs/{run_id}/logs`

**Path Parameters:**
- `run_id` (string): Unique run identifier

**Query Parameters:**
- `tail` (optional): Number of recent lines (default: 500, max: 10000)
- `since` (optional): ISO 8601 timestamp to get logs after

**Response:** `200 OK`
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
      "level": "INFO",
      "message": "Processing item 1/50"
    }
  ],
  "total_lines": 150,
  "truncated": true
}
```

**Error Responses:**
- `404 Not Found` - Run doesn't exist

**Examples:**
```bash
# Last 500 lines (default)
curl http://localhost:8000/api/runs/run_abc123/logs

# Last 100 lines
curl http://localhost:8000/api/runs/run_abc123/logs?tail=100

# Logs since timestamp
curl http://localhost:8000/api/runs/run_abc123/logs?since=2025-10-31T12:00:00Z
```

### Stream Logs (Real-Time)

Stream logs in real-time using Server-Sent Events (SSE).

**Endpoint:** `GET /api/runs/{run_id}/logs/stream`

**Path Parameters:**
- `run_id` (string): Unique run identifier

**Response:** `text/event-stream`

**Event Types:**
- `log`: New log entry
- `complete`: Run completed
- `error`: Error occurred

**Example SSE Stream:**
```
event: log
data: {"timestamp":"2025-10-31T12:00:01Z","level":"INFO","message":"Processing item 1/50"}

event: log
data: {"timestamp":"2025-10-31T12:00:02Z","level":"INFO","message":"Processing item 2/50"}

event: complete
data: {"status":"completed","exit_code":0}
```

**Client Example (JavaScript):**
```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/runs/run_abc123/logs/stream'
);

eventSource.addEventListener('log', (event) => {
  const log = JSON.parse(event.data);
  console.log(`[${log.level}] ${log.message}`);
});

eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data);
  console.log('Run completed with exit code:', data.exit_code);
  eventSource.close();
});

eventSource.addEventListener('error', (error) => {
  console.error('SSE error:', error);
  eventSource.close();
});
```

**Error Responses:**
- `404 Not Found` - Run doesn't exist

### Download Logs

Download complete log file for a run.

**Endpoint:** `GET /api/runs/{run_id}/logs/download`

**Path Parameters:**
- `run_id` (string): Unique run identifier

**Response:** `200 OK` (text/plain)

**Response Headers:**
- `Content-Type: text/plain`
- `Content-Disposition: attachment; filename={run_id}.log`

**Example Response:**
```
[2025-10-31T12:00:00Z] [INFO] [stdout] Starting module execution...
[2025-10-31T12:00:01Z] [INFO] [stdout] Processing item 1/50
[2025-10-31T12:00:02Z] [WARNING] [stdout] Rate limit approaching
[2025-10-31T12:00:03Z] [ERROR] [stderr] Connection timeout
[2025-10-31T12:00:04Z] [INFO] [stdout] Retrying...
```

**Error Responses:**
- `404 Not Found` - Run doesn't exist or logs not available

**Example:**
```bash
curl http://localhost:8000/api/runs/run_abc123/logs/download \
  -o run_abc123.log
```

## System Endpoints

### Health Check

Check server health and status.

**Endpoint:** `GET /health`

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

**Example:**
```bash
curl http://localhost:8000/health
```

### System Statistics

Get system statistics and metrics.

**Endpoint:** `GET /api/system/stats`

**Response:** `200 OK`
```json
{
  "total_runs": 1234,
  "active_runs": 3,
  "completed_runs": 1150,
  "failed_runs": 81,
  "success_rate": 93.4,
  "total_modules": 15,
  "uptime_seconds": 86400,
  "memory_usage_mb": 256.5,
  "disk_usage_mb": 1024.8
}
```

**Example:**
```bash
curl http://localhost:8000/api/system/stats
```

## Data Models

### Module

```typescript
interface Module {
  id: string;                    // Unique identifier
  name: string;                  // Human-readable name
  description: string;           // Module description
  category: string;              // Category path (e.g., "Sources/Content/Shorts")
  script_path: string;           // Path to executable script
  parameters: ModuleParameter[]; // Parameter definitions
  tags: string[];                // Module tags
  version?: string;              // Module version
  author?: string;               // Module author
  last_run?: string;             // Last run timestamp (ISO 8601)
  total_runs?: number;           // Total number of runs
  success_rate?: number;         // Success rate percentage
}
```

### ModuleParameter

```typescript
interface ModuleParameter {
  name: string;          // Parameter name
  type: 'text' | 'number' | 'select' | 'checkbox' | 'password';
  default: any;          // Default value
  required: boolean;     // Whether parameter is required
  description: string;   // Parameter description
  placeholder?: string;  // Placeholder text
  min?: number;          // Minimum value (number type)
  max?: number;          // Maximum value (number type)
  step?: number;         // Step value (number type)
  options?: string[];    // Available options (select type)
  pattern?: string;      // Validation regex (text type)
  maxLength?: number;    // Maximum length (text type)
}
```

### Run

```typescript
interface Run {
  run_id: string;            // Unique run identifier
  module_id: string;         // Module identifier
  module_name: string;       // Module name
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  created_at: string;        // Creation timestamp (ISO 8601)
  started_at?: string;       // Start timestamp (ISO 8601)
  completed_at?: string;     // Completion timestamp (ISO 8601)
  duration_seconds?: number; // Run duration
  progress_percent?: number; // Progress percentage (0-100)
  items_processed?: number;  // Number of items processed
  items_total?: number;      // Total number of items
  exit_code?: number;        // Process exit code
  error_message?: string;    // Error message if failed
  parameters: object;        // Run parameters
}
```

### LogEntry

```typescript
interface LogEntry {
  timestamp: string;  // Log timestamp (ISO 8601)
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  message: string;    // Log message
}
```

## Error Handling

### Standard Error Response

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "OPTIONAL_ERROR_CODE",
  "timestamp": "2025-10-31T12:00:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/DELETE request |
| 202 | Accepted | Async operation started (e.g., module launch) |
| 400 | Bad Request | Invalid parameters or malformed request |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (e.g., max concurrent runs) |
| 500 | Internal Server Error | Unexpected server error |

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `MODULE_NOT_FOUND` | Module ID doesn't exist |
| `RUN_NOT_FOUND` | Run ID doesn't exist |
| `INVALID_PARAMETERS` | Parameter validation failed |
| `MAX_CONCURRENT_RUNS` | Too many concurrent runs |
| `RUN_NOT_CANCELLABLE` | Run cannot be cancelled (already completed) |

## Interactive Documentation

The backend provides interactive API documentation:

### Swagger UI

Visit **http://localhost:8000/docs** for:
- Full API schema
- Request/response examples
- Try-it-out functionality
- Model schemas
- Live testing

### ReDoc

Visit **http://localhost:8000/redoc** for:
- Clean, readable documentation
- Comprehensive API reference
- Search functionality
- Export to OpenAPI spec

### Postman Collection

For comprehensive API testing with Postman:

**Collection File**: `PrismQ_Web_Client.postman_collection.json` (in Client directory)

**Features**:
- All 13 API endpoints included
- Example requests and responses
- Error scenario examples
- Pre-configured variables
- Ready-to-use collection

**Quick Import**:
1. Open Postman
2. Click **Import**
3. Select `PrismQ_Web_Client.postman_collection.json`
4. Start testing!

See the [Postman Collection Guide](POSTMAN_COLLECTION.md) for detailed usage instructions.

## Rate Limiting

Currently, there is no rate limiting. For production use, consider:
- Limiting requests per IP
- Limiting concurrent runs per user
- Implementing request throttling

## Versioning

API version is included in responses:
```json
{
  "version": "1.0.0"
}
```

Future versions may use URL versioning:
```
/api/v2/modules
```

## CORS

CORS is configured to allow requests from:
- `http://localhost:5173` (default frontend dev server)
- `http://127.0.0.1:5173`

Configure additional origins in `Backend/.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## WebSocket Support

WebSocket support is planned for future versions to enable:
- Bidirectional communication
- Real-time notifications
- Advanced streaming features

Currently, Server-Sent Events (SSE) provide real-time log streaming.

## See Also

- [User Guide](USER_GUIDE.md) - Using the Web Client
- [Development Guide](DEVELOPMENT.md) - Contributing to the API
- [Configuration Reference](CONFIGURATION.md) - API configuration
- [Troubleshooting](TROUBLESHOOTING.md) - API issues

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team
