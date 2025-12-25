# HackerNews Stories Workers

Worker implementation for fetching stories from HackerNews with TaskManager integration.

## Overview

This worker system provides automated fetching of HackerNews stories with:
- **TaskManager Integration**: Reports task completion to centralized TaskManager API
- **Multiple Story Types**: Support for top, best, new, Ask HN, Show HN, and job stories
- **Rate Limiting**: Respects HackerNews API rate limits
- **Graceful Degradation**: Works without TaskManager if unavailable
- **SOLID Principles**: Clean architecture with dependency injection

## Architecture

### Components

1. **HackerNewsClient** (`client.py`)
   - Communicates with HackerNews Firebase API
   - Handles rate limiting and error handling
   - Single Responsibility: API communication only

2. **BaseWorker** (`workers/base_worker.py`)
   - Base class for all HackerNews workers
   - Handles task claiming, processing, and reporting
   - Integrates with TaskManager API (optional)

3. **HackerNewsStoryWorker** (`workers/hackernews_story_worker.py`)
   - Fetches stories from HackerNews
   - Stores results in IdeaInspiration database
   - Uses IdeaProcessor for data storage

4. **Task Queue** (`workers/schema.sql`)
   - SQLite-based local task queue
   - Supports multiple claiming strategies (FIFO, LIFO, Priority)
   - Tracks worker heartbeats

## Usage

### Basic Usage

```python
from pathlib import Path
from core.config import Config
from core.database import Database
from workers.hackernews_story_worker import HackerNewsStoryWorker

# Initialize configuration and database
config = Config()
results_db = Database(config)

# Create worker
worker = HackerNewsStoryWorker(
    worker_id="hn-worker-01",
    queue_db_path="path/to/queue.db",
    config=config,
    results_db=results_db,
    enable_taskmanager=True,
    strategy="LIFO",
    poll_interval=5
)

# Run worker (blocks until stopped)
worker.run()
```

### With TaskManager

```python
# TaskManager integration is automatic if TaskManagerClient is available
worker = HackerNewsStoryWorker(
    worker_id="hn-worker-01",
    queue_db_path="queue.db",
    config=config,
    results_db=results_db,
    enable_taskmanager=True  # Enable TaskManager integration
)

worker.run()
```

### Without TaskManager

```python
# Disable TaskManager for local-only operation
worker = HackerNewsStoryWorker(
    worker_id="hn-worker-01",
    queue_db_path="queue.db",
    config=config,
    results_db=results_db,
    enable_taskmanager=False  # Disable TaskManager
)

worker.run()
```

## Task Types

The following task types are supported:

1. **PrismQ.Text.HackerNews.Story.Fetch** - Fetch stories by type
2. **PrismQ.Text.HackerNews.Story.FrontPage** - Fetch front page stories
3. **PrismQ.Text.HackerNews.Story.Best** - Fetch best stories
4. **PrismQ.Text.HackerNews.Story.New** - Fetch new stories
5. **PrismQ.Text.HackerNews.Story.Ask** - Fetch Ask HN stories
6. **PrismQ.Text.HackerNews.Story.Show** - Fetch Show HN stories
7. **PrismQ.Text.HackerNews.Story.Job** - Fetch job postings

### Task Parameters

```python
{
    "story_type": "top",  # top, best, new, ask, show, job
    "limit": 30          # Number of stories to fetch (1-500)
}
```

## Registering Task Types

Before using the worker, register task types with TaskManager:

```bash
cd Source/Text/HackerNews/Stories
python scripts/register_task_types.py
```

## Queue Database

The worker uses a SQLite database for local task queuing:

```sql
-- Main task queue
CREATE TABLE task_queue (
    id INTEGER PRIMARY KEY,
    task_type TEXT,
    parameters TEXT,  -- JSON
    priority INTEGER,
    status TEXT,      -- queued, claimed, completed, failed
    ...
);

-- Worker heartbeats for monitoring
CREATE TABLE worker_heartbeats (
    worker_id TEXT PRIMARY KEY,
    last_heartbeat TEXT,
    tasks_processed INTEGER,
    tasks_failed INTEGER
);

-- Task history for audit trail
CREATE TABLE task_history (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    status_from TEXT,
    status_to TEXT,
    changed_at TEXT,
    ...
);
```

## Claiming Strategies

The worker supports multiple task claiming strategies:

1. **FIFO** (First-In-First-Out)
   - Process oldest tasks first
   - ORDER BY: `created_at ASC, priority DESC`

2. **LIFO** (Last-In-First-Out)
   - Process newest tasks first (default)
   - ORDER BY: `created_at DESC, priority DESC`

3. **PRIORITY**
   - Process highest priority tasks first
   - ORDER BY: `priority DESC, created_at ASC`

## Configuration

### Environment Variables

```env
# HackerNews Configuration
HACKERNEWS_API_URL=https://hacker-news.firebaseio.com/v0
HACKERNEWS_ENABLE_TASKMANAGER=true
HACKERNEWS_WORKER_ID=hackernews-story-worker-01
HACKERNEWS_POLL_INTERVAL=5
HACKERNEWS_MAX_STORIES=500
```

### Worker Parameters

- `worker_id`: Unique worker identifier (required)
- `queue_db_path`: Path to SQLite queue database (required)
- `config`: Configuration object (required)
- `results_db`: Results database (required)
- `enable_taskmanager`: Enable TaskManager API integration (default: True)
- `strategy`: Task claiming strategy - FIFO, LIFO, PRIORITY (default: LIFO)
- `heartbeat_interval`: Heartbeat interval in seconds (default: 30)
- `poll_interval`: Polling interval in seconds (default: 5)
- `max_backoff`: Maximum backoff time in seconds (default: 60)
- `backoff_multiplier`: Backoff multiplier (default: 1.5)

## Testing

Run tests:

```bash
cd Source/Text/HackerNews/Stories
python _meta/tests/test_hackernews_basic.py
```

## SOLID Principles

This implementation follows SOLID principles:

### Single Responsibility Principle (SRP)
- **HackerNewsClient**: Only handles API communication
- **BaseWorker**: Only manages task lifecycle
- **HackerNewsStoryWorker**: Only fetches HackerNews stories

### Open/Closed Principle (OCP)
- TaskManager integration is optional (can be enabled/disabled)
- New story types can be added without modifying base classes
- New claiming strategies can be added without modifying workers

### Liskov Substitution Principle (LSP)
- Any BaseWorker subclass can replace BaseWorker
- All workers implement WorkerProtocol interface

### Interface Segregation Principle (ISP)
- WorkerProtocol defines minimal interface (claim_task, process_task, report_result)
- No unnecessary dependencies

### Dependency Inversion Principle (DIP)
- Depends on abstractions (Config, Database, TaskManagerClient)
- Dependencies injected via constructor
- No direct instantiation of concrete classes

## Performance

- **Task processing**: <30s for 30 stories
- **TaskManager API calls**: <100ms per call
- **HackerNews API calls**: <200ms per request
- **Memory usage**: <150MB per worker
- **Rate limiting**: ~10 requests/second (gentle)

## Troubleshooting

### TaskManager Connection Failed

If TaskManager is unavailable:
```
WARNING: TaskManager client init failed: Connection refused
```

This is expected and the worker will continue without TaskManager integration.

### Queue Database Locked

If multiple workers share a database:
```
ERROR: database is locked
```

Solution: Use WAL mode (enabled by default) or separate queue databases per worker.

### HackerNews API Rate Limiting

If you see many 429 errors:
```
ERROR: Failed to fetch topstories: 429 Too Many Requests
```

Solution: Increase `rate_limit_delay` in HackerNewsClient initialization.

## References

- [HackerNews API Documentation](https://github.com/HackerNews/API)
- [TaskManager API Documentation](../../TaskManager/README.md)
- [SOLID Principles](_meta/docs/SOLID_PRINCIPLES.md)
