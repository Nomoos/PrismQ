# PHP Worker Integration Guide

Complete guide for implementing and deploying PHP workers for the TaskManager system.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Worker](#running-the-worker)
6. [Implementing Custom Task Handlers](#implementing-custom-task-handlers)
7. [Error Handling](#error-handling)
8. [Production Deployment](#production-deployment)
9. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
10. [Advanced Usage](#advanced-usage)

## Overview

The PHP worker implementation provides a robust, production-ready solution for processing tasks from the TaskManager API. It includes:

- **Automatic task claiming** from the queue
- **Extensible task handlers** for different task types
- **Comprehensive error handling** with retry logic
- **Graceful shutdown** on signals (SIGTERM, SIGINT)
- **Health checks** and connectivity monitoring
- **Configurable polling** and timeout settings
- **Debug logging** for troubleshooting

### Architecture

```
┌─────────────────┐
│  TaskManager    │
│     API         │
└────────┬────────┘
         │ HTTP REST API
         │
┌────────▼────────┐
│  WorkerClient   │  Helper class for API communication
└────────┬────────┘
         │
┌────────▼────────┐
│   worker.php    │  Main worker loop
│                 │
│  ┌───────────┐  │
│  │  Handler  │  │  Task-specific processing logic
│  │  Function │  │
│  └───────────┘  │
└─────────────────┘
```

## Quick Start

### 1. Basic Usage

```bash
# Navigate to the worker directory
cd examples/workers/php

# Run the worker with default settings
php worker.php --api-url=http://localhost/api
```

### 2. Test with Example Tasks

```bash
# In another terminal, create test tasks using curl
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "example.echo",
    "params": {
      "message": "Hello, World!"
    }
  }'
```

The worker will automatically claim and process the task.

## Installation

### Prerequisites

- **PHP 7.4 or higher** (PHP 8.x recommended)
- **cURL extension** for PHP (`php-curl`)
- **PCNTL extension** (optional, for signal handling)
- **Access to TaskManager API** (local or remote)

### Verify Prerequisites

```bash
# Check PHP version
php --version

# Check required extensions
php -m | grep -E "(curl|pcntl)"

# If missing, install them:
# Ubuntu/Debian:
sudo apt-get install php-curl php-cli

# CentOS/RHEL:
sudo yum install php-curl php-cli

# macOS (with Homebrew):
brew install php
```

### Download Worker Files

If not already present, ensure you have:

1. `worker.php` - Main worker script
2. `WorkerClient.php` - API client helper class

```bash
# Verify files are present
ls -l examples/workers/php/
# Should show: worker.php, WorkerClient.php
```

### Set Permissions

```bash
# Make worker executable
chmod +x examples/workers/php/worker.php
```

## Configuration

The worker can be configured via:
1. **Command line arguments** (highest priority)
2. **Environment variables** (medium priority)
3. **Default values** (lowest priority)

### Configuration Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `--api-url` | `TASKMANAGER_API_URL` | `http://localhost/api` | TaskManager API base URL |
| `--worker-id` | `WORKER_ID` | Auto-generated | Unique worker identifier |
| `--type-pattern` | `TASK_TYPE_PATTERN` | `null` | Filter tasks by type (SQL LIKE pattern) |
| `--poll-interval` | `POLL_INTERVAL` | `10` | Seconds between polls when idle |
| `--max-runs` | `MAX_RUNS` | `0` (unlimited) | Maximum tasks to process before exit |
| `--debug` | `DEBUG` | `false` | Enable debug logging |

### Example Configurations

#### 1. Production Worker

```bash
php worker.php \
  --api-url=https://api.example.com/api \
  --worker-id=prod-worker-01 \
  --type-pattern="PrismQ.%" \
  --poll-interval=5
```

#### 2. Development Worker with Debug

```bash
php worker.php \
  --api-url=http://localhost/api \
  --worker-id=dev-worker \
  --debug
```

#### 3. Using Environment Variables

```bash
export TASKMANAGER_API_URL=https://api.example.com/api
export WORKER_ID=prod-worker-02
export TASK_TYPE_PATTERN="PrismQ.Script.%"
export POLL_INTERVAL=5
export DEBUG=false

php worker.php
```

#### 4. One-Time Task Processing

```bash
# Process exactly 100 tasks then exit
php worker.php --max-runs=100
```

## Running the Worker

### Foreground (Development)

```bash
# Run in foreground with debug output
php worker.php --debug

# Stop with Ctrl+C (graceful shutdown)
```

### Background (Production)

```bash
# Run in background with log file
nohup php worker.php --api-url=https://api.example.com/api > worker.log 2>&1 &

# Save process ID
echo $! > worker.pid

# View logs
tail -f worker.log

# Stop worker (graceful)
kill -TERM $(cat worker.pid)
```

### Using systemd (Recommended for Production)

Create `/etc/systemd/system/taskmanager-worker.service`:

```ini
[Unit]
Description=TaskManager PHP Worker
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/examples/workers/php
ExecStart=/usr/bin/php /path/to/examples/workers/php/worker.php --api-url=https://api.example.com/api
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable taskmanager-worker
sudo systemctl start taskmanager-worker

# View logs
sudo journalctl -u taskmanager-worker -f

# Check status
sudo systemctl status taskmanager-worker

# Stop
sudo systemctl stop taskmanager-worker
```

### Using Supervisor

Create `/etc/supervisor/conf.d/taskmanager-worker.conf`:

```ini
[program:taskmanager-worker]
command=/usr/bin/php /path/to/examples/workers/php/worker.php --api-url=https://api.example.com/api
directory=/path/to/examples/workers/php
autostart=true
autorestart=true
startretries=3
user=www-data
redirect_stderr=true
stdout_logfile=/var/log/taskmanager-worker.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
```

Apply:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start taskmanager-worker

# View status
sudo supervisorctl status

# View logs
sudo tail -f /var/log/taskmanager-worker.log
```

## Implementing Custom Task Handlers

### Basic Structure

The `processTask()` function routes tasks to appropriate handlers based on type:

```php
function processTask($task) {
    $type = $task['type'];
    $params = $task['params'];
    
    switch ($type) {
        case 'your.task.type':
            return handleYourTask($params);
            
        default:
            throw new Exception("Unknown task type: {$type}");
    }
}
```

### Example Handler Implementation

```php
/**
 * Example: Process a script generation task
 */
function handleScriptGeneration($params) {
    // 1. Validate parameters
    if (!isset($params['topic']) || !isset($params['style'])) {
        throw new Exception("Missing required parameters");
    }
    
    $topic = $params['topic'];
    $style = $params['style'];
    $length = $params['length'] ?? 1000;
    
    // 2. Perform the actual work
    $script = generateScript($topic, $style, $length);
    
    // 3. Return result data
    return [
        'script' => $script,
        'word_count' => str_word_count($script),
        'generated_at' => date('c'),
        'metadata' => [
            'topic' => $topic,
            'style' => $style,
            'requested_length' => $length
        ]
    ];
}

function generateScript($topic, $style, $length) {
    // Your actual script generation logic here
    // This could call an AI API, template engine, etc.
    
    return "Generated script about {$topic} in {$style} style...";
}
```

### Handler Best Practices

1. **Validate all inputs** at the start of your handler
2. **Use descriptive exceptions** to help with debugging
3. **Return structured data** as associative arrays
4. **Handle external API failures** gracefully
5. **Use timeouts** for external calls
6. **Log progress** for long-running tasks

### Example: Calling External API

```php
function handleApiTask($params) {
    $url = $params['url'];
    $method = $params['method'] ?? 'GET';
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($error) {
        throw new Exception("API request failed: {$error}");
    }
    
    if ($httpCode >= 400) {
        throw new Exception("API returned error: HTTP {$httpCode}");
    }
    
    return [
        'response' => $response,
        'http_code' => $httpCode,
        'fetched_at' => date('c')
    ];
}
```

### Registering Task Types

Before creating tasks, register the task type with its schema:

```php
require_once 'WorkerClient.php';

$client = new WorkerClient('http://localhost/api', 'admin');

// Register task type
$client->registerTaskType(
    'your.task.type',
    '1.0.0',
    [
        'type' => 'object',
        'properties' => [
            'topic' => [
                'type' => 'string',
                'minLength' => 1,
                'maxLength' => 200
            ],
            'style' => [
                'type' => 'string',
                'enum' => ['formal', 'casual', 'technical']
            ],
            'length' => [
                'type' => 'integer',
                'minimum' => 100,
                'maximum' => 5000
            ]
        ],
        'required' => ['topic', 'style']
    ]
);

// Create a task
$task = $client->createTask('your.task.type', [
    'topic' => 'AI in Healthcare',
    'style' => 'technical',
    'length' => 1500
]);

echo "Created task #{$task['id']}\n";
```

## Error Handling

The worker implements multiple levels of error handling:

### 1. Task Processing Errors

When a task handler throws an exception:

- Task is marked as **failed**
- Error message is stored in TaskManager
- Task may be retried (up to `MAX_TASK_ATTEMPTS`)
- Worker continues processing other tasks

```php
function handleTask($params) {
    // Validation errors
    if (!isset($params['required_field'])) {
        throw new Exception("Missing required field");
    }
    
    // Processing errors
    try {
        $result = externalApiCall($params);
    } catch (Exception $e) {
        throw new Exception("External API failed: " . $e->getMessage());
    }
    
    return $result;
}
```

### 2. API Communication Errors

When API communication fails:

- Error is logged
- Worker waits longer before retry (2x poll interval)
- After `maxConsecutiveErrors` (default: 5), worker exits
- You should restart the worker (use supervisor/systemd)

### 3. Graceful Shutdown

Worker handles signals properly:

```bash
# Send SIGTERM for graceful shutdown
kill -TERM <pid>

# Worker will:
# 1. Finish processing current task
# 2. Print statistics
# 3. Exit cleanly
```

### Debugging Failed Tasks

```bash
# View failed tasks
curl http://localhost/api/tasks?status=failed

# Get specific task details
curl http://localhost/api/tasks/123

# Check error_message field for failure reason
```

## Production Deployment

### Deployment Checklist

- [ ] PHP and extensions installed
- [ ] Worker files deployed to server
- [ ] Configuration set (API URL, worker ID, etc.)
- [ ] Process manager configured (systemd/supervisor)
- [ ] Logging configured
- [ ] Monitoring configured
- [ ] Health checks enabled
- [ ] Tested with sample tasks
- [ ] Documentation for ops team

### Multiple Workers

Run multiple worker instances for higher throughput:

#### Method 1: Multiple systemd Services

```bash
# Create multiple service files
/etc/systemd/system/taskmanager-worker-1.service
/etc/systemd/system/taskmanager-worker-2.service
/etc/systemd/system/taskmanager-worker-3.service

# Each with unique worker-id
ExecStart=/usr/bin/php /path/worker.php --worker-id=worker-01 ...
ExecStart=/usr/bin/php /path/worker.php --worker-id=worker-02 ...
ExecStart=/usr/bin/php /path/worker.php --worker-id=worker-03 ...
```

#### Method 2: Supervisor with Multiple Processes

```ini
[program:taskmanager-worker]
command=/usr/bin/php /path/worker.php --worker-id=worker-%(process_num)02d
process_name=%(program_name)s_%(process_num)02d
numprocs=5
autostart=true
autorestart=true
```

### Resource Limits

Configure memory and time limits:

```ini
# In systemd service
[Service]
MemoryLimit=512M
TimeoutStopSec=30

# In supervisor
stopasgroup=true
killasgroup=true
```

## Monitoring and Troubleshooting

### Health Checks

Check if worker is running:

```bash
# systemd
systemctl status taskmanager-worker

# supervisor
supervisorctl status taskmanager-worker

# Process
ps aux | grep worker.php
```

### Log Analysis

```bash
# View recent logs
tail -n 100 /var/log/taskmanager-worker.log

# Search for errors
grep ERROR /var/log/taskmanager-worker.log

# Count processed tasks
grep "Completed successfully" /var/log/taskmanager-worker.log | wc -l

# View failed tasks
grep "Failed:" /var/log/taskmanager-worker.log
```

### Performance Monitoring

Track key metrics:

```bash
# Tasks processed per hour
grep "Completed successfully" worker.log | \
  awk '{print $1,$2}' | \
  uniq -c

# Average task processing time (requires instrumentation)
# Add timing to your handlers:
$start = microtime(true);
$result = processTask($task);
$duration = microtime(true) - $start;
echo "[METRICS] Task processed in " . round($duration, 2) . "s\n";
```

### Common Issues

#### Issue: Worker not claiming tasks

**Symptoms**: Worker logs "No tasks available" continuously

**Solutions**:
1. Check if tasks exist: `curl http://localhost/api/tasks?status=pending`
2. Verify type pattern matches task types
3. Check if other workers claimed all tasks
4. Verify API connectivity

#### Issue: Tasks timing out

**Symptoms**: Tasks remain in "claimed" status

**Solutions**:
1. Increase `TASK_CLAIM_TIMEOUT` in TaskManager config
2. Optimize task handler performance
3. Check if worker process is killed/crashed
4. Review worker logs for errors

#### Issue: High failure rate

**Symptoms**: Many tasks marked as "failed"

**Solutions**:
1. Review error messages: `curl http://localhost/api/tasks?status=failed`
2. Check task parameter validation
3. Test handlers individually
4. Review external API availability
5. Check resource limits (memory, disk space)

#### Issue: Worker consuming too much memory

**Symptoms**: Worker killed by OOM, high memory usage

**Solutions**:
1. Set PHP memory limit: `php -d memory_limit=256M worker.php`
2. Process large files in chunks
3. Clear variables after processing: `unset($largeVariable)`
4. Use `--max-runs` to restart worker periodically
5. Monitor with `ps aux | grep worker.php`

## Advanced Usage

### Custom WorkerClient Extensions

Extend WorkerClient for custom functionality:

```php
class CustomWorkerClient extends WorkerClient {
    /**
     * Claim task with priority
     */
    public function claimTaskWithPriority($minPriority) {
        // Custom implementation
        $task = $this->claimTask();
        
        if ($task && isset($task['params']['priority'])) {
            if ($task['params']['priority'] < $minPriority) {
                // Release task back to queue
                $this->failTask($task['id'], 'Priority too low', null);
                return null;
            }
        }
        
        return $task;
    }
    
    /**
     * Report progress for long-running tasks
     */
    public function reportProgress($taskId, $progress) {
        // Implement custom progress reporting
        echo "[PROGRESS] Task #{$taskId}: {$progress}%\n";
    }
}

// Example: Create client with custom timeout for long-running tasks
$client = new WorkerClient(
    'https://api.example.com/api',
    'worker-01',
    true,  // debug
    60     // 60 second timeout for API requests
);
```

### Task Result Callbacks

Implement callbacks for task results:

```php
function processTaskWithCallback($task, $onComplete, $onError) {
    try {
        $result = processTask($task);
        $onComplete($task['id'], $result);
        return $result;
    } catch (Exception $e) {
        $onError($task['id'], $e);
        throw $e;
    }
}

// Usage in worker loop
$result = processTaskWithCallback(
    $task,
    function($taskId, $result) {
        // Send notification, update dashboard, etc.
        notifyTaskComplete($taskId, $result);
    },
    function($taskId, $error) {
        // Log to external system, send alert, etc.
        logErrorToExternal($taskId, $error);
    }
);
```

### Distributed Tracing

Add tracing for debugging distributed systems:

```php
function processTaskWithTracing($task) {
    $traceId = generateTraceId();
    
    echo "[TRACE:{$traceId}] Start task #{$task['id']}\n";
    
    try {
        $result = processTask($task);
        echo "[TRACE:{$traceId}] Success task #{$task['id']}\n";
        return $result;
    } catch (Exception $e) {
        echo "[TRACE:{$traceId}] Error task #{$task['id']}: {$e->getMessage()}\n";
        throw $e;
    }
}

function generateTraceId() {
    return bin2hex(random_bytes(16));
}
```

### Worker Pools

Manage multiple workers programmatically:

```bash
#!/bin/bash
# worker-pool.sh

WORKERS=5
API_URL="http://localhost/api"

for i in $(seq 1 $WORKERS); do
    php worker.php \
        --api-url=$API_URL \
        --worker-id=worker-$(hostname)-$i \
        > logs/worker-$i.log 2>&1 &
    
    echo "Started worker $i (PID: $!)"
done

echo "Started $WORKERS workers"
```

## Support and Contributing

### Getting Help

- Review TaskManager API documentation: `/Backend/TaskManager/docs/API_REFERENCE.md`
- Check TaskManager README: `/Backend/TaskManager/README.md`
- Review example handlers in `worker.php`

### Reporting Issues

When reporting issues, include:

1. Worker configuration (API URL, worker ID, options)
2. PHP version (`php --version`)
3. Task type and parameters
4. Error messages from logs
5. Expected vs actual behavior

### Contributing

To add new example handlers:

1. Add handler function to `worker.php`
2. Add case to `processTask()` switch statement
3. Document parameters and return value
4. Test with sample task
5. Update this guide with example

---

## Summary

You now have a complete PHP worker implementation with:

✅ **Production-ready code** - Error handling, signals, logging  
✅ **Easy configuration** - CLI args and environment variables  
✅ **Extensible handlers** - Add your own task types easily  
✅ **Multiple deployment options** - Foreground, background, systemd, supervisor  
✅ **Comprehensive documentation** - This guide!  

**Next Steps:**

1. Deploy the worker to your environment
2. Create your first task type
3. Implement custom handler
4. Configure monitoring
5. Scale with multiple workers

Happy processing! 🚀
