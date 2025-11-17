"""Worker factory for creating scoring workers.

Provides factory methods for creating configured worker instances.
Follows Factory pattern for simplified worker instantiation.
"""

import logging
from pathlib import Path
from typing import Optional

from .scoring_worker import ScoringWorker
from ..config import Config
from ..scoring import ScoringEngine

logger = logging.getLogger(__name__)


class WorkerFactory:
    """Factory for creating scoring worker instances."""
    
    @staticmethod
    def create_scoring_worker(
        worker_id: Optional[str] = None,
        config: Optional[Config] = None,
        claiming_policy: str = "FIFO",
        poll_interval: int = 5,
        max_backoff: int = 60,
        enable_autoscore: bool = True,
        autoscore_db_path: Optional[str] = None,
        autoscore_batch_size: int = 10,
    ) -> ScoringWorker:
        """Create a configured scoring worker instance.
        
        Uses TaskManager API (external service) for task coordination.
        
        Args:
            worker_id: Unique worker identifier (auto-generated if None)
            config: Configuration object (creates new if None)
            claiming_policy: Task claiming strategy - "FIFO", "LIFO", or "PRIORITY"
            poll_interval: Base polling interval in seconds
            max_backoff: Maximum backoff time in seconds
            enable_autoscore: Enable automatic scoring of unscored IdeaInspiration items
            autoscore_db_path: Path to IdeaInspiration database (default: auto-detect)
            autoscore_batch_size: Number of unscored items to fetch at once
            
        Returns:
            Configured ScoringWorker instance
        """
        # Auto-generate worker ID if not provided
        if worker_id is None:
            import uuid
            worker_id = f"scoring-worker-{uuid.uuid4().hex[:8]}"
        
        # Create config if not provided
        if config is None:
            config = Config(interactive=False)
        
        # Create scoring engine
        scoring_engine = ScoringEngine()
        
        logger.info(f"Creating scoring worker: {worker_id}")
        
        # Create and return worker
        return ScoringWorker(
            worker_id=worker_id,
            config=config,
            scoring_engine=scoring_engine,
            claiming_policy=claiming_policy,
            poll_interval=poll_interval,
            max_backoff=max_backoff,
            enable_autoscore=enable_autoscore,
            autoscore_db_path=autoscore_db_path,
            autoscore_batch_size=autoscore_batch_size,
        )


__all__ = ["WorkerFactory"]
