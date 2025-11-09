# TaskManager - Lightweight PHP Task Queue

A simple, on-demand task management system designed to run on shared hosting (e.g., Vedos) using only MySQL and PHP. No long-running processes required - all operations are triggered via HTTP requests.

## 🎯 Overview

TaskManager provides a REST API for managing tasks with parameter validation, deduplication, and worker coordination. It's designed for environments where you can't run background processes but need task queue functionality.

### Key Features

- ✅ **No background processes** - Pure on-demand HTTP architecture
- ✅ **JSON Schema validation** - Task parameters validated against schemas
- ✅ **Automatic deduplication** - Prevents duplicate task creation
- ✅ **Worker coordination** - Claim/complete workflow with timeout handling
- ✅ **Retry logic** - Failed tasks can be automatically retried
- ✅ **Task history tracking** - Optional audit trail of task status changes
- ✅ **Type-based organization** - Tasks organized by TaskType (e.g., `PrismQ.Script.Generate`)
- ✅ **Cache prevention** - All responses include `Cache-Control: no-store`
- ✅ **Shared hosting friendly** - Runs on basic PHP + MySQL hosting

## 📋 Requirements

- PHP 8.0 or higher
- MySQL 5.7+ or MariaDB 10.2+
- Apache with mod_rewrite (for clean URLs)
- PDO MySQL extension

## 📚 Documentation

**Complete documentation is available in the `docs/` folder:**

- **[Data-Driven Architecture](docs/DATA_DRIVEN_ARCHITECTURE.md)** - Learn how endpoints are defined in the database, not code. Includes detailed guides on all action types (query, insert, update, delete, custom), template syntax, validation system, and how to add new endpoints without code changes.

- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation with all endpoints, request/response examples, and curl commands.

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Step-by-step guide for deploying to Vedos or any shared hosting, including database setup, configuration, and troubleshooting.

- **[Hosting Information](docs/HOSTING_INFO.md)** - Details about the Vedos/Wedos hosting account and resources.

## 🚀 Quick Start

### Step 0: Check Your Environment

**Before deployment, verify your server meets all requirements:**

```bash
# Upload check_setup.php to your server, then run:
php src/check_setup.php

# Or access via web browser:
https://your-domain.com/path/src/check_setup.php
```

The environment check will validate:
- PHP version and required extensions
- File and directory permissions
- Apache modules and .htaccess support
- MySQL/MariaDB availability
- Disk space and memory limits
- cURL and OpenSSL functionality

**⚠️ Important:** Fix any critical issues before proceeding with deployment!

### Automated Deployment (Recommended)

**Use the automated deployment scripts for easy setup:**

#### Option 1: Update Deploy Script First (Recommended)

```bash
# Step 1: Update deploy.php to the latest version
php src/deploy-deploy.php

# Step 2: Run the updated deployment script
php src/deploy.php
```

**Web browser method:**
1. Upload both `src/deploy-deploy.php` and `src/deploy.php` to your server
2. Access `https://your-domain.com/path/src/deploy-deploy.php` in your browser
3. Click "Continue to Deploy" after the update completes
4. Follow the deployment wizard

#### Option 2: Direct Deployment

1. Upload `deploy.php` to your server
2. Open in browser: `https://your-domain.com/path/deploy.php`
3. Enter admin password and database credentials
4. The script will automatically:
   - Download all files from GitHub
   - Set up the database
   - Configure the application
   - Validate the installation

**Why use deploy-deploy.php?**
- Ensures you always have the latest deployment script
- Gets bug fixes and improvements automatically
- Single responsibility: just updates deploy.php
- Recommended before each deployment

**📖 See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions**

### Manual Deployment

If you prefer manual setup:

#### 1. Database Setup

```bash
# Import the database schema
mysql -u username -p database_name < src/database/schema.sql
```

#### 2. Configuration

```bash
# Copy the example config and edit with your database credentials
cp src/config/config.example.php src/config/config.php
nano src/config/config.php
```

Edit `src/config/config.php`:
```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'your_database');
define('DB_USER', 'your_username');
define('DB_PASS', 'your_password');
```

#### 3. Deploy to Server

Upload the `TaskManager` directory to your web server. The API should be accessible at:
```
https://your-domain.com/api/
```

#### 4. Test the Installation

```bash
# Health check
curl https://your-domain.com/api/health

# View interactive API documentation
# Open in browser: https://your-domain.com/api/docs/
```

**Production Example:**
- API: `https://api.prismq.nomoos.cz/api/`
- Swagger UI: `https://api.prismq.nomoos.cz/api/docs/`

## 📚 API Documentation

### Interactive Documentation (Swagger UI)

The TaskManager API provides interactive documentation via Swagger UI:

**Access URL:** `https://your-domain.com/api/docs/`

Features:
- ✅ Browse all available endpoints
- ✅ View request/response schemas
- ✅ Try out API calls directly from the browser
- ✅ View authentication requirements
- ✅ Download OpenAPI specification

**Example for production:** `https://api.prismq.nomoos.cz/api/docs/`

### Task Type Management

#### Register/Update Task Type
```http
POST /api/task-types/register
Content-Type: application/json

{
  "name": "PrismQ.Script.Generate",
  "version": "1.0.0",
  "param_schema": {
    "type": "object",
    "properties": {
      "topic": {"type": "string", "minLength": 1},
      "style": {"type": "string", "enum": ["formal", "casual", "technical"]},
      "length": {"type": "integer", "minimum": 100, "maximum": 5000}
    },
    "required": ["topic", "style"]
  }
}
```

#### Get Task Type
```http
GET /api/task-types/{name}
```

#### List All Task Types
```http
GET /api/task-types?active_only=true
```

### Task Management

#### Create Task
```http
POST /api/tasks
Content-Type: application/json

{
  "type": "PrismQ.Script.Generate",
  "params": {
    "topic": "AI in Healthcare",
    "style": "formal",
    "length": 1500
  },
  "priority": 10  // Optional: task priority (default: 0, higher = more important)
}
```

Response:
```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "id": 123,
    "type": "PrismQ.Script.Generate",
    "status": "pending",
    "priority": 10,
    "dedupe_key": "abc123..."
  }
}
```

#### Claim Task (Worker)
```http
POST /api/tasks/claim
Content-Type: application/json

{
  "worker_id": "worker-001",
  "task_type_id": 5,                    // Required: specific task type ID
  "type_pattern": "PrismQ.Script.%",    // Optional: filter by type pattern
  "sort_by": "priority",                // Optional: created_at (default), priority, id, attempts
  "sort_order": "DESC"                  // Optional: ASC (default) or DESC
}
```

**Sorting Examples:**
- FIFO (First In, First Out): `"sort_by": "created_at", "sort_order": "ASC"` (default)
- LIFO (Last In, First Out): `"sort_by": "created_at", "sort_order": "DESC"`
- Highest Priority First: `"sort_by": "priority", "sort_order": "DESC"`
- Lowest Attempts First: `"sort_by": "attempts", "sort_order": "ASC"`

Response:
```json
{
  "success": true,
  "message": "Task claimed successfully",
  "data": {
    "id": 123,
    "type": "PrismQ.Script.Generate",
    "params": {
      "topic": "AI in Healthcare",
      "style": "formal",
      "length": 1500
    },
    "attempts": 1,
    "priority": 10
  }
}
```

#### Complete Task (Worker)
```http
POST /api/tasks/{id}/complete
Content-Type: application/json

{
  "worker_id": "worker-001",
  "success": true,
  "result": {
    "output": "Generated script content...",
    "word_count": 1487
  }
}
```

Or for failures:
```json
{
  "worker_id": "worker-001",
  "success": false,
  "error": "API rate limit exceeded"
}
```

#### Get Task Status
```http
GET /api/tasks/{id}
```

#### List Tasks
```http
GET /api/tasks?status=pending&type=PrismQ.Script.%&limit=10&offset=0
```

## 🔧 Architecture

### Database Schema

**task_types**: Stores task type definitions with JSON schemas
- `name`: Unique task type identifier (e.g., `PrismQ.Script.Generate`)
- `version`: Schema version
- `param_schema_json`: JSON Schema for parameter validation
- `is_active`: Whether this type accepts new tasks

**tasks**: Stores individual task instances
- `type_id`: Reference to task_types
- `status`: pending | claimed | completed | failed
- `params_json`: Task parameters (validated against schema)
- `dedupe_key`: SHA-256 hash for deduplication
- `priority`: Task priority (higher values = higher priority, default: 0)
- `result_json`: Task result when completed
- `attempts`: Retry counter
- `claimed_by`: Worker ID that claimed the task
- `claimed_at`: Claim timestamp (for timeout detection)

**task_history**: Optional audit trail
- Tracks all status changes for debugging

### Task Lifecycle

```
1. Task Created → status: pending
2. Worker Claims → status: claimed, claimed_at set
3. Worker Completes:
   - Success → status: completed
   - Failure → status: failed (or pending if retries available)
4. Timeout → status: pending (released for reclaim)
```

### Deduplication

Tasks are deduplicated using a SHA-256 hash of `type + params`. If you create a task with identical type and parameters, you'll get the existing task ID instead of creating a duplicate.

### Retry Logic

Failed tasks are automatically returned to `pending` status if:
- `attempts < MAX_TASK_ATTEMPTS` (default: 3)

This allows workers to retry failed tasks up to the configured limit.

### Claim Timeout

Tasks that remain in `claimed` status for longer than `TASK_CLAIM_TIMEOUT` (default: 300 seconds / 5 minutes) are automatically made available for reclaiming by the next worker.

## 👨‍💻 Worker Implementation

Workers can be implemented in any language. Here's a simple PHP example:

```php
<?php
// Simple worker loop
while (true) {
    // Try to claim a task
    $response = apiPost('/tasks/claim', [
        'worker_id' => 'worker-001',
        'type_pattern' => 'PrismQ.Script.%'
    ]);
    
    if ($response['success']) {
        $task = $response['data'];
        
        try {
            // Process the task
            $result = processTask($task['params']);
            
            // Mark as completed
            apiPost("/tasks/{$task['id']}/complete", [
                'worker_id' => 'worker-001',
                'success' => true,
                'result' => $result
            ]);
        } catch (Exception $e) {
            // Mark as failed
            apiPost("/tasks/{$task['id']}/complete", [
                'worker_id' => 'worker-001',
                'success' => false,
                'error' => $e->getMessage()
            ]);
        }
    } else {
        // No tasks available, wait before trying again
        sleep(10);
    }
}
```

## 🔒 Security Considerations

1. **Database Access**: Use dedicated MySQL user with minimal privileges
2. **Input Validation**: All inputs are validated and sanitized
3. **SQL Injection**: All queries use prepared statements
4. **API Authentication**: Consider adding API key authentication for production
5. **HTTPS Only**: Always use HTTPS in production
6. **Error Logging**: Errors are logged but not exposed in API responses

## 📊 Monitoring

### Health Check
```bash
curl https://your-domain.com/api/health
```

### Task Statistics
```bash
# Count pending tasks
mysql> SELECT COUNT(*) FROM tasks WHERE status = 'pending';

# Count by status
mysql> SELECT status, COUNT(*) FROM tasks GROUP BY status;

# Failed tasks
mysql> SELECT id, type_id, error_message, attempts 
       FROM tasks WHERE status = 'failed';
```

## 🐛 Troubleshooting

### Common Issues

**Problem**: "Database connection failed"
- Check database credentials in `src/config/config.php`
- Verify MySQL service is running
- Check firewall/networking settings

**Problem**: "Route not found" 
- Verify `.htaccess` file is present in `src/api/` directory
- Check that mod_rewrite is enabled on Apache
- Review Apache error logs

**Problem**: Tasks not being claimed
- Check if `TASK_CLAIM_TIMEOUT` is too low
- Verify worker_id matches when claiming/completing
- Check for database connection issues in workers

**Problem**: Duplicate tasks despite deduplication
- Verify parameters are identical (order matters in JSON)
- Check dedupe_key generation

## 📄 Configuration Options

Edit `src/config/config.php`:

```php
// Task claim timeout (seconds) - how long before claimed task can be reclaimed
define('TASK_CLAIM_TIMEOUT', 300);  // 5 minutes

// Maximum retry attempts for failed tasks
define('MAX_TASK_ATTEMPTS', 3);

// Enable task history tracking (audit trail)
define('ENABLE_TASK_HISTORY', true);

// Enable JSON schema validation
define('ENABLE_SCHEMA_VALIDATION', true);
```

## 📝 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ

## 🔗 Related

- [PrismQ.Client](../../) - Main client application
- [Data-Driven Architecture](docs/DATA_DRIVEN_ARCHITECTURE.md) - **Complete guide to the data-driven API architecture**
- [Custom Handlers Analysis](docs/CUSTOM_HANDLERS_ANALYSIS.md) - **Evaluation of custom handlers vs data-driven actions**
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - **Automated deployment script documentation**
- [API Reference](docs/API_REFERENCE.md) - Detailed API documentation
- [Hosting Information](docs/HOSTING_INFO.md) - Vedos/Wedos account details and resource allocation

## 📋 Project Management

- [Project Plan](_meta/PROJECT_PLAN.md) - Comprehensive project roadmap and timeline
- [Issue Tracking](_meta/issues/INDEX.md) - All project issues organized by worker
- [Parallelization Matrix](_meta/PARALLELIZATION_MATRIX.md) - Worker coordination and dependencies
- [Organization Summary](_meta/ORGANIZATION_SUMMARY.md) - Project structure and implementation details
- [Worker03 Implementation Summary](WORKER03_IMPLEMENTATION_SUMMARY.md) - Custom Handlers evaluation and approval
