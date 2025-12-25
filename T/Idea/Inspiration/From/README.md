# PrismQ Inspiration From Module

**Modern, scalable source integration architecture for PrismQ.T.Idea.Inspiration**

## Overview

The From module provides a clean, hierarchical architecture for integrating external content sources into the PrismQ ecosystem. Each platform is organized under `From/{Platform}/{Variant}` structure.

It also includes the **Content Funnel** - a transformation pipeline that processes content from one media type to another (Video → Audio → Text), enabling unified text extraction across all content types.

## Directory Structure

**Organization: Platform-Based with Variants**

```
From/
├── _meta/                      # From module meta information
│   ├── docs/                   # Documentation (including Content Funnel)
│   ├── examples/               # Usage examples
│   └── tests/                  # Test suite
├── src/                        # Shared code across ALL From modules
│   └── core/                   # Core utilities (including ContentFunnel)
├── YouTube/                    # YouTube inspiration sources
│   ├── Video/                  # Single video scraping
│   ├── Channel/                # Channel-based scraping
│   └── Search/                 # Search/trending scraping
├── HackerNews/                 # HackerNews sources
│   └── Stories/                # Story scraping
├── Reddit/                     # Reddit sources
│   └── Posts/                  # Post scraping
└── {Platform}/                 # Other platforms follow same pattern
    └── {Variant}/              # Platform-specific variants
```

## Content Funnel

The **Content Funnel** is a transformation pipeline that enriches IdeaInspiration objects by extracting content through stages:

```
Video → Audio → Text (via subtitle extraction or audio transcription)
Audio → Text (via transcription)
Text (final form, passthrough)
```

**Key Features:**
- 🎯 Unified text extraction from any media type
- 📊 Transformation tracking and confidence scores
- 🔄 Flexible processing with multiple extraction methods
- 🛡️ Graceful error handling and fallback mechanisms

**Quick Example:**
```python
from T.Idea.Inspiration.From.src.core import ContentFunnel
from Model.src import IdeaInspiration

# Create funnel with extractors
funnel = ContentFunnel(subtitle_extractor=my_subtitle_extractor)

# Process video to extract text content
video_idea = IdeaInspiration.from_video(
    title="Python Tutorial",
    source_url="https://youtube.com/watch?v=abc123"
)

enriched = funnel.process(video_idea, extract_subtitles=True)
# enriched.content now contains subtitle text
```

**Documentation:**
- [Content Funnel Architecture](_meta/docs/CONTENT_FUNNEL_ARCHITECTURE.md) - Complete guide
- [Usage Examples](_meta/examples/content_funnel_example.py) - Working code examples

## Naming Pattern

Following the established `From.{Source}` pattern:

**Pattern**: `T/Idea/Inspiration/From/{Platform}/{Variant}`

**Examples**:
- `T/Idea/Inspiration/From/YouTube/Video` → `PrismQ.T.Idea.Inspiration.From.YouTube.Video`
- `T/Idea/Inspiration/From/YouTube/Channel` → `PrismQ.T.Idea.Inspiration.From.YouTube.Channel`
- `T/Idea/Inspiration/From/HackerNews/Stories` → `PrismQ.T.Idea.Inspiration.From.HackerNews.Stories`

### Current Platforms

- **YouTube/** ✓ - Video platform with Video, Channel, Search variants
- **Reddit/** ✓ - Social platform with Posts variant
- **HackerNews/** ✓ - Tech news with Stories variant
- **Spotify/** ✓ - Music and podcast platform
- **JustWatch/** ✓ - Movie and TV show tracking
- **Text/HackerNews/** ✓ - Tech news

### Future Sources (Recommended Next)

- **Text/Trends/GoogleTrends/** ⭐ - Keyword/trend analysis (text data)
- **Video/TikTok/** - Short-form video
- **Text/Articles/Medium/** - Long-form articles
- **Other/Commerce/Amazon/** - E-commerce product data
- **Other/Events/CalendarHolidays/** - Event-based inspiration

## GoogleTrends Placement: Text Category

**Location:** `Source/Text/Trends/GoogleTrends/`

**Rationale:**
- Analyzes text keywords and search queries
- Produces text-based trend insights
- Consistent with other text analytics (hashtags, memes)
- Text is the primary data type

**Import:**
```python
from Source.Text.Trends.GoogleTrends import GoogleTrendsSource
```

## Usage Examples

```python
# Top-level sources (brand names)
from Source.YouTube import YouTubeSource
from Source.Reddit import RedditSource
from Source.Spotify import SpotifyClient

# Text sources
from Source.Text.HackerNews import HackerNewsSource
from Source.Text.Trends.GoogleTrends import GoogleTrendsSource  # Future

# Audio sources
from Source.Audio.Podcasts import PodcastClient

# Other sources (specialized)
from Source.Other.Commerce.Amazon import AmazonSource  # Future
from Source.Other.Events.CalendarHolidays import HolidaysSource  # Future
```

## Documentation

**Complete legacy source mapping (27+ sources):**
[`_meta/research/LEGACY_SOURCE_PLACEMENT_GUIDE.md`](/_meta/research/LEGACY_SOURCE_PLACEMENT_GUIDE.md)

**Research documents:**
- FLAT_VS_GROUPED_ANALYSIS.md - 5 structural variants
- SHALLOW_HIERARCHY_CONTENT_TYPE_VARIANTS.md - 5 content-type variants
- LEGACY_SOURCE_PLACEMENT_GUIDE.md - Complete source mapping

## Other Category

The "Other" category provides a home for specialized sources that don't fit the core media types:
- **Commerce/** - E-commerce integrations (Amazon, Etsy, AppStore)
- **Events/** - Calendar-based sources (Holidays, Sports, Entertainment)
- **Community/** - User feedback and Q&A sources
- **Internal/** - Internal tools and utilities

See [Other/README.md](Other/README.md) for details.

---

**Architecture Version**: 4.0 (4-Category)  
**Last Updated**: 2025-11-11
