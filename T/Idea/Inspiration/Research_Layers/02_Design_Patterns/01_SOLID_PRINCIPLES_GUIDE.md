# SOLID Principles - PrismQ.T.Idea.Inspiration

This document explains SOLID design principles with concrete examples from the PrismQ.T.Idea.Inspiration codebase. These principles guide our architecture and code design decisions.

## Table of Contents

- [Overview](#overview)
- [1. Single Responsibility Principle (SRP)](#1-single-responsibility-principle-srp)
- [2. Open/Closed Principle (OCP)](#2-openclosed-principle-ocp)
- [3. Liskov Substitution Principle (LSP)](#3-liskov-substitution-principle-lsp)
- [4. Interface Segregation Principle (ISP)](#4-interface-segregation-principle-isp)
- [5. Dependency Inversion Principle (DIP)](#5-dependency-inversion-principle-dip)
- [Additional Design Principles](#additional-design-principles)
- [Applying SOLID in Your Code](#applying-solid-in-your-code)

## Overview

**SOLID** is an acronym for five design principles that make software more maintainable, flexible, and scalable:

- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

These principles work together to create a clean architecture that is:
- ✅ Easy to understand and maintain
- ✅ Flexible and extensible
- ✅ Testable with minimal mocking
- ✅ Resistant to bugs and regressions

## 1. Single Responsibility Principle (SRP)

### Definition

> A class should have one, and only one, reason to change.

Each class should focus on a single responsibility or concern. This makes code easier to understand, test, and maintain.

### Example from Codebase: Worker Task Lifecycle

**File**: `Source/Video/YouTube/Channel/src/workers/base_worker.py`

```python
class BaseWorker(ABC):
    """Base worker class providing common functionality.
    
    Follows Single Responsibility Principle (SRP):
    - Manages task lifecycle        ← Single responsibility
    - Handles polling and claiming  ← Single responsibility
    - Reports results              ← Single responsibility
    
    Does NOT handle:
    - Specific scraping logic (abstract method)
    - Queue implementation (injected dependency)
    - API integration (separate responsibility)
    """
```

**Why this is good:**
- ✅ `BaseWorker` focuses solely on task lifecycle management
- ✅ Delegates scraping logic to subclasses via `process_task()` abstract method
- ✅ Delegates queue operations to injected `QueueDatabase`
- ✅ Each method has a single, clear purpose

### Example: Pure Data Models

**File**: `Source/Video/YouTube/Channel/src/workers/__init__.py`

```python
@dataclass
class Task:
    """Represents a task from the queue.
    
    Following Single Responsibility Principle - only represents task data.
    """
    id: int
    task_type: str
    parameters: Dict[str, Any]
    created_at: Optional[datetime] = None
    priority: int = 5

@dataclass
class TaskResult:
    """Result of task processing.
    
    Following Single Responsibility Principle - only represents result data.
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

**Why this is good:**
- ✅ Data classes have **zero business logic** - pure data containers
- ✅ Each dataclass represents exactly one concept
- ✅ No mixed responsibilities (data + behavior)

### Common SRP Violations (Anti-patterns)

❌ **Bad Example:**

```python
class GodClass:
    """Does everything - BAD!"""
    
    def fetch_data_from_api(self): pass
    def parse_response(self): pass
    def validate_data(self): pass
    def save_to_database(self): pass
    def send_email_notification(self): pass
    def generate_report(self): pass
    def log_activity(self): pass
    # ... 20 more methods
```

✅ **Good Example (Separation of Concerns):**

```python
class APIClient:
    """Responsible only for API communication."""
    def fetch_data(self): pass

class DataParser:
    """Responsible only for parsing data."""
    def parse(self, raw_data): pass

class DataValidator:
    """Responsible only for validation."""
    def validate(self, data): pass

class DatabaseRepository:
    """Responsible only for database operations."""
    def save(self, data): pass
```

### Guidelines for SRP

1. **Each class should do one thing well**
2. **If you can't describe a class's purpose in one sentence without using "and", it probably violates SRP**
3. **Extract separate concerns into separate classes**
4. **Use composition to combine responsibilities**

---

## 2. Open/Closed Principle (OCP)

### Definition

> Software entities should be open for extension but closed for modification.

You should be able to add new functionality without changing existing code. This is typically achieved through abstraction, polymorphism, and design patterns.

### Example from Codebase: Worker Factory

**File**: `Source/Video/YouTube/Channel/src/workers/factory.py`

```python
class WorkerFactory:
    """Factory for creating worker instances (Factory Pattern).
    
    Follows Open/Closed Principle (OCP):
    - Open for extension: New workers can be registered
    - Closed for modification: Factory logic remains stable
    """
    
    def __init__(self):
        """Initialize the worker factory with default workers."""
        self._worker_types: Dict[str, Type[BaseWorker]] = {}
        
        # Register default workers
        self.register('youtube_video_single', YouTubeVideoWorker)
        self.register('youtube_video_search', YouTubeVideoWorker)
    
    def register(self, task_type: str, worker_class: Type[BaseWorker]):
        """Register a worker class for a task type.
        
        Args:
            task_type: The task type identifier
            worker_class: The worker class to handle this task type
        """
        self._worker_types[task_type] = worker_class
    
    def create(self, task_type: str, **kwargs) -> BaseWorker:
        """Create a worker instance for the given task type."""
        if task_type not in self._worker_types:
            raise ValueError(f"Unknown task type: {task_type}")
        
        worker_class = self._worker_types[task_type]
        return worker_class(**kwargs)
```

**How to extend (no factory modification needed):**

```python
# In your own module:
from Source.Video.YouTube.Channel.src.workers.factory import worker_factory
from my_module import CustomWorker

# Add new worker type WITHOUT modifying factory code
worker_factory.register('custom_task', CustomWorker)
```

**Why this is good:**
- ✅ New worker types can be added via `register()` method
- ✅ Factory logic remains unchanged
- ✅ Registry pattern enables runtime extensibility

### Example: Strategy Pattern

**File**: `Source/Video/YouTube/Channel/src/workers/claiming_strategies.py`

```python
class BaseClaimStrategy(ABC):
    """Base class for task claiming strategies."""
    
    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause for this strategy."""
        pass

class FIFOStrategy(BaseClaimStrategy):
    """First-In-First-Out: Oldest tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "created_at ASC, priority DESC"

class LIFOStrategy(BaseClaimStrategy):
    """Last-In-First-Out: Newest tasks first."""
    
    def get_order_by_clause(self) -> str:
        return "created_at DESC, priority DESC"

# Strategy registry for easy lookup
STRATEGIES = {
    'FIFO': FIFOStrategy(),
    'LIFO': LIFOStrategy(),
    'PRIORITY': PriorityStrategy(),
    'WEIGHTED_RANDOM': WeightedRandomStrategy(),
}
```

**How to extend:**

```python
# Add new strategy without modifying existing code:
class ShortestJobFirstStrategy(BaseClaimStrategy):
    def get_order_by_clause(self) -> str:
        return "estimated_duration ASC, priority DESC"

# Register it:
STRATEGIES['SJF'] = ShortestJobFirstStrategy()
```

**Why this is good:**
- ✅ New strategies added by subclassing `BaseClaimStrategy`
- ✅ No modification of existing strategy classes
- ✅ Registration pattern allows runtime extension

### Guidelines for OCP

1. **Use abstract base classes and interfaces (Protocols)**
2. **Depend on abstractions, not concrete implementations**
3. **Use design patterns: Strategy, Factory, Template Method**
4. **Make extension points explicit (register methods, hooks)**

---

## 3. Liskov Substitution Principle (LSP)

### Definition

> Objects of a superclass should be replaceable with objects of a subclass without breaking the application.

If class B is a subtype of class A, we should be able to replace A with B without disrupting the behavior of our program.

### Example from Codebase: Strategy Substitutability

**File**: `Source/Video/YouTube/Channel/src/workers/claiming_strategies.py`

```python
class BaseClaimStrategy(ABC):
    """Base class for claiming strategies."""
    
    @abstractmethod
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause."""
        pass

# All strategies are substitutable:
strategy: BaseClaimStrategy = FIFOStrategy()     # ✅ Works
strategy: BaseClaimStrategy = LIFOStrategy()     # ✅ Works
strategy: BaseClaimStrategy = PriorityStrategy() # ✅ Works

# Consumer code doesn't care which strategy:
order_by = strategy.get_order_by_clause()  # ✅ Always works
```

**Why this is good:**
- ✅ All strategies have identical interface
- ✅ No precondition strengthening (all strategies accept no parameters)
- ✅ No postcondition weakening (all return valid SQL strings)
- ✅ Behavioral substitutability maintained

### Example: Worker Substitutability

**File**: `Source/Video/YouTube/Channel/src/workers/base_worker.py`

```python
class BaseWorker(ABC):
    """Base worker with lifecycle management."""
    
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        """Process a claimed task - MUST be implemented by subclass."""
        pass

# Subclass implementation:
class YouTubeVideoWorker(BaseWorker):
    def process_task(self, task: Task) -> TaskResult:
        # YouTube-specific processing
        return TaskResult(success=True, data={...})

# Consumer code (in BaseWorker.run_once):
result = self.process_task(task)  # ✅ Works for ANY subclass
```

**Why this is good:**
- ✅ All workers return `TaskResult` (consistent contract)
- ✅ No exceptions thrown beyond base class contract
- ✅ Subclasses don't require additional preconditions
- ✅ Perfect behavioral substitutability

### Common LSP Violations (Anti-patterns)

❌ **Bad Example:**

```python
class Bird:
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def fly(self):
        raise NotImplementedError("Penguins can't fly!")  # ❌ Breaks LSP
```

✅ **Good Example:**

```python
class Bird(ABC):
    @abstractmethod
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        return "Flying"

class Penguin(Bird):
    def move(self):
        return "Swimming"  # ✅ Substitutable behavior
```

### Guidelines for LSP

1. **Subclasses should honor the base class contract**
2. **Don't strengthen preconditions (require more than base)**
3. **Don't weaken postconditions (return less than base promises)**
4. **Don't throw new exceptions not in base class contract**
5. **Preserve expected behavior, not just method signatures**

---

## 4. Interface Segregation Principle (ISP)

### Definition

> Clients should not be forced to depend on interfaces they don't use.

Many small, specific interfaces are better than one large, general-purpose interface.

### Example from Codebase: Minimal Protocol Interfaces

**File**: `Source/Video/YouTube/Channel/src/workers/__init__.py`

```python
class WorkerProtocol(Protocol):
    """Protocol (interface) that all workers must implement.
    
    Following Interface Segregation Principle (ISP) - minimal interface.
    Only essential methods, no unnecessary dependencies.
    """
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from the queue."""
        ...
    
    def process_task(self, task: Task) -> TaskResult:
        """Process a claimed task."""
        ...
    
    def report_result(self, task: Task, result: TaskResult) -> None:
        """Report task result."""
        ...
```

**Why this is good:**
- ✅ **Only 3 essential methods** - no bloat
- ✅ Each method serves a distinct purpose
- ✅ No "kitchen sink" interface with dozens of methods
- ✅ Clients only implement what they need

### Example: Focused Strategy Interface

**File**: `Source/Video/YouTube/Channel/src/workers/claiming_strategies.py`

```python
class ClaimingStrategy(Protocol):
    """Protocol for task claiming strategies.
    
    Following Interface Segregation Principle - minimal interface.
    Only the essential method needed for strategy selection.
    """
    
    def get_order_by_clause(self) -> str:
        """Get SQL ORDER BY clause for this strategy."""
        ...
```

**Why this is good:**
- ✅ **Single method interface** - ultra-minimal
- ✅ Strategies don't need to implement unnecessary methods
- ✅ Perfect example of ISP

### Example: Plugin Interface

**File**: `Source/Video/YouTube/src/plugins/__init__.py`

```python
class SourcePlugin(ABC):
    """Abstract base class for source scraper plugins.
    
    Follows the Interface Segregation Principle (ISP) by providing
    a minimal interface that all source plugins must implement.
    """
    
    @abstractmethod
    def scrape(self) -> List[IdeaInspiration]:
        """Scrape ideas from the source."""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source."""
        pass
    
    def format_tags(self, tags: List[str]) -> List[str]:
        """Format tags (optional utility method with default implementation)."""
        return [tag.strip() for tag in tags if tag.strip()]
```

**Why this is good:**
- ✅ Only **2 required methods** (scrape, get_source_name)
- ✅ One **optional utility method** with default implementation
- ✅ Plugins aren't forced to implement unused methods

### Common ISP Violations (Anti-patterns)

❌ **Bad Example:**

```python
class GodInterface(ABC):
    """Too many methods - forces implementations to provide unused methods."""
    
    @abstractmethod
    def scrape(self): pass
    
    @abstractmethod
    def save_to_database(self): pass  # ❌ Not all plugins need this
    
    @abstractmethod
    def send_to_api(self): pass       # ❌ Not all plugins need this
    
    @abstractmethod
    def validate_api_key(self): pass   # ❌ Not all plugins need this
    
    @abstractmethod
    def schedule_task(self): pass      # ❌ Not all plugins need this
    # ... 20 more methods
```

✅ **Good Example (segregated interfaces):**

```python
class SourcePlugin(ABC):
    """Minimal interface for scraping."""
    @abstractmethod
    def scrape(self): pass

class PersistablePlugin(ABC):
    """Optional interface for plugins that persist data."""
    @abstractmethod
    def save_to_database(self): pass

class APIPlugin(ABC):
    """Optional interface for plugins that use APIs."""
    @abstractmethod
    def validate_api_key(self): pass
```

### Guidelines for ISP

1. **Keep interfaces small and focused**
2. **Split large interfaces into smaller, cohesive ones**
3. **Use Python Protocols for flexible interfaces**
4. **Provide default implementations for optional methods**
5. **Clients should only depend on methods they use**

---

## 5. Dependency Inversion Principle (DIP)

### Definition

> High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details. Details should depend on abstractions.

This principle encourages depending on interfaces/protocols rather than concrete implementations, enabling flexibility and testability.

### Example from Codebase: Dependency Injection

**File**: `Source/Video/YouTube/Channel/src/workers/base_worker.py`

```python
class BaseWorker(ABC):
    """Base worker class providing common functionality.
    
    Follows Dependency Inversion Principle (DIP):
    - Depends on abstractions (Config, Database)  ← DIP
    - Dependencies injected via constructor        ← DIP
    """
    
    def __init__(
        self,
        worker_id: str,
        queue_db_path: str,
        config: Config,           # ← Injected dependency
        results_db: Database,     # ← Injected dependency
        strategy: str = "LIFO",
        max_iterations: Optional[int] = None,
        poll_interval: float = 5.0,
    ):
        self.worker_id = worker_id
        self.config = config
        self.results_db = results_db
        self.strategy = strategy
        # ...
```

**Why this is good:**
- ✅ Dependencies are **injected**, not created internally
- ✅ Depends on abstractions (`Config`, `Database`)
- ✅ Testable: can inject mock dependencies
- ✅ Flexible: can swap implementations

### Example: Strategy Injection

**File**: `Source/Video/YouTube/Channel/src/workers/base_worker.py`

```python
def claim_task(self) -> Optional[Task]:
    """Claim a task using configured strategy."""
    try:
        # Get strategy dynamically (depends on abstraction)
        strategy_obj = get_strategy(self.strategy)
        order_by = strategy_obj.get_order_by_clause()
        # ...
```

**Why this is good:**
- ✅ Strategy selected at runtime
- ✅ Worker depends on `ClaimingStrategy` abstraction
- ✅ No hard-coded concrete strategy class
- ✅ Strategy pattern enables DIP

### Example: Plugin System

**File**: `Source/Video/YouTube/src/plugins/__init__.py`

```python
# High-level code depends on SourcePlugin abstraction:
def collect_ideas(plugin: SourcePlugin) -> List[IdeaInspiration]:
    """Collect ideas from any source plugin."""
    return plugin.scrape()  # ← Depends on abstraction, not concrete class

# Usage with different implementations:
ideas1 = collect_ideas(YouTubePlugin(config))        # ✅
ideas2 = collect_ideas(YouTubeChannelPlugin(config)) # ✅
ideas3 = collect_ideas(RedditPlugin(config))         # ✅ (future)
```

**Why this is good:**
- ✅ High-level code (`collect_ideas`) depends on abstraction (`SourcePlugin`)
- ✅ Low-level implementations depend on same abstraction
- ✅ Inversion of dependency achieved

### Common DIP Violations (Anti-patterns)

❌ **Bad Example:**

```python
class BadWorker:
    def __init__(self):
        # ❌ Creates its own dependencies (concrete classes)
        self.config = Config()
        self.database = SQLiteDatabase("/path/to/db.sqlite")
        self.logger = FileLogger("/path/to/log.txt")
        self.strategy = LIFOStrategy()  # ❌ Hard-coded strategy
```

✅ **Good Example:**

```python
class GoodWorker:
    def __init__(
        self,
        config: Config,         # ✅ Injected (can be any Config implementation)
        database: Database,     # ✅ Injected (can be any Database implementation)
        logger: Logger,         # ✅ Injected (can be any Logger implementation)
        strategy: str = "LIFO", # ✅ String -> resolved to strategy instance
    ):
        self.config = config
        self.database = database
        self.logger = logger
        # Strategy resolved dynamically from abstraction
```

### Guidelines for DIP

1. **Inject dependencies via constructor (Dependency Injection)**
2. **Depend on abstractions (ABC, Protocol), not concrete classes**
3. **Use factory patterns to create concrete instances**
4. **Pass interfaces/protocols as type hints**
5. **Invert the dependency: high-level defines interface, low-level implements it**

---

## Additional Design Principles

### DRY (Don't Repeat Yourself)

**Definition**: Every piece of knowledge should have a single, unambiguous representation in the system.

**Examples from codebase:**
- ✅ Shared base classes: `BaseWorker`, `BaseClaimStrategy`, `SourcePlugin`
- ✅ Utility functions: `db_utils.py` provides reusable database functions
- ✅ Configuration centralization: Single `Config` class for all configuration

### KISS (Keep It Simple, Stupid)

**Definition**: Systems work best if they are kept simple rather than made complex.

**Examples from codebase:**
- ✅ Simple data classes: `Task`, `TaskResult` are plain dataclasses
- ✅ Minimal interfaces: `ClaimingStrategy` has 1 method
- ✅ Clear naming: `FIFOStrategy`, `claim_task()`, `process_task()`

### YAGNI (You Aren't Gonna Need It)

**Definition**: Don't add functionality until it's actually needed.

**Examples from codebase:**
- ✅ No premature abstractions: Code adds abstractions only when needed
- ✅ Focused implementations: Each class does what's needed, nothing more
- ✅ No unused features: All code serves a clear purpose

### Composition Over Inheritance

**Definition**: Favor object composition over class inheritance for code reuse.

**Examples from codebase:**
- ✅ Strategy pattern: Strategies composed into worker, not inherited
- ✅ Database injection: Database composed into worker
- ✅ Limited inheritance depth: Most hierarchies are 2 levels max

---

## Applying SOLID in Your Code

### Checklist for New Code

When writing new code, ask yourself:

#### Single Responsibility
- [ ] Does this class have only one reason to change?
- [ ] Can I describe its purpose in one sentence without using "and"?
- [ ] Is business logic separated from infrastructure?

#### Open/Closed
- [ ] Can I add new behavior without modifying this class?
- [ ] Am I using abstract base classes or Protocols?
- [ ] Are extension points clearly defined?

#### Liskov Substitution
- [ ] Can subclasses be used wherever the base class is expected?
- [ ] Do subclasses honor the base class contract?
- [ ] Are there any unexpected exceptions or behaviors?

#### Interface Segregation
- [ ] Is this interface as small as possible?
- [ ] Do all implementations use all methods?
- [ ] Should this be split into multiple interfaces?

#### Dependency Inversion
- [ ] Are dependencies injected rather than created?
- [ ] Am I depending on abstractions rather than concrete classes?
- [ ] Can I easily swap implementations for testing?

### Code Review Questions

When reviewing code, check:

1. **SRP**: Does each class have a single, well-defined responsibility?
2. **OCP**: Can new features be added without modifying existing code?
3. **LSP**: Are subclasses truly substitutable for their base classes?
4. **ISP**: Are interfaces minimal and focused?
5. **DIP**: Are dependencies injected and abstracted?

### Refactoring Anti-patterns

Watch for these common violations:

- ❌ God classes with too many responsibilities
- ❌ Concrete dependencies in constructors
- ❌ Large interfaces with many methods
- ❌ Subclasses that break base class assumptions
- ❌ Modifying existing classes to add features

### Learning Resources

- Review the [SOLID Architecture Review](../issues/done/Developer10/001-SOLID_ARCHITECTURE_REVIEW.md) for real examples
- Study `Source/Video/YouTube/Channel/src/workers/` for exemplary SOLID code
- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system-level design
- See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines

---

## Summary

SOLID principles create maintainable, flexible, and testable code:

| Principle | Key Idea | Benefit |
|-----------|----------|---------|
| **SRP** | One reason to change | Easy to understand and maintain |
| **OCP** | Open for extension, closed for modification | Add features without breaking existing code |
| **LSP** | Subclasses substitutable for base classes | Polymorphism works correctly |
| **ISP** | Small, focused interfaces | No unnecessary dependencies |
| **DIP** | Depend on abstractions, inject dependencies | Flexible, testable architecture |

**Remember**: These principles work together. Following one often helps you follow others.

**Next Steps**:
1. Read the [Architecture Guide](./ARCHITECTURE.md)
2. Review the [Code Review Guidelines](./CODE_REVIEW_GUIDELINES.md) (coming soon)
3. Study exemplary code in `Source/Video/YouTube/Channel/src/workers/`
4. Apply these principles in your own code

---

**Last Updated**: 2025-11-14  
**Related Documents**: 
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [CODE_REVIEW_GUIDELINES.md](./CODE_REVIEW_GUIDELINES.md) (coming soon)
