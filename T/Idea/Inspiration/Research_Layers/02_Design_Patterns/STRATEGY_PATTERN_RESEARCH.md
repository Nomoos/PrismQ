# Strategy Pattern and Composition-Based Design

## Overview

This document provides comprehensive research on the Strategy Pattern and Composition-Based design principles, with practical applications for the PrismQ.IdeaInspiration project. These patterns are essential for building flexible, maintainable, and extensible layered systems.

## Table of Contents

1. [Strategy Pattern (Composition-Based)](#strategy-pattern-composition-based)
2. [Composition and Shallow Inheritance](#composition-and-shallow-inheritance)
3. [Pattern Comparison](#pattern-comparison)
4. [Practical Applications in PrismQ](#practical-applications-in-prismq)
5. [Best Practices](#best-practices)
6. [References](#references)

---

## Strategy Pattern (Composition-Based)

### Definition

The Strategy pattern encapsulates interchangeable behaviors (algorithms or tactics) into separate classes, which are then composed with the context object. Instead of using inheritance to override parts of an algorithm, the context class holds a reference to a strategy interface and delegates work to it.

**Key Principle**: Favor composition over inheritance by delegating behavior to strategy objects.

### When to Use

Use the Strategy pattern when:

1. **Runtime Behavior Changes**: Variations in behavior need to be selected or changed at runtime
2. **Independent Variations**: A module has multiple aspects that can vary independently
3. **Avoiding Subclass Explosion**: Multiple combinations of behaviors would create too many subclasses
4. **Replacing Conditionals**: Complex conditional code switching between behaviors can be replaced by polymorphism

### Common Use Cases in Layered Systems

#### Multi-Layer Scraper Example

Instead of creating subclasses for every combination:
- ❌ `YouTubeDBScraper`, `YouTubeFileScraper`, `TikTokDBScraper`, `TikTokFileScraper`...
- ✅ One scraper class that composes strategies:

```python
from typing import Protocol
from abc import abstractmethod

# Strategy Interfaces
class ExtractionStrategy(Protocol):
    """Strategy for extracting data from different sources."""
    
    @abstractmethod
    def extract(self, source_url: str) -> dict:
        """Extract data from the given source."""
        pass

class StorageStrategy(Protocol):
    """Strategy for storing extracted data."""
    
    @abstractmethod
    def store(self, data: dict) -> None:
        """Store the extracted data."""
        pass

# Concrete Extraction Strategies
class HTMLParsingStrategy:
    """Extract data by parsing HTML."""
    
    def extract(self, source_url: str) -> dict:
        # Parse HTML and extract data
        return {"type": "html", "data": "..."}

class APIFetchingStrategy:
    """Extract data by calling an API."""
    
    def extract(self, source_url: str) -> dict:
        # Call API and get structured data
        return {"type": "api", "data": "..."}

# Concrete Storage Strategies
class DatabaseStorageStrategy:
    """Store data in a database."""
    
    def store(self, data: dict) -> None:
        # Save to database
        pass

class FileStorageStrategy:
    """Store data in a file."""
    
    def store(self, data: dict) -> None:
        # Save to file
        pass

# Context Class - The Scraper
class ContentScraper:
    """
    Scraper that uses composition to handle different extraction
    and storage methods without subclassing.
    """
    
    def __init__(
        self,
        extraction_strategy: ExtractionStrategy,
        storage_strategy: StorageStrategy
    ):
        self._extraction_strategy = extraction_strategy
        self._storage_strategy = storage_strategy
    
    def scrape(self, source_url: str) -> None:
        """Execute the scraping workflow using injected strategies."""
        # Delegate extraction to strategy
        data = self._extraction_strategy.extract(source_url)
        
        # Delegate storage to strategy
        self._storage_strategy.store(data)
    
    # Allow runtime strategy changes
    def set_extraction_strategy(self, strategy: ExtractionStrategy) -> None:
        self._extraction_strategy = strategy
    
    def set_storage_strategy(self, strategy: StorageStrategy) -> None:
        self._storage_strategy = strategy

# Usage Examples
if __name__ == "__main__":
    # Create scraper with API extraction and DB storage
    scraper = ContentScraper(
        extraction_strategy=APIFetchingStrategy(),
        storage_strategy=DatabaseStorageStrategy()
    )
    scraper.scrape("https://example.com/content")
    
    # Change to file storage at runtime
    scraper.set_storage_strategy(FileStorageStrategy())
    scraper.scrape("https://example.com/content")
    
    # Create different scraper with HTML parsing and file storage
    html_scraper = ContentScraper(
        extraction_strategy=HTMLParsingStrategy(),
        storage_strategy=FileStorageStrategy()
    )
    html_scraper.scrape("https://example.com/page")
```

### Benefits

1. **Flexibility**: Swap algorithms without changing the context's code (Open/Closed Principle)
2. **Separation of Concerns**: Complex logic is isolated in its own class, easier to reason about and test
3. **Reusability**: Mix and match strategies, achieving reuse by combining simple pieces
4. **Reduced Inheritance Explosion**: One context class instead of many subclasses for every combination
5. **Runtime Configuration**: Strategies can be changed at runtime based on conditions or user input
6. **Testability**: Each strategy can be tested independently; context can be tested with mock strategies

### Drawbacks

1. **Increased Complexity**: More classes and interfaces to design and maintain
2. **Wiring Overhead**: Strategies must be wired to context (often via dependency injection or factories)
3. **Client Awareness**: Clients must understand strategy differences to choose the correct one
4. **Potential Overkill**: For only 2-3 variations, simpler conditionals or subclasses may suffice

### Real-World Example: Data Import Module

```python
from typing import Protocol, List
from abc import abstractmethod

# Strategy Interface
class ReadStrategy(Protocol):
    """Interface for reading different file formats."""
    
    @abstractmethod
    def read(self, file_path: str) -> List[dict]:
        """Read data from file and return as list of records."""
        pass

# Concrete Strategies
class XMLReadStrategy:
    """Read data from XML files."""
    
    def read(self, file_path: str) -> List[dict]:
        # Parse XML and return data
        return [{"format": "xml", "data": "..."}]

class CSVReadStrategy:
    """Read data from CSV files."""
    
    def read(self, file_path: str) -> List[dict]:
        # Parse CSV and return data
        return [{"format": "csv", "data": "..."}]

class JSONReadStrategy:
    """Read data from JSON files."""
    
    def read(self, file_path: str) -> List[dict]:
        # Parse JSON and return data
        return [{"format": "json", "data": "..."}]

# Context - Import Workflow
class DataImporter:
    """
    Import workflow that delegates format handling to strategies.
    Input format handling is independent from validation or output.
    """
    
    def __init__(self, read_strategy: ReadStrategy):
        self._read_strategy = read_strategy
    
    def import_data(self, file_path: str) -> List[dict]:
        """Import data using the configured read strategy."""
        # Delegate reading to strategy
        data = self._read_strategy.read(file_path)
        
        # Common validation logic (same for all formats)
        validated_data = self._validate(data)
        
        return validated_data
    
    def _validate(self, data: List[dict]) -> List[dict]:
        """Validate imported data (format-independent)."""
        # Validation logic here
        return data

# Adding a new format is simple - just implement a new strategy
class ParquetReadStrategy:
    """Read data from Parquet files."""
    
    def read(self, file_path: str) -> List[dict]:
        # Parse Parquet and return data
        return [{"format": "parquet", "data": "..."}]

# Usage
xml_importer = DataImporter(XMLReadStrategy())
csv_importer = DataImporter(CSVReadStrategy())
json_importer = DataImporter(JSONReadStrategy())

# New format - no changes to existing code
parquet_importer = DataImporter(ParquetReadStrategy())
```

---

## Composition and Shallow Inheritance

### Favor Composition Over Inheritance

**Principle**: Build classes by combining or aggregating simpler components, rather than relying exclusively on deep inheritance. Use "has-a" relationships to share functionality instead of stretching "is-a" relationships too far.

### When to Use Composition

Prefer composition when:

1. **Clean Separation**: A behavior can be cleanly separated as an independent component
2. **Deep Hierarchies**: An inheritance hierarchy is getting too deep or unwieldy
3. **Optional Features**: Not every class needs a feature; compose it into those that do
4. **Cross-Cutting Concerns**: Multiple unrelated classes need the same functionality

### Benefits of Composition

1. **Flexibility**: Change or replace components without affecting others
2. **Loose Coupling**: Components can be reused across different parts of the system
3. **Better Testability**: Mock or stub out components easily
4. **Simpler Classes**: Each piece is simpler and more maintainable
5. **SOLID Adherence**: Better alignment with Single Responsibility and Open/Closed principles

### Drawbacks of Composition

1. **More Moving Parts**: More objects and relationships to understand
2. **Interface Design**: Need well-defined interfaces between components
3. **Slight Performance Overhead**: More objects and indirection (usually negligible)

### Avoiding Deep Inheritance Pitfalls

**Problems with Deep Inheritance:**
- **Fragile Base Class Problem**: Small base changes ripple through all subclasses
- **Method Override Confusion**: Difficult to track which methods are overridden where
- **Complex Program Flow**: Hard to reason about behavior across multiple levels
- **Tight Coupling**: Changes to base classes affect all descendants

**Solution: Keep Inheritance Shallow**

```python
# ❌ BAD: Deep inheritance hierarchy (5 levels)
class Idea:
    pass

class VideoIdea(Idea):
    pass

class YouTubeIdea(VideoIdea):
    pass

class YouTubeShortIdea(YouTubeIdea):
    pass

class YouTubeTrendingShortIdea(YouTubeShortIdea):
    pass

# ✅ GOOD: Shallow inheritance with composition (2 levels)
class Idea:
    """Base idea class."""
    pass

class VideoIdea(Idea):
    """Video-specific idea."""
    
    def __init__(
        self,
        platform_handler: PlatformHandler,  # Composed
        content_type_handler: ContentTypeHandler,  # Composed
        source_handler: SourceHandler  # Composed
    ):
        self._platform = platform_handler
        self._content_type = content_type_handler
        self._source = source_handler

# Helper components (composed, not inherited)
class PlatformHandler:
    """Handle platform-specific logic."""
    pass

class YouTubePlatformHandler(PlatformHandler):
    """Handle YouTube-specific logic."""
    pass

class ContentTypeHandler:
    """Handle content type logic."""
    pass

class ShortContentHandler(ContentTypeHandler):
    """Handle short-form content."""
    pass

class SourceHandler:
    """Handle source-specific logic."""
    pass

class TrendingSourceHandler(SourceHandler):
    """Handle trending source logic."""
    pass
```

### Practical Example: Caching Feature

```python
from typing import Protocol, Optional, Any

# Instead of inheritance, use composition
class CacheHelper:
    """Helper component for caching functionality."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: dict = {}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Store value in cache."""
        self._cache[key] = value
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

# ❌ BAD: Forcing caching via inheritance
class CacheableYouTubeSource(YouTubeSource):
    """Adds caching to YouTube source via inheritance."""
    pass

# ✅ GOOD: Composing caching functionality
class YouTubeSource:
    """YouTube source with optional caching via composition."""
    
    def __init__(self, cache: Optional[CacheHelper] = None):
        # Cache is optional - only use if provided
        self._cache = cache
    
    def fetch_data(self, url: str) -> dict:
        """Fetch data with optional caching."""
        # Check cache if available
        if self._cache:
            cached = self._cache.get(url)
            if cached:
                return cached
        
        # Fetch from source
        data = self._fetch_from_api(url)
        
        # Cache if cache is available
        if self._cache:
            self._cache.set(url, data)
        
        return data
    
    def _fetch_from_api(self, url: str) -> dict:
        """Fetch from API."""
        return {"url": url, "data": "..."}

# Usage
# Source without caching
simple_source = YouTubeSource()

# Source with caching
cached_source = YouTubeSource(cache=CacheHelper(ttl_seconds=1800))

# Same CacheHelper can be used by other sources
vimeo_source = VimeoSource(cache=CacheHelper(ttl_seconds=1800))
```

### Guidelines for Shallow Inheritance

1. **Two to Three Levels Maximum**: Keep inheritance hierarchies to 2-3 levels at most
2. **Critically Justify Each Level**: Each additional level should solve a clear problem
3. **Look for Extraction Opportunities**: If subclasses only tweak small behaviors, extract to Strategy or helper
4. **Use Interfaces/Protocols**: Define contracts without forcing inheritance
5. **Review Regularly**: Periodically review class hierarchies for refactoring opportunities

---

## Pattern Comparison

### Template Method vs Strategy vs Composition

| Aspect | Template Method | Strategy Pattern | Composition |
|--------|----------------|------------------|-------------|
| **Mechanism** | Base class defines algorithm skeleton; subclasses override specific steps (inheritance) | Context holds a strategy object; behavior is delegated to it (composition) | Build classes by containing other components or using mixins, rather than deep inheritance |
| **Use When** | • Common process with variant steps per module<br>• Want to enforce consistent workflow across all subclasses | • Need to swap or vary behavior at runtime<br>• Avoid combinatorial subclasses for independent variations | • Behavior can be cleanly separated as independent component<br>• Inheritance hierarchy is getting too deep<br>• Optional features not needed by all classes |
| **Pros** | • Eliminates duplicate code by reusing base algorithm<br>• Subclasses focus only on their unique logic<br>• Ensures uniform sequence (easy to follow one template) | • Flexible: can change behavior without modifying context (Open/Closed Principle)<br>• Encourages composition and separation of concerns<br>• Reduces subclass explosion | • Flexible and loosely coupled<br>• Components can be reused across system<br>• Better testability<br>• Simpler, more maintainable classes |
| **Cons** | • Rigid: changing algorithm affects all subclasses<br>• Inheritance coupling (less flexible at runtime)<br>• Can lead to deep hierarchies if overused | • More classes and interfaces to manage<br>• Client must select or be aware of appropriate strategy<br>• Slight overhead in wiring strategies | • More moving parts to understand<br>• Need well-defined interfaces between components<br>• Slight performance overhead (usually negligible) |
| **Coupling** | Tight coupling to base class | Loose coupling via interface | Very loose coupling |
| **Runtime Flexibility** | Low (behavior fixed at compile time) | High (strategies can be swapped at runtime) | High (components can be replaced) |
| **Testing** | Moderate (must test with actual subclasses) | Excellent (can mock strategies easily) | Excellent (can mock components easily) |

### When to Choose Each Pattern

#### Choose Template Method When:
- You have a **well-defined, stable algorithm** with varying steps
- All implementations **follow the same sequence**
- You want to **enforce a workflow** across all subclasses
- The variations are **simple overrides** of specific methods
- Runtime flexibility is **not required**

**Example**: Processing pipeline where all steps must occur in order:
```python
class DataProcessor:
    """Template method for data processing."""
    
    def process(self, data: Any) -> Any:
        """Template method defining the processing workflow."""
        validated = self.validate(data)
        transformed = self.transform(validated)
        result = self.store(transformed)
        return result
    
    def validate(self, data: Any) -> Any:
        """Validate data (must be overridden)."""
        raise NotImplementedError
    
    def transform(self, data: Any) -> Any:
        """Transform data (must be overridden)."""
        raise NotImplementedError
    
    def store(self, data: Any) -> Any:
        """Store data (can be overridden)."""
        # Default implementation
        return data
```

#### Choose Strategy Pattern When:
- You need **runtime behavior changes**
- Multiple **independent aspects** vary (avoid combinatorial subclasses)
- You want to **replace conditional logic** with polymorphism
- Behaviors should be **easily swappable**
- You need **better testability** with mock strategies

**Example**: Different sorting algorithms that can be selected at runtime:
```python
class Sorter:
    """Context that uses different sorting strategies."""
    
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy
    
    def sort(self, data: List[int]) -> List[int]:
        return self._strategy.sort(data)
    
    def set_strategy(self, strategy: SortStrategy) -> None:
        """Change sorting strategy at runtime."""
        self._strategy = strategy
```

#### Choose Composition When:
- You want to **avoid deep inheritance**
- Features are **optional** (not all classes need them)
- The same functionality is needed **across unrelated classes**
- You want **maximum flexibility** and **loose coupling**
- **Testability** is a priority

**Example**: Adding logging, caching, and metrics to various classes:
```python
class YouTubeSource:
    """Source with composed helpers for optional features."""
    
    def __init__(
        self,
        logger: Optional[Logger] = None,
        cache: Optional[CacheHelper] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        self._logger = logger
        self._cache = cache
        self._metrics = metrics
```

### Combining Patterns

These patterns are not mutually exclusive. You can combine them:

1. **Template Method + Strategy**: Use Template Method for the high-level algorithm, but delegate specific steps to Strategy objects
2. **Template Method + Composition**: Use Template Method for the workflow, but compose helper objects for optional features
3. **Strategy + Composition**: Strategies themselves can be composed of multiple smaller components

**Example: Combined Approach**
```python
class DataPipeline:
    """
    Template Method for workflow + Strategy for varying behaviors + 
    Composition for optional features.
    """
    
    def __init__(
        self,
        extraction_strategy: ExtractionStrategy,
        transformation_strategy: TransformationStrategy,
        logger: Optional[Logger] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        # Strategies for varying behaviors
        self._extraction = extraction_strategy
        self._transformation = transformation_strategy
        # Composed helpers for optional features
        self._logger = logger
        self._metrics = metrics
    
    def execute(self, source: str) -> dict:
        """Template method defining the workflow."""
        # Step 1: Extract (delegated to strategy)
        data = self._extract(source)
        
        # Step 2: Validate (fixed logic)
        validated = self._validate(data)
        
        # Step 3: Transform (delegated to strategy)
        transformed = self._transform(validated)
        
        # Step 4: Store (fixed logic)
        result = self._store(transformed)
        
        return result
    
    def _extract(self, source: str) -> dict:
        """Extract data using strategy."""
        if self._logger:
            self._logger.info(f"Extracting from {source}")
        
        data = self._extraction.extract(source)
        
        if self._metrics:
            self._metrics.increment("extractions")
        
        return data
    
    def _validate(self, data: dict) -> dict:
        """Fixed validation logic."""
        # Common validation
        return data
    
    def _transform(self, data: dict) -> dict:
        """Transform data using strategy."""
        if self._logger:
            self._logger.info("Transforming data")
        
        transformed = self._transformation.transform(data)
        
        if self._metrics:
            self._metrics.increment("transformations")
        
        return transformed
    
    def _store(self, data: dict) -> dict:
        """Fixed storage logic."""
        # Common storage
        return data
```

---

## Practical Applications in PrismQ

### Application 1: Source Data Extraction

The PrismQ.IdeaInspiration project has multiple source integrations (YouTube, TikTok, Reddit, etc.). Using Strategy Pattern:

```python
from typing import Protocol, List
from dataclasses import dataclass

@dataclass
class IdeaInspiration:
    """Core data model."""
    title: str
    description: str
    source: str
    url: str
    metadata: dict

# Strategy Interface
class SourceStrategy(Protocol):
    """Interface for different source platforms."""
    
    def fetch_ideas(self, query: str, limit: int = 10) -> List[IdeaInspiration]:
        """Fetch ideas from the source."""
        pass

# Concrete Strategies
class YouTubeSourceStrategy:
    """Fetch ideas from YouTube."""
    
    def fetch_ideas(self, query: str, limit: int = 10) -> List[IdeaInspiration]:
        # YouTube API logic
        return [
            IdeaInspiration(
                title="Video Title",
                description="Description",
                source="YouTube",
                url="https://youtube.com/...",
                metadata={"views": 1000}
            )
        ]

class RedditSourceStrategy:
    """Fetch ideas from Reddit."""
    
    def fetch_ideas(self, query: str, limit: int = 10) -> List[IdeaInspiration]:
        # Reddit API logic
        return [
            IdeaInspiration(
                title="Post Title",
                description="Post content",
                source="Reddit",
                url="https://reddit.com/...",
                metadata={"upvotes": 500}
            )
        ]

class TikTokSourceStrategy:
    """Fetch ideas from TikTok."""
    
    def fetch_ideas(self, query: str, limit: int = 10) -> List[IdeaInspiration]:
        # TikTok API logic
        return [
            IdeaInspiration(
                title="TikTok Video",
                description="Video description",
                source="TikTok",
                url="https://tiktok.com/...",
                metadata={"likes": 2000}
            )
        ]

# Context - Idea Collector
class IdeaCollector:
    """Collect ideas using different source strategies."""
    
    def __init__(self, strategies: List[SourceStrategy]):
        self._strategies = strategies
    
    def collect_all(self, query: str, limit_per_source: int = 10) -> List[IdeaInspiration]:
        """Collect ideas from all configured sources."""
        all_ideas = []
        for strategy in self._strategies:
            ideas = strategy.fetch_ideas(query, limit_per_source)
            all_ideas.extend(ideas)
        return all_ideas
    
    def add_strategy(self, strategy: SourceStrategy) -> None:
        """Add a new source strategy at runtime."""
        self._strategies.append(strategy)

# Usage
collector = IdeaCollector([
    YouTubeSourceStrategy(),
    RedditSourceStrategy(),
    TikTokSourceStrategy()
])

ideas = collector.collect_all("AI content ideas")

# Add a new source at runtime
collector.add_strategy(TwitterSourceStrategy())
```

### Application 2: Scoring Strategies

The Scoring module can use different scoring algorithms based on content type:

```python
from typing import Protocol

class ScoringStrategy(Protocol):
    """Interface for different scoring algorithms."""
    
    def calculate_score(self, idea: IdeaInspiration) -> float:
        """Calculate a score for the idea."""
        pass

class EngagementScoringStrategy:
    """Score based on engagement metrics."""
    
    def calculate_score(self, idea: IdeaInspiration) -> float:
        views = idea.metadata.get("views", 0)
        likes = idea.metadata.get("likes", 0)
        comments = idea.metadata.get("comments", 0)
        
        # Weighted scoring
        score = (views * 0.3 + likes * 0.5 + comments * 0.2) / 1000
        return min(score, 100.0)

class QualityScoringStrategy:
    """Score based on content quality indicators."""
    
    def calculate_score(self, idea: IdeaInspiration) -> float:
        # Analyze title, description quality
        title_score = len(idea.title.split()) / 20 * 50  # Word count
        desc_score = len(idea.description.split()) / 100 * 50  # Word count
        
        return min(title_score + desc_score, 100.0)

class HybridScoringStrategy:
    """Combine multiple scoring strategies."""
    
    def __init__(
        self,
        engagement_weight: float = 0.6,
        quality_weight: float = 0.4
    ):
        self._engagement_strategy = EngagementScoringStrategy()
        self._quality_strategy = QualityScoringStrategy()
        self._engagement_weight = engagement_weight
        self._quality_weight = quality_weight
    
    def calculate_score(self, idea: IdeaInspiration) -> float:
        engagement_score = self._engagement_strategy.calculate_score(idea)
        quality_score = self._quality_strategy.calculate_score(idea)
        
        return (
            engagement_score * self._engagement_weight +
            quality_score * self._quality_weight
        )

# Context
class IdeaScorer:
    """Score ideas using a configured strategy."""
    
    def __init__(self, strategy: ScoringStrategy):
        self._strategy = strategy
    
    def score(self, idea: IdeaInspiration) -> float:
        return self._strategy.calculate_score(idea)
    
    def set_strategy(self, strategy: ScoringStrategy) -> None:
        self._strategy = strategy

# Usage
scorer = IdeaScorer(EngagementScoringStrategy())
score1 = scorer.score(idea)

# Change strategy at runtime
scorer.set_strategy(HybridScoringStrategy())
score2 = scorer.score(idea)
```

### Application 3: Classification with Composed Helpers

The Classification module can use composition for optional features:

```python
from typing import Optional, List

class CategoryPredictor:
    """Helper component for ML-based category prediction."""
    
    def predict(self, text: str) -> str:
        # ML model prediction
        return "Technology"

class StoryDetector:
    """Helper component for story potential detection."""
    
    def has_story_potential(self, idea: IdeaInspiration) -> bool:
        # Analyze if idea has story elements
        return "story" in idea.description.lower()

class SentimentAnalyzer:
    """Helper component for sentiment analysis."""
    
    def analyze(self, text: str) -> str:
        # Sentiment analysis
        return "positive"

# Shallow inheritance with composition
class IdeaClassifier:
    """
    Classify ideas using composed helper components.
    Features are optional and can be mixed and matched.
    """
    
    def __init__(
        self,
        category_predictor: Optional[CategoryPredictor] = None,
        story_detector: Optional[StoryDetector] = None,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None
    ):
        # Compose helpers - all optional
        self._category_predictor = category_predictor
        self._story_detector = story_detector
        self._sentiment_analyzer = sentiment_analyzer
    
    def classify(self, idea: IdeaInspiration) -> dict:
        """Classify idea using available helpers."""
        result = {"idea": idea.title}
        
        # Use category predictor if available
        if self._category_predictor:
            category = self._category_predictor.predict(
                f"{idea.title} {idea.description}"
            )
            result["category"] = category
        
        # Use story detector if available
        if self._story_detector:
            has_story = self._story_detector.has_story_potential(idea)
            result["has_story"] = has_story
        
        # Use sentiment analyzer if available
        if self._sentiment_analyzer:
            sentiment = self._sentiment_analyzer.analyze(idea.description)
            result["sentiment"] = sentiment
        
        return result

# Usage - different configurations
# Minimal classifier (no helpers)
basic_classifier = IdeaClassifier()

# With category prediction only
category_classifier = IdeaClassifier(
    category_predictor=CategoryPredictor()
)

# Full-featured classifier
full_classifier = IdeaClassifier(
    category_predictor=CategoryPredictor(),
    story_detector=StoryDetector(),
    sentiment_analyzer=SentimentAnalyzer()
)
```

---

## Best Practices

### 1. Start Simple, Add Complexity as Needed

Don't over-engineer. Start with the simplest solution and refactor to patterns when complexity emerges.

```python
# Start simple
class YouTubeSource:
    def fetch(self):
        return self._fetch_from_api()

# Refactor to Strategy when you need multiple sources
class SourceCollector:
    def __init__(self, strategy: SourceStrategy):
        self._strategy = strategy
```

### 2. Use Protocols for Python Strategy Interfaces

Python's Protocol (from `typing`) provides structural typing without forcing inheritance:

```python
from typing import Protocol

class Strategy(Protocol):
    """Strategy interface using Protocol."""
    
    def execute(self) -> str:
        """Execute the strategy."""
        ...

# Implementations don't need to explicitly inherit
class ConcreteStrategy:
    def execute(self) -> str:
        return "executed"

# This works due to structural typing
def use_strategy(strategy: Strategy) -> str:
    return strategy.execute()

use_strategy(ConcreteStrategy())  # ✅ Works
```

### 3. Inject Dependencies Through Constructor

Use constructor injection for strategies and composed components:

```python
class Context:
    def __init__(self, strategy: Strategy, helper: Helper):
        self._strategy = strategy
        self._helper = helper
```

### 4. Provide Default Strategies/Behaviors

Make common use cases easy with sensible defaults:

```python
class Processor:
    def __init__(
        self,
        strategy: Optional[Strategy] = None,
        cache: Optional[CacheHelper] = None
    ):
        self._strategy = strategy or DefaultStrategy()
        self._cache = cache  # Optional, no default
```

### 5. Document Strategy Differences

Help clients understand when to use which strategy:

```python
class FastStrategy:
    """
    Fast but less accurate strategy.
    Use for: Real-time processing, large datasets.
    Trade-off: Lower precision for speed.
    """
    pass

class AccurateStrategy:
    """
    Slower but more accurate strategy.
    Use for: Critical decisions, small datasets.
    Trade-off: Higher precision but slower.
    """
    pass
```

### 6. Keep Inheritance Shallow (Max 2-3 Levels)

```python
# ✅ GOOD: 2 levels
class Base:
    pass

class Derived(Base):
    pass

# ⚠️ ACCEPTABLE: 3 levels (max)
class Base:
    pass

class Middle(Base):
    pass

class Derived(Middle):
    pass

# ❌ BAD: 4+ levels - refactor to composition
```

### 7. Test Strategies Independently

Each strategy should have its own unit tests:

```python
def test_fast_strategy():
    strategy = FastStrategy()
    result = strategy.execute()
    assert result == expected_result

def test_accurate_strategy():
    strategy = AccurateStrategy()
    result = strategy.execute()
    assert result == expected_result
```

### 8. Use Factory Pattern for Strategy Creation

Simplify strategy selection with a factory:

```python
class StrategyFactory:
    """Factory for creating appropriate strategies."""
    
    @staticmethod
    def create(strategy_type: str) -> Strategy:
        if strategy_type == "fast":
            return FastStrategy()
        elif strategy_type == "accurate":
            return AccurateStrategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy_type}")

# Usage
strategy = StrategyFactory.create("fast")
context = Context(strategy)
```

---

## References

### Official Documentation
- [Refactoring.Guru - Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Refactoring.Guru - Composition over Inheritance](https://refactoring.guru/design-patterns/strategy)

### Articles
- [Medium - Favor Composition Over Inheritance](https://medium.com/)
- [Software Engineering Stack Exchange - Strategy Pattern Discussion](https://softwareengineering.stackexchange.com/)

### Related PrismQ Documentation
- [SOLID Principles](./SOLID_PRINCIPLES.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [SOLID Review - Core Modules](./code_reviews/SOLID_REVIEW_CORE_MODULES.md)

### Python Resources
- [Python Type Hints - Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Python Abstract Base Classes](https://docs.python.org/3/library/abc.html)

---

## Conclusion

The Strategy Pattern and Composition-Based design are powerful tools for building flexible, maintainable systems:

- **Use Strategy Pattern** when you need runtime behavior changes and want to avoid subclass explosion
- **Use Composition** to keep inheritance shallow and add optional features without forcing them on all classes
- **Combine Patterns** strategically - Template Method for stable workflows, Strategy for varying behaviors, Composition for optional features
- **Keep Inheritance Shallow** (2-3 levels max) and extract varying behaviors to strategies or composed helpers
- **Follow SOLID Principles** - especially Open/Closed (Strategy) and Dependency Inversion (both)

These patterns are already in use within PrismQ (see SOLID reviews), and this document provides a comprehensive reference for applying them consistently across the project.
