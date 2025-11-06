#!/usr/bin/env python
"""
Integration example: Worker with configuration (Issue #328 + #327)

This example demonstrates:
- Loading worker configuration from file
- Creating a database and task claimer
- Processing tasks using the configured strategy
- Complete worker loop with configuration

Usage:
    cd Client/Backend
    python src/queue/example_worker.py
"""

import sys
import tempfile
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from queue import (
    load_worker_config,
    QueueDatabase,
    TaskClaimerFactory,
)


def process_task(task):
    """
    Simulate task processing.
    
    In a real implementation, this would:
    - Parse task payload
    - Execute the task logic
    - Handle errors and retries
    """
    print(f"    Processing task {task.id}: {task.type}")
    time.sleep(0.1)  # Simulate work
    print(f"    Task {task.id} completed")


def run_worker(config_file: str, max_tasks: int = 5):
    """
    Run a worker with configuration.
    
    Args:
        config_file: Path to worker configuration file
        max_tasks: Maximum number of tasks to process (for demo)
    """
    print("="*70)
    print("Worker Example - Issue #328")
    print("="*70)
    
    # Load configuration
    print(f"\n1. Loading configuration from: {config_file}")
    config = load_worker_config(config_file, apply_env_overrides=True)
    
    print(f"\n   Worker Configuration:")
    print(f"     Worker ID: {config.worker_id}")
    print(f"     Strategy: {config.scheduling_strategy.value}")
    print(f"     Lease Duration: {config.lease_duration_seconds}s")
    print(f"     Poll Interval: {config.poll_interval_seconds}s")
    print(f"     Max Retries: {config.max_retries}")
    print(f"     Capabilities: {config.capabilities}")
    
    # Create database (temporary for demo)
    print(f"\n2. Initializing database...")
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "worker.db"
        db = QueueDatabase(str(db_path))
        db.initialize_schema()
        print(f"   ✓ Database initialized")
        
        # Create task claimer based on configuration
        print(f"\n3. Creating task claimer...")
        claimer = TaskClaimerFactory.create(config.scheduling_strategy, db)
        print(f"   ✓ Using {claimer.__class__.__name__}")
        
        # Enqueue test tasks
        print(f"\n4. Enqueueing test tasks...")
        task_types = [
            ("video_processing", 50),
            ("image_resize", 100),
            ("urgent_task", 1),
            ("background_job", 200),
            ("normal_task", 100),
        ]
        
        for task_type, priority in task_types:
            db.execute(
                """
                INSERT INTO task_queue (type, payload, priority, status, run_after_utc)
                VALUES (?, ?, ?, 'queued', datetime('now'))
                """,
                (task_type, '{"data": "test"}', priority)
            )
        db.get_connection().commit()
        print(f"   ✓ Enqueued {len(task_types)} tasks")
        
        # Worker loop
        print(f"\n5. Starting worker loop...")
        print(f"   Strategy: {config.scheduling_strategy.value}")
        print(f"   Processing order:")
        
        processed = 0
        while processed < max_tasks:
            # Claim task using configured strategy
            task = claimer.claim_task(
                worker_id=config.worker_id,
                capabilities=config.capabilities,
                lease_seconds=config.lease_duration_seconds
            )
            
            if task:
                print(f"\n   Claimed Task #{task.id}:")
                print(f"     Type: {task.type}")
                print(f"     Priority: {task.priority}")
                print(f"     Status: {task.status}")
                
                try:
                    # Process the task
                    process_task(task)
                    
                    # Mark as completed
                    db.execute(
                        """
                        UPDATE task_queue 
                        SET status = 'completed',
                            finished_at_utc = datetime('now')
                        WHERE id = ?
                        """,
                        (task.id,)
                    )
                    db.get_connection().commit()
                    processed += 1
                    
                except Exception as e:
                    # Mark as failed
                    print(f"    ✗ Task failed: {e}")
                    db.execute(
                        """
                        UPDATE task_queue 
                        SET status = 'failed',
                            error_message = ?,
                            finished_at_utc = datetime('now')
                        WHERE id = ?
                        """,
                        (str(e), task.id)
                    )
                    db.get_connection().commit()
                    processed += 1
            else:
                # No tasks available
                print(f"\n   No tasks available (processed {processed}/{max_tasks})")
                break
            
            # Wait before polling again
            time.sleep(config.poll_interval_seconds)
        
        # Summary
        print(f"\n6. Worker Summary:")
        
        cursor = db.execute(
            "SELECT status, COUNT(*) as count FROM task_queue GROUP BY status"
        )
        for row in cursor:
            print(f"   {row['status']}: {row['count']}")
        
        db.close()
    
    print("\n" + "="*70)
    print("Worker completed successfully!")
    print("="*70)


def main():
    """Run worker example."""
    # Determine example configuration file
    examples_dir = Path(__file__).parent / "examples"
    
    # Try different strategies
    configs = [
        ("worker_config.json", "Default (Priority)"),
        ("worker_priority.yaml", "Priority Strategy"),
    ]
    
    for config_file, description in configs:
        config_path = examples_dir / config_file
        
        if config_path.exists():
            print(f"\n\nRunning example: {description}")
            try:
                run_worker(str(config_path))
            except ImportError as e:
                print(f"\n⚠ Skipped: {e}")
            break
    else:
        print("No example configuration files found")
        print(f"Expected location: {examples_dir}")


if __name__ == "__main__":
    main()
