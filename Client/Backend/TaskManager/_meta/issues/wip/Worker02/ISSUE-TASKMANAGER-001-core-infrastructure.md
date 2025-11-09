# ISSUE-TASKMANAGER-001: Core Infrastructure and Database Schema

## Status
🟢 IN PROGRESS

## Component
Backend/TaskManager/database

## Type
Feature

## Priority
High

## Description
Create the foundational database schema and configuration infrastructure for the TaskManager system. This includes the MySQL/MariaDB tables for task types, tasks, and task history.

## Problem Statement
The TaskManager needs a robust database schema to store task definitions, task instances, and their execution history. The schema must support:
- Task type registration with JSON schema validation
- Task creation with parameter validation
- Task deduplication using hash keys
- Task lifecycle management (pending → claimed → completed/failed)
- Retry logic with attempt tracking
- Optional history logging for audit trails

## Solution
Create SQL schema with three main tables:
1. **task_types**: Store task type definitions with JSON schemas
2. **tasks**: Store individual task instances with status tracking
3. **task_history**: Optional audit trail for task status changes

Database features:
- Foreign key relationships for data integrity
- Indexes for query performance
- UTF-8 support for international content
- Timestamps for tracking task lifecycle
- Unique constraints for deduplication

Configuration:
- Example configuration file with all settings
- Database connection singleton pattern
- Configurable timeouts and retry limits

## Acceptance Criteria
- [x] SQL schema file created with all tables
- [x] Foreign key relationships defined
- [x] Appropriate indexes added for performance
- [x] Example configuration file created
- [x] Database connection class implemented
- [x] Configuration supports all required settings:
  - Database credentials
  - Task claim timeout
  - Max retry attempts
  - History logging toggle
  - Schema validation toggle

## Dependencies
None - This is the foundation

## Related Issues
- ISSUE-TASKMANAGER-002 (Core API endpoints)
- ISSUE-TASKMANAGER-003 (Validation and deduplication)

## Implementation Details

### Database Tables
1. **task_types**
   - Fields: id, name, version, param_schema_json, is_active, created_at, updated_at
   - Indexes: name (unique), is_active
   - Purpose: Store task type definitions

2. **tasks**
   - Fields: id, type_id, status, params_json, dedupe_key, result_json, error_message, attempts, claimed_by, claimed_at, completed_at, created_at, updated_at
   - Indexes: type_id+status, status, dedupe_key (unique), created_at
   - Purpose: Store task instances

3. **task_history**
   - Fields: id, task_id, status_change, worker_id, message, created_at
   - Indexes: task_id, created_at
   - Purpose: Audit trail for debugging

### Configuration Options
```php
DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_CHARSET
TASK_CLAIM_TIMEOUT (default: 300s)
MAX_TASK_ATTEMPTS (default: 3)
ENABLE_TASK_HISTORY (default: true)
ENABLE_SCHEMA_VALIDATION (default: true)
```

## Testing
Manual testing:
```sql
-- Import schema
mysql -u user -p database < schema.sql

-- Verify tables created
SHOW TABLES;
DESCRIBE task_types;
DESCRIBE tasks;
DESCRIBE task_history;

-- Test configuration
php -r "require 'config/config.php'; echo 'Config loaded successfully';"
```

## Files Created
- `/Backend/TaskManager/database/schema.sql`
- `/Backend/TaskManager/database/Database.php`
- `/Backend/TaskManager/config/config.example.php`

## Notes
- Schema uses InnoDB engine for transaction support
- UTF-8 encoding for international content support
- Timestamps use MySQL's automatic updating
- Singleton pattern for database connection prevents multiple connections
- Configuration example file should never contain real credentials

## Security Considerations
- Use prepared statements (implemented in Database.php)
- Store config.php outside public directory
- Use restrictive file permissions (640) on config.php
- Never commit config.php to version control
- Use strong database passwords
- Grant minimal database privileges to taskmanager user
