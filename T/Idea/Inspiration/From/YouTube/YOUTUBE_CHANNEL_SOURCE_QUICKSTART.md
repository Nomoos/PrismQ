# YouTube Channel Source - Quick Start

## Overview

YouTubeChannelSource fetches videos from specific YouTube channels using an efficient two-stage approach that saves 99% API quota compared to traditional methods.

## Installation

Already included in YouTube Foundation requirements.

## Basic Usage

```python
from src.sources import YouTubeChannelSource
from src.config import YouTubeConfig

# Initialize
config = YouTubeConfig(api_key="YOUR_YOUTUBE_API_KEY")
source = YouTubeChannelSource(config)

# Fetch videos from channel
videos = source.fetch_videos(
    query='@mkbhd',  # Can use @username, channel ID, or URL
    limit=50
)

print(f"Found {len(videos)} videos")
for video in videos[:5]:
    print(f"- {video['title']} ({video['duration_seconds']}s)")
```

## Advanced Features

### 1. Fetch with Filters

```python
# Filter by date range
videos = source.fetch_videos(
    query='UC...',  # Channel ID
    limit=100,
    filters={
        'published_after': '2024-01-01T00:00:00Z',
        'published_before': '2024-12-31T23:59:59Z',
        'order': 'viewCount'  # Sort by views
    }
)
```

### 2. TaskManager Integration

```python
from TaskManager import TaskManagerClient

# Initialize TaskManager client
tm_client = TaskManagerClient(api_url="http://localhost:8000")

# Create tasks for new videos
new_tasks = source.create_tasks_for_new_videos(
    channel_id='UC...',
    task_manager_client=tm_client
)

print(f"Created {new_tasks} new tasks")
```

### 3. Monitor Multiple Channels

```python
channels = [
    'UC...channel1',
    'UC...channel2',
    '@mkbhd',
    '@linustechtips'
]

for channel in channels:
    try:
        videos = source.fetch_videos(channel, limit=20)
        print(f"{channel}: {len(videos)} videos")
    except Exception as e:
        print(f"Error with {channel}: {e}")
```

## Efficiency

### Two-Stage Approach

**Stage 1**: Extract video IDs (yt-dlp, no API quota)
```python
video_ids = source.fetch_channel_videos_efficient('@mkbhd', limit=100)
# Returns: ['abc123', 'def456', ...] in ~5 seconds
```

**Stage 2**: Batch fetch details (API, minimal quota)
```python
# Fetches details for 50 videos using only 1 quota unit
videos = source._fetch_videos_batch(video_ids[:50])
```

### Quota Savings

| Method | Quota for 100 videos | Time |
|--------|---------------------|------|
| Traditional API | ~200 units | 30s |
| YouTubeChannelSource | ~2 units | 7s |
| **Savings** | **99%** | **77%** |

## Channel Identifier Formats

The source accepts multiple channel identifier formats:

```python
# Username with @
source.fetch_videos('@mkbhd')

# Username without @
source.fetch_videos('mkbhd')

# Channel ID
source.fetch_videos('UC123456789')

# Full URL
source.fetch_videos('https://www.youtube.com/@mkbhd/videos')
```

## Error Handling

```python
from src.exceptions import YouTubeError

try:
    videos = source.fetch_videos('@invalid_channel')
except YouTubeError as e:
    print(f"Error: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
```

## Performance Tips

1. **Use TaskManager for deduplication**: Avoid fetching videos already processed
2. **Batch process channels**: Process multiple channels in parallel
3. **Set appropriate limits**: Don't fetch more videos than needed
4. **Cache results**: Store channel metadata to reduce repeated fetches
5. **Monitor quota**: Use `source.get_quota_usage()` to track API usage

## Integration with Video Module

YouTubeChannelSource is compatible with Video module's BaseVideoSource:

```python
from Video.src.core.base_video_source import BaseVideoSource

# Polymorphic usage
source: BaseVideoSource = YouTubeChannelSource(config)
videos = source.fetch_videos('@mkbhd', limit=10)
```

## Examples

See `examples/youtube_channel_examples.py` for more detailed examples.

## Troubleshooting

### yt-dlp not found
```bash
pip install yt-dlp
```

### API quota exceeded
Check quota usage:
```python
quota = source.get_quota_usage()
print(f"Used: {quota['used']}/{quota['limit']}")
```

### Channel not found
Verify channel identifier:
```python
# Get uploads playlist
playlist_id = source.get_channel_uploads_playlist('UC...')
print(f"Uploads playlist: {playlist_id}")
```

## API Reference

See source code docstrings for detailed API documentation.
