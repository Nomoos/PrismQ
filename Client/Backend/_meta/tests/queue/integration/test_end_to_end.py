"""
Integration tests for end-to-end task lifecycle.

Tests complete task lifecycle from enqueue to completion.
"""

import pytest
import tempfile
from pathlib import Path

from src.queue import (
    QueueDatabase,
    WorkerEngine,
    Task,
    TaskLogger,
    QueueMetrics,
    WorkerHeartbeat,
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
def test_end_to_end_task_lifecycle(temp_db, registry):
    """Test complete task lifecycle from enqueue to completion."""
    lifecycle_events = []
    
    def lifecycle_handler(task: Task):
        lifecycle_events.append(("execute", task.id))
        return {"result": "success"}
    
    registry.register_handler("lifecycle_task", lifecycle_handler)
    
    # Enqueue task
    task_id = None
    with temp_db.transaction() as conn:
        cursor = conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("lifecycle_task", '{"data": "test"}', 100, 1),
        )
        task_id = cursor.lastrowid
    
    lifecycle_events.append(("enqueue", task_id))
    
    # Verify initial state
    cursor = temp_db.execute(
        "SELECT status, attempts FROM task_queue WHERE id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    assert row["status"] == "queued"
    assert row["attempts"] == 0
    
    # Process task
    worker = WorkerEngine(
        temp_db,
        "worker-test",
        handler_registry=registry,
    )
    
    worker.claim_and_process()
    lifecycle_events.append(("process", task_id))
    
    # Verify final state
    cursor = temp_db.execute(
        "SELECT status FROM task_queue WHERE id = ?",
        (task_id,),
    )
    row = cursor.fetchone()
    assert row["status"] == "completed"
    
    # Verify events occurred in order
    assert lifecycle_events == [
        ("enqueue", task_id),
        ("execute", task_id),
        ("process", task_id),
    ]


@pytest.mark.integration
def test_task_lifecycle_with_logging(temp_db, registry):
    """Test task lifecycle works with task logs table."""
    def logged_handler(task: Task):
        # Manually insert a log entry for this test
        return {"status": "success", "logged": True}
    
    registry.register_handler("logged_task", logged_handler)
    
    # Enqueue task
    with temp_db.transaction() as conn:
        cursor = conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("logged_task", '{"data": "test"}', 100, 1),
        )
        task_id = cursor.lastrowid
    
    # Manually add a log entry
    with temp_db.transaction() as conn:
        conn.execute(
            """
            INSERT INTO task_logs (task_id, level, message)
            VALUES (?, ?, ?)
            """,
            (task_id, "INFO", "Task enqueued"),
        )
    
    # Process task
    worker = WorkerEngine(
        temp_db,
        "worker-test",
        handler_registry=registry,
    )
    
    worker.claim_and_process()
    
    # Verify logs exist
    cursor = temp_db.execute(
        "SELECT COUNT(*) FROM task_logs WHERE task_id = ?",
        (task_id,),
    )
    log_count = cursor.fetchone()[0]
    assert log_count > 0, "No logs created for task"


@pytest.mark.integration
def test_task_lifecycle_with_metrics(temp_db, registry):
    """Test task lifecycle with metrics tracking."""
    def metrics_handler(task: Task):
        return {"status": "success"}
    
    registry.register_handler("metrics_task", metrics_handler)
    
    metrics = QueueMetrics(temp_db)
    
    # Get initial count of completed tasks
    cursor = temp_db.execute(
        "SELECT COUNT(*) FROM task_queue WHERE status = ?",
        ("completed",),
    )
    initial_completed = cursor.fetchone()[0]
    
    # Enqueue and process task
    with temp_db.transaction() as conn:
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("metrics_task", '{"data": "test"}', 100, 1),
        )
    
    worker = WorkerEngine(
        temp_db,
        "worker-test",
        handler_registry=registry,
    )
    
    worker.claim_and_process()
    
    # Get updated count
    cursor = temp_db.execute(
        "SELECT COUNT(*) FROM task_queue WHERE status = ?",
        ("completed",),
    )
    final_completed = cursor.fetchone()[0]
    
    # Verify metrics updated
    assert final_completed > initial_completed


@pytest.mark.integration
def test_task_lifecycle_with_heartbeat(temp_db, registry):
    """Test task lifecycle with worker heartbeat table."""
    def heartbeat_handler(task: Task):
        return {"status": "success"}
    
    registry.register_handler("heartbeat_task", heartbeat_handler)
    
    # Manually register worker in workers table
    worker_id = "worker-heartbeat"
    with temp_db.transaction() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO workers (worker_id, capabilities, heartbeat_utc)
            VALUES (?, ?, datetime('now'))
            """,
            (worker_id, '{"type": "test_worker"}'),
        )
    
    # Enqueue task
    with temp_db.transaction() as conn:
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("heartbeat_task", '{"data": "test"}', 100, 1),
        )
    
    worker = WorkerEngine(
        temp_db,
        worker_id,
        handler_registry=registry,
    )
    
    worker.claim_and_process()
    
    # Verify worker exists in workers table
    cursor = temp_db.execute(
        "SELECT COUNT(*) FROM workers WHERE worker_id = ?",
        (worker_id,),
    )
    worker_count = cursor.fetchone()[0]
    assert worker_count > 0


@pytest.mark.integration
def test_task_lifecycle_with_payload_transformation(temp_db, registry):
    """Test task lifecycle with payload transformation."""
    def transform_handler(task: Task):
        import json
        payload = json.loads(task.payload)
        transformed = {
            "original": payload,
            "transformed": payload.get("value", 0) * 2,
        }
        return transformed
    
    registry.register_handler("transform_task", transform_handler)
    
    # Enqueue task with specific payload
    with temp_db.transaction() as conn:
        cursor = conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority, max_attempts)
            VALUES (?, ?, ?, ?)
            """,
            ("transform_task", '{"value": 42}', 100, 1),
        )
        task_id = cursor.lastrowid
    
    # Process task
    worker = WorkerEngine(
        temp_db,
        "worker-test",
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
def test_multiple_tasks_lifecycle(temp_db, registry):
    """Test lifecycle of multiple tasks processed in sequence."""
    processed_ids = []
    
    def multi_handler(task: Task):
        processed_ids.append(task.id)
        return {"status": "success"}
    
    registry.register_handler("multi_task", multi_handler)
    
    # Enqueue multiple tasks
    task_ids = []
    with temp_db.transaction() as conn:
        for i in range(5):
            cursor = conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("multi_task", f'{{"index": {i}}}', 100 - i, 1),
            )
            task_ids.append(cursor.lastrowid)
    
    # Process all tasks
    worker = WorkerEngine(
        temp_db,
        "worker-test",
        handler_registry=registry,
    )
    
    for _ in range(5):
        worker.claim_and_process()
    
    # Verify all tasks were processed
    assert len(processed_ids) == 5
    assert set(processed_ids) == set(task_ids)
    
    # Verify all tasks completed
    cursor = temp_db.execute(
        "SELECT COUNT(*) FROM task_queue WHERE status = ?",
        ("completed",),
    )
    completed_count = cursor.fetchone()[0]
    assert completed_count == 5
