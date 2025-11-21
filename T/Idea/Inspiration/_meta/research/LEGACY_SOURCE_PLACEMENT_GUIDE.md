# Legacy Source Placement Guide

## Overview

This document provides a comprehensive mapping of all 27+ legacy sources from `Legacy_Reference/` to the new simplified 3-category Media Type structure (Video, Audio, Text).

## New Simplified Structure

```
Source/
├── _meta/            # Source-level meta information
├── src/              # Source-level shared code
├── Video/            # VIDEO: All video content sources
├── Audio/            # AUDIO: All audio content sources
└── Text/             # TEXT: All text-based content and data sources
```

## Design Philosophy

**3 Core Categories Only:**
- **Video** - Visual moving content (YouTube, TikTok, streams)
- **Audio** - Sound content (podcasts, music, audio streams)
- **Text** - Written content and structured data (articles, trends, commerce, events)

**Rationale:**
- Simplest possible categorization (3 items at root)
- Universally understood media types
- Maximum cognitive ease
- Text category encompasses all text-based data including trends, analytics, commerce, and events

## Legacy Source Mapping

### Video Category Sources

**Category:** `Source/Video/`

**Current Sources:**
- ✅ YouTube (Shorts, Channel, Search, Video) - `Source/Video/YouTube/`

**Legacy Mapping:**

1. **Content/Shorts/** → `Source/Video/`
   - TikTok → `Source/Video/TikTok/`
   - Instagram Reels → `Source/Video/Instagram/`
   - YouTube Shorts → Already in `Source/Video/YouTube/`

2. **Content/Streams/** → `Source/Video/`
   - Twitch → `Source/Video/Twitch/`
   - YouTube Live → Part of `Source/Video/YouTube/`
   - Facebook Live → `Source/Video/FacebookLive/`

**Total Video Sources:** 5-10 sources
- YouTube ✓ (implemented)
- TikTok (future)
- Instagram (future)
- Twitch (future)
- Vimeo (future)
- Facebook Video (future)

**Import Examples:**
```python
from Source.Video.YouTube import YouTubeSource
from Source.Video.TikTok import TikTokSource
from Source.Video.Instagram import InstagramSource
from Source.Video.Twitch import TwitchSource
```

---

### Audio Category Sources

**Category:** `Source/Audio/`

**Legacy Mapping:**

1. **Content/Podcasts/** → `Source/Audio/Podcasts/`
   - Spotify Podcasts → `Source/Audio/Podcasts/Spotify/`
   - Apple Podcasts → `Source/Audio/Podcasts/Apple/`
   - Google Podcasts → `Source/Audio/Podcasts/Google/`
   - Generic RSS → `Source/Audio/Podcasts/RSS/`

2. **Music Streaming** → `Source/Audio/Music/`
   - Spotify Music → `Source/Audio/Music/Spotify/`
   - SoundCloud → `Source/Audio/Music/SoundCloud/`
   - Apple Music → `Source/Audio/Music/Apple/`

3. **Signals/Sounds** → `Source/Audio/Sounds/`
   - Trending Sounds → `Source/Audio/Sounds/Trending/`
   - Sound Effects → `Source/Audio/Sounds/Effects/`

**Total Audio Sources:** 3-8 sources
- Spotify Podcasts (future)
- Apple Podcasts (future)
- Spotify Music (future)
- SoundCloud (future)
- Trending Sounds (future)

**Import Examples:**
```python
from Source.Audio.Podcasts.Spotify import SpotifyPodcastsSource
from Source.Audio.Music.Spotify import SpotifyMusicSource
from Source.Audio.Music.SoundCloud import SoundCloudSource
from Source.Audio.Sounds.Trending import TrendingSoundsSource
```

---

### Text Category Sources

**Category:** `Source/Text/`

**Current Sources:**
- ✅ Reddit - `Source/Text/Reddit/`
- ✅ HackerNews - `Source/Text/HackerNews/`

**Legacy Mapping:**

#### 1. Forums & Discussion Platforms

**Content/Forums/** → `Source/Text/Forums/`
- Reddit → Already in `Source/Text/Reddit/` ✓
- HackerNews → Already in `Source/Text/HackerNews/` ✓
- Stack Overflow → `Source/Text/Forums/StackOverflow/`
- Quora → `Source/Text/Forums/Quora/`
- Discord Communities → `Source/Text/Forums/Discord/`

#### 2. Articles & Publishing Platforms

**Content/Articles/** → `Source/Text/Articles/`
- Medium → `Source/Text/Articles/Medium/`
- Substack → `Source/Text/Articles/Substack/`
- Dev.to → `Source/Text/Articles/DevTo/`
- Blogs (RSS) → `Source/Text/Articles/Blogs/`

#### 3. News & Information

**Signals/News** → `Source/Text/News/`
- RSS News Aggregator → `Source/Text/News/RSS/`
- NewsAPI → `Source/Text/News/NewsAPI/`
- Google News → `Source/Text/News/GoogleNews/`

#### 4. Trends & Analytics (Text Data)

**Signals/Trends** → `Source/Text/Trends/`
- **GoogleTrends** → `Source/Text/Trends/GoogleTrends/` ⭐
- Trending Topics → `Source/Text/Trends/Topics/`
- Keyword Analyzer → `Source/Text/Trends/Keywords/`

**Signals/Hashtags** → `Source/Text/Trends/Hashtags/`
- Twitter Hashtags → `Source/Text/Trends/Hashtags/Twitter/`
- Instagram Hashtags → `Source/Text/Trends/Hashtags/Instagram/`
- TikTok Hashtags → `Source/Text/Trends/Hashtags/TikTok/`

**Signals/Memes** → `Source/Text/Trends/Memes/`
- Meme Tracker → `Source/Text/Trends/Memes/Tracker/`
- Reddit Memes → `Source/Text/Trends/Memes/Reddit/`

**Signals/Challenges** → `Source/Text/Trends/Challenges/`
- Viral Challenges → `Source/Text/Trends/Challenges/Viral/`

**Signals/Locations** → `Source/Text/Trends/Locations/`
- Location Trends → `Source/Text/Trends/Locations/Trending/`

#### 5. Commerce & E-commerce

**Commerce/** → `Source/Text/Commerce/`
- Amazon Bestsellers → `Source/Text/Commerce/Amazon/`
- Etsy Trending → `Source/Text/Commerce/Etsy/`
- App Store Top Charts → `Source/Text/Commerce/AppStore/`
- Product Hunt → `Source/Text/Commerce/ProductHunt/`

**Rationale:** Product descriptions, reviews, and listings are text-based content.

#### 6. Events & Calendars

**Events/** → `Source/Text/Events/`
- Calendar Holidays → `Source/Text/Events/CalendarHolidays/`
- Sports Highlights → `Source/Text/Events/SportsHighlights/`
- Entertainment Releases → `Source/Text/Events/EntertainmentReleases/`
- Concert Schedules → `Source/Text/Events/Concerts/`

**Rationale:** Event descriptions, schedules, and metadata are text-based.

#### 7. Community & User Feedback

**Community/** → `Source/Text/Community/`
- QA Source → `Source/Text/Community/QASource/`
- Comment Mining → `Source/Text/Community/CommentMining/`
- User Feedback → `Source/Text/Community/UserFeedback/`
- Prompt Box → `Source/Text/Community/PromptBox/`

**Rationale:** User-generated text content and feedback.

#### 8. Creative Content

**Creative/** → `Source/Text/Creative/`
- Lyric Snippets → `Source/Text/Creative/LyricSnippets/`
- Script Beats → `Source/Text/Creative/ScriptBeats/`
- Visual Moodboard (descriptions) → `Source/Text/Creative/VisualMoodboard/`

**Rationale:** Creative text content for inspiration.

#### 9. Internal Tools

**Internal/** → `Source/Text/Internal/`
- CSV Import → `Source/Text/Internal/CSVImport/`
- Manual Backlog → `Source/Text/Internal/ManualBacklog/`

**Rationale:** Structured text data and manual entries.

**Total Text Sources:** 15-30+ sources
- Reddit ✓ (implemented)
- HackerNews ✓ (implemented)
- GoogleTrends ⭐ (recommended next)
- Medium (future)
- Substack (future)
- News APIs (future)
- Commerce sources (future)
- Event sources (future)
- Community sources (future)
- And 15+ more...

**Import Examples:**
```python
# Forums
from Source.Text.Reddit import RedditSource
from Source.Text.HackerNews import HackerNewsSource
from Source.Text.Forums.StackOverflow import StackOverflowSource

# Articles
from Source.Text.Articles.Medium import MediumSource
from Source.Text.Articles.Substack import SubstackSource

# Trends & Analytics (Including GoogleTrends)
from Source.Text.Trends.GoogleTrends import GoogleTrendsSource
from Source.Text.Trends.Hashtags.Twitter import TwitterHashtagsSource
from Source.Text.Trends.Memes import MemeTrackerSource

# Commerce
from Source.Text.Commerce.Amazon import AmazonSource
from Source.Text.Commerce.Etsy import EtsySource

# Events
from Source.Text.Events.CalendarHolidays import HolidaysSource
from Source.Text.Events.SportsHighlights import SportsSource

# Community
from Source.Text.Community.QASource import QASource
from Source.Text.Community.UserFeedback import FeedbackSource

# Creative
from Source.Text.Creative.LyricSnippets import LyricsSource
from Source.Text.Creative.ScriptBeats import ScriptSource

# Internal
from Source.Text.Internal.CSVImport import CSVImportSource
from Source.Text.Internal.ManualBacklog import ManualBacklogSource
```

---

## GoogleTrends Placement: Deep Dive

### Question: Where should GoogleTrends live?

**Answer: `Source/Text/Trends/GoogleTrends/`**

### Rationale

1. **Primary Data Type: Text**
   - Google Trends analyzes keyword search queries
   - Search queries = text strings
   - Trending topics = text-based insights
   - Query comparisons = text analysis

2. **Nature of Content**
   - Input: Text keywords
   - Output: Text-based trend reports
   - Analysis: Text pattern matching
   - Results: Text descriptions and numerical data about text searches

3. **Category Hierarchy**
   - Text/ (primary media type)
   - → Trends/ (sub-category for analytics)
   - → GoogleTrends/ (specific source)

4. **Consistency with Other Analytics**
   - Hashtag Trends → Text/Trends/Hashtags/ (text hashtags)
   - Meme Trends → Text/Trends/Memes/ (text meme descriptions)
   - Keyword Trends → Text/Trends/Keywords/ (text keywords)
   - GoogleTrends → Text/Trends/GoogleTrends/ (text search queries) ✓

5. **Not Video or Audio**
   - GoogleTrends doesn't analyze video content
   - GoogleTrends doesn't analyze audio content
   - GoogleTrends analyzes text search behavior

### Alternative Considered: Data Category

**Why NOT a separate Data category:**
- Would create 4th top-level category (adds complexity)
- "Data" is too abstract (everything is data)
- GoogleTrends produces text-based insights
- Better to keep simple: Video, Audio, Text

### Implementation

**Location:** `Source/Text/Trends/GoogleTrends/`

**Structure:**
```
Source/Text/Trends/GoogleTrends/
├── _meta/
│   ├── docs/
│   ├── examples/
│   ├── scripts/
│   ├── tests/
│   └── issues/
├── src/
│   ├── core/
│   ├── schemas/
│   ├── mappers/
│   └── clients/
├── README.md
├── pyproject.toml
└── requirements.txt
```

**Import:**
```python
from Source.Text.Trends.GoogleTrends import GoogleTrendsSource
```

**Usage:**
```python
# Initialize
trends = GoogleTrendsSource()

# Analyze keywords (text queries)
results = trends.get_trending_keywords(
    keywords=["AI", "machine learning", "ChatGPT"],  # Text input
    timeframe="today 3-m"
)

# Results contain text-based insights
for trend in results:
    print(f"Keyword: {trend.keyword}")  # Text
    print(f"Interest: {trend.interest}")  # Number about text query
    print(f"Related: {trend.related_queries}")  # More text
```

---

## Category Characteristics

### Video
- **Media Format:** Moving visual content
- **Processing:** Video codecs, frame analysis, thumbnails
- **Team Focus:** Video editors, visual content creators
- **Examples:** YouTube, TikTok, Instagram Reels, Twitch

### Audio
- **Media Format:** Sound/audio content
- **Processing:** Audio codecs, waveform analysis, transcription
- **Team Focus:** Audio engineers, podcast producers
- **Examples:** Spotify, Podcasts, SoundCloud, Audio streams

### Text
- **Media Format:** Written content and structured text data
- **Processing:** NLP, text analysis, keyword extraction, sentiment analysis
- **Team Focus:** Content writers, data analysts, researchers
- **Examples:** Reddit, HackerNews, GoogleTrends, Medium, News, Commerce, Events

**Key Insight:** Text category is the most versatile and includes:
- Pure text content (articles, forums, blogs)
- Text-based analytics (trends, keywords, hashtags)
- Text-rich structured data (commerce, events, calendars)
- Text conversations (community, Q&A, comments)

---

## Migration Priority

### Phase 1: Current (Implemented)
1. ✅ YouTube → Video/YouTube/
2. ✅ Reddit → Text/Reddit/
3. ✅ HackerNews → Text/HackerNews/

### Phase 2: High Priority (Next)
4. GoogleTrends → Text/Trends/GoogleTrends/ ⭐ **RECOMMENDED**
5. TikTok → Video/TikTok/
6. Medium → Text/Articles/Medium/

### Phase 3: Medium Priority
7. Spotify Podcasts → Audio/Podcasts/Spotify/
8. Instagram → Video/Instagram/
9. Twitter Hashtags → Text/Trends/Hashtags/Twitter/
10. Amazon → Text/Commerce/Amazon/

### Phase 4: Lower Priority
11-27. Remaining 15+ sources from legacy

---

## Benefits of Simplified Structure

### 1. Cognitive Simplicity
- **3 categories** at root (optimal for human cognition)
- No confusion about placement
- Easy to explain to new team members

### 2. Universal Understanding
- Video, Audio, Text = universally understood
- No domain-specific jargon
- Works across cultures and languages

### 3. Technical Alignment
- Processing pipelines match media types
- Video team handles video sources
- Audio team handles audio sources
- Text/Data team handles text sources

### 4. Scalability
- Each category can grow independently
- Sub-categories provide organization
- No need to restructure as sources grow

### 5. Predictable Imports
```python
# Pattern is always clear:
from Source.{MediaType}.{SourceName} import Source
from Source.Video.YouTube import YouTubeSource
from Source.Audio.Spotify import SpotifySource
from Source.Text.GoogleTrends import GoogleTrendsSource
```

---

## Summary

**Current Structure:**
```
Source/
├── Video/     # 5-10 sources (YouTube ✓, TikTok, Instagram, Twitch, etc.)
├── Audio/     # 3-8 sources (Podcasts, Spotify, SoundCloud, etc.)
└── Text/      # 15-30+ sources (Reddit ✓, HackerNews ✓, GoogleTrends ⭐, Medium, News, Commerce, Events, etc.)
```

**Total Legacy Sources Mapped:** 27+
- Video category: 5-10 sources
- Audio category: 3-8 sources  
- Text category: 15-30+ sources

**GoogleTrends Placement:** `Source/Text/Trends/GoogleTrends/`
- Text-based keyword analysis
- Consistent with other trend sources
- Natural fit in Text/Trends/ hierarchy

**Next Recommended Implementation:** GoogleTrends (high value, clear text categorization)

---

## Questions & Answers

**Q: Why not a separate "Data" category for analytics like GoogleTrends?**
**A:** "Data" is too abstract (everything is data). GoogleTrends analyzes text keywords, so it naturally belongs in Text/Trends/. Keeping only 3 top-level categories (Video, Audio, Text) maximizes simplicity.

**Q: Where do memes go (they're images)?**
**A:** Text/Trends/Memes/ - Memes are shared via text platforms with text captions. The searchable/trendable part is the text description.

**Q: Where does video metadata go?**
**A:** With the video source (e.g., YouTube/src/schemas/metadata.py). Metadata travels with its media type.

**Q: What about multimodal sources (text + images)?**
**A:** Categorize by primary media type. Blog posts with images → Text/Articles/. Social media with video → Video/. Choose based on core format.

**Q: Can sources be in multiple categories?**
**A:** No. Each source has one canonical location based on its primary media type. Use metadata/tags for cross-referencing if needed.

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-11  
**Author:** GitHub Copilot  
**Status:** Final Recommendation
