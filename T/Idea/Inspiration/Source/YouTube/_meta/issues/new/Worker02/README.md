# Worker02 - Python Specialist

**Role**: Core Infrastructure & Plugin Implementation  
**Language**: Python 3.10+  
**Project**: YouTube Worker Refactor  
**Duration**: Weeks 1-3 (8 issues total)

---

## Overview

Worker02 is a **Python specialist** responsible for implementing the core worker infrastructure and migrating all YouTube scraping plugins to the worker pattern. This is the **critical path role** with the most issues (8 total) and requires deep Python expertise, particularly in:

- Object-oriented design and SOLID principles
- Async programming and concurrency
- Protocol-based interfaces (Python 3.10+ typing)
- SQLite database interactions
- Abstract base classes and factory patterns
- Error handling and retry logic

---

## Skills Required

### Core Competencies
- ✅ **Python 3.10+**: Advanced features (Protocol, TypedDict, match/case, etc.)
- ✅ **SOLID Principles**: Deep understanding of all 5 principles
- ✅ **Design Patterns**: Factory, Strategy, Repository, Abstract Factory
- ✅ **Async/Await**: Concurrent task execution
- ✅ **SQLite**: Connection management, transactions, WAL mode
- ✅ **Type Hints**: Full type annotation, mypy compliance

### Domain Knowledge
- ✅ **YouTube API**: Experience with yt-dlp and/or YouTube Data API
- ✅ **Web Scraping**: HTML parsing, API interactions
- ✅ **Data Transformation**: ETL processes, data validation
- ✅ **Testing**: pytest, unittest, mocking, fixtures

### Tools & Libraries
- Python 3.10+
- yt-dlp (YouTube scraping)
- sqlite3 (database)
- pytest (testing)
- mypy (type checking)
- black/ruff (formatting/linting)

---

## Assigned Issues (8 Total)

### Phase 1: Core Infrastructure (Issues #002-#006)

#### Issue #002: Create Worker Base Class and Interface ⭐ CRITICAL
**Duration**: 2-3 days  
**Priority**: Critical (blocking all other issues)  
**Dependencies**: None

**Deliverables**:
- `WorkerProtocol` interface (Python Protocol)
- `BaseWorker` abstract base class
- `WorkerFactory` for plugin registration
- Task/TaskResult data classes
- Atomic task claiming mechanism
- Heartbeat system
- Unit tests (>80% coverage)

**Python Components**:
```python
# src/workers/__init__.py
class WorkerProtocol(Protocol):
    def claim_task(self) -> Optional[Task]: ...
    def process_task(self, task: Task) -> TaskResult: ...
    def report_result(self, task: Task, result: TaskResult) -> None: ...

# src/workers/base_worker.py
class BaseWorker(ABC):
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        pass
```

**Key Challenges**:
- Protocol typing (Python 3.10+ feature)
- Abstract class design
- Dependency injection pattern
- Thread-safe SQLite connections

---

#### Issue #003: Implement Task Polling Mechanism ⭐ CRITICAL
**Duration**: 2 days  
**Priority**: Critical  
**Dependencies**: #002 (Worker Base), #004 (DB Schema)

**Deliverables**:
- `ClaimingStrategy` protocol
- 4 strategy implementations:
  - FIFOStrategy (oldest first)
  - LIFOStrategy (newest first) - DEFAULT
  - PriorityStrategy (highest priority)
  - WeightedRandomStrategy (priority-weighted)
- `TaskPoller` class with backoff mechanism
- Integration with BaseWorker
- Performance tests (<10ms claiming target)

**Python Components**:
```python
# src/workers/claiming_strategies.py
class ClaimingStrategy(Protocol):
    def get_order_by_clause(self) -> str: ...

class LIFOStrategy(BaseClaimStrategy):
    def get_order_by_clause(self) -> str:
        return "created_at DESC, priority DESC"

# src/workers/task_poller.py
class TaskPoller:
    def __init__(self, queue_conn, worker_id, strategy="LIFO"):
        self.strategy = get_strategy(strategy)
    
    def claim_task(self) -> Optional[Task]:
        # Atomic claiming with IMMEDIATE transaction
        pass
```

**Key Challenges**:
- IMMEDIATE transactions for atomic claiming
- SQL query optimization
- Backoff algorithm implementation
- SQLITE_BUSY handling

---

#### Issue #005: Refactor Plugin Architecture for Worker Pattern
**Duration**: 2-3 days  
**Priority**: High  
**Dependencies**: #002, #003

**Deliverables**:
- Abstract `PluginBase` class
- Plugin registration system
- Dependency injection framework
- Plugin lifecycle management
- Plugin discovery mechanism

**Python Components**:
```python
# src/plugins/base_plugin.py
class PluginBase(ABC):
    @abstractmethod
    def scrape(self, **params) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass

# src/plugins/registry.py
class PluginRegistry:
    def register(self, plugin_class: Type[PluginBase]):
        pass
```

**Key Challenges**:
- Backward compatibility with existing plugins
- Plugin discovery pattern
- Configuration injection
- Error boundary implementation

---

#### Issue #006: Implement Error Handling and Retry Logic
**Duration**: 2 days  
**Priority**: High  
**Dependencies**: #002, #005

**Deliverables**:
- Retry strategy with exponential backoff
- Error classification (retryable vs permanent)
- Max retry handling
- Error logging and metrics
- Dead letter queue for failed tasks

**Python Components**:
```python
# src/workers/error_handler.py
class RetryStrategy:
    def should_retry(self, error: Exception, attempt: int) -> bool:
        pass
    
    def get_retry_delay(self, attempt: int) -> float:
        return 2 ** attempt  # Exponential backoff

class ErrorClassifier:
    def is_retryable(self, error: Exception) -> bool:
        pass
```

**Key Challenges**:
- Error taxonomy design
- Exponential backoff calculation
- Dead letter queue implementation
- Error context preservation

---

### Phase 2: Plugin Migration (Issues #009-#012)

#### Issue #009: Migrate YouTubeChannelPlugin to Worker
**Duration**: 2-3 days  
**Priority**: High  
**Dependencies**: #005

**Deliverables**:
- `YouTubeChannelWorker` class
- Task type: `channel_scrape`
- Parameter validation
- Result transformation
- Unit tests

**Python Components**:
```python
# src/workers/youtube_channel_worker.py
class YouTubeChannelWorker(BaseWorker):
    def process_task(self, task: Task) -> TaskResult:
        # Migrate logic from YouTubeChannelPlugin
        channel_url = task.parameters['channel_url']
        top_n = task.parameters.get('top_n', 10)
        # ... scraping logic
        return TaskResult(success=True, data=ideas)
```

---

#### Issue #010: Migrate YouTubeTrendingPlugin to Worker
**Duration**: 2-3 days  
**Priority**: High  
**Dependencies**: #005

**Deliverables**:
- `YouTubeTrendingWorker` class
- Task type: `trending_scrape`
- Category filtering
- Unit tests

---

#### Issue #011: Implement YouTube Keyword Search Worker
**Duration**: 2-3 days  
**Priority**: High  
**Dependencies**: #005

**Deliverables**:
- `YouTubeKeywordWorker` class (NEW)
- Task type: `keyword_search`
- Search query handling
- Result ranking
- Unit tests

---

#### Issue #012: Migrate YouTubePlugin to Worker (Optional/Legacy)
**Duration**: 2 days  
**Priority**: Low (optional)  
**Dependencies**: #005

**Deliverables**:
- `YouTubeAPIWorker` class
- Task type: `api_scrape`
- API quota handling
- Unit tests

---

## Python Code Standards

### Type Hints (Required)
```python
from typing import Optional, List, Dict, Any, Protocol
from dataclasses import dataclass

def process_task(self, task: Task) -> TaskResult:
    """Process a task and return result.
    
    Args:
        task: Task to process
        
    Returns:
        TaskResult with success status and data
        
    Raises:
        TaskError: If task processing fails
    """
    pass
```

### Docstrings (Google Style)
```python
class BaseWorker(ABC):
    """Base worker class for task processing.
    
    Follows Single Responsibility Principle - manages task lifecycle only.
    Does NOT handle specific scraping logic (delegated to subclasses).
    
    Attributes:
        worker_id: Unique worker identifier
        queue_conn: SQLite database connection
        strategy: Task claiming strategy (FIFO, LIFO, PRIORITY)
        
    Example:
        >>> worker = YouTubeChannelWorker(
        ...     worker_id="worker-1",
        ...     queue_db_path="queue.db",
        ...     config=config,
        ...     results_db=db
        ... )
        >>> worker.run()
    """
```

### Error Handling
```python
try:
    result = self.process_task(task)
except RetryableError as e:
    # Log and retry
    logger.warning(f"Retryable error: {e}")
    raise
except PermanentError as e:
    # Log and fail permanently
    logger.error(f"Permanent error: {e}")
    return TaskResult(success=False, error=str(e))
```

### Testing Standards
```python
def test_worker_claims_task():
    """Test worker can claim a task from queue."""
    # Arrange
    worker = TestWorker(...)
    
    # Act
    task = worker.claim_task()
    
    # Assert
    assert task is not None
    assert task.status == TaskStatus.CLAIMED
```

---

## Timeline & Milestones

### Week 1 (Days 1-5)
- ✅ Day 1-3: Complete #002 (Worker Base Class)
- ✅ Day 3-5: Complete #003 (Task Polling)

### Week 2 (Days 6-10)
- ⏳ Day 6-8: Complete #005 (Plugin Refactor)
- ⏳ Day 8-10: Complete #006 (Error Handling)

### Week 3 (Days 11-15)
- ⏳ Day 11-13: Complete #009 (Channel Worker)
- ⏳ Day 13-15: Complete #010 (Trending Worker)

### Week 3-4 (Days 16-20)
- ⏳ Day 16-18: Complete #011 (Keyword Worker)
- ⏳ Day 18-20: Optional #012 (API Worker)

---

## Collaboration Points

### With Worker06 (Database Specialist)
- **Week 1**: Coordinate on schema design (#002, #004)
- **Week 2**: Integrate result storage (#006, #007)
- **Daily**: Sync on database queries and indexes

### With Worker03 (Full Stack)
- **Week 2-3**: Coordinate on API integration (#013, #014)
- **Week 3**: CLI updates for worker-based execution (#015)

### With Worker04 (QA/Testing)
- **Week 3-4**: Provide test fixtures and mocks
- **Week 4**: Support integration testing (#020)

### With Worker10 (Review Specialist)
- **Week 4**: Code review sessions (#023)
- **Week 5**: Architecture validation (#024)

---

## Success Criteria

### Code Quality
- [ ] All 8 issues completed
- [ ] >80% test coverage
- [ ] 100% type hint coverage
- [ ] All mypy checks pass
- [ ] All pylint checks pass (or justified suppressions)
- [ ] SOLID principles verified by Worker10

### Performance
- [ ] Task claiming <10ms (P95)
- [ ] Worker startup <5 seconds
- [ ] Memory usage <500MB per worker
- [ ] Zero memory leaks (tested with valgrind)

### Documentation
- [ ] All classes have docstrings
- [ ] All public methods have docstrings
- [ ] README updated
- [ ] Architecture diagrams created

---

## Resources

### Documentation
- Python typing docs: https://docs.python.org/3/library/typing.html
- SQLite Python: https://docs.python.org/3/library/sqlite3.html
- pytest docs: https://docs.pytest.org/
- yt-dlp docs: https://github.com/yt-dlp/yt-dlp

### Internal References
- Master Plan: `_meta/issues/new/400-refactor-youtube-as-worker-master-plan.md`
- Current YouTube Module: `Sources/Content/Shorts/YouTube/README.md`
- SOLID Principles: Repository custom instructions

### Code Examples
- Worker Template: PrismQ.Client WORKER_IMPLEMENTATION_TEMPLATE.md
- Integration Guide: PrismQ.Client INTEGRATION_GUIDE.md
- SQLite Queue: Issues #320-340 (PrismQ.Client)

---

## Contact

**Primary Contact**: Worker02 - Python Specialist  
**Backup**: Worker01 - Project Manager  
**Technical Review**: Worker10 - Review Specialist

---

**Status**: 📋 Ready for Assignment  
**Created**: 2025-11-11  
**Last Updated**: 2025-11-11  
**Issues**: 8 total (2 completed, 6 remaining)
