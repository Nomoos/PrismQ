# Implement Spotify Podcasts Source

**Type**: Feature
**Priority**: High
**Status**: Done
**Category**: Content/Podcasts
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
**Completed**: 2025-10-30

## Description

Implement SpotifyPodcastsSource for collecting podcast episodes, metadata, and trending shows from Spotify, following the architecture pattern established in YouTubeShortsSource.

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Scrape Spotify podcast episodes with metadata
2. Extract engagement indicators (ratings, followers)
3. Support category and trending discovery
4. Transform data to IdeaInspiration format
5. Store in SQLite database with deduplication

## Technical Requirements

### Architecture Components
```
SpotifyPodcasts/
├── src/
│   ├── cli.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── idea_processor.py
│   └── plugins/
│       ├── __init__.py
│       ├── spotify_trending.py
│       ├── spotify_category.py
│       └── spotify_show.py
```

### Dependencies
- Spotipy (Spotify API wrapper)
- SQLite, ConfigLoad

### Data Model
```python
{
    'source': 'spotify_podcasts',
    'source_id': 'episode_id',
    'title': 'Episode title',
    'description': 'Episode description',
    'tags': ['category', 'show_name'],
    'show': {
        'name': 'Show Name',
        'publisher': 'Publisher',
        'total_episodes': 100
    },
    'metrics': {
        'duration_ms': 3600000,
        'release_date': '2025-01-15'
    },
    'universal_metrics': {
        'engagement_estimate': 5.0
    }
}
```

## Success Criteria

- [x] Trending podcasts scraping works
- [x] Category-based discovery works
- [x] Episode metadata complete
- [x] CLI interface implemented
- [x] Tests >80% coverage (94% for core modules)

## Implementation Summary

Successfully implemented SpotifyPodcastsSource module with:
- ✅ Complete architecture matching YouTubeShortsSource pattern
- ✅ Three scraping plugins: trending, category, show
- ✅ Full CLI with 7 commands
- ✅ 19 passing tests with 94%+ coverage on core modules
- ✅ Universal metrics for cross-platform compatibility
- ✅ SQLite database with deduplication
- ✅ IdeaInspiration transformation support

Location: `Sources/Content/Podcasts/SpotifyPodcasts/`

## Related Issues

- #001, #008

## Estimated Effort

2 weeks
