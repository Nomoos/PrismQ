# Implementation Guide: User-Provided YouTube Video Inspiration

## Overview

This module implements the simplest case of user-interactive inspiration gathering: downloading text content from a single YouTube video URL provided by the user.

## Architecture

### Module Location
`T/Idea/Inspiration/From/User/YouTube/Video`

### Namespace
`PrismQ.T.Idea.Inspiration.From.User.YouTube.Video`

### Key Components

1. **downloader.py**: Core logic for downloading video metadata
2. **cli.py**: Interactive command-line interface
3. **__init__.py**: Module exports

## How It Works

1. User provides a YouTube video URL
2. System validates the URL format
3. Uses `yt-dlp` to download:
   - Video metadata (title, description, channel, etc.)
   - Subtitles/transcript (if available)
4. Returns structured inspiration data

## Distinction from Automated Scraping

| Aspect | User-Provided (This Module) | Automated Scraping |
|--------|----------------------------|-------------------|
| **Location** | `From/User/YouTube/Video` | `From/YouTube/Video` |
| **URL Source** | User input (manual) | System discovery (trending/search) |
| **Trigger** | Interactive | Automated/scheduled |
| **Use Case** | "I want inspiration from THIS video" | "Find trending videos for inspiration" |

## Usage Examples

### Command Line
```bash
cd T/Idea/Inspiration/From/User/YouTube/Video
python -m src.cli
```

### Python API
```python
from T.Idea.Inspiration.From.User.YouTube.Video import download_video_inspiration

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
inspiration = download_video_inspiration(url)

print(inspiration['title'])
print(inspiration['content'])
```

### Integration with IdeaInspiration Model
```python
from T.Idea.Inspiration.From.User.YouTube.Video import download_video_inspiration
from Model.Entities.idea_inspiration import IdeaInspiration

# Download inspiration data
data = download_video_inspiration(user_provided_url)

# Create IdeaInspiration record
inspiration = IdeaInspiration(
    source=data['source'],
    source_url=data['source_url'],
    title=data['title'],
    content=data['content'],
    metadata=data['metadata']
)

# Save to database
inspiration.save()
```

## Error Handling

The module handles:
- Invalid YouTube URLs
- Network errors
- Missing yt-dlp installation
- Videos without subtitles (falls back to description)
- Timeouts

## Future Enhancements

Potential additions (not in initial implementation):
- Multiple URL batch processing
- Playlist support
- Quality checks (duration, views, etc.)
- Content filtering
- Integration with TaskManager for async processing

## Testing

```bash
# Manual testing
python -m src.cli

# Enter test URLs:
# - Regular video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
# - Short URL: https://youtu.be/dQw4w9WgXcQ
# - Shorts: https://www.youtube.com/shorts/abc123
```

## Dependencies

- `yt-dlp`: Video metadata and subtitle extraction
- Python 3.8+

## Related Modules

- `T/Idea/Inspiration/From/YouTube/Video`: Automated video scraping
- `T/Idea/Inspiration/From/YouTube/Search`: Trending video discovery
- `T/Idea/Inspiration/From/YouTube/Channel`: Channel-based scraping
- `T/Idea/From/User`: Direct idea creation from user input
