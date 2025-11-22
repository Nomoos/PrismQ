# Model Extension - Questions & Answers

**Quick Reference Guide**  
**Date**: October 31, 2025  
**Full Research**: See [MODEL_EXTENSION_RESEARCH.md](./MODEL_EXTENSION_RESEARCH.md)

## Architecture Overview

**Important**: This repository is the **collection layer**. Blending happens in **PrismQ.Idea.Extractor** (separate module).

```
Sources → IdeaInspiration (this repo) → PrismQ.Idea.Extractor (blending) → PrismQ.Idea.Model (generation)
```

## Q1: Are Sources/Content ideal for IdeaInspiration?

**Answer: Yes, the current IdeaInspiration model works well as a general-purpose format.**

### Current Approach
✅ Works well - Sources transform platform data into `IdeaInspiration` objects  
✅ Dual-save - Stores in both source-specific tables AND central database  
✅ Flexible `metadata` dict accommodates platform-specific fields  

### When to Use IdeaInspiration (90% of cases)
Use the general model for:
- Content Sources: YouTube, TikTok, Reddit, Medium
- Creative Sources: Lyrics, scripts, moodboards
- Event Sources: Holidays, sports, releases

### When to Add Signal Type (10% of cases)
Use Signal for lightweight trend/keyword data without rich content:
- Google Trends detecting "Trump" with strength 0.95
- TikTok hashtag "#booktok" emerging
- News mentions spiking

## Q2: Can other things be saved as different types?

**Answer: No. Use IdeaInspiration universally for all sources.**

### IdeaInspiration is Universal

All sources return IdeaInspiration, including:
- **Content sources** (YouTube, TikTok): populate `content` field with transcript
- **Trend sources** (Google Trends): leave `content` empty, use `keywords` field

**Example: Google Trends as IdeaInspiration**
```python
trend_idea = IdeaInspiration.from_text(
    title="Trending: Trump",
    description="Search interest spiked 95%",
    text_content="",  # Empty for trends
    keywords=["Trump", "politics", "election"],  # The actual signal
    metadata={
        'platform': 'google_trends',
        'trend_strength': '0.95'
    }
)
```

**Key Insight**: IdeaInspiration doesn't require `content` field - trends have keywords but no content.

**Use Case:** Track "MrBeast" across YouTube, TikTok, Instagram as same creator.

### Collection
Manual or auto-curated lists of Ideas (playlists/series).

```python
@dataclass
class Collection:
    collection_id: str
    name: str
    collection_type: CollectionType  # MANUAL, AUTO_TOPIC, AUTO_TREND, PLAYLIST, SERIES
    idea_ids: List[str]
    created_by: str  # System or user
```

**Examples:**
- "Halloween 2025 Ideas" (manual)
- "True Crime Trending This Week" (auto_trend)
- "BookTok Series Part 1-5" (series)

## Q3: How to use Sources for creating IdeaInspiration?

### Recommended Flow (Single DB)

```python
# In Source module (e.g., YouTube)
def scrape(self) -> List[IdeaInspiration]:
    # 1. Fetch from platform
    videos = youtube_api.search("true crime")
    
    # 2. Transform to IdeaInspiration
    ideas = []
    for video in videos:
        idea = IdeaInspiration.from_video(
            title=video['title'],
            subtitle_text=video['transcript'],
            keywords=extract_keywords(video),
            source_platform="youtube",  # Recommended: dedicated field
            metadata={
                # Platform-specific metrics
                'views': str(video['views']),
                'likes': str(video['likes']),
                'duration_seconds': str(video['duration']),
                'audience_geography': 'US:50%,UK:20%,CA:15%'
            }
        )
        ideas.append(idea)
    
    # 3. Save to central database (single DB)
    for idea in ideas:
        central_db.insert(idea)
    
    return ideas
```

This is the **output of this repository** - IdeaInspiration objects.

### Google Trends as IdeaInspiration

Trend sources also return IdeaInspiration (not a separate type):

```python
# GoogleTrends plugin
def scrape(self) -> List[IdeaInspiration]:
    trends = api.get_trending("US")
    
    ideas = []
    for trend in trends:
        # Trend as IdeaInspiration (no content, just keywords)
        idea = IdeaInspiration.from_text(
            title=f"Trending: {trend['keyword']}",
            description=f"Interest spiked {trend['interest']}%",
            text_content="",  # Empty for trends
            keywords=[trend['keyword']],
            source_platform="google_trends",
            metadata={
                'trend_strength': str(trend['interest'] / 100.0),
                'region': 'US'
            }
        )
        ideas.append(idea)
    
    # Save to central database
    for idea in ideas:
        central_db.insert(idea)
    
    return ideas
```

## Q4: Can we blend IdeaInspiration from YouTubeShorts by topic/trend?

**Answer: Yes. Multiple IdeaInspiration objects are blended in PrismQ.Idea.Extractor.**

### What This Repository Provides

**Collection & Querying:**

```python
# Collect YouTube Shorts
from sources.youtube import YouTubeTrendingPlugin

plugin = YouTubeTrendingPlugin(config)
shorts = plugin.scrape_by_keyword("true crime", top_n=20)
# Returns: List[IdeaInspiration]

# Save to database
db = IdeaInspirationDatabase("db.s3db")
for idea in shorts:
    db.insert(idea)

# Query capabilities
true_crime_shorts = db.filter(
    keywords=["true_crime"],
    metadata_contains={'platform': 'youtube', 'is_short': 'true'}
)
```

### What PrismQ.Idea.Extractor Does (Separate Module)

**Blending Multiple IdeaInspiration:**

```python
# In PrismQ.Idea.Extractor (NOT this repository)
from prismq.idea.extractor import IdeaExtractor

extractor = IdeaExtractor()

# 1. Get content IdeaInspiration
true_crime_stories = db.filter(keywords=["true_crime"])
# Returns: [IdeaInspiration(YouTube video), IdeaInspiration(TikTok), ...]

# 2. Get trend IdeaInspiration
trending_topics = db.filter(
    keywords=["Trump"],
    metadata_contains={'platform': 'google_trends'}
)
# Returns: [IdeaInspiration(trend with keywords but no content)]

# 3. Blend MULTIPLE IdeaInspiration together
story = extractor.blend(
    inspirations=true_crime_stories + trending_topics
)

# Result: Story concept combining content + trends
```

### Example: Multiple IdeaInspiration Blending

From feedback: Multiple IdeaInspiration (not just one + signal) can be blended:

**In This Repository (Collection):**
```python
# Collect story inspiration #1
story1 = IdeaInspiration.from_video(
    title="Political Thriller",
    subtitle_text="Government secrets...",
    keywords=["politics", "thriller"]
)
db.insert(story1)

# Collect trend inspiration (as IdeaInspiration, not Signal)
trend = IdeaInspiration.from_text(
    title="Trending: Trump",
    text_content="",  # Empty for trends
    keywords=["Trump", "politics"]
)
db.insert(trend)

# Collect story inspiration #2
story2 = IdeaInspiration.from_video(
    title="Election Mystery",
    subtitle_text="Investigation...",
    keywords=["election", "mystery"]
)
db.insert(story2)
```

**In PrismQ.Idea.Extractor (Blending):**
```python
# Blend MULTIPLE IdeaInspiration
extractor.blend(
    inspirations=[story1, trend, story2]
)
# → Creates unified story incorporating:
#    - Political thriller from story1
#    - Trending "Trump" from trend
#    - Election mystery from story2
```

**In PrismQ.Idea.Model (Generation):**
```python
# Generate actual script/video
script = generator.create_script(story_concept)
```

## Implementation Status

### ✅ Currently Available
- Sources collect IdeaInspiration
- Dual-save to source-specific + central DB
- Unified query interface
- Factory methods for content types

### 🚧 Recommended Next Steps
1. Add Signal type (if needed for trend sources)
2. Improve querying capabilities
3. Build PrismQ.Idea.Extractor (separate repository)
4. Create blending/mixing logic in Extractor

### 📋 Future Enhancements
- Content versioning (track metric changes)
- Semantic search with embeddings
- Trend detection service
- Builder module (Issue #503)

## Quick Links

- **[Full Research](./MODEL_EXTENSION_RESEARCH.md)** - Comprehensive analysis
- **[Model README](../../Model/README.md)** - Updated architecture
- **[Database Integration](./DATABASE_INTEGRATION_SUMMARY.md)** - Dual-save pattern
- **[PR #69](https://github.com/Nomoos/PrismQ.T.Idea.Inspiration/pull/69)** - Dual-save implementation

---

**Last Updated**: October 31, 2025  
**Architecture**: IdeaInspiration Collection → PrismQ.Idea.Extractor (Blending) → PrismQ.Idea.Model (Generation)
