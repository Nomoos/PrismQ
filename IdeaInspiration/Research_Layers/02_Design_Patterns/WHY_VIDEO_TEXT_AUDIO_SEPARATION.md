# Why Separate Video, Text, and Audio Workers?

**Question**: If YouTube videos are converted to text (subtitles/transcripts), why not treat YouTube as a text source? Why maintain Video, Text, and Audio categories?

---

## Executive Summary

**Answer**: Media type (Video/Text/Audio) represents the **SOURCE FORMAT**, not the **processing output**. The separation is crucial for:

1. **Source-specific operations** - Videos need thumbnail extraction, duration parsing, view counts
2. **Different metadata** - Each media type has unique metadata requirements
3. **Processing pipelines** - Different extraction strategies (API vs scraping vs OCR)
4. **Progressive enrichment** - Media-specific operations before text conversion

Even though all content eventually becomes text for analysis, the **acquisition and preprocessing** stages are fundamentally different.

---

## Detailed Explanation

### The Content Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: Source Acquisition (Media-Specific)               │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│ │   VIDEO      │  │     TEXT     │  │    AUDIO     │      │
│ │              │  │              │  │              │      │
│ │ • Fetch API  │  │ • Scrape HTML│  │ • Download   │      │
│ │ • Extract    │  │ • Parse MD   │  │   file       │      │
│ │   metadata   │  │ • Get author │  │ • Extract    │      │
│ │ • Thumbnails │  │ • Get date   │  │   metadata   │      │
│ │ • Duration   │  │ • Get votes  │  │ • Duration   │      │
│ │ • Views      │  │              │  │ • Speaker    │      │
│ └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: Text Extraction (Media-Specific Methods)          │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│ │   VIDEO      │  │     TEXT     │  │    AUDIO     │      │
│ │              │  │              │  │              │      │
│ │ • Subtitle   │  │ • Direct     │  │ • Whisper    │      │
│ │   API call   │  │   content    │  │   STT        │      │
│ │ • Caption    │  │ • Already    │  │ • Speaker    │      │
│ │   download   │  │   text       │  │   diarization│      │
│ │ • OCR (if    │  │ • Minimal    │  │ • Timestamp  │      │
│ │   needed)    │  │   processing │  │   alignment  │      │
│ └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: Unified Processing (Same for All)                 │
│                                                             │
│ • Classification (STORYTELLING, BUSINESS, etc.)            │
│ • Scoring (0-100)                                          │
│ • Storage (IdeaInspiration database)                       │
│ • Analysis                                                  │
└─────────────────────────────────────────────────────────────┘
```

### Why Video ≠ Text (Even With Subtitles)

#### 1. **Metadata Differences**

**Video Sources** (YouTube, TikTok):
```python
{
    'video_id': 'abc123',
    'title': 'How to Build a Startup',
    'duration': 'PT15M30S',  # 15 minutes 30 seconds
    'view_count': 1_250_000,
    'like_count': 45_000,
    'comment_count': 3_200,
    'thumbnail_url': 'https://...',
    'channel_id': 'UC...',
    'published_at': '2024-01-15T10:00:00Z',
    'video_quality': '1080p',
    'is_live': False,
    'subtitles': ['en', 'es', 'fr']  # Available subtitle languages
}
```

**Text Sources** (Reddit, HackerNews):
```python
{
    'post_id': '123abc',
    'title': 'Ask HN: How to Build a Startup',
    'text': 'I have an idea...',
    'author': 'user123',
    'score': 450,
    'num_comments': 120,
    'created_utc': 1705315200,
    'url': 'https://...',
    'subreddit': 'startups'
    # No duration, no views, no thumbnails!
}
```

**Key Differences**:
- Videos have **duration** - critical for content filtering (Shorts vs long-form)
- Videos have **view counts** - different scale than text upvotes
- Videos have **thumbnails** - visual preview (may extract later for AI analysis)
- Videos have **quality metrics** - resolution, format
- Text has **upvotes/karma** - community validation metric
- Text has **nested comments** - different engagement pattern

#### 2. **Different Extraction Strategies**

**Video Text Extraction**:
```python
class BaseVideoSourceWorker:
    def extract_text(self, video_id: str) -> str:
        # Strategy 1: Try official subtitle API
        subtitles = self.youtube_client.get_subtitles(video_id, lang='en')
        if subtitles:
            return subtitles
        
        # Strategy 2: Try auto-generated captions
        auto_captions = self.youtube_client.get_auto_captions(video_id)
        if auto_captions:
            return auto_captions
        
        # Strategy 3: Download video and use Whisper STT
        video_path = self.download_video(video_id)
        transcript = self.whisper_transcribe(video_path)
        return transcript
```

**Text Extraction** (Already Text):
```python
class BaseTextSourceWorker:
    def extract_text(self, post_id: str) -> str:
        # It's already text!
        post = self.reddit_client.get_post(post_id)
        return post['selftext']  # Done!
```

**Completely Different!**

#### 3. **API Differences**

**YouTube API** (Video-Specific):
- `videos.list` - Get video metadata
- `captions.list` - Get available captions
- `captions.download` - Download subtitle file
- Quota costs: 1 unit per video, 50 units per caption
- Rate limits: 10,000 units/day
- Returns: Video-specific formats (ISO 8601 duration, etc.)

**Reddit API** (Text-Specific):
- `r/{subreddit}/hot` - Get hot posts
- `comments/{post_id}` - Get comments
- Rate limits: 60 requests/minute
- Returns: Text-specific formats (markdown, HTML)

**Different APIs = Different Workers!**

#### 4. **Business Logic Differences**

**Video-Specific Logic**:
```python
class BaseVideoSourceWorker:
    def should_process(self, video_data: dict) -> bool:
        """Video-specific filtering."""
        # Skip very short videos (< 1 minute)
        if self.parse_duration(video_data['duration']) < 60:
            return False
        
        # Skip low-quality videos
        if video_data.get('view_count', 0) < 1000:
            return False
        
        # Prefer videos with subtitles
        if not video_data.get('has_subtitles'):
            return False
        
        return True
```

**Text-Specific Logic**:
```python
class BaseTextSourceWorker:
    def should_process(self, post_data: dict) -> bool:
        """Text-specific filtering."""
        # Skip short posts
        if len(post_data['text']) < 100:
            return False
        
        # Skip low-score posts
        if post_data.get('score', 0) < 50:
            return False
        
        # Skip posts without engagement
        if post_data.get('num_comments', 0) < 5:
            return False
        
        return True
```

**Different Criteria = Different Methods!**

---

## Progressive Enrichment Example

### Level 3: BaseVideoSourceWorker

**What it adds** (BEFORE text extraction):
```python
class BaseVideoSourceWorker(BaseSourceWorker):
    """Video-specific operations BEFORE text conversion."""
    
    def validate_video_metadata(self, data: dict) -> bool:
        """Ensure video has required fields."""
        return all([
            'id' in data,
            'title' in data,
            'duration' in data,
            'url' in data
        ])
    
    def parse_duration(self, duration_str: str) -> int:
        """Convert PT15M30S to 930 seconds."""
        # Video-specific: YouTube uses ISO 8601 duration
        pass
    
    def calculate_engagement_rate(self, data: dict) -> float:
        """Video-specific: (likes + comments) / views."""
        views = data.get('view_count', 0)
        if views == 0:
            return 0.0
        likes = data.get('like_count', 0)
        comments = data.get('comment_count', 0)
        return (likes + comments) / views
    
    def categorize_video_length(self, duration: int) -> str:
        """Video-specific: Shorts vs long-form."""
        if duration < 60:
            return 'short'  # YouTube Shorts
        elif duration < 300:
            return 'medium'
        else:
            return 'long'
```

**This wouldn't make sense in BaseTextSourceWorker!**

### Level 4: BaseYouTubeWorker

**What it adds** (YouTube-specific, BEFORE text extraction):
```python
class BaseYouTubeWorker(BaseVideoSourceWorker):
    """YouTube-specific operations."""
    
    def __init__(self, ...):
        super().__init__(...)
        self.youtube_client = YouTubeAPIClient(api_key)
        self.quota_manager = QuotaManager()
    
    def check_quota(self) -> bool:
        """YouTube-specific: Check API quota."""
        return self.quota_manager.remaining_quota > 100
    
    def handle_youtube_errors(self, error: HttpError) -> TaskResult:
        """YouTube-specific error handling."""
        if 'quotaExceeded' in str(error):
            return TaskResult(success=False, error='Quota exceeded')
        elif 'videoNotFound' in str(error):
            return TaskResult(success=False, error='Video deleted')
        # ... more YouTube-specific errors
    
    def fetch_youtube_video(self, video_id: str) -> dict:
        """YouTube API call with quota tracking."""
        if not self.check_quota():
            raise QuotaExceededException()
        
        video = self.youtube_client.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()
        
        self.quota_manager.record_usage(1)  # 1 unit used
        return video
```

### Level 5: YouTubeVideoWorker

**What it adds** (Finally, text extraction):
```python
class YouTubeVideoWorker(BaseYouTubeWorker):
    """Specific video endpoint."""
    
    def process_task(self, task: Task) -> TaskResult:
        # 1. Video-specific acquisition (from Level 4)
        video_data = self.fetch_youtube_video(video_id)
        
        # 2. Video-specific validation (from Level 3)
        if not self.validate_video_metadata(video_data):
            return TaskResult(success=False)
        
        # 3. Video-specific filtering (from Level 3)
        duration = self.parse_duration(video_data['duration'])
        if duration < 60:
            return TaskResult(success=False, error='Too short')
        
        # 4. NOW extract text (video-specific method)
        transcript = self._extract_video_text(video_data)
        
        # 5. Create IdeaInspiration with VIDEO metadata
        idea = self.create_video_inspiration(
            video_data=video_data,
            transcript=transcript,  # The text!
            platform='youtube',
            source_url=f"https://youtube.com/watch?v={video_id}"
        )
        
        return TaskResult(success=True, data=idea)
```

---

## Why NOT Merge Video and Text?

### Option 1: Single "ContentWorker" (BAD)

```python
class ContentWorker(BaseSourceWorker):
    def process_task(self, task: Task) -> TaskResult:
        content_type = task.parameters.get('type')
        
        if content_type == 'video':
            # Video logic
            video_data = self.fetch_video(...)
            duration = self.parse_duration(...)  # Video-only
            views = video_data.get('view_count')  # Video-only
            transcript = self.extract_subtitles(...)  # Video-only
        elif content_type == 'text':
            # Text logic
            post_data = self.fetch_post(...)
            score = post_data.get('score')  # Text-only
            comments = self.fetch_comments(...)  # Text-only
            text = post_data['selftext']  # Already text!
        
        # This violates Single Responsibility Principle!
        # Too many if/else branches
        # Hard to test
        # Hard to extend
```

**Problems**:
- ❌ Violates Single Responsibility Principle
- ❌ Complex if/else logic
- ❌ Can't reuse video logic for TikTok
- ❌ Can't reuse text logic for HackerNews
- ❌ Testing nightmare

### Option 2: Separate Video and Text Workers (GOOD)

```python
class BaseVideoSourceWorker(BaseSourceWorker):
    """Video-specific operations only."""
    def parse_duration(self, duration: str) -> int: ...
    def validate_video_metadata(self, data: dict) -> bool: ...
    def extract_subtitles(self, video_id: str) -> str: ...

class BaseTextSourceWorker(BaseSourceWorker):
    """Text-specific operations only."""
    def extract_markdown(self, text: str) -> str: ...
    def extract_urls(self, text: str) -> List[str]: ...
    def calculate_readability(self, text: str) -> float: ...
```

**Benefits**:
- ✅ Single Responsibility - Each class does one thing
- ✅ Reusable - YouTube and TikTok both inherit BaseVideoSourceWorker
- ✅ Testable - Test video and text logic separately
- ✅ Extensible - Add new platforms easily

---

## Real-World Example: YouTube Video Worker

### Full Pipeline

```python
# Stage 1: Acquisition (Video-Specific)
video_data = youtube_worker.fetch_youtube_video('abc123')
# Returns: {
#     'id': 'abc123',
#     'title': 'Startup Ideas',
#     'duration': 'PT15M30S',
#     'view_count': 100000,
#     'like_count': 5000,
#     ...
# }

# Stage 2: Video-Specific Processing
duration = youtube_worker.parse_duration(video_data['duration'])
# Returns: 930 (seconds)

engagement = youtube_worker.calculate_engagement_rate(video_data)
# Returns: 0.05 (5% engagement)

category = youtube_worker.categorize_video_length(duration)
# Returns: 'medium'

# Stage 3: Text Extraction (Video-Specific Method)
transcript = youtube_worker.extract_video_text(video_data)
# Returns: "Welcome to this video about startup ideas..."

# Stage 4: Create IdeaInspiration (With VIDEO metadata)
idea = IdeaInspiration(
    title=video_data['title'],
    content=transcript,  # The text!
    source_type=ContentType.VIDEO,  # Still VIDEO!
    metadata={
        'video_id': 'abc123',
        'duration': 930,
        'view_count': 100000,
        'engagement_rate': 0.05,
        'video_length_category': 'medium',
        'thumbnail_url': '...',
        # Video-specific metadata!
    }
)

# Stage 5: Unified Processing (Same for Video, Text, Audio)
# Classification, Scoring, Storage happens at this level
```

### Compare with Reddit (Text Source)

```python
# Stage 1: Acquisition (Text-Specific)
post_data = reddit_worker.fetch_reddit_post('123abc')
# Returns: {
#     'id': '123abc',
#     'title': 'Ask HN: Startup Ideas',
#     'selftext': 'I have an idea...',  # Already text!
#     'score': 450,
#     'num_comments': 120,
#     ...
# }

# Stage 2: Text-Specific Processing
readability = reddit_worker.calculate_readability(post_data['selftext'])
# Returns: 65 (Flesch Reading Ease)

urls = reddit_worker.extract_urls(post_data['selftext'])
# Returns: ['https://example.com']

# Stage 3: Text "Extraction" (Already Text!)
text = post_data['selftext']  # Done!

# Stage 4: Create IdeaInspiration (With TEXT metadata)
idea = IdeaInspiration(
    title=post_data['title'],
    content=text,
    source_type=ContentType.TEXT,  # Still TEXT!
    metadata={
        'post_id': '123abc',
        'score': 450,
        'num_comments': 120,
        'readability': 65,
        'urls': urls,
        # Text-specific metadata!
    }
)

# Stage 5: Same unified processing
```

**Different metadata, different processing, different methods!**

---

## Summary

### Why Video, Text, Audio Separation Makes Sense

1. **Source Format ≠ Processing Output**
   - Media type represents HOW content is acquired and preprocessed
   - All eventually become text, but acquisition differs

2. **Different Metadata Requirements**
   - Videos: duration, views, thumbnails, quality
   - Text: upvotes, comments, readability
   - Audio: speaker, duration, audio quality

3. **Different APIs and Methods**
   - YouTube API vs Reddit API vs Spotify API
   - Different rate limits, quota systems, authentication

4. **Different Business Logic**
   - Video filtering: duration, views, quality
   - Text filtering: length, score, engagement
   - Audio filtering: duration, speaker, clarity

5. **Progressive Enrichment**
   - Each level adds media-specific functionality
   - BaseVideoSourceWorker adds video operations
   - BaseTextSourceWorker adds text operations
   - Can't be merged without violating SRP

6. **Reusability**
   - BaseVideoSourceWorker → YouTube, TikTok, Instagram
   - BaseTextSourceWorker → Reddit, HackerNews, Medium
   - BaseAudioSourceWorker → Spotify, Apple Podcasts

7. **SOLID Compliance**
   - Single Responsibility: One media type per worker hierarchy
   - Open/Closed: Add new platforms without modifying base
   - Liskov Substitution: All video workers substitutable
   - Interface Segregation: Focused interfaces per media type
   - Dependency Inversion: Depends on abstractions

### The Key Insight

**Media type categorization happens at the SOURCE level, not the OUTPUT level.**

Yes, all content eventually becomes text for analysis. But the **journey from source to text** is fundamentally different for each media type, requiring different:
- APIs
- Extraction methods
- Metadata
- Validation logic
- Filtering criteria
- Business rules

Therefore, **Video, Text, and Audio workers must remain separate** to maintain clean architecture, code reuse, and SOLID principles.

---

**Last Updated**: 2025-11-16  
**Maintained By**: PrismQ.IdeaInspiration Team
