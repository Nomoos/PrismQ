#!/usr/bin/env python3
"""
YouTube Video Worker Launcher Script

This script launches a YouTube Video Worker that processes video scraping tasks.
The worker integrates with TaskManager API for task management and IdeaInspiration
database for result storage.

Usage:
    python scripts/run_worker.py [OPTIONS]

Options:
    --worker-id TEXT        Unique worker identifier (default: auto-generated)
    --task-type TEXT        Task type to process (default: youtube_video_single)
                           Options: youtube_video_single, youtube_video_search, youtube_video_scrape
    --poll-interval INT     Seconds between task polls (default: 5)
    --max-iterations INT    Max iterations (0 = unlimited, default: 0)
    --env-file TEXT         Path to .env file (default: .env)
    --help                  Show this message and exit

Examples:
    # Run worker with default settings
    python scripts/run_worker.py

    # Run worker with custom ID and task type
    python scripts/run_worker.py --worker-id youtube-worker-001 --task-type youtube_video_search

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
from core.database import Database
from workers.factory import worker_factory


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("youtube_worker.log")],
    )


def generate_worker_id() -> str:
    """Generate a unique worker ID based on hostname and UUID."""
    hostname = socket.gethostname()
    unique_id = str(uuid.uuid4())[:8]
    return f"youtube-worker-{hostname}-{unique_id}"


@click.command()
@click.option(
    "--worker-id", default=None, help="Unique worker identifier (default: auto-generated)"
)
@click.option(
    "--task-type",
    default="youtube_video_single",
    type=click.Choice(["youtube_video_single", "youtube_video_search", "youtube_video_scrape"]),
    help="Task type to process (default: youtube_video_single)",
)
@click.option(
    "--poll-interval", default=5, type=int, help="Seconds between task polls (default: 5)"
)
@click.option(
    "--max-iterations", default=0, type=int, help="Max iterations (0 = unlimited, default: 0)"
)
@click.option("--env-file", default=".env", help="Path to .env file (default: .env)")
def main(worker_id, task_type, poll_interval, max_iterations, env_file):
    """Launch YouTube Video Worker for processing video scraping tasks."""

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
        # Initialize configuration and database
        logger.info("Initializing configuration and database...")
        config = Config()
        results_db = Database(config.database_path)

        # Create worker instance
        logger.info(f"Creating worker for task type: {task_type}")
        worker = worker_factory.create(
            task_type=task_type,
            worker_id=worker_id,
            queue_db_path=os.getenv("QUEUE_DB_PATH", "data/worker_queue.db"),
            config=config,
            results_db=results_db,
        )

        # Log worker information
        logger.info("=" * 80)
        logger.info("YouTube Video Worker Started")
        logger.info("=" * 80)
        logger.info(f"Worker ID: {worker_id}")
        logger.info(f"Task Type: {task_type}")
        logger.info(f"Poll Interval: {poll_interval} seconds")
        logger.info(f"Max Iterations: {max_iterations if max_iterations > 0 else 'unlimited'}")
        logger.info(f"Results Database: {config.database_path}")
        logger.info("=" * 80)

        # Run worker
        if max_iterations > 0:
            logger.info(f"Starting worker (will process up to {max_iterations} tasks)...")
            worker.run(poll_interval=poll_interval, max_iterations=max_iterations)
        else:
            logger.info("Starting worker (unlimited iterations, press Ctrl+C to stop)...")
            worker.run(poll_interval=poll_interval)

        logger.info("Worker completed successfully")

    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
