"""Batch processor for processing multiple ideas in parallel.

This module provides the main BatchProcessor class for efficient parallel
processing of idea batches with configurable concurrency, retry logic,
and comprehensive reporting.
"""

import asyncio
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .queue_manager import QueueConfig, QueueManager
from .report_generator import BatchReport, ReportGenerator
from .retry_handler import RetryConfig, RetryHandler

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing mode for batch operations."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    QUEUE = "queue"


@dataclass
class BatchConfig:
    """Configuration for batch processing.

    Attributes:
        max_concurrent: Maximum concurrent workers (default: 5)
        mode: Processing mode (default: parallel)
        retry_attempts: Maximum retry attempts per item (default: 3)
        retry_backoff: Exponential backoff factor (default: 2.0)
        timeout_per_item: Timeout per item in seconds (default: 300)
        chunk_size: Chunk size for queue mode (default: 50)
        enable_progress_tracking: Enable real-time progress tracking (default: True)
    """

    max_concurrent: int = 5
    mode: ProcessingMode = ProcessingMode.PARALLEL
    retry_attempts: int = 3
    retry_backoff: float = 2.0
    timeout_per_item: float = 300.0
    chunk_size: int = 50
    enable_progress_tracking: bool = True


@dataclass
class BatchResult:
    """Result for a single item in a batch.

    Attributes:
        idea_id: ID of the processed idea
        status: Processing status ('success' | 'failed')
        result: Processing result data
        duration: Processing time in seconds
        attempts: Number of processing attempts
        error: Error message if failed
    """

    idea_id: str
    status: str
    result: Optional[Any] = None
    duration: float = 0.0
    attempts: int = 1
    error: Optional[str] = None


class BatchProcessor:
    """Processor for handling batch idea processing operations."""

    def __init__(self, config: Optional[BatchConfig] = None):
        """Initialize batch processor.

        Args:
            config: Optional batch configuration
        """
        self.config = config or BatchConfig()

        # Initialize components
        retry_config = RetryConfig(
            max_attempts=self.config.retry_attempts, backoff_factor=self.config.retry_backoff
        )
        self.retry_handler = RetryHandler(retry_config)
        self.report_generator = ReportGenerator()

        # Queue manager for large batches
        if self.config.mode == ProcessingMode.QUEUE:
            queue_config = QueueConfig(chunk_size=self.config.chunk_size)
            self.queue_manager = QueueManager(queue_config)
        else:
            self.queue_manager = None

        # Progress tracking
        self.total_items = 0
        self.processed_items = 0
        self.start_time = None
        self.batch_id = None

    async def process_batch(
        self,
        ideas: List[Dict[str, Any]],
        process_func: Callable[[Dict[str, Any]], Awaitable[Any]],
        batch_id: Optional[str] = None,
    ) -> BatchReport:
        """Process a batch of ideas.

        Args:
            ideas: List of idea dictionaries to process
            process_func: Async function to process a single idea
            batch_id: Optional batch identifier

        Returns:
            BatchReport with processing results
        """
        self.batch_id = batch_id or f"batch-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.total_items = len(ideas)
        self.processed_items = 0
        self.start_time = datetime.now(timezone.utc)

        logger.info(
            f"Starting batch {self.batch_id}: {self.total_items} items, "
            f"mode={self.config.mode.value}, max_concurrent={self.config.max_concurrent}"
        )

        # Choose processing strategy based on mode
        if self.config.mode == ProcessingMode.SEQUENTIAL:
            results = await self._process_sequential(ideas, process_func)
        elif self.config.mode == ProcessingMode.PARALLEL:
            results = await self._process_parallel(ideas, process_func)
        else:  # QUEUE mode
            results = await self._process_queue(ideas, process_func)

        # Generate report
        completed_at = datetime.now(timezone.utc)
        report = self.report_generator.generate_report(
            batch_id=self.batch_id,
            results=results,
            started_at=self.start_time,
            completed_at=completed_at,
            config={
                "mode": self.config.mode.value,
                "max_concurrent": self.config.max_concurrent,
                "retry_attempts": self.config.retry_attempts,
            },
        )

        logger.info(
            f"Batch {self.batch_id} completed: {report.success_count} success, "
            f"{report.failure_count} failed, {report.total_duration:.2f}s"
        )

        return report

    async def _process_sequential(
        self, ideas: List[Dict[str, Any]], process_func: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> List[Dict[str, Any]]:
        """Process ideas sequentially.

        Args:
            ideas: List of ideas to process
            process_func: Processing function

        Returns:
            List of processing results
        """
        results = []

        for i, idea in enumerate(ideas, 1):
            logger.info(f"Processing item {i}/{self.total_items}")
            result = await self._process_single_item(idea, process_func)
            results.append(result)
            self.processed_items += 1

            if self.config.enable_progress_tracking:
                self._log_progress()

        return results

    async def _process_parallel(
        self, ideas: List[Dict[str, Any]], process_func: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> List[Dict[str, Any]]:
        """Process ideas in parallel with concurrency limit.

        Args:
            ideas: List of ideas to process
            process_func: Processing function

        Returns:
            List of processing results
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def process_with_semaphore(idea: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                result = await self._process_single_item(idea, process_func)
                self.processed_items += 1

                if self.config.enable_progress_tracking:
                    self._log_progress()

                return result

        # Create tasks for all ideas
        tasks = [process_with_semaphore(idea) for idea in ideas]

        # Process all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = {
                    "idea_id": ideas[i].get("id", f"unknown-{i}"),
                    "status": "failed",
                    "error": str(result),
                    "duration": 0.0,
                    "attempts": 1,
                }
                processed_results.append(error_result)
            else:
                processed_results.append(result)

        return processed_results

    async def _process_queue(
        self, ideas: List[Dict[str, Any]], process_func: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> List[Dict[str, Any]]:
        """Process ideas using queue-based chunking.

        Args:
            ideas: List of ideas to process
            process_func: Processing function

        Returns:
            List of processing results
        """
        # Add items to queue
        self.queue_manager.add_items(ideas)

        # Define chunk processing function
        async def process_chunk(
            chunk: List[Dict[str, Any]], max_concurrent: int
        ) -> List[Dict[str, Any]]:
            return await self._process_parallel(chunk, process_func)

        # Process queue
        results = await self.queue_manager.process_queue(process_chunk, self.config.max_concurrent)

        return results

    async def _process_single_item(
        self, idea: Dict[str, Any], process_func: Callable[[Dict[str, Any]], Awaitable[Any]]
    ) -> Dict[str, Any]:
        """Process a single idea with retry logic.

        Args:
            idea: Idea dictionary to process
            process_func: Processing function

        Returns:
            Processing result dictionary
        """
        idea_id = idea.get("id", "unknown")
        start_time = time.time()

        try:
            # Apply timeout
            result, attempts, error = await asyncio.wait_for(
                self.retry_handler.execute_with_retry(process_func, idea),
                timeout=self.config.timeout_per_item,
            )

            duration = time.time() - start_time

            if error:
                return {
                    "idea_id": idea_id,
                    "status": "failed",
                    "error": error,
                    "duration": duration,
                    "attempts": attempts,
                }

            return {
                "idea_id": idea_id,
                "status": "success",
                "result": result,
                "duration": duration,
                "attempts": attempts,
            }

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            return {
                "idea_id": idea_id,
                "status": "failed",
                "error": f"Timeout after {self.config.timeout_per_item}s",
                "duration": duration,
                "attempts": 1,
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "idea_id": idea_id,
                "status": "failed",
                "error": str(e),
                "duration": duration,
                "attempts": 1,
            }

    def _log_progress(self) -> None:
        """Log current processing progress."""
        if self.start_time and self.total_items > 0:
            elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            progress_pct = (self.processed_items / self.total_items) * 100

            # Estimate remaining time
            if self.processed_items > 0:
                avg_time_per_item = elapsed / self.processed_items
                remaining_items = self.total_items - self.processed_items
                estimated_remaining = avg_time_per_item * remaining_items

                logger.info(
                    f"Progress: {self.processed_items}/{self.total_items} "
                    f"({progress_pct:.1f}%) - ETA: {estimated_remaining:.0f}s"
                )

    def generate_report(self, results: List[Dict[str, Any]]) -> BatchReport:
        """Generate a batch report from results.

        Args:
            results: List of processing results

        Returns:
            BatchReport instance
        """
        completed_at = datetime.now(timezone.utc)

        return self.report_generator.generate_report(
            batch_id=self.batch_id or "unknown",
            results=results,
            started_at=self.start_time or completed_at,
            completed_at=completed_at,
            config={
                "mode": self.config.mode.value,
                "max_concurrent": self.config.max_concurrent,
                "retry_attempts": self.config.retry_attempts,
            },
        )


__all__ = ["BatchProcessor", "BatchConfig", "BatchResult", "ProcessingMode"]
