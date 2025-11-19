#!/usr/bin/env python3
"""
Example Usage - YouTube Video Worker

This script demonstrates how to use the YouTube Video Worker programmatically.
It shows various ways to create and run workers for different use cases.

Run this script to see examples of:
1. Single video scraping
2. Search-based scraping
3. Multiple workers running in parallel
4. Custom worker configuration
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 80)
print("YouTube Video Worker - Example Usage")
print("=" * 80)
print()

# Example 1: Simple Worker Creation
print("Example 1: Create a simple worker")
print("-" * 80)
print("""
from src.workers.factory import worker_factory
from src.core.config import Config
from src.core.database import Database

# Initialize
config = Config()
results_db = Database(config.database_path)

# Create worker
worker = worker_factory.create(
    task_type='youtube_video_single',
    worker_id='my-worker-001',
    queue_db_path='data/worker_queue.db',
    config=config,
    results_db=results_db
)

# Run for 10 iterations
worker.run(poll_interval=5, max_iterations=10)
""")
print()

# Example 2: Search Worker
print("Example 2: Create a search worker")
print("-" * 80)
print("""
# Create worker for search tasks
worker = worker_factory.create(
    task_type='youtube_video_search',
    worker_id='search-worker-001',
    queue_db_path='data/worker_queue.db',
    config=config,
    results_db=results_db
)

# Run continuously
worker.run(poll_interval=5)
""")
print()

# Example 3: Multiple Workers
print("Example 3: Run multiple workers in parallel")
print("-" * 80)
print("""
import threading

def run_worker(worker_id, task_type):
    worker = worker_factory.create(
        task_type=task_type,
        worker_id=worker_id,
        queue_db_path='data/worker_queue.db',
        config=config,
        results_db=results_db
    )
    worker.run(poll_interval=5, max_iterations=100)

# Start 3 workers in parallel
threads = []
for i in range(3):
    worker_id = f'worker-{i+1:03d}'
    thread = threading.Thread(
        target=run_worker,
        args=(worker_id, 'youtube_video_single')
    )
    thread.start()
    threads.append(thread)

# Wait for all to complete
for thread in threads:
    thread.join()
""")
print()

# Summary
print("=" * 80)
print("Summary of Worker Usage Patterns")
print("=" * 80)
print("""
1. Single Worker: Best for small-scale scraping (<100 videos/hour)
2. Multiple Workers: Scale horizontally for higher throughput
3. Custom Config: Adjust settings per worker for specific needs
4. TaskManager: Use for production task management
5. Monitoring: Track progress and handle errors gracefully

Next Steps:
- Review scripts/run_worker.py for production usage
- See DEPLOYMENT_GUIDE.md for deployment instructions
- Check _meta/docs/YOUTUBE_VIDEO_WORKER.md for complete guide
""")
print("=" * 80)
