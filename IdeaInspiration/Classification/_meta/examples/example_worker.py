#!/usr/bin/env python3
"""
Example: Using Classification Worker with TaskManager API

This example demonstrates how to use the classification worker
with the TaskManager API for distributed classification processing.
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Source' / 'TaskManager'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import TaskManager client
try:
    from TaskManager import TaskManagerClient
    HAS_TASKMANAGER = True
except ImportError:
    HAS_TASKMANAGER = False
    print("Note: TaskManager not available. Skipping API examples.")

from workers.classification_worker import ClassificationWorker
from workers import Task, TaskStatus


def example_create_classification_task():
    """Example: Create a classification task via TaskManager API."""
    if not HAS_TASKMANAGER:
        print("\nSkipping: TaskManager not available")
        return None
    
    print("\n=== Example: Create Classification Task ===\n")
    
    client = TaskManagerClient()
    
    # Get or register task type
    try:
        task_type = client.get_task_type("PrismQ.Classification.ContentEnrich")
        task_type_id = task_type['id']
        print(f"Task type exists with ID: {task_type_id}")
    except:
        # Register if doesn't exist
        result = client.register_task_type(
            name="PrismQ.Classification.ContentEnrich",
            version="1.0.0",
            param_schema={
                "type": "object",
                "properties": {
                    "idea_data": {"type": "object"},
                    "save_to_db": {"type": "boolean", "default": True}
                }
            }
        )
        task_type_id = result['id']
        print(f"Task type registered with ID: {task_type_id}")
    
    # Create a task
    task = client.create_task(
        task_type_id=task_type_id,
        params={
            "idea_data": {
                "title": "Amazing startup story",
                "description": "A founder shares their journey building a successful startup",
                "content": "This is a narrative about overcoming challenges...",
                "keywords": ["startup", "entrepreneurship", "story"],
                "source_type": "text",
                "source_platform": "reddit"
            },
            "save_to_db": False
        },
        priority=1
    )
    
    print(f"Created task {task['id']}")
    print(f"Task status: {task['status']}")
    return task['id']


def example_process_task_directly():
    """Example: Process a classification task directly with worker."""
    print("\n=== Example: Direct Task Processing ===\n")
    
    # Create worker
    worker = ClassificationWorker(
        worker_id="example-worker-001",
        idea_db_path=":memory:"  # Use in-memory database for example
    )
    
    # Create a test task
    task = Task(
        id=1,
        task_type="classification_enrich",
        params={
            "idea_data": {
                "title": "Top 10 startup mistakes to avoid",
                "description": "Learn from common entrepreneurial pitfalls",
                "content": "Starting a business is challenging. Here are the top mistakes...",
                "keywords": ["startup", "business", "education"],
                "source_type": "text",
                "source_platform": "medium"
            },
            "save_to_db": False
        },
        status=TaskStatus.CLAIMED
    )
    
    # Process the task
    result = worker.process_task(task)
    
    if result.success:
        print("✓ Task processed successfully!")
        print(f"  Category: {result.data['category']}")
        print(f"  Confidence: {result.data['category_confidence']:.2%}")
        print(f"  Flags: {result.data['flags']}")
        print(f"  Tags: {result.data['tags']}")
    else:
        print(f"✗ Task failed: {result.error}")
    
    print(f"\nWorker statistics:")
    print(f"  Tasks processed: {worker.tasks_processed}")
    print(f"  Tasks failed: {worker.tasks_failed}")


def example_batch_classification():
    """Example: Batch classification of multiple items."""
    print("\n=== Example: Batch Classification ===\n")
    
    worker = ClassificationWorker(
        worker_id="example-worker-002",
        idea_db_path=":memory:"
    )
    
    # Create batch task
    task = Task(
        id=2,
        task_type="classification_batch",
        params={
            "idea_inspiration_ids": ["123", "456", "789"],
            "save_to_db": False
        },
        status=TaskStatus.CLAIMED
    )
    
    # Note: This would normally fetch from database
    # For this example, it will show how the batch processing works
    result = worker.process_task(task)
    
    if result.success:
        print("✓ Batch processing completed!")
        print(f"  Total: {result.data['total']}")
        print(f"  Successful: {result.data['successful']}")
        print(f"  Failed: {result.data['failed']}")
    else:
        print(f"✗ Batch failed: {result.error}")


def example_worker_with_different_policies():
    """Example: Worker with different claiming policies."""
    print("\n=== Example: Claiming Policies ===\n")
    
    policies = ["FIFO", "LIFO", "PRIORITY"]
    
    for policy in policies:
        print(f"\nPolicy: {policy}")
        print(f"  Sort: ", end="")
        
        if policy == "FIFO":
            print("created_at ASC (oldest first)")
        elif policy == "LIFO":
            print("created_at DESC (newest first)")
        elif policy == "PRIORITY":
            print("priority DESC (highest priority first)")
        
        print(f"  Use case: ", end="")
        
        if policy == "FIFO":
            print("Fair processing order")
        elif policy == "LIFO":
            print("Time-sensitive content")
        elif policy == "PRIORITY":
            print("Importance-based processing")


def main():
    """Run all examples."""
    print("=" * 80)
    print("Classification Worker Examples")
    print("=" * 80)
    
    # Example 1: Direct task processing
    example_process_task_directly()
    
    # Example 2: Batch classification
    example_batch_classification()
    
    # Example 3: Claiming policies
    example_worker_with_different_policies()
    
    # Example 4: Create task via API (commented out - requires API access)
    print("\n=== Example: Create Task via API ===\n")
    print("To create tasks via TaskManager API:")
    print("  1. Set TASKMANAGER_API_URL and TASKMANAGER_API_KEY in environment")
    print("  2. Run: python scripts/register_task_types.py")
    print("  3. Use client.create_task() as shown in example_create_classification_task()")
    print("\nSee src/workers/README.md for complete documentation.")
    
    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
