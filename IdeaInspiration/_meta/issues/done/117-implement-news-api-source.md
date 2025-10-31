# Implement NewsApiSource

**Type**: Feature
**Priority**: Medium
**Status**: New
**Category**: Signals/News
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
**Estimated Effort**: 1 week
**Part of**: Issue #027 (Source Implementation Master Plan), Issue #021 (Signals Category)

## Description

Implement NewsApiSource to collect news signals from NewsAPI. This source provides comprehensive news coverage from multiple sources with category filtering.

## Goals

- Collect news articles from NewsAPI
- Track article sources and categories
- Identify trending topics
- Calculate universal signal metrics
- Store signals in SQLite with deduplication
- Provide CLI interface for management

## Reference Implementation

- **Template**: `Sources/Signals/Trends/GoogleTrends/`
- **Guide**: `Sources/Signals/IMPLEMENTATION_GUIDE.md`

## Technical Requirements

### Dependencies
- `newsapi-python` - NewsAPI client library
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

### API Requirements
- **Requires API Key**: Yes
- Sign up at https://newsapi.org/
- Add `NEWSAPI_API_KEY` to .env

### Signal Type
`'news'` - News articles

### Key Features
- Multi-source news aggregation
- Category filtering
- Source credibility tracking
- Language support
- Topic extraction

## Implementation Steps

1. Setup structure from template
2. Implement `news_api_plugin.py`
3. Add NewsAPI client initialization
4. Implement article fetching and parsing
5. Add API key configuration
6. Implement metrics calculations
7. Write comprehensive tests (mock API responses)
8. Document usage and API setup

## Success Criteria

- [ ] SOLID principles followed
- [ ] API key configuration secure
- [ ] Rate limiting implemented
- [ ] Universal metrics calculated
- [ ] CLI interface functional
- [ ] Tests >80% coverage (with mocks)
- [ ] Documentation complete
- [ ] No security vulnerabilities

## Related Issues

- #027 - Source Implementation Master Plan
- #021 - Signals Category Implementation

## Notes

MEDIUM priority - NewsAPI provides comprehensive coverage but requires paid API access for production use.
