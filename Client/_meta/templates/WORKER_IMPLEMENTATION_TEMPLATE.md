# [Worker Name/Type] Implementation Guide

**Version**: [X.Y.Z]  
**Last Updated**: [YYYY-MM-DD]  
**Worker Type**: [Background Worker / Task Processor / Service Worker / Scheduled Worker]

---

## Table of Contents

- [Overview](#overview)
- [Worker Responsibilities](#worker-responsibilities)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Implementation](#implementation)
- [Configuration](#configuration)
- [Task Processing](#task-processing)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide explains how to implement a [Worker Type] that [brief description of what the worker does].

### What is a Worker?

A worker is a background process that:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

### Why Use This Worker?

- ✅ [Benefit 1]
- ✅ [Benefit 2]
- ✅ [Benefit 3]

### Worker Lifecycle

```
Start → Initialize → Poll for Tasks → Process Task → Report Results → Repeat or Shutdown
```

---

## Worker Responsibilities

### Primary Responsibilities

1. **[Responsibility 1]**: [Description]
2. **[Responsibility 2]**: [Description]
3. **[Responsibility 3]**: [Description]

### Task Types Handled

| Task Type | Description | Priority | Frequency |
|-----------|-------------|----------|-----------|
| `task.type.1` | [Description] | High | [X per hour] |
| `task.type.2` | [Description] | Medium | [Y per hour] |
| `task.type.3` | [Description] | Low | [Z per hour] |

### What This Worker Does NOT Do

- ❌ [Not responsible for X]
- ❌ [Not responsible for Y]
- ❌ [Not responsible for Z]

---

## Architecture

### System Architecture

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Task       │────────▶│   Worker     │────────▶│   Result     │
│   Queue      │         │   Process    │         │   Store      │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                        │
       │                        │                        │
       └────────────────────────┴────────────────────────┘
                        Monitoring & Logging
```

### Worker Components

```
Worker Process
├── Task Poller       # Fetches tasks from queue
├── Task Processor    # Executes task logic
├── Error Handler     # Manages failures and retries
├── Result Reporter   # Reports task completion
└── Health Monitor    # Reports worker health
```

### Data Flow

1. **Task Polling**: Worker polls queue for available tasks
2. **Task Claim**: Worker claims a task for processing
3. **Task Execution**: Worker executes task logic
4. **Result Storage**: Worker stores task results
5. **Task Completion**: Worker marks task as complete

---

## Prerequisites

### System Requirements

- **Runtime**: [Language/Runtime] [Version] (e.g., PHP 8.0+, Python 3.8+, Node.js 16+)
- **Memory**: [Minimum RAM] (e.g., 512MB)
- **CPU**: [Minimum cores]
- **Disk**: [Minimum storage]

### Dependencies

**Required Libraries**:
```bash
# Node.js example
npm install axios dotenv

# Python example
pip install requests python-dotenv

# PHP example
composer require guzzlehttp/guzzle vlucas/phpdotenv
```

### API Access

- [ ] Access to Task Queue API
- [ ] API credentials/tokens
- [ ] Network access to required services

### Configuration Files

- [ ] `.env` file with configuration
- [ ] Worker configuration file
- [ ] Logging configuration

---

## Implementation

### Basic Worker Structure

**Node.js Example**:
```javascript
const axios = require('axios');
require('dotenv').config();

class Worker {
  constructor(config) {
    this.apiUrl = config.apiUrl;
    this.apiKey = config.apiKey;
    this.pollingInterval = config.pollingInterval || 5000;
    this.running = false;
  }

  async start() {
    console.log('Worker starting...');
    this.running = true;
    
    while (this.running) {
      try {
        await this.poll();
      } catch (error) {
        console.error('Polling error:', error);
        await this.sleep(this.pollingInterval);
      }
    }
  }

  async poll() {
    // 1. Fetch available task
    const task = await this.claimTask();
    
    if (!task) {
      // No tasks available, wait before next poll
      await this.sleep(this.pollingInterval);
      return;
    }

    // 2. Process task
    try {
      const result = await this.processTask(task);
      await this.completeTask(task.id, result);
    } catch (error) {
      await this.failTask(task.id, error);
    }
  }

  async claimTask() {
    try {
      const response = await axios.post(
        `${this.apiUrl}/tasks/claim`,
        { worker_id: this.getWorkerId() },
        { headers: { 'Authorization': `Bearer ${this.apiKey}` } }
      );
      
      return response.data.task;
    } catch (error) {
      if (error.response?.status === 404) {
        return null;  // No tasks available
      }
      throw error;
    }
  }

  async processTask(task) {
    console.log(`Processing task ${task.id}...`);
    
    // Implement your task processing logic here
    const result = await this.executeTaskLogic(task);
    
    return result;
  }

  async executeTaskLogic(task) {
    // TODO: Implement specific task logic based on task type
    switch (task.type) {
      case 'task.type.1':
        return await this.handleType1(task);
      case 'task.type.2':
        return await this.handleType2(task);
      default:
        throw new Error(`Unknown task type: ${task.type}`);
    }
  }

  async completeTask(taskId, result) {
    await axios.post(
      `${this.apiUrl}/tasks/${taskId}/complete`,
      { result },
      { headers: { 'Authorization': `Bearer ${this.apiKey}` } }
    );
    
    console.log(`Task ${taskId} completed`);
  }

  async failTask(taskId, error) {
    await axios.post(
      `${this.apiUrl}/tasks/${taskId}/fail`,
      { error: error.message, stack: error.stack },
      { headers: { 'Authorization': `Bearer ${this.apiKey}` } }
    );
    
    console.error(`Task ${taskId} failed:`, error.message);
  }

  getWorkerId() {
    return process.env.WORKER_ID || `worker-${process.pid}`;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  stop() {
    console.log('Worker stopping...');
    this.running = false;
  }
}

// Start worker
const worker = new Worker({
  apiUrl: process.env.API_URL,
  apiKey: process.env.API_KEY,
  pollingInterval: parseInt(process.env.POLLING_INTERVAL) || 5000
});

worker.start();

// Graceful shutdown
process.on('SIGTERM', () => worker.stop());
process.on('SIGINT', () => worker.stop());
```

**PHP Example**:
```php
<?php
require 'vendor/autoload.php';

use GuzzleHttp\Client;

class Worker {
    private $client;
    private $apiUrl;
    private $apiKey;
    private $pollingInterval;
    private $running = false;

    public function __construct($config) {
        $this->apiUrl = $config['api_url'];
        $this->apiKey = $config['api_key'];
        $this->pollingInterval = $config['polling_interval'] ?? 5;
        
        $this->client = new Client([
            'base_uri' => $this->apiUrl,
            'timeout' => 30,
            'headers' => [
                'Authorization' => 'Bearer ' . $this->apiKey,
                'Content-Type' => 'application/json'
            ]
        ]);
    }

    public function start() {
        echo "Worker starting...\n";
        $this->running = true;
        
        while ($this->running) {
            try {
                $this->poll();
            } catch (Exception $e) {
                error_log("Polling error: " . $e->getMessage());
                sleep($this->pollingInterval);
            }
        }
    }

    private function poll() {
        // Claim a task
        $task = $this->claimTask();
        
        if (!$task) {
            sleep($this->pollingInterval);
            return;
        }

        // Process task
        try {
            $result = $this->processTask($task);
            $this->completeTask($task['id'], $result);
        } catch (Exception $e) {
            $this->failTask($task['id'], $e);
        }
    }

    private function claimTask() {
        try {
            $response = $this->client->post('/tasks/claim', [
                'json' => ['worker_id' => $this->getWorkerId()]
            ]);
            
            $data = json_decode($response->getBody(), true);
            return $data['task'] ?? null;
        } catch (GuzzleHttp\Exception\ClientException $e) {
            if ($e->getResponse()->getStatusCode() === 404) {
                return null;  // No tasks available
            }
            throw $e;
        }
    }

    private function processTask($task) {
        echo "Processing task {$task['id']}...\n";
        
        // Implement task processing logic
        return $this->executeTaskLogic($task);
    }

    private function executeTaskLogic($task) {
        switch ($task['type']) {
            case 'task.type.1':
                return $this->handleType1($task);
            case 'task.type.2':
                return $this->handleType2($task);
            default:
                throw new Exception("Unknown task type: {$task['type']}");
        }
    }

    private function completeTask($taskId, $result) {
        $this->client->post("/tasks/{$taskId}/complete", [
            'json' => ['result' => $result]
        ]);
        
        echo "Task {$taskId} completed\n";
    }

    private function failTask($taskId, Exception $e) {
        $this->client->post("/tasks/{$taskId}/fail", [
            'json' => [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]
        ]);
        
        error_log("Task {$taskId} failed: " . $e->getMessage());
    }

    private function getWorkerId() {
        return getenv('WORKER_ID') ?: 'worker-' . getmypid();
    }

    public function stop() {
        echo "Worker stopping...\n";
        $this->running = false;
    }
}

// Configuration
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

// Start worker
$worker = new Worker([
    'api_url' => $_ENV['API_URL'],
    'api_key' => $_ENV['API_KEY'],
    'polling_interval' => (int)($_ENV['POLLING_INTERVAL'] ?? 5)
]);

// Handle signals for graceful shutdown
pcntl_signal(SIGTERM, function() use ($worker) {
    $worker->stop();
});
pcntl_signal(SIGINT, function() use ($worker) {
    $worker->stop();
});

$worker->start();
?>
```

**Python Example**:
```python
import os
import time
import signal
import requests
from dotenv import load_dotenv

class Worker:
    def __init__(self, config):
        self.api_url = config['api_url']
        self.api_key = config['api_key']
        self.polling_interval = config.get('polling_interval', 5)
        self.running = False
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        })

    def start(self):
        print("Worker starting...")
        self.running = True
        
        while self.running:
            try:
                self.poll()
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(self.polling_interval)

    def poll(self):
        # Claim a task
        task = self.claim_task()
        
        if not task:
            time.sleep(self.polling_interval)
            return

        # Process task
        try:
            result = self.process_task(task)
            self.complete_task(task['id'], result)
        except Exception as e:
            self.fail_task(task['id'], e)

    def claim_task(self):
        try:
            response = self.session.post(
                f"{self.api_url}/tasks/claim",
                json={'worker_id': self.get_worker_id()}
            )
            response.raise_for_status()
            return response.json().get('task')
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None  # No tasks available
            raise

    def process_task(self, task):
        print(f"Processing task {task['id']}...")
        return self.execute_task_logic(task)

    def execute_task_logic(self, task):
        task_type = task['type']
        
        if task_type == 'task.type.1':
            return self.handle_type1(task)
        elif task_type == 'task.type.2':
            return self.handle_type2(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def complete_task(self, task_id, result):
        self.session.post(
            f"{self.api_url}/tasks/{task_id}/complete",
            json={'result': result}
        )
        print(f"Task {task_id} completed")

    def fail_task(self, task_id, error):
        import traceback
        self.session.post(
            f"{self.api_url}/tasks/{task_id}/fail",
            json={
                'error': str(error),
                'traceback': traceback.format_exc()
            }
        )
        print(f"Task {task_id} failed: {error}")

    def get_worker_id(self):
        return os.getenv('WORKER_ID', f'worker-{os.getpid()}')

    def stop(self):
        print("Worker stopping...")
        self.running = False

# Load environment variables
load_dotenv()

# Create worker
worker = Worker({
    'api_url': os.getenv('API_URL'),
    'api_key': os.getenv('API_KEY'),
    'polling_interval': int(os.getenv('POLLING_INTERVAL', 5))
})

# Graceful shutdown handlers
def signal_handler(signum, frame):
    worker.stop()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Start worker
if __name__ == '__main__':
    worker.start()
```

---

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# API Configuration
API_URL=https://api.example.com/v1
API_KEY=your_api_key_here

# Worker Configuration
WORKER_ID=worker-001
POLLING_INTERVAL=5
MAX_RETRIES=3
TIMEOUT=30

# Logging
LOG_LEVEL=info
LOG_FILE=/var/log/worker.log

# Performance
CONCURRENT_TASKS=1
MEMORY_LIMIT=512M
```

### Configuration File (Optional)

`config.json`:
```json
{
  "worker": {
    "id": "worker-001",
    "polling_interval": 5,
    "max_retries": 3,
    "timeout": 30
  },
  "logging": {
    "level": "info",
    "file": "/var/log/worker.log"
  },
  "performance": {
    "concurrent_tasks": 1,
    "memory_limit": "512M"
  }
}
```

---

## Task Processing

### Task Structure

```json
{
  "id": "task_12345",
  "type": "task.type.1",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "priority": "high",
  "created_at": "2025-11-09T15:00:00Z",
  "claimed_by": "worker-001",
  "claimed_at": "2025-11-09T15:00:05Z"
}
```

### Processing Example

```javascript
async function executeTaskLogic(task) {
  const { type, parameters } = task;
  
  switch (type) {
    case 'send.email':
      return await sendEmail(parameters);
      
    case 'process.image':
      return await processImage(parameters);
      
    case 'generate.report':
      return await generateReport(parameters);
      
    default:
      throw new Error(`Unknown task type: ${type}`);
  }
}

async function sendEmail(params) {
  // Email sending logic
  const { to, subject, body } = params;
  
  // Send email via service
  await emailService.send({ to, subject, body });
  
  return {
    success: true,
    sent_at: new Date().toISOString()
  };
}
```

---

## Error Handling

### Retry Logic

```javascript
async function processWithRetry(task, maxRetries = 3) {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await processTask(task);
    } catch (error) {
      lastError = error;
      console.error(`Attempt ${attempt} failed:`, error.message);
      
      if (attempt < maxRetries) {
        // Exponential backoff
        const delay = Math.pow(2, attempt) * 1000;
        await sleep(delay);
      }
    }
  }
  
  throw new Error(`Task failed after ${maxRetries} attempts: ${lastError.message}`);
}
```

### Error Types

```javascript
class TaskError extends Error {
  constructor(message, type, retryable = false) {
    super(message);
    this.type = type;
    this.retryable = retryable;
  }
}

// Usage
throw new TaskError('Rate limit exceeded', 'RATE_LIMIT', true);
throw new TaskError('Invalid parameters', 'VALIDATION', false);
```

---

## Testing

### Unit Tests

```javascript
const { Worker } = require('./worker');

describe('Worker', () => {
  let worker;
  
  beforeEach(() => {
    worker = new Worker({
      apiUrl: 'http://test-api.com',
      apiKey: 'test-key'
    });
  });
  
  test('should claim task successfully', async () => {
    const task = await worker.claimTask();
    expect(task).toHaveProperty('id');
  });
  
  test('should process task', async () => {
    const task = { id: '123', type: 'test', parameters: {} };
    const result = await worker.processTask(task);
    expect(result).toBeDefined();
  });
});
```

### Integration Tests

```javascript
async function integrationTest() {
  // Start worker
  const worker = new Worker(config);
  
  // Create test task
  const task = await createTestTask();
  
  // Process task
  await worker.poll();
  
  // Verify result
  const result = await getTaskResult(task.id);
  assert(result.status === 'completed');
  
  console.log('Integration test passed ✅');
}
```

---

## Deployment

### Running as a Service

**systemd (Linux)**:

`/etc/systemd/system/worker.service`:
```ini
[Unit]
Description=Task Worker Service
After=network.target

[Service]
Type=simple
User=worker
WorkingDirectory=/opt/worker
ExecStart=/usr/bin/node /opt/worker/worker.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable worker
sudo systemctl start worker
sudo systemctl status worker
```

**Docker**:

`Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .

CMD ["node", "worker.js"]
```

```bash
# Build and run
docker build -t worker .
docker run -d --name worker --env-file .env worker
```

---

## Monitoring

### Health Check Endpoint

```javascript
// Add health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    uptime: process.uptime(),
    tasks_processed: tasksProcessed,
    last_task_at: lastTaskTimestamp
  });
});
```

### Metrics Collection

```javascript
class WorkerMetrics {
  constructor() {
    this.tasksProcessed = 0;
    this.tasksFailed = 0;
    this.averageProcessingTime = 0;
  }
  
  recordSuccess(duration) {
    this.tasksProcessed++;
    this.updateAverageTime(duration);
  }
  
  recordFailure() {
    this.tasksFailed++;
  }
  
  getMetrics() {
    return {
      tasks_processed: this.tasksProcessed,
      tasks_failed: this.tasksFailed,
      success_rate: this.tasksProcessed / (this.tasksProcessed + this.tasksFailed),
      average_time: this.averageProcessingTime
    };
  }
}
```

---

## Best Practices

1. **Graceful Shutdown**: Always handle SIGTERM/SIGINT
2. **Idempotency**: Make task processing idempotent
3. **Timeout Handling**: Set timeouts for long-running tasks
4. **Resource Cleanup**: Clean up resources after task completion
5. **Logging**: Log all important events
6. **Monitoring**: Track metrics and health
7. **Error Handling**: Distinguish between retryable and permanent errors
8. **Testing**: Test error scenarios

---

## Troubleshooting

### Worker Not Processing Tasks

**Check**:
- Worker is running (`ps aux | grep worker`)
- API connectivity (`curl $API_URL/health`)
- Tasks in queue (`curl $API_URL/tasks`)
- Worker logs

### High Memory Usage

**Solutions**:
- Limit concurrent tasks
- Add memory limits
- Fix memory leaks
- Restart worker periodically

---

**Worker Implementation Guide Version**: 1.0  
**Last Updated**: [YYYY-MM-DD]  
**Maintained by**: [Team/Person Name]
