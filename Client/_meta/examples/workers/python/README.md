# Python Worker for TaskManager

Production-ready Python worker implementation for processing tasks from the TaskManager API.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run worker with local API
python worker.py --debug

# Run worker with remote API
python worker.py --api-url=https://api.example.com/api --worker-id=worker-01
```

## Files

- **`worker.py`** - Main worker script with complete implementation
- **`test_worker.py`** - Test script for creating sample tasks
- **`requirements.txt`** - Python dependencies
- **`INTEGRATION_GUIDE.md`** - Complete documentation and deployment guide

## Features

✅ **Automatic task claiming** from TaskManager queue  
✅ **Extensible task handlers** - Easy to add custom task types  
✅ **Error handling** - Comprehensive error handling with retries  
✅ **Graceful shutdown** - Handles SIGTERM and SIGINT properly  
✅ **Health checks** - Verifies API connectivity before starting  
✅ **Debug logging** - Optional verbose logging for troubleshooting  
✅ **Multiple workers** - Run multiple instances for higher throughput  
✅ **Production ready** - Includes systemd config examples  

## Example Usage

### 1. Basic Worker

```bash
python worker.py
```

### 2. Worker with Type Filter

Process only specific task type IDs:

```bash
python worker.py --task-type-ids="1,2"
```

### 3. Debug Mode

Enable verbose logging:

```bash
python worker.py --debug
```

### 4. Limited Run

Process 100 tasks then exit:

```bash
python worker.py --max-runs=100
```

## Testing

```bash
# Create test tasks
python test_worker.py --num-tasks=10

# Run worker to process them
python worker.py --debug
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
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "example.echo",
    "params": {
      "message": "Hello, World!"
    }
  }'
```

## Adding Custom Handlers

Edit `worker.py` and add your handler in the `process_task` method:

```python
def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    task_type = task.get('type', 'unknown')
    params = task.get('params', {})
    
    if task_type == 'your.custom.type':
        return self._handle_custom_task(params)
    # ... other handlers

def _handle_custom_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    # Your logic here
    return {
        'success': True,
        'data': {'result': 'custom result'},
        'message': 'Task processed successfully'
    }
```

## Configuration

| Option | Environment Variable | Default |
|--------|---------------------|---------|
| `--api-url` | `TASKMANAGER_API_URL` | `http://localhost:8000/api` |
| `--worker-id` | `WORKER_ID` | Auto-generated |
| `--task-type-ids` | `TASK_TYPE_IDS` | `null` (all active types) |
| `--poll-interval` | `POLL_INTERVAL` | `10` seconds |
| `--max-runs` | `MAX_RUNS` | `0` (unlimited) |
| `--debug` | `DEBUG` | `false` |

## Requirements

- Python 3.7 or higher (3.9+ recommended)
- requests library

## Production Deployment

### Using systemd

```bash
# Create service file
sudo nano /etc/systemd/system/taskmanager-worker.service
```

```ini
[Unit]
Description=TaskManager Python Worker
After=network.target

[Service]
Type=simple
User=worker
WorkingDirectory=/opt/worker
Environment="TASKMANAGER_API_URL=https://api.example.com/api"
Environment="WORKER_ID=python-worker-01"
ExecStart=/usr/bin/python3 /opt/worker/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable taskmanager-worker
sudo systemctl start taskmanager-worker

# View logs
sudo journalctl -u taskmanager-worker -f
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

CMD ["python", "worker.py"]
```

```bash
# Build and run
docker build -t python-worker .
docker run -d \
  --name python-worker-01 \
  -e TASKMANAGER_API_URL=https://api.example.com/api \
  -e WORKER_ID=python-worker-docker-01 \
  --restart unless-stopped \
  python-worker
```

## Help

```bash
python worker.py --help
```

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ

## Related Documentation

- [TaskManager README](../../../Backend/TaskManager/README.md) - TaskManager system overview
- [TaskManager API Reference](../../../Backend/TaskManager/docs/API_REFERENCE.md) - Complete API documentation
- [PHP Worker Example](../php/) - PHP implementation example
