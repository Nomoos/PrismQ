# Implement Instagram Reels Source

**Type**: Feature
**Priority**: High
**Status**: Completed
**Category**: Content/Shorts
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement InstagramReelsSource for collecting short-form video content from Instagram Reels, following the architecture pattern established in YouTubeShortsSource.

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Scrape Instagram Reels with comprehensive metadata
2. Extract engagement metrics (views, likes, comments)
3. Support hashtag-based and explore page discovery
4. Transform data to IdeaInspiration format
5. Store in SQLite database with deduplication

## Key Features

### Data Collection
- Reel metadata (caption, hashtags, music, location)
- Creator information (username, followers, verification)
- Engagement metrics (plays, likes, comments, saves, shares)
- Reel characteristics (duration, filters, effects)
- Audio/music information
- Related reels and trends

### Scraping Methods
- Explore/trending reels discovery
- Hashtag-based search
- Creator profile reels
- Audio/music trend tracking
- Location-based discovery

### Universal Metrics
- Engagement rate calculation
- Reach and impression estimates
- Viral velocity scoring
- Cross-platform normalization

## Technical Requirements

### SOLID Principles
- **SRP**: Separate config, database, metrics, processor, and plugin components
- **OCP**: Extensible plugin architecture for multiple scraping methods
- **LSP**: All Instagram plugins inherit from `SourcePlugin` base class
- **ISP**: Minimal interface with `scrape()` and `get_source_name()`
- **DIP**: Dependency injection for config and database

### Architecture Components
```
InstagramReels/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── idea_processor.py      # IdeaInspiration transform
│   └── plugins/
│       ├── __init__.py             # SourcePlugin base
│       ├── instagram_explore.py    # Explore/trending scraper
│       ├── instagram_hashtag.py    # Hashtag scraper
│       └── instagram_creator.py    # Creator profile scraper
├── _meta/
│   ├── tests/
│   ├── docs/
│   └── issues/
├── requirements.txt
└── README.md
```

### Dependencies
- Instagram scraping library (instaloader, instagram-private-api, or similar)
- SQLite (data persistence)
- ConfigLoad (configuration management)
- Requests/BeautifulSoup (web scraping)

### Data Model
```python
{
    'source': 'instagram_reels',
    'source_id': 'reel_id',
    'title': 'Caption text',
    'description': 'Full caption with hashtags',
    'tags': ['hashtag1', 'hashtag2'],
    'creator': {
        'username': 'creator_username',
        'followers': 50000,
        'verified': False
    },
    'metrics': {
        'plays': 500000,
        'likes': 25000,
        'comments': 1000,
        'saves': 500,
        'shares': 200
    },
    'reel': {
        'duration': 25,
        'audio': 'Original audio - username',
        'location': 'City, Country',
        'filters': ['filter1', 'filter2']
    },
    'universal_metrics': {
        'engagement_rate': 5.2,
        'plays_per_hour': 5000,
        'viral_velocity': 7.8
    }
}
```

## Success Criteria

- [x] Can scrape trending/explore Instagram Reels
- [x] Hashtag-based discovery working
- [x] Creator profile scraping implemented
- [x] All metadata extracted and stored
- [x] Universal metrics calculated correctly
- [x] Deduplication prevents duplicate entries
- [x] Data transforms to IdeaInspiration format
- [x] CLI interface matches YouTube implementation
- [x] Comprehensive tests (14 tests, all passing)
- [x] Documentation complete

## Implementation Steps

1. Set up project structure following YouTube pattern
2. Implement Config class with Instagram-specific settings
3. Create Database schema for Instagram Reels content
4. Implement UniversalMetrics for Instagram engagement
5. Create SourcePlugin base class
6. Implement InstagramExplorePlugin
7. Implement InstagramHashtagPlugin
8. Implement InstagramCreatorPlugin
9. Create IdeaProcessor for data transformation
10. Build CLI interface
11. Write comprehensive tests
12. Create documentation

## Related Issues

- #001 - Unified Pipeline Integration
- #008 - Advanced Source Integrations

## API/Scraping Considerations

- Instagram has strict rate limiting and anti-bot measures
- May require authentication for full access
- Consider using unofficial APIs carefully
- Respect robots.txt and ToS
- Implement session management and cookies
- Handle CAPTCHAs and rate limit errors
- Rotate user agents and IPs if needed

## Estimated Effort

2-3 weeks

## Notes

Instagram Reels is a major platform for short-form content with high engagement rates. Focus on explore/trending discovery as primary use case for IdeaInspiration.
