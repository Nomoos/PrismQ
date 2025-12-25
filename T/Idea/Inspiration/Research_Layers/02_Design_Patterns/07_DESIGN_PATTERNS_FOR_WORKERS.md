# Design Patterns for Workers - Research

**Date**: 2025-11-14  
**Purpose**: Research design patterns applicable to worker implementations in PrismQ.T.Idea.Inspiration

## Table of Contents

- [Overview](#overview)
- [Worker Hierarchy Pattern](#worker-hierarchy-pattern)
- [Strategy Pattern](#strategy-pattern)
- [Factory Pattern](#factory-pattern)
- [Template Method Pattern](#template-method-pattern)
- [Observer Pattern](#observer-pattern)
- [Command Pattern](#command-pattern)
- [Chain of Responsibility Pattern](#chain-of-responsibility-pattern)
- [Best Practices](#best-practices)

---

## Overview

Workers in PrismQ.T.Idea.Inspiration follow a layered, modular architecture where specificity increases at each level:

```
PrismQ.T.Idea.Inspiration.From.Video             ← General (Video content handling)
    ↓
PrismQ.T.Idea.Inspiration.From.Video.YouTube     ← Platform-specific (YouTube operations)
    ↓
PrismQ.T.Idea.Inspiration.From.Video.YouTube.Video ← Endpoint-specific (Video scraping)
```

This hierarchy enables:
- **Code reuse** at each abstraction level
- **Specialization** without duplication
- **Flexibility** to add new platforms/endpoints

---

## Worker Hierarchy Pattern

### Concept

Three-tier hierarchy where each level adds specificity:

1. **Media Type Level** - Handles media-specific concerns (Video, Audio, Text)
2. **Platform Level** - Handles platform-specific operations (YouTube, TikTok, Reddit)
3. **Endpoint Level** - Handles specific data types or API endpoints (Video, Channel, Search)

### Implementation

**Level 1: Media Type (Base)**
```python
# Source/Video/src/base_video_worker.py
from abc import ABC, abstractmethod
from Model import IdeaInspiration

class BaseVideoWorker(ABC):
    """Base worker for all video content.
    
    Responsibilities:
    - Video-specific validation
    - Video metadata extraction
    - Video duration handling
    - Thumbnail processing
    """
    
    def __init__(self, config: Config):
        self.config = config
    
    def validate_video_metadata(self, metadata: dict) -> bool:
        """Validate video-specific fields."""
        required = ['title', 'duration', 'url']
        return all(field in metadata for field in required)
    
    @abstractmethod
    def fetch_video_data(self) -> List[dict]:
        """Fetch video data - platform-specific."""
        pass
    
    def process_video(self, raw_data: dict) -> IdeaInspiration:
        """Process video data into IdeaInspiration."""
        if not self.validate_video_metadata(raw_data):
            raise ValueError("Invalid video metadata")
        
        return IdeaInspiration(
            id=self._generate_id(raw_data),
            source=self.get_source_name(),
            platform=self.get_platform_name(),
            title=raw_data['title'],
            url=raw_data['url'],
            media_type='video',
            duration=raw_data['duration'],
            thumbnail_url=raw_data.get('thumbnail'),
        )
```

**Level 2: Platform-Specific**
```python
# Source/Video/YouTube/src/base_youtube_worker.py
from Source.Video.src import BaseVideoWorker

class BaseYouTubeWorker(BaseVideoWorker):
    """Base worker for all YouTube operations.
    
    Responsibilities:
    - YouTube API authentication
    - YouTube-specific error handling
    - YouTube rate limiting
    - YouTube data format conversion
    """
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.api_key = config.youtube_api_key
        self.api_client = YouTubeAPI(self.api_key)
    
    def get_platform_name(self) -> str:
        return "youtube"
    
    def handle_youtube_api_error(self, error: Exception):
        """YouTube-specific error handling."""
        if "quotaExceeded" in str(error):
            logger.error("YouTube API quota exceeded")
            raise QuotaExceededError()
        elif "videoNotFound" in str(error):
            logger.warning("Video not found, skipping")
            return None
        else:
            raise
    
    @abstractmethod
    def get_youtube_endpoint(self) -> str:
        """Specify which YouTube endpoint to use."""
        pass
```

**Level 3: Endpoint-Specific**
```python
# Source/Video/YouTube/Video/src/youtube_video_worker.py
from Source.Video.YouTube.src import BaseYouTubeWorker

class YouTubeVideoWorker(BaseYouTubeWorker):
    """Worker for scraping individual YouTube videos.
    
    Responsibilities:
    - Fetch single video metadata
    - Process video comments (optional)
    - Extract video transcripts (optional)
    """
    
    def get_source_name(self) -> str:
        return "youtube_video"
    
    def get_youtube_endpoint(self) -> str:
        return "videos"
    
    def fetch_video_data(self) -> List[dict]:
        """Fetch video data from YouTube API."""
        try:
            video_id = self.config.video_id
            response = self.api_client.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            ).execute()
            
            return response.get('items', [])
        except Exception as e:
            self.handle_youtube_api_error(e)
            return []
    
    def scrape(self) -> List[IdeaInspiration]:
        """Main entry point for video scraping."""
        raw_videos = self.fetch_video_data()
        return [self.process_video(video) for video in raw_videos]
```

### Benefits

1. **Single Responsibility Principle (SRP)**
   - Each level handles its specific concern
   - Media type handles media operations
   - Platform handles platform operations
   - Endpoint handles specific data fetching

2. **Open/Closed Principle (OCP)**
   - Add new platforms without modifying BaseVideoWorker
   - Add new endpoints without modifying BaseYouTubeWorker
   - Extension through subclassing

3. **Liskov Substitution Principle (LSP)**
   - Any YouTube worker can replace BaseYouTubeWorker
   - Any video worker can replace BaseVideoWorker
   - Polymorphism works correctly

4. **Code Reuse**
   - YouTube API handling shared by all YouTube workers
   - Video validation shared by all video workers
   - No duplication across similar workers

---

## Strategy Pattern

### Concept

Define a family of algorithms, encapsulate each one, and make them interchangeable.

### Use Case: Task Claiming Strategies

```python
# Workers can use different strategies for claiming tasks from queue

from abc import ABC, abstractmethod

class ClaimingStrategy(ABC):
    """Strategy for claiming tasks from queue."""
    
    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Return SQL ORDER BY clause for this strategy."""
        pass

class FIFOStrategy(ClaimingStrategy):
    """First-In-First-Out: Oldest tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "created_at ASC, priority DESC"

class LIFOStrategy(ClaimingStrategy):
    """Last-In-First-Out: Newest tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "created_at DESC, priority DESC"

class PriorityStrategy(ClaimingStrategy):
    """Priority-based: Highest priority first."""
    
    def get_order_by_clause(self) -> str:
        return "priority DESC, created_at ASC"

# Worker uses strategy
class BaseWorker:
    def __init__(self, strategy: ClaimingStrategy):
        self.strategy = strategy
    
    def claim_task(self):
        order_by = self.strategy.get_order_by_clause()
        query = f"SELECT * FROM tasks WHERE status='pending' ORDER BY {order_by} LIMIT 1"
        return execute_query(query)
```

### Benefits

- **Flexibility**: Easy to change algorithm at runtime
- **Testability**: Each strategy tested independently
- **Open/Closed**: Add new strategies without modifying worker

---

## Factory Pattern

### Concept

Create objects without specifying their exact classes.

### Use Case: Worker Creation

```python
from typing import Dict, Type

class WorkerFactory:
    """Factory for creating worker instances.
    
    Follows Open/Closed Principle:
    - Open for extension: Register new workers
    - Closed for modification: Factory logic stable
    """
    
    def __init__(self):
        self._workers: Dict[str, Type[BaseWorker]] = {}
        self._register_default_workers()
    
    def _register_default_workers(self):
        """Register built-in workers."""
        self.register('youtube_video', YouTubeVideoWorker)
        self.register('youtube_channel', YouTubeChannelWorker)
        self.register('youtube_search', YouTubeSearchWorker)
        self.register('tiktok_video', TikTokVideoWorker)
    
    def register(self, task_type: str, worker_class: Type[BaseWorker]):
        """Register a worker class for a task type."""
        self._workers[task_type] = worker_class
    
    def create(self, task_type: str, **kwargs) -> BaseWorker:
        """Create worker instance for task type."""
        if task_type not in self._workers:
            raise ValueError(f"Unknown task type: {task_type}")
        
        worker_class = self._workers[task_type]
        return worker_class(**kwargs)

# Usage
factory = WorkerFactory()

# Create workers without knowing concrete classes
youtube_worker = factory.create('youtube_video', config=config)
tiktok_worker = factory.create('tiktok_video', config=config)

# Extend by registering custom workers
factory.register('custom_worker', MyCustomWorker)
custom_worker = factory.create('custom_worker', config=config)
```

### Benefits

- **Decoupling**: Client code doesn't depend on concrete classes
- **Extensibility**: Easy to add new worker types
- **Single Responsibility**: Creation logic centralized

---

## Template Method Pattern

### Concept

Define the skeleton of an algorithm, letting subclasses override specific steps.

### Use Case: Worker Lifecycle

```python
from abc import ABC, abstractmethod

class BaseWorker(ABC):
    """Template method pattern for worker lifecycle."""
    
    def run(self):
        """Template method defining workflow.
        
        This method is NOT overridden by subclasses.
        Subclasses override the hook methods.
        """
        self.initialize()
        
        while not self.should_stop():
            task = self.claim_task()
            
            if task:
                self.before_processing(task)
                
                try:
                    result = self.process_task(task)  # Hook method
                    self.on_success(task, result)
                except Exception as e:
                    self.on_error(task, e)
                finally:
                    self.after_processing(task)
            else:
                self.on_no_task()
        
        self.cleanup()
    
    # Template methods with default implementations
    def initialize(self):
        """Initialize worker resources."""
        logger.info(f"Initializing {self.__class__.__name__}")
    
    def cleanup(self):
        """Cleanup worker resources."""
        logger.info(f"Cleaning up {self.__class__.__name__}")
    
    def before_processing(self, task):
        """Hook called before processing task."""
        logger.debug(f"Processing task {task.id}")
    
    def after_processing(self, task):
        """Hook called after processing task."""
        logger.debug(f"Completed task {task.id}")
    
    def on_success(self, task, result):
        """Hook called on successful processing."""
        self.report_result(task, result)
    
    def on_error(self, task, error):
        """Hook called on processing error."""
        logger.error(f"Task {task.id} failed: {error}")
        self.report_error(task, error)
    
    def on_no_task(self):
        """Hook called when no task available."""
        time.sleep(self.poll_interval)
    
    # Abstract methods that MUST be implemented
    @abstractmethod
    def process_task(self, task) -> TaskResult:
        """Process a task - implemented by subclasses."""
        pass
    
    @abstractmethod
    def should_stop(self) -> bool:
        """Determine if worker should stop."""
        pass
```

### Benefits

- **Code Reuse**: Common workflow in base class
- **Customization**: Subclasses override specific steps
- **Inversion of Control**: Framework calls subclass methods

---

## Observer Pattern

### Concept

Define a one-to-many dependency so observers are notified of state changes.

### Use Case: Worker Progress Monitoring

```python
from typing import List, Protocol

class WorkerObserver(Protocol):
    """Observer interface for worker events."""
    
    def on_task_started(self, worker_id: str, task_id: int): ...
    def on_task_completed(self, worker_id: str, task_id: int, duration: float): ...
    def on_task_failed(self, worker_id: str, task_id: int, error: str): ...

class MetricsObserver:
    """Observer that tracks worker metrics."""
    
    def __init__(self):
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.total_duration = 0
    
    def on_task_started(self, worker_id: str, task_id: int):
        logger.debug(f"Worker {worker_id} started task {task_id}")
    
    def on_task_completed(self, worker_id: str, task_id: int, duration: float):
        self.tasks_processed += 1
        self.total_duration += duration
        logger.info(f"Task {task_id} completed in {duration}s")
    
    def on_task_failed(self, worker_id: str, task_id: int, error: str):
        self.tasks_failed += 1
        logger.error(f"Task {task_id} failed: {error}")

class ObservableWorker(BaseWorker):
    """Worker that notifies observers of events."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.observers: List[WorkerObserver] = []
    
    def attach(self, observer: WorkerObserver):
        """Attach an observer."""
        self.observers.append(observer)
    
    def detach(self, observer: WorkerObserver):
        """Detach an observer."""
        self.observers.remove(observer)
    
    def notify_started(self, task_id: int):
        """Notify all observers that task started."""
        for observer in self.observers:
            observer.on_task_started(self.worker_id, task_id)
    
    def notify_completed(self, task_id: int, duration: float):
        """Notify all observers that task completed."""
        for observer in self.observers:
            observer.on_task_completed(self.worker_id, task_id, duration)
    
    def process_task(self, task) -> TaskResult:
        """Process task with notifications."""
        self.notify_started(task.id)
        start_time = time.time()
        
        try:
            result = self._do_processing(task)
            duration = time.time() - start_time
            self.notify_completed(task.id, duration)
            return result
        except Exception as e:
            self.notify_failed(task.id, str(e))
            raise

# Usage
worker = ObservableWorker(config)
metrics = MetricsObserver()
worker.attach(metrics)
worker.run()
```

### Benefits

- **Decoupling**: Worker doesn't know about observers
- **Extensibility**: Add new observers without modifying worker
- **Monitoring**: Easy to track worker behavior

---

## Command Pattern

### Concept

Encapsulate requests as objects, allowing parameterization and queuing.

### Use Case: Task Queue

```python
from abc import ABC, abstractmethod

class Command(ABC):
    """Command interface for tasks."""
    
    @abstractmethod
    def execute(self) -> TaskResult:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self):
        """Undo the command (if possible)."""
        pass

class ScrapeVideoCommand(Command):
    """Command to scrape a video."""
    
    def __init__(self, worker: YouTubeVideoWorker, video_id: str):
        self.worker = worker
        self.video_id = video_id
        self.result = None
    
    def execute(self) -> TaskResult:
        """Execute video scraping."""
        self.result = self.worker.scrape_video(self.video_id)
        return self.result
    
    def undo(self):
        """Undo scraping (e.g., delete from database)."""
        if self.result:
            database.delete_idea(self.result.id)

class TaskQueue:
    """Queue that processes commands."""
    
    def __init__(self):
        self.commands: List[Command] = []
        self.history: List[Command] = []
    
    def add_command(self, command: Command):
        """Add command to queue."""
        self.commands.append(command)
    
    def process_next(self):
        """Process next command in queue."""
        if not self.commands:
            return None
        
        command = self.commands.pop(0)
        result = command.execute()
        self.history.append(command)
        return result
    
    def undo_last(self):
        """Undo last executed command."""
        if self.history:
            command = self.history.pop()
            command.undo()
```

### Benefits

- **Flexibility**: Tasks are first-class objects
- **Undo Support**: Commands can be reversed
- **Queuing**: Tasks can be queued and scheduled

---

## Chain of Responsibility Pattern

### Concept

Pass request along a chain of handlers until one handles it.

### Use Case: Data Validation Pipeline

```python
from abc import ABC, abstractmethod

class ValidationHandler(ABC):
    """Base handler for validation chain."""
    
    def __init__(self):
        self._next_handler = None
    
    def set_next(self, handler: 'ValidationHandler'):
        """Set the next handler in chain."""
        self._next_handler = handler
        return handler  # Allow chaining
    
    def handle(self, data: dict) -> bool:
        """Handle validation."""
        if not self._validate(data):
            return False
        
        if self._next_handler:
            return self._next_handler.handle(data)
        
        return True
    
    @abstractmethod
    def _validate(self, data: dict) -> bool:
        """Perform specific validation."""
        pass

class RequiredFieldsValidator(ValidationHandler):
    """Validate required fields present."""
    
    def __init__(self, required_fields: List[str]):
        super().__init__()
        self.required_fields = required_fields
    
    def _validate(self, data: dict) -> bool:
        """Check all required fields present."""
        missing = [f for f in self.required_fields if f not in data]
        if missing:
            logger.error(f"Missing required fields: {missing}")
            return False
        return True

class DataTypeValidator(ValidationHandler):
    """Validate data types are correct."""
    
    def __init__(self, type_spec: Dict[str, type]):
        super().__init__()
        self.type_spec = type_spec
    
    def _validate(self, data: dict) -> bool:
        """Check data types match specification."""
        for field, expected_type in self.type_spec.items():
            if field in data and not isinstance(data[field], expected_type):
                logger.error(f"Field {field} has wrong type")
                return False
        return True

class RangeValidator(ValidationHandler):
    """Validate numeric values in range."""
    
    def __init__(self, ranges: Dict[str, tuple]):
        super().__init__()
        self.ranges = ranges
    
    def _validate(self, data: dict) -> bool:
        """Check values within specified ranges."""
        for field, (min_val, max_val) in self.ranges.items():
            if field in data:
                value = data[field]
                if not (min_val <= value <= max_val):
                    logger.error(f"Field {field} out of range")
                    return False
        return True

# Build validation chain
validator = RequiredFieldsValidator(['title', 'url'])
validator.set_next(
    DataTypeValidator({'title': str, 'duration': int})
).set_next(
    RangeValidator({'duration': (0, 86400)})  # Max 24 hours
)

# Use chain
if validator.handle(video_data):
    process_video(video_data)
```

### Benefits

- **Flexibility**: Easy to add/remove/reorder validators
- **Single Responsibility**: Each validator handles one concern
- **Decoupling**: Handlers don't know about each other

---

## Best Practices

### 1. Layer-Specific Responsibilities

**Do**:
```python
# Video layer - video-specific concerns
class BaseVideoWorker:
    def validate_video_metadata(self, data): ...
    def extract_video_duration(self, data): ...

# Platform layer - platform-specific concerns  
class BaseYouTubeWorker(BaseVideoWorker):
    def authenticate_youtube_api(self): ...
    def handle_youtube_errors(self, error): ...

# Endpoint layer - specific data fetching
class YouTubeVideoWorker(BaseYouTubeWorker):
    def fetch_video_by_id(self, video_id): ...
```

**Don't**:
```python
# Mixing concerns - BAD!
class YouTubeVideoWorker:
    def validate_video_metadata(self): ...  # Should be in BaseVideoWorker
    def authenticate_youtube_api(self): ...  # Should be in BaseYouTubeWorker
    def fetch_video_by_id(self): ...        # OK here
```

### 2. Use Composition Over Inheritance

**Do**:
```python
class Worker:
    def __init__(self, strategy: ClaimingStrategy, observer: MetricsObserver):
        self.strategy = strategy  # Composition
        self.observer = observer  # Composition
```

**Don't**:
```python
class Worker(ClaimingStrategy, MetricsObserver):  # Multiple inheritance - BAD!
    pass
```

### 3. Depend on Abstractions

**Do**:
```python
class Worker:
    def __init__(self, config: Config, database: Database):
        self.config = config      # Depends on interface
        self.database = database  # Depends on interface
```

**Don't**:
```python
class Worker:
    def __init__(self):
        self.config = Config()              # Creates concrete instance
        self.database = SQLiteDatabase()    # Depends on concrete class
```

### 4. Keep Classes Focused

**Do**:
```python
class YouTubeAPIClient:
    """Only handles YouTube API communication."""
    def fetch_video(self, video_id): ...

class VideoProcessor:
    """Only processes video data."""
    def process(self, raw_video): ...

class DatabaseRepository:
    """Only handles database operations."""
    def save_video(self, video): ...
```

**Don't**:
```python
class YouTubeManager:  # God class - BAD!
    def fetch_video(self): ...
    def process_video(self): ...
    def save_to_database(self): ...
    def send_notifications(self): ...
```

---

## Summary

Design patterns enable:
- **SOLID Principles** in practice
- **Code reuse** through inheritance and composition
- **Flexibility** through strategy and factory patterns
- **Maintainability** through clear separation of concerns

**Key Takeaway**: Use patterns to solve specific problems, not for the sake of using patterns. Always consider whether a pattern adds value or just complexity.

---

**Last Updated**: 2025-11-14  
**Related Documents**:
- [01_SOLID_PRINCIPLES_GUIDE.md](./01_SOLID_PRINCIPLES_GUIDE.md)
- [02_LAYERED_ARCHITECTURE_ADR.md](./02_LAYERED_ARCHITECTURE_ADR.md)
- [STRATEGY_PATTERN_RESEARCH.md](./STRATEGY_PATTERN_RESEARCH.md)
