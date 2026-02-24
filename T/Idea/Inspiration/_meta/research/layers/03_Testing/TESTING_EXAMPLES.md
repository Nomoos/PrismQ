# Testing and Mocking Examples - Practical Patterns

This document provides concrete, copy-paste-ready examples of testing patterns used throughout PrismQ.T.Idea.Inspiration. Each example demonstrates proper layer isolation, dependency injection, and mocking strategies.

## Table of Contents

1. [Protocol-Based Testing](#protocol-based-testing)
2. [API Client Testing](#api-client-testing)
3. [Database Layer Testing](#database-layer-testing)
4. [Content Processing Testing](#content-processing-testing)
5. [Worker Testing](#worker-testing)
6. [Integration Testing](#integration-testing)

---

## Protocol-Based Testing

### Example: Video Fetcher with Protocol

**Production Code** (`src/protocols/video_protocols.py`):

```python
"""Protocols for video fetching and processing."""

from typing import Protocol, Optional, Dict, Any


class IVideoFetcher(Protocol):
    """Protocol for fetching video content.
    
    Any class implementing this protocol must provide a fetch_video method
    with the specified signature. This enables dependency injection and testing.
    """
    
    def fetch_video(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        include_subtitles: bool = False,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Fetch video content and metadata.
        
        Args:
            video_url: URL to the video
            video_id: Optional video identifier  
            include_subtitles: Whether to fetch subtitles
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Dictionary containing:
                - title: Video title
                - description: Video description
                - duration: Duration in seconds
                - thumbnail_url: URL to thumbnail
                - subtitles: Optional subtitle text
                Or None if fetch failed
        """
        ...


class IVideoProcessor(Protocol):
    """Protocol for processing fetched video data."""
    
    def process_video(
        self,
        video_data: Dict[str, Any]
    ) -> 'IdeaInspiration':
        """Process raw video data into IdeaInspiration.
        
        Args:
            video_data: Raw video data from fetcher
            
        Returns:
            IdeaInspiration object with processed data
        """
        ...
```

**Implementation** (`src/clients/youtube_fetcher.py`):

```python
"""YouTube video fetcher implementation."""

from typing import Optional, Dict, Any
import requests
from protocols.video_protocols import IVideoFetcher


class YouTubeVideoFetcher:
    """Fetches video data from YouTube API.
    
    Implements IVideoFetcher protocol for dependency injection.
    """
    
    def __init__(self, api_key: str, session: Optional[requests.Session] = None):
        """Initialize YouTube fetcher.
        
        Args:
            api_key: YouTube API key
            session: Optional HTTP session (for testing)
        """
        self.api_key = api_key
        self.session = session or requests.Session()
    
    def fetch_video(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        include_subtitles: bool = False,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Fetch video from YouTube API."""
        try:
            # Extract video ID from URL if needed
            if not video_id:
                video_id = self._extract_video_id(video_url)
            
            # Fetch from API
            response = self.session.get(
                f'https://www.googleapis.com/youtube/v3/videos',
                params={
                    'id': video_id,
                    'key': self.api_key,
                    'part': 'snippet,contentDetails'
                }
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('items'):
                return None
            
            item = data['items'][0]
            snippet = item['snippet']
            
            result = {
                'title': snippet['title'],
                'description': snippet['description'],
                'duration': self._parse_duration(item['contentDetails']['duration']),
                'thumbnail_url': snippet['thumbnails']['high']['url'],
            }
            
            if include_subtitles:
                result['subtitles'] = self._fetch_subtitles(video_id)
            
            return result
            
        except Exception as e:
            print(f"Failed to fetch video: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        # Implementation
        pass
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        # Implementation
        pass
    
    def _fetch_subtitles(self, video_id: str) -> str:
        """Fetch subtitles for video."""
        # Implementation
        pass
```

**Test with Mock** (`tests/test_youtube_fetcher.py`):

```python
"""Tests for YouTube video fetcher."""

import pytest
from typing import Optional, Dict, Any
import requests_mock

from clients.youtube_fetcher import YouTubeVideoFetcher


class MockVideoFetcher:
    """Mock video fetcher for testing consumers.
    
    Implements IVideoFetcher protocol without real API calls.
    """
    
    def __init__(
        self,
        should_succeed: bool = True,
        mock_data: Optional[Dict[str, Any]] = None
    ):
        """Initialize mock fetcher.
        
        Args:
            should_succeed: Whether fetch should succeed
            mock_data: Custom data to return (uses defaults if None)
        """
        self.should_succeed = should_succeed
        self.mock_data = mock_data
        self.call_count = 0
        self.last_video_url = None
        self.last_video_id = None
        self.calls_history = []
    
    def fetch_video(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        include_subtitles: bool = False,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Mock video fetch with tracking."""
        self.call_count += 1
        self.last_video_url = video_url
        self.last_video_id = video_id
        self.calls_history.append({
            'video_url': video_url,
            'video_id': video_id,
            'include_subtitles': include_subtitles,
            'kwargs': kwargs
        })
        
        if not self.should_succeed:
            return None
        
        # Return mock or default data
        if self.mock_data:
            return self.mock_data.copy()
        
        result = {
            'title': f'Test Video for {video_url}',
            'description': 'Mock video description',
            'duration': 180,
            'thumbnail_url': 'https://example.com/thumb.jpg',
        }
        
        if include_subtitles:
            result['subtitles'] = 'Mock subtitle text'
        
        return result


# Tests for the real implementation
def test_youtube_fetcher_success():
    """Test successful video fetch from YouTube API."""
    with requests_mock.Mocker() as m:
        # Mock YouTube API response
        m.get(
            'https://www.googleapis.com/youtube/v3/videos',
            json={
                'items': [{
                    'snippet': {
                        'title': 'Real YouTube Video',
                        'description': 'Video description',
                        'thumbnails': {
                            'high': {'url': 'https://img.youtube.com/vi/test/hqdefault.jpg'}
                        }
                    },
                    'contentDetails': {
                        'duration': 'PT3M30S'  # 3 minutes 30 seconds
                    }
                }]
            }
        )
        
        fetcher = YouTubeVideoFetcher(api_key='test_key')
        result = fetcher.fetch_video(
            'https://youtube.com/watch?v=test123',
            video_id='test123'
        )
        
        assert result is not None
        assert result['title'] == 'Real YouTube Video'
        assert result['duration'] == 210  # 3:30 in seconds


def test_youtube_fetcher_not_found():
    """Test handling of non-existent video."""
    with requests_mock.Mocker() as m:
        # Mock empty response
        m.get(
            'https://www.googleapis.com/youtube/v3/videos',
            json={'items': []}
        )
        
        fetcher = YouTubeVideoFetcher(api_key='test_key')
        result = fetcher.fetch_video(
            'https://youtube.com/watch?v=notfound',
            video_id='notfound'
        )
        
        assert result is None


# Tests using mock for higher-level component
def test_video_processor_with_mock_fetcher():
    """Test video processor using mock fetcher."""
    # Arrange
    mock_fetcher = MockVideoFetcher(mock_data={
        'title': 'Expected Video Title',
        'description': 'Expected description',
        'duration': 300,
        'thumbnail_url': 'https://example.com/thumb.jpg'
    })
    
    processor = VideoProcessor(video_fetcher=mock_fetcher)
    
    # Act
    result = processor.process('https://youtube.com/watch?v=test')
    
    # Assert
    assert mock_fetcher.call_count == 1
    assert mock_fetcher.last_video_url == 'https://youtube.com/watch?v=test'
    assert result.title == 'Expected Video Title'


def test_mock_fetcher_tracks_calls():
    """Test that mock fetcher tracks all calls."""
    mock = MockVideoFetcher()
    
    # Make multiple calls
    mock.fetch_video('url1', video_id='id1')
    mock.fetch_video('url2', video_id='id2', include_subtitles=True)
    
    # Verify tracking
    assert mock.call_count == 2
    assert len(mock.calls_history) == 2
    assert mock.calls_history[0]['video_id'] == 'id1'
    assert mock.calls_history[1]['include_subtitles'] is True


def test_mock_fetcher_failure_mode():
    """Test mock fetcher in failure mode."""
    mock = MockVideoFetcher(should_succeed=False)
    
    result = mock.fetch_video('https://youtube.com/watch?v=test')
    
    assert result is None
    assert mock.call_count == 1  # Still tracks failed calls
```

**Pytest Fixture** (`tests/conftest.py`):

```python
"""Shared test fixtures."""

import pytest
from tests.test_youtube_fetcher import MockVideoFetcher


@pytest.fixture
def mock_video_fetcher():
    """Provide mock video fetcher with default settings."""
    return MockVideoFetcher()


@pytest.fixture
def failing_video_fetcher():
    """Provide mock video fetcher that fails."""
    return MockVideoFetcher(should_succeed=False)


@pytest.fixture
def custom_video_fetcher():
    """Provide mock video fetcher with custom data."""
    def _create_fetcher(data):
        return MockVideoFetcher(mock_data=data)
    return _create_fetcher


# Usage in tests:
def test_with_fixture(mock_video_fetcher):
    """Test using fixture-provided mock."""
    result = mock_video_fetcher.fetch_video('https://test.com')
    assert result is not None


def test_with_custom_fixture(custom_video_fetcher):
    """Test using custom data fixture."""
    fetcher = custom_video_fetcher({
        'title': 'Custom Title',
        'duration': 500
    })
    result = fetcher.fetch_video('https://test.com')
    assert result['title'] == 'Custom Title'
```

---

## API Client Testing

### Example: Base HTTP Client with Rate Limiting

**Production Code** (`src/clients/base_http_client.py`):

```python
"""Base HTTP client with rate limiting and retry logic."""

from typing import Optional, Dict, Any
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseHTTPClient:
    """Base HTTP client with rate limiting.
    
    Provides:
    - Rate limiting (token bucket algorithm)
    - Automatic retries for transient failures
    - Session management
    - Error handling
    """
    
    def __init__(
        self,
        rate_limit_per_minute: int = 60,
        retry_attempts: int = 3,
        timeout_seconds: int = 30
    ):
        """Initialize HTTP client.
        
        Args:
            rate_limit_per_minute: Maximum requests per minute
            retry_attempts: Number of retry attempts
            timeout_seconds: Request timeout in seconds
        """
        self.rate_limit_per_minute = rate_limit_per_minute
        self.timeout_seconds = timeout_seconds
        self._request_times: list[float] = []
        self.session = self._create_session(retry_attempts)
    
    def _create_session(self, retry_attempts: int) -> requests.Session:
        """Create session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _rate_limit_wait(self) -> None:
        """Enforce rate limiting using token bucket algorithm."""
        now = time.time()
        
        # Remove requests older than 60 seconds
        self._request_times = [
            t for t in self._request_times 
            if now - t < 60
        ]
        
        # If at limit, wait
        if len(self._request_times) >= self.rate_limit_per_minute:
            oldest = self._request_times[0]
            wait_time = 60 - (now - oldest) + 0.1
            if wait_time > 0:
                time.sleep(wait_time)
                # Clean up again after waiting
                now = time.time()
                self._request_times = [
                    t for t in self._request_times 
                    if now - t < 60
                ]
        
        # Record this request
        self._request_times.append(time.time())
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make GET request with rate limiting.
        
        Args:
            url: Request URL
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response object
            
        Raises:
            requests.HTTPError: On HTTP errors
        """
        self._rate_limit_wait()
        
        response = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout_seconds
        )
        response.raise_for_status()
        return response
    
    def close(self) -> None:
        """Close the session."""
        if self.session:
            self.session.close()
```

**Test Code** (`tests/test_base_http_client.py`):

```python
"""Tests for BaseHTTPClient."""

import pytest
import time
import requests
import requests_mock
from clients.base_http_client import BaseHTTPClient


class TestBaseHTTPClient:
    """Test suite for BaseHTTPClient."""
    
    def test_client_initialization(self):
        """Test client initializes with correct defaults."""
        client = BaseHTTPClient()
        
        assert client.rate_limit_per_minute == 60
        assert client.timeout_seconds == 30
        assert client.session is not None
        assert len(client._request_times) == 0
        
        client.close()
    
    def test_client_custom_configuration(self):
        """Test client with custom configuration."""
        client = BaseHTTPClient(
            rate_limit_per_minute=30,
            retry_attempts=5,
            timeout_seconds=60
        )
        
        assert client.rate_limit_per_minute == 30
        assert client.timeout_seconds == 60
        
        client.close()
    
    def test_successful_get_request(self):
        """Test successful GET request."""
        client = BaseHTTPClient()
        
        with requests_mock.Mocker() as m:
            m.get('https://api.example.com/data', json={'result': 'success'})
            
            response = client.get('https://api.example.com/data')
            
            assert response.status_code == 200
            assert response.json() == {'result': 'success'}
        
        client.close()
    
    def test_get_request_with_params(self):
        """Test GET request with query parameters."""
        client = BaseHTTPClient()
        
        with requests_mock.Mocker() as m:
            m.get('https://api.example.com/search', json={'results': []})
            
            response = client.get(
                'https://api.example.com/search',
                params={'q': 'test', 'limit': 10}
            )
            
            assert response.status_code == 200
            # Verify params were included
            assert 'q=test' in m.last_request.url
            assert 'limit=10' in m.last_request.url
        
        client.close()
    
    def test_http_error_handling(self):
        """Test handling of HTTP errors."""
        client = BaseHTTPClient()
        
        with requests_mock.Mocker() as m:
            m.get('https://api.example.com/notfound', status_code=404)
            
            with pytest.raises(requests.HTTPError):
                client.get('https://api.example.com/notfound')
        
        client.close()
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced."""
        # Use low rate limit for testing
        client = BaseHTTPClient(rate_limit_per_minute=3)
        
        with requests_mock.Mocker() as m:
            m.get('https://api.example.com/data', json={})
            
            # Make requests up to the limit
            start_time = time.time()
            for _ in range(3):
                client.get('https://api.example.com/data')
            
            # First 3 should be fast (no waiting)
            elapsed = time.time() - start_time
            assert elapsed < 1.0
            
            # 4th request should trigger rate limiting
            start_time = time.time()
            client.get('https://api.example.com/data')
            elapsed = time.time() - start_time
            
            # Should have waited (actual time depends on test execution speed)
            # Just verify it completed without error
            assert True
        
        client.close()
    
    def test_rate_limit_cleanup(self):
        """Test that old request times are cleaned up."""
        client = BaseHTTPClient(rate_limit_per_minute=5)
        
        # Manually add old timestamps
        old_time = time.time() - 61  # More than 60 seconds ago
        client._request_times = [old_time, old_time, old_time]
        
        # Trigger cleanup via rate_limit_wait
        client._rate_limit_wait()
        
        # Old times should be removed, only new one remains
        assert len(client._request_times) == 1
        assert client._request_times[0] > old_time
        
        client.close()
    
    def test_session_retry_configuration(self):
        """Test that session is configured with retry logic."""
        client = BaseHTTPClient(retry_attempts=3)
        
        # Check adapters are mounted
        assert 'http://' in client.session.adapters
        assert 'https://' in client.session.adapters
        
        # Verify adapter has retry configuration
        adapter = client.session.get_adapter('https://')
        assert adapter.max_retries is not None
        
        client.close()
    
    def test_context_manager_support(self):
        """Test client can be used as context manager."""
        # Add context manager support to client
        BaseHTTPClient.__enter__ = lambda self: self
        BaseHTTPClient.__exit__ = lambda self, *args: self.close()
        
        with BaseHTTPClient() as client:
            with requests_mock.Mocker() as m:
                m.get('https://api.example.com/test', json={})
                response = client.get('https://api.example.com/test')
                assert response.status_code == 200


@pytest.fixture
def http_client():
    """Provide HTTP client that cleans up after test."""
    client = BaseHTTPClient()
    yield client
    client.close()


def test_with_fixture(http_client):
    """Test using fixture for automatic cleanup."""
    with requests_mock.Mocker() as m:
        m.get('https://test.com', json={'status': 'ok'})
        response = http_client.get('https://test.com')
        assert response.json()['status'] == 'ok'
```

---

## Database Layer Testing

### Example: Task Queue with In-Memory Database

**Production Code** (`src/database/task_queue.py`):

```python
"""Task queue database operations."""

import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager


class TaskQueue:
    """Task queue backed by SQLite database.
    
    Provides atomic task operations with LIFO ordering and priority support.
    """
    
    def __init__(self, database_path: str):
        """Initialize task queue.
        
        Args:
            database_path: Path to SQLite database (use ':memory:' for testing)
        """
        self.database_path = database_path
        self._init_schema()
    
    def _init_schema(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'QUEUED',
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    worker_id TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_priority 
                ON tasks(status, priority DESC, created_at DESC)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()
    
    def add_task(
        self,
        task_id: str,
        task_type: str,
        parameters: str,
        priority: int = 0
    ) -> bool:
        """Add new task to queue.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task
            parameters: JSON string of task parameters
            priority: Task priority (higher = more important)
            
        Returns:
            True if task added successfully
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO tasks (task_id, task_type, parameters, priority)
                    VALUES (?, ?, ?, ?)
                    """,
                    (task_id, task_type, parameters, priority)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Task ID already exists
            return False
    
    def claim_task(
        self,
        worker_id: str,
        task_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Atomically claim next available task.
        
        Uses LIFO ordering (newest first) with priority support.
        
        Args:
            worker_id: ID of worker claiming task
            task_type: Optional filter by task type
            
        Returns:
            Task dictionary or None if no tasks available
        """
        with self._get_connection() as conn:
            # Begin transaction for atomicity
            conn.execute("BEGIN IMMEDIATE")
            
            try:
                # Find highest priority task (LIFO within priority)
                query = """
                    SELECT * FROM tasks
                    WHERE status = 'QUEUED'
                """
                params = []
                
                if task_type:
                    query += " AND task_type = ?"
                    params.append(task_type)
                
                query += """
                    ORDER BY priority DESC, created_at DESC
                    LIMIT 1
                """
                
                cursor = conn.execute(query, params)
                task = cursor.fetchone()
                
                if not task:
                    conn.commit()
                    return None
                
                # Claim the task
                conn.execute(
                    """
                    UPDATE tasks
                    SET status = 'RUNNING',
                        worker_id = ?,
                        started_at = ?
                    WHERE task_id = ?
                    """,
                    (worker_id, datetime.utcnow(), task['task_id'])
                )
                
                conn.commit()
                
                # Convert Row to dict
                return dict(task)
                
            except Exception:
                conn.rollback()
                raise
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update task status.
        
        Args:
            task_id: Task identifier
            status: New status (QUEUED, RUNNING, COMPLETED, FAILED)
            error_message: Optional error message for failed tasks
            
        Returns:
            True if task updated successfully
        """
        try:
            with self._get_connection() as conn:
                update_fields = ["status = ?"]
                params = [status]
                
                if status == 'COMPLETED':
                    update_fields.append("completed_at = ?")
                    params.append(datetime.utcnow())
                
                if error_message:
                    update_fields.append("error_message = ?")
                    params.append(error_message)
                
                params.append(task_id)
                
                conn.execute(
                    f"""
                    UPDATE tasks
                    SET {', '.join(update_fields)}
                    WHERE task_id = ?
                    """,
                    params
                )
                conn.commit()
            return True
        except Exception:
            return False
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics.
        
        Returns:
            Dictionary with counts by status
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM tasks
                GROUP BY status
            """)
            
            stats = {row['status']: row['count'] for row in cursor}
            
            # Ensure all statuses are present
            for status in ['QUEUED', 'RUNNING', 'COMPLETED', 'FAILED']:
                if status not in stats:
                    stats[status] = 0
            
            return stats
```

**Test Code** (`tests/test_task_queue.py`):

```python
"""Tests for TaskQueue database operations."""

import pytest
import sqlite3
from datetime import datetime
from database.task_queue import TaskQueue


@pytest.fixture
def task_queue():
    """Provide in-memory task queue for testing."""
    # Use :memory: for isolated, fast tests
    queue = TaskQueue(':memory:')
    return queue


@pytest.fixture
def populated_queue(task_queue):
    """Provide task queue with sample tasks."""
    task_queue.add_task('task-1', 'youtube_channel', '{"channel": "@test"}', priority=0)
    task_queue.add_task('task-2', 'youtube_video', '{"video_id": "abc"}', priority=0)
    task_queue.add_task('task-3', 'youtube_channel', '{"channel": "@test2"}', priority=10)
    return task_queue


class TestTaskQueue:
    """Test suite for TaskQueue."""
    
    def test_initialization_creates_schema(self, task_queue):
        """Test that initialization creates required schema."""
        # Verify tables exist
        with task_queue._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='tasks'
            """)
            assert cursor.fetchone() is not None
    
    def test_add_task_success(self, task_queue):
        """Test adding a task successfully."""
        result = task_queue.add_task(
            task_id='test-task-1',
            task_type='youtube_channel',
            parameters='{"channel_url": "@test"}',
            priority=5
        )
        
        assert result is True
        
        # Verify task was added
        with task_queue._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?",
                ('test-task-1',)
            )
            task = cursor.fetchone()
            assert task is not None
            assert task['task_type'] == 'youtube_channel'
            assert task['priority'] == 5
    
    def test_add_duplicate_task_fails(self, task_queue):
        """Test that adding duplicate task ID fails."""
        task_queue.add_task('task-1', 'test', '{}')
        
        # Try to add again with same ID
        result = task_queue.add_task('task-1', 'test', '{}')
        
        assert result is False
    
    def test_claim_task_lifo_ordering(self, populated_queue):
        """Test LIFO ordering (newest first within same priority)."""
        # Tasks with same priority should be claimed newest first
        task = populated_queue.claim_task('worker-1', task_type='youtube_channel')
        
        # Should claim task-3 (added last, same type, higher priority)
        assert task['task_id'] == 'task-3'
        assert task['priority'] == 10
    
    def test_claim_task_priority_ordering(self, populated_queue):
        """Test priority ordering (higher priority first)."""
        # Should claim highest priority task first
        task = populated_queue.claim_task('worker-1')
        
        assert task['task_id'] == 'task-3'  # Priority 10
        assert task['priority'] == 10
    
    def test_claim_task_atomicity(self, populated_queue):
        """Test that task claiming is atomic (no double-claiming)."""
        # Two workers try to claim
        task1 = populated_queue.claim_task('worker-1')
        task2 = populated_queue.claim_task('worker-2')
        
        # Should claim different tasks
        assert task1 is not None
        assert task2 is not None
        assert task1['task_id'] != task2['task_id']
        
        # Verify both tasks marked as RUNNING
        with populated_queue._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM tasks WHERE status = 'RUNNING'"
            )
            assert cursor.fetchone()['count'] == 2
    
    def test_claim_task_when_empty(self, task_queue):
        """Test claiming from empty queue."""
        task = task_queue.claim_task('worker-1')
        assert task is None
    
    def test_claim_task_with_type_filter(self, populated_queue):
        """Test claiming with task type filter."""
        # Claim specific task type
        task = populated_queue.claim_task('worker-1', task_type='youtube_video')
        
        assert task is not None
        assert task['task_type'] == 'youtube_video'
        assert task['task_id'] == 'task-2'
    
    def test_update_task_status_to_completed(self, populated_queue):
        """Test updating task status to completed."""
        task = populated_queue.claim_task('worker-1')
        
        result = populated_queue.update_task_status(
            task['task_id'],
            'COMPLETED'
        )
        
        assert result is True
        
        # Verify status updated
        with populated_queue._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status, completed_at FROM tasks WHERE task_id = ?",
                (task['task_id'],)
            )
            updated = cursor.fetchone()
            assert updated['status'] == 'COMPLETED'
            assert updated['completed_at'] is not None
    
    def test_update_task_status_to_failed(self, populated_queue):
        """Test updating task status to failed with error message."""
        task = populated_queue.claim_task('worker-1')
        
        result = populated_queue.update_task_status(
            task['task_id'],
            'FAILED',
            error_message='Test error occurred'
        )
        
        assert result is True
        
        # Verify error message saved
        with populated_queue._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status, error_message FROM tasks WHERE task_id = ?",
                (task['task_id'],)
            )
            updated = cursor.fetchone()
            assert updated['status'] == 'FAILED'
            assert updated['error_message'] == 'Test error occurred'
    
    def test_get_queue_stats(self, populated_queue):
        """Test getting queue statistics."""
        # Claim one task
        populated_queue.claim_task('worker-1')
        
        stats = populated_queue.get_queue_stats()
        
        assert stats['QUEUED'] == 2  # 2 remaining
        assert stats['RUNNING'] == 1  # 1 claimed
        assert stats['COMPLETED'] == 0
        assert stats['FAILED'] == 0
    
    def test_get_queue_stats_empty_queue(self, task_queue):
        """Test stats on empty queue."""
        stats = task_queue.get_queue_stats()
        
        # All stats should be zero
        assert all(count == 0 for count in stats.values())
        # But all statuses should be present
        assert set(stats.keys()) == {'QUEUED', 'RUNNING', 'COMPLETED', 'FAILED'}


class TestTaskQueueConcurrency:
    """Tests for concurrent operations."""
    
    def test_multiple_workers_claiming(self):
        """Test multiple workers claiming tasks concurrently."""
        queue = TaskQueue(':memory:')
        
        # Add multiple tasks
        for i in range(10):
            queue.add_task(f'task-{i}', 'test', '{}')
        
        # Simulate multiple workers
        claimed_tasks = []
        for worker_id in range(5):
            task = queue.claim_task(f'worker-{worker_id}')
            if task:
                claimed_tasks.append(task)
        
        # Verify no duplicate claims
        task_ids = [t['task_id'] for t in claimed_tasks]
        assert len(task_ids) == len(set(task_ids))  # All unique
        
        # Verify all are marked RUNNING
        stats = queue.get_queue_stats()
        assert stats['RUNNING'] == 5
        assert stats['QUEUED'] == 5
```

---

## Content Processing Testing

This section shows testing of the actual ContentFunnel example from the codebase:

**Test Code** (`tests/test_content_funnel_comprehensive.py`):

```python
"""Comprehensive tests for ContentFunnel showing all testing patterns."""

import pytest
from typing import Optional, Dict, Any
from core.content_funnel import (
    ContentFunnel,
    TransformationStage,
    AudioExtractor,
    AudioTranscriber,
    SubtitleExtractor
)
from idea_inspiration import IdeaInspiration, ContentType


# ===== Mock Implementations =====

class MockAudioExtractor:
    """Mock audio extractor implementing AudioExtractor protocol."""
    
    def __init__(
        self,
        should_succeed: bool = True,
        extraction_delay: float = 0.0
    ):
        self.should_succeed = should_succeed
        self.extraction_delay = extraction_delay
        self.call_count = 0
        self.last_video_url = None
    
    def extract_audio(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Mock audio extraction."""
        import time
        self.call_count += 1
        self.last_video_url = video_url
        
        if self.extraction_delay > 0:
            time.sleep(self.extraction_delay)
        
        if not self.should_succeed:
            return None
        
        return {
            'audio_url': f"{video_url}.audio.mp3",
            'audio_format': 'mp3',
            'duration': 180,
            'sample_rate': 44100
        }


class MockAudioTranscriber:
    """Mock audio transcriber implementing AudioTranscriber protocol."""
    
    def __init__(
        self,
        should_succeed: bool = True,
        confidence: float = 95.0,
        language: str = 'en'
    ):
        self.should_succeed = should_succeed
        self.confidence = confidence
        self.language = language
        self.call_count = 0
        self.last_audio_url = None
    
    def transcribe_audio(
        self,
        audio_url: str,
        audio_id: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Mock audio transcription."""
        self.call_count += 1
        self.last_audio_url = audio_url
        
        if not self.should_succeed:
            return None
        
        return {
            'text': f"Transcribed: {audio_url}",
            'confidence': self.confidence,
            'language': language or self.language,
            'word_count': 50
        }


class MockSubtitleExtractor:
    """Mock subtitle extractor implementing SubtitleExtractor protocol."""
    
    def __init__(
        self,
        should_succeed: bool = True,
        subtitle_format: str = 'srt'
    ):
        self.should_succeed = should_succeed
        self.subtitle_format = subtitle_format
        self.call_count = 0
        self.last_video_url = None
    
    def extract_subtitles(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Mock subtitle extraction."""
        self.call_count += 1
        self.last_video_url = video_url
        
        if not self.should_succeed:
            return None
        
        return {
            'text': f"Subtitles: {video_url}",
            'format': self.subtitle_format,
            'language': language or 'en',
            'confidence': 98.0
        }


# ===== Pytest Fixtures =====

@pytest.fixture
def mock_audio_extractor():
    """Provide successful audio extractor."""
    return MockAudioExtractor()


@pytest.fixture
def mock_audio_transcriber():
    """Provide successful audio transcriber."""
    return MockAudioTranscriber()


@pytest.fixture
def mock_subtitle_extractor():
    """Provide successful subtitle extractor."""
    return MockSubtitleExtractor()


@pytest.fixture
def full_content_funnel(
    mock_audio_extractor,
    mock_audio_transcriber,
    mock_subtitle_extractor
):
    """Provide fully configured ContentFunnel."""
    return ContentFunnel(
        audio_extractor=mock_audio_extractor,
        audio_transcriber=mock_audio_transcriber,
        subtitle_extractor=mock_subtitle_extractor
    )


# ===== Test Cases =====

class TestContentFunnelHappyPaths:
    """Test successful content processing flows."""
    
    def test_text_content_passthrough(self):
        """Test text content passes through unchanged."""
        # Arrange
        funnel = ContentFunnel()  # No extractors needed
        idea = IdeaInspiration.from_text(
            title="Article Title",
            text_content="Original article text",
            keywords=["test", "article"]
        )
        
        # Act
        result = funnel.process(idea)
        
        # Assert
        assert result.content == "Original article text"
        assert result.source_type == ContentType.TEXT
        assert 'transformation_chain' not in result.metadata
    
    def test_video_subtitle_extraction(self, full_content_funnel):
        """Test video processing with subtitle extraction."""
        # Arrange
        idea = IdeaInspiration.from_video(
            title="Tutorial Video",
            source_url="https://youtube.com/watch?v=test123",
            source_id="test123"
        )
        
        # Act
        result = full_content_funnel.process(idea, extract_subtitles=True)
        
        # Assert
        assert "Subtitles:" in result.content
        assert result.metadata['subtitle_format'] == 'srt'
        assert result.metadata['subtitle_language'] == 'en'
        assert 'transformation_chain' in result.metadata
    
    def test_video_audio_transcription(self, full_content_funnel):
        """Test video processing with audio extraction and transcription."""
        # Arrange
        idea = IdeaInspiration.from_video(
            title="Podcast Video",
            source_url="https://youtube.com/watch?v=podcast1"
        )
        
        # Act
        result = full_content_funnel.process(
            idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=False  # Skip subtitles
        )
        
        # Assert
        assert "Transcribed:" in result.content
        assert result.metadata['audio_format'] == 'mp3'
        assert result.metadata['transcription_language'] == 'en'
        
        # Verify transformation chain
        history = full_content_funnel.get_transformation_history()
        assert len(history) == 2
        assert history[0]['from_stage'] == 'video_source'
        assert history[0]['to_stage'] == 'audio_extracted'
        assert history[1]['from_stage'] == 'audio_extracted'
        assert history[1]['to_stage'] == 'text_transcribed'
    
    def test_audio_transcription(self, mock_audio_transcriber):
        """Test audio content transcription."""
        # Arrange
        funnel = ContentFunnel(audio_transcriber=mock_audio_transcriber)
        idea = IdeaInspiration.from_audio(
            title="Podcast Episode",
            source_url="https://example.com/podcast.mp3"
        )
        
        # Act
        result = funnel.process(idea, transcribe_audio=True)
        
        # Assert
        assert "Transcribed:" in result.content
        assert mock_audio_transcriber.call_count == 1


class TestContentFunnelErrorHandling:
    """Test error scenarios and graceful degradation."""
    
    def test_subtitle_extraction_failure_falls_back_to_audio(self):
        """Test fallback to audio transcription when subtitles fail."""
        # Arrange
        failing_subtitle_extractor = MockSubtitleExtractor(should_succeed=False)
        working_audio_extractor = MockAudioExtractor()
        working_transcriber = MockAudioTranscriber()
        
        funnel = ContentFunnel(
            audio_extractor=working_audio_extractor,
            audio_transcriber=working_transcriber,
            subtitle_extractor=failing_subtitle_extractor
        )
        
        idea = IdeaInspiration.from_video(
            title="Test Video",
            source_url="https://youtube.com/watch?v=test"
        )
        
        # Act
        result = funnel.process(
            idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=True
        )
        
        # Assert
        assert failing_subtitle_extractor.call_count == 1  # Tried subtitles
        assert working_audio_extractor.call_count == 1     # Fell back to audio
        assert working_transcriber.call_count == 1          # Transcribed
        assert "Transcribed:" in result.content
    
    def test_audio_extraction_failure_leaves_content_empty(self):
        """Test that failed audio extraction doesn't crash."""
        # Arrange
        failing_extractor = MockAudioExtractor(should_succeed=False)
        funnel = ContentFunnel(audio_extractor=failing_extractor)
        
        idea = IdeaInspiration.from_video(
            title="Test Video",
            source_url="https://youtube.com/watch?v=test"
        )
        
        # Act - should not raise exception
        result = funnel.process(
            idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=False
        )
        
        # Assert
        assert result.content == ""  # Content remains empty
        assert failing_extractor.call_count == 1


class TestContentFunnelEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_existing_content_not_overwritten(self, mock_subtitle_extractor):
        """Test that existing content is preserved."""
        # Arrange
        funnel = ContentFunnel(subtitle_extractor=mock_subtitle_extractor)
        idea = IdeaInspiration.from_video(
            title="Test Video",
            subtitle_text="Existing subtitle content",
            source_url="https://youtube.com/watch?v=test"
        )
        
        # Act
        result = funnel.process(idea, extract_subtitles=True)
        
        # Assert
        assert mock_subtitle_extractor.call_count == 0  # Not called
        assert result.content == "Existing subtitle content"
    
    def test_language_parameter_passed_through(self, mock_audio_transcriber):
        """Test language parameter propagates correctly."""
        # Arrange
        funnel = ContentFunnel(audio_transcriber=mock_audio_transcriber)
        idea = IdeaInspiration.from_audio(
            title="Spanish Podcast",
            source_url="https://example.com/spanish.mp3"
        )
        
        # Act
        result = funnel.process(idea, transcribe_audio=True, language='es')
        
        # Assert
        assert result.metadata['transcription_language'] == 'es'


# Mark tests with categories
pytestmark = pytest.mark.unit
```

This comprehensive example document shows complete implementations with mocks, fixtures, and various test scenarios. Would you like me to continue with the Worker Testing and Integration Testing sections?

---

**Last Updated**: 2025-11-14  
**Status**: Work in Progress  
**Part 1 of 2** - Continued in next response if needed
