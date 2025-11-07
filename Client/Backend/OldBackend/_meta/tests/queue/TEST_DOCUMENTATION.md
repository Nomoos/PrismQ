# Queue System Test Suite Documentation

## Overview

Comprehensive test suite for the PrismQ SQLite queue system, implementing Issue #333.

## Test Structure

```
_meta/tests/queue/
├── __init__.py
├── test_task_handler_registry.py  # Unit tests (21 tests)
├── integration/                    # Integration tests (16 tests)
│   ├── test_multi_worker.py
│   ├── test_end_to_end.py
│   └── test_failure_recovery.py
├── performance/                    # Performance benchmarks (7 tests)
│   └── test_benchmarks.py
└── windows/                        # Windows compatibility (9 tests)
    └── test_compatibility.py
```

## Test Categories

### Unit Tests (21 tests)
**File:** `test_task_handler_registry.py`

Tests the TaskHandlerRegistry functionality for Worker 10 (Issue #339):
- Handler registration and validation
- Duplicate handler detection
- Handler retrieval and unregistration
- Global registry management
- Thread-safe concurrent registration

**Run:** `pytest _meta/tests/queue/test_task_handler_registry.py -v`

### Integration Tests (16 tests)
**Files:** `integration/test_*.py`

#### Multi-Worker Tests (5 tests)
Tests concurrent worker operations:
- `test_multi_worker_no_duplicate_claims`: Ensures no task is claimed twice
- `test_multi_worker_load_distribution`: Verifies work distribution across workers
- `test_multi_worker_priority_handling`: Tests priority-based task ordering
- `test_multi_worker_error_isolation`: Ensures worker errors don't affect others
- `test_worker_no_duplicate_processing`: Validates no duplicate processing

#### End-to-End Tests (7 tests)
Tests complete task lifecycle:
- `test_end_to_end_task_lifecycle`: Full lifecycle from enqueue to completion
- `test_task_lifecycle_with_logging`: Integration with task logging
- `test_task_lifecycle_with_metrics`: Integration with queue metrics
- `test_task_lifecycle_with_heartbeat`: Integration with worker heartbeat
- `test_task_lifecycle_with_payload_transformation`: Payload handling
- `test_multiple_tasks_lifecycle`: Processing multiple tasks sequentially

#### Failure Recovery Tests (5 tests)
Tests error handling and recovery:
- `test_worker_crash_recovery`: Recovery after worker failure
- `test_partial_batch_failure_recovery`: Partial batch processing with failures
- `test_queue_full_recovery`: Handling queue at capacity
- `test_stuck_task_recovery`: Recovery of stuck/leased tasks
- `test_unregistered_task_type_handling`: Handling of unregistered task types

**Run:** `pytest _meta/tests/queue/integration/ -v -m integration`

### Performance Benchmarks (7 tests)
**File:** `performance/test_benchmarks.py`

Performance measurement tests:
- `test_task_throughput_single_worker`: Measures tasks/second (target: >10/sec)
- `test_task_latency_measurement`: Measures p50, p95, p99 latency (target: <100ms avg)
- `test_concurrent_worker_scalability`: Tests 4-worker throughput (target: >30/sec)
- `test_database_query_performance`: Measures query performance (target: <50ms)
- `test_enqueue_performance`: Measures enqueue rate (target: >500/sec)
- `test_claim_performance`: Measures claim+process time (target: <50ms)

**Run:** `pytest _meta/tests/queue/performance/ -v -m performance -s`

Note: Use `-s` flag to see benchmark output

### Windows Compatibility Tests (9 tests)
**File:** `windows/test_compatibility.py`

Windows-specific functionality:
- `test_wal_mode_enabled`: Verifies WAL journal mode
- `test_concurrent_database_access`: Tests concurrent file access
- `test_path_handling_with_backslashes`: Windows path compatibility
- `test_busy_timeout_handling`: Verifies busy_timeout configuration
- `test_foreign_keys_enabled`: Validates foreign key constraints
- `test_large_payload_handling`: Tests large payload support (10KB)
- `test_windows_specific_pragmas`: Windows-optimized PRAGMA settings (runs only on Windows)
- `test_path_with_spaces`: Paths with spaces handling
- `test_unicode_in_paths_and_data`: Unicode character support

**Run:** `pytest _meta/tests/queue/windows/ -v -m windows`

## Running Tests

### Run All Queue Tests
```bash
cd Backend
python -m pytest _meta/tests/queue/ -v
```

### Run by Category
```bash
# Integration tests only
pytest _meta/tests/queue/ -v -m integration

# Performance benchmarks only
pytest _meta/tests/queue/ -v -m performance -s

# Windows tests only
pytest _meta/tests/queue/ -v -m windows

# Exclude specific categories
pytest _meta/tests/queue/ -v -m "not performance"
```

### Run Specific Test Files
```bash
pytest _meta/tests/queue/integration/test_multi_worker.py -v
pytest _meta/tests/queue/performance/test_benchmarks.py -v -s
pytest _meta/tests/queue/windows/test_compatibility.py -v
```

## Test Markers

Custom pytest markers are registered in `pyproject.toml`:
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.performance`: Performance benchmarks
- `@pytest.mark.windows`: Windows-specific tests

## Test Coverage

### Current Coverage
- **Total Tests**: 53 tests
- **Passing**: 51 tests
- **Skipped**: 1 test (Windows-specific pragma test requires Windows environment)
- **Platform-dependent**: 1 test (runs only on Windows)
- **Pass Rate**: 96% (51/53 tests pass on Linux)

### Coverage by Component
- **Core Infrastructure**: 41 tests ✅ (from earlier work)
- **Task Handler Registry**: 21 tests ✅
- **Multi-Worker Operations**: 5 tests ✅
- **End-to-End Lifecycle**: 7 tests ✅
- **Failure Recovery**: 5 tests ✅
- **Performance**: 7 tests ✅
- **Windows Compatibility**: 9 tests ✅ (1 skipped on Linux)

## Performance Targets

Based on Issue #337 research:
- **Throughput**: >100 tasks/second (benchmarked at >10/sec single worker, >30/sec with 4 workers)
- **Latency**: <10ms claim, <5ms enqueue (actual: <50ms avg claim+process)
- **Concurrency**: Support 5-10 concurrent workers
- **Database**: <1% SQLITE_BUSY rate

## Test Fixtures

### Common Fixtures
All test files use these fixtures:
- `temp_db`: Creates a temporary SQLite database with schema initialized
- `registry`: Fresh TaskHandlerRegistry for each test

### Cleanup
All fixtures use context managers or pytest teardown to ensure proper cleanup.

## Integration with CI/CD

These tests are ready for CI/CD integration:
```yaml
# Example GitHub Actions workflow
- name: Run Queue Tests
  run: |
    cd Backend
    pip install -e .[dev]
    pytest _meta/tests/queue/ -v --junitxml=test-results.xml
    
- name: Run Performance Benchmarks
  run: |
    pytest _meta/tests/queue/performance/ -v -m performance -s
```

## Troubleshooting

### Common Issues

1. **Transaction errors**: Ensure TaskLogger and WorkerHeartbeat calls are outside transaction contexts
2. **Path issues on Windows**: Use `Path` objects from `pathlib` for cross-platform compatibility
3. **Performance test failures**: Performance targets may vary by system; adjust thresholds as needed

### Debug Mode
```bash
# Run with verbose output and show print statements
pytest _meta/tests/queue/ -v -s --tb=short

# Run with full traceback
pytest _meta/tests/queue/ -v --tb=long

# Run specific test with debugging
pytest _meta/tests/queue/integration/test_multi_worker.py::test_multi_worker_no_duplicate_claims -v -s
```

## Future Enhancements

Potential additions:
- Memory profiling tests with `memory_profiler`
- Stress tests with 100+ workers
- Network latency simulation
- Database corruption recovery tests
- Long-running stability tests (24+ hours)

## References

- Issue #333: Testing - Comprehensive Test Suite
- Issue #337: Research - Concurrency and Performance
- Issue #339: Integration - Task Handler Registry
- Backend README: `Backend/README.md`
- Queue API Documentation: `Backend/src/queue/QUEUE_API.md`
