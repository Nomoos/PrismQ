# PrismQ.IdeaInspiration.Sources

A comprehensive, modular library for collecting and managing various types of content sources for the PrismQ idea generation ecosystem. Each source module implements a **dual-save architecture** that maintains both domain-specific data and contributes to a unified central database.

## Overview

This library provides specialized source modules for collecting inspiration from diverse platforms and data sources. Each source:
- Implements a plugin-based architecture for data collection
- Returns standardized `IdeaInspiration` domain objects
- Saves to both source-specific tables (detailed metadata) AND a central database (unified queries)
- Follows SOLID principles for clean, maintainable code

## Architecture: Dual-Save Pattern

### Database Strategy

Each source implements a **dual-save pattern** for optimal data management:

```
┌────────────────────────┐
│   Source Plugin        │
│   (e.g., Genius API)   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  IdeaInspiration       │
│  (Domain Object)       │
└───────┬───────┬────────┘
        │       │
        │       │
   ┌────▼──┐ ┌─▼─────────┐
   │ Source│ │  Central  │
   │ DB    │ │  DB       │
   │       │ │           │
   │Detail │ │ Unified   │
   │Metadata│ │ Queries   │
   └───────┘ └───────────┘
```

**Benefits:**
1. **Domain-Specific Storage**: Preserve platform-specific metadata (e.g., YouTube view counts, Genius pageviews)
2. **Unified Access**: Query all sources together via central `IdeaInspiration` table
3. **Analytics**: Cross-source analysis and comparison
4. **Flexibility**: Sources evolve independently without breaking unified interface

### Source Module Structure

Each source follows this standard structure:

```
SourceName/
├── src/
│   ├── cli.py              # Command-line interface
│   ├── core/
│   │   ├── config.py       # Configuration management
│   │   ├── database.py     # Source-specific database
│   │   └── metrics.py      # Platform metrics conversion
│   └── plugins/
│       └── *_plugin.py     # Data collection implementations
├── tests/
│   └── test_*.py           # Comprehensive tests
├── README.md               # Source-specific documentation
├── requirements.txt        # Dependencies
└── pyproject.toml          # Python project config
```

## Source Categories & Implementations

### ✅ Implemented Sources

Sources with dual-save architecture in place:

| Category | Source | Status | Database Tables |
|----------|--------|--------|-----------------|
| **Creative** | LyricSnippets | ✅ Dual-Save | `lyric_snippets` + `IdeaInspiration` |
| **Signals** | GoogleTrends | ✅ Dual-Save | `signals` + `IdeaInspiration` |
| **Events** | CalendarHolidays | ✅ Dual-Save | `events` + `IdeaInspiration` |

### 🚧 Implementation In Progress

Sources ready for dual-save migration:

| Category | Source | Priority | Notes |
|----------|--------|----------|-------|
| **Creative** | ScriptBeats | High | Narrative structure data |
| **Creative** | VisualMoodboard | High | Visual inspiration data |
| **Events** | SportsHighlights | Medium | Sports event data |
| **Events** | EntertainmentReleases | Medium | Movie/music release data |
| **Signals** | NewsApi | Medium | News signal data |
| **Signals** | GoogleNews | Medium | News trend data |
| **Signals** | SocialChallenge | Medium | Viral challenge data |
| **Signals** | GeoLocalTrends | Low | Location-based trends |

## Complete Source Taxonomy

## Complete Source Taxonomy

Current repository structure organized by category:

```
Sources/
├── Creative/                  # Creative inspiration sources
│   ├── LyricSnippets/        # ✅ Song lyrics (Genius API)
│   ├── ScriptBeats/          # 🚧 Narrative structures
│   └── VisualMoodboard/      # 🚧 Visual aesthetics
│
├── Signals/                   # Early trend indicators
│   ├── Trends/
│   │   └── GoogleTrends/     # ✅ Search trends
│   ├── News/
│   │   ├── GoogleNews/       # 🚧 News aggregation
│   │   └── NewsApi/          # 🚧 News API
│   ├── Challenges/
│   │   └── SocialChallenge/  # 🚧 Viral challenges
│   └── Locations/
│       └── GeoLocalTrends/   # 🚧 Location trends
│
├── Events/                    # Scheduled & recurring events
│   ├── CalendarHolidays/     # ✅ Holidays & observances
│   ├── SportsHighlights/     # 🚧 Sports events
│   └── EntertainmentReleases/# 🚧 Movie/music releases
│
├── Content/                   # Rich content sources
│   ├── Shorts/
│   │   ├── YouTube/          # YouTube Shorts
│   │   ├── TikTok/           # TikTok videos
│   │   └── InstagramReels/   # Instagram Reels
│   ├── Articles/
│   │   ├── Medium/           # Medium articles
│   │   └── WebArticles/      # General web articles
│   ├── Podcasts/
│   │   ├── ApplePodcasts/    # Apple Podcasts
│   │   └── SpotifyPodcasts/  # Spotify Podcasts
│   ├── Forums/
│   │   ├── Reddit/           # Reddit posts/comments
│   │   └── HackerNews/       # HN discussions
│   └── Streams/
│       └── KickClips/        # Kick streaming clips
│
├── Commerce/                  # Product & marketplace trends
│   ├── AmazonBestsellers/    # Amazon bestsellers
│   ├── EtsyTrending/         # Etsy trending items
│   └── AppStoreTopCharts/    # App store rankings
│
├── Community/                 # Audience feedback
│   ├── CommentMiningSource/  # Platform comments
│   ├── UserFeedbackSource/   # Channel feedback
│   ├── QASource/             # Q&A platforms
│   └── PromptBoxSource/      # User prompts
│
└── Internal/                  # Internal sources
    ├── ManualBacklog/        # Manual entries
    └── CSVImport/            # CSV imports

Legend: ✅ Dual-save implemented | 🚧 Ready for migration | ⚪ Planned
```

## Quick Start

### Using an Existing Source

```bash
# Example: LyricSnippets source
cd Sources/Creative/LyricSnippets

# Install dependencies
pip install -r requirements.txt

# Configure (copy .env.example to .env and set API keys)
cp .env.example .env
# Edit .env with your Genius API key

# Run the scraper
python -m src.cli scrape --query "trending songs" --max-results 10
```

### Implementing Dual-Save in a New Source

See the **Migration Guide** section below for step-by-step instructions.

## Key Concepts

### IdeaInspiration Domain Model

All sources return `IdeaInspiration` objects from the Model module:

```python
from idea_inspiration import IdeaInspiration

# Factory methods for different content types
idea = IdeaInspiration.from_text(
    title="Article Title",
    description="Brief description",
    text_content="Full text content",
    keywords=["keyword1", "keyword2"],
    metadata={"platform_specific": "data"},
    source_id="unique-id",
    source_url="https://...",
    source_created_by="Creator Name"
)

# Also available:
# IdeaInspiration.from_video(...)
# IdeaInspiration.from_audio(...)
```

### Dual-Save Implementation

Each source saves data twice:

1. **Source-Specific Database**: Detailed platform metadata
   ```python
   db.insert_resource(
       source='genius',
       source_id=idea.source_id,
       title=idea.title,
       content=idea.content,
       pageviews=metadata['pageviews'],  # Platform-specific
       # ... other source-specific fields
   )
   ```

2. **Central Database**: Normalized IdeaInspiration
   ```python
   central_db.insert(idea)  # Unified access across all sources
   ```

### Benefits by Category

**Creative Sources** (Lyrics, Scripts, Visuals)
- Store platform-specific metrics (pageviews, engagement)
- Unified creative inspiration queries
- Cross-source creative analytics

**Signal Sources** (Trends, News, Challenges)
- Store temporal data (trend velocity, peaks)
- Unified trend analysis across platforms
- Early signal detection

**Event Sources** (Holidays, Sports, Entertainment)
- Store event-specific data (dates, recurrence patterns)
- Unified event calendar
- Content opportunity planning

**Content Sources** (Videos, Articles, Podcasts)
- Store engagement metrics (views, likes, comments)
- Unified content discovery
- Performance benchmarking

## Migration Guide

### Adding Dual-Save to an Existing Source

Follow these steps to migrate a source to the dual-save pattern:

**Step 1: Import Central Database**
```python
# In src/cli.py
import sys
from pathlib import Path

# Import central database utilities
model_path = Path(__file__).resolve().parents[4] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path
```

**Step 2: Initialize Both Databases**
```python
# Initialize source-specific database
db = Database(config.database_path, interactive=not no_interactive)

# Initialize central database
central_db_path = get_central_database_path()
central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
```

**Step 3: Implement Dual-Save**
```python
for idea in ideas:
    # Save to source-specific database
    source_saved = db.insert_resource(
        source='your_source',
        source_id=idea.source_id,
        # ... source-specific fields
    )
    
    # Save to central database
    central_saved = central_db.insert(idea)
```

**Step 4: Update CLI Output**
```python
click.echo(f"\nScraping complete!")
click.echo(f"Saved to source database: {total_saved_source}")
click.echo(f"Saved to central database: {total_saved_central}")
click.echo(f"Source database: {config.database_path}")
click.echo(f"Central database: {central_db_path}")
```

See implemented examples:
- `Sources/Creative/LyricSnippets/src/cli.py`
- `Sources/Signals/Trends/GoogleTrends/src/cli.py`
- `Sources/Events/CalendarHolidays/src/cli.py`

## Testing Strategy

Each source should include:

1. **Unit Tests**: Test plugin logic independently
2. **Integration Tests**: Test dual-save functionality
3. **Database Tests**: Verify both databases receive data

```python
# Example integration test
def test_dual_save():
    source_db = SourceDatabase(":memory:")
    central_db = IdeaInspirationDatabase(":memory:")
    
    ideas = plugin.scrape()
    
    for idea in ideas:
        source_db.insert_resource(...)
        central_db.insert(idea)
    
    # Verify both databases
    assert source_db.count() == len(ideas)
    assert central_db.count() == len(ideas)
```

## Documentation

### Core Documentation
- **[DATABASE_INTEGRATION.md](../_meta/docs/DATABASE_INTEGRATION.md)**: Complete dual-save architecture guide
- **[DATABASE_INTEGRATION_SUMMARY.md](../_meta/docs/DATABASE_INTEGRATION_SUMMARY.md)**: Executive summary

### Strategic Planning
Future enhancements documented in `_meta/issues/backlog/`:
- **Issue #500**: Repository Pattern Implementation
- **Issue #501**: Unit of Work Pattern (transaction management)
- **Issue #502**: SQLAlchemy ORM Layer
- **Issue #503**: Builder Module Implementation (transform layer)
- **Issue #504**: Extended Model Schema (Classification/Scoring tables)

### Source-Specific Docs
Each source has its own README with:
- Platform-specific setup instructions
- API key configuration
- Data points captured
- Usage examples

## Architecture Principles

This library follows SOLID principles:

- **Single Responsibility**: Each source handles one platform/data type
- **Open/Closed**: Easy to add new sources without modifying existing code
- **Liskov Substitution**: All sources return IdeaInspiration objects
- **Interface Segregation**: Minimal, focused plugin interfaces
- **Dependency Inversion**: Sources depend on IdeaInspiration abstraction

Additional principles:
- **DRY**: Shared utilities in Model module
- **KISS**: Simple, understandable implementations
- **YAGNI**: Implement what's needed now

## Related Modules

| Module | Purpose | Link |
|--------|---------|------|
| **Model** | IdeaInspiration domain model & central database | `../Model/` |
| **Classification** | Content categorization | `../Classification/` |
| **Scoring** | Content quality evaluation | `../Scoring/` |
| **Client** | Web-based control panel | `../Client/` |

## Performance Considerations

Optimized for target platform:
- **OS**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen
- **RAM**: 64GB DDR5

Best practices:
- Batch operations for database inserts
- Connection pooling where supported
- Async operations for I/O-bound tasks
- GPU utilization for ML-based features (future)

## Contributing

### Adding a New Source

1. **Choose a category** (Creative, Signals, Events, Content, Commerce, Community, Internal)
2. **Create source structure**:
   ```bash
   mkdir -p Sources/CategoryName/SourceName/{src/{core,plugins},tests}
   ```
3. **Implement plugin** that returns `IdeaInspiration` objects
4. **Add CLI** with dual-save pattern
5. **Write tests** (unit + integration)
6. **Document** in source-specific README

### Code Quality Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Write comprehensive docstrings (Google style)
- Achieve >80% test coverage
- Pass all linters (flake8, mypy)

### Pull Request Checklist

- [ ] Plugin returns `IdeaInspiration` objects
- [ ] Dual-save implemented (source DB + central DB)
- [ ] Tests pass (unit + integration)
- [ ] Documentation updated
- [ ] Example usage provided
- [ ] Security scan passes (CodeQL)

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Dual-save architecture implemented
- ✅ 3 reference implementations (LyricSnippets, GoogleTrends, CalendarHolidays)
- ✅ Comprehensive documentation

### Phase 2: Source Migration (Q4 2025)
- Migrate remaining Creative sources (2)
- Migrate remaining Signal sources (6+)
- Migrate remaining Event sources (2)
- Add Commerce sources (3)

### Phase 3: Content Sources (Q1 2026)
- YouTube Shorts integration
- TikTok API integration
- Reddit data collection
- Article scraping (Medium, web)

### Phase 4: Advanced Features (Q2 2026)
- Repository Pattern (Issue #500)
- Unit of Work Pattern (Issue #501)
- Builder Module (Issue #503)
- SQLAlchemy ORM Layer (Issue #502)

### Phase 5: Analytics & ML (Q3 2026)
- Extended schema with Classification/Scoring tables (Issue #504)
- Cross-source analytics
- ML-based trend detection
- Predictive content opportunity scoring

## License

All Rights Reserved - Part of the PrismQ Ecosystem

## Contact & Support

- **Issues**: Open an issue in this repository
- **Documentation**: See `_meta/docs/` for detailed guides
- **Examples**: Check implemented sources for reference patterns

---

**Status**: ✅ Production Ready (Dual-Save Architecture)
**Version**: 1.0.0
**Last Updated**: October 2025
