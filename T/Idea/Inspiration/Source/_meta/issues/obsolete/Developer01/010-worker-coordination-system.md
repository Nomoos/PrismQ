# Issue #010: Worker Coordination System

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE  
**Reason**: External TaskManager API already implements worker coordination  
**Alternative**: Python client (Issue #008) will use existing coordination features

---

## ⚠️ Issue Superseded

This issue was for implementing **PHP API backend worker coordination**. The external API already handles this. Python client will leverage existing coordination.

---

## Original (Not Implemented) Overview

## Overview

Implement worker coordination system with heartbeat mechanism, stale task detection, and automatic re-queuing of abandoned tasks. This ensures tasks don't get stuck when workers crash or become unresponsive.

---

## Business Context

Workers can fail for many reasons:
- Process crashes
- Network issues
- Server restarts
- Out of memory errors

Without coordination, claimed tasks would remain stuck forever. We need:
- Heartbeat system to detect dead workers
- Automatic task re-queueing
- Worker status tracking
- Graceful shutdown handling

**Impact**: Ensures tasks always complete even if workers fail.

---

## Implementation Requirements

### Worker Heartbeat System

```php
<?php
namespace TaskManager\Services;

use TaskManager\Models\WorkerHeartbeatRepository;

class WorkerCoordinationService {
    private WorkerHeartbeatRepository $heartbeatRepo;
    private int $heartbeatInterval = 30; // seconds
    private int $staleTimeout = 300; // 5 minutes
    
    public function __construct(WorkerHeartbeatRepository $heartbeatRepo) {
        $this->heartbeatRepo = $heartbeatRepo;
    }
    
    /**
     * Register worker heartbeat
     */
    public function sendHeartbeat(string $workerId, array $metadata = []): void {
        $this->heartbeatRepo->upsert([
            'worker_id' => $workerId,
            'last_seen_at' => date('Y-m-d H:i:s'),
            'status' => 'active',
            'metadata' => json_encode($metadata)
        ]);
    }
    
    /**
     * Detect and re-queue stale tasks
     */
    public function requeueStaleTasks(): array {
        $staleWorkers = $this->heartbeatRepo->findStaleWorkers($this->staleTimeout);
        
        $requeuedTasks = [];
        
        foreach ($staleWorkers as $worker) {
            // Find tasks claimed by this worker
            $staleTasks = $this->taskRepo->findByWorkerIdAndStatus(
                $worker['worker_id'],
                'claimed'
            );
            
            foreach ($staleTasks as $task) {
                // Re-queue task
                $this->taskRepo->update($task['id'], [
                    'status' => 'pending',
                    'worker_id' => null,
                    'claimed_at' => null,
                    'updated_at' => date('Y-m-d H:i:s')
                ]);
                
                // Log event
                $this->logTaskEvent(
                    $task['id'],
                    'requeued',
                    null,
                    "Task re-queued due to stale worker: {$worker['worker_id']}"
                );
                
                $requeuedTasks[] = $task['id'];
            }
            
            // Mark worker as stale
            $this->heartbeatRepo->updateStatus($worker['worker_id'], 'stale');
        }
        
        return $requeuedTasks;
    }
    
    /**
     * Get active workers
     */
    public function getActiveWorkers(): array {
        return $this->heartbeatRepo->findActiveWorkers($this->heartbeatInterval * 2);
    }
    
    /**
     * Graceful worker shutdown
     */
    public function shutdownWorker(string $workerId): void {
        // Release any claimed tasks
        $this->taskRepo->releaseWorkerTasks($workerId);
        
        // Mark worker as inactive
        $this->heartbeatRepo->updateStatus($workerId, 'inactive');
    }
}
```

### Database Schema Addition

```sql
-- Worker heartbeats table
CREATE TABLE worker_heartbeats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',     -- active, stale, inactive
    last_seen_at TIMESTAMP NOT NULL,
    metadata TEXT,                            -- JSON worker info
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (status IN ('active', 'stale', 'inactive'))
);

CREATE INDEX idx_worker_heartbeats_worker_id ON worker_heartbeats(worker_id);
CREATE INDEX idx_worker_heartbeats_last_seen ON worker_heartbeats(last_seen_at);
CREATE INDEX idx_worker_heartbeats_status ON worker_heartbeats(status);
```

### Heartbeat Endpoint

```
POST /api/workers/heartbeat
```

**Request Body**:
```json
{
  "worker_id": "worker-youtube-01",
  "metadata": {
    "hostname": "server-01",
    "pid": 12345,
    "version": "1.0.0",
    "tasks_processed": 42
  }
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Heartbeat recorded",
  "next_heartbeat_in": 30
}
```

### Stale Task Checker (Background Job)

```php
<?php
// scripts/check_stale_tasks.php

require_once __DIR__ . '/../vendor/autoload.php';

$coordination = new WorkerCoordinationService($heartbeatRepo);

while (true) {
    // Check for stale tasks every minute
    $requeuedTasks = $coordination->requeueStaleTasks();
    
    if (!empty($requeuedTasks)) {
        echo "[" . date('Y-m-d H:i:s') . "] Re-queued " . count($requeuedTasks) . " stale tasks\n";
    }
    
    sleep(60);
}
```

---

## Worker Implementation Example

```php
<?php
// Example worker with heartbeat

class YouTubeVideoWorker {
    private $coordination;
    private $workerId;
    private $running = true;
    
    public function run(): void {
        // Register signal handlers for graceful shutdown
        pcntl_signal(SIGTERM, [$this, 'handleShutdown']);
        pcntl_signal(SIGINT, [$this, 'handleShutdown']);
        
        $lastHeartbeat = 0;
        
        while ($this->running) {
            // Send heartbeat every 30 seconds
            if (time() - $lastHeartbeat >= 30) {
                $this->coordination->sendHeartbeat($this->workerId, [
                    'hostname' => gethostname(),
                    'pid' => getmypid(),
                    'tasks_processed' => $this->tasksProcessed
                ]);
                $lastHeartbeat = time();
            }
            
            // Claim and process task
            $task = $this->claimTask();
            
            if ($task) {
                $this->processTask($task);
            } else {
                sleep(5); // No tasks, wait
            }
            
            pcntl_signal_dispatch();
        }
        
        // Graceful shutdown
        $this->coordination->shutdownWorker($this->workerId);
    }
    
    public function handleShutdown(): void {
        echo "Received shutdown signal, gracefully exiting...\n";
        $this->running = false;
    }
}
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] POST `/api/workers/heartbeat` records heartbeats
- [ ] Stale worker detection working (no heartbeat for 5 min)
- [ ] Stale tasks automatically re-queued
- [ ] Active workers list available
- [ ] Graceful shutdown releases tasks
- [ ] Background job checks for stale tasks

### Non-Functional Requirements
- [ ] Heartbeat processing <5ms
- [ ] Stale check completes in <100ms
- [ ] Background job runs every 60 seconds

### Testing
- [ ] Unit tests for coordination service
- [ ] Test stale task detection
- [ ] Test task re-queuing
- [ ] Test graceful shutdown

### Documentation
- [ ] Worker implementation guide
- [ ] Heartbeat mechanism documented
- [ ] Graceful shutdown guide

---

## Monitoring Dashboard

### Worker Status View

```sql
CREATE VIEW worker_status AS
SELECT 
    w.worker_id,
    w.status,
    w.last_seen_at,
    COUNT(t.id) as active_tasks,
    ROUND((JULIANDAY('now') - JULIANDAY(w.last_seen_at)) * 24 * 60) as minutes_since_heartbeat
FROM worker_heartbeats w
LEFT JOIN tasks t ON t.worker_id = w.worker_id AND t.status = 'claimed'
GROUP BY w.worker_id, w.status, w.last_seen_at;
```

---

## Definition of Done

- [ ] Heartbeat system implemented
- [ ] Stale task detection working
- [ ] Automatic re-queuing working
- [ ] Background job created
- [ ] Graceful shutdown handling
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Code reviewed by Developer10
- [ ] Documentation complete

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 1-2 days  
**Assignee**: Developer02  
**Reviewer**: Developer10
