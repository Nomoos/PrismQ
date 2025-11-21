# Issue #002: Implement RedditSearchWorker

**Priority**: High  
**Status**: New  
**Dependencies**: None  
**Duration**: 1-2 days

## Objective

Implement a worker for Reddit search functionality, enabling keyword-based post discovery through the worker pattern.

## Problem Statement

The `RedditSearchPlugin` exists but needs worker integration for:
- Processing search queries from the task queue
- Filtering and sorting search results
- Saving discovered posts to IdeaInspiration database

## Proposed Solution

### RedditSearchWorker Implementation

```python
class RedditSearchWorker(BaseWorker):
    """Worker for searching Reddit posts.
    
    Task Parameters:
        query: Search query string (required)
        subreddit: Subreddit to search (default: 'all')
        limit: Number of results (default: 10)
        sort: Sort method - 'relevance', 'hot', 'top', 'new' (default: 'relevance')
        time_filter: Time filter for 'top' sort (optional)
    
    Task Types:
        - search_scrape: Search for posts matching query
    """
```

## Acceptance Criteria

- [ ] RedditSearchWorker created and functional
- [ ] Handles all search parameters correctly
- [ ] Validates search query requirements
- [ ] Saves results to database
- [ ] Tests added and passing
- [ ] Documentation complete

## Testing Strategy

1. Test basic search functionality
2. Test with various sort methods
3. Test time filters
4. Test empty results handling
5. Test invalid query handling

## Implementation Notes

- Search queries must be non-empty
- Support subreddit-specific and site-wide searches
- Handle Reddit API search limitations
- Consider rate limiting for high-volume searches

## References

- RedditSearchPlugin: `Source/Text/Reddit/Posts/src/plugins/reddit_search.py`
- RedditSubredditWorker: `Source/Text/Reddit/Posts/src/workers/reddit_subreddit_worker.py`
