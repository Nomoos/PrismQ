# Template Method Pattern - Alternatives Analysis

**Pattern Being Evaluated**: Template Method Pattern for Worker Hierarchy  
**Question**: Are there better alternatives? Why are other patterns less suitable?  
**Primary Reference**: https://refactoring.guru/design-patterns  
**Date**: 2025-11-16

---

## Executive Summary

**Selected Pattern**: Template Method Pattern with Progressive Enrichment  
**Reason**: Best fit for hierarchical worker structure with shared behavior and progressive specialization

**Alternatives Considered**:
1. ✅ **Template Method** - BEST FIT
2. ❌ Strategy Pattern - Less suitable (no hierarchy)
3. ❌ Factory Pattern - Less suitable (creation only, no behavior)
4. ❌ Builder Pattern - Less suitable (object construction focus)
5. ❌ Decorator Pattern - Less suitable (runtime composition complexity)
6. ⚠️ Strategy + Composition - Viable but more complex
7. ⚠️ Mixin Pattern - Viable but less explicit

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements Analysis](#requirements-analysis)
3. [Pattern Comparison Matrix](#pattern-comparison-matrix)
4. [Alternative 1: Strategy Pattern](#alternative-1-strategy-pattern)
5. [Alternative 2: Factory Pattern](#alternative-2-factory-pattern)
6. [Alternative 3: Builder Pattern](#alternative-3-builder-pattern)
7. [Alternative 4: Decorator Pattern](#alternative-4-decorator-pattern)
8. [Alternative 5: Strategy + Composition](#alternative-5-strategy--composition)
9. [Alternative 6: Mixin Pattern](#alternative-6-mixin-pattern)
10. [Alternative 7: Plugin Architecture](#alternative-7-plugin-architecture)
11. [Why Template Method is Best](#why-template-method-is-best)
12. [Conclusion and Recommendation](#conclusion-and-recommendation)

---

## Problem Statement

We need a design pattern for workers that:
- Shares common behavior (task claiming, result reporting)
- Progressively adds specific functionality (config → video ops → YouTube API → video scraping)
- Maintains clear hierarchy (Worker → Source → Video → YouTube → VideoEndpoint)
- Follows SOLID principles (especially OCP and DIP)
- Easy to extend with new platforms/sources
- Easy to test at each level

**Current Challenge**: Each source has duplicated base worker code with slight variations.

---

## Requirements Analysis

### Functional Requirements

1. **Progressive Enrichment**: Each level adds functionality
   - Level 1: Task processing
   - Level 2: Configuration
   - Level 3: Video operations
   - Level 4: YouTube API
   - Level 5: Video endpoint

2. **Code Reuse**: Share common logic across all workers
   - Task claiming
   - Result reporting
   - Error handling
   - Statistics tracking

3. **Extensibility**: Easy to add new platforms
   - Add TikTok without touching YouTube
   - Add Instagram without touching TikTok
   - Add new endpoints without touching platform code

4. **Testability**: Test each level independently
   - Mock parent behavior
   - Test specific level logic
   - Integration tests for full hierarchy

### Non-Functional Requirements

1. **Maintainability**: Clear structure, easy to understand
2. **Performance**: Minimal overhead
3. **Type Safety**: Strong typing with Python type hints
4. **Simplicity**: KISS principle - keep it simple

---

## Pattern Comparison Matrix

| Pattern | Code Reuse | Extensibility | Hierarchy | Testability | Complexity | SOLID | Best For |
|---------|------------|---------------|-----------|-------------|------------|-------|----------|
| **Template Method** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **Hierarchical behavior** |
| Strategy | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Algorithm variation |
| Factory | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Object creation |
| Builder | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Complex object construction |
| Decorator | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | Runtime behavior addition |
| Strategy + Composition | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Flat behavior composition |
| Mixin | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Python-specific sharing |

**Legend**: ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐⭐ Adequate | ⭐⭐ Poor | ⭐ Very Poor

---

## Alternative 1: Strategy Pattern

**Reference**: https://refactoring.guru/design-patterns/strategy

### Description

Define a family of algorithms, encapsulate each one, and make them interchangeable.

### Implementation Example

```python
from abc import ABC, abstractmethod
from typing import Protocol

# Strategy interfaces
class TaskProcessor(Protocol):
    def process(self, task: Task) -> TaskResult: ...

class ConfigManager(Protocol):
    def get_config(self) -> Config: ...

class VideoProcessor(Protocol):
    def process_video(self, video_data: dict) -> IdeaInspiration: ...

class YouTubeAPIClient(Protocol):
    def fetch_video(self, video_id: str) -> dict: ...

# Worker uses composition with strategies
class YouTubeVideoWorker:
    def __init__(
        self,
        task_processor: TaskProcessor,
        config_manager: ConfigManager,
        video_processor: VideoProcessor,
        youtube_client: YouTubeAPIClient
    ):
        self.task_processor = task_processor
        self.config_manager = config_manager
        self.video_processor = video_processor
        self.youtube_client = youtube_client
    
    def run(self):
        while True:
            task = self.task_processor.claim_task()
            if task:
                video_id = task.parameters['video_id']
                video_data = self.youtube_client.fetch_video(video_id)
                idea = self.video_processor.process_video(video_data)
                self.task_processor.report_result(task, idea)
```

### Advantages

✅ **Maximum flexibility** - can swap strategies at runtime  
✅ **Excellent testability** - mock each strategy independently  
✅ **Strong SOLID adherence** - especially DIP  
✅ **No inheritance** - avoids inheritance pitfalls  
✅ **Clear dependencies** - explicit in constructor  

### Disadvantages

❌ **No natural hierarchy** - doesn't express Source → Video → YouTube progression  
❌ **More boilerplate** - many small classes and interfaces  
❌ **Complex initialization** - many dependencies to inject  
❌ **Harder to share state** - strategies are independent  
❌ **No progressive enrichment** - each worker starts from scratch  

### Why Less Suitable for Our Use Case

1. **Missing Hierarchy**: Doesn't express the natural hierarchy of:
   - Worker (general) → Video (media) → YouTube (platform) → Video (endpoint)

2. **No Code Reuse Across Levels**: Each worker must compose all strategies:
   ```python
   # YouTubeVideoWorker - must compose everything
   worker1 = YouTubeVideoWorker(task_proc, config, video_proc, yt_client)
   
   # TikTokVideoWorker - must compose everything again
   worker2 = TikTokVideoWorker(task_proc, config, video_proc, tt_client)
   
   # No shared VideoWorker level!
   ```

3. **State Sharing Complexity**: Strategies need to share state (statistics, config), requiring:
   - Shared state object passed to all strategies
   - More complex coordination

4. **Doesn't Match Mental Model**: Developers think:
   - "YouTube Video Worker IS-A YouTube Worker IS-A Video Worker"
   - Not: "YouTube Video Worker HAS-A task processor AND video processor AND YouTube client"

### When Strategy Would Be Better

- Swapping algorithms at runtime (e.g., different scoring algorithms)
- No natural hierarchy (flat structure)
- Need maximum flexibility
- Testing each component in complete isolation

---

## Alternative 2: Factory Pattern

**Reference**: https://refactoring.guru/design-patterns/factory-method

### Description

Provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created.

### Implementation Example

```python
from abc import ABC, abstractmethod

class WorkerFactory(ABC):
    """Factory for creating workers."""
    
    @abstractmethod
    def create_worker(self, worker_id: str) -> BaseWorker:
        """Create a worker instance."""
        pass
    
    def create_and_run(self, worker_id: str):
        """Template method using factory."""
        worker = self.create_worker(worker_id)
        worker.run()

class YouTubeVideoWorkerFactory(WorkerFactory):
    def create_worker(self, worker_id: str) -> BaseWorker:
        return YouTubeVideoWorker(
            worker_id=worker_id,
            config=self.config,
            api_client=YouTubeAPIClient()
        )

# Usage
factory = YouTubeVideoWorkerFactory(config=Config())
factory.create_and_run("worker-01")
```

### Advantages

✅ **Decouples creation** - client doesn't know concrete classes  
✅ **Easy to add types** - register new worker types  
✅ **Centralized creation** - single place for instantiation logic  

### Disadvantages

❌ **Only handles creation** - doesn't define behavior  
❌ **No code reuse** - each worker still needs full implementation  
❌ **No hierarchy** - doesn't help with progressive enrichment  
❌ **Complements, doesn't replace** - often used WITH Template Method  

### Why Less Suitable for Our Use Case

1. **Wrong Problem**: Factory solves object creation, not behavior sharing
   
2. **Doesn't Eliminate Duplication**: Still need to implement full worker behavior:
   ```python
   # Still need to implement all these methods in each worker
   class YouTubeVideoWorker:
       def claim_task(self): ...  # Duplicated
       def process_task(self): ...
       def report_result(self): ...  # Duplicated
   ```

3. **Not Mutually Exclusive**: Factory often works WITH Template Method:
   ```python
   # Template Method defines behavior hierarchy
   class BaseWorker:
       def run(self): ...  # Template method
   
   # Factory creates instances
   class WorkerFactory:
       def create(self, type: str) -> BaseWorker:
           if type == "youtube": return YouTubeWorker()
           if type == "tiktok": return TikTokWorker()
   ```

### When Factory Would Be Better

- **Creation is complex** - many configuration options
- **Need multiple creation methods** - different ways to create workers
- **Dynamic type selection** - create worker based on config/input
- **Used TOGETHER with Template Method** - factory creates hierarchy instances

### Our Use: Factory COMPLEMENTS Template Method

```python
# We CAN use both!
class WorkerFactory:
    """Factory creates workers from hierarchy."""
    
    def create(self, worker_type: str) -> BaseWorker:
        if worker_type == "youtube_video":
            return YouTubeVideoWorker(...)  # Instance of Template Method hierarchy
        elif worker_type == "tiktok_video":
            return TikTokVideoWorker(...)   # Instance of Template Method hierarchy
```

---

## Alternative 3: Builder Pattern

**Reference**: https://refactoring.guru/design-patterns/builder

### Description

Lets you construct complex objects step by step. The pattern allows you to produce different types and representations of an object using the same construction code.

### Implementation Example

```python
class WorkerBuilder:
    """Builder for constructing workers."""
    
    def __init__(self):
        self._worker_id = None
        self._config = None
        self._task_types = []
        self._api_client = None
    
    def with_id(self, worker_id: str):
        self._worker_id = worker_id
        return self
    
    def with_config(self, config: Config):
        self._config = config
        return self
    
    def with_task_types(self, task_types: list):
        self._task_types = task_types
        return self
    
    def with_api_client(self, client):
        self._api_client = client
        return self
    
    def build(self) -> BaseWorker:
        return YouTubeVideoWorker(
            worker_id=self._worker_id,
            config=self._config,
            task_type_ids=self._task_types,
            api_client=self._api_client
        )

# Usage
worker = (WorkerBuilder()
    .with_id("worker-01")
    .with_config(config)
    .with_task_types(["youtube_video"])
    .with_api_client(YouTubeAPI())
    .build())
```

### Advantages

✅ **Step-by-step construction** - build complex objects incrementally  
✅ **Readable creation** - fluent interface  
✅ **Validation** - can validate before building  

### Disadvantages

❌ **Only construction** - doesn't address behavior sharing  
❌ **More code** - builder classes add complexity  
❌ **Wrong problem** - solves construction, not hierarchy  

### Why Less Suitable for Our Use Case

**Same as Factory** - addresses object creation, not behavior hierarchy.

---

## Alternative 4: Decorator Pattern

**Reference**: https://refactoring.guru/design-patterns/decorator

### Description

Lets you attach new behaviors to objects by placing these objects inside special wrapper objects that contain the behaviors.

### Implementation Example

```python
class Worker(ABC):
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult: ...

class BaseWorkerDecorator(Worker):
    def __init__(self, worker: Worker):
        self._worker = worker

class TaskManagerDecorator(BaseWorkerDecorator):
    """Adds TaskManager integration."""
    
    def process_task(self, task: Task) -> TaskResult:
        result = self._worker.process_task(task)
        self._report_to_taskmanager(result)
        return result

class VideoProcessingDecorator(BaseWorkerDecorator):
    """Adds video processing."""
    
    def process_task(self, task: Task) -> TaskResult:
        # Add video-specific processing
        result = self._worker.process_task(task)
        # Add video metadata
        return result

# Usage - wrap multiple times
worker = ConcreteWorker()
worker = TaskManagerDecorator(worker)
worker = VideoProcessingDecorator(worker)
worker = YouTubeAPIDecorator(worker)
```

### Advantages

✅ **Runtime composition** - add behavior dynamically  
✅ **Open/Closed** - add features without modifying code  
✅ **Single Responsibility** - each decorator has one purpose  
✅ **Flexible combinations** - mix and match decorators  

### Disadvantages

❌ **Complex initialization** - many wrapping layers  
❌ **Order matters** - wrong order = wrong behavior  
❌ **Harder to debug** - many layers to trace  
❌ **No compile-time checks** - can wrap incorrectly  
❌ **Performance overhead** - each layer adds call  

### Why Less Suitable for Our Use Case

1. **Complexity**: 5 levels of wrapping for YouTubeVideoWorker:
   ```python
   worker = ConcreteWorker()
   worker = BaseWorkerDecorator(worker)      # Level 1
   worker = SourceWorkerDecorator(worker)    # Level 2
   worker = VideoWorkerDecorator(worker)     # Level 3
   worker = YouTubeWorkerDecorator(worker)   # Level 4
   worker = VideoEndpointDecorator(worker)   # Level 5
   # Too many layers!
   ```

2. **Static Hierarchy**: Our hierarchy is static (every YouTube video worker needs YouTube API), not dynamic

3. **Order-Dependent**: Must wrap in correct order, easy to make mistakes

4. **Not Natural**: Workers don't need runtime behavior addition

### When Decorator Would Be Better

- **Optional features** - some workers need extra features, some don't
- **Runtime configuration** - enable/disable features at runtime
- **Cross-cutting concerns** - logging, caching, retry logic
- **Many combinations** - different feature combinations

---

## Alternative 5: Strategy + Composition

**Reference**: Combination pattern (Favor Composition Over Inheritance)

### Description

Combine Strategy Pattern with Composition - workers compose shared components rather than inherit.

### Implementation Example

```python
# Shared components
class TaskManager:
    def claim_task(self, worker_id: str, task_types: list) -> Task: ...
    def report_result(self, task: Task, result: TaskResult): ...

class VideoProcessor:
    def validate_video(self, data: dict) -> bool: ...
    def create_inspiration(self, data: dict) -> IdeaInspiration: ...

class YouTubeAPIClient:
    def fetch_video(self, video_id: str) -> dict: ...
    def search_videos(self, query: str) -> list: ...

# Worker composes components
class YouTubeVideoWorker:
    def __init__(self, worker_id: str, config: Config):
        # Compose shared components
        self.task_manager = TaskManager(config)
        self.video_processor = VideoProcessor()
        self.youtube_client = YouTubeAPIClient(config.api_key)
        self.worker_id = worker_id
    
    def run(self):
        while True:
            task = self.task_manager.claim_task(self.worker_id, ["youtube_video"])
            if task:
                result = self.process_task(task)
                self.task_manager.report_result(task, result)
    
    def process_task(self, task: Task) -> TaskResult:
        video_id = task.parameters['video_id']
        video_data = self.youtube_client.fetch_video(video_id)
        
        if self.video_processor.validate_video(video_data):
            idea = self.video_processor.create_inspiration(video_data)
            return TaskResult(success=True, data=idea)
```

### Advantages

✅ **Favor composition over inheritance** - best practice  
✅ **Flexible** - can mix components as needed  
✅ **Easy testing** - mock each component  
✅ **No inheritance coupling** - independent components  
✅ **Clear dependencies** - explicit in constructor  

### Disadvantages

⚠️ **More boilerplate** - each worker creates components  
⚠️ **Repeated initialization** - similar code in each worker  
⚠️ **No hierarchy expression** - loses conceptual model  
⚠️ **State management** - components need access to worker state  

### Why Viable But More Complex

This is actually a **VIABLE ALTERNATIVE** that follows best practices, but:

1. **More Code Duplication**:
   ```python
   # Every worker must initialize same components
   class YouTubeVideoWorker:
       def __init__(self, ...):
           self.task_manager = TaskManager(config)  # Repeated
           self.video_processor = VideoProcessor()   # Repeated
           self.youtube_client = YouTubeAPIClient(...)
   
   class YouTubeChannelWorker:
       def __init__(self, ...):
           self.task_manager = TaskManager(config)  # Repeated again!
           self.video_processor = VideoProcessor()   # Repeated again!
           self.youtube_client = YouTubeAPIClient(...)
   ```

2. **Component Factory Needed**:
   ```python
   # Need factory to reduce duplication
   class YouTubeWorkerComponents:
       @staticmethod
       def create(config: Config):
           return (
               TaskManager(config),
               VideoProcessor(),
               YouTubeAPIClient(config.api_key)
           )
   ```

3. **Loses Hierarchy**: Can't express "YouTubeVideoWorker IS-A YouTubeWorker IS-A VideoWorker"

### When This Would Be Better

- **Flat structure** - no natural hierarchy
- **High variation** - many different component combinations
- **Runtime flexibility** - need to swap components
- **Avoiding inheritance** - explicit policy against inheritance

### Hybrid Approach: Template Method + Composition

**BEST OF BOTH WORLDS**:

```python
# Template Method for hierarchy
class BaseWorker(ABC):
    def __init__(self, worker_id: str, task_type_ids: list):
        # Compose TaskManager (not inherit)
        self.task_manager = TaskManager()
        self.worker_id = worker_id
        self.task_type_ids = task_type_ids
    
    def run(self):  # Template method
        while True:
            task = self.task_manager.claim_task(...)
            result = self.process_task(task)  # Abstract
            self.task_manager.report_result(task, result)
    
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        pass

# Inherit for hierarchy, compose for flexibility
class YouTubeVideoWorker(BaseYouTubeWorker):
    def __init__(self, worker_id: str, config: Config):
        super().__init__(worker_id, ["youtube_video"], config)
        # Compose YouTube client (not inherit)
        self.youtube_client = YouTubeAPIClient(config.api_key)
```

---

## Alternative 6: Mixin Pattern

**Reference**: Python-specific pattern (Multiple Inheritance)

### Description

Use Python's multiple inheritance to mix in behaviors from multiple classes.

### Implementation Example

```python
# Mixins provide specific behaviors
class TaskManagerMixin:
    def claim_task(self, task_types: list) -> Task: ...
    def report_result(self, task: Task, result: TaskResult): ...

class VideoProcessingMixin:
    def validate_video(self, data: dict) -> bool: ...
    def parse_duration(self, duration: str) -> int: ...

class YouTubeAPIMixin:
    def init_youtube_client(self, api_key: str): ...
    def fetch_youtube_video(self, video_id: str) -> dict: ...

# Worker mixes in behaviors
class YouTubeVideoWorker(TaskManagerMixin, VideoProcessingMixin, YouTubeAPIMixin):
    def __init__(self, worker_id: str, config: Config):
        self.worker_id = worker_id
        self.init_youtube_client(config.youtube_api_key)
    
    def process_task(self, task: Task) -> TaskResult:
        video_id = task.parameters['video_id']
        video_data = self.fetch_youtube_video(video_id)
        
        if self.validate_video(video_data):
            # Process video
            pass
```

### Advantages

✅ **Python-idiomatic** - uses language features  
✅ **Code reuse** - share methods across unrelated classes  
✅ **Flexible** - mix and match behaviors  
✅ **No deep hierarchy** - flat mixin structure  

### Disadvantages

❌ **Method resolution order (MRO)** - can be confusing  
❌ **Name conflicts** - mixins can have same method names  
❌ **Implicit dependencies** - mixins may depend on each other  
❌ **Harder to understand** - not clear what methods come from where  
❌ **No initialization order** - `__init__` conflicts  

### Why Less Suitable for Our Use Case

1. **MRO Complexity**: With 5 levels, MRO becomes hard to reason about

2. **Initialization Problems**:
   ```python
   class Worker(TaskMixin, VideoMixin, YouTubeMixin):
       def __init__(self, ...):
           # How to call all mixin __init__?
           # What order?
           TaskMixin.__init__(self, ...)
           VideoMixin.__init__(self, ...)
           YouTubeMixin.__init__(self, ...)
   ```

3. **Less Explicit**: Not clear what methods available without checking all mixins

4. **State Conflicts**: Mixins may set same attributes

### When Mixin Would Be Better

- **Cross-cutting concerns** - logging, caching, retry
- **Optional features** - not all workers need all mixins
- **Python-specific projects** - taking advantage of Python
- **Flat structure** - not deep hierarchy

---

## Alternative 7: Plugin Architecture

**Reference**: https://refactoring.guru/design-patterns/plugin

### Description

Core system discovers and loads plugins at runtime. Each plugin implements standard interface.

### Implementation Example

```python
class WorkerPlugin(ABC):
    @abstractmethod
    def get_name(self) -> str: ...
    
    @abstractmethod
    def process(self, task: Task) -> TaskResult: ...

class PluginManager:
    def __init__(self):
        self._plugins = {}
    
    def register(self, plugin: WorkerPlugin):
        self._plugins[plugin.get_name()] = plugin
    
    def get_plugin(self, name: str) -> WorkerPlugin:
        return self._plugins[name]

# Plugins implement interface
class YouTubeVideoPlugin(WorkerPlugin):
    def get_name(self) -> str:
        return "youtube_video"
    
    def process(self, task: Task) -> TaskResult:
        # Full implementation
        pass

# Usage
manager = PluginManager()
manager.register(YouTubeVideoPlugin())
manager.register(TikTokVideoPlugin())

plugin = manager.get_plugin("youtube_video")
result = plugin.process(task)
```

### Advantages

✅ **Dynamic loading** - add plugins without recompiling  
✅ **Extensible** - third-party plugins  
✅ **Modular** - complete isolation between plugins  

### Disadvantages

❌ **No code reuse** - each plugin from scratch  
❌ **Complex infrastructure** - plugin discovery, loading  
❌ **Overkill** - our workers are built-in, not third-party  

### Why Less Suitable for Our Use Case

**Completely Wrong Problem** - we're building integrated workers, not extensible plugin system.

---

## Why Template Method is Best

### Perfect Match for Our Requirements

✅ **Natural Hierarchy**: Expresses Worker → Video → YouTube → VideoEndpoint  
✅ **Progressive Enrichment**: Each level adds specific functionality  
✅ **Code Reuse**: Base behavior shared automatically  
✅ **Clear Mental Model**: IS-A relationships  
✅ **Easy to Extend**: Add new platform = new subclass  
✅ **Simple**: No complex initialization or component wiring  
✅ **Testable**: Mock parent, test level  
✅ **SOLID**: Follows all 5 principles  

### Comparison Table: Our Requirements

| Requirement | Template Method | Strategy + Composition | Mixin |
|-------------|----------------|----------------------|-------|
| Express hierarchy | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Code reuse | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Progressive enrichment | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Simplicity | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Testability | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Type safety | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### Real-World Usage

Template Method is used in:
- **Django**: Class-Based Views (ListView, DetailView)
- **Java Servlets**: HttpServlet.service() template method
- **React**: Component lifecycle methods
- **pytest**: Test fixture setup/teardown
- **unittest**: setUp()/tearDown() template methods

### Example: Django Class-Based Views

```python
# Django uses Template Method Pattern!
class ListView(View):
    """Base view - template method."""
    
    def get(self, request):
        """Template method defines algorithm."""
        context = self.get_context_data()  # Hook
        return self.render_to_response(context)  # Hook
    
    def get_context_data(self):
        """Hook method - override in subclass."""
        return {'object_list': self.get_queryset()}
    
    def get_queryset(self):
        """Hook method - override in subclass."""
        return []

# Subclass overrides specific steps
class PostListView(ListView):
    def get_queryset(self):
        """Provide specific query."""
        return Post.objects.all()
```

This is EXACTLY our pattern!

---

## Conclusion and Recommendation

### Selected Pattern: Template Method ✅

**Rationale**:
1. **Natural fit** for hierarchical worker structure
2. **Expresses IS-A relationships** clearly
3. **Progressive enrichment** at each level
4. **Proven pattern** used in major frameworks
5. **Simplest solution** that meets all requirements

### Alternative Patterns: When to Use

| Pattern | Use When |
|---------|----------|
| **Strategy** | Need to swap algorithms at runtime |
| **Factory** | Complex object creation (use WITH Template Method) |
| **Builder** | Step-by-step object construction |
| **Decorator** | Optional runtime behaviors |
| **Strategy + Composition** | Avoiding inheritance is priority |
| **Mixin** | Cross-cutting concerns in Python |
| **Plugin** | Third-party extensibility needed |

### Hybrid Approach: Template Method + Others

We can combine patterns:

```python
# Template Method for hierarchy
class BaseWorker(ABC):
    def run(self):  # Template method
        while True:
            task = self.claim_task()  # Hook
            result = self.process_task(task)  # Abstract
            self.report_result(task, result)  # Hook

# + Factory for creation
class WorkerFactory:
    def create(self, type: str) -> BaseWorker:
        if type == "youtube": return YouTubeWorker()

# + Strategy for algorithms
class YouTubeWorker(BaseWorker):
    def __init__(self, claiming_strategy: ClaimingStrategy):
        self.strategy = claiming_strategy  # Strategy Pattern
```

### Final Recommendation

✅ **Use Template Method Pattern** for worker hierarchy  
✅ **Add Factory Pattern** for worker creation (complementary)  
✅ **Add Strategy Pattern** for claiming strategies (complementary)  
✅ **Use Composition** for external dependencies (API clients, databases)  

**Result**: Clean, maintainable, extensible worker hierarchy following SOLID principles.

---

## References

1. **Refactoring.Guru**:
   - [Template Method](https://refactoring.guru/design-patterns/template-method)
   - [Strategy](https://refactoring.guru/design-patterns/strategy)
   - [Factory Method](https://refactoring.guru/design-patterns/factory-method)

2. **Design Patterns** by Gang of Four

3. **Head First Design Patterns** by Freeman & Freeman

4. **Python Design Patterns**: https://python-patterns.guide/

5. **Django Class-Based Views**: https://docs.djangoproject.com/en/stable/topics/class-based-views/

---

**Last Updated**: 2025-11-16  
**Maintained By**: PrismQ.T.Idea.Inspiration Team
