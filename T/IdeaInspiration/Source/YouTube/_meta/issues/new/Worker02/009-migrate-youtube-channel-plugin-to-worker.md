# Issue #009: Migrate YouTubeChannelPlugin to Worker

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 02 - Python Specialist  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: High  
**Duration**: 2 days  
**Dependencies**: #002 (Worker Base Class), #005 (Plugin Architecture Refactor)

---

## Worker Details: Worker02 - Python Specialist

**Role**: Plugin Migration to Worker Pattern  
**Expertise Required**:
- Python 3.10+ (inheritance, abstract classes)
- YouTube scraping (yt-dlp)
- Worker pattern implementation
- SQLite integration
- Testing (pytest, mocking)

**Collaboration**:
- **Worker02** (self): Build on #002, #005
- **Worker06** (Database): Coordinate on result storage
- **Worker01** (PM): Daily standup, progress reporting

**See**: `_meta/issues/new/Worker02/README.md` for complete role description

---

## Objective

Migrate the existing YouTubeChannelPlugin to use the worker base class and plugin architecture, enabling channel scraping as worker tasks that can be queued, claimed, and executed by workers.

---

## Problem Statement

The current `youtube_channel_plugin.py` exists but is not integrated with the worker pattern. It needs to:

1. Extend the refactored `PluginBase` from #005
2. Work with the `BaseWorker` from #002
3. Accept task parameters from the queue
4. Return standardized `TaskResult` objects
5. Handle errors appropriately
6. Support worker-based execution lifecycle

**Current Location**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_channel_plugin.py`

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**One Responsibility**: Channel scraping logic only
- Scrape videos from YouTube channels
- Parse channel data
- Extract video metadata

**NOT Responsible For**:
- Task queue management (handled by worker)
- Database storage (handled by result storage layer)
- Task claiming/reporting (handled by BaseWorker)

### Open/Closed Principle (OCP) ✅
**Open for Extension**:
- Can extend scraping features
- Can add new parameters
- Can customize result formatting

**Closed for Modification**:
- Core scraping interface remains stable
- Worker integration doesn't change
- Plugin registration pattern fixed

### Liskov Substitution Principle (LSP) ✅
**Substitutability**:
- Can be used anywhere `PluginBase` is expected
- Works with any worker that supports plugins
- Consistent with other plugin implementations

### Interface Segregation Principle (ISP) ✅
**Minimal Interface**:
- Implements only `PluginBase` methods
- No unnecessary dependencies
- Clean parameter validation

### Dependency Inversion Principle (DIP) ✅
**Depend on Abstractions**:
- Depends on `PluginBase` interface
- Dependencies injected via constructor
- No tight coupling to specific implementations

---

## Current Implementation Analysis

### Existing Plugin Structure

The current `youtube_channel_plugin.py` likely has:
- `YouTubeChannelPlugin` class
- `scrape()` or `fetch()` method
- yt-dlp integration
- Basic error handling

### What Needs to Change

1. **Inherit from new PluginBase** (from #005)
2. **Implement required methods**:
   - `get_metadata()` - Return plugin metadata
   - `scrape(**params)` - Main scraping method
   - `validate_parameters(params)` - Validate inputs
3. **Standardize parameters**:
   - `channel_url` (required)
   - `top_n` (optional, default: 10)
   - `max_age_days` (optional)
4. **Return standardized results**:
   - List of video dictionaries
   - Consistent schema across all plugins
5. **Add proper error handling**:
   - Network errors
   - Invalid channel URLs
   - API rate limits

---

## Proposed Solution

### 1. Refactor Plugin Class

**File**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_channel_plugin.py`

```python
"""YouTube channel scraping plugin for worker system.

This plugin scrapes videos from YouTube channels using yt-dlp.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from .base_plugin import PluginBase, PluginMetadata


logger = logging.getLogger(__name__)


class YouTubeChannelPlugin(PluginBase):
    """YouTube channel scraping plugin.
    
    Scrapes video metadata from YouTube channels using yt-dlp.
    Implements the PluginBase interface for worker integration.
    
    Task Parameters:
        channel_url (str): YouTube channel URL (required)
        top_n (int): Number of videos to scrape (default: 10)
        max_age_days (int): Maximum age of videos in days (optional)
    
    Returns:
        List of video dictionaries with standardized schema
    
    Example:
        >>> plugin = YouTubeChannelPlugin(config, database, metrics)
        >>> results = plugin.scrape(
        ...     channel_url='https://youtube.com/@channel',
        ...     top_n=50
        ... )
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="YouTube Channel Scraper",
            task_type="channel_scrape",
            version="2.0.0",
            description="Scrape videos from YouTube channels using yt-dlp"
        )
    
    def scrape(self, **params) -> List[Dict[str, Any]]:
        """Scrape videos from a YouTube channel.
        
        Args:
            channel_url: YouTube channel URL (required)
            top_n: Number of videos to scrape (default: 10)
            max_age_days: Maximum age of videos in days (optional)
            
        Returns:
            List of video dictionaries with schema:
            {
                'video_id': str,
                'title': str,
                'url': str,
                'channel': str,
                'channel_url': str,
                'published_date': str (ISO 8601),
                'view_count': int,
                'like_count': int,
                'duration_seconds': int,
                'thumbnail_url': str,
                'description': str,
                'tags': List[str]
            }
            
        Raises:
            ValueError: If parameters are invalid
            Exception: On scraping errors
        """
        # Validate parameters
        if not self.validate_parameters(params):
            raise ValueError(f"Invalid parameters for channel_scrape: {params}")
        
        channel_url = params['channel_url']
        top_n = params.get('top_n', 10)
        max_age_days = params.get('max_age_days')
        
        logger.info(
            f"Scraping channel: {channel_url} "
            f"(top_n={top_n}, max_age_days={max_age_days})"
        )
        
        try:
            # Use yt-dlp to scrape channel
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'playlistend': top_n,
            }
            
            results = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract channel info
                info = ydl.extract_info(channel_url, download=False)
                
                if not info or 'entries' not in info:
                    logger.warning(f"No videos found for channel: {channel_url}")
                    return []
                
                # Process each video
                for entry in info['entries'][:top_n]:
                    if not entry:
                        continue
                    
                    # Filter by age if specified
                    if max_age_days:
                        upload_date = entry.get('upload_date')
                        if upload_date:
                            video_date = datetime.strptime(upload_date, '%Y%m%d')
                            age_days = (datetime.now() - video_date).days
                            if age_days > max_age_days:
                                continue
                    
                    # Standardize video data
                    video_data = self._standardize_video(entry)
                    results.append(video_data)
            
            logger.info(f"Scraped {len(results)} videos from {channel_url}")
            return results
            
        except Exception as e:
            logger.error(f"Error scraping channel {channel_url}: {e}")
            raise
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate scraping parameters.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required parameters
        if 'channel_url' not in params:
            logger.error("Missing required parameter: channel_url")
            return False
        
        channel_url = params['channel_url']
        
        # Validate channel URL format
        if not isinstance(channel_url, str):
            logger.error(f"channel_url must be string, got {type(channel_url)}")
            return False
        
        if not channel_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid channel URL format: {channel_url}")
            return False
        
        # Validate optional parameters
        top_n = params.get('top_n', 10)
        if not isinstance(top_n, int) or top_n < 1 or top_n > 500:
            logger.error(f"top_n must be integer between 1 and 500, got {top_n}")
            return False
        
        max_age_days = params.get('max_age_days')
        if max_age_days is not None:
            if not isinstance(max_age_days, int) or max_age_days < 1:
                logger.error(f"max_age_days must be positive integer, got {max_age_days}")
                return False
        
        return True
    
    def _standardize_video(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize video data to consistent schema.
        
        Args:
            entry: Raw yt-dlp video entry
            
        Returns:
            Standardized video dictionary
        """
        return {
            'video_id': entry.get('id', ''),
            'title': entry.get('title', ''),
            'url': entry.get('webpage_url', f"https://youtube.com/watch?v={entry.get('id', '')}"),
            'channel': entry.get('channel', ''),
            'channel_url': entry.get('channel_url', ''),
            'published_date': self._format_date(entry.get('upload_date')),
            'view_count': entry.get('view_count', 0),
            'like_count': entry.get('like_count', 0),
            'duration_seconds': entry.get('duration', 0),
            'thumbnail_url': entry.get('thumbnail', ''),
            'description': entry.get('description', ''),
            'tags': entry.get('tags', []),
        }
    
    def _format_date(self, upload_date: Optional[str]) -> str:
        """Format upload date to ISO 8601.
        
        Args:
            upload_date: Date string in YYYYMMDD format
            
        Returns:
            ISO 8601 formatted date string
        """
        if not upload_date:
            return ''
        
        try:
            dt = datetime.strptime(upload_date, '%Y%m%d')
            return dt.isoformat()
        except (ValueError, TypeError):
            return ''
```

### 2. Create Concrete Worker (Optional)

**File**: `Sources/Content/Shorts/YouTube/src/workers/youtube_channel_worker.py`

```python
"""Concrete worker for YouTube channel scraping.

This worker handles channel_scrape tasks using YouTubeChannelPlugin.
"""

from typing import Dict, Any
import logging

from .base_worker import BaseWorker
from ..workers import Task, TaskResult
from ..plugins import PluginFactory


logger = logging.getLogger(__name__)


class YouTubeChannelWorker(BaseWorker):
    """Worker for channel scraping tasks.
    
    Handles 'channel_scrape' task type using YouTubeChannelPlugin.
    """
    
    def process_task(self, task: Task) -> TaskResult:
        """Process a channel scraping task.
        
        Args:
            task: Task with type 'channel_scrape'
            
        Returns:
            TaskResult with scraped videos
        """
        logger.info(f"Processing channel scrape task {task.id}")
        
        try:
            # Create plugin via factory
            plugin = self.plugin_factory.create_plugin('channel_scrape')
            
            # Validate parameters
            if not plugin.validate_parameters(task.parameters):
                return TaskResult(
                    success=False,
                    error="Invalid task parameters"
                )
            
            # Execute scraping
            videos = plugin.scrape(**task.parameters)
            
            # Return success result
            return TaskResult(
                success=True,
                data={'videos': videos},
                items_processed=len(videos),
                metrics={
                    'channel_url': task.parameters.get('channel_url'),
                    'videos_scraped': len(videos)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in channel scrape task {task.id}: {e}")
            return TaskResult(
                success=False,
                error=str(e)
            )
```

### 3. Update Plugin Registration

**File**: `Sources/Content/Shorts/YouTube/src/plugins/__init__.py`

Ensure `YouTubeChannelPlugin` is registered:

```python
from .youtube_channel_plugin import YouTubeChannelPlugin

def register_default_plugins():
    """Register default plugins on import."""
    registry = PluginRegistry.get_instance()
    registry.register(YouTubeChannelPlugin)
    # ... other plugins ...
```

---

## Implementation Plan

### Step 1: Refactor Plugin Class (Day 1, Morning)
- Update class to extend new `PluginBase`
- Implement required methods (`get_metadata`, `validate_parameters`)
- Keep existing `scrape()` logic but standardize interface

### Step 2: Standardize Results (Day 1, Afternoon)
- Define consistent video schema
- Add `_standardize_video()` helper method
- Ensure all video data has same structure

### Step 3: Add Parameter Validation (Day 1, Evening)
- Implement comprehensive `validate_parameters()`
- Add validation for `channel_url`, `top_n`, `max_age_days`
- Add logging for validation errors

### Step 4: Create Concrete Worker (Day 2, Morning)
- Create `YouTubeChannelWorker` class (optional)
- Integrate with `BaseWorker`
- Use `PluginFactory` to get plugin instance

### Step 5: Testing (Day 2, Afternoon)
- Unit tests for plugin
- Test parameter validation
- Test with real channel URLs
- Integration test with worker

### Step 6: Documentation (Day 2, Evening)
- Update docstrings
- Add usage examples
- Document parameter schema
- Update README

---

## Acceptance Criteria

### Functional Requirements
- [ ] `YouTubeChannelPlugin` extends new `PluginBase`
- [ ] Implements all required abstract methods
- [ ] `scrape()` method works with task parameters
- [ ] Returns standardized video data schema
- [ ] Parameter validation working
- [ ] Handles errors gracefully
- [ ] Integrates with worker base class

### Non-Functional Requirements
- [ ] SOLID principles maintained
- [ ] No breaking changes to scraping logic
- [ ] Backward compatibility preserved
- [ ] Performance similar to current implementation
- [ ] Logging comprehensive

### Code Quality
- [ ] Type hints on all methods
- [ ] Docstrings (Google style) complete
- [ ] mypy type checking passes
- [ ] pylint score >8.5/10

### Testing Requirements
- [ ] Unit tests for plugin methods
- [ ] Test parameter validation (valid and invalid)
- [ ] Test with multiple channel URLs
- [ ] Integration test with worker
- [ ] Test error handling
- [ ] Test coverage >80%

---

## Testing Strategy

### Unit Tests

**File**: `_meta/tests/test_youtube_channel_plugin.py`

```python
import pytest
from unittest.mock import Mock, patch
from src.plugins.youtube_channel_plugin import YouTubeChannelPlugin


def test_plugin_metadata():
    """Test plugin metadata is correct."""
    plugin = YouTubeChannelPlugin(None, None, None)
    metadata = plugin.get_metadata()
    
    assert metadata.name == "YouTube Channel Scraper"
    assert metadata.task_type == "channel_scrape"
    assert metadata.version == "2.0.0"


def test_parameter_validation_success():
    """Test valid parameters pass validation."""
    plugin = YouTubeChannelPlugin(None, None, None)
    
    params = {
        'channel_url': 'https://youtube.com/@channel',
        'top_n': 10
    }
    
    assert plugin.validate_parameters(params) is True


def test_parameter_validation_missing_url():
    """Test validation fails without channel_url."""
    plugin = YouTubeChannelPlugin(None, None, None)
    
    params = {'top_n': 10}
    
    assert plugin.validate_parameters(params) is False


def test_parameter_validation_invalid_url():
    """Test validation fails with invalid URL."""
    plugin = YouTubeChannelPlugin(None, None, None)
    
    params = {'channel_url': 'not-a-url'}
    
    assert plugin.validate_parameters(params) is False


def test_parameter_validation_invalid_top_n():
    """Test validation fails with invalid top_n."""
    plugin = YouTubeChannelPlugin(None, None, None)
    
    params = {
        'channel_url': 'https://youtube.com/@channel',
        'top_n': 0
    }
    
    assert plugin.validate_parameters(params) is False


@patch('src.plugins.youtube_channel_plugin.yt_dlp.YoutubeDL')
def test_scrape_success(mock_ydl):
    """Test successful channel scraping."""
    # Mock yt-dlp response
    mock_ydl.return_value.__enter__.return_value.extract_info.return_value = {
        'entries': [
            {
                'id': 'video1',
                'title': 'Test Video',
                'upload_date': '20251111',
                'view_count': 1000,
                'like_count': 50,
                'duration': 300,
            }
        ]
    }
    
    plugin = YouTubeChannelPlugin(Mock(), Mock(), Mock())
    
    results = plugin.scrape(
        channel_url='https://youtube.com/@test',
        top_n=1
    )
    
    assert len(results) == 1
    assert results[0]['video_id'] == 'video1'
    assert results[0]['title'] == 'Test Video'


def test_scrape_invalid_parameters():
    """Test scrape raises error with invalid parameters."""
    plugin = YouTubeChannelPlugin(Mock(), Mock(), Mock())
    
    with pytest.raises(ValueError):
        plugin.scrape(invalid_param='value')
```

### Integration Tests

```python
def test_worker_integration():
    """Test plugin works with BaseWorker."""
    from src.workers.base_worker import BaseWorker
    from src.workers import Task, TaskStatus
    
    # Create mock worker
    # Create task
    # Process task using plugin
    # Verify result
    pass
```

---

## Files to Modify

1. `Sources/Content/Shorts/YouTube/src/plugins/youtube_channel_plugin.py` - Refactor plugin
2. `Sources/Content/Shorts/YouTube/src/plugins/__init__.py` - Update registration
3. `Sources/Content/Shorts/YouTube/src/workers/youtube_channel_worker.py` - NEW: Concrete worker (optional)

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/_meta/tests/test_youtube_channel_plugin.py` - Unit tests
2. `Sources/Content/Shorts/YouTube/_meta/tests/test_youtube_channel_worker.py` - Worker tests

---

## Dependencies

### External
- yt-dlp (existing dependency)
- Python 3.10+

### Internal
- #002 (BaseWorker) - Required
- #005 (PluginBase) - Required
- #004 (Database Schema) - For result storage

---

## Estimated Effort

**2 days**:
- Day 1: Refactor plugin, standardize results, parameter validation
- Day 2: Concrete worker (optional), testing, documentation

---

## Target Platform

- Windows (primary)
- Python 3.10+
- yt-dlp for YouTube scraping

---

## Related Issues

- **#001**: Master plan (parent)
- **#002**: Worker base class (dependency)
- **#005**: Plugin architecture refactor (dependency)
- **#010**: Trending plugin migration (similar)
- **#011**: Keyword search plugin (similar)

---

## Notes

### Design Decisions

1. **Why standardize video schema?**
   - Consistent data format across all plugins
   - Easier to process and store
   - Reduces coupling between plugins and consumers

2. **Why optional concrete worker?**
   - BaseWorker can handle plugin execution generically
   - Concrete worker only needed for custom logic
   - Keeps implementation flexible

3. **Why validate parameters separately?**
   - Clear separation of concerns
   - Better error messages
   - Testable in isolation

### Migration Strategy

1. Keep existing implementation intact
2. Add new methods around it
3. Test thoroughly before deployment
4. No breaking changes

### Performance Considerations

- yt-dlp is the bottleneck (network I/O)
- Worker implementation adds minimal overhead
- Standardization adds ~1ms per video (negligible)

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker02 - Python Specialist  
**Estimated Start**: Week 2, Day 1 (after #005 complete)  
**Estimated Completion**: Week 2, Day 2
