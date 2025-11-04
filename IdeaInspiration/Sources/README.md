# PrismQ.IdeaInspiration.Sources

A comprehensive, modular library for collecting and managing various types of content sources for the PrismQ idea generation ecosystem. Each source module uses a **single database architecture** that stores all data in a unified central database.

## Overview

This library provides specialized source modules for collecting inspiration from diverse platforms and data sources. Each source:
- Implements a plugin-based architecture for data collection
- Returns standardized `IdeaInspiration` domain objects
- Saves to a single central database with `source_platform` field for identification
- Follows SOLID principles for clean, maintainable code

## Architecture: Single Database Pattern

### Database Strategy

All sources use a **single database pattern** for simplified data management:

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
│  source_platform="genius"
└───────────┬────────────┘
            │
            ▼
   ┌────────────────────┐
   │   Central DB       │
   │                    │
   │  - All sources     │
   │  - Unified queries │
   │  - Platform field  │
   └────────────────────┘
```

**Benefits:**
1. **Simplified Architecture**: Single database to maintain and backup
2. **Unified Access**: Query all sources together via central `IdeaInspiration` table
3. **Platform Identification**: Use `source_platform` field to filter by source (e.g., "youtube", "google_trends", "genius")
4. **Metadata Storage**: Platform-specific data preserved in `metadata` dictionary field
5. **No Data Duplication**: Single source of truth for all content ideas

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

All sources now use the single database architecture:

| Category | Source | Status | Platform ID |
|----------|--------|--------|-------------|
| **Creative** | LyricSnippets | ✅ Migrated | `lyric_snippets` |
| **Creative** | ScriptBeats | ✅ Migrated | `script_beats` |
| **Creative** | VisualMoodboard | ✅ Migrated | `visual_moodboard` |
| **Signals** | GoogleTrends | ✅ Migrated | `google_trends` |
| **Signals** | NewsApi | ✅ Migrated | `news_api` |
| **Signals** | TikTokHashtag | ✅ Migrated | `tiktok_hashtag` |
| **Signals** | InstagramHashtag | ✅ Migrated | `instagram_hashtag` |
| **Signals** | MemeTracker | ✅ Migrated | `meme_tracker` |
| **Signals** | SocialChallenge | ✅ Migrated | `social_challenge` |
| **Signals** | GeoLocalTrends | ✅ Migrated | `geo_local_trends` |
| **Signals** | TikTokSounds | ✅ Migrated | `tiktok_sounds` |
| **Signals** | InstagramAudioTrends | ✅ Migrated | `instagram_audio_trends` |
| **Events** | CalendarHolidays | ✅ Migrated | `calendar_holidays` |
| **Events** | SportsHighlights | ✅ Migrated | `sports_highlights` |
| **Events** | EntertainmentReleases | ✅ Migrated | `entertainment_releases` |
| **Commerce** | AmazonBestsellers | ✅ Migrated | `amazon_bestsellers` |
| **Commerce** | AppStoreTopCharts | ✅ Migrated | `app_store_top_charts` |
| **Commerce** | EtsyTrending | ✅ Migrated | `etsy_trending` |
| **Community** | QASource | ✅ Migrated | `qa_source` |
| **Community** | PromptBoxSource | ✅ Migrated | `prompt_box` |
| **Community** | CommentMiningSource | ✅ Migrated | `comment_mining` |
| **Community** | UserFeedbackSource | ✅ Migrated | `user_feedback` |
| **Internal** | CSVImport | ✅ Migrated | `csv_import` |
| **Internal** | ManualBacklog | ✅ Migrated | `manual_backlog` |

**Migration Completed**: November 1, 2025 (24/24 sources)

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

Legend: ✅ Single DB (all sources migrated as of Nov 1, 2025)
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

### Creating a New Source

All new sources should follow the single database pattern. See examples in existing source modules.

## Key Concepts

### IdeaInspiration Domain Model

All sources return `IdeaInspiration` objects from the Model module with `source_platform` field:

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
    source_created_by="Creator Name",
    source_platform="your_platform_id"  # e.g., "genius", "youtube", "google_trends"
)

# Also available:
# IdeaInspiration.from_video(..., source_platform="youtube")
# IdeaInspiration.from_audio(..., source_platform="spotify")
```

### Single Database Implementation

All sources now save data to a single central database:

```python
from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path

# Initialize central database
central_db = IdeaInspirationDatabase(get_central_database_path())

# Save IdeaInspiration with source_platform
for idea in ideas:
    central_db.insert(idea)  # Platform identified by source_platform field
```

### Querying by Source

```python
# Query specific source
youtube_ideas = db.get_all(source_platform="youtube")
trends = db.get_all(source_platform="google_trends")

# Count by platform
youtube_count = db.count(source_platform="youtube")
```

### Benefits by Category

**Creative Sources** (Lyrics, Scripts, Visuals)
- Platform-specific metrics stored in `metadata` field
- Unified creative inspiration queries
- Cross-source creative analytics

**Signal Sources** (Trends, News, Challenges)
- Temporal data in `metadata` (trend velocity, peaks)
- Unified trend analysis across platforms
- Early signal detection

**Event Sources** (Holidays, Sports, Entertainment)
- Event-specific data in `metadata` (dates, recurrence patterns)
- Unified event calendar
- Content opportunity planning

**Content Sources** (Videos, Articles, Podcasts)
- Engagement metrics in `metadata` (views, likes, comments)
- Unified content discovery
- Performance benchmarking

## Implementation Guide

### Creating a Source with Single Database

All sources use the single database pattern:

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

**Step 2: Initialize Central Database**
```python
# Initialize central database only
central_db_path = get_central_database_path()
central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
```

**Step 3: Save to Single Database**
```python
for idea in ideas:
    # Save to central database with source_platform field
    central_db.insert(idea)
```

**Step 4: Update CLI Output**
```python
click.echo(f"\nScraping complete!")
click.echo(f"Saved to source database: {total_saved_source}")
click.echo(f"Saved to central database: {total_saved_central}")
click.echo(f"Source database: {config.database_path}")
click.echo(f"Central database: {central_db_path}")
```

**Step 4: Update CLI Output**
```python
click.echo(f"\nScraping complete!")
click.echo(f"Saved to central database: {total_saved}")
click.echo(f"Central database: {central_db_path}")
```

See implemented examples:
- `Sources/Creative/LyricSnippets/src/cli.py`
- `Sources/Signals/Trends/GoogleTrends/src/cli.py`
- `Sources/Events/CalendarHolidays/src/cli.py`

## Testing Strategy

Each source should include:

1. **Unit Tests**: Test plugin logic independently
2. **Integration Tests**: Test database save functionality
3. **Query Tests**: Verify source_platform filtering

```python
# Example integration test
def test_single_db_save():
    central_db = IdeaInspirationDatabase(":memory:")
    
    ideas = plugin.scrape()
    
    for idea in ideas:
        central_db.insert(idea)
    
    # Verify database
    assert central_db.count() == len(ideas)
    
    # Verify platform filtering
    platform_ideas = central_db.get_all(source_platform="your_platform")
    assert len(platform_ideas) == len(ideas)
```

## Documentation

### Core Documentation
- **[SINGLE_DB_MIGRATION_COMPLETE.md](../_meta/docs/SINGLE_DB_MIGRATION_COMPLETE.md)**: Migration completion summary
- **[SINGLE_DB_IMPLEMENTATION_SUMMARY.md](../_meta/docs/SINGLE_DB_IMPLEMENTATION_SUMMARY.md)**: Implementation details

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
3. **Implement plugin** that returns `IdeaInspiration` objects with `source_platform` field
4. **Add CLI** using single database pattern
5. **Write tests** (unit + integration)
6. **Document** in source-specific README

### Code Quality Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Write comprehensive docstrings (Google style)
- Achieve >80% test coverage
- Pass all linters (flake8, mypy)

### Pull Request Checklist

- [ ] Plugin returns `IdeaInspiration` objects with `source_platform` field
- [ ] Single database implementation (central DB only)
- [ ] Tests pass (unit + integration)
- [ ] Documentation updated
- [ ] Example usage provided
- [ ] Security scan passes (CodeQL)

## Roadmap

### ✅ Phase 1: Single Database Migration (Completed November 2025)
- ✅ Single database architecture implemented
- ✅ All 24 sources migrated successfully
- ✅ Comprehensive documentation and migration guides
- ✅ Testing and validation complete

### Phase 2: Content Sources (Q1 2026)
- YouTube Shorts integration
- TikTok API integration
- Reddit data collection
- Article scraping (Medium, web)

### Phase 3: Advanced Features (Q2 2026)
- Repository Pattern (Issue #500)
- Unit of Work Pattern (Issue #501)
- Builder Module (Issue #503)
- SQLAlchemy ORM Layer (Issue #502)

### Phase 4: Analytics & ML (Q3 2026)
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

**Status**: ✅ Production Ready (Single Database Architecture)
**Version**: 2.0.0
**Last Updated**: November 2025
