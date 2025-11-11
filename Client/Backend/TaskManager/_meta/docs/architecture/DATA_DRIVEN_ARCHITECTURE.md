# Data-Driven Architecture

## Overview

TaskManager implements a **truly data-driven API architecture** where endpoints, validation rules, and actions are defined in the **database**, not hardcoded in PHP. This revolutionary approach enables unprecedented flexibility and maintainability.

## 🎯 Core Principle

Traditional APIs require code changes and deployment for every new endpoint. TaskManager eliminates this bottleneck by storing endpoint definitions in the database, allowing you to:

- ✅ **Add endpoints via SQL** - No code changes required
- ✅ **Modify validation rules dynamically** - Update database, not code
- ✅ **Enable/disable endpoints** - Toggle `is_active` flag
- ✅ **Perfect for shared hosting** - No framework dependencies or background processes

## 🏗️ Architecture Components

### 1. Database Tables

#### api_endpoints
Stores complete endpoint definitions:
```sql
CREATE TABLE api_endpoints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path VARCHAR(255) NOT NULL,           -- e.g., /tasks/:id
    method ENUM('GET', 'POST', 'PUT', 'DELETE', 'PATCH'),
    description TEXT,
    action_type VARCHAR(100) NOT NULL,    -- query, insert, update, delete, custom
    action_config_json TEXT NOT NULL,     -- JSON configuration for the action
    auth_required BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE KEY unique_route (path, method)
);
```

#### api_validations
Stores validation rules per endpoint:
```sql
CREATE TABLE api_validations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint_id INT NOT NULL,
    param_name VARCHAR(100) NOT NULL,
    param_source ENUM('body', 'query', 'path', 'header'),
    validation_rules_json TEXT NOT NULL,  -- JSON validation configuration
    error_message VARCHAR(255),
    FOREIGN KEY (endpoint_id) REFERENCES api_endpoints(id)
);
```

#### api_transformations
Stores data transformation rules:
```sql
CREATE TABLE api_transformations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint_id INT NOT NULL,
    transform_type ENUM('request', 'response'),
    transform_config_json TEXT NOT NULL,
    execution_order INT DEFAULT 0,
    FOREIGN KEY (endpoint_id) REFERENCES api_endpoints(id)
);
```

### 2. PHP Components

#### EndpointRouter.php
- Loads endpoint definitions from database
- Matches incoming requests to endpoints
- Validates requests against database-defined rules
- Routes to ActionExecutor

#### ActionExecutor.php
- Executes actions based on database configuration
- Supports 5 action types:
  - `query`: SELECT operations with JOINs, filtering, sorting
  - `insert`: INSERT operations with field mapping
  - `update`: UPDATE operations with conditions
  - `delete`: DELETE operations with safety checks
  - `custom`: Custom PHP handlers for complex logic

#### CustomHandlers.php
- Implements complex business logic for custom actions
- Referenced by `action_type: custom` in endpoint definitions

## 📋 Request Flow

```
1. HTTP Request arrives at index.php
         ↓
2. EndpointRouter loads endpoint from database
         ↓
3. EndpointRouter validates request (database-defined rules)
         ↓
4. ActionExecutor reads action_config_json
         ↓
5. ActionExecutor executes appropriate action
         ↓
6. Response returned with data transformations applied
```

## 🎨 Action Types Explained

### Query Action
Executes SELECT queries with full SQL capabilities:

```json
{
    "table": "tasks t",
    "joins": [
        {
            "type": "INNER",
            "table": "task_types tt",
            "on": "t.type_id = tt.id"
        }
    ],
    "select": ["t.id", "t.status", "tt.name as type_name"],
    "where": {
        "t.id": "{{path.id}}"
    },
    "where_optional": {
        "t.status": "{{query.status}}",
        "tt.name": "{{query.type}}"
    },
    "order": "t.created_at DESC",
    "limit": "{{query.limit:50}}",
    "offset": "{{query.offset:0}}",
    "single": false,
    "transform": {
        "params_json": "json_decode"
    }
}
```

**Features:**
- Complex JOINs between tables
- Required and optional WHERE conditions
- Dynamic ORDER BY and pagination
- Automatic JSON decoding for JSON fields
- Path, query, and body parameter substitution

### Insert Action
Inserts records with field mapping:

```json
{
    "table": "tasks",
    "fields": {
        "type_id": "{{body.type_id}}",
        "status": "pending",
        "params_json": "{{body.params}}",
        "dedupe_key": "{{body.dedupe_key}}",
        "created_at": "{{NOW}}"
    },
    "return_insert_id": true
}
```

**Features:**
- Field mapping from request body
- Static field values (e.g., `status: "pending"`)
- Special values (e.g., `{{NOW}}` for current timestamp)
- Returns inserted record ID

### Update Action
Updates records with conditions:

```json
{
    "table": "tasks",
    "set": {
        "status": "{{body.status}}",
        "result_json": "{{body.result}}",
        "completed_at": "{{NOW}}"
    },
    "where": {
        "id": "{{path.id}}",
        "status": "claimed"
    }
}
```

**Features:**
- Multiple field updates
- Multiple WHERE conditions (all must match)
- Safe updates (won't update if conditions don't match)

### Delete Action
Soft or hard deletes with conditions:

```json
{
    "table": "tasks",
    "where": {
        "id": "{{path.id}}",
        "status": "failed"
    },
    "soft_delete": false
}
```

**Features:**
- Conditional deletion (safety)
- Optional soft delete support
- Returns affected row count

### Custom Action
Delegates to PHP handler for complex logic:

```json
{
    "handler": "task_claim",
    "required_fields": ["worker_id"],
    "config": {
        "max_attempts": 3,
        "claim_timeout": 300
    }
}
```

**Features:**
- Full access to request data
- Custom business logic in PHP
- Transactional operations
- Complex queries and multi-step operations

## 🔧 Template Syntax

### Parameter Resolution

The system uses a powerful template syntax for dynamic parameter substitution:

#### Path Parameters
```
"{{path.id}}"        → /tasks/123 → "123"
"{{path.name}}"      → /users/john → "john"
```

#### Query Parameters
```
"{{query.limit}}"    → ?limit=10 → "10"
"{{query.status}}"   → ?status=active → "active"
```

#### Body Parameters
```
"{{body.title}}"     → {"title": "Test"} → "Test"
"{{body.user.name}}" → {"user": {"name": "John"}} → "John"
```

#### Default Values
```
"{{query.limit:50}}" → No limit param → "50"
"{{query.limit:50}}" → ?limit=10 → "10"
```

#### Special Values
```
"{{NOW}}"            → Current Unix timestamp
```

## 🛡️ Validation System

Validation rules are defined per-endpoint in the `api_validations` table:

```sql
INSERT INTO api_validations (endpoint_id, param_name, param_source, validation_rules_json)
VALUES (
    1,
    'worker_id',
    'body',
    '{
        "type": "string",
        "required": true,
        "minLength": 1,
        "maxLength": 255
    }'
);
```

**Supported Validation Rules:**
- `type`: string, integer, number, boolean, array, object
- `required`: true/false
- `minLength`, `maxLength`: For strings
- `minimum`, `maximum`: For numbers
- `enum`: Array of allowed values
- `pattern`: Regular expression
- `format`: email, url, date, etc.

## 🚀 Adding New Endpoints

### Step 1: Define Endpoint

```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json, is_active)
VALUES (
    '/tasks/:id',
    'GET',
    'Get task by ID',
    'query',
    '{
        "table": "tasks",
        "select": ["id", "status", "params_json"],
        "where": {"id": "{{path.id}}"},
        "single": true,
        "transform": {"params_json": "json_decode"}
    }',
    TRUE
);
```

### Step 2: Add Validations (Optional)

```sql
-- Validate the ID parameter
INSERT INTO api_validations (endpoint_id, param_name, param_source, validation_rules_json)
SELECT 
    id,
    'id',
    'path',
    '{"type": "integer", "minimum": 1}'
FROM api_endpoints
WHERE path = '/tasks/:id' AND method = 'GET';
```

### Step 3: Test

```bash
curl https://your-domain.com/api/tasks/123
```

That's it! No code changes, no deployment needed.

## 📊 Comparison: Traditional vs Data-Driven

### Traditional Hardcoded API

```php
// Adding new endpoint requires code changes
class TaskController {
    public function getTask($id) {
        // Hardcoded query
        $stmt = $db->prepare("SELECT * FROM tasks WHERE id = ?");
        $stmt->execute([$id]);
        return $stmt->fetch();
    }
}

// Route configuration
$router->get('/tasks/{id}', [TaskController::class, 'getTask']);
```

**Problems:**
- Code changes for every new endpoint
- Requires testing and deployment
- Tight coupling between routes and controllers
- Can't modify behavior without code updates
- Merge conflicts when multiple developers add routes

### Data-Driven API

```sql
-- Adding new endpoint is just a database INSERT
INSERT INTO api_endpoints (path, method, action_type, action_config_json)
VALUES (
    '/tasks/:id',
    'GET',
    'query',
    '{"table": "tasks", "select": ["*"], "where": {"id": "{{path.id}}"}}'
);
```

**Benefits:**
- ✅ No code changes required
- ✅ No deployment needed (just database update)
- ✅ Enable/disable endpoints dynamically
- ✅ Modify endpoint behavior via SQL UPDATE
- ✅ No merge conflicts (database handles concurrency)
- ✅ Perfect for shared hosting
- ✅ Rapid prototyping and iteration
- ✅ A/B testing by toggling `is_active`
- ✅ Multi-tenant support (different endpoints per tenant)

## 🎯 Use Cases

### 1. Rapid Prototyping
Add and test new endpoints in minutes without code deployment:
```sql
INSERT INTO api_endpoints (path, method, action_type, action_config_json)
VALUES ('/prototype/new-feature', 'GET', 'query', '{"table": "data", "select": ["*"]}');
```

### 2. A/B Testing
Enable/disable endpoints for testing:
```sql
-- Enable experimental endpoint
UPDATE api_endpoints SET is_active = TRUE WHERE path = '/v2/new-algo';

-- Disable after testing
UPDATE api_endpoints SET is_active = FALSE WHERE path = '/v2/new-algo';
```

### 3. Multi-Tenant
Different endpoints per tenant:
```sql
-- Tenant-specific endpoints
INSERT INTO api_endpoints (path, method, action_type, action_config_json)
VALUES ('/tenant/acme/data', 'GET', 'query', '{"table": "tenant_data", "where": {"tenant_id": 123}}');
```

### 4. API Versioning
Multiple versions of same endpoint:
```sql
-- v1 endpoint
INSERT INTO api_endpoints (path, method, action_type, action_config_json)
VALUES ('/v1/tasks', 'GET', 'query', '{"table": "tasks", "select": ["id", "status"]}');

-- v2 endpoint with more fields
INSERT INTO api_endpoints (path, method, action_type, action_config_json)
VALUES ('/v2/tasks', 'GET', 'query', '{"table": "tasks", "select": ["id", "status", "params_json"]}');
```

### 5. Dynamic Business Rules
Update validation rules without code changes:
```sql
-- Tighten validation rules
UPDATE api_validations 
SET validation_rules_json = '{"type": "string", "minLength": 10, "maxLength": 100}'
WHERE param_name = 'description';
```

## 🔒 Security Considerations

### SQL Injection Prevention
- ✅ All queries use PDO prepared statements
- ✅ Parameter binding for all user inputs
- ✅ No string concatenation in SQL queries
- ✅ ActionExecutor validates and sanitizes all parameters

### Input Validation
- ✅ Database-driven validation rules
- ✅ Type checking enforced
- ✅ Range and format validation
- ✅ Custom error messages

### Access Control
- ✅ `auth_required` flag per endpoint
- ✅ `is_active` flag to disable endpoints
- ✅ IP whitelisting support (future)
- ✅ Rate limiting support (future)

## 📈 Performance Considerations

### Endpoint Caching
The system caches endpoint definitions in memory to avoid repeated database lookups:
- Endpoints loaded once per request cycle
- Indexed on `path` and `method` for fast lookups
- Cache invalidated automatically on endpoint updates

### Query Optimization
- Use indexes on frequently queried fields
- Limit result sets with `limit` and `offset`
- Use `select` to retrieve only needed fields
- Optimize JOINs for large tables

### Database Indexing
Recommended indexes:
```sql
-- For endpoint lookups
CREATE INDEX idx_path ON api_endpoints(path);
CREATE INDEX idx_active ON api_endpoints(is_active);

-- For validation lookups
CREATE INDEX idx_endpoint ON api_validations(endpoint_id);
```

## 🧪 Testing Endpoints

### Manual Testing
```bash
# Test GET endpoint
curl https://your-domain.com/api/tasks/123

# Test POST endpoint
curl -X POST https://your-domain.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type_id": 1, "params": {"key": "value"}}'

# Test with query parameters
curl "https://your-domain.com/api/tasks?status=pending&limit=10"
```

### Validation Testing
```bash
# Test validation error (missing required field)
curl -X POST https://your-domain.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{}' \
  | jq

# Expected: {"success": false, "error": "Validation failed", ...}
```

### Debugging
Enable debug mode in `config/config.php`:
```php
define('DEBUG_MODE', true);
```

This will return detailed error messages including:
- SQL queries executed
- Parameter values
- Validation failures
- Exception stack traces

## 📚 Related Documentation

- **[API Reference](API_REFERENCE.md)** - Complete endpoint documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Deploy to shared hosting
- **[README](../README.md)** - Quick start and overview

## 🎓 Learning Path

1. **Start Simple**: Create a basic GET endpoint with query action
2. **Add Validation**: Define validation rules for parameters
3. **Try Insert/Update**: Create POST/PUT endpoints
4. **Complex Queries**: Use JOINs and transformations
5. **Custom Handlers**: Implement complex business logic

## 💡 Best Practices

### Endpoint Design
- Use RESTful conventions for paths and methods
- Group related endpoints by prefix (e.g., `/tasks/*`)
- Use descriptive endpoint descriptions
- Set appropriate `auth_required` flags

### Action Configuration
- Use `where_optional` for filters that may or may not be present
- Set reasonable default limits (e.g., `limit:50`)
- Use `single: true` for endpoints that return one record
- Transform JSON fields with `"json_decode"` for automatic parsing

### Validation Rules
- Always require critical parameters
- Use appropriate type checking
- Set reasonable min/max constraints
- Provide clear error messages

### Security
- Set `auth_required: true` for sensitive endpoints
- Use `is_active: false` to disable endpoints in development
- Never expose sensitive data in error messages
- Use HTTPS in production

## 🔮 Future Enhancements

Planned features for the data-driven architecture:

- [ ] Response caching with TTL
- [ ] Rate limiting per endpoint
- [ ] API key authentication
- [ ] Webhook support
- [ ] GraphQL-style field selection
- [ ] Bulk operations
- [ ] Async job scheduling
- [ ] Audit logging for all endpoint calls
- [ ] OpenAPI/Swagger spec generation from database
- [ ] Web UI for managing endpoints

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
