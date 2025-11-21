# YouTube Video Scripts

This directory contains production-ready scripts for deploying and managing YouTube Video Workers.

## Quick Start

```bash
# 1. Configure environment
cp ../.env.example .env
# Edit .env with your API keys and configuration

# 2. Initialize production environment
python init_production.py --register-tasks

# 3. Start worker
python run_worker.py
```

## Available Scripts

### `init_production.py` ⭐ NEW

**Purpose**: Initialize the YouTube Video Worker for production deployment

**Features**:
- Creates necessary directories (data/, logs/, temp/)
- Validates environment configuration
- Initializes IdeaInspiration database
- Initializes local queue database (for testing)
- Tests YouTube API connectivity
- Registers task types with TaskManager API (optional)

**Usage**:
```bash
# Standard initialization
python init_production.py

# Initialize and register task types
python init_production.py --register-tasks

# Use custom .env file
python init_production.py --env-file .env.production

# Skip validation
python init_production.py --skip-validation
```

**When to run:**
- Before first deployment
- After configuration changes
- When setting up new environment

---

### `run_worker.py` ⭐ NEW

**Purpose**: Launch a YouTube Video Worker to process video scraping tasks

**Features**:
- Auto-generates unique worker ID if not provided
- Supports multiple task types
- Configurable poll interval
- Unlimited or limited iterations
- Comprehensive logging
- Graceful shutdown (Ctrl+C)

**Usage**:
```bash
# Run with defaults
python run_worker.py

# Custom worker ID and task type
python run_worker.py --worker-id youtube-worker-001 --task-type youtube_video_search

# Limited iterations (useful for testing)
python run_worker.py --max-iterations 100

# Custom poll interval
python run_worker.py --poll-interval 10
```

**Task Types**:
- `youtube_video_single` - Scrape single video by ID/URL (default)
- `youtube_video_search` - Search and scrape multiple videos
- `youtube_video_scrape` - General scraping (auto-routes)

---

### `verify_task_type.py`

Verifies that all task types are properly registered in the worker factory.

**Usage:**
```bash
# From the Video directory
python scripts/verify_task_type.py

# Or make it executable and run directly
chmod +x scripts/verify_task_type.py
./scripts/verify_task_type.py
```

**What it does:**
- Checks that all three task types are registered
- Verifies the worker factory is working correctly
- No external dependencies required

**Output:**
```
======================================================================
YouTube Video Task Type Verification
======================================================================

Registered task types:
  ✓ youtube_video_single
  ✓ youtube_video_search
  ✓ youtube_video_scrape

Verifying youtube_video_scrape:
  ✅ youtube_video_scrape is registered

Verifying all expected task types:
  ✅ youtube_video_single
  ✅ youtube_video_search
  ✅ youtube_video_scrape

✅ All task types verified successfully!

Task Type Details:
  • youtube_video_single - Scrape single video by ID/URL
  • youtube_video_search - Search and scrape multiple videos
  • youtube_video_scrape - General scraping (auto-routes)

======================================================================
Verification PASSED
======================================================================
```

### `register_task_types.py`

Registers YouTube video scraping task types with the TaskManager API.

**Task Types Registered:**
- `youtube_video_single` - Scrape a single video by ID/URL
- `youtube_video_search` - Search and scrape multiple videos
- `youtube_video_scrape` - General scraping (auto-routes based on parameters)

**Usage:**
```bash
# From the Video directory
python scripts/register_task_types.py

# Or make it executable and run directly
chmod +x scripts/register_task_types.py
./scripts/register_task_types.py
```

**Requirements:**
- TaskManager module must be installed: `pip install -e Source/TaskManager`
- Environment variables must be set:
  - `TASKMANAGER_API_URL` (e.g., https://api.prismq.nomoos.cz/api)
  - `TASKMANAGER_API_KEY` (your API key)

**What it does:**
1. Connects to the TaskManager API
2. Registers all three task types with their JSON schemas
3. Verifies registration was successful
4. Reports any errors

**When to run:**
- During initial deployment
- After updating task type schemas
- When setting up a new environment

**Output:**
```
======================================================================
YouTube Video Task Type Registration
======================================================================
Connected to TaskManager API: https://api.prismq.nomoos.cz/api

Registering task type: youtube_video_single
  ✅ Created - ID: 1
  Description: Scrape a single YouTube video by ID or URL

Registering task type: youtube_video_search
  ✅ Already exists - ID: 2
  Description: Search YouTube and scrape multiple videos

Registering task type: youtube_video_scrape
  ✅ Created - ID: 3
  Description: General YouTube video scraping (auto-routes based on parameters)

======================================================================
Registration complete: 3/3 task types registered
======================================================================

======================================================================
Verifying task type registration...
======================================================================
✅ youtube_video_single - ID: 1 - Active: True
✅ youtube_video_search - ID: 2 - Active: True
✅ youtube_video_scrape - ID: 3 - Active: True

✅ All task types verified successfully!

✅ Registration and verification complete!
```

---

## Production Deployment

### Step 1: Prepare Environment

```bash
# Navigate to Video module
cd Source/Video/YouTube/Video

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### Step 2: Initialize

```bash
# Initialize and register task types
python scripts/init_production.py --register-tasks
```

### Step 3: Start Worker

```bash
# Start single worker
python scripts/run_worker.py

# Or run multiple workers in parallel
python scripts/run_worker.py --worker-id youtube-worker-001 &
python scripts/run_worker.py --worker-id youtube-worker-002 &
python scripts/run_worker.py --worker-id youtube-worker-003 &
```

### Step 4: Monitor

```bash
# View worker log
tail -f youtube_worker.log
```

---

## Environment Configuration

Required environment variables (create `.env` file):

```bash
# YouTube API Configuration (Required)
YOUTUBE_API_KEY=your_youtube_api_key_here

# IdeaInspiration Database (Required)
DATABASE_PATH=data/ideas.db

# TaskManager API (Required for production)
TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
TASKMANAGER_API_KEY=your_taskmanager_api_key_here

# Local Queue Database (Optional - for testing only)
QUEUE_DB_PATH=data/worker_queue.db

# Worker Configuration (Optional)
WORKER_ID=youtube-worker-001
POLL_INTERVAL=5
```

See `../.env.example` for a complete template.

---

## Troubleshooting

### "TaskManager module not found"
```bash
pip install -e Source/TaskManager
```

### "YOUTUBE_API_KEY not set"
```bash
echo "YOUTUBE_API_KEY=your_key_here" >> .env
```

### Worker not claiming tasks
1. Verify TaskManager API is accessible
2. Check API credentials in `.env`
3. Verify task types are registered
4. Check if tasks exist in queue

---

## Adding New Scripts

When adding new scripts:
1. Use descriptive names (e.g., `process_youtube_queue.py`)
2. Add shebang line: `#!/usr/bin/env python3`
3. Include docstring with usage instructions
4. Make executable: `chmod +x scripts/your_script.py`
5. Document in this README
6. Follow SOLID principles
7. Add error handling and logging
