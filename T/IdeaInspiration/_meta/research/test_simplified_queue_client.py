"""
Unit tests for SimplifiedQueueClient.

Tests core functionality:
- Task enqueueing with priority
- Task retrieval ordered by priority
- Atomic task claiming
- Task completion
- Idempotency handling
"""

import pytest
import asyncio
import sqlite3
from pathlib import Path
from simplified_queue_client import SimplifiedQueueClient


@pytest.fixture
def queue(tmp_path):
    """Create a temporary queue for testing."""
    db_path = tmp_path / "test_queue.db"
    return SimplifiedQueueClient(str(db_path))


@pytest.mark.asyncio
async def test_enqueue_task(queue):
    """Test basic task enqueueing."""
    task_id = await queue.enqueue_task(
        task_type="test_task",
        parameters={"key": "value"},
        priority=10
    )
    
    assert task_id is not None
    
    # Verify task exists in database
    status = await queue.get_task_status(task_id)
    assert status is not None
    assert status["task_type"] == "test_task"
    assert status["parameters"] == {"key": "value"}
    assert status["priority"] == 10
    assert status["status"] == "queued"


@pytest.mark.asyncio
async def test_priority_ordering(queue):
    """Test that tasks are retrieved in priority order (highest first)."""
    # Enqueue tasks with different priorities
    low = await queue.enqueue_task("task", {"name": "low"}, priority=0)
    high = await queue.enqueue_task("task", {"name": "high"}, priority=100)
    medium = await queue.enqueue_task("task", {"name": "medium"}, priority=50)
    
    # Retrieve tasks - should be in priority order
    task1 = await queue.get_next_task()
    assert task1["task_id"] == high
    assert task1["priority"] == 100
    
    # Claim and complete to move on
    await queue.claim_task(high)
    await queue.complete_task(high, "completed")
    
    task2 = await queue.get_next_task()
    assert task2["task_id"] == medium
    assert task2["priority"] == 50
    
    await queue.claim_task(medium)
    await queue.complete_task(medium, "completed")
    
    task3 = await queue.get_next_task()
    assert task3["task_id"] == low
    assert task3["priority"] == 0


@pytest.mark.asyncio
async def test_fifo_within_same_priority(queue):
    """Test FIFO ordering within same priority level."""
    # Enqueue multiple tasks with same priority
    task1 = await queue.enqueue_task("task", {"order": 1}, priority=50)
    await asyncio.sleep(0.01)  # Ensure different timestamps
    task2 = await queue.enqueue_task("task", {"order": 2}, priority=50)
    await asyncio.sleep(0.01)
    task3 = await queue.enqueue_task("task", {"order": 3}, priority=50)
    
    # Should retrieve in FIFO order (oldest first)
    next_task = await queue.get_next_task()
    assert next_task["task_id"] == task1
    assert next_task["parameters"]["order"] == 1


@pytest.mark.asyncio
async def test_atomic_task_claiming(queue):
    """Test that task claiming is atomic (only one worker can claim)."""
    task_id = await queue.enqueue_task("task", {}, priority=10)
    
    # First claim should succeed
    success1 = await queue.claim_task(task_id)
    assert success1 is True
    
    # Second claim should fail (already running)
    success2 = await queue.claim_task(task_id)
    assert success2 is False
    
    # Verify task status is running
    status = await queue.get_task_status(task_id)
    assert status["status"] == "running"
    assert status["started_at"] is not None


@pytest.mark.asyncio
async def test_complete_task_success(queue):
    """Test completing a task successfully."""
    task_id = await queue.enqueue_task("task", {}, priority=10)
    await queue.claim_task(task_id)
    
    await queue.complete_task(task_id, "completed")
    
    status = await queue.get_task_status(task_id)
    assert status["status"] == "completed"
    assert status["completed_at"] is not None
    assert status["error_message"] is None


@pytest.mark.asyncio
async def test_complete_task_failure(queue):
    """Test completing a task with failure."""
    task_id = await queue.enqueue_task("task", {}, priority=10)
    await queue.claim_task(task_id)
    
    error_msg = "Task failed due to error"
    await queue.complete_task(task_id, "failed", error_msg)
    
    status = await queue.get_task_status(task_id)
    assert status["status"] == "failed"
    assert status["completed_at"] is not None
    assert status["error_message"] == error_msg


@pytest.mark.asyncio
async def test_idempotency_key(queue):
    """Test idempotency key prevents duplicate tasks."""
    idem_key = "unique-operation-123"
    
    # First enqueue with idempotency key
    task1 = await queue.enqueue_task(
        "task", {"data": "first"}, priority=10, idempotency_key=idem_key
    )
    
    # Second enqueue with same key should return same task_id
    task2 = await queue.enqueue_task(
        "task", {"data": "second"}, priority=20, idempotency_key=idem_key
    )
    
    assert task1 == task2
    
    # Verify only one task exists
    stats = await queue.get_queue_stats()
    assert stats["queued"] == 1


@pytest.mark.asyncio
async def test_task_type_filtering(queue):
    """Test filtering tasks by type."""
    # Enqueue tasks of different types
    await queue.enqueue_task("type_a", {}, priority=50)
    await queue.enqueue_task("type_b", {}, priority=100)
    await queue.enqueue_task("type_a", {}, priority=75)
    
    # Get next task filtered by type_a
    task = await queue.get_next_task(task_types=["type_a"])
    assert task is not None
    assert task["task_type"] == "type_a"
    assert task["priority"] == 75  # Highest priority type_a task


@pytest.mark.asyncio
async def test_get_queue_stats(queue):
    """Test queue statistics."""
    # Enqueue and process various tasks
    task1 = await queue.enqueue_task("task", {}, priority=10)
    task2 = await queue.enqueue_task("task", {}, priority=20)
    task3 = await queue.enqueue_task("task", {}, priority=30)
    
    # Check initial stats
    stats = await queue.get_queue_stats()
    assert stats["queued"] == 3
    assert stats["running"] == 0
    assert stats["completed"] == 0
    
    # Claim one task
    await queue.claim_task(task1)
    stats = await queue.get_queue_stats()
    assert stats["queued"] == 2
    assert stats["running"] == 1
    
    # Complete one task
    await queue.complete_task(task1, "completed")
    stats = await queue.get_queue_stats()
    assert stats["queued"] == 2
    assert stats["running"] == 0
    assert stats["completed"] == 1
    
    # Fail one task
    await queue.claim_task(task2)
    await queue.complete_task(task2, "failed", "error")
    stats = await queue.get_queue_stats()
    assert stats["failed"] == 1


@pytest.mark.asyncio
async def test_no_tasks_available(queue):
    """Test behavior when no tasks are available."""
    task = await queue.get_next_task()
    assert task is None


@pytest.mark.asyncio
async def test_invalid_complete_status(queue):
    """Test that invalid completion status raises error."""
    task_id = await queue.enqueue_task("task", {}, priority=10)
    
    with pytest.raises(ValueError, match="Invalid status"):
        await queue.complete_task(task_id, "invalid_status")


@pytest.mark.asyncio
async def test_wal_mode_enabled(queue):
    """Test that WAL mode is enabled for better concurrency."""
    conn = sqlite3.connect(queue.db_path)
    cursor = conn.execute("PRAGMA journal_mode")
    mode = cursor.fetchone()[0]
    conn.close()
    
    assert mode.lower() == "wal"


@pytest.mark.asyncio
async def test_concurrent_claiming(queue):
    """Test that concurrent workers cannot claim the same task."""
    task_id = await queue.enqueue_task("task", {}, priority=10)
    
    # Simulate two workers trying to claim simultaneously
    results = await asyncio.gather(
        queue.claim_task(task_id),
        queue.claim_task(task_id),
        return_exceptions=True
    )
    
    # Only one should succeed
    successes = sum(1 for r in results if r is True)
    assert successes == 1


@pytest.mark.asyncio
async def test_max_increasing_priority_example(queue):
    """
    Test the 'max increasing priority' behavior described in requirements.
    
    This demonstrates:
    1. Tasks are retrieved in max priority order (highest first)
    2. Higher priority values are processed before lower values
    """
    # Create tasks with increasing priorities
    tasks = []
    for i in range(5):
        task_id = await queue.enqueue_task(
            f"task_{i}",
            {"index": i},
            priority=i * 10  # 0, 10, 20, 30, 40
        )
        tasks.append((task_id, i * 10))
    
    # Retrieve tasks - should be in max priority order
    retrieved_priorities = []
    for _ in range(5):
        task = await queue.get_next_task()
        assert task is not None
        retrieved_priorities.append(task["priority"])
        await queue.claim_task(task["task_id"])
        await queue.complete_task(task["task_id"], "completed")
    
    # Verify priorities are in descending order (max first)
    assert retrieved_priorities == [40, 30, 20, 10, 0]


@pytest.mark.asyncio
async def test_database_persistence(tmp_path):
    """Test that tasks persist across client instances."""
    db_path = tmp_path / "persist_test.db"
    
    # Create first client and enqueue task
    queue1 = SimplifiedQueueClient(str(db_path))
    task_id = await queue1.enqueue_task("task", {"data": "test"}, priority=50)
    
    # Create second client with same database
    queue2 = SimplifiedQueueClient(str(db_path))
    
    # Should be able to retrieve task from second client
    task = await queue2.get_next_task()
    assert task is not None
    assert task["task_id"] == task_id
    assert task["parameters"]["data"] == "test"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
