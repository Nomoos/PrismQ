# Issue #010: Create Integration Tests for Worker System

## Status
New

## Priority
Medium

## Category
Testing

## Description

Create integration tests that validate the complete worker system end-to-end, including task queue interaction, worker execution, result storage, and error recovery. These tests ensure all components work together correctly.

## Problem Statement

Unit tests validate individual components, but we need integration tests to verify that the entire worker system functions correctly when all components interact. This includes task lifecycle, worker coordination, database persistence, and error scenarios.

## Proposed Solution

Create integration test suites that:
- Test complete task lifecycle (queue → execute → complete)
- Validate worker coordination (multiple workers)
- Test error recovery and retry logic
- Verify database persistence
- Test with real SQLite database
- Use realistic test data

## Acceptance Criteria

- [ ] End-to-end task execution tests
- [ ] Multi-worker coordination tests
- [ ] Error recovery and retry tests
- [ ] Database persistence tests
- [ ] Task status transition tests
- [ ] LIFO claiming verification with real DB
- [ ] Priority handling tests
- [ ] Heartbeat mechanism tests
- [ ] All tests pass on Windows
- [ ] Integration test suite runs in < 30 seconds
- [ ] Clear test documentation

## Technical Details

### Implementation Approach

1. Create integration test directory
2. Set up test database fixtures
3. Create end-to-end test scenarios
4. Add multi-worker tests
5. Add error recovery tests
6. Add performance benchmarks

### Files to Modify/Create

- **Create**: `Sources/Content/Shorts/YouTube/tests/integration/test_worker_lifecycle.py`
  - Complete task lifecycle tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/integration/test_multi_worker.py`
  - Multiple worker coordination
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/integration/test_error_recovery.py`
  - Error and retry tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/integration/test_database_persistence.py`
  - Database persistence tests
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/integration/conftest.py`
  - Integration test fixtures
  - Test database setup
  
- **Create**: `Sources/Content/Shorts/YouTube/tests/integration/README.md`
  - Integration test documentation

### Integration Test Examples

```python
# tests/integration/conftest.py - Integration fixtures

import pytest
import sqlite3
import tempfile
from pathlib import Path

@pytest.fixture(scope='function')
def test_database():
    """Create a temporary test database"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'
        
        # Create schema
        conn = sqlite3.connect(db_path)
        
        # Load and execute schema
        from src.core.task_schema import TaskSchemaManager
        schema_mgr = TaskSchemaManager(str(db_path))
        schema_mgr.create_schema()
        
        yield str(db_path)
        
        conn.close()

@pytest.fixture
def integration_config(test_database):
    """Configuration for integration tests"""
    from src.core.config import Config
    
    config = Config()
    config.database_path = test_database
    config.max_results = 5  # Small for fast tests
    return config
```

```python
# tests/integration/test_worker_lifecycle.py

import pytest
import json
from src.core.task_queue import TaskQueueManager, TaskDefinition
from src.workers.channel_worker import YouTubeChannelWorker
from src.core.worker_base import WorkerConfig

def test_complete_task_lifecycle(test_database, integration_config):
    """Test complete task lifecycle: queue → run → complete"""
    
    # 1. Enqueue a task
    queue_mgr = TaskQueueManager(test_database)
    task_def = TaskDefinition(
        task_type='youtube_channel',
        parameters={
            'channel_url': '@SnappyStories_1',
            'max_results': 5
        },
        priority=0
    )
    task_id = queue_mgr.enqueue_task(task_def)
    
    # 2. Verify task is queued
    task = queue_mgr.get_task(task_id)
    assert task['status'] == 'QUEUED'
    
    # 3. Worker claims and executes task
    worker_config = WorkerConfig(
        worker_id='test-worker-001',
        worker_type='youtube_channel'
    )
    
    # Mock the actual scraping for test
    from unittest.mock import Mock, patch
    
    with patch('src.plugins.youtube_channel_plugin.YouTubeChannelPlugin') as mock_plugin:
        # Mock to return test data
        mock_plugin.return_value.scrape_channel.return_value = [
            {
                'source_id': 'test-video-123',
                'title': 'Test Video',
                'description': 'Test Description',
                'tags': ['test'],
                'score': 75.0,
                'metrics': {'views': 1000}
            }
        ]
        
        worker = YouTubeChannelWorker(
            worker_config,
            task_queue=None,  # Will use directly
            db=None,  # Will use directly  
            app_config=integration_config
        )
        
        # Execute task
        result = worker.execute_task({
            'task_id': task_id,
            'task_type': 'youtube_channel',
            'parameters': json.dumps(task_def.parameters)
        })
    
    # 4. Verify results
    assert result['status'] == 'success'
    assert result['ideas_scraped'] > 0
    
    # 5. Update task status
    queue_mgr.update_task_status(
        task_id,
        status='COMPLETED',
        result=result
    )
    
    # 6. Verify task is completed
    task = queue_mgr.get_task(task_id)
    assert task['status'] == 'COMPLETED'
    assert task['completed_at'] is not None

def test_task_status_transitions(test_database):
    """Test valid task status transitions"""
    queue_mgr = TaskQueueManager(test_database)
    
    # Create task
    task_def = TaskDefinition(
        task_type='youtube_channel',
        parameters={'channel_url': '@test', 'max_results': 5}
    )
    task_id = queue_mgr.enqueue_task(task_def)
    
    # QUEUED → RUNNING
    queue_mgr.update_task_status(task_id, 'RUNNING')
    task = queue_mgr.get_task(task_id)
    assert task['status'] == 'RUNNING'
    
    # RUNNING → COMPLETED
    queue_mgr.update_task_status(task_id, 'COMPLETED')
    task = queue_mgr.get_task(task_id)
    assert task['status'] == 'COMPLETED'

def test_lifo_with_real_database(test_database):
    """Test LIFO task claiming with real database"""
    from src.core.task_poller import TaskPoller, PollerConfig
    
    queue_mgr = TaskQueueManager(test_database)
    
    # Enqueue multiple tasks in order
    task_ids = []
    for i in range(3):
        task_def = TaskDefinition(
            task_type='youtube_channel',
            parameters={'channel_url': f'@test-{i}', 'max_results': 5}
        )
        task_id = queue_mgr.enqueue_task(task_def)
        task_ids.append(task_id)
    
    # Create poller
    poller = TaskPoller(test_database, 'worker-1', PollerConfig())
    
    # Claim tasks - should get newest first (LIFO)
    claimed_task = poller.claim_next_task()
    assert claimed_task['task_id'] == task_ids[2]  # Last one enqueued
```

```python
# tests/integration/test_multi_worker.py

import pytest
import threading
import time
from src.core.task_queue import TaskQueueManager, TaskDefinition
from src.core.task_poller import TaskPoller, PollerConfig

def test_multiple_workers_no_conflict(test_database):
    """Test multiple workers don't claim same task"""
    queue_mgr = TaskQueueManager(test_database)
    
    # Enqueue tasks
    for i in range(10):
        task_def = TaskDefinition(
            task_type='youtube_channel',
            parameters={'channel_url': f'@test-{i}', 'max_results': 5}
        )
        queue_mgr.enqueue_task(task_def)
    
    # Track claimed tasks
    claimed_tasks = []
    lock = threading.Lock()
    
    def worker_thread(worker_id):
        """Worker thread that claims tasks"""
        poller = TaskPoller(test_database, worker_id, PollerConfig())
        
        for _ in range(5):  # Each worker tries to claim 5 tasks
            task = poller.claim_next_task()
            if task:
                with lock:
                    claimed_tasks.append((worker_id, task['task_id']))
                time.sleep(0.01)  # Simulate work
    
    # Start multiple workers
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker_thread, args=(f'worker-{i}',))
        threads.append(t)
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    # Verify no duplicate claims
    task_ids = [task_id for _, task_id in claimed_tasks]
    assert len(task_ids) == len(set(task_ids)), "Duplicate task claims detected"

def test_worker_heartbeat(test_database):
    """Test worker heartbeat updates"""
    from src.core.task_poller import TaskPoller, PollerConfig
    
    queue_mgr = TaskQueueManager(test_database)
    
    # Enqueue task
    task_def = TaskDefinition(
        task_type='youtube_channel',
        parameters={'channel_url': '@test', 'max_results': 5}
    )
    task_id = queue_mgr.enqueue_task(task_def)
    
    # Claim task
    poller = TaskPoller(test_database, 'worker-1', PollerConfig())
    task = poller.claim_next_task()
    
    # Get initial heartbeat
    task_data = queue_mgr.get_task(task_id)
    initial_heartbeat = task_data.get('last_heartbeat')
    
    # Wait and update heartbeat
    time.sleep(0.1)
    poller.update_heartbeat(task_id)
    
    # Verify heartbeat updated
    task_data = queue_mgr.get_task(task_id)
    new_heartbeat = task_data.get('last_heartbeat')
    
    if initial_heartbeat and new_heartbeat:
        assert new_heartbeat > initial_heartbeat
```

```python
# tests/integration/test_error_recovery.py

import pytest
from src.core.task_queue import TaskQueueManager, TaskDefinition

def test_task_retry_on_failure(test_database):
    """Test task retry mechanism on failure"""
    queue_mgr = TaskQueueManager(test_database)
    
    # Create task with max retries
    task_def = TaskDefinition(
        task_type='youtube_channel',
        parameters={'channel_url': '@invalid', 'max_results': 5},
        max_retries=3
    )
    task_id = queue_mgr.enqueue_task(task_def)
    
    # Simulate failures
    for i in range(3):
        # Update to RUNNING
        queue_mgr.update_task_status(task_id, 'RUNNING')
        
        # Fail the task
        queue_mgr.update_task_status(
            task_id, 
            'FAILED',
            error=f'Test error {i+1}'
        )
        
        # Check retry count
        task = queue_mgr.get_task(task_id)
        assert task['retry_count'] == i + 1
    
    # After max retries, should stay FAILED
    task = queue_mgr.get_task(task_id)
    assert task['status'] == 'FAILED'
    assert task['retry_count'] == 3

def test_error_with_partial_results(test_database, integration_config):
    """Test handling errors with partial results saved"""
    # This tests that even if worker fails midway,
    # already saved ideas are preserved
    pass  # Implementation depends on worker error handling
```

### Dependencies

- Issue #002-008 - All components must be implemented
- pytest >= 7.0
- Python 3.10+
- Real SQLite database (not mocked)

## Estimated Effort
2 days

## Target Platform
- Windows
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [x] End-to-end workflow tests
- [x] Multi-worker concurrency tests
- [x] Error and retry tests
- [x] Database persistence tests
- [x] Performance benchmarks
- [ ] Windows-specific integration tests (separate issue)
- [ ] Load testing (future)

## Related Issues

- Issue #001 - Master Plan
- Issue #002-008 - Components being integrated
- Issue #009 - Unit Tests
- Issue #011 - Windows-Specific Tests

## Notes

### Test Scenarios

1. **Happy Path**: Queue task → Execute → Complete
2. **Multi-Worker**: Multiple workers, no conflicts
3. **LIFO**: Newest tasks claimed first
4. **Priority**: High priority tasks claimed first
5. **Retry**: Failed tasks retry up to max
6. **Heartbeat**: Long-running tasks update heartbeat
7. **Persistence**: Tasks survive process restart

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific integration test
pytest tests/integration/test_worker_lifecycle.py -v

# Run with real yt-dlp (slow)
pytest tests/integration/ --real-scraping -v
```

### Performance Benchmarks

- Task enqueue: < 10ms
- Task claim: < 20ms
- Worker execution (mocked): < 100ms
- Multi-worker (10 tasks, 3 workers): < 5s

### Future Enhancements

- Load testing (100+ concurrent workers)
- Stress testing (10,000+ tasks)
- Performance profiling
- Memory leak detection
