# ISSUE-TASKMANAGER-002: Core API Endpoints

## Status
🟢 IN PROGRESS

## Component
Backend/TaskManager/api

## Type
Feature

## Priority
High

## Description
Implement the core REST API endpoints for task type management and task operations. This includes registration, creation, claiming, completion, and status retrieval.

## Problem Statement
The TaskManager needs a complete REST API that workers and clients can use to:
- Register task types with JSON schemas
- Create tasks with parameter validation
- Claim tasks for processing
- Complete tasks with results
- Query task status
- List tasks and task types

All endpoints must return JSON responses with `Cache-Control: no-store` headers to prevent caching issues on shared hosting.

## Solution
Create a PHP-based REST API with clean URL routing via .htaccess:

**API Router** (`index.php`):
- Parse incoming requests
- Route to appropriate controllers
- Handle OPTIONS for CORS
- Global error handling

**Controllers**:
1. `TaskTypeController`: Task type registration and retrieval
2. `TaskController`: Task lifecycle management
3. `ApiResponse`: Standardized response formatting

**Helper Classes**:
- `JsonSchemaValidator`: Basic JSON schema validation
- `Database`: Database connection management

## Acceptance Criteria
- [x] API router created with request parsing
- [x] Clean URL routing via .htaccess
- [x] TaskTypeController implemented:
  - [x] POST /task-types/register
  - [x] GET /task-types/{name}
  - [x] GET /task-types
- [x] TaskController implemented:
  - [x] POST /tasks
  - [x] POST /tasks/claim
  - [x] POST /tasks/{id}/complete
  - [x] GET /tasks/{id}
  - [x] GET /tasks
- [x] ApiResponse helper with standard formatting
- [x] All responses include Cache-Control: no-store
- [x] CORS headers for cross-origin requests
- [x] Error handling with appropriate HTTP codes
- [x] Request body parsing and validation

## Dependencies
- ISSUE-TASKMANAGER-001 (Database schema) ✅

## Related Issues
- ISSUE-TASKMANAGER-003 (Validation and deduplication)
- ISSUE-TASKMANAGER-004 (Documentation)

## Implementation Details

### Endpoint Specifications

**Task Type Endpoints**:
1. `POST /task-types/register`: Register or update task type
   - Input: name, version, param_schema
   - Output: task type ID, created/updated flag
   - Validation: JSON schema structure check

2. `GET /task-types/{name}`: Get task type details
   - Input: name (URL parameter)
   - Output: Full task type with parsed schema

3. `GET /task-types`: List all task types
   - Input: active_only (optional query param)
   - Output: Array of task types

**Task Endpoints**:
1. `POST /tasks`: Create new task
   - Input: type, params
   - Validation: Against task type schema
   - Deduplication: Check dedupe_key
   - Output: Task ID, status, dedupe_key

2. `POST /tasks/claim`: Claim task for processing
   - Input: worker_id, type_pattern (optional)
   - Transaction: Lock row while claiming
   - Timeout recovery: Reclaim stuck tasks
   - Output: Task details with params

3. `POST /tasks/{id}/complete`: Complete task
   - Input: worker_id, success, result/error
   - Validation: Worker ID matches claimer
   - Retry logic: Reset to pending if under max attempts
   - Output: Final task status

4. `GET /tasks/{id}`: Get task status
   - Output: Complete task details including params, result, history

5. `GET /tasks`: List tasks with filters
   - Input: status, type, limit, offset
   - Output: Paginated task list

### HTTP Status Codes
- 200 OK: Success
- 201 Created: Resource created
- 400 Bad Request: Validation failed
- 403 Forbidden: Authorization failed
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server error

### Response Format
All responses follow:
```json
{
  "success": true/false,
  "message": "...",
  "data": {...},
  "timestamp": 1234567890
}
```

## Testing
Manual testing with curl:

```bash
# Health check
curl http://localhost/api/health

# Register task type
curl -X POST http://localhost/api/task-types/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test.Simple","version":"1.0.0","param_schema":{"type":"object","properties":{"msg":{"type":"string"}},"required":["msg"]}}'

# Create task
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"Test.Simple","params":{"msg":"Hello"}}'

# Claim task
curl -X POST http://localhost/api/tasks/claim \
  -H "Content-Type: application/json" \
  -d '{"worker_id":"worker-1"}'

# Complete task
curl -X POST http://localhost/api/tasks/1/complete \
  -H "Content-Type: application/json" \
  -d '{"worker_id":"worker-1","success":true,"result":{"status":"done"}}'

# Get task status
curl http://localhost/api/tasks/1

# List tasks
curl http://localhost/api/tasks?status=pending&limit=5
```

## Files Created
- `/Backend/TaskManager/api/index.php`
- `/Backend/TaskManager/api/.htaccess`
- `/Backend/TaskManager/api/ApiResponse.php`
- `/Backend/TaskManager/api/TaskTypeController.php`
- `/Backend/TaskManager/api/TaskController.php`
- `/Backend/TaskManager/api/JsonSchemaValidator.php`

## Notes
- .htaccess requires mod_rewrite enabled on Apache
- RewriteBase may need adjustment based on deployment path
- Transaction handling in claim endpoint prevents race conditions
- Worker ID validation in complete endpoint prevents unauthorized completions
- Pagination defaults: limit=50, max=100
- Task claim uses FOR UPDATE lock to prevent concurrent claims

## Security Considerations
- All database queries use prepared statements
- Input validation on all endpoints
- Worker ID verification on task completion
- JSON decode error handling
- SQL injection prevention via PDO
- XSS prevention by not echoing raw input
- Consider adding API key authentication for production

## Performance Considerations
- Database indexes on frequently queried columns
- Pagination to limit response size
- Transaction scoping minimized
- Connection pooling via singleton pattern
- Query optimization with proper WHERE clauses
