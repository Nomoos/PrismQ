#!/usr/bin/env python3
"""Run the scoring worker.

This script starts a scoring worker that processes scoring tasks from:
1. Local SQLite queue database
2. TaskManager API (if configured)

Usage:
    python scripts/run_worker.py [options]
    
Options:
    --worker-id WORKER_ID       Unique worker identifier
    --strategy STRATEGY         Task claiming strategy (FIFO, LIFO, PRIORITY)
    --poll-interval SECONDS     Polling interval in seconds (default: 5)
    --max-backoff SECONDS       Maximum backoff time in seconds (default: 60)
    --queue-db PATH            Path to queue database
    --no-taskmanager           Disable TaskManager API integration
    --max-iterations N         Maximum iterations (for testing)
"""

import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir.parent))  # For ConfigLoad
sys.path.insert(0, str(parent_dir))  # For src

from ConfigLoad import Config, get_module_logger
from src.workers.factory import WorkerFactory

# Configure logging
logger = get_module_logger(
    module_name="PrismQ.IdeaInspiration.Scoring.Worker",
    module_version="1.0.0",
    module_path=str(Path(__file__).parent.parent),
    log_startup=True
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run PrismQ Scoring Worker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--worker-id',
        type=str,
        help='Unique worker identifier (auto-generated if not provided)'
    )
    
    parser.add_argument(
        '--strategy',
        type=str,
        choices=['FIFO', 'LIFO', 'PRIORITY'],
        default='FIFO',
        help='Task claiming strategy'
    )
    
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=5,
        help='Base polling interval in seconds'
    )
    
    parser.add_argument(
        '--max-backoff',
        type=int,
        default=60,
        help='Maximum backoff time in seconds'
    )
    

    
    parser.add_argument(
        '--max-iterations',
        type=int,
        help='Maximum iterations (for testing, default: infinite)'
    )
    
    parser.add_argument(
        '--no-autoscore',
        action='store_true',
        help='Disable automatic scoring of unscored IdeaInspiration items'
    )
    
    parser.add_argument(
        '--autoscore-db',
        type=str,
        help='Path to IdeaInspiration database (default: auto-detect)'
    )
    
    parser.add_argument(
        '--autoscore-batch-size',
        type=int,
        default=10,
        help='Number of unscored items to fetch at once'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for scoring worker."""
    args = parse_args()
    
    logger.info("=" * 80)
    logger.info("PrismQ Scoring Worker - Starting")
    logger.info("=" * 80)
    logger.info(f"Worker ID: {args.worker_id or 'auto-generated'}")
    logger.info(f"Claiming Policy: {args.strategy}")
    logger.info(f"Poll Interval: {args.poll_interval}s")
    logger.info(f"Max Backoff: {args.max_backoff}s")
    logger.info(f"Task Coordination: TaskManager API (external service)")
    logger.info(f"Auto-Score: {'disabled' if args.no_autoscore else 'enabled'}")
    
    if not args.no_autoscore:
        if args.autoscore_db:
            logger.info(f"Auto-Score DB: {args.autoscore_db}")
        logger.info(f"Auto-Score Batch Size: {args.autoscore_batch_size}")
    
    if args.max_iterations:
        logger.info(f"Max Iterations: {args.max_iterations}")
    
    logger.info("=" * 80)
    
    try:
        # Create worker using factory
        worker = WorkerFactory.create_scoring_worker(
            worker_id=args.worker_id,
            claiming_policy=args.strategy,
            poll_interval=args.poll_interval,
            max_backoff=args.max_backoff,
            enable_autoscore=not args.no_autoscore,
            autoscore_db_path=args.autoscore_db,
            autoscore_batch_size=args.autoscore_batch_size,
        )
        
        # Run worker
        logger.info("Worker initialized successfully - starting main loop...")
        worker.run(max_iterations=args.max_iterations)
        
    except KeyboardInterrupt:
        logger.info("Shutdown signal received - stopping worker...")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("Worker stopped gracefully")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
