# TaskManager - Data-Driven API MVP

## Overview

This is a **truly data-driven API** where endpoints, validation rules, and actions are defined in the **database**, not hardcoded in PHP. This architecture makes it easy to:

- Add new endpoints without code changes
- Modify validation rules on-the-fly
- Update business logic through database configuration
- Deploy on shared hosting (Vedos No Limit) with just Apache + PHP + MySQL

## 🎯 Key Features

### Data-Driven Architecture

1. **Endpoints in Database** (`api_endpoints` table)
   - Define routes, methods, and actions in SQL
   - No PHP code changes needed for new endpoints
   - Enable/disable endpoints without deployment

2. **Flexible Actions** (query, insert, update, delete, custom)
   - `query`: Direct SELECT queries with JOINs, WHERE, ORDER BY
   - `insert`: INSERT records with field mapping
   - `update`: UPDATE records with conditions
   - `delete`: DELETE records safely
   - `custom`: PHP handlers for complex logic

3. **Database-Driven Validation** (`api_validations` table)
   - Define validation rules per endpoint
   - Type checking, min/max, required fields
   - Custom error messages

4. **Dynamic Parameter Resolution**
   - Template syntax: `{{query.limit}}`, `{{path.id}}`, `{{body.name}}`
   - Default values: `{{query.limit:50}}`
   - Special values: `{{NOW}}`

## 🏗️ Architecture

```
Request → index.php → EndpointRouter → ActionExecutor → Response
                           ↓              ↓
                     api_endpoints   CustomHandlers
                     api_validations
```

### Core Components

1. **index.php** - Entry point, delegates to EndpointRouter
2. **EndpointRouter.php** - Matches routes, validates requests
3. **ActionExecutor.php** - Executes database-driven actions
4. **CustomHandlers.php** - Custom business logic handlers
5. **Database tables** - Store endpoint definitions

## 📊 Database Schema

### api_endpoints
Stores endpoint definitions:
```sql
path: /tasks/:id
method: GET
action_type: query
action_config_json: {"table": "tasks", "select": [...], "where": {...}}
```

### api_validations
Stores validation rules:
```sql
endpoint_id: 1
param_name: worker_id
validation_rules_json: {"type": "string", "required": true}
```

### api_transformations
Stores data transformations (request/response):
```sql
endpoint_id: 1
transform_type: response
transform_config_json: {"field": "params", "action": "json_decode"}
```

## 🚀 Quick Start

### 1. Setup Database

#### Option A: PHP Script (Recommended for shared hosting)
```bash
php setup_database.php
```

Or open in browser: `http://your-domain.com/path/to/setup_database.php`

#### Option B: Shell Script (If you have shell access)
```bash
./setup_database.sh
```

This will:
- Create database schema (5 tables)
- Seed endpoint definitions (10+ endpoints)
- Validate setup

### 2. Configure

Update `config/config.php` with your database credentials:
```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'your_database');
define('DB_USER', 'your_username');
define('DB_PASS', 'your_password');
```

### 3. Test

```bash
# Health check
curl http://your-domain.com/api/health

# Should return:
# {"success":true,"message":"Success","data":{"status":"healthy","timestamp":...}}
```

## 📚 Endpoint Examples

### Example 1: Simple Query Endpoint

```sql
INSERT INTO api_endpoints (path, method, action_type, action_config_json) VALUES
('/users/:id', 'GET', 'query', '{
    "table": "users",
    "select": ["id", "name", "email"],
    "where": {"id": "{{path.id}}"},
    "single": true
}');
```

Usage: `GET /api/users/123`

### Example 2: List with Filters

```sql
INSERT INTO api_endpoints (path, method, action_type, action_config_json) VALUES
('/tasks', 'GET', 'query', '{
    "table": "tasks",
    "select": ["id", "status", "created_at"],
    "where_optional": {
        "status": "{{query.status}}",
        "priority": "{{query.priority}}"
    },
    "order": "created_at DESC",
    "limit": "{{query.limit:20}}",
    "offset": "{{query.offset:0}}"
}');
```

Usage: `GET /api/tasks?status=pending&limit=10`

### Example 3: Insert Endpoint

```sql
INSERT INTO api_endpoints (path, method, action_type, action_config_json) VALUES
('/tasks', 'POST', 'insert', '{
    "table": "tasks",
    "fields": {
        "title": "{{body.title}}",
        "description": "{{body.description}}",
        "status": "pending",
        "created_at": "{{NOW}}"
    }
}');
```

### Example 4: Update Endpoint

```sql
INSERT INTO api_endpoints (path, method, action_type, action_config_json) VALUES
('/tasks/:id', 'PUT', 'update', '{
    "table": "tasks",
    "set": {
        "status": "{{body.status}}",
        "updated_at": "{{NOW}}"
    },
    "where": {"id": "{{path.id}}"}
}');
```

### Example 5: Custom Handler

```sql
INSERT INTO api_endpoints (path, method, action_type, action_config_json) VALUES
('/tasks/claim', 'POST', 'custom', '{
    "handler": "task_claim",
    "required_fields": ["worker_id"]
}');
```

Then implement in `CustomHandlers.php`:
```php
public function task_claim($requestData, $config) {
    // Complex business logic here
    return ['task_id' => 123, 'claimed' => true];
}
```

## 🔧 Configuration Templates

### Query Action Template
```json
{
    "table": "table_name [t]",
    "joins": [
        {"type": "INNER", "table": "other_table o", "on": "t.id = o.table_id"}
    ],
    "select": ["t.id", "t.name", "o.value"],
    "where": {
        "t.id": "{{path.id}}"
    },
    "where_optional": {
        "t.status": "{{query.status}}",
        "t.type": "{{query.type}}"
    },
    "order": "t.created_at DESC",
    "limit": "{{query.limit:50}}",
    "offset": "{{query.offset:0}}",
    "single": false,
    "transform": {
        "json_field": "json_decode"
    }
}
```

### Insert Action Template
```json
{
    "table": "table_name",
    "fields": {
        "field1": "{{body.field1}}",
        "field2": "{{body.field2}}",
        "created_at": "{{NOW}}"
    }
}
```

### Update Action Template
```json
{
    "table": "table_name",
    "set": {
        "field1": "{{body.field1}}",
        "updated_at": "{{NOW}}"
    },
    "where": {
        "id": "{{path.id}}"
    }
}
```

### Custom Action Template
```json
{
    "handler": "handler_name",
    "required_fields": ["field1", "field2"],
    "any_custom_config": "value"
}
```

## 🔒 Security

1. **SQL Injection Protection**: All queries use prepared statements
2. **Input Validation**: Database-driven validation rules
3. **Parameter Binding**: No string concatenation in SQL
4. **Error Handling**: Generic errors in production, detailed in development

## 📈 Adding New Endpoints

### Step 1: Define Endpoint
```sql
INSERT INTO api_endpoints (path, method, description, action_type, action_config_json) 
VALUES (
    '/my-endpoint',
    'POST',
    'My custom endpoint',
    'query',
    '{"table": "my_table", "select": ["*"]}'
);
```

### Step 2: Add Validations (Optional)
```sql
INSERT INTO api_validations (endpoint_id, param_name, param_source, validation_rules_json)
SELECT id, 'my_param', 'body', '{"type": "string", "required": true}'
FROM api_endpoints 
WHERE path = '/my-endpoint' AND method = 'POST';
```

### Step 3: Test
```bash
curl -X POST http://your-domain.com/api/my-endpoint \
  -H "Content-Type: application/json" \
  -d '{"my_param": "value"}'
```

## 🎨 Template Syntax

### Path Parameters
```
"{{path.id}}"        → /tasks/123 → "123"
"{{path.name}}"      → /users/john → "john"
```

### Query Parameters
```
"{{query.limit}}"    → ?limit=10 → "10"
"{{query.status}}"   → ?status=active → "active"
```

### Body Parameters
```
"{{body.title}}"     → {"title": "Test"} → "Test"
"{{body.user.name}}" → {"user": {"name": "John"}} → "John"
```

### Default Values
```
"{{query.limit:50}}" → No limit param → "50"
"{{query.limit:50}}" → ?limit=10 → "10"
```

### Special Values
```
"{{NOW}}"            → Current Unix timestamp
```

## 🐛 Debugging

Enable debug mode in `config/config.php`:
```php
define('DEBUG_MODE', true);
```

Check endpoint definitions:
```sql
SELECT * FROM api_endpoints WHERE is_active = TRUE;
```

Check validation rules:
```sql
SELECT e.path, e.method, v.param_name, v.validation_rules_json
FROM api_validations v
JOIN api_endpoints e ON v.endpoint_id = e.id;
```

## 📝 Comparison: Hardcoded vs Data-Driven

### Hardcoded Approach (Traditional)
```php
// Need PHP code change for each new endpoint
if ($path === '/tasks' && $method === 'GET') {
    $controller = new TaskController();
    $controller->list();
}
```

**Problems:**
- Code changes for new endpoints
- Requires deployment
- Can't enable/disable features dynamically
- Harder to maintain

### Data-Driven Approach (This MVP)
```sql
-- Just add a database row
INSERT INTO api_endpoints (path, method, action_type, action_config_json)
VALUES ('/tasks', 'GET', 'query', '{"table": "tasks", ...}');
```

**Benefits:**
- No code changes
- No deployment needed
- Enable/disable via SQL
- Easy to modify behavior
- Perfect for shared hosting

## 🎯 Use Cases

1. **Rapid Prototyping**: Add endpoints in minutes via SQL
2. **Multi-tenant**: Different endpoints per tenant via database
3. **A/B Testing**: Enable/disable endpoints by `is_active` flag
4. **API Versioning**: Multiple endpoints for same resource
5. **Shared Hosting**: No code deployment, just database updates

## 📦 Files Structure

```
TaskManager/
├── api/
│   ├── index.php              # Entry point
│   ├── EndpointRouter.php     # Route matching
│   ├── ActionExecutor.php     # Action execution
│   ├── CustomHandlers.php     # Custom logic
│   ├── ApiResponse.php        # Response helpers
│   ├── JsonSchemaValidator.php
│   └── .htaccess              # URL rewriting
├── config/
│   ├── config.example.php
│   └── config.php             # Your credentials (gitignored)
├── database/
│   ├── schema.sql             # Database schema
│   └── seed_endpoints.sql     # Default endpoints
├── setup_database.php         # PHP setup script
└── setup_database.sh          # Shell setup script
```

## 🚀 Deployment to Vedos/Wedos

1. Upload all files via FTP
2. Run `setup_database.php` from browser
3. Update `config/config.php` with database credentials
4. Test: Visit `http://your-domain.com/api/health`
5. Done! Add endpoints via phpMyAdmin

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
