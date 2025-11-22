# HackerNews Source Module

**HackerNews content scraping module for PrismQ.T.Idea.Inspiration**

## Overview

This module provides integration with HackerNews to scrape stories, comments, and discussions for content inspiration and trending tech topics.

## Module Structure

```
HackerNews/
├── _meta/                      # Non-implementation files
│   ├── docs/                   # Documentation
│   ├── examples/               # Usage examples
│   ├── scripts/                # Utility scripts
│   └── issues/                 # Issue tracking
│
├── Stories/                    # Story scraping sub-module
│   ├── _meta/                  # Stories-specific docs
│   └── src/                    # Stories implementation
│       ├── core/               # Story utilities
│       ├── plugins/            # hackernews_story_plugin.py
│       └── workers/            # hackernews_story_worker.py
│
├── Comments/                   # Comment scraping sub-module
│   ├── _meta/                  # Comments-specific docs
│   └── src/                    # Comments implementation
│       ├── core/               # Comment utilities
│       ├── plugins/            # hackernews_comment_plugin.py
│       └── workers/            # hackernews_comment_worker.py
│
└── src/                        # HackerNews-shared code
    ├── core/                   # HackerNews API client
    ├── schemas/                # HackerNews data schemas
    └── mappers/                # HackerNews → IdeaInspiration mappers
```

## Sub-Modules

### Stories
Scrapes HackerNews stories including:
- Titles, URLs, text content
- Points, rank, age
- Author and submission time
- Story type (story, ask, show, job)

### Comments
Scrapes HackerNews comments including:
- Comment threads and trees
- Points and replies
- Author information
- Thread depth and context

## Architecture

Follows the layered Source architecture:

```
IdeaInspiration (Domain)
    ↑
hackernews_*_source.py (Adapter)
    ↑
schemas.py → mappers.py
    ↑
client.py (HackerNews API)
```

## Usage

See `_meta/examples/` for usage examples.

## Legacy Reference

Legacy implementation: `Legacy_Reference/Content/Forums/HackerNews/`

---

**Status**: Migrated from legacy structure  
**Last Updated**: 2025-11-11
