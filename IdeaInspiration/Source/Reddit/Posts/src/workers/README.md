# Reddit Workers

This directory contains worker implementations for Reddit scraping tasks using TaskManager API pattern.

## Architecture

The worker system follows SOLID principles and uses pure TaskManager API for task management:

```
Worker → TaskManagerClient → External TaskManager API
       ↓
IdeaInspiration Database (results only)
```

### Components

1. **Base Worker** (`base_worker.py`) - Abstract base class using TaskManager API
2. **Concrete Workers** - Specific implementations for Reddit scraping
   - `reddit_subreddit_worker.py` - Scrapes subreddit posts
3. **Worker Factory** (`factory.py`) - Factory pattern for creating workers

## Worker Pattern

Workers follow this pattern:

1. **Register Task Types** - Register with TaskManager API on startup
2. **Claim Task** - Claim tasks from TaskManager API using configured policy
3. **Process Task** - Execute the scraping logic
4. **Report Result** - Report completion to TaskManager API, save to IdeaInspiration DB

### Task Types

- `PrismQ.Text.Reddit.Post.Subreddit` - Scrape posts from a subreddit

## Usage

### Basic Worker Execution

```python
from src.workers.factory import worker_factory
from src.core.config import Config

# Initialize
config = Config(interactive=False)

# Create worker
worker = RedditSubredditWorker(
    worker_id="worker-01",
    queue_db_path="queue.db",
    config=config,
    claiming_policy="FIFO"  # or LIFO, PRIORITY
)

# Run worker (blocks)
worker.run()
```

### Creating Tasks via TaskManager API

Tasks are created through the TaskManager API, not locally. Use the TaskManager API client:

```python
from TaskManager import TaskManagerClient

# Initialize TaskManager client
client = TaskManagerClient()

# Create a task
task = client.create_task(
    task_type_id=123,  # Get from task type registration
    params={
        "subreddit": "python",
        "limit": 50,
        "sort": "hot"
    },
    priority=5
)
```

## Configuration

Workers require:

1. **TaskManager API** - External REST API for task management:
   ```
   TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
   TASKMANAGER_API_KEY=your_api_key
   ```
2. **Reddit API Credentials** - Set in .env file:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_secret
   REDDIT_USER_AGENT=PrismQ.IdeaInspiration:Reddit:v1.0.0
   ```
3. **IdeaInspiration Database** - Path to save scraped ideas

## Claiming Policies

Workers support different claiming policies via TaskManager API:

- **FIFO** (First-In-First-Out) - Oldest tasks first, fair distribution
- **LIFO** (Last-In-First-Out) - Newest tasks first, low latency
- **PRIORITY** - Highest priority first

## Testing

See `_meta/tests/` for worker tests.

## Design Principles

### SOLID Compliance

- **Single Responsibility** - Each worker handles one task type
- **Open/Closed** - Easy to add new workers without modifying existing code
- **Liskov Substitution** - All workers can substitute BaseWorker
- **Interface Segregation** - Minimal WorkerProtocol interface
- **Dependency Inversion** - Depends on abstractions (Config, Database)

### Additional Patterns

- **Strategy Pattern** - Task claiming strategies
- **Template Method** - BaseWorker defines workflow, subclasses implement specifics
- **Factory Pattern** - Worker factory (planned)

## Future Enhancements

See `_meta/issues/new/Reddit/` for planned improvements.
