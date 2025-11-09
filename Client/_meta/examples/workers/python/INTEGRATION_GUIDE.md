# Python Worker Integration Guide

Complete guide for implementing and deploying Python workers that integrate with the PrismQ TaskManager system.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Worker](#running-the-worker)
6. [Task Processing](#task-processing)
7. [Adding Custom Task Types](#adding-custom-task-types)
8. [Error Handling](#error-handling)
9. [Production Deployment](#production-deployment)
10. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
11. [Advanced Usage](#advanced-usage)

## Overview

The Python worker is a production-ready implementation that:

- Polls the TaskManager API for new tasks
- Processes tasks with extensible handlers
- Reports results back to TaskManager
- Handles failures and retries gracefully
- Supports graceful shutdown

### Key Features

- **Distributed Processing** - Multiple workers can run in parallel
- **Fault Tolerant** - Automatic task claiming prevents duplicate work
- **Scalable** - Easy to add more workers for higher throughput
- **Configurable** - Flexible configuration via CLI or environment variables
- **Production Ready** - Includes logging, monitoring, and graceful shutdown

## Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│                    TaskManager API                       │
│                   (FastAPI + MySQL)                      │
│                                                          │
│  - Task Queue Management                                │
│  - Task Status Tracking                                 │
│  - Worker Coordination                                  │
└──────────────┬───────────────────────────────┬──────────┘
               │                               │
               │ HTTP REST API                 │
               │                               │
    ┌──────────▼─────────┐        ┌───────────▼──────────┐
    │  Python Worker 1   │        │  Python Worker 2     │
    │                    │        │                      │
    │  - Claim tasks     │        │  - Claim tasks       │
    │  - Process tasks   │        │  - Process tasks     │
    │  - Report results  │        │  - Report results    │
    └────────────────────┘        └──────────────────────┘
```

### Data Flow

```
1. Task Creation
   Client → POST /tasks → Creates task with params

2. Task Claiming
   Worker → POST /tasks/claim → Claims next available task by type ID

3. Task Processing
   Worker → Process task → Execute business logic

4. Task Completion
   Worker → POST /tasks/{id}/complete → Marks complete
```

## Installation

### Prerequisites

- Python 3.7 or higher (3.9+ recommended)
- pip (Python package manager)
- Access to TaskManager API

### Install Dependencies

```bash
# Navigate to worker directory
cd examples/workers/python

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python worker.py --help
```

### Verify Installation

```bash
# Check Python version
python --version

# Check dependencies
pip list | grep requests

# Test worker help
python worker.py --help
```

## Configuration

### Command Line Arguments

The worker accepts configuration via command-line arguments:

```bash
python worker.py \
  --api-url=http://localhost:8000/api \
  --worker-id=python-worker-01 \
  --task-type-ids="1,2,3" \
  --poll-interval=10 \
  --max-runs=0 \
  --debug
```

### Environment Variables

Alternatively, use environment variables:

```bash
# Create .env file
cat > .env << EOF
TASKMANAGER_API_URL=http://localhost:8000/api
WORKER_ID=python-worker-01
TASK_TYPE_IDS=1,2,3
POLL_INTERVAL=10
MAX_RUNS=0
DEBUG=false
EOF

# Load and run
export $(cat .env | xargs)
python worker.py
```

### Configuration Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `--api-url` | `TASKMANAGER_API_URL` | `http://localhost:8000/api` | TaskManager API base URL |
| `--worker-id` | `WORKER_ID` | Auto-generated UUID | Unique worker identifier |
| `--task-type-ids` | `TASK_TYPE_IDS` | All active types | Comma-separated task type IDs to process |
| `--poll-interval` | `POLL_INTERVAL` | `10` | Seconds to wait between polls when no tasks |
| `--max-runs` | `MAX_RUNS` | `0` (unlimited) | Maximum number of tasks to process before exiting |
| `--debug` | `DEBUG` | `false` | Enable verbose debug logging |

## Running the Worker

### Development Mode

For local development and testing:

```bash
# Basic usage (localhost, all task types)
python worker.py

# With debug logging
python worker.py --debug

# Process limited number of tasks
python worker.py --max-runs=10

# Process only specific task type IDs
python worker.py --task-type-ids="1,2"
```

### Production Mode

For production deployment:

```bash
# Run with production API URL and specific task types
python worker.py \
  --api-url=https://taskmanager.example.com/api \
  --worker-id=python-worker-prod-01 \
  --task-type-ids="1,2,3" \
  --poll-interval=5

# Run in background
nohup python worker.py \
  --api-url=https://taskmanager.example.com/api \
  --worker-id=python-worker-prod-01 \
  --task-type-ids="1,2,3" \
  > worker.log 2>&1 &

# Check worker process
ps aux | grep worker.py
```

### Multiple Workers

Run multiple workers for higher throughput:

```bash
# Terminal 1
python worker.py --worker-id=python-worker-01

# Terminal 2
python worker.py --worker-id=python-worker-02

# Terminal 3
python worker.py --worker-id=python-worker-03
```

Each worker will claim and process tasks independently.

## Task Processing

### Task Structure

Tasks in TaskManager follow this structure:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "example.echo",
  "status": "pending",
  "params": {
    "message": "Hello, World!"
  },
  "created_at": "2025-11-07T17:30:00Z",
  "claimed_at": null,
  "completed_at": null,
  "worker_id": null,
  "result": null,
  "error": null
}
```

### Processing Flow

1. **Claim Task**
   ```python
   task = worker.claim_task()
   # Returns task if available, None otherwise
   ```

2. **Process Task**
   ```python
   result = worker.process_task(task)
   # Executes task processing logic
   # Returns success/failure with data
   ```

3. **Complete or Fail**
   ```python
   if result['success']:
       worker.complete_task(task['id'], result)
   else:
       worker.fail_task(task['id'], result['message'])
   ```

### Task Claiming Details

The claim endpoint **requires** specifying which task type to claim by its ID (not name). The `task_type_id` parameter is **mandatory** and must be a positive integer.

**API Endpoint**: `POST /tasks/claim`

**Required Parameters**:
- `worker_id` (string): Unique identifier for this worker - **required**
- `task_type_id` (integer): Specific task type ID to claim - **required, must be a positive integer**

**Optional Parameters**:
- `type_pattern` (string): Additional SQL LIKE filter (e.g., "PrismQ.%")
- `sort_by` (string): Field to sort by (`created_at`, `priority`, `id`, `attempts`)
- `sort_order` (string): Sort direction (`ASC` or `DESC`)

**How to Get Task Type IDs**:

Before claiming tasks, you need to know the task type ID. Query the API:

```python
import requests

# Get all task types
response = requests.get('http://localhost:8000/api/task-types')
task_types = response.json()['data']['task_types']

# Find the ID for a specific task type
for task_type in task_types:
    if task_type['name'] == 'example.echo':
        task_type_id = task_type['id']
        print(f"Task type 'example.echo' has ID: {task_type_id}")
```

**Claiming Example**:

```python
# Claim a task with specific type ID
response = requests.post(
    'http://localhost:8000/api/tasks/claim',
    json={
        'worker_id': 'python-worker-01',
        'task_type_id': 1,  # Must specify task type ID
        'sort_by': 'priority',
        'sort_order': 'DESC'  # Claim highest priority first
    }
)

if response.status_code == 200:
    task = response.json()['data']
    print(f"Claimed task {task['id']} of type {task['type']}")
```

**Claiming Strategies**:

Different sorting options allow different processing strategies:

1. **FIFO (First In, First Out)**: Process oldest tasks first
   - `sort_by='created_at'`, `sort_order='ASC'` (default)

2. **LIFO (Last In, First Out)**: Process newest tasks first
   - `sort_by='created_at'`, `sort_order='DESC'`

3. **Priority-based**: Process highest priority tasks first
   - `sort_by='priority'`, `sort_order='DESC'`

4. **Retry failed tasks first**: Process tasks with most attempts
   - `sort_by='attempts'`, `sort_order='DESC'`

## Adding Custom Task Types

### Step 1: Add Handler Method

Edit `worker.py` and add a new handler method:

```python
def _handle_my_custom_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Process my custom task type."""
    try:
        # Extract parameters
        input_data = params.get('input', '')
        
        # Perform your business logic
        result = perform_custom_processing(input_data)
        
        # Return success
        return {
            'success': True,
            'data': {
                'output': result,
                'processed_at': datetime.now().isoformat()
            },
            'message': 'Custom task processed successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing custom task: {str(e)}'
        }
```

### Step 2: Register Handler

Add the handler to the `process_task` method:

```python
def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    task_type = task.get('type', 'unknown')
    params = task.get('params', {})
    
    # Add your custom handler
    if task_type == 'my.custom.task':
        return self._handle_my_custom_task(params)
    # ... other handlers
```

### Step 3: Test Your Handler

Create a test task:

```python
import requests

response = requests.post(
    'http://localhost:8000/api/tasks',
    json={
        'type': 'my.custom.task',
        'params': {
            'input': 'test data'
        }
    }
)
```

Run the worker:

```bash
python worker.py --debug --task-types="my.custom.task"
```

## Error Handling

### Built-in Error Handling

The worker includes several error handling mechanisms:

1. **Consecutive Error Limit**
   ```python
   # Worker stops after 5 consecutive errors
   max_consecutive_errors = 5
   ```

2. **Task Failure Reporting**
   ```python
   try:
       result = process_task(task)
   except Exception as e:
       fail_task(task['id'], str(e))
   ```

3. **Graceful Shutdown**
   ```python
   # Handles SIGTERM and SIGINT
   signal.signal(signal.SIGTERM, signal_handler)
   signal.signal(signal.SIGINT, signal_handler)
   ```

### Custom Error Handling

Add custom error handling for specific scenarios:

```python
def _handle_my_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Process task
        result = process_data(params)
        return {'success': True, 'data': result}
        
    except ValidationError as e:
        # Handle validation errors
        self.logger.warning(f"Validation error: {e}")
        return {
            'success': False,
            'message': f'Invalid parameters: {e}'
        }
        
    except ExternalAPIError as e:
        # Handle external API errors
        self.logger.error(f"External API error: {e}")
        return {
            'success': False,
            'message': 'External service unavailable, retry later'
        }
        
    except Exception as e:
        # Handle unexpected errors
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }
```

## Production Deployment

### Option 1: Systemd Service (Linux)

Create a systemd service file:

```ini
# /etc/systemd/system/python-worker.service
[Unit]
Description=TaskManager Python Worker
After=network.target

[Service]
Type=simple
User=worker
WorkingDirectory=/opt/python-worker
Environment="TASKMANAGER_API_URL=https://taskmanager.example.com/api"
Environment="WORKER_ID=python-worker-prod-01"
ExecStart=/usr/bin/python3 /opt/python-worker/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable python-worker

# Start service
sudo systemctl start python-worker

# Check status
sudo systemctl status python-worker

# View logs
sudo journalctl -u python-worker -f
```

### Option 2: Docker Container

Create Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY worker.py .

# Run worker
CMD ["python", "worker.py"]
```

Build and run:

```bash
# Build image
docker build -t python-worker .

# Run container
docker run -d \
  --name python-worker-01 \
  -e TASKMANAGER_API_URL=https://taskmanager.example.com/api \
  -e WORKER_ID=python-worker-docker-01 \
  --restart unless-stopped \
  python-worker

# View logs
docker logs -f python-worker-01
```

### Option 3: Docker Compose (Multiple Workers)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  python-worker-01:
    build: .
    container_name: python-worker-01
    environment:
      - TASKMANAGER_API_URL=https://taskmanager.example.com/api
      - WORKER_ID=python-worker-01
    restart: unless-stopped

  python-worker-02:
    build: .
    container_name: python-worker-02
    environment:
      - TASKMANAGER_API_URL=https://taskmanager.example.com/api
      - WORKER_ID=python-worker-02
    restart: unless-stopped

  python-worker-03:
    build: .
    container_name: python-worker-03
    environment:
      - TASKMANAGER_API_URL=https://taskmanager.example.com/api
      - WORKER_ID=python-worker-03
    restart: unless-stopped
```

Run:

```bash
# Start all workers
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale python-worker-01=5
```

## Monitoring and Troubleshooting

### Logging

The worker provides detailed logging:

```
2025-11-07 17:30:00 [INFO] PrismQ TaskManager Worker (Python)
2025-11-07 17:30:00 [INFO] Worker ID:      python-worker-01
2025-11-07 17:30:00 [INFO] API URL:        http://localhost:8000/api
2025-11-07 17:30:01 [INFO] ✓ API health check passed
2025-11-07 17:30:01 [INFO] Worker started. Waiting for tasks...
2025-11-07 17:30:02 [INFO] ✓ Claimed task 123e4567-e89b-12d3-a456-426614174000
2025-11-07 17:30:04 [INFO] ✓ Task 123e4567-e89b-12d3-a456-426614174000 completed
```

### Health Checks

Check worker health:

```bash
# Check if worker is running
ps aux | grep worker.py

# Check recent logs
tail -f worker.log

# Test API connectivity
curl http://localhost:8000/api/health
```

### Common Issues

#### Worker Can't Connect to API

```bash
# Verify API URL
echo $TASKMANAGER_API_URL

# Test connectivity
curl -v http://localhost:8000/api/health

# Check firewall rules
sudo ufw status
```

#### Worker Not Claiming Tasks

```bash
# Check pending tasks
curl http://localhost:8000/api/tasks?status=pending

# Verify task type matches
python worker.py --debug --task-types="example.echo"

# Check worker logs
python worker.py --debug
```

#### Worker Exits with Errors

```bash
# Enable debug logging
python worker.py --debug

# Check for Python errors
python -m py_compile worker.py

# Verify dependencies
pip install -r requirements.txt
```

## Advanced Usage

### Custom Worker Class

Extend the worker for advanced functionality:

```python
from worker import TaskManagerWorker

class MyCustomWorker(TaskManagerWorker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize custom resources
        self.database = connect_to_database()
        self.cache = initialize_cache()
    
    def process_task(self, task):
        # Custom processing logic
        result = super().process_task(task)
        # Additional processing
        return result
```

### Rate Limiting

Implement rate limiting to avoid overload:

```python
import time
from datetime import datetime, timedelta

class RateLimitedWorker(TaskManagerWorker):
    def __init__(self, *args, max_tasks_per_minute=60, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_tasks_per_minute = max_tasks_per_minute
        self.task_times = []
    
    def claim_task(self):
        # Check rate limit
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        self.task_times = [t for t in self.task_times if t > cutoff]
        
        if len(self.task_times) >= self.max_tasks_per_minute:
            sleep_time = (self.task_times[0] - cutoff).total_seconds()
            time.sleep(sleep_time)
        
        task = super().claim_task()
        if task:
            self.task_times.append(now)
        return task
```

### Async Processing

Use asyncio for concurrent task processing:

```python
import asyncio
import aiohttp

class AsyncWorker(TaskManagerWorker):
    async def process_task_async(self, task):
        # Async task processing
        async with aiohttp.ClientSession() as session:
            result = await self.fetch_data(session, task['params'])
        return result
    
    def run(self):
        asyncio.run(self.run_async())
    
    async def run_async(self):
        # Async main loop
        while not self.should_stop:
            task = self.claim_task()
            if task:
                result = await self.process_task_async(task)
                self.complete_task(task['id'], result)
            else:
                await asyncio.sleep(self.poll_interval)
```

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
