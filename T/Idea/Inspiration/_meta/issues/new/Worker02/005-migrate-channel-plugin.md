# Issue #005: Migrate YouTubeChannelPlugin to Worker Pattern

## Status
New

## Priority
High

## Category
Feature - Plugin Migration

## Description

Migrate the existing `YouTubeChannelPlugin` to use the worker-based architecture. This is the first and highest priority plugin migration as channel scraping is the most commonly used mode.

## Problem Statement

The current `YouTubeChannelPlugin` works well but executes directly when called. It needs to be refactored to work as a worker that processes tasks from the queue, enabling better scalability, persistence, and monitoring.

## Proposed Solution

Create `YouTubeChannelWorker` that:
- Extends `YouTubeWorkerBase`
- Uses existing channel scraping logic from `YouTubeChannelPlugin`
- Processes tasks from the SQLite queue
- Reports results to TaskManager API
- Maintains all current functionality

## Acceptance Criteria

- [ ] `YouTubeChannelWorker` class created extending `YouTubeWorkerBase`
- [ ] Channel scraping logic migrated from plugin
- [ ] Task parameter validation implemented
- [ ] Results saved to both local DB and queue
- [ ] Error handling with retry logic
- [ ] Maintains yt-dlp integration
- [ ] Subtitle extraction still works
- [ ] Metrics calculation preserved
- [ ] All existing tests pass
- [ ] New worker-specific tests added
- [ ] Documentation updated

## Technical Details

### Implementation Approach

1. Create `YouTubeChannelWorker` in `src/workers/`
2. Extract core logic from `YouTubeChannelPlugin`
3. Implement `execute_task()` method
4. Add parameter validation
5. Integrate with task queue
6. Preserve all existing functionality

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/src/workers/channel_worker.py`
  - YouTubeChannelWorker class
  - Task execution logic
  - Parameter validation

- **Modify**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_channel_plugin.py`
  - Keep plugin for backward compatibility
  - Optionally delegate to worker

- **Create**: `Sources/Content/Shorts/YouTube/tests/test_channel_worker.py`
  - Worker-specific tests
  - Mock task queue
  - End-to-end tests

### Worker Implementation

```python
from typing import Dict, Any
from ..core.worker_base import YouTubeWorkerBase, WorkerConfig
from ..plugins.youtube_channel_plugin import YouTubeChannelPlugin
import json

class YouTubeChannelWorker(YouTubeWorkerBase):
    """Worker for YouTube channel scraping tasks"""
    
    def __init__(self, config: WorkerConfig, task_queue, db, app_config):
        super().__init__(config, task_queue)
        self.db = db
        self.app_config = app_config
        self._plugin = None
        
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute channel scraping task.
        
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
            self._plugin = YouTubeChannelPlugin(self.app_config)
        
        # Extract parameters
        channel_url = params['channel_url']
        max_results = params.get('max_results', 50)
        
        # Execute scraping
        ideas = self._plugin.scrape_channel(
            channel_url=channel_url,
            max_results=max_results
        )
        
        # Save to local database
        saved_count = 0
        for idea in ideas:
            self.db.insert_idea(
                source='youtube_channel',
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
            'channel_url': channel_url
        }
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Validate task parameters.
        
        Args:
            params: Parameters dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['channel_url']
        
        # Check required fields
        for field in required_fields:
            if field not in params:
                return False
        
        # Validate channel URL format
        channel_url = params['channel_url']
        if not (channel_url.startswith('@') or 
                'youtube.com' in channel_url or
                'youtu.be' in channel_url):
            return False
        
        # Validate max_results if present
        if 'max_results' in params:
            max_results = params['max_results']
            if not isinstance(max_results, int) or max_results <= 0:
                return False
        
        return True
```

### Task Parameters Format

```json
{
    "channel_url": "@SnappyStories_1",
    "max_results": 50,
    "include_subtitles": true,
    "min_duration": 15,
    "max_duration": 180
}
```

### Dependencies

- Issue #002 - Worker Base Class (required)
- Issue #003 - Task Polling (required)
- Issue #004 - Task Schema (required)
- Existing YouTubeChannelPlugin (reuse logic)
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
- ✅ Can use any plugin implementing the interface

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
- [x] Mock plugin for testing
- [x] Test task execution end-to-end
- [x] Test error handling
- [x] Test result format
- [ ] Integration tests with real yt-dlp (manual)
- [ ] Performance tests (compare to direct execution)

## Related Issues

- Issue #001 - Master Plan
- Issue #002 - Worker Base Class (depends on)
- Issue #003 - Task Polling (depends on)
- Issue #004 - Task Schema (depends on)
- Issue #006 - Migrate Trending Plugin (similar pattern)
- Issue #007 - Migrate Keyword Search (similar pattern)

## Notes

### Migration Strategy

1. **Phase 1**: Create worker alongside existing plugin
2. **Phase 2**: Test worker in isolation
3. **Phase 3**: Integrate with task queue
4. **Phase 4**: Update CLI to use worker (optional)
5. **Phase 5**: Keep plugin for backward compatibility

### Backward Compatibility

- Keep existing plugin interface intact
- CLI can use either worker or plugin
- Gradual migration path

### Feature Parity

Must maintain all current features:
- ✅ Channel URL support (@username, full URL)
- ✅ Max results limit
- ✅ Subtitle extraction
- ✅ Metrics calculation
- ✅ Deduplication
- ✅ Error handling
- ✅ Progress logging

### Performance Considerations

- Worker adds minimal overhead
- Task queue enables better resource management
- Can run multiple workers in parallel
- Persistent queue survives restarts

### Testing with Real Channels

Test channels for validation:
- `@SnappyStories_1` - Small channel, fast testing
- `@MrBeast` - Large channel, stress testing
- Invalid channels - Error handling

## Future Enhancements

- Batch channel scraping (multiple channels per task)
- Incremental scraping (only new videos)
- Channel monitoring (periodic re-scraping)
- Rate limiting per channel
- Webhook notifications on completion
