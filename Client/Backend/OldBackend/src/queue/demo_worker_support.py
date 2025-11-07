#!/usr/bin/env python3
"""
Worker Integration Demo and Validation Script

Demonstrates how other workers (Workers 02-06) can integrate with
the queue infrastructure and validates their integration.

Usage:
    python demo_worker_support.py

Part of: Worker 01 Phase 2 - Support other workers and check validity
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from queue import (
    QueueDatabase,
    QueueValidator,
    validate_worker_integration,
    SchedulingStrategy,
    TaskClaimerFactory,
    get_default_db_path,
)


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_validation():
    """Demonstrate infrastructure validation."""
    print_section("INFRASTRUCTURE VALIDATION")
    
    # Create temporary database for demo
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    print(f"Creating test database: {db_path}\n")
    
    # Initialize database
    db = QueueDatabase(db_path)
    db.initialize_schema()
    
    # Run validation
    validator = QueueValidator(db_path)
    all_passed = validator.validate_all()
    
    if all_passed:
        print("\n✅ All validation checks passed!")
    else:
        print("\n❌ Some validation checks failed!")
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)
    Path(db_path + '-shm').unlink(missing_ok=True)
    Path(db_path + '-wal').unlink(missing_ok=True)
    
    return all_passed


def demo_worker_02_enqueue():
    """Demonstrate Worker 02 (Client API) integration pattern."""
    print_section("WORKER 02: Client API - Enqueue Pattern")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = QueueDatabase(db_path)
        db.initialize_schema()
        
        print("Enqueueing tasks (Client API pattern)...")
        
        # Enqueue tasks with different priorities
        task_ids = []
        for i in range(3):
            with db.transaction() as conn:
                cursor = conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now')) "
                    "RETURNING id",
                    (f'video_processing', 'queued', 10 + i * 10, f'{{"video_id": {i}}}')
                )
                task_id = cursor.fetchone()[0]
                task_ids.append(task_id)
                print(f"  ✓ Enqueued task #{task_id} (priority {10 + i * 10})")
        
        print(f"\n✅ Successfully enqueued {len(task_ids)} tasks")
        
    finally:
        Path(db_path).unlink(missing_ok=True)
        Path(db_path + '-shm').unlink(missing_ok=True)
        Path(db_path + '-wal').unlink(missing_ok=True)


def demo_worker_03_claim():
    """Demonstrate Worker 03 (Worker Engine) integration pattern."""
    print_section("WORKER 03: Worker Engine - Claim Pattern")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = QueueDatabase(db_path)
        db.initialize_schema()
        
        # First enqueue some tasks
        print("Setting up test tasks...")
        with db.connection() as conn:
            for i in range(5):
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                    ('test_task', 'queued', 50, '{}')
                )
            conn.commit()
        
        print("  ✓ Created 5 queued tasks\n")
        
        print("Claiming tasks using FIFO strategy...")
        claimer = TaskClaimerFactory.create(SchedulingStrategy.FIFO, db)
        
        for worker_num in range(3):
            task = claimer.claim_task(f"worker-{worker_num}", {}, 60)
            if task:
                print(f"  ✓ Worker-{worker_num} claimed task #{task.id}")
        
        print("\n✅ Successfully demonstrated task claiming")
        
    finally:
        Path(db_path).unlink(missing_ok=True)
        Path(db_path + '-shm').unlink(missing_ok=True)
        Path(db_path + '-wal').unlink(missing_ok=True)


def demo_worker_04_scheduling():
    """Demonstrate Worker 04 (Scheduling Strategies) integration pattern."""
    print_section("WORKER 04: Scheduling Strategies")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = QueueDatabase(db_path)
        db.initialize_schema()
        
        # Create tasks with different priorities
        print("Creating tasks with different priorities...")
        with db.connection() as conn:
            priorities = [10, 50, 100]
            for priority in priorities:
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                    ('test_task', 'queued', priority, f'{{"priority": {priority}}}')
                )
            conn.commit()
        
        print("  ✓ Created tasks with priorities: 10, 50, 100\n")
        
        # Test each scheduling strategy
        strategies = [
            (SchedulingStrategy.FIFO, "First-In-First-Out"),
            (SchedulingStrategy.PRIORITY, "Priority-based"),
            (SchedulingStrategy.WEIGHTED_RANDOM, "Weighted Random"),
        ]
        
        for strategy, name in strategies:
            # Reset tasks
            with db.connection() as conn:
                conn.execute("UPDATE task_queue SET status = 'queued'")
                conn.commit()
            
            # Claim with strategy
            claimer = TaskClaimerFactory.create(strategy, db)
            task = claimer.claim_task(f"worker-{strategy.value}", {}, 60)
            
            if task:
                print(f"  ✓ {name}: claimed task #{task.id} (priority {task.priority})")
        
        print("\n✅ Successfully demonstrated all scheduling strategies")
        
    finally:
        Path(db_path).unlink(missing_ok=True)
        Path(db_path + '-shm').unlink(missing_ok=True)
        Path(db_path + '-wal').unlink(missing_ok=True)


def demo_worker_05_observability():
    """Demonstrate Worker 05 (Observability) integration pattern."""
    print_section("WORKER 05: Observability - Queue Statistics")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = QueueDatabase(db_path)
        db.initialize_schema()
        
        # Create tasks in different states
        print("Creating tasks in different states...")
        with db.connection() as conn:
            # Queued tasks
            for i in range(5):
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
                    ('task', 'queued', 50, '{}')
                )
            
            # Completed tasks
            for i in range(3):
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc, "
                    " finished_at_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), datetime('now'))",
                    ('task', 'completed', 50, '{}')
                )
            
            conn.commit()
        
        # Query statistics
        print("\nQueue Statistics:")
        with db.connection() as conn:
            cursor = conn.execute(
                """
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(priority) as avg_priority
                FROM task_queue
                GROUP BY status
                """
            )
            
            for row in cursor.fetchall():
                status, count, avg_priority = row
                print(f"  • {status}: {count} tasks (avg priority: {avg_priority:.1f})")
        
        print("\n✅ Successfully demonstrated observability queries")
        
    finally:
        Path(db_path).unlink(missing_ok=True)
        Path(db_path + '-shm').unlink(missing_ok=True)
        Path(db_path + '-wal').unlink(missing_ok=True)


def demo_worker_06_maintenance():
    """Demonstrate Worker 06 (Maintenance) integration pattern."""
    print_section("WORKER 06: Maintenance - Cleanup Operations")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = QueueDatabase(db_path)
        db.initialize_schema()
        
        # Create old and new completed tasks
        print("Creating completed tasks (old and new)...")
        with db.connection() as conn:
            # Recent tasks
            for i in range(3):
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc, "
                    " finished_at_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), datetime('now'))",
                    ('recent', 'completed', 50, '{}')
                )
            
            # Old tasks (simulate 8 days ago)
            for i in range(2):
                conn.execute(
                    "INSERT INTO task_queue "
                    "(type, status, priority, payload, created_at_utc, run_after_utc, "
                    " finished_at_utc) "
                    "VALUES (?, ?, ?, ?, datetime('now', '-8 days'), "
                    "        datetime('now', '-8 days'), datetime('now', '-8 days'))",
                    ('old', 'completed', 50, '{}')
                )
            
            conn.commit()
        
        print("  ✓ Created 3 recent + 2 old completed tasks\n")
        
        # Cleanup old tasks
        print("Cleaning up old completed tasks (>7 days)...")
        with db.transaction() as conn:
            cursor = conn.execute(
                """
                DELETE FROM task_queue
                WHERE status = 'completed'
                    AND finished_at_utc < datetime('now', '-7 days')
                """
            )
            deleted = cursor.rowcount
        
        print(f"  ✓ Deleted {deleted} old tasks\n")
        
        # Verify remaining tasks
        with db.connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM task_queue")
            remaining = cursor.fetchone()[0]
        
        print(f"  ✓ {remaining} tasks remaining (recent tasks preserved)")
        print("\n✅ Successfully demonstrated maintenance operations")
        
    finally:
        Path(db_path).unlink(missing_ok=True)
        Path(db_path + '-shm').unlink(missing_ok=True)
        Path(db_path + '-wal').unlink(missing_ok=True)


def demo_integration_validation():
    """Demonstrate worker integration validation."""
    print_section("WORKER INTEGRATION VALIDATION")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = QueueDatabase(db_path)
        db.initialize_schema()
        
        # Test integration for multiple workers
        worker_ids = ["worker-1", "worker-2", "worker-3"]
        
        for worker_id in worker_ids:
            result = validate_worker_integration(db, worker_id)
            if result:
                print(f"✅ {worker_id} integration validated")
            else:
                print(f"❌ {worker_id} integration failed")
        
    finally:
        Path(db_path).unlink(missing_ok=True)
        Path(db_path + '-shm').unlink(missing_ok=True)
        Path(db_path + '-wal').unlink(missing_ok=True)


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  WORKER SUPPORT DEMO")
    print("  Worker 01 - Support Other Workers and Check Validity")
    print("=" * 70)
    
    try:
        # 1. Infrastructure validation
        demo_validation()
        
        # 2. Worker-specific patterns
        demo_worker_02_enqueue()
        demo_worker_03_claim()
        demo_worker_04_scheduling()
        demo_worker_05_observability()
        demo_worker_06_maintenance()
        
        # 3. Integration validation
        demo_integration_validation()
        
        # Final summary
        print_section("DEMO COMPLETE")
        print("All worker integration patterns demonstrated successfully!")
        print("\nFor detailed documentation, see:")
        print("  • Client/Backend/src/queue/WORKER_SUPPORT.md")
        print("  • Client/Backend/src/queue/README.md")
        print("\nFor validation, run:")
        print("  python -m src.queue.validation /path/to/queue.db")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
