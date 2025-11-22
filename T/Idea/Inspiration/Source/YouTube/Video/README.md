# YouTube Video Scraping Module

**Status**: ✅ PRODUCTION READY  
**Version**: 1.0.0  
**Last Updated**: 2025-11-13

Part of the PrismQ.T.Idea.Inspiration.Sources ecosystem.

---

## 🚀 Quick Start - NEW!

**Get started in 5 minutes!**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.production.example .env
# Edit .env with your API keys

# 3. Initialize
python scripts/init_production.py --register-tasks

# 4. Start worker
python scripts/run_worker.py
```

**📚 Documentation:**
- **Quick Start**: [`QUICKSTART.md`](QUICKSTART.md) - 5-minute setup guide
- **Deployment**: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) - Production deployment
- **Scripts**: [`scripts/README.md`](scripts/README.md) - Script documentation
- **Examples**: [`examples/example_usage.py`](examples/example_usage.py) - Code examples

---

## ⚠️ Important Architecture Note

**Task Management**: Tasks are managed by the external TaskManager API via REST (https://api.prismq.nomoos.cz/api). 
- ⚠️ **Do NOT use local SQLite task queue** - all task management goes through the external REST API
- Workers claim tasks from TaskManager API, not from local database

**Result Storage**: Uses IdeaInspiration model (PrismQ.T.Idea.Inspiration.Model) ✅ Correct architecture.

---

## 🎉 MVP Complete!

The **YouTubeVideoWorker** core functionality is ready with:
- ✅ Worker-based processing system
- ✅ Single video & search-based scraping
- ✅ IdeaInspiration database integration (correct architecture)
- ✅ TaskManager API integration for task management
- ✅ 84% test coverage (13/13 tests passing)
- ✅ SOLID principles validated
- ✅ Complete documentation

**Quick Start**: See [YOUTUBE_VIDEO_WORKER.md](_meta/docs/YOUTUBE_VIDEO_WORKER.md)

---

## Overview

This module handles YouTube video scraping with two approaches:

1. **Worker-Based** (✅ Production Ready - MVP Complete)
2. **Plugin-Based** (Legacy - will be migrated)

---

## Components

### Workers (✅ MVP Complete)

**Location**: `src/workers/`

**Core Infrastructure**:
- `base_worker.py` - Abstract worker base class
- `youtube_video_worker.py` - Video scraping worker
- `factory.py` - Worker factory with dependency injection
- `claiming_strategies.py` - FIFO, LIFO, PRIORITY strategies
- `task_poller.py` - Intelligent task polling

**Features**:
- ✅ Task claiming from TaskManager API via REST
- ✅ Worker heartbeat monitoring
- ✅ Task retry logic
- ✅ Multiple claiming strategies
- ✅ IdeaInspiration result storage (correct architecture)

**Task Types**:
- `youtube_video_single` - Scrape single video by ID/URL
- `youtube_video_search` - Search and scrape multiple videos
- `youtube_video_scrape` - General scraping (auto-routes based on parameters)

### Plugins (Legacy)

**Location**: `src/plugins/`

- `youtube_plugin.py` - API-based video scraping (will be migrated to worker)

---

## Installation

```bash
cd Source/Video/YouTube/Video
pip install -r requirements.txt
```

**Requirements**:
- Python 3.10+
- google-api-python-client
- sqlite3 (built-in)

### Task Type Registration

Before running workers in production, register task types with TaskManager API:

```bash
# Set up environment variables
export TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
export TASKMANAGER_API_KEY=your_api_key_here

# Register task types
python scripts/register_task_types.py
```

This registers:
- `youtube_video_single` - Single video scraping
- `youtube_video_search` - Search-based scraping
- `youtube_video_scrape` - General scraping (auto-routing)

See [scripts/README.md](scripts/README.md) for details.

---

## Usage

### Worker-Based Scraping with TaskManager API

Workers automatically claim tasks from the external TaskManager API:

```python
from src.workers.factory import worker_factory
from src.core.config import Config
from src.core.database import Database

# Initialize configuration and database
config = Config()
results_db = Database(config.database_path)

# Create worker instance
worker = worker_factory.create(
    task_type='youtube_video_single',  # or 'youtube_video_search' or 'youtube_video_scrape'
    worker_id='youtube-worker-1',
    config=config,
    results_db=results_db
)

# Run worker (polls TaskManager API for tasks)
worker.run()
```

### Creating Tasks via TaskManager API

Use the TaskManager client to create tasks:

```python
from TaskManager import TaskManagerClient
import json

# Initialize TaskManager client (uses TASKMANAGER_API_URL and TASKMANAGER_API_KEY from environment)
client = TaskManagerClient()

# Create single video task
task = client.create_task(
    task_type='youtube_video_single',
    params={
        'video_id': 'dQw4w9WgXcQ'
    }
)
print(f"Created task: {task['id']}")

# Create search task
task = client.create_task(
    task_type='youtube_video_search',
    params={
        'search_query': 'startup ideas',
        'max_results': 5
    }
)
print(f"Created task: {task['id']}")

# Create general scrape task (auto-routes)
task = client.create_task(
    task_type='youtube_video_scrape',
    params={
        'video_id': 'dQw4w9WgXcQ'  # or use 'search_query' for search
    }
)
print(f"Created task: {task['id']}")
```

**Note**: Tasks are managed by the external TaskManager API at `https://api.prismq.nomoos.cz/api`. Do not use local SQLite database for task management.

---

## Testing

```bash
# Run all tests
python -m pytest _meta/tests/ -v

# Run with coverage
python -m pytest _meta/tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
python -m pytest _meta/tests/test_youtube_video_worker.py -v
```

**Test Coverage**: 84% (13/13 tests passing)

---

## Architecture

### SOLID Principles

The implementation follows SOLID design principles:

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Extensible via factory registration, stable core
- **Liskov Substitution**: All workers are substitutable
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Depends on abstractions, injected dependencies

See [YOUTUBE_VIDEO_WORKER.md](_meta/docs/YOUTUBE_VIDEO_WORKER.md) for detailed analysis.

### Component Diagram

```
BaseWorker (Abstract)
    ↓
YouTubeVideoWorker
    ├── YouTube API Client
    ├── IdeaInspiration Database
    └── Task Processing Logic

WorkerFactory
    ├── Registers workers by task_type
    └── Creates instances with DI

TaskManager API (External)
    ├── Task queue management via REST
    ├── Worker coordination
    └── Task status tracking
```

---

## Documentation

### Module Documentation

- **[NEXT-STEPS.md](_meta/docs/NEXT-STEPS.md)** - Next steps and action items
- **[YOUTUBE_VIDEO_WORKER.md](_meta/docs/YOUTUBE_VIDEO_WORKER.md)** - Complete MVP guide
- **[src/workers/README.md](src/workers/README.md)** - Worker infrastructure docs

### Parent Documentation

- **Parent YouTube Module**: See `../README.md`
- **Master Plan**: See `../_meta/issues/new/001-refactor-youtube-as-worker-master-plan.md`
- **Issue Tracking**: See `../_meta/issues/new/INDEX.md`

---

## What's Next

### Phase 2: Plugin Migration (Weeks 2-3)

- Migrate Channel plugin to worker
- Migrate Trending plugin to worker  
- Implement Keyword search worker
- Migrate legacy API plugin

See [NEXT-STEPS.md](_meta/docs/NEXT-STEPS.md) for complete roadmap.

### Architectural Considerations

**Worker Infrastructure Location**: Worker infrastructure is currently in `Video/src/workers/`  
**Consideration**: May need to move to `Source/Workers/` for cross-module reuse  
**Timeline**: 1.5-2 days refactoring if needed

---

## Performance

- **Task Claiming**: Fast task claiming from TaskManager API
- **Throughput**: 200-500 tasks/minute (estimated)
- **Concurrency**: Multiple workers can process tasks in parallel
- **Windows Optimized**: Proper settings for RTX 5090 system

---

## Configuration

### Environment Variables

Create `.env` file (see `.env.example`):

```bash
# YouTube API
YOUTUBE_API_KEY=your_api_key_here

# Database (IdeaInspiration storage)
DATABASE_PATH=data/ideas.db

# TaskManager API (External task management)
TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
TASKMANAGER_API_KEY=your_taskmanager_api_key_here

# Worker Configuration
WORKER_ID=youtube-worker-1
POLL_INTERVAL=5
HEARTBEAT_INTERVAL=30
```

---

## Troubleshooting

### Common Issues

**Issue**: `No module named 'google.api_core'`  
**Solution**: `pip install google-api-python-client`

**Issue**: `No module named 'TaskManager'`  
**Solution**: `pip install -e Source/TaskManager`

**Issue**: No tasks being claimed  
**Solution**: Check TaskManager API connection and verify tasks exist via `client.list_tasks()`

**Issue**: Worker not processing  
**Solution**: Check logs, verify API keys are set (YOUTUBE_API_KEY, TASKMANAGER_API_KEY), ensure TaskManager API is accessible

---

## Contributing

### Adding a New Worker

1. Subclass `BaseWorker`
2. Implement `process_task()` method
3. Register with factory: `worker_factory.register('task_type', YourWorker)`
4. Write tests (>80% coverage)
5. Update documentation

Example:
```python
from src.workers.base_worker import BaseWorker
from src.workers import Task, TaskResult

class MyCustomWorker(BaseWorker):
    def process_task(self, task: Task) -> TaskResult:
        # Your implementation
        return TaskResult(
            success=True,
            data={'key': 'value'},
            items_processed=1
        )

# Register
from src.workers.factory import worker_factory
worker_factory.register('my_task_type', MyCustomWorker)
```

---

## License

Proprietary - PrismQ

---

## Contact

**Project Manager**: Worker01  
**Lead Developer**: Worker02 (Python Specialist)  
**Questions?**: See parent YouTube module documentation

**Status**: ✅ MVP Complete - Production Ready  
**Version**: 1.0.0  
**Coverage**: 84%  
**Next Milestone**: Phase 2 Plugin Migration
