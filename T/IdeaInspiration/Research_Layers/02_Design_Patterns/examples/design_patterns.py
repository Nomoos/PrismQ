#!/usr/bin/env python3
"""
Design Patterns for PrismQ.IdeaInspiration

Demonstrates common design patterns used in the project:
1. Strategy Pattern - Interchangeable algorithms
2. Factory Pattern - Object creation
3. Observer Pattern - Event notification
4. Adapter Pattern - Interface adaptation
5. Repository Pattern - Data access abstraction
"""

from typing import Protocol, List, Dict, Any, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod


# =============================================================================
# 1. STRATEGY PATTERN - Interchangeable Algorithms
# =============================================================================

@dataclass
class Video:
    id: str
    title: str
    duration: int  # seconds


class ScoringStrategy(Protocol):
    """Strategy interface for different scoring algorithms."""
    
    def calculate_score(self, video: Video) -> float:
        """Calculate relevance score."""
        ...


class KeywordScoring:
    """Score based on keywords in title."""
    
    def __init__(self, keywords: List[str]):
        self._keywords = keywords
    
    def calculate_score(self, video: Video) -> float:
        matches = sum(1 for kw in self._keywords if kw.lower() in video.title.lower())
        return min(matches / len(self._keywords), 1.0)


class DurationScoring:
    """Score based on video duration."""
    
    def __init__(self, ideal_duration: int = 600):  # 10 minutes
        self._ideal_duration = ideal_duration
    
    def calculate_score(self, video: Video) -> float:
        diff = abs(video.duration - self._ideal_duration)
        return max(0.0, 1.0 - (diff / self._ideal_duration))


class VideoScorer:
    """Context that uses a scoring strategy."""
    
    def __init__(self, strategy: ScoringStrategy):
        self._strategy = strategy
    
    def score(self, video: Video) -> float:
        return self._strategy.calculate_score(video)
    
    def set_strategy(self, strategy: ScoringStrategy):
        """Change strategy at runtime."""
        self._strategy = strategy


# =============================================================================
# 2. FACTORY PATTERN - Object Creation
# =============================================================================

class Worker(ABC):
    """Abstract worker base class."""
    
    @abstractmethod
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task."""
        pass


class YouTubeWorker(Worker):
    """Worker for YouTube tasks."""
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[YouTube Worker] Processing: {task.get('url')}")
        return {"status": "success", "platform": "youtube"}


class TikTokWorker(Worker):
    """Worker for TikTok tasks."""
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[TikTok Worker] Processing: {task.get('url')}")
        return {"status": "success", "platform": "tiktok"}


class WorkerFactory:
    """Factory for creating workers based on task type."""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, task_type: str, worker_class: type):
        """Register worker class for task type."""
        cls._registry[task_type] = worker_class
    
    @classmethod
    def create(cls, task_type: str) -> Worker:
        """Create worker for task type."""
        worker_class = cls._registry.get(task_type)
        if not worker_class:
            raise ValueError(f"Unknown task type: {task_type}")
        return worker_class()


# Register workers
WorkerFactory.register("youtube", YouTubeWorker)
WorkerFactory.register("tiktok", TikTokWorker)


# =============================================================================
# 3. OBSERVER PATTERN - Event Notification
# =============================================================================

class Observer(Protocol):
    """Observer interface for receiving updates."""
    
    def update(self, event: str, data: Any) -> None:
        """Receive update notification."""
        ...


class TaskCompletionLogger:
    """Observer that logs task completions."""
    
    def update(self, event: str, data: Any) -> None:
        if event == "task_completed":
            print(f"[Logger] Task completed: {data.get('task_id')}")
        elif event == "task_failed":
            print(f"[Logger] Task failed: {data.get('task_id')}")


class TaskCompletionNotifier:
    """Observer that sends notifications."""
    
    def update(self, event: str, data: Any) -> None:
        if event == "task_completed":
            print(f"[Notifier] Sending notification for task: {data.get('task_id')}")


class TaskSubject:
    """Subject that notifies observers of task events."""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Add observer."""
        self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Remove observer."""
        self._observers.remove(observer)
    
    def notify(self, event: str, data: Any) -> None:
        """Notify all observers."""
        for observer in self._observers:
            observer.update(event, data)
    
    def complete_task(self, task_id: str) -> None:
        """Complete task and notify observers."""
        print(f"[Subject] Completing task: {task_id}")
        self.notify("task_completed", {"task_id": task_id})


# =============================================================================
# 4. ADAPTER PATTERN - Interface Adaptation
# =============================================================================

@dataclass
class IdeaInspiration:
    """Our domain model."""
    id: str
    title: str
    source: str


class YouTubeAPIResponse:
    """Third-party YouTube API response (different format)."""
    
    def __init__(self, video_id: str, video_title: str):
        self.videoId = video_id  # Different naming convention
        self.videoTitle = video_title


class YouTubeAdapter:
    """Adapter that converts YouTube API response to our domain model."""
    
    def __init__(self, api_response: YouTubeAPIResponse):
        self._api_response = api_response
    
    def to_idea_inspiration(self) -> IdeaInspiration:
        """Convert to IdeaInspiration."""
        return IdeaInspiration(
            id=self._api_response.videoId,
            title=self._api_response.videoTitle,
            source="youtube"
        )


# =============================================================================
# 5. REPOSITORY PATTERN - Data Access Abstraction
# =============================================================================

class IdeaRepository(Protocol):
    """Repository interface for idea persistence."""
    
    def save(self, idea: IdeaInspiration) -> str:
        """Save idea."""
        ...
    
    def find_by_id(self, idea_id: str) -> IdeaInspiration:
        """Find idea by ID."""
        ...
    
    def list_all(self) -> List[IdeaInspiration]:
        """List all ideas."""
        ...


class InMemoryIdeaRepository:
    """In-memory implementation for testing."""
    
    def __init__(self):
        self._ideas: Dict[str, IdeaInspiration] = {}
    
    def save(self, idea: IdeaInspiration) -> str:
        self._ideas[idea.id] = idea
        print(f"[InMemory] Saved idea: {idea.id}")
        return idea.id
    
    def find_by_id(self, idea_id: str) -> IdeaInspiration:
        return self._ideas.get(idea_id)
    
    def list_all(self) -> List[IdeaInspiration]:
        return list(self._ideas.values())


class SqliteIdeaRepository:
    """SQLite implementation for production."""
    
    def __init__(self, db_path: str):
        self._db_path = db_path
    
    def save(self, idea: IdeaInspiration) -> str:
        print(f"[SQLite] Saving idea to {self._db_path}")
        return idea.id
    
    def find_by_id(self, idea_id: str) -> IdeaInspiration:
        print(f"[SQLite] Finding idea: {idea_id}")
        return None
    
    def list_all(self) -> List[IdeaInspiration]:
        print("[SQLite] Listing all ideas")
        return []


# =============================================================================
# DEMONSTRATION
# =============================================================================

def demonstrate_patterns():
    """Demonstrate all design patterns."""
    print("\n" + "="*70)
    print("DESIGN PATTERNS DEMONSTRATION")
    print("="*70)
    
    # 1. Strategy Pattern
    print("\n1. STRATEGY PATTERN - Interchangeable Scoring")
    video = Video(id="1", title="Python Tutorial for Beginners", duration=720)
    
    # Use keyword strategy
    scorer = VideoScorer(KeywordScoring(["python", "tutorial"]))
    print(f"   Keyword score: {scorer.score(video):.2f}")
    
    # Change strategy at runtime
    scorer.set_strategy(DurationScoring(ideal_duration=600))
    print(f"   Duration score: {scorer.score(video):.2f}")
    print("   ✅ Strategies are interchangeable!")
    
    # 2. Factory Pattern
    print("\n2. FACTORY PATTERN - Worker Creation")
    youtube_worker = WorkerFactory.create("youtube")
    result = youtube_worker.process({"url": "https://youtube.com/watch?v=123"})
    print(f"   Result: {result}")
    
    tiktok_worker = WorkerFactory.create("tiktok")
    result = tiktok_worker.process({"url": "https://tiktok.com/@user/video/456"})
    print(f"   Result: {result}")
    print("   ✅ Factory creates appropriate workers!")
    
    # 3. Observer Pattern
    print("\n3. OBSERVER PATTERN - Event Notification")
    subject = TaskSubject()
    
    # Attach observers
    logger = TaskCompletionLogger()
    notifier = TaskCompletionNotifier()
    subject.attach(logger)
    subject.attach(notifier)
    
    # Complete task (notifies all observers)
    subject.complete_task("task-123")
    print("   ✅ All observers notified!")
    
    # 4. Adapter Pattern
    print("\n4. ADAPTER PATTERN - API Response Adaptation")
    api_response = YouTubeAPIResponse(
        video_id="yt-789",
        video_title="Awesome Video"
    )
    adapter = YouTubeAdapter(api_response)
    idea = adapter.to_idea_inspiration()
    print(f"   Adapted to IdeaInspiration: {idea.title} (source: {idea.source})")
    print("   ✅ External API adapted to domain model!")
    
    # 5. Repository Pattern
    print("\n5. REPOSITORY PATTERN - Data Access Abstraction")
    
    # Use in-memory repo for testing
    repo: IdeaRepository = InMemoryIdeaRepository()
    repo.save(idea)
    
    # Can swap to SQLite without changing code
    repo = SqliteIdeaRepository("ideas.db")
    repo.save(idea)
    print("   ✅ Repository implementation swappable!")
    
    print("\n" + "="*70)
    print("KEY BENEFITS:")
    print("✅ Strategy: Change algorithms at runtime")
    print("✅ Factory: Centralize object creation")
    print("✅ Observer: Decouple event sources from handlers")
    print("✅ Adapter: Integrate third-party systems")
    print("✅ Repository: Abstract data access")
    print("="*70 + "\n")


if __name__ == "__main__":
    demonstrate_patterns()
