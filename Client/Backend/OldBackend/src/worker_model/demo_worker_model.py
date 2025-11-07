"""
Demo: Worker.Model Usage

Demonstrates the Worker.Model separation - how workers interact with
the database using the WorkerDatabase abstraction.

Worker 10 - Issue #339: Move worker DB definition into Worker.Model
"""

import sys
from pathlib import Path

# Add Backend directory to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from src.worker_model import (
    WorkerDatabase,
    TaskHandlerRegistry,
    SchedulingStrategy,
    WorkerConfig,
)
from src.queue import Task


def demo_worker_database_creation():
    """Demonstrate WorkerDatabase creation and configuration."""
    print("\n" + "=" * 70)
    print("DEMO 1: Worker Database Creation")
    print("=" * 70)
    
    # Create worker database
    worker_db = WorkerDatabase(":memory:")
    print("\n1. Created WorkerDatabase instance")
    print("   ✓ Database initialized")
    print("   ✓ Schema created")
    
    # Create a task handler registry
    registry = TaskHandlerRegistry()
    
    def test_handler(task: Task):
        print(f"  ✓ Processing task #{task.id}: {task.type}")
    
    registry.register_handler("test_task", test_handler)
    print("\n2. Created and configured TaskHandlerRegistry")
    print("   ✓ Registered test_task handler")
    
    # Create worker with config
    config = WorkerConfig(
        worker_id="worker-01",
        capabilities={"type": "processor"},
        scheduling_strategy=SchedulingStrategy.PRIORITY,
        lease_duration_seconds=60
    )
    
    worker = worker_db.create_worker(
        worker_id="worker-01",
        config=config,
        handler_registry=registry
    )
    print("\n3. Created worker using WorkerDatabase.create_worker()")
    print(f"   ✓ Worker ID: {worker.worker_id}")
    print(f"   ✓ Strategy: {worker.scheduling_strategy}")
    print(f"   ✓ Capabilities: {config.capabilities}")
    
    # Cleanup
    worker_db.close()
    print("\n4. Database closed cleanly")


def demo_separation_of_concerns():
    """Demonstrate separation between API and Worker.Model."""
    print("\n" + "=" * 70)
    print("DEMO 2: Separation of Concerns")
    print("=" * 70)
    
    print("\n1. Architecture Layers:")
    print("   ┌─────────────────────────────────┐")
    print("   │  Frontend (Vue 3)               │")
    print("   └─────────────────────────────────┘")
    print("                 ↓ HTTP")
    print("   ┌─────────────────────────────────┐")
    print("   │  Backend.API (FastAPI)          │")
    print("   │  - REST endpoints               │")
    print("   │  - Queue management API         │")
    print("   └─────────────────────────────────┘")
    print("                 ↓ DB")
    print("   ┌─────────────────────────────────┐")
    print("   │  SQLite Database                │")
    print("   └─────────────────────────────────┘")
    print("                 ↑ DB")
    print("   ┌─────────────────────────────────┐")
    print("   │  Backend.Worker.Model           │")
    print("   │  - Worker processes             │")
    print("   │  - Task execution               │")
    print("   │  - Handler registry             │")
    print("   └─────────────────────────────────┘")
    
    print("\n2. Worker.Model Components:")
    print("   • WorkerDatabase - Worker DB interface")
    print("   • WorkerEngine - Task processing engine")
    print("   • TaskHandlerRegistry - Handler management")
    print("   • WorkerConfig - Worker configuration")
    print("   • TaskExecutor - Task lifecycle management")
    
    print("\n3. Benefits of Separation:")
    print("   ✓ API layer doesn't need worker internals")
    print("   ✓ Workers don't need API dependencies")
    print("   ✓ Independent scaling of workers")
    print("   ✓ Clear responsibility boundaries")
    print("   ✓ Easier testing and deployment")
    
    print("\n4. Usage Pattern:")
    print("   # In worker process:")
    print("   from src.worker_model import WorkerDatabase, TaskHandlerRegistry")
    print("   ")
    print("   worker_db = WorkerDatabase()")
    print("   registry = TaskHandlerRegistry()")
    print("   # ... register handlers ...")
    print("   worker = worker_db.create_worker('worker-01', registry=registry)")
    print("   worker.run_loop()")


def demo_multiple_workers():
    """Demonstrate creating multiple workers with different configs."""
    print("\n" + "=" * 70)
    print("DEMO 3: Multiple Workers")
    print("=" * 70)
    
    print("\n1. Creating workers with different strategies:")
    
    worker_db = WorkerDatabase(":memory:")
    registry = TaskHandlerRegistry()
    
    # Register a handler
    def generic_handler(task: Task):
        print(f"  Processing {task.type}")
    
    registry.register_handler("generic_task", generic_handler)
    
    # Create workers with different strategies
    configs = [
        ("worker-fifo", SchedulingStrategy.FIFO, "First-In-First-Out"),
        ("worker-lifo", SchedulingStrategy.LIFO, "Last-In-First-Out"),
        ("worker-priority", SchedulingStrategy.PRIORITY, "Priority-based"),
        ("worker-random", SchedulingStrategy.WEIGHTED_RANDOM, "Weighted Random"),
    ]
    
    workers = []
    for worker_id, strategy, description in configs:
        config = WorkerConfig(
            worker_id=worker_id,
            scheduling_strategy=strategy
        )
        worker = worker_db.create_worker(worker_id, config, registry)
        workers.append((worker_id, strategy, description))
        print(f"   ✓ {worker_id}: {description}")
    
    print(f"\n2. Created {len(workers)} workers with different strategies")
    print("   Each worker can run independently")
    print("   Each uses the same task handler registry")
    
    worker_db.close()
    print("\n3. All workers share the same database connection pool")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("Worker.Model Demo")
    print("Worker 10 - Issue #339: Move Worker DB into Worker.Model")
    print("=" * 70)
    
    demo_worker_database_creation()
    demo_separation_of_concerns()
    demo_multiple_workers()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("• Worker.Model provides focused worker interface")
    print("• Separates worker concerns from API layer")
    print("• WorkerDatabase encapsulates worker DB operations")
    print("• Enables independent worker process deployment")
    print("• Maintains clean architecture boundaries")
    print("• Supports multiple workers with different strategies")
    print()


if __name__ == "__main__":
    main()
