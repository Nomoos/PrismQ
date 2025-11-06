"""
Demo script for scheduling strategies (Issue #327).

This script demonstrates all four scheduling strategies:
- FIFO: First-In-First-Out
- LIFO: Last-In-First-Out
- Priority: Priority-based (lower number = higher priority)
- Weighted Random: Probabilistic selection weighted by priority

Usage:
    cd Client/Backend
    python src/queue/demo_scheduling.py
"""

import sys
import tempfile
from pathlib import Path
from collections import Counter

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from queue.database import QueueDatabase
from queue.models import SchedulingStrategy
from queue.scheduling import TaskClaimerFactory


def insert_tasks(db: QueueDatabase, task_configs):
    """Insert multiple tasks into the queue."""
    for task_type, priority in task_configs:
        sql = """
        INSERT INTO task_queue (type, priority, payload, compatibility, status, run_after_utc)
        VALUES (?, ?, '{}', '{}', 'queued', datetime('now'))
        """
        db.execute(sql, (task_type, priority))
        db.get_connection().commit()


def demo_strategy(db: QueueDatabase, strategy: SchedulingStrategy, task_configs):
    """Demonstrate a single scheduling strategy."""
    print(f"\n{'='*70}")
    print(f"Strategy: {strategy.value.upper()}")
    print(f"{'='*70}")
    
    # Clear and insert tasks
    db.execute("DELETE FROM task_queue", ())
    db.get_connection().commit()
    insert_tasks(db, task_configs)
    
    print(f"\nInserted {len(task_configs)} tasks:")
    for i, (task_type, priority) in enumerate(task_configs, 1):
        print(f"  Task {i}: type={task_type}, priority={priority}")
    
    # Create claimer and claim all tasks
    claimer = TaskClaimerFactory.create(strategy, db)
    
    print(f"\nClaiming order with {strategy.value}:")
    claimed_order = []
    for i in range(len(task_configs)):
        task = claimer.claim_task(f"worker-{i}", {}, 60)
        if task:
            claimed_order.append((task.type, task.priority, task.id))
            print(f"  {i+1}. Task ID={task.id}, type={task.type}, priority={task.priority}")
    
    return claimed_order


def demo_weighted_random_distribution(db: QueueDatabase, trials: int = 100):
    """Demonstrate weighted random distribution over multiple trials."""
    print(f"\n{'='*70}")
    print(f"Weighted Random Distribution Test ({trials} trials)")
    print(f"{'='*70}")
    
    priority_counts = Counter()
    
    for trial in range(trials):
        # Clear and insert fresh tasks for each trial
        db.execute("DELETE FROM task_queue", ())
        db.get_connection().commit()
        
        # Insert 5 tasks of each priority
        tasks = [
            ("high", 1),
            ("high", 1),
            ("high", 1),
            ("high", 1),
            ("high", 1),
            ("low", 100),
            ("low", 100),
            ("low", 100),
            ("low", 100),
            ("low", 100),
        ]
        insert_tasks(db, tasks)
        
        # Claim one task per trial
        claimer = TaskClaimerFactory.create(SchedulingStrategy.WEIGHTED_RANDOM, db)
        task = claimer.claim_task(f"worker-{trial}", {}, 60)
        if task:
            priority_counts[task.priority] += 1
    
    print(f"\nResults from {trials} trials (5 high priority, 5 low priority each):")
    print(f"  Priority 1 (high):   {priority_counts[1]:3d} times ({priority_counts[1]/trials*100:.1f}%)")
    print(f"  Priority 100 (low):  {priority_counts[100]:3d} times ({priority_counts[100]/trials*100:.1f}%)")
    print(f"\nExpected: ~98% for priority 1 (50x more weight)")
    print(f"Actual:   {priority_counts[1]/trials*100:.1f}% for priority 1")


def main():
    """Run all scheduling strategy demos."""
    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo_scheduling.db"
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        print("="*70)
        print("Scheduling Strategies Demo - Issue #327")
        print("="*70)
        
        # Define test tasks
        tasks = [
            ("task-1", 100),  # Low priority
            ("task-2", 50),   # Medium priority
            ("task-3", 1),    # High priority
            ("task-4", 100),  # Low priority
            ("task-5", 10),   # Medium-high priority
        ]
        
        # Demo each strategy
        demo_strategy(db, SchedulingStrategy.FIFO, tasks)
        demo_strategy(db, SchedulingStrategy.LIFO, tasks)
        demo_strategy(db, SchedulingStrategy.PRIORITY, tasks)
        demo_strategy(db, SchedulingStrategy.WEIGHTED_RANDOM, tasks)
        
        # Demo weighted random distribution
        demo_weighted_random_distribution(db, trials=100)
        
        print(f"\n{'='*70}")
        print("Demo Complete!")
        print(f"{'='*70}\n")
        
        db.close()


if __name__ == "__main__":
    main()
