# Issue #020: Implement Integration Tests

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 04 - QA/Testing Specialist  
**Language**: Python 3.10+ (pytest)  
**Status**: New  
**Priority**: High  
**Duration**: 2 days  
**Dependencies**: #019 (Unit tests complete), #002-#015 (All implementations)

---

## Worker Details: Worker04 - QA/Testing Specialist

**Role**: Integration Testing & System Validation  
**Expertise Required**: 
- Integration testing patterns
- End-to-end test design
- Concurrent testing (multi-worker scenarios)
- SQLite integration testing
- Real database testing (not just mocks)
- Test data management
- Test fixtures and factories

**Collaboration**:
- **Worker02** (Python): Test real worker implementations
- **Worker06** (Database): Test database persistence
- **Worker03** (Full Stack): Test API integration
- **Worker10** (Review): Validate integration test quality

**See**: `_meta/issues/new/Worker04/README.md` for complete role description

---

## Objective

Create comprehensive integration tests that validate the entire worker system end-to-end. Tests must use real components (minimal mocking), real SQLite databases, and verify complete workflows from task creation through execution to completion. Ensure multi-worker scenarios, error recovery, and database persistence all work correctly.

---

## Problem Statement

Unit tests validate individual components in isolation, but we need integration tests to ensure:
1. All components work together correctly
2. Database operations persist correctly
3. Task lifecycle flows end-to-end
4. Multiple workers don't conflict
5. Error recovery works in real scenarios
6. Status updates propagate correctly
7. Performance is acceptable under load

Without integration tests:
- ❌ Component integration bugs won't be caught
- ❌ Database transaction issues won't be found
- ❌ Race conditions won't be detected
- ❌ Real-world scenarios won't be validated
- ❌ Deployment confidence will be low

---

## SOLID Principles in Integration Testing

### Single Responsibility Principle (SRP) ✅
**Test Organization**:
- Each test scenario tests ONE workflow
- Each test file tests ONE integration point
- Test fixtures create ONE type of test environment

```python
# test_worker_lifecycle.py - Tests complete task lifecycle only
# test_multi_worker.py - Tests multi-worker coordination only
# test_error_recovery.py - Tests error handling workflows only
```

### Dependency Inversion Principle (DIP) ✅
**Real Dependencies with Configuration Injection**:
- Use real SQLite (not mocked)
- Use real worker implementations
- Inject test configuration (not production)

```python
@pytest.fixture
def test_database():
    """Create temporary test database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test_queue.db'
        # Create real database with test schema
        yield str(db_path)

def test_integration(test_database):
    """Test uses real database, not mock."""
    worker = BaseWorker(queue_db_path=test_database)
    # Test with real components
```

---

## Integration Test Architecture

### Test Directory Structure

```
Source/Video/YouTube/
└── tests/
    ├── conftest.py                  # Shared fixtures
    ├── unit/                        # Unit tests (Issue #019)
    │   └── ...
    ├── integration/                 # Integration tests (this issue)
    │   ├── __init__.py
    │   ├── conftest.py              # Integration-specific fixtures
    │   ├── test_worker_lifecycle.py
    │   ├── test_multi_worker.py
    │   ├── test_error_recovery.py
    │   ├── test_database_persistence.py
    │   ├── test_api_integration.py
    │   ├── test_task_status_flow.py
    │   └── test_performance.py
    └── e2e/                         # End-to-end tests (future)
        └── ...
```

---

## Integration Test Scenarios

### 1. Complete Task Lifecycle Flow

#### Test Suite: `test_worker_lifecycle.py`

```python
"""Integration tests for complete task lifecycle."""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from src.workers.base_worker import BaseWorker, WorkerConfig
from src.queue.queue_manager import QueueManager
from src.plugins.channel_plugin import YouTubeChannelPlugin

# ===== Fixtures =====

@pytest.fixture
def test_database():
    """Create temporary test database with schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test_queue.db'
        
        # Initialize database schema
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE task_queue (
                task_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                parameters TEXT NOT NULL,
                status TEXT DEFAULT 'QUEUED',
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                worker_id TEXT,
                claimed_at TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                result TEXT,
                retry_count INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE results (
                result_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                source_id TEXT,
                title TEXT,
                description TEXT,
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES task_queue(task_id)
            )
        """)
        conn.commit()
        conn.close()
        
        yield str(db_path)

@pytest.fixture
def queue_manager(test_database):
    """Queue manager with test database."""
    return QueueManager(test_database)

@pytest.fixture
def test_worker(test_database):
    """Worker instance with test configuration."""
    config = WorkerConfig(
        worker_id='test-worker-001',
        task_type='youtube_channel',
        poll_interval=0.1,  # Fast for testing
        max_retries=3
    )
    
    plugin = YouTubeChannelPlugin()
    worker = BaseWorker(
        config=config,
        queue_db_path=test_database,
        plugin=plugin
    )
    
    return worker

# ===== Lifecycle Tests =====

def test_complete_task_lifecycle_success(queue_manager, test_worker):
    """
    Test complete task lifecycle from creation to completion.
    
    Flow:
    1. Create task via QueueManager
    2. Worker claims task
    3. Worker processes task (scrapes)
    4. Worker stores results
    5. Worker updates status to COMPLETED
    6. Verify all status transitions
    """
    # 1. Create task
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={
            'channel_url': '@SnappyStories_1',
            'max_results': 5
        },
        priority=0
    )
    
    # Verify task is queued
    task = queue_manager.get_task(task_id)
    assert task['status'] == 'QUEUED'
    assert task['worker_id'] is None
    
    # 2. Worker claims task
    claimed_task = test_worker.claim_task()
    assert claimed_task is not None
    assert claimed_task['task_id'] == task_id
    
    # Verify status updated to CLAIMED
    task = queue_manager.get_task(task_id)
    assert task['status'] == 'CLAIMED'
    assert task['worker_id'] == 'test-worker-001'
    assert task['claimed_at'] is not None
    
    # 3. Worker processes task
    # Note: This uses real yt-dlp scraping or mocked for CI
    result = test_worker.process_task(claimed_task)
    
    # 4. Verify results stored
    assert result.success is True
    assert result.ideas_count > 0
    
    # 5. Verify status updated to COMPLETED
    task = queue_manager.get_task(task_id)
    assert task['status'] == 'COMPLETED'
    assert task['completed_at'] is not None
    assert task['error_message'] is None
    
    # 6. Verify results in database
    results = queue_manager.get_task_results(task_id)
    assert len(results) > 0
    assert results[0]['source_id'] is not None
    assert results[0]['score'] > 0

def test_task_lifecycle_with_validation_error(queue_manager, test_worker):
    """
    Test task lifecycle when parameters are invalid.
    
    Flow:
    1. Create task with invalid parameters
    2. Worker claims task
    3. Worker attempts processing
    4. Validation fails
    5. Status updated to FAILED
    6. Error message recorded
    """
    # 1. Create task with missing required parameter
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={'max_results': 5},  # Missing channel_url
        priority=0
    )
    
    # 2. Worker claims task
    claimed_task = test_worker.claim_task()
    assert claimed_task is not None
    
    # 3. Worker attempts processing (should fail validation)
    result = test_worker.process_task(claimed_task)
    
    # 4. Verify failure
    assert result.success is False
    assert 'channel_url' in result.error_message
    
    # 5. Verify status and error recorded
    task = queue_manager.get_task(task_id)
    assert task['status'] == 'FAILED'
    assert task['error_message'] is not None
    assert 'channel_url' in task['error_message']
    assert task['retry_count'] == 0  # No retry for validation errors

def test_task_status_transitions(queue_manager, test_worker):
    """
    Test all valid task status transitions.
    
    Valid transitions:
    - QUEUED → CLAIMED → RUNNING → COMPLETED
    - QUEUED → CLAIMED → RUNNING → FAILED
    - FAILED → QUEUED (retry)
    """
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={'channel_url': '@SnappyStories_1', 'max_results': 5}
    )
    
    # QUEUED → CLAIMED
    queue_manager.update_task_status(task_id, 'CLAIMED', worker_id='test-worker-001')
    task = queue_manager.get_task(task_id)
    assert task['status'] == 'CLAIMED'
    
    # CLAIMED → RUNNING
    queue_manager.update_task_status(task_id, 'RUNNING')
    task = queue_manager.get_task(task_id)
    assert task['status'] == 'RUNNING'
    assert task['started_at'] is not None
    
    # RUNNING → COMPLETED
    queue_manager.update_task_status(
        task_id,
        'COMPLETED',
        result={'ideas_count': 5}
    )
    task = queue_manager.get_task(task_id)
    assert task['status'] == 'COMPLETED'
    assert task['completed_at'] is not None

def test_lifo_task_claiming(queue_manager, test_worker):
    """
    Test LIFO task claiming (newest first).
    
    Create multiple tasks and verify worker claims newest first.
    """
    # Create tasks in order
    task_ids = []
    for i in range(3):
        task_id = queue_manager.create_task(
            task_type='youtube_channel',
            parameters={'channel_url': f'@test-{i}', 'max_results': 5}
        )
        task_ids.append(task_id)
    
    # Worker should claim newest task (LIFO)
    claimed_task = test_worker.claim_task()
    assert claimed_task['task_id'] == task_ids[2]  # Last one created

---

### 2. Multi-Worker Coordination

#### Test Suite: `test_multi_worker.py`

```python
"""Integration tests for multi-worker scenarios."""

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor

def test_multiple_workers_no_double_claiming(queue_manager, test_database):
    """
    Test multiple workers don't claim the same task.
    
    Scenario:
    - Create 10 tasks
    - Start 3 workers concurrently
    - Verify each task claimed by exactly one worker
    """
    # Create tasks
    task_ids = []
    for i in range(10):
        task_id = queue_manager.create_task(
            task_type='youtube_channel',
            parameters={'channel_url': f'@test-{i}', 'max_results': 5}
        )
        task_ids.append(task_id)
    
    # Track claimed tasks
    claimed_tasks = []
    lock = threading.Lock()
    
    def worker_thread(worker_id):
        """Worker thread that claims tasks."""
        worker = BaseWorker(
            config=WorkerConfig(
                worker_id=worker_id,
                task_type='youtube_channel'
            ),
            queue_db_path=test_database,
            plugin=YouTubeChannelPlugin()
        )
        
        # Try to claim multiple tasks
        for _ in range(5):
            task = worker.claim_task()
            if task:
                with lock:
                    claimed_tasks.append({
                        'worker_id': worker_id,
                        'task_id': task['task_id']
                    })
                time.sleep(0.01)  # Simulate work
    
    # Start workers
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(worker_thread, f'worker-{i}')
            for i in range(3)
        ]
        
        # Wait for completion
        for future in futures:
            future.result()
    
    # Verify no double-claiming
    task_ids_claimed = [c['task_id'] for c in claimed_tasks]
    assert len(task_ids_claimed) == len(set(task_ids_claimed)), \
        "Duplicate task claims detected!"
    
    # Verify all tasks claimed
    assert len(claimed_tasks) == 10

def test_worker_load_balancing(queue_manager, test_database):
    """
    Test tasks are distributed across workers.
    
    Verify roughly equal distribution of tasks among workers.
    """
    # Create 30 tasks
    for i in range(30):
        queue_manager.create_task(
            task_type='youtube_channel',
            parameters={'channel_url': f'@test-{i}', 'max_results': 5}
        )
    
    # Track claims by worker
    claims_by_worker = {'worker-0': 0, 'worker-1': 0, 'worker-2': 0}
    
    def worker_thread(worker_id):
        """Worker thread."""
        worker = BaseWorker(
            config=WorkerConfig(worker_id=worker_id, task_type='youtube_channel'),
            queue_db_path=test_database,
            plugin=YouTubeChannelPlugin()
        )
        
        # Claim all available tasks
        while True:
            task = worker.claim_task()
            if not task:
                break
            claims_by_worker[worker_id] += 1
            time.sleep(0.01)
    
    # Start workers
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(worker_thread, f'worker-{i}')
            for i in range(3)
        ]
        for future in futures:
            future.result()
    
    # Verify distribution is roughly equal (within 20% variance)
    avg_claims = sum(claims_by_worker.values()) / 3
    for worker_id, claims in claims_by_worker.items():
        variance = abs(claims - avg_claims) / avg_claims
        assert variance < 0.2, f"{worker_id} has unbalanced load: {claims} vs avg {avg_claims}"

def test_worker_heartbeat_updates(queue_manager, test_worker):
    """
    Test worker sends heartbeat updates during processing.
    
    Verify heartbeat timestamp updates during long-running task.
    """
    # Create task
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={'channel_url': '@SnappyStories_1', 'max_results': 50}
    )
    
    # Mock plugin to be slow
    def slow_scrape(**params):
        time.sleep(3)  # Simulate slow scraping
        return [{'source_id': 'video-123', 'title': 'Test', 'score': 75.0}]
    
    test_worker.plugin.scrape = slow_scrape
    
    # Process task
    claimed_task = test_worker.claim_task()
    test_worker.process_task(claimed_task)
    
    # Verify heartbeat was updated
    task = queue_manager.get_task(task_id)
    # Implementation should have heartbeat field
    # assert task.get('last_heartbeat') is not None

---

### 3. Error Recovery & Retry Logic

#### Test Suite: `test_error_recovery.py`

```python
"""Integration tests for error handling and recovery."""

import pytest
from unittest.mock import patch

def test_task_retry_on_network_error(queue_manager, test_worker):
    """
    Test task is retried on network error.
    
    Flow:
    1. Task processing fails with network error
    2. Task status set to FAILED
    3. Retry count incremented
    4. Task re-queued for retry
    5. Subsequent attempt succeeds
    """
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={'channel_url': '@SnappyStories_1', 'max_results': 5}
    )
    
    # Mock plugin to fail once, then succeed
    call_count = [0]
    
    def mock_scrape(**params):
        call_count[0] += 1
        if call_count[0] == 1:
            raise ConnectionError("Network timeout")
        return [{'source_id': 'video-123', 'title': 'Test', 'score': 75.0}]
    
    test_worker.plugin.scrape = mock_scrape
    
    # First attempt - should fail and retry
    claimed_task = test_worker.claim_task()
    result1 = test_worker.process_task(claimed_task)
    
    assert result1.success is False
    
    # Verify retry count updated
    task = queue_manager.get_task(task_id)
    assert task['retry_count'] == 1
    assert task['status'] in ['FAILED', 'QUEUED']  # Re-queued for retry
    
    # Second attempt - should succeed
    claimed_task = test_worker.claim_task()
    result2 = test_worker.process_task(claimed_task)
    
    assert result2.success is True
    assert call_count[0] == 2

def test_task_not_retried_on_validation_error(queue_manager, test_worker):
    """
    Test task is NOT retried on validation error.
    
    Validation errors are permanent - no retry.
    """
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={'invalid_param': 'value'},  # Invalid parameters
        priority=0
    )
    
    # Process task
    claimed_task = test_worker.claim_task()
    result = test_worker.process_task(claimed_task)
    
    assert result.success is False
    
    # Verify NOT retried
    task = queue_manager.get_task(task_id)
    assert task['retry_count'] == 0  # No retry
    assert task['status'] == 'FAILED'

def test_max_retries_exceeded(queue_manager, test_worker):
    """
    Test task fails permanently after max retries.
    
    After max_retries attempts, task should be marked permanently failed.
    """
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={'channel_url': '@SnappyStories_1', 'max_results': 5}
    )
    
    # Mock plugin to always fail
    test_worker.plugin.scrape = lambda **params: (_ for _ in ()).throw(
        ConnectionError("Network timeout")
    )
    
    # Try processing multiple times
    for attempt in range(3):  # max_retries = 3
        claimed_task = test_worker.claim_task()
        if claimed_task:
            result = test_worker.process_task(claimed_task)
            assert result.success is False
    
    # Verify permanently failed
    task = queue_manager.get_task(task_id)
    assert task['retry_count'] >= 3
    assert task['status'] == 'FAILED'
    # Should NOT be re-queued

---

### 4. Database Persistence

#### Test Suite: `test_database_persistence.py`

```python
"""Integration tests for database persistence."""

import pytest
import sqlite3

def test_task_persists_across_connections(test_database, queue_manager):
    """
    Test task data persists across database connections.
    
    Create task, close connection, reopen, verify task still exists.
    """
    # Create task
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={'channel_url': '@SnappyStories_1', 'max_results': 5}
    )
    
    # Close and reopen connection
    queue_manager.close()
    
    new_queue_manager = QueueManager(test_database)
    task = new_queue_manager.get_task(task_id)
    
    assert task is not None
    assert task['task_id'] == task_id
    assert task['status'] == 'QUEUED'

def test_results_persist_correctly(test_database, queue_manager, test_worker):
    """
    Test scraping results are persisted correctly.
    
    Verify all result fields are saved and retrievable.
    """
    task_id = queue_manager.create_task(
        task_type='youtube_channel',
        parameters={'channel_url': '@SnappyStories_1', 'max_results': 5}
    )
    
    # Process task
    claimed_task = test_worker.claim_task()
    test_worker.process_task(claimed_task)
    
    # Retrieve results
    results = queue_manager.get_task_results(task_id)
    
    assert len(results) > 0
    
    # Verify result structure
    result = results[0]
    assert result['source_id'] is not None
    assert result['title'] is not None
    assert result['score'] is not None
    assert result['task_id'] == task_id

def test_concurrent_writes_no_corruption(test_database):
    """
    Test concurrent writes don't corrupt database.
    
    Multiple workers writing results simultaneously should be safe.
    """
    # Start multiple workers writing concurrently
    def write_results(worker_id):
        queue_mgr = QueueManager(test_database)
        
        for i in range(10):
            task_id = queue_mgr.create_task(
                task_type='youtube_channel',
                parameters={'channel_url': f'@test-{worker_id}-{i}', 'max_results': 5}
            )
            
            # Simulate result storage
            queue_mgr.store_result(
                task_id=task_id,
                source_id=f'video-{worker_id}-{i}',
                title=f'Test Video {i}',
                score=75.0
            )
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(write_results, f'worker-{i}')
            for i in range(5)
        ]
        for future in futures:
            future.result()
    
    # Verify database integrity
    conn = sqlite3.connect(test_database)
    count = conn.execute("SELECT COUNT(*) FROM task_queue").fetchone()[0]
    conn.close()
    
    assert count == 50  # 5 workers * 10 tasks each

---

## Performance Integration Tests

### Test Suite: `test_performance.py`

```python
"""Performance integration tests."""

import pytest
import time

def test_task_processing_throughput(queue_manager, test_database):
    """
    Test system can process tasks at acceptable rate.
    
    Target: >5 tasks/second with single worker
    """
    # Create 50 tasks
    for i in range(50):
        queue_manager.create_task(
            task_type='youtube_channel',
            parameters={'channel_url': f'@test-{i}', 'max_results': 5}
        )
    
    # Mock fast plugin
    class FastPlugin:
        def scrape(self, **params):
            return [{'source_id': 'video-123', 'title': 'Test', 'score': 75.0}]
    
    worker = BaseWorker(
        config=WorkerConfig(worker_id='perf-worker', task_type='youtube_channel'),
        queue_db_path=test_database,
        plugin=FastPlugin()
    )
    
    # Process all tasks
    start_time = time.time()
    processed = 0
    
    while True:
        task = worker.claim_task()
        if not task:
            break
        worker.process_task(task)
        processed += 1
    
    elapsed = time.time() - start_time
    throughput = processed / elapsed
    
    print(f"Processed {processed} tasks in {elapsed:.2f}s ({throughput:.2f} tasks/s)")
    assert throughput > 5  # >5 tasks/second

def test_database_query_latency(test_database, queue_manager):
    """
    Test database queries are fast.
    
    Task claiming should be <10ms (P95)
    """
    # Create tasks
    for i in range(100):
        queue_manager.create_task(
            task_type='youtube_channel',
            parameters={'channel_url': f'@test-{i}', 'max_results': 5}
        )
    
    # Measure claim latency
    latencies = []
    
    for _ in range(50):
        start = time.time()
        task = queue_manager.claim_next_task('youtube_channel', 'test-worker')
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)
    
    # Calculate P95
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    
    print(f"Task claiming P95 latency: {p95:.2f}ms")
    assert p95 < 10  # <10ms

---

## Test Execution & Configuration

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with real yt-dlp (slow, requires network)
pytest tests/integration/ --real-scraping -v

# Run specific test file
pytest tests/integration/test_worker_lifecycle.py -v

# Run with performance profiling
pytest tests/integration/ --durations=10

# Run multi-worker tests only
pytest tests/integration/test_multi_worker.py -v
```

### pytest Configuration

```ini
[tool:pytest]
markers =
    integration: Integration tests
    slow: Slow-running tests (>1s)
    requires_network: Tests requiring network access
    
# Integration test settings
integration_addopts = 
    --tb=short
    --maxfail=3
    --timeout=60
```

---

## Acceptance Criteria

- [ ] End-to-end task lifecycle tests (5+ scenarios)
- [ ] Multi-worker coordination tests (3+ scenarios)
- [ ] Error recovery and retry tests (5+ scenarios)
- [ ] Database persistence tests (4+ scenarios)
- [ ] Performance integration tests (2+ scenarios)
- [ ] All tests pass with real SQLite database
- [ ] All tests pass on Windows
- [ ] Multi-worker tests verify no race conditions
- [ ] Tests complete in <30 seconds (with mocked scraping)
- [ ] Tests are reliable and repeatable
- [ ] Clear test failure messages
- [ ] Integration test documentation complete

---

## Deliverables

1. **Integration Test Files** (5 files)
   - `tests/integration/test_worker_lifecycle.py` (300+ lines, 10+ tests)
   - `tests/integration/test_multi_worker.py` (250+ lines, 8+ tests)
   - `tests/integration/test_error_recovery.py` (250+ lines, 8+ tests)
   - `tests/integration/test_database_persistence.py` (200+ lines, 6+ tests)
   - `tests/integration/test_performance.py` (150+ lines, 4+ tests)

2. **Test Configuration**
   - `tests/integration/conftest.py` - Integration fixtures
   - Integration test documentation

3. **Test Reports**
   - Integration test results
   - Performance benchmarks
   - Coverage integration with unit tests

---

## Target Platform

- Windows 10/11
- Python 3.10+
- pytest 7.0+
- Real SQLite database (not mocked)

---

## Timeline

- **Day 1** (6-8 hours): Lifecycle, Multi-worker, Error recovery tests
- **Day 2** (4-6 hours): Database persistence, Performance tests, Documentation

**Total**: 2 days

---

## Related Issues

- #019: Unit Tests (Dependency - must complete first)
- #002-#015: All implementations (Components being tested)
- #021: Windows Subprocess Testing (Related testing)
- #022: Performance Testing (Related to performance integration tests)

---

**Assignee**: Worker04 - QA/Testing Specialist  
**Timeline**: Week 4, Days 1-2  
**Status**: Ready to Start (After #019)
