# YouTube Integration Coordination Document

**Project**: PrismQ.IdeaInspiration - YouTube Integration  
**Owner**: Developer01 (SCRUM Master & Planning Expert)  
**Created**: 2025-11-12  
**Status**: 🟢 Active Planning  
**Priority**: ⭐ CRITICAL  
**Timeline**: 5-7 days coordinated effort

---

## Executive Summary

This document coordinates the integration of all YouTube sub-modules (Channel, Search, Video) with the Video module infrastructure. It provides the master plan for implementing shared YouTube components and ensuring consistent patterns across all sub-modules.

### Key Deliverables
- ✅ YouTubeBaseSource extending BaseVideoSource
- ✅ YouTubeAPIClient with rate limiting
- ✅ YouTube-specific schemas and mappers
- ✅ Integration of all three sub-modules (Channel, Search, Video)
- ✅ Comprehensive testing and documentation

### Success Metrics
- All YouTube sub-modules use shared foundation
- API quota management working correctly
- >80% test coverage
- SOLID principles validated
- Production-ready implementation

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Shared Foundation](#shared-foundation)
3. [Sub-Module Integration](#sub-module-integration)
4. [Implementation Timeline](#implementation-timeline)
5. [Team Coordination](#team-coordination)
6. [Quality Standards](#quality-standards)
7. [Risk Management](#risk-management)
8. [Success Criteria](#success-criteria)

---

## Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────────────┐
│           PrismQ.IdeaInspiration                │
│         (IdeaInspiration Model)                 │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────┐
│            Video Module Layer                    │
│  (BaseVideoSource, VideoProcessor, Schemas)     │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────┐
│          YouTube Integration Layer               │
│      (YouTubeBaseSource, YouTubeClient)         │
└────┬────────────┬────────────┬──────────────────┘
     │            │            │
┌────┴────┐  ┌───┴────┐  ┌───┴────────┐
│ Channel │  │ Search │  │   Video    │
│ Module  │  │ Module │  │   Module   │
└─────────┘  └────────┘  └────────────┘
```

### Current State Analysis

**Existing Structure:**
```
Source/Video/YouTube/
├── Channel/        ✅ Active (has workers)
├── Search/         🔵 To implement
├── Video/          🔵 To implement
└── src/            📋 Shared foundation (to create)
```

**Status:**
- ✅ Channel module exists with worker implementation
- ❓ Search module structure exists but needs implementation
- ❓ Video module structure exists but needs implementation
- ❌ Shared YouTube foundation needs to be created

---

## Shared Foundation

### Directory Structure

```
Source/Video/YouTube/src/
├── __init__.py
├── base/
│   ├── __init__.py
│   └── youtube_base_source.py    # Extends BaseVideoSource
├── client/
│   ├── __init__.py
│   ├── youtube_api_client.py     # YouTube Data API v3 client
│   └── rate_limiter.py            # API quota management
├── schemas/
│   ├── __init__.py
│   ├── youtube_video.py           # YouTube video schema
│   ├── youtube_channel.py         # YouTube channel schema
│   └── youtube_search.py          # YouTube search result schema
└── mappers/
    ├── __init__.py
    └── youtube_mapper.py          # YouTube → VideoMetadata
```

### Core Components

#### 1. YouTubeBaseSource
**Purpose**: Base class for all YouTube content sources  
**Responsibilities**:
- API client management
- Rate limiting enforcement
- Response parsing (YouTube → standard format)
- Error handling and retries
- Common configuration validation

**Key Methods**:
- `__init__(config)` - Initialize with YouTube-specific config
- `_validate_config()` - Validate API key and settings
- `_parse_video_response(response)` - Parse YouTube API response
- `_parse_duration(duration_str)` - Parse ISO 8601 duration
- `fetch_videos()` - Abstract method for subclasses

**SOLID Compliance**:
- ✅ Single Responsibility: YouTube-specific base functionality
- ✅ Open/Closed: Extensible without modification
- ✅ Liskov Substitution: All YouTube sources substitutable
- ✅ Interface Segregation: Focused interface
- ✅ Dependency Inversion: Depends on abstractions

#### 2. YouTubeAPIClient
**Purpose**: YouTube Data API v3 client with rate limiting  
**Responsibilities**:
- API authentication
- Rate limiting and quota management
- Request retries with exponential backoff
- Error handling

**Key Methods**:
- `search()` - Search for videos
- `get_video_details()` - Get detailed video information
- `get_channel_details()` - Get channel information
- `_make_request()` - Internal request handler with retries

**Configuration**:
```python
{
    'api_key': str,              # YouTube API key
    'rate_limit': int,           # Requests per minute (default: 100)
    'retry_count': int,          # Max retries (default: 3)
    'timeout': int               # Request timeout (default: 30)
}
```

#### 3. RateLimiter
**Purpose**: Manage API quota and prevent rate limit errors  
**Responsibilities**:
- Track request timestamps
- Enforce rate limits
- Implement token bucket algorithm

**Features**:
- Configurable requests per minute
- Thread-safe implementation
- Automatic wait management

#### 4. YouTubeMapper
**Purpose**: Map YouTube API responses to VideoMetadata format  
**Responsibilities**:
- Parse YouTube video data
- Convert to standard VideoMetadata schema
- Handle missing/optional fields
- Extract shorts detection

**Key Mappings**:
- YouTube snippet → VideoMetadata
- Duration parsing (ISO 8601 → seconds)
- Thumbnail selection
- Statistics mapping

#### 5. YouTube Schemas
**Purpose**: Define YouTube-specific data structures  
**Components**:
- `YouTubeVideoSchema` - Video data structure
- `YouTubeChannelSchema` - Channel data structure
- `YouTubeSearchResultSchema` - Search result structure

---

## Sub-Module Integration

### 1. Channel Module

**Current Status**: ✅ Existing with worker implementation

**Integration Tasks**:
- [ ] Refactor to extend YouTubeBaseSource
- [ ] Migrate to shared YouTubeAPIClient
- [ ] Update schemas to use shared components
- [ ] Maintain backward compatibility
- [ ] Update tests for new structure

**Implementation Priority**: HIGH (most common use case)

**Key Features**:
- Channel video listing
- Channel metadata retrieval
- Shorts vs regular video filtering
- Upload schedule tracking

**Timeline**: Days 3-4

---

### 2. Search Module

**Current Status**: 🔵 Structure exists, implementation needed

**Integration Tasks**:
- [ ] Implement YouTubeSearchSource extending YouTubeBaseSource
- [ ] Keyword search functionality
- [ ] Advanced filtering (duration, date, order)
- [ ] Trending detection
- [ ] Integration with storage schema
- [ ] Unit and integration tests
- [ ] CLI commands

**Implementation Priority**: HIGH (essential for discovery)

**Key Features**:
- Keyword search
- Trending content discovery
- Category-based search
- Advanced filters (duration, date, etc.)

**Search Parameters**:
```python
{
    'query': str,                # Search query (optional)
    'channel_id': str,           # Filter by channel (optional)
    'max_results': int,          # Max results 1-50 (default: 10)
    'order': str,                # relevance, date, rating, viewCount
    'published_after': str,      # RFC 3339 timestamp
    'video_duration': str,       # any, short, medium, long
    'video_type': str            # any, episode, movie
}
```

**Timeline**: Days 4-5

---

### 3. Video Module

**Current Status**: 🔵 Structure exists, implementation needed

**Integration Tasks**:
- [ ] Implement YouTubeVideoSource extending YouTubeBaseSource
- [ ] Single video details endpoint
- [ ] Batch video retrieval (up to 50 videos)
- [ ] Related videos fetching
- [ ] Integration tests
- [ ] CLI commands

**Implementation Priority**: MEDIUM (supporting functionality)

**Key Features**:
- Single video details
- Batch video retrieval
- Related videos
- Comments and transcripts (future)

**Video Details Parameters**:
```python
{
    'video_ids': List[str],      # Video IDs (max 50)
    'include_related': bool,     # Include related videos
    'include_comments': bool     # Include comments (future)
}
```

**Timeline**: Days 5-6

---

## Implementation Timeline

### Phase 1: Foundation (Days 1-2)
**Focus**: Create shared YouTube components

**Day 1 - Morning**:
- [ ] Create directory structure (YouTube/src/)
- [ ] Implement YouTubeBaseSource class
- [ ] Create basic error handling

**Day 1 - Afternoon**:
- [ ] Implement RateLimiter class
- [ ] Start YouTubeAPIClient implementation
- [ ] Unit tests for RateLimiter

**Day 2 - Morning**:
- [ ] Complete YouTubeAPIClient
- [ ] Implement YouTubeMapper
- [ ] Create YouTube schemas

**Day 2 - Afternoon**:
- [ ] Unit tests for all foundation components
- [ ] Integration tests with mock API
- [ ] Documentation for foundation

**Deliverables**:
- ✅ YouTubeBaseSource complete
- ✅ YouTubeAPIClient with rate limiting
- ✅ YouTubeMapper functional
- ✅ Schemas defined
- ✅ Unit tests passing
- ✅ Foundation documentation

---

### Phase 2: Channel Module Integration (Days 3-4)
**Focus**: Refactor existing Channel module

**Day 3 - Morning**:
- [ ] Analyze existing Channel implementation
- [ ] Create migration plan
- [ ] Update Channel to extend YouTubeBaseSource

**Day 3 - Afternoon**:
- [ ] Migrate to shared YouTubeAPIClient
- [ ] Update channel-specific logic
- [ ] Run existing tests

**Day 4 - Morning**:
- [ ] Fix failing tests
- [ ] Add new integration tests
- [ ] Performance testing

**Day 4 - Afternoon**:
- [ ] Update CLI commands
- [ ] Update documentation
- [ ] Code review

**Deliverables**:
- ✅ Channel module using shared foundation
- ✅ All tests passing
- ✅ CLI commands working
- ✅ Documentation updated

---

### Phase 3: Search Module Implementation (Days 4-5)
**Focus**: Implement Search functionality

**Day 4 - Evening** (parallel with Channel testing):
- [ ] Create YouTubeSearchSource class
- [ ] Implement basic search functionality

**Day 5 - Morning**:
- [ ] Implement advanced filtering
- [ ] Add trending detection
- [ ] Unit tests for search logic

**Day 5 - Afternoon**:
- [ ] Integration tests
- [ ] CLI commands for search
- [ ] Documentation

**Deliverables**:
- ✅ Search module functional
- ✅ Tests passing
- ✅ CLI commands working
- ✅ Documentation complete

---

### Phase 4: Video Module Implementation (Days 5-6)
**Focus**: Implement Video details functionality

**Day 5 - Evening** (parallel with Search testing):
- [ ] Create YouTubeVideoSource class
- [ ] Implement single video details

**Day 6 - Morning**:
- [ ] Implement batch video retrieval
- [ ] Add related videos fetching
- [ ] Unit tests

**Day 6 - Afternoon**:
- [ ] Integration tests
- [ ] CLI commands
- [ ] Documentation

**Deliverables**:
- ✅ Video module functional
- ✅ Tests passing
- ✅ CLI commands working
- ✅ Documentation complete

---

### Phase 5: Integration & Polish (Days 6-7)
**Focus**: End-to-end testing and optimization

**Day 6 - Evening**:
- [ ] End-to-end integration testing
- [ ] Cross-module compatibility testing

**Day 7 - Morning**:
- [ ] Performance optimization
- [ ] Memory usage analysis
- [ ] API quota monitoring

**Day 7 - Afternoon**:
- [ ] Final documentation review
- [ ] Example scripts creation
- [ ] Code review and refactoring

**Deliverables**:
- ✅ All modules integrated
- ✅ Performance targets met
- ✅ Documentation complete
- ✅ Production-ready

---

## Team Coordination

### Role Assignments

| Developer | Primary Role | Module Focus | Days |
|-----------|-------------|--------------|------|
| Developer01 | Coordination | Overall planning, issue tracking | 7 |
| Developer02 | Backend Lead | Foundation (YouTubeBaseSource, APIClient) | 2 |
| Developer03 | Full-Stack | Channel module refactoring | 2 |
| Developer06 | Database | Schema integration, storage | 2 |
| Developer08 | Integration | Search & Video modules | 3 |
| Developer04 | Testing | Test coverage, integration tests | 7 |
| Developer09 | Documentation | All documentation and examples | 7 |
| Developer10 | Code Review | Architecture review, SOLID validation | 7 |

### Communication Protocol

**Daily Standups** (15 minutes, 9:00 AM):
- What was completed yesterday
- What will be done today
- Any blockers or dependencies

**Integration Points** (as needed):
- Developer02 → Developer03: Foundation → Channel integration
- Developer02 → Developer08: Foundation → Search/Video integration
- Developer06 → All: Schema coordination
- Developer04 → All: Test coordination

**Code Reviews**:
- All PRs require review from Developer10
- Foundation code requires review from Developer02
- Integration code requires cross-developer review

**Documentation Updates**:
- Developer09 tracks all documentation needs
- Each developer documents their own code
- Final documentation review by Developer09

---

## Quality Standards

### Code Quality

**SOLID Principles Validation**:
- ✅ Single Responsibility: Each class has one clear purpose
- ✅ Open/Closed: Extensions without modifications
- ✅ Liskov Substitution: All subclasses substitutable
- ✅ Interface Segregation: Focused interfaces
- ✅ Dependency Inversion: Abstract dependencies

**Code Review Checklist**:
- [ ] Follows SOLID principles
- [ ] Type hints on all functions
- [ ] Google-style docstrings
- [ ] Error handling comprehensive
- [ ] No code duplication (DRY)
- [ ] Appropriate use of shared components

### Testing Standards

**Coverage Requirements**:
- Unit tests: >80% coverage
- Integration tests: All major flows
- API mock tests: All API interactions
- Error scenario tests: All error paths

**Test Categories**:
1. **Unit Tests**:
   - Individual class/function tests
   - Mock external dependencies
   - Fast execution (<1s)

2. **Integration Tests**:
   - Multi-component interactions
   - Mock YouTube API
   - Medium execution (<10s)

3. **End-to-End Tests**:
   - Full workflow tests
   - Real API (rate limited)
   - Slow execution (>10s)

### Documentation Standards

**Required Documentation**:
- [ ] Architecture documentation (this document)
- [ ] API client documentation
- [ ] Integration guide per sub-module
- [ ] Example scripts
- [ ] Troubleshooting guide

**Documentation Format**:
- Markdown for all docs
- Code examples with output
- Diagrams for architecture
- Step-by-step guides

---

## Risk Management

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| YouTube API quota limits | High | High | Implement efficient batching, caching, quota monitoring |
| API changes/deprecation | Low | Medium | Use official client library, version pinning, monitoring |
| Rate limiting issues | Medium | Medium | Implement backoff, queue system, adaptive rate limiting |
| Large data volumes | Medium | High | Pagination, incremental fetching, memory optimization |
| Channel module breaking changes | Medium | High | Comprehensive testing, backward compatibility layer |
| Integration complexity | Medium | Medium | Clear interfaces, incremental integration, testing |

### Mitigation Strategies

**1. Quota Management**:
- Track API usage in real-time
- Implement request prioritization
- Cache frequently accessed data
- Use incremental updates

**2. Error Recovery**:
- Robust retry logic with exponential backoff
- Graceful degradation on API failures
- Comprehensive error logging
- Alert system for critical failures

**3. Performance Optimization**:
- Batch API requests efficiently
- Implement connection pooling
- Use async/await for parallel requests
- Monitor and optimize slow operations

**4. Testing Strategy**:
- Extensive mocking for API tests
- Separate rate-limited real API tests
- Continuous integration testing
- Performance regression tests

---

## Success Criteria

### Functional Requirements
- [ ] All YouTube sub-modules implemented
- [ ] Consistent interface across sub-modules
- [ ] Proper inheritance hierarchy (YouTubeBaseSource → BaseVideoSource)
- [ ] Shared code in YouTube/src/
- [ ] Rate limiting working correctly
- [ ] API quota management operational
- [ ] Error handling comprehensive
- [ ] Deduplication working

### Non-Functional Requirements
- [ ] API calls <500ms (p95)
- [ ] Batch processing efficient (50 videos <1s)
- [ ] Memory usage reasonable (<500MB for 1000 videos)
- [ ] Respects YouTube API quotas (10,000/day)
- [ ] Handles rate limits gracefully
- [ ] Concurrent request handling

### Testing Requirements
- [ ] Unit tests for all components (>80% coverage)
- [ ] Integration tests for each sub-module
- [ ] End-to-end tests for full pipeline
- [ ] API mock tests
- [ ] Error scenario tests
- [ ] Performance tests

### Documentation Requirements
- [ ] Architecture documentation (this file)
- [ ] API client documentation
- [ ] Integration guide for each sub-module
- [ ] Example scripts (at least 3)
- [ ] Troubleshooting guide
- [ ] API reference

---

## Performance Targets

### Response Time Targets
| Operation | Target | Max Acceptable |
|-----------|--------|----------------|
| Single video fetch | <500ms | <1s |
| Channel listing (50 videos) | <2s | <5s |
| Search (50 results) | <2s | <5s |
| Batch video details (50 videos) | <1s | <2s |

### Resource Targets
| Resource | Target | Max Acceptable |
|----------|--------|----------------|
| Memory usage (1000 videos) | <300MB | <500MB |
| API quota daily usage | <5,000 | <10,000 |
| Concurrent connections | 5-10 | 20 |

### Optimization Strategies
1. **Connection Pooling**: Reuse HTTP connections
2. **Request Batching**: Combine multiple requests
3. **Caching**: Cache channel metadata and video details
4. **Incremental Updates**: Only fetch new content
5. **Compression**: Use gzip for API responses

---

## Dependencies

### Upstream Dependencies (Blocks This)
- #001: Video Infrastructure Setup (BaseVideoSource)
- #002: CLI Integration (CLI framework)
- #003: Storage Schema Design (Database schema)

### Downstream Dependencies (This Blocks)
- Future video source integrations (TikTok, Instagram)
- Analytics features
- Content recommendation system
- Advanced trending detection

### External Dependencies
- YouTube Data API v3
- Python requests library
- Rate limiting libraries
- Testing frameworks (pytest)

---

## Integration Checklist

### Phase 1: Foundation (Days 1-2)
- [ ] Create YouTube/src/ directory structure
- [ ] Implement YouTubeBaseSource extending BaseVideoSource
- [ ] Implement YouTubeAPIClient with rate limiting
- [ ] Implement RateLimiter class
- [ ] Create YouTube-specific schemas
- [ ] Implement YouTubeMapper (YouTube → VideoMetadata)
- [ ] Unit tests for all foundation components (>80% coverage)
- [ ] Documentation for YouTube foundation
- [ ] Code review and approval

### Phase 2: Channel Module (Days 3-4)
- [ ] Analyze existing Channel implementation
- [ ] Refactor Channel to extend YouTubeBaseSource
- [ ] Migrate to shared YouTubeAPIClient
- [ ] Update channel-specific logic
- [ ] Maintain shorts filtering functionality
- [ ] Integration with storage schema
- [ ] Update unit tests for new structure
- [ ] Add integration tests
- [ ] Update CLI commands
- [ ] Update documentation
- [ ] Code review and approval

### Phase 3: Search Module (Days 4-5)
- [ ] Implement YouTubeSearchSource extending YouTubeBaseSource
- [ ] Implement keyword search functionality
- [ ] Implement advanced filtering
- [ ] Add trending detection
- [ ] Integration with storage schema
- [ ] Unit tests for search logic
- [ ] Integration tests
- [ ] CLI commands for search operations
- [ ] Documentation
- [ ] Code review and approval

### Phase 4: Video Module (Days 5-6)
- [ ] Implement YouTubeVideoSource extending YouTubeBaseSource
- [ ] Implement single video details
- [ ] Implement batch video retrieval
- [ ] Add related videos fetching
- [ ] Integration with storage schema
- [ ] Unit tests
- [ ] Integration tests
- [ ] CLI commands
- [ ] Documentation
- [ ] Code review and approval

### Phase 5: Integration & Polish (Days 6-7)
- [ ] End-to-end integration testing
- [ ] Cross-module compatibility testing
- [ ] Performance optimization
- [ ] Memory usage analysis
- [ ] API quota monitoring implementation
- [ ] Documentation completion
- [ ] Example scripts (minimum 3)
- [ ] Troubleshooting guide
- [ ] Final code review and refactoring
- [ ] Production deployment checklist

---

## Definition of Done

A phase is considered "Done" when:

1. **Code Complete**:
   - All planned features implemented
   - Code follows SOLID principles
   - No critical bugs or issues
   - Code reviewed and approved

2. **Tests Passing**:
   - All unit tests passing
   - All integration tests passing
   - Coverage >80%
   - Performance tests meeting targets

3. **Documentation Complete**:
   - Code documented (docstrings)
   - API documentation updated
   - User guides updated
   - Examples provided

4. **Review Approved**:
   - Code review passed (Developer10)
   - Architecture review passed
   - Security review passed (if applicable)
   - SOLID validation passed

5. **Integration Verified**:
   - Works with other modules
   - CLI commands functional
   - Storage integration working
   - No breaking changes

---

## Next Steps After Completion

### Immediate (Week 8)
1. Monitor YouTube integration performance
2. Collect production metrics
3. Address any production issues
4. Optimize based on real-world usage

### Short-term (Weeks 9-12)
1. Plan TikTok integration (similar pattern)
2. Plan Instagram integration
3. Implement advanced caching
4. Add analytics features

### Long-term (Months 4-6)
1. Advanced trending detection
2. Content recommendation system
3. Multi-platform aggregation
4. Machine learning integration

---

## Related Documents

- [Issue #004: YouTube Integration Planning](../issues/new/Developer01/004-youtube-integration-planning.md)
- [Video Infrastructure Setup](../../_meta/issues/new/Developer01/001-video-infrastructure-setup.md)
- [CLI Integration](../../_meta/issues/new/Developer01/002-cli-integration.md)
- [Source Module Coordination Plan](../../../../_meta/issues/new/Developer01/SOURCE-MODULE-COORDINATION-PLAN.md)
- [YouTube Architecture](./ARCHITECTURE.md)
- [YouTube Configuration](./CONFIGURATION.md)

---

## Appendix A: API Quota Management

### YouTube API Quota Limits
- **Daily Quota**: 10,000 units
- **Search Query**: 100 units
- **Video Details**: 1 unit per video
- **Channel Details**: 1 unit per channel

### Quota Optimization Strategies
1. **Batch Requests**: Get 50 videos in 1 request instead of 50
2. **Caching**: Cache channel and video metadata
3. **Incremental Updates**: Only fetch new content
4. **Priority Queuing**: Prioritize high-value requests

### Quota Monitoring
- Track usage in real-time
- Alert when approaching limits (80%)
- Implement quota-aware scheduling
- Fallback to cached data when quota exhausted

---

## Appendix B: Error Handling Strategy

### Error Categories
1. **API Errors**: YouTube API failures
2. **Rate Limit Errors**: Too many requests
3. **Quota Errors**: Daily quota exceeded
4. **Network Errors**: Connection issues
5. **Data Errors**: Invalid response format

### Error Handling Approach
```python
try:
    # API call
except YouTubeAPIError as e:
    # Handle API-specific errors
    logger.error(f"API error: {e}")
    # Retry with backoff
except RateLimitError as e:
    # Handle rate limiting
    logger.warning(f"Rate limited: {e}")
    # Wait and retry
except QuotaExceededError as e:
    # Handle quota exhaustion
    logger.error(f"Quota exceeded: {e}")
    # Use cached data or fail gracefully
```

---

## Appendix C: Example Usage

### Example 1: Fetch Channel Videos
```python
from youtube.src.base.youtube_channel_source import YouTubeChannelSource

config = {
    'api_key': 'YOUR_API_KEY',
    'rate_limit': 100
}

channel_source = YouTubeChannelSource(config)
videos = channel_source.fetch_videos(
    channel_id='UC_x5XG1OV2P6uZZ5FSM9Ttw',
    limit=50,
    filters={'video_type': 'shorts'}
)

for video in videos:
    print(f"{video['title']} - {video['view_count']} views")
```

### Example 2: Search Videos
```python
from youtube.src.search.youtube_search_source import YouTubeSearchSource

config = {
    'api_key': 'YOUR_API_KEY',
    'rate_limit': 100
}

search_source = YouTubeSearchSource(config)
results = search_source.fetch_videos(
    query='AI tutorials',
    limit=10,
    filters={
        'order': 'viewCount',
        'published_after': '2024-01-01T00:00:00Z',
        'video_duration': 'short'
    }
)

for video in results:
    print(f"{video['title']} by {video['channel_name']}")
```

### Example 3: Get Video Details
```python
from youtube.src.video.youtube_video_source import YouTubeVideoSource

config = {
    'api_key': 'YOUR_API_KEY',
    'rate_limit': 100
}

video_source = YouTubeVideoSource(config)
videos = video_source.get_video_details(
    video_ids=['dQw4w9WgXcQ', 'jNQXAC9IVRw'],
    include_related=True
)

for video in videos:
    print(f"{video['title']}")
    print(f"Duration: {video['duration']}s")
    print(f"Views: {video['view_count']}")
    print(f"Related: {len(video.get('related_videos', []))}")
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-12  
**Next Review**: 2025-11-19  
**Status**: 🟢 Active Planning
