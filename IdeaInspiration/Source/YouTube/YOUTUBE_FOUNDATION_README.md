# YouTube Foundation - Quick Start Guide

## Overview

The YouTube Foundation provides shared infrastructure for all YouTube sub-modules (Channel, Search, Video). It includes API client, rate limiting, quota management, data mapping, and standardized schemas.

## Installation

```bash
cd Source/Video/YouTube
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Usage

```python
from src.config import YouTubeConfig
from src.client import YouTubeAPIClient

# Create configuration
config = YouTubeConfig(api_key="YOUR_YOUTUBE_API_KEY")

# Create API client
client = YouTubeAPIClient(
    api_key=config.api_key,
    rate_limit=100,  # requests per minute
    quota_per_day=10000  # daily quota limit
)

# Search for videos
results = client.search(query="python tutorial", max_results=10)
print(f"Found {len(results['items'])} videos")

# Get video details
video_ids = [item['id']['videoId'] for item in results['items']]
details = client.get_video_details(video_ids)
```

### 2. Using YouTubeBaseSource

```python
from src.base import YouTubeBaseSource
from typing import List, Dict, Any, Optional

class MyYouTubeSource(YouTubeBaseSource):
    """Custom YouTube source implementation."""
    
    def fetch_videos(
        self,
        query: Optional[str] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch videos with custom logic."""
        # Use inherited API client
        results = self.api_client.search(query=query, max_results=limit)
        
        # Parse and map results
        videos = []
        for item in results.get('items', []):
            video = self.mapper.parse_search_result(item)
            metadata = self.mapper.to_video_metadata_dict(video)
            videos.append(metadata)
        
        return videos

# Use the custom source
config = {'api_key': 'YOUR_API_KEY', 'rate_limit': 100}
source = MyYouTubeSource(config=config)
videos = source.fetch_videos(query="machine learning", limit=5)
```

### 3. Configuration from Environment

```python
import os
from src.config import YouTubeConfig

# Set environment variables
os.environ['YOUTUBE_API_KEY'] = 'your_key_here'
os.environ['YOUTUBE_RATE_LIMIT'] = '50'
os.environ['YOUTUBE_QUOTA_PER_DAY'] = '5000'

# Load from environment
config = YouTubeConfig.from_env()
print(config)  # YouTubeConfig(api_key=***, rate_limit=50, quota_per_day=5000)
```

### 4. Rate Limiting and Quota Management

```python
from src.client import RateLimiter

# Create rate limiter
limiter = RateLimiter(
    requests_per_minute=100,
    quota_per_day=10000
)

# Check quota before making request
if limiter.can_make_request(cost=100):  # search costs 100 units
    limiter.wait_if_needed()  # Wait if rate limit would be exceeded
    # Make your API request
    limiter.track_request(cost=100)  # Track quota usage

# Get statistics
stats = limiter.get_stats()
print(f"Quota used: {stats['quota_used']}/{stats['quota_limit']}")
print(f"Remaining: {stats['quota_remaining']}")
```

### 5. Data Mapping

```python
from src.mappers import YouTubeMapper

mapper = YouTubeMapper()

# Parse YouTube API response
api_response = {
    'id': 'abc123',
    'snippet': {'title': 'Test Video', 'channelId': 'UC123', ...},
    'contentDetails': {'duration': 'PT5M30S'},
    'statistics': {'viewCount': '1000', ...}
}

# Parse to YouTubeVideo model
youtube_video = mapper.parse_video(api_response)
print(f"Duration: {youtube_video.duration} seconds")
print(f"Is Short: {youtube_video.is_short}")

# Convert to standardized VideoMetadata format
metadata = mapper.to_video_metadata_dict(youtube_video)
print(metadata['url'])  # https://www.youtube.com/watch?v=abc123
```

### 6. Error Handling

```python
from src.exceptions import (
    YouTubeError,
    YouTubeAPIError,
    YouTubeQuotaExceededError,
    YouTubeRateLimitError
)

try:
    results = client.search(query="test")
except YouTubeQuotaExceededError as e:
    print(f"Quota exceeded: {e.current_usage}/{e.daily_limit}")
    # Wait until quota resets or use alternative source
except YouTubeAPIError as e:
    print(f"API error: {e} (status: {e.status_code})")
    # Handle API errors (retry, fallback, etc.)
except YouTubeError as e:
    print(f"YouTube error: {e}")
```

## Components

### Core Classes

- **YouTubeConfig**: Configuration management with validation
- **YouTubeAPIClient**: YouTube Data API v3 client with rate limiting
- **RateLimiter**: Token bucket rate limiting and quota tracking
- **YouTubeMapper**: Data transformation and parsing
- **YouTubeBaseSource**: Base class for YouTube sources
- **YouTube Schemas**: YouTubeVideo, YouTubeChannel, YouTubeSearchResult

### Exception Classes

- **YouTubeError**: Base exception
- **YouTubeAPIError**: API request failures
- **YouTubeQuotaExceededError**: Quota exceeded
- **YouTubeRateLimitError**: Rate limit exceeded
- **YouTubeInvalidVideoError**: Invalid video data
- **YouTubeConfigError**: Configuration errors

## API Quota Costs

| Operation | Quota Cost |
|-----------|-----------|
| search | 100 units |
| videos.list | 1 unit |
| channels.list | 1 unit |
| playlistItems.list | 1 unit |

**Free tier**: 10,000 units/day

## Best Practices

1. **Always use rate limiting** to avoid hitting API limits
2. **Check quota before expensive operations** (searches)
3. **Batch video details requests** (up to 50 videos per request)
4. **Cache results** when appropriate
5. **Handle quota exceeded errors** gracefully
6. **Use environment variables** for API keys (never commit keys!)

## Testing

```bash
# Run all tests
python -m pytest _meta/tests/unit/ -v

# Run specific test file
python -m pytest _meta/tests/unit/test_youtube_exceptions.py -v

# Run with coverage
python -m pytest _meta/tests/ --cov=src --cov-report=html
```

## Architecture

```
YouTubeBaseSource (extends BaseVideoSource)
├── YouTubeAPIClient (YouTube Data API v3)
│   └── RateLimiter (token bucket + quota tracking)
├── YouTubeMapper (data transformation)
│   └── YouTube Schemas (Video, Channel, SearchResult)
└── YouTubeConfig (configuration management)
```

## Integration with Video Module

The YouTube Foundation extends the Video module's BaseVideoSource class,
ensuring compatibility with the standardized Video module infrastructure:

```python
from Video.src.core.base_video_source import BaseVideoSource
from Video.src.schemas.video_metadata import VideoMetadata

# YouTubeBaseSource is substitutable for BaseVideoSource
source: BaseVideoSource = YouTubeChannelSource(config)
videos: List[Dict] = source.fetch_videos(query="channel_id")

# Results are compatible with VideoMetadata schema
from pydantic import ValidationError
try:
    video_meta = VideoMetadata(**videos[0])
    print(f"Valid video: {video_meta.title}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Documentation

- [Testing Summary](_meta/docs/TESTING_SUMMARY.md)
- [Issue #005: Implementation Plan](../../../_meta/issues/new/Developer01/005-youtube-foundation-implementation.md)
- [YouTube Integration Coordination](_meta/docs/YOUTUBE_INTEGRATION_COORDINATION.md)

## Support

For issues or questions about the YouTube Foundation:
1. Check the documentation in `_meta/docs/`
2. Review test examples in `_meta/tests/unit/`
3. See issue #005 for implementation details

## License

Part of PrismQ.IdeaInspiration project.
