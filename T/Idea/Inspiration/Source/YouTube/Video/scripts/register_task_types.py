#!/usr/bin/env python3
"""
YouTube Video Task Type Registration Content

Registers the youtube_video_scrape task type with the TaskManager API.

This script should be run once during deployment to register the task type
with the central TaskManager API at https://api.prismq.nomoos.cz/api/

Usage:
    python scripts/register_task_types.py

Requirements:
    - TASKMANAGER_API_URL set in environment or config
    - TASKMANAGER_API_KEY set in environment or config
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path to import TaskManager
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

try:
    from TaskManager import TaskManagerClient
except ImportError:
    print("Error: TaskManager module not found.")
    print("Please install TaskManager: pip install -e Source/TaskManager")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def register_youtube_video_task_types():
    """
    Register YouTube video scraping task types with TaskManager API.

    Registers three task types:
    1. youtube_video_single - Scrape a single video by ID/URL
    2. youtube_video_search - Search and scrape multiple videos
    3. youtube_video_scrape - General scraping (auto-routes based on parameters)
    """
    logger.info("=" * 70)
    logger.info("YouTube Video Task Type Registration")
    logger.info("=" * 70)

    # Initialize TaskManager client
    try:
        client = TaskManagerClient()
        logger.info(f"Connected to TaskManager API: {client.api_url}")
    except Exception as e:
        logger.error(f"Failed to initialize TaskManager client: {e}")
        logger.error("Please check your TASKMANAGER_API_URL and TASKMANAGER_API_KEY configuration")
        return False

    # Define task types
    task_types = [
        {
            "name": "youtube_video_single",
            "version": "1.0.0",
            "description": "Scrape a single YouTube video by ID or URL",
            "param_schema": {
                "type": "object",
                "properties": {
                    "video_id": {
                        "type": "string",
                        "description": "YouTube video ID (11 characters)",
                        "pattern": "^[a-zA-Z0-9_-]{11}$",
                    },
                    "video_url": {
                        "type": "string",
                        "description": "Full YouTube video URL",
                        "format": "uri",
                    },
                },
                "oneOf": [{"required": ["video_id"]}, {"required": ["video_url"]}],
            },
        },
        {
            "name": "youtube_video_search",
            "version": "1.0.0",
            "description": "Search YouTube and scrape multiple videos",
            "param_schema": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "YouTube search query",
                        "minLength": 1,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of videos to scrape",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 5,
                    },
                },
                "required": ["search_query"],
            },
        },
        {
            "name": "youtube_video_scrape",
            "version": "1.0.0",
            "description": "General YouTube video scraping (auto-routes based on parameters)",
            "param_schema": {
                "type": "object",
                "properties": {
                    "video_id": {
                        "type": "string",
                        "description": "YouTube video ID (11 characters)",
                        "pattern": "^[a-zA-Z0-9_-]{11}$",
                    },
                    "video_url": {
                        "type": "string",
                        "description": "Full YouTube video URL",
                        "format": "uri",
                    },
                    "search_query": {
                        "type": "string",
                        "description": "YouTube search query",
                        "minLength": 1,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of videos to scrape (for search)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 5,
                    },
                },
                "oneOf": [
                    {"required": ["video_id"]},
                    {"required": ["video_url"]},
                    {"required": ["search_query"]},
                ],
            },
        },
    ]

    # Register each task type
    registered_count = 0
    for task_type_def in task_types:
        try:
            logger.info(f"\nRegistering task type: {task_type_def['name']}")

            result = client.register_task_type(
                name=task_type_def["name"],
                version=task_type_def["version"],
                param_schema=task_type_def["param_schema"],
            )

            task_type_id = result.get("id")
            is_new = result.get("created", False)
            status = "✅ Created" if is_new else "✅ Already exists"

            logger.info(f"  {status} - ID: {task_type_id}")
            logger.info(f"  Description: {task_type_def['description']}")
            registered_count += 1

        except Exception as e:
            logger.error(f"  ❌ Failed to register '{task_type_def['name']}': {e}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info(
        f"Registration complete: {registered_count}/{len(task_types)} task types registered"
    )
    logger.info("=" * 70)

    return registered_count == len(task_types)


def verify_registration():
    """Verify that all task types are registered correctly."""
    logger.info("\n" + "=" * 70)
    logger.info("Verifying task type registration...")
    logger.info("=" * 70)

    try:
        client = TaskManagerClient()

        task_type_names = ["youtube_video_single", "youtube_video_search", "youtube_video_scrape"]

        for name in task_type_names:
            try:
                task_type = client.get_task_type(name)
                logger.info(
                    f"✅ {name} - ID: {task_type.get('id')} - Active: {task_type.get('active', True)}"
                )
            except Exception as e:
                logger.error(f"❌ {name} - Not found: {e}")
                return False

        logger.info("\n✅ All task types verified successfully!")
        return True

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


def main():
    """Main entry point for the registration script."""
    logger.info("Starting YouTube Video task type registration...\n")

    # Register task types
    success = register_youtube_video_task_types()

    if not success:
        logger.error("\n❌ Registration failed. Please check the errors above.")
        sys.exit(1)

    # Verify registration
    if verify_registration():
        logger.info("\n✅ Registration and verification complete!")
        sys.exit(0)
    else:
        logger.error("\n❌ Verification failed. Some task types may not be registered correctly.")
        sys.exit(1)


if __name__ == "__main__":
    main()
