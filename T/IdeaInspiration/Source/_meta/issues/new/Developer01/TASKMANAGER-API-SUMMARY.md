# TaskManager API - Complete Implementation Plan Summary

**Project**: TaskManager API (PHP-based Task Queue)  
**Created**: 2025-11-12  
**Owner**: Developer01 (SCRUM Master & Planning Expert)  
**Total Issues**: 10  
**Timeline**: Week 1-2 (Foundation Phase)

---

## Overview

The TaskManager API provides a lightweight, PHP-based task queue system designed for shared hosting environments. It enables coordination of work across all PrismQ Source modules (Audio, Video, Text, Other) with features like task registration, claiming, completion tracking, and deduplication.

---

## Complete Issue List

### Foundation & Core (Issues #001-#002) ✅
- [x] **#001**: TaskManager API Foundation Setup (2-3 days) - CREATED
- [x] **#002**: Health Check Endpoint (0.5 days) - CREATED

### Task Type Management (Issue #003)
- [ ] **#003**: Task Type Registration Endpoint (2 days)
  - POST /api/task-types/register
  - GET /api/task-types/{name}
  - GET /api/task-types (list all)
  - JSON Schema validation for param_schema

### Task Operations (Issues #004-#006)
- [ ] **#004**: Task Creation with Deduplication (2-3 days)
  - POST /api/tasks (create task)
  - GET /api/tasks (list with filters)
  - Deduplication via dedupe_key (hash of type + params)
  - JSON Schema validation against task type

- [ ] **#005**: Task Claiming Mechanism (2 days)
  - POST /api/tasks/claim (claim oldest pending task)
  - GET /api/tasks/{id} (get task details)
  - Atomic claiming with database transactions
  - Support for sort_by and sort_order
  - Worker coordination (prevent double-claiming)

- [ ] **#006**: Task Completion Reporting (1-2 days)
  - POST /api/tasks/{id}/complete
  - Success/failure handling
  - Result storage
  - Error message recording
  - Attempts tracking

### Infrastructure (Issues #007-#010)
- [ ] **#007**: API Security & Authentication (2 days)
  - API key authentication (X-API-Key header)
  - Middleware implementation
  - Rate limiting per API key
  - Secure key storage

- [ ] **#008**: Database Schema Design (2-3 days)
  - task_types table
  - tasks table
  - task_logs table (audit trail)
  - Indexes for performance (<10ms queries)
  - SQLite primary, MySQL fallback

- [ ] **#009**: JSON Schema Validation (1-2 days)
  - Task type param_schema validation
  - Task params validation against schema
  - Clear validation error messages
  - Schema caching for performance

- [ ] **#010**: Worker Coordination System (1-2 days)
  - Heartbeat mechanism
  - Stale task detection
  - Task re-queue logic
  - Worker status tracking

---

## Database Schema (Issue #008)

### task_types Table
```sql
CREATE TABLE task_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(50) NOT NULL,
    param_schema TEXT NOT NULL,  -- JSON Schema
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, version)
);

CREATE INDEX idx_task_types_name ON task_types(name);
CREATE INDEX idx_task_types_active ON task_types(is_active);
```

### tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, claimed, completed, failed
    params TEXT NOT NULL,  -- JSON
    result TEXT,  -- JSON
    error_message TEXT,
    dedupe_key VARCHAR(64) UNIQUE,  -- SHA256 hash for deduplication
    priority INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    worker_id VARCHAR(255),
    claimed_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_type_id) REFERENCES task_types(id),
    CHECK (status IN ('pending', 'claimed', 'completed', 'failed'))
);

-- Critical indexes for <10ms performance
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type_status ON tasks(task_type_id, status);
CREATE INDEX idx_tasks_created ON tasks(created_at);
CREATE INDEX idx_tasks_priority_created ON tasks(priority DESC, created_at ASC);
CREATE INDEX idx_tasks_dedupe ON tasks(dedupe_key);
CREATE INDEX idx_tasks_worker ON tasks(worker_id);
```

### task_logs Table (Audit Trail)
```sql
CREATE TABLE task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    event VARCHAR(50) NOT NULL,  -- created, claimed, completed, failed, retried
    worker_id VARCHAR(255),
    message TEXT,
    metadata TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE INDEX idx_task_logs_task_id ON task_logs(task_id);
CREATE INDEX idx_task_logs_event ON task_logs(event);
```

---

## API Endpoints Summary

### Health & Status
- `GET /api/health` - System health check (no auth)

### Task Types
- `POST /api/task-types/register` - Register/update task type
- `GET /api/task-types/{name}` - Get specific task type
- `GET /api/task-types?active_only=true` - List task types

### Tasks
- `POST /api/tasks` - Create new task (with deduplication)
- `GET /api/tasks?status=pending&type=PrismQ.%&limit=10` - List tasks
- `GET /api/tasks/{id}` - Get task details
- `POST /api/tasks/claim` - Claim a pending task
- `POST /api/tasks/{id}/complete` - Mark task as completed/failed

---

## Key Technical Decisions

### 1. Deduplication Strategy
```php
// Generate dedupe key from task type and params
$dedupeKey = hash('sha256', $taskType . json_encode($params, JSON_UNESCAPED_SLASHES));
```

### 2. Atomic Task Claiming
```php
// Use database transactions with row locking
$db->beginTransaction();
$task = $db->query("
    SELECT * FROM tasks 
    WHERE status = 'pending' 
    AND task_type_id = ?
    ORDER BY priority DESC, created_at ASC
    LIMIT 1
    FOR UPDATE  -- Row lock
")->fetch();

if ($task) {
    $db->execute("
        UPDATE tasks 
        SET status = 'claimed', worker_id = ?, claimed_at = NOW()
        WHERE id = ? AND status = 'pending'
    ", [$workerId, $task['id']]);
}
$db->commit();
```

### 3. JSON Schema Validation
```php
use JsonSchema\Validator;

$validator = new Validator();
$validator->validate($taskParams, $taskType['param_schema']);

if (!$validator->isValid()) {
    $errors = array_map(fn($e) => $e['message'], $validator->getErrors());
    throw new ValidationException('Invalid task parameters', $errors);
}
```

### 4. Rate Limiting
```php
// Simple in-memory rate limiting (can be enhanced with Redis)
class RateLimiter {
    private array $requests = [];
    
    public function checkLimit(string $apiKey, int $limit = 100, int $window = 60): bool {
        $now = time();
        $this->requests[$apiKey] = array_filter(
            $this->requests[$apiKey] ?? [],
            fn($time) => $time > $now - $window
        );
        
        if (count($this->requests[$apiKey]) >= $limit) {
            return false;
        }
        
        $this->requests[$apiKey][] = $now;
        return true;
    }
}
```

---

## SOLID Principles Application

### Single Responsibility Principle (SRP) ✅
- **TaskTypeController**: Only handles task type endpoints
- **TaskController**: Only handles task endpoints
- **TaskTypeService**: Only business logic for task types
- **TaskService**: Only business logic for tasks
- **ValidationService**: Only parameter validation
- **DeduplicationService**: Only deduplication logic

### Open/Closed Principle (OCP) ✅
- Middleware system allows extending without modification
- Strategy pattern for claiming strategies
- Plugin system for custom validators

### Liskov Substitution Principle (LSP) ✅
- All controllers implement ControllerInterface
- All services implement service interfaces
- Database abstraction allows SQLite/MySQL swap

### Interface Segregation Principle (ISP) ✅
- Small, focused interfaces (no God interfaces)
- TaskRepositoryInterface vs TaskValidationInterface

### Dependency Inversion Principle (DIP) ✅
- Controllers depend on service interfaces
- Services depend on repository interfaces
- Dependency injection throughout

---

## Performance Targets

| Metric | Target | Measured |
|--------|--------|----------|
| Task Registration | <20ms | TBD |
| Task Creation | <30ms | TBD |
| Task Claiming | <10ms | TBD |
| Task Completion | <20ms | TBD |
| Health Check | <50ms | TBD |
| Throughput | 100+ req/s | TBD |
| Database Queries | <10ms (p95) | TBD |
| Memory Usage | <50MB/request | TBD |

---

## Security Checklist

- [ ] API key authentication implemented
- [ ] API keys stored securely (hashed)
- [ ] Rate limiting per API key
- [ ] SQL injection prevention (prepared statements)
- [ ] Input validation on all endpoints
- [ ] No sensitive data in error messages
- [ ] CORS headers configured
- [ ] Security headers (X-Frame-Options, etc.)
- [ ] .htaccess denies access to sensitive files
- [ ] No directory traversal vulnerabilities
- [ ] Audit logging for all operations

---

## Testing Strategy

### Unit Tests (>80% coverage target)
- All service methods
- All controller methods  
- Validation logic
- Deduplication logic
- Database queries

### Integration Tests
- Complete request/response flows
- Multi-developer scenarios
- Concurrent task claiming
- Database transaction handling

### Performance Tests
- Load testing (100+ req/s)
- Query performance (<10ms)
- Memory profiling
- Concurrent developer simulation

### Security Tests
- Authentication bypass attempts
- SQL injection attempts
- Rate limiting validation
- API key security

---

## Developer Assignments

| Issue | Developer | Priority | Duration |
|-------|-----------|----------|----------|
| #001 | Developer02 | ⭐⭐⭐ | 2-3 days |
| #002 | Developer02 | ⭐⭐⭐ | 0.5 days |
| #003 | Developer02 | ⭐⭐⭐ | 2 days |
| #004 | Developer02 | ⭐⭐⭐ | 2-3 days |
| #005 | Developer02 | ⭐⭐⭐ | 2 days |
| #006 | Developer02 | ⭐⭐ | 1-2 days |
| #007 | Developer07 | ⭐⭐⭐ | 2 days |
| #008 | Developer06 | ⭐⭐⭐ | 2-3 days |
| #009 | Developer02 | ⭐⭐ | 1-2 days |
| #010 | Developer02 | ⭐⭐ | 1-2 days |

**Testing**: Developer04 (continuous)  
**Documentation**: Developer09 (continuous)  
**Review**: Developer10 (after implementation)

---

## Timeline

### Week 1
- **Day 1-3**: #001 (Foundation) + #002 (Health Check)
- **Day 3-5**: #008 (Database Schema) + #007 (Security) [parallel]
- **Day 5-7**: #003 (Task Types)

### Week 2
- **Day 1-3**: #004 (Task Creation)
- **Day 3-5**: #005 (Task Claiming) + #009 (Validation) [parallel]
- **Day 5-7**: #006 (Task Completion) + #010 (Coordination) [parallel]

### End of Week 2
- **Testing**: Developer04 comprehensive tests
- **Documentation**: Developer09 complete docs
- **Review**: Developer10 final review

---

## Dependencies Graph

```
#001 (Foundation)
  ↓
#002 (Health) + #008 (Database) + #007 (Security)
  ↓
#003 (Task Types)
  ↓
#004 (Task Creation) + #009 (Validation)
  ↓
#005 (Task Claiming)
  ↓
#006 (Task Completion) + #010 (Coordination)
  ↓
Testing & Review
```

---

## Success Criteria

### Functional
- [ ] All 10 endpoints operational
- [ ] Task deduplication working
- [ ] Atomic task claiming verified
- [ ] JSON Schema validation functional
- [ ] Multi-developer coordination working

### Non-Functional
- [ ] Performance targets met
- [ ] Security review passed
- [ ] Test coverage >80%
- [ ] Documentation complete
- [ ] SOLID principles validated

### Business
- [ ] Can support 10+ concurrent developers
- [ ] Can handle 100+ tasks/minute
- [ ] Deployment on shared hosting successful
- [ ] Integration with Source modules working

---

## Next Steps After Completion

1. **Phase 2**: Integrate with Video/YouTube modules
2. **Phase 3**: Integrate with Text modules (Reddit, HackerNews)
3. **Phase 4**: Expand to Audio and Other modules
4. **Phase 5**: Production deployment and monitoring

---

**Status**: Planning Complete  
**Ready for Implementation**: Yes  
**Blocking**: All Source module implementations  
**Last Updated**: 2025-11-12
