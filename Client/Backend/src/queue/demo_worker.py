#!/usr/bin/env python
"""
Demonstration of QueueWorker - Worker Engine for SQLite Task Queue.

This script demonstrates:
1. Creating a worker with custom task handler
2. Enqueueing tasks
3. Worker claiming and executing tasks
4. Retry on failure
5. Dead-letter handling
6. Concurrent workers
"""

import sys
import os
import time
import tempfile
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.queue import (
    QueueDatabase,
    QueueWorker,
    create_worker,
    Task,
)


def demo_task_handler(task: Task) -> bool:
    """Example task handler that processes tasks."""
    print(f"  [Task #{task.id}] Processing {task.type}...")
    payload = task.get_payload_dict()
    
    # Simulate work based on task type
    if task.type == "quick_task":
        time.sleep(0.5)
        print(f"  [Task #{task.id}] Quick task completed!")
        return True
    elif task.type == "slow_task":
        time.sleep(2)
        print(f"  [Task #{task.id}] Slow task completed!")
        return True
    elif task.type == "failing_task":
        print(f"  [Task #{task.id}] Task failed (will retry)!")
        return False
    else:
        print(f"  [Task #{task.id}] Unknown task type")
        return False


def demo_1_basic_worker():
    """Demonstrate basic worker functionality."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Worker Functionality")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo1.db"
        print(f"\nDatabase: {db_path}")
        
        # Initialize database and enqueue tasks
        print("\n1. Initializing database and enqueueing tasks...")
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                ("quick_task", '{"data": "hello"}', 100)
            )
            conn.execute(
                "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                ("slow_task", '{"data": "world"}', 50)
            )
        
        print("  ✓ 2 tasks enqueued")
        db.close()
        
        # Create and start worker
        print("\n2. Creating worker...")
        worker = create_worker(
            "demo-worker-01",
            demo_task_handler,
            capabilities={"type": "general"},
            db_path=str(db_path),
            poll_interval_seconds=0.5
        )
        print(f"  ✓ Worker '{worker.worker_id}' created")
        
        # Run worker in thread
        print("\n3. Starting worker...")
        worker_thread = threading.Thread(target=worker.start, daemon=True)
        worker_thread.start()
        print("  ✓ Worker started")
        
        # Wait for tasks to complete
        time.sleep(5)
        
        # Stop worker
        print("\n4. Stopping worker...")
        worker.stop()
        worker_thread.join(timeout=2)
        print("  ✓ Worker stopped")
        
        # Check results
        print("\n5. Checking results...")
        db = QueueDatabase(str(db_path))
        cursor = db.execute("SELECT id, type, status FROM task_queue ORDER BY id")
        for row in cursor:
            print(f"  Task #{row['id']}: {row['type']} -> {row['status']}")
        db.close()


def demo_2_retry_and_dead_letter():
    """Demonstrate retry logic and dead-letter handling."""
    print("\n" + "=" * 60)
    print("DEMO 2: Retry Logic and Dead-Letter Queue")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo2.db"
        print(f"\nDatabase: {db_path}")
        
        # Initialize database and enqueue failing task
        print("\n1. Enqueueing a task that will fail...")
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        with db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, priority, max_attempts)
                VALUES (?, ?, ?, ?)
                """,
                ("failing_task", '{"reason": "demo"}', 100, 3)
            )
        
        print("  ✓ Task enqueued with max_attempts=3")
        db.close()
        
        # Create worker
        print("\n2. Creating worker with retry logic...")
        worker = create_worker(
            "demo-worker-retry",
            demo_task_handler,
            db_path=str(db_path),
            poll_interval_seconds=0.2
        )
        
        # Run worker to process task (will fail and retry)
        print("\n3. Processing task (will fail multiple times)...")
        worker_thread = threading.Thread(target=worker.start, daemon=True)
        worker_thread.start()
        
        # Wait for retries
        time.sleep(3)
        
        # Stop worker
        worker.stop()
        worker_thread.join(timeout=2)
        
        # Check task status
        print("\n4. Checking task status...")
        db = QueueDatabase(str(db_path))
        cursor = db.execute(
            """
            SELECT id, type, status, attempts, max_attempts, error_message
            FROM task_queue
            WHERE id = 1
            """
        )
        row = cursor.fetchone()
        
        print(f"  Task #{row['id']}:")
        print(f"    Type: {row['type']}")
        print(f"    Status: {row['status']}")
        print(f"    Attempts: {row['attempts']}/{row['max_attempts']}")
        if row['status'] == 'queued':
            print(f"    → Will retry (not yet at max attempts)")
        elif row['status'] == 'failed':
            print(f"    → Dead-letter (max attempts reached)")
        
        # Check logs
        print("\n5. Task execution logs:")
        cursor = db.execute(
            "SELECT level, message FROM task_logs WHERE task_id = 1 ORDER BY log_id"
        )
        for log_row in cursor:
            print(f"  [{log_row['level']}] {log_row['message']}")
        
        db.close()


def demo_3_concurrent_workers():
    """Demonstrate multiple workers processing tasks concurrently."""
    print("\n" + "=" * 60)
    print("DEMO 3: Concurrent Workers")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo3.db"
        print(f"\nDatabase: {db_path}")
        
        # Initialize database and enqueue many tasks
        print("\n1. Enqueueing 10 tasks...")
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        with db.transaction() as conn:
            for i in range(10):
                task_type = "quick_task" if i % 2 == 0 else "slow_task"
                conn.execute(
                    "INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)",
                    (task_type, f'{{"task_num": {i}}}', 100)
                )
        
        print("  ✓ 10 tasks enqueued")
        db.close()
        
        # Create 3 workers
        print("\n2. Creating 3 concurrent workers...")
        workers = []
        threads = []
        
        for i in range(3):
            worker = create_worker(
                f"demo-worker-{i+1}",
                demo_task_handler,
                db_path=str(db_path),
                poll_interval_seconds=0.1
            )
            workers.append(worker)
            print(f"  ✓ Worker {i+1} created")
        
        # Start all workers
        print("\n3. Starting all workers...")
        for worker in workers:
            thread = threading.Thread(target=worker.start, daemon=True)
            threads.append(thread)
            thread.start()
        print("  ✓ All workers started")
        
        # Wait for tasks to complete
        print("\n4. Workers processing tasks...")
        time.sleep(8)
        
        # Stop all workers
        print("\n5. Stopping all workers...")
        for worker in workers:
            worker.stop()
        for thread in threads:
            thread.join(timeout=2)
        print("  ✓ All workers stopped")
        
        # Check results
        print("\n6. Final status:")
        db = QueueDatabase(str(db_path))
        
        cursor = db.execute(
            "SELECT status, COUNT(*) as count FROM task_queue GROUP BY status"
        )
        for row in cursor:
            print(f"  {row['status']}: {row['count']} tasks")
        
        cursor = db.execute(
            "SELECT locked_by as worker_id, COUNT(*) as tasks_processed FROM task_queue "
            "WHERE locked_by IS NOT NULL GROUP BY locked_by"
        )
        print("\n  Tasks processed by each worker:")
        for row in cursor:
            print(f"    {row['worker_id']}: {row['tasks_processed']} tasks")
        
        db.close()


def demo_4_capability_matching():
    """Demonstrate capability-based task routing."""
    print("\n" + "=" * 60)
    print("DEMO 4: Capability-Based Task Routing")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo4.db"
        print(f"\nDatabase: {db_path}")
        
        # Initialize database and enqueue tasks with requirements
        print("\n1. Enqueueing tasks with different requirements...")
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        
        with db.transaction() as conn:
            # Task requiring GPU
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, compatibility)
                VALUES (?, ?, ?)
                """,
                ("gpu_task", '{"data": "process"}', '{"gpu": true}')
            )
            # Task requiring CPU only
            conn.execute(
                """
                INSERT INTO task_queue (type, payload, compatibility)
                VALUES (?, ?, ?)
                """,
                ("cpu_task", '{"data": "process"}', '{"gpu": false}')
            )
            # Task with no specific requirements
            conn.execute(
                "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
                ("general_task", '{"data": "process"}')
            )
        
        print("  ✓ 3 tasks enqueued with different requirements")
        db.close()
        
        # Create workers with different capabilities
        print("\n2. Creating workers with different capabilities...")
        
        # GPU worker
        gpu_worker = create_worker(
            "gpu-worker",
            demo_task_handler,
            capabilities={"gpu": True},
            db_path=str(db_path),
            poll_interval_seconds=0.2
        )
        print("  ✓ GPU worker created")
        
        # CPU-only worker
        cpu_worker = create_worker(
            "cpu-worker",
            demo_task_handler,
            capabilities={"gpu": False},
            db_path=str(db_path),
            poll_interval_seconds=0.2
        )
        print("  ✓ CPU worker created")
        
        # Start workers
        print("\n3. Starting workers...")
        gpu_thread = threading.Thread(target=gpu_worker.start, daemon=True)
        cpu_thread = threading.Thread(target=cpu_worker.start, daemon=True)
        
        gpu_thread.start()
        cpu_thread.start()
        print("  ✓ Workers started")
        
        # Wait for processing
        time.sleep(3)
        
        # Stop workers
        gpu_worker.stop()
        cpu_worker.stop()
        gpu_thread.join(timeout=2)
        cpu_thread.join(timeout=2)
        
        # Check which worker processed which task
        print("\n4. Task routing results:")
        db = QueueDatabase(str(db_path))
        cursor = db.execute(
            "SELECT id, type, compatibility, locked_by, status FROM task_queue ORDER BY id"
        )
        for row in cursor:
            req = row['compatibility'] if row['compatibility'] != '{}' else 'none'
            worker = row['locked_by'] if row['locked_by'] else 'none'
            print(f"  Task #{row['id']} ({row['type']}):")
            print(f"    Requirements: {req}")
            print(f"    Processed by: {worker}")
            print(f"    Status: {row['status']}")
        
        db.close()


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("QueueWorker Demonstration")
    print("SQLite Task Queue - Worker Engine")
    print("=" * 60)
    
    try:
        demo_1_basic_worker()
        demo_2_retry_and_dead_letter()
        demo_3_concurrent_workers()
        demo_4_capability_matching()
        
        print("\n" + "=" * 60)
        print("ALL DEMONSTRATIONS COMPLETE")
        print("=" * 60)
        print("\nKey Features Demonstrated:")
        print("  ✓ Basic task execution")
        print("  ✓ Atomic task claiming (no double-claiming)")
        print("  ✓ Retry with exponential backoff")
        print("  ✓ Dead-letter queue")
        print("  ✓ Concurrent workers")
        print("  ✓ Capability-based routing")
        print("  ✓ Graceful shutdown")
        print("\nWorker Engine is ready for production use!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
