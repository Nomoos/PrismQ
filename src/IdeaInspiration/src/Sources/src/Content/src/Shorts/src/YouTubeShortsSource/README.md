# PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeShortsSource

YouTube Shorts content source integration module.

## Purpose

This module is responsible for collecting, processing, and analyzing YouTube Shorts content as a source of inspiration for content generation.

## Module Structure

```
YouTubeShortsSource/
├── docs/              # Module documentation
├── issues/            # Module-specific issue tracking
│   ├── new/          # New issues
│   ├── wip/          # Work in progress
│   └── done/         # Completed issues
├── scripts/          # Module utility scripts
├── src/              # Module source code
└── tests/            # Module tests
```

## Responsibilities

- Authenticate with YouTube Data API
- Search and collect YouTube Shorts
- Extract video metadata (title, description, tags, views, etc.)
- Download video content when needed
- Track trending Shorts
- Analyze engagement metrics

## API Integration

This module uses the YouTube Data API v3 for:
- Searching for Shorts content
- Retrieving video details
- Accessing channel information
- Monitoring engagement metrics

## Configuration

Requires YouTube API credentials:
- API Key
- OAuth 2.0 credentials (for advanced features)

## Rate Limits

YouTube Data API quota: 10,000 units per day (default)
- Search: 100 units per request
- Video details: 1 unit per request

## Output Format

Collected Shorts are normalized to a standard format for downstream processing:
```json
{
  "id": "video_id",
  "title": "Video Title",
  "description": "Video Description",
  "channel": "Channel Name",
  "views": 1000000,
  "likes": 50000,
  "duration": 45,
  "published_at": "2025-01-01T00:00:00Z",
  "tags": ["tag1", "tag2"],
  "url": "https://youtube.com/shorts/...",
  "source": "youtube_shorts"
}
```

## Usage Example

```python
from prismq.idea_inspiration.sources.content.shorts.youtube_shorts_source import YouTubeShortsSource

source = YouTubeShortsSource(api_key="your_api_key")
shorts = source.search(query="AI tutorial", max_results=50)
```
