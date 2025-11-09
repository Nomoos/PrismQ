# Worker Integration Guide

Complete guide for implementing and deploying workers that integrate with the PrismQ TaskManager system.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Worker Architecture](#worker-architecture)
4. [Implementation Patterns](#implementation-patterns)
5. [Configuration](#configuration)
6. [Task Processing](#task-processing)
7. [Error Handling](#error-handling)
8. [Production Deployment](#production-deployment)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

## Overview

Workers are distributed task processors that integrate with the TaskManager API to:

- Poll for pending tasks
- Claim tasks atomically
- Process tasks with custom business logic
- Report results back to TaskManager
- Handle failures and retries

### Key Concepts

- **TaskManager API**: Central queue system managing tasks
- **Worker**: Independent process that claims and processes tasks
- **Task**: Unit of work with type, parameters, and result
- **Atomic Claiming**: Ensures only one worker processes each task
- **Idempotency**: Tasks can be retried safely

## Getting Started

### 1. Choose a Worker Implementation

We provide ready-to-use workers in multiple languages:

| Language | Best For | Documentation |
|----------|----------|---------------|
| **Python** | General purpose, data processing, ML | [Python Guide](./python/INTEGRATION_GUIDE.md) |
| **PHP** | Shared hosting, PHP projects, web apps | [PHP Guide](./php/INTEGRATION_GUIDE.md) |

### 2. Install Prerequisites

**Python:**
```bash
cd python/
pip install -r requirements.txt
```

**PHP:**
```bash
cd php/
# No additional dependencies required
# Just PHP 7.4+ with cURL extension
```

### 3. Configure Worker

Set the TaskManager API URL:

```bash
# Python
python worker.py --api-url=http://localhost:8000/api

# PHP
php worker.php --api-url=http://localhost:8000/api
```

### 4. Run Worker

```bash
# Python
python worker.py --debug

# PHP
php worker.php --debug
```

## Worker Architecture

### System Architecture

```
┌────────────────────────────────────────────────────────┐
│                  TaskManager API                       │
│               (FastAPI + MySQL/SQLite)                 │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Task Queue                                       │ │
│  │ - Create tasks                                   │ │
│  │ - Claim tasks (atomic)                           │ │
│  │ - Track status                                   │ │
│  │ - Store results                                  │ │
│  └──────────────────────────────────────────────────┘ │
└────────────┬──────────────────────────┬────────────────┘
             │                          │
             │ HTTP REST API            │
             │                          │
  ┌──────────▼─────────┐   ┌───────────▼──────────┐
  │  Worker 1          │   │  Worker 2            │
  │  (Python/PHP/etc)  │   │  (Python/PHP/etc)    │
  │                    │   │                      │
  │  ┌──────────────┐  │   │  ┌──────────────┐   │
  │  │ Task Handler │  │   │  │ Task Handler │   │
  │  └──────────────┘  │   │  └──────────────┘   │
  └────────────────────┘   └──────────────────────┘
```

### Worker Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ 1. Initialization                                       │
│    - Load configuration from CLI args or env vars       │
│    - Setup logging (info or debug mode)                │
│    - Register signal handlers (SIGTERM, SIGINT)        │
│    - Initialize worker state                           │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 2. Health Check                                         │
│    - Verify API connectivity (GET /health)             │
│    - Validate configuration                            │
│    - Check external dependencies                       │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 3. Main Loop (while !should_stop)                      │
│    ┌─────────────────────────────────────┐             │
│    │ a. Claim Task                       │             │
│    │    POST /tasks/claim                │             │
│    │    → Returns task or null           │             │
│    └──────────┬──────────────────────────┘             │
│               │                                         │
│    ┌──────────▼──────────────────────────┐             │
│    │ b. Process Task                     │             │
│    │    - Route to handler by type       │             │
│    │    - Execute business logic         │             │
│    │    - Return result/error            │             │
│    └──────────┬──────────────────────────┘             │
│               │                                         │
│    ┌──────────▼──────────────────────────┐             │
│    │ c. Report Result                    │             │
│    │    - Success: POST /tasks/{id}/complete          │
│    │    - Failure: POST /tasks/{id}/fail              │
│    └──────────┬──────────────────────────┘             │
│               │                                         │
│    ┌──────────▼──────────────────────────┐             │
│    │ d. Wait or Continue                 │             │
│    │    - If no task: sleep(poll_interval)            │
│    │    - If task: process immediately   │             │
│    └──────────┘                          │             │
│                                          │             │
└────────────────┬─────────────────────────┘             │
                 │                                         │
┌────────────────▼────────────────────────────────────────┐
│ 4. Graceful Shutdown                                    │
│    - Complete current task                              │
│    - Log final statistics                              │
│    - Clean up resources                                │
│    - Exit with appropriate code                        │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Task Creation (by client)
   Client → POST /tasks
   Body: {type, params}
   → Task created with status='pending'

2. Task Claiming (by worker)
   Worker → POST /tasks/claim
   Body: {worker_id, task_types?}
   → Returns first available task
   → Task status: pending → processing
   → claimed_at timestamp set
   → worker_id assigned

3. Task Processing (by worker)
   Worker → Execute handler for task.type
   → Returns {success, data/message}

4. Task Completion (by worker)
   a. Success:
      Worker → POST /tasks/{id}/complete
      Body: {result}
      → Task status: processing → completed
      → Result stored
   
   b. Failure:
      Worker → POST /tasks/{id}/fail
      Body: {error}
      → Task status: processing → failed
      → Error message stored
```

## Implementation Patterns

### Basic Worker Pattern

All workers follow this pattern:

```
class Worker:
    def __init__(api_url, worker_id, ...):
        # Initialize configuration
        # Setup logging
        # Register signal handlers
    
    def health_check():
        # Verify API connectivity
    
    def claim_task():
        # POST /tasks/claim
        # Return task or null
    
    def process_task(task):
        # Route to handler by task.type
        # Return {success, data/message}
    
    def complete_task(task_id, result):
        # POST /tasks/{id}/complete
    
    def fail_task(task_id, error):
        # POST /tasks/{id}/fail
    
    def run():
        # Main loop
        while not should_stop:
            task = claim_task()
            if task:
                result = process_task(task)
                if result.success:
                    complete_task(task.id, result)
                else:
                    fail_task(task.id, result.message)
            else:
                sleep(poll_interval)
```

### Task Handler Pattern

Handlers process specific task types:

```
function handle_task_type(params):
    try:
        # 1. Validate parameters
        validate(params)
        
        # 2. Perform business logic
        result = do_work(params)
        
        # 3. Return success
        return {
            success: true,
            data: result
        }
    catch error:
        # 4. Return failure
        return {
            success: false,
            message: error.message
        }
```

## Configuration

### Common Configuration Options

All workers support these configuration options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api-url` | string | `http://localhost:8000/api` | TaskManager API base URL |
| `worker-id` | string | Auto-generated | Unique identifier for this worker |
| `task-types` | array/string | All types | Specific task types to process |
| `poll-interval` | integer | 10 | Seconds to wait when no tasks available |
| `max-runs` | integer | 0 (unlimited) | Maximum tasks to process before exit |
| `debug` | boolean | false | Enable verbose debug logging |

### Configuration Methods

**1. Command Line Arguments:**
```bash
python worker.py --api-url=https://api.example.com/api --worker-id=worker-01 --debug
php worker.php --api-url=https://api.example.com/api --worker-id=worker-01 --debug
```

**2. Environment Variables:**
```bash
export TASKMANAGER_API_URL=https://api.example.com/api
export WORKER_ID=worker-01
export DEBUG=true
python worker.py
php worker.php
```

**3. Configuration File:**
```ini
# worker.conf
TASKMANAGER_API_URL=https://api.example.com/api
WORKER_ID=worker-01
POLL_INTERVAL=10
DEBUG=false
```

## Task Processing

### Task Structure

Tasks follow this structure in TaskManager:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "example.echo",
  "status": "pending",
  "params": {
    "message": "Hello, World!",
    "timestamp": "2025-11-07T18:00:00Z"
  },
  "created_at": "2025-11-07T18:00:00Z",
  "claimed_at": null,
  "completed_at": null,
  "worker_id": null,
  "result": null,
  "error": null
}
```

### Task Status Lifecycle

```
pending → processing → completed
                    → failed
```

### Adding Custom Task Types

**Step 1: Define Task Type**

Choose a namespaced task type:
```
your.app.task_name
Examples:
- prismq.youtube.scrape
- myapp.email.send
- analytics.report.generate
```

**Step 2: Implement Handler**

**Python:**
```python
def _handle_custom_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle your custom task type."""
    try:
        # Extract and validate parameters
        required_param = params.get('required_param')
        if not required_param:
            raise ValueError('required_param is missing')
        
        # Perform your business logic
        result = perform_work(required_param)
        
        # Return success
        return {
            'success': True,
            'data': {
                'result': result,
                'processed_at': datetime.now().isoformat()
            },
            'message': 'Task completed successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
```

**PHP:**
```php
function handleCustomTask($params) {
    try {
        // Extract and validate parameters
        if (!isset($params['required_param'])) {
            throw new Exception('required_param is missing');
        }
        
        // Perform your business logic
        $result = performWork($params['required_param']);
        
        // Return success
        return [
            'success' => true,
            'data' => [
                'result' => $result,
                'processed_at' => date('c')
            ],
            'message' => 'Task completed successfully'
        ];
    } catch (Exception $e) {
        return [
            'success' => false,
            'message' => $e->getMessage()
        ];
    }
}
```

**Step 3: Register Handler**

Add routing in `process_task` method:

**Python:**
```python
def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    task_type = task.get('type')
    params = task.get('params', {})
    
    if task_type == 'your.custom.task':
        return self._handle_custom_task(params)
    # ... other handlers
```

**PHP:**
```php
function processTask($task) {
    switch ($task['type']) {
        case 'your.custom.task':
            return handleCustomTask($task['params']);
        // ... other cases
    }
}
```

## Error Handling

### Error Types

1. **Validation Errors**: Invalid parameters
2. **External Service Errors**: API failures, timeouts
3. **Business Logic Errors**: Domain-specific failures
4. **System Errors**: Out of memory, disk full, etc.

### Error Handling Strategy

```
┌─────────────────────────────────────┐
│ Task Processing                     │
└──────────┬──────────────────────────┘
           │
    ┌──────▼──────┐
    │ Try Process │
    └──────┬──────┘
           │
    ┌──────▼──────────────────────┐
    │ Success?                    │
    └──┬──────────────────────┬───┘
       │ Yes                  │ No
       │                      │
┌──────▼──────┐        ┌─────▼────────┐
│ Complete    │        │ Categorize   │
│ Task        │        │ Error        │
└─────────────┘        └─────┬────────┘
                             │
                 ┌───────────┼───────────┐
                 │           │           │
          ┌──────▼──┐  ┌────▼────┐  ┌──▼──────┐
          │Retriable│  │Permanent│  │ System  │
          │  Error  │  │  Error  │  │  Error  │
          └──────┬──┘  └────┬────┘  └──┬──────┘
                 │          │           │
          ┌──────▼──┐  ┌────▼────┐  ┌──▼──────┐
          │ Fail    │  │ Fail    │  │ Fail &  │
          │ Task    │  │ Task    │  │ Exit    │
          └─────────┘  └─────────┘  └─────────┘
```

### Implementing Error Handling

**Python Example:**
```python
def _handle_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Validate parameters
        self._validate_params(params)
        
        # Process task
        result = self._do_work(params)
        
        return {
            'success': True,
            'data': result
        }
        
    except ValidationError as e:
        # Permanent error - bad parameters
        self.logger.error(f"Validation error: {e}")
        return {
            'success': False,
            'message': f'Invalid parameters: {e}'
        }
        
    except ExternalServiceError as e:
        # Retriable error - service temporarily down
        self.logger.warning(f"External service error: {e}")
        return {
            'success': False,
            'message': f'External service unavailable: {e}'
        }
        
    except Exception as e:
        # Unexpected error
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'Internal error: {e}'
        }
```

### Consecutive Error Handling

Workers should track consecutive errors and stop if too many occur:

```python
# In worker main loop
if self.consecutive_errors >= self.max_consecutive_errors:
    self.logger.error("Too many consecutive errors. Exiting.")
    break

# On successful task
self.consecutive_errors = 0

# On error
self.consecutive_errors += 1
```

## Production Deployment

### Deployment Options

1. **Systemd Service** (Linux)
2. **Docker Container**
3. **Docker Compose** (Multiple Workers)
4. **Kubernetes** (Container Orchestration)
5. **Supervisor** (Process Control)
6. **Cron Job** (Periodic Execution)

### Systemd Deployment

Create service file:

```ini
# /etc/systemd/system/taskmanager-worker.service
[Unit]
Description=TaskManager Worker
After=network.target

[Service]
Type=simple
User=worker
WorkingDirectory=/opt/worker
Environment="TASKMANAGER_API_URL=https://api.example.com/api"
Environment="WORKER_ID=worker-prod-01"
ExecStart=/usr/bin/python3 /opt/worker/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Commands:
```bash
sudo systemctl daemon-reload
sudo systemctl enable taskmanager-worker
sudo systemctl start taskmanager-worker
sudo systemctl status taskmanager-worker
sudo journalctl -u taskmanager-worker -f
```

### Docker Deployment

**Python Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY worker.py .
CMD ["python", "worker.py"]
```

**PHP Dockerfile:**
```dockerfile
FROM php:8.2-cli
WORKDIR /app
COPY . .
CMD ["php", "worker.php"]
```

**Run:**
```bash
docker build -t worker .
docker run -d \
  --name worker-01 \
  -e TASKMANAGER_API_URL=https://api.example.com/api \
  -e WORKER_ID=worker-docker-01 \
  --restart unless-stopped \
  worker
```

### Multiple Workers

Run multiple workers for higher throughput:

```bash
# Systemd instances
sudo systemctl start taskmanager-worker@01
sudo systemctl start taskmanager-worker@02
sudo systemctl start taskmanager-worker@03

# Docker Compose scale
docker-compose up -d --scale worker=5

# Kubernetes replica set
kubectl scale deployment worker --replicas=5
```

## Monitoring

### Key Metrics

1. **Worker Health**: Is worker running?
2. **Task Throughput**: Tasks processed per minute
3. **Error Rate**: Failed tasks percentage
4. **Queue Depth**: Pending tasks count
5. **Processing Time**: Average time per task

### Health Checks

Check worker is running:
```bash
# Process check
ps aux | grep worker

# Systemd status
systemctl status taskmanager-worker

# Docker status
docker ps | grep worker
```

### Log Monitoring

Monitor worker logs:
```bash
# Systemd
journalctl -u taskmanager-worker -f

# Docker
docker logs -f worker-01

# File
tail -f /var/log/worker.log
```

### Task Statistics

Query TaskManager for statistics:
```bash
# Pending tasks
curl http://api.example.com/api/tasks?status=pending

# Failed tasks
curl http://api.example.com/api/tasks?status=failed

# Worker performance
curl http://api.example.com/api/workers/{worker_id}/stats
```

## Troubleshooting

### Common Issues

#### Worker Can't Connect to API

**Symptoms:**
- "API health check failed" errors
- Connection refused/timeout errors

**Solutions:**
```bash
# 1. Verify API is running
curl http://localhost:8000/api/health

# 2. Check API URL configuration
echo $TASKMANAGER_API_URL

# 3. Test connectivity
ping api.example.com
telnet api.example.com 8000

# 4. Check firewall rules
sudo ufw status
sudo iptables -L
```

#### Worker Not Claiming Tasks

**Symptoms:**
- "No tasks available" constantly
- Tasks remain in pending status

**Solutions:**
```bash
# 1. Check for pending tasks
curl http://localhost:8000/api/tasks?status=pending

# 2. Verify task types match
# Worker: --task-types="example.echo"
# Tasks: Should have type="example.echo"

# 3. Create test tasks
python test_worker.py --num-tasks=5

# 4. Check worker configuration
python worker.py --debug
```

#### High Error Rate

**Symptoms:**
- Many failed tasks
- Worker exits frequently

**Solutions:**
```bash
# 1. Enable debug logging
python worker.py --debug

# 2. Check task parameters
curl http://localhost:8000/api/tasks/{task_id}

# 3. Review error logs
journalctl -u taskmanager-worker -n 100

# 4. Test handler manually
# Extract task params and test handler function
```

#### Worker Exits Unexpectedly

**Symptoms:**
- Worker stops without completing tasks
- No graceful shutdown logs

**Solutions:**
```bash
# 1. Check system logs
journalctl -xe

# 2. Check for OOM (Out of Memory)
dmesg | grep -i 'out of memory'

# 3. Check disk space
df -h

# 4. Verify worker configuration
# - max_consecutive_errors setting
# - max_runs setting
```

## Best Practices

### Development

1. **Test Locally First**: Always test with local API before production
2. **Use Debug Logging**: Enable debug mode during development
3. **Mock External Services**: Use mocks for external API calls
4. **Write Unit Tests**: Test task handlers independently
5. **Version Control**: Keep worker code in git

### Configuration

1. **Environment Variables**: Use env vars for production config
2. **Secrets Management**: Never commit API keys or passwords
3. **Configuration Validation**: Validate config at startup
4. **Sensible Defaults**: Provide good default values
5. **Documentation**: Document all configuration options

### Error Handling

1. **Specific Exceptions**: Catch specific errors, not generic Exception
2. **Error Messages**: Provide clear, actionable error messages
3. **Logging**: Log errors with context and stack traces
4. **Retry Logic**: Implement exponential backoff for retriable errors
5. **Circuit Breakers**: Stop calling failing services temporarily

### Production

1. **Monitoring**: Set up health checks and alerting
2. **Logging**: Centralize logs (ELK, CloudWatch, etc.)
3. **Graceful Shutdown**: Always handle SIGTERM/SIGINT
4. **Resource Limits**: Set memory and CPU limits
5. **Scaling**: Run multiple workers for redundancy

### Security

1. **HTTPS Only**: Always use HTTPS for API communication
2. **API Authentication**: Implement API key or token auth
3. **Input Validation**: Validate all task parameters
4. **Least Privilege**: Run workers with minimal permissions
5. **Secrets**: Use secret management tools (Vault, AWS Secrets Manager)

### Performance

1. **Connection Pooling**: Reuse HTTP connections
2. **Caching**: Cache frequently accessed data
3. **Batch Processing**: Process multiple tasks when possible
4. **Async I/O**: Use async for I/O-bound tasks
5. **Resource Cleanup**: Always clean up resources (files, connections)

## Additional Resources

- [TaskManager API Reference](../../Backend/TaskManager/docs/API_REFERENCE.md)
- [TaskManager README](../../Backend/TaskManager/README.md)
- [Python Worker Guide](./python/INTEGRATION_GUIDE.md)
- [PHP Worker Guide](./php/INTEGRATION_GUIDE.md)

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
