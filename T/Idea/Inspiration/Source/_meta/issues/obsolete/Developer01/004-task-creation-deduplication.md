# Issue #004: Task Creation with Deduplication

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE  
**Reason**: External TaskManager API already exists with deduplication built-in  
**Alternative**: Python client (Issue #008) will use existing `/tasks` endpoint

---

## ⚠️ Issue Superseded

This issue was for implementing **PHP API backend task creation with deduplication**. The external API already handles this. Python client will integrate with existing functionality.

---

## Original (Not Implemented) Overview

Implement the task creation system with automatic deduplication to prevent duplicate work across all developers. This system allows workers to submit tasks while ensuring that identical tasks (same type + parameters) are only queued once.

---

## Business Context

With 10 developers working across multiple Source modules, duplicate tasks are inevitable without a deduplication system. For example:
- Multiple developers might request the same YouTube video
- The same Reddit post might be discovered by different workers
- Trending content might be queued multiple times

**Impact**: Task deduplication prevents wasted resources and ensures efficient worker coordination.

---

## API Specification

### Endpoint 1: Create Task
```
POST /api/tasks
```

#### Authentication
- **Required**: API key via `X-API-Key` header

#### Request Body
```json
{
  "task_type": "youtube_video_scrape",
  "params": {
    "video_id": "dQw4w9WgXcQ",
    "quality": "hd",
    "extract_metadata": true
  },
  "priority": 5,
  "max_attempts": 3
}
```

#### Response (201 Created) - New Task
```json
{
  "success": true,
  "task": {
    "id": 123,
    "task_type": "youtube_video_scrape",
    "status": "pending",
    "params": {
      "video_id": "dQw4w9WgXcQ",
      "quality": "hd",
      "extract_metadata": true
    },
    "priority": 5,
    "max_attempts": 3,
    "attempts": 0,
    "dedupe_key": "a1b2c3d4e5f6...",
    "created_at": "2025-11-12T10:00:00Z"
  },
  "message": "Task created successfully",
  "was_duplicate": false
}
```

#### Response (200 OK) - Existing Task (Deduplicated)
```json
{
  "success": true,
  "task": {
    "id": 100,
    "task_type": "youtube_video_scrape",
    "status": "pending",
    "params": {
      "video_id": "dQw4w9WgXcQ",
      "quality": "hd",
      "extract_metadata": true
    },
    "priority": 5,
    "created_at": "2025-11-12T09:45:00Z"
  },
  "message": "Task already exists (deduplicated)",
  "was_duplicate": true
}
```

#### Response (400 Bad Request) - Validation Error
```json
{
  "success": false,
  "error": "Invalid task parameters",
  "details": [
    "params.video_id: Does not match pattern ^[A-Za-z0-9_-]{11}$",
    "params.quality: Must be one of: hd, sd, 4k"
  ]
}
```

---

### Endpoint 2: List Tasks
```
GET /api/tasks
```

#### Authentication
- **Required**: API key via `X-API-Key` header

#### Query Parameters
- `status` (string, optional) - Filter by status: pending, claimed, completed, failed
- `task_type` (string, optional) - Filter by task type (supports SQL LIKE pattern)
- `priority_min` (integer, optional) - Minimum priority
- `priority_max` (integer, optional) - Maximum priority
- `limit` (integer, default: 50, max: 100) - Results per page
- `offset` (integer, default: 0) - Pagination offset
- `sort_by` (string, default: created_at) - Sort field: created_at, priority
- `sort_order` (string, default: desc) - Sort order: asc, desc

#### Response (200 OK)
```json
{
  "success": true,
  "tasks": [
    {
      "id": 123,
      "task_type": "youtube_video_scrape",
      "status": "pending",
      "priority": 5,
      "attempts": 0,
      "max_attempts": 3,
      "created_at": "2025-11-12T10:00:00Z"
    },
    {
      "id": 122,
      "task_type": "reddit_post_fetch",
      "status": "claimed",
      "priority": 3,
      "worker_id": "worker-02",
      "claimed_at": "2025-11-12T09:55:00Z",
      "created_at": "2025-11-12T09:50:00Z"
    }
  ],
  "pagination": {
    "total": 245,
    "limit": 50,
    "offset": 0
  }
}
```

---

### Endpoint 3: Get Task Details
```
GET /api/tasks/{id}
```

#### Authentication
- **Required**: API key via `X-API-Key` header

#### Path Parameters
- `id` - Task ID

#### Response (200 OK)
```json
{
  "success": true,
  "task": {
    "id": 123,
    "task_type": "youtube_video_scrape",
    "status": "pending",
    "params": {
      "video_id": "dQw4w9WgXcQ",
      "quality": "hd",
      "extract_metadata": true
    },
    "result": null,
    "error_message": null,
    "priority": 5,
    "attempts": 0,
    "max_attempts": 3,
    "worker_id": null,
    "claimed_at": null,
    "completed_at": null,
    "created_at": "2025-11-12T10:00:00Z",
    "updated_at": "2025-11-12T10:00:00Z"
  }
}
```

#### Response (404 Not Found)
```json
{
  "success": false,
  "error": "Task not found",
  "task_id": 123
}
```

---

## Implementation Requirements

### Controller (src/Controllers/TaskController.php)

```php
<?php
namespace TaskManager\Controllers;

use TaskManager\Core\{Request, Response};
use TaskManager\Services\TaskService;

class TaskController {
    private TaskService $taskService;
    
    public function __construct(TaskService $taskService) {
        $this->taskService = $taskService;
    }
    
    /**
     * Create a new task with deduplication
     */
    public function create(Request $request): Response {
        $data = $request->getBody();
        
        // Validate required fields
        if (!isset($data['task_type']) || !isset($data['params'])) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Missing required fields: task_type, params'
            ], 400);
        }
        
        try {
            $result = $this->taskService->createTask(
                $data['task_type'],
                $data['params'],
                $data['priority'] ?? 0,
                $data['max_attempts'] ?? 3
            );
            
            $statusCode = $result['was_duplicate'] ? 200 : 201;
            
            return (new Response())->json([
                'success' => true,
                'task' => $result['task'],
                'message' => $result['message'],
                'was_duplicate' => $result['was_duplicate']
            ], $statusCode);
            
        } catch (\InvalidArgumentException $e) {
            return (new Response())->json([
                'success' => false,
                'error' => $e->getMessage(),
                'details' => $e->getDetails() ?? []
            ], 400);
            
        } catch (\Exception $e) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Internal server error'
            ], 500);
        }
    }
    
    /**
     * List tasks with filters and pagination
     */
    public function list(Request $request): Response {
        $filters = [
            'status' => $request->getQueryParam('status'),
            'task_type' => $request->getQueryParam('task_type'),
            'priority_min' => $request->getQueryParam('priority_min'),
            'priority_max' => $request->getQueryParam('priority_max')
        ];
        
        $limit = min((int)$request->getQueryParam('limit', 50), 100);
        $offset = (int)$request->getQueryParam('offset', 0);
        $sortBy = $request->getQueryParam('sort_by', 'created_at');
        $sortOrder = $request->getQueryParam('sort_order', 'desc');
        
        try {
            $result = $this->taskService->listTasks(
                $filters,
                $limit,
                $offset,
                $sortBy,
                $sortOrder
            );
            
            return (new Response())->json([
                'success' => true,
                'tasks' => $result['tasks'],
                'pagination' => $result['pagination']
            ], 200);
            
        } catch (\Exception $e) {
            return (new Response())->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * Get task details by ID
     */
    public function getById(Request $request): Response {
        $id = (int)$request->getPathParam('id');
        
        try {
            $task = $this->taskService->getTaskById($id);
            
            if (!$task) {
                return (new Response())->json([
                    'success' => false,
                    'error' => 'Task not found',
                    'task_id' => $id
                ], 404);
            }
            
            return (new Response())->json([
                'success' => true,
                'task' => $task
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

### Service (src/Services/TaskService.php)

```php
<?php
namespace TaskManager\Services;

use TaskManager\Models\{TaskRepository, TaskTypeRepository};
use TaskManager\Services\{JsonSchemaValidator, DeduplicationService};

class TaskService {
    private TaskRepository $taskRepo;
    private TaskTypeRepository $taskTypeRepo;
    private JsonSchemaValidator $validator;
    private DeduplicationService $deduplication;
    
    public function __construct(
        TaskRepository $taskRepo,
        TaskTypeRepository $taskTypeRepo,
        JsonSchemaValidator $validator,
        DeduplicationService $deduplication
    ) {
        $this->taskRepo = $taskRepo;
        $this->taskTypeRepo = $taskTypeRepo;
        $this->validator = $validator;
        $this->deduplication = $deduplication;
    }
    
    /**
     * Create a task with deduplication
     */
    public function createTask(
        string $taskType,
        array $params,
        int $priority = 0,
        int $maxAttempts = 3
    ): array {
        // 1. Get task type definition
        $taskTypeDef = $this->taskTypeRepo->findLatestByName($taskType);
        if (!$taskTypeDef) {
            throw new \InvalidArgumentException("Unknown task type: {$taskType}");
        }
        
        // 2. Validate params against JSON Schema
        $schema = json_decode($taskTypeDef['param_schema'], true);
        $errors = $this->validator->validate($params, $schema);
        
        if (!empty($errors)) {
            $exception = new \InvalidArgumentException('Invalid task parameters');
            $exception->setDetails($errors);
            throw $exception;
        }
        
        // 3. Generate deduplication key
        $dedupeKey = $this->deduplication->generateKey($taskType, $params);
        
        // 4. Check for existing task with same dedupe key
        $existing = $this->taskRepo->findByDedupeKey($dedupeKey);
        
        if ($existing && in_array($existing['status'], ['pending', 'claimed'])) {
            // Task already exists and is not complete
            return [
                'task' => $this->formatTask($existing),
                'message' => 'Task already exists (deduplicated)',
                'was_duplicate' => true
            ];
        }
        
        // 5. Create new task
        $task = $this->taskRepo->create([
            'task_type_id' => $taskTypeDef['id'],
            'params' => json_encode($params),
            'priority' => $priority,
            'max_attempts' => $maxAttempts,
            'dedupe_key' => $dedupeKey,
            'status' => 'pending'
        ]);
        
        // 6. Log task creation
        $this->logTaskEvent($task['id'], 'created', null, 'Task created via API');
        
        return [
            'task' => $this->formatTask($task),
            'message' => 'Task created successfully',
            'was_duplicate' => false
        ];
    }
    
    /**
     * List tasks with filters
     */
    public function listTasks(
        array $filters,
        int $limit,
        int $offset,
        string $sortBy,
        string $sortOrder
    ): array {
        // Validate sort parameters
        $allowedSortBy = ['created_at', 'priority', 'updated_at'];
        if (!in_array($sortBy, $allowedSortBy)) {
            $sortBy = 'created_at';
        }
        
        $sortOrder = strtoupper($sortOrder);
        if (!in_array($sortOrder, ['ASC', 'DESC'])) {
            $sortOrder = 'DESC';
        }
        
        // Fetch tasks
        $tasks = $this->taskRepo->findWithFilters(
            $filters,
            $limit,
            $offset,
            $sortBy,
            $sortOrder
        );
        
        $total = $this->taskRepo->countWithFilters($filters);
        
        return [
            'tasks' => array_map(
                fn($t) => $this->formatTask($t, false),
                $tasks
            ),
            'pagination' => [
                'total' => $total,
                'limit' => $limit,
                'offset' => $offset
            ]
        ];
    }
    
    /**
     * Get task by ID
     */
    public function getTaskById(int $id): ?array {
        $task = $this->taskRepo->findById($id);
        return $task ? $this->formatTask($task, true) : null;
    }
    
    /**
     * Format task for API response
     */
    private function formatTask(array $task, bool $includeDetails = true): array {
        $taskType = $this->taskTypeRepo->findById($task['task_type_id']);
        
        $formatted = [
            'id' => (int)$task['id'],
            'task_type' => $taskType['name'],
            'status' => $task['status'],
            'priority' => (int)$task['priority'],
            'attempts' => (int)$task['attempts'],
            'max_attempts' => (int)$task['max_attempts'],
            'created_at' => $task['created_at']
        ];
        
        if ($includeDetails) {
            $formatted['params'] = json_decode($task['params'], true);
            $formatted['result'] = $task['result'] ? json_decode($task['result'], true) : null;
            $formatted['error_message'] = $task['error_message'];
            $formatted['worker_id'] = $task['worker_id'];
            $formatted['claimed_at'] = $task['claimed_at'];
            $formatted['completed_at'] = $task['completed_at'];
            $formatted['updated_at'] = $task['updated_at'];
        } else {
            // Include worker info if claimed
            if ($task['status'] === 'claimed') {
                $formatted['worker_id'] = $task['worker_id'];
                $formatted['claimed_at'] = $task['claimed_at'];
            }
        }
        
        return $formatted;
    }
    
    /**
     * Log task event for audit trail
     */
    private function logTaskEvent(
        int $taskId,
        string $event,
        ?string $workerId,
        string $message
    ): void {
        // This will be implemented with task_logs table
        // For now, just a placeholder
    }
}
```

### Deduplication Service (src/Services/DeduplicationService.php)

```php
<?php
namespace TaskManager\Services;

class DeduplicationService {
    /**
     * Generate deduplication key from task type and params
     * 
     * The key is a SHA-256 hash of the task type + sorted params JSON.
     * This ensures identical tasks always get the same dedupe key.
     */
    public function generateKey(string $taskType, array $params): string {
        // Sort params to ensure consistent ordering
        $sortedParams = $this->sortRecursive($params);
        
        // Create deterministic JSON (no whitespace, sorted keys)
        $json = json_encode($sortedParams, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        
        // Combine task type + params
        $data = $taskType . ':' . $json;
        
        // Generate SHA-256 hash
        return hash('sha256', $data);
    }
    
    /**
     * Recursively sort array by keys
     */
    private function sortRecursive(array $array): array {
        ksort($array);
        
        foreach ($array as $key => $value) {
            if (is_array($value)) {
                $array[$key] = $this->sortRecursive($value);
            }
        }
        
        return $array;
    }
    
    /**
     * Check if two task parameter sets are equivalent
     */
    public function areParamsEquivalent(array $params1, array $params2): bool {
        $key1 = hash('sha256', json_encode($this->sortRecursive($params1)));
        $key2 = hash('sha256', json_encode($this->sortRecursive($params2)));
        
        return $key1 === $key2;
    }
}
```

### Repository (src/Models/TaskRepository.php)

```php
<?php
namespace TaskManager\Models;

use TaskManager\Core\Database;

class TaskRepository {
    private Database $db;
    
    public function __construct(Database $db) {
        $this->db = $db;
    }
    
    public function create(array $data): array {
        $sql = "INSERT INTO tasks (
                    task_type_id, status, params, priority, max_attempts, 
                    dedupe_key, created_at, updated_at
                ) VALUES (
                    :task_type_id, :status, :params, :priority, :max_attempts,
                    :dedupe_key, datetime('now'), datetime('now')
                )";
        
        $id = $this->db->execute($sql, $data);
        return $this->findById($id);
    }
    
    public function findById(int $id): ?array {
        $sql = "SELECT * FROM tasks WHERE id = :id";
        return $this->db->fetchOne($sql, ['id' => $id]);
    }
    
    public function findByDedupeKey(string $dedupeKey): ?array {
        $sql = "SELECT * FROM tasks WHERE dedupe_key = :dedupe_key";
        return $this->db->fetchOne($sql, ['dedupe_key' => $dedupeKey]);
    }
    
    public function findWithFilters(
        array $filters,
        int $limit,
        int $offset,
        string $sortBy,
        string $sortOrder
    ): array {
        $where = ['1=1'];
        $params = [];
        
        if (!empty($filters['status'])) {
            $where[] = 'status = :status';
            $params['status'] = $filters['status'];
        }
        
        if (!empty($filters['task_type'])) {
            $where[] = 'task_type_id IN (
                SELECT id FROM task_types WHERE name LIKE :task_type
            )';
            $params['task_type'] = $filters['task_type'];
        }
        
        if (isset($filters['priority_min'])) {
            $where[] = 'priority >= :priority_min';
            $params['priority_min'] = $filters['priority_min'];
        }
        
        if (isset($filters['priority_max'])) {
            $where[] = 'priority <= :priority_max';
            $params['priority_max'] = $filters['priority_max'];
        }
        
        $whereClause = implode(' AND ', $where);
        
        $sql = "SELECT * FROM tasks 
                WHERE {$whereClause}
                ORDER BY {$sortBy} {$sortOrder}
                LIMIT :limit OFFSET :offset";
        
        $params['limit'] = $limit;
        $params['offset'] = $offset;
        
        return $this->db->fetchAll($sql, $params);
    }
    
    public function countWithFilters(array $filters): int {
        $where = ['1=1'];
        $params = [];
        
        // Same filter logic as findWithFilters
        if (!empty($filters['status'])) {
            $where[] = 'status = :status';
            $params['status'] = $filters['status'];
        }
        
        if (!empty($filters['task_type'])) {
            $where[] = 'task_type_id IN (
                SELECT id FROM task_types WHERE name LIKE :task_type
            )';
            $params['task_type'] = $filters['task_type'];
        }
        
        if (isset($filters['priority_min'])) {
            $where[] = 'priority >= :priority_min';
            $params['priority_min'] = $filters['priority_min'];
        }
        
        if (isset($filters['priority_max'])) {
            $where[] = 'priority <= :priority_max';
            $params['priority_max'] = $filters['priority_max'];
        }
        
        $whereClause = implode(' AND ', $where);
        
        $sql = "SELECT COUNT(*) as count FROM tasks WHERE {$whereClause}";
        $result = $this->db->fetchOne($sql, $params);
        
        return (int)$result['count'];
    }
}
```

### Route Registration (config/routes.php)

```php
// Task Routes
$router->post('/api/tasks', [TaskController::class, 'create']);
$router->get('/api/tasks', [TaskController::class, 'list']);
$router->get('/api/tasks/{id}', [TaskController::class, 'getById']);
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] POST `/api/tasks` creates new tasks
- [ ] POST `/api/tasks` returns existing task if dedupe key matches
- [ ] Deduplication works correctly (same type + params = same dedupe key)
- [ ] Task parameters validated against task type schema
- [ ] Invalid parameters rejected with clear error messages
- [ ] GET `/api/tasks` lists tasks with filters
- [ ] GET `/api/tasks/{id}` returns task details
- [ ] Filtering by status, task_type, priority works
- [ ] Pagination (limit/offset) works correctly
- [ ] Sorting by created_at, priority works

### Non-Functional Requirements
- [ ] Task creation completes in <30ms (p95)
- [ ] Task retrieval completes in <10ms (p95)
- [ ] List tasks completes in <50ms (p95)
- [ ] Dedupe key generation is deterministic
- [ ] Database queries use proper indexes

### Testing
- [ ] Unit tests for TaskService (>80% coverage)
- [ ] Unit tests for DeduplicationService
- [ ] Integration tests for all 3 endpoints
- [ ] Test deduplication with various parameter orders
- [ ] Test deduplication with nested objects
- [ ] Test parameter validation
- [ ] Test filtering and sorting
- [ ] Test pagination

### Documentation
- [ ] API documentation updated with examples
- [ ] Deduplication algorithm documented
- [ ] README includes task creation guide

---

## Testing Strategy

### Unit Tests

```php
class DeduplicationServiceTest extends TestCase {
    public function testGenerateKeyIsDeterministic() {
        $service = new DeduplicationService();
        
        $params1 = ['video_id' => 'abc123', 'quality' => 'hd'];
        $params2 = ['quality' => 'hd', 'video_id' => 'abc123']; // Different order
        
        $key1 = $service->generateKey('youtube_video_scrape', $params1);
        $key2 = $service->generateKey('youtube_video_scrape', $params2);
        
        $this->assertEquals($key1, $key2);
    }
    
    public function testGenerateKeyWithNestedObjects() {
        $service = new DeduplicationService();
        
        $params1 = [
            'user' => ['name' => 'John', 'age' => 30],
            'filters' => ['active' => true]
        ];
        
        $params2 = [
            'filters' => ['active' => true],
            'user' => ['age' => 30, 'name' => 'John']
        ];
        
        $key1 = $service->generateKey('test_task', $params1);
        $key2 = $service->generateKey('test_task', $params2);
        
        $this->assertEquals($key1, $key2);
    }
    
    public function testDifferentTaskTypesDifferentKeys() {
        $service = new DeduplicationService();
        
        $params = ['video_id' => 'abc123'];
        
        $key1 = $service->generateKey('youtube_video_scrape', $params);
        $key2 = $service->generateKey('youtube_search', $params);
        
        $this->assertNotEquals($key1, $key2);
    }
}

class TaskServiceTest extends TestCase {
    public function testCreateTaskSuccess() {
        $service = new TaskService($mockTaskRepo, $mockTypeRepo, $mockValidator, $mockDedupe);
        
        $result = $service->createTask('test_task', ['param1' => 'value1']);
        
        $this->assertFalse($result['was_duplicate']);
        $this->assertEquals('test_task', $result['task']['task_type']);
    }
    
    public function testCreateTaskDeduplicated() {
        // Mock existing task
        $mockTaskRepo->method('findByDedupeKey')->willReturn(['id' => 100, 'status' => 'pending']);
        
        $service = new TaskService($mockTaskRepo, $mockTypeRepo, $mockValidator, $mockDedupe);
        
        $result = $service->createTask('test_task', ['param1' => 'value1']);
        
        $this->assertTrue($result['was_duplicate']);
        $this->assertEquals(100, $result['task']['id']);
    }
    
    public function testCreateTaskInvalidParams() {
        $this->expectException(\InvalidArgumentException::class);
        
        $mockValidator->method('validate')->willReturn(['error1', 'error2']);
        
        $service = new TaskService($mockTaskRepo, $mockTypeRepo, $mockValidator, $mockDedupe);
        $service->createTask('test_task', ['invalid' => 'params']);
    }
}
```

### Integration Tests

```php
class TaskEndpointTest extends IntegrationTestCase {
    public function testCreateTask() {
        // First register task type
        $this->registerTaskType('youtube_video_scrape');
        
        // Create task
        $response = $this->post('/api/tasks', [
            'task_type' => 'youtube_video_scrape',
            'params' => ['video_id' => 'dQw4w9WgXcQ'],
            'priority' => 5
        ]);
        
        $this->assertEquals(201, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['success']);
        $this->assertFalse($data['was_duplicate']);
        $this->assertArrayHasKey('dedupe_key', $data['task']);
    }
    
    public function testCreateDuplicateTask() {
        $this->registerTaskType('youtube_video_scrape');
        
        // Create first task
        $response1 = $this->post('/api/tasks', [
            'task_type' => 'youtube_video_scrape',
            'params' => ['video_id' => 'dQw4w9WgXcQ']
        ]);
        $task1 = json_decode($response1->getBody(), true)['task'];
        
        // Create duplicate
        $response2 = $this->post('/api/tasks', [
            'task_type' => 'youtube_video_scrape',
            'params' => ['video_id' => 'dQw4w9WgXcQ']
        ]);
        
        $this->assertEquals(200, $response2->getStatusCode());
        $data = json_decode($response2->getBody(), true);
        $this->assertTrue($data['was_duplicate']);
        $this->assertEquals($task1['id'], $data['task']['id']);
    }
    
    public function testListTasks() {
        $this->createMultipleTasks();
        
        $response = $this->get('/api/tasks?status=pending&limit=10');
        
        $this->assertEquals(200, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['success']);
        $this->assertIsArray($data['tasks']);
        $this->assertArrayHasKey('pagination', $data);
    }
    
    public function testGetTaskById() {
        $task = $this->createTask();
        
        $response = $this->get("/api/tasks/{$task['id']}");
        
        $this->assertEquals(200, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['success']);
        $this->assertEquals($task['id'], $data['task']['id']);
        $this->assertArrayHasKey('params', $data['task']);
    }
}
```

---

## Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| Create Task | <30ms (p95) | Includes validation + dedupe check |
| Get Task | <10ms (p95) | Simple indexed query |
| List Tasks | <50ms (p95) | With filters and pagination |
| Dedupe Check | <5ms (p95) | Indexed dedupe_key lookup |
| Param Validation | <10ms (p95) | JSON Schema validation |

---

## Deduplication Algorithm

### Key Generation
```
dedupe_key = SHA256(task_type + ":" + JSON(sorted_params))
```

### Process
1. Sort all parameter keys recursively
2. Generate deterministic JSON (no whitespace)
3. Concatenate task type + sorted JSON
4. Hash with SHA-256
5. Store 64-character hex string

### Example
```php
Task Type: youtube_video_scrape
Params: {"video_id": "abc123", "quality": "hd"}

Sorted: {"quality": "hd", "video_id": "abc123"}
Data: youtube_video_scrape:{"quality":"hd","video_id":"abc123"}
Key: a1b2c3d4e5f6789...
```

---

## SOLID Principles Validation

### Single Responsibility Principle (SRP) ✅
- **TaskController**: HTTP handling only
- **TaskService**: Business logic only
- **DeduplicationService**: Dedupe key generation only
- **TaskRepository**: Database operations only

### Open/Closed Principle (OCP) ✅
- Can add new filters without modifying core logic
- Deduplication strategy can be extended

### Liskov Substitution Principle (LSP) ✅
- Repository interface allows swapping implementations
- Validator interface allows different validation strategies

### Interface Segregation Principle (ISP) ✅
- Separate interfaces for each concern
- No God interfaces

### Dependency Inversion Principle (DIP) ✅
- All dependencies injected
- Depends on abstractions, not concrete implementations

---

## Security Considerations

### Authentication
- All endpoints require API key
- Verified via AuthMiddleware

### Input Validation
- Task type must exist
- Params validated against JSON Schema
- Priority and max_attempts have sensible limits

### SQL Injection Prevention
- All queries use prepared statements
- Parameters properly escaped

### Rate Limiting
- Standard rate limits apply (100 req/min per API key)

---

## Dependencies

### Depends On (Blocked By)
- #001 - API Foundation
- #003 - Task Type Registration (must register types first)
- #008 - Database Schema (tasks table)

### Blocks
- #005 - Task Claiming (needs tasks to claim)
- All worker implementations (workers create tasks)

---

## Related Issues
- #005 - Task Claiming
- #006 - Task Completion
- #009 - Enhanced JSON Schema Validation
- #010 - Worker Coordination

---

## Definition of Done

- [ ] All 3 endpoints implemented and working
- [ ] Deduplication working correctly
- [ ] Unit tests written with >80% coverage
- [ ] Integration tests passing
- [ ] Parameter validation working
- [ ] Filtering and pagination working
- [ ] Performance targets met
- [ ] Code reviewed by Developer10
- [ ] SOLID principles validated
- [ ] Security review passed
- [ ] Can create YouTube, Reddit, and Audio tasks
- [ ] Deduplication tested with 10+ concurrent developers

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 2-3 days  
**Assignee**: Developer02  
**Reviewer**: Developer10
