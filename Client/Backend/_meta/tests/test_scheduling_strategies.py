"""Unit tests for queue scheduling strategies (Issue #327)."""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

import sys
sys.path.insert(0, '/home/runner/work/PrismQ.IdeaInspiration/PrismQ.IdeaInspiration/Client/Backend/src')

from queue import (
    QueueDatabase,
    Task,
    SchedulingStrategy,
    WorkerConfig,
    TaskClaimerFactory,
    FIFOTaskClaimer,
    LIFOTaskClaimer,
    PriorityTaskClaimer,
    WeightedRandomTaskClaimer,
    QueueDatabaseError,
)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_scheduling.db"


@pytest.fixture
def db(temp_db_path):
    """Create a QueueDatabase instance for testing."""
    database = QueueDatabase(str(temp_db_path))
    database.initialize_schema()
    yield database
    database.close()


def insert_task(db: QueueDatabase, priority: int = 100, task_type: str = "test") -> int:
    """Helper function to insert a task into the queue."""
    sql = """
    INSERT INTO task_queue (type, priority, payload, compatibility, status, run_after_utc)
    VALUES (?, ?, '{}', '{}', 'queued', datetime('now'))
    """
    cursor = db.execute(sql, (task_type, priority))
    db.get_connection().commit()
    return cursor.lastrowid


class TestSchedulingStrategyEnum:
    """Test SchedulingStrategy enum."""
    
    def test_enum_values(self):
        """Test all enum values are defined correctly."""
        assert SchedulingStrategy.FIFO.value == "fifo"
        assert SchedulingStrategy.LIFO.value == "lifo"
        assert SchedulingStrategy.PRIORITY.value == "priority"
        assert SchedulingStrategy.WEIGHTED_RANDOM.value == "weighted_random"
    
    def test_enum_count(self):
        """Test there are exactly 4 strategies."""
        assert len(SchedulingStrategy) == 4


class TestWorkerConfig:
    """Test WorkerConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = WorkerConfig(worker_id="worker-1")
        assert config.worker_id == "worker-1"
        assert config.capabilities == {}
        assert config.scheduling_strategy == SchedulingStrategy.PRIORITY
        assert config.lease_duration_seconds == 60
        assert config.poll_interval_seconds == 1
        assert config.max_retries == 3
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = WorkerConfig(
            worker_id="worker-2",
            capabilities={"region": "us"},
            scheduling_strategy=SchedulingStrategy.FIFO,
            lease_duration_seconds=120,
        )
        assert config.worker_id == "worker-2"
        assert config.capabilities == {"region": "us"}
        assert config.scheduling_strategy == SchedulingStrategy.FIFO
        assert config.lease_duration_seconds == 120


class TestFIFOTaskClaimer:
    """Test FIFO (First-In-First-Out) scheduling strategy."""
    
    def test_claims_oldest_task_first(self, db):
        """Test FIFO claims oldest task first (lowest ID)."""
        # Insert tasks in order: 1, 2, 3
        id1 = insert_task(db, priority=100)
        id2 = insert_task(db, priority=100)
        id3 = insert_task(db, priority=100)
        
        claimer = FIFOTaskClaimer(db)
        
        # Claim should get task 1, then 2, then 3
        task1 = claimer.claim_task("worker-1", {}, 60)
        assert task1 is not None
        assert task1.id == id1
        
        task2 = claimer.claim_task("worker-1", {}, 60)
        assert task2 is not None
        assert task2.id == id2
        
        task3 = claimer.claim_task("worker-1", {}, 60)
        assert task3 is not None
        assert task3.id == id3
    
    def test_returns_none_when_no_tasks(self, db):
        """Test FIFO returns None when no tasks available."""
        claimer = FIFOTaskClaimer(db)
        task = claimer.claim_task("worker-1", {}, 60)
        assert task is None
    
    def test_task_status_updated(self, db):
        """Test claimed task status is updated correctly."""
        insert_task(db, priority=100)
        claimer = FIFOTaskClaimer(db)
        
        task = claimer.claim_task("worker-1", {}, 60)
        assert task is not None
        assert task.status == "leased"
        assert task.locked_by == "worker-1"
        assert task.reserved_at_utc is not None
        assert task.lease_until_utc is not None
    
    def test_no_duplicate_claims(self, db):
        """Test multiple workers don't claim the same task."""
        insert_task(db, priority=100)
        insert_task(db, priority=100)
        
        claimer = FIFOTaskClaimer(db)
        
        task1 = claimer.claim_task("worker-1", {}, 60)
        task2 = claimer.claim_task("worker-2", {}, 60)
        
        assert task1 is not None
        assert task2 is not None
        assert task1.id != task2.id


class TestLIFOTaskClaimer:
    """Test LIFO (Last-In-First-Out) scheduling strategy."""
    
    def test_claims_newest_task_first(self, db):
        """Test LIFO claims newest task first (highest ID)."""
        # Insert tasks in order: 1, 2, 3
        id1 = insert_task(db, priority=100)
        id2 = insert_task(db, priority=100)
        id3 = insert_task(db, priority=100)
        
        claimer = LIFOTaskClaimer(db)
        
        # Claim should get task 3, then 2, then 1 (reverse order)
        task1 = claimer.claim_task("worker-1", {}, 60)
        assert task1 is not None
        assert task1.id == id3
        
        task2 = claimer.claim_task("worker-1", {}, 60)
        assert task2 is not None
        assert task2.id == id2
        
        task3 = claimer.claim_task("worker-1", {}, 60)
        assert task3 is not None
        assert task3.id == id1
    
    def test_returns_none_when_no_tasks(self, db):
        """Test LIFO returns None when no tasks available."""
        claimer = LIFOTaskClaimer(db)
        task = claimer.claim_task("worker-1", {}, 60)
        assert task is None


class TestPriorityTaskClaimer:
    """Test Priority-based scheduling strategy."""
    
    def test_claims_high_priority_first(self, db):
        """Test priority claims high priority (lower number) first."""
        # Insert tasks with different priorities
        id_low = insert_task(db, priority=100)   # Low priority
        id_med = insert_task(db, priority=50)    # Medium priority
        id_high = insert_task(db, priority=1)    # High priority
        
        claimer = PriorityTaskClaimer(db)
        
        # Should claim high priority first
        task1 = claimer.claim_task("worker-1", {}, 60)
        assert task1 is not None
        assert task1.id == id_high
        assert task1.priority == 1
        
        # Then medium priority
        task2 = claimer.claim_task("worker-1", {}, 60)
        assert task2 is not None
        assert task2.id == id_med
        assert task2.priority == 50
        
        # Then low priority
        task3 = claimer.claim_task("worker-1", {}, 60)
        assert task3 is not None
        assert task3.id == id_low
        assert task3.priority == 100
    
    def test_fifo_within_same_priority(self, db):
        """Test FIFO ordering within same priority level."""
        # Insert multiple tasks with same priority
        id1 = insert_task(db, priority=50)
        id2 = insert_task(db, priority=50)
        id3 = insert_task(db, priority=50)
        
        claimer = PriorityTaskClaimer(db)
        
        # Should use FIFO within same priority
        task1 = claimer.claim_task("worker-1", {}, 60)
        assert task1.id == id1
        
        task2 = claimer.claim_task("worker-1", {}, 60)
        assert task2.id == id2
        
        task3 = claimer.claim_task("worker-1", {}, 60)
        assert task3.id == id3


class TestWeightedRandomTaskClaimer:
    """Test Weighted Random scheduling strategy."""
    
    def test_claims_task_successfully(self, db):
        """Test weighted random can claim tasks."""
        insert_task(db, priority=50)
        
        claimer = WeightedRandomTaskClaimer(db)
        task = claimer.claim_task("worker-1", {}, 60)
        
        assert task is not None
        assert task.status == "leased"
    
    def test_high_priority_more_likely(self, db):
        """
        Test high priority tasks are claimed more frequently.
        
        Statistical test: Run multiple trials where we insert tasks,
        claim one, and record which priority was claimed. This avoids
        the depletion effect where removing tasks changes the distribution.
        """
        trials = 100
        priority_counts = Counter()
        
        for trial in range(trials):
            # For each trial, insert fresh tasks
            # Use a separate connection to avoid transaction conflicts
            conn = db.get_connection()
            
            # Clear any existing tasks
            conn.execute("DELETE FROM task_queue")
            conn.commit()
            
            # Insert 5 high priority and 5 low priority tasks
            for _ in range(5):
                insert_task(db, priority=1)
            for _ in range(5):
                insert_task(db, priority=100)
            
            claimer = WeightedRandomTaskClaimer(db)
            
            # Claim one task and record its priority
            task = claimer.claim_task(f"worker-{trial}", {}, 60)
            if task:
                priority_counts[task.priority] += 1
        
        # With weighting formula: weight = 1.0 / (priority + 1)
        # - p=1:   weight = 0.500
        # - p=100: weight = 0.0099
        # Expected probability for p=1: ~98% (50x more likely)
        # We'll conservatively check for >80%
        assert priority_counts[1] > 80, (
            f"High priority claimed {priority_counts[1]}/{trials} times, "
            f"expected >80 (weighted random should heavily favor high priority)"
        )
    
    def test_low_priority_not_starved(self, db):
        """
        Test low priority tasks still get claimed (no complete starvation).
        
        Even with many high priority tasks, low priority should eventually claim.
        """
        # Insert mix: 10 high priority, 90 low priority
        for _ in range(10):
            insert_task(db, priority=1)
        for _ in range(90):
            insert_task(db, priority=100)
        
        claimer = WeightedRandomTaskClaimer(db)
        
        # Claim all tasks
        priority_counts = Counter()
        for _ in range(100):
            task = claimer.claim_task("worker-1", {}, 60)
            if task:
                priority_counts[task.priority] += 1
        
        # Low priority should still be claimed at least once
        # (probability is very high with 90 tasks)
        assert priority_counts[100] > 0, (
            f"Low priority never claimed - complete starvation detected"
        )


class TestTaskClaimerFactory:
    """Test TaskClaimerFactory."""
    
    def test_create_fifo_claimer(self, db):
        """Test factory creates FIFO claimer."""
        claimer = TaskClaimerFactory.create(SchedulingStrategy.FIFO, db)
        assert isinstance(claimer, FIFOTaskClaimer)
    
    def test_create_lifo_claimer(self, db):
        """Test factory creates LIFO claimer."""
        claimer = TaskClaimerFactory.create(SchedulingStrategy.LIFO, db)
        assert isinstance(claimer, LIFOTaskClaimer)
    
    def test_create_priority_claimer(self, db):
        """Test factory creates Priority claimer."""
        claimer = TaskClaimerFactory.create(SchedulingStrategy.PRIORITY, db)
        assert isinstance(claimer, PriorityTaskClaimer)
    
    def test_create_weighted_random_claimer(self, db):
        """Test factory creates Weighted Random claimer."""
        claimer = TaskClaimerFactory.create(SchedulingStrategy.WEIGHTED_RANDOM, db)
        assert isinstance(claimer, WeightedRandomTaskClaimer)
    
    def test_invalid_strategy_raises_error(self, db):
        """Test factory raises error for invalid strategy."""
        with pytest.raises(ValueError, match="Unknown scheduling strategy"):
            TaskClaimerFactory.create("invalid", db)


class TestStrategySwitching:
    """Test switching between strategies."""
    
    def test_can_switch_strategies(self, db):
        """Test worker can switch strategies dynamically."""
        # Insert tasks
        insert_task(db, priority=1)
        insert_task(db, priority=50)
        insert_task(db, priority=100)
        
        # Use FIFO first
        fifo_claimer = TaskClaimerFactory.create(SchedulingStrategy.FIFO, db)
        task1 = fifo_claimer.claim_task("worker-1", {}, 60)
        
        # Switch to Priority
        priority_claimer = TaskClaimerFactory.create(SchedulingStrategy.PRIORITY, db)
        task2 = priority_claimer.claim_task("worker-1", {}, 60)
        
        # Task 2 should be highest priority (not next in FIFO)
        assert task2.priority == 50  # Next highest after priority=1
    
    def test_concurrent_strategies(self, db):
        """Test multiple workers with different strategies don't conflict."""
        # Insert tasks
        id1 = insert_task(db, priority=100)
        id2 = insert_task(db, priority=50)
        id3 = insert_task(db, priority=1)
        
        # Worker 1 uses FIFO
        fifo_claimer = TaskClaimerFactory.create(SchedulingStrategy.FIFO, db)
        task_fifo = fifo_claimer.claim_task("worker-1", {}, 60)
        
        # Worker 2 uses Priority
        priority_claimer = TaskClaimerFactory.create(SchedulingStrategy.PRIORITY, db)
        task_priority = priority_claimer.claim_task("worker-2", {}, 60)
        
        # Should claim different tasks
        assert task_fifo.id != task_priority.id
        
        # FIFO gets oldest (id1), Priority gets highest priority (id3)
        assert task_fifo.id == id1
        assert task_priority.id == id3


class TestAtomicClaiming:
    """Test atomic claiming across all strategies."""
    
    @pytest.mark.parametrize("strategy", [
        SchedulingStrategy.FIFO,
        SchedulingStrategy.LIFO,
        SchedulingStrategy.PRIORITY,
        SchedulingStrategy.WEIGHTED_RANDOM,
    ])
    def test_no_duplicate_claims(self, db, strategy):
        """Test atomic claiming prevents duplicate claims for all strategies."""
        # Insert multiple tasks
        for i in range(10):
            insert_task(db, priority=50)
        
        claimer = TaskClaimerFactory.create(strategy, db)
        
        # Claim all tasks
        claimed_ids = set()
        for _ in range(10):
            task = claimer.claim_task("worker-1", {}, 60)
            if task:
                assert task.id not in claimed_ids, f"Duplicate claim: {task.id}"
                claimed_ids.add(task.id)
        
        # Should have claimed all 10 tasks with no duplicates
        assert len(claimed_ids) == 10


class TestPerformance:
    """Test performance characteristics of scheduling strategies."""
    
    @pytest.mark.parametrize("strategy", [
        SchedulingStrategy.FIFO,
        SchedulingStrategy.LIFO,
        SchedulingStrategy.PRIORITY,
        SchedulingStrategy.WEIGHTED_RANDOM,
    ])
    def test_claim_latency(self, db, strategy):
        """Test claim latency is under 10ms for all strategies."""
        # Insert tasks
        for i in range(100):
            insert_task(db, priority=i)
        
        claimer = TaskClaimerFactory.create(strategy, db)
        
        # Measure claim latency
        latencies = []
        for _ in range(10):  # Test 10 claims
            start = time.perf_counter()
            task = claimer.claim_task("worker-1", {}, 60)
            end = time.perf_counter()
            
            if task:
                latencies.append((end - start) * 1000)  # Convert to ms
        
        # Average latency should be under 10ms
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 10, (
            f"{strategy.value} average latency {avg_latency:.2f}ms exceeds 10ms"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
