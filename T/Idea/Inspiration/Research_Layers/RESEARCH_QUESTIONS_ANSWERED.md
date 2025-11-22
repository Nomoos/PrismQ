# Research Questions - Comprehensive Answers

**Document Created**: 2025-11-14  
**Purpose**: Address key research questions about Research_Layers organization and best practices

---

## 🎯 Quick Summary

This document answers the key research questions:
1. ✅ Python examples added throughout Research_Layers
2. ✅ Virtual environment strategy for layers with different dependencies
3. ✅ Layer integration patterns and protocols
4. ✅ Design patterns applicable to this project
5. ✅ Concerns and risk mitigation strategies
6. ✅ Language considerations (English/Czech)
7. ✅ Best practices compilation
8. ✅ Clean code and PEP standards guide

---

## 1. Python Examples Throughout Research_Layers

### Implementation Status

All major sections now include practical Python examples:

#### **01_Architecture** - Layer Examples
- `examples/layer_separation.py` - Shows proper layer boundaries
- `examples/dependency_flow.py` - Demonstrates dependency direction
- `examples/layer_communication.py` - Protocol-based layer interaction

#### **02_Design_Patterns** - Pattern Implementations
- `examples/solid_single_responsibility.py` - SRP in practice
- `examples/solid_open_closed.py` - OCP with abstractions
- `examples/solid_liskov_substitution.py` - LSP compliance
- `examples/solid_interface_segregation.py` - ISP with Protocols
- `examples/solid_dependency_inversion.py` - DIP with dependency injection
- `examples/design_patterns.py` - Strategy, Factory, Observer patterns

#### **03_Testing** - Testing Patterns
- `examples/unit_testing.py` - Pure unit tests
- `examples/integration_testing.py` - Layer integration tests
- `examples/mocking_examples.py` - Proper mocking patterns
- `examples/test_fixtures.py` - Reusable test fixtures

#### **04_WorkerHost** - Worker Examples
- `examples/worker_implementation.py` - Complete worker
- `examples/worker_testing.py` - Worker test patterns

#### **05_Templates** - Ready-to-Use Templates
- Already contains excellent examples (maintained)

---

## 2. Virtual Environments for Different Layers

### Strategy: Layer-Specific Virtual Environments

Each layer can have its own virtual environment with specific dependencies:

```
PrismQ.T.Idea.Inspiration/
├── Source/
│   ├── Audio/
│   │   ├── venv/              # Audio-specific dependencies
│   │   ├── requirements.txt   # pydub, spotify-api, etc.
│   │   └── pyproject.toml
│   ├── Video/
│   │   ├── venv/              # Video-specific dependencies
│   │   ├── requirements.txt   # yt-dlp, opencv, etc.
│   │   └── pyproject.toml
│   └── TaskManager/
│       ├── venv/              # API client dependencies
│       └── requirements.txt   # requests, httpx, etc.
├── Classification/
│   ├── venv/                  # NLP dependencies
│   └── requirements.txt       # transformers, spacy, etc.
└── Model/
    ├── venv/                  # Minimal dependencies
    └── requirements.txt       # dataclasses-json, pydantic
```

### Setup Script Example

```bash
# setup_environments.sh
#!/bin/bash

# Function to setup venv for a module
setup_module_venv() {
    local module_path=$1
    echo "Setting up venv for $module_path"
    
    cd "$module_path"
    py -3.10 -m venv venv
    
    # Activate and install dependencies
    source venv/Scripts/activate  # Windows: venv\Scripts\activate
    pip install --upgrade pip
    pip install -e .
    deactivate
}

# Setup each layer
setup_module_venv "Source/Audio"
setup_module_venv "Source/Video/YouTube"
setup_module_venv "Classification"
setup_module_venv "Model"
```

### Why Layer-Specific Virtual Environments?

**Advantages:**
- ✅ **Dependency Isolation**: Prevents conflicts between layer dependencies
- ✅ **Development Speed**: Faster installs for single-layer development
- ✅ **Deployment Flexibility**: Can deploy layers independently
- ✅ **Version Control**: Different layers can use different library versions
- ✅ **Testing Isolation**: Test one layer without others' dependencies

**Considerations:**
- ⚠️ **Disk Space**: Multiple venvs consume more space (manageable)
- ⚠️ **Setup Complexity**: Requires managing multiple environments
- ⚠️ **IDE Configuration**: Need to configure IDE for each venv

### Dependency Management Best Practices

```python
# pyproject.toml for each module
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "prismq-ideainspiration-audio"
version = "0.1.0"
requires-python = ">=3.10,<3.11"

# Core dependencies only
dependencies = [
    "pydantic>=2.0",
    "requests>=2.31",
]

# Optional dependencies for dev/test
[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "black>=23.0",
    "mypy>=1.5",
]
```

---

## 3. Layer Integration Patterns

### Integration Strategy: Protocol-Based Boundaries

Use Python Protocols (PEP 544) to define contracts between layers:

```python
from typing import Protocol, List
from dataclasses import dataclass

# Domain model (Model layer)
@dataclass
class IdeaInspiration:
    id: str
    title: str
    source: str

# Protocol defines contract (no implementation)
class IdeaRepository(Protocol):
    """Repository contract for persistence layer."""
    
    def save(self, idea: IdeaInspiration) -> str: ...
    def get_by_id(self, id: str) -> IdeaInspiration: ...
    def list_all(self) -> List[IdeaInspiration]: ...

# Higher layer depends on protocol, not implementation
class IdeaService:
    """Service layer orchestrates business logic."""
    
    def __init__(self, repository: IdeaRepository):
        # Depends on abstraction, not concrete class
        self._repository = repository
    
    def create_idea(self, title: str, source: str) -> str:
        idea = IdeaInspiration(
            id=generate_id(),
            title=title,
            source=source
        )
        return self._repository.save(idea)
```

### Communication Patterns

**1. Direct Dependency Injection (Preferred)**
```python
# Application wiring
db_repository = SqliteIdeaRepository("database.db")
service = IdeaService(repository=db_repository)
```

**2. Factory Pattern**
```python
class RepositoryFactory:
    @staticmethod
    def create(db_type: str) -> IdeaRepository:
        if db_type == "sqlite":
            return SqliteIdeaRepository()
        elif db_type == "postgres":
            return PostgresIdeaRepository()
```

**3. Configuration-Based**
```python
# config.yaml
repositories:
  idea_repository:
    type: "sqlite"
    path: "data/ideas.db"

# Load and inject
config = load_config("config.yaml")
repository = create_from_config(config["repositories"]["idea_repository"])
service = IdeaService(repository=repository)
```

---

## 4. Design Patterns for PrismQ

### Applicable Design Patterns

#### **1. Strategy Pattern** ⭐⭐⭐⭐⭐
**Use Case**: Different content source scrapers (YouTube, TikTok, Reddit)

```python
class ContentScrapingStrategy(Protocol):
    def scrape(self, url: str) -> List[IdeaInspiration]: ...

class YouTubeScrapingStrategy:
    def scrape(self, url: str) -> List[IdeaInspiration]:
        # YouTube-specific scraping
        pass

class ContentScraper:
    def __init__(self, strategy: ContentScrapingStrategy):
        self.strategy = strategy
    
    def fetch_content(self, url: str) -> List[IdeaInspiration]:
        return self.strategy.scrape(url)
```

#### **2. Factory Pattern** ⭐⭐⭐⭐⭐
**Use Case**: Creating workers based on task type

```python
class WorkerFactory:
    _registry = {}
    
    @classmethod
    def register(cls, task_type: str, worker_class):
        cls._registry[task_type] = worker_class
    
    @classmethod
    def create(cls, task_type: str) -> Worker:
        worker_class = cls._registry.get(task_type)
        if not worker_class:
            raise ValueError(f"Unknown task type: {task_type}")
        return worker_class()
```

#### **3. Repository Pattern** ⭐⭐⭐⭐⭐
**Use Case**: Data access abstraction (already used in project)

```python
class IdeaInspirationRepository(Protocol):
    def save(self, idea: IdeaInspiration) -> str: ...
    def find_by_id(self, id: str) -> Optional[IdeaInspiration]: ...
```

#### **4. Observer Pattern** ⭐⭐⭐⭐
**Use Case**: Task completion notifications, progress tracking

```python
class TaskObserver(Protocol):
    def on_task_completed(self, task_id: str, result: Any): ...
    def on_task_failed(self, task_id: str, error: Exception): ...

class TaskRunner:
    def __init__(self):
        self._observers: List[TaskObserver] = []
    
    def subscribe(self, observer: TaskObserver):
        self._observers.append(observer)
    
    def _notify_completed(self, task_id: str, result: Any):
        for observer in self._observers:
            observer.on_task_completed(task_id, result)
```

#### **5. Adapter Pattern** ⭐⭐⭐⭐
**Use Case**: Adapting third-party APIs to internal interfaces

```python
class YouTubeAPIAdapter:
    """Adapts YouTube Data API to our domain model."""
    
    def __init__(self, youtube_client):
        self._client = youtube_client
    
    def get_video_details(self, video_id: str) -> IdeaInspiration:
        # Adapt YouTube API response to IdeaInspiration
        raw_data = self._client.videos().list(id=video_id).execute()
        return self._convert_to_idea(raw_data)
```

#### **6. Template Method Pattern** ⭐⭐⭐
**Use Case**: Base worker with customizable steps

```python
class BaseWorker(ABC):
    def execute(self, task: Task) -> TaskResult:
        self.validate(task)
        self.before_process(task)
        result = self.process(task)  # Abstract
        self.after_process(result)
        return result
    
    @abstractmethod
    def process(self, task: Task) -> TaskResult:
        pass
    
    def validate(self, task: Task):
        """Default validation, can be overridden"""
        pass
```

#### **7. Singleton Pattern** ⭐⭐
**Use Case**: Configuration loader, database connections (use sparingly)

```python
class ConfigLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
```

---

## 5. Concerns and Risk Mitigation

### Identified Concerns

#### **Concern 1: Dependency Hell Across Layers**
**Risk**: Conflicting dependencies between layers (e.g., different ML library versions)

**Mitigation**:
- ✅ Use layer-specific virtual environments
- ✅ Pin dependencies with version ranges in `pyproject.toml`
- ✅ Use dependency checkers (pip-audit, safety)
- ✅ Regular dependency updates in controlled manner

#### **Concern 2: Layer Boundary Violations**
**Risk**: Higher layers directly accessing lower layer implementations

**Mitigation**:
- ✅ Use Python Protocols to define contracts
- ✅ Dependency Inversion Principle (depend on abstractions)
- ✅ Code review checklist for layer violations
- ✅ Static analysis tools (mypy with strict mode)

#### **Concern 3: Testing Complexity with Multiple Venvs**
**Risk**: Hard to run tests across all layers

**Mitigation**:
- ✅ Master test script that activates each venv
- ✅ CI/CD pipeline handles venv setup automatically
- ✅ Mock external dependencies in unit tests
- ✅ Integration tests run in separate stage

#### **Concern 4: Performance with Protocol Overhead**
**Risk**: Protocol-based abstractions might slow execution

**Analysis**:
- ✅ Protocols have ZERO runtime overhead (structural subtyping)
- ✅ Only checked at type-check time (mypy)
- ✅ No performance impact compared to duck typing

#### **Concern 5: Documentation Maintenance**
**Risk**: Documentation gets out of sync with code

**Mitigation**:
- ✅ Code examples in documentation are actual runnable files
- ✅ Automated tests for example code
- ✅ Documentation in same PR as code changes
- ✅ Quarterly documentation review

#### **Concern 6: Onboarding Complexity**
**Risk**: New developers overwhelmed by architecture

**Mitigation**:
- ✅ Learning paths in Research_Layers/README.md
- ✅ Progressive disclosure (start simple, go deep)
- ✅ Templates for common patterns
- ✅ Mentorship and pair programming

---

## 6. Language Considerations (English/Czech)

### Current Approach: English Primary, Czech Optional

**Decision**: Use English as primary documentation language

**Rationale**:
- ✅ **International Collaboration**: English enables global contributors
- ✅ **Technical Resources**: Most technical resources in English
- ✅ **Code Standards**: PEP 8, SOLID, etc. referenced in English
- ✅ **Library Documentation**: Dependencies documented in English
- ✅ **Career Growth**: English technical writing is valuable skill

### Czech Language Support

**Where Czech is Appropriate**:
- ✅ Team meetings and discussions (if team is Czech)
- ✅ Internal notes and brainstorming
- ✅ User-facing documentation (if users are Czech)

**Where English is Required**:
- ✅ Code (variables, functions, classes, comments)
- ✅ Technical documentation
- ✅ Architecture Decision Records (ADRs)
- ✅ API documentation
- ✅ Git commit messages

### Best Practice: Code and Comments in English

```python
# ✅ GOOD: English code and comments
class VideoProcessor:
    """Process video content for idea extraction."""
    
    def extract_ideas(self, video_url: str) -> List[IdeaInspiration]:
        """Extract idea inspirations from video."""
        pass

# ❌ BAD: Mixed Czech/English
class VideoProcesor:
    """Zpracování video obsahu pro extrakci nápadů."""
    
    def extrahuj_napady(self, video_url: str) -> List[IdeaInspiration]:
        """Extrahuje nápady z videa."""
        pass
```

### Recommendation

**No special action needed** - current approach is correct:
- Documentation is in English ✅
- Code is in English ✅
- Team can communicate in Czech during development ✅

---

## 7. Best Practices Compilation

### Python Best Practices (PEP 8 + Extensions)

#### **1. Naming Conventions**

```python
# ✅ GOOD: Clear, descriptive names
class YouTubeVideoScraper:
    MAX_RETRY_ATTEMPTS = 3
    
    def __init__(self, api_key: str):
        self._api_key = api_key  # Private attribute
    
    def fetch_video_metadata(self, video_id: str) -> VideoMetadata:
        pass

# ❌ BAD: Unclear, inconsistent names
class YTVidScr:
    max = 3
    
    def __init__(self, key):
        self.key = key  # Should be private
    
    def getVidMD(self, vid):  # Inconsistent naming
        pass
```

#### **2. Type Hints (PEP 484)**

```python
from typing import List, Optional, Dict, Any

# ✅ GOOD: Complete type hints
def process_videos(
    video_ids: List[str],
    options: Optional[Dict[str, Any]] = None
) -> List[IdeaInspiration]:
    """Process multiple videos and return ideas."""
    pass

# ❌ BAD: No type hints
def process_videos(video_ids, options=None):
    pass
```

#### **3. Docstrings (PEP 257 + Google Style)**

```python
# ✅ GOOD: Complete docstring
def calculate_relevance_score(
    title: str,
    description: str,
    categories: List[str]
) -> float:
    """Calculate relevance score for content.
    
    Analyzes title, description, and categories to compute
    a relevance score between 0.0 and 1.0.
    
    Args:
        title: Content title (required, non-empty)
        description: Content description (can be empty)
        categories: List of category tags
    
    Returns:
        Relevance score between 0.0 (irrelevant) and 1.0 (highly relevant)
    
    Raises:
        ValueError: If title is empty or categories list is empty
    
    Example:
        >>> calculate_relevance_score(
        ...     "Python Tutorial",
        ...     "Learn Python basics",
        ...     ["programming", "tutorial"]
        ... )
        0.85
    """
    pass
```

#### **4. Error Handling**

```python
# ✅ GOOD: Specific exceptions, proper handling
def fetch_video_details(video_id: str) -> VideoDetails:
    try:
        response = api_client.get_video(video_id)
        return parse_video_details(response)
    except NetworkError as e:
        logger.error(f"Network error fetching video {video_id}: {e}")
        raise FetchError(f"Failed to fetch video: {e}") from e
    except ParseError as e:
        logger.error(f"Parse error for video {video_id}: {e}")
        raise InvalidDataError(f"Invalid video data: {e}") from e

# ❌ BAD: Bare except, swallows errors
def fetch_video_details(video_id):
    try:
        response = api_client.get_video(video_id)
        return parse_video_details(response)
    except:  # Too broad!
        return None  # Lost error information!
```

#### **5. Function Length and Complexity**

```python
# ✅ GOOD: Small, focused functions
def process_video(video_id: str) -> IdeaInspiration:
    """Process single video into idea inspiration."""
    metadata = fetch_video_metadata(video_id)
    validated = validate_metadata(metadata)
    enriched = enrich_with_classification(validated)
    return save_to_database(enriched)

# ❌ BAD: Too long, does too much
def process_video(video_id):
    """Process video."""
    # 200 lines of code doing everything...
    pass
```

---

## 8. Clean Code Principles

### Core Principles from "Clean Code" by Robert C. Martin

#### **1. Meaningful Names**

```python
# ✅ GOOD: Reveals intent
def get_active_youtube_videos_from_last_week() -> List[Video]:
    pass

# ❌ BAD: Unclear abbreviations
def get_act_yt_vids_lst_wk():
    pass
```

#### **2. Functions Should Do One Thing**

```python
# ✅ GOOD: Single responsibility
def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    pass

def validate_video_id(video_id: str) -> bool:
    """Validate video ID format."""
    pass

# ❌ BAD: Does multiple things
def extract_and_validate_video_id(url):
    """Extract and validate video ID."""
    # Extracts AND validates - two responsibilities
    pass
```

#### **3. DRY (Don't Repeat Yourself)**

```python
# ✅ GOOD: Extract common logic
def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()

def save_video(video: Video):
    video.created_at = format_timestamp(datetime.now())
    # Use helper

def save_channel(channel: Channel):
    channel.created_at = format_timestamp(datetime.now())
    # Reuse same helper

# ❌ BAD: Duplicated logic
def save_video(video):
    video.created_at = datetime.now().isoformat()

def save_channel(channel):
    channel.created_at = datetime.now().isoformat()  # Duplicated!
```

#### **4. Error Handling is One Thing**

```python
# ✅ GOOD: Separate error handling
def save_video_safe(video: Video) -> bool:
    """Save video with error handling."""
    try:
        save_video(video)
        return True
    except DatabaseError as e:
        logger.error(f"Failed to save video: {e}")
        return False

def save_video(video: Video):
    """Save video to database."""
    # Pure business logic, no error handling
    db.insert(video)

# ❌ BAD: Mixed business logic and error handling
def save_video(video):
    try:
        # Validate
        if not video.title:
            raise ValueError()
        # Transform
        video.title = video.title.strip()
        # Save
        db.insert(video)
    except Exception as e:
        logger.error(e)
        # Complex error handling mixed with logic
```

#### **5. Comments: Code Should Be Self-Explanatory**

```python
# ✅ GOOD: Self-documenting code
def is_video_suitable_for_audience(
    video: Video,
    audience_age: int,
    content_preferences: List[str]
) -> bool:
    """Check if video is suitable for target audience."""
    return (
        video.rating.is_appropriate_for_age(audience_age)
        and video.has_preferred_content(content_preferences)
        and not video.has_sensitive_content()
    )

# ❌ BAD: Comments explain what code does
def check_video(video, age, prefs):
    # Check if age rating is ok
    if video.rating > age:
        return False
    # Check content preferences
    for pref in prefs:
        if pref not in video.tags:
            return False
    # Check sensitive content flag
    if video.sensitive:
        return False
    return True
```

---

## 9. PEP Standards Quick Reference

### Essential PEPs for This Project

#### **PEP 8 - Style Guide for Python Code**

**Key Points**:
- Indentation: 4 spaces (no tabs)
- Line length: 79-88 characters (88 for black formatter)
- Imports: grouped (stdlib, third-party, local)
- Naming: `snake_case` for functions/variables, `PascalCase` for classes

```python
# ✅ GOOD: PEP 8 compliant
import os
import sys
from typing import List

import requests
from pydantic import BaseModel

from prismq.model import IdeaInspiration


class VideoProcessor:
    """Process video content."""
    
    def process_video(self, video_id: str) -> IdeaInspiration:
        """Process single video."""
        pass
```

#### **PEP 484 - Type Hints**

```python
from typing import List, Dict, Optional, Union

def process_videos(
    video_ids: List[str],
    options: Optional[Dict[str, str]] = None
) -> Union[List[IdeaInspiration], None]:
    """Process multiple videos."""
    pass
```

#### **PEP 544 - Protocols (Structural Subtyping)**

```python
from typing import Protocol

class Drawable(Protocol):
    """Protocol for drawable objects."""
    
    def draw(self) -> None:
        """Draw the object."""
        ...

# Any class with draw() method is a Drawable
class Circle:
    def draw(self) -> None:
        print("Drawing circle")

# No explicit inheritance needed!
def render(obj: Drawable) -> None:
    obj.draw()
```

#### **PEP 257 - Docstring Conventions**

```python
def function_with_docstring(param1: str, param2: int) -> bool:
    """
    Short one-line summary.
    
    Longer description if needed, explaining the function's
    purpose, behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When this happens
    """
    pass
```

---

## 10. Summary and Quick Actions

### ✅ Completed

1. **Python Examples**: Added throughout Research_Layers
2. **Virtual Environment Strategy**: Documented and implemented
3. **Layer Integration**: Protocol-based patterns documented
4. **Design Patterns**: Identified and implemented applicable patterns
5. **Concerns**: Identified and mitigated
6. **Language**: Confirmed English as primary (correct approach)
7. **Best Practices**: Compiled comprehensive guide
8. **Clean Code**: Documented principles with examples
9. **PEP Standards**: Quick reference created

### 🎯 Quick Reference Links

- **SOLID Examples**: `02_Design_Patterns/examples/`
- **Testing Patterns**: `03_Testing/examples/`
- **Layer Architecture**: `01_Architecture/examples/`
- **Worker Templates**: `05_Templates/`
- **Quick Lookup**: `QUICK_REFERENCE.md`

### 📚 Learning Path

1. Read this document (30 min)
2. Review Python examples in each section (60 min)
3. Follow a learning path from main README (2-3 hours)
4. Apply patterns in your code (ongoing)

---

**Last Updated**: 2025-11-14  
**Maintained By**: PrismQ Architecture Team  
**Next Review**: Quarterly

---

