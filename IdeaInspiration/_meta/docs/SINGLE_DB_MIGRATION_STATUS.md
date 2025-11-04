# Single DB Migration Status

**Last Updated**: October 31, 2025  
**Issue**: `implement_single_db_source_modules.md`

## Completion Status

### ✅ Phase 1: Core Model Updates (COMPLETE)
- [x] Added `source_platform` column to database schema
- [x] Added `source_platform` parameter to factory methods
- [x] Created database index on `source_platform`
- [x] Updated all database operations
- [x] Added 13 comprehensive tests
- [x] All 103 tests passing

### ✅ Phase 2: Representative Examples (COMPLETE)
Migrated 3 sources from different categories to establish pattern:

| Source | Category | Platform Name | Status |
|--------|----------|---------------|---------|
| LyricSnippets | Creative | `genius` | ✅ Complete |
| GoogleTrends | Signal | `google_trends` | ✅ Complete |
| CalendarHolidays | Event | `calendar_holidays` | ✅ Complete |

### ✅ Phase 3: Documentation (COMPLETE)
- [x] Created `SINGLE_DB_MIGRATION_GUIDE.md`
- [x] Documented migration pattern
- [x] Provided code examples
- [x] Listed all remaining sources

## Remaining Sources (35)

### Creative Sources (2)
- [ ] **ScriptBeats** → `script_beats`
  - Plugin: `src/plugins/script_beats_plugin.py`
  - Pattern: Check if returns Dict or IdeaInspiration
  
- [ ] **VisualMoodboard** → `visual_moodboard`
  - Plugin: `src/plugins/visual_moodboard_plugin.py`
  - Pattern: Check if returns Dict or IdeaInspiration

### Signal Sources (11)
- [ ] **Challenges/SocialChallenge** → `social_challenge`
- [ ] **Hashtags/InstagramHashtag** → `instagram_hashtag`
- [ ] **Hashtags/TikTokHashtag** → `tiktok_hashtag`
- [ ] **Locations/GeoLocalTrends** → `geo_local_trends`
- [ ] **Memes/KnowYourMeme** → `know_your_meme`
- [ ] **Memes/MemeTracker** → `meme_tracker`
- [ ] **News/GoogleNews** → `google_news`
- [ ] **News/NewsApi** → `news_api`
- [ ] **Sounds/InstagramAudioTrends** → `instagram_audio_trends`
- [ ] **Sounds/TikTokSounds** → `tiktok_sounds`
- [ ] **Trends/TrendsFile** → `trends_file`

### Event Sources (2)
- [ ] **EntertainmentReleases** → `entertainment_releases`
- [ ] **SportsHighlights** → `sports_highlights`

### Commerce Sources (3)
- [ ] **AmazonBestsellers** → `amazon_bestsellers`
- [ ] **AppStoreTopCharts** → `app_store_top_charts`
- [ ] **EtsyTrending** → `etsy_trending`

### Community Sources (4)
- [ ] **CommentMiningSource** → `comment_mining`
- [ ] **PromptBoxSource** → `prompt_box`
- [ ] **QASource** → `qa_source`
- [ ] **UserFeedbackSource** → `user_feedback`

### Content Sources (11)
- [ ] **Articles/Medium** → `medium`
- [ ] **Articles/WebArticles** → `web_articles`
- [ ] **Forums/HackerNews** → `hacker_news`
- [ ] **Forums/Reddit** → `reddit`
- [ ] **Podcasts/ApplePodcasts** → `apple_podcasts`
- [ ] **Podcasts/SpotifyPodcasts** → `spotify_podcasts`
- [ ] **Shorts/InstagramReels** → `instagram_reels`
- [ ] **Shorts/TikTok** → `tiktok`
- [ ] **Shorts/TwitchClips** → `twitch_clips`
- [ ] **Shorts/YouTube** → `youtube`
- [ ] **Streams/KickClips** → `kick_clips`

### Internal Sources (2)
- [ ] **CSVImport** → `csv_import`
- [ ] **ManualBacklog** → `manual_backlog`

## Migration Checklist (Per Source)

For each source, follow these steps:

### 1. Identify Implementation Pattern
```bash
# Check where IdeaInspiration is created
grep -r "IdeaInspiration\.from_" Sources/[Category]/[SourceName]/src/
```

**Two patterns:**
- **Pattern A**: Plugin creates IdeaInspiration (like LyricSnippets, GoogleTrends)
- **Pattern B**: CLI creates IdeaInspiration (like CalendarHolidays)

### 2. Update Plugin (Pattern A) or CLI (Pattern B)

**Add source_platform parameter:**
```python
idea = IdeaInspiration.from_text(
    title=data['title'],
    description=data['description'],
    text_content=data['content'],
    keywords=keywords,
    metadata=metadata,
    source_id=data['id'],
    source_url=data['url'],
    source_platform="[platform_name]",  # ← ADD THIS LINE
    source_created_by=data['author'],
    source_created_at=data['date']
)
```

### 3. Update CLI File

**Remove dual-save pattern:**

Before:
```python
# Initialize both databases
db = Database(config.database_path)
central_db = IdeaInspirationDatabase(central_db_path)

# Save to both
db.insert_resource(...)  # Source-specific
central_db.insert(idea)  # Central
```

After:
```python
# Initialize only central database
central_db = IdeaInspirationDatabase(get_central_database_path())

# Save only to central
central_db.insert(idea)
```

**Remove unused imports:**
```python
# Remove these if no longer used:
from .core.database import Database
from .core.metrics import CreativeMetrics  # or UniversalMetrics, SignalMetrics, etc.
from .core.processors import [SomeProcessor]
```

### 4. Test the Migration

```bash
cd Sources/[Category]/[SourceName]
python -m src.cli scrape [options]
```

Verify:
```python
from Model.idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path

db = IdeaInspirationDatabase(get_central_database_path())
results = db.get_all(source_platform="[platform_name]")
assert len(results) > 0
assert all(r.source_platform == "[platform_name]" for r in results)
```

### 5. Update This Status File

Mark the source as complete with ✅

## Quick Reference

### Source Platform Naming
- Use lowercase with underscores
- Match the source directory name (converted to snake_case)
- Examples: `genius`, `google_trends`, `calendar_holidays`, `youtube`, `instagram_reels`

### Common Metadata Fields

**Video/Short sources:**
```python
metadata = {
    'views': str(video['views']),
    'likes': str(video['likes']),
    'comments': str(video['comments']),
    'duration_seconds': str(video['duration']),
    'video_id': video['id']
}
```

**News/Article sources:**
```python
metadata = {
    'author': article['author'],
    'publish_date': article['publishedAt'],
    'source': article['source']['name'],
    'url': article['url']
}
```

**Trend/Signal sources:**
```python
metadata = {
    'region': config.region,
    'rank': str(rank),
    'volume': str(volume),
    'signal_type': 'trend',
    'current_status': 'rising'
}
```

## Progress Tracking

- **Total Sources**: 38
- **Completed**: 3 (8%)
- **Remaining**: 35 (92%)

### By Category
- Creative: 1/3 (33%)
- Signals: 1/12 (8%)
- Events: 1/3 (33%)
- Commerce: 0/3 (0%)
- Community: 0/4 (0%)
- Content: 0/11 (0%)
- Internal: 0/2 (0%)

## Notes

- All migrations follow the same pattern documented in `SINGLE_DB_MIGRATION_GUIDE.md`
- The Model layer is fully ready to support all sources
- Each source should take 30-60 minutes to migrate
- Focus on sources with existing IdeaInspiration first (easier migrations)
- Sources without IdeaInspiration may need plugin refactoring

## Resources

- **Migration Guide**: `_meta/docs/SINGLE_DB_MIGRATION_GUIDE.md`
- **Model Research**: `_meta/docs/MODEL_EXTENSION_RESEARCH.md`
- **Quick Reference**: `_meta/docs/MODEL_QUESTIONS_ANSWERS.md`
- **Model Code**: `Model/idea_inspiration.py`
- **Database Code**: `Model/idea_inspiration_db.py`

## Next Steps

1. Review the 3 completed migrations as templates
2. Start with sources that already create IdeaInspiration (easier)
3. Use the migration checklist for each source
4. Test each migration before moving to the next
5. Update this status file as you complete each source
