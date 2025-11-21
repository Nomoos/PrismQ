# Issue #006: Task Completion Reporting

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE  
**Reason**: External TaskManager API already implements task completion  
**Alternative**: Python client (Issue #008) will use existing `/tasks/{id}/complete` endpoint

---

## ⚠️ Issue Superseded

This issue was for implementing **PHP API backend task completion**. The external API already handles this. Python client will integrate with existing functionality.

---

## Original (Not Implemented) Overview

## Overview

Implement task completion reporting system that allows workers to report task success or failure, store results, handle retries, and maintain an audit trail. This completes the task lifecycle: create → claim → complete.

---

## Business Context

After a worker claims and processes a task, it needs to:
- Report successful completion with results
- Report failure with error details
- Support automatic retries for transient failures
- Track attempts and prevent infinite retries
- Store results for downstream consumers

**Impact**: Task completion closes the loop, making results available and freeing workers to claim new tasks.

---

## API Specification

### Endpoint: Complete Task
```
POST /api/tasks/{id}/complete
```

#### Authentication
- **Required**: API key via `X-API-Key` header

#### Path Parameters
- `id` - Task ID

#### Request Body (Success)
```json
{
  "worker_id": "worker-youtube-01",
  "success": true,
  "result": {
    "video_title": "Never Gonna Give You Up",
    "views": 1234567890,
    "duration": 213,
    "channel": "RickAstleyVEVO",
    "processed_at": "2025-11-12T10:45:00Z"
  }
}
```

#### Request Body (Failure - Transient)
```json
{
  "worker_id": "worker-youtube-01",
  "success": false,
  "error_message": "Rate limit exceeded",
  "error_code": "RATE_LIMIT",
  "is_retryable": true
}
```

#### Request Body (Failure - Permanent)
```json
{
  "worker_id": "worker-youtube-01",
  "success": false,
  "error_message": "Video not found or private",
  "error_code": "VIDEO_NOT_FOUND",
  "is_retryable": false
}
```

#### Response (200 OK) - Success
```json
{
  "success": true,
  "task": {
    "id": 123,
    "task_type": "youtube_video_scrape",
    "status": "completed",
    "result": {
      "video_title": "Never Gonna Give You Up",
      "views": 1234567890
    },
    "attempts": 1,
    "worker_id": "worker-youtube-01",
    "completed_at": "2025-11-12T10:45:00Z",
    "created_at": "2025-11-12T10:00:00Z",
    "claimed_at": "2025-11-12T10:30:00Z"
  },
  "message": "Task completed successfully"
}
```

#### Response (200 OK) - Failed (Retry Available)
```json
{
  "success": true,
  "task": {
    "id": 123,
    "task_type": "youtube_video_scrape",
    "status": "pending",
    "error_message": "Rate limit exceeded",
    "attempts": 1,
    "max_attempts": 3,
    "worker_id": null,
    "claimed_at": null
  },
  "message": "Task failed, re-queued for retry (attempt 1/3)",
  "will_retry": true
}
```

#### Response (200 OK) - Failed (Max Attempts Reached)
```json
{
  "success": true,
  "task": {
    "id": 123,
    "task_type": "youtube_video_scrape",
    "status": "failed",
    "error_message": "Rate limit exceeded",
    "attempts": 3,
    "max_attempts": 3,
    "completed_at": "2025-11-12T10:50:00Z"
  },
  "message": "Task failed permanently (max attempts reached)",
  "will_retry": false
}
```

#### Response (400 Bad Request) - Invalid Request
```json
{
  "success": false,
  "error": "Missing required field: worker_id",
  "details": []
}
```

#### Response (403 Forbidden) - Wrong Worker
```json
{
  "success": false,
  "error": "Task is claimed by another worker",
  "claimed_by": "worker-youtube-02",
  "requested_by": "worker-youtube-01"
}
```

#### Response (404 Not Found) - Task Not Found
```json
{
  "success": false,
  "error": "Task not found",
  "task_id": 123
}
```

---

## Implementation Requirements

### Controller (src/Controllers/TaskController.php - Enhancement)

```php
<?php
namespace TaskManager\Controllers;

use TaskManager\Core\{Request, Response};
use TaskManager\Services\TaskCompletionService;

class TaskController {
    // ... existing methods ...
    
    private TaskCompletionService $completionService;
    
    /**
     * Complete a claimed task (success or failure)
     */
    public function complete(Request $request): Response {
        $id = (int)$request->getPathParam('id');
        $data = $request->getBody();
        
        // Validate required fields
        if (!isset($data['worker_id']) || !isset($data['success'])) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Missing required fields: worker_id, success'
            ], 400);
        }
        
        try {
            $result = $this->completionService->completeTask(
                $id,
                $data['worker_id'],
                $data['success'],
                $data['result'] ?? null,
                $data['error_message'] ?? null,
                $data['error_code'] ?? null,
                $data['is_retryable'] ?? false
            );
            
            return (new Response())->json([
                'success' => true,
                'task' => $result['task'],
                'message' => $result['message'],
                'will_retry' => $result['will_retry'] ?? false
            ], 200);
            
        } catch (\InvalidArgumentException $e) {
            return (new Response())->json([
                'success' => false,
                'error' => $e->getMessage()
            ], 400);
            
        } catch (\UnauthorizedException $e) {
            return (new Response())->json([
                'success' => false,
                'error' => $e->getMessage(),
                'claimed_by' => $e->getClaimedBy(),
                'requested_by' => $e->getRequestedBy()
            ], 403);
            
        } catch (\NotFoundException $e) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Task not found',
                'task_id' => $id
            ], 404);
            
        } catch (\Exception $e) {
            return (new Response())->json([
                'success' => false,
                'error' => 'Internal server error'
            ], 500);
        }
    }
}
```

### Service (src/Services/TaskCompletionService.php)

```php
<?php
namespace TaskManager\Services;

use TaskManager\Models\{TaskRepository, TaskTypeRepository};
use TaskManager\Core\Database;

class TaskCompletionService {
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
     * Complete a task (success or failure)
     */
    public function completeTask(
        int $taskId,
        string $workerId,
        bool $success,
        ?array $result,
        ?string $errorMessage,
        ?string $errorCode,
        bool $isRetryable
    ): array {
        // 1. Fetch task
        $task = $this->taskRepo->findById($taskId);
        
        if (!$task) {
            throw new \NotFoundException("Task not found: {$taskId}");
        }
        
        // 2. Verify task is claimed by this worker
        if ($task['status'] !== 'claimed') {
            throw new \InvalidArgumentException(
                "Task is not in claimed state (current: {$task['status']})"
            );
        }
        
        if ($task['worker_id'] !== $workerId) {
            $exception = new \UnauthorizedException(
                "Task is claimed by another worker"
            );
            $exception->setClaimedBy($task['worker_id']);
            $exception->setRequestedBy($workerId);
            throw $exception;
        }
        
        // 3. Increment attempts
        $attempts = $task['attempts'] + 1;
        
        // 4. Begin transaction
        $this->db->beginTransaction();
        
        try {
            if ($success) {
                // SUCCESS: Mark as completed
                $this->completeTaskSuccess($taskId, $result, $attempts, $workerId);
                $message = "Task completed successfully";
                $willRetry = false;
                
            } else {
                // FAILURE: Determine if we should retry
                if ($isRetryable && $attempts < $task['max_attempts']) {
                    // Re-queue for retry
                    $this->requeueTaskForRetry($taskId, $errorMessage, $attempts, $workerId);
                    $message = "Task failed, re-queued for retry (attempt {$attempts}/{$task['max_attempts']})";
                    $willRetry = true;
                    
                } else {
                    // Permanent failure (max attempts or not retryable)
                    $this->failTaskPermanently($taskId, $errorMessage, $attempts, $workerId);
                    $reason = $isRetryable ? 'max attempts reached' : 'permanent error';
                    $message = "Task failed permanently ({$reason})";
                    $willRetry = false;
                }
            }
            
            $this->db->commit();
            
            // 5. Fetch updated task
            $updatedTask = $this->taskRepo->findById($taskId);
            
            return [
                'task' => $this->formatTask($updatedTask),
                'message' => $message,
                'will_retry' => $willRetry
            ];
            
        } catch (\Exception $e) {
            $this->db->rollback();
            throw $e;
        }
    }
    
    /**
     * Mark task as successfully completed
     */
    private function completeTaskSuccess(
        int $taskId,
        ?array $result,
        int $attempts,
        string $workerId
    ): void {
        $now = date('Y-m-d H:i:s');
        
        $this->taskRepo->update($taskId, [
            'status' => 'completed',
            'result' => $result ? json_encode($result) : null,
            'attempts' => $attempts,
            'completed_at' => $now,
            'updated_at' => $now
        ]);
        
        $this->logTaskEvent(
            $taskId,
            'completed',
            $workerId,
            'Task completed successfully'
        );
    }
    
    /**
     * Re-queue task for retry
     */
    private function requeueTaskForRetry(
        int $taskId,
        ?string $errorMessage,
        int $attempts,
        string $workerId
    ): void {
        $now = date('Y-m-d H:i:s');
        
        $this->taskRepo->update($taskId, [
            'status' => 'pending',
            'error_message' => $errorMessage,
            'attempts' => $attempts,
            'worker_id' => null,
            'claimed_at' => null,
            'updated_at' => $now
        ]);
        
        $this->logTaskEvent(
            $taskId,
            'retried',
            $workerId,
            "Task failed, re-queued for retry (attempt {$attempts}): {$errorMessage}"
        );
    }
    
    /**
     * Mark task as permanently failed
     */
    private function failTaskPermanently(
        int $taskId,
        ?string $errorMessage,
        int $attempts,
        string $workerId
    ): void {
        $now = date('Y-m-d H:i:s');
        
        $this->taskRepo->update($taskId, [
            'status' => 'failed',
            'error_message' => $errorMessage,
            'attempts' => $attempts,
            'completed_at' => $now,
            'updated_at' => $now
        ]);
        
        $this->logTaskEvent(
            $taskId,
            'failed',
            $workerId,
            "Task failed permanently: {$errorMessage}"
        );
    }
    
    /**
     * Format task for API response
     */
    private function formatTask(array $task): array {
        $taskType = $this->taskTypeRepo->findById($task['task_type_id']);
        
        $formatted = [
            'id' => (int)$task['id'],
            'task_type' => $taskType['name'],
            'status' => $task['status'],
            'attempts' => (int)$task['attempts'],
            'max_attempts' => (int)$task['max_attempts']
        ];
        
        if ($task['result']) {
            $formatted['result'] = json_decode($task['result'], true);
        }
        
        if ($task['error_message']) {
            $formatted['error_message'] = $task['error_message'];
        }
        
        if ($task['worker_id']) {
            $formatted['worker_id'] = $task['worker_id'];
        }
        
        if ($task['claimed_at']) {
            $formatted['claimed_at'] = $task['claimed_at'];
        }
        
        if ($task['completed_at']) {
            $formatted['completed_at'] = $task['completed_at'];
        }
        
        $formatted['created_at'] = $task['created_at'];
        
        return $formatted;
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
     * Update task fields
     */
    public function update(int $id, array $data): bool {
        $fields = [];
        $params = [];
        
        foreach ($data as $key => $value) {
            $fields[] = "{$key} = ?";
            $params[] = $value;
        }
        
        $params[] = $id;
        
        $sql = "UPDATE tasks 
                SET " . implode(', ', $fields) . "
                WHERE id = ?";
        
        $affected = $this->db->execute($sql, $params);
        
        return $affected > 0;
    }
}
```

### Custom Exceptions

```php
<?php
namespace TaskManager\Exceptions;

class NotFoundException extends \Exception {
    // Task not found
}

class UnauthorizedException extends \Exception {
    private ?string $claimedBy = null;
    private ?string $requestedBy = null;
    
    public function setClaimedBy(string $workerId): void {
        $this->claimedBy = $workerId;
    }
    
    public function setRequestedBy(string $workerId): void {
        $this->requestedBy = $workerId;
    }
    
    public function getClaimedBy(): ?string {
        return $this->claimedBy;
    }
    
    public function getRequestedBy(): ?string {
        return $this->requestedBy;
    }
}
```

### Route Registration (config/routes.php)

```php
// Task Completion Route
$router->post('/api/tasks/{id}/complete', [TaskController::class, 'complete']);
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] POST `/api/tasks/{id}/complete` marks task as completed (success)
- [ ] POST `/api/tasks/{id}/complete` re-queues task for retry (transient failure)
- [ ] POST `/api/tasks/{id}/complete` marks task as failed (permanent or max attempts)
- [ ] Success: Result stored, status = completed, completed_at set
- [ ] Retry: Status = pending, worker_id cleared, attempts incremented
- [ ] Failed: Status = failed, error_message stored, completed_at set
- [ ] Attempts counter incremented on each completion
- [ ] Worker verification (only claiming worker can complete)
- [ ] Audit log records all completion events

### Non-Functional Requirements
- [ ] Completion processing <20ms (p95)
- [ ] Result storage supports large JSON (up to 1MB)
- [ ] Error messages truncated if too long (max 1000 chars)
- [ ] Transactional integrity (no partial updates)

### Testing
- [ ] Unit tests for TaskCompletionService (>80% coverage)
- [ ] Integration tests for complete endpoint
- [ ] Test successful completion
- [ ] Test transient failure with retry
- [ ] Test permanent failure
- [ ] Test max attempts reached
- [ ] Test wrong worker attempt
- [ ] Test task not found
- [ ] Test task not in claimed state

### Documentation
- [ ] API documentation updated
- [ ] Retry logic documented
- [ ] README includes completion examples

---

## Testing Strategy

### Unit Tests

```php
class TaskCompletionServiceTest extends TestCase {
    public function testCompleteTaskSuccess() {
        $service = new TaskCompletionService($mockRepo, $mockTypeRepo, $mockDb);
        
        $mockRepo->method('findById')->willReturn([
            'id' => 123,
            'status' => 'claimed',
            'worker_id' => 'worker-01',
            'attempts' => 0,
            'max_attempts' => 3
        ]);
        
        $result = $service->completeTask(
            123,
            'worker-01',
            true,
            ['data' => 'result'],
            null,
            null,
            false
        );
        
        $this->assertEquals('completed', $result['task']['status']);
        $this->assertFalse($result['will_retry']);
    }
    
    public function testCompleteTaskRetry() {
        $service = new TaskCompletionService($mockRepo, $mockTypeRepo, $mockDb);
        
        $mockRepo->method('findById')->willReturn([
            'id' => 123,
            'status' => 'claimed',
            'worker_id' => 'worker-01',
            'attempts' => 0,
            'max_attempts' => 3
        ]);
        
        $result = $service->completeTask(
            123,
            'worker-01',
            false,
            null,
            'Rate limit',
            'RATE_LIMIT',
            true  // is_retryable
        );
        
        $this->assertEquals('pending', $result['task']['status']);
        $this->assertTrue($result['will_retry']);
        $this->assertEquals(1, $result['task']['attempts']);
    }
    
    public function testCompleteTaskMaxAttemptsReached() {
        $service = new TaskCompletionService($mockRepo, $mockTypeRepo, $mockDb);
        
        $mockRepo->method('findById')->willReturn([
            'id' => 123,
            'status' => 'claimed',
            'worker_id' => 'worker-01',
            'attempts' => 2,
            'max_attempts' => 3
        ]);
        
        $result = $service->completeTask(
            123,
            'worker-01',
            false,
            null,
            'Rate limit',
            'RATE_LIMIT',
            true  // is_retryable but max attempts reached
        );
        
        $this->assertEquals('failed', $result['task']['status']);
        $this->assertFalse($result['will_retry']);
        $this->assertEquals(3, $result['task']['attempts']);
    }
    
    public function testCompleteTaskWrongWorker() {
        $this->expectException(\UnauthorizedException::class);
        
        $service = new TaskCompletionService($mockRepo, $mockTypeRepo, $mockDb);
        
        $mockRepo->method('findById')->willReturn([
            'id' => 123,
            'status' => 'claimed',
            'worker_id' => 'worker-01'
        ]);
        
        // Different worker tries to complete
        $service->completeTask(123, 'worker-02', true, [], null, null, false);
    }
}
```

### Integration Tests

```php
class TaskCompletionEndpointTest extends IntegrationTestCase {
    public function testCompleteTaskSuccess() {
        // Create and claim a task
        $task = $this->createAndClaimTask('worker-01');
        
        // Complete it
        $response = $this->post("/api/tasks/{$task['id']}/complete", [
            'worker_id' => 'worker-01',
            'success' => true,
            'result' => ['video_title' => 'Test Video']
        ]);
        
        $this->assertEquals(200, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['success']);
        $this->assertEquals('completed', $data['task']['status']);
        $this->assertArrayHasKey('result', $data['task']);
    }
    
    public function testCompleteTaskRetry() {
        $task = $this->createAndClaimTask('worker-01');
        
        // Fail with retry
        $response = $this->post("/api/tasks/{$task['id']}/complete", [
            'worker_id' => 'worker-01',
            'success' => false,
            'error_message' => 'Rate limit exceeded',
            'is_retryable' => true
        ]);
        
        $data = json_decode($response->getBody(), true);
        $this->assertTrue($data['will_retry']);
        $this->assertEquals('pending', $data['task']['status']);
        $this->assertEquals(1, $data['task']['attempts']);
        
        // Verify task can be claimed again
        $claimResponse = $this->post('/api/tasks/claim', [
            'worker_id' => 'worker-02'
        ]);
        $this->assertEquals(200, $claimResponse->getStatusCode());
    }
    
    public function testCompleteTaskWrongWorker() {
        $task = $this->createAndClaimTask('worker-01');
        
        // Different worker tries to complete
        $response = $this->post("/api/tasks/{$task['id']}/complete", [
            'worker_id' => 'worker-02',
            'success' => true,
            'result' => []
        ]);
        
        $this->assertEquals(403, $response->getStatusCode());
        $data = json_decode($response->getBody(), true);
        $this->assertFalse($data['success']);
        $this->assertEquals('worker-01', $data['claimed_by']);
    }
}
```

---

## Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| Complete Task | <20ms (p95) | Includes update + audit log |
| Status Update | <5ms | Simple indexed update |
| Audit Log Insert | <3ms | Single INSERT |
| Result Storage | <10ms | Even with large JSON |

---

## Retry Logic Flow

```
Task Completion Request
    ↓
Is Success = true?
    ↓ YES
    ├─> Set status = 'completed'
    ├─> Store result
    ├─> Set completed_at
    └─> Log 'completed' event
    
    ↓ NO
    ├─> Increment attempts
    ├─> Is Retryable AND attempts < max_attempts?
    │   ↓ YES (Transient Failure)
    │   ├─> Set status = 'pending'
    │   ├─> Clear worker_id and claimed_at
    │   ├─> Store error_message
    │   └─> Log 'retried' event
    │   
    │   ↓ NO (Permanent Failure)
    │   ├─> Set status = 'failed'
    │   ├─> Store error_message
    │   ├─> Set completed_at
    │   └─> Log 'failed' event
```

---

## SOLID Principles Validation

### Single Responsibility Principle (SRP) ✅
- **TaskCompletionService**: Only handles completion logic
- Clear separation: success, retry, permanent failure

### Open/Closed Principle (OCP) ✅
- Can extend with custom retry strategies
- Can add result processors without modifying core

### Liskov Substitution Principle (LSP) ✅
- Repository interface allows swapping implementations

### Interface Segregation Principle (ISP) ✅
- Focused completion interface
- Separate from claiming and creation

### Dependency Inversion Principle (DIP) ✅
- Service depends on Repository interface
- Database abstraction

---

## Security Considerations

### Authentication
- API key required

### Authorization
- Only the worker that claimed the task can complete it
- Worker ID verification prevents unauthorized completion

### Input Validation
- Result JSON validated (max size 1MB)
- Error messages sanitized and truncated
- Worker ID format validated

### Audit Trail
- All completions logged with worker ID and timestamp

---

## Dependencies

### Depends On (Blocked By)
- #001 - API Foundation
- #005 - Task Claiming (must claim before completing)
- #008 - Database Schema

### Blocks
- All worker implementations (workers need to complete tasks)
- Result consumer services (need completed tasks with results)

---

## Related Issues
- #005 - Task Claiming
- #010 - Worker Coordination (stale task handling)
- #008 - Database Schema

---

## Definition of Done

- [ ] POST `/api/tasks/{id}/complete` endpoint implemented
- [ ] Success completion works (result stored, status updated)
- [ ] Retry logic works (transient failures re-queued)
- [ ] Permanent failure logic works (max attempts or non-retryable)
- [ ] Worker verification works (403 for wrong worker)
- [ ] Attempts counter increments correctly
- [ ] Unit tests written with >80% coverage
- [ ] Integration tests passing
- [ ] Performance targets met (<20ms p95)
- [ ] Code reviewed by Developer10
- [ ] SOLID principles validated
- [ ] Security review passed
- [ ] Audit logging working
- [ ] Can handle 1MB+ result JSON

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 1-2 days  
**Assignee**: Developer02  
**Reviewer**: Developer10
