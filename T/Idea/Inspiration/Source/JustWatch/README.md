# JustWatch Video Source

Integration module for JustWatch streaming analytics platform.

## Overview

This module provides unified access to streaming content analytics across 7+ major streaming platforms through the JustWatch API.

**Status**: Foundation Complete ✅  
**API**: JustWatch API  
**Category**: Video

## Features

- **Multi-Platform Support** - Access data from Disney+, Netflix, Prime Video, Hulu, HBO Max, Apple TV+, Paramount+
- **Popularity Metrics** - Standardized popularity scores (0-10 scale)
- **Trending Content** - Daily trending shows and movies
- **New Releases** - Recently added content tracking
- **Cross-Platform Comparison** - Compare metrics across platforms
- **Country Support** - Data for 60+ countries
- **Rate Limiting** - Built-in rate limiting support

## Supported Streaming Providers

| Provider | Code | Content Types |
|----------|------|---------------|
| Disney+ | `disney` | Series, Movies, Originals |
| Amazon Prime | `prime` | Series, Movies, Originals |
| Netflix | `netflix` | Series, Movies, Originals |
| Hulu | `hulu` | Series, Movies, Originals |
| HBO Max | `hbomax` | Series, Movies, Originals |
| Apple TV+ | `appletv` | Series, Movies, Originals |
| Paramount+ | `paramount` | Series, Movies, Originals |

## Quick Start

```python
from Source.Video.JustWatch.src import JustWatchClient

# Initialize client
client = JustWatchClient(
    api_key="your_api_key",
    default_country="US"
)

# Fetch popular content for Disney+
popular = client.fetch_popular_content(
    provider="disney",
    content_type="show",
    limit=50
)

# Fetch trending content for Netflix
trending = client.fetch_trending_content(
    provider="netflix",
    limit=30
)

# Search for content
results = client.search_content(
    query="Breaking Bad",
    provider="netflix"
)

# Get cross-platform trending
cross_platform = client.get_cross_platform_trending(
    limit=20
)
```

## Configuration

Set environment variables or pass directly:

```bash
JUSTWATCH_API_KEY=your_api_key_here
JUSTWATCH_DEFAULT_COUNTRY=US
```

## API Credentials

1. Go to [JustWatch API](https://www.justwatch.com/us/JustWatch-API)
2. Sign up for API access
3. Get your API key
4. Set environment variable or pass to client

## Rate Limits

- **Free Tier**: 1,000 requests per month
- **Basic Tier**: 10,000 requests per month  
- **Pro Tier**: 100,000 requests per month
- **Recommended**: Cache results, update daily

## Content Metadata

The client returns content with the following structure:

```python
{
    'title': 'The Mandalorian',
    'content': 'A Mandalorian bounty hunter...',
    'metadata': {
        'platform': 'justwatch',
        'provider': 'disney',
        'content_type': 'show',
        'country': 'US',
        'justwatch_id': '12345',
        'popularity_score': 8.5,
        'trending_rank': 3,
        'release_date': '2019',
        'genres': ['Action', 'Adventure', 'Sci-Fi'],
        'imdb_score': 8.7,
        'tmdb_score': 8.5,
        'runtime_minutes': 40,
        'seasons': 3,
        'episodes': 24,
        'is_original': True
    }
}
```

## Migration from Old Structure

This is a single source implementation. The old multi-platform structure at `Source/JustWatch/` with separate subdirectories for each platform (Disney/, Netflix/, etc.) has been consolidated into this unified client.

**Key Changes:**
- Single `JustWatchClient` instead of multiple worker classes
- Providers handled as parameters, not separate classes
- Simplified imports: `from Source.Video.JustWatch.src import JustWatchClient`
- All platform functionality accessible through one client instance

## Dependencies

- `requests>=2.31.0` - HTTP client
- `python-dotenv>=1.0.0` - Environment variables

## Testing

```bash
cd Source/Video/JustWatch
pytest _meta/tests/
```

## Documentation

- [JustWatch API Documentation](https://www.justwatch.com/us/JustWatch-API)
- [Video Module Documentation](../README.md)

## Benefits

### Cross-Platform Analytics
- Unified data source for all streaming platforms
- Standardized popularity metrics
- Comparative analysis capabilities
- Trend detection across platforms

### Cost-Effective
- Free tier available for MVP
- Single API integration reduces complexity
- No per-platform authentication needed
- Pre-processed popularity metrics

### Comprehensive Coverage
- Major US streaming platforms
- International support (60+ countries)
- Real-time updates
- Historical data tracking

## License

Part of PrismQ.IdeaInspiration project - Proprietary
