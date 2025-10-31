# Implement Apple Podcasts Source

**Type**: Feature
**Priority**: High
**Status**: New
**Category**: Content/Podcasts
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement ApplePodcastsSource for collecting podcast episodes, metadata, and trending shows from Apple Podcasts, following the architecture pattern established in YouTubeShortsSource.

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Scrape Apple Podcasts episodes with metadata
2. Extract engagement indicators (ratings, reviews)
3. Support category and chart-based discovery
4. Transform data to IdeaInspiration format
5. Store in SQLite database with deduplication

## Technical Requirements

### Architecture Components
```
ApplePodcasts/
├── src/
│   ├── cli.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── idea_processor.py
│   └── plugins/
│       ├── __init__.py
│       ├── apple_charts.py
│       ├── apple_category.py
│       └── apple_show.py
```

### Dependencies
- iTunes Search API or podcastindex
- Requests, BeautifulSoup
- SQLite, ConfigLoad

### Data Model
```python
{
    'source': 'apple_podcasts',
    'source_id': 'episode_id',
    'title': 'Episode title',
    'description': 'Episode description',
    'tags': ['category', 'show_name'],
    'show': {
        'name': 'Show Name',
        'artist': 'Creator',
        'rating': 4.8
    },
    'metrics': {
        'duration_ms': 3600000,
        'release_date': '2025-01-15',
        'rating_count': 1000
    },
    'universal_metrics': {
        'engagement_estimate': 4.8
    }
}
```

## Success Criteria

- [ ] Top charts scraping works
- [ ] Category-based discovery works
- [ ] Episode metadata complete
- [ ] CLI interface implemented
- [ ] Tests >80% coverage

## Related Issues

- #001, #008

## Estimated Effort

2 weeks
