# ADR-001: Layered Architecture for PrismQ.T.Idea.Inspiration

**Status**: Accepted  
**Date**: 2025-11-14  
**Decision Makers**: Architecture Team  
**Related ADRs**: None (foundational decision)

## Context

PrismQ.T.Idea.Inspiration is a multi-module ecosystem for AI-powered content idea collection, classification, scoring, and processing. As the system grows, we need a clear architectural pattern that:

- Maintains separation of concerns
- Enables independent module development
- Prevents tight coupling between layers
- Facilitates testing and maintenance
- Supports extensibility without modifying existing code

### Background

The system has evolved to include multiple specialized modules:
- **Sources** - Multi-platform content collection (24+ sources)
- **Model** - Core data structures (IdeaInspiration)
- **Classification** - Content categorization and story detection
- **Scoring** - Quality and engagement evaluation
- **ConfigLoad** - Centralized configuration management

Without clear architectural boundaries, we risk:
- Circular dependencies between modules
- Duplicated logic across layers
- Difficulty in testing individual components
- Tight coupling that prevents independent deployment

### Assumptions

- Python 3.10+ is the primary language
- Modules may be used independently or together
- Windows with RTX 5090 is the primary platform
- Some modules will have domain-specific sub-layers

## Decision

We adopt a **layered architecture** with clearly defined responsibilities, dependencies, and allowed interactions between layers.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  (CLI tools, Web interfaces - separate repositories)        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Processing Pipeline                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Classification│  │   Scoring    │  │    Future    │     │
│  │    Module    │  │    Module    │  │   Modules    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Data Model Layer                        │
│                   (Model Module)                            │
│  • IdeaInspiration core structure                          │
│  • Common schemas and interfaces                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Data Collection Layer                     │
│                   (Sources Module)                          │
│                                                             │
│  Media Type Layer:                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Video   │  │   Audio  │  │   Text   │  │  Other   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  Platform Layer (within each media type):                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ YouTube  │  │  TikTok  │  │  Reddit  │  ...           │
│  └──────────┘  └──────────┘  └──────────┘                │
│                                                             │
│  Endpoint Layer (within each platform):                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Channel  │  │  Video   │  │  Search  │  ...           │
│  └──────────┘  └──────────┘  └──────────┘                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                       │
│                  (ConfigLoad Module)                        │
│  • Configuration management                                 │
│  • Environment variables                                    │
│  • Cross-module utilities                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
│  (YouTube API, TikTok API, Reddit API, etc.)               │
└─────────────────────────────────────────────────────────────┘
```

### Layer Definitions

#### 1. Infrastructure Layer (ConfigLoad)

**Purpose**: Provide foundational services used by all other layers

**Responsibilities**:
- ✅ Configuration management from environment variables
- ✅ Cross-module utility functions
- ✅ Logging infrastructure setup
- ✅ Common constants and enumerations

**Allowed Dependencies**:
- ✅ External libraries (os, json, yaml, etc.)
- ❌ NO dependencies on other PrismQ modules

**Interface**:
- Must use dependency injection patterns
- Provides configuration objects, not global state

**Example**:
```python
# ConfigLoad/config.py
class Config:
    """Configuration management."""
    
    def __init__(self, env_file: Optional[str] = None):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.database_url = os.getenv('DATABASE_URL')
        # ...
```

---

#### 2. Data Collection Layer (Sources)

**Purpose**: Collect raw content from external sources and transform into IdeaInspiration objects

**Responsibilities**:
- ✅ API integration with external platforms
- ✅ Data fetching and rate limiting
- ✅ Basic data transformation to IdeaInspiration
- ✅ Error handling and retry logic

**Sub-Layer Structure** (3-tier hierarchy):

**Level 1: Media Type** (Video, Audio, Text, Other)
- Groups sources by content medium
- Provides media-specific base classes and utilities
- Example: `Source/Video/`, `Source/Audio/`, `Source/Text/`

**Level 2: Platform** (YouTube, TikTok, Reddit, etc.)
- Platform-specific integration logic
- API clients and authentication
- Example: `Source/Video/YouTube/`, `Source/Text/Reddit/`

**Level 3: Endpoint** (Channel, Video, Search, etc.)
- Specific API endpoints or data types
- Specialized scraping/collection logic
- Example: `Source/Video/YouTube/Channel/`, `Source/Video/YouTube/Video/`

**Allowed Dependencies**:
- ✅ Model module (for IdeaInspiration)
- ✅ ConfigLoad module (for configuration)
- ✅ External API libraries
- ❌ NO dependencies on Classification or Scoring

**Naming Conventions**:
- Classes: `{Platform}{MediaType}{Endpoint}Plugin` (e.g., `YouTubeVideoChannelPlugin`)
- Files: `{platform}_{endpoint}_plugin.py`
- Must inherit from appropriate base class (`SourcePlugin`, `BaseWorker`, etc.)

**Example**:
```python
# Source/Video/YouTube/Channel/src/plugins/channel_plugin.py
from Source.Model import IdeaInspiration
from Source.Video.src.plugins import VideoPlugin

class YouTubeChannelPlugin(VideoPlugin):
    """YouTube channel scraping plugin."""
    
    def scrape(self) -> List[IdeaInspiration]:
        """Scrape channel videos and convert to IdeaInspiration."""
        # Fetch from API
        # Transform to IdeaInspiration
        return ideas
```

---

#### 3. Data Model Layer (Model)

**Purpose**: Define core data structures and interfaces used across all modules

**Responsibilities**:
- ✅ IdeaInspiration base class and fields
- ✅ Common data schemas (Pydantic models, dataclasses)
- ✅ Serialization/deserialization logic
- ✅ Validation rules

**Allowed Dependencies**:
- ✅ External libraries (pydantic, dataclasses, typing)
- ❌ NO dependencies on other PrismQ modules

**Must Be**:
- Pure data models (no business logic)
- Immutable where possible
- Well-documented with type hints

**Example**:
```python
# Model/idea_inspiration.py
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class IdeaInspiration:
    """Core data structure for all content ideas."""
    
    # Identity
    id: str
    source: str
    platform: str
    
    # Content
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    
    # Metadata
    created_at: datetime
    collected_at: datetime
    
    # Will be enriched by Classification
    categories: Optional[List[str]] = None
    is_story: Optional[bool] = None
    
    # Will be enriched by Scoring
    quality_score: Optional[float] = None
    engagement_score: Optional[float] = None
```

---

#### 4. Processing Pipeline Layer (Classification, Scoring)

**Purpose**: Enrich IdeaInspiration objects with additional data

**Responsibilities**:

**Classification Module**:
- ✅ Categorize content into predefined categories
- ✅ Detect story potential
- ✅ Tag with relevant topics
- ✅ Update IdeaInspiration with classification results

**Scoring Module**:
- ✅ Evaluate content quality (title, description, text quality)
- ✅ Calculate engagement metrics
- ✅ Perform readability and sentiment analysis
- ✅ Update IdeaInspiration with scores

**Allowed Dependencies**:
- ✅ Model module (for IdeaInspiration)
- ✅ ConfigLoad module (for configuration)
- ✅ External ML/NLP libraries
- ❌ NO dependencies on Sources
- ❌ NO dependencies on each other (Classification ↔ Scoring)

**Must Be**:
- Stateless processors (no side effects on other modules)
- Idempotent (can be run multiple times safely)
- Independently testable

**Example**:
```python
# Classification/classifier.py
from Model import IdeaInspiration

class ContentClassifier:
    """Classify content into categories."""
    
    def classify(self, idea: IdeaInspiration) -> IdeaInspiration:
        """Add classification data to IdeaInspiration."""
        categories = self._determine_categories(idea.title, idea.description)
        is_story = self._detect_story(idea)
        
        # Return new instance (immutability)
        return IdeaInspiration(
            **idea.__dict__,
            categories=categories,
            is_story=is_story
        )
```

---

#### 5. Application Layer (Separate Repositories)

**Purpose**: Provide user interfaces and orchestration

**Examples**:
- CLI tools for each module
- Web interfaces (separate repository)
- Workflow orchestration scripts

**Allowed Dependencies**:
- ✅ All PrismQ modules
- ✅ Can orchestrate workflows across modules

**Must NOT**:
- ❌ Contain business logic (belongs in modules)
- ❌ Directly access external APIs (use Sources)

---

### Dependency Rules

**Allowed Dependency Flow** (downward only):

```
Application Layer
       ↓
Processing Layer (Classification, Scoring)
       ↓
Model Layer
       ↓
Collection Layer (Sources)
       ↓
Infrastructure Layer (ConfigLoad)
       ↓
External Services
```

**Dependency Rules**:

1. ✅ **Layers can depend on layers below them**
   - Sources → Model, ConfigLoad
   - Classification → Model, ConfigLoad
   - Scoring → Model, ConfigLoad

2. ❌ **Layers CANNOT depend on layers above them**
   - Model ❌→ Sources
   - ConfigLoad ❌→ Model
   - Sources ❌→ Classification

3. ❌ **Peer dependencies are NOT allowed**
   - Classification ❌↔ Scoring

4. ✅ **Use dependency injection for flexibility**
   - Pass dependencies via constructors
   - Don't create dependencies internally

5. ✅ **Depend on abstractions, not implementations**
   - Use ABC, Protocol for interfaces
   - Type hint with abstractions

---

### Layer Communication Patterns

#### Pattern 1: Data Flow (Sources → Model → Processing)

```python
# 1. Sources creates IdeaInspiration
from Model import IdeaInspiration

plugin = YouTubeChannelPlugin(config)
ideas = plugin.scrape()  # Returns List[IdeaInspiration]

# 2. Classification enriches
classifier = ContentClassifier(config)
classified_ideas = [classifier.classify(idea) for idea in ideas]

# 3. Scoring evaluates
scorer = ContentScorer(config)
scored_ideas = [scorer.score(idea) for idea in classified_ideas]
```

#### Pattern 2: Configuration Injection

```python
# ConfigLoad provides config
from ConfigLoad import Config

config = Config()

# All modules receive config
source_plugin = YouTubePlugin(config=config)
classifier = ContentClassifier(config=config)
scorer = ContentScorer(config=config)
```

#### Pattern 3: Event-Based (Future)

```python
# For decoupled communication (future enhancement)
from typing import Protocol

class EventPublisher(Protocol):
    def publish(self, event: Event): ...

class IdeaCollectedEvent:
    idea: IdeaInspiration

# Sources publishes events
publisher.publish(IdeaCollectedEvent(idea))

# Classification subscribes
subscriber.on_idea_collected(event)
```

---

### Module Structure Convention

Each module follows a standard structure:

```
ModuleName/
├── README.md                    # Module overview (navigation hub)
├── pyproject.toml              # Python packaging configuration
├── requirements.txt            # Dependencies (if needed)
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── core/                   # Core infrastructure
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   └── database.py (if needed)
│   ├── plugins/                # Extensible plugins (Sources)
│   │   └── ...
│   ├── workers/                # Worker implementations (Sources)
│   │   └── ...
│   └── [domain_logic]/         # Business logic files
│
├── _meta/                      # Metadata and documentation
│   ├── docs/                   # Module-specific documentation
│   │   ├── ARCHITECTURE.md
│   │   ├── USER_GUIDE.md
│   │   └── API.md
│   ├── examples/               # Usage examples
│   ├── issues/                 # Issue tracking
│   ├── research/               # Research notes
│   └── tests/                  # Unit and integration tests
│
└── tests/                      # Test directory (alternative location)
    ├── test_*.py
    └── conftest.py
```

---

## Considered Alternatives

### Alternative 1: Monolithic Architecture

**Description**: Single large codebase with all functionality together

**Pros**:
- Simpler initial setup
- No inter-module coordination needed
- Easier refactoring across boundaries

**Cons**:
- Difficult to maintain as it grows
- Tight coupling between components
- Hard to test individual parts
- Cannot deploy modules independently

**Decision**: Rejected - Does not scale for our multi-module ecosystem

### Alternative 2: Microservices Architecture

**Description**: Each module as a separate service with API boundaries

**Pros**:
- Strong isolation
- Independent deployment
- Language flexibility

**Cons**:
- Overhead of network communication
- Complex orchestration
- Overkill for local development on single machine
- Performance overhead

**Decision**: Rejected - Too complex for our use case (single Windows machine)

### Alternative 3: Flat Module Structure

**Description**: All modules at same level with no hierarchy

**Pros**:
- Simple to understand
- No dependency constraints

**Cons**:
- No clear boundaries
- Prone to circular dependencies
- Difficult to reason about architecture
- Hard to enforce conventions

**Decision**: Rejected - Leads to architectural chaos

---

## Consequences

### Positive

1. **Clear Separation of Concerns**
   - Each layer has well-defined responsibilities
   - Easy to understand where code belongs
   - Reduces cognitive load

2. **Testability**
   - Can test each layer independently
   - Mock dependencies easily with DI
   - Clear interfaces between layers

3. **Maintainability**
   - Changes localized to specific layers
   - Reduced risk of breaking other modules
   - Easier to onboard new developers

4. **Extensibility**
   - New sources can be added without touching other layers
   - New processing modules can be added independently
   - Follows Open/Closed Principle

5. **Reusability**
   - Model layer used by all modules
   - ConfigLoad shared across system
   - Plugins can be reused

### Negative

1. **Initial Complexity**
   - More upfront planning required
   - Developers must understand layer boundaries
   - May feel over-engineered for small features

2. **Coordination Overhead**
   - Changes affecting multiple layers require coordination
   - Interface changes need careful planning
   - More files and directories to navigate

3. **Performance Considerations**
   - Data transformation between layers
   - Potential for unnecessary object copying
   - Abstraction overhead (minimal in Python)

### Neutral

1. **Learning Curve**
   - New team members need to understand architecture
   - Requires documentation and examples
   - Offset by improved maintainability

2. **Tooling Requirements**
   - May need additional tools for dependency checking
   - Static analysis to enforce rules
   - Worth it for long-term benefits

---

## Implementation

### Changes Required

- [x] Document layer definitions (this ADR)
- [ ] Update existing modules to follow conventions
- [ ] Create layer-specific templates
- [ ] Add architectural tests
- [ ] Update developer onboarding

### Migration Plan

1. **Phase 1: Documentation**
   - Create this ADR
   - Document each layer's purpose
   - Create coding conventions guide

2. **Phase 2: Gradual Refactoring**
   - Identify violations in existing code
   - Refactor module by module
   - Add tests to prevent regressions

3. **Phase 3: Enforcement**
   - Add pre-commit hooks
   - Configure static analysis
   - Update CI/CD pipelines

### Rollback Strategy

If this architecture doesn't work:
1. Keep module boundaries but relax dependency rules
2. Allow peer dependencies if justified
3. Document exceptions in ADRs

---

## Compliance and Verification

### How to Verify Compliance

Developers can check compliance by asking:

1. **Is my module at the right layer?**
   - Check the layer definitions above

2. **Are my dependencies allowed?**
   - Review dependency rules
   - Check dependency flow diagram

3. **Am I following naming conventions?**
   - Review naming patterns for your layer
   - Check existing examples

4. **Is my code in the right directory?**
   - Follow module structure convention
   - Match existing patterns

### Code Review Checklist

During code reviews, verify:

- [ ] Module is at correct layer
- [ ] Dependencies only flow downward
- [ ] No peer dependencies (Classification ↔ Scoring)
- [ ] Follows naming conventions
- [ ] Uses dependency injection
- [ ] Depends on abstractions, not implementations
- [ ] Includes appropriate tests

### Automated Checks

Future automated checks:
- Import linting (check dependency direction)
- Static analysis for architecture violations
- CI/CD pipeline checks
- Pre-commit hooks

---

## Related Documents

- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture overview
- [SOLID_PRINCIPLES.md](../SOLID_PRINCIPLES.md) - Design principles
- [CODING_CONVENTIONS.md](../CODING_CONVENTIONS.md) - Coding standards
- [CODE_REVIEW_GUIDELINES.md](../CODE_REVIEW_GUIDELINES.md) - Review process

---

## Examples

### Good: Proper Layering

```python
# Classification/classifier.py
from Model import IdeaInspiration  # ✅ Lower layer
from ConfigLoad import Config      # ✅ Lower layer

class ContentClassifier:
    def __init__(self, config: Config):  # ✅ Dependency injection
        self.config = config
    
    def classify(self, idea: IdeaInspiration) -> IdeaInspiration:
        # ✅ Operates on Model layer objects
        # ✅ No dependencies on Sources
        pass
```

### Bad: Improper Layering

```python
# Model/idea_inspiration.py
from Classification import ContentClassifier  # ❌ Upper layer!

class IdeaInspiration:
    def auto_classify(self):  # ❌ Business logic in model
        classifier = ContentClassifier()  # ❌ Creates dependency
        return classifier.classify(self)  # ❌ Model knows about Classification
```

### Good: Source Plugin

```python
# Source/Video/YouTube/Channel/src/plugins/channel_plugin.py
from Model import IdeaInspiration  # ✅ Lower layer
from Source.Video.src.plugins import VideoPlugin  # ✅ Parent layer

class YouTubeChannelPlugin(VideoPlugin):
    def scrape(self) -> List[IdeaInspiration]:
        # ✅ Fetches data and creates IdeaInspiration
        # ✅ No classification or scoring logic
        pass
```

---

## Timeline

- **Proposed**: 2025-11-14
- **Accepted**: 2025-11-14
- **Implemented**: In Progress
- **Next Review**: 2025-12-14 (1 month)

---

## Notes

- This is a foundational ADR that other decisions will build upon
- Layer definitions may be refined based on experience
- Exceptions must be documented in separate ADRs
- Review this ADR quarterly and update as needed

---

**ADR Version**: 1.0  
**Last Updated**: 2025-11-14  
**Maintained By**: Architecture Team  
**Status**: Accepted ✅
