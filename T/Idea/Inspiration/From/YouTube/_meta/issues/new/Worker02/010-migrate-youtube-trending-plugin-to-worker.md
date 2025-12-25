# Issue #010: Migrate YouTubeTrendingPlugin to Worker

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 02 - Python Specialist  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: High  
**Duration**: 2 days  
**Dependencies**: #002 (Worker Base Class), #005 (Plugin Architecture Refactor), #009 (Channel Plugin - for pattern reference)

---

## Worker Details: Worker02 - Python Specialist

**Role**: Plugin Migration to Worker Pattern  
**Expertise Required**:
- Python 3.10+ (inheritance, abstract classes)
- Web scraping (BeautifulSoup, requests, or yt-dlp)
- Worker pattern implementation
- SQLite integration
- Testing (pytest, mocking)

**Collaboration**:
- **Worker02** (self): Build on #002, #005, #009
- **Worker06** (Database): Coordinate on result storage
- **Worker01** (PM): Daily standup, progress reporting

**See**: `_meta/issues/new/Worker02/README.md` for complete role description

---

## Objective

Migrate the existing YouTubeTrendingPlugin to use the worker base class and plugin architecture, enabling trending page scraping as worker tasks that can be queued, claimed, and executed by workers.

---

## Problem Statement

The current `youtube_trending_plugin.py` exists but is not integrated with the worker pattern. It needs to:

1. Extend the refactored `PluginBase` from #005
2. Work with the `BaseWorker` from #002
3. Accept task parameters from the queue
4. Return standardized `TaskResult` objects
5. Handle errors appropriately
6. Support worker-based execution lifecycle

**Current Location**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_trending_plugin.py`

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**One Responsibility**: Trending page scraping logic only
- Scrape videos from YouTube trending page
- Parse trending video data
- Extract video metadata

**NOT Responsible For**:
- Task queue management (handled by worker)
- Database storage (handled by result storage layer)
- Task claiming/reporting (handled by BaseWorker)

### Open/Closed Principle (OCP) ✅
**Open for Extension**:
- Can extend scraping features
- Can add new parameters (country, category)
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

## Proposed Solution

### 1. Refactor Plugin Class

**File**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_trending_plugin.py`

```python
"""YouTube trending page scraping plugin for worker system.

This plugin scrapes videos from YouTube trending page.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .base_plugin import PluginBase, PluginMetadata


logger = logging.getLogger(__name__)


class YouTubeTrendingPlugin(PluginBase):
    """YouTube trending page scraping plugin.
    
    Scrapes video metadata from YouTube trending page using yt-dlp or web scraping.
    Implements the PluginBase interface for worker integration.
    
    Task Parameters:
        country (str): Country code for trending (default: 'US')
        category (str): Category filter (default: 'all')
        top_n (int): Number of videos to scrape (default: 50)
    
    Returns:
        List of trending video dictionaries with standardized schema
    
    Example:
        >>> plugin = YouTubeTrendingPlugin(config, database, metrics)
        >>> results = plugin.scrape(
        ...     country='US',
        ...     top_n=50
        ... )
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="YouTube Trending Scraper",
            task_type="trending_scrape",
            version="2.0.0",
            description="Scrape videos from YouTube trending page"
        )
    
    def scrape(self, **params) -> List[Dict[str, Any]]:
        """Scrape videos from YouTube trending page.
        
        Args:
            country: Country code for trending (default: 'US')
            category: Category filter (default: 'all')
            top_n: Number of videos to scrape (default: 50)
            
        Returns:
            List of video dictionaries with standardized schema (same as channel plugin)
            
        Raises:
            ValueError: If parameters are invalid
            Exception: On scraping errors
        """
        # Validate parameters
        if not self.validate_parameters(params):
            raise ValueError(f"Invalid parameters for trending_scrape: {params}")
        
        country = params.get('country', 'US')
        category = params.get('category', 'all')
        top_n = params.get('top_n', 50)
        
        logger.info(
            f"Scraping trending page: country={country}, "
            f"category={category}, top_n={top_n}"
        )
        
        try:
            # Build trending URL
            trending_url = self._build_trending_url(country, category)
            
            # Use yt-dlp to scrape trending page
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'playlistend': top_n,
            }
            
            results = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract trending videos
                info = ydl.extract_info(trending_url, download=False)
                
                if not info or 'entries' not in info:
                    logger.warning(f"No videos found on trending page: {trending_url}")
                    return []
                
                # Process each video
                for entry in info['entries'][:top_n]:
                    if not entry:
                        continue
                    
                    # Standardize video data
                    video_data = self._standardize_video(entry)
                    video_data['trending_country'] = country
                    video_data['trending_category'] = category
                    results.append(video_data)
            
            logger.info(f"Scraped {len(results)} videos from trending page")
            return results
            
        except Exception as e:
            logger.error(f"Error scraping trending page: {e}")
            raise
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate scraping parameters.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Validate country code
        country = params.get('country', 'US')
        if not isinstance(country, str) or len(country) != 2:
            logger.error(f"Invalid country code: {country}")
            return False
        
        # Validate category
        valid_categories = ['all', 'music', 'gaming', 'news', 'movies']
        category = params.get('category', 'all')
        if category not in valid_categories:
            logger.error(f"Invalid category: {category}. Must be one of {valid_categories}")
            return False
        
        # Validate top_n
        top_n = params.get('top_n', 50)
        if not isinstance(top_n, int) or top_n < 1 or top_n > 200:
            logger.error(f"top_n must be integer between 1 and 200, got {top_n}")
            return False
        
        return True
    
    def _build_trending_url(self, country: str, category: str) -> str:
        """Build YouTube trending URL.
        
        Args:
            country: Country code (e.g., 'US', 'GB')
            category: Category filter ('all', 'music', 'gaming', etc.)
            
        Returns:
            Trending page URL
        """
        base_url = "https://www.youtube.com/feed/trending"
        
        # Add country parameter
        url = f"{base_url}?gl={country}"
        
        # Add category if not 'all'
        if category != 'all':
            # Map category to YouTube parameter
            category_map = {
                'music': 'bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D',
                'gaming': 'bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D',
                'news': 'bp=4gIKGgh0cmFuc2xhdGU%3D',
                'movies': 'bp=4gIKGgh0cmFpbGVycw%3D%3D',
            }
            if category in category_map:
                url += f"&{category_map[category]}"
        
        return url
    
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

---

## Implementation Plan

### Step 1: Refactor Plugin Class (Day 1, Morning)
- Update class to extend new `PluginBase`
- Implement required methods
- Keep existing scraping logic but standardize interface

### Step 2: Add Trending URL Building (Day 1, Afternoon)
- Implement `_build_trending_url()` method
- Support country codes
- Support category filters

### Step 3: Parameter Validation (Day 1, Evening)
- Implement comprehensive `validate_parameters()`
- Validate country, category, top_n
- Add logging for validation errors

### Step 4: Testing (Day 2)
- Unit tests for plugin
- Test parameter validation
- Test with real trending URLs
- Integration test with worker
- Documentation updates

---

## Acceptance Criteria

### Functional Requirements
- [ ] `YouTubeTrendingPlugin` extends new `PluginBase`
- [ ] Implements all required abstract methods
- [ ] `scrape()` method works with task parameters
- [ ] Returns standardized video data schema
- [ ] Parameter validation working
- [ ] Supports country and category parameters
- [ ] Handles errors gracefully
- [ ] Integrates with worker base class

### Code Quality
- [ ] Type hints on all methods
- [ ] Docstrings (Google style) complete
- [ ] mypy type checking passes
- [ ] pylint score >8.5/10
- [ ] Test coverage >80%

---

## Testing Strategy

```python
def test_plugin_metadata():
    """Test plugin metadata is correct."""
    plugin = YouTubeTrendingPlugin(None, None, None)
    metadata = plugin.get_metadata()
    
    assert metadata.task_type == "trending_scrape"


def test_parameter_validation_success():
    """Test valid parameters pass validation."""
    plugin = YouTubeTrendingPlugin(None, None, None)
    
    params = {
        'country': 'US',
        'category': 'music',
        'top_n': 50
    }
    
    assert plugin.validate_parameters(params) is True


def test_build_trending_url():
    """Test trending URL building."""
    plugin = YouTubeTrendingPlugin(None, None, None)
    
    url = plugin._build_trending_url('US', 'all')
    assert 'youtube.com/feed/trending' in url
    assert 'gl=US' in url
```

---

## Files to Modify

1. `Sources/Content/Shorts/YouTube/src/plugins/youtube_trending_plugin.py` - Refactor plugin
2. `Sources/Content/Shorts/YouTube/src/plugins/__init__.py` - Update registration

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/_meta/tests/test_youtube_trending_plugin.py` - Unit tests

---

## Dependencies

### Internal
- #002 (BaseWorker) - Required
- #005 (PluginBase) - Required
- #009 (Channel Plugin) - Pattern reference

---

## Estimated Effort

**2 days**:
- Day 1: Refactor plugin, URL building, parameter validation
- Day 2: Testing, documentation

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker02 - Python Specialist  
**Estimated Start**: Week 2, Day 3 (after #009 complete)  
**Estimated Completion**: Week 2, Day 4
