# Issue #003: Task Type Registration Endpoint

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE  
**Reason**: External TaskManager API already exists at https://api.prismq.nomoos.cz/api/  
**Alternative**: Python client (Issue #008) will use existing `/task-types` endpoint

---

## ⚠️ Issue Superseded

This issue was for implementing a **PHP API backend task type registration endpoint**. Since we're integrating with an existing external API, this implementation is **not needed**.

The Python client will use the existing endpoints from https://api.prismq.nomoos.cz/api/

---

## Original (Not Implemented) Overview

Implement the task type registration system that allows developers to register custom task types with JSON Schema validation. This is a core feature that enables all Source modules (Audio, Video, Text, Other) to define their specific task structures and parameters.

---

## Business Context

Each PrismQ module needs to define its own task types (e.g., `youtube_video_scrape`, `reddit_post_fetch`, `spotify_metadata_extract`). The task type registration system provides:
- Centralized task type definitions
- JSON Schema validation for task parameters
- Version management for task types
- Discovery of available task types

**Impact**: All workers need to register their task types before they can create tasks.

---

## API Specification

### Endpoint 1: Register/Update Task Type
```
POST /api/task-types/register
```

#### Authentication
- **Required**: API key via `X-API-Key` header

#### Request Body
```json
{
  "name": "youtube_video_scrape",
  "version": "1.0.0",
  "param_schema": {
    "type": "object",
    "properties": {
      "video_id": {
        "type": "string",
        "pattern": "^[A-Za-z0-9_-]{11}$"
      },
      "quality": {
        "type": "string",
        "enum": ["hd", "sd", "4k"]
      },
      "extract_metadata": {
        "type": "boolean",
        "default": true
      }
    },
    "required": ["video_id"]
  }
}
```

#### Response (201 Created)
```json
{
  "success": true,
  "task_type": {
    "id": 1,
    "name": "youtube_video_scrape",
    "version": "1.0.0",
    "is_active": true,
    "created_at": "2025-11-12T10:00:00Z",
    "updated_at": "2025-11-12T10:00:00Z"
  },
  "message": "Task type registered successfully"
}
```

#### Response (400 Bad Request)
```json
{
  "success": false,
  "error": "Invalid JSON Schema",
  "details": [
    "param_schema.properties.video_id.pattern: Invalid regex pattern"
  ]
}
```

---

### Endpoint 2: Get Task Type by Name
```
GET /api/task-types/{name}
```

#### Authentication
- **Required**: API key via `X-API-Key` header

#### Path Parameters
- `name` - Task type name (e.g., `youtube_video_scrape`)

#### Query Parameters
- `version` (optional) - Specific version to retrieve (defaults to latest active version)

#### Response (200 OK)
```json
{
  "success": true,
  "task_type": {
    "id": 1,
    "name": "youtube_video_scrape",
    "version": "1.0.0",
    "param_schema": {
      "type": "object",
      "properties": {
        "video_id": {
          "type": "string",
          "pattern": "^[A-Za-z0-9_-]{11}$"
        }
      },
      "required": ["video_id"]
    },
    "is_active": true,
    "created_at": "2025-11-12T10:00:00Z",
    "updated_at": "2025-11-12T10:00:00Z"
  }
}
```

#### Response (404 Not Found)
```json
{
  "success": false,
  "error": "Task type not found",
  "name": "unknown_task_type"
}
```

---

### Endpoint 3: List All Task Types
```
GET /api/task-types
```

#### Authentication
- **Required**: API key via `X-API-Key` header

#### Query Parameters
- `active_only` (boolean, default: true) - Only return active task types
- `limit` (integer, default: 50, max: 100) - Number of results per page
- `offset` (integer, default: 0) - Pagination offset

#### Response (200 OK)
```json
{
  "success": true,
  "task_types": [
    {
      "id": 1,
      "name": "youtube_video_scrape",
      "version": "1.0.0",
      "is_active": true,
      "created_at": "2025-11-12T10:00:00Z"
    },
    {
      "id": 2,
      "name": "reddit_post_fetch",
      "version": "1.0.0",
      "is_active": true,
      "created_at": "2025-11-12T10:15:00Z"
    }
  ],
  "pagination": {
    "total": 2,
    "limit": 50,
    "offset": 0
  }
}
```

---

## Implementation Requirements

### Controller (src/Controllers/TaskTypeController.php)

```php
<?php
namespace TaskManager\Controllers;

use TaskManager\Core\{Request, Response};
use TaskManager\Services\TaskTypeService;

class TaskTypeController {
    private TaskTypeService $taskTypeService;
    
    public function __construct(TaskTypeService $taskTypeService) {
        $this->taskTypeService = $taskTypeService;
    }
    
    /**
     * Register or update a task type
     */
    public function register(Request $request): Response {
        $data = $request->getBody();
        
        // Validate required fields
        $required = ['name', 'version', 'param_schema'];
        foreach ($required as $field) {
            if (!isset($data[$field])) {
                return (new Response())->json([
                    'success' => false,
                    'error' => "Missing required field: {$field}"
                ], 400);
            }
        }
        
        try {
            $taskType = $this->taskTypeService->register(
                $data['name'],
                $data['version'],
                $data['param_schema']
            );
            
            return (new Response())->json([
                'success' => true,
                'task_type' => $taskType,
                'message' => 'Task type registered successfully'
            ], 201);
        } catch (\Exception $e) {
            return (new Response())->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 400);
        }
    }
    
    /**
     * Get a specific task type by name
     */
    public function getByName(Request $request): Response {
        $name = $request->getPathParam('name');
        $version = $request->getQueryParam('version');
        
        try {
            $taskType = $this->taskTypeService->getByName($name, $version);
            
            if (!$taskType) {
                return (new Response())->json([
                    'success' => false,
                    'error' => 'Task type not found',
                    'name' => $name
                ], 404);
            }
            
            return (new Response())->json([
                'success' => true,
                'task_type' => $taskType
            ], 200);
        } catch (\Exception $e) {
            return (new Response())->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * List all task types
     */
    public function list(Request $request): Response {
        $activeOnly = $request->getQueryParam('active_only', true);
        $limit = min((int)$request->getQueryParam('limit', 50), 100);
        $offset = (int)$request->getQueryParam('offset', 0);
        
        try {
            $result = $this->taskTypeService->list($activeOnly, $limit, $offset);
            
            return (new Response())->json([
                'success' => true,
                'task_types' => $result['task_types'],
                'pagination' => $result['pagination']
            ], 200);
        } catch (\Exception $e) {
            return (new Response())->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
```

### Service (src/Services/TaskTypeService.php)

```php
<?php
namespace TaskManager\Services;

use TaskManager\Models\TaskTypeRepository;
use TaskManager\Services\JsonSchemaValidator;

class TaskTypeService {
    private TaskTypeRepository $repository;
    private JsonSchemaValidator $validator;
    
    public function __construct(
        TaskTypeRepository $repository,
        JsonSchemaValidator $validator
    ) {
        $this->repository = $repository;
        $this->validator = $validator;
    }
    
    /**
     * Register or update a task type
     */
    public function register(string $name, string $version, array $paramSchema): array {
        // Validate task type name
        if (!preg_match('/^[a-z0-9_]+$/', $name)) {
            throw new \InvalidArgumentException(
                'Task type name must contain only lowercase letters, numbers, and underscores'
            );
        }
        
        // Validate version format (semver)
        if (!preg_match('/^\d+\.\d+\.\d+$/', $version)) {
            throw new \InvalidArgumentException(
                'Version must be in semver format (e.g., 1.0.0)'
            );
        }
        
        // Validate param_schema is valid JSON Schema
        $this->validator->validateSchema($paramSchema);
        
        // Check if task type already exists
        $existing = $this->repository->findByNameAndVersion($name, $version);
        
        if ($existing) {
            // Update existing task type
            $taskType = $this->repository->update($existing['id'], [
                'param_schema' => json_encode($paramSchema),
                'updated_at' => date('Y-m-d H:i:s')
            ]);
        } else {
            // Create new task type
            $taskType = $this->repository->create([
                'name' => $name,
                'version' => $version,
                'param_schema' => json_encode($paramSchema),
                'is_active' => 1
            ]);
        }
        
        return $this->formatTaskType($taskType);
    }
    
    /**
     * Get task type by name (and optional version)
     */
    public function getByName(string $name, ?string $version = null): ?array {
        if ($version) {
            $taskType = $this->repository->findByNameAndVersion($name, $version);
        } else {
            $taskType = $this->repository->findLatestByName($name);
        }
        
        return $taskType ? $this->formatTaskType($taskType) : null;
    }
    
    /**
     * List task types with pagination
     */
    public function list(bool $activeOnly, int $limit, int $offset): array {
        $taskTypes = $this->repository->findAll($activeOnly, $limit, $offset);
        $total = $this->repository->count($activeOnly);
        
        return [
            'task_types' => array_map(
                fn($tt) => $this->formatTaskType($tt, false),
                $taskTypes
            ),
            'pagination' => [
                'total' => $total,
                'limit' => $limit,
                'offset' => $offset
            ]
        ];
    }
    
    /**
     * Format task type for API response
     */
    private function formatTaskType(array $taskType, bool $includeSchema = true): array {
        $formatted = [
            'id' => (int)$taskType['id'],
            'name' => $taskType['name'],
            'version' => $taskType['version'],
            'is_active' => (bool)$taskType['is_active'],
            'created_at' => $taskType['created_at'],
            'updated_at' => $taskType['updated_at']
        ];
        
        if ($includeSchema) {
            $formatted['param_schema'] = json_decode($taskType['param_schema'], true);
        }
        
        return $formatted;
    }
}
```

### Repository (src/Models/TaskTypeRepository.php)

```php
<?php
namespace TaskManager\Models;

use TaskManager\Core\Database;

class TaskTypeRepository {
    private Database $db;
    
    public function __construct(Database $db) {
        $this->db = $db;
    }
    
    public function create(array $data): array {
        $sql = "INSERT INTO task_types (name, version, param_schema, is_active, created_at, updated_at)
                VALUES (:name, :version, :param_schema, :is_active, datetime('now'), datetime('now'))";
        
        $id = $this->db->execute($sql, $data);
        
        return $this->findById($id);
    }
    
    public function update(int $id, array $data): array {
        $fields = [];
        foreach ($data as $key => $value) {
            $fields[] = "{$key} = :{$key}";
        }
        
        $sql = "UPDATE task_types SET " . implode(', ', $fields) . " WHERE id = :id";
        $data['id'] = $id;
        
        $this->db->execute($sql, $data);
        
        return $this->findById($id);
    }
    
    public function findById(int $id): ?array {
        $sql = "SELECT * FROM task_types WHERE id = :id";
        return $this->db->fetchOne($sql, ['id' => $id]);
    }
    
    public function findByNameAndVersion(string $name, string $version): ?array {
        $sql = "SELECT * FROM task_types WHERE name = :name AND version = :version";
        return $this->db->fetchOne($sql, ['name' => $name, 'version' => $version]);
    }
    
    public function findLatestByName(string $name): ?array {
        $sql = "SELECT * FROM task_types 
                WHERE name = :name AND is_active = 1 
                ORDER BY created_at DESC 
                LIMIT 1";
        return $this->db->fetchOne($sql, ['name' => $name]);
    }
    
    public function findAll(bool $activeOnly, int $limit, int $offset): array {
        $where = $activeOnly ? 'WHERE is_active = 1' : '';
        $sql = "SELECT * FROM task_types {$where} 
                ORDER BY created_at DESC 
                LIMIT :limit OFFSET :offset";
        
        return $this->db->fetchAll($sql, [
            'limit' => $limit,
            'offset' => $offset
        ]);
    }
    
    public function count(bool $activeOnly): int {
        $where = $activeOnly ? 'WHERE is_active = 1' : '';
        $sql = "SELECT COUNT(*) as count FROM task_types {$where}";
        $result = $this->db->fetchOne($sql);
        return (int)$result['count'];
    }
}
```

### JSON Schema Validator (src/Services/JsonSchemaValidator.php)

```php
<?php
namespace TaskManager\Services;

class JsonSchemaValidator {
    /**
     * Validate that a schema is valid JSON Schema
     */
    public function validateSchema(array $schema): void {
        // Check that schema has required 'type' field
        if (!isset($schema['type'])) {
            throw new \InvalidArgumentException('Schema must have a "type" field');
        }
        
        // Validate type is one of the allowed types
        $allowedTypes = ['object', 'array', 'string', 'number', 'integer', 'boolean', 'null'];
        if (!in_array($schema['type'], $allowedTypes)) {
            throw new \InvalidArgumentException(
                "Invalid type '{$schema['type']}'. Must be one of: " . implode(', ', $allowedTypes)
            );
        }
        
        // For object types, validate properties if present
        if ($schema['type'] === 'object' && isset($schema['properties'])) {
            if (!is_array($schema['properties'])) {
                throw new \InvalidArgumentException('properties must be an object');
            }
            
            // Recursively validate nested properties
            foreach ($schema['properties'] as $propName => $propSchema) {
                if (!is_array($propSchema)) {
                    throw new \InvalidArgumentException(
                        "Property '{$propName}' schema must be an object"
                    );
                }
                $this->validateSchema($propSchema);
            }
        }
        
        // Validate 'required' field if present
        if (isset($schema['required'])) {
            if (!is_array($schema['required'])) {
                throw new \InvalidArgumentException('required must be an array');
            }
        }
        
        // Validate 'enum' field if present
        if (isset($schema['enum'])) {
            if (!is_array($schema['enum']) || empty($schema['enum'])) {
                throw new \InvalidArgumentException('enum must be a non-empty array');
            }
        }
        
        // Validate pattern if present (for string types)
        if (isset($schema['pattern'])) {
            // Test that the pattern is a valid regex
            if (@preg_match('/' . $schema['pattern'] . '/', '') === false) {
                throw new \InvalidArgumentException(
                    "Invalid regex pattern: {$schema['pattern']}"
                );
            }
        }
    }
    
    /**
     * Validate data against a JSON Schema
     */
    public function validate(array $data, array $schema): array {
        $errors = [];
        
        // Type validation
        $actualType = $this->getType($data);
        if ($actualType !== $schema['type']) {
            $errors[] = "Expected type '{$schema['type']}', got '{$actualType}'";
            return $errors;
        }
        
        // Object validation
        if ($schema['type'] === 'object') {
            // Check required fields
            if (isset($schema['required'])) {
                foreach ($schema['required'] as $required) {
                    if (!isset($data[$required])) {
                        $errors[] = "Missing required field: {$required}";
                    }
                }
            }
            
            // Validate properties
            if (isset($schema['properties'])) {
                foreach ($data as $key => $value) {
                    if (isset($schema['properties'][$key])) {
                        $propErrors = $this->validate(
                            [$value],
                            $schema['properties'][$key]
                        );
                        foreach ($propErrors as $error) {
                            $errors[] = "{$key}: {$error}";
                        }
                    }
                }
            }
        }
        
        // String validation
        if ($schema['type'] === 'string') {
            if (isset($schema['pattern'])) {
                if (!preg_match('/' . $schema['pattern'] . '/', $data)) {
                    $errors[] = "String does not match pattern: {$schema['pattern']}";
                }
            }
            
            if (isset($schema['enum'])) {
                if (!in_array($data, $schema['enum'])) {
                    $errors[] = "Value must be one of: " . implode(', ', $schema['enum']);
                }
            }
        }
        
        return $errors;
    }
    
    private function getType($value): string {
        if (is_array($value)) {
            return array_keys($value) === range(0, count($value) - 1) ? 'array' : 'object';
        }
        if (is_bool($value)) return 'boolean';
        if (is_int($value)) return 'integer';
        if (is_float($value)) return 'number';
        if (is_string($value)) return 'string';
        if (is_null($value)) return 'null';
        return 'unknown';
    }
}
```

### Route Registration (config/routes.php)

```php
// Task Type Routes
$router->post('/api/task-types/register', [TaskTypeController::class, 'register']);
$router->get('/api/task-types/{name}', [TaskTypeController::class, 'getByName']);
$router->get('/api/task-types', [TaskTypeController::class, 'list']);
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] POST `/api/task-types/register` creates new task types
- [ ] POST `/api/task-types/register` updates existing task types (same name+version)
- [ ] GET `/api/task-types/{name}` returns task type details including schema
- [ ] GET `/api/task-types/{name}?version=x.y.z` returns specific version
- [ ] GET `/api/task-types` lists all active task types
- [ ] GET `/api/task-types?active_only=false` includes inactive task types
- [ ] Task type names must match pattern: `^[a-z0-9_]+$`
- [ ] Versions must be valid semver (x.y.z)
- [ ] JSON Schema validation works correctly
- [ ] Invalid schemas are rejected with clear error messages

### Non-Functional Requirements
- [ ] Registration completes in <50ms (p95)
- [ ] Retrieval completes in <20ms (p95)
- [ ] List endpoint supports pagination (limit/offset)
- [ ] API returns consistent JSON format
- [ ] All endpoints require authentication (except health)

### Testing
- [ ] Unit tests for TaskTypeService (>80% coverage)
- [ ] Unit tests for JsonSchemaValidator
- [ ] Integration tests for all 3 endpoints
- [ ] Test invalid schema rejection
- [ ] Test name/version validation
- [ ] Test pagination

### Documentation
- [ ] API documentation updated
- [ ] JSON Schema examples provided
- [ ] README includes task type registration guide

---

## Testing Strategy

### Unit Tests

```php
class TaskTypeServiceTest extends TestCase {
    public function testRegisterValidTaskType() {
        $service = new TaskTypeService($mockRepo, $mockValidator);
        
        $result = $service->register('test_task', '1.0.0', [
            'type' => 'object',
            'properties' => [
                'param1' => ['type' => 'string']
            ]
        ]);
        
        $this->assertIsArray($result);
        $this->assertEquals('test_task', $result['name']);
        $this->assertEquals('1.0.0', $result['version']);
    }
    
    public function testRegisterInvalidName() {
        $this->expectException(\InvalidArgumentException::class);
        
        $service = new TaskTypeService($mockRepo, $mockValidator);
        $service->register('Invalid-Name!', '1.0.0', ['type' => 'object']);
    }
    
    public function testRegisterInvalidVersion() {
        $this->expectException(\InvalidArgumentException::class);
        
        $service = new TaskTypeService($mockRepo, $mockValidator);
        $service->register('test_task', 'invalid', ['type' => 'object']);
    }
}

class JsonSchemaValidatorTest extends TestCase {
    public function testValidateValidSchema() {
        $validator = new JsonSchemaValidator();
        
        // Should not throw exception
        $validator->validateSchema([
            'type' => 'object',
            'properties' => [
                'name' => ['type' => 'string'],
                'age' => ['type' => 'integer']
            ],
            'required' => ['name']
        ]);
        
        $this->assertTrue(true);
    }
    
    public function testValidateInvalidPattern() {
        $this->expectException(\InvalidArgumentException::class);
        
        $validator = new JsonSchemaValidator();
        $validator->validateSchema([
            'type' => 'string',
            'pattern' => '[invalid(regex'
        ]);
    }
}
```

### Integration Tests

```php
class TaskTypeEndpointTest extends IntegrationTestCase {
    public function testRegisterTaskType() {
        $response = $this->post('/api/task-types/register', [
            'name' => 'youtube_video_scrape',
            'version' => '1.0.0',
            'param_schema' => [
                'type' => 'object',
                'properties' => [
                    'video_id' => ['type' => 'string']
                ],
                'required' => ['video_id']
            ]
        ]);
        
        $this->assertEquals(201, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['success']);
        $this->assertEquals('youtube_video_scrape', $data['task_type']['name']);
    }
    
    public function testGetTaskType() {
        // Register first
        $this->post('/api/task-types/register', [...]);
        
        // Then retrieve
        $response = $this->get('/api/task-types/youtube_video_scrape');
        
        $this->assertEquals(200, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['success']);
        $this->assertArrayHasKey('param_schema', $data['task_type']);
    }
    
    public function testListTaskTypes() {
        $response = $this->get('/api/task-types?limit=10');
        
        $this->assertEquals(200, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['success']);
        $this->assertIsArray($data['task_types']);
        $this->assertArrayHasKey('pagination', $data);
    }
}
```

---

## Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| Register Task Type | <50ms (p95) | Infrequent operation, acceptable latency |
| Get Task Type | <20ms (p95) | Frequent lookups, needs to be fast |
| List Task Types | <30ms (p95) | With pagination, should be efficient |
| Database Query | <10ms (p95) | Using indexes, SQLite should be fast |

---

## SOLID Principles Validation

### Single Responsibility Principle (SRP) ✅
- **TaskTypeController**: Only handles HTTP request/response
- **TaskTypeService**: Only handles business logic
- **TaskTypeRepository**: Only handles database operations
- **JsonSchemaValidator**: Only handles schema validation

### Open/Closed Principle (OCP) ✅
- Service can be extended with new validation rules without modification
- Validator can support additional JSON Schema features via plugins

### Liskov Substitution Principle (LSP) ✅
- Repository implements RepositoryInterface
- Can swap SQLite repository with MySQL without breaking service

### Interface Segregation Principle (ISP) ✅
- TaskTypeRepository focuses only on task type operations
- JsonSchemaValidator has focused interface

### Dependency Inversion Principle (DIP) ✅
- TaskTypeService depends on RepositoryInterface, not concrete implementation
- Controller depends on Service interface
- All dependencies injected via constructor

---

## Security Considerations

### Authentication
- All endpoints require API key authentication
- API keys validated via AuthMiddleware

### Input Validation
- Task type names validated against `^[a-z0-9_]+$` pattern
- Versions validated against semver pattern
- JSON Schema validated before storage
- Prevent regex DoS by limiting pattern complexity

### SQL Injection Prevention
- All queries use prepared statements with parameter binding

### Rate Limiting
- Standard rate limits apply (100 req/min per API key)

---

## Dependencies

### Depends On (Blocked By)
- #001 - API Foundation (Router, Request, Response, Database)
- #002 - Health Check (ensures API is operational)

### Blocks
- #004 - Task Creation (needs task types to validate against)
- All worker implementations (must register task types first)

---

## Related Issues
- #004 - Task Creation (will use task types for validation)
- #009 - JSON Schema Validation (enhanced validation features)
- #008 - Database Schema (task_types table)

---

## Definition of Done

- [ ] All 3 endpoints implemented and working
- [ ] Unit tests written with >80% coverage
- [ ] Integration tests passing
- [ ] API documentation updated
- [ ] JSON Schema validation working correctly
- [ ] Name and version validation implemented
- [ ] Performance targets met
- [ ] Code reviewed by Developer10
- [ ] SOLID principles validated
- [ ] Security review passed
- [ ] Can register and retrieve YouTube, Reddit, and Audio task types

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 2 days  
**Assignee**: Developer02  
**Reviewer**: Developer10
