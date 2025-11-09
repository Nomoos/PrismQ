#!/usr/bin/env python3
"""
Test script for YouTube Shorts Scraper Worker

This script helps verify the worker functionality by:
1. Creating test tasks in TaskManager
2. Verifying task parameters and validation
3. Monitoring task completion

Usage:
    python test_youtube_worker.py [options]

Options:
    --api-url URL    TaskManager API base URL (default: http://localhost:8000/api)
    --num-tasks N    Number of test tasks to create (default: 3)

Examples:
    # Create 3 test tasks with default settings
    python test_youtube_worker.py

    # Create 10 test tasks with custom API URL
    python test_youtube_worker.py --api-url=https://api.example.com/api --num-tasks=10
"""

import argparse
import json
import sys
import time
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Install it with: pip install requests")
    sys.exit(1)


def create_test_task(api_url: str, task_num: int) -> dict:
    """Create a test YouTube scraping task."""
    test_queries = [
        'inspiration',
        'motivation',
        'creativity',
        'productivity',
        'mindfulness'
    ]
    
    task_data = {
        'type': 'PrismQ.YouTube.ScrapeShorts',
        'params': {
            'search_query': test_queries[task_num % len(test_queries)],
            'max_results': 5 + (task_num % 10),
            'language': 'en'
        }
    }
    
    try:
        response = requests.post(
            urljoin(api_url, '/tasks'),
            json=task_data,
            timeout=10
        )
        
        if response.status_code == 201:
            task = response.json()
            print(f"✓ Created task {task['id']}: {task_data['params']['search_query']}")
            return task
        else:
            print(f"✗ Failed to create task: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error creating task: {e}")
        return None


def get_task_status(api_url: str, task_id: str) -> dict:
    """Get the status of a task."""
    try:
        response = requests.get(
            urljoin(api_url, f'/tasks/{task_id}'),
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except requests.exceptions.RequestException:
        return None


def list_pending_tasks(api_url: str) -> list:
    """List all pending tasks."""
    try:
        response = requests.get(
            urljoin(api_url, '/tasks'),
            params={'status': 'pending'},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
            
    except requests.exceptions.RequestException:
        return []


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test script for YouTube Shorts Scraper Worker'
    )
    
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000/api',
        help='TaskManager API base URL (default: http://localhost:8000/api)'
    )
    
    parser.add_argument(
        '--num-tasks',
        type=int,
        default=3,
        help='Number of test tasks to create (default: 3)'
    )
    
    args = parser.parse_args()
    api_url = args.api_url.rstrip('/')
    
    print("=" * 60)
    print("YouTube Worker Test Script")
    print("=" * 60)
    print(f"API URL:    {api_url}")
    print(f"Test tasks: {args.num_tasks}")
    print("=" * 60)
    
    # Check API health
    print("\n[1] Checking API health...")
    try:
        response = requests.get(urljoin(api_url, '/health'), timeout=5)
        if response.status_code == 200:
            print("✓ API is healthy")
        else:
            print(f"✗ API health check failed: HTTP {response.status_code}")
            return 1
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to API: {e}")
        return 1
    
    # Create test tasks
    print(f"\n[2] Creating {args.num_tasks} test tasks...")
    created_tasks = []
    for i in range(args.num_tasks):
        task = create_test_task(api_url, i)
        if task:
            created_tasks.append(task)
        time.sleep(0.5)  # Small delay between requests
    
    if not created_tasks:
        print("✗ No tasks were created successfully")
        return 1
    
    print(f"\n✓ Successfully created {len(created_tasks)} tasks")
    
    # List pending tasks
    print("\n[3] Listing pending tasks...")
    pending = list_pending_tasks(api_url)
    print(f"Total pending tasks: {len(pending)}")
    
    if pending:
        print("\nPending tasks:")
        for task in pending[:5]:  # Show first 5
            print(f"  - {task['id']}: {task['type']} (status: {task['status']})")
    
    # Instructions
    print("\n" + "=" * 60)
    print("Test tasks created successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the worker in another terminal:")
    print(f"   python youtube_worker.py --api-url={api_url}")
    print("\n2. Monitor task processing in worker logs")
    print("\n3. Check task completion status:")
    print(f"   curl {api_url}/tasks")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
