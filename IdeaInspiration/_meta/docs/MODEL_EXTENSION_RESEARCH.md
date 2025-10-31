# Model Extension Research

**Date**: October 31, 2025  
**Status**: Comprehensive Research  
**Related**: PR #69, DATABASE_INTEGRATION_SUMMARY.md

## Executive Summary

This document provides comprehensive research on extending the PrismQ.IdeaInspiration.Model to better support collecting content inspirations from various sources. Based on analysis of the current dual-save architecture (PR #69) and industry best practices, we examine how Sources can be optimally transformed into IdeaInspiration objects, which are then consumed by downstream modules like **PrismQ.Idea.Model** for story generation.

## Architecture Context

**Important Clarification:**

- **This Repository (PrismQ.IdeaInspiration)**: Collection layer - Sources → IdeaInspiration objects
- **PrismQ.Idea.Model**: Content generation layer - takes IdeaInspiration(s) → creates story suggestions/scripts
- **PrismQ.Idea.Extractor**: Blending/mixing layer - combines multiple IdeaInspiration objects before story creation

```
Sources → IdeaInspiration (this repo) → PrismQ.Idea.Extractor (blending) → PrismQ.Idea.Model (story generation)
```

## Research Questions

### 1. Are Sources/Content ideal for IdeaInspiration?

**Answer: Yes, the current IdeaInspiration model works well as a general-purpose collection format.**

The current `IdeaInspiration` model serves as a unified output format from all Sources:

1. **Source metadata** - Platform, author/channel, URL, timestamps in `source_*` fields
2. **Content payload** - Title, description, text/transcript in main content fields
3. **Platform metrics** - Views, likes, etc. in `metadata` dict

#### Current Implementation Analysis

**What Works Well:**
- ✅ Dual-save architecture preserves platform-specific details
- ✅ `IdeaInspiration` provides unified output format for all Sources
- ✅ Factory methods (`from_text`, `from_video`, `from_audio`) abstract content types
- ✅ Minimal friction for Source modules to save data
- ✅ Flexible `metadata` dict accommodates platform-specific fields

**Extension Considerations:**

Before extending the model, evaluate if existing fields suffice:
- `title`, `description`, `content` - Core content fields
- `keywords` - Tags, hashtags, extracted terms
- `source_type` - TEXT, VIDEO, AUDIO (extensible)
- `metadata` - Platform-specific data (views, likes, duration, etc.)
- `source_*` fields - Origin tracking
- `score`, `category`, `subcategory_relevance` - Classification data

**When to Extend:**

Only extend if a Source type cannot fit into the general model. Examples where extension might be needed:
- **Signal Sources** (trends, keywords) - very different from content sources
- **Event Sources** (holidays, releases) - structured temporal data
- **Relationship data** - connections between content pieces

#### Recommended Approach: Flexible IdeaInspiration + Optional Signal Type

**Option 1: Use General IdeaInspiration (Preferred)**

Most Sources should use the existing model:

```python
# YouTube Short
idea = IdeaInspiration.from_video(
    title="True Crime Documentary",
    subtitle_text="Transcript...",
    keywords=["true_crime", "mystery"],
    metadata={
        'platform': 'youtube',
        'duration_seconds': '45',
        'views': '1500000',
        'video_id': 'abc123'
    }
)

# Google Trends
idea = IdeaInspiration.from_text(
    title="Trending: True Crime",
    text_content="Search interest in 'true crime' increased 45% this week",
    keywords=["true_crime", "trend"],
    metadata={
        'platform': 'google_trends',
        'trend_strength': '0.85',
        'region': 'US'
    },
    source_type=ContentType.TEXT
)
```

### 2. Can other things be saved as different types?

**Answer: No need for separate types. Use IdeaInspiration universally.**

#### IdeaInspiration is Universal (100% of cases)

The `IdeaInspiration` model handles **all** Sources, including trend/signal sources:

**Content Sources** (with rich content):
- YouTube, TikTok, Reddit - use `content` field for transcript/text
- Lyrics, scripts - use `content` field
- Articles, podcasts - use `content` field

**Trend/Signal Sources** (without content):
- Google Trends - **no content field**, just `keywords` and `metadata`
- Hashtag trends - **no content field**, just `keywords`
- News mentions - can have brief `description`, keywords in `keywords` field

**The key insight**: IdeaInspiration doesn't require the `content` field to be populated. Trend sources can have:
- Empty or minimal `content` field
- Rich `keywords` list (the actual signals)
- `metadata` with trend strength, region, etc.

#### Example: Google Trends as IdeaInspiration

```python
# Google Trends - represented as IdeaInspiration (not a separate Signal type)
trend_idea = IdeaInspiration.from_text(
    title="Trending: Trump",
    description="Search interest in 'Trump' spiked 95% in last 24h",
    text_content="",  # No content for trend sources
    keywords=["Trump", "politics", "election"],  # The actual signal
    metadata={
        'platform': 'google_trends',
        'trend_strength': '0.95',  # 95% interest
        'region': 'US',
        'related_queries': 'election,debate,rally'
    },
    source_type=ContentType.TEXT
)
```

**How PrismQ.Idea.Extractor Uses Multiple IdeaInspiration:**

The Extractor can blend **multiple IdeaInspiration objects** together:

```python
# Example: Blend story + trend + another story
story1 = IdeaInspiration(...)  # YouTube Short about political mystery
trend_idea = IdeaInspiration(...)  # Google Trends: "Trump" keyword trending
story2 = IdeaInspiration(...)  # Another YouTube Short about election intrigue

# PrismQ.Idea.Extractor combines ALL of them:
extractor.blend(
    inspirations=[story1, trend_idea, story2]
)
# Result: Combined story incorporating:
# - Mystery elements from story1
# - Trending "Trump" keyword from trend_idea
# - Election theme from story2
```

This blending happens in **PrismQ.Idea.Extractor**, not in this repository.
- YouTube video thumbnail
- TikTok video clip
- Article featured image
- Podcast episode audio file

##### **Person / Channel**
Normalized creator/author entities, deduplicated across platforms.

```python
@dataclass
class Channel:
    channel_id: str  # Internal stable ID
    name: str
    platform: str  # "youtube", "tiktok", "genius"
    platform_channel_id: str  # Platform-specific ID
    url: str
    subscriber_count: Optional[int]
    verified: bool
    description: str
    metadata: Dict[str, str]
    
    # Deduplication support
    canonical_channel_id: Optional[str]  # For merged channels
```

**Use Cases:**
- Track same creator across YouTube, TikTok, Instagram
- Deduplicate "MrBeast" vs "mrbeast" vs "Mr Beast"
- Analyze creator performance across platforms

##### **Collection**
Manual or auto-curated lists of Ideas.

```python
@dataclass
class Collection:
    collection_id: str
    name: str
    description: str
    collection_type: CollectionType
    idea_ids: List[str]  # References to Ideas
    created_by: str  # System or user
    created_at: str
    updated_at: str
    metadata: Dict[str, str]

class CollectionType(Enum):
    MANUAL = "manual"  # User-curated
    AUTO_TOPIC = "auto_topic"  # AI-grouped by topic
    AUTO_TREND = "auto_trend"  # Trending cluster
    PLAYLIST = "playlist"  # Ordered sequence
    SERIES = "series"  # Multi-part content
```

**Use Cases:**
- "Halloween 2025 Ideas" (manual)
- "True Crime Trending This Week" (auto_trend)
- "BookTok Series Part 1-5" (series)

#### Entity Relationship Diagram

```
┌─────────────┐
│   Channel   │ ──┐
└─────────────┘   │
                  │ 1:N
                  ▼
┌─────────────┐ 1:N  ┌─────────────┐
│   Source    │─────▶│   Content   │
└──────┬──────┘      └──────┬──────┘
       │                    │
       │ N:M                │ 1:N
       │                    ▼
       │             ┌─────────────┐
       │             │     Idea    │◀─┐
       │             └──────┬──────┘  │
       │                    │         │
       │ 1:N                │ N:M     │ N:M
       ▼                    ▼         │
┌─────────────┐      ┌─────────────┐ │
│   Signal    │      │   Category  │ │
└─────────────┘      └─────────────┘ │
                                     │
       ┌─────────────┐               │
       │ Attachment  │───────────────┘
       └─────────────┘
                │
                │ N:M
                ▼
         ┌─────────────┐
         │ Collection  │
         └─────────────┘
```


### 3. How to use Sources for creating IdeaInspiration?

#### Recommended Flow (Single DB Approach)

Sources transform platform data into IdeaInspiration objects:

```python
# In Source module (e.g., LyricSnippets)
def scrape(self) -> List[IdeaInspiration]:
    # 1. Plugin scrapes platform (Genius API)
    api_data = genius_api.search_songs("trending")
    
    # 2. Transform to IdeaInspiration
    ideas = []
    for song in api_data:
        idea = IdeaInspiration.from_text(
            title=f"{song['title']} - {song['artist']}",
            text_content=song['lyrics_snippet'],
            keywords=['lyrics', song['artist'].lower()],
            source_platform="genius",  # Dedicated platform field (recommended addition)
            metadata={
                # Platform-specific metrics in metadata
                'song_id': str(song['id']),
                'pageviews': str(song['pageviews']),
                'annotation_count': str(song.get('annotation_count', 0)),
                'audience_geography': 'US:45%,UK:20%,DE:15%'  # Geography data
            },
            source_id=str(song['id']),
            source_url=song['url'],
            source_created_by=song['artist']
        )
        ideas.append(idea)
    
    # 3. Save to central database (single DB)
    for idea in ideas:
        central_db.insert(idea)
    
    return ideas
```

**Key Benefits of Single DB:**
- Simpler architecture (one database)
- All data in IdeaInspiration format
- Platform-specific fields in `metadata` dict
- No duplication between databases

This is the **output of this repository** - IdeaInspiration objects ready for downstream consumption.

#### Source → IdeaInspiration Pipeline

```
Stage 1: COLLECT
├─ Plugin authenticates with platform API
├─ Fetches raw data (JSON, HTML, RSS, etc.)
└─ Returns platform-specific data structures

Stage 2: TRANSFORM
├─ Map platform data to IdeaInspiration fields
├─ Extract keywords and tags
├─ Populate metadata dict with platform-specific fields
└─ Use appropriate factory method (from_text, from_video, from_audio)

Stage 3: ENRICH (Optional)
├─ Run scoring (PrismQ.IdeaInspiration.Scoring)
├─ Run classification (PrismQ.IdeaInspiration.Classification)
├─ Add contextual scores
└─ Compute relevance scores

Stage 4: SAVE
├─ Write to central database (IdeaInspiration)
└─ Index for search
```

**Output**: IdeaInspiration objects ready for consumption by **PrismQ.Idea.Model**.

#### Example: Google Trends as IdeaInspiration

Trend sources return IdeaInspiration with keywords but minimal/no content:

```python
# GoogleTrends plugin
def scrape(self) -> List[IdeaInspiration]:
    trends = google_trends_api.get_trending("US")
    
    ideas = []
    for trend in trends:
        # Trend as IdeaInspiration (not a separate Signal type)
        idea = IdeaInspiration.from_text(
            title=f"Trending: {trend['keyword']}",
            description=f"Search interest spiked {trend['interest']}%",
            text_content="",  # No content for trend sources
            keywords=[trend['keyword']] + trend.get('related', []),
            metadata={
                'platform': 'google_trends',
                'trend_strength': str(trend['interest'] / 100.0),
                'region': 'US',
                'category': trend.get('category', '')
            },
            source_id=f"trend_{trend['keyword']}_{datetime.now().date()}",
            source_type=ContentType.TEXT
        )
        ideas.append(idea)
    
    # Dual-save (same as other sources)
    for idea in ideas:
        source_db.insert_trend(idea)
        central_db.insert(idea)
    
    return ideas
```

These trend IdeaInspiration objects are then available to **PrismQ.Idea.Extractor** for blending with content-rich IdeaInspiration.

### 4. Can we blend IdeaInspiration from YouTubeShorts by topic/trend?

**Answer: Yes. Multiple IdeaInspiration objects are blended in PrismQ.Idea.Extractor.**

#### Architecture Clarification

```
┌─────────────────────────────────┐
│  PrismQ.IdeaInspiration         │
│  (This Repository)              │
│                                 │
│  Sources → IdeaInspiration      │
│  - YouTube Shorts               │
│  - TikTok                       │
│  - Lyric Snippets               │
│  - Google Trends (Signals)      │
└────────────┬────────────────────┘
             │
             │ IdeaInspiration objects + Signals
             ▼
┌─────────────────────────────────┐
│  PrismQ.Idea.Extractor          │
│  (Blending/Mixing Layer)        │
│                                 │
│  - Query multiple IdeaInspiration│
│  - Blend by topic/trend         │
│  - Add trending Signals         │
│  - Create story concepts        │
└────────────┬────────────────────┘
             │
             │ Blended story concepts
             ▼
┌─────────────────────────────────┐
│  PrismQ.Idea.Model              │
│  (Story Generation)             │
│                                 │
│  - Generate scripts             │
│  - Create YouTube videos        │
└─────────────────────────────────┘
```

#### What This Repository Provides

**IdeaInspiration Collection:**
- YouTube Shorts collected as IdeaInspiration objects
- Keywords, metadata, scores attached
- Stored in central database for querying

**Example:**
```python
# YouTube Shorts Source
shorts = youtube_plugin.scrape_by_keyword("true crime", top_n=20)
# Returns: List[IdeaInspiration]

# Each IdeaInspiration has:
# - title: "Unsolved Mystery Documentary"
# - content: "Transcript of the video..."
# - keywords: ["true_crime", "mystery", "documentary"]
# - metadata: {'platform': 'youtube', 'views': '1500000', 'duration_seconds': '45'}

# Save to database
for idea in shorts:
    db.insert(idea)
```

**Trend Collection (as IdeaInspiration):**
```python
# Google Trends Source
trends = trends_plugin.scrape()
# Returns: List[IdeaInspiration]

# Each trend IdeaInspiration has:
# - title: "Trending: Trump"
# - content: "" (empty for trend sources)
# - keywords: ["Trump", "politics", "election"]
# - metadata: {'platform': 'google_trends', 'trend_strength': '0.95'}

# Save to database (same as other sources)
for idea in trends:
    db.insert(idea)
```

#### What PrismQ.Idea.Extractor Does

**Blending happens in PrismQ.Idea.Extractor**, not here. Example workflow:

```python
# In PrismQ.Idea.Extractor (separate repository)

from prismq.idea.extractor import IdeaExtractor
from idea_inspiration_db import IdeaInspirationDatabase

extractor = IdeaExtractor()
db = IdeaInspirationDatabase("db.s3db")

# 1. Query content IdeaInspiration
true_crime_stories = db.filter(keywords=["true_crime"], days_back=7)
# Returns: [IdeaInspiration(YouTube video), IdeaInspiration(TikTok), ...]

# 2. Query trend IdeaInspiration
trending_topics = db.filter(
    keywords=["Trump"],
    metadata_contains={'platform': 'google_trends'}
)
# Returns: [IdeaInspiration(trend data with keywords but no content)]

# 3. Blend MULTIPLE IdeaInspiration together → Story concept
story = extractor.blend(
    inspirations=true_crime_stories + trending_topics,
    strategy="multi_source"
)

# Result: Story concept combining:
# - True crime narrative from YouTube/TikTok
# - Trending "Trump" keyword from Google Trends
# - Creates unified story incorporating all elements
```

**Blending Strategies in PrismQ.Idea.Extractor:**

1. **Multi-Source**: Combine multiple IdeaInspiration (content + trends + more content)
2. **Topic-Based**: Combine IdeaInspiration on same topic
3. **Multi-Platform**: Blend YouTube Shorts + TikTok + Instagram
4. **Temporal**: Track how topics evolve over time

**Key Insight**: All blending uses IdeaInspiration objects - some with rich content (videos, articles), some with just keywords (trends).

#### Query Patterns This Repository Supports

To enable blending, this repository provides queryable IdeaInspiration:

```python
# Query by keywords
db.filter(keywords=["true_crime", "mystery"])

# Query by platform
db.filter(metadata_contains={'platform': 'youtube'})

# Query trends
db.filter(metadata_contains={'platform': 'google_trends'})

# Query recent content
db.filter(days_back=7)

# Query by score threshold
db.filter(min_score=80)

# Query by category
db.filter(category="true_crime")
```

**PrismQ.Idea.Extractor** uses these queries to collect multiple IdeaInspiration for blending.

#### Example: Multiple IdeaInspiration Blending

From feedback: Multiple IdeaInspiration (not just one + signal) can be blended:

**In This Repository:**
```python
# 1. Collect story inspiration #1
story1 = IdeaInspiration.from_video(
    title="Political Thriller Documentary",
    subtitle_text="Transcript about government secrets...",
    keywords=["politics", "thriller", "documentary"]
)
db.insert(story1)

# 2. Collect trend inspiration (as IdeaInspiration, not Signal)
trend_idea = IdeaInspiration.from_text(
    title="Trending: Trump",
    description="Search interest spiked 95%",
    text_content="",  # Empty for trends
    keywords=["Trump", "politics", "election"],
    metadata={
        'platform': 'google_trends',
        'trend_strength': '0.95'
    }
)
db.insert(trend_idea)

# 3. Collect story inspiration #2
story2 = IdeaInspiration.from_video(
    title="Election Intrigue Investigation",
    subtitle_text="Transcript about election mysteries...",
    keywords=["election", "mystery", "investigation"]
)
db.insert(story2)
```

**In PrismQ.Idea.Extractor:**
```python
# 4. Blend MULTIPLE IdeaInspiration together
extractor.blend(
    inspirations=[story1, trend_idea, story2]
)
# → Creates story concept incorporating:
#    - Political thriller elements from story1
#    - Trending "Trump" keyword from trend_idea
#    - Election mystery from story2
#    Result: "Political thriller about election intrigue involving Trump"
```

**Key Point**: All three inputs are IdeaInspiration objects - two with content, one with just keywords.

## Recommendations

### Immediate Actions (Low Effort, High Value)

1. **Add source_platform Field to IdeaInspiration Model**
   - Add `source_platform: Optional[str] = None` to model
   - Avoids duplication (no platform in metadata)
   - Enables efficient platform filtering
   - ~5 lines of code change

2. **Use Single DB Approach** ✅
   - Store all data in central IdeaInspiration database
   - Platform-specific metrics in `metadata` dict
   - Simpler architecture, no dual-save complexity
   - Easier to maintain and query

3. **Use IdeaInspiration Universally** ✅
   - ALL Sources return IdeaInspiration (including trends)
   - Content-rich sources: populate `content` field
   - Trend sources: leave `content` empty, use `keywords`
   - No separate Signal type needed

4. **Use Metadata for Platform-Specific Data**
   - Audience geography: `'audience_geography': 'US:45%,UK:20%'`
   - Platform metrics: `'views'`, `'likes'`, `'shares'`
   - Custom fields: any platform-specific data as strings

### Medium-Term Actions (Requires Planning)

5. **Build PrismQ.Idea.Extractor** (Separate Repository)
   - Implement blending/mixing logic
   - Combine multiple IdeaInspiration objects
   - Create story concepts for PrismQ.Idea.Model
   - Handle both content-rich and keyword-only IdeaInspiration

6. **Enhance Querying Capabilities**
   - Add semantic search (embeddings)
   - Improve keyword matching
   - Enable complex filters
   - Support batch queries

6. **Extend Classification Integration**
   - Auto-tag ideas with categories
   - Compute relevance scores
   - Feed classified data to Extractor

### Long-Term Actions (Strategic)

7. **Add Content Versioning** (Optional)
   - Track view count changes over time
   - Store multiple snapshots of same content
   - Analyze performance trends

8. **Build Trend Detection Service**
   - Monitor Signal strength over time
   - Detect emerging vs declining trends
   - Alert when trends cross thresholds

9. **Create PrismQ.Idea.Builder Module** (Issue #503)
   - Centralize source transformations
   - Standardize IdeaInspiration creation
   - Quality control layer

## Conclusion

The PrismQ.IdeaInspiration repository serves as the **collection layer** in the content generation pipeline. Key takeaways:

1. **Current IdeaInspiration model works well** - Handles most Sources without modification
2. **Use general model first** - Only extend with Signal type when truly needed
3. **Blending happens downstream** - PrismQ.Idea.Extractor handles combining multiple IdeaInspiration
4. **Focus on collection** - This repo collects and stores, downstream modules blend and generate
5. **Query support is key** - Provide flexible querying for Extractor to find content

**Architecture Summary:**

```
Sources → IdeaInspiration (this repo) → PrismQ.Idea.Extractor (blending) → PrismQ.Idea.Model (generation)
```

**Next Steps:**
1. Add Signal type if needed for trend sources
2. Improve query capabilities for filtering IdeaInspiration
3. Build PrismQ.Idea.Extractor (separate repository) for blending
4. Enhance Classification integration for better categorization
5. Consider Builder module (Issue #503) for transformation quality

---

**Authors**: PrismQ Research Team  
**Review Date**: October 31, 2025  
**Status**: ✅ Research Complete, Architecture Clarified
