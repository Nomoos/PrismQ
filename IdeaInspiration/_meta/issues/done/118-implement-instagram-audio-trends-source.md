# Implement InstagramAudioTrendsSource

**Type**: Feature
**Priority**: Lower
**Status**: New
**Category**: Signals/Sounds
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
**Estimated Effort**: 1 week
**Part of**: Issue #027 (Source Implementation Master Plan), Issue #021 (Signals Category)

## Description

Implement InstagramAudioTrendsSource to collect trending audio signals from Instagram Reels. This source identifies popular audio tracks used in Reels content.

## Goals

- Collect trending Instagram Reels audio
- Track audio usage and trends
- Identify original vs. licensed music
- Calculate universal signal metrics
- Store signals in SQLite with deduplication
- Provide CLI interface for management

## Reference Implementation

- **Template**: `Sources/Signals/Trends/GoogleTrends/`
- **Guide**: `Sources/Signals/IMPLEMENTATION_GUIDE.md`

## Technical Requirements

### Dependencies
- `instaloader` - Instagram data access
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

### Signal Type
`'sound'` - Trending audio

### Key Features
- Audio trend tracking
- Usage count monitoring
- Artist attribution
- Audio type classification
- Geographic trends

## Implementation Steps

1. Setup structure from template
2. Implement `instagram_audio_trends_plugin.py`
3. Add audio trend scraping
4. Implement metrics calculations
5. Write comprehensive tests
6. Document usage and examples

## Success Criteria

- [ ] SOLID principles followed
- [ ] Universal metrics calculated
- [ ] CLI interface functional
- [ ] Tests >80% coverage
- [ ] Documentation complete
- [ ] No security vulnerabilities

## Related Issues

- #027 - Source Implementation Master Plan
- #021 - Signals Category Implementation

## Notes

LOWER priority - Similar to TikTokSounds but for Instagram Reels. Implement after higher priority sources.
