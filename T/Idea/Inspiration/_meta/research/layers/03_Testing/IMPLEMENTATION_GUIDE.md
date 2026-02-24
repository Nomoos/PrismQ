# Implementation Guide - Refactoring for Testability

## Overview

This guide provides step-by-step instructions for refactoring existing code to follow the testing and mocking patterns documented in this research. Use this when working with legacy code or untested modules.

## Table of Contents

1. [Identifying Testability Issues](#identifying-testability-issues)
2. [Refactoring Strategy](#refactoring-strategy)
3. [Step-by-Step Refactoring](#step-by-step-refactoring)
4. [Common Patterns](#common-patterns)
5. [Migration Examples](#migration-examples)
6. [Common Pitfalls](#common-pitfalls)

---

## Identifying Testability Issues

### Signs Your Code Needs Refactoring

#### ❌ Hard to Test

```python
class VideoProcessor:
    def process_video(self, video_url: str):
        # Hardcoded dependency - can't mock
        fetcher = YouTubeAPIFetcher()
        data = fetcher.fetch(video_url)
        
        # Direct database access - can't test without DB
        db = sqlite3.connect('production.db')
        db.execute("INSERT INTO videos ...")
        
        # Global state - makes tests interdependent
        global_cache[video_url] = data
        
        return data
```

**Problems**:
- Can't run without YouTube API access
- Requires production database
- Tests affect each other via global state
- Hard to test error scenarios

#### ✅ Easy to Test

```python
class VideoProcessor:
    def __init__(
        self,
        fetcher: IVideoFetcher,
        database: IDatabase
    ):
        self.fetcher = fetcher
        self.database = database
    
    def process_video(self, video_url: str):
        # Use injected dependencies
        data = self.fetcher.fetch(video_url)
        self.database.save_video(data)
        return data
```

**Benefits**:
- Dependencies can be mocked
- No external service calls needed
- Each test is independent
- Easy to test error scenarios

### Checklist for Testability

Use this checklist to evaluate code:

- [ ] Dependencies injected via constructor?
- [ ] Uses interfaces/protocols for dependencies?
- [ ] No hardcoded instantiation of dependencies?
- [ ] No direct file system access?
- [ ] No direct database access?
- [ ] No global state or singletons?
- [ ] No direct HTTP calls?
- [ ] Pure functions where possible?
- [ ] Side effects isolated and injectable?

---

## Refactoring Strategy

### The Three-Phase Approach

#### Phase 1: Extract Interfaces
Define protocols for all dependencies

#### Phase 2: Inject Dependencies
Modify constructors to accept dependencies

#### Phase 3: Add Tests
Write comprehensive test coverage

### When to Refactor

**Refactor Now**:
- Working on new features in the area
- Fixing bugs (add tests to prevent regression)
- Code is causing production issues
- Planning major changes to the module

**Refactor Later**:
- Code is stable and working
- Low risk area
- Low change frequency
- Other priorities

---

## Step-by-Step Refactoring

### Example: YouTube Channel Scraper

#### Original Code (Hard to Test)

```python
# src/scrapers/youtube_scraper.py
import requests
import sqlite3
from yt_dlp import YoutubeDL

class YouTubeChannelScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def scrape_channel(self, channel_url: str):
        # Hardcoded HTTP calls
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/channels',
            params={'key': self.api_key, 'forUsername': channel_url}
        )
        channel_data = response.json()
        
        # Hardcoded yt-dlp usage
        ydl = YoutubeDL({'quiet': True})
        videos = ydl.extract_info(channel_url, download=False)
        
        # Hardcoded database access
        conn = sqlite3.connect('data/videos.db')
        for video in videos['entries']:
            conn.execute(
                "INSERT INTO videos (title, url) VALUES (?, ?)",
                (video['title'], video['url'])
            )
        conn.commit()
        conn.close()
        
        return len(videos['entries'])
```

**Problems**:
- Can't test without YouTube API
- Can't test without real database
- Can't test error scenarios easily
- Hard to verify behavior

---

#### Step 1: Extract Interfaces

Create protocols for each dependency:

```python
# src/protocols/scraper_protocols.py
from typing import Protocol, Dict, Any, List, Optional

class IHTTPClient(Protocol):
    """Protocol for making HTTP requests."""
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request and return JSON response."""
        ...

class IVideoExtractor(Protocol):
    """Protocol for extracting video information."""
    
    def extract_channel_videos(
        self,
        channel_url: str
    ) -> List[Dict[str, Any]]:
        """Extract all videos from a channel."""
        ...

class IVideoDatabase(Protocol):
    """Protocol for video database operations."""
    
    def save_video(
        self,
        title: str,
        url: str
    ) -> bool:
        """Save video to database."""
        ...
```

---

#### Step 2: Create Concrete Implementations

Move existing logic into protocol implementations:

```python
# src/clients/youtube_http_client.py
from typing import Dict, Any, Optional
import requests

class YouTubeHTTPClient:
    """YouTube API HTTP client."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request to YouTube API."""
        params = params or {}
        params['key'] = self.api_key
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()


# src/extractors/ytdlp_extractor.py
from typing import List, Dict, Any
from yt_dlp import YoutubeDL

class YtDlpVideoExtractor:
    """Video extractor using yt-dlp."""
    
    def __init__(self, ydl_options: Optional[Dict[str, Any]] = None):
        self.ydl_options = ydl_options or {'quiet': True}
    
    def extract_channel_videos(
        self,
        channel_url: str
    ) -> List[Dict[str, Any]]:
        """Extract videos from channel using yt-dlp."""
        ydl = YoutubeDL(self.ydl_options)
        info = ydl.extract_info(channel_url, download=False)
        
        return [
            {
                'title': video['title'],
                'url': video['url'],
                'duration': video.get('duration'),
                'view_count': video.get('view_count')
            }
            for video in info.get('entries', [])
        ]


# src/database/video_database.py
import sqlite3
from typing import Optional

class SQLiteVideoDatabase:
    """SQLite-based video database."""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.database_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def save_video(self, title: str, url: str) -> bool:
        """Save video to database."""
        try:
            conn = sqlite3.connect(self.database_path)
            conn.execute(
                "INSERT INTO videos (title, url) VALUES (?, ?)",
                (title, url)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Video already exists
            return False
```

---

#### Step 3: Refactor to Use Dependency Injection

Update the main class to accept dependencies:

```python
# src/scrapers/youtube_scraper.py
from typing import List, Dict, Any
from protocols.scraper_protocols import (
    IHTTPClient,
    IVideoExtractor,
    IVideoDatabase
)

class YouTubeChannelScraper:
    """YouTube channel scraper with dependency injection.
    
    All dependencies are injected for testability.
    """
    
    def __init__(
        self,
        http_client: IHTTPClient,
        video_extractor: IVideoExtractor,
        database: IVideoDatabase
    ):
        """Initialize scraper with dependencies.
        
        Args:
            http_client: HTTP client for API calls
            video_extractor: Video information extractor
            database: Video database for persistence
        """
        self.http_client = http_client
        self.video_extractor = video_extractor
        self.database = database
    
    def scrape_channel(self, channel_url: str) -> int:
        """Scrape videos from YouTube channel.
        
        Args:
            channel_url: YouTube channel URL
            
        Returns:
            Number of videos scraped
        """
        # Get channel info via injected HTTP client
        channel_data = self.http_client.get(
            'https://www.googleapis.com/youtube/v3/channels',
            params={'forUsername': channel_url}
        )
        
        # Extract videos via injected extractor
        videos = self.video_extractor.extract_channel_videos(channel_url)
        
        # Save videos via injected database
        saved_count = 0
        for video in videos:
            if self.database.save_video(video['title'], video['url']):
                saved_count += 1
        
        return saved_count
```

---

#### Step 4: Create Production Factory

Create a factory for production use:

```python
# src/factories/scraper_factory.py
from scrapers.youtube_scraper import YouTubeChannelScraper
from clients.youtube_http_client import YouTubeHTTPClient
from extractors.ytdlp_extractor import YtDlpVideoExtractor
from database.video_database import SQLiteVideoDatabase

def create_youtube_scraper(
    api_key: str,
    database_path: str = 'data/videos.db'
) -> YouTubeChannelScraper:
    """Create production YouTube scraper with real dependencies.
    
    Args:
        api_key: YouTube API key
        database_path: Path to SQLite database
        
    Returns:
        Configured YouTubeChannelScraper
    """
    http_client = YouTubeHTTPClient(api_key)
    video_extractor = YtDlpVideoExtractor()
    database = SQLiteVideoDatabase(database_path)
    
    return YouTubeChannelScraper(
        http_client=http_client,
        video_extractor=video_extractor,
        database=database
    )

# Usage in production:
# scraper = create_youtube_scraper(api_key='my-key')
# videos_scraped = scraper.scrape_channel('@channel')
```

---

#### Step 5: Create Mock Implementations

Create mocks for testing:

```python
# tests/mocks/mock_clients.py
from typing import Dict, Any, Optional, List

class MockHTTPClient:
    """Mock HTTP client for testing."""
    
    def __init__(self, mock_response: Optional[Dict[str, Any]] = None):
        self.mock_response = mock_response or {}
        self.call_count = 0
        self.last_url = None
        self.last_params = None
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mock GET request."""
        self.call_count += 1
        self.last_url = url
        self.last_params = params
        return self.mock_response


class MockVideoExtractor:
    """Mock video extractor for testing."""
    
    def __init__(self, mock_videos: Optional[List[Dict[str, Any]]] = None):
        self.mock_videos = mock_videos or []
        self.call_count = 0
        self.last_channel_url = None
    
    def extract_channel_videos(
        self,
        channel_url: str
    ) -> List[Dict[str, Any]]:
        """Mock video extraction."""
        self.call_count += 1
        self.last_channel_url = channel_url
        return self.mock_videos


class MockVideoDatabase:
    """Mock video database for testing."""
    
    def __init__(self):
        self.videos = []
        self.save_count = 0
    
    def save_video(self, title: str, url: str) -> bool:
        """Mock video save."""
        self.save_count += 1
        self.videos.append({'title': title, 'url': url})
        return True
```

---

#### Step 6: Write Tests

Now testing is easy with mocks:

```python
# tests/test_youtube_scraper.py
import pytest
from scrapers.youtube_scraper import YouTubeChannelScraper
from tests.mocks.mock_clients import (
    MockHTTPClient,
    MockVideoExtractor,
    MockVideoDatabase
)

class TestYouTubeChannelScraper:
    """Test suite for YouTubeChannelScraper."""
    
    def test_scrape_channel_success(self):
        """Test successful channel scraping."""
        # Arrange
        mock_http = MockHTTPClient({
            'items': [{'id': 'channel123', 'snippet': {'title': 'Test Channel'}}]
        })
        mock_extractor = MockVideoExtractor([
            {'title': 'Video 1', 'url': 'https://youtube.com/watch?v=1'},
            {'title': 'Video 2', 'url': 'https://youtube.com/watch?v=2'}
        ])
        mock_db = MockVideoDatabase()
        
        scraper = YouTubeChannelScraper(
            http_client=mock_http,
            video_extractor=mock_extractor,
            database=mock_db
        )
        
        # Act
        count = scraper.scrape_channel('@testchannel')
        
        # Assert
        assert count == 2
        assert mock_http.call_count == 1
        assert mock_extractor.call_count == 1
        assert mock_db.save_count == 2
        assert len(mock_db.videos) == 2
        assert mock_db.videos[0]['title'] == 'Video 1'
    
    def test_scrape_channel_no_videos(self):
        """Test scraping channel with no videos."""
        # Arrange
        mock_http = MockHTTPClient({'items': []})
        mock_extractor = MockVideoExtractor([])  # No videos
        mock_db = MockVideoDatabase()
        
        scraper = YouTubeChannelScraper(
            http_client=mock_http,
            video_extractor=mock_extractor,
            database=mock_db
        )
        
        # Act
        count = scraper.scrape_channel('@emptychannel')
        
        # Assert
        assert count == 0
        assert mock_db.save_count == 0
    
    def test_http_client_receives_correct_params(self):
        """Test that HTTP client is called with correct parameters."""
        # Arrange
        mock_http = MockHTTPClient({'items': []})
        mock_extractor = MockVideoExtractor([])
        mock_db = MockVideoDatabase()
        
        scraper = YouTubeChannelScraper(
            http_client=mock_http,
            video_extractor=mock_extractor,
            database=mock_db
        )
        
        # Act
        scraper.scrape_channel('@testchannel')
        
        # Assert
        assert 'youtube.com' in mock_http.last_url
        assert mock_http.last_params['forUsername'] == '@testchannel'


@pytest.fixture
def scraper_with_mocks():
    """Provide scraper with mock dependencies."""
    return YouTubeChannelScraper(
        http_client=MockHTTPClient(),
        video_extractor=MockVideoExtractor(),
        database=MockVideoDatabase()
    )


def test_with_fixture(scraper_with_mocks):
    """Test using pytest fixture."""
    count = scraper_with_mocks.scrape_channel('@test')
    assert count == 0  # No mock videos configured
```

---

## Common Patterns

### Pattern 1: Refactoring Hardcoded File Access

**Before**:
```python
class ConfigLoader:
    def load(self):
        with open('config.json') as f:
            return json.load(f)
```

**After**:
```python
# Protocol
class IFileReader(Protocol):
    def read(self, path: str) -> str: ...

# Implementation
class FileSystemReader:
    def read(self, path: str) -> str:
        with open(path) as f:
            return f.read()

# Refactored class
class ConfigLoader:
    def __init__(self, file_reader: IFileReader):
        self.file_reader = file_reader
    
    def load(self, path: str):
        content = self.file_reader.read(path)
        return json.loads(content)

# Mock for testing
class MockFileReader:
    def __init__(self, mock_content: str):
        self.mock_content = mock_content
    
    def read(self, path: str) -> str:
        return self.mock_content
```

### Pattern 2: Refactoring Global State

**Before**:
```python
# Global cache
_cache = {}

class DataProcessor:
    def process(self, key: str):
        if key in _cache:
            return _cache[key]
        data = expensive_operation(key)
        _cache[key] = data
        return data
```

**After**:
```python
# Protocol
class ICache(Protocol):
    def get(self, key: str) -> Optional[Any]: ...
    def set(self, key: str, value: Any) -> None: ...

# Implementation
class MemoryCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

# Refactored class
class DataProcessor:
    def __init__(self, cache: ICache):
        self.cache = cache
    
    def process(self, key: str):
        cached = self.cache.get(key)
        if cached:
            return cached
        
        data = expensive_operation(key)
        self.cache.set(key, data)
        return data

# Mock for testing
class MockCache:
    def __init__(self):
        self.data = {}
        self.get_count = 0
        self.set_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        self.get_count += 1
        return self.data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self.set_count += 1
        self.data[key] = value
```

### Pattern 3: Refactoring Time Dependencies

**Before**:
```python
from datetime import datetime

class EventLogger:
    def log_event(self, event: str):
        timestamp = datetime.now()  # Hard to test!
        self.save(f"{timestamp}: {event}")
```

**After**:
```python
# Protocol
class IClock(Protocol):
    def now(self) -> datetime: ...

# Implementation
class SystemClock:
    def now(self) -> datetime:
        return datetime.now()

# Refactored class
class EventLogger:
    def __init__(self, clock: IClock):
        self.clock = clock
    
    def log_event(self, event: str):
        timestamp = self.clock.now()
        self.save(f"{timestamp}: {event}")

# Mock for testing
class MockClock:
    def __init__(self, fixed_time: datetime):
        self.fixed_time = fixed_time
    
    def now(self) -> datetime:
        return self.fixed_time

# Test
def test_event_logger():
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    mock_clock = MockClock(fixed_time)
    logger = EventLogger(mock_clock)
    
    # Can now verify exact timestamp!
    logger.log_event("test")
    assert logger.last_entry.startswith("2025-01-01 12:00:00")
```

---

## Common Pitfalls

### Pitfall 1: Testing Implementation Instead of Behavior

**❌ Bad**:
```python
def test_uses_requests_library():
    """This tests implementation, not behavior."""
    with patch('requests.get') as mock_get:
        client.fetch_data('url')
        mock_get.assert_called()  # Testing internal implementation
```

**✅ Good**:
```python
def test_fetches_data_successfully():
    """This tests behavior."""
    mock_fetcher = MockFetcher({'data': 'value'})
    client = DataClient(fetcher=mock_fetcher)
    
    result = client.fetch_data('url')
    
    assert result['data'] == 'value'  # Testing outcome
```

### Pitfall 2: Over-Mocking

**❌ Bad**:
```python
def test_calculate_total():
    """Mocking pure functions is unnecessary."""
    with patch('math.sqrt') as mock_sqrt:
        mock_sqrt.return_value = 5
        result = calculate_distance(3, 4)
        assert result == 5
```

**✅ Good**:
```python
def test_calculate_total():
    """Pure functions don't need mocks."""
    result = calculate_distance(3, 4)
    assert result == 5.0  # Direct test
```

### Pitfall 3: Forgetting to Reset Mocks

**❌ Bad**:
```python
mock_db = MockDatabase()

def test_first():
    processor.save(data1)
    assert mock_db.save_count == 1

def test_second():
    processor.save(data2)
    assert mock_db.save_count == 1  # Fails! Count is 2
```

**✅ Good**:
```python
@pytest.fixture
def mock_db():
    """Create fresh mock for each test."""
    return MockDatabase()

def test_first(mock_db):
    processor = Processor(mock_db)
    processor.save(data1)
    assert mock_db.save_count == 1

def test_second(mock_db):
    processor = Processor(mock_db)
    processor.save(data2)
    assert mock_db.save_count == 1  # Correct!
```

### Pitfall 4: Not Testing Error Paths

**❌ Bad**:
```python
def test_fetch_data():
    """Only tests happy path."""
    mock = MockFetcher({'data': 'value'})
    result = client.fetch_data('url')
    assert result is not None
```

**✅ Good**:
```python
def test_fetch_data_success():
    """Test happy path."""
    mock = MockFetcher({'data': 'value'})
    result = client.fetch_data('url')
    assert result['data'] == 'value'

def test_fetch_data_failure():
    """Test error path."""
    mock = MockFetcher(should_fail=True)
    result = client.fetch_data('url')
    assert result is None

def test_fetch_data_timeout():
    """Test timeout scenario."""
    mock = SlowMockFetcher(delay=100)
    with pytest.raises(TimeoutError):
        client.fetch_data('url', timeout=1)
```

---

## Migration Checklist

When refactoring code for testability:

- [ ] Identify all dependencies (APIs, databases, file system, time, etc.)
- [ ] Create Protocol definitions for each dependency
- [ ] Create concrete implementations for production use
- [ ] Create mock implementations for testing
- [ ] Refactor class to accept dependencies via constructor
- [ ] Update all existing instantiation sites to use factory or DI
- [ ] Write tests using mock dependencies
- [ ] Verify tests cover happy paths
- [ ] Verify tests cover error paths
- [ ] Verify tests cover edge cases
- [ ] Run full test suite
- [ ] Update documentation

---

## Summary

Refactoring for testability:

1. **Extract Interfaces** - Define Protocols for dependencies
2. **Inject Dependencies** - Accept dependencies via constructor
3. **Create Mocks** - Implement mock classes for testing
4. **Write Tests** - Add comprehensive test coverage
5. **Use Factories** - Create production instances via factories

Benefits:
- Fast, reliable tests
- Better code design
- Easier to understand and modify
- Confidence to refactor

---

**Last Updated**: 2025-11-14  
**Status**: Active Guide
