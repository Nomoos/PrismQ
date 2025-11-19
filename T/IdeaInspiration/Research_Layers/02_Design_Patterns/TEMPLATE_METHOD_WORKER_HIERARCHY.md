# Template Method Pattern - Worker Hierarchy Implementation

**Design Pattern**: Template Method Pattern (with Progressive Enrichment)  
**Primary Reference**: https://refactoring.guru/design-patterns/template-method  
**Research Status**: ✅ Implemented  
**Date**: 2025-11-16

---

## Pattern Classification

**Category**: Behavioral Design Pattern  
**Intent**: Define the skeleton of an algorithm in a base class, letting subclasses override specific steps without changing the algorithm's structure.  
**Also Known As**: Progressive Enrichment via Inheritance, Layered Template Method

---

## Overview

This document describes the progressive enrichment pattern used for workers in PrismQ.IdeaInspiration.
Workers are organized in a hierarchical inheritance structure where each level adds specific functionality
without modifying parent classes, following the **Open/Closed Principle** and **Template Method Pattern**.

## Pattern Name

**Progressive Enrichment via Inheritance** (also known as **Layered Inheritance** or **Hierarchical Template Method**)

## Problem

Workers across different sources (YouTube, Reddit, HackerNews) share common functionality but also need:
- Source-specific operations (API clients, authentication)
- Media-specific operations (video processing, text analysis)
- Platform-specific operations (YouTube API, Reddit API)
- Endpoint-specific operations (video scraping, channel scraping)

Without a proper hierarchy, this leads to:
- ❌ Code duplication across workers
- ❌ Difficult maintenance (changes must be made in multiple places)
- ❌ Hard to add new sources or platforms
- ❌ Violates DRY principle

## Solution

Create a hierarchical inheritance structure where each level adds specific functionality:

```
BaseWorker (Source level)
  ├─ Common task processing logic
  ├─ TaskManager integration
  ├─ Result reporting
  └─ Worker lifecycle management
      ↓
BaseSourceWorker (Source level)
  ├─ Configuration management
  ├─ Database operations
  └─ API client management
      ↓
BaseVideoSourceWorker (Video level)
  ├─ Video-specific validation
  ├─ Video metadata processing
  ├─ Duration handling
  └─ Thumbnail processing
      ↓
BaseYouTubeWorker (YouTube level)
  ├─ YouTube API client
  ├─ YouTube authentication
  ├─ YouTube-specific error handling
  ├─ Quota management
  └─ YouTube data format conversion
      ↓
YouTubeVideoWorker (Video endpoint)
  ├─ Single video scraping
  ├─ Video search
  └─ Video batch processing
```

## Implementation

### Level 1: BaseWorker (General Task Processing)

**Location**: `Source/src/core/base_worker.py`

**Responsibilities**:
- Task claiming from TaskManager API
- Worker lifecycle (run loop, start/stop)
- Result reporting to TaskManager
- Exponential backoff for empty queues
- Statistics tracking

**Key Methods**:
- `claim_task()` - Template method for task claiming
- `process_task()` - Abstract method (must be implemented)
- `report_result()` - Template method for result reporting
- `run()` - Main worker loop
- `run_once()` - Single iteration

**Example**:
```python
from Source.src.core.base_worker import BaseWorker, Task, TaskResult

class MyWorker(BaseWorker):
    def process_task(self, task: Task) -> TaskResult:
        # Implement specific processing logic
        return TaskResult(success=True, items_processed=1)
```

### Level 2: BaseSourceWorker (Source Configuration & Storage)

**Location**: `Source/src/core/base_source_worker.py`

**Adds**:
- Configuration management (Config object)
- Database operations (results_db)
- Configuration validation
- Result persistence

**Inherits from**: `BaseWorker`

**Example**:
```python
from Source.src.core.base_source_worker import BaseSourceWorker

class MySourceWorker(BaseSourceWorker):
    def __init__(self, worker_id, task_type_ids, config, results_db):
        super().__init__(
            worker_id=worker_id,
            task_type_ids=task_type_ids,
            config=config,
            results_db=results_db
        )
```

### Level 3: BaseVideoSourceWorker (Video-Specific Operations)

**Location**: `Source/Video/src/core/base_video_source_worker.py`

**Adds**:
- Video metadata validation
- Video duration parsing
- Thumbnail URL handling
- IdeaInspiration creation for videos
- Video-specific error handling

**Inherits from**: `BaseSourceWorker`

**Example**:
```python
from Source.Video.src.core.base_video_source_worker import BaseVideoSourceWorker

class MyVideoWorker(BaseVideoSourceWorker):
    def process_task(self, task: Task) -> TaskResult:
        # Use video-specific methods
        if self.validate_video_metadata(raw_data):
            idea = self.create_video_inspiration(raw_data)
            return TaskResult(success=True)
```

### Level 4: BaseYouTubeWorker (YouTube Platform Operations)

**Location**: `Source/Video/YouTube/src/workers/base_youtube_worker.py`

**Adds**:
- YouTube API client initialization
- YouTube API authentication
- YouTube-specific error handling (quota exceeded, video not found)
- YouTube rate limiting
- YouTube data format conversion
- Quota management

**Inherits from**: `BaseVideoSourceWorker`

**Example**:
```python
from Source.Video.YouTube.src.workers.base_youtube_worker import BaseYouTubeWorker

class MyYouTubeWorker(BaseYouTubeWorker):
    def process_task(self, task: Task) -> TaskResult:
        # Use YouTube-specific methods
        try:
            video_data = self.youtube_client.get_video(video_id)
            return TaskResult(success=True)
        except QuotaExceededException as e:
            return self.handle_quota_error(e)
```

### Level 5: YouTubeVideoWorker (Video Endpoint)

**Location**: `Source/Video/YouTube/Video/src/workers/youtube_video_worker.py`

**Adds**:
- Single video scraping
- Video search functionality
- Video batch processing
- Video-specific task routing

**Inherits from**: `BaseYouTubeWorker`

**Example**:
```python
from Source.Video.YouTube.src.workers.base_youtube_worker import BaseYouTubeWorker

class YouTubeVideoWorker(BaseYouTubeWorker):
    def process_task(self, task: Task) -> TaskResult:
        if task.task_type == "youtube_video_single":
            return self._process_single_video(task)
        elif task.task_type == "youtube_video_search":
            return self._process_search(task)
```

## Benefits

### 1. Code Reuse (DRY Principle)
- TaskManager integration written once in BaseWorker
- YouTube API handling written once in BaseYouTubeWorker
- Video processing written once in BaseVideoSourceWorker
- No duplication across similar workers

### 2. Single Responsibility Principle (SRP)
- Each level has one clear responsibility
- BaseWorker: Task processing
- BaseSourceWorker: Configuration and storage
- BaseVideoSourceWorker: Video operations
- BaseYouTubeWorker: YouTube API operations
- YouTubeVideoWorker: Video endpoint operations

### 3. Open/Closed Principle (OCP)
- Add new platforms without modifying BaseVideoSourceWorker
- Add new endpoints without modifying BaseYouTubeWorker
- Extension through subclassing, not modification

### 4. Liskov Substitution Principle (LSP)
- Any YouTubeWorker can replace BaseYouTubeWorker
- Any VideoWorker can replace BaseVideoSourceWorker
- Any SourceWorker can replace BaseSourceWorker
- Polymorphism works correctly

### 5. Easy to Test
- Mock dependencies at each level
- Test each level independently
- Focused unit tests

### 6. Easy to Extend
- Add TikTokWorker by inheriting from BaseVideoSourceWorker
- Add RedditWorker by inheriting from BaseSourceWorker
- Add AudioWorker by inheriting from BaseSourceWorker

## Progressive Enrichment

Each level progressively enriches the functionality:

| Level | Adds | Inherits |
|-------|------|----------|
| **BaseWorker** | Task processing, TaskManager integration | - |
| **BaseSourceWorker** | Configuration, database | BaseWorker |
| **BaseVideoSourceWorker** | Video operations | BaseSourceWorker |
| **BaseYouTubeWorker** | YouTube API, quota | BaseVideoSourceWorker |
| **YouTubeVideoWorker** | Video scraping | BaseYouTubeWorker |

## Parallel Hierarchies

Different media types can have parallel hierarchies:

```
BaseSourceWorker
    ├─ BaseVideoSourceWorker
    │    ├─ BaseYouTubeWorker
    │    │    ├─ YouTubeVideoWorker
    │    │    ├─ YouTubeChannelWorker
    │    │    └─ YouTubeSearchWorker
    │    ├─ BaseTikTokWorker
    │    │    └─ TikTokVideoWorker
    │    └─ BaseInstagramWorker
    │         └─ InstagramReelsWorker
    │
    ├─ BaseTextSourceWorker
    │    ├─ BaseRedditWorker
    │    │    ├─ RedditPostsWorker
    │    │    └─ RedditCommentsWorker
    │    └─ BaseHackerNewsWorker
    │         └─ HackerNewsStoriesWorker
    │
    └─ BaseAudioSourceWorker
         ├─ BaseSpotifyWorker
         │    └─ SpotifyPodcastWorker
         └─ BaseApplePodcastsWorker
              └─ ApplePodcastsWorker
```

## Migration Strategy

To migrate existing workers to this hierarchy:

1. ✅ Create `Source/src/core/base_worker.py` with common task processing
2. ✅ Create `Source/src/core/base_source_worker.py` with config and database
3. 🔄 Create `Source/Video/src/core/base_video_source_worker.py` with video operations
4. 🔄 Create `Source/Video/YouTube/src/workers/base_youtube_worker.py` with YouTube API
5. 🔄 Update `YouTubeVideoWorker` to inherit from `BaseYouTubeWorker`
6. 🔄 Update other YouTube workers (Channel, Search) to inherit from `BaseYouTubeWorker`
7. 🔄 Create similar hierarchies for Reddit, HackerNews, etc.
8. 🔄 Remove duplicated `base_worker.py` files

## Testing Strategy

Test each level independently:

```python
# Test Level 1: BaseWorker
def test_base_worker_task_claiming():
    worker = MockWorker(worker_id="test", task_type_ids=["test"])
    task = worker.claim_task()
    assert task is not None

# Test Level 2: BaseSourceWorker
def test_source_worker_config():
    worker = MockSourceWorker(
        worker_id="test",
        task_type_ids=["test"],
        config=Config(),
        results_db=Database()
    )
    assert worker.config is not None

# Test Level 3: BaseVideoSourceWorker
def test_video_worker_validation():
    worker = MockVideoWorker(...)
    assert worker.validate_video_metadata({"title": "test", "duration": "PT1M"})

# Test Level 4: BaseYouTubeWorker
def test_youtube_worker_api():
    worker = MockYouTubeWorker(...)
    assert worker.youtube_client is not None

# Test Level 5: YouTubeVideoWorker
def test_youtube_video_worker_scraping():
    worker = YouTubeVideoWorker(...)
    result = worker.process_task(task)
    assert result.success
```

## Design Patterns Used

### 1. Template Method Pattern
- BaseWorker defines the algorithm structure
- Subclasses override specific steps
- `run()`, `claim_task()`, `report_result()` are template methods

### 2. Strategy Pattern
- Task claiming strategies (FIFO, LIFO, PRIORITY)
- Injected via constructor parameter

### 3. Factory Pattern
- WorkerFactory creates appropriate worker instances
- Decouples worker creation from usage

### 4. Dependency Injection
- Config and Database injected via constructor
- Follows Dependency Inversion Principle

## Related Documentation

- [SOLID Principles](../../Research_Layers/02_Design_Patterns/SOLID_PRINCIPLES.md)
- [Design Patterns for Workers](../../Research_Layers/02_Design_Patterns/07_DESIGN_PATTERNS_FOR_WORKERS.md)
- [Template Method Pattern](https://refactoring.guru/design-patterns/template-method)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)

## References

- **Refactoring.Guru**: https://refactoring.guru/design-patterns/template-method
- **Clean Architecture** by Robert C. Martin
- **Design Patterns** by Gang of Four
- **SOLID Principles** documentation

---

**Last Updated**: 2025-11-16  
**Maintained By**: PrismQ.IdeaInspiration Team
