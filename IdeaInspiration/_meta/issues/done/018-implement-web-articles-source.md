# Implement Web Articles Source

**Type**: Feature
**Priority**: High
**Status**: New
**Category**: Content/Articles
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement WebArticleSource for collecting general web articles from news sites, blogs, and content platforms, following the architecture pattern established in YouTubeShortsSource.

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Scrape web articles from various sources with metadata
2. Extract article content and key information
3. Support URL-based and RSS feed discovery
4. Transform data to IdeaInspiration format
5. Store in SQLite database with deduplication

## Key Features

### Data Collection
- Article metadata (title, author, publish date, modified date)
- Content extraction (full text, summary)
- Source information (domain, publication)
- Images and media references
- Keywords and categories
- Social share counts (if available)

### Scraping Methods
- URL-based scraping (individual articles)
- RSS/Atom feed parsing
- Sitemap crawling
- Multi-source aggregation
- Content archive scraping

### Universal Metrics
- Social engagement estimates
- Reading time calculation
- Content quality scoring
- Freshness factor
- Cross-platform normalization

## Technical Requirements

### Architecture Components
```
WebArticles/
├── src/
│   ├── cli.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── idea_processor.py
│   └── plugins/
│       ├── __init__.py
│       ├── article_url.py
│       ├── article_rss.py
│       └── article_sitemap.py
```

### Dependencies
- newspaper3k or trafilatura (article extraction)
- feedparser (RSS/Atom feeds)
- BeautifulSoup4, requests
- SQLite, ConfigLoad

### Data Model
```python
{
    'source': 'web_article',
    'source_id': 'url_hash',
    'title': 'Article title',
    'description': 'Article summary',
    'tags': ['category', 'keywords'],
    'author': {
        'name': 'Author Name',
        'email': 'author@example.com'
    },
    'source_info': {
        'domain': 'example.com',
        'publication': 'Publication Name'
    },
    'content': {
        'text': 'Full article text',
        'html': 'Original HTML',
        'top_image': 'image_url'
    },
    'metrics': {
        'reading_time_min': 5,
        'word_count': 1200,
        'social_shares': 500
    },
    'universal_metrics': {
        'engagement_estimate': 3.5,
        'freshness_score': 0.9,
        'quality_score': 7.8
    }
}
```

## Success Criteria

- [ ] URL-based scraping works
- [ ] RSS feed parsing works
- [ ] Article text extraction accurate
- [ ] Metadata extraction complete
- [ ] Universal metrics calculated
- [ ] CLI interface implemented
- [ ] Tests >80% coverage
- [ ] Documentation complete

## Related Issues

- #001 - Unified Pipeline Integration
- #008 - Advanced Source Integrations

## Estimated Effort

2-3 weeks

## Notes

Generic web article scraping provides flexibility to collect from any source. Focus on robust content extraction and source diversity.
