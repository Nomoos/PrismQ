# Issue #005: Task Claiming Mechanism

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE  
**Reason**: External TaskManager API already implements task claiming  
**Alternative**: Python client (Issue #008) will use existing `/tasks/{id}/claim` endpoint

---

## ⚠️ Issue Superseded

This issue was for implementing **PHP API backend task claiming**. The external API already handles this. Python client will integrate with existing functionality.

---

## Original (Not Implemented) Overview

## Overview

Implement atomic task claiming mechanism that allows workers to claim pending tasks without race conditions. This is critical for coordinating work across 10 concurrent developers, ensuring each task is processed by exactly one worker.

---

## Business Context

With 10 developers working simultaneously across multiple modules, we need a robust claiming system that:
- Prevents double-claiming (two workers claiming the same task)
- Supports prioritization (high-priority tasks claimed first)
- Enables fair distribution (FIFO, priority-based, or load-balanced)
- Tracks worker assignments
- Handles worker failures gracefully

**Impact**: Without atomic claiming, multiple workers could process the same task, wasting resources and potentially causing conflicts.

---

## API Specification

### Endpoint: Claim Task
```
POST /api/tasks/claim
```

#### Authentication
- **Required**: API key via `X-API-Key` header

#### Request Body
```json
{
  "worker_id": "worker-youtube-01",
  "task_types": ["youtube_video_scrape", "youtube_search"],
  "max_attempts_remaining": 1,
  "sort_by": "priority",
  "sort_order": "desc"
}
```

**Parameters**:
- `worker_id` (required): Unique identifier for the worker
- `task_types` (optional): Array of task types to claim (filters by type)
- `max_attempts_remaining` (optional): Only claim tasks with attempts < max_attempts
- `sort_by` (optional): `priority` (default), `created_at`, `random`
- `sort_order` (optional): `desc` (default), `asc`

#### Response (200 OK) - Task Claimed
```json
{
  "success": true,
  "task": {
    "id": 123,
    "task_type": "youtube_video_scrape",
    "status": "claimed",
    "params": {
      "video_id": "dQw4w9WgXcQ",
      "quality": "hd"
    },
    "priority": 5,
    "attempts": 0,
    "max_attempts": 3,
    "worker_id": "worker-youtube-01",
    "claimed_at": "2025-11-12T10:30:00Z",
    "created_at": "2025-11-12T10:00:00Z"
  },
  "message": "Task claimed successfully"
}
```

#### Response (404 Not Found) - No Tasks Available
```json
{
  "success": false,
  "message": "No pending tasks available",
  "filters": {
    "task_types": ["youtube_video_scrape"],
    "max_attempts_remaining": 1
  }
}
```

#### Response (409 Conflict) - Race Condition Detected
```json
{
  "success": false,
  "error": "Task already claimed by another worker",
  "message": "Race condition detected, please retry"
}
```

---

### Endpoint: Get Task Details (Enhanced)
```
GET /api/tasks/{id}
```

Enhanced to include worker and claiming information (already defined in #004, no changes needed).

---

## Implementation Requirements

### Controller (src/Controllers/TaskController.php - Enhancement)

```php
<?php
namespace TaskManager\Controllers;

use TaskManager\Core\{Request, Response};
use TaskManager\Services\TaskClaimingService;

class TaskController {
    // ... existing methods ...
    
    private TaskClaimingService $claimingService;
    
    /**
     * Claim a pending task atomically
     */
    public function claim(Request $request): Response {
        $data = $request->getBody();
        
        // Validate required field
        if (!isset($data['worker_id'])) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Missing required field: worker_id'
            ], 400);
        }
        
        // Validate worker_id format
        if (!preg_match('/^[a-zA-Z0-9_-]+$/', $data['worker_id'])) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Invalid worker_id format'
            ], 400);
        }
        
        try {
            $filters = [
                'task_types' => $data['task_types'] ?? null,
                'max_attempts_remaining' => $data['max_attempts_remaining'] ?? null
            ];
            
            $sortBy = $data['sort_by'] ?? 'priority';
            $sortOrder = $data['sort_order'] ?? 'desc';
            
            $task = $this->claimingService->claimTask(
                $data['worker_id'],
                $filters,
                $sortBy,
                $sortOrder
            );
            
            if (!$task) {
                return (new Response())->json([
                    'success' => false,
                    'message' => 'No pending tasks available',
                    'filters' => $filters
                ], 404);
            }
            
            return (new Response())->json([
                'success' => true,
                'task' => $task,
                'message' => 'Task claimed successfully'
            ], 200);
            
        } catch (\RuntimeException $e) {
            // Race condition detected
            return (new Response())->json([
                'success' => false,
                'error' => 'Task already claimed by another worker',
                'message' => 'Race condition detected, please retry'
            ], 409);
            
        } catch (\Exception $e) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Internal server error'
            ], 500);
        }
    }
}
```

### Service (src/Services/TaskClaimingService.php)

```php
<?php
namespace TaskManager\Services;

use TaskManager\Models\{TaskRepository, TaskTypeRepository};
use TaskManager\Core\Database;

class TaskClaimingService {
    private TaskRepository $taskRepo;
    private TaskTypeRepository $taskTypeRepo;
    private Database $db;
    
    public function __construct(
        TaskRepository $taskRepo,
        TaskTypeRepository $taskTypeRepo,
        Database $db
    ) {
        $this->taskRepo = $taskRepo;
        $this->taskTypeRepo = $taskTypeRepo;
        $this->db = $db;
    }
    
    /**
     * Claim a pending task atomically using database transaction
     */
    public function claimTask(
        string $workerId,
        array $filters,
        string $sortBy,
        string $sortOrder
    ): ?array {
        // Start transaction for atomic operation
        $this->db->beginTransaction();
        
        try {
            // 1. Find a pending task with row lock (SELECT ... FOR UPDATE)
            $task = $this->findAndLockTask($filters, $sortBy, $sortOrder);
            
            if (!$task) {
                $this->db->rollback();
                return null;
            }
            
            // 2. Update task to claimed status
            $now = date('Y-m-d H:i:s');
            $updated = $this->taskRepo->updateStatus($task['id'], [
                'status' => 'claimed',
                'worker_id' => $workerId,
                'claimed_at' => $now,
                'updated_at' => $now
            ], 'pending'); // Only update if still pending (race condition check)
            
            if (!$updated) {
                // Task was claimed by another worker between SELECT and UPDATE
                $this->db->rollback();
                throw new \RuntimeException('Task already claimed by another worker');
            }
            
            // 3. Log claiming event
            $this->logTaskEvent($task['id'], 'claimed', $workerId, 'Task claimed by worker');
            
            // 4. Commit transaction
            $this->db->commit();
            
            // 5. Fetch and return updated task
            $claimedTask = $this->taskRepo->findById($task['id']);
            return $this->formatTask($claimedTask);
            
        } catch (\Exception $e) {
            $this->db->rollback();
            throw $e;
        }
    }
    
    /**
     * Find a pending task and lock it for update
     */
    private function findAndLockTask(
        array $filters,
        string $sortBy,
        string $sortOrder
    ): ?array {
        // Build WHERE clause
        $where = ["status = 'pending'"];
        $params = [];
        
        // Filter by task types
        if (!empty($filters['task_types'])) {
            $typeIds = $this->getTaskTypeIds($filters['task_types']);
            if (empty($typeIds)) {
                return null;
            }
            $placeholders = implode(',', array_fill(0, count($typeIds), '?'));
            $where[] = "task_type_id IN ({$placeholders})";
            $params = array_merge($params, $typeIds);
        }
        
        // Filter by max attempts
        if (isset($filters['max_attempts_remaining'])) {
            $where[] = "attempts < max_attempts - ?";
            $params[] = $filters['max_attempts_remaining'];
        }
        
        $whereClause = implode(' AND ', $where);
        
        // Validate and sanitize sort parameters
        $allowedSortBy = ['priority', 'created_at'];
        if (!in_array($sortBy, $allowedSortBy)) {
            $sortBy = 'priority';
        }
        
        $sortOrder = strtoupper($sortOrder);
        if (!in_array($sortOrder, ['ASC', 'DESC'])) {
            $sortOrder = 'DESC';
        }
        
        // For priority sorting, use priority DESC, created_at ASC (high priority, oldest first)
        // For created_at sorting, use created_at ASC (FIFO)
        $orderBy = $sortBy === 'priority' 
            ? 'priority DESC, created_at ASC'
            : "created_at {$sortOrder}";
        
        // SQLite doesn't support SELECT ... FOR UPDATE, so we use a different approach:
        // 1. Select the task
        // 2. Update with WHERE status='pending' (atomic at database level)
        $sql = "SELECT * FROM tasks 
                WHERE {$whereClause}
                ORDER BY {$orderBy}
                LIMIT 1";
        
        return $this->db->fetchOne($sql, $params);
    }
    
    /**
     * Get task type IDs from names
     */
    private function getTaskTypeIds(array $taskTypeNames): array {
        $ids = [];
        foreach ($taskTypeNames as $name) {
            $taskType = $this->taskTypeRepo->findLatestByName($name);
            if ($taskType) {
                $ids[] = $taskType['id'];
            }
        }
        return $ids;
    }
    
    /**
     * Format task for API response
     */
    private function formatTask(array $task): array {
        $taskType = $this->taskTypeRepo->findById($task['task_type_id']);
        
        return [
            'id' => (int)$task['id'],
            'task_type' => $taskType['name'],
            'status' => $task['status'],
            'params' => json_decode($task['params'], true),
            'priority' => (int)$task['priority'],
            'attempts' => (int)$task['attempts'],
            'max_attempts' => (int)$task['max_attempts'],
            'worker_id' => $task['worker_id'],
            'claimed_at' => $task['claimed_at'],
            'created_at' => $task['created_at']
        ];
    }
    
    /**
     * Log task event for audit trail
     */
    private function logTaskEvent(
        int $taskId,
        string $event,
        string $workerId,
        string $message
    ): void {
        $sql = "INSERT INTO task_logs (task_id, event, worker_id, message, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))";
        
        $this->db->execute($sql, [$taskId, $event, $workerId, $message]);
    }
}
```

### Repository Enhancement (src/Models/TaskRepository.php)

```php
<?php
namespace TaskManager\Models;

class TaskRepository {
    // ... existing methods ...
    
    /**
     * Update task status atomically (only if current status matches)
     * 
     * This prevents race conditions by using optimistic locking:
     * UPDATE only succeeds if status hasn't changed since we checked
     */
    public function updateStatus(
        int $id,
        array $data,
        string $expectedCurrentStatus
    ): bool {
        $fields = [];
        $params = [];
        
        foreach ($data as $key => $value) {
            $fields[] = "{$key} = ?";
            $params[] = $value;
        }
        
        $params[] = $id;
        $params[] = $expectedCurrentStatus;
        
        $sql = "UPDATE tasks 
                SET " . implode(', ', $fields) . "
                WHERE id = ? AND status = ?";
        
        $affected = $this->db->execute($sql, $params);
        
        return $affected > 0;
    }
}
```

### Route Registration (config/routes.php)

```php
// Task Claiming Route
$router->post('/api/tasks/claim', [TaskController::class, 'claim']);
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] POST `/api/tasks/claim` claims a pending task
- [ ] Worker ID is recorded on claimed task
- [ ] Claimed timestamp is recorded
- [ ] Task status changes from `pending` to `claimed`
- [ ] Claiming is atomic (no race conditions)
- [ ] Only pending tasks can be claimed
- [ ] Supports filtering by task types
- [ ] Supports filtering by max attempts
- [ ] Supports sorting by priority (default)
- [ ] Supports sorting by created_at (FIFO)
- [ ] Returns 404 when no tasks available
- [ ] Returns 409 when race condition detected

### Non-Functional Requirements
- [ ] Claiming completes in <10ms (p95) - CRITICAL
- [ ] Handles concurrent claims correctly (10+ workers)
- [ ] No double-claiming under any circumstance
- [ ] Audit log records all claiming events

### Testing
- [ ] Unit tests for TaskClaimingService (>80% coverage)
- [ ] Integration tests for claim endpoint
- [ ] Concurrency tests (10+ workers claiming simultaneously)
- [ ] Race condition tests (verify no double-claiming)
- [ ] Test all filtering options
- [ ] Test all sorting options
- [ ] Performance tests (<10ms claiming)

### Documentation
- [ ] API documentation updated
- [ ] Atomic claiming algorithm documented
- [ ] Race condition handling explained
- [ ] README includes worker claiming guide

---

## Testing Strategy

### Unit Tests

```php
class TaskClaimingServiceTest extends TestCase {
    public function testClaimTaskSuccess() {
        $service = new TaskClaimingService($mockTaskRepo, $mockTypeRepo, $mockDb);
        
        // Mock a pending task
        $mockDb->method('fetchOne')->willReturn([
            'id' => 123,
            'status' => 'pending',
            'task_type_id' => 1
        ]);
        
        $mockTaskRepo->method('updateStatus')->willReturn(true);
        
        $task = $service->claimTask('worker-01', [], 'priority', 'desc');
        
        $this->assertNotNull($task);
        $this->assertEquals(123, $task['id']);
        $this->assertEquals('worker-01', $task['worker_id']);
    }
    
    public function testClaimTaskNoneAvailable() {
        $service = new TaskClaimingService($mockTaskRepo, $mockTypeRepo, $mockDb);
        
        // No tasks available
        $mockDb->method('fetchOne')->willReturn(null);
        
        $task = $service->claimTask('worker-01', [], 'priority', 'desc');
        
        $this->assertNull($task);
    }
    
    public function testClaimTaskRaceCondition() {
        $this->expectException(\RuntimeException::class);
        
        $service = new TaskClaimingService($mockTaskRepo, $mockTypeRepo, $mockDb);
        
        // Task found but update fails (claimed by another worker)
        $mockDb->method('fetchOne')->willReturn(['id' => 123, 'status' => 'pending']);
        $mockTaskRepo->method('updateStatus')->willReturn(false);
        
        $service->claimTask('worker-01', [], 'priority', 'desc');
    }
    
    public function testClaimTaskWithFilters() {
        $service = new TaskClaimingService($mockTaskRepo, $mockTypeRepo, $mockDb);
        
        $filters = [
            'task_types' => ['youtube_video_scrape'],
            'max_attempts_remaining' => 2
        ];
        
        $task = $service->claimTask('worker-01', $filters, 'priority', 'desc');
        
        // Verify SQL query includes filters
        // ... assertions ...
    }
}
```

### Integration Tests

```php
class TaskClaimingEndpointTest extends IntegrationTestCase {
    public function testClaimTask() {
        // Create a pending task
        $task = $this->createTask(['status' => 'pending']);
        
        // Claim it
        $response = $this->post('/api/tasks/claim', [
            'worker_id' => 'worker-01'
        ]);
        
        $this->assertEquals(200, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['success']);
        $this->assertEquals('claimed', $data['task']['status']);
        $this->assertEquals('worker-01', $data['task']['worker_id']);
        $this->assertNotNull($data['task']['claimed_at']);
    }
    
    public function testClaimNoTasksAvailable() {
        // No pending tasks
        $response = $this->post('/api/tasks/claim', [
            'worker_id' => 'worker-01'
        ]);
        
        $this->assertEquals(404, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertFalse($data['success']);
        $this->assertStringContainsString('No pending tasks', $data['message']);
    }
    
    public function testClaimWithTaskTypeFilter() {
        // Create tasks of different types
        $this->createTask(['task_type' => 'youtube_video_scrape', 'status' => 'pending']);
        $this->createTask(['task_type' => 'reddit_post_fetch', 'status' => 'pending']);
        
        // Claim only YouTube tasks
        $response = $this->post('/api/tasks/claim', [
            'worker_id' => 'worker-01',
            'task_types' => ['youtube_video_scrape']
        ]);
        
        $data = json_decode($response->getBody(), true);
        $this->assertEquals('youtube_video_scrape', $data['task']['task_type']);
    }
}
```

### Concurrency Tests

```php
class TaskClaimingConcurrencyTest extends IntegrationTestCase {
    /**
     * Test that 10 workers can claim 10 tasks concurrently without double-claiming
     */
    public function testConcurrentClaimingNoRaceCondition() {
        // Create 10 pending tasks
        for ($i = 0; $i < 10; $i++) {
            $this->createTask(['status' => 'pending']);
        }
        
        // Simulate 10 workers claiming simultaneously
        $workers = [];
        for ($i = 1; $i <= 10; $i++) {
            $workers[] = "worker-{$i}";
        }
        
        $claimedTasks = [];
        $threads = [];
        
        foreach ($workers as $workerId) {
            $threads[] = function() use ($workerId, &$claimedTasks) {
                $response = $this->post('/api/tasks/claim', [
                    'worker_id' => $workerId
                ]);
                
                if ($response->getStatusCode() === 200) {
                    $data = json_decode($response->getBody(), true);
                    $claimedTasks[] = [
                        'task_id' => $data['task']['id'],
                        'worker_id' => $workerId
                    ];
                }
            };
        }
        
        // Execute all threads concurrently (using thread pool or async requests)
        $this->executeParallel($threads);
        
        // Verify: 10 tasks claimed, each by a different worker
        $this->assertCount(10, $claimedTasks);
        
        // Verify: No duplicate task IDs (no double-claiming)
        $taskIds = array_column($claimedTasks, 'task_id');
        $uniqueTaskIds = array_unique($taskIds);
        $this->assertEquals(count($taskIds), count($uniqueTaskIds));
        
        // Verify: Each worker claimed exactly one task
        $workerIds = array_column($claimedTasks, 'worker_id');
        $this->assertEquals(10, count(array_unique($workerIds)));
    }
    
    /**
     * Test that when 10 workers try to claim 5 tasks, exactly 5 succeed
     */
    public function testConcurrentClaimingWithLimitedTasks() {
        // Create only 5 pending tasks
        for ($i = 0; $i < 5; $i++) {
            $this->createTask(['status' => 'pending']);
        }
        
        // 10 workers try to claim
        $results = [];
        $threads = [];
        
        for ($i = 1; $i <= 10; $i++) {
            $workerId = "worker-{$i}";
            $threads[] = function() use ($workerId, &$results) {
                $response = $this->post('/api/tasks/claim', [
                    'worker_id' => $workerId
                ]);
                
                $results[] = [
                    'worker_id' => $workerId,
                    'status_code' => $response->getStatusCode()
                ];
            };
        }
        
        $this->executeParallel($threads);
        
        // Verify: Exactly 5 succeeded (200), 5 failed (404)
        $successful = array_filter($results, fn($r) => $r['status_code'] === 200);
        $failed = array_filter($results, fn($r) => $r['status_code'] === 404);
        
        $this->assertCount(5, $successful);
        $this->assertCount(5, $failed);
    }
}
```

---

## Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| Claim Task | <10ms (p95) | CRITICAL for worker responsiveness |
| Transaction | <5ms | SQLite transactions are very fast |
| Query with Lock | <3ms | Simple indexed query |
| Status Update | <2ms | Single row update |

**Note**: <10ms claiming is essential for supporting 10+ concurrent workers efficiently.

---

## Atomic Claiming Algorithm

### Approach: Optimistic Locking with Transaction

```
1. BEGIN TRANSACTION
2. SELECT task WHERE status='pending' ... LIMIT 1
3. UPDATE task SET status='claimed', worker_id=? 
   WHERE id=? AND status='pending'
4. IF rows_affected = 0:
     ROLLBACK (race condition, task claimed by another worker)
     THROW exception
5. INSERT INTO task_logs (...)
6. COMMIT TRANSACTION
7. RETURN claimed task
```

### Why This Works

1. **Atomic Read-Modify-Write**: Transaction ensures atomicity
2. **Optimistic Locking**: UPDATE checks current status matches expected
3. **Race Condition Detection**: If UPDATE affects 0 rows, another worker got there first
4. **Retry Pattern**: Client can retry on 409 Conflict

### Alternative Approach (For MySQL with FOR UPDATE)

```sql
BEGIN TRANSACTION;

SELECT * FROM tasks 
WHERE status = 'pending'
ORDER BY priority DESC, created_at ASC
LIMIT 1
FOR UPDATE;  -- Row-level lock

UPDATE tasks 
SET status = 'claimed', worker_id = ?, claimed_at = NOW()
WHERE id = ?;

COMMIT;
```

---

## SOLID Principles Validation

### Single Responsibility Principle (SRP) ✅
- **TaskClaimingService**: Only handles task claiming logic
- **TaskRepository**: Only handles database operations
- Clear separation of concerns

### Open/Closed Principle (OCP) ✅
- Can add new claiming strategies without modifying core
- Extensible via strategy pattern

### Liskov Substitution Principle (LSP) ✅
- Repository interface allows swapping implementations
- Service doesn't depend on concrete repository

### Interface Segregation Principle (ISP) ✅
- Focused interface for claiming
- Separate from task creation and completion

### Dependency Inversion Principle (DIP) ✅
- Service depends on Repository interface
- Database abstraction allows SQLite/MySQL swap

---

## Security Considerations

### Authentication
- API key required for claiming
- Worker ID validated (alphanumeric + dash/underscore only)

### Authorization
- Workers can only claim tasks, not modify claimed tasks of other workers
- Future: Add worker authentication/authorization

### Audit Trail
- All claims logged in task_logs table
- Includes worker ID, timestamp, event type

### Rate Limiting
- Standard rate limits apply (100 req/min per API key)
- Prevents worker from monopolizing queue

---

## Dependencies

### Depends On (Blocked By)
- #001 - API Foundation
- #004 - Task Creation (need tasks to claim)
- #008 - Database Schema (tasks table with status, worker_id, claimed_at)

### Blocks
- #006 - Task Completion (workers must claim before completing)
- All worker implementations (workers need to claim tasks)

---

## Related Issues
- #006 - Task Completion
- #010 - Worker Coordination (heartbeat, stale task detection)
- #008 - Database Schema

---

## Edge Cases & Handling

### 1. No Tasks Available
- **Scenario**: Worker tries to claim but queue is empty
- **Response**: 404 with message "No pending tasks available"
- **Recommendation**: Worker should back off (exponential backoff)

### 2. Race Condition
- **Scenario**: Two workers try to claim same task simultaneously
- **Response**: One succeeds (200), other gets 409 Conflict
- **Recommendation**: Client should retry immediately

### 3. Worker Crashes After Claiming
- **Scenario**: Worker claims task but crashes before completing
- **Solution**: Implemented in #010 (Worker Coordination) with:
  - Heartbeat mechanism
  - Stale task detection
  - Auto re-queue after timeout

### 4. Filter Returns No Tasks
- **Scenario**: Worker filters by task_type that has no pending tasks
- **Response**: 404 with filter details
- **Recommendation**: Worker should widen filters or wait

---

## Definition of Done

- [ ] POST `/api/tasks/claim` endpoint implemented
- [ ] Atomic claiming using database transactions
- [ ] Optimistic locking prevents race conditions
- [ ] Worker ID and claimed timestamp recorded
- [ ] Filtering by task types works
- [ ] Filtering by max attempts works
- [ ] Sorting by priority and created_at works
- [ ] Unit tests written with >80% coverage
- [ ] Integration tests passing
- [ ] Concurrency tests passing (10+ workers, no double-claims)
- [ ] Performance target met (<10ms p95)
- [ ] Code reviewed by Developer10
- [ ] SOLID principles validated
- [ ] Security review passed
- [ ] Audit logging working
- [ ] Can support 10 concurrent developers

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 2 days  
**Assignee**: Developer02  
**Reviewer**: Developer10  
**Critical Performance Target**: <10ms claiming (p95)
