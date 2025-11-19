# Issue #005: Refactor Plugin Architecture for Worker Pattern

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 02 - Python Specialist  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: High  
**Duration**: 2-3 days  
**Dependencies**: #002 (Worker Base Class), #003 (Task Polling Mechanism)

---

## Worker Details: Worker02 - Python Specialist

**Role**: Plugin Architecture Refactoring  
**Expertise Required**:
- Abstract base classes and interfaces (ABC, Protocol)
- Plugin/Factory pattern implementation
- Dependency injection patterns
- Python module discovery mechanisms
- Configuration management

**Collaboration**:
- **Worker02** (self): Build on #002 and #003
- **Worker06** (Database): Coordinate on data storage interfaces
- **Worker01** (PM): Daily standup, architecture review

**See**: `_meta/issues/new/Worker02/README.md` for complete role description

---

## Objective

Refactor the existing plugin architecture to work seamlessly with the worker pattern, enabling dynamic plugin registration, dependency injection, and lifecycle management while maintaining backward compatibility with existing scraping plugins.

---

## Problem Statement

The current YouTube module has three scraping plugins:
1. `youtube_plugin.py` - YouTube API search
2. `youtube_channel_plugin.py` - Channel-based scraping
3. `youtube_trending_plugin.py` - Trending page scraping

These plugins currently:
- Have a `SourcePlugin` base class but aren't integrated with workers
- Use direct instantiation rather than factory pattern
- Don't support task-based execution
- Lack standardized configuration injection
- Have no lifecycle management

We need to refactor the plugin architecture to:
1. Support worker-based task execution
2. Enable dynamic plugin discovery and registration
3. Provide dependency injection for Config, Database, etc.
3. Maintain SOLID principles throughout
4. Support future plugin additions without modifying core code

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅

**PluginBase Responsibilities**:
- Define plugin contract/interface
- Provide plugin metadata (name, task_type, version)
- Declare scraping method signature

**NOT Responsible For**:
- Plugin discovery (PluginRegistry)
- Plugin instantiation (PluginFactory)
- Task execution (Worker classes)
- Configuration management (Config class)

**PluginRegistry Responsibilities**:
- Store registered plugins
- Provide plugin lookup by task type
- Validate plugin registration

**NOT Responsible For**:
- Plugin implementation
- Plugin instantiation
- Configuration

**PluginFactory Responsibilities**:
- Create plugin instances
- Inject dependencies
- Manage plugin lifecycle

**NOT Responsible For**:
- Plugin registration
- Plugin logic
- Task execution

### Open/Closed Principle (OCP) ✅

**Open for Extension**:
- New plugins can be added by extending `PluginBase`
- New scrapers registered without modifying registry
- New dependency injection patterns supported

**Closed for Modification**:
- `PluginBase` interface remains stable
- Registry core logic unchanged
- Factory pattern encapsulates creation

### Liskov Substitution Principle (LSP) ✅

**Substitutability**:
- All plugins implementing `PluginBase` can be used interchangeably
- Workers can use any plugin through the base interface
- No subclass breaks base class contracts

### Interface Segregation Principle (ISP) ✅

**Minimal Interface**:
```python
class PluginBase(ABC):
    @abstractmethod
    def get_task_type(self) -> str: ...
    
    @abstractmethod
    def scrape(self, **params) -> List[Dict[str, Any]]: ...
    
    @abstractmethod
    def validate_parameters(self, params: Dict[str, Any]) -> bool: ...
```

Only essential methods, no unnecessary dependencies.

### Dependency Inversion Principle (DIP) ✅

**Depend on Abstractions**:
- Workers depend on `PluginBase`, not concrete plugins
- Dependencies (Config, Database) injected via constructor
- Factory pattern enables flexible instantiation

---

## Proposed Solution

### Architecture Overview

```
Plugin System Architecture
├── PluginBase (ABC)              # Abstract base class
│   ├── get_task_type()           # Returns task type string
│   ├── scrape(**params)          # Main scraping method
│   └── validate_parameters()     # Parameter validation
│
├── PluginRegistry (Singleton)    # Plugin registration
│   ├── register(plugin_class)    # Register plugin class
│   ├── get_plugin_class(type)    # Get plugin by task type
│   └── list_plugins()            # List all registered plugins
│
├── PluginFactory                 # Plugin instantiation
│   ├── create_plugin(type)       # Create plugin instance
│   └── inject_dependencies()     # Inject Config, Database
│
└── Concrete Plugins
    ├── YouTubeChannelPlugin      # Extends PluginBase
    ├── YouTubeTrendingPlugin     # Extends PluginBase
    └── YouTubeKeywordPlugin      # Extends PluginBase (new)
```

---

## Implementation Details

### File Structure

```
src/
├── plugins/
│   ├── __init__.py              # SourcePlugin → PluginBase, registry
│   ├── base_plugin.py           # NEW: PluginBase abstract class
│   ├── registry.py              # NEW: PluginRegistry singleton
│   ├── factory.py               # NEW: PluginFactory
│   ├── youtube_plugin.py        # REFACTOR: Use new base
│   ├── youtube_channel_plugin.py # REFACTOR: Use new base
│   └── youtube_trending_plugin.py # REFACTOR: Use new base
│
├── workers/
│   ├── base_worker.py           # From #002 - uses plugins
│   └── ...
```

### 1. PluginBase Abstract Class

**File**: `src/plugins/base_plugin.py`

```python
"""Plugin base class for YouTube scrapers.

This module provides the abstract base class that all scraping plugins
must implement. It follows the Interface Segregation Principle by
providing only the essential methods needed for plugin operation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class PluginMetadata:
    """Plugin metadata.
    
    Attributes:
        name: Human-readable plugin name
        task_type: Task type identifier (e.g., 'channel_scrape')
        version: Plugin version
        description: Plugin description
    """
    name: str
    task_type: str
    version: str = "1.0.0"
    description: str = ""


class PluginBase(ABC):
    """Abstract base class for scraping plugins.
    
    All YouTube scraping plugins must extend this class and implement
    the required abstract methods. Follows Single Responsibility Principle
    by focusing only on the scraping contract.
    
    Attributes:
        config: Configuration object (injected)
        database: Database connection (injected)
        metrics: Metrics calculator (injected)
    
    Example:
        >>> class MyPlugin(PluginBase):
        ...     def get_metadata(self) -> PluginMetadata:
        ...         return PluginMetadata(
        ...             name="My Plugin",
        ...             task_type="my_scrape"
        ...         )
        ...     
        ...     def scrape(self, **params) -> List[Dict[str, Any]]:
        ...         # Scraping logic here
        ...         return results
        ...     
        ...     def validate_parameters(self, params: Dict[str, Any]) -> bool:
        ...         return 'url' in params
    """
    
    def __init__(self, config, database, metrics):
        """Initialize plugin with injected dependencies.
        
        Args:
            config: Configuration object
            database: Database connection
            metrics: Metrics calculator
        """
        self.config = config
        self.database = database
        self.metrics = metrics
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata.
        
        Returns:
            PluginMetadata with name, task_type, version, description
        """
        pass
    
    @abstractmethod
    def scrape(self, **params) -> List[Dict[str, Any]]:
        """Perform scraping with given parameters.
        
        Args:
            **params: Scraping parameters (plugin-specific)
        
        Returns:
            List of scraped items as dictionaries
            
        Raises:
            ValueError: If parameters are invalid
            Exception: On scraping errors
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate scraping parameters.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        pass
    
    def get_task_type(self) -> str:
        """Get task type for this plugin.
        
        Returns:
            Task type string
        """
        return self.get_metadata().task_type
```

### 2. PluginRegistry Singleton

**File**: `src/plugins/registry.py`

```python
"""Plugin registry for managing plugin classes.

This module provides a singleton registry for plugin registration and
lookup. It follows the Open/Closed Principle by allowing new plugins
to be registered without modifying the registry code.
"""

from typing import Dict, Type, List, Optional
from threading import Lock

from .base_plugin import PluginBase, PluginMetadata


class PluginRegistry:
    """Singleton registry for plugin classes.
    
    Manages plugin registration and provides lookup by task type.
    Thread-safe for concurrent registration.
    
    Example:
        >>> registry = PluginRegistry.get_instance()
        >>> registry.register(YouTubeChannelPlugin)
        >>> plugin_class = registry.get_plugin_class('channel_scrape')
    """
    
    _instance: Optional['PluginRegistry'] = None
    _lock: Lock = Lock()
    
    def __init__(self):
        """Initialize empty registry."""
        self._plugins: Dict[str, Type[PluginBase]] = {}
    
    @classmethod
    def get_instance(cls) -> 'PluginRegistry':
        """Get singleton instance (thread-safe).
        
        Returns:
            PluginRegistry singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def register(self, plugin_class: Type[PluginBase]) -> None:
        """Register a plugin class.
        
        Args:
            plugin_class: Plugin class to register (must extend PluginBase)
            
        Raises:
            TypeError: If plugin_class doesn't extend PluginBase
            ValueError: If task_type already registered
        """
        if not issubclass(plugin_class, PluginBase):
            raise TypeError(
                f"{plugin_class.__name__} must extend PluginBase"
            )
        
        # Get metadata by instantiating with None dependencies
        # (only to get metadata, not for actual use)
        try:
            temp_instance = plugin_class(None, None, None)
            metadata = temp_instance.get_metadata()
            task_type = metadata.task_type
        except Exception as e:
            raise ValueError(
                f"Cannot get metadata from {plugin_class.__name__}: {e}"
            )
        
        if task_type in self._plugins:
            raise ValueError(
                f"Plugin with task_type '{task_type}' already registered"
            )
        
        self._plugins[task_type] = plugin_class
    
    def get_plugin_class(self, task_type: str) -> Optional[Type[PluginBase]]:
        """Get plugin class by task type.
        
        Args:
            task_type: Task type identifier
            
        Returns:
            Plugin class or None if not found
        """
        return self._plugins.get(task_type)
    
    def list_plugins(self) -> List[PluginMetadata]:
        """List all registered plugins.
        
        Returns:
            List of plugin metadata
        """
        metadata_list = []
        for plugin_class in self._plugins.values():
            try:
                temp_instance = plugin_class(None, None, None)
                metadata_list.append(temp_instance.get_metadata())
            except Exception:
                # Skip plugins that can't be instantiated
                continue
        return metadata_list
    
    def clear(self) -> None:
        """Clear all registered plugins (for testing)."""
        self._plugins.clear()
```

### 3. PluginFactory

**File**: `src/plugins/factory.py`

```python
"""Plugin factory for creating plugin instances.

This module provides a factory for creating plugin instances with
proper dependency injection. Follows Dependency Inversion Principle.
"""

from typing import Optional

from .base_plugin import PluginBase
from .registry import PluginRegistry


class PluginFactory:
    """Factory for creating plugin instances with dependency injection.
    
    Creates plugin instances and injects required dependencies (Config,
    Database, Metrics).
    
    Attributes:
        config: Configuration object to inject
        database: Database connection to inject
        metrics: Metrics calculator to inject
        registry: Plugin registry (singleton)
    
    Example:
        >>> factory = PluginFactory(config, database, metrics)
        >>> plugin = factory.create_plugin('channel_scrape')
        >>> results = plugin.scrape(channel_url='https://...')
    """
    
    def __init__(self, config, database, metrics):
        """Initialize factory with dependencies.
        
        Args:
            config: Configuration object
            database: Database connection
            metrics: Metrics calculator
        """
        self.config = config
        self.database = database
        self.metrics = metrics
        self.registry = PluginRegistry.get_instance()
    
    def create_plugin(self, task_type: str) -> Optional[PluginBase]:
        """Create plugin instance by task type.
        
        Args:
            task_type: Task type identifier
            
        Returns:
            Plugin instance with dependencies injected, or None if not found
            
        Raises:
            ValueError: If plugin not registered for task_type
        """
        plugin_class = self.registry.get_plugin_class(task_type)
        
        if plugin_class is None:
            raise ValueError(
                f"No plugin registered for task_type '{task_type}'"
            )
        
        # Create instance with dependency injection
        plugin = plugin_class(
            config=self.config,
            database=self.database,
            metrics=self.metrics
        )
        
        return plugin
```

### 4. Update Existing Plugins

**Refactor Pattern** (apply to all three plugins):

```python
# src/plugins/youtube_channel_plugin.py (example)

from .base_plugin import PluginBase, PluginMetadata
from typing import Dict, Any, List


class YouTubeChannelPlugin(PluginBase):
    """YouTube channel scraping plugin.
    
    Scrapes videos from YouTube channels using yt-dlp.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="YouTube Channel Scraper",
            task_type="channel_scrape",
            version="1.0.0",
            description="Scrape videos from YouTube channels"
        )
    
    def scrape(self, **params) -> List[Dict[str, Any]]:
        """Scrape channel videos.
        
        Args:
            channel_url: YouTube channel URL (required)
            top_n: Number of videos to scrape (optional, default: 10)
            
        Returns:
            List of video dictionaries
        """
        # Existing scraping logic (keep as-is)
        channel_url = params['channel_url']
        top_n = params.get('top_n', 10)
        # ... existing implementation ...
        return results
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate parameters."""
        return (
            'channel_url' in params and
            isinstance(params['channel_url'], str) and
            params['channel_url'].startswith('http')
        )
```

### 5. Auto-Registration System

**File**: `src/plugins/__init__.py`

```python
"""Plugin system for YouTube scrapers.

This module provides the plugin system for registering and managing
YouTube scraping plugins.
"""

from .base_plugin import PluginBase, PluginMetadata
from .registry import PluginRegistry
from .factory import PluginFactory

# Import concrete plugins for auto-registration
from .youtube_channel_plugin import YouTubeChannelPlugin
from .youtube_trending_plugin import YouTubeTrendingPlugin
from .youtube_plugin import YouTubePlugin


def register_default_plugins():
    """Register default plugins on import."""
    registry = PluginRegistry.get_instance()
    
    # Register all default plugins
    try:
        registry.register(YouTubeChannelPlugin)
        registry.register(YouTubeTrendingPlugin)
        registry.register(YouTubePlugin)
    except ValueError:
        # Already registered (in case of multiple imports)
        pass


# Auto-register on import
register_default_plugins()


__all__ = [
    'PluginBase',
    'PluginMetadata',
    'PluginRegistry',
    'PluginFactory',
    'YouTubeChannelPlugin',
    'YouTubeTrendingPlugin',
    'YouTubePlugin',
]
```

---

## Integration with Worker Base Class

The worker base class from #002 will use the plugin system:

```python
# src/workers/base_worker.py (partial)

from src.plugins import PluginFactory

class BaseWorker(ABC):
    def __init__(self, worker_id, queue_db, config, results_db, metrics):
        self.worker_id = worker_id
        self.queue_db = queue_db
        self.plugin_factory = PluginFactory(config, results_db, metrics)
    
    def process_task(self, task: Task) -> TaskResult:
        """Process task using appropriate plugin."""
        # Get plugin for task type
        plugin = self.plugin_factory.create_plugin(task.task_type)
        
        if plugin is None:
            raise ValueError(f"Unknown task type: {task.task_type}")
        
        # Validate parameters
        if not plugin.validate_parameters(task.parameters):
            raise ValueError(f"Invalid parameters for {task.task_type}")
        
        # Execute scraping
        results = plugin.scrape(**task.parameters)
        
        return TaskResult(success=True, data=results)
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] `PluginBase` abstract class created with minimal interface
- [ ] `PluginRegistry` singleton implemented with thread safety
- [ ] `PluginFactory` implemented with dependency injection
- [ ] All three existing plugins refactored to use new base
- [ ] Auto-registration system working on import
- [ ] Workers can create plugins via factory
- [ ] Parameter validation working for all plugins

### Non-Functional Requirements
- [ ] All SOLID principles verified (especially OCP, DIP)
- [ ] Thread-safe plugin registration
- [ ] No circular dependencies
- [ ] Backward compatibility maintained (old code still works)
- [ ] Zero breaking changes to existing plugin logic

### Code Quality
- [ ] Type hints on all public methods
- [ ] Docstrings (Google style) on all classes and methods
- [ ] mypy type checking passes
- [ ] pylint score >8.5/10

### Testing Requirements
- [ ] Unit tests for PluginBase abstract class
- [ ] Unit tests for PluginRegistry (singleton, registration, lookup)
- [ ] Unit tests for PluginFactory (creation, injection)
- [ ] Integration tests with all three plugins
- [ ] Test parameter validation for each plugin
- [ ] Test auto-registration system
- [ ] Test thread safety of registry
- [ ] Test coverage >80%

### Documentation
- [ ] All classes have docstrings
- [ ] All public methods documented
- [ ] Architecture diagram updated
- [ ] README updated with plugin system usage
- [ ] Migration guide for future plugins

---

## Testing Strategy

### Unit Tests

**File**: `_meta/tests/test_plugin_base.py`

```python
def test_plugin_metadata():
    """Test PluginMetadata dataclass."""
    metadata = PluginMetadata(
        name="Test Plugin",
        task_type="test_scrape",
        version="1.0.0"
    )
    assert metadata.name == "Test Plugin"
    assert metadata.task_type == "test_scrape"


def test_plugin_base_abstract():
    """Test that PluginBase cannot be instantiated."""
    with pytest.raises(TypeError):
        PluginBase(None, None, None)
```

**File**: `_meta/tests/test_plugin_registry.py`

```python
def test_registry_singleton():
    """Test registry is singleton."""
    registry1 = PluginRegistry.get_instance()
    registry2 = PluginRegistry.get_instance()
    assert registry1 is registry2


def test_register_plugin():
    """Test plugin registration."""
    registry = PluginRegistry.get_instance()
    registry.clear()
    
    registry.register(YouTubeChannelPlugin)
    plugin_class = registry.get_plugin_class('channel_scrape')
    assert plugin_class is YouTubeChannelPlugin


def test_register_duplicate_task_type():
    """Test registering duplicate task type raises error."""
    registry = PluginRegistry.get_instance()
    registry.clear()
    
    registry.register(YouTubeChannelPlugin)
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register(YouTubeChannelPlugin)


def test_thread_safety():
    """Test concurrent registration is thread-safe."""
    # Test with ThreadPoolExecutor
    pass
```

**File**: `_meta/tests/test_plugin_factory.py`

```python
def test_create_plugin():
    """Test plugin creation with dependency injection."""
    config = MockConfig()
    database = MockDatabase()
    metrics = MockMetrics()
    
    factory = PluginFactory(config, database, metrics)
    plugin = factory.create_plugin('channel_scrape')
    
    assert isinstance(plugin, YouTubeChannelPlugin)
    assert plugin.config is config
    assert plugin.database is database
    assert plugin.metrics is metrics


def test_create_unknown_plugin():
    """Test creating unknown plugin raises error."""
    factory = PluginFactory(None, None, None)
    
    with pytest.raises(ValueError, match="No plugin registered"):
        factory.create_plugin('unknown_type')
```

### Integration Tests

**File**: `_meta/tests/test_plugin_integration.py`

```python
def test_plugin_system_integration():
    """Test complete plugin system integration."""
    # Setup
    config = load_test_config()
    database = Database(":memory:")
    metrics = UniversalMetrics()
    
    # Create factory
    factory = PluginFactory(config, database, metrics)
    
    # Create and use plugin
    plugin = factory.create_plugin('channel_scrape')
    params = {'channel_url': 'https://youtube.com/@test', 'top_n': 5}
    
    assert plugin.validate_parameters(params)
    
    # Note: Actual scraping tested in plugin-specific tests
```

### Performance Tests

```python
def test_plugin_creation_performance():
    """Test plugin creation is fast (<1ms)."""
    factory = PluginFactory(config, database, metrics)
    
    start = time.time()
    for _ in range(1000):
        plugin = factory.create_plugin('channel_scrape')
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # 1000 creations in <1 second
```

---

## Migration Guide for Existing Code

### Before (Old Code)

```python
# Old way - direct instantiation
from src.plugins.youtube_channel_plugin import YouTubeChannelPlugin

plugin = YouTubeChannelPlugin(config, database, metrics)
results = plugin.scrape(channel_url='https://...')
```

### After (New Code)

```python
# New way - factory pattern
from src.plugins import PluginFactory

factory = PluginFactory(config, database, metrics)
plugin = factory.create_plugin('channel_scrape')
results = plugin.scrape(channel_url='https://...')
```

**Note**: Old code still works! We're adding a new system, not breaking existing code.

---

## Dependencies

### Issue Dependencies
- **#002** (Worker Base Class): Workers will use plugin factory
- **#003** (Task Polling): Task types map to plugin types

### External Dependencies (No new dependencies)
- Existing: Python 3.10+ standard library
- Existing: yt-dlp (for plugins)

### Collaboration
- **Worker06**: Coordinate on database interfaces for plugins
- **Worker02** (self): Build on completed #002, #003

---

## Windows-Specific Considerations

- Plugin discovery uses `importlib` (cross-platform)
- Thread-safe registry for Windows threading model
- No OS-specific code in plugin system
- File paths use `pathlib` (cross-platform)

---

## Performance Targets

- [ ] Plugin creation: <1ms per instance
- [ ] Registry lookup: <0.1ms per lookup
- [ ] Registry registration: <1ms per plugin
- [ ] Zero memory leaks (tested with continuous creation)

---

## Success Metrics

### Code Metrics
- Lines of code: ~400-500 (reasonable for refactor)
- Cyclomatic complexity: <10 per method
- Test coverage: >80%
- mypy compliance: 100%

### Quality Metrics
- SOLID compliance: 100% (verified by Worker10)
- Documentation: Complete for all public APIs
- Backward compatibility: 100% (no breaking changes)

---

## Risks & Mitigation

### Risk: Breaking Existing Plugins
**Mitigation**: Maintain backward compatibility, comprehensive tests

### Risk: Circular Import Dependencies
**Mitigation**: Careful import structure, lazy imports if needed

### Risk: Thread Safety Issues
**Mitigation**: Use threading.Lock in registry, test with concurrent access

---

## Future Extensibility

This architecture enables:
- New plugin types added without modifying core
- Plugin versioning support
- Plugin marketplace/discovery
- Hot-reloading of plugins
- Plugin configuration validation
- Plugin dependency management

---

## References

### Internal
- Issue #002: Worker Base Class
- Issue #003: Task Polling Mechanism
- Master Plan: #001
- Current plugins: `src/plugins/*.py`

### External
- Python ABC: https://docs.python.org/3/library/abc.html
- Python Protocol: https://docs.python.org/3/library/typing.html#typing.Protocol
- Factory Pattern: Design Patterns book

---

## Approval Checklist

### SOLID Compliance
- [x] SRP: Each component has single responsibility
- [x] OCP: Open for extension (new plugins), closed for modification
- [x] LSP: All plugins substitutable
- [x] ISP: Minimal plugin interface
- [x] DIP: Depends on abstractions, dependency injection

### Code Review Checklist
- [ ] All acceptance criteria met
- [ ] Tests written and passing (>80% coverage)
- [ ] Documentation complete
- [ ] Type hints complete
- [ ] No breaking changes
- [ ] Performance targets met
- [ ] Worker10 reviewed

---

**Status**: 📋 Ready for Assignment  
**Created**: 2025-11-11  
**Assigned To**: Worker02 - Python Specialist  
**Estimated Start**: After #002, #003 complete  
**Estimated Duration**: 2-3 days
