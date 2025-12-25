# YouTube Shorts Scraper Worker Example

Production-ready Python worker implementation for processing YouTube shorts scraping tasks from the TaskManager API.

This example demonstrates how to implement a worker in the [PrismQ.T.Idea.Inspiration.Froms.Content.Shorts.YouTube](https://github.com/Nomoos/PrismQ.T.Idea.Inspiration.Froms.Content.Shorts.YouTube) repository.

## 🎯 Overview

This worker implementation shows:

- ✅ **Task claiming** from TaskManager queue
- ✅ **Mock YouTube scraping** - Simulates scraping without actual API calls
- ✅ **Error handling** - Comprehensive error handling with retries
- ✅ **Graceful shutdown** - Handles SIGTERM and SIGINT properly
- ✅ **Configurable polling** - Adjustable poll intervals
- ✅ **Debug logging** - Optional verbose logging for troubleshooting
- ✅ **Production ready** - Ready to be adapted for real YouTube scraping

## 📋 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests
```

### 2. Start the Worker

```bash
# Run with default settings (localhost)
python youtube_worker.py

# Run with custom API URL
python youtube_worker.py --api-url=https://api.example.com/api

# Enable debug logging
python youtube_worker.py --debug

# Process 10 tasks then exit
python youtube_worker.py --max-runs=10
```

### 3. Create Test Tasks

In another terminal:

```bash
# Create test tasks
python test_youtube_worker.py

# Create more test tasks
python test_youtube_worker.py --num-tasks=10
```

## 📁 Files

- **`youtube_worker.py`** - Main worker implementation with mock YouTube scraping
- **`test_youtube_worker.py`** - Test script for creating sample tasks
- **`requirements.txt`** - Python dependencies
- **`README.md`** - This file
- **`INTEGRATION_GUIDE.md`** - Complete implementation guide

## 🔧 Configuration

### Command Line Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `--api-url` | `TASKMANAGER_API_URL` | `http://localhost:8000/api` | TaskManager API URL |
| `--worker-id` | `WORKER_ID` | Auto-generated | Worker identifier |
| `--poll-interval` | `POLL_INTERVAL` | `10` | Seconds between polls |
| `--max-runs` | `MAX_RUNS` | `0` (unlimited) | Max tasks to process |
| `--debug` | `DEBUG` | `false` | Enable debug logging |

### Environment Variables

```bash
# Set environment variables
export TASKMANAGER_API_URL=https://api.example.com/api
export WORKER_ID=youtube-worker-01
export POLL_INTERVAL=5
export DEBUG=true

# Run worker
python youtube_worker.py
```

## 📝 Task Format

### Creating a Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "PrismQ.YouTube.ScrapeShorts",
    "params": {
      "search_query": "inspiration",
      "max_results": 10,
      "language": "en"
    }
  }'
```

### Task Parameters

- **`search_query`** (string, required) - Search term for YouTube shorts
- **`max_results`** (integer, optional) - Maximum number of results (default: 10)
- **`language`** (string, optional) - Language code for results (default: "en")

### Example Response

```json
{
  "success": true,
  "data": {
    "shorts": [
      {
        "video_id": "mock_video_1",
        "title": "Inspiring Short #1: inspiration",
        "description": "A mock short video about inspiration",
        "duration": 46,
        "views": 10000,
        "likes": 500,
        "channel": "Creator 1",
        "published_at": "2025-11-07T17:30:00",
        "thumbnail_url": "https://example.com/thumbnail_1.jpg",
        "video_url": "https://youtube.com/shorts/mock_video_1"
      }
    ],
    "total_found": 5,
    "search_query": "inspiration",
    "language": "en",
    "scraped_at": "2025-11-07T17:30:00"
  },
  "message": "Successfully scraped 5 YouTube shorts"
}
```

## 🚀 Adapting for Real YouTube Scraping

This example uses **mock data** for demonstration. To implement real YouTube scraping:

### Option 1: YouTube Data API v3

```python
from googleapiclient.discovery import build

def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    params = task.get('params', {})
    search_query = params.get('search_query', 'inspiration')
    max_results = params.get('max_results', 10)
    
    # Initialize YouTube API client
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Search for shorts
    request = youtube.search().list(
        part='snippet',
        q=search_query,
        maxResults=max_results,
        type='video',
        videoDuration='short'
    )
    response = request.execute()
    
    # Process results...
    return {'success': True, 'data': results}
```

### Option 2: Web Scraping

```python
from selenium import webdriver
from bs4 import BeautifulSoup

def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    params = task.get('params', {})
    search_query = params.get('search_query', 'inspiration')
    
    # Setup Selenium
    driver = webdriver.Chrome()
    url = f"https://www.youtube.com/results?search_query={search_query}+shorts"
    driver.get(url)
    
    # Extract short videos...
    # Process results...
    
    driver.quit()
    return {'success': True, 'data': results}
```

### Required Dependencies

Add to `requirements.txt`:

```txt
# For YouTube Data API
google-api-python-client>=2.100.0

# For web scraping
selenium>=4.15.0
beautifulsoup4>=4.12.0
```

## 🔄 Worker Lifecycle

```
┌─────────────────────────────────────────────────────┐
│ 1. Worker starts                                    │
│    - Initialize configuration                       │
│    - Setup logging                                  │
│    - Register signal handlers                       │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ 2. Health check                                     │
│    - Verify API connectivity                        │
│    - Exit if API unavailable                        │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ 3. Main loop                                        │
│    ┌─────────────────────────────────────┐          │
│    │ a. Claim task from queue            │          │
│    │    - Filter by task type            │          │
│    │    - Mark as claimed                │          │
│    └──────────┬──────────────────────────┘          │
│               │                                      │
│    ┌──────────▼──────────────────────────┐          │
│    │ b. Process task                     │          │
│    │    - Execute YouTube scraping       │          │
│    │    - Handle errors                  │          │
│    └──────────┬──────────────────────────┘          │
│               │                                      │
│    ┌──────────▼──────────────────────────┐          │
│    │ c. Report result                    │          │
│    │    - Complete or fail task          │          │
│    │    - Store results                  │          │
│    └──────────┬──────────────────────────┘          │
│               │                                      │
│    └──────────┘                                      │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ 4. Graceful shutdown                                │
│    - Wait for current task to complete              │
│    - Report statistics                              │
│    - Exit cleanly                                   │
└─────────────────────────────────────────────────────┘
```

## 🎓 Learning Path

### Basic Usage
1. Start with default settings: `python youtube_worker.py`
2. Create test tasks: `python test_youtube_worker.py`
3. Monitor worker logs to see task processing

### Intermediate
1. Configure custom API URL and worker ID
2. Adjust poll intervals for your workload
3. Enable debug logging for troubleshooting

### Advanced
1. Implement real YouTube API integration
2. Add custom error handling and retry logic
3. Deploy as a systemd service or Docker container
4. Scale to multiple workers for higher throughput

## 📖 Documentation

- **[Integration Guide](./INTEGRATION_GUIDE.md)** - Complete implementation guide
- **[Worker Implementation Plan](../../docs/WORKER_IMPLEMENTATION_PLAN.md)** - Implementation strategy
- **[Worker Guidelines](../../docs/WORKER_IMPLEMENTATION_GUIDELINES.md)** - Best practices
- **[TaskManager API](../../../Backend/TaskManager/docs/API_REFERENCE.md)** - API reference

## 🔗 Related

- [Main Repository](https://github.com/Nomoos/PrismQ.T.Idea.Inspiration.Froms.Content.Shorts.YouTube)
- [TaskManager System](../../../Backend/TaskManager/README.md)
- [PHP Worker Example](../php/README.md)

## 🐛 Troubleshooting

### Worker Can't Connect to API

```bash
# Check API is running
curl http://localhost:8000/api/health

# Try with explicit API URL
python youtube_worker.py --api-url=http://localhost:8000/api --debug
```

### No Tasks Being Claimed

```bash
# Check pending tasks
curl http://localhost:8000/api/tasks?status=pending

# Create test tasks
python test_youtube_worker.py --num-tasks=5
```

### Worker Exits Immediately

```bash
# Check for errors with debug logging
python youtube_worker.py --debug

# Verify task type matches
curl http://localhost:8000/api/tasks/claim \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"task_types": ["PrismQ.YouTube.ScrapeShorts"]}'
```

## 📄 License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
