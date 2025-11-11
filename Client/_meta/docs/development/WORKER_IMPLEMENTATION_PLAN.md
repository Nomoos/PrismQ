# Worker Implementation Plan

Strategic plan for implementing distributed workers in external repositories (e.g., PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTube) to process tasks from the TaskManager system.

## Executive Summary

This document outlines the implementation strategy for creating distributed workers that integrate with the PrismQ TaskManager API. Workers can be deployed in separate repositories to handle specific task types (e.g., YouTube scraping, content processing, data transformation) while maintaining loose coupling with the main PrismQ.Client system.

## Goals

1. **Distributed Architecture** - Enable task processing across multiple repositories and deployments
2. **Loose Coupling** - Workers communicate only via REST API, no shared code dependencies
3. **Scalability** - Support multiple workers processing tasks in parallel
4. **Fault Tolerance** - Handle failures gracefully with automatic retries
5. **Flexibility** - Easy to add new worker types for different task categories

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     PrismQ.Client                           │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              TaskManager API                         │  │
│  │         (FastAPI + MySQL Backend)                    │  │
│  │                                                      │  │
│  │  - Task Queue Management                            │  │
│  │  - Task Status Tracking                             │  │
│  │  - Worker Coordination                              │  │
│  │  - Result Storage                                   │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │ REST API                            │
└──────────────────────┼─────────────────────────────────────┘
                       │
                       │ HTTP/HTTPS
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Worker Repo 1 │ │ Worker Repo 2 │ │ Worker Repo N │
│               │ │               │ │               │
│ YouTube       │ │ Instagram     │ │ Custom        │
│ Scraper       │ │ Scraper       │ │ Processor     │
└───────────────┘ └───────────────┘ └───────────────┘
```

### Data Flow

```
1. Task Creation
   Client/API → TaskManager → Creates task (status: pending)

2. Task Discovery
   Worker → TaskManager → Polls for available tasks

3. Task Claiming
   Worker → TaskManager → Claims task (status: processing)

4. Task Processing
   Worker → External APIs/Services → Processes data

5. Task Completion
   Worker → TaskManager → Reports result (status: completed/failed)
```

## Implementation Phases

### Phase 1: Repository Setup

**Objective**: Prepare the external repository for worker implementation

**Tasks**:
1. Create worker directory structure
2. Setup Python virtual environment
3. Install dependencies (requests, etc.)
4. Configure environment variables
5. Create basic worker skeleton

**Deliverables**:
- Worker directory with proper structure
- `requirements.txt` for dependencies
- Configuration files (.env, config.py)
- Basic worker script

**Example Structure**:
```
PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTube/
├── worker/
│   ├── youtube_worker.py       # Main worker script
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── README.md              # Worker documentation
│   └── tests/
│       └── test_worker.py     # Worker tests
├── src/
│   └── (existing YouTube scraping code)
└── README.md
```

### Phase 2: Core Worker Implementation

**Objective**: Implement core worker functionality

**Tasks**:
1. Implement task claiming logic
2. Add task processing workflow
3. Implement result reporting
4. Add error handling
5. Setup logging

**Key Components**:

**a. Worker Class**
```python
class YouTubeWorker:
    def __init__(self, api_url, worker_id, poll_interval):
        self.api_url = api_url
        self.worker_id = worker_id
        self.poll_interval = poll_interval
        
    def claim_task(self):
        # POST /tasks/claim
        # Returns task or None
        
    def process_task(self, task):
        # Execute task-specific logic
        # Returns result dict
        
    def complete_task(self, task_id, result):
        # POST /tasks/{id}/complete
        
    def fail_task(self, task_id, error):
        # POST /tasks/{id}/fail
        
    def run(self):
        # Main worker loop
        while not self.should_stop:
            task = self.claim_task()
            if task:
                result = self.process_task(task)
                if result['success']:
                    self.complete_task(task['id'], result)
                else:
                    self.fail_task(task['id'], result['error'])
```

**b. Configuration Management**
```python
# Load from environment or CLI arguments
config = {
    'api_url': os.getenv('TASKMANAGER_API_URL', 'http://localhost:8000/api'),
    'worker_id': os.getenv('WORKER_ID', f'worker-{uuid.uuid4().hex[:8]}'),
    'poll_interval': int(os.getenv('POLL_INTERVAL', '10')),
    'max_runs': int(os.getenv('MAX_RUNS', '0')),
    'debug': os.getenv('DEBUG', 'false').lower() == 'true'
}
```

**c. Error Handling**
```python
try:
    result = self.process_task(task)
    self.complete_task(task['id'], result)
except Exception as e:
    logger.error(f"Task processing failed: {e}")
    self.fail_task(task['id'], str(e))
    self.consecutive_errors += 1
    
    if self.consecutive_errors >= self.max_consecutive_errors:
        logger.error("Too many consecutive errors, exiting")
        break
```

**Deliverables**:
- Functional worker that can claim and process tasks
- Comprehensive error handling
- Logging system
- Configuration management

### Phase 3: Task-Specific Implementation

**Objective**: Implement the specific task processing logic (e.g., YouTube scraping)

**Tasks**:
1. Integrate with external APIs/services
2. Implement data extraction logic
3. Add data validation
4. Implement result formatting
5. Add task-specific error handling

**YouTube Worker Example**:
```python
def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """Process YouTube shorts scraping task."""
    params = task.get('params', {})
    search_query = params.get('search_query')
    max_results = params.get('max_results', 10)
    
    try:
        # Initialize YouTube API client
        youtube = build('youtube', 'v3', developerKey=self.api_key)
        
        # Search for shorts
        search_response = youtube.search().list(
            part='snippet',
            q=search_query,
            maxResults=max_results,
            type='video',
            videoDuration='short'
        ).execute()
        
        # Process results
        shorts = []
        for item in search_response.get('items', []):
            shorts.append({
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail_url': item['snippet']['thumbnails']['high']['url']
            })
        
        return {
            'success': True,
            'data': {
                'shorts': shorts,
                'total_found': len(shorts),
                'search_query': search_query
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

**Deliverables**:
- Fully functional task processing
- Integration with external services
- Validated and formatted results

### Phase 4: Testing and Validation

**Objective**: Ensure worker reliability and correctness

**Tasks**:
1. Create unit tests for worker components
2. Create integration tests with TaskManager
3. Test error scenarios
4. Test graceful shutdown
5. Perform load testing

**Test Categories**:

**a. Unit Tests**
```python
def test_claim_task_success():
    worker = YouTubeWorker(api_url='http://test', worker_id='test')
    task = worker.claim_task()
    assert task is not None
    
def test_process_task_valid_params():
    worker = YouTubeWorker(api_url='http://test', worker_id='test')
    result = worker.process_task({
        'params': {'search_query': 'test', 'max_results': 5}
    })
    assert result['success'] == True
```

**b. Integration Tests**
```python
def test_full_task_lifecycle():
    # Create task in TaskManager
    task = create_task({'type': 'PrismQ.YouTube.ScrapeShorts'})
    
    # Worker claims task
    claimed_task = worker.claim_task()
    assert claimed_task['id'] == task['id']
    
    # Worker processes task
    result = worker.process_task(claimed_task)
    
    # Worker completes task
    worker.complete_task(claimed_task['id'], result)
    
    # Verify task status
    updated_task = get_task(task['id'])
    assert updated_task['status'] == 'completed'
```

**c. Error Scenario Tests**
```python
def test_api_unavailable():
    worker = YouTubeWorker(api_url='http://invalid', worker_id='test')
    result = worker.run()
    assert result == 1  # Exit code indicates error

def test_consecutive_errors():
    worker = YouTubeWorker(api_url='http://test', worker_id='test')
    worker.max_consecutive_errors = 3
    # Simulate errors...
    # Worker should exit after 3 errors
```

**Deliverables**:
- Comprehensive test suite
- Test documentation
- Performance benchmarks

### Phase 5: Deployment and Operations

**Objective**: Deploy worker to production and establish monitoring

**Tasks**:
1. Create deployment documentation
2. Setup production configuration
3. Deploy worker (systemd/Docker/Kubernetes)
4. Configure monitoring and alerting
5. Establish operational procedures

**Deployment Options**:

**a. Systemd Service**
```ini
[Unit]
Description=YouTube Shorts Scraper Worker
After=network.target

[Service]
Type=simple
User=worker
WorkingDirectory=/opt/youtube-worker
Environment="TASKMANAGER_API_URL=https://api.example.com"
ExecStart=/usr/bin/python3 youtube_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**b. Docker Container**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY youtube_worker.py .
CMD ["python", "youtube_worker.py"]
```

**c. Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: youtube-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: youtube-worker
  template:
    metadata:
      labels:
        app: youtube-worker
    spec:
      containers:
      - name: youtube-worker
        image: youtube-worker:latest
        env:
        - name: TASKMANAGER_API_URL
          value: "https://api.example.com"
```

**Monitoring**:
- Worker uptime and health
- Tasks processed per hour
- Task success/failure rates
- API response times
- Error rates and types

**Deliverables**:
- Production deployment
- Monitoring dashboard
- Operational runbooks
- Incident response procedures

## Task Type Definition

### Task Structure

All tasks follow a standard structure:

```json
{
  "id": "uuid",
  "type": "PrismQ.YouTube.ScrapeShorts",
  "status": "pending|processing|completed|failed",
  "params": {
    "search_query": "inspiration",
    "max_results": 10,
    "language": "en"
  },
  "created_at": "timestamp",
  "claimed_at": "timestamp",
  "completed_at": "timestamp",
  "worker_id": "worker-id",
  "result": {},
  "error": null
}
```

### Task Type Naming Convention

Use hierarchical naming with dots:
- `PrismQ.YouTube.ScrapeShorts` - Scrape YouTube shorts
- `PrismQ.YouTube.AnalyzeTrends` - Analyze trending videos
- `PrismQ.Instagram.ScrapeReels` - Scrape Instagram reels
- `PrismQ.Content.ProcessText` - Process text content

### Parameter Schema

Define task parameters clearly:

```json
{
  "type": "PrismQ.YouTube.ScrapeShorts",
  "params": {
    "search_query": {
      "type": "string",
      "required": true,
      "description": "Search term for YouTube shorts"
    },
    "max_results": {
      "type": "integer",
      "required": false,
      "default": 10,
      "min": 1,
      "max": 50,
      "description": "Maximum number of results to return"
    },
    "language": {
      "type": "string",
      "required": false,
      "default": "en",
      "pattern": "^[a-z]{2}$",
      "description": "ISO 639-1 language code"
    }
  }
}
```

## API Integration

### Required Endpoints

Workers must integrate with these TaskManager endpoints:

1. **Health Check**
   ```
   GET /api/health
   Response: {"status": "healthy"}
   ```

2. **Claim Task**
   ```
   POST /api/tasks/claim
   Body: {
     "worker_id": "worker-id",
     "task_types": ["PrismQ.YouTube.ScrapeShorts"]
   }
   Response: Task object or null
   ```

3. **Complete Task**
   ```
   POST /api/tasks/{task_id}/complete
   Body: {
     "worker_id": "worker-id",
     "result": {result_data}
   }
   Response: {"status": "success"}
   ```

4. **Fail Task**
   ```
   POST /api/tasks/{task_id}/fail
   Body: {
     "worker_id": "worker-id",
     "error": "error message"
   }
   Response: {"status": "success"}
   ```

### Error Handling

Handle these API scenarios:

- **200 OK** - Success
- **404 Not Found** - No tasks available
- **409 Conflict** - Task already claimed
- **500 Internal Server Error** - API error
- **Connection Timeout** - API unavailable

## Best Practices

### 1. Configuration Management

- Use environment variables for sensitive data
- Provide sensible defaults
- Support both CLI arguments and env vars
- Document all configuration options

### 2. Logging

- Use structured logging (JSON format)
- Include worker_id in all logs
- Log task lifecycle events
- Include timestamps and log levels

### 3. Error Handling

- Catch and log all exceptions
- Report errors back to TaskManager
- Implement exponential backoff for retries
- Set maximum consecutive error limit

### 4. Graceful Shutdown

- Handle SIGTERM and SIGINT signals
- Complete current task before exiting
- Report statistics on shutdown
- Clean up resources properly

### 5. Security

- Never log sensitive data (API keys, passwords)
- Use HTTPS for API communication
- Validate all input parameters
- Implement rate limiting

### 6. Performance

- Implement caching where appropriate
- Use connection pooling
- Batch operations when possible
- Monitor memory usage

### 7. Monitoring

- Track key metrics (tasks/hour, success rate)
- Implement health checks
- Set up alerting for failures
- Monitor resource usage

## Implementation Checklist

- [ ] Repository structure created
- [ ] Dependencies installed
- [ ] Worker class implemented
- [ ] Configuration management setup
- [ ] Task claiming logic implemented
- [ ] Task processing logic implemented
- [ ] Result reporting implemented
- [ ] Error handling added
- [ ] Logging configured
- [ ] Graceful shutdown implemented
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Documentation completed
- [ ] Deployment configuration created
- [ ] Production deployment done
- [ ] Monitoring configured
- [ ] Operational procedures documented

## Success Criteria

1. **Functionality**
   - Worker can claim tasks successfully
   - Worker processes tasks correctly
   - Worker reports results properly
   - Worker handles errors gracefully

2. **Reliability**
   - Worker recovers from transient failures
   - Worker shuts down gracefully
   - Worker doesn't lose tasks
   - Worker doesn't process duplicates

3. **Performance**
   - Worker processes tasks within acceptable time
   - Worker doesn't exceed resource limits
   - Worker scales horizontally

4. **Maintainability**
   - Code is well-documented
   - Tests provide good coverage
   - Configuration is clear
   - Deployment is automated

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Repository Setup | 1-2 days | None |
| Phase 2: Core Implementation | 3-5 days | Phase 1 |
| Phase 3: Task-Specific Logic | 5-10 days | Phase 2 |
| Phase 4: Testing | 3-5 days | Phase 3 |
| Phase 5: Deployment | 2-3 days | Phase 4 |
| **Total** | **14-25 days** | |

## Resources

### Documentation
- [Worker Implementation Guidelines](./WORKER_IMPLEMENTATION_GUIDELINES.md)
- [YouTube Worker Example](../_meta/examples/workers/youtube/README.md)
- [TaskManager API Reference](../../Backend/TaskManager/docs/API_REFERENCE.md)

### Examples
- [YouTube Worker](../_meta/examples/workers/youtube/)
- [PHP Worker](../../examples/workers/php/)

### Tools
- Python 3.7+
- requests library
- pytest for testing
- Docker for containerization

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
