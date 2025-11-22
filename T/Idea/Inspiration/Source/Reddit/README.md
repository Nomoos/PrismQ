# Reddit Source Module

**Reddit content scraping module for PrismQ.T.Idea.Inspiration**

## Overview

This module provides integration with Reddit to scrape posts, comments, and community discussions for content inspiration.

## Module Structure

```
Reddit/
├── _meta/                      # Non-implementation files
│   ├── docs/                   # Documentation
│   ├── examples/               # Usage examples
│   ├── scripts/                # Utility scripts
│   └── issues/                 # Issue tracking
│
├── Posts/                      # Post scraping sub-module
│   ├── _meta/                  # Posts-specific docs
│   └── src/                    # Posts implementation
│       ├── core/               # Post utilities
│       ├── plugins/            # reddit_post_plugin.py
│       └── workers/            # reddit_post_worker.py
│
├── Comments/                   # Comment scraping sub-module
│   ├── _meta/                  # Comments-specific docs
│   └── src/                    # Comments implementation
│       ├── core/               # Comment utilities
│       ├── plugins/            # reddit_comment_plugin.py
│       └── workers/            # reddit_comment_worker.py
│
└── src/                        # Reddit-shared code
    ├── core/                   # Reddit API client, auth
    ├── schemas/                # Reddit data schemas
    └── mappers/                # Reddit → IdeaInspiration mappers
```

## Sub-Modules

### Posts
Scrapes Reddit posts (submissions) including:
- Titles, content, URLs
- Upvotes, awards, engagement metrics
- Subreddit metadata
- Author information

### Comments
Scrapes Reddit comments including:
- Comment threads and trees
- Upvotes and replies
- Author information
- Thread context

## Architecture

Follows the layered Source architecture:

```
IdeaInspiration (Domain)
    ↑
reddit_*_source.py (Adapter)
    ↑
schemas.py → mappers.py
    ↑
client.py (Reddit API)
```

## Usage

See `_meta/examples/` for usage examples.

## Legacy Reference

Legacy implementation: `Legacy_Reference/Content/Forums/Reddit/`

---

**Status**: Migrated from legacy structure  
**Last Updated**: 2025-11-11
