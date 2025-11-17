#!/usr/bin/env python3
"""
Register Classification Task Types with TaskManager API

This script registers classification task types with the TaskManager API.
Run this before starting workers to ensure task types are available.

Usage:
    python scripts/register_task_types.py [--env-file .env]
"""

import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import click

# Add TaskManager to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Source' / 'TaskManager'))

try:
    from TaskManager import TaskManagerClient
except ImportError:
    print("ERROR: TaskManager module not found. Please ensure TaskManager is installed.")
    sys.exit(1)


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


@click.command()
@click.option(
    '--env-file',
    default='.env',
    help='Path to .env file (default: .env)'
)
def main(env_file):
    """Register classification task types with TaskManager API."""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Load environment variables
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")
    else:
        logger.warning(f"Environment file {env_file} not found, using system environment")
    
    try:
        # Initialize TaskManager client
        logger.info("Initializing TaskManager API client...")
        client = TaskManagerClient()
        
        # Test connection
        logger.info("Testing API connection...")
        health = client.health_check()
        logger.info(f"API Status: {health.get('status', 'unknown')}")
        
        # Define task types
        task_types = [
            {
                "name": "PrismQ.Classification.ContentEnrich",
                "version": "1.0.0",
                "param_schema": {
                    "type": "object",
                    "properties": {
                        "idea_inspiration_id": {
                            "type": "string",
                            "description": "ID of IdeaInspiration to classify"
                        },
                        "idea_data": {
                            "type": "object",
                            "description": "IdeaInspiration data dictionary (alternative to ID)"
                        },
                        "save_to_db": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to save enriched data to database"
                        }
                    }
                },
                "description": "Classify and enrich a single IdeaInspiration object"
            },
            {
                "name": "PrismQ.Classification.BatchEnrich",
                "version": "1.0.0",
                "param_schema": {
                    "type": "object",
                    "properties": {
                        "idea_inspiration_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of IdeaInspiration IDs to classify"
                        },
                        "save_to_db": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to save enriched data to database"
                        }
                    },
                    "required": ["idea_inspiration_ids"]
                },
                "description": "Classify and enrich multiple IdeaInspiration objects in batch"
            }
        ]
        
        # Register task types
        logger.info("Registering classification task types...")
        logger.info("=" * 80)
        
        for task_type_def in task_types:
            try:
                result = client.register_task_type(
                    name=task_type_def["name"],
                    version=task_type_def["version"],
                    param_schema=task_type_def["param_schema"]
                )
                
                task_type_id = result['id']
                status = "Created" if result.get('created') else "Already exists"
                
                logger.info(f"✓ {task_type_def['name']}")
                logger.info(f"  Status: {status}")
                logger.info(f"  ID: {task_type_id}")
                logger.info(f"  Version: {task_type_def['version']}")
                logger.info(f"  Description: {task_type_def.get('description', 'N/A')}")
                logger.info("")
                
            except Exception as e:
                logger.error(f"✗ Failed to register {task_type_def['name']}: {e}")
        
        logger.info("=" * 80)
        logger.info("Task type registration complete!")
        logger.info("")
        logger.info("You can now start workers with:")
        logger.info("  python scripts/run_worker.py")
        
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
