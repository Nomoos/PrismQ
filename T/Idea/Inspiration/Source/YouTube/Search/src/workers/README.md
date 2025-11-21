# Worker System - TaskManager API Integration

This directory contains the worker infrastructure for processing tasks from the **TaskManager API** (external service).

## Overview

Workers use the **external TaskManager API** exclusively for task management. This provides:
- Centralized task management across all PrismQ modules
- Better monitoring via web UI
- Automatic task deduplication
- Cross-module task coordination
- Scalability across multiple workers

## Quick Start

```python
from TaskManager import TaskManagerClient
from src.workers import BaseWorker
from src.core.config import Config
from src.core.database import Database

# 1. Register task types (one-time setup)
client = TaskManagerClient()
result = client.register_task_type(
    name="PrismQ.YouTube.Channel.Scrape",
    version="1.0.0",
    param_schema={...}
)
task_type_ids = [result['id']]

# 2. Create worker
worker = MyWorker(
    worker_id="worker-001",
    config=Config(),
    results_db=Database(),
    task_type_ids=task_type_ids  # Required
)

# 3. Run worker
worker.run()
```

**Complete example:** See `_meta/examples/taskmanager_worker_example.py`

## Configuration

Workers require TaskManager API configuration in `.env`:

```env
TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
TASKMANAGER_API_KEY=your-api-key-here
```

## Architecture

```
Worker → TaskManager API (external REST service)
       ↓
       IdeaInspiration Database (results storage)
```

### Task Flow

1. **Task Creation**: Tasks are created via TaskManager API
2. **Task Claiming**: Worker polls API and claims available tasks
3. **Processing**: Worker processes the task (scraping, etc.)
4. **Result Storage**: Results saved to IdeaInspiration database
5. **Completion**: Worker reports completion to TaskManager API

## BaseWorker Class

All workers inherit from `BaseWorker`:

```python
class BaseWorker(ABC):
    """Base worker class using TaskManager API.
    
    Required Parameters:
        worker_id: Unique worker identifier
        config: Configuration object
        results_db: IdeaInspiration database for results
        task_type_ids: List of TaskManager task type IDs to claim
    
    Optional Parameters:
        strategy: Task claiming strategy (FIFO, LIFO, PRIORITY)
        poll_interval: Seconds between polls (default: 5)
        max_backoff: Maximum backoff seconds (default: 60)
    """
```

### Claiming Strategies

- **FIFO** (First In, First Out): Oldest tasks first
- **LIFO** (Last In, First Out): Newest tasks first  
- **PRIORITY**: Highest priority tasks first

## Components

### BaseWorker
Abstract base class providing:
- Task claiming from TaskManager API
- Task processing lifecycle
- Result reporting to API and IdeaInspiration DB
- Exponential backoff for empty queues
- Error handling and retry logic

### WorkerFactory
Factory pattern for creating worker instances:
- Register worker types
- Create workers with configuration
- Dependency injection

### Task Types

Workers process different task types defined in TaskManager API:
- `PrismQ.YouTube.Channel.Scrape`
- `PrismQ.YouTube.Video.Search`
- `PrismQ.YouTube.Video.Single`
- etc.

## Example Usage

See `_meta/examples/taskmanager_worker_example.py` for complete working example.

## Monitoring

Task status and worker activity can be monitored via:
- TaskManager API web interface
- API endpoints for task and worker status
- IdeaInspiration database for processed results

## See Also

- [TaskManager Client Documentation](../../../../TaskManager/README.md)
- [TaskManager Worker Guide](../../../../TaskManager/_meta/docs/WORKER_IMPLEMENTATION_GUIDE.md)
- [IdeaInspiration Model](../../../../../Model/README.md)
