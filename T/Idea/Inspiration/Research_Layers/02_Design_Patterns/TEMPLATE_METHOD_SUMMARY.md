# Template Method Pattern - Executive Summary

**Pattern**: Template Method Pattern for Progressive Worker Enrichment  
**Status**: ✅ Core Implementation Complete  
**Reference**: https://refactoring.guru/design-patterns/template-method  
**Date**: 2025-11-16

---

## Quick Reference

### What is it?

A **hierarchical inheritance pattern** where workers progressively gain more specific functionality at each level:

```
Worker → Source → Video → YouTube → VideoEndpoint
```

Each level adds specific responsibilities without modifying parent classes.

### Why Template Method?

**Best fit** for our hierarchical worker structure because it provides:
- ✅ Natural hierarchy expression (IS-A relationships)
- ✅ Progressive enrichment at each level
- ✅ Maximum code reuse (DRY)
- ✅ Easy extension (Open/Closed)
- ✅ Clear mental model
- ✅ Simple implementation

### Alternative Patterns Considered

We analyzed **7 alternative patterns** and found Template Method superior:

| Pattern | Why Not Chosen |
|---------|----------------|
| Strategy | No natural hierarchy |
| Factory | Only handles creation |
| Builder | Wrong problem |
| Decorator | Too complex (5 layers!) |
| Composition | More boilerplate, loses hierarchy |
| Mixin | MRO complexity |
| Plugin | Overkill |

See [TEMPLATE_METHOD_ALTERNATIVES_ANALYSIS.md](./TEMPLATE_METHOD_ALTERNATIVES_ANALYSIS.md) for detailed analysis.

---

## Documentation Structure

### 📖 For Learning

1. **Start Here**: [TEMPLATE_METHOD_WORKER_HIERARCHY.md](./TEMPLATE_METHOD_WORKER_HIERARCHY.md)
   - Implementation guide
   - Progressive enrichment explanation
   - Code examples
   - Benefits and SOLID principles

2. **Pattern Selection**: [TEMPLATE_METHOD_ALTERNATIVES_ANALYSIS.md](./TEMPLATE_METHOD_ALTERNATIVES_ANALYSIS.md)
   - Why Template Method vs alternatives
   - Comprehensive comparison matrix
   - 7 patterns analyzed
   - When to use alternatives

3. **This Document**: Quick reference and overview

### 🔨 For Implementation

**Core Classes** (in order of hierarchy):

1. `Source/src/core/base_worker.py`
   - Level 1: Task processing, TaskManager integration

2. `Source/src/core/base_source_worker.py`
   - Level 2: Configuration, database operations

3. `Source/Video/src/core/base_video_source_worker.py`
   - Level 3: Video-specific operations

4. `Source/Video/YouTube/src/workers/base_youtube_worker.py` (TODO)
   - Level 4: YouTube API, quota management

5. `Source/Video/YouTube/Video/src/workers/youtube_video_worker.py` (TODO)
   - Level 5: Video endpoint scraping

---

## The 5-Level Hierarchy

### Visual Representation

```
┌─────────────────────────────────────────────────────────┐
│ Level 1: BaseWorker                                     │
│ • Task claiming (FIFO/LIFO/PRIORITY)                   │
│ • Worker lifecycle (run loop, start/stop)              │
│ • Result reporting to TaskManager                      │
│ • Exponential backoff                                   │
│ • Statistics tracking                                   │
└─────────────────────────────────────────────────────────┘
                         ↓ inherits
┌─────────────────────────────────────────────────────────┐
│ Level 2: BaseSourceWorker                              │
│ • Configuration management (Config object)             │
│ • Database operations (results_db)                     │
│ • Configuration validation                             │
│ • Result persistence hook                              │
└─────────────────────────────────────────────────────────┘
                         ↓ inherits
┌─────────────────────────────────────────────────────────┐
│ Level 3: BaseVideoSourceWorker                         │
│ • Video metadata validation                            │
│ • Duration parsing (ISO 8601: PT1H2M10S → seconds)    │
│ • IdeaInspiration creation for videos                  │
│ • Video feature extraction                             │
│ • Engagement rate calculation                          │
└─────────────────────────────────────────────────────────┘
                         ↓ inherits
┌─────────────────────────────────────────────────────────┐
│ Level 4: BaseYouTubeWorker (TODO)                      │
│ • YouTube API client initialization                    │
│ • YouTube authentication                               │
│ • YouTube-specific error handling                      │
│ • Quota management and tracking                        │
│ • YouTube data format conversion                       │
└─────────────────────────────────────────────────────────┘
                         ↓ inherits
┌─────────────────────────────────────────────────────────┐
│ Level 5: YouTubeVideoWorker (TODO)                     │
│ • Single video scraping by ID                          │
│ • Video search functionality                           │
│ • Video batch processing                               │
│ • Task routing (single/search/batch)                   │
└─────────────────────────────────────────────────────────┘
```

### What Each Level Adds

| Level | Class | Adds | Inherits From |
|-------|-------|------|---------------|
| **1** | BaseWorker | Task processing, TaskManager | - |
| **2** | BaseSourceWorker | Config, database | BaseWorker |
| **3** | BaseVideoSourceWorker | Video operations | BaseSourceWorker |
| **4** | BaseYouTubeWorker | YouTube API | BaseVideoSourceWorker |
| **5** | YouTubeVideoWorker | Video scraping | BaseYouTubeWorker |

---

## SOLID Principles Applied

### Single Responsibility Principle (SRP)

Each level has **one clear responsibility**:
- BaseWorker: Task lifecycle
- BaseSourceWorker: Configuration & storage
- BaseVideoSourceWorker: Video operations
- BaseYouTubeWorker: YouTube API
- YouTubeVideoWorker: Video scraping

### Open/Closed Principle (OCP)

**Open for extension** via inheritance, **closed for modification**:
- Add TikTok without touching YouTube
- Add Instagram without touching TikTok
- Add new endpoints without touching platform code

### Liskov Substitution Principle (LSP)

Any subclass can substitute its parent:
```python
def process_with_worker(worker: BaseWorker):
    worker.run()  # Works with ANY worker in hierarchy

process_with_worker(BaseWorker())
process_with_worker(BaseSourceWorker())
process_with_worker(YouTubeVideoWorker())  # All work!
```

### Interface Segregation Principle (ISP)

Each level has **focused interface**:
- BaseWorker: 6 core methods
- BaseSourceWorker: +2 methods (config, storage)
- BaseVideoSourceWorker: +4 methods (video operations)

No class forced to implement unused methods.

### Dependency Inversion Principle (DIP)

Depends on **abstractions**, not concretions:
- TaskManager client (abstraction)
- Config object (abstraction)
- Database object (abstraction)

All injected via constructor.

---

## Real-World Examples

Template Method is used in major frameworks:

### Django Class-Based Views

```python
class ListView(View):
    def get(self, request):  # Template method
        context = self.get_context_data()  # Hook
        return self.render_to_response(context)  # Hook

class PostListView(ListView):  # Override hooks
    def get_queryset(self):
        return Post.objects.all()
```

### pytest Fixtures

```python
class TestCase:
    def setup(self):  # Hook
        pass
    
    def teardown(self):  # Hook
        pass
    
    def run_test(self):  # Template method
        self.setup()
        try:
            self.test()  # Abstract
        finally:
            self.teardown()
```

### Our Pattern (Same Structure!)

```python
class BaseWorker:
    def run(self):  # Template method
        while True:
            task = self.claim_task()  # Hook
            result = self.process_task(task)  # Abstract
            self.report_result(task, result)  # Hook

class YouTubeVideoWorker(BaseWorker):  # Override abstract
    def process_task(self, task):
        return self._scrape_video(task)
```

---

## Code Reuse Benefits

### Without Hierarchy (Current Problem)

```python
# Source/Video/YouTube/Video/src/workers/base_worker.py
class BaseWorker:  # 376 lines
    def claim_task(self): ...  # Duplicated!
    def report_result(self): ...  # Duplicated!

# Source/Video/YouTube/Channel/src/workers/base_worker.py
class BaseWorker:  # 376 lines AGAIN!
    def claim_task(self): ...  # Duplicated!
    def report_result(self): ...  # Duplicated!

# Source/Text/Reddit/Posts/src/workers/base_worker.py
class BaseWorker:  # 376 lines AGAIN!
    def claim_task(self): ...  # Duplicated!
    def report_result(self): ...  # Duplicated!
```

**Problem**: 376 lines × 6 modules = **2,256 lines of duplicated code!**

### With Hierarchy (Our Solution)

```python
# Source/src/core/base_worker.py (500 lines, ONE TIME!)
class BaseWorker:
    def claim_task(self): ...  # Written once
    def report_result(self): ...  # Written once

# All workers inherit automatically
class YouTubeVideoWorker(BaseYouTubeWorker):
    # Just implement video-specific logic
    def process_task(self, task):
        return self._scrape_video(task)
```

**Result**: ~2,000 lines saved, one place to maintain!

---

## Parallel Hierarchies

Different media types can have parallel hierarchies:

```
BaseSourceWorker
    │
    ├─ BaseVideoSourceWorker
    │    ├─ BaseYouTubeWorker
    │    │    ├─ YouTubeVideoWorker
    │    │    ├─ YouTubeChannelWorker
    │    │    └─ YouTubeSearchWorker
    │    │
    │    ├─ BaseTikTokWorker
    │    │    └─ TikTokVideoWorker
    │    │
    │    └─ BaseInstagramWorker
    │         └─ InstagramReelsWorker
    │
    ├─ BaseTextSourceWorker
    │    ├─ BaseRedditWorker
    │    │    ├─ RedditPostsWorker
    │    │    └─ RedditCommentsWorker
    │    │
    │    └─ BaseHackerNewsWorker
    │         └─ HackerNewsStoriesWorker
    │
    └─ BaseAudioSourceWorker
         ├─ BaseSpotifyWorker
         │    └─ SpotifyPodcastWorker
         │
         └─ BaseApplePodcastsWorker
              └─ ApplePodcastsWorker
```

Each branch shares common functionality at appropriate levels!

---

## Testing Strategy

Test each level **independently**:

```python
# Test Level 1: BaseWorker
def test_base_worker_task_claiming():
    worker = MockWorker(worker_id="test", task_type_ids=["test"])
    task = worker.claim_task()
    assert task is not None
    assert task.id == "mock-task-id"

# Test Level 2: BaseSourceWorker
def test_source_worker_config():
    worker = MockSourceWorker(
        worker_id="test",
        task_type_ids=["test"],
        config=MockConfig(),
        results_db=MockDatabase()
    )
    assert worker.config is not None
    assert worker.results_db is not None

# Test Level 3: BaseVideoSourceWorker
def test_video_worker_duration_parsing():
    worker = MockVideoWorker(...)
    assert worker.parse_duration("PT1H2M10S") == 3730  # 1:02:10
    assert worker.parse_duration("PT15M") == 900       # 15:00
    assert worker.parse_duration("PT45S") == 45        # 0:45

# Test Level 4: BaseYouTubeWorker
def test_youtube_worker_api_initialization():
    worker = MockYouTubeWorker(...)
    assert worker.youtube_client is not None
    assert worker.quota_manager is not None

# Test Level 5: YouTubeVideoWorker
def test_youtube_video_worker_single_scrape():
    worker = YouTubeVideoWorker(...)
    result = worker.process_task(Task(
        id="task-1",
        task_type="youtube_video_single",
        parameters={"video_id": "abc123"}
    ))
    assert result.success
    assert result.items_processed == 1
```

---

## Migration Guide

### Step 1: Identify Current Base Workers

Find all duplicated `base_worker.py` files:
```bash
find ./Source -name "base_worker.py" -path "*/workers/*"
```

### Step 2: Update Imports

Change from local to shared:
```python
# Before
from ..workers.base_worker import BaseWorker

# After
from Source.src.core.base_worker import BaseWorker
```

### Step 3: Update Inheritance

```python
# Before
class YouTubeVideoWorker:
    def __init__(self, worker_id, config, results_db, ...):
        self.worker_id = worker_id
        self.config = config
        # ... lots of initialization

# After
class YouTubeVideoWorker(BaseYouTubeWorker):
    def __init__(self, worker_id, config, results_db):
        super().__init__(worker_id, ["youtube_video"], config, results_db)
        # Parent handles most initialization!
```

### Step 4: Remove Duplicated Code

Delete methods that now come from parent:
- `claim_task()` - from BaseWorker
- `report_result()` - from BaseWorker
- `run()` - from BaseWorker
- `_validate_config()` - from BaseSourceWorker
- `validate_video_metadata()` - from BaseVideoSourceWorker

### Step 5: Keep Only Specific Logic

Keep only endpoint-specific methods:
```python
class YouTubeVideoWorker(BaseYouTubeWorker):
    def process_task(self, task: Task) -> TaskResult:
        # Only implement specific scraping logic
        if task.task_type == "youtube_video_single":
            return self._process_single_video(task)
        elif task.task_type == "youtube_video_search":
            return self._process_search(task)
```

---

## Key Takeaways

1. **Template Method** = Skeleton algorithm in base class, details in subclasses
2. **Progressive Enrichment** = Each level adds specific functionality
3. **Natural Hierarchy** = Express IS-A relationships clearly
4. **Code Reuse** = Write once, inherit everywhere
5. **Easy Extension** = Add new platforms without touching existing code
6. **SOLID Compliant** = All 5 principles followed
7. **Proven Pattern** = Used in Django, Java, React, pytest

---

## Next Steps

### Immediate (In Progress)

1. ✅ Create BaseWorker (DONE)
2. ✅ Create BaseSourceWorker (DONE)
3. ✅ Create BaseVideoSourceWorker (DONE)
4. 🔄 Create BaseYouTubeWorker
5. 🔄 Refactor YouTubeVideoWorker
6. 🔄 Add tests

### Short-term

1. Create BaseTextSourceWorker
2. Refactor Reddit workers
3. Refactor HackerNews workers
4. Create BaseAudioSourceWorker

### Long-term

1. Create BaseTikTokWorker
2. Create BaseInstagramWorker
3. Create BaseSpotifyWorker
4. Migrate all workers to hierarchy

---

## Resources

### Documentation

- [TEMPLATE_METHOD_WORKER_HIERARCHY.md](./TEMPLATE_METHOD_WORKER_HIERARCHY.md) - Full implementation guide
- [TEMPLATE_METHOD_ALTERNATIVES_ANALYSIS.md](./TEMPLATE_METHOD_ALTERNATIVES_ANALYSIS.md) - Pattern comparison
- [07_DESIGN_PATTERNS_FOR_WORKERS.md](./07_DESIGN_PATTERNS_FOR_WORKERS.md) - Worker patterns overview

### External References

- [Refactoring.Guru - Template Method](https://refactoring.guru/design-patterns/template-method)
- [Python Design Patterns](https://python-patterns.guide/)
- [Django Class-Based Views](https://docs.djangoproject.com/en/stable/topics/class-based-views/)

### Code Examples

- `Source/src/core/base_worker.py` - Level 1 implementation
- `Source/src/core/base_source_worker.py` - Level 2 implementation
- `Source/Video/src/core/base_video_source_worker.py` - Level 3 implementation

---

**Last Updated**: 2025-11-16  
**Maintained By**: PrismQ.T.Idea.Inspiration Team  
**Status**: ✅ Core implementation complete, refinement in progress
