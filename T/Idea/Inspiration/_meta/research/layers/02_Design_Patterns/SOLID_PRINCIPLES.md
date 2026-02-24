# SOLID Principles for PrismQ.T.Idea.Inspiration

This document provides comprehensive guidelines on applying SOLID principles to the PrismQ.T.Idea.Inspiration codebase. These principles are fundamental to maintaining a clean, maintainable, and extensible architecture.

## Overview

SOLID is an acronym for five design principles intended to make software designs more understandable, flexible, and maintainable:

- **S**ingle Responsibility Principle (SRP)
- **O**pen/Closed Principle (OCP)
- **L**iskov Substitution Principle (LSP)
- **I**nterface Segregation Principle (ISP)
- **D**ependency Inversion Principle (DIP)

## 1. Single Responsibility Principle (SRP)

> **"A class should have one, and only one, reason to change."**

Each module, class, or function should have responsibility over a single part of the functionality, and that responsibility should be entirely encapsulated by the class.

### Guidelines

- Each class should focus on a single concern or business domain
- If you can describe what a class does with "AND", it probably violates SRP
- Changes to one responsibility should not affect other parts of the code
- Extract separate responsibilities into different classes

### Good Example

```python
# ✅ GOOD: Each class has a single, clear responsibility

class CategoryClassifier:
    """Classifies content into primary categories using keyword analysis."""
    
    def classify(self, title: str, description: str = "") -> CategoryResult:
        """Classify content into a primary category."""
        # Only handles category classification logic
        pass

class StoryDetector:
    """Detects if content is likely a story based on metadata analysis."""
    
    def detect(self, title: str, description: str = "") -> Tuple[bool, float, List[str]]:
        """Detect if content is likely a story."""
        # Only handles story detection logic
        pass

class TextClassifier:
    """Classification enrichment orchestrator for IdeaInspiration content."""
    
    def __init__(self, category_classifier: CategoryClassifier, story_detector: StoryDetector):
        """Initialize with injected dependencies."""
        self.category_classifier = category_classifier
        self.story_detector = story_detector
    
    def enrich(self, inspiration: IdeaInspiration) -> ClassificationEnrichment:
        """Orchestrate classification and detection for enrichment."""
        # Orchestrates other classifiers, doesn't implement classification logic
        pass
```

### Bad Example

```python
# ❌ BAD: Class has multiple responsibilities

class ContentProcessor:
    """Processes content by classifying, detecting stories, scoring, AND saving to database."""
    
    def process(self, content: str):
        # Classifies content
        category = self._classify(content)
        
        # Detects stories
        is_story = self._detect_story(content)
        
        # Scores content
        score = self._calculate_score(content)
        
        # Saves to database
        self._save_to_db(category, is_story, score)
        
        # Sends notifications
        self._send_notification(category)
```

**Problem**: This class violates SRP because it has multiple reasons to change:
- Classification algorithm changes
- Story detection logic changes
- Scoring algorithm changes
- Database schema changes
- Notification system changes

### Application in PrismQ.T.Idea.Inspiration

Examples from the codebase:

- **Classification Module**: `CategoryClassifier`, `StoryDetector`, and `TextClassifier` are separate classes with distinct responsibilities
- **Model Module**: `IdeaInspiration` (data model) is separate from `IdeaInspirationDatabase` (persistence)
- **ConfigLoad Module**: `Config` class only manages configuration, not application logic

## 2. Open/Closed Principle (OCP)

> **"Software entities should be open for extension, but closed for modification."**

You should be able to add new functionality without changing existing code. This is typically achieved through abstraction and polymorphism.

### Guidelines

- Use inheritance, interfaces, or composition to extend behavior
- Design classes to be extended without modification
- Use configuration or strategy patterns for variable behavior
- Avoid modifying working code when adding features

### Good Example

```python
# ✅ GOOD: Open for extension, closed for modification

class IdeaInspiration:
    """Core data model - closed for modification, open for extension."""
    
    @classmethod
    def from_text(cls, title: str, text_content: str, **kwargs) -> "IdeaInspiration":
        """Create text-based inspiration."""
        return cls(
            title=title,
            content=text_content,
            source_type=ContentType.TEXT,
            **kwargs
        )
    
    @classmethod
    def from_video(cls, title: str, subtitle_text: str, **kwargs) -> "IdeaInspiration":
        """Create video-based inspiration."""
        return cls(
            title=title,
            content=subtitle_text,
            source_type=ContentType.VIDEO,
            **kwargs
        )
    
    # NEW: Add new content types without modifying existing methods
    @classmethod
    def from_podcast(cls, title: str, transcript: str, **kwargs) -> "IdeaInspiration":
        """Create podcast-based inspiration."""
        return cls(
            title=title,
            content=transcript,
            source_type=ContentType.AUDIO,
            **kwargs
        )
```

### Strategy Pattern for Extensibility

```python
# ✅ GOOD: Strategy pattern for pluggable scoring algorithms
# SOLID Principles

## Overview

SOLID is an acronym for five design principles that help create maintainable, flexible, and scalable software. These principles are fundamental to the architecture of PrismQ.T.Idea.Inspiration and should be applied throughout the codebase.

## Table of Contents

1. [Single Responsibility Principle (SRP)](#single-responsibility-principle-srp)
2. [Open/Closed Principle (OCP)](#openclosed-principle-ocp)
3. [Liskov Substitution Principle (LSP)](#liskov-substitution-principle-lsp)
4. [Interface Segregation Principle (ISP)](#interface-segregation-principle-isp)
5. [Dependency Inversion Principle (DIP)](#dependency-inversion-principle-dip)
6. [Practical Applications in PrismQ](#practical-applications-in-prismq)
7. [Related Patterns](#related-patterns)

---

## Single Responsibility Principle (SRP)

### Definition

**A class should have only one reason to change.**

Each class should focus on a single responsibility or concern. When a class has multiple responsibilities, changes to one responsibility can affect or break the others.

### Benefits
- Easier to understand and maintain
- Reduced coupling between different concerns
- Easier to test (focused, smaller tests)
- Changes are localized and less risky

### Example: Violation

```python
# ❌ BAD: Multiple responsibilities
class VideoProcessor:
    """This class does too much."""
    
    def fetch_video_metadata(self, video_id: str) -> dict:
        """Fetch metadata from API."""
        # API fetching logic
        pass
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text."""
        # NLP analysis logic
        pass
    
    def save_to_database(self, data: dict) -> None:
        """Save data to database."""
        # Database logic
        pass
    
    def generate_report(self, data: dict) -> str:
        """Generate HTML report."""
        # Report generation logic
        pass
```

**Problems:**
- Changes to API fetching affect the entire class
- Database changes require modifying this class
- Difficult to test individual responsibilities
- Hard to reuse parts of this functionality elsewhere

### Example: Following SRP

```python
# ✅ GOOD: Separate responsibilities into focused classes

class VideoMetadataFetcher:
    """Responsible only for fetching video metadata."""
    
    def fetch(self, video_id: str) -> dict:
        """Fetch metadata from API."""
        # API fetching logic
        return {"video_id": video_id, "title": "..."}

class SentimentAnalyzer:
    """Responsible only for sentiment analysis."""
    
    def analyze(self, text: str) -> str:
        """Analyze sentiment of text."""
        # NLP analysis logic
        return "positive"

class VideoDataRepository:
    """Responsible only for data persistence."""
    
    def save(self, data: dict) -> None:
        """Save data to database."""
        # Database logic
        pass

class ReportGenerator:
    """Responsible only for report generation."""
    
    def generate(self, data: dict) -> str:
        """Generate HTML report."""
        # Report generation logic
        return "<html>...</html>"

# Compose these focused classes as needed
class VideoProcessor:
    """Orchestrates video processing using focused components."""
    
    def __init__(
        self,
        fetcher: VideoMetadataFetcher,
        analyzer: SentimentAnalyzer,
        repository: VideoDataRepository,
        reporter: ReportGenerator
    ):
        self._fetcher = fetcher
        self._analyzer = analyzer
        self._repository = repository
        self._reporter = reporter
    
    def process(self, video_id: str) -> str:
        """Process video through the pipeline."""
        metadata = self._fetcher.fetch(video_id)
        sentiment = self._analyzer.analyze(metadata.get("title", ""))
        metadata["sentiment"] = sentiment
        self._repository.save(metadata)
        return self._reporter.generate(metadata)
```

### Guidelines
- Ask: "What is the one thing this class does?"
- If you need "and" to describe what a class does, it probably violates SRP
- Extract methods into separate classes when they represent distinct concerns
- Use composition to combine focused classes

---

## Open/Closed Principle (OCP)

### Definition

**Software entities should be open for extension, but closed for modification.**

You should be able to add new functionality without changing existing code. This is typically achieved through abstraction and polymorphism.

### Benefits
- Existing code remains stable (fewer bugs from changes)
- New features can be added with minimal risk
- Better code reusability
- Easier to maintain and extend

### Example: Violation

```python
# ❌ BAD: Requires modification to add new functionality
class ContentScorer:
    """Calculate scores for different content types."""
    
    def calculate_score(self, content: dict) -> float:
        content_type = content.get("type")
        
        if content_type == "video":
            return self._score_video(content)
        elif content_type == "article":
            return self._score_article(content)
        elif content_type == "podcast":
            return self._score_podcast(content)
        else:
            return 0.0
    
    def _score_video(self, content: dict) -> float:
        return content.get("views", 0) / 1000
    
    def _score_article(self, content: dict) -> float:
        return content.get("words", 0) / 100
    
    def _score_podcast(self, content: dict) -> float:
        return content.get("duration", 0) / 60
```

**Problems:**
- Adding a new content type requires modifying `calculate_score`
- Risk of breaking existing functionality
- Violates SRP as well (too many content types in one class)

### Example: Following OCP

```python
# ✅ GOOD: Open for extension, closed for modification

from typing import Protocol

class ScoringStrategy(Protocol):
    """Protocol for scoring strategies."""
    
    def score(self, text: str) -> float:
        """Calculate score for given text."""
        ...

class ReadabilityScorer:
    """Scores text based on readability metrics."""
    
    def score(self, text: str) -> float:
        # Readability-based scoring
        pass

class SentimentScorer:
    """Scores text based on sentiment analysis."""
    
    def score(self, text: str) -> float:
        # Sentiment-based scoring
        pass

class AIModelScorer:
    """Scores text using AI/ML models."""
    
    def score(self, text: str) -> float:
        # AI model-based scoring
        pass

class TextScorer:
    """Orchestrates multiple scoring strategies."""
    
    def __init__(self, strategies: List[ScoringStrategy]):
        self.strategies = strategies
    
    def score_text(self, text: str) -> Dict[str, float]:
        """Score text using all configured strategies."""
        return {
            strategy.__class__.__name__: strategy.score(text)
            for strategy in self.strategies
        }
```

### Bad Example

```python
# ❌ BAD: Must modify existing code to add new functionality

class TextScorer:
    def score(self, text: str, score_type: str) -> float:
        # Must modify this method every time we add a new scoring type
        if score_type == "readability":
            return self._score_readability(text)
        elif score_type == "sentiment":
            return self._score_sentiment(text)
        elif score_type == "ai_model":  # NEW: Must modify existing code
            return self._score_with_ai(text)
        # Adding more types requires modifying this method
```

### Application in PrismQ.T.Idea.Inspiration

- **CategoryClassifier**: New categories can be added to `CATEGORY_KEYWORDS` without modifying classification logic
- **IdeaInspiration**: Factory methods allow new content types without changing core model
- **StoryDetector**: Configurable threshold allows behavior modification without code changes

## 3. Liskov Substitution Principle (LSP)

> **"Objects of a superclass should be replaceable with objects of a subclass without breaking the application."**

Subtypes must be substitutable for their base types. If class B is a subtype of class A, then objects of type A should be replaceable with objects of type B without altering the correctness of the program.

### Guidelines

- Subclasses should strengthen postconditions, not weaken them
- Subclasses should not throw unexpected exceptions
- Subclasses should preserve the behavior expected by clients of the base class
- Use composition over inheritance when behavior differs significantly

### Good Example

```python
# ✅ GOOD: Subtypes are substitutable for base type

from abc import ABC, abstractmethod
from typing import Dict, Any

class ContentSource(ABC):
    """Abstract base class for all content sources."""
    
    @abstractmethod
    def fetch(self, query: str) -> List[Dict[str, Any]]:
        """Fetch content based on query. Must return list of content items."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate source configuration. Must return True if valid."""
        pass

class YouTubeSource(ContentSource):
    """YouTube content source."""
    
    def fetch(self, query: str) -> List[Dict[str, Any]]:
        """Fetch YouTube videos matching query."""
        # Returns list as expected by base class
        results = self.api.search(query)
        return [self._normalize(item) for item in results]
    
    def validate_config(self) -> bool:
        """Validate YouTube API configuration."""
        # Returns bool as expected by base class
        return self.api_key is not None

class RedditSource(ContentSource):
    """Reddit content source."""
    
    def fetch(self, query: str) -> List[Dict[str, Any]]:
        """Fetch Reddit posts matching query."""
        # Returns list as expected by base class
        posts = self.reddit.search(query)
        return [self._normalize(post) for post in posts]
    
    def validate_config(self) -> bool:
        """Validate Reddit API configuration."""
        # Returns bool as expected by base class
        return self.client_id is not None and self.client_secret is not None

# Client code works with any ContentSource
def collect_content(source: ContentSource, query: str) -> List[Dict[str, Any]]:
    """Collect content from any source."""
    if source.validate_config():
        return source.fetch(query)
    return []

# Both work identically from client perspective
youtube = YouTubeSource()
reddit = RedditSource()

results1 = collect_content(youtube, "AI trends")  # Works
results2 = collect_content(reddit, "AI trends")   # Works
```

### Bad Example

```python
# ❌ BAD: Subtype is not substitutable for base type

class ContentSource(ABC):
    @abstractmethod
    def fetch(self, query: str) -> List[Dict[str, Any]]:
        """Fetch content based on query."""
        pass

class BrokenSource(ContentSource):
    def fetch(self, query: str) -> str:  # ❌ Returns wrong type
        """Fetch content - but returns string instead of list."""
        return "some results"  # Violates LSP

class RestrictedSource(ContentSource):
    def fetch(self, query: str) -> List[Dict[str, Any]]:
        """Fetch content - but adds unexpected restrictions."""
        if len(query) < 5:  # ❌ Adds constraint not in base class
            raise ValueError("Query too short")
        return self._do_fetch(query)
```

### Application in PrismQ.T.Idea.Inspiration

- **Factory Methods**: All factory methods return `IdeaInspiration` instances with consistent behavior
- **Enum Types**: `ContentType` and `PrimaryCategory` enum values are interchangeable
- **Protocol-Based Design**: Uses Python's Protocol for duck typing, providing LSP-like guarantees

**Note**: Python uses duck typing rather than strict inheritance hierarchies. LSP is implicitly followed through consistent interfaces and type hints.

## 4. Interface Segregation Principle (ISP)

> **"No client should be forced to depend on methods it does not use."**

Many client-specific interfaces are better than one general-purpose interface. Classes should not be forced to implement interfaces they don't use.

### Guidelines

- Create focused, minimal interfaces
- Split large interfaces into smaller, specific ones
- Clients should only depend on the methods they actually need
- Use composition to combine interfaces when needed

### Good Example

```python
# ✅ GOOD: Focused, minimal interfaces

from typing import Protocol

class Readable(Protocol):
    """Protocol for readable sources."""
    
    def read(self) -> str:
        """Read content from source."""
        ...

class Writable(Protocol):
    """Protocol for writable destinations."""
    
    def write(self, content: str) -> None:
        """Write content to destination."""
        ...

class Searchable(Protocol):
    """Protocol for searchable sources."""
    
    def search(self, query: str) -> List[str]:
        """Search for content matching query."""
        ...

# Implementations choose which interfaces to support

class TextFile:
    """Text file supports read and write."""
    
    def read(self) -> str:
        """Read file content."""
        pass
    
    def write(self, content: str) -> None:
        """Write content to file."""
        pass

class APIClient:
    """API client supports read and search."""
    
    def read(self) -> str:
        """Fetch content from API."""
        pass
    
    def search(self, query: str) -> List[str]:
        """Search API for content."""
        pass

class Logger:
    """Logger only supports write."""
    
    def write(self, content: str) -> None:
        """Write log message."""
        pass

# Clients use only what they need

def backup_content(source: Readable, destination: Writable) -> None:
    """Backup content from source to destination."""
    content = source.read()
    destination.write(content)

def find_content(source: Searchable, query: str) -> List[str]:
    """Find content in searchable source."""
    return source.search(query)
```

### Bad Example

```python
# ❌ BAD: Bloated interface forcing unnecessary implementations

class ContentManager(Protocol):
    """Bloated interface with too many responsibilities."""
    
    def read(self) -> str: ...
    def write(self, content: str) -> None: ...
    def search(self, query: str) -> List[str]: ...
    def delete(self, id: str) -> None: ...
    def backup(self) -> None: ...
    def restore(self) -> None: ...
    def compress(self) -> None: ...
    def encrypt(self) -> None: ...

class Logger:
    """Logger only needs write, but must implement everything."""
    
    def read(self) -> str:
        raise NotImplementedError("Logger cannot read")  # ❌ Forced to implement
    
    def write(self, content: str) -> None:
        self._log(content)  # Only method actually used
    
    def search(self, query: str) -> List[str]:
        raise NotImplementedError("Logger cannot search")  # ❌ Forced to implement
    
    # ... Must implement all other methods even though they don't make sense
```

### Application in PrismQ.T.Idea.Inspiration

- **CategoryClassifier**: Only 2 methods (`classify`, `classify_from_metadata`)
- **StoryDetector**: Only 2 methods (`detect`, `detect_from_metadata`)
- **Config**: Only 3 core methods (`get`, `set`, `get_or_prompt`)
- **IdeaInspirationDatabase**: Focused CRUD methods, each with single purpose

All classes follow ISP by providing minimal, focused interfaces.

## 5. Dependency Inversion Principle (DIP)

> **"Depend upon abstractions, not concretions."**

High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions.

### Guidelines

- Depend on interfaces/protocols, not concrete implementations
- Use dependency injection to provide implementations
- High-level business logic should not depend on low-level details
- Abstractions should be stable; implementations can vary

### Good Example

```python
# ✅ GOOD: Depends on abstractions, uses dependency injection

from typing import Protocol

# Define abstractions (protocols)

class CategoryClassifierProtocol(Protocol):
    """Abstract interface for category classification."""
    
    def classify(self, title: str, description: str) -> CategoryResult:
        """Classify content into categories."""
        ...

class StoryDetectorProtocol(Protocol):
    """Abstract interface for story detection."""
    
    def detect(self, title: str, description: str) -> Tuple[bool, float, List[str]]:
        """Detect if content is a story."""
        ...

# High-level class depends on abstractions

class TextClassifier:
    """High-level classification orchestrator."""
    
    def __init__(
        self,
        category_classifier: CategoryClassifierProtocol,
        story_detector: StoryDetectorProtocol
    ):
        """Initialize with injected dependencies (abstractions)."""
        self.category_classifier = category_classifier
        self.story_detector = story_detector
    
    def enrich(self, inspiration: IdeaInspiration) -> ClassificationEnrichment:
        """Enrich content using injected classifiers."""
        category = self.category_classifier.classify(
            inspiration.title,
            inspiration.description
        )
        is_story, confidence, keywords = self.story_detector.detect(
            inspiration.title,
            inspiration.description
        )
        return ClassificationEnrichment(category, is_story, confidence, keywords)

# Concrete implementations

class KeywordCategoryClassifier:
    """Concrete implementation using keyword matching."""
    
    def classify(self, title: str, description: str) -> CategoryResult:
        # Keyword-based classification
        pass

class MLCategoryClassifier:
    """Concrete implementation using ML model."""
    
    def classify(self, title: str, description: str) -> CategoryResult:
        # ML-based classification
        pass

# Usage: Inject dependencies

keyword_classifier = KeywordCategoryClassifier()
story_detector = StoryDetector()

# Can easily swap implementations
enricher = TextClassifier(
    category_classifier=keyword_classifier,  # Or MLCategoryClassifier()
    story_detector=story_detector
)

# Testing: Easy to inject mocks
mock_classifier = Mock(spec=CategoryClassifierProtocol)
mock_detector = Mock(spec=StoryDetectorProtocol)
test_enricher = TextClassifier(mock_classifier, mock_detector)
```

### Database Abstraction Example

```python
# ✅ GOOD: Database abstraction for testability

from typing import Protocol, List, Optional

class DatabaseConnection(Protocol):
    """Abstract database connection interface."""
    
    def execute(self, query: str, params: tuple) -> Any:
        """Execute query with parameters."""
        ...
    
    def commit(self) -> None:
        """Commit transaction."""
        ...
    
    def rollback(self) -> None:
        """Rollback transaction."""
        ...

class IdeaInspirationRepository:
    """Repository pattern with injected database connection."""
    
    def __init__(self, connection: DatabaseConnection):
        """Initialize with database connection abstraction."""
        self.connection = connection
    
    def insert(self, idea: IdeaInspiration) -> Optional[int]:
        """Insert idea into database."""
        query = "INSERT INTO ideas (...) VALUES (?, ?, ?)"
        result = self.connection.execute(query, (idea.title, idea.description, ...))
        self.connection.commit()
        return result.lastrowid
    
    def get_by_id(self, idea_id: int) -> Optional[IdeaInspiration]:
        """Retrieve idea by ID."""
        query = "SELECT * FROM ideas WHERE id = ?"
        result = self.connection.execute(query, (idea_id,))
        return self._map_to_idea(result) if result else None

# Concrete implementations

class SQLiteConnection:
    """SQLite database connection."""
    
    def __init__(self, database_path: str):
        self.conn = sqlite3.connect(database_path)
    
    def execute(self, query: str, params: tuple) -> Any:
        return self.conn.execute(query, params)
    
    def commit(self) -> None:
        self.conn.commit()
    
    def rollback(self) -> None:
        self.conn.rollback()

class MockConnection:
    """Mock connection for testing."""
    
    def __init__(self):
        self.queries = []
    
    def execute(self, query: str, params: tuple) -> Any:
        self.queries.append((query, params))
        return Mock(lastrowid=1)
    
    def commit(self) -> None:
        pass
    
    def rollback(self) -> None:
        pass

# Production usage
sqlite_conn = SQLiteConnection("ideas.db")
repo = IdeaInspirationRepository(sqlite_conn)

# Testing usage
mock_conn = MockConnection()
test_repo = IdeaInspirationRepository(mock_conn)
```

### Bad Example

```python
# ❌ BAD: Depends on concrete implementations, hard to test

class TextClassifier:
    """Tightly coupled to concrete implementations."""
    
    def __init__(self):
        # Direct dependency on concrete classes
        self.category_classifier = KeywordCategoryClassifier()
        self.story_detector = RuleBasedStoryDetector()
        self.database = SQLiteDatabase("prod.db")  # ❌ Hardcoded
    
    def enrich(self, inspiration: IdeaInspiration) -> ClassificationEnrichment:
        # Cannot swap implementations
        # Cannot test without real database
        category = self.category_classifier.classify(...)
        
        # Directly saves to database (mixed responsibilities)
        self.database.save(category)  # ❌ Violates SRP and DIP
        
        return category
```

**Problems**:
- Cannot swap keyword classifier for ML classifier
- Cannot test without real database
- Hard to mock dependencies
- Violates SRP by mixing classification and persistence

### Application in PrismQ.T.Idea.Inspiration

Current implementation:

```python
# Classification/src/classification/text_classifier.py
class TextClassifier:
    def __init__(
        self,
        category_classifier: Optional[CategoryClassifier] = None,
        story_detector: Optional[StoryDetector] = None
    ):
        """Initialize with optional classifier instances."""
        self.category_classifier = category_classifier or CategoryClassifier()
        self.story_detector = story_detector or StoryDetector()
```

**Strengths**:
- Dependencies injected via constructor
- Default implementations for convenience
- Easy to test with mocks

**Recommendation**: Add explicit Protocol types for better documentation and type checking.

## Additional Design Principles

### DRY (Don't Repeat Yourself)

> **"Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."**

- Avoid code duplication
- Extract common logic into reusable functions/classes
- Use inheritance or composition to share behavior
- Centralize configuration and constants

**Example**:
```python
# ✅ GOOD: Centralized configuration
class Config:
    """Single source of truth for configuration."""
    
    def get(self, key: str) -> Optional[str]:
        """Get configuration value."""
        pass

# All modules use Config class
config = Config()
api_key = config.get("YOUTUBE_API_KEY")
```

### KISS (Keep It Simple, Stupid)

> **"Simplicity should be a key goal in design, and unnecessary complexity should be avoided."**

- Favor simple solutions over complex ones
- Write clear, readable code
- Avoid premature optimization
- Use straightforward algorithms when possible

**Example**:
```python
# ✅ GOOD: Simple, clear implementation
def calculate_length_score(text: str) -> float:
    """Score text based on length."""
    length = len(text)
    if length < 50:
        return 0.0
    elif length < 200:
        return 0.5
    else:
        return 1.0
```

### YAGNI (You Aren't Gonna Need It)

> **"Don't implement something until it is necessary."**

- Only implement features you need now
- Avoid speculative features
- Keep code minimal and focused
- Add complexity only when required

**Example**:
```python
# ✅ GOOD: Simple dataclass, no unnecessary features
@dataclass
class CategoryResult:
    """Classification result."""
    category: PrimaryCategory
    confidence: float
    
# Don't add: caching, serialization, validation, etc. until needed
```

### Composition Over Inheritance

> **"Favor object composition over class inheritance."**

- Use composition to build complex behavior from simple parts
- Inheritance creates tight coupling
- Composition provides more flexibility
- Use inheritance only for true "is-a" relationships

**Example**:
```python
# ✅ GOOD: Composition for flexibility
class TextClassifier:
    """Composes classifier and detector."""
    
    def __init__(self, category_classifier: CategoryClassifier, 
                 story_detector: StoryDetector):
        self.category_classifier = category_classifier
        self.story_detector = story_detector

# ❌ BAD: Deep inheritance hierarchy
class TextClassifier(BaseClassifier, StoryDetector, Scorer, Validator):
    # Too many responsibilities, tight coupling
    pass
```

## Testing and SOLID Principles

### How SOLID Enables Testing

1. **SRP**: Each class has one reason to test
2. **OCP**: Can test extensions without modifying existing tests
3. **LSP**: Subtypes can be tested interchangeably
4. **ISP**: Small interfaces are easy to mock
5. **DIP**: Dependencies can be injected as mocks

### Example: Testing with Dependency Injection

```python
# Test using mock dependencies
def test_text_classifier_with_mocks():
    """Test TextClassifier with injected mocks."""
    # Arrange
    mock_classifier = Mock(spec=CategoryClassifierProtocol)
    mock_classifier.classify.return_value = CategoryResult(
        category=PrimaryCategory.STORYTELLING,
        confidence=0.9
    )
    
    mock_detector = Mock(spec=StoryDetectorProtocol)
    mock_detector.detect.return_value = (True, 0.8, ["narrative", "story"])
    
    # Act
    enricher = TextClassifier(mock_classifier, mock_detector)
    result = enricher.enrich(sample_inspiration)
    
    # Assert
    assert result.category == PrimaryCategory.STORYTELLING
    assert result.is_story is True
    mock_classifier.classify.assert_called_once()
    mock_detector.detect.assert_called_once()
```

## Applying SOLID to PrismQ.T.Idea.Inspiration

### Module Guidelines

1. **Sources Module**: Each source (YouTube, Reddit, etc.) should be a separate class with SRP
2. **Classification Module**: Keep classifier, detector, and enricher separate (SRP)
3. **Scoring Module**: Use strategy pattern for different scoring algorithms (OCP)
4. **Model Module**: Keep data model separate from persistence (SRP)
5. **ConfigLoad Module**: Single responsibility for configuration management

### Code Review Checklist

When reviewing code, check for:

- [ ] **SRP**: Does each class have a single, clear responsibility?
- [ ] **OCP**: Can I add new features without modifying existing code?
- [ ] **LSP**: Are subtypes substitutable for their base types?
- [ ] **ISP**: Are interfaces minimal and focused?
- [ ] **DIP**: Do classes depend on abstractions, not concretions?
- [ ] **DRY**: Is there any duplicated code?
- [ ] **KISS**: Is the solution as simple as possible?
- [ ] **YAGNI**: Are we implementing only what's needed?

### Refactoring for SOLID

When refactoring code to follow SOLID:

1. **Identify violations**: Which principles are violated?
2. **Extract classes**: Separate responsibilities into different classes
3. **Define interfaces**: Create protocols for abstraction
4. **Inject dependencies**: Use constructor injection for dependencies
5. **Write tests**: Verify behavior is preserved
6. **Document design**: Explain the SOLID principles applied

## References and Further Reading

- **Books**:
  - "Clean Architecture" by Robert C. Martin
  - "Design Patterns" by Gang of Four
  - "Refactoring" by Martin Fowler

- **Articles**:
  - [SOLID Principles Explained](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
  - [Python Design Patterns](https://python-patterns.guide/)

- **PrismQ Documentation**:
  - [Architecture Documentation](./ARCHITECTURE.md)
  - [SOLID Code Reviews](./code_reviews/)
  - [Contributing Guidelines](./CONTRIBUTING.md)

## Summary

Following SOLID principles leads to:

- ✅ **Maintainable code**: Easy to understand and modify
- ✅ **Testable code**: Easy to write unit tests
- ✅ **Extensible code**: Easy to add new features
- ✅ **Reusable code**: Components can be used in different contexts
- ✅ **Robust code**: Changes in one area don't break others

**Remember**: SOLID principles are guidelines, not rigid rules. Apply them pragmatically based on the specific needs of your code. Sometimes, a simpler solution that bends the rules is better than a complex solution that follows them perfectly.

---

**Last Updated**: 2025-11-14  
**Maintained By**: PrismQ.T.Idea.Inspiration Team
    """Interface for content scoring strategies."""
    
    def calculate_score(self, content: dict) -> float:
        """Calculate score for content."""
        ...

class VideoScoringStrategy:
    """Score video content."""
    
    def calculate_score(self, content: dict) -> float:
        return content.get("views", 0) / 1000

class ArticleScoringStrategy:
    """Score article content."""
    
    def calculate_score(self, content: dict) -> float:
        return content.get("words", 0) / 100

class PodcastScoringStrategy:
    """Score podcast content."""
    
    def calculate_score(self, content: dict) -> float:
        return content.get("duration", 0) / 60

# NEW: Add social media scoring without modifying existing code
class SocialMediaScoringStrategy:
    """Score social media content."""
    
    def calculate_score(self, content: dict) -> float:
        likes = content.get("likes", 0)
        shares = content.get("shares", 0)
        comments = content.get("comments", 0)
        return (likes + shares * 2 + comments * 3) / 1000

class ContentScorer:
    """Calculate scores using injected strategies."""
    
    def __init__(self, strategies: dict[str, ScoringStrategy]):
        self._strategies = strategies
    
    def calculate_score(self, content: dict) -> float:
        content_type = content.get("type")
        strategy = self._strategies.get(content_type)
        
        if strategy:
            return strategy.calculate_score(content)
        return 0.0
    
    def register_strategy(self, content_type: str, strategy: ScoringStrategy) -> None:
        """Register a new scoring strategy (extension point)."""
        self._strategies[content_type] = strategy

# Usage
scorer = ContentScorer({
    "video": VideoScoringStrategy(),
    "article": ArticleScoringStrategy(),
    "podcast": PodcastScoringStrategy()
})

# Extend without modifying ContentScorer
scorer.register_strategy("social", SocialMediaScoringStrategy())
```

### Guidelines
- Use abstractions (interfaces/protocols) instead of concrete implementations
- Design extension points into your classes
- Favor composition and delegation over direct implementation
- Use Strategy Pattern for varying behaviors

---

## Liskov Substitution Principle (LSP)

### Definition

**Subtypes must be substitutable for their base types without altering program correctness.**

If class B is a subtype of class A, you should be able to replace A with B without breaking the functionality. Subclasses should strengthen, not weaken, the base class contract.

### Benefits
- Polymorphism works correctly
- Subclasses behave predictably
- Prevents subtle bugs from inheritance
- Code is more maintainable and reliable

### Example: Violation

```python
# ❌ BAD: Subclass violates base class expectations
class Bird:
    """Base class for birds."""
    
    def fly(self) -> str:
        """All birds can fly."""
        return "Flying"

class Sparrow(Bird):
    """Sparrow can fly."""
    pass  # Works fine

class Penguin(Bird):
    """Penguin cannot fly!"""
    
    def fly(self) -> str:
        """Penguins can't fly - violates LSP."""
        raise NotImplementedError("Penguins cannot fly")

# This breaks when using polymorphism
def make_bird_fly(bird: Bird) -> None:
    print(bird.fly())

sparrow = Sparrow()
make_bird_fly(sparrow)  # ✅ Works

penguin = Penguin()
make_bird_fly(penguin)  # ❌ Raises exception - LSP violated
```

**Problems:**
- Penguin claims to be a Bird but violates the flying contract
- Code that works with Bird breaks with Penguin
- Forces clients to check type before calling methods

### Example: Following LSP

```python
# ✅ GOOD: Design hierarchy to respect capabilities

class Bird:
    """Base class for all birds."""
    
    def eat(self) -> str:
        """All birds can eat."""
        return "Eating"

class FlyingBird(Bird):
    """Birds that can fly."""
    
    def fly(self) -> str:
        """Flying birds can fly."""
        return "Flying"

class Sparrow(FlyingBird):
    """Sparrow can fly."""
    pass

class Penguin(Bird):
    """Penguin cannot fly, but is still a bird."""
    
    def swim(self) -> str:
        """Penguins can swim."""
        return "Swimming"

# Now polymorphism works correctly
def make_bird_eat(bird: Bird) -> None:
    print(bird.eat())

def make_bird_fly(bird: FlyingBird) -> None:
    print(bird.fly())

sparrow = Sparrow()
make_bird_eat(sparrow)  # ✅ Works
make_bird_fly(sparrow)  # ✅ Works

penguin = Penguin()
make_bird_eat(penguin)  # ✅ Works
# make_bird_fly(penguin)  # ❌ Type error - penguin is not FlyingBird
```

### Guidelines
- Subclasses should strengthen, not weaken, preconditions
- Subclasses should strengthen, not weaken, postconditions
- Don't throw unexpected exceptions in subclasses
- Respect the base class contract completely
- If you can't substitute, reconsider the inheritance relationship

---

## Interface Segregation Principle (ISP)

### Definition

**Clients should not be forced to depend on interfaces they don't use.**

Create focused, minimal interfaces rather than large, monolithic ones. Classes should only implement methods they actually need.

### Benefits
- Smaller, more focused interfaces
- Reduces coupling
- Easier to implement
- Changes to one interface don't affect others

### Example: Violation

```python
# ❌ BAD: Fat interface forces implementations to provide unused methods
from typing import Protocol

class DataSource(Protocol):
    """Large interface with many methods."""
    
    def fetch_data(self) -> dict:
        """Fetch data from source."""
        ...
    
    def cache_data(self, data: dict) -> None:
        """Cache data."""
        ...
    
    def validate_data(self, data: dict) -> bool:
        """Validate data."""
        ...
    
    def transform_data(self, data: dict) -> dict:
        """Transform data."""
        ...
    
    def log_access(self) -> None:
        """Log access."""
        ...

class SimpleAPISource:
    """Simple API source - doesn't need caching or transformation."""
    
    def fetch_data(self) -> dict:
        return {"data": "from API"}
    
    def cache_data(self, data: dict) -> None:
        # Forced to implement - not needed
        pass
    
    def validate_data(self, data: dict) -> bool:
        # Forced to implement - not needed
        return True
    
    def transform_data(self, data: dict) -> dict:
        # Forced to implement - not needed
        return data
    
    def log_access(self) -> None:
        # Forced to implement - not needed
        pass
```

**Problems:**
- Simple implementations must provide many unused methods
- Changes to the interface affect all implementations
- Hard to understand which methods are actually used

### Example: Following ISP

```python
# ✅ GOOD: Split into focused interfaces

from typing import Protocol

class Fetchable(Protocol):
    """Minimal interface for data fetching."""
    
    def fetch_data(self) -> dict:
        """Fetch data from source."""
        ...

class Cacheable(Protocol):
    """Minimal interface for caching."""
    
    def cache_data(self, data: dict) -> None:
        """Cache data."""
        ...

class Validatable(Protocol):
    """Minimal interface for validation."""
    
    def validate_data(self, data: dict) -> bool:
        """Validate data."""
        ...

class Transformable(Protocol):
    """Minimal interface for transformation."""
    
    def transform_data(self, data: dict) -> dict:
        """Transform data."""
        ...

class Loggable(Protocol):
    """Minimal interface for logging."""
    
    def log_access(self) -> None:
        """Log access."""
        ...

# Implementations only implement what they need
class SimpleAPISource:
    """Simple API source - only implements fetching."""
    
    def fetch_data(self) -> dict:
        return {"data": "from API"}

class CachedAPISource:
    """API source with caching - implements two interfaces."""
    
    def fetch_data(self) -> dict:
        return {"data": "from API"}
    
    def cache_data(self, data: dict) -> None:
        # Actually uses caching
        pass

class FullFeaturedSource:
    """Source with all features - implements all interfaces."""
    
    def fetch_data(self) -> dict:
        return {"data": "from source"}
    
    def cache_data(self, data: dict) -> None:
        pass
    
    def validate_data(self, data: dict) -> bool:
        return True
    
    def transform_data(self, data: dict) -> dict:
        return data
    
    def log_access(self) -> None:
        pass

# Use only the interfaces you need
def process_fetchable(source: Fetchable) -> dict:
    """Process any fetchable source."""
    return source.fetch_data()

def process_cached_source(source: Fetchable & Cacheable) -> dict:
    """Process sources that support caching."""
    data = source.fetch_data()
    source.cache_data(data)
    return data
```

### Guidelines
- Keep interfaces small and focused (prefer many small interfaces)
- Use Python Protocols for structural typing
- Clients should depend on minimal interfaces
- Combine interfaces when needed (intersection types)

---

## Dependency Inversion Principle (DIP)

### Definition

**Depend on abstractions, not on concrete implementations.**

1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

### Benefits
- Loose coupling between modules
- Easy to swap implementations
- Better testability (can mock dependencies)
- Flexibility and extensibility

### Example: Violation

```python
# ❌ BAD: High-level module depends on low-level concrete class
class MySQLDatabase:
    """Concrete database implementation."""
    
    def save(self, data: dict) -> None:
        # MySQL-specific code
        pass

class IdeaCollector:
    """High-level module that directly depends on MySQL."""
    
    def __init__(self):
        # Hardcoded dependency on concrete class
        self._database = MySQLDatabase()
    
    def collect_and_save(self, idea: dict) -> None:
        # ... collection logic ...
        self._database.save(idea)
```

**Problems:**
- Cannot use a different database without modifying IdeaCollector
- Hard to test (must have MySQL available)
- Tight coupling to MySQL implementation
- Cannot switch databases at runtime

### Example: Following DIP

```python
# ✅ GOOD: Both depend on abstraction

from typing import Protocol

# Abstraction
class DataRepository(Protocol):
    """Abstract interface for data storage."""
    
    def save(self, data: dict) -> None:
        """Save data to repository."""
        ...

# Low-level modules depend on abstraction
class MySQLRepository:
    """MySQL implementation of DataRepository."""
    
    def save(self, data: dict) -> None:
        # MySQL-specific code
        pass

class PostgreSQLRepository:
    """PostgreSQL implementation of DataRepository."""
    
    def save(self, data: dict) -> None:
        # PostgreSQL-specific code
        pass

class FileRepository:
    """File-based implementation of DataRepository."""
    
    def save(self, data: dict) -> None:
        # File I/O code
        pass

# High-level module depends on abstraction
class IdeaCollector:
    """High-level module that depends on abstraction."""
    
    def __init__(self, repository: DataRepository):
        # Dependency injected through constructor
        self._repository = repository
    
    def collect_and_save(self, idea: dict) -> None:
        # ... collection logic ...
        self._repository.save(idea)

# Dependency injection at runtime
mysql_repo = MySQLRepository()
collector = IdeaCollector(mysql_repo)

# Can easily swap implementations
postgres_repo = PostgreSQLRepository()
collector = IdeaCollector(postgres_repo)

# Can use mock for testing
class MockRepository:
    def save(self, data: dict) -> None:
        print(f"Mock save: {data}")

test_collector = IdeaCollector(MockRepository())
```

### Dependency Injection Patterns

#### 1. Constructor Injection (Recommended)
```python
class Service:
    def __init__(self, dependency: Dependency):
        self._dependency = dependency
```

#### 2. Property Injection
```python
class Service:
    def set_dependency(self, dependency: Dependency) -> None:
        self._dependency = dependency
```

#### 3. Method Injection
```python
class Service:
    def process(self, data: dict, dependency: Dependency) -> None:
        dependency.handle(data)
```

### Guidelines
- Define abstractions (Protocols) for dependencies
- Inject dependencies through constructors
- Depend on interfaces, not concrete classes
- Use dependency injection frameworks for complex graphs
- Make dependencies explicit in constructors

---

## Practical Applications in PrismQ

### Application 1: Source Module (SRP + DIP)

```python
from typing import Protocol, List

# Abstraction for DIP
class DataFetcher(Protocol):
    def fetch(self, query: str) -> List[dict]:
        ...

# SRP: Each source has single responsibility
class YouTubeFetcher:
    """Responsible only for YouTube API calls."""
    
    def fetch(self, query: str) -> List[dict]:
        # YouTube API logic
        return [{"source": "youtube", "data": "..."}]

class RedditFetcher:
    """Responsible only for Reddit API calls."""
    
    def fetch(self, query: str) -> List[dict]:
        # Reddit API logic
        return [{"source": "reddit", "data": "..."}]

# High-level orchestrator depends on abstraction (DIP)
class IdeaCollector:
    """Orchestrates idea collection from multiple sources."""
    
    def __init__(self, fetchers: List[DataFetcher]):
        self._fetchers = fetchers
    
    def collect_all(self, query: str) -> List[dict]:
        results = []
        for fetcher in self._fetchers:
            results.extend(fetcher.fetch(query))
        return results
```

### Application 2: Scoring Module (OCP + ISP)

```python
from typing import Protocol

# ISP: Small, focused interfaces
class TitleScorer(Protocol):
    def score_title(self, title: str) -> float:
        ...

class DescriptionScorer(Protocol):
    def score_description(self, description: str) -> float:
        ...

class EngagementScorer(Protocol):
    def score_engagement(self, metrics: dict) -> float:
        ...

# Implementations can choose which interfaces to implement
class BasicScorer:
    """Implements only basic scoring."""
    
    def score_title(self, title: str) -> float:
        return len(title.split()) / 20 * 100

class AdvancedScorer:
    """Implements all scoring interfaces."""
    
    def score_title(self, title: str) -> float:
        return len(title.split()) / 20 * 100
    
    def score_description(self, description: str) -> float:
        return len(description.split()) / 100 * 100
    
    def score_engagement(self, metrics: dict) -> float:
        return metrics.get("engagement", 0)

# OCP: Easy to add new scorers without modifying existing code
class MLScorer:
    """New ML-based scorer - extends without modifying others."""
    
    def score_title(self, title: str) -> float:
        # ML model inference
        return 85.0
```

### Application 3: Classification Module (LSP + Composition)

```python
from typing import Protocol, Optional

# LSP: All classifiers must honor this contract
class Classifier(Protocol):
    def classify(self, text: str) -> str:
        """Must return a valid category string."""
        ...

class CategoryClassifier:
    """Classifies into predefined categories."""
    
    def classify(self, text: str) -> str:
        # Always returns a valid category
        return "Technology"

class MLCategoryClassifier:
    """ML-based classifier - substitutable for CategoryClassifier."""
    
    def classify(self, text: str) -> str:
        # Also always returns a valid category
        # Honors the base contract
        return "Business"

# Composition over inheritance
class EnhancedClassifier:
    """Composed of multiple classifiers."""
    
    def __init__(
        self,
        category_classifier: Classifier,
        sentiment_classifier: Optional[Classifier] = None
    ):
        self._category = category_classifier
        self._sentiment = sentiment_classifier
    
    def classify_with_sentiment(self, text: str) -> dict:
        result = {"category": self._category.classify(text)}
        if self._sentiment:
            result["sentiment"] = self._sentiment.classify(text)
        return result
```

---

## Related Patterns

### Strategy Pattern (OCP + DIP)
- Open/Closed: Add new strategies without modifying context
- Dependency Inversion: Context depends on Strategy abstraction

### Template Method (SRP + LSP)
- Single Responsibility: Base class defines workflow, subclasses handle steps
- Liskov Substitution: Subclasses must honor the template contract

### Composition (SRP + ISP)
- Single Responsibility: Each component has one job
- Interface Segregation: Components implement minimal interfaces

For detailed information on these patterns, see [Strategy Pattern Research](./STRATEGY_PATTERN_RESEARCH.md).

---

## Summary

| Principle | Key Question | Solution Pattern |
|-----------|-------------|------------------|
| **SRP** | Does this class have more than one reason to change? | Extract responsibilities into separate classes |
| **OCP** | Can I add new behavior without modifying existing code? | Use abstractions, Strategy pattern, dependency injection |
| **LSP** | Can I substitute this subclass without breaking functionality? | Design proper hierarchies, honor contracts |
| **ISP** | Am I forced to implement methods I don't need? | Split into smaller, focused interfaces |
| **DIP** | Do I depend on concrete implementations? | Depend on abstractions, inject dependencies |

### Applying SOLID in PrismQ

1. **Keep classes focused** (SRP) - One responsibility per class
2. **Design for extension** (OCP) - Use protocols and strategies
3. **Honor contracts** (LSP) - Subclasses must be substitutable
4. **Use minimal interfaces** (ISP) - Python Protocols are perfect for this
5. **Inject dependencies** (DIP) - Constructor injection with abstractions

Following these principles leads to code that is:
- **Maintainable** - Easy to understand and modify
- **Testable** - Components can be tested in isolation
- **Flexible** - Easy to extend and adapt to new requirements
- **Robust** - Changes in one area don't break others

---

## References

- [SOLID Principles - Wikipedia](https://en.wikipedia.org/wiki/SOLID)
- [Robert C. Martin - Clean Architecture](https://blog.cleancoder.com/)
- [Strategy Pattern Research](./STRATEGY_PATTERN_RESEARCH.md)
- [PrismQ Architecture](./ARCHITECTURE.md)
- [SOLID Review - Core Modules](./code_reviews/SOLID_REVIEW_CORE_MODULES.md)
