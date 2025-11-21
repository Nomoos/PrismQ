# HackerNews Stories Integration

Integration module for fetching HackerNews stories with TaskManager API coordination.

## Overview

This module provides:
- **HackerNews API integration** via public Firebase API (no authentication required)
- **TaskManager API integration** for centralized task coordination
- **Multiple plugins** for different story types (top, best, new, ask, show, job)
- **Robust worker implementation** with retry logic and exponential backoff
- **Database utilities** for queue management and results storage

## Quick Start

### 1. Configure Environment

Copy the example configuration:
```bash
cp config.example.env .env
```

Edit `.env` and adjust settings as needed (no credentials required).

### 2. Register Task Types (Optional)

If using TaskManager API:
```bash
python scripts/register_task_types.py
```

### 3. Start Worker

```bash
python -m src.worker
```

## Components

### HackerNews API Client

HackerNews provides a free, public API for accessing stories, comments, and user data.

**Features:**
- No authentication required
- JSON-based REST API
- Real-time data access
- Firebase-backed for reliability

**API Endpoints:**
- Top Stories: `/v0/topstories.json`
- Best Stories: `/v0/beststories.json`
- New Stories: `/v0/newstories.json`
- Ask HN: `/v0/askstories.json`
- Show HN: `/v0/showstories.json`
- Job Stories: `/v0/jobstories.json`
- Item Details: `/v0/item/{id}.json`

**Usage:**
```python
import requests

# Get top story IDs
response = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')
story_ids = response.json()

# Get story details
story = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_ids[0]}.json')
```

### Task Type Registration (`scripts/register_task_types.py`)

Registers HackerNews task types with TaskManager API.

**Task Types:**
1. **PrismQ.Text.HackerNews.Story.Fetch** - Fetch by type
2. **PrismQ.Text.HackerNews.Story.FrontPage** - Front page stories
3. **PrismQ.Text.HackerNews.Story.Best** - Best stories
4. **PrismQ.Text.HackerNews.Story.New** - Newest stories
5. **PrismQ.Text.HackerNews.Story.Ask** - Ask HN stories
6. **PrismQ.Text.HackerNews.Story.Show** - Show HN stories
7. **PrismQ.Text.HackerNews.Story.Job** - Job postings

**Usage:**
```bash
python scripts/register_task_types.py
```

### Workers

#### BaseWorker (`src/workers/base_worker.py`)

Abstract base class providing:
- Task claiming with configurable strategies (FIFO, LIFO, PRIORITY)
- TaskManager API integration
- Retry logic with exponential backoff
- Heartbeat mechanism
- Graceful shutdown

#### HackerNewsStoryWorker (`src/workers/hackernews_story_worker.py`)

Fetches stories from HackerNews API.

### Plugins

Located in `src/plugins/`:
- `hn_frontpage.py` - Fetch front page stories
- `hn_best.py` - Fetch best stories
- `hn_new.py` - Fetch newest stories
- `hn_type.py` - Fetch by story type (ask, show, job)

## Configuration

See `config.example.env` for all configuration options.

**Optional:**
- `HACKERNEWS_API_URL` - API base URL (default: https://hacker-news.firebaseio.com/v0)
- `HACKERNEWS_ENABLE_TASKMANAGER` - Enable TaskManager integration (default: true)
- `HACKERNEWS_WORKER_ID` - Worker identifier
- `HACKERNEWS_POLL_INTERVAL` - Polling interval in seconds (default: 5)
- `HACKERNEWS_MAX_BACKOFF` - Maximum backoff time (default: 60)
- `HACKERNEWS_MAX_STORIES` - Max stories per fetch (default: 500)
- `HACKERNEWS_REQUEST_DELAY` - Delay between requests (default: 0.1s)

## TaskManager Integration

The HackerNews Stories worker integrates with the external TaskManager API service for:
- Centralized task coordination
- Task status tracking
- Result reporting
- Cross-module task prioritization

**Integration Points:**
1. **Task Registration** - Register task types via `register_task_types.py`
2. **Task Claiming** - Worker claims tasks from local queue
3. **Task Processing** - Worker fetches HackerNews content
4. **Result Reporting** - Worker reports completion to TaskManager API

**Note:** Tasks are managed externally via TaskManager REST API. Workers only report completion and connect results by task ID. Results are stored in the IdeaInspiration database.

## Architecture

```
HackerNews/Stories/
├── scripts/
│   ├── register_task_types.py    # Task type registration
│   └── README.md                  # Scripts documentation
│
├── src/
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database utilities
│   │   ├── db_utils.py            # Database helpers
│   │   ├── metrics.py             # Performance metrics
│   │   └── idea_processor.py     # Content processing
│   │
│   ├── workers/
│   │   ├── base_worker.py         # Base worker with TaskManager
│   │   ├── hackernews_story_worker.py
│   │   └── claiming_strategies.py
│   │
│   ├── plugins/
│   │   ├── hn_frontpage.py
│   │   ├── hn_best.py
│   │   ├── hn_new.py
│   │   └── hn_type.py
│   │
│   ├── cli.py                     # Command-line interface
│   └── client.py                  # API client
│
├── _meta/
│   └── tests/
│       ├── test_hackernews_basic.py
│       └── test_hackernews_integration.py
│
└── config.example.env             # Configuration example
```

## Testing

### Run Basic Tests
```bash
python _meta/tests/test_hackernews_basic.py
```

### Run Integration Tests
```bash
python _meta/tests/test_hackernews_integration.py
```

### Test API Connection
```bash
python -c "import requests; \
          r = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json'); \
          print('✓ Connected' if r.status_code == 200 else '✗ Failed')"
```

## Rate Limiting

HackerNews API has no official rate limits, but follow best practices:
- Add delays between requests (0.1s recommended)
- Don't hammer the API
- Cache results when appropriate
- Be respectful of the free service

The worker implements:
- Configurable request delays
- Exponential backoff on errors
- Connection pooling for efficiency

## Data Flow

1. **Task Creation** → Tasks created in local queue or via TaskManager API
2. **Task Claiming** → Worker claims task using configured strategy
3. **Content Fetching** → Worker fetches stories from HackerNews API
4. **Data Mapping** → Stories mapped to IdeaInspiration model
5. **Storage** → Results stored in IdeaInspiration database
6. **Reporting** → Worker reports completion to TaskManager API

## Story Types

### Top Stories
Front page stories with high visibility and engagement.

### Best Stories
High-quality stories based on HackerNews algorithm.

### New Stories
Recently submitted stories (newest first).

### Ask HN
Community questions and discussions.

### Show HN
Project showcases and demonstrations.

### Job Stories
Job postings from companies.

## SOLID Principles

This implementation follows SOLID principles:

- **SRP** - Each class has single responsibility (Worker, Database, Config, etc.)
- **OCP** - Extensible via plugins without modifying base classes
- **LSP** - Workers can substitute base class
- **ISP** - Small, focused interfaces
- **DIP** - Depends on abstractions (Config, Database, TaskManagerClient)

## Troubleshooting

### "Connection refused"
- Check internet connectivity
- Verify API URL is correct
- Check HackerNews status: https://status.ycombinator.com/

### "TaskManager client not available"
- Check TaskManager module is installed
- Verify TaskManager API is running
- Set `HACKERNEWS_ENABLE_TASKMANAGER=false` to disable

### "Failed to fetch stories"
- Check HackerNews API status
- Verify internet connectivity
- Check for rate limiting or blocking

### "Database locked"
- Ensure only one worker per queue database
- Check database permissions
- Verify WAL mode is enabled

## Advantages Over Reddit

- ✅ **No Authentication Required** - Public API, no credentials needed
- ✅ **No Rate Limits** - Be respectful, but no hard limits
- ✅ **High Quality Content** - Tech-focused, curated community
- ✅ **Simple API** - Easy to use, well-documented
- ✅ **Free Forever** - No API fees or subscription

## Related Documentation

- [Issue #003: HackerNews Stories Integration](../../_meta/issues/wip/003-hackernews-stories-integration.md)
- [Text Module Documentation](../../README.md)
- [TaskManager Documentation](../../../../TaskManager/README.md)
- [Model/IdeaInspiration Documentation](../../../../Model/README.md)
- [HackerNews API Documentation](https://github.com/HackerNews/API)

## Contributing

When adding new features:
1. Follow existing code patterns
2. Maintain SOLID principles
3. Add tests for new functionality
4. Update documentation
5. Ensure graceful degradation when dependencies unavailable

## License

Part of PrismQ.IdeaInspiration project.
