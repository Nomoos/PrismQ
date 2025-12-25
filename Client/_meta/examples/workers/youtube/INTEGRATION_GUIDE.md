# YouTube Shorts Scraper Worker - Integration Guide

Complete guide for implementing and deploying the YouTube Shorts Scraper worker in the [PrismQ.T.Idea.Inspiration.Froms.Content.Shorts.YouTube](https://github.com/Nomoos/PrismQ.T.Idea.Inspiration.Froms.Content.Shorts.YouTube) repository.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Worker](#running-the-worker)
6. [Task Processing](#task-processing)
7. [Implementing Real YouTube Scraping](#implementing-real-youtube-scraping)
8. [Error Handling](#error-handling)
9. [Production Deployment](#production-deployment)
10. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
11. [Advanced Usage](#advanced-usage)

## Overview

The YouTube Shorts Scraper Worker is a Python-based distributed task processor that:

- Polls the TaskManager API for new scraping tasks
- Processes YouTube shorts search and metadata extraction
- Reports results back to TaskManager
- Handles failures and retries gracefully

### Key Features

- **Distributed Processing** - Multiple workers can run in parallel
- **Fault Tolerant** - Automatic task claiming prevents duplicate work
- **Scalable** - Easy to add more workers for higher throughput
- **Configurable** - Flexible configuration via CLI or environment variables
- **Production Ready** - Includes logging, monitoring, and graceful shutdown

## Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│                    TaskManager API                       │
│                   (FastAPI + MySQL)                      │
│                                                          │
│  - Task Queue Management                                │
│  - Task Status Tracking                                 │
│  - Worker Coordination                                  │
└──────────────┬───────────────────────────────┬──────────┘
               │                               │
               │ HTTP REST API                 │
               │                               │
    ┌──────────▼─────────┐        ┌───────────▼──────────┐
    │  YouTube Worker 1  │        │  YouTube Worker 2    │
    │                    │        │                      │
    │  - Claim tasks     │        │  - Claim tasks       │
    │  - Scrape YouTube  │        │  - Scrape YouTube    │
    │  - Report results  │        │  - Report results    │
    └────────────────────┘        └──────────────────────┘
```

### Data Flow

```
1. Task Creation
   ┌─────────┐
   │ Client  │ POST /tasks → Creates task with params
   └─────────┘                (search_query, max_results, etc.)
                              
2. Task Claiming
   ┌─────────┐
   │ Worker  │ POST /tasks/claim → Claims next available task
   └─────────┘                     (marks as 'processing')
                              
3. Task Processing
   ┌─────────┐
   │ Worker  │ → YouTube API/Scraping → Extracts metadata
   └─────────┘
                              
4. Task Completion
   ┌─────────┐
   │ Worker  │ POST /tasks/{id}/complete → Marks complete
   └─────────┘                              (stores results)
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Access to TaskManager API
- (Optional) YouTube Data API key for real scraping

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/Nomoos/PrismQ.T.Idea.Inspiration.Froms.Content.Shorts.YouTube
cd PrismQ.T.Idea.Inspiration.Froms.Content.Shorts.YouTube

# Copy worker example from PrismQ.Client
cp -r path/to/PrismQ.Client/_meta/examples/workers/youtube ./worker

# Navigate to worker directory
cd worker

# Install Python dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Check Python version
python --version

# Check dependencies
pip list | grep requests

# Test worker help
python youtube_worker.py --help
```

## Configuration

### Command Line Arguments

The worker accepts configuration via command-line arguments:

```bash
python youtube_worker.py \
  --api-url=http://localhost:8000/api \
  --worker-id=youtube-worker-01 \
  --poll-interval=10 \
  --max-runs=0 \
  --debug
```

### Environment Variables

Alternatively, use environment variables:

```bash
# Create .env file
cat > .env << EOF
TASKMANAGER_API_URL=http://localhost:8000/api
WORKER_ID=youtube-worker-01
POLL_INTERVAL=10
MAX_RUNS=0
DEBUG=false
EOF

# Load and run
export $(cat .env | xargs)
python youtube_worker.py
```

### Configuration Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `--api-url` | `TASKMANAGER_API_URL` | `http://localhost:8000/api` | TaskManager API base URL |
| `--worker-id` | `WORKER_ID` | Auto-generated UUID | Unique worker identifier |
| `--poll-interval` | `POLL_INTERVAL` | `10` | Seconds to wait between polls when no tasks |
| `--max-runs` | `MAX_RUNS` | `0` (unlimited) | Maximum number of tasks to process before exiting |
| `--debug` | `DEBUG` | `false` | Enable verbose debug logging |

## Running the Worker

### Development Mode

For local development and testing:

```bash
# Basic usage (localhost)
python youtube_worker.py

# With debug logging
python youtube_worker.py --debug

# Process limited number of tasks
python youtube_worker.py --max-runs=10
```

### Production Mode

For production deployment:

```bash
# Run with production API URL
python youtube_worker.py \
  --api-url=https://taskmanager.example.com/api \
  --worker-id=youtube-worker-prod-01 \
  --poll-interval=5

# Run in background
nohup python youtube_worker.py \
  --api-url=https://taskmanager.example.com/api \
  --worker-id=youtube-worker-prod-01 \
  > worker.log 2>&1 &

# Check worker process
ps aux | grep youtube_worker
```

### Multiple Workers

Run multiple workers for higher throughput:

```bash
# Terminal 1
python youtube_worker.py --worker-id=youtube-worker-01

# Terminal 2
python youtube_worker.py --worker-id=youtube-worker-02

# Terminal 3
python youtube_worker.py --worker-id=youtube-worker-03
```

Each worker will claim and process tasks independently.

## Task Processing

### Task Structure

Tasks in TaskManager follow this structure:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "PrismQ.YouTube.ScrapeShorts",
  "status": "pending",
  "params": {
    "search_query": "inspiration",
    "max_results": 10,
    "language": "en"
  },
  "created_at": "2025-11-07T17:30:00Z",
  "claimed_at": null,
  "completed_at": null,
  "worker_id": null,
  "result": null,
  "error": null
}
```

### Processing Flow

1. **Claim Task**
   ```python
   task = worker.claim_task()
   # Returns task if available, None otherwise
   ```

2. **Process Task**
   ```python
   result = worker.process_task(task)
   # Executes YouTube scraping logic
   # Returns success/failure with data
   ```

3. **Complete or Fail**
   ```python
   if result['success']:
       worker.complete_task(task['id'], result)
   else:
       worker.fail_task(task['id'], result['message'])
   ```

### Mock Implementation

The example worker uses mock data for demonstration:

```python
def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    params = task.get('params', {})
    search_query = params.get('search_query', 'inspiration')
    max_results = params.get('max_results', 10)
    
    # Simulate API call delay
    time.sleep(2)
    
    # Return mock results
    return {
        'success': True,
        'data': {
            'shorts': [...],  # Mock video data
            'total_found': 5,
            'search_query': search_query
        }
    }
```

## Implementing Real YouTube Scraping

### Option 1: YouTube Data API v3 (Recommended)

**Advantages:**
- Official API with structured data
- Reliable and well-documented
- Rate limits are predictable

**Implementation:**

```python
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """Process YouTube shorts scraping using official API."""
    params = task.get('params', {})
    search_query = params.get('search_query', 'inspiration')
    max_results = params.get('max_results', 10)
    language = params.get('language', 'en')
    
    try:
        # Initialize YouTube API client
        youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        
        # Search for shorts videos
        search_request = youtube.search().list(
            part='snippet',
            q=search_query,
            maxResults=max_results,
            type='video',
            videoDuration='short',  # Filter for short videos
            relevanceLanguage=language
        )
        
        search_response = search_request.execute()
        
        # Extract video IDs
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        
        if not video_ids:
            return {
                'success': True,
                'data': {'shorts': [], 'total_found': 0},
                'message': 'No videos found'
            }
        
        # Get detailed video information
        videos_request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids)
        )
        
        videos_response = videos_request.execute()
        
        # Process results
        shorts = []
        for item in videos_response.get('items', []):
            shorts.append({
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'duration': item['contentDetails']['duration'],
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0)),
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                'video_url': f"https://youtube.com/shorts/{item['id']}"
            })
        
        return {
            'success': True,
            'data': {
                'shorts': shorts,
                'total_found': len(shorts),
                'search_query': search_query,
                'language': language,
                'scraped_at': datetime.now().isoformat()
            },
            'message': f'Successfully scraped {len(shorts)} YouTube shorts'
        }
        
    except HttpError as e:
        return {
            'success': False,
            'message': f'YouTube API error: {e.reason}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }
```

**Dependencies:**

```txt
google-api-python-client>=2.100.0
google-auth-httplib2>=0.1.1
google-auth-oauthlib>=1.1.0
```

**Setup:**

```bash
# Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Get API key from Google Cloud Console
# https://console.cloud.google.com/apis/credentials

# Set API key
export YOUTUBE_API_KEY=your_api_key_here
```

### Option 2: Web Scraping

**Advantages:**
- No API key required
- No rate limits (besides ethical scraping practices)

**Disadvantages:**
- Brittle - breaks when YouTube changes HTML
- Slower than API
- May violate YouTube Terms of Service

**Implementation:**

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """Process YouTube shorts scraping using web scraping."""
    params = task.get('params', {})
    search_query = params.get('search_query', 'inspiration')
    max_results = params.get('max_results', 10)
    
    try:
        # Setup Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        # Navigate to YouTube search for shorts
        search_url = f"https://www.youtube.com/results?search_query={search_query}+shorts"
        driver.get(search_url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'contents')))
        
        # Scroll to load more videos
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Parse page HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract video data (YouTube HTML structure may vary)
        # This is a simplified example
        shorts = []
        video_renderers = soup.find_all('ytd-video-renderer', limit=max_results)
        
        for renderer in video_renderers:
            # Extract video details
            # Note: Selectors may need adjustment based on YouTube's current HTML
            title_elem = renderer.find('a', {'id': 'video-title'})
            channel_elem = renderer.find('ytd-channel-name')
            views_elem = renderer.find('span', {'class': 'style-scope ytd-video-meta-block'})
            
            if title_elem:
                shorts.append({
                    'video_id': title_elem.get('href', '').split('v=')[1] if 'v=' in title_elem.get('href', '') else None,
                    'title': title_elem.text.strip(),
                    'channel': channel_elem.text.strip() if channel_elem else 'Unknown',
                    'views': views_elem.text.strip() if views_elem else '0',
                    'video_url': f"https://youtube.com{title_elem.get('href', '')}"
                })
        
        driver.quit()
        
        return {
            'success': True,
            'data': {
                'shorts': shorts[:max_results],
                'total_found': len(shorts),
                'search_query': search_query,
                'scraped_at': datetime.now().isoformat()
            },
            'message': f'Successfully scraped {len(shorts)} YouTube shorts'
        }
        
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return {
            'success': False,
            'message': f'Scraping error: {str(e)}'
        }
```

**Dependencies:**

```txt
selenium>=4.15.0
beautifulsoup4>=4.12.0
webdriver-manager>=4.0.0
```

## Error Handling

### Built-in Error Handling

The worker includes several error handling mechanisms:

1. **Consecutive Error Limit**
   ```python
   # Worker stops after 5 consecutive errors
   max_consecutive_errors = 5
   ```

2. **Task Failure Reporting**
   ```python
   try:
       result = process_task(task)
   except Exception as e:
       fail_task(task['id'], str(e))
   ```

3. **Graceful Shutdown**
   ```python
   # Handles SIGTERM and SIGINT
   signal.signal(signal.SIGTERM, signal_handler)
   signal.signal(signal.SIGINT, signal_handler)
   ```

### Custom Error Handling

Add custom error handling for specific scenarios:

```python
def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Process task
        result = scrape_youtube(task['params'])
        return {'success': True, 'data': result}
        
    except YouTubeAPIQuotaExceeded as e:
        # Handle quota exceeded
        self.logger.error("YouTube API quota exceeded")
        return {
            'success': False,
            'message': 'API quota exceeded, retry later'
        }
        
    except VideoNotAvailable as e:
        # Handle video not found
        self.logger.warning(f"Video not available: {e}")
        return {
            'success': True,  # Not a fatal error
            'data': {'shorts': [], 'total_found': 0},
            'message': 'No videos found'
        }
        
    except Exception as e:
        # Handle unexpected errors
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }
```

## Production Deployment

### Option 1: Systemd Service (Linux)

Create a systemd service file:

```ini
# /etc/systemd/system/youtube-worker.service
[Unit]
Description=YouTube Shorts Scraper Worker
After=network.target

[Service]
Type=simple
User=worker
WorkingDirectory=/opt/youtube-worker
Environment="TASKMANAGER_API_URL=https://taskmanager.example.com/api"
Environment="WORKER_ID=youtube-worker-prod-01"
Environment="YOUTUBE_API_KEY=your_api_key"
ExecStart=/usr/bin/python3 /opt/youtube-worker/youtube_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable youtube-worker

# Start service
sudo systemctl start youtube-worker

# Check status
sudo systemctl status youtube-worker

# View logs
sudo journalctl -u youtube-worker -f
```

### Option 2: Docker Container

Create Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY youtube_worker.py .

# Run worker
CMD ["python", "youtube_worker.py"]
```

Build and run:

```bash
# Build image
docker build -t youtube-worker .

# Run container
docker run -d \
  --name youtube-worker-01 \
  -e TASKMANAGER_API_URL=https://taskmanager.example.com/api \
  -e WORKER_ID=youtube-worker-docker-01 \
  -e YOUTUBE_API_KEY=your_api_key \
  --restart unless-stopped \
  youtube-worker

# View logs
docker logs -f youtube-worker-01
```

### Option 3: Docker Compose (Multiple Workers)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  youtube-worker-01:
    build: .
    container_name: youtube-worker-01
    environment:
      - TASKMANAGER_API_URL=https://taskmanager.example.com/api
      - WORKER_ID=youtube-worker-01
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
    restart: unless-stopped

  youtube-worker-02:
    build: .
    container_name: youtube-worker-02
    environment:
      - TASKMANAGER_API_URL=https://taskmanager.example.com/api
      - WORKER_ID=youtube-worker-02
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
    restart: unless-stopped

  youtube-worker-03:
    build: .
    container_name: youtube-worker-03
    environment:
      - TASKMANAGER_API_URL=https://taskmanager.example.com/api
      - WORKER_ID=youtube-worker-03
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
    restart: unless-stopped
```

Run:

```bash
# Start all workers
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale youtube-worker-01=5
```

## Monitoring and Troubleshooting

### Logging

The worker provides detailed logging:

```
2025-11-07 17:30:00 [INFO] YouTube Shorts Scraper Worker
2025-11-07 17:30:00 [INFO] Worker ID:      youtube-worker-01
2025-11-07 17:30:00 [INFO] API URL:        http://localhost:8000/api
2025-11-07 17:30:01 [INFO] ✓ API health check passed
2025-11-07 17:30:01 [INFO] Worker started. Waiting for tasks...
2025-11-07 17:30:02 [INFO] ✓ Claimed task 123e4567-e89b-12d3-a456-426614174000
2025-11-07 17:30:04 [INFO] ✓ Successfully scraped 5 shorts
2025-11-07 17:30:04 [INFO] ✓ Task 123e4567-e89b-12d3-a456-426614174000 completed
```

### Health Checks

Check worker health:

```bash
# Check if worker is running
ps aux | grep youtube_worker

# Check recent logs
tail -f worker.log

# Test API connectivity
curl http://localhost:8000/api/health
```

### Common Issues

#### Worker Can't Connect to API

```bash
# Verify API URL
echo $TASKMANAGER_API_URL

# Test connectivity
curl -v http://localhost:8000/api/health

# Check firewall rules
sudo ufw status
```

#### Worker Not Claiming Tasks

```bash
# Check pending tasks
curl http://localhost:8000/api/tasks?status=pending

# Verify task type matches
curl http://localhost:8000/api/tasks/claim \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"task_types": ["PrismQ.YouTube.ScrapeShorts"]}'
```

#### Worker Exits with Errors

```bash
# Enable debug logging
python youtube_worker.py --debug

# Check for Python errors
python -m py_compile youtube_worker.py

# Verify dependencies
pip install -r requirements.txt
```

## Advanced Usage

### Custom Task Handlers

Add support for different task types:

```python
def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    task_type = task['type']
    
    if task_type == 'PrismQ.YouTube.ScrapeShorts':
        return self.scrape_shorts(task['params'])
    elif task_type == 'PrismQ.YouTube.AnalyzeTrends':
        return self.analyze_trends(task['params'])
    elif task_type == 'PrismQ.YouTube.DownloadVideo':
        return self.download_video(task['params'])
    else:
        return {
            'success': False,
            'message': f'Unknown task type: {task_type}'
        }
```

### Rate Limiting

Implement rate limiting to avoid API quotas:

```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        now = datetime.now()
        cutoff = now - self.time_window
        self.requests = [r for r in self.requests if r > cutoff]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = (self.requests[0] - cutoff).total_seconds()
            time.sleep(sleep_time)
        
        self.requests.append(now)

# Use in worker
limiter = RateLimiter(max_requests=100, time_window=timedelta(hours=1))

def process_task(self, task):
    self.limiter.wait_if_needed()
    # Process task...
```

### Caching

Implement caching for frequently accessed data:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1000)
def get_video_metadata(video_id: str):
    """Cache video metadata for 1 hour."""
    # Fetch from YouTube API
    return metadata

# Clear cache periodically
def clear_cache_if_needed():
    if datetime.now() - self.last_cache_clear > timedelta(hours=1):
        get_video_metadata.cache_clear()
        self.last_cache_clear = datetime.now()
```

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
