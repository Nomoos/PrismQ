# Implement Reddit Source

**Type**: Feature
**Priority**: High
**Status**: New
**Category**: Content/Forums
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement RedditSource for collecting community discussions, trending posts, and viral content from Reddit, following the architecture pattern established in YouTubeShortsSource.

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Scrape Reddit posts with comprehensive metadata
2. Extract engagement metrics (upvotes, comments, awards)
3. Support subreddit-based and trending discovery
4. Transform data to IdeaInspiration format
5. Store in SQLite database with deduplication

## Key Features

### Data Collection
- Post metadata (title, selftext, flair, timestamp)
- Author information (username, karma, account age)
- Engagement metrics (score, upvote ratio, comments, awards)
- Subreddit context (name, subscribers, rules)
- Comment analysis (top comments, sentiment)
- Media content (images, videos, links)

### Scraping Methods
- r/all trending posts
- Subreddit-specific trending
- Rising posts discovery
- Top posts (daily, weekly, monthly)
- Search-based discovery
- Multireddit aggregation

### Universal Metrics
- Upvote velocity (score per hour/day)
- Engagement rate (comments/views ratio)
- Award density (premium engagement)
- Viral potential scoring
- Cross-platform normalization

## Technical Requirements

### SOLID Principles
- **SRP**: Separate config, database, metrics, processor, and plugin components
- **OCP**: Extensible plugin architecture for multiple scraping methods
- **LSP**: All Reddit plugins inherit from `SourcePlugin` base class
- **ISP**: Minimal interface with `scrape()` and `get_source_name()`
- **DIP**: Dependency injection for config and database

### Architecture Components
```
Reddit/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── idea_processor.py      # IdeaInspiration transform
│   └── plugins/
│       ├── __init__.py             # SourcePlugin base
│       ├── reddit_trending.py      # r/all trending scraper
│       ├── reddit_subreddit.py     # Subreddit scraper
│       ├── reddit_rising.py        # Rising posts scraper
│       └── reddit_search.py        # Search-based scraper
├── tests/
├── _meta/
│   ├── docs/
│   └── issues/
├── requirements.txt
└── README.md
```

### Dependencies
- PRAW (Python Reddit API Wrapper) - official Reddit API
- SQLite (data persistence)
- ConfigLoad (configuration management)
- NLTK or TextBlob (comment sentiment analysis)

### Data Model
```python
{
    'source': 'reddit',
    'source_id': 'post_id',
    'title': 'Post title',
    'description': 'Selftext content',
    'tags': ['subreddit', 'flair', 'keywords'],
    'author': {
        'username': 'author_name',
        'karma': 50000,
        'account_age_days': 365
    },
    'subreddit': {
        'name': 'subreddit_name',
        'subscribers': 1000000,
        'type': 'public'
    },
    'metrics': {
        'score': 10000,
        'upvote_ratio': 0.95,
        'num_comments': 500,
        'num_awards': 25,
        'award_types': ['gold', 'platinum']
    },
    'content': {
        'type': 'text|link|image|video',
        'url': 'content_url',
        'media_metadata': {}
    },
    'comments': {
        'top_comments': ['comment1', 'comment2'],
        'sentiment_avg': 0.75
    },
    'universal_metrics': {
        'engagement_rate': 5.0,
        'score_per_hour': 1000,
        'viral_velocity': 8.2,
        'award_density': 2.5
    }
}
```

## Success Criteria

- [ ] Can scrape r/all trending posts
- [ ] Subreddit-specific scraping working
- [ ] Rising posts discovery implemented
- [ ] Search functionality working
- [ ] All metadata extracted and stored
- [ ] Comment analysis implemented
- [ ] Universal metrics calculated correctly
- [ ] Deduplication prevents duplicate entries
- [ ] Data transforms to IdeaInspiration format
- [ ] CLI interface matches YouTube implementation
- [ ] Comprehensive tests (>80% coverage)
- [ ] Documentation complete

## Implementation Steps

1. Set up project structure following YouTube pattern
2. Register Reddit application for API access
3. Implement Config class with Reddit-specific settings
4. Create Database schema for Reddit posts
5. Implement UniversalMetrics for Reddit engagement
6. Create SourcePlugin base class
7. Implement RedditTrendingPlugin
8. Implement RedditSubredditPlugin
9. Implement RedditRisingPlugin
10. Implement RedditSearchPlugin
11. Add comment analysis module
12. Create IdeaProcessor for data transformation
13. Build CLI interface
14. Write comprehensive tests
15. Create documentation

## Related Issues

- #001 - Unified Pipeline Integration
- #008 - Advanced Source Integrations

## API Considerations

- Reddit API requires OAuth authentication
- Rate limits: 60 requests per minute for authenticated users
- Need Client ID and Client Secret from https://www.reddit.com/prefs/apps
- PRAW handles rate limiting automatically
- Consider Read-Only mode for scraping (no posting needed)
- Respect subreddit rules and Reddit ToS

## Estimated Effort

2-3 weeks

## Notes

Reddit is an excellent source for IdeaInspiration due to its diverse communities and trending content discovery. Focus on trending and rising posts as they indicate viral potential. Comment analysis can provide additional context and sentiment data.
