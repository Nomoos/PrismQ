"""
Integration tests for failure recovery scenarios.

Tests how the system handles and recovers from various failure conditions.
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
def test_worker_crash_recovery(temp_db, registry):
    """Test task recovery after simulated worker crash."""
    def crash_handler(task: Task):
        raise RuntimeError("Simulated worker crash")
    
    registry.register_handler("crash_task", crash_handler)
    
    # Enqueue task
    with temp_db.transaction() as conn:
        cursor = conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("crash_task", '{"data": "test"}', 100, 1),
        )
        task_id = cursor.lastrowid
    
    # Try to process with first worker (will fail)
    worker1 = WorkerEngine(
        temp_db,
        "worker-crash",
        handler_registry=registry,
    )
    
    worker1.claim_and_process()
    
    # Verify task is marked as failed
    cursor = temp_db.execute(
        "SELECT status FROM task_queue WHERE id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    assert row["status"] == "failed"
    
    # Update handler to succeed
    def success_handler(task: Task):
        return {"status": "recovered"}
    
    registry.register_handler("crash_task", success_handler, allow_override=True)
    
    # Reset task to queued state (manual recovery)
    with temp_db.transaction() as conn:
        conn.execute(
            "UPDATE task_queue SET status = ?, attempts = 0 WHERE id = ?",
            ("queued", task_id),
        )
    
    # Process with second worker
    worker2 = WorkerEngine(
        temp_db,
        "worker-recovery",
        handler_registry=registry,
    )
    
    worker2.claim_and_process()
    
    # Verify task completed
    cursor = temp_db.execute(
        "SELECT status FROM task_queue WHERE id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    assert row["status"] == "completed"


@pytest.mark.integration
def test_partial_batch_failure_recovery(temp_db, registry):
    """Test that batch processing continues after some failures."""
    processed = []
    
    def batch_handler(task: Task):
        import json
        payload = json.loads(task.payload)
        index = payload["index"]
        
        # Fail on even indices
        if index % 2 == 0:
            raise ValueError(f"Failed on index {index}")
        
        processed.append(index)
        return {"status": "success", "index": index}
    
    registry.register_handler("batch_task", batch_handler)
    
    # Enqueue batch of tasks
    with temp_db.transaction() as conn:
        for i in range(10):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("batch_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Process batch
    worker = WorkerEngine(
        temp_db,
        "worker-test",
        handler_registry=registry,
    )
    
    for _ in range(10):
        worker.claim_and_process()
    
    # Verify odd-indexed tasks completed
    assert len(processed) == 5
    assert all(i % 2 == 1 for i in processed)
    
    # Verify even-indexed tasks failed
    cursor = temp_db.execute(
        "SELECT COUNT(*) FROM task_queue WHERE status = ?",
        ("failed",),
    )
    failed_count = cursor.fetchone()[0]
    assert failed_count == 5


@pytest.mark.integration
def test_queue_full_recovery(temp_db, registry):
    """Test behavior when queue is full and tasks are added."""
    claim_count = [0]
    
    def queue_handler(task: Task):
        claim_count[0] += 1
        return {"status": "success"}
    
    registry.register_handler("queue_task", queue_handler)
    
    # Fill queue with tasks
    with temp_db.transaction() as conn:
        for i in range(50):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("queue_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Process some tasks
    worker = WorkerEngine(
        temp_db,
        "worker-test",
        handler_registry=registry,
    )
    
    # Process partial batch
    for _ in range(10):
        worker.claim_and_process()
    
    # Add more tasks while processing
    with temp_db.transaction() as conn:
        for i in range(50, 60):
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("queue_task", f'{{"index": {i}}}', 100, 1),
            )
    
    # Continue processing
    for _ in range(20):
        worker.claim_and_process()
    
    # Verify queue can handle additions during processing
    assert claim_count[0] >= 10


@pytest.mark.integration
def test_stuck_task_recovery(temp_db, registry):
    """Test recovery of tasks stuck in leased state."""
    def stuck_handler(task: Task):
        return {"status": "success"}
    
    registry.register_handler("stuck_task", stuck_handler)
    
    # Enqueue task
    with temp_db.transaction() as conn:
        cursor = conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("stuck_task", '{"data": "test"}', 100, 1),
        )
        task_id = cursor.lastrowid
    
    # Manually mark task as leased (simulating stuck worker)
    with temp_db.transaction() as conn:
        conn.execute(
            """
            UPDATE task_queue 
            SET status = ?, locked_by = ?, reserved_at_utc = datetime('now', '-10 minutes')
            WHERE id = ?
            """,
            ("leased", "stuck-worker", task_id),
        )
    
    # Verify task is stuck
    cursor = temp_db.execute(
        "SELECT status, locked_by FROM task_queue WHERE id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    assert row["status"] == "leased"
    assert row["locked_by"] == "stuck-worker"
    
    # Reset stuck task (manual intervention)
    with temp_db.transaction() as conn:
        conn.execute(
            """
            UPDATE task_queue 
            SET status = ?, locked_by = NULL, reserved_at_utc = NULL
            WHERE id = ? AND status = ? AND locked_by = ?
            """,
            ("queued", task_id, "leased", "stuck-worker"),
        )
    
    # Process with new worker
    worker = WorkerEngine(
        temp_db,
        "worker-recovery",
        handler_registry=registry,
    )
    
    worker.claim_and_process()
    
    # Verify task completed
    cursor = temp_db.execute(
        "SELECT status FROM task_queue WHERE id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    assert row["status"] == "completed"


@pytest.mark.integration
def test_unregistered_task_type_handling(temp_db, registry):
    """Test handling of tasks with unregistered handlers."""
    # Enqueue task without registering handler
    with temp_db.transaction() as conn:
        cursor = conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("unregistered_task", '{"data": "test"}', 100, 1),
        )
        task_id = cursor.lastrowid
    
    # Try to process with worker
    worker = WorkerEngine(
        temp_db,
        "worker-test",
        handler_registry=registry,
    )
    
    # Should claim but fail the task
    worker.claim_and_process()
    
    # Verify task is marked as failed
    cursor = temp_db.execute(
        "SELECT status FROM task_queue WHERE id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    assert row["status"] == "failed"
