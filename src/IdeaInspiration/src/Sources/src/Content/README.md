# PrismQ.IdeaInspiration.Sources.Content

Content processing module for handling and categorizing collected content.

## Purpose

This module is responsible for processing and categorizing content collected from various sources.

## Module Structure

```
Content/
├── docs/              # Module documentation
├── issues/            # Module-specific issue tracking
│   ├── new/          # New issues
│   ├── wip/          # Work in progress
│   └── done/         # Completed issues
├── scripts/          # Module utility scripts
├── src/              # Module source code
│   └── Shorts/       # Nested submodule for short-form content
└── tests/            # Module tests
```

## Responsibilities

- Process raw content from sources
- Extract metadata and key information
- Categorize content by type and format
- Transform content for downstream processing

## Submodules

- **Shorts** - Short-form content handling (TikTok, YouTube Shorts, Reels)

## Processing Pipeline

1. Content ingestion
2. Metadata extraction
3. Content categorization
4. Format transformation
5. Quality validation
