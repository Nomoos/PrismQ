#!/usr/bin/env python3
"""
PrismQ TaskManager Worker - Python Example

A production-ready Python worker implementation that demonstrates how to integrate
with the TaskManager API for distributed task processing.

This example shows:
- Task claiming from TaskManager API using task type IDs
- Extensible task processing handlers
- Task completion and error handling
- Graceful shutdown handling
- Comprehensive logging

Usage:
    python worker.py [options]

Options:
    --api-url URL          TaskManager API base URL (default: http://localhost:8000/api)
    --worker-id ID         Worker identifier (default: auto-generated)
    --task-type-ids IDS    Comma-separated task type IDs to process (default: all active types)
    --poll-interval SEC    Seconds to wait between polls (default: 10)
    --max-runs NUM         Maximum tasks to process (default: unlimited)
    --debug                Enable debug logging

Examples:
    # Run with default settings (processes all active task types)
    python worker.py

    # Run with custom API URL
    python worker.py --api-url=https://api.example.com/api

    # Process only specific task type IDs
    python worker.py --task-type-ids="1,2,3"

    # Process 10 tasks then exit
    python worker.py --max-runs=10
"""

import argparse
import json
import logging
import signal
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Install it with: pip install requests")
    sys.exit(1)


class TaskManagerWorker:
    """Worker for processing tasks from TaskManager API."""

    def __init__(
        self,
        api_url: str,
        worker_id: str,
        task_type_ids: Optional[List[int]] = None,
        poll_interval: int = 10,
        max_runs: int = 0,
        debug: bool = False
    ):
        self.api_url = api_url.rstrip('/')
        self.worker_id = worker_id
        self.task_type_ids = task_type_ids  # List of task type IDs to claim
        self.poll_interval = poll_interval
        self.max_runs = max_runs
        self.debug = debug
        
        # Worker state
        self.should_stop = False
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # Task type ID cache
        self._task_type_cache = {}
        
        # Setup logging
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        signal_name = 'SIGTERM' if signum == signal.SIGTERM else 'SIGINT'
        self.logger.info(f"Received {signal_name}, finishing current task and exiting...")
        self.should_stop = True
        
    def health_check(self) -> bool:
        """Verify API connectivity."""
        try:
            response = requests.get(
                urljoin(self.api_url, '/health'),
                timeout=5
            )
            if response.status_code == 200:
                self.logger.info("✓ API health check passed")
                return True
            else:
                self.logger.error(f"✗ API health check failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"✗ API health check failed: {e}")
            return False
            
    def get_task_type_id(self, task_type_name: str) -> Optional[int]:
        """Get task type ID from task type name."""
        # Check cache first
        if task_type_name in self._task_type_cache:
            return self._task_type_cache[task_type_name]
        
        try:
            response = requests.get(
                urljoin(self.api_url, f'/task-types/{task_type_name}'),
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    task_type_id = data['data']['id']
                    self._task_type_cache[task_type_name] = task_type_id
                    return task_type_id
            
            self.logger.warning(f"Task type '{task_type_name}' not found")
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching task type ID: {e}")
            return None
    
    def list_task_types(self) -> List[Dict[str, Any]]:
        """Get list of all active task types."""
        try:
            response = requests.get(
                urljoin(self.api_url, '/task-types'),
                params={'active_only': 'true'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data['data']['task_types']
            
            return []
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error listing task types: {e}")
            return []
            
    def claim_task(self) -> Optional[Dict[str, Any]]:
        """Claim a task from the queue."""
        # If no task type IDs specified, get all active task types
        task_type_ids = self.task_type_ids
        if not task_type_ids:
            # Get all active task types
            task_types = self.list_task_types()
            if task_types:
                task_type_ids = [tt['id'] for tt in task_types]
            else:
                self.logger.warning("No active task types found")
                return None
        
        # Try to claim a task from each task type
        for task_type_id in task_type_ids:
            try:
                payload = {
                    'worker_id': self.worker_id,
                    'task_type_id': task_type_id
                }
                
                response = requests.post(
                    urljoin(self.api_url, '/tasks/claim'),
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        task = data['data']
                        self.logger.info(f"✓ Claimed task {task['id']} (type: {task['type']})")
                        self.consecutive_errors = 0
                        return task
                elif response.status_code == 404:
                    # No tasks available for this type, try next
                    continue
                else:
                    self.logger.warning(f"Failed to claim task for type {task_type_id}: HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error claiming task for type {task_type_id}: {e}")
                self.consecutive_errors += 1
        
        # No tasks available from any type
        self.logger.debug("No tasks available from any task type")
        return None
            
    def update_progress(self, task_id: str, progress: int, message: Optional[str] = None) -> bool:
        """Update task progress."""
        # Validate progress range
        if not 0 <= progress <= 100:
            self.logger.error(f"Invalid progress value: {progress}. Must be between 0 and 100.")
            return False
            
        try:
            payload = {
                'worker_id': self.worker_id,
                'progress': progress
            }
            if message:
                payload['message'] = message
            
            response = requests.post(
                urljoin(self.api_url, f'/tasks/{task_id}/progress'),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"✓ Task {task_id} progress: {progress}%")
                return True
            else:
                self.logger.warning(f"Failed to update progress: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error updating progress: {e}")
            return False
            
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark a task as completed."""
        try:
            payload = {
                'worker_id': self.worker_id,
                'success': True,
                'result': result.get('data', {})
            }
            
            response = requests.post(
                urljoin(self.api_url, f'/tasks/{task_id}/complete'),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"✓ Task {task_id} completed")
                return True
            else:
                self.logger.error(f"Failed to complete task: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error completing task: {e}")
            return False
            
    def fail_task(self, task_id: str, error_message: str) -> bool:
        """Mark a task as failed."""
        try:
            payload = {
                'worker_id': self.worker_id,
                'success': False,
                'error': error_message
            }
            
            response = requests.post(
                urljoin(self.api_url, f'/tasks/{task_id}/complete'),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"✓ Task {task_id} marked as failed")
                return True
            else:
                self.logger.error(f"Failed to mark task as failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error marking task as failed: {e}")
            return False
            
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task based on its type.
        
        Override this method or add handlers for your specific task types.
        """
        task_type = task.get('type', 'unknown')
        params = task.get('params', {})
        
        self.logger.info(f"Processing task type: {task_type}")
        
        # Route to specific handler based on task type
        if task_type == 'example.echo':
            return self._handle_echo(params)
        elif task_type == 'example.uppercase':
            return self._handle_uppercase(params)
        elif task_type == 'example.math.add':
            return self._handle_math_add(params)
        elif task_type == 'example.sleep':
            return self._handle_sleep(params)
        elif task_type == 'example.error':
            return self._handle_error(params)
        else:
            return {
                'success': False,
                'message': f'Unknown task type: {task_type}'
            }
    
    # Example task handlers
    def _handle_echo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Echo back a message."""
        message = params.get('message', '')
        self.logger.debug(f"Echo: {message}")
        return {
            'success': True,
            'data': {
                'echo': message,
                'length': len(message)
            },
            'message': 'Message echoed successfully'
        }
    
    def _handle_uppercase(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert text to uppercase."""
        text = params.get('text', '')
        result = text.upper()
        self.logger.debug(f"Uppercase: {text} -> {result}")
        return {
            'success': True,
            'data': {
                'original': text,
                'uppercase': result
            },
            'message': 'Text converted to uppercase'
        }
    
    def _handle_math_add(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add two numbers."""
        try:
            a = float(params.get('a', 0))
            b = float(params.get('b', 0))
            result = a + b
            self.logger.debug(f"Math: {a} + {b} = {result}")
            return {
                'success': True,
                'data': {
                    'a': a,
                    'b': b,
                    'result': result
                },
                'message': 'Numbers added successfully'
            }
        except (ValueError, TypeError) as e:
            return {
                'success': False,
                'message': f'Invalid parameters: {e}'
            }
    
    def _handle_sleep(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate long-running task with progress updates."""
        duration = min(params.get('duration', 2), 30)  # Max 30 seconds
        self.logger.debug(f"Sleeping for {duration} seconds with progress updates")
        
        # Simulate progress updates during long-running task
        steps = min(duration, 10)  # Update progress at most 10 times
        step_duration = duration / steps if steps > 0 else duration
        
        for i in range(1, steps + 1):
            time.sleep(step_duration)
            
            # Update progress
            progress = int((i / steps) * 100)
            # Note: task_id would need to be passed to handlers for this to work
            # For now, just log the progress
            self.logger.info(f"Progress: {progress}% (step {i}/{steps})")
            
        return {
            'success': True,
            'data': {
                'duration': duration
            },
            'message': f'Slept for {duration} seconds'
        }
    
    def _handle_error(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate error for testing."""
        error_message = params.get('message', 'Simulated error')
        self.logger.debug(f"Simulating error: {error_message}")
        return {
            'success': False,
            'message': error_message
        }
    
    def run(self):
        """Main worker loop."""
        self.logger.info("=" * 60)
        self.logger.info("PrismQ TaskManager Worker (Python)")
        self.logger.info("=" * 60)
        self.logger.info(f"Worker ID:      {self.worker_id}")
        self.logger.info(f"API URL:        {self.api_url}")
        
        if self.task_type_ids:
            self.logger.info(f"Task Type IDs:  {', '.join(map(str, self.task_type_ids))}")
        else:
            self.logger.info(f"Task Type IDs:  all active types")
            
        self.logger.info(f"Poll Interval:  {self.poll_interval}s")
        self.logger.info(f"Max Runs:       {self.max_runs if self.max_runs > 0 else 'unlimited'}")
        self.logger.info(f"Debug Mode:     {self.debug}")
        self.logger.info("=" * 60)
        
        # Health check
        if not self.health_check():
            self.logger.error("Failed to connect to API. Exiting.")
            sys.exit(1)
        
        self.logger.info("Worker started. Waiting for tasks...")
        
        while not self.should_stop:
            # Check if max runs reached
            if self.max_runs > 0 and self.tasks_processed >= self.max_runs:
                self.logger.info(f"Max runs ({self.max_runs}) reached. Exiting.")
                break
            
            # Check consecutive errors
            if self.consecutive_errors >= self.max_consecutive_errors:
                self.logger.error(
                    f"Too many consecutive errors ({self.consecutive_errors}). Exiting."
                )
                break
            
            # Claim a task
            task = self.claim_task()
            
            if task:
                try:
                    # Process the task
                    result = self.process_task(task)
                    
                    # Report result
                    if result.get('success', False):
                        self.complete_task(task['id'], result)
                        self.tasks_processed += 1
                    else:
                        self.fail_task(task['id'], result.get('message', 'Task failed'))
                        self.tasks_failed += 1
                        
                except Exception as e:
                    self.logger.error(f"Error processing task: {e}", exc_info=True)
                    self.fail_task(task['id'], f"Exception: {str(e)}")
                    self.tasks_failed += 1
                    self.consecutive_errors += 1
            else:
                # No tasks available, wait before polling again
                time.sleep(self.poll_interval)
        
        # Print summary
        self.logger.info("=" * 60)
        self.logger.info("Worker stopped")
        self.logger.info(f"Tasks processed: {self.tasks_processed}")
        self.logger.info(f"Tasks failed:    {self.tasks_failed}")
        self.logger.info("=" * 60)


def main():
    """Parse arguments and start worker."""
    parser = argparse.ArgumentParser(
        description='PrismQ TaskManager Worker (Python)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (processes all task types)
  python worker.py

  # Run with custom API URL
  python worker.py --api-url=https://api.example.com/api

  # Process only specific task type IDs
  python worker.py --task-type-ids="1,2,3"

  # Process 10 tasks then exit
  python worker.py --max-runs=10
        """
    )
    
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000/api',
        help='TaskManager API base URL (default: http://localhost:8000/api)'
    )
    
    parser.add_argument(
        '--worker-id',
        default=f'python-worker-{uuid.uuid4().hex[:8]}',
        help='Worker identifier (default: auto-generated)'
    )
    
    parser.add_argument(
        '--task-type-ids',
        help='Comma-separated task type IDs to process (default: all active types)'
    )
    
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=10,
        help='Seconds to wait between polls when no tasks (default: 10)'
    )
    
    parser.add_argument(
        '--max-runs',
        type=int,
        default=0,
        help='Maximum number of tasks to process (default: unlimited)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Parse task type IDs
    task_type_ids = None
    if args.task_type_ids:
        task_type_ids = [int(tid.strip()) for tid in args.task_type_ids.split(',')]
    
    # Create and run worker
    worker = TaskManagerWorker(
        api_url=args.api_url,
        worker_id=args.worker_id,
        task_type_ids=task_type_ids,
        poll_interval=args.poll_interval,
        max_runs=args.max_runs,
        debug=args.debug
    )
    
    try:
        worker.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)


if __name__ == '__main__':
    main()
