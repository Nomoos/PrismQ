"""Queue manager for handling large batch processing operations.

This module provides queue-based management for processing batches larger than
100 ideas, with support for pause/resume functionality and distributed processing.
"""

import asyncio
import json
import logging
from collections import deque
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Deque
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class QueueStatus(Enum):
    """Status of a queue."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueueConfig:
    """Configuration for queue management.
    
    Attributes:
        chunk_size: Number of items per chunk (default: 50)
        max_queue_size: Maximum items in queue (default: 1000)
        enable_persistence: Whether to persist queue state (default: False)
        persistence_path: Path for queue state persistence
    """
    chunk_size: int = 50
    max_queue_size: int = 1000
    enable_persistence: bool = False
    persistence_path: str = "queue_state.json"


class QueueManager:
    """Manager for queue-based batch processing."""
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """Initialize queue manager.
        
        Args:
            config: Optional queue configuration
        """
        self.config = config or QueueConfig()
        self.queue: Deque[Dict[str, Any]] = deque()
        self.processed: List[Dict[str, Any]] = []
        self.status = QueueStatus.PENDING
        self.current_chunk: List[Dict[str, Any]] = []
        self.total_items = 0
        self.processed_count = 0
    
    def add_items(self, items: List[Dict[str, Any]]) -> None:
        """Add items to the processing queue.
        
        Args:
            items: List of items to process
            
        Raises:
            ValueError: If adding items would exceed max queue size
        """
        if len(self.queue) + len(items) > self.config.max_queue_size:
            raise ValueError(
                f"Adding {len(items)} items would exceed max queue size "
                f"of {self.config.max_queue_size}"
            )
        
        self.queue.extend(items)
        self.total_items += len(items)
        logger.info(f"Added {len(items)} items to queue (total: {len(self.queue)})")
    
    def get_next_chunk(self) -> List[Dict[str, Any]]:
        """Get the next chunk of items to process.
        
        Returns:
            List of items (up to chunk_size)
        """
        chunk = []
        chunk_size = min(self.config.chunk_size, len(self.queue))
        
        for _ in range(chunk_size):
            if self.queue:
                chunk.append(self.queue.popleft())
        
        self.current_chunk = chunk
        logger.debug(f"Retrieved chunk of {len(chunk)} items")
        return chunk
    
    def mark_chunk_processed(
        self, 
        results: List[Dict[str, Any]]
    ) -> None:
        """Mark current chunk as processed and store results.
        
        Args:
            results: Processing results for the chunk
        """
        self.processed.extend(results)
        self.processed_count += len(results)
        self.current_chunk = []
        
        logger.info(
            f"Chunk processed: {self.processed_count}/{self.total_items} "
            f"({len(self.queue)} remaining)"
        )
    
    def pause(self) -> None:
        """Pause queue processing."""
        if self.status == QueueStatus.RUNNING:
            self.status = QueueStatus.PAUSED
            logger.info("Queue processing paused")
            
            if self.config.enable_persistence:
                self._save_state()
    
    def resume(self) -> None:
        """Resume queue processing."""
        if self.status == QueueStatus.PAUSED:
            self.status = QueueStatus.RUNNING
            logger.info("Queue processing resumed")
    
    def is_complete(self) -> bool:
        """Check if all items have been processed.
        
        Returns:
            True if queue is empty and no current chunk
        """
        return len(self.queue) == 0 and len(self.current_chunk) == 0
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current queue processing progress.
        
        Returns:
            Dictionary with progress information
        """
        return {
            "total_items": self.total_items,
            "processed_count": self.processed_count,
            "remaining_count": len(self.queue),
            "current_chunk_size": len(self.current_chunk),
            "progress_percentage": (
                (self.processed_count / self.total_items * 100) 
                if self.total_items > 0 else 0.0
            ),
            "status": self.status.value
        }
    
    def _save_state(self) -> None:
        """Save queue state to disk for persistence."""
        state = {
            "queue": list(self.queue),
            "processed": self.processed,
            "current_chunk": self.current_chunk,
            "total_items": self.total_items,
            "processed_count": self.processed_count,
            "status": self.status.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            with open(self.config.persistence_path, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Queue state saved to {self.config.persistence_path}")
        except Exception as e:
            logger.error(f"Failed to save queue state: {e}")
    
    def load_state(self) -> bool:
        """Load queue state from disk.
        
        Returns:
            True if state was loaded successfully
        """
        try:
            with open(self.config.persistence_path, 'r') as f:
                state = json.load(f)
            
            self.queue = deque(state.get('queue', []))
            self.processed = state.get('processed', [])
            self.current_chunk = state.get('current_chunk', [])
            self.total_items = state.get('total_items', 0)
            self.processed_count = state.get('processed_count', 0)
            self.status = QueueStatus(state.get('status', 'pending'))
            
            logger.info(
                f"Queue state loaded from {self.config.persistence_path}: "
                f"{self.processed_count}/{self.total_items} processed"
            )
            return True
            
        except FileNotFoundError:
            logger.debug(f"No saved state found at {self.config.persistence_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to load queue state: {e}")
            return False
    
    async def process_queue(
        self,
        process_chunk_func,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """Process entire queue with chunks.
        
        Args:
            process_chunk_func: Async function to process a chunk
            max_concurrent: Maximum concurrent chunk processing
            
        Returns:
            List of all processing results
        """
        self.status = QueueStatus.RUNNING
        
        try:
            while not self.is_complete() and self.status == QueueStatus.RUNNING:
                chunk = self.get_next_chunk()
                
                if not chunk:
                    break
                
                # Process chunk
                results = await process_chunk_func(chunk, max_concurrent)
                self.mark_chunk_processed(results)
                
                # Check if paused
                while self.status == QueueStatus.PAUSED:
                    await asyncio.sleep(1)
            
            if self.is_complete():
                self.status = QueueStatus.COMPLETED
                logger.info("Queue processing completed")
            
            return self.processed
            
        except Exception as e:
            self.status = QueueStatus.FAILED
            logger.error(f"Queue processing failed: {e}")
            raise


__all__ = ["QueueManager", "QueueConfig", "QueueStatus"]
