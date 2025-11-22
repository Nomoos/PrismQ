# PrismQ.T.Idea.Inspiration Directory Structure - Platform-First Architecture

**Date**: 2025-11-16  
**Pattern**: Template Method with Platform-First Hierarchy  
**MVP**: YouTube Platform + yt-dlp Integration

---

## Current Structure (Media-First - 5 Levels) ⚠️ DEPRECATED

```
PrismQ.T.Idea.Inspiration/
├── Source/
│   ├── src/
│   │   └── core/
│   │       ├── base_worker.py              # Level 1: Task processing
│   │       ├── base_source_worker.py       # Level 2: Config, database
│   │       └── __init__.py
│   │
│   ├── Video/                               # ❌ MEDIA TYPE LAYER (to be removed)
│   │   ├── src/
│   │   │   └── core/
│   │   │       ├── base_video_source_worker.py  # Level 3: Video operations
│   │   │       └── __init__.py
│   │   │
│   │   └── YouTube/                         # Platform under media type
│   │       ├── src/
│   │       │   └── workers/
│   │       │       ├── base_youtube_worker.py   # Level 4: YouTube operations
│   │       │       └── __init__.py
│   │       │
│   │       └── Video/                       # Endpoint under platform
│   │           └── src/
│   │               └── workers/
│   │                   ├── youtube_video_worker_refactored.py  # Level 5
│   │                   └── __init__.py
│   │
│   ├── Audio/                               # ❌ MEDIA TYPE LAYER
│   │   └── ...
│   │
│   └── Text/                                # ❌ MEDIA TYPE LAYER
│       └── ...
│
└── Research_Layers/
    └── 02_Design_Patterns/
        ├── TEMPLATE_METHOD_SUMMARY.md
        ├── TEMPLATE_METHOD_WORKER_HIERARCHY.md
        ├── TEMPLATE_METHOD_ALTERNATIVES_ANALYSIS.md
        ├── WHY_VIDEO_TEXT_AUDIO_SEPARATION.md      # OUTDATED
        ├── WHEN_TO_UNIFY_TO_TEXT.md
        ├── TEMPLATE_METHOD_JUSTIFICATION.md
        ├── MEDIA_TYPE_RECATEGORIZATION.md
        └── DIRECTORY_STRUCTURE_PLATFORMFIRST.md    # THIS FILE
```

**Problems with Current Structure**:
- ❌ Media type layer adds unnecessary complexity (5 levels)
- ❌ Platform (YouTube) nested under media type (Video)
- ❌ Difficult to find: `Source/Video/YouTube/Video/src/workers/`
- ❌ Implies media type is more important than platform (wrong!)
- ❌ Hard to add cross-media platforms (YouTube has videos AND podcasts)

---

## Recommended Structure (Platform-First - 4 Levels) ✅

### Overview

```
PrismQ.T.Idea.Inspiration/
├── Source/
│   ├── src/
│   │   ├── core/
│   │   │   ├── base_worker.py              # Level 1: Task processing
│   │   │   ├── base_source_worker.py       # Level 2: Config, database
│   │   │   └── __init__.py
│   │   │
│   │   └── utils/
│   │       ├── video_utils.py              # Video helpers (not hierarchy!)
│   │       ├── text_utils.py               # Text helpers
│   │       ├── audio_utils.py              # Audio helpers
│   │       └── __init__.py
│   │
│   ├── YouTube/                             # ✅ PLATFORM LAYER (Level 3)
│   │   ├── src/
│   │   │   └── workers/
│   │   │       ├── base_youtube_worker.py  # Level 3: YouTube + yt-dlp
│   │   │       └── __init__.py
│   │   │
│   │   ├── Video/                           # ✅ ENDPOINT LAYER (Level 4)
│   │   │   └── src/
│   │   │       └── workers/
│   │   │           ├── youtube_video_worker.py
│   │   │           └── __init__.py
│   │   │
│   │   ├── Channel/                         # ✅ ENDPOINT LAYER (Level 4)
│   │   │   └── src/
│   │   │       └── workers/
│   │   │           ├── youtube_channel_worker.py
│   │   │           └── __init__.py
│   │   │
│   │   ├── Playlist/                        # ✅ ENDPOINT LAYER (Level 4)
│   │   │   └── src/
│   │   │       └── workers/
│   │   │           ├── youtube_playlist_worker.py
│   │   │           └── __init__.py
│   │   │
│   │   └── Search/                          # ✅ ENDPOINT LAYER (Level 4)
│   │       └── src/
│   │           └── workers/
│   │               ├── youtube_search_worker.py
│   │               └── __init__.py
│   │
│   ├── Reddit/                              # ✅ PLATFORM LAYER (Level 3)
│   │   ├── src/
│   │   │   └── workers/
│   │   │       ├── base_reddit_worker.py   # Level 3: Reddit API
│   │   │       └── __init__.py
│   │   │
│   │   ├── Posts/                           # ✅ ENDPOINT LAYER (Level 4)
│   │   │   └── src/
│   │   │       └── workers/
│   │   │           ├── reddit_posts_worker.py
│   │   │           └── __init__.py
│   │   │
│   │   └── Comments/                        # ✅ ENDPOINT LAYER (Level 4)
│   │       └── src/
│   │           └── workers/
│   │               ├── reddit_comments_worker.py
│   │               └── __init__.py
│   │
│   ├── TikTok/                              # ✅ PLATFORM LAYER (Level 3)
│   │   ├── src/
│   │   │   └── workers/
│   │   │       ├── base_tiktok_worker.py   # Level 3: TikTok API
│   │   │       └── __init__.py
│   │   │
│   │   └── Video/                           # ✅ ENDPOINT LAYER (Level 4)
│   │       └── src/
│   │           └── workers/
│   │               ├── tiktok_video_worker.py
│   │               └── __init__.py
│   │
│   ├── Spotify/                             # ✅ PLATFORM LAYER (Level 3)
│   │   ├── src/
│   │   │   └── workers/
│   │   │       ├── base_spotify_worker.py  # Level 3: Spotify API
│   │   │       └── __init__.py
│   │   │
│   │   └── Podcast/                         # ✅ ENDPOINT LAYER (Level 4)
│   │       └── src/
│   │           └── workers/
│   │               ├── spotify_podcast_worker.py
│   │               └── __init__.py
│   │
│   ├── HackerNews/                          # ✅ PLATFORM LAYER (Level 3)
│   │   ├── src/
│   │   │   └── workers/
│   │   │       ├── base_hackernews_worker.py  # Level 3: HN API
│   │   │       └── __init__.py
│   │   │
│   │   └── Posts/                           # ✅ ENDPOINT LAYER (Level 4)
│   │       └── src/
│   │           └── workers/
│   │               ├── hackernews_posts_worker.py
│   │               └── __init__.py
│   │
│   └── TaskManager/                         # Task coordination service
│       └── src/
│           └── ...
│
├── Research_Layers/
│   └── 02_Design_Patterns/
│       ├── TEMPLATE_METHOD_SUMMARY.md
│       ├── TEMPLATE_METHOD_WORKER_HIERARCHY.md
│       ├── TEMPLATE_METHOD_ALTERNATIVES_ANALYSIS.md
│       ├── WHEN_TO_UNIFY_TO_TEXT.md
│       ├── TEMPLATE_METHOD_JUSTIFICATION.md
│       ├── MEDIA_TYPE_RECATEGORIZATION.md
│       └── DIRECTORY_STRUCTURE_PLATFORMFIRST.md
│
├── Model/                                   # IdeaInspiration model
├── Classification/                          # Content classification
├── Scoring/                                 # Content scoring
└── ConfigLoad/                              # Configuration management
```

### Benefits of Platform-First Structure

1. ✅ **Clear hierarchy**: Platform → Endpoint (not Media → Platform → Endpoint)
2. ✅ **Easier navigation**: `Source/YouTube/Video/` vs `Source/Video/YouTube/Video/`
3. ✅ **Platform as primary**: Reflects that YouTube API differs more from Reddit API than video differs from text
4. ✅ **Flexible content types**: YouTube can have videos, podcasts, livestreams under same platform
5. ✅ **Simpler**: 4 levels instead of 5

---

## Detailed Structure: YouTube Platform (MVP)

### Complete YouTube Directory Structure

```
Source/YouTube/
├── README.md                                # YouTube platform documentation
│
├── src/
│   ├── workers/
│   │   ├── base_youtube_worker.py          # Level 3: Base YouTube Worker
│   │   │   # - yt-dlp integration (no API limits)
│   │   │   # - YouTube API client (optional)
│   │   │   # - Quota management
│   │   │   # - YouTube-specific error handling
│   │   │   # - Subtitle extraction
│   │   │   # - Video metadata extraction
│   │   │   # - Inherits from: BaseSourceWorker
│   │   │
│   │   └── __init__.py
│   │
│   ├── extractors/                          # Content extraction strategies
│   │   ├── subtitle_extractor.py           # yt-dlp subtitle extraction
│   │   ├── ytdlp_extractor.py              # yt-dlp video extraction
│   │   ├── whisper_extractor.py            # Whisper transcription
│   │   ├── whisperx_extractor.py           # WhisperX transcription
│   │   ├── description_extractor.py        # AI video description
│   │   └── __init__.py
│   │
│   ├── clients/
│   │   ├── ytdlp_client.py                 # yt-dlp wrapper
│   │   ├── youtube_api_client.py           # YouTube Data API v3
│   │   └── __init__.py
│   │
│   └── utils/
│       ├── quota_manager.py                # Quota tracking
│       ├── video_validator.py              # Video metadata validation
│       └── __init__.py
│
├── Video/                                   # Video endpoint
│   ├── README.md
│   │
│   ├── src/
│   │   └── workers/
│   │       ├── youtube_video_worker.py     # Level 4: YouTube Video Worker
│   │       │   # - Single video scraping
│   │       │   # - Video search
│   │       │   # - Inherits from: BaseYouTubeWorker
│   │       │
│   │       └── __init__.py
│   │
│   └── _meta/
│       ├── docs/
│       ├── tests/
│       └── examples/
│
├── Channel/                                 # Channel endpoint
│   ├── README.md
│   │
│   ├── src/
│   │   └── workers/
│   │       ├── youtube_channel_worker.py   # Level 4: Channel Worker
│   │       │   # - Channel metadata scraping
│   │       │   # - Channel video listing
│   │       │   # - Subscriber tracking
│   │       │   # - Inherits from: BaseYouTubeWorker
│   │       │
│   │       └── __init__.py
│   │
│   └── _meta/
│
├── Playlist/                                # Playlist endpoint
│   ├── README.md
│   │
│   ├── src/
│   │   └── workers/
│   │       ├── youtube_playlist_worker.py  # Level 4: Playlist Worker
│   │       │   # - Playlist metadata
│   │       │   # - Video list extraction
│   │       │   # - Inherits from: BaseYouTubeWorker
│   │       │
│   │       └── __init__.py
│   │
│   └── _meta/
│
├── Search/                                  # Search endpoint
│   ├── README.md
│   │
│   ├── src/
│   │   └── workers/
│   │       ├── youtube_search_worker.py    # Level 4: Search Worker
│   │       │   # - Keyword search
│   │       │   # - Trending videos
│   │       │   # - Inherits from: BaseYouTubeWorker
│   │       │
│   │       └── __init__.py
│   │
│   └── _meta/
│
└── _meta/
    ├── docs/
    │   └── youtube_api.md                  # YouTube API documentation
    ├── tests/
    │   ├── test_base_youtube_worker.py
    │   ├── test_ytdlp_integration.py
    │   └── test_subtitle_extraction.py
    └── examples/
        └── youtube_video_example.py
```

---

## Import Paths (Platform-First)

### Level 1: BaseWorker
```python
from Source.src.core.base_worker import BaseWorker, Task, TaskResult
```

### Level 2: BaseSourceWorker
```python
from Source.src.core.base_source_worker import BaseSourceWorker
```

### Level 3: Platform Workers
```python
# YouTube
from Source.YouTube.src.workers.base_youtube_worker import BaseYouTubeWorker

# Reddit
from Source.Reddit.src.workers.base_reddit_worker import BaseRedditWorker

# TikTok
from Source.TikTok.src.workers.base_tiktok_worker import BaseTikTokWorker

# Spotify
from Source.Spotify.src.workers.base_spotify_worker import BaseSpotifyWorker
```

### Level 4: Endpoint Workers
```python
# YouTube endpoints
from Source.YouTube.Video.src.workers.youtube_video_worker import YouTubeVideoWorker
from Source.YouTube.Channel.src.workers.youtube_channel_worker import YouTubeChannelWorker
from Source.YouTube.Playlist.src.workers.youtube_playlist_worker import YouTubePlaylistWorker
from Source.YouTube.Search.src.workers.youtube_search_worker import YouTubeSearchWorker

# Reddit endpoints
from Source.Reddit.Posts.src.workers.reddit_posts_worker import RedditPostsWorker
from Source.Reddit.Comments.src.workers.reddit_comments_worker import RedditCommentsWorker

# TikTok endpoints
from Source.TikTok.Video.src.workers.tiktok_video_worker import TikTokVideoWorker

# Spotify endpoints
from Source.Spotify.Podcast.src.workers.spotify_podcast_worker import SpotifyPodcastWorker
```

### Utilities (Not Hierarchy!)
```python
# Video utilities
from Source.src.utils.video_utils import parse_duration, validate_video_metadata

# Text utilities
from Source.src.utils.text_utils import parse_markdown, calculate_readability

# Audio utilities
from Source.src.utils.audio_utils import extract_audio, transcribe_audio
```

### Extractors (Visitor Pattern)
```python
# YouTube extractors
from Source.YouTube.src.extractors.subtitle_extractor import SubtitleExtractor
from Source.YouTube.src.extractors.ytdlp_extractor import YtDlpExtractor
from Source.YouTube.src.extractors.whisper_extractor import WhisperExtractor
```

---

## Class Hierarchy (Platform-First)

### Inheritance Chain

```
BaseWorker (Level 1)
    ↓ inherits
BaseSourceWorker (Level 2)
    ↓ inherits
BaseYouTubeWorker (Level 3) ← PLATFORM LAYER
    ↓ inherits
YouTubeVideoWorker (Level 4) ← ENDPOINT LAYER


BaseWorker (Level 1)
    ↓ inherits
BaseSourceWorker (Level 2)
    ↓ inherits
BaseRedditWorker (Level 3) ← PLATFORM LAYER
    ↓ inherits
RedditPostsWorker (Level 4) ← ENDPOINT LAYER


BaseWorker (Level 1)
    ↓ inherits
BaseSourceWorker (Level 2)
    ↓ inherits
BaseTikTokWorker (Level 3) ← PLATFORM LAYER
    ↓ inherits
TikTokVideoWorker (Level 4) ← ENDPOINT LAYER
```

### Parallel Platform Hierarchies

```
                    BaseWorker
                        ↓
                 BaseSourceWorker
                        ↓
        ┌───────────────┼───────────────────┬──────────────┐
        ↓               ↓                   ↓              ↓
BaseYouTubeWorker  BaseRedditWorker  BaseTikTokWorker  BaseSpotifyWorker
        ↓               ↓                   ↓              ↓
    ┌───┼───┬───┐       ├──────┐            ↓              ↓
    ↓   ↓   ↓   ↓       ↓      ↓            ↓              ↓
  Video Channel     Posts Comments       Video          Podcast
        Playlist
        Search
```

---

## File Organization Conventions

### Naming Convention

- **Platform folders**: PascalCase (e.g., `YouTube`, `Reddit`, `TikTok`)
- **Endpoint folders**: PascalCase (e.g., `Video`, `Channel`, `Posts`)
- **Python files**: snake_case (e.g., `base_youtube_worker.py`, `youtube_video_worker.py`)
- **Classes**: PascalCase (e.g., `BaseYouTubeWorker`, `YouTubeVideoWorker`)

### File Structure Pattern

Every platform and endpoint follows this pattern:

```
Platform/
├── README.md                    # Platform overview
├── src/
│   └── workers/
│       ├── base_platform_worker.py  # Base worker for platform
│       └── __init__.py
│
├── Endpoint1/
│   ├── README.md
│   ├── src/
│   │   └── workers/
│   │       ├── platform_endpoint1_worker.py
│   │       └── __init__.py
│   └── _meta/
│
├── Endpoint2/
│   └── ...
│
└── _meta/
    ├── docs/
    ├── tests/
    └── examples/
```

---

## Metadata Storage (Content Type as Field)

### IdeaInspiration Model

```python
class IdeaInspiration:
    """Unified idea representation."""
    
    id: str
    title: str
    content: str  # Extracted text (unified)
    
    # Metadata (NOT class hierarchy!)
    metadata: dict = {
        'platform': 'youtube',           # Platform name
        'content_type': 'video',         # video, audio, text, image, live, short
        'endpoint': 'video',             # video, channel, playlist, search
        'source_url': 'https://...',
        'extraction_method': 'ytdlp_subtitles',  # How text was extracted
        
        # Platform-specific metadata
        'platform_metadata': {
            'duration': 3730,            # Video-specific
            'view_count': 1000000,       # Video-specific
            'like_count': 50000,         # Video-specific
            'thumbnail_url': 'https://...', # Video-specific
            'video_quality': '1080p',    # Video-specific
            
            # OR for Reddit
            'score': 450,                # Reddit-specific
            'num_comments': 120,         # Reddit-specific
            'upvotes': 320,              # Reddit-specific
            'subreddit': 'python',       # Reddit-specific
        },
        
        # Timestamps
        'scraped_at': '2025-11-16T10:00:00Z',
        'published_at': '2025-11-10T15:30:00Z',
    }
```

### Content Type Field Values

```python
CONTENT_TYPES = [
    'video',         # Standard video content
    'short',         # Short-form video (TikTok, YouTube Shorts)
    'livestream',    # Live streaming content
    'podcast',       # Audio podcast
    'audio',         # Other audio content
    'text',          # Text-only content (posts, articles)
    'image',         # Image content
    'thread',        # Discussion thread
    'comment',       # Comment/reply
    'other',         # Other content types
]
```

---

## Migration Guide: Media-First to Platform-First

### Step 1: Create Platform Directory Structure

```bash
# Create platform directories
mkdir -p Source/YouTube/src/workers
mkdir -p Source/YouTube/Video/src/workers
mkdir -p Source/YouTube/Channel/src/workers
mkdir -p Source/Reddit/src/workers
mkdir -p Source/Reddit/Posts/src/workers
mkdir -p Source/TikTok/src/workers
mkdir -p Source/TikTok/Video/src/workers
```

### Step 2: Move Base Workers

```bash
# Move BaseYouTubeWorker up one level
mv Source/Video/YouTube/src/workers/base_youtube_worker.py \
   Source/YouTube/src/workers/base_youtube_worker.py

# Move endpoint workers
mv Source/Video/YouTube/Video/src/workers/youtube_video_worker_refactored.py \
   Source/YouTube/Video/src/workers/youtube_video_worker.py
```

### Step 3: Convert BaseVideoSourceWorker to Utilities

```bash
# Create utils directory
mkdir -p Source/src/utils

# Convert BaseVideoSourceWorker to utility functions
# Extract methods to video_utils.py
```

```python
# Source/src/utils/video_utils.py
"""Video utility functions (not a class hierarchy!)."""

def parse_duration(duration_str: str) -> int:
    """Parse ISO 8601 duration to seconds."""
    # Implementation from BaseVideoSourceWorker
    pass

def validate_video_metadata(data: dict) -> bool:
    """Validate video metadata."""
    # Implementation from BaseVideoSourceWorker
    pass

def calculate_engagement_rate(data: dict) -> float:
    """Calculate engagement rate."""
    # Implementation from BaseVideoSourceWorker
    pass
```

### Step 4: Update BaseYouTubeWorker

```python
# Source/YouTube/src/workers/base_youtube_worker.py
from Source.src.core.base_source_worker import BaseSourceWorker
from Source.src.utils.video_utils import parse_duration, validate_video_metadata

class BaseYouTubeWorker(BaseSourceWorker):  # Inherit directly from Level 2!
    """Base worker for YouTube platform.
    
    Level 3: Platform-specific operations.
    - yt-dlp integration (no API limits)
    - YouTube API client (optional)
    - Subtitle extraction
    - Video metadata extraction
    """
    
    def __init__(self, ...):
        super().__init__(...)
        self.ytdlp = YtDlpClient()
        self.youtube_api = YouTubeAPIClient() if use_api else None
    
    def fetch_video_metadata(self, video_id: str) -> dict:
        """Fetch video metadata using yt-dlp."""
        return self.ytdlp.extract_info(video_id)
    
    def extract_subtitles(self, video_id: str) -> str:
        """Extract subtitles using yt-dlp."""
        return self.ytdlp.download_subtitles(video_id)
    
    # Can still use video utilities!
    def parse_duration(self, duration: str) -> int:
        """Parse duration using utility function."""
        return parse_duration(duration)  # From utils
```

### Step 5: Update Import Paths

```python
# OLD (media-first)
from Source.Video.YouTube.src.workers.base_youtube_worker import BaseYouTubeWorker
from Source.Video.YouTube.Video.src.workers.youtube_video_worker_refactored import YouTubeVideoWorker

# NEW (platform-first)
from Source.YouTube.src.workers.base_youtube_worker import BaseYouTubeWorker
from Source.YouTube.Video.src.workers.youtube_video_worker import YouTubeVideoWorker
```

### Step 6: Update Content Type to Metadata

```python
# OLD (media type in hierarchy)
class BaseVideoSourceWorker(BaseSourceWorker):  # Media type as class
    pass

# NEW (media type as metadata field)
class BaseSourceWorker:
    def create_inspiration(self, ..., content_type: str = 'video'):
        return IdeaInspiration(
            content=text,
            metadata={
                'platform': 'youtube',
                'content_type': content_type,  # Just a field!
                # ...
            }
        )
```

### Step 7: Remove Old Media Type Directories

```bash
# After migration is complete and tested
rm -rf Source/Video/YouTube  # Old location
rm -rf Source/Audio/Spotify  # Old location
rm -rf Source/Text/Reddit    # Old location
```

---

## MVP Directory Structure (YouTube Only)

For MVP implementation, focus on YouTube platform only:

```
Source/
├── src/
│   ├── core/
│   │   ├── base_worker.py              # Level 1 ✅
│   │   ├── base_source_worker.py       # Level 2 ✅
│   │   └── __init__.py
│   │
│   └── utils/
│       ├── video_utils.py              # Video helpers ✅
│       └── __init__.py
│
├── YouTube/                             # Level 3 ✅
│   ├── README.md
│   │
│   ├── src/
│   │   ├── workers/
│   │   │   ├── base_youtube_worker.py  # yt-dlp + YouTube API ✅
│   │   │   └── __init__.py
│   │   │
│   │   ├── extractors/
│   │   │   ├── subtitle_extractor.py   # Primary method ✅
│   │   │   ├── whisper_extractor.py    # Fallback ✅
│   │   │   └── __init__.py
│   │   │
│   │   └── clients/
│   │       ├── ytdlp_client.py         # yt-dlp wrapper ✅
│   │       └── __init__.py
│   │
│   ├── Video/                           # Level 4 ✅
│   │   ├── README.md
│   │   │
│   │   └── src/
│   │       └── workers/
│   │           ├── youtube_video_worker.py  # Single video ✅
│   │           └── __init__.py
│   │
│   └── _meta/
│       ├── docs/
│       ├── tests/
│       └── examples/
│
└── TaskManager/
    └── ...
```

**MVP Checklist**:
- ✅ Level 1: BaseWorker (task processing)
- ✅ Level 2: BaseSourceWorker (config, database)
- ✅ Level 3: BaseYouTubeWorker (yt-dlp + extractors)
- ✅ Level 4: YouTubeVideoWorker (single video endpoint)
- ✅ Subtitle extraction via yt-dlp (primary method)
- ✅ Whisper extraction (fallback)
- ✅ No API limits (yt-dlp based)
- ✅ Content type as metadata field

---

## Summary

### Key Differences: Media-First vs Platform-First

| Aspect | Media-First (Old) | Platform-First (New) |
|--------|-------------------|----------------------|
| **Hierarchy** | 5 levels | 4 levels |
| **Structure** | Media → Platform → Endpoint | Platform → Endpoint |
| **Example Path** | `Source/Video/YouTube/Video/` | `Source/YouTube/Video/` |
| **Media Type** | Class hierarchy (Level 3) | Metadata field |
| **Flexibility** | Limited (media type fixed) | High (platform can have any content type) |
| **Navigation** | Complex (5 levels deep) | Simple (4 levels) |
| **Extensibility** | Add media types (wrong) | Add platforms (correct) |
| **Code Reuse** | Moderate | High |
| **Imports** | Long, nested | Short, flat |

### Platform-First Advantages

1. ✅ **Simpler**: 4 levels instead of 5
2. ✅ **More accurate**: Platform is the real differentiator
3. ✅ **More flexible**: YouTube can handle videos, podcasts, shorts, livestreams
4. ✅ **Easier to navigate**: `Source/YouTube/Video/` vs `Source/Video/YouTube/Video/`
5. ✅ **Easier to extend**: Add new platforms (Reddit, TikTok), not media types
6. ✅ **Better separation**: Content extraction via Visitor pattern (strategies)
7. ✅ **Clearer naming**: Platform name directly under Source/
8. ✅ **Consistent**: All platforms at same level (Source/YouTube, Source/Reddit, Source/TikTok)

### Content Type Handling

**Old Way** (Media-First):
```python
class BaseVideoSourceWorker(BaseSourceWorker):  # Video IS-A hierarchy
    pass

class BaseYouTubeWorker(BaseVideoSourceWorker):  # YouTube IS-A Video
    pass
```

**New Way** (Platform-First):
```python
class BaseYouTubeWorker(BaseSourceWorker):  # YouTube IS-A Source (directly!)
    pass

# Content type is metadata
metadata['content_type'] = 'video'  # Just a field!
```

---

**Last Updated**: 2025-11-16  
**Author**: PrismQ.T.Idea.Inspiration Team  
**Status**: Recommended for Implementation
