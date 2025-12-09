"""Reddit worker entry point with TaskManager integration.

This script provides a command-line entry point for running the Reddit worker
with TaskManager API integration for centralized task coordination.

Following SOLID principles:
- Single Responsibility: Worker lifecycle management
- Dependency Inversion: Depends on abstractions (Config, Database, TaskManagerClient)
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
_src_path = Path(__file__).resolve().parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from core.config import Config
from core.database import Database
from workers.reddit_subreddit_worker import RedditSubredditWorker

# Import TaskManager client (optional)
try:
    # Add TaskManager to path
    _taskmanager_path = Path(__file__).resolve().parents[4] / "TaskManager"
    if str(_taskmanager_path) not in sys.path:
        sys.path.insert(0, str(_taskmanager_path))

    from src.client import TaskManagerClient

    _taskmanager_available = True
except ImportError:
    _taskmanager_available = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_worker(
    worker_id: str = "reddit-worker-01",
    queue_db_path: Optional[str] = None,
    config: Optional[Config] = None,
    enable_taskmanager: bool = True,
    **kwargs,
) -> RedditSubredditWorker:
    """
    Create and configure a Reddit worker.

    Args:
        worker_id: Unique worker identifier
        queue_db_path: Path to queue database (defaults to working_dir/queue.db)
        config: Configuration object (creates new if None)
        enable_taskmanager: Whether to enable TaskManager integration
        **kwargs: Additional arguments passed to worker

    Returns:
        Configured RedditSubredditWorker instance

    Raises:
        ValueError: If configuration is invalid
    """
    # Load configuration
    if config is None:
        config = Config(interactive=False)

    # Set queue database path
    if queue_db_path is None:
        queue_db_path = str(Path(config.working_directory) / "queue.db")

    # Initialize results database
    results_db = Database(config.database_path)

    # Initialize worker with TaskManager integration flag
    worker = RedditSubredditWorker(
        worker_id=worker_id,
        queue_db_path=queue_db_path,
        config=config,
        results_db=results_db,
        idea_db_path=config.database_path,
        enable_taskmanager=enable_taskmanager,
        **kwargs,
    )

    return worker


def main():
    """
    Main entry point for Reddit worker.

    This function initializes and runs the Reddit worker with TaskManager integration.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Reddit worker with TaskManager integration")
    parser.add_argument(
        "--worker-id",
        default="reddit-worker-01",
        help="Unique worker identifier (default: reddit-worker-01)",
    )
    parser.add_argument("--queue-db", help="Path to queue database (default: working_dir/queue.db)")
    parser.add_argument(
        "--poll-interval", type=int, default=5, help="Polling interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--max-backoff", type=int, default=60, help="Maximum backoff time in seconds (default: 60)"
    )
    parser.add_argument(
        "--strategy",
        default="LIFO",
        choices=["FIFO", "LIFO", "PRIORITY"],
        help="Task claiming strategy (default: LIFO)",
    )
    parser.add_argument(
        "--disable-taskmanager", action="store_true", help="Disable TaskManager integration"
    )
    parser.add_argument(
        "--max-iterations", type=int, help="Maximum iterations before stopping (default: infinite)"
    )

    args = parser.parse_args()

    # Check TaskManager availability
    if not _taskmanager_available and not args.disable_taskmanager:
        logger.warning(
            "TaskManager module not available. "
            "Worker will run without TaskManager integration. "
            "Use --disable-taskmanager to suppress this warning."
        )

    try:
        # Create worker
        logger.info(f"Initializing Reddit worker '{args.worker_id}'...")
        worker = create_worker(
            worker_id=args.worker_id,
            queue_db_path=args.queue_db,
            enable_taskmanager=not args.disable_taskmanager and _taskmanager_available,
            strategy=args.strategy,
            poll_interval=args.poll_interval,
            max_backoff=args.max_backoff,
        )

        # Log configuration
        logger.info(f"Worker configuration:")
        logger.info(f"  - Worker ID: {args.worker_id}")
        logger.info(f"  - Strategy: {args.strategy}")
        logger.info(f"  - Poll interval: {args.poll_interval}s")
        logger.info(f"  - Max backoff: {args.max_backoff}s")
        logger.info(
            f"  - TaskManager: {'enabled' if not args.disable_taskmanager and _taskmanager_available else 'disabled'}"
        )

        # Run worker
        logger.info("Starting worker loop...")
        worker.run(max_iterations=args.max_iterations)

    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
