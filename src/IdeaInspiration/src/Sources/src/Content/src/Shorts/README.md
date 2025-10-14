# PrismQ.IdeaInspiration.Sources.Content.Shorts

Short-form content handling module for processing videos under 60 seconds.

## Purpose

This module is responsible for handling short-form content from various platforms including YouTube Shorts, TikTok, Instagram Reels, and similar formats.

## Module Structure

```
Shorts/
├── docs/              # Module documentation
├── issues/            # Module-specific issue tracking
│   ├── new/          # New issues
│   ├── wip/          # Work in progress
│   └── done/         # Completed issues
├── scripts/          # Module utility scripts
├── src/              # Module source code
│   └── YouTubeShortsSource/  # Nested submodule for YouTube Shorts
└── tests/            # Module tests
```

## Responsibilities

- Process short-form video content
- Handle platform-specific formats (vertical video, aspect ratios)
- Extract trends and viral content patterns
- Manage short-form content metadata

## Submodules

- **YouTubeShortsSource** - YouTube Shorts specific integration

## Supported Platforms

- YouTube Shorts (via YouTubeShortsSource submodule)
- TikTok (planned)
- Instagram Reels (planned)
- Facebook Reels (planned)

## Content Characteristics

- Video length: < 60 seconds
- Format: Typically vertical (9:16 aspect ratio)
- High engagement metrics
- Trend-focused content
