# Coding Conventions - PrismQ.IdeaInspiration

**Last Updated**: 2025-11-14  
**Status**: Active

## Purpose

This document defines coding conventions for PrismQ.IdeaInspiration to ensure consistency, maintainability, and adherence to our layered architecture.

## Table of Contents

- [Layered Architecture Conventions](#layered-architecture-conventions)
- [Naming Conventions](#naming-conventions)
- [Module Structure](#module-structure)
- [Import Conventions](#import-conventions)
- [Code Style](#code-style)
- [Documentation Standards](#documentation-standards)
- [Testing Conventions](#testing-conventions)

---

## Layered Architecture Conventions

### Layer Definitions

Our system uses a **5-layer architecture**:

1. **Infrastructure Layer** (ConfigLoad)
2. **Data Collection Layer** (Sources)
3. **Data Model Layer** (Model)
4. **Processing Pipeline Layer** (Classification, Scoring)
5. **Application Layer** (Separate repositories)

See [ADR-001: Layered Architecture](./decisions/ADR-001-LAYERED_ARCHITECTURE.md) for complete definitions.

### Dependency Rules

**✅ Allowed** (downward dependencies):
```python
# Processing → Model
from Model import IdeaInspiration

# Sources → Model
from Model import IdeaInspiration

# Any module → ConfigLoad
from ConfigLoad import Config
```

**❌ Forbidden** (upward dependencies):
```python
# Model → Sources (NO!)
from Source.Video.YouTube import YouTubePlugin  # ❌

# ConfigLoad → Model (NO!)
from Model import IdeaInspiration  # ❌
```

**❌ Forbidden** (peer dependencies):
```python
# Classification → Scoring (NO!)
from Scoring import ContentScorer  # ❌

# Scoring → Classification (NO!)
from Classification import ContentClassifier  # ❌
```

### Dependency Injection

**✅ Do** - Inject dependencies:
```python
class BaseWorker:
    def __init__(
        self,
        config: Config,        # Injected
        database: Database,    # Injected
    ):
        self.config = config
        self.database = database
```

**❌ Don't** - Create dependencies internally:
```python
class BadWorker:
    def __init__(self):
        self.config = Config()  # ❌ Creates own dependency
        self.database = Database()  # ❌ Hard-coded
```

---

## Naming Conventions

### Layer-Specific Naming

#### Infrastructure Layer (ConfigLoad)

**Classes**:
- `Config` - Configuration management
- `Logger` - Logging utilities
- Simple, descriptive names

**Files**:
- `config.py` - Configuration
- `utils.py` - Utilities
- `constants.py` - Constants

#### Data Model Layer (Model)

**Classes**:
- `IdeaInspiration` - Core data model
- `{Concept}Schema` - Pydantic schemas
- Pure data model names (no "Manager", "Service", etc.)

**Files**:
- `idea_inspiration.py` - Main model
- `schemas.py` - Schema definitions
- Noun-based names

#### Data Collection Layer (Sources)

**Plugins**:
```python
# Pattern: {Platform}{MediaType}Plugin
class YouTubeVideoPlugin(VideoPlugin):
    pass

class RedditTextPlugin(TextPlugin):
    pass
```

**Workers**:
```python
# Pattern: {Platform}{MediaType}Worker
class YouTubeVideoWorker(BaseWorker):
    pass
```

**Files**:
```
# Pattern: {platform}_{endpoint}_plugin.py
youtube_channel_plugin.py
youtube_video_plugin.py
reddit_posts_plugin.py
```

**Directories**:
```
Source/
├── {MediaType}/          # Video, Audio, Text, Other
│   ├── {Platform}/       # YouTube, Reddit, etc.
│   │   └── {Endpoint}/   # Channel, Video, Search
```

#### Processing Layer (Classification, Scoring)

**Classes**:
```python
# Pattern: Content{Purpose} or {Purpose}{Type}
class ContentClassifier:
    pass

class StoryDetector:
    pass

class ContentScorer:
    pass

class EngagementScorer:
    pass
```

**Files**:
```
classifier.py
story_detector.py
scorer.py
engagement_scorer.py
```

### General Naming Rules

#### Classes

**Do**:
- Use PascalCase: `ContentClassifier`, `BaseWorker`
- Use descriptive names: `YouTubeChannelPlugin` not `YTCPlugin`
- Follow layer conventions (see above)

**Don't**:
- Use abbreviations: `YTPlugin` ❌
- Use generic names: `Helper`, `Manager`, `Utils` ❌ (unless truly generic)
- Mix naming styles: `youtube_Plugin` ❌

#### Functions and Methods

**Do**:
- Use snake_case: `process_task()`, `get_source_name()`
- Use verb phrases: `fetch_data()`, `calculate_score()`
- Be specific: `scrape_youtube_channel()` not `scrape()`

**Don't**:
- Use camelCase: `processTask()` ❌
- Use ambiguous names: `do_it()`, `handle()` ❌

#### Variables

**Do**:
- Use snake_case: `api_key`, `database_url`
- Use descriptive names: `youtube_api_key` not `key`
- Use plural for collections: `ideas`, `categories`

**Don't**:
- Use single letters (except loops): `x`, `y` ❌
- Use generic names: `data`, `info`, `temp` ❌

#### Constants

**Do**:
- Use UPPER_SNAKE_CASE: `MAX_RETRIES`, `API_TIMEOUT`
- Define in appropriate layer (usually ConfigLoad or module level)

```python
# Good
MAX_WORKERS = 10
DEFAULT_POLL_INTERVAL = 5.0
API_BASE_URL = "https://api.example.com"
```

#### Private Members

**Do**:
- Use single underscore prefix: `_private_method()`, `_internal_var`
- Use for internal implementation details

```python
class ContentClassifier:
    def classify(self, idea: IdeaInspiration):
        """Public API method."""
        return self._perform_classification(idea)
    
    def _perform_classification(self, idea: IdeaInspiration):
        """Private implementation detail."""
        pass
```

---

## Module Structure

### Pattern 1: Simple Module (ConfigLoad, Model)

Use for modules with minimal code:

```
ModuleName/
├── __init__.py           # Package initialization
├── main_module.py        # Main implementation
├── README.md             # Navigation hub
├── pyproject.toml        # Package configuration
└── tests/                # Tests
    └── test_main.py
```

**When to use**: < 500 lines of code, single purpose

### Pattern 2: Standard Module (Classification, Scoring)

Use for most modules:

```
ModuleName/
├── README.md
├── pyproject.toml
├── src/                  # Source code
│   ├── __init__.py
│   ├── core/            # Core logic
│   │   ├── config.py
│   │   └── logging_config.py
│   └── [domain]/        # Domain-specific code
├── _meta/               # Metadata
│   ├── docs/           # Documentation
│   ├── examples/       # Usage examples
│   └── issues/         # Issue tracking
└── tests/              # Tests
    └── test_*.py
```

**When to use**: Most modules

### Pattern 3: Plugin Module (Sources)

Use for extensible modules:

```
ModuleName/
├── README.md
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── core/           # Infrastructure
│   ├── plugins/        # Plugin implementations
│   │   ├── __init__.py
│   │   └── plugin_impl.py
│   └── workers/        # Worker implementations (if needed)
├── _meta/
└── tests/
```

**When to use**: Modules with plugins or workers

### Pattern 4: Multi-Tier Module (Sources with sub-layers)

Use for hierarchical modules:

```
Source/
├── Video/              # Level 1: Media Type
│   ├── YouTube/        # Level 2: Platform
│   │   ├── Channel/    # Level 3: Endpoint
│   │   ├── Video/
│   │   └── Search/
│   └── src/            # Shared utilities
├── Audio/
├── Text/
└── Other/
```

**When to use**: Multi-dimensional hierarchies

### File Organization

**Infrastructure** (`core/`, `src/core/`):
- `config.py` - Configuration management
- `logging_config.py` - Logging setup
- `database.py` - Database utilities
- `utils.py` - General utilities

**Business Logic** (`mod/`, domain-specific):
- Organized by domain/feature
- Focused, cohesive modules
- Clear purpose

**Tests** (`tests/`, `_meta/tests/`):
- Mirror source structure
- `test_{module}.py` naming
- `conftest.py` for fixtures

---

## Import Conventions

### Import Order

Follow PEP 8 import order:

```python
# 1. Standard library imports
import os
import sys
from pathlib import Path
from typing import List, Optional

# 2. Third-party imports
import pytest
from pydantic import BaseModel

# 3. PrismQ module imports (lower layers first)
from ConfigLoad import Config
from Model import IdeaInspiration

# 4. Local imports (relative)
from .core.database import Database
from .plugins import SourcePlugin
```

### Import Style

**Do**:
```python
# Explicit imports
from Model import IdeaInspiration
from typing import List, Optional

# Grouped imports
from ConfigLoad import (
    Config,
    Logger,
    load_config,
)
```

**Don't**:
```python
# Wildcard imports
from Model import *  # ❌

# Module-level imports (when specific names available)
import Model  # ❌ Use: from Model import IdeaInspiration
```

### Relative vs Absolute Imports

**Within a module** - Use relative imports:
```python
# In Source/Video/YouTube/Channel/src/plugins/channel_plugin.py
from ..core.config import Config  # ✅
from .base_plugin import BasePlugin  # ✅
```

**Between modules** - Use absolute imports:
```python
# Any module importing from Model
from Model import IdeaInspiration  # ✅

# Any module importing from ConfigLoad
from ConfigLoad import Config  # ✅
```

---

## Code Style

### PEP 8 Compliance

Follow [PEP 8](https://pep8.org/) with these modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Blank lines**: 2 between classes, 1 between methods

### Type Hints

**Always use type hints** for:
- Function parameters
- Return values
- Class attributes

```python
from typing import List, Optional

def classify(
    self,
    idea: IdeaInspiration,
    categories: List[str],
) -> Optional[str]:
    """Classify an idea into a category."""
    pass
```

### Docstrings

Use **Google-style docstrings**:

```python
def process_task(self, task: Task) -> TaskResult:
    """Process a claimed task.
    
    This method implements the core task processing logic.
    Subclasses must override this method.
    
    Args:
        task: The task to process
        
    Returns:
        TaskResult with success status and data
        
    Raises:
        ValueError: If task parameters are invalid
        APIError: If external API call fails
        
    Example:
        >>> worker = YouTubeVideoWorker(config)
        >>> task = Task(id=1, task_type="youtube_video")
        >>> result = worker.process_task(task)
        >>> assert result.success
    """
    pass
```

### Comments

**Do** - Comment complex logic:
```python
# Calculate weighted average using exponential decay
# This gives more weight to recent items
weighted_sum = sum(value * (0.9 ** i) for i, value in enumerate(values))
```

**Don't** - Comment obvious code:
```python
# Set the name variable
name = "John"  # ❌ Obvious
```

### Error Handling

**Do** - Be specific:
```python
try:
    api_response = fetch_from_api()
except requests.HTTPError as e:
    logger.error(f"API request failed: {e}")
    raise
except requests.Timeout:
    logger.warning("API timeout, retrying...")
    retry()
```

**Don't** - Catch all exceptions:
```python
try:
    do_something()
except:  # ❌ Too broad
    pass
```

---

## Documentation Standards

### README Files

Follow the **navigation hub pattern** (see [README_STANDARDS.md](./README_STANDARDS.md)):

**Do**:
- ✅ Brief overview (1-2 sentences)
- ✅ Key highlights (3-5 bullets)
- ✅ Minimal quick start (1-2 commands)
- ✅ Links to detailed docs

**Don't**:
- ❌ Detailed installation instructions
- ❌ Complete usage guides
- ❌ Architecture explanations
- ❌ Duplicate information from docs/

### Module Documentation

Organize documentation in `_meta/docs/`:

```
_meta/docs/
├── ARCHITECTURE.md      # Module architecture
├── USER_GUIDE.md        # How to use
├── API.md               # API reference
└── CONTRIBUTING.md      # How to contribute
```

### Code Documentation

**Classes**:
```python
class ContentClassifier:
    """Classifies content into predefined categories.
    
    This classifier uses NLP techniques to analyze content
    and assign appropriate categories. It follows the
    Single Responsibility Principle by focusing solely
    on classification.
    
    Attributes:
        config: Configuration object
        categories: List of available categories
        
    Example:
        >>> classifier = ContentClassifier(config)
        >>> result = classifier.classify(idea)
        >>> print(result.categories)
        ['technology', 'ai']
    """
```

**Functions**:
```python
def scrape(self) -> List[IdeaInspiration]:
    """Scrape ideas from YouTube channel.
    
    Fetches recent videos from the configured channel
    and converts them to IdeaInspiration objects.
    
    Returns:
        List of IdeaInspiration objects, one per video
        
    Raises:
        APIError: If YouTube API request fails
        ConfigError: If channel ID not configured
    """
```

---

## Testing Conventions

### Test Organization

Mirror source structure:

```
src/
└── plugins/
    └── youtube_plugin.py

tests/
└── plugins/
    └── test_youtube_plugin.py
```

### Test Naming

**Files**: `test_{module}.py`  
**Classes**: `Test{Feature}`  
**Methods**: `test_{scenario}_{expected_result}`

```python
# tests/test_classifier.py

class TestContentClassifier:
    """Tests for ContentClassifier."""
    
    def test_classify_returns_valid_category(self):
        """classify() returns a valid category from the list."""
        pass
    
    def test_classify_handles_empty_input(self):
        """classify() raises ValueError for empty input."""
        pass
```

### Test Structure

Use **Arrange-Act-Assert**:

```python
def test_worker_processes_task_successfully(self):
    """Worker processes task and returns success result."""
    # Arrange
    config = Config()
    worker = YouTubeVideoWorker(config)
    task = Task(id=1, task_type="youtube_video")
    
    # Act
    result = worker.process_task(task)
    
    # Assert
    assert result.success
    assert result.data is not None
    assert "video_id" in result.data
```

### Fixtures

Use pytest fixtures for common setup:

```python
# conftest.py

@pytest.fixture
def config():
    """Provide test configuration."""
    return Config(test_mode=True)

@pytest.fixture
def mock_idea():
    """Provide mock IdeaInspiration."""
    return IdeaInspiration(
        id="test-1",
        source="test",
        title="Test Idea",
    )
```

### Test Coverage

- **Aim for >80% coverage**
- Test happy paths and error cases
- Test edge cases
- Test integration points

---

## Quick Reference

### Checklist for New Code

- [ ] Follows layer conventions (correct layer, dependencies)
- [ ] Uses proper naming conventions
- [ ] Includes type hints
- [ ] Has docstrings (Google style)
- [ ] Follows PEP 8 (with 100 char lines)
- [ ] Uses dependency injection
- [ ] Has appropriate tests (>80% coverage)
- [ ] Documentation updated

### Common Patterns

**Dependency Injection**:
```python
def __init__(self, config: Config, database: Database):
    self.config = config
    self.database = database
```

**Abstract Base Class**:
```python
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    @abstractmethod
    def scrape(self) -> List[IdeaInspiration]:
        pass
```

**Protocol (Interface)**:
```python
from typing import Protocol

class PluginProtocol(Protocol):
    def scrape(self) -> List[IdeaInspiration]: ...
```

**Dataclass**:
```python
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    task_type: str
```

---

## Related Documents

- [SOLID Principles](./SOLID_PRINCIPLES.md)
- [ADR-001: Layered Architecture](./decisions/ADR-001-LAYERED_ARCHITECTURE.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Code Review Guidelines](./CODE_REVIEW_GUIDELINES.md)
- [Contributing Guide](./CONTRIBUTING.md)

---

## Enforcement

These conventions are enforced through:

1. **Code Reviews** - Manual review using checklist
2. **Linting** - Black, flake8, mypy
3. **Tests** - Architecture tests in CI/CD
4. **Pre-commit Hooks** - Automated checks (future)

See [ENFORCEMENT_STRATEGIES.md](../research/Research_Layers/ENFORCEMENT_STRATEGIES.md) for details.

---

**Maintained By**: Architecture Team  
**Last Updated**: 2025-11-14  
**Status**: Active
