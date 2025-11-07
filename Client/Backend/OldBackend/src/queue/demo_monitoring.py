"""
Demo script for queue monitoring and observability (Issue #330).

This script demonstrates:
- Worker registration and heartbeat updates
- Stale worker detection
- Queue metrics collection
- Worker activity tracking
"""

import time
import json
from pathlib import Path
import tempfile

from src.queue import QueueDatabase, QueueMonitoring


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def demo_worker_registration():
    """Demonstrate worker registration and heartbeat updates."""
    print_section("Worker Registration & Heartbeat")
    
    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo_queue.db"
        
        with QueueDatabase(str(db_path)) as db:
            db.initialize_schema()
            monitoring = QueueMonitoring(db)
            
            # Register workers
            print("1. Registering workers...")
            monitoring.register_worker("worker-01", {"cpu": 8, "gpu": True, "type": "video"})
            monitoring.register_worker("worker-02", {"cpu": 4, "type": "audio"})
            monitoring.register_worker("worker-03", {"cpu": 16, "type": "image"})
            print("   ✓ Registered 3 workers")
            
            # List all workers
            workers = monitoring.get_all_workers()
            print(f"\n2. All workers ({len(workers)}):")
            for worker in workers:
                capabilities = worker.get_capabilities_dict()
                print(f"   - {worker.worker_id}: {json.dumps(capabilities)}")
            
            # Update heartbeat
            print("\n3. Updating heartbeats...")
            time.sleep(1.1)  # SQLite datetime precision is 1 second
            monitoring.update_heartbeat("worker-01")
            monitoring.update_heartbeat("worker-02")
            print("   ✓ Updated heartbeats for worker-01 and worker-02")
            
            # Check active workers
            active = monitoring.get_active_workers(active_threshold_seconds=60)
            print(f"\n4. Active workers ({len(active)}):")
            for worker in active:
                print(f"   - {worker.worker_id} (last heartbeat: {worker.heartbeat_utc})")


def demo_stale_worker_detection():
    """Demonstrate stale worker detection."""
    print_section("Stale Worker Detection")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo_queue.db"
        
        with QueueDatabase(str(db_path)) as db:
            db.initialize_schema()
            monitoring = QueueMonitoring(db)
            
            # Register workers
            print("1. Registering workers...")
            monitoring.register_worker("worker-01", {"status": "active"})
            monitoring.register_worker("worker-02", {"status": "active"})
            monitoring.register_worker("worker-03", {"status": "active"})
            print("   ✓ Registered 3 workers")
            
            # Simulate worker-02 becoming stale
            print("\n2. Simulating worker-02 becoming stale...")
            db.execute(
                "UPDATE workers SET heartbeat_utc = datetime('now', '-10 minutes') WHERE worker_id = ?",
                ("worker-02",)
            )
            db.get_connection().commit()
            print("   ✓ Worker-02 heartbeat set to 10 minutes ago")
            
            # Check active and stale workers
            active = monitoring.get_active_workers(active_threshold_seconds=60)
            stale = monitoring.get_stale_workers(stale_threshold_seconds=300)
            
            print(f"\n3. Worker status:")
            print(f"   Active workers ({len(active)}): {[w.worker_id for w in active]}")
            print(f"   Stale workers ({len(stale)}): {[w.worker_id for w in stale]}")
            
            # Cleanup stale workers
            print("\n4. Cleaning up stale workers...")
            for worker in stale:
                monitoring.remove_worker(worker.worker_id)
                print(f"   ✓ Removed {worker.worker_id}")
            
            remaining = monitoring.get_all_workers()
            print(f"\n5. Remaining workers: {[w.worker_id for w in remaining]}")


def demo_queue_metrics():
    """Demonstrate queue metrics collection."""
    print_section("Queue Metrics & Statistics")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo_queue.db"
        
        with QueueDatabase(str(db_path)) as db:
            db.initialize_schema()
            monitoring = QueueMonitoring(db)
            
            # Add workers
            print("1. Registering workers...")
            monitoring.register_worker("worker-01", {"type": "video"})
            monitoring.register_worker("worker-02", {"type": "audio"})
            print("   ✓ Registered 2 workers")
            
            # Add tasks
            print("\n2. Adding tasks to queue...")
            tasks_data = [
                ("video", "queued", 100),
                ("video", "queued", 50),
                ("audio", "processing", 100),
                ("image", "completed", 100),
                ("text", "completed", 100),
                ("data", "failed", 100),
            ]
            
            for task_type, status, priority in tasks_data:
                db.execute(
                    "INSERT INTO task_queue (type, status, priority, payload) VALUES (?, ?, ?, ?)",
                    (task_type, status, priority, "{}")
                )
            db.get_connection().commit()
            print(f"   ✓ Added {len(tasks_data)} tasks")
            
            # Get metrics
            print("\n3. Queue metrics:")
            metrics = monitoring.get_queue_metrics()
            
            print(f"\n   Queue depth by status:")
            for status, count in metrics["queue_depth_by_status"].items():
                print(f"     - {status}: {count}")
            
            print(f"\n   Queue depth by type (queued only):")
            for task_type, count in metrics["queue_depth_by_type"].items():
                print(f"     - {task_type}: {count}")
            
            print(f"\n   Task statistics:")
            print(f"     - Success rate: {metrics['success_rate']:.1%}" if metrics['success_rate'] else "     - Success rate: N/A")
            print(f"     - Failure rate: {metrics['failure_rate']:.1%}" if metrics['failure_rate'] else "     - Failure rate: N/A")
            
            print(f"\n   Worker statistics:")
            print(f"     - Total workers: {metrics['total_workers']}")
            print(f"     - Active workers: {metrics['active_workers']}")
            print(f"     - Stale workers: {metrics['stale_workers']}")


def demo_worker_activity():
    """Demonstrate worker activity tracking."""
    print_section("Worker Activity Tracking")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo_queue.db"
        
        with QueueDatabase(str(db_path)) as db:
            db.initialize_schema()
            monitoring = QueueMonitoring(db)
            
            # Register workers at different times
            print("1. Registering workers at different times...")
            monitoring.register_worker("worker-01", {"priority": "high"})
            print("   ✓ Registered worker-01")
            
            time.sleep(1.1)
            monitoring.register_worker("worker-02", {"priority": "medium"})
            print("   ✓ Registered worker-02")
            
            time.sleep(1.1)
            monitoring.register_worker("worker-03", {"priority": "low"})
            print("   ✓ Registered worker-03")
            
            # Get worker activity
            print("\n2. Worker activity (sorted by most recent heartbeat):")
            activity = monitoring.get_worker_activity()
            
            for worker_activity in activity:
                worker_id = worker_activity["worker_id"]
                seconds_since = worker_activity["seconds_since_heartbeat"]
                capabilities = json.loads(worker_activity["capabilities"])
                
                print(f"   - {worker_id}:")
                print(f"     • Last heartbeat: {seconds_since} seconds ago")
                print(f"     • Capabilities: {json.dumps(capabilities)}")


def demo_worker_lifecycle():
    """Demonstrate complete worker lifecycle."""
    print_section("Complete Worker Lifecycle")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo_queue.db"
        
        with QueueDatabase(str(db_path)) as db:
            db.initialize_schema()
            monitoring = QueueMonitoring(db)
            
            print("1. Worker registration")
            monitoring.register_worker("worker-lifecycle", {"cpu": 8})
            worker = monitoring.get_worker("worker-lifecycle")
            print(f"   ✓ Registered: {worker.worker_id}")
            print(f"   ✓ Capabilities: {worker.get_capabilities_dict()}")
            
            print("\n2. Heartbeat updates")
            for i in range(3):
                time.sleep(1.1)
                monitoring.update_heartbeat("worker-lifecycle")
                print(f"   ✓ Heartbeat update #{i+1}")
            
            print("\n3. Check worker status")
            active = monitoring.get_active_workers()
            print(f"   ✓ Worker is active: {'worker-lifecycle' in [w.worker_id for w in active]}")
            
            print("\n4. Worker removal")
            monitoring.remove_worker("worker-lifecycle")
            worker = monitoring.get_worker("worker-lifecycle")
            print(f"   ✓ Worker removed: {worker is None}")


def main():
    """Run all demo functions."""
    print("\n" + "=" * 60)
    print("  Queue Monitoring & Observability Demo (Issue #330)")
    print("=" * 60)
    
    demo_worker_registration()
    demo_stale_worker_detection()
    demo_queue_metrics()
    demo_worker_activity()
    demo_worker_lifecycle()
    
    print_section("Demo Complete!")
    print("All monitoring features demonstrated successfully.\n")


if __name__ == "__main__":
    main()
