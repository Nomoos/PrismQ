#!/usr/bin/env python3
"""
Example: YouTube Channel Worker with TaskManager API

This example demonstrates how to use the refactored BaseWorker with
the TaskManager API instead of the legacy SQLite queue.

Architecture:
  Worker → TaskManagerClient → External TaskManager API
        ↓
   Results Database (local)
"""

import logging
from pathlib import Path
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def register_task_types():
    """
    Step 1: Register task types with TaskManager API.

    This should be run once during setup or on first worker startup.
    Task type IDs are persistent and can be reused across worker restarts.
    """
    from TaskManager import TaskManagerClient

    logger.info("=== Registering Task Types ===")

    client = TaskManagerClient()

    # Define task types for YouTube Channel workers
    task_types = [
        {
            "name": "PrismQ.YouTube.Channel.Scrape",
            "version": "1.0.0",
            "param_schema": {
                "type": "object",
                "properties": {
                    "channel_url": {"type": "string", "description": "YouTube channel URL"},
                    "max_videos": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 50,
                        "description": "Maximum videos to scrape",
                    },
                },
                "required": ["channel_url"],
            },
        }
    ]

    # Register each task type
    task_type_ids = []
    for task_type_def in task_types:
        try:
            result = client.register_task_type(
                name=task_type_def["name"],
                version=task_type_def["version"],
                param_schema=task_type_def["param_schema"],
            )

            task_type_id = result["id"]
            task_type_ids.append(task_type_id)

            status = "created" if result.get("created") else "exists"
            logger.info(f"Task type '{task_type_def['name']}' {status} (ID: {task_type_id})")

        except Exception as e:
            logger.error(f"Failed to register task type: {e}")
            raise

    logger.info(f"Registered task type IDs: {task_type_ids}")
    return task_type_ids


def create_example_worker(task_type_ids: list):
    """
    Step 2: Create a worker instance using TaskManager API.

    Args:
        task_type_ids: List of task type IDs from registration

    Returns:
        Configured worker instance (not started)
    """
    from src.core.config import Config
    from src.core.database import Database
    from src.workers import BaseWorker, Task, TaskResult

    logger.info("=== Creating Worker ===")

    # Initialize dependencies
    config = Config()
    results_db = Database(db_path=config.database_path, database_url=config.database_url)

    # Define a custom worker class
    class YouTubeChannelWorker(BaseWorker):
        """Worker for processing YouTube channel scraping tasks."""

        def process_task(self, task: Task) -> TaskResult:
            """Process a YouTube channel scraping task.

            Args:
                task: Task from TaskManager API

            Returns:
                TaskResult with success status and data
            """
            try:
                # Extract parameters
                channel_url = task.parameters.get("channel_url")
                max_videos = task.parameters.get("max_videos", 50)

                logger.info(
                    f"Processing channel scrape: {channel_url} " f"(max_videos: {max_videos})"
                )

                # TODO: Implement actual scraping logic here
                # For now, return a mock result
                result_data = {
                    "channel_id": "mock_channel_id",
                    "channel_title": "Mock Channel",
                    "videos_scraped": max_videos,
                    "channel_url": channel_url,
                }

                # Save to results database
                # self.results_db.save_channel_data(result_data)

                return TaskResult(success=True, data=result_data, items_processed=max_videos)

            except Exception as e:
                logger.error(f"Error processing task {task.id}: {e}", exc_info=True)
                return TaskResult(success=False, error=str(e))

    # Create worker with TaskManager API
    worker = YouTubeChannelWorker(
        worker_id="youtube-channel-worker-001",
        config=config,
        results_db=results_db,
        task_type_ids=task_type_ids,
        use_taskmanager=True,  # Use TaskManager API (default)
        strategy="LIFO",  # FIFO, LIFO, or PRIORITY
        poll_interval=5,
        max_backoff=60,
    )

    logger.info(
        f"Worker '{worker.worker_id}' created "
        f"(mode: TaskManager API, strategy: {worker.strategy})"
    )

    return worker


def create_example_tasks():
    """
    Step 3 (Optional): Create example tasks via TaskManager API.

    In production, tasks would be created by other modules or
    via the API web interface.
    """
    from TaskManager import TaskManagerClient

    logger.info("=== Creating Example Tasks ===")

    client = TaskManagerClient()

    # Example channels to scrape
    channels = [
        "https://youtube.com/@example1",
        "https://youtube.com/@example2",
    ]

    for channel_url in channels:
        try:
            task = client.create_task(
                task_type="PrismQ.YouTube.Channel.Scrape",
                params={"channel_url": channel_url, "max_videos": 50},
            )

            logger.info(
                f"Task created: ID={task['id']}, " f"Duplicate={task.get('duplicate', False)}"
            )

        except Exception as e:
            logger.error(f"Failed to create task for {channel_url}: {e}")


def main():
    """
    Main entry point demonstrating the complete workflow.
    """
    logger.info("=" * 60)
    logger.info("YouTube Channel Worker - TaskManager API Example")
    logger.info("=" * 60)

    try:
        # Step 1: Register task types (run once)
        task_type_ids = register_task_types()

        # Step 2: Create worker
        worker = create_example_worker(task_type_ids)

        # Step 3: (Optional) Create example tasks
        # Uncomment to create test tasks:
        # create_example_tasks()

        # Step 4: Start worker (runs until interrupted)
        logger.info("=" * 60)
        logger.info("Starting worker... (Press Ctrl+C to stop)")
        logger.info("=" * 60)

        # Run worker indefinitely
        worker.run()

    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Note: This example requires:
    # 1. TaskManager module installed: pip install -e Source/TaskManager
    # 2. Environment configured with TASKMANAGER_API_URL and TASKMANAGER_API_KEY
    # 3. EnvLoad module available

    main()
