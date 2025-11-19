# Issue #019: Create Worker Unit Tests

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 04 - QA/Testing Specialist  
**Language**: Python 3.10+ (pytest)  
**Status**: New  
**Priority**: Critical  
**Duration**: 2-3 days  
**Dependencies**: #002-#015 (All implementations)

---

## Worker Details: Worker04 - QA/Testing Specialist

**Role**: Test Infrastructure & Quality Assurance  
**Expertise Required**: 
- pytest framework (fixtures, parametrize, mocking)
- unittest.mock (Mock, MagicMock, patch)
- Test coverage tools (pytest-cov, coverage.py)
- SQLite testing patterns (in-memory databases)
- SOLID principles testing
- Windows-specific testing considerations

**Collaboration**:
- **Worker02** (Python): Coordinate on test fixtures and mocks
- **Worker06** (Database): Test database schema and queries
- **Worker10** (Review): Validate test quality and coverage

**See**: `_meta/issues/new/Worker04/README.md` for complete role description

---

## Objective

Create a comprehensive unit test suite for all worker system components following testing best practices. Ensure >80% code coverage, fast execution (<5 minutes), and proper isolation of dependencies through mocking. Tests must validate SOLID principles compliance and prevent regressions.

---

## Problem Statement

The worker refactor introduces new components that need thorough testing:
1. BaseWorker lifecycle management needs unit tests
2. Plugin system needs validation tests
3. Task claiming strategies need correctness tests
4. Database operations need isolation tests
5. Error handling needs comprehensive coverage
6. All components need to be testable independently (mocked dependencies)

Without comprehensive unit tests:
- ❌ Regressions will slip through
- ❌ Refactoring becomes risky
- ❌ Bug fixes can't be validated
- ❌ SOLID violations won't be caught
- ❌ Production deployment is risky

---

## SOLID Principles in Testing

### Single Responsibility Principle (SRP) ✅
**Test Organization**:
- Each test file tests ONE component only
- Each test function tests ONE behavior
- Test fixtures have ONE purpose

```python
# test_base_worker.py - Tests BaseWorker only
# test_plugin_registry.py - Tests PluginRegistry only
# test_task_poller.py - Tests TaskPoller only
```

### Dependency Inversion Principle (DIP) ✅
**Mock Dependencies**:
- Tests depend on Protocol types, not concrete implementations
- Dependencies injected via fixtures
- No hard-coded test data

```python
@pytest.fixture
def mock_queue() -> QueueProtocol:
    """Mock queue following QueueProtocol."""
    queue = Mock(spec=QueueProtocol)
    return queue

def test_worker_claims_task(mock_queue):
    """Test uses abstraction, not concrete queue."""
    worker = BaseWorker(queue=mock_queue)
    # Test using mock
```

### Interface Segregation Principle (ISP) ✅
**Minimal Test Fixtures**:
- Fixtures provide only what tests need
- No "god fixtures" with everything
- Compose fixtures as needed

---

## Test Architecture

### Test Directory Structure

```
Source/Video/YouTube/
├── src/
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── base_worker.py
│   │   ├── task_poller.py
│   │   └── ...
│   └── plugins/
│       ├── __init__.py
│       ├── base_plugin.py
│       └── ...
└── tests/
    ├── conftest.py              # Shared fixtures
    ├── unit/                    # Unit tests (this issue)
    │   ├── __init__.py
    │   ├── test_base_worker.py
    │   ├── test_task_poller.py
    │   ├── test_claiming_strategies.py
    │   ├── test_plugin_registry.py
    │   ├── test_channel_plugin.py
    │   ├── test_trending_plugin.py
    │   ├── test_keyword_plugin.py
    │   ├── test_parameter_registry.py
    │   ├── test_error_handler.py
    │   └── test_database_schema.py
    └── integration/             # Integration tests (Issue #020)
        └── ...
```

---

## Components to Test

### 1. BaseWorker (#002) - Critical Priority

#### Test Coverage Requirements
- Task claiming (atomic operations)
- Task processing lifecycle
- Result reporting
- Heartbeat mechanism
- Error handling
- Status transitions
- Dependency injection

#### Test Suite: `test_base_worker.py`

```python
"""Unit tests for BaseWorker class."""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from src.workers.base_worker import BaseWorker, WorkerConfig
from src.workers.task_poller import TaskPoller
from src.core.models import Task, TaskResult, TaskStatus

# ===== Fixtures =====

@pytest.fixture
def worker_config():
    """Worker configuration fixture."""
    return WorkerConfig(
        worker_id='test-worker-001',
        task_type='youtube_channel',
        poll_interval=1.0,
        max_retries=3,
        heartbeat_interval=30
    )

@pytest.fixture
def mock_queue():
    """Mock task queue."""
    queue = Mock()
    queue.claim_task = Mock(return_value=None)
    queue.update_task_status = Mock()
    queue.update_heartbeat = Mock()
    return queue

@pytest.fixture
def mock_plugin():
    """Mock plugin for scraping."""
    plugin = Mock()
    plugin.scrape = Mock(return_value=[
        {'source_id': 'video-123', 'title': 'Test Video', 'score': 75.0}
    ])
    return plugin

@pytest.fixture
def sample_task():
    """Sample task for testing."""
    return Task(
        task_id='task-123',
        task_type='youtube_channel',
        parameters={'channel_url': '@SnappyStories_1', 'max_results': 5},
        priority=0,
        status=TaskStatus.QUEUED,
        created_at='2025-01-01 00:00:00'
    )

# ===== Initialization Tests =====

def test_worker_initialization(worker_config, mock_queue, mock_plugin):
    """Test worker can be initialized with dependencies."""
    worker = BaseWorker(
        config=worker_config,
        queue=mock_queue,
        plugin=mock_plugin
    )
    
    assert worker.config == worker_config
    assert worker.queue == mock_queue
    assert worker.plugin == mock_plugin
    assert worker.worker_id == 'test-worker-001'

def test_worker_initialization_validates_config(mock_queue, mock_plugin):
    """Test worker validates configuration on init."""
    with pytest.raises(ValueError, match="worker_id"):
        BaseWorker(
            config=WorkerConfig(worker_id='', task_type='test'),
            queue=mock_queue,
            plugin=mock_plugin
        )

# ===== Task Claiming Tests =====

def test_worker_claims_task_successfully(worker_config, mock_queue, mock_plugin, sample_task):
    """Test worker can claim a task from queue."""
    mock_queue.claim_task.return_value = sample_task
    
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    task = worker._claim_task()
    
    assert task == sample_task
    mock_queue.claim_task.assert_called_once_with(
        worker_id='test-worker-001',
        task_type='youtube_channel'
    )

def test_worker_handles_no_task_available(worker_config, mock_queue, mock_plugin):
    """Test worker handles empty queue gracefully."""
    mock_queue.claim_task.return_value = None
    
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    task = worker._claim_task()
    
    assert task is None

def test_worker_claims_only_matching_task_type(worker_config, mock_queue, mock_plugin):
    """Test worker only claims tasks matching its task_type."""
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    worker._claim_task()
    
    # Verify task_type filter was used
    mock_queue.claim_task.assert_called_with(
        worker_id='test-worker-001',
        task_type='youtube_channel'
    )

# ===== Task Processing Tests =====

def test_worker_processes_task_successfully(
    worker_config, mock_queue, mock_plugin, sample_task
):
    """Test worker can process a task end-to-end."""
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    
    result = worker._process_task(sample_task)
    
    assert result.success is True
    assert result.ideas_count == 1
    mock_plugin.scrape.assert_called_once_with(
        channel_url='@SnappyStories_1',
        max_results=5
    )

def test_worker_validates_task_parameters(worker_config, mock_queue, mock_plugin):
    """Test worker validates task parameters before processing."""
    invalid_task = Task(
        task_id='task-123',
        task_type='youtube_channel',
        parameters={'invalid_param': 'value'},  # Missing required params
        priority=0,
        status=TaskStatus.QUEUED
    )
    
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    
    with pytest.raises(ValueError, match="Missing required parameter"):
        worker._process_task(invalid_task)

def test_worker_updates_status_during_processing(
    worker_config, mock_queue, mock_plugin, sample_task
):
    """Test worker updates task status during processing."""
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    
    worker._process_task(sample_task)
    
    # Verify status updates were made
    assert mock_queue.update_task_status.called
    status_calls = [call[0][1] for call in mock_queue.update_task_status.call_args_list]
    assert TaskStatus.RUNNING in status_calls
    assert TaskStatus.COMPLETED in status_calls

# ===== Error Handling Tests =====

def test_worker_handles_plugin_error(worker_config, mock_queue, mock_plugin, sample_task):
    """Test worker handles plugin errors gracefully."""
    mock_plugin.scrape.side_effect = Exception("Plugin error")
    
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    result = worker._process_task(sample_task)
    
    assert result.success is False
    assert "Plugin error" in result.error_message
    
    # Verify error was reported to queue
    mock_queue.update_task_status.assert_any_call(
        'task-123',
        TaskStatus.FAILED,
        error="Plugin error"
    )

def test_worker_retries_on_retryable_error(
    worker_config, mock_queue, mock_plugin, sample_task
):
    """Test worker retries task on retryable errors."""
    mock_plugin.scrape.side_effect = [
        ConnectionError("Network timeout"),  # Retry 1
        ConnectionError("Network timeout"),  # Retry 2
        [{'source_id': 'video-123', 'title': 'Test'}]  # Success
    ]
    
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    result = worker._process_task(sample_task)
    
    assert result.success is True
    assert mock_plugin.scrape.call_count == 3  # 2 failures + 1 success

def test_worker_respects_max_retries(worker_config, mock_queue, mock_plugin, sample_task):
    """Test worker stops after max_retries attempts."""
    mock_plugin.scrape.side_effect = ConnectionError("Network timeout")
    
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    result = worker._process_task(sample_task)
    
    assert result.success is False
    assert mock_plugin.scrape.call_count == 3  # max_retries

# ===== Heartbeat Tests =====

def test_worker_sends_heartbeat_during_processing(
    worker_config, mock_queue, mock_plugin, sample_task
):
    """Test worker sends heartbeat updates during long tasks."""
    def slow_scrape(**kwargs):
        """Simulate slow scraping."""
        import time
        time.sleep(2)  # Longer than heartbeat interval
        return [{'source_id': 'video-123', 'title': 'Test'}]
    
    mock_plugin.scrape.side_effect = slow_scrape
    
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    worker._process_task(sample_task)
    
    # Verify heartbeat was sent
    mock_queue.update_heartbeat.assert_called()

def test_worker_heartbeat_includes_worker_id(
    worker_config, mock_queue, mock_plugin, sample_task
):
    """Test heartbeat includes correct worker ID."""
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    worker._send_heartbeat('task-123')
    
    mock_queue.update_heartbeat.assert_called_with(
        worker_id='test-worker-001',
        task_id='task-123'
    )

# ===== Result Reporting Tests =====

def test_worker_reports_success_result(worker_config, mock_queue, mock_plugin, sample_task):
    """Test worker reports successful result to queue."""
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    
    result = TaskResult(success=True, ideas_count=5, duration=10.5)
    worker._report_result(sample_task, result)
    
    mock_queue.update_task_status.assert_called_with(
        'task-123',
        TaskStatus.COMPLETED,
        result={'ideas_count': 5, 'duration': 10.5}
    )

def test_worker_reports_failure_result(worker_config, mock_queue, mock_plugin, sample_task):
    """Test worker reports failure result to queue."""
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    
    result = TaskResult(success=False, error_message="Test error")
    worker._report_result(sample_task, result)
    
    mock_queue.update_task_status.assert_called_with(
        'task-123',
        TaskStatus.FAILED,
        error="Test error"
    )

# ===== SOLID Compliance Tests =====

def test_worker_follows_srp():
    """Test BaseWorker has single responsibility (task lifecycle)."""
    # BaseWorker should only manage task lifecycle
    # It should NOT:
    # - Implement scraping logic (delegated to plugin)
    # - Manage database schema (delegated to queue)
    # - Handle API endpoints (delegated to API layer)
    
    from src.workers.base_worker import BaseWorker
    import inspect
    
    methods = [m for m in dir(BaseWorker) if not m.startswith('_')]
    
    # Should have minimal public interface
    essential_methods = ['run', 'stop', 'get_status']
    for method in essential_methods:
        assert method in methods, f"Missing essential method: {method}"
    
    # Should not have scraping methods
    assert 'scrape' not in methods
    assert 'download' not in methods

def test_worker_follows_dip(worker_config, mock_queue, mock_plugin):
    """Test BaseWorker depends on abstractions (DIP)."""
    # Worker should accept Protocol types, not concrete classes
    from src.workers.base_worker import BaseWorker
    from typing import get_type_hints
    
    hints = get_type_hints(BaseWorker.__init__)
    
    # Queue should be a Protocol, not concrete class
    assert 'Protocol' in str(hints.get('queue', ''))
    
    # Plugin should be a Protocol, not concrete class  
    assert 'Protocol' in str(hints.get('plugin', ''))

# ===== Performance Tests =====

def test_worker_claims_task_quickly(worker_config, mock_queue, mock_plugin, benchmark):
    """Test task claiming is fast (<10ms)."""
    mock_queue.claim_task.return_value = Mock(spec=Task)
    
    worker = BaseWorker(config=worker_config, queue=mock_queue, plugin=mock_plugin)
    
    # Benchmark task claiming
    result = benchmark(worker._claim_task)
    
    # Should be < 10ms
    assert benchmark.stats.stats.median < 0.010  # 10ms

# ===== Test Configuration =====

# pytest.ini or conftest.py
"""
[pytest]
testpaths = tests/unit
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
"""
```

---

### 2. Task Polling & Claiming Strategies (#003)

#### Test Suite: `test_task_poller.py`

```python
"""Unit tests for TaskPoller and claiming strategies."""

import pytest
import sqlite3
from unittest.mock import Mock, patch
from src.workers.task_poller import TaskPoller, PollerConfig
from src.workers.claiming_strategies import (
    FIFOStrategy, LIFOStrategy, PriorityStrategy
)

@pytest.fixture
def in_memory_db():
    """In-memory SQLite database for testing."""
    conn = sqlite3.connect(':memory:')
    
    # Create task_queue table
    conn.execute("""
        CREATE TABLE task_queue (
            task_id TEXT PRIMARY KEY,
            task_type TEXT NOT NULL,
            parameters TEXT NOT NULL,
            status TEXT DEFAULT 'QUEUED',
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            worker_id TEXT,
            claimed_at TIMESTAMP
        )
    """)
    conn.commit()
    
    yield conn
    conn.close()

def test_fifo_strategy_claims_oldest_first(in_memory_db):
    """Test FIFO strategy claims oldest task first."""
    # Insert tasks in order
    in_memory_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters) VALUES (?, ?, ?)",
        ('task-1', 'youtube_channel', '{}')
    )
    in_memory_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters) VALUES (?, ?, ?)",
        ('task-2', 'youtube_channel', '{}')
    )
    in_memory_db.commit()
    
    strategy = FIFOStrategy()
    poller = TaskPoller(in_memory_db, 'worker-1', PollerConfig(), strategy)
    
    task = poller.claim_task()
    assert task['task_id'] == 'task-1'  # Oldest first

def test_lifo_strategy_claims_newest_first(in_memory_db):
    """Test LIFO strategy claims newest task first."""
    # Insert tasks in order
    in_memory_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters) VALUES (?, ?, ?)",
        ('task-1', 'youtube_channel', '{}')
    )
    in_memory_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters) VALUES (?, ?, ?)",
        ('task-2', 'youtube_channel', '{}')
    )
    in_memory_db.commit()
    
    strategy = LIFOStrategy()
    poller = TaskPoller(in_memory_db, 'worker-1', PollerConfig(), strategy)
    
    task = poller.claim_task()
    assert task['task_id'] == 'task-2'  # Newest first

def test_priority_strategy_claims_high_priority_first(in_memory_db):
    """Test Priority strategy claims high priority task first."""
    # Insert tasks with different priorities
    in_memory_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters, priority) VALUES (?, ?, ?, ?)",
        ('task-low', 'youtube_channel', '{}', 0)
    )
    in_memory_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters, priority) VALUES (?, ?, ?, ?)",
        ('task-high', 'youtube_channel', '{}', 10)
    )
    in_memory_db.commit()
    
    strategy = PriorityStrategy()
    poller = TaskPoller(in_memory_db, 'worker-1', PollerConfig(), strategy)
    
    task = poller.claim_task()
    assert task['task_id'] == 'task-high'  # High priority first

def test_task_claiming_is_atomic(in_memory_db):
    """Test task claiming is atomic (no double-claiming)."""
    # Insert a task
    in_memory_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters) VALUES (?, ?, ?)",
        ('task-1', 'youtube_channel', '{}')
    )
    in_memory_db.commit()
    
    # Create two pollers (simulating two workers)
    poller1 = TaskPoller(in_memory_db, 'worker-1', PollerConfig(), FIFOStrategy())
    poller2 = TaskPoller(in_memory_db, 'worker-2', PollerConfig(), FIFOStrategy())
    
    # Both try to claim
    task1 = poller1.claim_task()
    task2 = poller2.claim_task()
    
    # Only one should succeed
    assert task1 is not None
    assert task2 is None

def test_poller_backoff_on_empty_queue():
    """Test poller uses exponential backoff when queue is empty."""
    config = PollerConfig(
        poll_interval=5,
        max_backoff=60,
        backoff_multiplier=2.0
    )
    
    poller = TaskPoller(Mock(), 'worker-1', config, FIFOStrategy())
    
    # Initial backoff
    assert poller._current_backoff == 5
    
    # Increase backoff
    poller._increase_backoff()
    assert poller._current_backoff == 10
    
    poller._increase_backoff()
    assert poller._current_backoff == 20
    
    # Should cap at max
    for _ in range(10):
        poller._increase_backoff()
    assert poller._current_backoff == 60
```

---

### 3. Plugin System (#005, #009-#011)

#### Test Suite: `test_plugin_registry.py`

```python
"""Unit tests for Plugin Registry."""

import pytest
from unittest.mock import Mock
from src.plugins.registry import PluginRegistry
from src.plugins.base_plugin import PluginBase

def test_register_plugin():
    """Test plugin can be registered."""
    registry = PluginRegistry()
    
    class TestPlugin(PluginBase):
        def get_task_type(self) -> str:
            return 'test_task'
        
        def scrape(self, **params):
            return []
    
    registry.register(TestPlugin)
    
    assert registry.has_plugin('test_task')

def test_get_plugin_by_task_type():
    """Test can retrieve plugin by task type."""
    registry = PluginRegistry()
    
    class TestPlugin(PluginBase):
        def get_task_type(self) -> str:
            return 'test_task'
    
    registry.register(TestPlugin)
    plugin = registry.get_plugin('test_task')
    
    assert isinstance(plugin, TestPlugin)

def test_register_duplicate_plugin_raises_error():
    """Test registering duplicate task type raises error."""
    registry = PluginRegistry()
    
    class TestPlugin1(PluginBase):
        def get_task_type(self) -> str:
            return 'test_task'
    
    class TestPlugin2(PluginBase):
        def get_task_type(self) -> str:
            return 'test_task'
    
    registry.register(TestPlugin1)
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register(TestPlugin2)
```

---

### 4. Parameter Validation (#013)

#### Test Suite: `test_parameter_registry.py`

```python
"""Unit tests for Parameter Registry."""

import pytest
from src.core.parameter_registry import ParameterRegistry, ParameterSchema

def test_validate_valid_parameters():
    """Test validation passes for valid parameters."""
    registry = ParameterRegistry()
    
    schema = ParameterSchema(
        task_type='youtube_channel',
        required_params=['channel_url'],
        optional_params={'max_results': 50}
    )
    registry.register_schema(schema)
    
    params = {'channel_url': '@SnappyStories_1', 'max_results': 10}
    result = registry.validate('youtube_channel', params)
    
    assert result.is_valid is True

def test_validate_missing_required_parameter():
    """Test validation fails for missing required parameter."""
    registry = ParameterRegistry()
    
    schema = ParameterSchema(
        task_type='youtube_channel',
        required_params=['channel_url'],
        optional_params={}
    )
    registry.register_schema(schema)
    
    params = {'max_results': 10}  # Missing channel_url
    result = registry.validate('youtube_channel', params)
    
    assert result.is_valid is False
    assert 'channel_url' in result.errors

def test_apply_defaults():
    """Test default values are applied."""
    registry = ParameterRegistry()
    
    schema = ParameterSchema(
        task_type='youtube_channel',
        required_params=['channel_url'],
        optional_params={'max_results': 50}
    )
    registry.register_schema(schema)
    
    params = {'channel_url': '@SnappyStories_1'}
    validated = registry.apply_defaults('youtube_channel', params)
    
    assert validated['max_results'] == 50  # Default applied
```

---

## Test Execution & Coverage

### Running Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_base_worker.py -v

# Run specific test
pytest tests/unit/test_base_worker.py::test_worker_initialization -v

# Run tests matching pattern
pytest tests/unit/ -k "test_worker_claims" -v

# Run with performance profiling
pytest tests/unit/ --durations=10
```

### Coverage Goals

| Component | Target Coverage | Critical Paths |
|-----------|----------------|----------------|
| BaseWorker | >90% | Task lifecycle, error handling |
| TaskPoller | >85% | Claiming strategies, atomicity |
| Plugin System | >85% | Registration, factory, validation |
| Parameter Registry | >90% | Validation, defaults |
| Error Handler | >80% | Retry logic, classification |
| Database Schema | >75% | PRAGMA settings, indexes |

**Overall Target: >80% coverage**

---

## Test Quality Standards

### Test Naming Convention

```python
def test_<component>_<behavior>_<condition>():
    """Test <what is being tested> <under what condition>."""
    pass

# Examples:
def test_worker_claims_task_successfully():
def test_worker_handles_plugin_error():
def test_poller_uses_fifo_strategy():
```

### Test Structure (AAA Pattern)

```python
def test_example():
    """Test description."""
    # Arrange - Setup test data and mocks
    worker = BaseWorker(...)
    mock_queue.claim_task.return_value = sample_task
    
    # Act - Execute the behavior
    result = worker._process_task(sample_task)
    
    # Assert - Verify the outcome
    assert result.success is True
    mock_queue.update_task_status.assert_called()
```

### Mock Guidelines

```python
# Use spec to ensure mock matches interface
mock_queue = Mock(spec=QueueProtocol)

# Verify calls were made correctly
mock_queue.claim_task.assert_called_once_with(
    worker_id='worker-1',
    task_type='youtube_channel'
)

# Use side_effect for sequences
mock_plugin.scrape.side_effect = [
    ConnectionError(),  # First call fails
    [{'id': '123'}]     # Second call succeeds
]
```

---

## CI/CD Integration

### pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests/unit
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing:skip-covered
    --cov-report=html
    --cov-fail-under=80
    --maxfail=5
markers =
    unit: Unit tests
    slow: Slow-running tests
    windows: Windows-specific tests
```

### Coverage Configuration (`.coveragerc`)

```ini
[run]
source = src
omit =
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

---

## Windows-Specific Testing Considerations

### Path Handling Tests

```python
def test_worker_handles_windows_paths():
    """Test worker handles Windows path separators."""
    import os
    
    # Test with Windows path
    path = r"C:\Users\test\data\queue.db"
    worker = BaseWorker(config=WorkerConfig(queue_db_path=path))
    
    # Should normalize path correctly
    assert os.path.exists(worker.queue_db_path)
```

### SQLite WAL Mode Tests

```python
def test_sqlite_wal_mode_on_windows():
    """Test SQLite WAL mode works on Windows."""
    import sqlite3
    
    conn = sqlite3.connect('test.db')
    conn.execute('PRAGMA journal_mode=WAL')
    result = conn.execute('PRAGMA journal_mode').fetchone()
    
    assert result[0].upper() == 'WAL'
```

---

## Performance Benchmarks

### Task Claiming Speed

```python
def test_task_claiming_latency(benchmark):
    """Benchmark task claiming latency."""
    poller = TaskPoller(...)
    
    # Should be < 10ms (P95)
    result = benchmark(poller.claim_task)
    assert result.stats.stats.p95 < 0.010  # 10ms
```

### Test Suite Execution Time

```bash
# Target: < 5 minutes for all unit tests
$ pytest tests/unit/ --durations=0
```

**Targets**:
- Individual test: < 100ms
- Test file: < 5 seconds
- Full suite: < 5 minutes

---

## Acceptance Criteria

- [ ] Test suite for BaseWorker (20+ tests)
- [ ] Test suite for TaskPoller (15+ tests)
- [ ] Test suite for claiming strategies (12+ tests)
- [ ] Test suite for Plugin Registry (10+ tests)
- [ ] Test suite for Parameter Registry (10+ tests)
- [ ] Test suite for Error Handler (10+ tests)
- [ ] Test coverage >80% overall
- [ ] All tests passing on Linux
- [ ] All tests passing on Windows
- [ ] Fast execution (<5 minutes total)
- [ ] Comprehensive mocking of external dependencies
- [ ] CI/CD integration configured
- [ ] Coverage reports generated (HTML + terminal)
- [ ] SOLID compliance validated through tests
- [ ] Windows-specific tests included
- [ ] Performance benchmarks passing

---

## Deliverables

1. **Test Files** (9 files)
   - `tests/unit/test_base_worker.py` (300+ lines, 20+ tests)
   - `tests/unit/test_task_poller.py` (200+ lines, 15+ tests)
   - `tests/unit/test_claiming_strategies.py` (150+ lines, 12+ tests)
   - `tests/unit/test_plugin_registry.py` (100+ lines, 10+ tests)
   - `tests/unit/test_channel_plugin.py` (100+ lines, 10+ tests)
   - `tests/unit/test_trending_plugin.py` (100+ lines, 10+ tests)
   - `tests/unit/test_keyword_plugin.py` (100+ lines, 10+ tests)
   - `tests/unit/test_parameter_registry.py` (100+ lines, 10+ tests)
   - `tests/unit/test_error_handler.py` (100+ lines, 10+ tests)

2. **Test Configuration**
   - `pytest.ini` - pytest configuration
   - `.coveragerc` - coverage configuration
   - `tests/conftest.py` - shared fixtures

3. **Documentation**
   - Test execution guide
   - Coverage report
   - Windows testing guide

---

## Target Platform

- Windows 10/11
- Python 3.10+
- pytest 7.0+
- pytest-cov 4.0+
- pytest-mock 3.10+

---

## Timeline

- **Day 1** (6-8 hours): BaseWorker, TaskPoller, Claiming Strategies tests
- **Day 2** (6-8 hours): Plugin system, Parameter Registry tests
- **Day 3** (4-6 hours): Error Handler, Database tests, CI/CD integration

**Total**: 2-3 days

---

## Related Issues

- #002: Create Worker Base Class (Component to test)
- #003: Implement Task Polling (Component to test)
- #004: Design Database Schema (Component to test)
- #005: Refactor Plugin Architecture (Component to test)
- #009-#011: Plugin migrations (Components to test)
- #013: Parameter Registration (Component to test)
- #020: Integration Tests (Depends on unit tests)
- #021: Windows Subprocess Testing (Related testing)

---

**Assignee**: Worker04 - QA/Testing Specialist  
**Timeline**: Week 3, Days 5-7  
**Status**: Ready to Start (Dependencies complete)
