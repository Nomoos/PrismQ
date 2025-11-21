# SOLID Principles Guide

**Purpose**: Guide for applying SOLID design principles in PrismQ.IdeaInspiration  
**Last Updated**: 2025-11-17  
**Version**: 1.0

---

## 📋 Overview

SOLID is a set of five design principles that help create maintainable, flexible, and scalable software. This guide provides practical guidance for applying these principles in Python code for the PrismQ ecosystem.

---

## 🎯 The SOLID Principles

### 1. Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change.

**What it means**: Each class should focus on doing one thing well. If a class has multiple responsibilities, changes to one responsibility may affect the others.

**Python Example**:

```python
# ❌ BAD: Multiple responsibilities
class VideoProcessor:
    def download_video(self, url: str) -> bytes:
        """Downloads video from URL."""
        pass
    
    def process_video(self, video: bytes) -> bytes:
        """Processes video content."""
        pass
    
    def save_to_database(self, video: bytes) -> None:
        """Saves video to database."""
        pass

# ✅ GOOD: Single responsibility per class
class VideoDownloader:
    """Responsible only for downloading videos."""
    def download(self, url: str) -> bytes:
        pass

class VideoProcessor:
    """Responsible only for processing videos."""
    def process(self, video: bytes) -> bytes:
        pass

class VideoRepository:
    """Responsible only for video storage."""
    def save(self, video: bytes) -> None:
        pass
```

**Guidelines**:
- Each class should have a clear, focused purpose
- If you can't describe a class in one sentence without using "and", it probably violates SRP
- Changes to business logic should not affect data access or presentation layers

---

### 2. Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension but closed for modification.

**What it means**: You should be able to add new functionality without changing existing code. Use abstraction and polymorphism to achieve this.

**Python Example**:

```python
# ❌ BAD: Need to modify class for new formats
class VideoExporter:
    def export(self, video: Video, format: str) -> bytes:
        if format == "mp4":
            return self._export_mp4(video)
        elif format == "webm":
            return self._export_webm(video)
        # Need to modify this class for each new format

# ✅ GOOD: Open for extension, closed for modification
from abc import ABC, abstractmethod
from typing import Protocol

class VideoExporter(Protocol):
    """Abstract interface for video exporters."""
    def export(self, video: Video) -> bytes:
        """Export video to specific format."""
        ...

class MP4Exporter:
    """Exports video to MP4 format."""
    def export(self, video: Video) -> bytes:
        return self._convert_to_mp4(video)

class WebMExporter:
    """Exports video to WebM format."""
    def export(self, video: Video) -> bytes:
        return self._convert_to_webm(video)

# New formats can be added without modifying existing code
class AVIExporter:
    """Exports video to AVI format."""
    def export(self, video: Video) -> bytes:
        return self._convert_to_avi(video)
```

**Guidelines**:
- Use abstract base classes (ABC) or Protocols to define interfaces
- Design systems around stable abstractions
- Add new features by creating new classes, not modifying existing ones
- Use dependency injection to swap implementations

---

### 3. Liskov Substitution Principle (LSP)

**Definition**: Subtypes must be substitutable for their base types without altering program correctness.

**What it means**: If class B is a subtype of class A, you should be able to replace A with B without breaking the program.

**Python Example**:

```python
# ❌ BAD: Violates LSP - ReadOnlyVideo can't replace Video
class Video:
    def set_title(self, title: str) -> None:
        self.title = title
    
    def get_title(self) -> str:
        return self.title

class ReadOnlyVideo(Video):
    def set_title(self, title: str) -> None:
        raise NotImplementedError("Cannot modify read-only video")
    # This breaks LSP - can't substitute Video with ReadOnlyVideo

# ✅ GOOD: Properly designed hierarchy
from abc import ABC, abstractmethod

class VideoMetadata(ABC):
    """Base class for video metadata."""
    @abstractmethod
    def get_title(self) -> str:
        pass

class MutableVideo(VideoMetadata):
    """Video with mutable metadata."""
    def __init__(self):
        self._title = ""
    
    def get_title(self) -> str:
        return self._title
    
    def set_title(self, title: str) -> None:
        self._title = title

class ImmutableVideo(VideoMetadata):
    """Video with immutable metadata."""
    def __init__(self, title: str):
        self._title = title
    
    def get_title(self) -> str:
        return self._title
```

**Guidelines**:
- Subclasses should strengthen postconditions, not weaken them
- Don't throw unexpected exceptions in subclasses
- Maintain the behavioral contract of the parent class
- If you need to disable parent functionality, reconsider your inheritance hierarchy

---

### 4. Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they don't use.

**What it means**: Create small, focused interfaces rather than large, monolithic ones. Classes should only implement methods they actually need.

**Python Example**:

```python
# ❌ BAD: Fat interface forces implementations to provide unused methods
from abc import ABC, abstractmethod

class VideoSource(ABC):
    @abstractmethod
    def fetch_videos(self) -> list[Video]:
        pass
    
    @abstractmethod
    def upload_video(self, video: Video) -> None:
        pass
    
    @abstractmethod
    def delete_video(self, video_id: str) -> None:
        pass
    
    @abstractmethod
    def search_videos(self, query: str) -> list[Video]:
        pass

# Read-only source must implement upload/delete
class YouTubeSource(VideoSource):
    def upload_video(self, video: Video) -> None:
        raise NotImplementedError("YouTube API is read-only")
    
    def delete_video(self, video_id: str) -> None:
        raise NotImplementedError("YouTube API is read-only")

# ✅ GOOD: Segregated interfaces
from typing import Protocol

class VideoReader(Protocol):
    """Read-only video source interface."""
    def fetch_videos(self) -> list[Video]:
        ...
    
    def search_videos(self, query: str) -> list[Video]:
        ...

class VideoWriter(Protocol):
    """Write-only video destination interface."""
    def upload_video(self, video: Video) -> None:
        ...
    
    def delete_video(self, video_id: str) -> None:
        ...

class YouTubeSource:
    """Only implements what it needs - reading."""
    def fetch_videos(self) -> list[Video]:
        pass
    
    def search_videos(self, query: str) -> list[Video]:
        pass

class LocalVideoStorage:
    """Implements both reading and writing."""
    def fetch_videos(self) -> list[Video]:
        pass
    
    def search_videos(self, query: str) -> list[Video]:
        pass
    
    def upload_video(self, video: Video) -> None:
        pass
    
    def delete_video(self, video_id: str) -> None:
        pass
```

**Guidelines**:
- Use Python's `Protocol` for duck typing and interface definition
- Create role-based interfaces (e.g., `Readable`, `Writable`, `Searchable`)
- Keep interfaces small and focused on specific capabilities
- Clients should depend only on the methods they actually use

---

### 5. Dependency Inversion Principle (DIP)

**Definition**: 
- High-level modules should not depend on low-level modules. Both should depend on abstractions.
- Abstractions should not depend on details. Details should depend on abstractions.

**What it means**: Depend on interfaces/abstractions, not concrete implementations. Use dependency injection to provide implementations.

**Python Example**:

```python
# ❌ BAD: High-level class depends on low-level implementation
class VideoAnalyzer:
    def __init__(self):
        self.storage = PostgresDatabase()  # Depends on concrete class
    
    def analyze(self, video_id: str) -> dict:
        video = self.storage.get_video(video_id)
        return self._perform_analysis(video)

# ✅ GOOD: Depend on abstractions, inject dependencies
from typing import Protocol

class VideoStorage(Protocol):
    """Abstract storage interface."""
    def get_video(self, video_id: str) -> Video:
        ...

class VideoAnalyzer:
    """High-level class depends on abstraction."""
    def __init__(self, storage: VideoStorage):
        self.storage = storage  # Depends on Protocol
    
    def analyze(self, video_id: str) -> dict:
        video = self.storage.get_video(video_id)
        return self._perform_analysis(video)

# Low-level implementations
class PostgresDatabase:
    """Concrete implementation of VideoStorage."""
    def get_video(self, video_id: str) -> Video:
        # PostgreSQL-specific implementation
        pass

class MongoDatabase:
    """Alternative implementation of VideoStorage."""
    def get_video(self, video_id: str) -> Video:
        # MongoDB-specific implementation
        pass

# Usage with dependency injection
postgres_storage = PostgresDatabase()
analyzer = VideoAnalyzer(storage=postgres_storage)

# Easy to swap implementations
mongo_storage = MongoDatabase()
analyzer = VideoAnalyzer(storage=mongo_storage)
```

**Guidelines**:
- Use constructor injection to provide dependencies
- Define abstractions using `Protocol` or `ABC` (Abstract Base Classes)
- Depend on interfaces, not concrete classes
- Use dependency injection containers for complex applications
- Configuration should inject concrete implementations

---

## 🔍 Code Reviews

For detailed examples of SOLID principles applied in this repository, see:

- **[SOLID Review: Core Modules](./solid/code_reviews/SOLID_REVIEW_CORE_MODULES.md)** - Classification, ConfigLoad, Model, Scoring
- **[SOLID Review: Video and Text Modules](./solid/code_reviews/SOLID_REVIEW_VIDEO_TEXT_MODULES.md)** - Video and Text source modules

---

## 📚 Additional Design Principles

While not part of SOLID, these complementary principles are also important:

### DRY (Don't Repeat Yourself)
- Eliminate code duplication
- Extract common functionality into reusable components
- Use inheritance, composition, or utility functions

### KISS (Keep It Simple, Stupid)
- Favor simplicity over complexity
- Write clear, readable code
- Avoid over-engineering

### YAGNI (You Aren't Gonna Need It)
- Only implement what's needed now
- Don't add functionality for hypothetical future needs
- Refactor when requirements actually emerge

### Composition Over Inheritance
- Prefer object composition to class inheritance
- Use composition for "has-a" relationships
- Use inheritance only for "is-a" relationships
- Composition provides more flexibility

---

## 🛠️ Applying SOLID in Python

### Use Python's Protocol for Interfaces

```python
from typing import Protocol

class VideoProcessor(Protocol):
    """Define interface without forcing inheritance."""
    def process(self, video: Video) -> Video:
        ...
```

### Use Dataclasses for Data Containers

```python
from dataclasses import dataclass

@dataclass
class VideoMetadata:
    """Pure data container - follows SRP."""
    title: str
    duration: int
    format: str
```

### Use Type Hints

```python
def process_video(processor: VideoProcessor, video: Video) -> Video:
    """Type hints document dependencies and contracts."""
    return processor.process(video)
```

### Use Dependency Injection

```python
class VideoService:
    def __init__(
        self,
        downloader: VideoDownloader,
        processor: VideoProcessor,
        storage: VideoStorage
    ):
        self.downloader = downloader
        self.processor = processor
        self.storage = storage
```

---

## ✅ Checklist for SOLID Code

When writing or reviewing code, ask:

- **SRP**: Does this class have a single, well-defined responsibility?
- **OCP**: Can I add new features without modifying existing code?
- **LSP**: Can I substitute any subclass for its parent without breaking things?
- **ISP**: Are my interfaces focused and minimal?
- **DIP**: Do I depend on abstractions rather than concrete implementations?

---

## 📖 References

- [SOLID Principles Explained](https://en.wikipedia.org/wiki/SOLID)
- [Python Design Patterns](https://refactoring.guru/design-patterns/python)
- [Architecture Guide](.ARCHITECTURE.md)
- [Contributing Guide](./CONTRIBUTING.md)

---

## 🔗 Related Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [Code Review Guidelines](./solid/code_reviews/)
- [Development Guide](./development/)
- [Testing Guide](./development/TESTING.md)
