# ISSUE-TASKMANAGER-000: TaskManager Implementation Plan

## Status
🟢 IN PROGRESS

## Component
Backend/TaskManager (Complete System)

## Type
Epic

## Priority
High

## Description
Master issue tracking the complete implementation of the TaskManager backend system - a lightweight PHP+MySQL task queue designed for shared hosting environments (Vedos).

## Problem Statement
PrismQ needs a task management backend that can run on basic shared hosting (Vedos) without long-running processes. The system must:
- Organize tasks by type (e.g., PrismQ.IdeaInspiration.*, PrismQ.Script.*)
- Validate task parameters using JSON Schema
- Support multiple workers claiming and completing tasks
- Prevent duplicate task creation
- Operate entirely on-demand via HTTP requests
- Minimize caching issues with proper headers
- Handle retry logic for failed tasks

## Solution Overview
Implement a REST API-based TaskManager using:
- **Backend**: PHP 7.4+ (no frameworks, pure PHP for compatibility)
- **Database**: MySQL 5.7+ / MariaDB 10.2+
- **Server**: Apache with mod_rewrite
- **Architecture**: Pure on-demand HTTP, no background processes

### System Components
1. **Database Schema**: MySQL tables for task types, tasks, and history
2. **API Endpoints**: REST API for task management
3. **Validation**: JSON Schema validation for parameters
4. **Deduplication**: SHA-256 hash-based duplicate prevention
5. **Documentation**: Complete guides for deployment and usage

## Architecture

### Database Tables
```
task_types (id, name, version, param_schema_json, is_active, timestamps)
tasks (id, type_id, status, params_json, dedupe_key, result_json, error_message, 
       attempts, claimed_by, claimed_at, completed_at, timestamps)
task_history (id, task_id, status_change, worker_id, message, created_at)
```

### API Endpoints
```
POST   /api/task-types/register    - Register task type with schema
GET    /api/task-types/{name}      - Get task type details
GET    /api/task-types             - List all task types

POST   /api/tasks                  - Create task with params
POST   /api/tasks/claim            - Claim task for worker
POST   /api/tasks/{id}/complete    - Complete task with result
GET    /api/tasks/{id}             - Get task status
GET    /api/tasks                  - List tasks (with filters)

GET    /api/health                 - Health check
```

### Task Lifecycle
```
1. Register TaskType → store schema
2. Create Task → validate params → dedupe check → insert
3. Worker Claims → UPDATE status='claimed', lock row
4. Worker Processes → business logic in worker
5. Worker Completes → UPDATE status='completed'/'failed'
6. Retry Logic → if failed + attempts < max → reset to 'pending'
7. Timeout Recovery → reclaim if claimed_at > timeout
```

## Implementation Issues

### Phase 1: Core Infrastructure ✅
**ISSUE-TASKMANAGER-001**: Core Infrastructure and Database Schema
- Status: 🟢 IN PROGRESS
- Database schema (task_types, tasks, task_history)
- Configuration system (config.php, Database.php)
- MySQL connection management

### Phase 2: API Implementation ✅
**ISSUE-TASKMANAGER-002**: Core API Endpoints
- Status: 🟢 IN PROGRESS
- API router (index.php)
- TaskTypeController (register, get, list)
- TaskController (create, claim, complete, get, list)
- ApiResponse helper
- .htaccess for clean URLs

### Phase 3: Validation and Deduplication ✅
**ISSUE-TASKMANAGER-003**: Validation and Deduplication
- Status: 🟢 IN PROGRESS
- JsonSchemaValidator (pure PHP implementation)
- SHA-256 hash-based deduplication
- Parameter validation on task creation
- Error messaging

### Phase 4: Documentation ✅
**ISSUE-TASKMANAGER-004**: Documentation
- Status: 🟢 IN PROGRESS
- README.md (overview, quick start, architecture)
- API_REFERENCE.md (complete endpoint docs)
- DEPLOYMENT.md (step-by-step deployment guide)

### Phase 5: Testing and Examples (PENDING)
**ISSUE-TASKMANAGER-005**: Testing and Examples
- Status: 🔴 NOT STARTED
- Unit tests for validators
- Integration tests for API endpoints
- Example worker implementations
- Postman collection
- Performance benchmarks

## Acceptance Criteria

### Core Functionality
- [x] Database schema supports task types, tasks, and history
- [x] Task types can be registered with JSON schemas
- [x] Tasks are validated against their type's schema
- [x] Duplicate tasks are detected and prevented
- [x] Workers can claim tasks atomically (no race conditions)
- [x] Tasks can be completed with success or failure
- [x] Failed tasks are retried up to max attempts
- [x] Claimed tasks timeout and become reclaimable
- [x] All responses include Cache-Control: no-store

### API Requirements
- [x] RESTful API with clean URLs
- [x] JSON request/response format
- [x] Standardized error responses
- [x] CORS headers for cross-origin access
- [x] Health check endpoint

### Documentation Requirements
- [x] Installation guide
- [x] API reference with examples
- [x] Deployment guide for shared hosting
- [x] Worker implementation examples
- [x] Troubleshooting guide
- [x] Security best practices

### Deployment Requirements
- [ ] Tested on Vedos shared hosting
- [ ] Works with PHP 7.4+
- [ ] Works with MySQL 5.7+
- [ ] Compatible with Apache mod_rewrite
- [ ] No external dependencies
- [ ] File size < 100KB total

## Dependencies
None - This is a standalone system

## Related Issues
- ISSUE-TASKMANAGER-001 (Infrastructure)
- ISSUE-TASKMANAGER-002 (API Endpoints)
- ISSUE-TASKMANAGER-003 (Validation)
- ISSUE-TASKMANAGER-004 (Documentation)
- ISSUE-TASKMANAGER-005 (Testing - future)

## File Structure
```
Backend/TaskManager/
├── README.md                      # Main documentation
├── api/
│   ├── .htaccess                  # URL rewriting
│   ├── index.php                  # API router
│   ├── ApiResponse.php            # Response helper
│   ├── TaskTypeController.php     # Task type endpoints
│   ├── TaskController.php         # Task endpoints
│   └── JsonSchemaValidator.php    # Validation
├── config/
│   └── config.example.php         # Configuration template
├── database/
│   ├── schema.sql                 # Database schema
│   └── Database.php               # Connection manager
└── docs/
    ├── API_REFERENCE.md           # Complete API docs
    └── DEPLOYMENT.md              # Deployment guide
```

## Progress Tracking

### Completed ✅
- [x] Database schema designed and created
- [x] Configuration system implemented
- [x] Database connection class
- [x] API router with request parsing
- [x] TaskType endpoints (register, get, list)
- [x] Task endpoints (create, claim, complete, get, list)
- [x] JSON Schema validator
- [x] Deduplication logic
- [x] Health check endpoint
- [x] README.md
- [x] API_REFERENCE.md
- [x] DEPLOYMENT.md

### In Progress 🟡
- [ ] Testing on actual shared hosting
- [ ] Example worker implementations
- [ ] Postman collection

### Pending 🔴
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Production deployment
- [ ] Monitoring dashboard (optional)

## Key Features Implemented

✅ **No Long-Running Processes**: Pure HTTP request/response
✅ **JSON Schema Validation**: Parameter validation without dependencies
✅ **Deduplication**: SHA-256 hash prevents duplicates
✅ **Worker Coordination**: Claim/complete with timeout handling
✅ **Retry Logic**: Automatic retry of failed tasks
✅ **Cache Prevention**: Cache-Control: no-store on all responses
✅ **Transaction Safety**: Row locking prevents race conditions
✅ **Audit Trail**: Optional task history logging
✅ **Clean URLs**: mod_rewrite for REST-style URLs
✅ **Error Handling**: Comprehensive error messages
✅ **Documentation**: Complete guides and references

## Technical Specifications

### Performance Targets
- Task creation: < 100ms
- Task claim: < 200ms (includes transaction)
- Task completion: < 100ms
- Health check: < 10ms

### Scalability
- Supports 1000+ pending tasks
- 10+ concurrent workers
- 100+ task types
- Suitable for low-to-medium traffic

### Limitations
- No WebSocket support (polling only)
- No real-time notifications
- Limited by shared hosting resources
- No built-in authentication (add manually)
- Basic JSON Schema validation

## Security Measures

✅ **Implemented**:
- SQL injection prevention (prepared statements)
- Input validation on all endpoints
- Worker ID verification
- XSS prevention
- Secure password hashing for config

🔴 **Recommended for Production**:
- [ ] API key authentication
- [ ] Rate limiting
- [ ] HTTPS enforcement
- [ ] Request signing
- [ ] IP whitelisting

## Next Steps

1. **Testing** (ISSUE-TASKMANAGER-005):
   - Create unit tests for validation
   - Create integration tests for API
   - Test on actual Vedos hosting
   - Create example workers

2. **Production Readiness**:
   - Add API authentication
   - Implement rate limiting
   - Set up monitoring
   - Create backup scripts

3. **Worker Development**:
   - PHP worker template
   - Python worker template
   - Node.js worker template
   - Worker best practices guide

4. **Advanced Features** (Optional):
   - Task priorities
   - Task scheduling (delayed execution)
   - Task dependencies
   - Task cancellation
   - Bulk operations
   - Webhook notifications

## Success Metrics

- ✅ All core endpoints implemented
- ✅ Documentation complete
- ⏳ Successfully deployed to shared hosting
- ⏳ Workers claiming and completing tasks
- ⏳ Zero SQL injection vulnerabilities
- ⏳ < 100ms average response time
- ⏳ < 1% task failure rate

## Timeline

- **Week 1**: Core implementation (DONE)
  - Database schema
  - API endpoints
  - Validation and deduplication
  - Documentation

- **Week 2**: Testing and deployment (IN PROGRESS)
  - Deploy to Vedos
  - Create test workers
  - Integration testing
  - Performance testing

- **Week 3**: Production readiness (PENDING)
  - Security hardening
  - Monitoring setup
  - Backup procedures
  - Production deployment

## Notes

### Design Decisions
1. **No Framework**: Pure PHP for maximum compatibility with shared hosting
2. **No External Dependencies**: Everything self-contained
3. **Simple Schema Validator**: Enough for most cases, avoids composer
4. **Polling Model**: No long-polling or WebSockets (not supported on shared hosting)
5. **Transaction Locking**: Prevents race conditions in task claiming

### Shared Hosting Constraints
- No long-running processes (hence on-demand only)
- Limited PHP execution time (30-60 seconds)
- Limited memory (128-256 MB)
- No composer/dependencies in some cases
- No SSH access in some cases
- Limited cron job frequency

### Lessons Learned
- Keep it simple - shared hosting has many limitations
- Pure PHP works better than frameworks for compatibility
- Proper indexing is critical for query performance
- Transaction locking is essential for claim atomicity
- Cache-Control headers are important for shared hosting
- Documentation is as important as code

## References
- [JSON Schema Specification](https://json-schema.org/)
- [REST API Best Practices](https://restfulapi.net/)
- [PHP PDO Documentation](https://www.php.net/manual/en/book.pdo.php)
- [Apache mod_rewrite Guide](https://httpd.apache.org/docs/current/mod/mod_rewrite.html)
