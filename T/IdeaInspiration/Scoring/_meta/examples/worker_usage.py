#!/usr/bin/env python3
"""Example: Using the Scoring Worker.

This example demonstrates:
1. Creating a scoring worker
2. Adding tasks to the queue
3. Running the worker to process tasks
4. Checking results
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import time

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir.parent))  # For ConfigLoad
sys.path.insert(0, str(parent_dir))  # For src

from src.workers.factory import WorkerFactory

# Use temporary database for example
QUEUE_DB = "/tmp/scoring_worker_example.db"


def add_sample_tasks():
    """Add sample tasks to the queue."""
    print("Adding sample tasks to queue...")
    
    conn = sqlite3.connect(QUEUE_DB)
    now = datetime.now(timezone.utc).isoformat()
    
    # Task 1: Text Scoring
    conn.execute("""
        INSERT INTO task_queue 
        (task_type, parameters, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "PrismQ.Scoring.TextScoring",
        json.dumps({
            "title": "Introduction to Machine Learning",
            "description": "A comprehensive guide to ML basics",
            "text_content": """
            Machine learning is a subset of artificial intelligence that enables 
            systems to learn and improve from experience. This guide covers fundamental
            concepts including supervised learning, unsupervised learning, and 
            reinforcement learning. You'll discover how to apply these techniques to 
            real-world problems and build intelligent applications.
            """
        }),
        0,
        "queued",
        now,
        now
    ))
    
    # Task 2: Engagement Scoring
    conn.execute("""
        INSERT INTO task_queue 
        (task_type, parameters, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "PrismQ.Scoring.EngagementScoring",
        json.dumps({
            "views": 1000000,
            "likes": 50000,
            "comments": 1000,
            "shares": 5000,
            "platform": "youtube"
        }),
        1,  # Higher priority
        "queued",
        now,
        now
    ))
    
    # Task 3: Batch Scoring
    conn.execute("""
        INSERT INTO task_queue 
        (task_type, parameters, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "PrismQ.Scoring.BatchScoring",
        json.dumps({
            "items": [
                {
                    "title": "Python Tutorial Part 1",
                    "description": "Learn Python basics",
                    "text_content": "Python is a high-level programming language..."
                },
                {
                    "title": "Python Tutorial Part 2",
                    "description": "Advanced Python concepts",
                    "text_content": "In this tutorial, we explore advanced Python..."
                }
            ]
        }),
        0,
        "queued",
        now,
        now
    ))
    
    conn.commit()
    conn.close()
    
    print("✓ Added 3 sample tasks")


def check_results():
    """Check and display task results."""
    print("\nChecking results...")
    
    conn = sqlite3.connect(QUEUE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get completed tasks
    cursor.execute("""
        SELECT id, task_type, status, result_data, error_message
        FROM task_queue
        WHERE status IN ('completed', 'failed')
        ORDER BY id
    """)
    
    tasks = cursor.fetchall()
    
    print(f"\nProcessed {len(tasks)} tasks:")
    print("-" * 80)
    
    for task in tasks:
        print(f"\nTask #{task['id']} - {task['task_type']}")
        print(f"Status: {task['status']}")
        
        if task['status'] == 'completed' and task['result_data']:
            result = json.loads(task['result_data'])
            
            # Display key results
            if 'overall_score' in result:
                print(f"Overall Score: {result['overall_score']:.2f}")
            
            if 'engagement_score' in result:
                print(f"Engagement Score: {result['engagement_score']:.2f}")
            
            if 'results' in result:
                print(f"Batch Results: {result['successful']}/{result['total_items']} successful")
        
        elif task['status'] == 'failed':
            print(f"Error: {task['error_message']}")
    
    print("-" * 80)
    
    conn.close()


def main():
    """Main example execution."""
    print("=" * 80)
    print("Scoring Worker Example")
    print("=" * 80)
    
    # Step 1: Add sample tasks
    add_sample_tasks()
    
    # Step 2: Create and configure worker
    print("\nCreating worker...")
    worker = WorkerFactory.create_scoring_worker(
        worker_id="example-worker",
        queue_db_path=QUEUE_DB,
        strategy="PRIORITY",  # Process high-priority tasks first
        poll_interval=1,  # Poll frequently for demo
        enable_taskmanager=False  # Local queue only for example
    )
    print("✓ Worker created")
    
    # Step 3: Run worker for limited iterations
    print("\nStarting worker (processing 3 tasks)...")
    print("-" * 80)
    
    # Run worker with max iterations
    worker.run(max_iterations=10)  # Will stop after processing all tasks
    
    print("-" * 80)
    print("✓ Worker stopped")
    
    # Step 4: Check results
    check_results()
    
    print("\n" + "=" * 80)
    print("Example completed!")
    print(f"Queue database: {QUEUE_DB}")
    print("=" * 80)


if __name__ == "__main__":
    main()
