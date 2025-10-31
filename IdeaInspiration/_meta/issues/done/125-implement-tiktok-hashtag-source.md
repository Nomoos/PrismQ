# Issue #125: Implement TikTokHashtagSource

**Type**: Feature
**Priority**: High
**Status**: New
**Category**: Signals/Hashtags
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
**Estimated Effort**: 1 week
**Part of**: Issue #027 (Source Implementation Master Plan), Issue #021 (Signals Category)

## Description

Implement TikTokHashtagSource to collect trending hashtag signals from TikTok. This source identifies viral hashtags and their usage patterns to inform content strategy.

## Goals

- Collect trending TikTok hashtags
- Track hashtag view counts and usage metrics
- Identify related hashtags and trending combinations
- Calculate universal signal metrics (trend strength, velocity, acceleration)
- Store signals in SQLite with deduplication
- Provide CLI interface for management

## Reference Implementation

Follow the proven architecture from:
- **Template**: `Sources/Signals/Trends/GoogleTrends/`
- **Guide**: `Sources/Signals/IMPLEMENTATION_GUIDE.md`

## Technical Requirements

### Architecture
```
TikTokHashtag/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── config.py             # Configuration management
│   │   ├── database.py           # Database operations (reuse from template)
│   │   ├── metrics.py            # Universal metrics
│   │   └── signal_processor.py  # Signal transformation
│   └── plugins/
│       ├── __init__.py           # SignalPlugin base class
│       └── tiktok_hashtag_plugin.py  # TikTok implementation
├── tests/                        # >80% coverage
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Dependencies
- `TikTokApi` - TikTok data access
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

### Signal Format
```python
{
    'source_id': 'hashtag_id_timestamp',
    'signal_type': 'hashtag',
    'name': '#HashtagName',
    'description': 'Hashtag description/context',
    'tags': ['tiktok', 'viral', 'category'],
    'metrics': {
        'volume': 1500000,  # View count
        'velocity': 45.2,   # Growth rate
        'acceleration': 12.1,  # Change in velocity
        'geographic_spread': ['US', 'UK', 'CA']
    },
    'temporal': {
        'first_seen': '2025-10-30T00:00:00Z',
        'peak_time': None,
        'current_status': 'rising'
    },
    'universal_metrics': {
        'trend_strength': 8.7,
        'virality_score': 9.1
    }
}
```

## Implementation Steps

1. **Setup** (Day 1)
   - Use scaffolding generator: `python scripts/generate_signal_sources.py`
   - Or manually copy GoogleTrends template
   - Update configuration files

2. **Core Implementation** (Days 2-3)
   - Implement `tiktok_hashtag_plugin.py`
   - Initialize TikTokApi client
   - Implement hashtag scraping logic
   - Map TikTok data to signal format
   - Add error handling and rate limiting

3. **Metrics & Processing** (Day 4)
   - Implement universal metrics calculations
   - Add trend strength scoring
   - Calculate velocity and acceleration
   - Implement signal processor

4. **Testing** (Day 5)
   - Write unit tests for plugin
   - Test database operations
   - Test metrics calculations
   - Mock TikTok API responses
   - Achieve >80% code coverage

5. **Documentation & Polish** (Days 6-7)
   - Update README with usage examples
   - Document configuration options
   - Add CLI examples
   - Test end-to-end functionality
   - Update issue #027 progress

## Success Criteria

- [ ] TikTokHashtagSource implemented with SOLID principles
- [ ] Plugin architecture extensible
- [ ] Universal metrics calculated correctly
- [ ] Data persists to SQLite with deduplication
- [ ] Signals transform to unified format
- [ ] CLI interface functional (scrape, list, stats, export, clear)
- [ ] Tests >80% coverage
- [ ] Documentation complete
- [ ] No security vulnerabilities
- [ ] Integration with existing Signals ecosystem

## API Considerations

- TikTok API may require authentication
- Respect rate limits (implement delays)
- Handle API changes gracefully
- Consider using async patterns if needed

## Related Issues

- #027 - Source Implementation Master Plan
- #021 - Signals Category Implementation

## Notes

This is a HIGH priority signal source as hashtags are strong indicators of viral content trends. TikTok is a leading platform for trend generation, making this source valuable for content strategy.

**Scaffolding Available**: Run `python scripts/generate_signal_sources.py` to generate initial structure.
