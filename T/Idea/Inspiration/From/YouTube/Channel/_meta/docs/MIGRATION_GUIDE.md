# Migration Guide: SQLite Queue to TaskManager API

This guide helps you migrate from the legacy SQLite-based queue to the new TaskManager API integration.

## Overview

The worker system has been refactored to use the external TaskManager API by default, while maintaining backwards compatibility with the legacy SQLite queue.

## Key Changes

### Before (SQLite Queue)
```python
from src.workers import BaseWorker
from src.core.config import Config
from src.core.database import Database

worker = BaseWorker(
    worker_id="worker-001",
    queue_db_path="data/worker_queue.db",
    config=config,
    results_db=results_db,
    strategy="LIFO"
)
worker.run()
```

### After (TaskManager API)
```python
from src.workers import BaseWorker
from src.core.config import Config
from src.core.database import Database
from TaskManager import TaskManagerClient

# Step 1: Register task types with TaskManager API (one-time setup)
client = TaskManagerClient()
task_type_result = client.register_task_type(
    name="PrismQ.YouTube.Channel.Scrape",
    version="1.0.0",
    param_schema={
        "type": "object",
        "properties": {
            "channel_url": {"type": "string"}
        },
        "required": ["channel_url"]
    }
)
task_type_id = task_type_result['id']

# Step 2: Create worker with task_type_ids
worker = BaseWorker(
    worker_id="worker-001",
    config=config,
    results_db=results_db,
    task_type_ids=[task_type_id],  # List of task type IDs from registration
    use_taskmanager=True,  # Default
    strategy="LIFO"
)
worker.run()
```

## Migration Steps

### 1. Install TaskManager Client

```bash
cd Source/TaskManager
pip install -e .
```

### 2. Configure Environment

Add to your `PrismQ_WD/.env` file:

```env
TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
TASKMANAGER_API_KEY=your-api-key-here
```

### 3. Register Task Types

Create a registration script (run once or on startup):

```python
from TaskManager import TaskManagerClient

client = TaskManagerClient()

# Register all task types your workers handle
task_types = {
    "youtube_channel_scrape": {
        "name": "PrismQ.YouTube.Channel.Scrape",
        "version": "1.0.0",
        "param_schema": {
            "type": "object",
            "properties": {
                "channel_url": {"type": "string"}
            },
            "required": ["channel_url"]
        }
    },
    "youtube_video_scrape": {
        "name": "PrismQ.YouTube.Video.Scrape",
        "version": "1.0.0",
        "param_schema": {
            "type": "object",
            "properties": {
                "video_url": {"type": "string"}
            },
            "required": ["video_url"]
        }
    }
}

# Register and store IDs
task_type_ids = []
for key, task_type_def in task_types.items():
    result = client.register_task_type(**task_type_def)
    task_type_ids.append(result['id'])
    print(f"Registered {task_type_def['name']}: ID={result['id']}")

# Save these IDs to config for worker initialization
```

### 4. Update Worker Initialization

**Old SQLite-based initialization:**
```python
worker = MyWorker(
    worker_id="worker-001",
    queue_db_path="data/worker_queue.db",
    config=config,
    results_db=results_db
)
```

**New TaskManager API initialization:**
```python
# Get task type IDs from config or registration
task_type_ids = [1, 2, 3]  # From step 3

worker = MyWorker(
    worker_id="worker-001",
    config=config,
    results_db=results_db,
    task_type_ids=task_type_ids,
    use_taskmanager=True
)
```

### 5. Update Task Creation

**Before (SQLite):**
```python
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect("data/worker_queue.db")
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO task_queue 
    (task_type, parameters, priority, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?)
""", (
    'youtube_channel_scrape',
    json.dumps({"channel_url": "https://youtube.com/@example"}),
    5,
    datetime.utcnow().isoformat(),
    datetime.utcnow().isoformat()
))
conn.commit()
conn.close()
```

**After (TaskManager API):**
```python
from TaskManager import TaskManagerClient

client = TaskManagerClient()
task = client.create_task(
    task_type="PrismQ.YouTube.Channel.Scrape",
    params={"channel_url": "https://youtube.com/@example"}
)
print(f"Task created: {task['id']}")
```

## Backwards Compatibility

The legacy SQLite queue mode is still supported for gradual migration:

```python
worker = MyWorker(
    worker_id="worker-001",
    config=config,
    results_db=results_db,
    queue_db_path="data/worker_queue.db",
    use_taskmanager=False  # Use legacy SQLite mode
)
```

## Benefits of TaskManager API

1. **Centralized Task Management**: All PrismQ modules share the same task queue
2. **Better Monitoring**: Web UI for task status, statistics, and debugging
3. **Deduplication**: Automatic task deduplication prevents redundant work
4. **Cross-Module Coordination**: Tasks can trigger tasks in other modules
5. **Scalability**: API can handle multiple workers across different machines
6. **No Local Database**: No need to manage SQLite files per worker

## Task Type Naming Convention

Use hierarchical naming for task types:
- `PrismQ.{Module}.{SubModule}.{Action}`
- Examples:
  - `PrismQ.YouTube.Channel.Scrape`
  - `PrismQ.YouTube.Video.Scrape`
  - `PrismQ.Script.Generate`
  - `PrismQ.Audio.Synthesize`

## API Claiming Policies

Both modes support the same claiming strategies:
- **FIFO**: First In, First Out (oldest tasks first)
- **LIFO**: Last In, First Out (newest tasks first)
- **PRIORITY**: Highest priority first

Configure via the `strategy` parameter:
```python
worker = BaseWorker(
    ...,
    strategy="PRIORITY"  # FIFO, LIFO, or PRIORITY
)
```

## Troubleshooting

### "TaskManager module not available"
```bash
cd Source/TaskManager
pip install -e .
```

### "Invalid or missing API key"
Check your `.env` file has:
```env
TASKMANAGER_API_KEY=your-api-key-here
```

### "task_type_ids is required"
You must register task types and provide their IDs:
```python
client = TaskManagerClient()
result = client.register_task_type(name="...", version="...", param_schema={...})
task_type_ids = [result['id']]
```

### "Connection error"
Check API endpoint is accessible:
```python
from TaskManager import TaskManagerClient
client = TaskManagerClient()
health = client.health_check()
print(health)
```

## Complete Example

See `Source/TaskManager/_meta/examples/worker_example.py` for a complete working example.

## Questions?

Refer to:
- TaskManager API Documentation: `Source/TaskManager/README.md`
- Worker Implementation Guide: `Source/TaskManager/_meta/docs/WORKER_IMPLEMENTATION_GUIDE.md`
- API Documentation: https://api.prismq.nomoos.cz/public/swagger-ui
