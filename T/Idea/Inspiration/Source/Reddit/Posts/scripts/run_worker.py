#!/usr/bin/env python3
"""
Reddit Posts Worker Launcher Script - TaskManager API Pattern

This script launches a Reddit Posts Worker that uses pure TaskManager API.
No local SQLite queue is used - all task management is via external API.

Architecture:
    Worker → TaskManagerClient → External TaskManager API
           ↓
    IdeaInspiration Database (results only)

Usage:
    python scripts/run_worker.py [OPTIONS]

Options:
    --worker-id TEXT        Unique worker identifier (default: auto-generated)
    --worker-type TEXT      Worker type to create (default: reddit_subreddit)
    --claiming-policy TEXT  Task claiming policy: FIFO, LIFO, PRIORITY (default: FIFO)
    --poll-interval INT     Seconds between task polls (default: 5)
    --max-iterations INT    Max iterations (0 = unlimited, default: 0)
    --env-file TEXT         Path to .env file (default: .env)
    --help                  Show this message and exit

Examples:
    # Run worker with default settings
    python scripts/run_worker.py

    # Run worker with custom ID and policy
    python scripts/run_worker.py --worker-id reddit-worker-001 --claiming-policy LIFO

    # Run worker for limited iterations
    python scripts/run_worker.py --max-iterations 100

    # Run worker with custom .env file
    python scripts/run_worker.py --env-file .env.production
"""

import logging
import os
import socket
import sys
import uuid
from pathlib import Path

import click
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import Config
from workers.factory import worker_factory


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("reddit_worker.log")],
    )


def generate_worker_id() -> str:
    """Generate a unique worker ID based on hostname and UUID."""
    hostname = socket.gethostname()
    unique_id = str(uuid.uuid4())[:8]
    return f"reddit-worker-{hostname}-{unique_id}"


@click.command()
@click.option(
    "--worker-id", default=None, help="Unique worker identifier (default: auto-generated)"
)
@click.option(
    "--worker-type",
    default="reddit_subreddit",
    type=click.Choice(["reddit_subreddit"]),
    help="Worker type to create (default: reddit_subreddit)",
)
@click.option(
    "--claiming-policy",
    default="FIFO",
    type=click.Choice(["FIFO", "LIFO", "PRIORITY"]),
    help="Task claiming policy (default: FIFO)",
)
@click.option(
    "--poll-interval", default=5, type=int, help="Seconds between task polls (default: 5)"
)
@click.option(
    "--max-iterations", default=0, type=int, help="Max iterations (0 = unlimited, default: 0)"
)
@click.option("--env-file", default=".env", help="Path to .env file (default: .env)")
def main(worker_id, worker_type, claiming_policy, poll_interval, max_iterations, env_file):
    """Launch Reddit Posts Worker using TaskManager API pattern."""

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load environment variables
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
    else:
        logger.warning(f"Environment file {env_file} not found, using system environment")

    # Generate worker ID if not provided
    if not worker_id:
        worker_id = generate_worker_id()
        logger.info(f"Generated worker ID: {worker_id}")

    try:
        # Initialize configuration
        logger.info("Initializing configuration...")
        config = Config(interactive=False)

        # Create worker instance using factory
        logger.info(f"Creating worker (type: {worker_type})...")
        worker = worker_factory.create(
            worker_type=worker_type,
            worker_id=worker_id,
            config=config,
            claiming_policy=claiming_policy,
            poll_interval=poll_interval,
        )

        # Log worker information
        logger.info("=" * 80)
        logger.info("Reddit Posts Worker Started (TaskManager API Pattern)")
        logger.info("=" * 80)
        logger.info(f"Worker ID: {worker_id}")
        logger.info(f"Worker Type: {worker_type}")
        logger.info(f"Claiming Policy: {claiming_policy}")
        logger.info(f"Poll Interval: {poll_interval} seconds")
        logger.info(f"Max Iterations: {max_iterations if max_iterations > 0 else 'unlimited'}")
        logger.info(f"IdeaInspiration DB: {config.database_path}")
        logger.info("Task Queue: TaskManager API (external)")
        logger.info("=" * 80)

        # Run worker
        if max_iterations > 0:
            logger.info(f"Starting worker (will process up to {max_iterations} tasks)...")
            worker.run(max_iterations=max_iterations)
        else:
            logger.info("Starting worker (unlimited iterations, press Ctrl+C to stop)...")
            worker.run()

        logger.info("Worker completed successfully")

    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
