"""
Demo: Task Handler Registry

Demonstrates Worker 10 Issue #339: Ensure Client takes only registered task handlers.
Shows how to prevent automatic module discovery from database.

This demo shows:
1. Registering task handlers explicitly
2. Processing tasks with registered handlers
3. Handling tasks without registered handlers (fail immediately)
4. Using the global registry singleton
"""

import json
import sys
from pathlib import Path

# Add Backend directory to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.queue import (
    QueueDatabase,
    Task,
    WorkerEngine,
    TaskHandlerRegistry,
    get_global_registry,
    SchedulingStrategy,
)


def demo_basic_registration():
    """Demonstrate basic handler registration."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Handler Registration")
    print("=" * 70)
    
    registry = TaskHandlerRegistry()
    
    # Define some task handlers
    def email_handler(task: Task):
        """Handle email sending tasks."""
        payload = task.get_payload_dict()
        print(f"  📧 Sending email to: {payload.get('to', 'unknown')}")
        print(f"     Subject: {payload.get('subject', 'No subject')}")
    
    def report_handler(task: Task):
        """Handle report generation tasks."""
        payload = task.get_payload_dict()
        print(f"  📊 Generating report: {payload.get('report_type', 'unknown')}")
    
    def data_import_handler(task: Task):
        """Handle data import tasks."""
        payload = task.get_payload_dict()
        print(f"  📥 Importing data from: {payload.get('source', 'unknown')}")
    
    # Register handlers
    print("\n1. Registering task handlers:")
    registry.register_handler(
        "send_email",
        email_handler,
        description="Handles email sending tasks",
        version="1.0.0"
    )
    print("   ✓ Registered: send_email")
    
    registry.register_handler(
        "generate_report",
        report_handler,
        description="Handles report generation tasks",
        version="1.0.0"
    )
    print("   ✓ Registered: generate_report")
    
    registry.register_handler(
        "import_data",
        data_import_handler,
        description="Handles data import tasks",
        version="1.0.0"
    )
    print("   ✓ Registered: import_data")
    
    # Show registered types
    print("\n2. Registered task types:")
    for task_type in sorted(registry.get_registered_types()):
        info = registry.get_handler_info(task_type)
        print(f"   • {task_type}: {info.description} (v{info.version})")
    
    # Try to get a handler
    print("\n3. Getting handler for 'send_email':")
    handler = registry.get_handler("send_email")
    print(f"   ✓ Retrieved handler: {handler.__name__}")
    
    # Try to get an unregistered handler
    print("\n4. Trying to get unregistered handler 'unknown_task':")
    try:
        registry.get_handler("unknown_task")
        print("   ✗ Should have raised error!")
    except Exception as e:
        print(f"   ✓ Correctly raised error: {type(e).__name__}")
        print(f"   Message: {str(e)[:80]}...")


def demo_worker_with_registry():
    """Demonstrate worker engine with handler registry."""
    print("\n" + "=" * 70)
    print("DEMO 2: Worker Engine with Handler Registry")
    print("=" * 70)
    
    # Create database
    db = QueueDatabase(":memory:")
    db.initialize_schema()
    
    # Create registry and register handlers
    registry = TaskHandlerRegistry()
    
    def process_payment(task: Task):
        """Process payment task."""
        payload = task.get_payload_dict()
        print(f"  💳 Processing payment of ${payload.get('amount', 0)} for order {payload.get('order_id', 'unknown')}")
    
    def send_notification(task: Task):
        """Send notification task."""
        payload = task.get_payload_dict()
        print(f"  🔔 Sending notification: {payload.get('message', 'No message')}")
    
    registry.register_handler("process_payment", process_payment)
    registry.register_handler("send_notification", send_notification)
    
    print("\n1. Registered handlers:")
    print(f"   {', '.join(sorted(registry.get_registered_types()))}")
    
    # Enqueue some tasks
    print("\n2. Enqueuing tasks:")
    
    with db.transaction() as conn:
        # Task 1: Registered handler
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority)
            VALUES (?, ?, ?)
            """,
            ("process_payment", json.dumps({"amount": 99.99, "order_id": "ORD-123"}), 10)
        )
        print("   ✓ Enqueued: process_payment (has handler)")
        
        # Task 2: Registered handler
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority)
            VALUES (?, ?, ?)
            """,
            ("send_notification", json.dumps({"message": "Payment received"}), 20)
        )
        print("   ✓ Enqueued: send_notification (has handler)")
        
        # Task 3: NO registered handler
        conn.execute(
            """
            INSERT INTO task_queue (type, payload, priority)
            VALUES (?, ?, ?)
            """,
            ("unregistered_task", json.dumps({"data": "some data"}), 30)
        )
        print("   ⚠️  Enqueued: unregistered_task (NO handler)")
    
    # Create worker with registry
    print("\n3. Creating worker with registry:")
    worker = WorkerEngine(
        db=db,
        worker_id="demo-worker-01",
        scheduling_strategy=SchedulingStrategy.PRIORITY,
        handler_registry=registry
    )
    print("   ✓ Worker created with registry")
    
    # Process tasks
    print("\n4. Processing tasks:")
    for i in range(3):
        processed = worker.claim_and_process()
        if processed:
            print(f"   Task {i+1} processed")
        else:
            print(f"   No more tasks available")
            break
    
    # Check final task statuses
    print("\n5. Final task statuses:")
    cursor = db.execute(
        "SELECT id, type, status, error_message FROM task_queue ORDER BY id"
    )
    for row in cursor.fetchall():
        task_dict = dict(row)
        status_icon = "✓" if task_dict["status"] == "completed" else "✗"
        print(f"   {status_icon} Task #{task_dict['id']}: {task_dict['type']} - {task_dict['status']}")
        if task_dict["error_message"]:
            print(f"     Error: {task_dict['error_message'][:80]}...")


def demo_global_registry():
    """Demonstrate using the global registry singleton."""
    print("\n" + "=" * 70)
    print("DEMO 3: Global Registry Singleton")
    print("=" * 70)
    
    # Get global registry
    registry = get_global_registry()
    
    print("\n1. Using global registry singleton:")
    print(f"   Registry instance: {id(registry)}")
    
    # Register a handler
    def backup_handler(task: Task):
        print("  💾 Running backup task")
    
    registry.register_handler("backup_database", backup_handler)
    print("   ✓ Registered: backup_database")
    
    # Get registry again - should be same instance
    registry2 = get_global_registry()
    print(f"\n2. Getting registry again:")
    print(f"   Same instance? {registry is registry2}")
    print(f"   Handler still registered? {registry2.is_registered('backup_database')}")


def demo_handler_override():
    """Demonstrate handler override functionality."""
    print("\n" + "=" * 70)
    print("DEMO 4: Handler Override")
    print("=" * 70)
    
    registry = TaskHandlerRegistry()
    
    def handler_v1(task: Task):
        print("  Handler version 1")
    
    def handler_v2(task: Task):
        print("  Handler version 2")
    
    # Register v1
    print("\n1. Registering handler v1:")
    registry.register_handler("my_task", handler_v1, version="1.0.0")
    print("   ✓ Registered v1")
    
    # Try to register v2 without override - should fail
    print("\n2. Trying to register v2 without allow_override:")
    try:
        registry.register_handler("my_task", handler_v2, version="2.0.0")
        print("   ✗ Should have raised error!")
    except Exception as e:
        print(f"   ✓ Correctly raised: {type(e).__name__}")
    
    # Register v2 with override
    print("\n3. Registering v2 with allow_override=True:")
    registry.register_handler("my_task", handler_v2, version="2.0.0", allow_override=True)
    print("   ✓ Successfully overridden")
    
    # Verify new handler is active
    info = registry.get_handler_info("my_task")
    print(f"   Current version: {info.version}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("Task Handler Registry Demo")
    print("Worker 10 - Issue #339: Registered Task Handlers Only")
    print("=" * 70)
    
    demo_basic_registration()
    demo_worker_with_registry()
    demo_global_registry()
    demo_handler_override()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("• Task handlers must be explicitly registered")
    print("• Unregistered task types will fail immediately (no retry)")
    print("• No automatic discovery of tasks from database")
    print("• Use global registry for convenience")
    print("• Thread-safe handler registration")
    print()


if __name__ == "__main__":
    main()
