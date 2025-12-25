# Reddit Posts Integration - TaskManager API Pattern

Integration module for fetching Reddit posts using pure TaskManager API pattern.

## Overview

This module provides:
- **Reddit OAuth authentication** via PRAW (Python Reddit API Wrapper)
- **Pure TaskManager API integration** for task queue management (no local queue)
- **Multiple plugins** for different Reddit content types (subreddit, search, trending, rising)
- **Robust worker implementation** with retry logic and exponential backoff
- **IdeaInspiration database** for storing scraped results

## Architecture

```
Worker → TaskManagerClient → External TaskManager API
       ↓
IdeaInspiration Database (results only)
```

**Key Points:**
- ✅ All task management via external TaskManager REST API
- ✅ No local SQLite queue (TaskManager API handles queuing)
- ✅ Results saved to IdeaInspiration database only
- ✅ Distributed workers can process tasks concurrently
- ✅ Automatic task deduplication and retry via TaskManager API

## Quick Start

### 1. Install Dependencies

```bash
pip install praw python-dotenv click
```

### 2. Configure Reddit API Credentials

Copy the example configuration:
```bash
cp config.example.env .env
```

Edit `.env` and add your Reddit API credentials:
- Get credentials from: https://www.reddit.com/prefs/apps
- See `config.example.env` for detailed instructions

### 3. Configure TaskManager API

Ensure TaskManager API credentials are set:
```bash
# In .env file
TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
TASKMANAGER_API_KEY=your_api_key_here
```

### 4. Start Worker

**Using the worker launcher script:**
```bash
python scripts/run_worker.py
```

**Worker Launcher Options:**
```bash
# Show help
python scripts/run_worker.py --help

# Run with custom worker ID
python scripts/run_worker.py --worker-id reddit-worker-001

# Use LIFO claiming policy
python scripts/run_worker.py --claiming-policy LIFO

# Run for limited iterations (testing)
python scripts/run_worker.py --max-iterations 10

# Use custom .env file
python scripts/run_worker.py --env-file .env.production
```

## Components

### OAuth Client (`src/core/oauth.py`)

Handles Reddit API authentication using PRAW.

**Features:**
- Support for both read-only and read/write modes
- Environment variable configuration
- Graceful handling of missing PRAW library
- Connection testing

**Usage:**
```python
from src.core.oauth import create_reddit_client_from_env

# Create client from environment variables
client = create_reddit_client_from_env()

if client and client.test_connection():
    # Use Reddit API
    reddit = client.reddit
    subreddit = reddit.subreddit("python")
```

### Task Type Registration (`scripts/register_task_types.py`)

Registers Reddit task types with TaskManager API.

**Task Types:**
1. **PrismQ.Text.Reddit.Post.Fetch** - Fetch posts from specific subreddit
2. **PrismQ.Text.Reddit.Post.Search** - Search across Reddit
3. **PrismQ.Text.Reddit.Post.Trending** - Get trending posts

**Usage:**
```bash
python scripts/register_task_types.py
```

### Workers

#### BaseWorker (`src/workers/base_worker.py`)

Abstract base class using pure TaskManager API pattern.

**Features:**
- Task registration with TaskManager API
- Task claiming with configurable policies (FIFO, LIFO, PRIORITY)
- Automatic task polling and exponential backoff
- Result reporting to TaskManager API
- Graceful shutdown and statistics

**Architecture:**
- NO local SQLite queue
- ALL task operations via TaskManager REST API
- Results saved to IdeaInspiration database only

#### RedditSubredditWorker (`src/workers/reddit_subreddit_worker.py`)

Worker for scraping Reddit subreddit posts using TaskManager API.

**Task Type Registered:**
- `PrismQ.Text.Reddit.Post.Subreddit` - Scrape posts from subreddits

**Task Parameters:**
- `subreddit`: Subreddit name (default: 'all')
- `limit`: Number of posts (1-100, default: 10)
- `sort`: Sort method - 'hot', 'new', 'top', 'rising' (default: 'hot')
- `time_filter`: Time filter for 'top' sort (optional)

#### WorkerFactory (`src/workers/factory.py`)

Factory pattern for creating worker instances using TaskManager API.

**Features:**
- Open/Closed Principle (OCP) - extensible without modification
- Lazy worker registration
- Dynamic worker creation based on worker type
- Simplified dependency injection (Config only)

**Usage:**
```python
from workers.factory import worker_factory
from core.config import Config

# Create configuration
config = Config(interactive=False)

# Create worker instance
worker = worker_factory.create(
    worker_type='reddit_subreddit',
    worker_id='reddit-worker-001',
    config=config,
    claiming_policy='FIFO'
)

# Run worker (registers task types automatically)
worker.run()
```

**Supported Worker Types:**
- `reddit_subreddit` - Reddit subreddit scraper worker

### Plugins

Located in `src/plugins/`:
- `reddit_subreddit.py` - Fetch from specific subreddit
- `reddit_search.py` - Search across Reddit
- `reddit_trending.py` - Get trending posts
- `reddit_rising.py` - Get rising posts

## Configuration

See `config.example.env` for all configuration options.

**Required:**
- `REDDIT_CLIENT_ID` - Reddit API client ID
- `REDDIT_CLIENT_SECRET` - Reddit API client secret

**Optional:**
- `REDDIT_USER_AGENT` - User agent string (default: PrismQ-IdeaInspiration/1.0)
- `REDDIT_USERNAME` - For user authentication (leave empty for read-only)
- `REDDIT_PASSWORD` - For user authentication
- `REDDIT_ENABLE_TASKMANAGER` - Enable TaskManager integration (default: true)
- `REDDIT_WORKER_ID` - Worker identifier
- `REDDIT_POLL_INTERVAL` - Polling interval in seconds (default: 5)
- `REDDIT_MAX_BACKOFF` - Maximum backoff time (default: 60)

## TaskManager Integration

The Reddit Posts worker integrates with the external TaskManager API service for:
- Centralized task coordination
- Task status tracking
- Result reporting
- Cross-module task prioritization

**Integration Points:**
1. **Task Registration** - Register task types via `register_task_types.py`
2. **Task Claiming** - Worker claims tasks from local queue
3. **Task Processing** - Worker fetches Reddit content
4. **Result Reporting** - Worker reports completion to TaskManager API

**Note:** Tasks are managed externally via TaskManager REST API. Workers only report completion and connect results by task ID. Results are stored in the IdeaInspiration database.

## Architecture

```
Reddit/Posts/
├── scripts/
│   ├── register_task_types.py    # Task type registration
│   └── README.md                  # Scripts documentation
│
├── src/
│   ├── core/
│   │   ├── oauth.py               # Reddit authentication
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database utilities
│   │   └── ...
│   │
│   ├── workers/
│   │   ├── base_worker.py         # Base worker (TaskManager API)
│   │   ├── reddit_subreddit_worker.py
│   │   └── factory.py             # Worker factory
│   │
│   ├── plugins/
│   │   ├── reddit_subreddit.py
│   │   ├── reddit_search.py
│   │   ├── reddit_trending.py
│   │   └── reddit_rising.py
│   │
│   └── ...
│
├── _meta/
│   └── tests/
│       ├── test_oauth_basic.py    # OAuth client tests
│       ├── test_reddit_worker_basic.py
│       └── ...
│
└── config.example.env             # Configuration example
```

## Testing

### Run OAuth Tests
```bash
python _meta/tests/test_oauth_basic.py
```

### Run Worker Tests
```bash
python _meta/tests/test_reddit_worker_basic.py
```

### Test OAuth Connection
```bash
python -c "from src.core.oauth import create_reddit_client_from_env; \
          client = create_reddit_client_from_env(); \
          print('✓ Connected' if client and client.test_connection() else '✗ Failed')"
```

## Rate Limiting

Reddit API has rate limits:
- **60 requests per minute** for authenticated apps
- **600 requests per 10 minutes**

The worker implements:
- Exponential backoff on rate limit errors
- Configurable polling intervals
- Request delays to stay under limits

## Security

**Best Practices:**
1. ✅ Store credentials in environment variables (`.env` file)
2. ✅ Add `.env` to `.gitignore`
3. ✅ Use read-only mode when write access is not needed
4. ✅ Rotate API keys regularly
5. ✅ Monitor API usage
6. ⚠️ NEVER commit credentials to source control

## Data Flow

1. **Task Creation** → Tasks created in local queue or via TaskManager API
2. **Task Claiming** → Worker claims task using configured strategy
3. **Content Fetching** → Worker uses OAuth client to fetch Reddit content
4. **Data Mapping** → Reddit posts mapped to IdeaInspiration model
5. **Storage** → Results stored in IdeaInspiration database
6. **Reporting** → Worker reports completion to TaskManager API

## SOLID Principles

This implementation follows SOLID principles:

- **SRP** - Each class has single responsibility (OAuth, Worker, Database, etc.)
- **OCP** - Extensible via plugins without modifying base classes
- **LSP** - Workers can substitute base class
- **ISP** - Small, focused interfaces
- **DIP** - Depends on abstractions (Config, Database, TaskManagerClient)

## Troubleshooting

### "PRAW not installed"
```bash
pip install praw
```

### "Invalid credentials"
- Verify `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` are correct
- Check credentials at https://www.reddit.com/prefs/apps

### "429 Too Many Requests"
- Reduce request rate
- Increase `REDDIT_POLL_INTERVAL`
- Implement longer backoff times

### "TaskManager client not available"
- Check TaskManager module is installed
- Verify TaskManager API is running
- Set `REDDIT_ENABLE_TASKMANAGER=false` to disable

## Related Documentation

- [Issue #002: Reddit Posts Integration](../../_meta/issues/wip/002-reddit-posts-integration.md)
- [Text Module Documentation](../../README.md)
- [TaskManager Documentation](../../../../TaskManager/README.md)
- [Model/IdeaInspiration Documentation](../../../../Model/README.md)

## Contributing

When adding new features:
1. Follow existing code patterns
2. Maintain SOLID principles
3. Add tests for new functionality
4. Update documentation
5. Ensure graceful degradation when dependencies unavailable

## License

Part of PrismQ.T.Idea.Inspiration project.
