#!/usr/bin/env python3
"""
Classification Worker with TaskManager API Integration

This worker integrates with the TaskManager API to process classification tasks.
It follows the worker pattern established in the TaskManager documentation.

The worker:
1. Registers classification task types with TaskManager API
2. Polls for available tasks
3. Claims tasks using configured policy (FIFO, LIFO, PRIORITY)
4. Processes classification enrichment
5. Reports completion status back to API
6. Continues until no tasks exist, then waits

Usage:
    python scripts/run_worker.py [OPTIONS]

Options:
    --worker-id TEXT        Unique worker identifier (default: auto-generated)
    --task-type TEXT        Task type to process (default: classification_enrich)
    --poll-interval INT     Seconds between task polls (default: 5)
    --max-iterations INT    Max iterations (0 = unlimited, default: 0)
    --claiming-policy TEXT  Task claiming policy (FIFO, LIFO, PRIORITY, default: FIFO)
    --env-file TEXT         Path to .env file (default: .env)
    --idea-db-path TEXT     Path to IdeaInspiration database
    --help                  Show this message and exit

Examples:
    # Run worker with default settings
    python scripts/run_worker.py
    
    # Run worker with custom ID and policy
    python scripts/run_worker.py --worker-id classification-worker-001 --claiming-policy LIFO
    
    # Run worker for limited iterations
    python scripts/run_worker.py --max-iterations 100
"""

import sys
import os
import logging
import time
import click
from pathlib import Path
from dotenv import load_dotenv
import socket
import uuid
from typing import Optional, List
from datetime import datetime, timezone

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Source' / 'TaskManager'))

# Import TaskManager client
try:
    from TaskManager import TaskManagerClient, ResourceNotFoundError
    HAS_TASKMANAGER = True
except ImportError:
    HAS_TASKMANAGER = False
    TaskManagerClient = None
    ResourceNotFoundError = Exception
    print("WARNING: TaskManager module not found. Worker will run in standalone mode (processing unclassified IdeaInspiration records only).")

# Import worker
from workers.factory import worker_factory


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('classification_worker.log')
        ]
    )


def generate_worker_id() -> str:
    """Generate a unique worker ID based on hostname and UUID."""
    hostname = socket.gethostname()
    unique_id = str(uuid.uuid4())[:8]
    return f"classification-worker-{hostname}-{unique_id}"


def register_task_types(client: TaskManagerClient) -> List[int]:
    """Register classification task types with TaskManager API.
    
    Args:
        client: TaskManager API client
        
    Returns:
        List of registered task type IDs
    """
    logger = logging.getLogger(__name__)
    logger.info("Registering classification task types...")
    
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
            }
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
            }
        }
    ]
    
    task_type_ids = []
    
    for task_type_def in task_types:
        try:
            result = client.register_task_type(
                name=task_type_def["name"],
                version=task_type_def["version"],
                param_schema=task_type_def["param_schema"]
            )
            
            task_type_id = result['id']
            task_type_ids.append(task_type_id)
            
            status = "created" if result.get('created') else "exists"
            logger.info(
                f"Task type '{task_type_def['name']}' {status} "
                f"(ID: {task_type_id})"
            )
            
        except Exception as e:
            logger.error(f"Failed to register task type: {e}")
            raise
    
    logger.info(f"Registered {len(task_type_ids)} task types: {task_type_ids}")
    return task_type_ids


def run_standalone_loop(
    worker,
    poll_interval: int,
    max_backoff: int,
    max_iterations: int = 0
):
    """Run worker loop in standalone mode (no TaskManager API).
    
    In standalone mode, the worker only processes unclassified IdeaInspiration
    records from the database.
    
    Args:
        worker: Worker instance
        poll_interval: Initial polling interval in seconds
        max_backoff: Maximum backoff time in seconds
        max_iterations: Maximum iterations (0 = unlimited)
    """
    logger = logging.getLogger(__name__)
    
    current_backoff = poll_interval
    iterations = 0
    
    logger.info("Worker started in standalone mode - processing unclassified IdeaInspiration records")
    
    try:
        while True:
            # Check max iterations
            if max_iterations > 0 and iterations >= max_iterations:
                logger.info(f"Reached maximum iterations ({max_iterations})")
                break
            
            # Process unclassified ideas
            try:
                result = worker.process_unclassified_ideas(limit=10)
                
                if result['processed'] > 0:
                    logger.info(
                        f"Processed {result['processed']} unclassified ideas: "
                        f"{result['successful']} successful, {result['failed']} failed"
                    )
                    # Reset backoff after finding work
                    current_backoff = poll_interval
                    iterations += 1
                else:
                    # No unclassified ideas found, wait with backoff
                    logger.debug(f"No unclassified ideas found, waiting {current_backoff:.1f}s")
                    time.sleep(current_backoff)
                    current_backoff = min(current_backoff * 1.5, max_backoff)
                    
            except Exception as e:
                logger.error(f"Error processing unclassified ideas: {e}")
                time.sleep(current_backoff)
                current_backoff = min(current_backoff * 1.5, max_backoff)
    
    except KeyboardInterrupt:
        logger.info(
            f"Worker shutdown requested "
            f"(processed: {worker.tasks_processed}, failed: {worker.tasks_failed})"
        )
    except Exception as e:
        logger.error(f"Fatal error in worker: {e}", exc_info=True)
        raise


def run_worker_loop(
    worker,
    client: TaskManagerClient,
    worker_id: str,
    task_type_ids: List[int],
    poll_interval: int,
    max_backoff: int,
    claiming_policy: str,
    max_iterations: int = 0
):
    """Run the main worker loop with TaskManager API integration.
    
    Args:
        worker: Worker instance
        client: TaskManager API client
        worker_id: Worker identifier
        task_type_ids: List of task type IDs to process
        poll_interval: Initial polling interval in seconds
        max_backoff: Maximum backoff time in seconds
        claiming_policy: Task claiming strategy
        max_iterations: Maximum iterations (0 = unlimited)
    """
    logger = logging.getLogger(__name__)
    
    # Configure sort parameters based on policy
    if claiming_policy == "FIFO":
        sort_by, sort_order = "created_at", "ASC"
    elif claiming_policy == "LIFO":
        sort_by, sort_order = "created_at", "DESC"
    elif claiming_policy == "PRIORITY":
        sort_by, sort_order = "priority", "DESC"
    else:
        sort_by, sort_order = "created_at", "ASC"
    
    current_backoff = poll_interval
    iterations = 0
    
    logger.info(
        f"Worker {worker_id} started - waiting for tasks "
        f"(policy: {claiming_policy}, poll: {poll_interval}s)"
    )
    
    try:
        while True:
            # Check max iterations
            if max_iterations > 0 and iterations >= max_iterations:
                logger.info(f"Reached maximum iterations ({max_iterations})")
                break
            
            # Try to claim a task from any registered type
            task = None
            for task_type_id in task_type_ids:
                try:
                    api_task = client.claim_task(
                        worker_id=worker_id,
                        task_type_id=task_type_id,
                        sort_by=sort_by,
                        sort_order=sort_order
                    )
                    if api_task:
                        # Convert to worker Task format
                        from workers import Task, TaskStatus
                        task = Task(
                            id=api_task['id'],
                            task_type="classification_enrich",  # Map API type to worker type
                            params=api_task['params'],
                            status=TaskStatus.CLAIMED,
                            priority=api_task.get('priority', 0)
                        )
                        break
                except ResourceNotFoundError:
                    continue
            
            if task:
                # Process the task
                logger.info(f"Processing task {task.id}")
                result = worker.process_task(task)
                
                # Complete the task via API
                if result.success:
                    client.complete_task(
                        task_id=task.id,
                        worker_id=worker_id,
                        success=True,
                        result=result.data
                    )
                    logger.info(
                        f"Task {task.id} completed successfully "
                        f"(IdeaInspiration ID: {result.data.get('idea_inspiration_id')})"
                    )
                else:
                    client.complete_task(
                        task_id=task.id,
                        worker_id=worker_id,
                        success=False,
                        error=result.error
                    )
                    logger.error(f"Task {task.id} failed: {result.error}")
                
                # Reset backoff after successful processing
                current_backoff = poll_interval
                iterations += 1
            else:
                # No tasks available from TaskManager API
                # Try to process unclassified IdeaInspiration records from database
                logger.debug(
                    f"No TaskManager tasks available "
                    f"(processed: {worker.tasks_processed}, failed: {worker.tasks_failed})"
                )
                
                # Process unclassified ideas when idle
                try:
                    result = worker.process_unclassified_ideas(limit=5)
                    if result['processed'] > 0:
                        logger.info(
                            f"Processed {result['processed']} unclassified ideas from database: "
                            f"{result['successful']} successful, {result['failed']} failed"
                        )
                        # Reset backoff after finding work
                        current_backoff = poll_interval
                    else:
                        # No unclassified ideas either, wait with backoff
                        logger.debug(f"No unclassified ideas found, waiting {current_backoff:.1f}s")
                        time.sleep(current_backoff)
                        current_backoff = min(current_backoff * 1.5, max_backoff)
                except Exception as e:
                    logger.error(f"Error processing unclassified ideas: {e}")
                    time.sleep(current_backoff)
                    current_backoff = min(current_backoff * 1.5, max_backoff)
    
    except KeyboardInterrupt:
        logger.info(
            f"Worker {worker_id} shutdown requested "
            f"(processed: {worker.tasks_processed}, failed: {worker.tasks_failed})"
        )
    except Exception as e:
        logger.error(f"Fatal error in worker: {e}", exc_info=True)
        raise


@click.command()
@click.option(
    '--worker-id',
    default=None,
    help='Unique worker identifier (default: auto-generated)'
)
@click.option(
    '--task-type',
    default='classification_enrich',
    type=click.Choice(['classification_enrich', 'classification_batch']),
    help='Task type to process (default: classification_enrich)'
)
@click.option(
    '--poll-interval',
    default=5,
    type=int,
    help='Seconds between task polls (default: 5)'
)
@click.option(
    '--max-iterations',
    default=0,
    type=int,
    help='Max iterations (0 = unlimited, default: 0)'
)
@click.option(
    '--claiming-policy',
    default='FIFO',
    type=click.Choice(['FIFO', 'LIFO', 'PRIORITY']),
    help='Task claiming policy (default: FIFO)'
)
@click.option(
    '--max-backoff',
    default=60,
    type=int,
    help='Maximum backoff time in seconds (default: 60)'
)
@click.option(
    '--env-file',
    default='.env',
    help='Path to .env file (default: .env)'
)
@click.option(
    '--idea-db-path',
    default=None,
    help='Path to IdeaInspiration database'
)
def main(worker_id, task_type, poll_interval, max_iterations, claiming_policy, 
         max_backoff, env_file, idea_db_path):
    """Launch Classification Worker for processing classification tasks."""
    
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
        # Determine idea_db_path
        if not idea_db_path:
            idea_db_path = os.getenv('IDEA_DB_PATH', 'ideas.db')
        
        # Create worker instance
        logger.info(f"Creating worker for task type: {task_type}")
        worker = worker_factory.create(
            task_type=task_type,
            worker_id=worker_id,
            idea_db_path=idea_db_path
        )
        
        # Check if TaskManager is available
        if HAS_TASKMANAGER:
            # Initialize TaskManager client
            logger.info("Initializing TaskManager API client...")
            client = TaskManagerClient()
            
            # Register task types
            task_type_ids = register_task_types(client)
            
            # Log worker information
            logger.info("=" * 80)
            logger.info("Classification Worker Started (TaskManager + Standalone Mode)")
            logger.info("=" * 80)
            logger.info(f"Worker ID: {worker_id}")
            logger.info(f"Task Type: {task_type}")
            logger.info(f"Claiming Policy: {claiming_policy}")
            logger.info(f"Poll Interval: {poll_interval} seconds")
            logger.info(f"Max Backoff: {max_backoff} seconds")
            logger.info(f"Max Iterations: {max_iterations if max_iterations > 0 else 'unlimited'}")
            logger.info(f"IdeaInspiration DB: {idea_db_path}")
            logger.info(f"Mode: TaskManager API + Auto-classify unclassified records when idle")
            logger.info("=" * 80)
            
            # Run worker loop with TaskManager
            run_worker_loop(
                worker=worker,
                client=client,
                worker_id=worker_id,
                task_type_ids=task_type_ids,
                poll_interval=poll_interval,
                max_backoff=max_backoff,
                claiming_policy=claiming_policy,
                max_iterations=max_iterations
            )
        else:
            # Run in standalone mode without TaskManager
            logger.info("=" * 80)
            logger.info("Classification Worker Started (Standalone Mode)")
            logger.info("=" * 80)
            logger.info(f"Worker ID: {worker_id}")
            logger.info(f"Poll Interval: {poll_interval} seconds")
            logger.info(f"Max Backoff: {max_backoff} seconds")
            logger.info(f"Max Iterations: {max_iterations if max_iterations > 0 else 'unlimited'}")
            logger.info(f"IdeaInspiration DB: {idea_db_path}")
            logger.info(f"Mode: Standalone - Processing unclassified IdeaInspiration records only")
            logger.info("=" * 80)
            
            # Run in standalone mode (only process unclassified ideas)
            run_standalone_loop(
                worker=worker,
                poll_interval=poll_interval,
                max_backoff=max_backoff,
                max_iterations=max_iterations
            )
            max_iterations=max_iterations
        )
        
        logger.info("Worker completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
