# Issue #001: Implement RedditTrendingWorker

**Priority**: High  
**Status**: New  
**Dependencies**: None (MVP is complete)  
**Duration**: 1-2 days

## Objective

Migrate the RedditTrendingPlugin to use the worker pattern, enabling trending post scraping as worker tasks that can be queued, claimed, and executed by workers.

## Problem Statement

Currently, the `RedditTrendingPlugin` exists but is not integrated with the worker pattern implemented in the MVP. We need to:

1. Create a `RedditTrendingWorker` that extends `BaseWorker`
2. Process `trending_scrape` task type
3. Use the existing `RedditTrendingPlugin` for scraping logic
4. Save results to IdeaInspiration database
5. Follow the same pattern as `RedditSubredditWorker`

## Proposed Solution

### 1. Create RedditTrendingWorker

**File**: `Source/Text/Reddit/Posts/src/workers/reddit_trending_worker.py` (NEW)

```python
"""Reddit Trending Worker for scraping trending posts.

This worker processes Reddit trending scraping tasks from the task queue.
"""

import logging
from typing import Dict, Any, Optional, List
from workers.base_worker import BaseWorker
from workers import Task, TaskResult, TaskStatus
from core.config import Config
from core.database import Database
from plugins.reddit_trending import RedditTrendingPlugin

class RedditTrendingWorker(BaseWorker):
    """Worker for scraping Reddit trending posts.
    
    Task Parameters:
        subreddit: Subreddit name (default: 'all')
        limit: Number of posts to scrape (default: 10)
    
    Task Types:
        - trending_scrape: Scrape trending posts from a subreddit
    """
    
    def process_task(self, task: Task) -> TaskResult:
        # Implementation similar to RedditSubredditWorker
        pass
```

### 2. Update __init__.py

Add RedditTrendingWorker to exports

### 3. Add Tests

Create `test_reddit_trending_worker.py` with basic tests

## Acceptance Criteria

- [ ] `RedditTrendingWorker` class created and extends `BaseWorker`
- [ ] Implements `process_task` method for `trending_scrape` task type
- [ ] Uses `RedditTrendingPlugin` for scraping logic
- [ ] Saves results to IdeaInspiration database
- [ ] Handles errors gracefully
- [ ] Basic tests added and passing
- [ ] Documentation updated in workers README

## Testing Strategy

1. Unit test for worker initialization
2. Test task processing with mocked Reddit API
3. Test error handling (missing parameters, API errors)
4. Test database save functionality

## Implementation Notes

- Follow the same pattern as `RedditSubredditWorker`
- Reuse existing `RedditTrendingPlugin` scraping logic
- Parameters should match existing plugin interface
- Use same error handling and logging patterns

## References

- RedditSubredditWorker: `Source/Text/Reddit/Posts/src/workers/reddit_subreddit_worker.py`
- RedditTrendingPlugin: `Source/Text/Reddit/Posts/src/plugins/reddit_trending.py`
- Base Worker: `Source/Text/Reddit/Posts/src/workers/base_worker.py`
