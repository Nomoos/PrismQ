#!/usr/bin/env python3
"""
Test script for PrismQ TaskManager Worker

This script creates sample tasks for testing the worker implementation.
"""

import argparse
import json
import sys
import time

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Install it with: pip install requests")
    sys.exit(1)


def create_task(api_url: str, task_type: str, params: dict) -> dict:
    """Create a task in TaskManager."""
    try:
        response = requests.post(
            f"{api_url}/tasks",
            json={
                'type': task_type,
                'params': params
            },
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            task = response.json()
            print(f"✓ Created task: {task['id']} (type: {task_type})")
            return task
        else:
            print(f"✗ Failed to create task: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error creating task: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Create test tasks for worker')
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000/api',
        help='TaskManager API base URL (default: http://localhost:8000/api)'
    )
    parser.add_argument(
        '--num-tasks',
        type=int,
        default=5,
        help='Number of test tasks to create (default: 5)'
    )
    
    args = parser.parse_args()
    api_url = args.api_url.rstrip('/')
    
    print("=" * 60)
    print("Creating test tasks")
    print("=" * 60)
    print(f"API URL: {api_url}")
    print(f"Tasks to create: {args.num_tasks}")
    print("=" * 60)
    
    # Create various test tasks
    tasks = []
    
    # Echo tasks
    for i in range(args.num_tasks // 5 + 1):
        task = create_task(
            api_url,
            'example.echo',
            {'message': f'Hello from test #{i+1}'}
        )
        if task:
            tasks.append(task)
            time.sleep(0.1)
    
    # Uppercase tasks
    for i in range(args.num_tasks // 5 + 1):
        task = create_task(
            api_url,
            'example.uppercase',
            {'text': f'test message number {i+1}'}
        )
        if task:
            tasks.append(task)
            time.sleep(0.1)
    
    # Math tasks
    for i in range(args.num_tasks // 5 + 1):
        task = create_task(
            api_url,
            'example.math.add',
            {'a': i + 1, 'b': i + 2}
        )
        if task:
            tasks.append(task)
            time.sleep(0.1)
    
    # Sleep tasks
    for i in range(args.num_tasks // 5 + 1):
        task = create_task(
            api_url,
            'example.sleep',
            {'duration': 2}
        )
        if task:
            tasks.append(task)
            time.sleep(0.1)
    
    # Error task (for testing error handling)
    if args.num_tasks >= 5:
        task = create_task(
            api_url,
            'example.error',
            {'message': 'This is a test error'}
        )
        if task:
            tasks.append(task)
    
    print("=" * 60)
    print(f"Created {len(tasks)} tasks successfully")
    print("=" * 60)
    print("\nStart the worker to process these tasks:")
    print("  python worker.py")
    print("\nOr with debug logging:")
    print("  python worker.py --debug")


if __name__ == '__main__':
    main()
