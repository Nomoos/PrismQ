# Issue #007: Implement YouTube Keyword Search Worker

## Status
New

## Priority
High

## Category
Feature - New Worker

## Description

Implement a new YouTube keyword search worker that can perform search-based content discovery. This is a priority feature requested in the master plan that will complement channel and trending scraping.

## Problem Statement

Currently, the module supports channel and trending scraping but lacks keyword-based search functionality. Users need the ability to search YouTube for specific topics, keywords, or trends to discover relevant Shorts content.

## Proposed Solution

Create `YouTubeKeywordWorker` that:
- Extends `YouTubeWorkerBase`
- Uses yt-dlp for keyword search (no API quota)
- Supports advanced search filters (duration, date, sort)
- Filters for Shorts content only
- Processes search results into IdeaInspiration format

## Acceptance Criteria

- [ ] `YouTubeKeywordWorker` class created extending `YouTubeWorkerBase`
- [ ] Keyword search implemented using yt-dlp
- [ ] Shorts filtering (duration < 180s, vertical format)
- [ ] Support for search filters (upload date, sort order)
- [ ] Task parameter validation implemented
- [ ] Results saved to both local DB and queue
- [ ] Deduplication logic works
- [ ] Error handling with retry logic
- [ ] Unit tests with >80% coverage
- [ ] Integration tests with mock data
- [ ] Documentation with examples

## Technical Details

### Implementation Approach

1. Create `YouTubeKeywordWorker` in `src/workers/`
2. Implement search using yt-dlp ytsearch API
3. Add Shorts filtering logic
4. Implement search filters
5. Add parameter validation
6. Integrate with task queue

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/src/workers/keyword_worker.py`
  - YouTubeKeywordWorker class
  - Search implementation
  - Filtering logic

- **Create**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_keyword_plugin.py`
  - Optional: Reusable plugin for search logic
  - Can be used by worker and CLI

- **Create**: `Sources/Content/Shorts/YouTube/tests/test_keyword_worker.py`
  - Worker-specific tests
  - Mock yt-dlp results
  - Filter validation tests

### Worker Implementation

```python
from typing import Dict, Any, List, Optional
from ..core.worker_base import YouTubeWorkerBase, WorkerConfig
import json
import yt_dlp

class YouTubeKeywordWorker(YouTubeWorkerBase):
    """Worker for YouTube keyword search tasks"""
    
    def __init__(self, config: WorkerConfig, task_queue, db, app_config):
        super().__init__(config, task_queue)
        self.db = db
        self.app_config = app_config
        
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute keyword search task.
        
        Args:
            task: Task dictionary with parameters
            
        Returns:
            Result dictionary with scraped ideas
        """
        params = json.loads(task['parameters'])
        
        # Validate parameters
        if not self.validate_parameters(params):
            raise ValueError(f"Invalid parameters: {params}")
        
        # Extract parameters
        query = params['query']
        max_results = params.get('max_results', 50)
        sort_by = params.get('sort_by', 'relevance')
        upload_date = params.get('upload_date', None)
        
        # Execute search
        videos = self._search_youtube(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
            upload_date=upload_date
        )
        
        # Filter for Shorts
        shorts = self._filter_shorts(videos)
        
        # Save to local database
        saved_count = 0
        for video in shorts:
            idea = self._video_to_idea(video, query)
            
            self.db.insert_idea(
                source='youtube_keyword',
                source_id=idea['source_id'],
                title=idea['title'],
                description=idea['description'],
                tags=idea.get('tags', []),
                score=idea.get('score', 0.0),
                score_dictionary=idea.get('metrics', {})
            )
            saved_count += 1
        
        return {
            'status': 'success',
            'query': query,
            'videos_found': len(videos),
            'shorts_found': len(shorts),
            'ideas_saved': saved_count
        }
    
    def _search_youtube(
        self, 
        query: str,
        max_results: int,
        sort_by: str,
        upload_date: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Search YouTube using yt-dlp.
        
        Args:
            query: Search query
            max_results: Maximum results to fetch
            sort_by: Sort order (relevance, date, views)
            upload_date: Upload date filter (today, week, month)
            
        Returns:
            List of video metadata dictionaries
        """
        # yt-dlp options
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just metadata
            'playlistend': max_results,
        }
        
        # Build search URL
        search_url = f"ytsearch{max_results}:{query}"
        
        # Add filters
        if sort_by == 'date':
            search_url += " sort:date"
        elif sort_by == 'views':
            search_url += " sort:views"
        
        if upload_date:
            search_url += f" upload_date:{upload_date}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_url, download=False)
            return result.get('entries', [])
    
    def _filter_shorts(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter videos to only include Shorts.
        
        Args:
            videos: List of video metadata
            
        Returns:
            Filtered list containing only Shorts
        """
        shorts = []
        
        for video in videos:
            # Check duration (Shorts are < 60s typically, max 180s)
            duration = video.get('duration', 0)
            if duration == 0 or duration > 180:
                continue
            
            # Check aspect ratio if available
            width = video.get('width', 0)
            height = video.get('height', 0)
            if width > 0 and height > 0:
                aspect_ratio = width / height
                # Shorts are vertical (< 1.0)
                if aspect_ratio >= 1.0:
                    continue
            
            shorts.append(video)
        
        return shorts
    
    def _video_to_idea(self, video: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Convert yt-dlp video metadata to IdeaInspiration format"""
        return {
            'source_id': video.get('id'),
            'title': video.get('title', ''),
            'description': video.get('description', ''),
            'tags': [query] + video.get('tags', [])[:10],
            'score': 0.0,  # Will be calculated by scoring module
            'metrics': {
                'view_count': video.get('view_count', 0),
                'like_count': video.get('like_count', 0),
                'duration': video.get('duration', 0),
                'upload_date': video.get('upload_date', ''),
            }
        }
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Validate task parameters.
        
        Args:
            params: Parameters dictionary
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if 'query' not in params:
            return False
        
        query = params['query']
        if not isinstance(query, str) or len(query.strip()) == 0:
            return False
        
        # Validate max_results if present
        if 'max_results' in params:
            max_results = params['max_results']
            if not isinstance(max_results, int) or max_results <= 0:
                return False
        
        # Validate sort_by if present
        if 'sort_by' in params:
            valid_sorts = ['relevance', 'date', 'views']
            if params['sort_by'] not in valid_sorts:
                return False
        
        # Validate upload_date if present
        if 'upload_date' in params:
            valid_dates = ['today', 'week', 'month', 'year']
            if params['upload_date'] not in valid_dates:
                return False
        
        return True
```

### Task Parameters Format

```json
{
    "query": "startup ideas",
    "max_results": 50,
    "sort_by": "relevance",
    "upload_date": "week",
    "min_duration": 15,
    "max_duration": 180
}
```

### Search Filters

**Sort Options:**
- `relevance` - Most relevant (default)
- `date` - Most recent
- `views` - Most viewed

**Upload Date Options:**
- `today` - Uploaded today
- `week` - Last 7 days
- `month` - Last 30 days
- `year` - Last year
- `null` - All time (default)

### Dependencies

- Issue #002 - Worker Base Class (required)
- Issue #003 - Task Polling (required)
- Issue #004 - Task Schema (required)
- yt-dlp library (for search)

### SOLID Principles Analysis

**Single Responsibility Principle (SRP)**
- ✅ Worker handles task execution
- ✅ Search logic separated into methods
- ✅ Filtering logic isolated

**Open/Closed Principle (OCP)**
- ✅ Extends YouTubeWorkerBase
- ✅ Can add new search filters without modifying core

**Liskov Substitution Principle (LSP)**
- ✅ Can substitute YouTubeWorkerBase
- ✅ Follows base class contract

**Interface Segregation Principle (ISP)**
- ✅ Implements only required worker methods
- ✅ No unused methods

**Dependency Inversion Principle (DIP)**
- ✅ Depends on abstractions (WorkerBase, TaskQueue)
- ✅ Config and DB injected

## Estimated Effort
2 days

## Target Platform
- Windows
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [x] Unit tests for worker methods
- [x] Parameter validation tests
- [x] Search filter tests (mock yt-dlp)
- [x] Shorts filtering tests
- [x] Test different query types
- [x] Test sort options
- [x] Test upload date filters
- [x] Test error handling
- [ ] Integration tests with real yt-dlp (manual)
- [ ] Performance tests (search speed)

## Related Issues

- Issue #001 - Master Plan
- Issue #002 - Worker Base Class (depends on)
- Issue #003 - Task Polling (depends on)
- Issue #004 - Task Schema (depends on)
- Issue #005 - Migrate Channel Plugin (similar pattern)
- Issue #006 - Migrate Trending Plugin (similar pattern)

## Notes

### Use Cases

**Content Discovery**
- Search for specific topics or trends
- Find content related to keywords
- Discover niche content

**Trend Analysis**
- Track keyword popularity over time
- Compare search results across dates
- Identify emerging topics

**Content Research**
- Research competitor content
- Find inspiration for new content
- Analyze successful content patterns

### Feature Advantages

- ✅ No API quota limits (uses yt-dlp)
- ✅ Advanced search filters
- ✅ Shorts-specific filtering
- ✅ Deduplication with existing content
- ✅ Worker-based = schedulable searches

### Performance Considerations

- Search can be slow for large result sets
- Consider pagination for >100 results
- Rate limiting to respect YouTube ToS
- Caching search results (optional)

### Testing Queries

Good test queries:
- "startup ideas" - General topic
- "business tips" - Popular niche
- "productivity hacks" - Trending topic
- "cooking recipes" - High volume
- "tech news" - News content

### Future Enhancements

- Advanced search operators (AND, OR, NOT)
- Channel filtering in search
- Subscription-based searches
- Search result ranking
- Duplicate detection across sources
- Search history tracking
- Popular search suggestions
