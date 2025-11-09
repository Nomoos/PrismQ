# PHP Worker for TaskManager

Production-ready PHP worker implementation for processing tasks from the TaskManager API.

## Quick Start

```bash
# Run worker with local API
php worker.php --api-url=http://localhost/api --debug

# Run worker with remote API
php worker.php --api-url=https://api.example.com/api --worker-id=worker-01
```

## Files

- **`worker.php`** - Main worker script with complete implementation
- **`WorkerClient.php`** - Helper class for TaskManager API communication
- **`INTEGRATION_GUIDE.md`** - Complete documentation and deployment guide
- **`test_worker.php`** - Test script for verifying worker functionality

## Features

✅ **Automatic task claiming** from TaskManager queue  
✅ **Extensible task handlers** - Easy to add custom task types  
✅ **Error handling** - Comprehensive error handling with retries  
✅ **Graceful shutdown** - Handles SIGTERM and SIGINT properly  
✅ **Health checks** - Verifies API connectivity before starting  
✅ **Debug logging** - Optional verbose logging for troubleshooting  
✅ **Multiple workers** - Run multiple instances for higher throughput  
✅ **Production ready** - Includes systemd and supervisor configs  

## Documentation

📖 **[Complete Integration Guide](INTEGRATION_GUIDE.md)** - Everything you need to know:
- Installation and setup
- Configuration options
- Running the worker (foreground, background, systemd, supervisor)
- Implementing custom task handlers
- Error handling and debugging
- Production deployment
- Monitoring and troubleshooting
- Advanced usage patterns

## Example Usage

### 1. Basic Worker

```bash
php worker.php --api-url=http://localhost/api
```

### 2. Worker with Type Filter

Process only specific task types:

```bash
php worker.php --type-pattern="PrismQ.Script.%"
```

### 3. Debug Mode

Enable verbose logging:

```bash
php worker.php --debug
```

### 4. Limited Run

Process 100 tasks then exit:

```bash
php worker.php --max-runs=100
```

## Testing

```bash
# Test worker functionality
php test_worker.php --api-url=http://localhost/api
```

## Example Task Handlers

The worker includes example handlers for:

- **`example.echo`** - Echo back a message
- **`example.uppercase`** - Convert text to uppercase
- **`example.math.add`** - Add two numbers
- **`example.sleep`** - Simulate long-running task
- **`example.error`** - Test error handling

### Creating a Task

```bash
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "example.echo",
    "params": {
      "message": "Hello, World!"
    }
  }'
```

## Adding Custom Handlers

Edit `worker.php` and add your handler:

```php
function processTask($task) {
    switch ($task['type']) {
        case 'your.custom.type':
            return handleCustomTask($task['params']);
        // ... other cases
    }
}

function handleCustomTask($params) {
    // Your logic here
    return [
        'result' => 'success',
        'data' => $params
    ];
}
```

## Configuration

| Option | Environment Variable | Default |
|--------|---------------------|---------|
| `--api-url` | `TASKMANAGER_API_URL` | `http://localhost/api` |
| `--worker-id` | `WORKER_ID` | Auto-generated |
| `--type-pattern` | `TASK_TYPE_PATTERN` | `null` (all types) |
| `--poll-interval` | `POLL_INTERVAL` | `10` seconds |
| `--max-runs` | `MAX_RUNS` | `0` (unlimited) |
| `--debug` | `DEBUG` | `false` |

## Requirements

- **PHP 8.0 or higher** (8.1+ recommended for best compatibility)
  - The worker uses `mixed` type hints (PHP 8.0+)
  - The worker uses `never` return type (PHP 8.1+)
- cURL extension (`php-curl`)
- PCNTL extension (optional, for signal handling)

## Production Deployment

### Using systemd

```bash
# Copy service file
sudo cp taskmanager-worker.service /etc/systemd/system/

# Enable and start
sudo systemctl enable taskmanager-worker
sudo systemctl start taskmanager-worker

# View logs
sudo journalctl -u taskmanager-worker -f
```

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md#production-deployment) for complete deployment instructions.

## Help

```bash
php worker.php --help
```

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ

## Related Documentation

- [TaskManager README](../../../Backend/TaskManager/README.md) - TaskManager system overview
- [TaskManager API Reference](../../../Backend/TaskManager/docs/API_REFERENCE.md) - Complete API documentation
- [Integration Guide](INTEGRATION_GUIDE.md) - Detailed worker documentation
