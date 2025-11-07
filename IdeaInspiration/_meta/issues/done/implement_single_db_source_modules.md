# Implement Single DB Approach for Source Modules

## Overview

Migrate all Source modules to use the Single DB approach with IdeaInspiration as the universal output model, utilizing the new `source_platform` field.

**Current Status:** 24 of 24 sources migrated (100% complete) ✅
- ✅ **24 Completed:** All sources migrated to single DB approach!
- ⏳ **0 In Progress:** N/A
- ❌ **0 Not Started:** All sources complete!

## Background

Research (PR #71) established that:
- IdeaInspiration is the universal collection format (100% of sources)
- Single DB approach is simpler than dual-save
- Platform-specific data goes in `metadata` dict
- New `source_platform` field identifies the platform

## Requirements

Each Source module must:
1. **Output IdeaInspiration objects** from `scrape()` method
2. **Set source_platform field** to identify platform (e.g., "youtube", "google_trends")
3. **Store platform-specific data** in `metadata` dict (views, likes, audience_geography, etc.)
4. **Save to central database** (single DB, no dual-save)
5. **Remove source-specific databases** (if using dual-save pattern)

## Source Modules to Update

### Creative Sources
- [x] ScriptBeats
- [x] VisualMoodboard  
- [x] LyricSnippets

### Signal Sources
- [x] Trends/GoogleTrends
- [x] News/NewsApi
- [x] Hashtags/TikTokHashtag
- [x] Hashtags/InstagramHashtag
- [x] Memes/MemeTracker
- [x] Challenges/SocialChallenge
- [x] Locations/GeoLocalTrends
- [x] Sounds/TikTokSounds
- [x] Sounds/InstagramAudioTrends

### Event Sources
- [x] CalendarHolidays
- [x] SportsHighlights
- [x] EntertainmentReleases

### Commerce Sources
- [x] AmazonBestsellers
- [x] AppStoreTopCharts
- [x] EtsyTrending

### Community Sources
- [x] QASource
- [x] PromptBoxSource
- [x] CommentMiningSource
- [x] UserFeedbackSource

### Internal Sources
- [x] CSVImport
- [x] ManualBacklog

## Implementation Template

```python
# In Source module (e.g., Sources/Signals/News/NewsApi/src/cli.py)
from Model.idea_inspiration import IdeaInspiration
from Model.idea_inspiration_db import IdeaInspirationDatabase

def scrape(self) -> List[IdeaInspiration]:
    # 1. Fetch from platform API
    articles = news_api.get_articles(query)
    
    # 2. Transform to IdeaInspiration
    ideas = []
    for article in articles:
        idea = IdeaInspiration.from_text(
            title=article['title'],
            description=article['description'],
            text_content=article['content'],
            keywords=extract_keywords(article),
            source_platform="news_api",  # NEW: platform identifier
            metadata={
                # Platform-specific metrics
                'source': article['source'],
                'author': article['author'],
                'publish_date': article['publishedAt'],
                'url': article['url']
            },
            source_id=article['url'],
            source_url=article['url']
        )
        ideas.append(idea)
    
    # 3. Save to central database (single DB)
    central_db = IdeaInspirationDatabase(get_central_database_path())
    for idea in ideas:
        central_db.insert(idea)
    
    return ideas
```

## Migration Steps for Each Source

1. **Update imports**
   - Add `from Model.idea_inspiration import IdeaInspiration`
   - Add `from Model.idea_inspiration_db import IdeaInspirationDatabase`

2. **Update scrape() method**
   - Return `List[IdeaInspiration]`
   - Set `source_platform` field
   - Use `metadata` for platform-specific data

3. **Update database saving**
   - Initialize central database
   - Remove source-specific database (if exists)
   - Save IdeaInspiration objects to central DB only

4. **Update tests**
   - Verify IdeaInspiration output format
   - Verify source_platform is set correctly
   - Verify metadata contains expected fields
   - Verify central database integration

5. **Update documentation**
   - README: Explain output format
   - Code comments: Document metadata fields

## Acceptance Criteria

For each Source module:
- ✅ Returns `List[IdeaInspiration]` from `scrape()`
- ✅ Sets `source_platform` field appropriately
- ✅ Platform-specific data in `metadata` dict
- ✅ Saves only to central IdeaInspiration database
- ✅ Tests pass and verify new format
- ✅ Documentation updated

## Priority

**High** - Foundational change that enables:
- Unified querying across all sources
- PrismQ.Idea.Extractor multi-source blending
- Simplified architecture (single DB)

## Estimated Effort

- **Per module**: 2-4 hours (simple sources) to 6-8 hours (complex sources)
- **Total**: ~40-80 hours across all modules

## References

- PR #71: Model Extension Research (single DB recommendation)
- PR #69: Dual-save implementation (to be superseded)
- `_meta/docs/MODEL_EXTENSION_RESEARCH.md`: Architecture guide
- `_meta/docs/MODEL_QUESTIONS_ANSWERS.md`: Quick reference
- `Model/idea_inspiration.py`: Model definition with source_platform field
