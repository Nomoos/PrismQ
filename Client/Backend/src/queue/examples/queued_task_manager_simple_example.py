"""
Example: Using QueuedTaskManager as BackgroundTaskManager replacement

This example demonstrates how QueuedTaskManager provides a drop-in
replacement for BackgroundTaskManager with persistent queue backend.

To run this example from the Backend directory:
    python -c "import sys; sys.path.insert(0, 'src'); import asyncio; from queue.examples.queued_task_manager_simple_example import main; asyncio.run(main())"
"""

import asyncio
from datetime import datetime, timezone

from src.core.queued_task_manager import QueuedTaskManager
from src.core.run_registry import RunRegistry
from src.queue import QueueDatabase
from src.queue.integration import create_queued_task_manager
from src.models.run import Run, RunStatus


async def example_1_basic_usage():
    """Example 1: Basic usage - drop-in replacement."""
    print("\n=== Example 1: Basic Usage ===")
    
    # Initialize QueuedTaskManager (same interface as BackgroundTaskManager)
    manager = create_queued_task_manager()
    
    # Create a Run object
    run = Run(
        run_id="cleanup-001",
        module_id="cleanup",
        module_name="Cleanup Task",
        status=RunStatus.QUEUED,
        created_at=datetime.now(timezone.utc),
        parameters={"max_age_hours": 24}
    )
    
    # Add to registry
    manager.registry.add_run(run)
    
    # Define task (coroutine not actually used, kept for API compatibility)
    async def cleanup_task():
        print("  [Task] Cleanup running...")
        await asyncio.sleep(0.5)
        print("  [Task] Cleanup done!")
        return "completed"
    
    # Start task (same API as BackgroundTaskManager!)
    print(f"  Starting task: {run.run_id}")
    task_id = manager.start_task(run, cleanup_task())
    print(f"  Task enqueued with ID: {task_id}")
    
    # Check status
    status = await manager.get_task_status(task_id)
    print(f"  Task status: {status['status']}")
    
    # Task is now in persistent queue!
    print("  ✓ Task persisted in SQLite queue")
    
    return manager


async def example_2_enhanced_features():
    """Example 2: Using enhanced queue features."""
    print("\n=== Example 2: Enhanced Features ===")
    
    manager = create_queued_task_manager()
    
    # Feature 1: Direct task scheduling (without Run object)
    print("  Scheduling task directly...")
    task_id = await manager.schedule_task(
        task_type="backup",
        payload={"backup_type": "full", "target": "s3"},
        priority=50  # Lower = higher priority
    )
    print(f"  Task scheduled with ID: {task_id}")
    
    # Feature 2: Get detailed status
    status = await manager.get_task_status(task_id)
    print(f"  Task type: {status['type']}")
    print(f"  Task status: {status['status']}")
    print(f"  Created at: {status['created_at']}")
    
    # Feature 3: Register task handlers
    print("\n  Registering task handlers...")
    
    async def backup_handler(task):
        print(f"    Processing backup task {task.id}...")
        return {"status": "completed"}
    
    await manager.register_task(
        "backup",
        backup_handler,
        "Handles backup tasks"
    )
    print("  ✓ Handler registered")
    
    return manager


async def example_3_backward_compatibility():
    """Example 3: Full backward compatibility test."""
    print("\n=== Example 3: Backward Compatibility ===")
    
    manager = create_queued_task_manager()
    
    # Use all BackgroundTaskManager methods
    print("  Testing BackgroundTaskManager API compatibility...")
    
    # 1. start_task
    run = Run(
        run_id="compat-test-001",
        module_id="test",
        module_name="Compatibility Test",
        status=RunStatus.QUEUED,
        created_at=datetime.now(timezone.utc),
        parameters={}
    )
    manager.registry.add_run(run)
    
    async def test_task():
        return "done"
    
    task_id = manager.start_task(run, test_task())
    print(f"  ✓ start_task: {task_id}")
    
    # 2. is_task_active
    is_active = manager.is_task_active(task_id)
    print(f"  ✓ is_task_active: {is_active}")
    
    # 3. get_active_task_count
    count = manager.get_active_task_count()
    print(f"  ✓ get_active_task_count: {count}")
    
    # 4. get_active_task_ids
    ids = manager.get_active_task_ids()
    print(f"  ✓ get_active_task_ids: {ids}")
    
    # 5. cancel_task
    success = await manager.cancel_task(task_id)
    print(f"  ✓ cancel_task: {success}")
    
    # 6. wait_all
    await manager.wait_all()
    print("  ✓ wait_all: completed")
    
    print("\n  All BackgroundTaskManager methods work! ✓")
    
    return manager


async def example_4_multiple_tasks():
    """Example 4: Managing multiple tasks."""
    print("\n=== Example 4: Multiple Tasks ===")
    
    manager = create_queued_task_manager()
    
    # Schedule multiple tasks
    print("  Scheduling multiple tasks...")
    task_ids = []
    
    for i in range(5):
        task_id = await manager.schedule_task(
            task_type=f"task_type_{i % 2}",  # Alternate between two types
            payload={"task_num": i},
            priority=100 - (i * 10)  # Varying priorities
        )
        task_ids.append(task_id)
        print(f"    Task {i+1}: ID={task_id}, priority={100 - (i * 10)}")
    
    # Check all task statuses
    print("\n  Checking task statuses...")
    for task_id in task_ids:
        status = await manager.get_task_status(task_id)
        print(f"    Task {task_id}: {status['status']}")
    
    print(f"\n  Total active tasks: {manager.get_active_task_count()}")
    
    return manager


async def example_5_migration_pattern():
    """Example 5: Migration pattern - old code to new."""
    print("\n=== Example 5: Migration Pattern ===")
    
    print("  Before: BackgroundTaskManager")
    print("  ----------------------------------------")
    print("  from src.core.task_manager import BackgroundTaskManager")
    print("  manager = BackgroundTaskManager(registry)")
    print("  manager.start_task(run, coro)")
    
    print("\n  After: QueuedTaskManager (same API!)")
    print("  ----------------------------------------")
    print("  from src.queue.integration import create_queued_task_manager")
    print("  manager = create_queued_task_manager()")
    print("  manager.start_task(run, coro)  # Same API!")
    
    # Demonstrate actual migration
    manager = create_queued_task_manager()
    
    run = Run(
        run_id="migration-test",
        module_id="test",
        module_name="Migration Test",
        status=RunStatus.QUEUED,
        created_at=datetime.now(timezone.utc),
        parameters={}
    )
    manager.registry.add_run(run)
    
    async def test_task():
        return "migrated!"
    
    task_id = manager.start_task(run, test_task())
    
    print(f"\n  ✓ Migration successful! Task ID: {task_id}")
    print("  ✓ No code changes needed - just swap the import!")
    
    return manager


async def main():
    """Run all examples."""
    print("=" * 60)
    print("QueuedTaskManager Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await example_1_basic_usage()
        await example_2_enhanced_features()
        await example_3_backward_compatibility()
        await example_4_multiple_tasks()
        await example_5_migration_pattern()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully! ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
