# Implement Hacker News Source

**Type**: Feature
**Priority**: High
**Status**: New
**Category**: Content/Forums
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement HackerNewsSource for collecting tech community discussions, trending posts, and high-quality content from Hacker News (news.ycombinator.com), following the architecture pattern established in YouTubeShortsSource.

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Scrape Hacker News posts with comprehensive metadata
2. Extract engagement metrics (points, comments)
3. Support front page, new, and best discovery
4. Transform data to IdeaInspiration format
5. Store in SQLite database with deduplication

## Key Features

### Data Collection
- Post metadata (title, URL, text, timestamp)
- Author information (username, karma)
- Engagement metrics (points, comments)
- Post type (story, ask, show, job, poll)
- Comment tree analysis
- Domain and URL metadata

### Scraping Methods
- Front page trending stories
- New stories discovery
- Best stories (algorithmically ranked)
- Ask HN posts (questions)
- Show HN posts (projects/products)
- Top stories (by time period)

### Universal Metrics
- Point velocity (points per hour)
- Comment engagement rate
- Time to front page
- Viral potential scoring
- Cross-platform normalization

## Technical Requirements

### SOLID Principles
- **SRP**: Separate config, database, metrics, processor, and plugin components
- **OCP**: Extensible plugin architecture for multiple scraping methods
- **LSP**: All HN plugins inherit from `SourcePlugin` base class
- **ISP**: Minimal interface with `scrape()` and `get_source_name()`
- **DIP**: Dependency injection for config and database

### Architecture Components
```
HackerNews/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── idea_processor.py      # IdeaInspiration transform
│   └── plugins/
│       ├── __init__.py             # SourcePlugin base
│       ├── hn_frontpage.py         # Front page scraper
│       ├── hn_new.py               # New stories scraper
│       ├── hn_best.py              # Best stories scraper
│       └── hn_type.py              # Type-based scraper (Ask/Show HN)
├── tests/
├── _meta/
│   ├── docs/
│   └── issues/
├── requirements.txt
└── README.md
```

### Dependencies
- HackerNews API (official Firebase API)
- python-hn or custom API client
- Requests (for API calls)
- SQLite (data persistence)
- ConfigLoad (configuration management)

### Data Model
```python
{
    'source': 'hackernews',
    'source_id': 'item_id',
    'title': 'Post title',
    'description': 'Post text content (for Ask/Show HN)',
    'tags': ['type', 'domain', 'keywords'],
    'author': {
        'username': 'author_id',
        'karma': 5000
    },
    'post': {
        'type': 'story|ask|show|job|poll',
        'url': 'external_url',
        'domain': 'example.com',
        'text': 'Self-post text'
    },
    'metrics': {
        'score': 500,
        'num_comments': 150,
        'descendants': 200  # total comment tree size
    },
    'timing': {
        'created_at': '2025-01-15T10:30:00Z',
        'time_to_frontpage_hours': 2.5
    },
    'comments': {
        'top_level_count': 50,
        'avg_depth': 3.2
    },
    'universal_metrics': {
        'engagement_rate': 30.0,  # comments/score ratio
        'points_per_hour': 100,
        'viral_velocity': 7.5
    }
}
```

## Success Criteria

- [ ] Can scrape HN front page stories
- [ ] New stories discovery working
- [ ] Best stories scraping implemented
- [ ] Type-based filtering (Ask/Show HN) working
- [ ] All metadata extracted and stored
- [ ] Comment metrics calculated
- [ ] Universal metrics calculated correctly
- [ ] Deduplication prevents duplicate entries
- [ ] Data transforms to IdeaInspiration format
- [ ] CLI interface matches YouTube implementation
- [ ] Comprehensive tests (>80% coverage)
- [ ] Documentation complete

## Implementation Steps

1. Set up project structure following YouTube pattern
2. Implement Config class with HN-specific settings
3. Create Database schema for HN stories
4. Implement UniversalMetrics for HN engagement
5. Create SourcePlugin base class
6. Implement HNFrontpagePlugin
7. Implement HNNewPlugin
8. Implement HNBestPlugin
9. Implement HNTypePlugin (Ask/Show filtering)
10. Create IdeaProcessor for data transformation
11. Build CLI interface
12. Write comprehensive tests
13. Create documentation

## Related Issues

- #001 - Unified Pipeline Integration
- #008 - Advanced Source Integrations

## API Considerations

- HN official API: https://github.com/HackerNews/API
- Firebase-based API with real-time updates
- No authentication required
- No explicit rate limits (be respectful)
- API endpoints:
  - `/v0/topstories.json` - top 500 stories
  - `/v0/newstories.json` - newest stories
  - `/v0/beststories.json` - best stories
  - `/v0/item/{id}.json` - individual item
- Consider caching to minimize API calls

## Estimated Effort

1-2 weeks

## Notes

Hacker News provides high-quality tech and startup content with strong community curation. Excellent source for IdeaInspiration in tech/business domains. Simpler API than Reddit makes implementation faster. Focus on front page and Ask/Show HN posts for best content quality.
