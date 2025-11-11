# Issue #006: Migrate YouTubeTrendingPlugin to Worker Pattern

## Status
New

## Priority
Medium

## Category
Feature - Plugin Migration

## Description

Migrate the existing `YouTubeTrendingPlugin` to use the worker-based architecture. This enables trending page scraping as a background task that can be scheduled and monitored.

## Problem Statement

The current `YouTubeTrendingPlugin` works but executes synchronously. Converting it to a worker enables scheduled trending scans, better error handling, and integration with the task management system.

## Proposed Solution

Create `YouTubeTrendingWorker` that:
- Extends `YouTubeWorkerBase`
- Uses existing trending scraping logic
- Processes tasks from the SQLite queue
- Supports different trending categories (Gaming, Music, etc.)
- Reports results to TaskManager API

## Acceptance Criteria

- [ ] `YouTubeTrendingWorker` class created extending `YouTubeWorkerBase`
- [ ] Trending scraping logic migrated from plugin
- [ ] Task parameter validation implemented
- [ ] Support for trending categories (optional)
- [ ] Support for region-specific trending
- [ ] Results saved to both local DB and queue
- [ ] Error handling with retry logic
- [ ] All existing tests pass
- [ ] New worker-specific tests added
- [ ] Documentation updated

## Technical Details

### Implementation Approach

1. Create `YouTubeTrendingWorker` in `src/workers/`
2. Extract core logic from `YouTubeTrendingPlugin`
3. Implement `execute_task()` method
4. Add parameter validation
5. Support trending categories and regions
6. Integrate with task queue

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/src/workers/trending_worker.py`
  - YouTubeTrendingWorker class
  - Task execution logic
  - Category/region support

- **Modify**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_trending_plugin.py`
  - Keep plugin for backward compatibility
  - Optionally delegate to worker

- **Create**: `Sources/Content/Shorts/YouTube/tests/test_trending_worker.py`
  - Worker-specific tests
  - Mock task queue
  - Category tests

### Worker Implementation

```python
from typing import Dict, Any, Optional
from ..core.worker_base import YouTubeWorkerBase, WorkerConfig
from ..plugins.youtube_trending_plugin import YouTubeTrendingPlugin
import json

class YouTubeTrendingWorker(YouTubeWorkerBase):
    """Worker for YouTube trending page scraping tasks"""
    
    def __init__(self, config: WorkerConfig, task_queue, db, app_config):
        super().__init__(config, task_queue)
        self.db = db
        self.app_config = app_config
        self._plugin = None
        
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trending scraping task.
        
        Args:
            task: Task dictionary with parameters
            
        Returns:
            Result dictionary with scraped ideas
        """
        params = json.loads(task['parameters'])
        
        # Validate parameters
        if not self.validate_parameters(params):
            raise ValueError(f"Invalid parameters: {params}")
        
        # Initialize plugin (lazy)
        if not self._plugin:
            self._plugin = YouTubeTrendingPlugin(self.app_config)
        
        # Extract parameters
        max_results = params.get('max_results', 50)
        category = params.get('category', None)  # Gaming, Music, etc.
        region = params.get('region', 'US')
        
        # Execute scraping
        ideas = self._plugin.scrape_trending(
            max_results=max_results,
            category=category,
            region=region
        )
        
        # Save to local database
        saved_count = 0
        for idea in ideas:
            self.db.insert_idea(
                source='youtube_trending',
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
            'ideas_scraped': len(ideas),
            'ideas_saved': saved_count,
            'category': category,
            'region': region
        }
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Validate task parameters.
        
        Args:
            params: Parameters dictionary
            
        Returns:
            True if valid, False otherwise
        """
        # Validate max_results if present
        if 'max_results' in params:
            max_results = params['max_results']
            if not isinstance(max_results, int) or max_results <= 0:
                return False
        
        # Validate category if present
        if 'category' in params:
            valid_categories = ['Gaming', 'Music', 'News', 'Sports', 'Entertainment']
            if params['category'] not in valid_categories:
                return False
        
        # Validate region if present
        if 'region' in params:
            region = params['region']
            if not isinstance(region, str) or len(region) != 2:
                return False
        
        return True
```

### Task Parameters Format

```json
{
    "max_results": 50,
    "category": "Gaming",
    "region": "US",
    "min_duration": 15,
    "max_duration": 180
}
```

### Supported Categories
- `Gaming` - Gaming content
- `Music` - Music videos
- `News` - News content
- `Sports` - Sports videos
- `Entertainment` - General entertainment
- `null` - All trending (default)

### Supported Regions
- `US` - United States (default)
- `GB` - United Kingdom
- `CA` - Canada
- `AU` - Australia
- Any ISO 3166-1 alpha-2 country code

### Dependencies

- Issue #002 - Worker Base Class (required)
- Issue #003 - Task Polling (required)
- Issue #004 - Task Schema (required)
- Existing YouTubeTrendingPlugin (reuse logic)
- yt-dlp library

### SOLID Principles Analysis

**Single Responsibility Principle (SRP)**
- ✅ Worker handles task execution only
- ✅ Plugin handles scraping logic only
- ✅ Separation of concerns maintained

**Open/Closed Principle (OCP)**
- ✅ Extends YouTubeWorkerBase without modifying it
- ✅ Plugin can be swapped/upgraded independently

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
1.5 days

## Target Platform
- Windows
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [x] Unit tests for worker methods
- [x] Parameter validation tests
- [x] Test different categories
- [x] Test different regions
- [x] Mock plugin for testing
- [x] Test task execution end-to-end
- [x] Test error handling
- [ ] Integration tests with real yt-dlp (manual)
- [ ] Compare results with direct plugin execution

## Related Issues

- Issue #001 - Master Plan
- Issue #002 - Worker Base Class (depends on)
- Issue #003 - Task Polling (depends on)
- Issue #004 - Task Schema (depends on)
- Issue #005 - Migrate Channel Plugin (similar pattern)
- Issue #007 - Implement Keyword Search Worker (similar pattern)

## Notes

### Migration Strategy

1. Create worker alongside existing plugin
2. Test worker in isolation
3. Integrate with task queue
4. Keep plugin for backward compatibility

### Use Cases

**Scheduled Trending Scans**
- Daily trending scan at peak hours
- Regional trending comparison
- Category-specific monitoring

**Discovery Pipeline**
- Automatic trending content discovery
- Integration with classification
- Scoring and ranking

### Feature Parity

Must maintain all current features:
- ✅ Max results limit
- ✅ Shorts filtering
- ✅ Metrics calculation
- ✅ Deduplication
- ✅ Error handling
- ✅ Progress logging

### Performance Considerations

- Trending page changes frequently
- Consider caching (5-15 minutes)
- Rate limiting to respect YouTube ToS
- Worker enables scheduled execution

### Testing Scenarios

1. Default trending (no category)
2. Category-specific trending
3. Different regions
4. Error handling (network issues)
5. Empty results handling
6. Duplicate detection

## Future Enhancements

- Trending change detection (what's new)
- Historical trending tracking
- Trending velocity calculation
- Category comparison
- Webhook notifications for viral content
- Scheduled periodic scans
