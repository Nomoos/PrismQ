# Worker Implementation Guidelines

Comprehensive guidelines for implementing distributed workers that integrate with the PrismQ TaskManager system. Follow these best practices to create reliable, scalable, and maintainable workers.

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [Worker Structure](#worker-structure)
4. [Configuration Management](#configuration-management)
5. [Task Processing](#task-processing)
6. [Error Handling](#error-handling)
7. [Logging](#logging)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Security](#security)
11. [Performance](#performance)
12. [Monitoring](#monitoring)

## Overview

Workers are independent processes that:
1. Poll the TaskManager API for available tasks
2. Claim and process tasks
3. Report results back to TaskManager
4. Handle errors and edge cases gracefully

Workers should be:
- **Autonomous** - Operate independently without manual intervention
- **Resilient** - Recover from failures automatically
- **Scalable** - Support running multiple instances in parallel
- **Observable** - Provide visibility into their operation

## Core Principles

### 1. Stateless Design

Workers should not maintain state between tasks:

✅ **Good**:
```python
def process_task(self, task):
    # Fresh processing for each task
    result = scrape_youtube(task['params'])
    return result
```

❌ **Bad**:
```python
def process_task(self, task):
    # Don't accumulate state across tasks
    self.all_results.append(result)  # Bad!
    return result
```

### 2. Idempotent Operations

Tasks should produce the same result if processed multiple times:

✅ **Good**:
```python
def process_task(self, task):
    video_id = task['params']['video_id']
    # Fetch video data (same result every time)
    return get_video_metadata(video_id)
```

❌ **Bad**:
```python
def process_task(self, task):
    # Don't increment counters or modify shared state
    self.counter += 1  # Bad!
    return self.counter
```

### 3. Fail Fast

Detect errors early and report them:

✅ **Good**:
```python
def process_task(self, task):
    if 'search_query' not in task['params']:
        raise ValueError("Missing required parameter: search_query")
    # Continue processing...
```

❌ **Bad**:
```python
def process_task(self, task):
    # Don't ignore validation
    search_query = task['params'].get('search_query', '')
    # Continue with empty string...
```

### 4. Graceful Degradation

Handle partial failures gracefully:

✅ **Good**:
```python
def process_task(self, task):
    results = []
    errors = []
    for video_id in task['params']['video_ids']:
        try:
            results.append(fetch_video(video_id))
        except Exception as e:
            errors.append({'video_id': video_id, 'error': str(e)})
    
    return {
        'success': len(results) > 0,
        'results': results,
        'errors': errors
    }
```

## Worker Structure

### Recommended Class Structure

```python
class Worker:
    """Base worker implementation."""
    
    def __init__(self, api_url, worker_id, config):
        """Initialize worker with configuration."""
        self.api_url = api_url
        self.worker_id = worker_id
        self.config = config
        self.should_stop = False
        self.stats = {'processed': 0, 'failed': 0}
        
    def health_check(self):
        """Verify API connectivity before starting."""
        pass
        
    def claim_task(self):
        """Claim next available task from queue."""
        pass
        
    def process_task(self, task):
        """Process a single task (implement in subclass)."""
        raise NotImplementedError
        
    def complete_task(self, task_id, result):
        """Mark task as completed with result."""
        pass
        
    def fail_task(self, task_id, error):
        """Mark task as failed with error message."""
        pass
        
    def run(self):
        """Main worker loop."""
        if not self.health_check():
            return 1
            
        while not self.should_stop:
            task = self.claim_task()
            if task:
                try:
                    result = self.process_task(task)
                    self.complete_task(task['id'], result)
                    self.stats['processed'] += 1
                except Exception as e:
                    self.fail_task(task['id'], str(e))
                    self.stats['failed'] += 1
            else:
                time.sleep(self.config['poll_interval'])
                
        return 0
```

### File Organization

```
worker/
├── __init__.py
├── worker.py              # Main worker implementation
├── config.py              # Configuration management
├── api_client.py          # TaskManager API client
├── processors/            # Task processors
│   ├── __init__.py
│   └── youtube.py         # YouTube-specific processing
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── logging.py         # Logging utilities
│   └── validators.py      # Parameter validation
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_worker.py
│   └── test_processors.py
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # Documentation
```

## Configuration Management

### Environment Variables

Use environment variables for configuration:

```python
import os

class Config:
    """Worker configuration."""
    
    # Required settings
    API_URL = os.getenv('TASKMANAGER_API_URL', 'http://localhost:8000/api')
    WORKER_ID = os.getenv('WORKER_ID', f'worker-{uuid.uuid4().hex[:8]}')
    
    # Optional settings with defaults
    POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '10'))
    MAX_RUNS = int(os.getenv('MAX_RUNS', '0'))
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Service-specific settings
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.API_URL:
            raise ValueError("TASKMANAGER_API_URL is required")
```

### Command Line Arguments

Support CLI arguments with argparse:

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='YouTube Worker')
    
    parser.add_argument('--api-url', 
                       default=os.getenv('TASKMANAGER_API_URL'),
                       help='TaskManager API URL')
    
    parser.add_argument('--worker-id',
                       default=os.getenv('WORKER_ID'),
                       help='Worker identifier')
    
    parser.add_argument('--poll-interval',
                       type=int,
                       default=int(os.getenv('POLL_INTERVAL', '10')),
                       help='Poll interval in seconds')
    
    parser.add_argument('--debug',
                       action='store_true',
                       default=os.getenv('DEBUG', '').lower() == 'true',
                       help='Enable debug logging')
    
    return parser.parse_args()
```

### Configuration Priority

1. Command line arguments (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

## Task Processing

### Parameter Validation

Always validate task parameters:

```python
def process_task(self, task):
    """Process YouTube scraping task."""
    params = task.get('params', {})
    
    # Validate required parameters
    required = ['search_query']
    missing = [p for p in required if p not in params]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    
    # Validate parameter types
    if not isinstance(params['search_query'], str):
        raise TypeError("search_query must be a string")
    
    max_results = params.get('max_results', 10)
    if not isinstance(max_results, int) or max_results < 1 or max_results > 50:
        raise ValueError("max_results must be an integer between 1 and 50")
    
    # Process task...
```

### Result Format

Return consistent result format:

```python
def process_task(self, task):
    """Process task and return standardized result."""
    try:
        data = perform_work(task['params'])
        
        return {
            'success': True,
            'data': data,
            'message': f'Successfully processed task',
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'worker_id': self.worker_id,
                'processing_time': elapsed_time
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'metadata': {
                'failed_at': datetime.now().isoformat(),
                'worker_id': self.worker_id
            }
        }
```

### Timeout Handling

Set timeouts for long-running operations:

```python
import signal
from contextlib import contextmanager

# Note: signal.alarm() only works on Unix-like systems (Linux, macOS)
# For Windows compatibility, consider using threading.Timer or asyncio.wait_for

@contextmanager
def timeout(seconds):
    """
    Context manager for timing out operations (Unix-only).
    
    For cross-platform support, use:
    - threading.Timer for simple timeouts
    - asyncio.wait_for for async operations
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def process_task(self, task):
    """Process task with timeout."""
    try:
        with timeout(300):  # 5 minute timeout
            result = perform_work(task['params'])
        return {'success': True, 'data': result}
    except TimeoutError as e:
        return {'success': False, 'error': str(e)}
```

**Cross-platform alternative using threading:**

```python
import threading
from functools import wraps

def timeout(seconds):
    """Cross-platform timeout decorator using threading."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Operation timed out after {seconds} seconds")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        return wrapper
    return decorator

@timeout(300)
def process_task(self, task):
    """Process task with timeout (cross-platform)."""
    result = perform_work(task['params'])
    return {'success': True, 'data': result}
```

## Error Handling

### Exception Hierarchy

Create custom exceptions for different error types:

```python
class WorkerError(Exception):
    """Base worker exception."""
    pass

class TaskValidationError(WorkerError):
    """Task parameter validation failed."""
    pass

class APIConnectionError(WorkerError):
    """Cannot connect to external API."""
    pass

class TaskProcessingError(WorkerError):
    """Error processing task."""
    pass
```

### Retry Logic

Implement exponential backoff for retries:

```python
import time
from functools import wraps

def retry(max_attempts=3, backoff_factor=2, exceptions=(Exception,)):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
        return wrapper
    return decorator

@retry(max_attempts=3, backoff_factor=2, exceptions=(APIConnectionError,))
def fetch_from_api(url):
    """Fetch data from API with retry."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

### Error Reporting

Report detailed error information:

```python
def process_task(self, task):
    """Process task with detailed error reporting."""
    try:
        result = perform_work(task['params'])
        return {'success': True, 'data': result}
        
    except TaskValidationError as e:
        # Validation errors are not retryable
        return {
            'success': False,
            'error': str(e),
            'error_type': 'validation',
            'retryable': False
        }
        
    except APIConnectionError as e:
        # Connection errors are retryable
        return {
            'success': False,
            'error': str(e),
            'error_type': 'connection',
            'retryable': True
        }
        
    except Exception as e:
        # Unknown errors
        logger.exception("Unexpected error processing task")
        return {
            'success': False,
            'error': str(e),
            'error_type': 'unknown',
            'retryable': False,
            'traceback': traceback.format_exc()
        }
```

## Logging

### Structured Logging

Use structured logging with JSON format:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'worker_id': getattr(record, 'worker_id', None),
            'task_id': getattr(record, 'task_id', None),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Log Levels

Use appropriate log levels:

```python
# DEBUG - Detailed diagnostic information
logger.debug(f"Claiming task with params: {params}")

# INFO - General informational messages
logger.info(f"Processing task {task_id}")

# WARNING - Warning messages for recoverable issues
logger.warning(f"API rate limit approaching: {remaining}/{total}")

# ERROR - Error messages for failures
logger.error(f"Failed to process task {task_id}: {error}")

# CRITICAL - Critical errors requiring immediate attention
logger.critical(f"Cannot connect to API after {max_retries} attempts")
```

### Contextual Logging

Add context to log messages:

```python
import logging
from contextlib import contextmanager

@contextmanager
def log_context(**kwargs):
    """Add context to log messages."""
    logger = logging.getLogger(__name__)
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kw):
        record = old_factory(*args, **kw)
        for key, value in kwargs.items():
            setattr(record, key, value)
        return record
    
    logging.setLogRecordFactory(record_factory)
    try:
        yield
    finally:
        logging.setLogRecordFactory(old_factory)

# Usage
with log_context(worker_id=self.worker_id, task_id=task['id']):
    logger.info("Processing task")
    # All logs in this block will include worker_id and task_id
```

## Testing

### Unit Tests

Test individual components:

```python
import unittest
from unittest.mock import Mock, patch

class TestWorker(unittest.TestCase):
    """Unit tests for worker."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.worker = Worker(
            api_url='http://test',
            worker_id='test-worker',
            config={'poll_interval': 1}
        )
    
    def test_claim_task_success(self):
        """Test successful task claiming."""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                'id': 'task-123',
                'type': 'test.task'
            }
            
            task = self.worker.claim_task()
            
            self.assertIsNotNone(task)
            self.assertEqual(task['id'], 'task-123')
    
    def test_process_task_valid_params(self):
        """Test task processing with valid parameters."""
        task = {
            'id': 'task-123',
            'params': {'search_query': 'test', 'max_results': 5}
        }
        
        result = self.worker.process_task(task)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
```

### Integration Tests

Test worker integration with TaskManager:

```python
import unittest
import requests
from worker import Worker

class TestWorkerIntegration(unittest.TestCase):
    """Integration tests for worker."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment."""
        cls.api_url = 'http://localhost:8000/api'
        cls.worker = Worker(api_url=cls.api_url, worker_id='test')
    
    def test_health_check(self):
        """Test API health check."""
        healthy = self.worker.health_check()
        self.assertTrue(healthy)
    
    def test_full_task_lifecycle(self):
        """Test complete task lifecycle."""
        # Create task
        response = requests.post(
            f'{self.api_url}/tasks',
            json={
                'type': 'test.task',
                'params': {'search_query': 'test'}
            }
        )
        task_id = response.json()['id']
        
        # Claim task
        task = self.worker.claim_task()
        self.assertEqual(task['id'], task_id)
        
        # Process task
        result = self.worker.process_task(task)
        self.assertTrue(result['success'])
        
        # Complete task
        completed = self.worker.complete_task(task_id, result)
        self.assertTrue(completed)
```

### Mock Testing

Use mocks for external services:

```python
from unittest.mock import Mock, patch

def test_youtube_api_failure():
    """Test handling of YouTube API failure."""
    worker = YouTubeWorker(api_url='http://test', worker_id='test')
    
    with patch('googleapiclient.discovery.build') as mock_build:
        # Mock API failure
        mock_youtube = Mock()
        mock_youtube.search().list().execute.side_effect = Exception("API Error")
        mock_build.return_value = mock_youtube
        
        # Process task
        task = {'params': {'search_query': 'test'}}
        result = worker.process_task(task)
        
        # Verify error handling
        self.assertFalse(result['success'])
        self.assertIn('API Error', result['error'])
```

## Deployment

### Environment Setup

Create deployment checklist:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with production values

# 3. Verify configuration
python -c "from config import Config; Config.validate()"

# 4. Test connectivity
python -c "from worker import Worker; w = Worker(); w.health_check()"

# 5. Run worker
python worker.py
```

### Systemd Service

Create systemd service for Linux:

```ini
[Unit]
Description=YouTube Shorts Worker
After=network.target

[Service]
Type=simple
User=worker
Group=worker
WorkingDirectory=/opt/youtube-worker
EnvironmentFile=/opt/youtube-worker/.env
ExecStart=/usr/bin/python3 /opt/youtube-worker/worker.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

Create optimized Dockerfile:

```dockerfile
FROM python:3.11-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 worker && \
    chown -R worker:worker /app
USER worker

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from worker import Worker; w = Worker(); exit(0 if w.health_check() else 1)"

# Run worker
CMD ["python", "worker.py"]
```

## Security

### API Key Management

Never hardcode API keys:

✅ **Good**:
```python
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable required")
```

❌ **Bad**:
```python
API_KEY = 'AIzaSyAbc123...'  # Never do this!
```

### Input Validation

Always validate and sanitize inputs:

```python
def validate_search_query(query: str) -> str:
    """Validate and sanitize search query."""
    if not query or not isinstance(query, str):
        raise ValueError("Invalid search query")
    
    # Remove potentially dangerous characters
    query = re.sub(r'[^\w\s-]', '', query)
    
    # Limit length
    if len(query) > 200:
        raise ValueError("Search query too long")
    
    return query.strip()
```

### HTTPS Communication

Always use HTTPS for API communication:

```python
def __init__(self, api_url):
    if not api_url.startswith('https://'):
        logger.warning("API URL should use HTTPS")
    self.api_url = api_url
```

## Performance

### Connection Pooling

Use connection pooling for HTTP requests:

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        # Setup connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
```

### Caching

Implement caching for frequently accessed data:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedAPIClient:
    def __init__(self):
        self.cache_ttl = timedelta(hours=1)
        self.last_cache_clear = datetime.now()
    
    @lru_cache(maxsize=1000)
    def get_video_metadata(self, video_id: str):
        """Get video metadata with caching."""
        return fetch_from_api(video_id)
    
    def clear_cache_if_needed(self):
        """Clear cache after TTL expires."""
        if datetime.now() - self.last_cache_clear > self.cache_ttl:
            self.get_video_metadata.cache_clear()
            self.last_cache_clear = datetime.now()
```

### Batch Processing

Process multiple items in batches:

```python
def process_videos_batch(self, video_ids, batch_size=50):
    """Process videos in batches."""
    results = []
    
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i:i + batch_size]
        
        # Process batch
        response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(batch)
        ).execute()
        
        results.extend(response['items'])
    
    return results
```

## Monitoring

### Metrics Collection

Track key metrics:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WorkerMetrics:
    """Worker performance metrics."""
    
    started_at: datetime
    tasks_claimed: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return self.tasks_completed / total
    
    @property
    def avg_processing_time(self) -> float:
        """Calculate average processing time."""
        if self.tasks_completed == 0:
            return 0.0
        return self.total_processing_time / self.tasks_completed
    
    def report(self):
        """Generate metrics report."""
        uptime = datetime.now() - self.started_at
        return {
            'uptime_seconds': uptime.total_seconds(),
            'tasks_claimed': self.tasks_claimed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'success_rate': self.success_rate,
            'avg_processing_time': self.avg_processing_time
        }
```

### Health Checks

Implement comprehensive health checks:

```python
def health_check(self) -> dict:
    """Comprehensive health check."""
    checks = {}
    
    # API connectivity
    try:
        response = requests.get(f'{self.api_url}/health', timeout=5)
        checks['api_connectivity'] = response.status_code == 200
    except Exception as e:
        checks['api_connectivity'] = False
        checks['api_error'] = str(e)
    
    # External service connectivity
    try:
        # Check YouTube API or other services
        checks['youtube_api'] = self.test_youtube_api()
    except Exception as e:
        checks['youtube_api'] = False
        checks['youtube_error'] = str(e)
    
    # Resource usage
    checks['memory_usage_mb'] = self.get_memory_usage()
    checks['cpu_percent'] = self.get_cpu_usage()
    
    # Worker state
    checks['tasks_processed'] = self.metrics.tasks_completed
    checks['consecutive_errors'] = self.consecutive_errors
    
    checks['healthy'] = all([
        checks['api_connectivity'],
        checks['youtube_api'],
        checks['consecutive_errors'] < self.max_consecutive_errors
    ])
    
    return checks
```

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
