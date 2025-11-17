# Issue #011: Implement YouTube Keyword Search Worker

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 02 - Python Specialist  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: Medium  
**Duration**: 2-3 days  
**Dependencies**: #002 (Worker Base Class), #005 (Plugin Architecture Refactor), #009, #010 (for pattern reference)

---

## Worker Details: Worker02 - Python Specialist

**Role**: New Plugin Implementation  
**Expertise Required**:
- Python 3.10+ (inheritance, abstract classes)
- YouTube API or yt-dlp search functionality
- Worker pattern implementation
- SQLite integration
- Testing (pytest, mocking)

**Collaboration**:
- **Worker02** (self): Build on #002, #005, #009, #010
- **Worker06** (Database): Coordinate on result storage
- **Worker01** (PM): Daily standup, progress reporting

**See**: `_meta/issues/new/Worker02/README.md` for complete role description

---

## Objective

Implement a new YouTube keyword search plugin that enables searching for videos by keywords, phrases, or topics using the worker pattern. This expands scraping capabilities beyond channels and trending.

---

## Problem Statement

Currently, the YouTube module only supports:
1. Channel-based scraping (#009)
2. Trending page scraping (#010)

We need to add keyword/topic-based search to:
- Find videos by search queries
- Support filtering by date, views, duration
- Enable content discovery for specific topics
- Integrate with the worker pattern

This is a **new plugin**, not a migration, following the established pattern.

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**One Responsibility**: Keyword search scraping only
- Execute YouTube search queries
- Parse search results
- Extract video metadata

**NOT Responsible For**:
- Task queue management
- Database storage
- Task claiming/reporting

### Open/Closed Principle (OCP) ✅
**Open for Extension**:
- Can add new search filters
- Can customize ranking/sorting
- Can extend result processing

**Closed for Modification**:
- Core search interface stable
- Worker integration fixed

### Liskov Substitution Principle (LSP) ✅
**Substitutability**:
- Works anywhere `PluginBase` expected
- Consistent with other plugins

### Interface Segregation Principle (ISP) ✅
**Minimal Interface**:
- Implements only `PluginBase` methods
- No unnecessary dependencies

### Dependency Inversion Principle (DIP) ✅
**Depend on Abstractions**:
- Depends on `PluginBase` interface
- Dependencies injected via constructor

---

## Proposed Solution

### 1. Implement New Plugin

**File**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_keyword_plugin.py` (NEW)

```python
"""YouTube keyword search plugin for worker system.

This plugin searches for videos by keywords using yt-dlp.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from .base_plugin import PluginBase, PluginMetadata


logger = logging.getLogger(__name__)


class YouTubeKeywordPlugin(PluginBase):
    """YouTube keyword search plugin.
    
    Searches for videos by keywords/topics using yt-dlp search functionality.
    Implements the PluginBase interface for worker integration.
    
    Task Parameters:
        query (str): Search query/keywords (required)
        top_n (int): Number of results to return (default: 50)
        date_filter (str): Date filter ('day', 'week', 'month', 'year', 'all')
        duration_filter (str): Duration filter ('short', 'medium', 'long', 'all')
        sort_by (str): Sort order ('relevance', 'date', 'views', 'rating')
    
    Returns:
        List of video dictionaries with standardized schema
    
    Example:
        >>> plugin = YouTubeKeywordPlugin(config, database, metrics)
        >>> results = plugin.scrape(
        ...     query='python tutorial',
        ...     top_n=100,
        ...     date_filter='month'
        ... )
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="YouTube Keyword Search",
            task_type="keyword_search",
            version="1.0.0",
            description="Search for videos by keywords/topics"
        )
    
    def scrape(self, **params) -> List[Dict[str, Any]]:
        """Search for videos by keywords.
        
        Args:
            query: Search query/keywords (required)
            top_n: Number of results (default: 50)
            date_filter: Date filter (default: 'all')
            duration_filter: Duration filter (default: 'all')
            sort_by: Sort order (default: 'relevance')
            
        Returns:
            List of video dictionaries with standardized schema
            
        Raises:
            ValueError: If parameters are invalid
            Exception: On scraping errors
        """
        # Validate parameters
        if not self.validate_parameters(params):
            raise ValueError(f"Invalid parameters for keyword_search: {params}")
        
        query = params['query']
        top_n = params.get('top_n', 50)
        date_filter = params.get('date_filter', 'all')
        duration_filter = params.get('duration_filter', 'all')
        sort_by = params.get('sort_by', 'relevance')
        
        logger.info(
            f"Searching YouTube: query='{query}', top_n={top_n}, "
            f"date={date_filter}, duration={duration_filter}, sort={sort_by}"
        )
        
        try:
            # Build search URL
            search_url = self._build_search_url(
                query, date_filter, duration_filter, sort_by
            )
            
            # Use yt-dlp to search
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'playlistend': top_n,
            }
            
            results = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Execute search
                info = ydl.extract_info(search_url, download=False)
                
                if not info or 'entries' not in info:
                    logger.warning(f"No videos found for query: {query}")
                    return []
                
                # Process each video
                for entry in info['entries'][:top_n]:
                    if not entry:
                        continue
                    
                    # Standardize video data
                    video_data = self._standardize_video(entry)
                    video_data['search_query'] = query
                    video_data['search_rank'] = len(results) + 1
                    results.append(video_data)
            
            logger.info(f"Found {len(results)} videos for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching for query '{query}': {e}")
            raise
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate scraping parameters.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required parameters
        if 'query' not in params:
            logger.error("Missing required parameter: query")
            return False
        
        query = params['query']
        if not isinstance(query, str) or not query.strip():
            logger.error(f"query must be non-empty string, got: {query}")
            return False
        
        # Validate top_n
        top_n = params.get('top_n', 50)
        if not isinstance(top_n, int) or top_n < 1 or top_n > 500:
            logger.error(f"top_n must be integer between 1 and 500, got {top_n}")
            return False
        
        # Validate date_filter
        valid_date_filters = ['day', 'week', 'month', 'year', 'all']
        date_filter = params.get('date_filter', 'all')
        if date_filter not in valid_date_filters:
            logger.error(f"Invalid date_filter: {date_filter}. Must be one of {valid_date_filters}")
            return False
        
        # Validate duration_filter
        valid_duration_filters = ['short', 'medium', 'long', 'all']
        duration_filter = params.get('duration_filter', 'all')
        if duration_filter not in valid_duration_filters:
            logger.error(f"Invalid duration_filter: {duration_filter}. Must be one of {valid_duration_filters}")
            return False
        
        # Validate sort_by
        valid_sort_options = ['relevance', 'date', 'views', 'rating']
        sort_by = params.get('sort_by', 'relevance')
        if sort_by not in valid_sort_options:
            logger.error(f"Invalid sort_by: {sort_by}. Must be one of {valid_sort_options}")
            return False
        
        return True
    
    def _build_search_url(
        self,
        query: str,
        date_filter: str,
        duration_filter: str,
        sort_by: str
    ) -> str:
        """Build YouTube search URL with filters.
        
        Args:
            query: Search query
            date_filter: Date filter option
            duration_filter: Duration filter option
            sort_by: Sort order option
            
        Returns:
            Search URL with filters
        """
        import urllib.parse
        
        # Encode query
        encoded_query = urllib.parse.quote_plus(query)
        base_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        # Build filter string (sp parameter)
        filters = []
        
        # Date filter mapping
        date_map = {
            'hour': 'EgIIAQ%3D%3D',
            'day': 'EgIIAg%3D%3D',
            'week': 'EgIIAw%3D%3D',
            'month': 'EgIIBA%3D%3D',
            'year': 'EgIIBQ%3D%3D',
        }
        if date_filter in date_map:
            filters.append(date_map[date_filter])
        
        # Duration filter mapping
        duration_map = {
            'short': 'EgIYAQ%3D%3D',  # < 4 minutes
            'medium': 'EgIYAw%3D%3D',  # 4-20 minutes
            'long': 'EgIYAg%3D%3D',   # > 20 minutes
        }
        if duration_filter in duration_map:
            filters.append(duration_map[duration_filter])
        
        # Sort filter mapping
        sort_map = {
            'date': 'CAI%3D',
            'views': 'CAM%3D',
            'rating': 'CAE%3D',
        }
        if sort_by in sort_map:
            filters.append(sort_map[sort_by])
        
        # Add filters to URL if any
        if filters:
            # Combine filters (this is simplified; actual YouTube encoding is complex)
            base_url += f"&sp={filters[0]}"
        
        return base_url
    
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

### Step 1: Create Plugin Class (Day 1)
- Implement `YouTubeKeywordPlugin` class
- Implement all required methods
- Add search URL building logic

### Step 2: Add Filter Support (Day 2, Morning)
- Implement date filters
- Implement duration filters
- Implement sort options

### Step 3: Parameter Validation (Day 2, Afternoon)
- Comprehensive validation
- Error handling
- Logging

### Step 4: Testing & Documentation (Day 3)
- Unit tests
- Integration tests
- Documentation
- Usage examples

---

## Acceptance Criteria

### Functional Requirements
- [ ] `YouTubeKeywordPlugin` extends `PluginBase`
- [ ] Implements all required abstract methods
- [ ] Search by keywords works
- [ ] Date filters working
- [ ] Duration filters working
- [ ] Sort options working
- [ ] Returns standardized video data schema
- [ ] Parameter validation working
- [ ] Integrates with worker base class

### Code Quality
- [ ] Type hints on all methods
- [ ] Docstrings complete
- [ ] mypy passes
- [ ] pylint score >8.5/10
- [ ] Test coverage >80%

---

## Testing Strategy

```python
def test_plugin_metadata():
    """Test plugin metadata is correct."""
    plugin = YouTubeKeywordPlugin(None, None, None)
    metadata = plugin.get_metadata()
    
    assert metadata.task_type == "keyword_search"


def test_parameter_validation_success():
    """Test valid parameters pass validation."""
    plugin = YouTubeKeywordPlugin(None, None, None)
    
    params = {
        'query': 'python tutorial',
        'top_n': 50,
        'date_filter': 'month'
    }
    
    assert plugin.validate_parameters(params) is True


def test_parameter_validation_missing_query():
    """Test validation fails without query."""
    plugin = YouTubeKeywordPlugin(None, None, None)
    
    params = {'top_n': 50}
    
    assert plugin.validate_parameters(params) is False


def test_build_search_url():
    """Test search URL building with filters."""
    plugin = YouTubeKeywordPlugin(None, None, None)
    
    url = plugin._build_search_url('python', 'month', 'medium', 'views')
    assert 'youtube.com/results' in url
    assert 'search_query=python' in url
```

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/src/plugins/youtube_keyword_plugin.py` - NEW: Plugin implementation
2. `Sources/Content/Shorts/YouTube/_meta/tests/test_youtube_keyword_plugin.py` - NEW: Unit tests

---

## Files to Modify

1. `Sources/Content/Shorts/YouTube/src/plugins/__init__.py` - Add plugin registration

---

## Dependencies

### Internal
- #002 (BaseWorker) - Required
- #005 (PluginBase) - Required
- #009, #010 - Pattern reference

---

## Estimated Effort

**2-3 days**:
- Day 1: Plugin implementation
- Day 2: Filters and validation
- Day 3: Testing and documentation

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker02 - Python Specialist  
**Estimated Start**: Week 2, Day 5 (after #010 complete)  
**Estimated Completion**: Week 3, Day 2
