# Issue #009: Create Comprehensive Worker Unit Tests

## Status
New

## Priority
High

## Category
Testing

## Description

Create comprehensive unit tests for all YouTube worker components including worker base class, task poller, workers, and parameter registry. Ensure >80% code coverage and validate SOLID principles compliance.

## Problem Statement

The worker-based architecture needs thorough testing to ensure reliability, correctness, and maintainability. Unit tests must cover all core functionality, edge cases, error scenarios, and integration points.

## Proposed Solution

Create a comprehensive test suite that:
- Tests all worker components in isolation
- Uses mocks for dependencies
- Covers happy paths and error cases
- Validates SOLID principles
- Achieves >80% code coverage
- Runs fast (< 5 seconds total)

## Acceptance Criteria

- [ ] Test suite for `YouTubeWorkerBase`
- [ ] Test suite for `TaskPoller`
- [ ] Test suite for `YouTubeChannelWorker`
- [ ] Test suite for `YouTubeTrendingWorker`
- [ ] Test suite for `YouTubeKeywordWorker`
- [ ] Test suite for `ParameterVariantRegistry`
- [ ] Test suite for `TaskSchemaManager`
- [ ] Mock objects for dependencies (DB, TaskQueue, Config)
- [ ] Code coverage >80%
- [ ] All tests pass on Windows
- [ ] pytest configuration
- [ ] CI/CD integration ready

## Technical Details

### Implementation Approach

1. Create test files for each component
2. Implement mock objects
3. Write tests for happy paths
4. Write tests for error cases
5. Write tests for edge cases
6. Add pytest fixtures
7. Configure coverage reporting

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/tests/test_worker_base.py`
  - Worker base class tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/test_task_poller.py`
  - Task polling tests
  - LIFO verification
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/test_channel_worker.py`
  - Channel worker tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/test_trending_worker.py`
  - Trending worker tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/test_keyword_worker.py`
  - Keyword worker tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/test_variant_registry.py`
  - Registry tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/test_task_schema.py`
  - Schema tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/conftest.py`
  - pytest fixtures
  - Mock objects
  
- **Modify**: `Sources/Content/Shorts/YouTube/pytest.ini`
  - pytest configuration
  
- **Modify**: `Sources/Content/Shorts/YouTube/.coveragerc`
  - Coverage configuration

### Test Structure

```python
# tests/conftest.py - Shared fixtures and mocks

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, Optional

@pytest.fixture
def mock_config():
    """Mock application config"""
    config = Mock()
    config.database_path = ':memory:'
    config.youtube_api_key = 'test_key'
    config.max_results = 50
    return config

@pytest.fixture
def mock_database():
    """Mock database"""
    db = Mock()
    db.insert_idea = Mock(return_value=True)
    db.get_idea = Mock(return_value=None)
    return db

@pytest.fixture
def mock_task_queue():
    """Mock task queue"""
    queue = Mock()
    queue.claim_task = Mock(return_value=None)
    queue.update_task_status = Mock()
    return queue

@pytest.fixture
def worker_config():
    """Worker configuration"""
    from src.core.worker_base import WorkerConfig
    return WorkerConfig(
        worker_id='test-worker-001',
        worker_type='youtube_channel',
        poll_interval=1,
        max_retries=3
    )

@pytest.fixture
def sample_task():
    """Sample task for testing"""
    return {
        'task_id': 'task-123',
        'task_type': 'youtube_channel',
        'parameters': '{"channel_url": "@SnappyStories_1", "max_results": 5}',
        'priority': 0,
        'created_at': '2025-01-01 00:00:00'
    }
```

```python
# tests/test_worker_base.py - Worker base class tests

import pytest
from src.core.worker_base import YouTubeWorkerBase, WorkerConfig

class TestWorker(YouTubeWorkerBase):
    """Concrete worker for testing"""
    
    def execute_task(self, task):
        return {'status': 'success'}
    
    def validate_parameters(self, params):
        return True

def test_worker_initialization(worker_config, mock_task_queue):
    """Test worker can be initialized"""
    worker = TestWorker(worker_config, mock_task_queue)
    assert worker.config == worker_config
    assert worker.task_queue == mock_task_queue

def test_worker_poll_and_execute_no_task(worker_config, mock_task_queue):
    """Test polling when no tasks available"""
    mock_task_queue.claim_task.return_value = None
    worker = TestWorker(worker_config, mock_task_queue)
    
    # Should not raise, should backoff
    # Implementation will sleep, so we mock or test separately
    pass

def test_worker_poll_and_execute_with_task(
    worker_config, mock_task_queue, sample_task
):
    """Test polling and executing a task"""
    mock_task_queue.claim_task.return_value = sample_task
    worker = TestWorker(worker_config, mock_task_queue)
    
    # Execute one iteration
    result = worker.execute_task(sample_task)
    assert result['status'] == 'success'

def test_worker_error_handling(worker_config, mock_task_queue):
    """Test worker error handling"""
    class FailingWorker(YouTubeWorkerBase):
        def execute_task(self, task):
            raise ValueError("Test error")
        
        def validate_parameters(self, params):
            return True
    
    worker = FailingWorker(worker_config, mock_task_queue)
    
    with pytest.raises(ValueError):
        worker.execute_task({'task_id': 'test'})
```

```python
# tests/test_task_poller.py - Task poller tests

import pytest
import sqlite3
from src.core.task_poller import TaskPoller, PollerConfig

@pytest.fixture
def test_db():
    """In-memory test database"""
    conn = sqlite3.connect(':memory:')
    
    # Create schema
    conn.execute("""
        CREATE TABLE task_queue (
            task_id TEXT PRIMARY KEY,
            task_type TEXT NOT NULL,
            parameters TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'QUEUED',
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            worker_id TEXT,
            started_at TIMESTAMP
        )
    """)
    
    conn.commit()
    return conn

def test_claim_task_lifo(test_db):
    """Test LIFO task claiming (newest first)"""
    # Insert tasks in order
    test_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters) VALUES (?, ?, ?)",
        ('task-1', 'youtube_channel', '{}')
    )
    test_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters) VALUES (?, ?, ?)",
        ('task-2', 'youtube_channel', '{}')
    )
    test_db.commit()
    
    poller = TaskPoller(':memory:', 'worker-1', PollerConfig())
    
    # Should claim task-2 first (newest)
    task = poller.claim_next_task()
    assert task['task_id'] == 'task-2'

def test_claim_task_atomic(test_db):
    """Test atomic task claiming (no double-claiming)"""
    # Insert a task
    test_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters) VALUES (?, ?, ?)",
        ('task-1', 'youtube_channel', '{}')
    )
    test_db.commit()
    
    poller1 = TaskPoller(':memory:', 'worker-1', PollerConfig())
    poller2 = TaskPoller(':memory:', 'worker-2', PollerConfig())
    
    # Both try to claim
    task1 = poller1.claim_next_task()
    task2 = poller2.claim_next_task()
    
    # Only one should succeed
    assert task1 is not None
    assert task2 is None

def test_claim_task_priority(test_db):
    """Test priority-based task claiming"""
    # Insert tasks with different priorities
    test_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters, priority) VALUES (?, ?, ?, ?)",
        ('task-low', 'youtube_channel', '{}', 0)
    )
    test_db.execute(
        "INSERT INTO task_queue (task_id, task_type, parameters, priority) VALUES (?, ?, ?, ?)",
        ('task-high', 'youtube_channel', '{}', 10)
    )
    test_db.commit()
    
    poller = TaskPoller(':memory:', 'worker-1', PollerConfig())
    
    # Should claim high priority first
    task = poller.claim_next_task()
    assert task['task_id'] == 'task-high'

def test_backoff_mechanism():
    """Test exponential backoff when queue empty"""
    config = PollerConfig(poll_interval=5, max_backoff=60, backoff_multiplier=2.0)
    poller = TaskPoller(':memory:', 'worker-1', config)
    
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

```python
# tests/test_channel_worker.py - Channel worker tests

import pytest
from src.workers.channel_worker import YouTubeChannelWorker

def test_validate_parameters_valid():
    """Test parameter validation with valid params"""
    worker = YouTubeChannelWorker(None, None, None, None)
    
    params = {'channel_url': '@SnappyStories_1', 'max_results': 50}
    assert worker.validate_parameters(params) is True

def test_validate_parameters_missing_required():
    """Test parameter validation with missing required field"""
    worker = YouTubeChannelWorker(None, None, None, None)
    
    params = {'max_results': 50}  # Missing channel_url
    assert worker.validate_parameters(params) is False

def test_validate_parameters_invalid_url():
    """Test parameter validation with invalid URL"""
    worker = YouTubeChannelWorker(None, None, None, None)
    
    params = {'channel_url': 'invalid-url'}
    assert worker.validate_parameters(params) is False

def test_execute_task_success(
    worker_config, mock_task_queue, mock_database, mock_config, sample_task
):
    """Test successful task execution"""
    worker = YouTubeChannelWorker(
        worker_config, mock_task_queue, mock_database, mock_config
    )
    
    # Mock plugin to return test data
    worker._plugin = Mock()
    worker._plugin.scrape_channel = Mock(return_value=[
        {
            'source_id': 'video-123',
            'title': 'Test Video',
            'description': 'Test Description',
            'tags': ['test'],
            'score': 75.0,
            'metrics': {'views': 1000}
        }
    ])
    
    result = worker.execute_task(sample_task)
    
    assert result['status'] == 'success'
    assert result['ideas_scraped'] == 1
    assert mock_database.insert_idea.called
```

### Dependencies

- pytest >= 7.0
- pytest-cov >= 4.0
- pytest-mock >= 3.10
- Python 3.10+

### Test Coverage Goals

- Worker Base: >90%
- Task Poller: >85%
- Channel Worker: >80%
- Trending Worker: >80%
- Keyword Worker: >80%
- Registry: >90%
- Schema: >85%

**Overall: >80% coverage**

## Estimated Effort
2 days

## Target Platform
- Windows
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [x] Unit tests with mocks
- [x] Isolated component tests
- [x] Happy path tests
- [x] Error case tests
- [x] Edge case tests
- [x] LIFO verification
- [x] Atomic operations tests
- [ ] Windows-specific tests (separate issue)
- [ ] Integration tests (separate issue)

## Related Issues

- Issue #001 - Master Plan
- Issue #002-008 - Components to test
- Issue #010 - Integration Tests
- Issue #011 - Windows-Specific Tests

## Notes

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_worker_base.py      # Base class tests
├── test_task_poller.py      # Poller tests
├── test_channel_worker.py   # Channel worker
├── test_trending_worker.py  # Trending worker
├── test_keyword_worker.py   # Keyword worker
├── test_variant_registry.py # Registry tests
└── test_task_schema.py      # Schema tests
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test file
pytest tests/test_worker_base.py -v

# Run specific test
pytest tests/test_worker_base.py::test_worker_initialization -v
```

### Mocking Strategy

- Mock external dependencies (yt-dlp, database)
- Use in-memory SQLite for database tests
- Mock task queue for worker tests
- Use fixtures for reusable test data
