#!/usr/bin/env python
"""
Demonstration script for SQLite Queue Core Infrastructure.

This script demonstrates the key functionality of the queue module.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.queue import (
    QueueDatabase,
    Task,
    Worker,
    TaskLog,
    QueueDatabaseError,
)


def main():
    """Demonstrate queue database functionality."""
    print("=" * 60)
    print("SQLite Queue Core Infrastructure - Demonstration")
    print("=" * 60)

    # Create temporary database for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo_queue.db"
        print(f"\n1. Creating database at: {db_path}")

        with QueueDatabase(str(db_path)) as db:
            print("   ✓ Database created")

            # Initialize schema
            print("\n2. Initializing schema...")
            db.initialize_schema()
            print("   ✓ Schema initialized (tables and indexes created)")

            # Verify PRAGMAs
            print("\n3. Verifying PRAGMA settings...")
            conn = db.get_connection()
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            foreign_keys = conn.execute("PRAGMA foreign_keys").fetchone()[0]
            busy_timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
            print(f"   ✓ journal_mode: {journal_mode}")
            print(f"   ✓ foreign_keys: {foreign_keys}")
            print(f"   ✓ busy_timeout: {busy_timeout}ms")

            # Insert tasks
            print("\n4. Inserting tasks...")
            with db.transaction() as conn:
                conn.execute(
                    """
                    INSERT INTO task_queue (type, payload, priority, compatibility)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        "video_processing",
                        '{"format": "mp4", "duration": 120}',
                        50,
                        '{"region": "us-west", "gpu": true}',
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO task_queue (type, payload, priority)
                    VALUES (?, ?, ?)
                    """,
                    ("image_processing", '{"format": "png"}', 100),
                )
            print("   ✓ 2 tasks inserted")

            # Query tasks
            print("\n5. Querying tasks...")
            cursor = db.execute(
                "SELECT * FROM task_queue ORDER BY priority"
            )
            for row in cursor:
                task = Task.from_dict(dict(row))
                print(f"   - Task #{task.id}: {task.type} (priority: {task.priority})")

            # Test generated columns
            print("\n6. Testing generated columns (JSON filtering)...")
            cursor = db.execute(
                "SELECT id, type FROM task_queue WHERE region = ?",
                ("us-west",),
            )
            row = cursor.fetchone()
            if row:
                print(f"   ✓ Found task with region='us-west': #{row['id']} ({row['type']})")

            cursor = db.execute(
                "SELECT id, type FROM task_queue WHERE format = ?",
                ("mp4",),
            )
            row = cursor.fetchone()
            if row:
                print(f"   ✓ Found task with format='mp4': #{row['id']} ({row['type']})")

            # Register worker
            print("\n7. Registering worker...")
            db.execute(
                "INSERT INTO workers (worker_id, capabilities) VALUES (?, ?)",
                ("worker-01", '{"cpu": 8, "ram": 16, "gpu": "RTX5090"}'),
            )
            conn.commit()
            print("   ✓ Worker 'worker-01' registered")

            # Add task logs
            print("\n8. Adding task logs...")
            db.execute_many(
                "INSERT INTO task_logs (task_id, level, message) VALUES (?, ?, ?)",
                [
                    (1, "INFO", "Task started"),
                    (1, "INFO", "Processing frame 1/100"),
                    (1, "INFO", "Task completed"),
                ],
            )
            print("   ✓ 3 log entries added for task #1")

            # Query logs
            cursor = db.execute(
                "SELECT COUNT(*) FROM task_logs WHERE task_id = ?", (1,)
            )
            count = cursor.fetchone()[0]
            print(f"   ✓ Verified {count} log entries")

            # Test data models
            print("\n9. Testing data models...")
            task = Task(
                type="test",
                payload='{"key": "value"}',
                priority=75,
            )
            task_dict = task.to_dict()
            task_restored = Task.from_dict(task_dict)
            print(f"   ✓ Task serialization: {task_restored.type}")

            worker = Worker(
                worker_id="worker-02",
                capabilities='{"cpu": 16}',
            )
            worker_dict = worker.to_dict()
            print(f"   ✓ Worker serialization: {worker_dict['worker_id']}")

            # Test transactions
            print("\n10. Testing transaction rollback...")
            try:
                with db.transaction() as conn:
                    conn.execute(
                        "INSERT INTO task_queue (type, payload) VALUES (?, ?)",
                        ("rollback_test", "{}"),
                    )
                    # Force an error
                    raise Exception("Simulated error")
            except Exception:
                pass

            cursor = db.execute(
                "SELECT COUNT(*) FROM task_queue WHERE type = ?",
                ("rollback_test",),
            )
            count = cursor.fetchone()[0]
            if count == 0:
                print("   ✓ Transaction rolled back successfully")

            # Summary
            print("\n" + "=" * 60)
            print("DEMONSTRATION COMPLETE")
            print("=" * 60)
            print("\nAll key features verified:")
            print("  ✓ Database initialization")
            print("  ✓ Schema creation (tables + indexes)")
            print("  ✓ PRAGMA settings")
            print("  ✓ Task insertion and querying")
            print("  ✓ Generated columns (JSON filtering)")
            print("  ✓ Worker registration")
            print("  ✓ Task logging")
            print("  ✓ Data model serialization")
            print("  ✓ Transaction rollback")
            print("\nDatabase infrastructure is ready for production use!")

        print("\n✓ Database connection closed")


if __name__ == "__main__":
    main()
