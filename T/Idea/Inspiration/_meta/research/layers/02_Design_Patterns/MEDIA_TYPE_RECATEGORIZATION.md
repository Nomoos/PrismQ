# Media Type Categorization - Rethinking the Structure

**Question**: Should we keep media type categorization (Video/Audio/Text/Other)? Is it correct? How should we structure this with Template Method?

**User's Concerns**:
1. Current categorization (Video/Audio/Text/Other) might not be correct
2. Should media type category be removed or replaced?
3. MVP should focus on: subtitle extraction, YouTube platform, single video extraction, yt-dlp (no API limits)

---

## Analysis: Is Media Type Categorization Correct?

### Current Structure (What We Built)

```
BaseWorker
  ↓
BaseSourceWorker
  ↓
BaseVideoSourceWorker ← Media type level
  ↓
BaseYouTubeWorker ← Platform level
  ↓
YouTubeVideoWorker ← Endpoint level
```

### User's Valid Concern

**The problem**: Media type (Video/Audio/Text) might be the wrong abstraction because:
1. **All become text eventually** - Video → subtitles, Audio → transcript, Text → already text
2. **Processing is similar** - All go through: fetch → filter → extract text → store
3. **Metadata varies more by platform** - YouTube has views/likes, Reddit has upvotes/karma
4. **Extraction method is orthogonal** - Can use yt-dlp for video, whisper for audio, but these are tools, not types

---

## Proposed Alternative Structures

### Option 1: Platform-First (NO Media Type Layer) ✅ RECOMMENDED

```
BaseWorker (task processing)
  ↓
BaseSourceWorker (config, database)
  ↓
BasePlatformWorker (platform-specific: API, scraping, auth)
  ├─ BaseYouTubeWorker
  │    ├─ YouTubeVideoWorker
  │    ├─ YouTubeChannelWorker
  │    └─ YouTubePlaylistWorker
  ├─ BaseRedditWorker
  │    ├─ RedditPostsWorker
  │    └─ RedditCommentsWorker
  ├─ BaseTikTokWorker
  │    └─ TikTokVideoWorker
  └─ BaseSpotifyWorker
       └─ SpotifyPodcastWorker
```

**Why This Works Better**:
- ✅ **Platform is the real differentiator** - YouTube API vs Reddit API vs TikTok API
- ✅ **Media type becomes metadata** - Just a field: `content_type = 'video'`
- ✅ **Extraction is a strategy** - Use Visitor pattern for different extraction methods
- ✅ **Simpler hierarchy** - Only 4 levels instead of 5
- ✅ **More flexible** - YouTube can have videos, podcasts, audio-only content

**Extraction handled by Visitor**:
```python
class BaseYouTubeWorker:
    def extract_content(self, item_data, method='auto'):
        # Visitor pattern - choose extractor
        if method == 'auto':
            if item_data.get('has_subtitles'):
                return SubtitleExtractor().extract(item_data)
            elif item_data.get('has_audio'):
                return WhisperExtractor().extract(item_data)
        # ... fallback methods
```

### Option 2: Content-Type as Strategy (NO Media Type Layer)

```
BaseWorker (task processing)
  ↓
BaseSourceWorker (config, database)
  ↓
BasePlatformWorker (platform operations)
  ↓
PlatformContentWorker (uses ContentExtractionStrategy)
    - strategy: TextExtractor | VideoExtractor | AudioExtractor
```

**Content Type as Injectable Strategy**:
```python
class YouTubeVideoWorker(BaseYouTubeWorker):
    def __init__(self, ...):
        super().__init__(...)
        # Inject extraction strategy based on content type
        self.extractor = self._create_extractor()
    
    def _create_extractor(self):
        # Factory method for extractor
        if self.content_has_subtitles():
            return SubtitleExtractor()
        elif self.content_is_video():
            return VideoExtractor()  # yt-dlp
        elif self.content_is_audio():
            return AudioExtractor()  # whisper
```

### Option 3: Hybrid - Keep Media as Metadata, Not Hierarchy

```
BaseWorker (task processing)
  ↓
BaseSourceWorker (config, database, media_type metadata)
  ↓
BaseYouTubeWorker (YouTube platform)
  ↓
YouTubeContentWorker (handles all content types)
    - Delegates to extractors based on media_type
```

**Media Type as Field**:
```python
class BaseSourceWorker:
    def __init__(self, ..., media_type: str = 'auto'):
        self.media_type = media_type  # 'video', 'audio', 'text', 'auto'
        # Not part of class hierarchy!

class YouTubeContentWorker(BaseYouTubeWorker):
    def process_task(self, task):
        content = self.fetch_content(task.content_id)
        
        # Determine media type (if auto)
        if self.media_type == 'auto':
            detected_type = self._detect_media_type(content)
        else:
            detected_type = self.media_type
        
        # Extract based on detected type
        extractor = self._get_extractor(detected_type)
        text = extractor.extract(content)
        
        return self.create_inspiration(text, content)
```

---

## Recommendation: Platform-First Structure

### Why Remove Media Type Layer?

1. **Media type is metadata, not a class responsibility**
   - YouTube video vs TikTok video differ more by platform than by being videos
   - Reddit post vs HackerNews post differ more by platform than by being text

2. **Extraction method is orthogonal to media type**
   - Can extract video with: yt-dlp, youtube-dl, direct API, web scraping
   - Can extract audio with: whisper, whisperx, google speech-to-text
   - These are tools/strategies, not type hierarchies

3. **Platform determines operations, not media**
   - YouTube: quota management, API authentication, video quality selection
   - Reddit: karma tracking, subreddit rules, comment threading
   - Spotify: playlist management, artist tracking, episode handling

4. **Content type varies within platform**
   - YouTube has: videos, shorts, podcasts, music, live streams
   - Reddit has: posts, comments, images, videos
   - Forcing into Video/Audio/Text loses nuance

### Revised 4-Level Hierarchy (Recommended)

```
Level 1: BaseWorker
  - Task claiming, processing loop, result reporting
  - Platform-agnostic task management

Level 2: BaseSourceWorker
  - Configuration management
  - Database operations
  - Result persistence
  - Metadata handling (including media_type field)

Level 3: BasePlatformWorker (platform-specific)
  - BaseYouTubeWorker: YouTube API, quota, yt-dlp integration
  - BaseRedditWorker: Reddit API, karma, subreddit rules
  - BaseTikTokWorker: TikTok API, challenges, hashtags
  - BaseSpotifyWorker: Spotify API, playlists, episodes

Level 4: PlatformEndpointWorker (endpoint-specific)
  - YouTubeVideoWorker: Video scraping
  - YouTubeChannelWorker: Channel scraping
  - RedditPostsWorker: Post scraping
  - RedditCommentsWorker: Comment scraping
```

**Content Extraction via Visitor Pattern**:
```python
# Extractors (Visitor pattern)
class ContentExtractor(ABC):
    @abstractmethod
    def extract(self, content_data: dict) -> str:
        pass

class SubtitleExtractor(ContentExtractor):
    """Extract from subtitles (fastest, most accurate)."""
    def extract(self, content_data):
        return download_subtitles(content_data['id'])

class YtDlpExtractor(ContentExtractor):
    """Extract using yt-dlp (no API limits)."""
    def extract(self, content_data):
        return ytdlp.extract_info(content_data['url'])

class WhisperExtractor(ContentExtractor):
    """Extract using Whisper STT (local GPU)."""
    def extract(self, content_data):
        audio = download_audio(content_data['url'])
        return whisper.transcribe(audio)

# Usage in worker
class BaseYouTubeWorker:
    def extract_content_text(self, content_data, method='auto'):
        extractor = self._choose_extractor(method, content_data)
        return extractor.extract(content_data)
    
    def _choose_extractor(self, method, content_data):
        if method == 'auto':
            if content_data.get('has_subtitles'):
                return SubtitleExtractor()
            elif self.config.prefer_ytdlp:
                return YtDlpExtractor()
            else:
                return WhisperExtractor()
        # ... explicit method selection
```

---

## MVP Implementation: YouTube + yt-dlp + Subtitle Extraction

### MVP Focus (Per User Request)

1. ✅ **Platform**: YouTube only
2. ✅ **Method**: yt-dlp (no API limits) + subtitle extraction
3. ✅ **Scope**: Single video extraction
4. ✅ **Structure**: Platform-first (no media type layer)

### MVP Architecture

```
BaseWorker
  ↓
BaseSourceWorker
  ↓
BaseYouTubeWorker
  - Uses yt-dlp for video metadata (no API quota!)
  - Supports subtitle extraction
  - Supports audio extraction with Whisper (fallback)
  ↓
YouTubeVideoWorker
  - Fetches single video
  - Extracts subtitles if available
  - Falls back to Whisper if needed
```

### MVP Code Structure

```python
# Level 3: BaseYouTubeWorker (platform-specific)
class BaseYouTubeWorker(BaseSourceWorker):
    def __init__(self, ...):
        super().__init__(...)
        self.ytdlp = YtDlp()  # No API limits!
    
    def fetch_video_metadata(self, video_id: str) -> dict:
        """Fetch using yt-dlp (no quota limits)."""
        return self.ytdlp.extract_info(f"https://youtube.com/watch?v={video_id}")
    
    def extract_content_text(self, video_data: dict, method='auto') -> str:
        """Extract text using best available method."""
        if method == 'auto':
            # Priority: subtitles > auto-captions > whisper
            if self._has_subtitles(video_data):
                return self._extract_subtitles(video_data)
            elif self._has_auto_captions(video_data):
                return self._extract_auto_captions(video_data)
            else:
                return self._extract_with_whisper(video_data)
    
    def _extract_subtitles(self, video_data: dict) -> str:
        """Extract official subtitles using yt-dlp."""
        return self.ytdlp.download_subtitles(video_data['id'])
    
    def _extract_with_whisper(self, video_data: dict) -> str:
        """Extract audio and transcribe with Whisper."""
        audio_path = self.ytdlp.download_audio(video_data['id'])
        return whisper.transcribe(audio_path)

# Level 4: YouTubeVideoWorker (endpoint-specific)
class YouTubeVideoWorker(BaseYouTubeWorker):
    def process_task(self, task: Task) -> TaskResult:
        video_id = task.parameters['video_id']
        
        # Fetch metadata using yt-dlp (no quota!)
        video_data = self.fetch_video_metadata(video_id)
        
        # Filter before text extraction
        if video_data['duration'] < 60:
            return TaskResult(success=False, error='Too short')
        
        # Extract text (prioritize subtitles)
        text = self.extract_content_text(video_data, method='auto')
        
        # Create IdeaInspiration
        idea = self.create_inspiration(
            title=video_data['title'],
            content=text,
            metadata={
                'platform': 'youtube',
                'content_type': 'video',  # Just metadata!
                'duration': video_data['duration'],
                'view_count': video_data['view_count'],
                'extraction_method': 'subtitles' if video_data.get('has_subtitles') else 'whisper'
            }
        )
        
        return TaskResult(success=True, data=idea)
```

---

## Migration Path

### From Current (5 levels with Media Type) to Proposed (4 levels, Platform-First)

**Step 1: Keep BaseVideoSourceWorker as utility module**
```python
# Move BaseVideoSourceWorker → utils/video_utils.py
# Not a class hierarchy, just utility functions
def parse_duration(duration_str: str) -> int:
    """Parse ISO 8601 duration."""
    pass

def validate_video_metadata(data: dict) -> bool:
    """Validate video metadata."""
    pass
```

**Step 2: Integrate utilities into BaseYouTubeWorker**
```python
from utils.video_utils import parse_duration, validate_video_metadata

class BaseYouTubeWorker(BaseSourceWorker):  # Skip media type layer!
    def __init__(self, ...):
        super().__init__(...)
    
    # Can still use video utilities
    def parse_duration(self, duration):
        return parse_duration(duration)
```

**Step 3: Content type becomes metadata**
```python
class BaseSourceWorker:
    def create_inspiration(self, ..., content_type: str = 'auto'):
        """Create IdeaInspiration with content_type as metadata."""
        return IdeaInspiration(
            content=text,
            metadata={
                'content_type': content_type,  # Just a field!
                'platform': self.platform_name,
                # ...
            }
        )
```

---

## Categories to Replace "Media Type"

### Option 1: Content Format (More Granular)

Instead of: `Video, Audio, Text`  
Use: `youtube_video, youtube_short, youtube_podcast, reddit_post, reddit_comment, spotify_podcast, tiktok_video`

**Benefits**:
- More specific
- Platform + format in one
- No ambiguity

**Structure**:
```python
class BaseYouTubeWorker:
    content_formats = ['video', 'short', 'podcast', 'livestream']

class BaseRedditWorker:
    content_formats = ['post', 'comment', 'crosspost']
```

### Option 2: Extraction Strategy (What Matters)

Instead of: `Video, Audio, Text`  
Use: `subtitle_extraction, audio_transcription, direct_text, ocr_extraction`

**Benefits**:
- Describes actual operation
- Maps to implementation
- Clear cost implications

### Option 3: No Category - Just Platform + Endpoint

Simply: `youtube/video`, `youtube/channel`, `reddit/posts`, `spotify/podcast`

**Benefits**:
- Simplest
- Most flexible
- No forced categorization

---

## Recommended Structure for MVP

### Final Recommendation

```
BaseWorker (general task processing)
  ↓
BaseSourceWorker (config, database, utilities)
  ↓
BaseYouTubeWorker (YouTube + yt-dlp + extractors)
  - fetch_video_metadata(video_id) → uses yt-dlp
  - extract_subtitles(video_id) → uses yt-dlp
  - extract_with_whisper(video_id) → uses whisper
  - content_type stored as metadata, not hierarchy
  ↓
YouTubeVideoWorker (single video endpoint)
  - Focus: subtitle extraction
  - Fallback: whisper transcription
  - No API limits (uses yt-dlp)
```

**Key Changes**:
1. ❌ Remove `BaseVideoSourceWorker` (media type layer)
2. ✅ Keep utilities as helper functions
3. ✅ Platform-first hierarchy
4. ✅ Content type = metadata field
5. ✅ Extraction = Visitor pattern (strategies)

**Content Type Field Options**:
```python
# In metadata, not class hierarchy
content_type = 'video' | 'audio' | 'text' | 'image' | 'live' | 'short' | 'podcast'
```

---

## Summary

### Question 1: Is Video/Audio/Text categorization correct?
**Answer**: NO - Platform is the better abstraction. Media type should be metadata, not hierarchy.

### Question 2: Should media type be removed?
**Answer**: YES from hierarchy, NO from metadata. Keep as a field: `metadata['content_type'] = 'video'`

### Question 3: How to structure with Template Method?
**Answer**: 4-level Platform-First structure:
1. BaseWorker (task processing)
2. BaseSourceWorker (config, database)
3. BasePlatformWorker (YouTube, Reddit, etc.)
4. PlatformEndpointWorker (Video, Channel, Posts, etc.)

### Question 4: MVP focus
**Answer**: 
- ✅ YouTube platform only
- ✅ yt-dlp for video fetching (no API limits)
- ✅ Subtitle extraction as primary method
- ✅ Whisper as fallback
- ✅ Single video extraction

### Benefits of Platform-First:
1. ✅ Simpler (4 levels instead of 5)
2. ✅ More accurate (platform is real differentiator)
3. ✅ More flexible (YouTube can have any content type)
4. ✅ Easier to extend (add platforms, not media types)
5. ✅ Better separation of concerns (extraction = visitor pattern)

---

**Last Updated**: 2025-11-16  
**Maintained By**: PrismQ.T.Idea.Inspiration Team
