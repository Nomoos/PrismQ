# User-Provided YouTube Video Inspiration

**Namespace**: `PrismQ.T.Idea.Inspiration.From.User.YouTube.Video`

## Overview

This module allows users to provide a YouTube video URL interactively and downloads its text content (subtitles/transcript) for inspiration gathering.

## Purpose

Enable users to manually add specific YouTube videos to the inspiration pipeline by providing the video URL directly, rather than relying on automated discovery through trending or channel scraping.

## Key Difference from Automated

- **This module** (`From/User/YouTube/Video`): User provides a specific video URL
- **Automated module** (`From/YouTube/Video`): System discovers videos via trending/search

Both download the same type of content, but the source of the URL is different.

## Usage

```python
from T.Idea.Inspiration.From.User.YouTube.Video import download_video_inspiration

# User provides a YouTube URL
video_url = input("Enter YouTube video URL: ")

# Download and store as inspiration
inspiration = download_video_inspiration(video_url)
print(f"Downloaded: {inspiration.title}")
```

## Features

- ✅ Accept YouTube video URL from user
- ✅ Download video metadata (title, description, tags)
- ✅ Extract subtitles/transcript for text content
- ✅ Store as IdeaInspiration record
- ✅ Validate URL format
- ✅ Handle errors gracefully

## Installation

```bash
cd T/Idea/Inspiration/From/User/YouTube/Video
pip install -r requirements.txt
```

## Dependencies

- `yt-dlp` - For downloading video metadata and subtitles
- Parent IdeaInspiration model

## Interactive Mode

```bash
python -m T.Idea.Inspiration.From.User.YouTube.Video.src.cli
```

This will prompt for a YouTube URL and download the content.

## Module Structure

```
Video/
├── README.md              # This file
├── requirements.txt       # Dependencies
├── src/
│   ├── __init__.py       # Module exports
│   ├── cli.py            # Interactive CLI
│   └── downloader.py     # Core download logic
└── _meta/
    └── docs/             # Additional documentation
```

## Related Modules

- `T/Idea/Inspiration/From/YouTube/Video` - Automated video discovery
- `T/Idea/Inspiration/From/YouTube/Search` - Trending video scraping
- `T/Idea/Inspiration/From/YouTube/Channel` - Channel-based scraping
