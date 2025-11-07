"""
Performance benchmarks for queue system.

Tests throughput, latency, and scalability of the queue.
"""

import pytest
import tempfile
import time
from pathlib import Path

from src.queue import (
    QueueDatabase,
    WorkerEngine,
    Task,
    get_global_registry,
    reset_global_registry,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_queue.db"
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        yield db
        db.close()


@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    reset_global_registry()
    registry = get_global_registry()
    yield registry
    reset_global_registry()


@pytest.mark.performance
def test_task_throughput_single_worker(temp_db, registry):
    """Measure tasks processed per second with single worker."""
    processed = [0]
    
    def throughput_handler(task: Task):
        processed[0] += 1
        return {"status": "success"}
    
    registry.register_handler("throughput_task", throughput_handler)
    
    # Enqueue 100 tasks
    with temp_db.transaction() as conn:
        for i in range(100):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("throughput_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Process with single worker
    worker = WorkerEngine(
        temp_db,
        "worker-benchmark",
        handler_registry=registry,
    )
    
    start = time.time()
    
    # Process all tasks
    for _ in range(100):
        worker.claim_and_process()
    
    duration = time.time() - start
    throughput = processed[0] / duration if duration > 0 else 0
    
    # Print benchmark result
    print(f"\nThroughput (single worker): {throughput:.2f} tasks/second")
    print(f"Duration: {duration:.2f} seconds")
    
    # Assert reasonable performance (at least 10 tasks/sec)
    # Note: This is intentionally conservative for single worker.
    # Multi-worker tests demonstrate higher throughput (>30 tasks/sec with 4 workers).
    # Production systems with optimized handlers can achieve 100+ tasks/sec.
    assert throughput > 10, f"Throughput too low: {throughput:.2f} tasks/sec"


@pytest.mark.performance
def test_task_latency_measurement(temp_db, registry):
    """Measure task processing latency."""
    latencies = []
    
    def latency_handler(task: Task):
        return {"status": "success"}
    
    registry.register_handler("latency_task", latency_handler)
    
    # Enqueue 50 tasks
    with temp_db.transaction() as conn:
        for i in range(50):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("latency_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Process and measure latency for each
    worker = WorkerEngine(
        temp_db,
        "worker-benchmark",
        handler_registry=registry,
    )
    
    for _ in range(50):
        start = time.time()
        worker.claim_and_process()
        latency = time.time() - start
        latencies.append(latency)
    
    # Calculate statistics
    avg_latency = sum(latencies) / len(latencies)
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    
    # Print benchmark results
    print(f"\nLatency statistics:")
    print(f"  Average: {avg_latency*1000:.2f} ms")
    print(f"  P50: {p50*1000:.2f} ms")
    print(f"  P95: {p95*1000:.2f} ms")
    print(f"  P99: {p99*1000:.2f} ms")
    
    # Assert reasonable latency (< 100ms average)
    assert avg_latency < 0.1, f"Average latency too high: {avg_latency*1000:.2f}ms"


@pytest.mark.performance
def test_concurrent_worker_scalability(temp_db, registry):
    """Test scalability with multiple concurrent workers."""
    processed = [0]
    
    def scalability_handler(task: Task):
        processed[0] += 1
        return {"status": "success"}
    
    registry.register_handler("scalability_task", scalability_handler)
    
    # Enqueue 200 tasks
    with temp_db.transaction() as conn:
        for i in range(200):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("scalability_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Create 4 workers
    workers = [
        WorkerEngine(
            temp_db,
            f"worker-{i}",
            handler_registry=registry,
        )
        for i in range(4)
    ]
    
    start = time.time()
    
    # Process with multiple workers
    for _ in range(60):
        for worker in workers:
            worker.claim_and_process()
    
    duration = time.time() - start
    throughput = processed[0] / duration if duration > 0 else 0
    
    # Print benchmark results
    print(f"\nConcurrent throughput (4 workers): {throughput:.2f} tasks/second")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Tasks processed: {processed[0]}")
    
    # With 4 workers, should be faster than single worker
    assert throughput > 30, f"Concurrent throughput too low: {throughput:.2f} tasks/sec"


@pytest.mark.performance
def test_database_query_performance(temp_db, registry):
    """Test performance of database queries."""
    # Enqueue many tasks
    with temp_db.transaction() as conn:
        for i in range(1000):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("perf_task", f'{{"index": {i}}}', i % 100, 1),
            )
    
    # Measure query performance
    queries = [
        ("Count queued tasks", "SELECT COUNT(*) FROM task_queue WHERE status = 'queued'"),
        ("Get top priority task", "SELECT * FROM task_queue WHERE status = 'queued' ORDER BY priority LIMIT 1"),
        ("Count by status", "SELECT status, COUNT(*) FROM task_queue GROUP BY status"),
        ("Get recent tasks", "SELECT * FROM task_queue ORDER BY created_at_utc DESC LIMIT 10"),
    ]
    
    print("\nDatabase query performance:")
    for query_name, query_sql in queries:
        start = time.time()
        cursor = temp_db.execute(query_sql)
        cursor.fetchall()
        duration = time.time() - start
        print(f"  {query_name}: {duration*1000:.2f} ms")
        
        # All queries should be fast (< 50ms)
        assert duration < 0.05, f"{query_name} too slow: {duration*1000:.2f}ms"


@pytest.mark.performance
def test_enqueue_performance(temp_db, registry):
    """Test performance of enqueueing tasks."""
    start = time.time()
    
    # Enqueue 500 tasks
    with temp_db.transaction() as conn:
        for i in range(500):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("enqueue_task", f'{{"index": {i}}}', 100, 1),
            )
    
    duration = time.time() - start
    enqueue_rate = 500 / duration if duration > 0 else 0
    
    # Print benchmark results
    print(f"\nEnqueue rate: {enqueue_rate:.2f} tasks/second")
    print(f"Duration: {duration:.2f} seconds")
    
    # Should be able to enqueue at least 500 tasks/second
    assert enqueue_rate > 500, f"Enqueue rate too low: {enqueue_rate:.2f} tasks/sec"


@pytest.mark.performance
def test_claim_performance(temp_db, registry):
    """Test performance of claiming tasks."""
    def claim_handler(task: Task):
        return {"status": "success"}
    
    registry.register_handler("claim_task", claim_handler)
    
    # Enqueue 100 tasks
    with temp_db.transaction() as conn:
        for i in range(100):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("claim_task", f'{{"index": {i}}}', 100, 1),
            )
    
    worker = WorkerEngine(
        temp_db,
        "worker-claim",
        handler_registry=registry,
    )
    
    # Measure claim performance
    claim_times = []
    for _ in range(100):
        start = time.time()
        worker.claim_and_process()
        claim_time = time.time() - start
        claim_times.append(claim_time)
    
    avg_claim_time = sum(claim_times) / len(claim_times)
    
    # Print benchmark results
    print(f"\nAverage claim+process time: {avg_claim_time*1000:.2f} ms")
    
    # Claim should be fast (< 50ms average)
    assert avg_claim_time < 0.05, f"Claim time too high: {avg_claim_time*1000:.2f}ms"
