"""
Integration tests for multi-worker scenarios.

Tests that multiple workers can operate concurrently without conflicts.
"""

import pytest
import tempfile
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


@pytest.mark.integration
def test_multi_worker_no_duplicate_claims(temp_db, registry):
    """Test that multiple workers don't claim the same task."""
    # Register a simple test handler
    processed_tasks = []
    
    def test_handler(task: Task):
        processed_tasks.append(task.id)
        return {"status": "success"}
    
    registry.register_handler("test_task", test_handler)
    
    # Enqueue 10 tasks
    with temp_db.transaction() as conn:
        for i in range(10):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("test_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Create 3 workers
    workers = [
        WorkerEngine(
            temp_db,
            f"worker-{i}",
            handler_registry=registry,
        )
        for i in range(3)
    ]
    
    # Run workers to claim and process tasks
    for _ in range(5):  # Multiple rounds to process all
        for worker in workers:
            worker.claim_and_process()
    
    # Verify no duplicates were processed
    assert len(processed_tasks) == len(set(processed_tasks)), "Duplicate task processing detected"
    
    # Verify tasks were processed
    assert len(processed_tasks) >= 3, f"Expected at least 3 tasks processed, got {len(processed_tasks)}"


@pytest.mark.integration
def test_multi_worker_load_distribution(temp_db, registry):
    """Test that work is distributed across workers."""
    worker_task_counts = {}
    
    def tracking_handler(task: Task):
        worker_id = task.locked_by
        if worker_id:
            worker_task_counts[worker_id] = worker_task_counts.get(worker_id, 0) + 1
        return {"status": "success"}
    
    registry.register_handler("tracked_task", tracking_handler)
    
    # Enqueue 15 tasks
    with temp_db.transaction() as conn:
        for i in range(15):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("tracked_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Create 3 workers
    workers = [
        WorkerEngine(
            temp_db,
            f"worker-{i}",
            handler_registry=registry,
        )
        for i in range(3)
    ]
    
    # Run workers multiple times to process all tasks
    for _ in range(10):
        for worker in workers:
            worker.claim_and_process()
    
    # Verify work was distributed (at least 2 workers should have processed tasks)
    assert len(worker_task_counts) >= 2, f"Tasks not distributed across workers: {worker_task_counts}"
    
    # Verify tasks were processed
    total_processed = sum(worker_task_counts.values())
    assert total_processed >= 10, f"Expected at least 10 tasks processed, got {total_processed}"


@pytest.mark.integration
def test_multi_worker_priority_handling(temp_db, registry):
    """Test that workers respect task priorities."""
    processed_order = []
    
    def order_tracking_handler(task: Task):
        import json
        payload = json.loads(task.payload)
        processed_order.append(payload["priority"])
        return {"status": "success"}
    
    registry.register_handler("priority_task", order_tracking_handler)
    
    # Enqueue tasks with different priorities (lower = higher priority)
    priorities = [100, 50, 10, 75, 25]
    with temp_db.transaction() as conn:
        for priority in priorities:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("priority_task", f'{{"priority": {priority}}}', priority, 1),
            )
    
    # Create a single worker to process tasks sequentially
    worker = WorkerEngine(
        temp_db,
        "worker-0",
        handler_registry=registry,
    )
    
    # Process all tasks
    for _ in range(5):
        worker.claim_and_process()
    
    # Verify tasks were processed in priority order (lower priority number first)
    expected_order = sorted(priorities)
    assert processed_order == expected_order, f"Expected {expected_order}, got {processed_order}"


@pytest.mark.integration
def test_multi_worker_error_isolation(temp_db, registry):
    """Test that errors in one worker don't affect others."""
    success_count = [0]
    error_count = [0]
    
    def failing_handler(task: Task):
        import json
        payload = json.loads(task.payload)
        if payload.get("should_fail"):
            error_count[0] += 1
            raise ValueError("Intentional failure")
        success_count[0] += 1
        return {"status": "success"}
    
    registry.register_handler("error_task", failing_handler)
    
    # Enqueue mix of success and failure tasks
    with temp_db.transaction() as conn:
        for i in range(10):
            should_fail = i % 2 == 0
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("error_task", f'{{"index": {i}, "should_fail": {str(should_fail).lower()}}}', 100, 1),
            )
    
    # Create 3 workers
    workers = [
        WorkerEngine(
            temp_db,
            f"worker-{i}",
            handler_registry=registry,
        )
        for i in range(3)
    ]
    
    # Run workers
    for _ in range(5):
        for worker in workers:
            worker.claim_and_process()
    
    # Verify both successes and failures occurred
    assert success_count[0] == 5, f"Expected 5 successes, got {success_count[0]}"
    assert error_count[0] >= 5, f"Expected at least 5 errors, got {error_count[0]}"
    
    # Verify some tasks succeeded despite others failing
    cursor = temp_db.execute(
        "SELECT COUNT(*) FROM task_queue WHERE status = ?",
        ("completed",),
    )
    completed_count = cursor.fetchone()[0]
    assert completed_count == 5, "Successful tasks should complete despite failures"


@pytest.mark.integration
def test_worker_no_duplicate_processing(temp_db, registry):
    """Test that no task is processed twice."""
    all_processed = []
    
    def duplicate_check_handler(task: Task):
        all_processed.append(task.id)
        return {"status": "success"}
    
    registry.register_handler("dup_task", duplicate_check_handler)
    
    # Enqueue tasks
    with temp_db.transaction() as conn:
        for i in range(20):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("dup_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Create multiple workers
    workers = [
        WorkerEngine(
            temp_db,
            f"worker-{i}",
            handler_registry=registry,
        )
        for i in range(4)
    ]
    
    # Process tasks
    for _ in range(10):
        for worker in workers:
            worker.claim_and_process()
    
    # Verify no duplicates
    assert len(all_processed) == len(set(all_processed)), f"Found duplicate processing: {all_processed}"
