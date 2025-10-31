# Migration Guide: Updating Sources Plugins to Use IdeaInspiration Model

## Overview
All 33 plugins in the Sources directory need to be updated to use the standardized `IdeaInspiration` model from the Model directory instead of returning raw dictionaries.

## Status
- **Total Plugins**: 33
- **Completed**: 1 (youtube_plugin.py)
- **Remaining**: 32

## Pattern to Follow

### 1. Update Base Plugin Class (__init__.py in plugins/)

Add IdeaInspiration import and update return types:

```python
# Add import for IdeaInspiration model
import sys
from pathlib import Path

# Add Model directory to path
model_path = Path(__file__).resolve().parents[X] / 'Model'  # X depends on nesting level
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration

# Update scrape() return type
@abstractmethod
def scrape(self) -> List[IdeaInspiration]:  # Changed from List[Dict[str, Any]]
    pass

# Update format_tags() to return List[str]
def format_tags(self, tags: List[str]) -> List[str]:  # Changed from str
    return [tag.strip() for tag in tags if tag.strip()]
```

### 2. Update Concrete Plugin Classes

#### For VIDEO sources (YouTube, TikTok, Twitch, etc.):

```python
from . import SourcePlugin, IdeaInspiration

def scrape(self) -> List[IdeaInspiration]:
    ideas = []
    
    # ... fetch video data ...
    
    for video in videos:
        # Build metadata with STRING values only (SQLite compatibility)
        metadata = {
            'video_id': video['id'],
            'channel_id': video.get('channel_id', ''),
            'view_count': str(video.get('views', 0)),
            'like_count': str(video.get('likes', 0)),
            # ... other metadata as strings
        }
        
        # Use from_video() factory method
        idea = IdeaInspiration.from_video(
            title=video['title'],
            description=video.get('description', ''),
            subtitle_text=video.get('subtitles', ''),  # Captions/transcription
            keywords=self._extract_tags(video),  # List[str]
            metadata=metadata,
            source_id=video['id'],
            source_url=video_url,
            source_created_by=video.get('creator', ''),
            source_created_at=video.get('timestamp', '')
        )
        ideas.append(idea)
    
    return ideas
```

#### For TEXT sources (Articles, Reddit, Forums, etc.):

```python
from . import SourcePlugin, IdeaInspiration

def scrape(self) -> List[IdeaInspiration]:
    ideas = []
    
    # ... fetch text data ...
    
    for post in posts:
        # Build metadata with STRING values
        metadata = {
            'author': post.get('author', ''),
            'upvotes': str(post.get('upvotes', 0)),
            'comments': str(post.get('comments', 0)),
            # ... other metadata as strings
        }
        
        # Use from_text() factory method
        idea = IdeaInspiration.from_text(
            title=post['title'],
            description=post.get('summary', ''),
            text_content=post.get('body', ''),
            keywords=self._extract_tags(post),  # List[str]
            metadata=metadata,
            source_id=post['id'],
            source_url=post_url,
            source_created_by=post.get('author', ''),
            source_created_at=post.get('timestamp', '')
        )
        ideas.append(idea)
    
    return ideas
```

#### For AUDIO sources (Podcasts, etc.):

```python
from . import SourcePlugin, IdeaInspiration

def scrape(self) -> List[IdeaInspiration]:
    ideas = []
    
    # ... fetch audio data ...
    
    for episode in episodes:
        # Build metadata with STRING values
        metadata = {
            'duration': str(episode.get('duration', 0)),
            'format': episode.get('format', 'mp3'),
            # ... other metadata as strings
        }
        
        # Use from_audio() factory method
        idea = IdeaInspiration.from_audio(
            title=episode['title'],
            description=episode.get('description', ''),
            transcription=episode.get('transcription', ''),
            keywords=self._extract_tags(episode),  # List[str]
            metadata=metadata,
            source_id=episode['id'],
            source_url=episode_url,
            source_created_by=episode.get('host', ''),
            source_created_at=episode.get('publish_date', '')
        )
        ideas.append(idea)
    
    return ideas
```

### 3. Update Helper Methods

Change `_extract_tags()` and similar methods to return `List[str]`:

```python
def _extract_tags(self, data: Dict[str, Any]) -> List[str]:
    """Extract tags.
    
    Returns:
        List of tag strings
    """
    tags = ['source_name']
    # ... add tags ...
    return self.format_tags(tags)  # Returns List[str]
```

## Plugin-by-Category Checklist

### Content Sources
#### Articles
- [ ] Content/Articles/WebArticles - Use `from_text()`
- [ ] Content/Articles/Medium - Use `from_text()`

#### Forums  
- [ ] Content/Forums/HackerNews - Use `from_text()`
- [ ] Content/Forums/Reddit - Use `from_text()`

#### Podcasts
- [ ] Content/Podcasts/ApplePodcasts - Use `from_audio()`
- [ ] Content/Podcasts/SpotifyPodcasts - Use `from_audio()`

#### Shorts
- [x] Content/Shorts/YouTube/youtube_plugin.py - DONE
- [ ] Content/Shorts/YouTube/youtube_channel_plugin.py - Use `from_video()` with subtitles
- [ ] Content/Shorts/YouTube/youtube_trending_plugin.py - Use `from_video()` with subtitles
- [ ] Content/Shorts/TikTok - Use `from_video()`
- [ ] Content/Shorts/InstagramReels - Use `from_video()`
- [ ] Content/Shorts/TwitchClips - Use `from_video()`

#### Streams
- [ ] Content/Streams/KickClips - Use `from_video()`

### Commerce Sources
- [ ] Commerce/AppStoreTopCharts/apple_app_store_plugin.py - Use `from_text()` (app descriptions)
- [ ] Commerce/AppStoreTopCharts/google_play_plugin.py - Use `from_text()`
- [ ] Commerce/AmazonBestsellers - Use `from_text()`
- [ ] Commerce/EtsyTrending - Use `from_text()`

### Community Sources  
- [ ] Community/CommentMiningSource/multiplatform_plugin.py - Use `from_text()`
- [ ] Community/PromptBoxSource/form_submission_plugin.py - Use `from_text()`
- [ ] Community/QASource/stackexchange_plugin.py - Use `from_text()`
- [ ] Community/UserFeedbackSource/youtube_comments_plugin.py - Use `from_text()`

### Creative Sources
- [ ] Creative/LyricSnippets/genius_plugin.py - Use `from_text()` (lyrics are text)
- [ ] Creative/LyricSnippets/manual_import_plugin.py - Use `from_text()`
- [ ] Creative/ScriptBeats/template_plugin.py - Use `from_text()`
- [ ] Creative/ScriptBeats/manual_import_plugin.py - Use `from_text()`
- [ ] Creative/VisualMoodboard/unsplash_plugin.py - Use `from_text()` (image metadata/descriptions)
- [ ] Creative/VisualMoodboard/manual_import_plugin.py - Use `from_text()`

### Events Sources
- [ ] Events/CalendarHolidays/calendar_holidays_plugin.py - Use `from_text()`
- [ ] Events/EntertainmentReleases/tmdb_plugin.py - Use `from_text()` or `from_video()` depending on media type
- [ ] Events/SportsHighlights/thesportsdb_plugin.py - Use `from_video()` or `from_text()`

### Internal Sources
- [ ] Internal/CSVImport/csv_import_plugin.py - Determine type from CSV data
- [ ] Internal/ManualBacklog/manual_entry_plugin.py - Determine type from user input

### Signals Sources
- [ ] Signals/Trends/GoogleTrends/google_trends_plugin.py - Use `from_text()`

## Important Notes

1. **Metadata must use STRING values** - SQLite compatibility requires all metadata values to be strings
2. **Keywords/tags are List[str]** - No longer comma-separated strings
3. **Update return type hints** - Change from `List[Dict[str, Any]]` to `List[IdeaInspiration]`
4. **Import path** - Adjust the `parents[X]` number based on nesting level (count ../ to reach PrismQ.IdeaInspiration root)

## Testing After Migration

After updating each plugin:
1. Verify imports work correctly
2. Test that IdeaInspiration objects are created properly
3. Ensure metadata values are all strings
4. Verify tags are List[str]

## Next Steps

Continue updating plugins in batches by category, testing each batch before moving to the next.
