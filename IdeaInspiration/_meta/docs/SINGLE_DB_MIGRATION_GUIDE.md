# Single DB Migration Guide for Source Modules

**Date**: October 31, 2025  
**Related Issue**: `implement_single_db_source_modules.md`  
**Status**: In Progress (4/23 Complete)

## Migration Status

### ✅ Completed (4/23)
- Creative/LyricSnippets
- Creative/ScriptBeats
- Signals/Trends/GoogleTrends
- Events/CalendarHolidays

### 🔄 Remaining (19/23)
- Creative/VisualMoodboard
- Signals/News/NewsApi
- Signals/Hashtags/TikTokHashtag
- Signals/Hashtags/InstagramHashtag
- Signals/Memes/MemeTracker
- Signals/Challenges/SocialChallenge
- Signals/Locations/GeoLocalTrends
- Signals/Sounds/TikTokSounds
- Events/SportsHighlights
- Events/EntertainmentReleases
- Commerce/AmazonBestsellers
- Commerce/AppStoreTopCharts
- Commerce/EtsyTrending
- Community/QASource
- Community/PromptBoxSource
- Community/CommentMiningSource
- Community/UserFeedbackSource
- Internal/CSVImport
- Internal/ManualBacklog

## Overview

This guide explains how to migrate Source modules from the dual-save pattern to the single DB approach, where all sources save IdeaInspiration objects to a central database with proper `source_platform` identification.

## Background

### Previous Approach (Dual-Save)
- Sources maintained their own specialized databases (e.g., `lyric_snippets`, `signals`, `events`)
- Sources also saved to central IdeaInspiration database
- This created data duplication and complexity

### New Approach (Single DB)
- Sources save **only** to the central IdeaInspiration database
- Each IdeaInspiration has a `source_platform` field identifying its origin
- Platform-specific data goes in the `metadata` dictionary
- Simpler architecture, easier querying across sources

## Prerequisites

### Model Changes (Already Complete ✅)

The Model has been updated with:
1. `source_platform` field in IdeaInspiration dataclass
2. `source_platform` column in database schema (with migration for existing DBs)
3. `source_platform` parameter in factory methods (`from_text`, `from_video`, `from_audio`)
4. Database filtering by `source_platform`
5. Index on `source_platform` for efficient queries

## Reference Implementation

**ScriptBeats** is a complete reference implementation showing all migration steps. Use it as a template for migrating other sources.

Location: `Sources/Creative/ScriptBeats/`

Key files:
- `src/plugins/__init__.py` - Shows IdeaInspiration import pattern
- `src/plugins/template_plugin.py` - Shows IdeaInspiration creation
- `src/cli.py` - Shows central database usage

## Migration Steps for Each Source

### Step 1: Update Plugin Base Class (`plugins/__init__.py`)

Add IdeaInspiration import and update return type:

**Before:**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SourcePlugin(ABC):
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        pass
```

**After:**
```python
from abc import ABC, abstractmethod
from typing import List
import sys
from pathlib import Path

# Add Model directory to path
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration

class SourcePlugin(ABC):
    @abstractmethod
    def scrape(self) -> List[IdeaInspiration]:
        pass
```

### Step 2: Update Plugin to Set source_platform

In your plugin's `scrape()` method, add `source_platform` parameter when creating IdeaInspiration objects:

**Before:**
```python
idea = IdeaInspiration.from_text(
    title=article['title'],
    description=article['description'],
    text_content=article['content'],
    keywords=keywords,
    metadata=metadata,
    source_id=article['id'],
    source_url=article['url']
)
```

**After:**
```python
idea = IdeaInspiration.from_text(
    title=article['title'],
    description=article['description'],
    text_content=article['content'],
    keywords=keywords,
    metadata=metadata,
    source_id=article['id'],
    source_url=article['url'],
    source_platform="news_api",  # ⬅️ ADD THIS
    source_created_by=article['author'],
    source_created_at=article['publishedAt']
)
```

### Step 2: Update CLI to Remove Dual-Save

Remove source-specific database saves and keep only central database.

**Before:**
```python
# Initialize databases (source-specific AND central)
db = Database(config.database_path, interactive=not no_interactive)
central_db_path = get_central_database_path()
central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)

# ... scraping logic ...

for idea in ideas:
    # Save to source-specific database
    source_saved = db.insert_resource(
        source='news_api',
        source_id=idea.source_id,
        title=idea.title,
        # ... many fields ...
    )
    
    # Save to central database (DUAL-SAVE)
    central_saved = central_db.insert(idea)
```

**After:**
```python
# Initialize central database only (single DB approach)
central_db_path = get_central_database_path()
central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)

# ... scraping logic ...

for idea in ideas:
    # Save to central database (single DB)
    central_saved = central_db.insert(idea)
```

### Step 3: Remove Unused Imports

Remove imports that are no longer needed:

**Before:**
```python
from .core.database import Database
from .core.metrics import CreativeMetrics  # or UniversalMetrics, etc.
from .core.processors import SomeProcessor
```

**After:**
```python
# Remove unused imports - only keep what's needed
```

### Step 4: Update Status Reporting

Update the CLI output to reflect single DB:

**Before:**
```python
click.echo(f"Saved to source database: {total_saved_source}")
click.echo(f"Saved to central database: {total_saved_central}")
click.echo(f"Source database: {config.database_path}")
click.echo(f"Central database: {central_db_path}")
```

**After:**
```python
click.echo(f"Saved to central database: {total_saved_central}")
click.echo(f"Central database: {central_db_path}")
```

## Source Platform Naming Convention

Use lowercase with underscores, matching the source name:

| Source Module | source_platform Value |
|--------------|----------------------|
| LyricSnippets | `"genius"` |
| GoogleTrends | `"google_trends"` |
| CalendarHolidays | `"calendar_holidays"` |
| NewsApi | `"news_api"` |
| GoogleNews | `"google_news"` |
| TikTokHashtag | `"tiktok_hashtag"` |
| InstagramHashtag | `"instagram_hashtag"` |
| YouTubeShorts | `"youtube_shorts"` |
| InstagramReels | `"instagram_reels"` |
| TikTok | `"tiktok"` |

## Metadata Guidelines

Platform-specific data should go in the `metadata` dictionary with **string values** (SQLite compatibility):

```python
metadata = {
    'views': str(video['views']),
    'likes': str(video['likes']),
    'duration_seconds': str(video['duration']),
    'audience_geography': 'US:50%,UK:20%,CA:15%',
    'hashtags': ','.join(video['hashtags']),
    'engagement_rate': str(video['engagement_rate'])
}
```

## Examples

### Example 1: Creative Source (LyricSnippets)

**Plugin Change:**
```python
idea = IdeaInspiration.from_text(
    title=f"{song['title']} - {artist_name}",
    description=f"Lyric snippet from {artist_name}",
    text_content=lyric_snippet,
    keywords=tags,
    metadata={
        'song_id': str(song_id),
        'artist_id': str(artist['id']),
        'artist_name': artist_name,
        'pageviews': str(song['pageviews']),
        'language': song['language']
    },
    source_id=str(song_id),
    source_url=song['url'],
    source_platform="genius",  # ✅
    source_created_by=artist_name
)
```

**CLI Change:**
```python
# Before: Initialize both databases
# db = Database(config.database_path)
# central_db = IdeaInspirationDatabase(central_db_path)

# After: Initialize only central database
central_db = IdeaInspirationDatabase(get_central_database_path())

# Save only to central
for idea in ideas:
    central_db.insert(idea)
```

### Example 2: Signal Source (GoogleTrends)

**Plugin Change:**
```python
idea = IdeaInspiration.from_text(
    title=query,
    description=f"Trending search query in {region}",
    text_content=f"Search trend: {query}",
    keywords=tags,
    metadata={
        'region': region,
        'rank': str(idx + 1),
        'volume_estimate': str(volume),
        'signal_type': 'trend',
        'current_status': 'rising'
    },
    source_id=f"{query}_{region}_{timestamp}",
    source_url=f"https://trends.google.com/trends/explore?q={query}&geo={region}",
    source_platform="google_trends",  # ✅
    source_created_by="Google Trends"
)
```

### Example 3: Event Source (CalendarHolidays)

**CLI Change (when IdeaInspiration created in CLI):**
```python
idea = IdeaInspiration.from_text(
    title=holiday_data['name'],
    description=f"{holiday_data['type']} event in {country_code}",
    text_content=event_description,
    keywords=[holiday_data['type'], country_code, 'holiday'],
    metadata={
        'event_type': holiday_data['type'],
        'date': holiday_data['date'],
        'country': country_code,
        'scope': holiday_data['scope'],
        'importance': holiday_data['importance']
    },
    source_id=holiday_data['id'],
    source_platform="calendar_holidays",  # ✅
    source_created_by='calendar_holidays',
    source_created_at=holiday_data['date']
)

# Save only to central database
central_db.insert(idea)
```

## Testing After Migration

1. Run the source's scrape command
2. Verify data saved to central database
3. Query by source_platform:
   ```python
   from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path
   
   db = IdeaInspirationDatabase(get_central_database_path())
   results = db.get_all(source_platform="your_platform_name")
   
   # Verify results
   assert len(results) > 0
   assert all(r.source_platform == "your_platform_name" for r in results)
   ```

## Migration Status

### Completed ✅
- [x] Model: source_platform field and database support
- [x] LyricSnippets (Creative)
- [x] GoogleTrends (Signal)
- [x] CalendarHolidays (Event)

### Remaining Sources

**Creative Sources:**
- [ ] ScriptBeats
- [ ] VisualMoodboard

**Signal Sources:**
- [ ] News/NewsApi
- [ ] News/GoogleNews
- [ ] Hashtags/TikTokHashtag
- [ ] Hashtags/InstagramHashtag
- [ ] Memes/MemeTracker
- [ ] Challenges/SocialChallenge
- [ ] Locations/GeoLocalTrends
- [ ] Sounds/TrendingSounds

**Event Sources:**
- [ ] SportsHighlights
- [ ] EntertainmentReleases

**Commerce Sources:**
- [ ] AmazonBestsellers
- [ ] AppStoreTopCharts
- [ ] EtsyTrending

**Community Sources:**
- [ ] QASource
- [ ] PromptBoxSource
- [ ] CommentMiningSource
- [ ] UserFeedbackSource

**Content Sources:**
- [ ] Shorts/InstagramReels
- [ ] Shorts/TikTok
- [ ] Shorts/YouTubeShorts
- [ ] (and others - approximately 20+ content sources)

**Internal Sources:**
- [ ] CSVImport
- [ ] ManualBacklog

## Benefits of Single DB Approach

1. **Unified Querying**: Query across all sources with a single query
2. **Simplified Architecture**: No need to maintain multiple databases
3. **Easier Blending**: PrismQ.Idea.Extractor can easily blend ideas from multiple sources
4. **Platform Filtering**: Efficient filtering by source_platform
5. **Metadata Flexibility**: Platform-specific data in metadata dict

## Common Pitfalls

### ❌ Don't Do This
```python
# Don't set source_platform in metadata AND as parameter
metadata = {'source_platform': 'youtube'}  # ❌ WRONG
idea = IdeaInspiration.from_video(
    ...,
    metadata=metadata,
    source_platform='youtube'  # ✅ RIGHT - use parameter instead
)
```

### ❌ Don't Do This
```python
# Don't use non-string values in metadata
metadata = {
    'views': 1500000,  # ❌ WRONG - use str(1500000)
    'likes': 50000     # ❌ WRONG - use str(50000)
}
```

### ✅ Do This
```python
# Use source_platform parameter
idea = IdeaInspiration.from_video(
    ...,
    metadata={
        'views': str(1500000),  # ✅ String values
        'likes': str(50000)
    },
    source_platform='youtube'  # ✅ Use parameter
)
```

## Questions?

See:
- `_meta/docs/MODEL_EXTENSION_RESEARCH.md` - Full research
- `_meta/docs/MODEL_QUESTIONS_ANSWERS.md` - Quick reference
- `Model/idea_inspiration.py` - Model definition
- `Model/idea_inspiration_db.py` - Database operations
