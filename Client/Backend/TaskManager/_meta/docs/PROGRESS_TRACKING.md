# Task Progress Tracking - Implementation Guide

**Date**: 2025-11-08  
**Worker**: Worker10 (Integration & Migration)  
**Status**: ✅ Implemented

---

## Overview

The TaskManager now supports real-time progress tracking for long-running tasks. Workers can report progress as a percentage (0-100%) while processing tasks, allowing clients to monitor task execution in real-time.

---

## Features

### Core Capabilities
- **Progress Percentage**: Report task progress from 0-100%
- **Progress Messages**: Optional descriptive messages for each update
- **History Logging**: All progress updates are logged in task history
- **Worker Validation**: Only the worker that claimed a task can update its progress
- **State Validation**: Progress can only be updated for claimed tasks

### Database Schema
- **Column**: `tasks.progress` (INT, default 0)
- **Index**: `idx_progress` for efficient queries
- **Range**: 0-100 (validated at both API and application level)

---

## API Endpoint

### Update Task Progress

**Endpoint**: `POST /tasks/{id}/progress`

**Parameters**:
```json
{
  "worker_id": "string (required)",
  "progress": "integer (required, 0-100)",
  "message": "string (optional)"
}
```

**Success Response** (200):
```json
{
  "success": true,
  "data": {
    "id": 123,
    "progress": 50
  },
  "message": "Task progress updated successfully"
}
```

**Error Responses**:
- `400` - Invalid progress value or task not in claimed state
- `403` - Task is claimed by another worker
- `404` - Task not found

---

## Usage Examples

### PHP Worker

```php
use PrismQ\TaskManager\Worker\WorkerClient;

$client = new WorkerClient($apiUrl, $workerId);

// Claim a task
$task = $client->claimTask();

// Update progress during processing
$client->updateProgress($task['id'], 25, "Processing step 1 of 4");
// ... do some work ...

$client->updateProgress($task['id'], 50, "Processing step 2 of 4");
// ... do some work ...

$client->updateProgress($task['id'], 75, "Processing step 3 of 4");
// ... do some work ...

// Complete the task
$client->completeTask($task['id'], ['result' => 'success']);
```

### Python Worker

```python
from worker import TaskManagerWorker

worker = TaskManagerWorker(api_url, worker_id)

# Claim a task
task = worker.claim_task()

# Update progress during processing
worker.update_progress(task['id'], 25, "Processing step 1 of 4")
# ... do some work ...

worker.update_progress(task['id'], 50, "Processing step 2 of 4")
# ... do some work ...

worker.update_progress(task['id'], 75, "Processing step 3 of 4")
# ... do some work ...

# Complete the task
worker.complete_task(task['id'], {'result': 'success'})
```

### Direct API Call (cURL)

```bash
curl -X POST http://localhost/api/tasks/123/progress \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "worker-001",
    "progress": 50,
    "message": "Processing item 5 of 10"
  }'
```

---

## Example: Long-Running Task with Progress

### PHP Implementation

```php
function handleBatchProcessing(array $params): array
{
    global $client, $currentTaskId;
    
    $items = $params['items'];
    $totalItems = count($items);
    $processedItems = 0;
    
    foreach ($items as $item) {
        // Process the item
        processItem($item);
        $processedItems++;
        
        // Update progress
        $progress = intval(($processedItems / $totalItems) * 100);
        $message = "Processed {$processedItems}/{$totalItems} items";
        
        if ($currentTaskId && $client) {
            try {
                $client->updateProgress($currentTaskId, $progress, $message);
            } catch (Exception $e) {
                // Log but don't fail the task
                error_log("Progress update failed: " . $e->getMessage());
            }
        }
    }
    
    return [
        'processed' => $totalItems,
        'completed_at' => date('c')
    ];
}
```

### Python Implementation

```python
def handle_batch_processing(self, params: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    items = params.get('items', [])
    total_items = len(items)
    processed_items = 0
    
    for item in items:
        # Process the item
        self.process_item(item)
        processed_items += 1
        
        # Update progress
        progress = int((processed_items / total_items) * 100)
        message = f"Processed {processed_items}/{total_items} items"
        
        try:
            self.update_progress(task_id, progress, message)
        except Exception as e:
            # Log but don't fail the task
            self.logger.warning(f"Progress update failed: {e}")
    
    return {
        'success': True,
        'data': {
            'processed': total_items
        },
        'message': 'Batch processing completed'
    }
```

---

## Querying Task Progress

### Get Task with Progress

**Endpoint**: `GET /tasks/{id}`

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "type": "PrismQ.Script.Generate",
    "status": "claimed",
    "progress": 50,
    "priority": 5,
    "attempts": 1,
    "claimed_by": "worker-001",
    "claimed_at": "2025-11-08T10:30:00Z",
    "created_at": "2025-11-08T10:25:00Z",
    "params": {...},
    "result": null
  }
}
```

### List Tasks with Progress

**Endpoint**: `GET /tasks`

**Response**:
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": 123,
        "type": "PrismQ.Script.Generate",
        "status": "claimed",
        "priority": 5,
        "progress": 50,
        "attempts": 1,
        "claimed_by": "worker-001",
        "created_at": "2025-11-08T10:25:00Z",
        "completed_at": null
      }
    ],
    "count": 1,
    "limit": 50,
    "offset": 0
  }
}
```

---

## Database Changes

### Schema Updates

1. **Added Column**:
   ```sql
   ALTER TABLE tasks 
   ADD COLUMN progress INT DEFAULT 0 
   AFTER priority;
   ```

2. **Added Index**:
   ```sql
   ALTER TABLE tasks 
   ADD INDEX idx_progress (progress);
   ```

### Migration

Run the migration:
```bash
mysql -u username -p database_name < Backend/TaskManager/database/migrations/002_add_progress_column.sql
```

Or re-run the full schema setup:
```bash
php Backend/TaskManager/setup_database.php
```

---

## Best Practices

### When to Update Progress

✅ **Good Use Cases**:
- Long-running batch processing (> 30 seconds)
- Multi-step workflows
- File processing (large files)
- Data imports/exports
- Complex calculations

❌ **Avoid**:
- Very short tasks (< 5 seconds)
- Tasks with unpredictable duration
- Too frequent updates (< 1% progress changes)

### Update Frequency

- **Recommended**: Every 5-10% progress or every 10-30 seconds
- **Minimum**: Don't update more than once per second
- **Practical**: Update at meaningful milestones (steps, items, stages)

### Error Handling

Always catch and log progress update errors, but don't fail the task:

```php
try {
    $client->updateProgress($taskId, $progress, $message);
} catch (Exception $e) {
    error_log("Progress update failed: " . $e->getMessage());
    // Continue task processing
}
```

### Progress Messages

Keep messages concise and informative:
- ✅ "Processing item 5 of 10"
- ✅ "Uploading file (50 MB / 100 MB)"
- ✅ "Step 2/4: Validating data"
- ❌ "Still working on it..." (not informative)
- ❌ Very long messages (> 100 characters)

---

## History Logging

All progress updates are logged in `task_history`:

```sql
SELECT * FROM task_history 
WHERE task_id = 123 
AND status_change = 'progress_update'
ORDER BY created_at;
```

Example output:
```
| id  | task_id | status_change    | worker_id  | message                    | created_at          |
|-----|---------|------------------|------------|----------------------------|---------------------|
| 501 | 123     | progress_update  | worker-001 | Progress: 25% - Step 1/4   | 2025-11-08 10:30:00 |
| 502 | 123     | progress_update  | worker-001 | Progress: 50% - Step 2/4   | 2025-11-08 10:30:15 |
| 503 | 123     | progress_update  | worker-001 | Progress: 75% - Step 3/4   | 2025-11-08 10:30:30 |
| 504 | 123     | completed        | worker-001 | Task completed successfully | 2025-11-08 10:30:45 |
```

---

## Monitoring & Observability

### Dashboard Queries

**Tasks in Progress**:
```sql
SELECT id, type, progress, claimed_by, claimed_at
FROM tasks t
JOIN task_types tt ON t.type_id = tt.id
WHERE t.status = 'claimed'
ORDER BY t.claimed_at DESC;
```

**Slow Tasks** (claimed > 5 minutes, progress < 100%):
```sql
SELECT id, type, progress, claimed_by, 
       TIMESTAMPDIFF(MINUTE, claimed_at, NOW()) as minutes_running
FROM tasks t
JOIN task_types tt ON t.type_id = tt.id
WHERE t.status = 'claimed'
  AND t.claimed_at < DATE_SUB(NOW(), INTERVAL 5 MINUTE)
  AND t.progress < 100
ORDER BY minutes_running DESC;
```

**Average Progress by Task Type**:
```sql
SELECT tt.name, 
       AVG(t.progress) as avg_progress,
       COUNT(*) as active_tasks
FROM tasks t
JOIN task_types tt ON t.type_id = tt.id
WHERE t.status = 'claimed'
GROUP BY tt.name;
```

---

## Testing

### Manual Testing

1. **Create a test task**:
   ```bash
   curl -X POST http://localhost/api/tasks \
     -H "Content-Type: application/json" \
     -d '{
       "type": "example.sleep",
       "params": {"seconds": 30}
     }'
   ```

2. **Claim and update progress**:
   ```bash
   # Claim
   curl -X POST http://localhost/api/tasks/claim \
     -H "Content-Type: application/json" \
     -d '{"worker_id": "test-worker", "task_type_id": 1}'
   
   # Update progress
   curl -X POST http://localhost/api/tasks/123/progress \
     -H "Content-Type: application/json" \
     -d '{"worker_id": "test-worker", "progress": 50, "message": "Halfway done"}'
   ```

3. **Check task status**:
   ```bash
   curl http://localhost/api/tasks/123
   ```

### Automated Testing

See `Backend/TaskManager/tests/worker/WorkerTest.php` for test examples.

---

## Troubleshooting

### Common Issues

**Error: "Progress must be between 0 and 100"**
- Check that progress value is an integer
- Ensure progress is not negative or > 100

**Error: "Task is not in claimed state"**
- Task must be claimed before updating progress
- Check task status with GET /tasks/{id}

**Error: "Task is claimed by another worker"**
- Ensure worker_id matches the worker that claimed the task
- Check claimed_by field in task details

**Progress updates not appearing**
- Verify ENABLE_TASK_HISTORY is enabled in config
- Check task_history table for updates
- Verify database connection

---

## Configuration

### Enable/Disable History Logging

In `Backend/TaskManager/config/config.php`:
```php
define('ENABLE_TASK_HISTORY', true);  // Set to false to disable
```

### Adjust Update Validation

Progress validation happens in:
1. API endpoint validation (database-driven)
2. CustomHandlers.php `task_update_progress()` method
3. WorkerClient.php `updateProgress()` method

---

## Future Enhancements

Potential improvements for future versions:

- [ ] Progress ETA calculation based on rate
- [ ] Progress webhooks/notifications
- [ ] Progress percentage in list view by default
- [ ] Progress charts/graphs in admin UI
- [ ] Stalled task detection (no progress for X minutes)

---

## References

- **Database Schema**: `Backend/TaskManager/database/schema.sql`
- **Migration**: `Backend/TaskManager/database/migrations/002_add_progress_column.sql`
- **API Endpoint**: `Backend/TaskManager/database/seed_endpoints.sql`
- **Handler**: `Backend/TaskManager/api/CustomHandlers.php`
- **PHP Client**: `examples/workers/php/WorkerClient.php`
- **Python Client**: `examples/workers/python/worker.py`

---

**Created**: 2025-11-08  
**Worker**: Worker10 (Integration & Migration)  
**Status**: Production Ready
