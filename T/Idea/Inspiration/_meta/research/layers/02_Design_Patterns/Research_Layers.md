# SOLID Principles and Design Guidelines for PrismQ.T.Idea.Inspiration

## Overview

This document provides comprehensive guidance on applying SOLID principles and avoiding common design pitfalls in the PrismQ.T.Idea.Inspiration codebase. It emphasizes practical patterns for maintainable, extensible software while avoiding the fragility that comes from deep inheritance hierarchies and tight coupling.

## Table of Contents

1. [SOLID Principles Overview](#solid-principles-overview)
2. [Avoiding Pitfalls: Deep Inheritance and Tight Coupling](#avoiding-pitfalls-deep-inheritance-and-tight-coupling)
3. [Practical Guidelines for PrismQ](#practical-guidelines-for-prismq)
4. [Code Examples](#code-examples)
5. [Refactoring Strategies](#refactoring-strategies)

---

## SOLID Principles Overview

### Single Responsibility Principle (SRP)
**"A class should have one, and only one, reason to change."**

Each class or module should focus on a single responsibility or concern. This makes code easier to understand, test, and maintain.

**Example from PrismQ:**
```python
# ✅ Good: Single responsibility
class CategoryClassifier:
    """Only handles content classification."""
    def classify(self, title: str, description: str) -> str:
        # Classification logic only
        pass

# ❌ Bad: Multiple responsibilities
class CategoryClassifierAndStorage:
    """Handles both classification AND storage."""
    def classify(self, title: str) -> str:
        pass
    
    def save_to_database(self, data: dict) -> None:
        pass  # Storage is a separate concern!
```

### Open/Closed Principle (OCP)
**"Software entities should be open for extension, but closed for modification."**

Design your code so that new functionality can be added without modifying existing code. Use abstraction and polymorphism.

**Example from PrismQ:**
```python
# ✅ Good: Open for extension via strategy pattern
class BaseAudioClient(ABC):
    @abstractmethod
    def get_audio_metadata(self, audio_id: str) -> AudioMetadata:
        pass

class SpotifyClient(BaseAudioClient):
    def get_audio_metadata(self, audio_id: str) -> AudioMetadata:
        # Spotify-specific implementation
        pass

class PodcastClient(BaseAudioClient):
    def get_audio_metadata(self, audio_id: str) -> AudioMetadata:
        # Podcast-specific implementation
        pass
```

### Liskov Substitution Principle (LSP)
**"Subtypes must be substitutable for their base types."**

Any code that works with a base class should work correctly with any of its derived classes without knowing the difference.

**Example from PrismQ:**
```python
# ✅ Good: Proper substitution
def process_audio(client: BaseAudioClient, audio_id: str) -> AudioMetadata:
    """Works with any BaseAudioClient implementation."""
    return client.get_audio_metadata(audio_id)

# Works with any implementation
spotify_client = SpotifyClient(client_id="...", client_secret="...")
podcast_client = PodcastClient()

metadata1 = process_audio(spotify_client, "track_123")
metadata2 = process_audio(podcast_client, "feed_url")
```

### Interface Segregation Principle (ISP)
**"Clients should not be forced to depend on interfaces they don't use."**

Use focused, minimal interfaces rather than large, monolithic ones. In Python, use Protocols for this.

**Example from PrismQ:**
```python
# ✅ Good: Focused protocols
from typing import Protocol

class Searchable(Protocol):
    """Minimal interface for searchable clients."""
    def search(self, query: str, limit: int) -> List[Any]:
        ...

class Fetchable(Protocol):
    """Minimal interface for content fetching."""
    def fetch_metadata(self, content_id: str) -> Any:
        ...

# ❌ Bad: Fat interface forcing unnecessary methods
class MegaInterface(Protocol):
    def search(self, query: str) -> List[Any]: ...
    def fetch_metadata(self, id: str) -> Any: ...
    def upload(self, data: bytes) -> None: ...  # Not all clients need this!
    def delete(self, id: str) -> None: ...       # Not all clients need this!
```

### Dependency Inversion Principle (DIP)
**"Depend on abstractions, not on concretions."**

High-level modules should not depend on low-level modules. Both should depend on abstractions. Use dependency injection.

**Example from PrismQ:**
```python
# ✅ Good: Depends on abstraction (Config, Database)
class BaseWorker(ABC):
    def __init__(self, config: Config, results_db: Database):
        self.config = config
        self.results_db = results_db

# Dependencies injected at runtime
config = Config.load()
database = Database(config.db_path)
worker = ConcreteWorker(config, database)

# ❌ Bad: Creates dependencies internally
class BadWorker:
    def __init__(self):
        self.config = Config.load()  # Hard-coded dependency
        self.db = Database("hardcoded.db")  # Hard-coded dependency
```

---

## Avoiding Pitfalls: Deep Inheritance and Tight Coupling

Even with well-thought-out layered design, there are critical pitfalls to watch for. These anti-patterns can make your codebase fragile, hard to understand, and resistant to change.

### 1. Overly Deep Inheritance Hierarchies

**The Problem:**

Deep inheritance hierarchies (4+ levels) become fragile and confusing. As stressed in architectural best practices, **shallow hierarchies (2-3 levels maximum) are easier to manage** and align with human cognitive limits for comprehending relationships.

**Why It's Bad:**
- **Fragility**: Changes to base classes ripple through many levels
- **Complexity**: Hard to understand the full behavior of a deeply nested class
- **Maintenance**: Finding where behavior is defined becomes a treasure hunt
- **Testing**: Testing becomes exponentially harder with each level
- **Cognitive Load**: Human brains struggle to track more than 2-3 levels of abstraction

**Detection Warning Signs:**
- You're adding a fourth or fifth layer of subclasses
- You have to jump through multiple files to understand one method's behavior
- Method names include level indicators like `super_base_`, `abstract_base_`, etc.
- You're frequently using `super().super()` patterns
- You find yourself creating intermediate abstract classes just to share small bits of code

**Example of Deep Inheritance (AVOID):**
```python
# ❌ BAD: Too deep (5 levels!)
class BaseClient(ABC):
    """Level 1: Base client"""
    pass

class HTTPClient(BaseClient):
    """Level 2: HTTP-specific"""
    pass

class RESTClient(HTTPClient):
    """Level 3: REST-specific"""
    pass

class AuthenticatedRESTClient(RESTClient):
    """Level 4: With authentication"""
    pass

class RateLimitedAuthenticatedRESTClient(AuthenticatedRESTClient):
    """Level 5: With rate limiting - TOO DEEP!"""
    pass
```

**Refactored Solution:**
```python
# ✅ GOOD: Shallow hierarchy with composition (2 levels)
class BaseClient(ABC):
    """Level 1: Base abstraction"""
    def __init__(self, rate_limiter: RateLimiter, authenticator: Authenticator):
        self.rate_limiter = rate_limiter  # Composition
        self.authenticator = authenticator  # Composition

class SpotifyClient(BaseClient):
    """Level 2: Concrete implementation"""
    def get_data(self, resource_id: str) -> Dict:
        self.authenticator.ensure_valid_token()
        self.rate_limiter.wait_if_needed()
        return self._fetch(resource_id)
```

**When to Refactor:**
- If you notice you're adding a fourth layer, **stop and reconsider**
- The hierarchy might be trying to handle too many dimensions of variation
- These dimensions could be better handled with:
  - **Strategy Pattern**: For varying algorithms
  - **Composition**: For combining behaviors
  - **Decorator Pattern**: For adding responsibilities dynamically
  - **Dependency Injection**: For configurable behavior

**Key Principle:**
Always question if an "is-a" relationship truly holds. If it's a stretch or feels forced, **do not force it via inheritance**. Use composition instead.

### 2. Fragile Base Class Problem

**The Problem:**

In deep hierarchies, base classes often carry too much responsibility. A change in a base class method can have unintended consequences on subclasses (which might have relied on specific behavior).

**Why It's Bad:**
- **Hidden Dependencies**: Subclasses silently depend on base class implementation details
- **Brittle Code**: Small changes in the base break multiple subclasses
- **Testing Nightmare**: You must test all subclasses when base classes change
- **Violation of OCP**: Modifying base classes to add features breaks Open/Closed Principle

**Mitigation Strategies:**

1. **Keep Base Classes Small and Focused**
   ```python
   # ✅ Good: Minimal base class
   class BaseAudioClient(ABC):
       """Small, focused base class with clear contract."""
       
       @abstractmethod
       def get_audio_metadata(self, audio_id: str) -> AudioMetadata:
           """Single abstract method with clear purpose."""
           pass
       
       @abstractmethod
       def search_audio(self, query: str, limit: int) -> List[AudioMetadata]:
           """Another focused abstract method."""
           pass
   ```

2. **Document Expected Behaviors Clearly**
   ```python
   class BaseWorker(ABC):
       """Base worker for task processing.
       
       Subclass Contract:
       - Must implement process_task() to handle specific task type
       - Can override _on_task_start() and _on_task_complete() for hooks
       - Should NOT override run() or _claim_task() (template method pattern)
       - Base class handles: polling, claiming, heartbeats, error handling
       - Subclass handles: task-specific processing logic only
       
       Template Method Pattern:
       - run() orchestrates the workflow (DO NOT OVERRIDE)
       - process_task() is the extension point (MUST IMPLEMENT)
       """
       
       def run(self) -> None:
           """Template method - DO NOT OVERRIDE."""
           while self.running:
               task = self._claim_task()
               if task:
                   self._on_task_start(task)
                   result = self.process_task(task)  # Extension point
                   self._on_task_complete(task, result)
       
       @abstractmethod
       def process_task(self, task: Task) -> TaskResult:
           """Extension point - MUST IMPLEMENT in subclass."""
           pass
   ```

3. **Use Template Method Pattern Carefully**
   - Clearly delineate what can vary (abstract methods)
   - Document what should NOT be overridden
   - Keep the template method simple and stable

4. **Test Base Class Changes Against All Subclasses**
   ```python
   # In test suite:
   class BaseWorkerTests:
       """Tests that apply to ALL worker implementations."""
       
       @pytest.fixture(params=[
           YouTubeWorker,
           SpotifyWorker,
           PodcastWorker,
       ])
       def worker_class(self, request):
           """Parametrize tests across all worker implementations."""
           return request.param
       
       def test_worker_lifecycle(self, worker_class):
           """Ensure all workers follow lifecycle contract."""
           worker = worker_class(config, db)
           # Test common behavior
   ```

**Warning Signs of Fragile Base Classes:**
- Subclasses override base methods in ad-hoc ways
- Subclasses need to call `super()` in complex patterns
- Changes to base class break multiple subclasses
- You're afraid to modify the base class
- Documentation says "don't touch this"

### 3. Circular Dependencies

**The Problem:**

When higher-level modules depend on lower-level modules, and lower-level modules also depend on higher-level modules, you create circular dependencies. This violates proper layering and makes the system fragile.

**Why It's Bad:**
- **Import Errors**: Python import system can fail with circular imports
- **Tight Coupling**: Modules become inseparable
- **Testing Difficulty**: Can't test modules in isolation
- **Maintenance**: Can't upgrade one layer without affecting others

**Proper Layering Principles:**

```
┌─────────────────────────┐
│   Application Layer     │  ← High-level: Orchestration, workflows
│   (YouTube Worker)      │
└───────────┬─────────────┘
            │ depends on ↓
┌───────────┴─────────────┐
│   Domain Layer          │  ← Mid-level: Business logic
│   (Audio Clients)       │
└───────────┬─────────────┘
            │ depends on ↓
┌───────────┴─────────────┐
│   Infrastructure Layer  │  ← Low-level: Database, HTTP, utilities
│   (Config, Database)    │
└─────────────────────────┘
```

**Rules for Acyclic Dependencies:**
1. **Higher layers can depend on lower layers** ✅
2. **Lower layers CANNOT depend on higher layers** ❌
3. **Same-level layers should communicate via interfaces** ✅
4. **Lower layers should know nothing about higher layers** ✅
5. **Ensure the layered structure remains acyclic** - no circular paths ✅

**Example of Circular Dependency (AVOID):**
```python
# ❌ BAD: Circular dependency

# video_processor.py (High-level)
from .database import Database
from .youtube_context import YouTubeContext

class VideoProcessor:
    def __init__(self, db: Database):
        self.db = db
    
    def process(self, video_id: str) -> None:
        # High-level orchestration
        context = YouTubeContext(...)
        self.db.save_with_context(context)  # Passing high-level to low-level!

# database.py (Low-level)
from .youtube_context import YouTubeContext  # ❌ Low-level importing high-level!

class Database:
    def save_with_context(self, context: YouTubeContext) -> None:
        # Database now depends on high-level YouTubeContext!
        pass
```

**Refactored Solution:**
```python
# ✅ GOOD: Dependency inversion via abstraction

# database.py (Low-level - no knowledge of high-level)
from typing import Dict, Any

class Database:
    def save(self, data: Dict[str, Any]) -> None:
        """Generic save - accepts any dictionary."""
        # Low-level storage logic
        pass

# video_processor.py (High-level)
from .database import Database

class VideoProcessor:
    def __init__(self, db: Database):
        self.db = db
    
    def process(self, video_id: str) -> None:
        # High-level creates data structure
        data = {
            "video_id": video_id,
            "platform": "youtube",
            "processed_at": datetime.now()
        }
        # High-level calls low-level with simple data
        self.db.save(data)
```

**How to Enforce Acyclic Dependencies:**

1. **Use Layer Interfaces**
   ```python
   # ✅ Lower layer defines interface
   class StorageProtocol(Protocol):
       def save(self, data: Dict[str, Any]) -> None: ...
       def load(self, id: str) -> Dict[str, Any]: ...
   
   # ✅ Higher layer depends on protocol, not concrete implementation
   class VideoProcessor:
       def __init__(self, storage: StorageProtocol):
           self.storage = storage
   ```

2. **Don't Pass High-Level Objects to Low-Level Code**
   ```python
   # ❌ BAD
   def save_video_context(db: Database, context: YouTubeContext) -> None:
       db.save(context)  # Passing high-level to low-level
   
   # ✅ GOOD
   def save_video_context(db: Database, context: YouTubeContext) -> None:
       data = context.to_dict()  # Convert to primitive data
       db.save(data)  # Pass simple data structure
   ```

3. **Use Dependency Injection**
   - Inject dependencies from outside
   - Don't let modules create their own dependencies
   - Use factories or IoC containers for complex setups

**Verification:**
You should be able to upgrade or replace a lower layer without touching upper layers (as long as the interface is consistent).

### 4. Performance Considerations

**The Problem:**

Layering and abstraction can introduce overhead (function calls, object creation, etc.). While benefits usually outweigh costs, be mindful in performance-critical code.

**Guidelines:**

1. **Measure Before Optimizing**
   ```python
   # Use profiling to identify bottlenecks
   import cProfile
   import pstats
   
   profiler = cProfile.Profile()
   profiler.enable()
   # Run your code
   profiler.disable()
   stats = pstats.Stats(profiler)
   stats.sort_stats('cumulative')
   stats.print_stats(20)
   ```

2. **Allow Strategic Shortcuts (Documented)**
   ```python
   class DataProcessor:
       def process(self, data: List[Dict]) -> List[Dict]:
           """Standard processing with full validation."""
           return [self._validate_and_transform(item) for item in data]
       
       def process_trusted(self, data: List[Dict]) -> List[Dict]:
           """Fast path for pre-validated data.
           
           WARNING: Bypasses validation layer. Only use with data from
           trusted sources that have already been validated.
           
           Performance: ~3x faster than process() for large datasets.
           Use case: Processing data from our own database.
           """
           return [self._transform_only(item) for item in data]
   ```

3. **Encapsulate Optimizations**
   - Don't let optimizations spread throughout the codebase
   - Keep them isolated and documented
   - Make them optional/configurable

4. **Batch Operations**
   ```python
   # ✅ Efficient: Batch processing
   class AudioClient:
       def get_metadata_batch(self, audio_ids: List[str]) -> List[AudioMetadata]:
           """Fetch multiple items in one request."""
           return self._batch_api_call(audio_ids)
   
       def get_metadata(self, audio_id: str) -> AudioMetadata:
           """Single item - calls batch with one item."""
           return self.get_metadata_batch([audio_id])[0]
   ```

**Balance:**
- ✅ Prefer maintainability over premature optimization
- ✅ Profile before optimizing
- ✅ Document performance-critical code
- ❌ Don't sacrifice clean architecture without evidence
- ❌ Don't create hidden shortcuts that bypass safety checks

### 5. Resistance to Change (Rigid Layering)

**The Problem:**

A common pitfall is rigid layering that doesn't accommodate new requirements well. Architecture must evolve as the system grows.

**Guidelines:**

1. **Keep an Open Mind to Refactoring**
   - Architecture is **evolutionary**, not static
   - Revisit boundaries periodically
   - Refine based on usage patterns and pain points

2. **Recognize When to Adjust**
   ```python
   # Example: New requirement doesn't fit existing abstraction
   
   # Old: All sources return IdeaInspiration
   class BaseSource(ABC):
       @abstractmethod
       def fetch(self) -> List[IdeaInspiration]:
           pass
   
   # New: Script sources need different data structure
   # Option 1: Force it (BAD - square peg, round hole)
   class ScriptSource(BaseSource):
       def fetch(self) -> List[IdeaInspiration]:
           # Awkward conversion that loses information
           scripts = self._get_scripts()
           return [self._force_to_idea(s) for s in scripts]
   
   # Option 2: Adjust architecture (GOOD - adapt to reality)
   class BaseSource(ABC):
       @abstractmethod
       def fetch(self) -> List[Content]:  # More general type
           pass
   
   class IdeaSource(BaseSource):
       def fetch(self) -> List[IdeaInspiration]:
           pass
   
   class ScriptSource(BaseSource):
       def fetch(self) -> List[Script]:
           pass
   ```

3. **Introduce New Layers When Needed**
   - Don't force new concepts into existing layers
   - Better to add a layer than violate separation of concerns
   - Example: Adding a caching layer, transformation layer, etc.

4. **Recognize Pain Points**
   - If you're constantly working around the architecture, it's a sign
   - If new features always require major refactoring, reassess
   - If you're violating principles to add features, stop and redesign

5. **Document Evolution**
   ```markdown
   ## Architecture Decision Record: Adding Script Layer
   
   **Date**: 2025-11-14
   **Status**: Accepted
   
   **Context**: Script-based content sources don't fit IdeaInspiration model.
   
   **Decision**: Introduce parallel ScriptContent hierarchy instead of
   forcing scripts into IdeaInspiration.
   
   **Consequences**:
   - Positive: Cleaner abstraction, no forced conversions
   - Positive: Script-specific features can be added
   - Negative: Slightly more complex type handling
   - Mitigation: Use union types and shared protocols
   ```

**Key Principle:**
**It's better to adjust the architecture than to force a square peg into a round hole.** This prevents violations of separation of concerns and maintains system health.

---

## Practical Guidelines for PrismQ

### Inheritance Hierarchy Guidelines

1. **Maximum Depth: 2-3 Levels**
   - Level 1: Abstract base or protocol
   - Level 2: Concrete implementation
   - Level 3: Specialized variant (rarely needed)

2. **When to Use Inheritance**
   - ✅ True "is-a" relationships (Spotify **is an** AudioClient)
   - ✅ When behavior needs to be extended but not replaced
   - ✅ When using Template Method pattern appropriately
   - ❌ Just to reuse code (use composition instead)
   - ❌ When behavior needs to be mixed and matched (use composition)

3. **When to Use Composition**
   - ✅ "has-a" relationships (Worker **has a** Database)
   - ✅ Multiple dimensions of variation
   - ✅ Runtime behavior changes
   - ✅ Sharing behavior across unrelated classes

### Current PrismQ Architecture Analysis

**Audio Module** (Good Example - 2 Levels):
```
BaseAudioClient (ABC)          ← Level 1: Abstract base
├── SpotifyClient              ← Level 2: Concrete implementation
└── PodcastClient              ← Level 2: Concrete implementation
```
✅ **Status**: Excellent. Shallow hierarchy, clear responsibilities.

**Worker Module** (Good Example - 2 Levels):
```
BaseWorker (ABC)               ← Level 1: Abstract base with template method
├── YouTubeChannelWorker       ← Level 2: Concrete implementation
├── YouTubeVideoWorker         ← Level 2: Concrete implementation
└── SpotifyWorker              ← Level 2: Concrete implementation
```
✅ **Status**: Excellent. Uses Template Method pattern appropriately.

### Recommended Patterns for PrismQ

1. **Strategy Pattern for Algorithms**
   ```python
   # For varying algorithms/behaviors
   class TaskClaimingStrategy(Protocol):
       def select_task(self, tasks: List[Task]) -> Task:
           ...
   
   class FIFOStrategy:
       def select_task(self, tasks: List[Task]) -> Task:
           return tasks[0]  # First in, first out
   
   class LIFOStrategy:
       def select_task(self, tasks: List[Task]) -> Task:
           return tasks[-1]  # Last in, first out
   
   class Worker:
       def __init__(self, strategy: TaskClaimingStrategy):
           self.strategy = strategy  # Inject the algorithm
   ```

2. **Composition for Cross-Cutting Concerns**
   ```python
   # Compose behaviors instead of deep inheritance
   class AudioClient:
       def __init__(
           self,
           rate_limiter: RateLimiter,
           authenticator: Authenticator,
           cache: Cache,
           logger: Logger
       ):
           self.rate_limiter = rate_limiter
           self.authenticator = authenticator
           self.cache = cache
           self.logger = logger
       
       def fetch(self, resource_id: str) -> Dict:
           # Use composed components
           self.authenticator.ensure_valid()
           self.rate_limiter.wait_if_needed()
           
           if cached := self.cache.get(resource_id):
               return cached
           
           result = self._fetch_from_api(resource_id)
           self.cache.set(resource_id, result)
           return result
   ```

3. **Protocol-Based Design (ISP)**
   ```python
   # Use Python Protocols for interface segregation
   from typing import Protocol
   
   class Fetchable(Protocol):
       def fetch_metadata(self, id: str) -> Dict[str, Any]: ...
   
   class Searchable(Protocol):
       def search(self, query: str, limit: int) -> List[Dict]: ...
   
   # Client depends only on what it needs
   def process_search_results(client: Searchable, query: str) -> None:
       results = client.search(query, limit=10)
       # Process results
   ```

---

## Code Examples

### Example 1: Refactoring Deep Inheritance to Composition

**Before (Deep Inheritance - AVOID):**
```python
class BaseClient:
    def __init__(self):
        self.session = requests.Session()

class RateLimitedClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.rate_limit = 60
        self.requests = []

class AuthenticatedRateLimitedClient(RateLimitedClient):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key

class LoggingAuthenticatedRateLimitedClient(AuthenticatedRateLimitedClient):
    def __init__(self, api_key: str, logger: Logger):
        super().__init__(api_key)
        self.logger = logger

# 4 levels - too deep!
```

**After (Composition - PREFERRED):**
```python
@dataclass
class ClientConfig:
    """Configuration for client behavior."""
    rate_limit: int = 60
    timeout: int = 30
    retry_attempts: int = 3

class RateLimiter:
    """Handles rate limiting logic."""
    def __init__(self, limit_per_minute: int):
        self.limit = limit_per_minute
        self.requests = []
    
    def wait_if_needed(self) -> None:
        # Rate limiting logic
        pass

class Authenticator:
    """Handles authentication."""
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

class Client:
    """Composes behaviors instead of inheriting."""
    def __init__(
        self,
        config: ClientConfig,
        rate_limiter: RateLimiter,
        authenticator: Authenticator,
        logger: Logger
    ):
        self.config = config
        self.rate_limiter = rate_limiter
        self.authenticator = authenticator
        self.logger = logger
        self.session = requests.Session()
    
    def fetch(self, url: str) -> requests.Response:
        self.rate_limiter.wait_if_needed()
        headers = self.authenticator.get_headers()
        self.logger.info(f"Fetching {url}")
        return self.session.get(url, headers=headers)

# Factory for convenient creation
def create_authenticated_client(api_key: str) -> Client:
    config = ClientConfig()
    rate_limiter = RateLimiter(config.rate_limit)
    authenticator = Authenticator(api_key)
    logger = logging.getLogger(__name__)
    return Client(config, rate_limiter, authenticator, logger)
```

### Example 2: Avoiding Fragile Base Class

**Before (Fragile Base - AVOID):**
```python
class BaseWorker:
    """Big base class with lots of behavior."""
    
    def run(self) -> None:
        """Main loop - subclasses might override."""
        while self.running:
            task = self.get_task()  # Subclasses might override
            self.process(task)      # Subclasses override
            self.cleanup(task)      # Subclasses might override
    
    def get_task(self) -> Task:
        """Gets task - subclasses might override for custom logic."""
        return self.queue.pop()
    
    def cleanup(self, task: Task) -> None:
        """Cleanup - subclasses might override."""
        pass  # Does nothing by default

class ConcreteWorker(BaseWorker):
    def process(self, task: Task) -> None:
        # Must override
        pass
    
    def get_task(self) -> Task:
        # Override to add filtering
        task = super().get_task()
        return task if self.filter(task) else self.get_task()
    
    # Now changing BaseWorker.get_task() might break this!
```

**After (Template Method - PREFERRED):**
```python
class BaseWorker(ABC):
    """Clean base with Template Method pattern."""
    
    def run(self) -> None:
        """Template method - DO NOT OVERRIDE.
        
        Orchestrates the workflow with clear extension points.
        """
        while self.running:
            task = self._claim_task()           # Base handles claiming
            if task:
                self._on_task_start(task)       # Hook for subclasses
                result = self.process_task(task)  # EXTENSION POINT
                self._on_task_complete(result)  # Hook for subclasses
    
    def _claim_task(self) -> Optional[Task]:
        """Internal method - not meant to be overridden."""
        return self.queue.pop()
    
    def _on_task_start(self, task: Task) -> None:
        """Hook - subclasses can override for custom logic."""
        pass
    
    def _on_task_complete(self, result: TaskResult) -> None:
        """Hook - subclasses can override for custom logic."""
        pass
    
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        """Extension point - MUST be implemented by subclasses.
        
        This is where subclass-specific logic goes.
        """
        pass

class ConcreteWorker(BaseWorker):
    """Clean subclass with clear responsibility."""
    
    def process_task(self, task: Task) -> TaskResult:
        """Only implements task-specific logic."""
        # Process task
        return result
    
    def _on_task_start(self, task: Task) -> None:
        """Optional hook for additional startup logic."""
        self.logger.info(f"Starting task {task.id}")
```

### Example 3: Breaking Circular Dependencies

**Before (Circular Dependency - AVOID):**
```python
# worker.py
from .database import Database

class Worker:
    def __init__(self, db: Database):
        self.db = db
    
    def process(self) -> None:
        result = self.do_work()
        self.db.save_with_worker_context(self)  # Passes self to database!

# database.py
from .worker import Worker  # ❌ Circular import!

class Database:
    def save_with_worker_context(self, worker: Worker) -> None:
        # Database knows about Worker - circular dependency!
        data = {
            "worker_id": worker.worker_id,
            "result": worker.last_result
        }
        self._save(data)
```

**After (Dependency Inversion - PREFERRED):**
```python
# database.py (Low-level - no worker knowledge)
from typing import Dict, Any

class Database:
    """Generic database - no knowledge of Worker."""
    
    def save(self, data: Dict[str, Any]) -> None:
        """Accepts any dictionary."""
        self._save(data)

# worker.py (High-level)
from .database import Database

class Worker:
    def __init__(self, worker_id: str, db: Database):
        self.worker_id = worker_id
        self.db = db
    
    def process(self) -> None:
        result = self.do_work()
        
        # Worker creates the data structure
        data = {
            "worker_id": self.worker_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Passes simple data to database
        self.db.save(data)
```

---

## Refactoring Strategies

### Strategy 1: Extract Interface

When you have deep inheritance, extract common behavior into an interface/protocol.

```python
# Before: Deep inheritance
class Animal: pass
class Mammal(Animal): pass
class Dog(Mammal): pass

# After: Interface extraction
class Animal(Protocol):
    def make_sound(self) -> str: ...
    def move(self) -> None: ...

class Dog:  # Direct implementation
    def make_sound(self) -> str:
        return "Woof"
    
    def move(self) -> None:
        print("Walking on four legs")
```

### Strategy 2: Prefer Composition

Replace inheritance with composition when sharing behavior.

```python
# Before: Inheritance for code reuse
class LoggingMixin:
    def log(self, message: str) -> None:
        print(message)

class Worker(LoggingMixin):
    pass

# After: Composition
class Worker:
    def __init__(self, logger: Logger):
        self.logger = logger  # Composition
    
    def process(self) -> None:
        self.logger.log("Processing...")
```

### Strategy 3: Use Strategy Pattern

When subclasses only vary in one algorithm, use strategy pattern.

```python
# Before: Inheritance for algorithm variation
class BaseProcessor:
    def process(self, data: List) -> List:
        sorted_data = self.sort(data)
        return self.transform(sorted_data)
    
    def sort(self, data: List) -> List:
        raise NotImplementedError

class QuickSortProcessor(BaseProcessor):
    def sort(self, data: List) -> List:
        return quicksort(data)

# After: Strategy pattern
class SortStrategy(Protocol):
    def sort(self, data: List) -> List: ...

class QuickSort:
    def sort(self, data: List) -> List:
        return quicksort(data)

class Processor:
    def __init__(self, sort_strategy: SortStrategy):
        self.sort_strategy = sort_strategy
    
    def process(self, data: List) -> List:
        sorted_data = self.sort_strategy.sort(data)
        return self.transform(sorted_data)
```

### Strategy 4: Introduce Facade

Simplify complex hierarchies with a facade.

```python
# Complex hierarchy hidden behind simple interface
class AudioServiceFacade:
    """Simple interface hiding complex audio subsystem."""
    
    def __init__(self):
        self._spotify = SpotifyClient(...)
        self._podcast = PodcastClient(...)
        self._cache = Cache()
    
    def search(self, query: str, platform: str) -> List[AudioMetadata]:
        """Simple method hiding complexity."""
        if cached := self._cache.get(query):
            return cached
        
        if platform == "spotify":
            results = self._spotify.search(query)
        else:
            results = self._podcast.search(query)
        
        self._cache.set(query, results)
        return results
```

---

## Summary

### Key Takeaways

1. **Shallow Hierarchies (2-3 levels max)**
   - Easier to understand, test, and maintain
   - Align with human cognitive limits
   - Reduce fragility and cascading changes

2. **Composition Over Inheritance**
   - More flexible and maintainable
   - Avoids fragile base class problem
   - Allows runtime behavior changes

3. **Clear Abstractions**
   - Use protocols for interface segregation
   - Depend on abstractions, not concretions
   - Inject dependencies

4. **Acyclic Dependencies**
   - Higher layers depend on lower layers only
   - Lower layers use interfaces/protocols
   - No circular dependencies

5. **Evolutionary Architecture**
   - Be open to refactoring
   - Adjust architecture when it resists change
   - Document architectural decisions

### Design Checklist

Before implementing new features, ask:

- [ ] Does this follow Single Responsibility Principle?
- [ ] Is this "is-a" relationship genuine, or should I use composition?
- [ ] Will this create a 4th level of inheritance? (If yes, reconsider)
- [ ] Am I creating circular dependencies?
- [ ] Can subclasses truly substitute the base class?
- [ ] Is my base class small and focused?
- [ ] Have I documented the contract clearly?
- [ ] Can I test this in isolation?
- [ ] Will this be easy to change in the future?
- [ ] Am I forcing a square peg into a round hole?

### Resources

- **Martin Fowler**: [Refactoring](https://refactoring.com/)
- **Robert C. Martin**: Clean Architecture, SOLID Principles
- **Gang of Four**: Design Patterns
- **Python-Specific**: [Python Protocols](https://peps.python.org/pep-0544/)

---

**Last Updated**: 2025-11-14  
**Version**: 1.0  
**Maintainer**: PrismQ Architecture Team
# Best Practices for Layered Modular System Design

**Research Document**  
**Date**: 2025-11-14  
**Status**: Research Complete  
**Related**: See `ARCHITECTURE.md`, `SOLID_PRINCIPLES.md`, Developer10's SOLID Architecture Review

---

## Executive Summary

This document provides comprehensive guidance on designing layered modular systems that structure code into a hierarchy of modules, each responsible for a specific level of behavior. Using the PrismQ.T.Idea.Inspiration Source modules as reference implementations, we demonstrate how to apply layered architecture principles to achieve clear separation of concerns, high reusability, and ease of maintenance.

### Key Principles

1. **Clear Abstraction Layers** - Define focused interfaces at each level
2. **One Layer, One Responsibility** - Each layer handles a single concern
3. **Limited Coupling** - Depend on abstractions, not implementations
4. **Well-Designed Interfaces** - Keep contracts simple and stable

---

## 1. Overview: Layered Modular Architecture

### What is a Layered Modular System?

A layered modular system structures code into a **hierarchy of modules**, where each module is responsible for a specific level of behavior and abstraction. This creates a vertical stack of functionality, similar to the OSI networking model or a layered cake - each layer builds on the one below and provides services to the one above.

### Example Hierarchy in PrismQ.T.Idea.Inspiration

Consider the Source module hierarchy for video content:

```
┌─────────────────────────────────────────┐
│   Video (Individual)                    │  ← Concrete: YouTube Video, TikTok Video
│   - Scrape single video metadata        │     Handles platform-specific video details
│   - Parse video-specific fields         │
├─────────────────────────────────────────┤
│   YouTube Module                        │  ← Specialization: YouTube-specific logic
│   - YouTube authentication              │     Handles YouTube API, rate limits
│   - YouTube API integration             │
│   - YouTube data structures             │
├─────────────────────────────────────────┤
│   VideoSource Module                    │  ← Abstraction: Generic video operations
│   - Video format handling               │     Common video behaviors
│   - Video metadata extraction           │
│   - Video content processing            │
├─────────────────────────────────────────┤
│   Source Module (Base)                  │  ← Foundation: Core infrastructure
│   - HTTP client with retry logic        │     Shared by all source types
│   - Rate limiting                       │
│   - Authentication patterns             │
│   - Configuration management            │
└─────────────────────────────────────────┘
```

### Benefits of Layered Architecture

| Benefit | Description | Example |
|---------|-------------|---------|
| **Reusability** | Lower layers serve multiple upper layers | Base `Source` HTTP client used by Video, Audio, Text |
| **Maintainability** | Changes isolated to specific layers | Update rate limiting in base without touching YouTube logic |
| **Testability** | Each layer tested independently | Mock lower layers to test upper layers |
| **Understandability** | Clear responsibilities at each level | Know where to look for specific functionality |
| **Extensibility** | Add new platforms without changing base | Add TikTok by extending VideoSource, not modifying Source |

---

## 2. Structuring Modules and Class Hierarchies

### 2.1 Define Clear Abstraction Layers

**Principle**: Identify common functionality and define an interface or abstract base class for each layer of abstraction.

#### Implementation Pattern

Each layer should:
1. **Define a clear contract** (interface/abstract base class)
2. **Implement common behaviors** shared by all subclasses
3. **Declare abstract methods** that subclasses must implement
4. **Follow the contract** of its parent layer

#### Example from PrismQ.T.Idea.Inspiration: Audio Source Hierarchy

```python
# Layer 1: Base Source (Foundation)
class BaseSource(ABC):
    """Base interface for all content sources."""
    
    def __init__(self, api_key: Optional[str] = None,
                 rate_limit_per_minute: int = 60,
                 retry_attempts: int = 3,
                 timeout_seconds: int = 30):
        """Common initialization for all sources."""
        self.api_key = api_key
        self.rate_limit_per_minute = rate_limit_per_minute
        self.timeout_seconds = timeout_seconds
        self.session = self._create_session(retry_attempts)
        self._request_times: List[float] = []
    
    def _create_session(self, retry_attempts: int) -> requests.Session:
        """Create HTTP session with retry logic - SHARED BY ALL SOURCES."""
        session = requests.Session()
        retry_strategy = Retry(
            total=retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _rate_limit_wait(self) -> None:
        """Implement rate limiting - SHARED BY ALL SOURCES."""
        now = time.time()
        self._request_times = [t for t in self._request_times if now - t < 60]
        if len(self._request_times) >= self.rate_limit_per_minute:
            oldest = self._request_times[0]
            wait_time = 60 - (now - oldest) + 0.1
            if wait_time > 0:
                time.sleep(wait_time)
                now = time.time()
                self._request_times = [t for t in self._request_times if now - t < 60]
        self._request_times.append(time.time())
    
    @abstractmethod
    def fetch(self, identifier: str) -> Dict[str, Any]:
        """Fetch content by identifier - MUST BE IMPLEMENTED."""
        pass


# Layer 2: AudioSource (Specialization for Audio)
class AudioSource(BaseSource):
    """Base class for audio content sources."""
    
    @abstractmethod
    def get_audio_metadata(self, audio_id: str) -> AudioMetadata:
        """Fetch metadata for audio - AUDIO-SPECIFIC CONTRACT."""
        pass
    
    @abstractmethod
    def search_audio(self, query: str, limit: int = 10) -> List[AudioMetadata]:
        """Search for audio content - AUDIO-SPECIFIC CONTRACT."""
        pass
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration - SHARED AUDIO UTILITY."""
        # Common duration parsing logic for all audio sources
        pass


# Layer 3: SpotifyClient (Concrete Implementation)
class SpotifyClient(AudioSource):
    """Spotify-specific implementation."""
    
    BASE_URL = "https://api.spotify.com/v1"
    
    def __init__(self, client_id: str, client_secret: str, **kwargs):
        """Spotify-specific initialization."""
        super().__init__(**kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
    
    def _authenticate(self) -> str:
        """Spotify OAuth - SPOTIFY-SPECIFIC."""
        # Spotify authentication logic
        pass
    
    def get_audio_metadata(self, audio_id: str) -> AudioMetadata:
        """Fetch Spotify track metadata - IMPLEMENTS AUDIO CONTRACT."""
        self._rate_limit_wait()  # ← Uses base layer
        headers = {"Authorization": f"Bearer {self._access_token}"}
        response = self.session.get(  # ← Uses base layer session
            f"{self.BASE_URL}/tracks/{audio_id}",
            headers=headers,
            timeout=self.timeout_seconds
        )
        response.raise_for_status()
        data = response.json()
        
        # Transform Spotify data to common AudioMetadata
        return AudioMetadata(
            source_id=data["id"],
            title=data["name"],
            artist=data["artists"][0]["name"],
            duration=self._parse_duration(data["duration_ms"]),  # ← Uses audio layer
            # ...
        )
    
    def search_audio(self, query: str, limit: int = 10) -> List[AudioMetadata]:
        """Search Spotify - IMPLEMENTS AUDIO CONTRACT."""
        # Spotify-specific search implementation
        pass
```

#### Why This Structure Works

| Layer | Responsibility | Used By | Dependencies |
|-------|----------------|---------|--------------|
| `BaseSource` | HTTP, rate limiting, retry logic | All sources | None (stdlib + requests) |
| `AudioSource` | Audio metadata parsing, common audio utilities | Spotify, Podcast clients | `BaseSource` |
| `SpotifyClient` | Spotify API integration, OAuth | Application code | `AudioSource` |

**Key Insight**: Each layer adds **one level of specialization** without duplicating lower-level concerns.

---

### 2.2 One Layer, One Responsibility

**Principle**: Each module/class should handle a single level of behavior and not stray into the duties of other layers.

#### The "Adjacent Layer" Rule

A layer should **only interact** with:
- The layer **directly below** it (to use services)
- The layer **directly above** it (to provide services)

A layer should **never**:
- Skip layers to call functionality two levels down
- Reach up to call functionality in layers above
- Duplicate functionality that exists in another layer

#### ✅ Good Example: Proper Layer Interaction

```python
class YouTubeVideoClient(VideoSource):
    """YouTube video scraper - interacts with VideoSource and BaseSource only."""
    
    def get_video_metadata(self, video_id: str) -> VideoMetadata:
        """Fetch video metadata."""
        # ✅ Uses parent layer's method (VideoSource)
        self._rate_limit_wait()
        
        # ✅ Uses base layer's session (BaseSource)
        response = self.session.get(
            f"https://www.googleapis.com/youtube/v3/videos",
            params={"id": video_id, "key": self.api_key},
            timeout=self.timeout_seconds  # ✅ Uses base layer's config
        )
        response.raise_for_status()
        
        # ✅ Uses video layer's parsing utilities (VideoSource)
        raw_data = response.json()
        return self._parse_video_metadata(raw_data)  # VideoSource method
```

**Why this works**:
- Uses `_rate_limit_wait()` from base layer ✅
- Uses `session` from base layer ✅
- Uses `_parse_video_metadata()` from video layer ✅
- Doesn't reimplement HTTP client logic ✅
- Doesn't bypass layers ✅

#### ❌ Bad Example: Layer Violations

```python
class BadYouTubeVideoClient(VideoSource):
    """Example of INCORRECT layer interaction - DO NOT DO THIS."""
    
    def get_video_metadata(self, video_id: str) -> VideoMetadata:
        """Fetch video metadata."""
        # ❌ VIOLATION: Reimplements rate limiting (belongs in BaseSource)
        if len(self._request_times) >= self.rate_limit_per_minute:
            time.sleep(60)
        self._request_times.append(time.time())
        
        # ❌ VIOLATION: Creates new HTTP session instead of using base layer
        import requests
        session = requests.Session()
        response = session.get(
            f"https://www.googleapis.com/youtube/v3/videos",
            params={"id": video_id}
        )
        
        # ❌ VIOLATION: Parses video data inline instead of using video layer utilities
        data = response.json()
        return VideoMetadata(
            video_id=data["items"][0]["id"],
            title=data["items"][0]["snippet"]["title"],
            # ... inline parsing that should be in VideoSource
        )
```

**Problems**:
- Duplicates rate limiting logic (violates DRY) ❌
- Creates new HTTP session (wastes resources, loses retry logic) ❌
- Inline parsing makes code harder to maintain ❌
- Can't reuse parsing logic for other YouTube sources ❌
- Changes to rate limiting require updates in multiple places ❌

#### Layer Responsibility Matrix

| Layer | Should Handle | Should NOT Handle |
|-------|---------------|-------------------|
| **BaseSource** | HTTP, retry, rate limiting, auth patterns | Platform-specific API calls, content parsing |
| **VideoSource** | Video format handling, metadata parsing | HTTP client, platform-specific auth |
| **YouTubeSource** | YouTube API calls, YouTube auth | HTTP retry logic, generic video parsing |
| **YouTubeVideoClient** | Single video scraping | HTTP session management, rate limiting |

---

### 2.3 Limited Coupling Between Layers

**Principle**: Upper layers should depend on **abstractions** of lower layers, not concrete implementations.

#### Dependency Inversion in Action

The **Dependency Inversion Principle (DIP)** is crucial for layered architecture:
- High-level modules should not depend on low-level modules
- Both should depend on abstractions
- Abstractions should not depend on details
- Details should depend on abstractions

#### Example: Using Protocols for Abstraction

```python
from typing import Protocol, Dict, Any

# Define abstraction (interface) for HTTP client
class HTTPClientProtocol(Protocol):
    """Protocol defining the contract for HTTP operations."""
    
    def get(self, url: str, **kwargs) -> Any:
        """Perform GET request."""
        ...
    
    def post(self, url: str, **kwargs) -> Any:
        """Perform POST request."""
        ...


# Define abstraction for rate limiter
class RateLimiterProtocol(Protocol):
    """Protocol defining the contract for rate limiting."""
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit reached."""
        ...
    
    def record_request(self) -> None:
        """Record a request."""
        ...


# Upper layer depends on abstractions, not concrete implementations
class VideoSource(ABC):
    """Video source that depends on abstractions."""
    
    def __init__(
        self,
        http_client: HTTPClientProtocol,  # ← Depends on protocol, not concrete class
        rate_limiter: RateLimiterProtocol,  # ← Depends on protocol, not concrete class
    ):
        self.http_client = http_client
        self.rate_limiter = rate_limiter
    
    def fetch_video(self, video_id: str) -> Dict[str, Any]:
        """Fetch video using injected dependencies."""
        self.rate_limiter.wait_if_needed()  # ← Uses abstraction
        response = self.http_client.get(f"/videos/{video_id}")  # ← Uses abstraction
        self.rate_limiter.record_request()
        return response.json()
```

#### Benefits of Abstraction-Based Coupling

1. **Testability**: Can inject mock implementations for testing

```python
class MockHTTPClient:
    """Mock HTTP client for testing."""
    def get(self, url: str, **kwargs):
        return {"video_id": "123", "title": "Test Video"}

class MockRateLimiter:
    """Mock rate limiter for testing."""
    def wait_if_needed(self) -> None:
        pass  # No waiting in tests
    
    def record_request(self) -> None:
        pass  # No recording in tests

# Test with mocks
video_source = VideoSource(
    http_client=MockHTTPClient(),
    rate_limiter=MockRateLimiter()
)
```

2. **Flexibility**: Can swap implementations without changing upper layers

```python
# Production: Use real implementations
video_source_prod = VideoSource(
    http_client=RequestsHTTPClient(),
    rate_limiter=TokenBucketRateLimiter(rate=100)
)

# Development: Use alternative implementations
video_source_dev = VideoSource(
    http_client=CachedHTTPClient(),  # Caches responses
    rate_limiter=NoOpRateLimiter()   # No rate limiting in dev
)
```

3. **Decoupling**: Upper and lower layers can evolve independently

```python
# Can change HTTP client implementation without touching VideoSource
class AIOHTTPClient:  # New async implementation
    async def get(self, url: str, **kwargs):
        # Async implementation
        pass

# VideoSource doesn't need to change - still works with new implementation
```

#### Real-World Example from PrismQ.T.Idea.Inspiration

The `BaseWorker` class demonstrates excellent dependency inversion:

```python
class BaseWorker(ABC):
    """Base worker with dependency injection."""
    
    def __init__(
        self,
        config: Config,              # ← Injected dependency
        results_db: Database,        # ← Injected dependency
        plugin: SourcePlugin,        # ← Injected dependency (abstraction!)
        strategy: str = "LIFO",
    ):
        self.config = config
        self.results_db = results_db
        self.plugin = plugin  # Worker depends on SourcePlugin interface
        self.strategy = ClaimingStrategy.get_strategy(strategy)
    
    def process_task(self, task: Task) -> TaskResult:
        """Process task using injected plugin."""
        # Worker doesn't know if plugin is YouTube, Reddit, or TikTok
        # It only knows plugin follows SourcePlugin interface
        result = self.plugin.execute(task.parameters)  # ← Uses abstraction
        return result
```

**Key Points**:
- `BaseWorker` doesn't depend on `YouTubePlugin`, `RedditPlugin`, etc.
- `BaseWorker` depends on the `SourcePlugin` **interface**
- Any plugin implementing `SourcePlugin` can be injected
- Worker and plugins can evolve independently

---

### 2.4 Layer Interface Design

**Principle**: Carefully design the interface of each module layer to be simple, focused, and easy to use.

#### Interface Design Guidelines

1. **Minimal Interface** - Include only what the layer truly needs
2. **Stable Contracts** - Avoid frequent interface changes
3. **Clear Naming** - Methods should be self-documenting
4. **Consistent Patterns** - Similar operations should have similar signatures
5. **Focused Responsibility** - Each method does one thing well

#### Example: Well-Designed Layer Interfaces

```python
# BaseSource - Foundation Layer Interface
class BaseSource(ABC):
    """
    Base interface for all content sources.
    
    Provides:
    - HTTP session management
    - Rate limiting
    - Authentication patterns
    - Retry logic
    """
    
    @abstractmethod
    def fetch(self, identifier: str) -> Dict[str, Any]:
        """
        Fetch content by identifier.
        
        Args:
            identifier: Platform-specific content ID
            
        Returns:
            Raw content data as dictionary
        """
        pass
    
    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the service."""
        pass


# VideoSource - Video Layer Interface
class VideoSource(BaseSource):
    """
    Video content source interface.
    
    Extends BaseSource with video-specific operations.
    """
    
    @abstractmethod
    def get_video_metadata(self, video_id: str) -> VideoMetadata:
        """
        Fetch metadata for a video.
        
        Args:
            video_id: Platform-specific video identifier
            
        Returns:
            Standardized VideoMetadata object
        """
        pass
    
    @abstractmethod
    def search_videos(self, query: str, limit: int = 10) -> List[VideoMetadata]:
        """
        Search for videos.
        
        Args:
            query: Search query string
            limit: Maximum results (default: 10)
            
        Returns:
            List of VideoMetadata objects
        """
        pass


# YouTubeSource - Platform Layer Interface
class YouTubeSource(VideoSource):
    """
    YouTube-specific video source.
    
    Provides YouTube-specific methods while implementing
    the generic VideoSource interface.
    """
    
    def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 50
    ) -> List[VideoMetadata]:
        """
        Get videos from a YouTube channel.
        
        YouTube-specific method - not in VideoSource interface.
        
        Args:
            channel_id: YouTube channel identifier
            max_results: Maximum videos to fetch
            
        Returns:
            List of VideoMetadata objects
        """
        pass
    
    def get_trending_videos(
        self,
        region_code: str = "US",
        category_id: Optional[str] = None
    ) -> List[VideoMetadata]:
        """
        Get trending videos.
        
        YouTube-specific method.
        
        Args:
            region_code: ISO 3166-1 alpha-2 country code
            category_id: Optional YouTube category filter
            
        Returns:
            List of VideoMetadata objects
        """
        pass
```

#### Interface Design Checklist

When designing a layer interface, ask:

- [ ] **Does each method have a single, clear purpose?**
- [ ] **Are method names descriptive and consistent?**
- [ ] **Are parameters minimal and necessary?**
- [ ] **Do return types match across similar methods?**
- [ ] **Is the interface stable (unlikely to change frequently)?**
- [ ] **Can the interface be easily mocked for testing?**
- [ ] **Does the interface expose implementation details?** (Should be NO)
- [ ] **Do subclasses need all methods in the interface?** (ISP check)

#### Good vs. Bad Interface Design

**❌ Bad Interface Design**:

```python
class BadVideoSource(ABC):
    """Example of poor interface design - TOO MANY responsibilities."""
    
    @abstractmethod
    def get_video_and_download_and_process_and_analyze(
        self,
        video_id: str,
        download_path: str,
        process_audio: bool,
        extract_frames: bool,
        analyze_sentiment: bool,
        upload_to_s3: bool,
        s3_bucket: str,
        # ... many more parameters
    ) -> Dict[str, Any]:
        """
        Does everything! (WRONG - violates SRP)
        
        Problems:
        - Too many responsibilities in one method
        - Too many parameters (hard to use)
        - Mixes concerns (fetching, downloading, processing, analyzing, uploading)
        - Difficult to test
        - Forces all implementations to handle all concerns
        """
        pass
```

**✅ Good Interface Design**:

```python
class GoodVideoSource(ABC):
    """Example of good interface design - focused, composable."""
    
    @abstractmethod
    def get_video_metadata(self, video_id: str) -> VideoMetadata:
        """Fetch video metadata - ONE responsibility."""
        pass
    
    @abstractmethod
    def search_videos(self, query: str, limit: int = 10) -> List[VideoMetadata]:
        """Search for videos - ONE responsibility."""
        pass

# Separate concerns into separate classes
class VideoDownloader:
    """Handles video downloading - separate responsibility."""
    def download(self, video_url: str, output_path: str) -> Path:
        pass

class VideoProcessor:
    """Handles video processing - separate responsibility."""
    def extract_audio(self, video_path: Path) -> Path:
        pass
    
    def extract_frames(self, video_path: Path) -> List[Path]:
        pass

# Compose functionality as needed
def complete_video_workflow(video_id: str):
    """Compose separate concerns into workflow."""
    source = YouTubeSource()
    downloader = VideoDownloader()
    processor = VideoProcessor()
    
    metadata = source.get_video_metadata(video_id)  # ← Focused interface
    video_path = downloader.download(metadata.url, "/tmp")  # ← Separate concern
    audio_path = processor.extract_audio(video_path)  # ← Separate concern
```

---

## 3. Applying Design Patterns

### 3.1 Strategy Pattern for Layer Flexibility

The Strategy pattern allows algorithms (strategies) to be selected at runtime, enabling flexible behavior without modifying the layer that uses them.

#### Example: Task Claiming Strategies

```python
from typing import Protocol, List

# Strategy interface (abstraction)
class ClaimingStrategy(Protocol):
    """Protocol for task claiming strategies."""
    
    def select_task(self, available_tasks: List[Task]) -> Optional[Task]:
        """Select a task from available tasks."""
        ...

# Concrete strategies (implementations)
class FIFOStrategy:
    """First In, First Out strategy."""
    def select_task(self, available_tasks: List[Task]) -> Optional[Task]:
        return min(available_tasks, key=lambda t: t.created_at) if available_tasks else None

class LIFOStrategy:
    """Last In, First Out strategy."""
    def select_task(self, available_tasks: List[Task]) -> Optional[Task]:
        return max(available_tasks, key=lambda t: t.created_at) if available_tasks else None

class PriorityStrategy:
    """Priority-based strategy."""
    def select_task(self, available_tasks: List[Task]) -> Optional[Task]:
        return max(available_tasks, key=lambda t: t.priority) if available_tasks else None

# Layer uses strategy abstraction
class TaskManager:
    """Task manager that uses claiming strategy."""
    
    def __init__(self, strategy: ClaimingStrategy):
        self.strategy = strategy  # ← Depends on abstraction
    
    def claim_next_task(self) -> Optional[Task]:
        """Claim next task using configured strategy."""
        available = self._get_available_tasks()
        return self.strategy.select_task(available)  # ← Uses abstraction

# Usage: Strategy can be swapped at runtime
manager_fifo = TaskManager(FIFOStrategy())
manager_lifo = TaskManager(LIFOStrategy())
manager_priority = TaskManager(PriorityStrategy())
```

### 3.2 Factory Pattern for Layer Instantiation

The Factory pattern encapsulates object creation, allowing upper layers to request objects without knowing their concrete types.

#### Example: Worker Factory

```python
from typing import Dict, Type

class WorkerFactory:
    """Factory for creating workers based on task type."""
    
    _workers: Dict[str, Type[BaseWorker]] = {}
    
    @classmethod
    def register(cls, task_type: str, worker_class: Type[BaseWorker]) -> None:
        """Register a worker class for a task type."""
        cls._workers[task_type] = worker_class
    
    @classmethod
    def create_worker(
        cls,
        task_type: str,
        config: Config,
        database: Database,
        **kwargs
    ) -> BaseWorker:
        """
        Create a worker for the given task type.
        
        Upper layers don't need to know concrete worker classes.
        """
        if task_type not in cls._workers:
            raise ValueError(f"Unknown task type: {task_type}")
        
        worker_class = cls._workers[task_type]
        return worker_class(config=config, results_db=database, **kwargs)

# Register workers (typically done at module initialization)
WorkerFactory.register("youtube_video", YouTubeVideoWorker)
WorkerFactory.register("youtube_channel", YouTubeChannelWorker)
WorkerFactory.register("reddit_post", RedditPostWorker)

# Usage: Upper layer doesn't need to know concrete classes
def process_task(task: Task, config: Config, db: Database):
    """Process task without knowing worker implementation."""
    worker = WorkerFactory.create_worker(
        task_type=task.task_type,
        config=config,
        database=db
    )
    return worker.process_task(task)  # ← Polymorphism in action
```

### 3.3 Template Method Pattern for Layer Workflows

The Template Method pattern defines the skeleton of an algorithm in a base class, allowing subclasses to override specific steps.

#### Example: BaseWorker Template

```python
class BaseWorker(ABC):
    """Base worker defining the task processing template."""
    
    def run(self) -> None:
        """
        Template method defining the workflow.
        
        This is the algorithm skeleton - subclasses customize steps.
        """
        self.setup()  # ← Hook method
        
        try:
            while True:
                task = self.claim_task()  # ← Common behavior
                if not task:
                    break
                
                try:
                    result = self.process_task(task)  # ← Must be implemented
                    self.report_success(task, result)  # ← Common behavior
                except Exception as e:
                    self.handle_error(task, e)  # ← Hook method
        finally:
            self.cleanup()  # ← Hook method
    
    def setup(self) -> None:
        """Hook: Setup before processing (override if needed)."""
        pass
    
    def claim_task(self) -> Optional[Task]:
        """Common: Claim a task using strategy."""
        return self.task_queue.claim_next_task()
    
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        """Abstract: Must be implemented by subclasses."""
        pass
    
    def report_success(self, task: Task, result: TaskResult) -> None:
        """Common: Report successful task completion."""
        self.task_queue.complete_task(task.id, result)
    
    def handle_error(self, task: Task, error: Exception) -> None:
        """Hook: Error handling (override for custom behavior)."""
        self.task_queue.fail_task(task.id, str(error))
    
    def cleanup(self) -> None:
        """Hook: Cleanup after processing (override if needed)."""
        pass

# Subclass only implements/overrides what's needed
class YouTubeVideoWorker(BaseWorker):
    """YouTube video worker - implements specific processing."""
    
    def process_task(self, task: Task) -> TaskResult:
        """Implement YouTube-specific processing."""
        video_id = task.parameters["video_id"]
        metadata = self.plugin.get_video_metadata(video_id)
        return TaskResult(data=metadata)
    
    def setup(self) -> None:
        """Override: YouTube-specific setup."""
        super().setup()
        self.plugin.authenticate()  # YouTube-specific
    
    # Other methods (claim_task, report_success, etc.) inherited from base
```

---

## 4. Integration with PrismQ Ecosystem

### 4.1 Current Layered Structure in PrismQ.T.Idea.Inspiration

The PrismQ.T.Idea.Inspiration repository already demonstrates excellent layered architecture:

```
┌────────────────────────────────────────────────────────┐
│  Application Layer (CLI, API, Web Control Panel)       │
├────────────────────────────────────────────────────────┤
│  Workers & Plugins (Concrete Implementations)          │
│  - YouTubeVideoWorker, YouTubeChannelWorker            │
│  - RedditPostWorker, HackerNewsWorker                  │
│  - SpotifyClient, PodcastClient                        │
├────────────────────────────────────────────────────────┤
│  Domain Layer (Source-Specific Logic)                  │
│  - VideoSource, AudioSource, TextSource                │
│  - YouTube module, Reddit module, Audio module         │
├────────────────────────────────────────────────────────┤
│  Core/Infrastructure Layer (Shared Utilities)          │
│  - BaseWorker, BaseSource, SourcePlugin                │
│  - TaskManager client, ContentFunnel                   │
│  - Database, Config, Logging                           │
├────────────────────────────────────────────────────────┤
│  Data/Model Layer (Shared Data Structures)             │
│  - IdeaInspiration model                               │
│  - Task, TaskResult, VideoMetadata, AudioMetadata      │
└────────────────────────────────────────────────────────┘
```

### 4.2 Cross-Module Layering

Different PrismQ modules can share layers while maintaining independence:

```
PrismQ.T.Idea.Inspiration (this repo)
├── Source Module
│   ├── Infrastructure: BaseSource, HTTP client, rate limiting
│   ├── Domain: VideoSource, AudioSource, TextSource
│   └── Concrete: YouTube, Reddit, Spotify, etc.
│
├── Classification Module
│   ├── Infrastructure: BaseClassifier, feature extraction
│   ├── Domain: StoryDetector, CategoryClassifier
│   └── Concrete: ML models, rule-based classifiers
│
└── Scoring Module
    ├── Infrastructure: BaseScorer, metric computation
    ├── Domain: EngagementScorer, QualityScorer
    └── Concrete: YouTube scorer, Reddit scorer, etc.

PrismQ.IdeaCollector (separate repo)
└── Uses Source Module infrastructure
    └── Shares base layers but may have different upper layers

StoryGenerator (separate repo)
└── Uses Model layer
    └── Depends on IdeaInspiration model but not Source implementation
```

### 4.3 Naming Conventions Across Modules

Consistent naming helps identify layer responsibilities:

| Layer | Naming Pattern | Examples |
|-------|----------------|----------|
| **Base/Abstract** | `Base*`, `*Protocol`, `Abstract*` | `BaseSource`, `WorkerProtocol`, `AbstractScorer` |
| **Domain** | `*Source`, `*Manager`, `*Handler` | `VideoSource`, `TaskManager`, `ErrorHandler` |
| **Concrete** | `*Client`, `*Worker`, `*Plugin` | `YouTubeClient`, `VideoWorker`, `YouTubePlugin` |
| **Utilities** | `*Utils`, `*Helper`, `*Config` | `db_utils`, `DateHelper`, `Config` |

---

## 5. Testing Layered Architecture

### 5.1 Layer-Specific Testing Strategy

Each layer should have targeted tests:

```python
# Infrastructure Layer Tests (BaseSource)
class TestBaseSource:
    """Test common infrastructure behaviors."""
    
    def test_rate_limiting_enforced(self):
        """Verify rate limiting works across all sources."""
        source = ConcreteSourceForTesting()
        # Make requests exceeding rate limit
        # Assert: Requests are delayed appropriately
    
    def test_retry_logic_on_server_error(self):
        """Verify retry logic for 5xx errors."""
        # Mock HTTP 500 response
        # Assert: Request retried 3 times

# Domain Layer Tests (VideoSource)
class TestVideoSource:
    """Test video-specific behaviors."""
    
    def test_video_metadata_parsing(self):
        """Verify video metadata standardization."""
        source = MockVideoSource()
        metadata = source.get_video_metadata("test_id")
        # Assert: Returns VideoMetadata with required fields
    
    def test_duration_parsing_formats(self):
        """Verify duration parsing handles various formats."""
        # Test ISO 8601, seconds, HH:MM:SS formats

# Concrete Layer Tests (YouTubeVideoClient)
class TestYouTubeVideoClient:
    """Test YouTube-specific implementation."""
    
    def test_youtube_api_integration(self):
        """Verify YouTube API calls work correctly."""
        client = YouTubeVideoClient(api_key="test")
        # Mock YouTube API response
        # Assert: Correct API endpoint called with proper parameters
    
    def test_youtube_authentication(self):
        """Verify YouTube OAuth flow."""
        # Test YouTube-specific authentication
```

### 5.2 Testing Through Abstractions

Test upper layers by mocking lower layers:

```python
from unittest.mock import Mock

class TestWorkerWithMockedDependencies:
    """Test worker by mocking lower layers."""
    
    def test_worker_processes_task_successfully(self):
        """Test worker logic without real database/API calls."""
        # Mock dependencies (lower layers)
        mock_config = Mock(spec=Config)
        mock_database = Mock(spec=Database)
        mock_plugin = Mock(spec=SourcePlugin)
        mock_plugin.execute.return_value = {"video_id": "123", "title": "Test"}
        
        # Create worker with mocked dependencies
        worker = YouTubeVideoWorker(
            config=mock_config,
            results_db=mock_database,
            plugin=mock_plugin
        )
        
        # Test worker logic
        task = Task(task_type="youtube_video", parameters={"video_id": "123"})
        result = worker.process_task(task)
        
        # Assertions
        assert result.success
        mock_plugin.execute.assert_called_once_with({"video_id": "123"})
```

### 5.3 Integration Testing Across Layers

```python
class TestLayerIntegration:
    """Test that layers work together correctly."""
    
    def test_full_video_fetch_pipeline(self):
        """Test complete flow from worker to YouTube API."""
        # Use real config and database (test environment)
        config = TestConfig()
        database = TestDatabase()
        
        # Use real YouTube client with test API key
        youtube_client = YouTubeVideoClient(api_key=config.youtube_test_key)
        plugin = YouTubePlugin(client=youtube_client)
        
        # Create worker with real dependencies
        worker = YouTubeVideoWorker(
            config=config,
            results_db=database,
            plugin=plugin
        )
        
        # Test with real video ID (use public test video)
        task = Task(task_type="youtube_video", parameters={"video_id": "dQw4w9WgXcQ"})
        result = worker.process_task(task)
        
        # Assert: Full pipeline works end-to-end
        assert result.success
        assert "title" in result.data
        
        # Verify data stored in database
        stored_idea = database.get_idea(result.data["source_id"])
        assert stored_idea is not None
```

---

## 6. Common Pitfalls and Solutions

### 6.1 Pitfall: Layer Leakage

**Problem**: Implementation details from lower layers leak into upper layers.

**Example**:
```python
# ❌ Layer leakage - YouTubeWorker knows about HTTP details
class BadYouTubeWorker(BaseWorker):
    def process_task(self, task: Task):
        # ❌ Worker shouldn't know about HTTP status codes
        try:
            result = self.plugin.execute(task.parameters)
        except requests.HTTPError as e:
            if e.response.status_code == 429:  # ❌ HTTP detail leaked
                # Handle rate limiting at wrong layer
                time.sleep(60)
```

**Solution**: Handle implementation details at the appropriate layer.

```python
# ✅ No leakage - each layer handles its concerns
class YouTubePlugin(SourcePlugin):
    """Handles HTTP details at plugin layer."""
    
    def execute(self, parameters: Dict) -> Dict:
        try:
            return self.client.get_video_metadata(parameters["video_id"])
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                # ✅ Rate limiting handled at plugin layer
                self._handle_rate_limit()
                return self.client.get_video_metadata(parameters["video_id"])
            raise

class YouTubeWorker(BaseWorker):
    """Worker doesn't know about HTTP details."""
    
    def process_task(self, task: Task):
        # ✅ Worker just calls plugin, doesn't handle HTTP errors
        result = self.plugin.execute(task.parameters)
        return TaskResult(success=True, data=result)
```

### 6.2 Pitfall: God Layers

**Problem**: One layer trying to do everything.

**Example**:
```python
# ❌ God class - does too much
class BadSource:
    def fetch_and_parse_and_store_and_analyze(self, id: str):
        # Fetching (OK)
        data = self._http_get(id)
        # Parsing (OK)
        parsed = self._parse(data)
        # Storing (WRONG LAYER - should be separate)
        self._database.store(parsed)
        # Analysis (WRONG LAYER - should be separate)
        sentiment = self._analyze_sentiment(parsed)
        # Scoring (WRONG LAYER - should be separate)
        score = self._calculate_score(parsed, sentiment)
        return score
```

**Solution**: Split responsibilities across appropriate layers.

```python
# ✅ Separation of concerns
class GoodSource:
    """Source layer: Only fetching and parsing."""
    def fetch_video_metadata(self, video_id: str) -> VideoMetadata:
        data = self._http_get(video_id)
        return self._parse(data)

class IdeaRepository:
    """Repository layer: Only data storage."""
    def store_idea(self, idea: IdeaInspiration) -> None:
        self._database.insert(idea)

class ContentAnalyzer:
    """Analysis layer: Only content analysis."""
    def analyze_sentiment(self, content: str) -> SentimentResult:
        return self._ml_model.predict(content)

class ContentScorer:
    """Scoring layer: Only scoring logic."""
    def calculate_score(self, idea: IdeaInspiration, sentiment: SentimentResult) -> float:
        return self._scoring_algorithm(idea, sentiment)

# Orchestrate in application layer
def process_video(video_id: str):
    source = GoodSource()
    repository = IdeaRepository()
    analyzer = ContentAnalyzer()
    scorer = ContentScorer()
    
    metadata = source.fetch_video_metadata(video_id)  # ← Focused
    idea = create_idea_from_metadata(metadata)
    repository.store_idea(idea)  # ← Focused
    sentiment = analyzer.analyze_sentiment(idea.content)  # ← Focused
    score = scorer.calculate_score(idea, sentiment)  # ← Focused
```

### 6.3 Pitfall: Layer Skipping

**Problem**: Upper layers bypass intermediate layers to call lower layers directly.

**Example**:
```python
# ❌ Layer skipping
class BadYouTubeWorker(BaseWorker):
    def process_task(self, task: Task):
        # ❌ Skips VideoSource layer, calls HTTP directly
        import requests
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"id": task.parameters["video_id"]}
        )
        return response.json()
```

**Solution**: Always go through intermediate layers.

```python
# ✅ Proper layer usage
class GoodYouTubeWorker(BaseWorker):
    def __init__(self, plugin: YouTubePlugin, **kwargs):
        super().__init__(**kwargs)
        self.plugin = plugin  # ← Goes through plugin layer
    
    def process_task(self, task: Task):
        # ✅ Uses plugin layer, which uses video layer, which uses HTTP layer
        result = self.plugin.execute(task.parameters)
        return TaskResult(success=True, data=result)
```

### 6.4 Pitfall: Circular Dependencies

**Problem**: Layer A depends on Layer B, which depends on Layer A.

**Example**:
```python
# ❌ Circular dependency
# video_source.py
from .youtube_client import YouTubeClient  # ← Depends on lower layer

class VideoSource:
    def get_client(self):
        return YouTubeClient()  # Creates concrete class

# youtube_client.py
from .video_source import VideoSource  # ❌ Depends on upper layer!

class YouTubeClient:
    def get_all_videos(self):
        source = VideoSource()  # ❌ Circular dependency
        return source.fetch_all()
```

**Solution**: Use dependency injection and abstractions to break cycles.

```python
# ✅ No circular dependencies
# video_source.py
class VideoSource(ABC):
    """Abstract base - doesn't depend on concrete implementations."""
    @abstractmethod
    def get_video_metadata(self, video_id: str) -> VideoMetadata:
        pass

# youtube_client.py
class YouTubeClient(VideoSource):
    """Concrete class - depends on abstraction, not other concrete classes."""
    def get_video_metadata(self, video_id: str) -> VideoMetadata:
        # Implementation without depending on other concrete classes
        pass

# Usage: Dependency injection breaks potential cycles
def process_videos(client: VideoSource):  # ← Depends on abstraction
    metadata = client.get_video_metadata("123")
    # Process metadata

# No circular dependency:
# VideoSource (abstract) ← YouTubeClient (concrete)
# process_videos depends on VideoSource (abstract)
```

---

## 7. Best Practices Summary

### 7.1 Layer Design Checklist

When designing a new layer:

- [ ] **Single Responsibility**: Does the layer have one clear purpose?
- [ ] **Clear Interface**: Are method signatures simple and well-documented?
- [ ] **Minimal Coupling**: Does the layer depend on abstractions?
- [ ] **No Layer Skipping**: Does the layer only call adjacent layers?
- [ ] **Testable**: Can the layer be tested with mocked dependencies?
- [ ] **Reusable**: Can the layer be used by multiple upper layers?
- [ ] **Extensible**: Can new implementations be added without modifying the layer?
- [ ] **No Leakage**: Are implementation details hidden from upper layers?

### 7.2 SOLID Principles Application

All layered designs should follow SOLID principles:

| Principle | Application in Layers |
|-----------|----------------------|
| **Single Responsibility** | Each layer has one reason to change |
| **Open/Closed** | New layers/implementations can be added without modifying existing layers |
| **Liskov Substitution** | Concrete implementations can replace abstractions without breaking behavior |
| **Interface Segregation** | Layer interfaces are minimal and focused |
| **Dependency Inversion** | Layers depend on abstractions, not concrete implementations |

### 7.3 Code Quality Metrics

Measure layer quality:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Layer Cohesion** | High | All methods in layer related to same concern |
| **Layer Coupling** | Low | Layer depends on few external abstractions |
| **Interface Size** | Small | Abstract methods count ≤ 10 |
| **Implementation Complexity** | Moderate | Concrete methods ≤ 50 lines each |
| **Test Coverage** | >80% | Unit tests for each layer |
| **Dependency Direction** | Downward | Upper layers depend on lower layers only |

---

## 8. Further Reading

### Internal Documentation

- `_meta/docs/ARCHITECTURE.md` - System architecture overview
- `Source/_meta/issues/new/Developer10/001-SOLID_ARCHITECTURE_REVIEW.md` - SOLID principles review (10/10 score)
- `.github/copilot-instructions.md` - Repository-wide design principles

### External References

1. **Software Engineering Stack Exchange**: [Abstraction Layers](https://softwareengineering.stackexchange.com) - Defining clear interfaces for each layer
2. **Bitloops Blog**: [Layered Architecture Principles](https://bitloops.com) - Layer interaction patterns and the "one layer, one responsibility" principle
3. **Clean Architecture** (Robert C. Martin) - Comprehensive guide to layered architecture
4. **Domain-Driven Design** (Eric Evans) - Domain layer design patterns
5. **Patterns of Enterprise Application Architecture** (Martin Fowler) - Layer patterns and best practices

### Related Design Patterns

- **Strategy Pattern**: Flexible behavior selection
- **Factory Pattern**: Object creation abstraction
- **Template Method Pattern**: Algorithm skeleton definition
- **Repository Pattern**: Data access layer abstraction
- **Dependency Injection**: Loose coupling between layers

---

## 9. Conclusion

Layered modular system design provides a robust foundation for building maintainable, extensible, and testable software. By following the principles outlined in this document:

1. **Define clear abstraction layers** with focused interfaces
2. **Maintain single responsibility** per layer
3. **Minimize coupling** through dependency inversion
4. **Design stable interfaces** that serve as contracts

The PrismQ.T.Idea.Inspiration repository demonstrates these principles in practice, achieving a 10/10 SOLID compliance score and serving as a reference implementation for the PrismQ ecosystem.

### Key Takeaways

- **Layers are about vertical organization** - Each layer adds one level of abstraction
- **Adjacent layer rule** - Only interact with layers directly above/below
- **Depend on abstractions** - Use Protocols and abstract base classes
- **Keep interfaces minimal** - Follow Interface Segregation Principle
- **Test each layer independently** - Mock lower layers to test upper layers
- **Avoid common pitfalls** - No layer leakage, god layers, or layer skipping

By applying these practices consistently across the PrismQ ecosystem, we ensure that code remains maintainable, understandable, and extensible as the system grows.

---

**Document Status**: Research Complete  
**Application**: All PrismQ modules (IdeaInspiration, IdeaCollector, StoryGenerator, etc.)  
**Next Steps**: Apply these principles when designing new modules or refactoring existing code  
**Review Date**: 2025-11-14

# Layered System Design - Research Compilation

## Overview

This document consolidates comprehensive research on design patterns and principles for building flexible, maintainable, and extensible layered systems in the PrismQ.T.Idea.Inspiration project. It combines insights from Strategy Pattern (Composition-Based) research and SOLID Principles to guide architectural decision-making.

**Research Date**: November 2025  
**Focus**: Layered system architecture, composition-based design, and SOLID principles

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Strategy Pattern for Layered Systems](#strategy-pattern-for-layered-systems)
3. [Composition Over Inheritance](#composition-over-inheritance)
4. [SOLID Principles in Layered Architecture](#solid-principles-in-layered-architecture)
5. [Pattern Comparison and Selection Guide](#pattern-comparison-and-selection-guide)
6. [Practical Applications in PrismQ](#practical-applications-in-prismq)
7. [Best Practices](#best-practices)
8. [References](#references)

---

## Executive Summary

### Key Findings

**Strategy Pattern (Composition-Based)**
- Encapsulates interchangeable behaviors into separate classes composed with context objects
- Avoids combinatorial subclass explosion (e.g., one `ContentScraper` with injected strategies vs. `YouTubeDBScraper`, `YouTubeFileScraper`, etc.)
- Enables runtime behavior swapping and reduces coupling
- Best for: runtime behavior changes, avoiding subclass explosion, replacing conditional logic

**Composition Over Inheritance**
- Keep inheritance hierarchies shallow (2-3 levels maximum)
- Extract varying behaviors to strategy classes or composed helpers
- Use "has-a" relationships instead of stretching "is-a" relationships
- Best for: optional features, avoiding deep hierarchies, cross-cutting concerns

**SOLID Principles**
- **SRP**: Each class has one reason to change (single responsibility)
- **OCP**: Open for extension, closed for modification (use abstractions)
- **LSP**: Subtypes must be substitutable for base types without breaking functionality
- **ISP**: Use focused, minimal interfaces (Python Protocols)
- **DIP**: Depend on abstractions, inject dependencies through constructors

### Pattern Selection Guide

| Pattern | Use When | Primary Benefit |
|---------|----------|----------------|
| **Strategy** | Runtime behavior changes needed | Flexibility and swappable algorithms |
| **Composition** | Deep hierarchies or optional features | Loose coupling and reusability |
| **Template Method** | Stable algorithm with variant steps | Code reuse and enforced workflow |

---

## Strategy Pattern for Layered Systems

### Definition

The Strategy pattern encapsulates interchangeable behaviors (algorithms or tactics) into separate classes, which are then composed with the context object. Instead of using inheritance to override parts of an algorithm, the context class holds a reference to a strategy interface and delegates work to it.

**Key Principle**: Favor composition over inheritance by delegating behavior to strategy objects.

### When to Use in Layered Systems

1. **Multi-Layer Scraper**: Different extraction methods (HTML parsing vs. API fetching) and storage methods (DB vs. File)
2. **Data Processing Pipeline**: Varying input formats (XML, CSV, JSON) with independent validation/output handling
3. **Module Behavior Configuration**: Swapping algorithms without modifying module code
4. **Avoiding Combinatorial Explosion**: Multiple independent variations that would create too many subclasses

### Architecture Example: Multi-Layer Content Scraper

```python
from typing import Protocol

# Strategy Interfaces
class ExtractionStrategy(Protocol):
    """Strategy for extracting data from different sources."""
    def extract(self, source_url: str) -> dict:
        """Extract data from the given source."""
        pass

class StorageStrategy(Protocol):
    """Strategy for storing extracted data."""
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
    
    Instead of: YouTubeDBScraper, YouTubeFileScraper, TikTokDBScraper...
    We have: One ContentScraper with injected strategies
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
# API extraction + DB storage
scraper = ContentScraper(
    extraction_strategy=APIFetchingStrategy(),
    storage_strategy=DatabaseStorageStrategy()
)
scraper.scrape("https://example.com/content")

# Change to file storage at runtime
scraper.set_storage_strategy(FileStorageStrategy())
scraper.scrape("https://example.com/content")
```

### Benefits for Layered Systems

1. **Flexibility**: Swap algorithms without changing context code (Open/Closed Principle)
2. **Separation of Concerns**: Complex logic isolated in its own class
3. **Reusability**: Mix and match strategies, combine simple pieces
4. **Reduced Inheritance Explosion**: One context class instead of many subclasses
5. **Runtime Configuration**: Strategies can be changed at runtime
6. **Better Testability**: Each strategy tested independently; context tested with mocks

### Drawbacks

1. **Increased Complexity**: More classes and interfaces to manage
2. **Wiring Overhead**: Strategies must be wired to context (dependency injection)
3. **Client Awareness**: Clients must understand strategy differences
4. **Potential Overkill**: For 2-3 variations, simpler conditionals may suffice

---

## Composition Over Inheritance

### The Problem with Deep Inheritance

**Deep Inheritance Pitfalls:**
- **Fragile Base Class Problem**: Small base changes ripple through all subclasses
- **Method Override Confusion**: Difficult to track which methods are overridden where
- **Complex Program Flow**: Hard to reason about behavior across multiple levels
- **Tight Coupling**: Changes to base classes affect all descendants

**Example of Deep Inheritance (5 levels - BAD):**
```python
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
```

### Solution: Shallow Inheritance with Composition

**Keep inheritance to 2-3 levels maximum, use composition for variations:**

```python
# GOOD: Shallow inheritance (2 levels) with composition
class Idea:
    """Base idea class."""
    pass

class VideoIdea(Idea):
    """Video-specific idea."""
    
    def __init__(
        self,
        platform_handler: PlatformHandler,      # Composed
        content_type_handler: ContentTypeHandler,  # Composed
        source_handler: SourceHandler             # Composed
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

### Composition Benefits

1. **Flexibility**: Change or replace components without affecting others
2. **Loose Coupling**: Components can be reused across different parts of the system
3. **Better Testability**: Mock or stub out components easily
4. **Simpler Classes**: Each piece is simpler and more maintainable
5. **SOLID Adherence**: Better alignment with Single Responsibility and Open/Closed principles

### When to Use Composition

Prefer composition when:
1. **Clean Separation**: A behavior can be cleanly separated as an independent component
2. **Deep Hierarchies**: An inheritance hierarchy is getting too deep or unwieldy
3. **Optional Features**: Not every class needs a feature; compose it into those that do
4. **Cross-Cutting Concerns**: Multiple unrelated classes need the same functionality

### Practical Example: Optional Caching Feature

```python
from typing import Optional, Any

# Helper component for caching
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

# BAD: Forcing caching via inheritance
class CacheableYouTubeSource(YouTubeSource):
    """Adds caching to YouTube source via inheritance."""
    pass

# GOOD: Composing caching functionality
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

# Usage
# Source without caching
simple_source = YouTubeSource()

# Source with caching
cached_source = YouTubeSource(cache=CacheHelper(ttl_seconds=1800))
```

---

## SOLID Principles in Layered Architecture

### 1. Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change.

**Application in Layers**: Separate concerns into focused classes:
- `VideoMetadataFetcher` - only fetches metadata
- `SentimentAnalyzer` - only analyzes sentiment
- `VideoDataRepository` - only handles persistence
- `ReportGenerator` - only generates reports

**Example**:
```python
# GOOD: Each class has a single responsibility
class VideoMetadataFetcher:
    """Responsible only for fetching video metadata."""
    def fetch(self, video_id: str) -> dict:
        # API fetching logic
        return {"video_id": video_id, "title": "..."}

class VideoDataRepository:
    """Responsible only for data persistence."""
    def save(self, data: dict) -> None:
        # Database logic
        pass

# Orchestrator composes focused classes
class VideoProcessor:
    """Orchestrates video processing using focused components."""
    def __init__(
        self,
        fetcher: VideoMetadataFetcher,
        repository: VideoDataRepository
    ):
        self._fetcher = fetcher
        self._repository = repository
```

### 2. Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension, but closed for modification.

**Application in Layers**: Use abstractions and Strategy pattern to add new behaviors without modifying existing code.

**Example**:
```python
from typing import Protocol

class ScoringStrategy(Protocol):
    """Interface for content scoring strategies."""
    def calculate_score(self, content: dict) -> float:
        """Calculate score for content."""
        ...

# Existing strategies
class VideoScoringStrategy:
    """Score video content."""
    def calculate_score(self, content: dict) -> float:
        return content.get("views", 0) / 1000

# NEW: Add social media scoring without modifying existing code
class SocialMediaScoringStrategy:
    """Score social media content."""
    def calculate_score(self, content: dict) -> float:
        likes = content.get("likes", 0)
        shares = content.get("shares", 0)
        comments = content.get("comments", 0)
        return (likes + shares * 2 + comments * 3) / 1000

# Context is closed for modification, open for extension
class ContentScorer:
    """Calculate scores using injected strategies."""
    def __init__(self, strategies: dict[str, ScoringStrategy]):
        self._strategies = strategies
    
    def register_strategy(self, content_type: str, strategy: ScoringStrategy) -> None:
        """Extension point for new strategies."""
        self._strategies[content_type] = strategy
```

### 3. Liskov Substitution Principle (LSP)

**Definition**: Subtypes must be substitutable for their base types without altering program correctness.

**Application in Layers**: Design proper hierarchies that honor contracts.

**Example**:
```python
# GOOD: Design hierarchy to respect capabilities
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
def make_bird_fly(bird: FlyingBird) -> None:
    print(bird.fly())

sparrow = Sparrow()
make_bird_fly(sparrow)  # ✅ Works

penguin = Penguin()
# make_bird_fly(penguin)  # ❌ Type error - penguin is not FlyingBird
```

### 4. Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they don't use.

**Application in Layers**: Create focused, minimal interfaces using Python Protocols.

**Example**:
```python
from typing import Protocol

# GOOD: Split into focused interfaces
class Fetchable(Protocol):
    """Minimal interface for data fetching."""
    def fetch_data(self) -> dict:
        ...

class Cacheable(Protocol):
    """Minimal interface for caching."""
    def cache_data(self, data: dict) -> None:
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
```

### 5. Dependency Inversion Principle (DIP)

**Definition**: Depend on abstractions, not on concrete implementations.

**Application in Layers**: High-level modules depend on abstractions; inject dependencies through constructors.

**Example**:
```python
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
```

---

## Pattern Comparison and Selection Guide

### Comprehensive Comparison Table

| Aspect | Template Method | Strategy Pattern | Composition |
|--------|----------------|------------------|-------------|
| **Mechanism** | Base class defines algorithm skeleton; subclasses override specific steps (inheritance) | Context holds a strategy object; behavior is delegated to it (composition) | Build classes by containing other components or using mixins |
| **Use When** | • Common process with variant steps<br>• Enforce consistent workflow | • Need runtime behavior changes<br>• Avoid combinatorial subclasses | • Deep hierarchies<br>• Optional features<br>• Cross-cutting concerns |
| **Pros** | • Eliminates duplicate code<br>• Subclasses focus on unique logic<br>• Uniform sequence | • Flexible (Open/Closed)<br>• Separation of concerns<br>• Reduces subclass explosion | • Flexible and loosely coupled<br>• Reusable components<br>• Better testability |
| **Cons** | • Rigid algorithm<br>• Inheritance coupling<br>• Can lead to deep hierarchies | • More classes to manage<br>• Client awareness needed<br>• Wiring overhead | • More moving parts<br>• Need defined interfaces<br>• Slight performance overhead |
| **Coupling** | Tight coupling to base class | Loose coupling via interface | Very loose coupling |
| **Runtime Flexibility** | Low (behavior fixed at compile time) | High (strategies swappable at runtime) | High (components replaceable) |
| **Testing** | Moderate (must test with actual subclasses) | Excellent (can mock strategies easily) | Excellent (can mock components easily) |

### Decision Framework

**Choose Template Method When:**
- ✅ Well-defined, stable algorithm with varying steps
- ✅ All implementations follow the same sequence
- ✅ Want to enforce a workflow across all subclasses
- ✅ Variations are simple overrides of specific methods
- ✅ Runtime flexibility is NOT required

**Choose Strategy Pattern When:**
- ✅ Need runtime behavior changes
- ✅ Multiple independent aspects vary (avoid combinatorial subclasses)
- ✅ Want to replace conditional logic with polymorphism
- ✅ Behaviors should be easily swappable
- ✅ Need better testability with mock strategies

**Choose Composition When:**
- ✅ Want to avoid deep inheritance (> 3 levels)
- ✅ Features are optional (not all classes need them)
- ✅ Same functionality needed across unrelated classes
- ✅ Want maximum flexibility and loose coupling
- ✅ Testability is a priority

### Combining Patterns

These patterns are not mutually exclusive. Combine them for optimal design:

1. **Template Method + Strategy**: High-level algorithm in Template Method, delegate varying steps to Strategy objects
2. **Template Method + Composition**: Template Method for workflow, composed helpers for optional features
3. **Strategy + Composition**: Strategies themselves composed of multiple smaller components

---

## Practical Applications in PrismQ

### Application 1: Source Module (Strategy + DIP)

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

# Usage
collector = IdeaCollector([
    YouTubeFetcher(),
    RedditFetcher(),
    TikTokFetcher()  # Easy to add new sources
])
```

### Application 2: Scoring Module (Strategy + OCP)

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

# Context - Open for extension, closed for modification
class IdeaScorer:
    """Score ideas using a configured strategy."""
    def __init__(self, strategy: ScoringStrategy):
        self._strategy = strategy
    
    def score(self, idea: IdeaInspiration) -> float:
        return self._strategy.calculate_score(idea)
    
    def set_strategy(self, strategy: ScoringStrategy) -> None:
        """Change strategy at runtime."""
        self._strategy = strategy
```

### Application 3: Classification Module (Composition + ISP)

```python
from typing import Optional

# Helper components (ISP - focused interfaces)
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

### 4. Keep Inheritance Shallow (Max 2-3 Levels)

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

### 6. Test Strategies Independently

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

### 7. Use Factory Pattern for Strategy Creation

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

### 8. Apply SOLID Principles Consistently

- **SRP**: Keep classes focused on a single responsibility
- **OCP**: Design for extension using abstractions and strategies
- **LSP**: Ensure subclasses are properly substitutable
- **ISP**: Use minimal, focused interfaces (Python Protocols)
- **DIP**: Depend on abstractions, inject dependencies

---

## References

### Design Patterns
- [Refactoring.Guru - Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Medium - Favor Composition Over Inheritance](https://medium.com/)
- [Software Engineering Stack Exchange - Strategy Pattern Discussion](https://softwareengineering.stackexchange.com/)

### SOLID Principles
- [SOLID Principles - Wikipedia](https://en.wikipedia.org/wiki/SOLID)
- [Robert C. Martin - Clean Architecture](https://blog.cleancoder.com/)

### PrismQ Documentation
- [Strategy Pattern Research](./../docs/STRATEGY_PATTERN_RESEARCH.md) - Detailed research document
- [SOLID Principles](./../docs/SOLID_PRINCIPLES.md) - Complete SOLID guide
- [Architecture Overview](./../docs/ARCHITECTURE.md) - System architecture
- [SOLID Review - Core Modules](./../docs/code_reviews/SOLID_REVIEW_CORE_MODULES.md)

### Python Resources
- [Python Type Hints - Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Python Abstract Base Classes](https://docs.python.org/3/library/abc.html)

---

## Conclusion

This research compilation provides a comprehensive guide to building flexible, maintainable layered systems using:

1. **Strategy Pattern** for runtime behavior variations and avoiding subclass explosion
2. **Composition Over Inheritance** to keep hierarchies shallow and enable optional features
3. **SOLID Principles** as the foundation for clean, maintainable code
4. **Pattern Selection Framework** to choose the right approach for each situation

**Key Takeaways:**

- Use **Strategy** when you need runtime flexibility and want to avoid combinatorial subclass explosion
- Use **Composition** to keep inheritance shallow (2-3 levels max) and add optional features
- Apply **SOLID principles** consistently: SRP, OCP, LSP, ISP, DIP
- Combine patterns strategically: Template Method for stable workflows, Strategy for varying behaviors, Composition for optional features
- Start simple and refactor to patterns as complexity emerges
- Use Python Protocols for structural typing and dependency injection for loose coupling

These patterns and principles are already in use within PrismQ (see SOLID reviews) and should guide all future architectural decisions in the project.

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Complete
