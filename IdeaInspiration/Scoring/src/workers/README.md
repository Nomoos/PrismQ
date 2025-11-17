# Scoring Workers

Worker implementation for distributed scoring task processing, following the PrismQ Worker pattern.

## Architecture

The Scoring Worker follows SOLID principles and integrates with:
- **TaskManager API** (external service): For task coordination, queuing, and persistence
- **Scoring Engine**: For actual scoring computations
- **IdeaInspiration Database**: For automatic scoring of unscored items (Auto-Score Mode)

### Components

```
src/workers/
├── __init__.py                    # Worker protocol and data models
├── base_scoring_worker.py         # Base worker with TaskManager API integration
├── scoring_worker.py              # Concrete worker implementation
└── factory.py                     # Worker factory for easy instantiation
```

### External Dependencies

- **TaskManager API**: External REST service for task coordination
  - API Endpoint: https://api.prismq.nomoos.cz/api/
  - Client Library: `TaskManager` Python package
  - Install: `pip install -e Source/TaskManager`

## Features

### Auto-Score Mode (New!)

When enabled (default), the worker automatically:
1. Monitors the IdeaInspiration database for items without scores
2. Creates scoring tasks for unscored items when the queue is idle
3. Updates the database with calculated scores after processing

This enables autonomous operation - the worker can keep scoring new content without manual task creation.

## Task Types

The worker supports three types of scoring tasks:

### 1. Text Scoring (`PrismQ.Scoring.TextScoring`)

Score text content quality including readability, sentiment, and structure.

**Parameters:**
```json
{
  "title": "Content Title",
  "description": "Content Description",
  "text_content": "Full text content to score",
  "metadata": {}  // Optional
}
```

**Result:**
```json
{
  "score_breakdown": {
    "overall_score": 85.5,
    "title_score": 78.2,
    "text_quality_score": 82.3,
    "readability_score": 75.0,
    "sentiment_score": 10.5
  },
  "overall_score": 85.5,
  "items_processed": 1
}
```

### 2. Engagement Scoring (`PrismQ.Scoring.EngagementScoring`)

Score content based on engagement metrics (views, likes, comments).

**Parameters:**
```json
{
  "views": 1000000,
  "likes": 50000,
  "comments": 1000,
  "shares": 5000,
  "platform": "youtube"  // youtube, reddit, tiktok, generic
}
```

**Result:**
```json
{
  "engagement_score": 65.8,
  "score_details": {
    "view_score": 0.95,
    "like_score": 0.88,
    "comment_score": 0.75,
    "engagement_score": 0.65
  },
  "platform": "youtube",
  "items_processed": 1
}
```

### 3. Batch Scoring (`PrismQ.Scoring.BatchScoring`)

Score multiple items in a single task.

**Parameters:**
```json
{
  "items": [
    {
      "title": "First Item",
      "description": "Description",
      "text_content": "Content...",
      "metadata": {}
    },
    // ... more items
  ]
}
```

**Result:**
```json
{
  "results": [
    {
      "index": 0,
      "success": true,
      "score": 85.5,
      "score_breakdown": { ... }
    }
  ],
  "total_items": 10,
  "successful": 10,
  "failed": 0,
  "items_processed": 10
}
```

## Usage

### Starting a Worker

**Prerequisites**: TaskManager API must be running and accessible.

```bash
# Basic usage (auto-generated worker ID, FIFO strategy, auto-score enabled)
python scripts/run_worker.py

# Custom worker ID with priority strategy
python scripts/run_worker.py --worker-id scoring-01 --strategy PRIORITY

# Disable auto-scoring (manual task mode only)
python scripts/run_worker.py --no-autoscore

# Custom auto-score batch size
python scripts/run_worker.py --autoscore-batch-size 20

# Custom IdeaInspiration database path
python scripts/run_worker.py --autoscore-db /path/to/idea_inspiration.db

# Custom polling intervals
python scripts/run_worker.py --poll-interval 10 --max-backoff 120

# Testing mode with limited iterations
python scripts/run_worker.py --max-iterations 100
```

### Command Line Options

```
--worker-id WORKER_ID       Unique worker identifier (auto-generated if not provided)
--strategy STRATEGY         Task claiming policy: FIFO, LIFO, PRIORITY (default: FIFO)
--poll-interval SECONDS     Base polling interval (default: 5)
--max-backoff SECONDS       Maximum backoff time when no tasks available (default: 60)
--no-autoscore             Disable automatic scoring of unscored IdeaInspiration items
--autoscore-db PATH        Path to IdeaInspiration database (default: auto-detect)
--autoscore-batch-size N   Number of unscored items to fetch at once (default: 10)
--max-iterations N         Maximum iterations (for testing)
```

## Auto-Score Mode

### How It Works

1. **Idle Detection**: When no tasks are available from TaskManager API, the worker enters auto-score mode
2. **Fetch Unscored**: Queries the IdeaInspiration database for items where `score IS NULL`
3. **Create Tasks**: Automatically creates scoring tasks via TaskManager API for unscored items
4. **Process & Update**: Processes tasks and updates the IdeaInspiration database with calculated scores
5. **Resume Normal**: Returns to processing API tasks when available

### Benefits

- **Autonomous Operation**: Worker keeps busy without manual intervention
- **Incremental Scoring**: New content gets scored automatically as it's added
- **Resource Efficient**: Only activates when idle, doesn't compete with manual tasks
- **Transparent**: Auto-scored tasks go through TaskManager API and appear in statistics

### Configuration

```bash
# Enable with default settings (auto-detect database)
python scripts/run_worker.py

# Disable if you only want manual task processing
python scripts/run_worker.py --no-autoscore

# Custom batch size for higher throughput
python scripts/run_worker.py --autoscore-batch-size 50

# Explicit database path
python scripts/run_worker.py --autoscore-db /custom/path/idea_inspiration.db
```

## Task Claiming Policies

The worker supports different policies for claiming tasks from TaskManager API:

### FIFO (First In, First Out)
- Claims oldest tasks first
- Ensures fairness and predictable order
- **Best for**: General-purpose processing
- **Sort**: `created_at ASC`

### LIFO (Last In, First Out)
- Claims newest tasks first
- Good when recent data is more relevant
- **Best for**: Time-sensitive scoring
- **Sort**: `created_at DESC`

### PRIORITY
- Claims high-priority tasks first
- Within same priority, uses FIFO
- **Best for**: Mixed workloads with varying importance
- **Sort**: `priority DESC, created_at ASC`

## TaskManager API Integration

The worker operates exclusively with TaskManager API (external service) for all task coordination.

## Programmatic Usage

### Creating a Worker

```python
from src.workers.factory import WorkerFactory

# Create worker with factory
worker = WorkerFactory.create_scoring_worker(
    worker_id="my-worker",
    claiming_policy="PRIORITY",
    poll_interval=5,
    max_backoff=60,
    enable_autoscore=True
)

# Run worker
worker.run()
```

### Adding Tasks via TaskManager API

Tasks are created through the TaskManager API (external service):

```python
from TaskManager import TaskManagerClient

# Initialize client
client = TaskManagerClient()

# Register task type (one-time setup)
task_type = client.register_task_type(
    name="PrismQ.Scoring.TextScoring",
    version="1.0.0",
    param_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "text_content": {"type": "string"}
        }
    }
)

# Create scoring task
task = client.create_task(
    task_type_id=task_type['id'],
    params={
        "title": "Sample Title",
        "description": "Sample Description",
        "text_content": "Content to score..."
    },
    priority=0
)

print(f"Created task {task['id']}")
```

## Monitoring

All task monitoring and tracking is handled through the TaskManager API:

### Worker Status

```python
from TaskManager import TaskManagerClient

client = TaskManagerClient()

# Get worker statistics
stats = client.get_worker_stats(worker_id="my-worker")
print(f"Tasks processed: {stats['tasks_processed']}")
print(f"Tasks failed: {stats['tasks_failed']}")
```

### Task Status

```python
# Check task status
task = client.get_task(task_id=123)
print(f"Status: {task['status']}")
print(f"Result: {task.get('result')}")
```

### Queue Metrics

```python
# Get task type metrics
metrics = client.get_task_type_metrics(task_type_id=1)
print(f"Queued: {metrics['queued']}")
print(f"In Progress: {metrics['in_progress']}")
print(f"Completed: {metrics['completed']}")
```

## Development

### Running Tests

```bash
pytest _meta/tests/test_workers.py -v
```

### Custom Worker Implementation

```python
from src.workers.base_scoring_worker import BaseScoringWorker
from src.workers import Task, TaskResult

class CustomScoringWorker(BaseScoringWorker):
    """Custom worker with specialized scoring logic."""
    
    def process_task(self, task: Task) -> TaskResult:
        """Implement custom scoring logic."""
        # Your custom implementation
        pass
```

## References

- [Worker Pattern Example](../../Source/TaskManager/_meta/examples/worker_example.py)
- [Video Worker Implementation](../../Source/Video/YouTube/Channel/src/workers/)
- [TaskManager API Documentation](../../Source/TaskManager/README.md)
