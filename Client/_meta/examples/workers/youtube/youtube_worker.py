#!/usr/bin/env python3
"""
YouTube Shorts Scraper Worker Example

A complete worker implementation example for the
PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTube repository
demonstrating how to integrate with the TaskManager API for distributed task processing.

This example shows:
- Task claiming from TaskManager API
- Mock YouTube shorts scraping functionality
- Task completion and error handling
- Graceful shutdown handling
- Comprehensive logging

Usage:
    python youtube_worker.py [options]

Options:
    --api-url URL          TaskManager API base URL (default: http://localhost:8000/api)
    --worker-id ID         Worker identifier (default: auto-generated)
    --poll-interval SEC    Seconds to wait between polls (default: 10)
    --max-runs NUM         Maximum tasks to process (default: unlimited)
    --debug                Enable debug logging

Examples:
    # Run with default settings
    python youtube_worker.py

    # Run with custom API URL
    python youtube_worker.py --api-url=https://api.example.com/api

    # Process 10 tasks then exit
    python youtube_worker.py --max-runs=10
"""

import argparse
import json
import logging
import signal
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Install it with: pip install requests")
    sys.exit(1)


class YouTubeWorker:
    """Worker for processing YouTube shorts scraping tasks."""

    def __init__(
        self,
        api_url: str,
        worker_id: str,
        poll_interval: int = 10,
        max_runs: int = 0,
        debug: bool = False
    ):
        self.api_url = api_url.rstrip('/')
        self.worker_id = worker_id
        self.poll_interval = poll_interval
        self.max_runs = max_runs
        self.debug = debug
        
        # Worker state
        self.should_stop = False
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
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
            
    def claim_task(self) -> Optional[Dict[str, Any]]:
        """Claim a task from the queue."""
        try:
            response = requests.post(
                urljoin(self.api_url, '/tasks/claim'),
                json={
                    'worker_id': self.worker_id,
                    'task_types': ['PrismQ.YouTube.ScrapeShorts']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                task = response.json()
                if task:
                    self.logger.info(f"✓ Claimed task {task['id']} (type: {task['type']})")
                    self.consecutive_errors = 0
                    return task
                else:
                    self.logger.debug("No tasks available")
                    return None
            elif response.status_code == 404:
                self.logger.debug("No tasks available")
                return None
            else:
                self.logger.warning(f"Failed to claim task: HTTP {response.status_code}")
                self.consecutive_errors += 1
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error claiming task: {e}")
            self.consecutive_errors += 1
            return None
            
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark a task as completed."""
        try:
            response = requests.post(
                urljoin(self.api_url, f'/tasks/{task_id}/complete'),
                json={
                    'worker_id': self.worker_id,
                    'result': result
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"✓ Task {task_id} completed successfully")
                return True
            else:
                self.logger.error(f"Failed to complete task {task_id}: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error completing task {task_id}: {e}")
            return False
            
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed."""
        try:
            response = requests.post(
                urljoin(self.api_url, f'/tasks/{task_id}/fail'),
                json={
                    'worker_id': self.worker_id,
                    'error': error
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"✓ Task {task_id} marked as failed")
                return True
            else:
                self.logger.error(f"Failed to mark task {task_id} as failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error failing task {task_id}: {e}")
            return False
            
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a YouTube shorts scraping task.
        
        This is a MOCK implementation that simulates scraping without actual API calls.
        In a real implementation, this would:
        1. Connect to YouTube API or use web scraping
        2. Search for shorts videos based on parameters
        3. Extract video metadata (title, description, views, etc.)
        4. Download video thumbnails/content if needed
        5. Store results in database or return to TaskManager
        
        Args:
            task: Task dictionary with 'id', 'type', and 'params'
            
        Returns:
            Dictionary with processing results
        """
        task_id = task['id']
        task_type = task['type']
        params = task.get('params', {})
        
        self.logger.info(f"Processing task {task_id} with params: {json.dumps(params)}")
        
        # Extract parameters
        search_query = params.get('search_query', 'inspiration')
        max_results = params.get('max_results', 10)
        language = params.get('language', 'en')
        
        # Simulate processing time
        self.logger.debug("Simulating YouTube API call...")
        time.sleep(2)  # Simulate API call delay
        
        # Mock results - in real implementation, this would be actual scraped data
        # Note: Limited to 5 results for mock demonstration purposes
        MOCK_RESULT_LIMIT = 5
        mock_results = {
            'shorts': [
                {
                    'video_id': f'mock_video_{i}',
                    'title': f'Inspiring Short #{i}: {search_query}',
                    'description': f'A mock short video about {search_query}',
                    'duration': 45 + i,
                    'views': 10000 * (i + 1),
                    'likes': 500 * (i + 1),
                    'channel': f'Creator {i}',
                    'published_at': datetime.now().isoformat(),
                    'thumbnail_url': f'https://example.com/thumbnail_{i}.jpg',
                    'video_url': f'https://youtube.com/shorts/mock_video_{i}'
                }
                for i in range(1, min(max_results, MOCK_RESULT_LIMIT) + 1)
            ],
            'total_found': min(max_results, MOCK_RESULT_LIMIT),
            'search_query': search_query,
            'language': language,
            'scraped_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"✓ Successfully scraped {len(mock_results['shorts'])} shorts")
        
        return {
            'success': True,
            'data': mock_results,
            'message': f'Successfully scraped {len(mock_results["shorts"])} YouTube shorts'
        }
        
    def run(self):
        """Main worker loop."""
        self.logger.info("=" * 50)
        self.logger.info("YouTube Shorts Scraper Worker")
        self.logger.info("=" * 50)
        self.logger.info(f"Worker ID:      {self.worker_id}")
        self.logger.info(f"API URL:        {self.api_url}")
        self.logger.info(f"Poll Interval:  {self.poll_interval}s")
        self.logger.info(f"Max Runs:       {self.max_runs if self.max_runs > 0 else 'unlimited'}")
        self.logger.info("=" * 50)
        
        # Health check
        if not self.health_check():
            self.logger.error("API health check failed. Exiting.")
            return 1
            
        self.logger.info("Worker started. Waiting for tasks...")
        
        # Main processing loop
        while not self.should_stop:
            # Check if we've hit max runs
            if self.max_runs > 0 and self.tasks_processed >= self.max_runs:
                self.logger.info(f"Reached max runs ({self.max_runs}). Exiting.")
                break
                
            # Check consecutive errors
            if self.consecutive_errors >= self.max_consecutive_errors:
                self.logger.error(
                    f"Too many consecutive errors ({self.consecutive_errors}). Exiting."
                )
                break
                
            # Try to claim a task
            task = self.claim_task()
            
            if task is None:
                # No task available, wait before trying again
                self.logger.debug(f"No tasks available. Waiting {self.poll_interval}s...")
                time.sleep(self.poll_interval)
                continue
                
            # Process the task
            try:
                result = self.process_task(task)
                
                if result.get('success'):
                    # Task completed successfully
                    if self.complete_task(task['id'], result):
                        self.tasks_processed += 1
                    else:
                        self.tasks_failed += 1
                else:
                    # Task processing failed
                    error_message = result.get('message', 'Unknown error')
                    self.logger.error(f"Task processing failed: {error_message}")
                    if self.fail_task(task['id'], error_message):
                        self.tasks_failed += 1
                        
            except Exception as e:
                # Unexpected error during processing
                self.logger.error(f"Unexpected error processing task: {e}", exc_info=True)
                error_message = f"Unexpected error: {str(e)}"
                self.fail_task(task['id'], error_message)
                self.tasks_failed += 1
                self.consecutive_errors += 1
                
        # Shutdown
        self.logger.info("=" * 50)
        self.logger.info("Worker shutting down")
        self.logger.info(f"Tasks processed: {self.tasks_processed}")
        self.logger.info(f"Tasks failed:    {self.tasks_failed}")
        self.logger.info("=" * 50)
        
        return 0 if self.tasks_failed == 0 else 1


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='YouTube Shorts Scraper Worker for TaskManager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python youtube_worker.py

  # Run with custom API URL
  python youtube_worker.py --api-url=https://api.example.com/api

  # Process 10 tasks then exit
  python youtube_worker.py --max-runs=10

  # Enable debug logging
  python youtube_worker.py --debug
        """
    )
    
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000/api',
        help='TaskManager API base URL (default: http://localhost:8000/api)'
    )
    
    parser.add_argument(
        '--worker-id',
        default=f'youtube-worker-{uuid.uuid4().hex[:8]}',
        help='Worker identifier (default: auto-generated)'
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
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    worker = YouTubeWorker(
        api_url=args.api_url,
        worker_id=args.worker_id,
        poll_interval=args.poll_interval,
        max_runs=args.max_runs,
        debug=args.debug
    )
    
    return worker.run()


if __name__ == '__main__':
    sys.exit(main())
