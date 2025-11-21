# YouTube Shorts Source Module

**Platform-optimized YouTube Shorts scraper with comprehensive metadata extraction**

## Overview

This module provides powerful tools for scraping YouTube Shorts content with comprehensive metadata extraction and universal metrics collection. It has been reorganized following SOLID principles for better maintainability and extensibility.

**🎉 NEW**: Restructured into specialized subdirectories for better organization:
- **Video/** - Single video scraping
- **Channel/** - Channel-based scraping
- **Search/** - Trending and search-based scraping

## Module Structure

```
YouTube/
├── Video/                          # Single video scraping
│   ├── src/
│   │   ├── core/                   # Core utilities
│   │   ├── plugins/                # Video plugins
│   │   │   └── youtube_plugin.py
│   │   └── workers/                # Video workers
│   │       └── youtube_video_worker.py
│   ├── README.md
│   └── requirements.txt
│
├── Channel/                        # Channel scraping
│   ├── src/
│   │   ├── core/                   # Core utilities
│   │   ├── plugins/                # Channel plugins
│   │   │   └── youtube_channel_plugin.py
│   │   └── workers/                # Worker infrastructure
│   ├── README.md
│   └── requirements.txt
│
├── Search/                         # Trending/search scraping
│   ├── src/
│   │   ├── core/                   # Core utilities
│   │   ├── plugins/                # Search plugins
│   │   │   └── youtube_trending_plugin.py
```
YouTube/
├── Video/                  # Single video scraping
│   ├── _meta/             # Non-implementation files
│   │   ├── docs/          # Module documentation
│   │   ├── examples/      # Usage examples
│   │   ├── scripts/       # Utility scripts
│   │   └── issues/        # Issue tracking
│   ├── src/               # Implementation files
│   │   ├── core/          # Shared utilities
│   │   ├── plugins/       # youtube_plugin.py
│   │   └── workers/       # youtube_video_worker.py
│   ├── README.md
│   └── requirements.txt
│
├── Channel/                # Channel scraping
│   ├── _meta/             # Non-implementation files
│   │   ├── docs/          # Module documentation
│   │   ├── examples/      # Usage examples
│   │   ├── scripts/       # Utility scripts
│   │   └── issues/        # Issue tracking
│   ├── src/               # Implementation files
│   │   ├── core/          # Shared utilities
│   │   ├── plugins/       # youtube_channel_plugin.py
│   │   └── workers/       # Worker infrastructure
│   ├── README.md
│   └── requirements.txt
│
├── Search/                 # Trending/search scraping
│   ├── _meta/             # Non-implementation files
│   │   ├── docs/          # Module documentation
│   │   ├── examples/      # Usage examples
│   │   ├── scripts/       # Utility scripts
│   │   └── issues/        # Issue tracking
│   ├── src/               # Implementation files
│   │   ├── core/          # Shared utilities
│   │   ├── plugins/       # youtube_trending_plugin.py
│   │   └── workers/       # Worker infrastructure
│   ├── README.md
│   └── requirements.txt
│
└── _meta/                  # Shared documentation
    ├── docs/               # Comprehensive documentation
    └── tests/              # Integration tests
```

## Architecture (SOLID Principles)

The module follows SOLID design principles:

### Single Responsibility Principle (SRP)
- `Config`: Handles configuration management only
- `Database`: Manages database operations only
- `UniversalMetrics`: Calculates and normalizes metrics only
- `IdeaProcessor`: Transforms data to IdeaInspiration format only
- Each plugin handles one specific scraping source
- `BaseWorker`: Handles task lifecycle management only
- Each subdirectory (Video/Channel/Search) handles one specific scraping type

### Open/Closed Principle (OCP)
- `SourcePlugin` is an abstract base class open for extension
- New scrapers can be added by extending `SourcePlugin` without modifying existing code
- `WorkerFactory` allows new workers to be registered without modification

### Liskov Substitution Principle (LSP)
- All YouTube plugins can substitute `SourcePlugin`
- All workers can substitute `BaseWorker` in any context

### Interface Segregation Principle (ISP)
- `SourcePlugin` provides a minimal interface with only required methods: `scrape()` and `get_source_name()`
- `WorkerProtocol` defines only essential methods: `claim_task()`, `process_task()`, `report_result()`

### Dependency Inversion Principle (DIP)
- High-level modules (CLI) depend on abstractions (`SourcePlugin`) not concrete implementations
- Dependencies are injected through constructors (Config, Database)
- Workers depend on abstractions (Config, Database) not concrete implementations

## Subdirectories

### Video/ - Single Video Scraping
Handles scraping individual YouTube videos by ID or URL.
- **Plugin**: `youtube_plugin.py` - API-based video scraping
- **Worker**: `youtube_video_worker.py` - Queue-based processing
- **Use case**: On-demand video metadata extraction

### Channel/ - Channel Scraping
Handles scraping all videos from a YouTube channel.
- **Plugin**: `youtube_channel_plugin.py` - Channel enumeration and video collection
- **Use case**: Bulk channel content analysis

### Search/ - Trending & Search Scraping
Handles trending videos and search-based discovery.
- **Plugin**: `youtube_trending_plugin.py` - Trending page scraping
- **Use case**: Discover viral and trending content

## Module Structure (Legacy - for reference)

```
YouTube/
├── src/
│   ├── __init__.py                 # Main module exports
│   ├── cli.py                      # Command-line interface
│   ├── core/                       # Core utilities (SRP)
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── db_utils.py             # Database utilities
│   │   ├── logging_config.py       # Logging configuration
│   │   ├── metrics.py              # Universal metrics calculation
│   │   └── idea_processor.py      # IdeaInspiration transformation
│   ├── plugins/                    # Scraper plugins (OCP, LSP, ISP)
│   │   ├── __init__.py             # SourcePlugin base class
│   │   ├── youtube_plugin.py       # YouTube API scraper
│   │   ├── youtube_channel_plugin.py  # Channel-based scraper
│   │   └── youtube_trending_plugin.py # Trending page scraper
│   └── workers/                    # 🆕 Worker task queue system
│       ├── __init__.py             # Worker protocols and data classes
│       ├── base_worker.py          # BaseWorker abstract class
│       ├── youtube_video_worker.py # ✅ YouTube video scraping worker (MVP)
│       ├── factory.py              # WorkerFactory for worker creation
│       ├── queue_database.py       # Task queue database management
│       ├── claiming_strategies.py  # Task claiming strategies (FIFO, LIFO, PRIORITY)
│       ├── task_poller.py          # Task polling with exponential backoff
│       └── schema.sql              # Database schema for task queue
├── tests/                          # Unit and integration tests
├── _meta/                          # Module metadata
│   ├── docs/                       # Comprehensive documentation
│   │   └── YOUTUBE_VIDEO_WORKER.md # 🆕 Worker MVP documentation
│   ├── issues/                     # Issue tracking (new/wip/done)
│   │   └── new/NEXT-STEPS.md       # Updated with MVP completion
│   └── research/                   # Research and experiments
├── scripts/                        # Utility scripts
│   └── init_queue_db.py            # 🆕 Initialize task queue database
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Package configuration
├── .env.example                    # Environment configuration template
└── README.md                       # This file
```

## Features

### 🆕 Worker-Based Task Queue (MVP COMPLETE)

**NEW**: Scalable, concurrent task processing with SQLite queue:

- **YouTubeVideoWorker**: Production-ready worker for YouTube video scraping
- **Task Queue**: SQLite-based task queue with atomic claiming (<10ms)
- **Claiming Strategies**: FIFO, LIFO, PRIORITY, WEIGHTED_RANDOM
- **Worker Pool**: Support for concurrent multi-worker execution
- **IdeaInspiration Integration**: Automatic transformation and storage
- **Monitoring**: Worker health tracking and task statistics
- **Error Handling**: Robust error handling with retry logic

See [Worker Documentation](_meta/docs/YOUTUBE_VIDEO_WORKER.md) for complete guide.

### Scraping Modes

1. **🆕 Worker-Based Video Scraping** (`src/workers/youtube_video_worker.py`) ✅ MVP COMPLETE
   - Task queue-based processing
   - Single video scraping by ID/URL
   - Search-based scraping with multiple results
   - IdeaInspiration integration
   - Production-ready with 84% test coverage

2. **YouTube API Search** (`src/plugins/youtube_plugin.py`)
   - Uses YouTube Data API v3
   - Search-based scraping with keywords
   - Requires API key (quota limited)

3. **Channel-Based Scraping** (`src/plugins/youtube_channel_plugin.py`)
   - Uses yt-dlp for channel scraping
   - No API quota limits
   - Rich metadata including subtitles
   - Engagement analytics

4. **Trending Scraping** (`src/plugins/youtube_trending_plugin.py`)
   - Scrapes from YouTube trending page
   - No API key required
   - Discovery of viral content

### Key Capabilities

- **🆕 Task Queue System**: Scalable task processing with worker pools
- **🆕 Atomic Task Claiming**: Fast (<10ms) and concurrent-safe
- **Comprehensive Metadata**: Title, description, tags, statistics, channel info
- **Subtitle Extraction**: Automatic subtitle download and parsing
- **Universal Metrics**: Standardized metrics for cross-platform analysis
- **Engagement Analytics**: Views per day/hour, engagement rates, ratios
- **Deduplication**: Prevents duplicate entries using (source, source_id) constraint
- **SQLite Storage**: Persistent storage with complete metadata
- **IdeaInspiration Transform**: Compatible with PrismQ.IdeaInspiration.Model

## Installation

### Prerequisites

- Python 3.10 or higher
- Windows OS (recommended) or Linux
- NVIDIA GPU with CUDA support (optional, for future AI features)

### Quick Start

```bash
# Navigate to the YouTube module
cd Sources/Content/Shorts/YouTube

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# (YouTube API key, database path, etc.)

# Run a scrape command
python -m src.cli scrape-channel --channel "https://youtube.com/@channel"
```

### Quick Test

To quickly test the module with example data:

```bash
# Use the test configuration
cp .env.test.example .env.test

# Test scraping from SnappyStories_1 channel (5 shorts)
python -m src.cli scrape-channel --env-file .env.test --top 5

# View collected data
python -m src.cli list --env-file .env.test

# Clean up test database
python -m src.cli clear --env-file .env.test
```

## Usage

### 🆕 Worker-Based Task Queue (Recommended)

**NEW**: Use the worker system for scalable, concurrent processing:

```bash
# 1. Initialize the task queue database
python scripts/init_queue_db.py

# 2. Add tasks to the queue (via CLI or API)
# Coming soon: CLI integration for task creation

# 3. Run a worker to process tasks
python -c "
from src.workers.factory import worker_factory
from src.core.config import Config
from src.core.database import Database

config = Config()
results_db = Database(config.database_path)

# Create a worker
worker = worker_factory.create(
    task_type='youtube_video_single',
    worker_id='youtube-worker-1',
    queue_db_path='data/worker_queue.db',
    config=config,
    results_db=results_db
)

# Run worker (processes tasks continuously)
worker.run(poll_interval=5, max_iterations=100)
"

# 4. Run multiple workers concurrently for high throughput
# Worker01, Worker02, Worker03... can all process tasks in parallel
```

**Python API**:

```python
from src.workers.factory import worker_factory
from src.core.config import Config
from src.core.database import Database

# Initialize
config = Config()
results_db = Database(config.database_path)

# Create worker
worker = worker_factory.create(
    task_type='youtube_video_single',
    worker_id='my-worker',
    queue_db_path='data/worker_queue.db',
    config=config,
    results_db=results_db
)

# Process tasks
worker.run(poll_interval=5)
```

See [Worker Documentation](_meta/docs/YOUTUBE_VIDEO_WORKER.md) for complete guide.

### Command Line Interface (Legacy)

```bash
# YouTube API search (legacy - quota limited)
python -m src.cli scrape

# Channel-based scraping (recommended)
python -m src.cli scrape-channel --channel "https://youtube.com/@channel"

# Example with test channel
python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 5

# Trending page scraping
python -m src.cli scrape-trending --max-results 50

# Keyword search
python -m src.cli scrape-keyword --query "startup ideas"

# Process ideas to IdeaInspiration format
python -m src.cli process

# View database statistics
python -m src.cli stats

# Export to JSON
python -m src.cli export --output ideas.json
```

### Python API

```python
from src import Config, Database, YouTubeChannelPlugin, UniversalMetrics

# Initialize components (Dependency Injection)
config = Config()
db = Database(config.database_path)

# Use a scraper plugin (Polymorphism via SourcePlugin)
plugin = YouTubeChannelPlugin(config)
ideas = plugin.scrape()

# Process metrics
for idea in ideas:
    metrics = UniversalMetrics.from_youtube(idea['metrics'])
    print(f"Engagement rate: {metrics.engagement_rate}%")
    
    # Save to database
    db.insert_idea(
        source=plugin.get_source_name(),
        source_id=idea['source_id'],
        title=idea['title'],
        description=idea['description'],
        tags=idea['tags'],
        score=metrics.engagement_rate or 0.0,
        score_dictionary=metrics.to_dict()
    )
```

## Configuration

Configuration is managed through `.env` file. See `.env.example` for all available options:

```bash
# YouTube API Configuration
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_MAX_RESULTS=50

# Database Configuration
DATABASE_PATH=./youtube_shorts.db

# Scraping Configuration  
MAX_VIDEO_LENGTH=180  # 3 minutes for Shorts
MIN_ASPECT_RATIO=0.5  # Vertical format validation

# Working Directory
WORKING_DIR=./
```

See [_meta/docs/CONFIGURATION.md](_meta/docs/CONFIGURATION.md) for detailed configuration guide.

## Documentation

### Core Architecture (Windows-Focused)

- **[EXECUTION_FLOW.md](docs/EXECUTION_FLOW.md)** - Complete Windows execution flow from Web Client to database
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Module architecture and SOLID design patterns
- **[KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)** - Known limitations and Windows-specific issues
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common problems and Windows debugging

### Usage & Configuration

- **[Quick Reference Card](_meta/docs/QUICK_REFERENCE.md)** - Fast command reference (Czech/English)
- **[Manual Testing Procedure](_meta/docs/MANUAL_TESTING_PROCEDURE.md)** - Complete step-by-step manual testing guide (Czech/English)
- **[Testing Guide](_meta/docs/TESTING_GUIDE.md)** - Testing with example channels and URLs
- **[Configuration Guide](_meta/docs/CONFIGURATION.md)** - Working directories, .env management
- **[Windows Quickstart](_meta/docs/WINDOWS_QUICKSTART.md)** - Windows-specific setup

### Advanced Topics

- **[Inspiration Sources](_meta/docs/INSPIRATION_SOURCES.md)** - Curated YouTube channels for content ideas
- **[Channel Scraping](_meta/docs/CHANNEL_SCRAPING.md)** - Advanced channel scraping features
- **[Metrics Documentation](_meta/docs/METRICS.md)** - Universal metrics system
- **[YouTube Data Model](_meta/docs/YTB_DATA_MODEL.md)** - Complete database schema
- **[Data Collection Guide](_meta/docs/DATA_COLLECTION_GUIDE.md)** - What data we collect
- **[Scraping Best Practices](_meta/docs/SCRAPING_BEST_PRACTICES.md)** - Safety and re-scraping
- **[Contributing](_meta/docs/CONTRIBUTING.md)** - How to contribute

For a complete list of documentation, see [_meta/docs/](_meta/docs/) and [docs/](docs/).

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test file
pytest tests/test_youtube_channel_plugin.py -v
```

## Design Patterns Used

1. **Abstract Factory Pattern**: `SourcePlugin` as factory interface
2. **Strategy Pattern**: Different scraping strategies via plugins
3. **Dependency Injection**: Config and Database injected into components
4. **Repository Pattern**: Database abstraction for data access
5. **Builder Pattern**: Config builder for environment setup

## Integration with PrismQ Ecosystem

This module integrates with:

- **[PrismQ.IdeaInspiration.Model](../../Model/)** - Data model for IdeaInspiration
- **[PrismQ.IdeaInspiration.Classification](../../Classification/)** - Content classification
- **[PrismQ.IdeaInspiration.Scoring](../../Scoring/)** - Content scoring

Use `IdeaProcessor` to transform scraped data to the standardized format.

## Performance Considerations

- **API Rate Limiting**: YouTube API has daily quota limits (use yt-dlp alternatives)
- **Batch Processing**: Process ideas in batches to minimize database writes
- **Caching**: Config and database connections are reused
- **Memory Management**: Large datasets are processed iteratively

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

## Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report via GitHub Issues
- **Contributing**: See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
