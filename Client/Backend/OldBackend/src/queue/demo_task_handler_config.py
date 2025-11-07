"""
Demo: Task Handler Configuration Loading

Demonstrates loading task handlers from configuration files.
Part of Worker 10 Issue #339.

Shows how to:
1. Load handlers from JSON configuration file
2. Automatically register handlers from config
3. Process tasks with config-loaded handlers
"""

import json
import sys
from pathlib import Path

# Add Backend directory to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.queue import (
    QueueDatabase,
    WorkerEngine,
    load_handlers_from_config,
    SchedulingStrategy,
)


def demo_config_loading():
    """Demonstrate loading handlers from configuration file."""
    print("\n" + "=" * 70)
    print("DEMO: Loading Task Handlers from Configuration")
    print("=" * 70)
    
    # Path to configuration file
    config_path = backend_dir / "configs" / "task_handlers.json"
    
    print(f"\n1. Configuration file: {config_path}")
    print(f"   Exists: {config_path.exists()}")
    
    # Load configuration to show what's in it
    with open(config_path) as f:
        config = json.load(f)
    
    print(f"\n2. Handlers defined in configuration:")
    for handler in config['handlers']:
        print(f"   • {handler['task_type']}")
        print(f"     Module: {handler['module']}")
        print(f"     Function: {handler['function']}")
        print(f"     Version: {handler['version']}")
        print()
    
    # Load handlers from config
    print("3. Loading handlers from configuration file...")
    registry = load_handlers_from_config(config_path)
    
    print(f"\n4. Successfully registered {len(registry.get_registered_types())} handlers:")
    for task_type in sorted(registry.get_registered_types()):
        info = registry.get_handler_info(task_type)
        print(f"   ✓ {task_type} (v{info.version}): {info.description}")


def demo_worker_with_config():
    """Demonstrate worker using config-loaded handlers."""
    print("\n" + "=" * 70)
    print("DEMO: Worker Using Config-Loaded Handlers")
    print("=" * 70)
    
    # Create database
    db = QueueDatabase(":memory:")
    db.initialize_schema()
    
    # Load handlers from config
    config_path = backend_dir / "configs" / "task_handlers.json"
    registry = load_handlers_from_config(config_path)
    
    print("\n1. Registry loaded from configuration")
    print(f"   Registered handlers: {', '.join(sorted(registry.get_registered_types()))}")
    
    # Enqueue various tasks
    print("\n2. Enqueuing tasks:")
    
    with db.transaction() as conn:
        # Email task
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority)
            VALUES (?, ?, ?)
            """,
            (
                "send_email",
                json.dumps({
                    "to": "user@example.com",
                    "subject": "Welcome!",
                    "body": "Thanks for signing up"
                }),
                10
            )
        )
        print("   ✓ Enqueued: send_email")
        
        # Report task
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority)
            VALUES (?, ?, ?)
            """,
            (
                "generate_report",
                json.dumps({
                    "report_type": "sales",
                    "format": "pdf",
                    "filters": {"month": "November"}
                }),
                20
            )
        )
        print("   ✓ Enqueued: generate_report")
        
        # Backup task
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority)
            VALUES (?, ?, ?)
            """,
            (
                "backup_database",
                json.dumps({
                    "database_name": "production",
                    "backup_path": "/backups",
                    "compress": True
                }),
                30
            )
        )
        print("   ✓ Enqueued: backup_database")
        
        # Payment task
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority)
            VALUES (?, ?, ?)
            """,
            (
                "process_payment",
                json.dumps({
                    "amount": 99.99,
                    "currency": "USD",
                    "payment_method": "credit_card",
                    "customer_id": "CUST-123"
                }),
                5
            )
        )
        print("   ✓ Enqueued: process_payment")
    
    # Create worker with config-loaded registry
    print("\n3. Creating worker with config-loaded handlers:")
    worker = WorkerEngine(
        db=db,
        worker_id="config-demo-worker",
        scheduling_strategy=SchedulingStrategy.PRIORITY,
        handler_registry=registry
    )
    print("   ✓ Worker ready")
    
    # Process all tasks
    print("\n4. Processing tasks:")
    task_count = 0
    while True:
        processed = worker.claim_and_process()
        if not processed:
            break
        task_count += 1
    
    print(f"\n5. Processed {task_count} tasks")
    
    # Show final status
    print("\n6. Final task statuses:")
    cursor = db.execute(
        "SELECT id, type, status FROM task_queue ORDER BY id"
    )
    for row in cursor.fetchall():
        task_dict = dict(row)
        status_icon = "✓" if task_dict["status"] == "completed" else "✗"
        print(f"   {status_icon} Task #{task_dict['id']}: {task_dict['type']} - {task_dict['status']}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("Task Handler Configuration Demo")
    print("Worker 10 - Issue #339: Configuration-Based Handler Registration")
    print("=" * 70)
    
    demo_config_loading()
    demo_worker_with_config()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("• Handlers can be defined in JSON/YAML/TOML configuration files")
    print("• Configuration maps task types to Python module functions")
    print("• No code changes needed to add new handler types")
    print("• Supports versioning and descriptions in config")
    print("• Workers automatically route tasks to configured handlers")
    print()


if __name__ == "__main__":
    main()
