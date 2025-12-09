"""T.Idea.Batch - Batch Idea Processing Module

This module provides efficient batch processing capabilities for idea generation,
supporting parallel execution, retry logic, and comprehensive reporting.

Key Features:
- Process 10-100+ ideas in parallel
- Configurable concurrency limits
- Automatic retry with exponential backoff
- Real-time progress tracking
- Comprehensive batch reports
- Queue management for large batches (>100 ideas)
- Pause/resume support for long-running batches

Example Usage:
    ```python
    import asyncio
    from T.Idea.Batch import BatchProcessor, BatchConfig, ProcessingMode

    async def process_idea(idea):
        # Your idea processing logic here
        return {"processed": True}

    async def main():
        # Create batch processor
        config = BatchConfig(
            max_concurrent=5,
            mode=ProcessingMode.PARALLEL,
            retry_attempts=3
        )
        processor = BatchProcessor(config)

        # Prepare ideas
        ideas = [
            {"id": f"idea-{i}", "text": f"Idea {i}"}
            for i in range(10)
        ]

        # Process batch
        report = await processor.process_batch(
            ideas=ideas,
            process_func=process_idea
        )

        # Print results
        print(f"Success: {report.success_count}/{report.total_items}")
        print(f"Duration: {report.total_duration:.2f}s")

    asyncio.run(main())
    ```

See POST-005-Batch-Processing.md for full requirements and specifications.
"""

from .src.batch_database import BatchDatabase
from .src.batch_processor import (
    BatchConfig,
    BatchProcessor,
    BatchResult,
    ProcessingMode,
)
from .src.queue_manager import QueueConfig, QueueManager, QueueStatus
from .src.report_generator import BatchItemReport, BatchReport, ReportGenerator
from .src.retry_handler import RetryConfig, RetryHandler

__version__ = "1.0.0"

__all__ = [
    # Main processor
    "BatchProcessor",
    "BatchConfig",
    "BatchResult",
    "ProcessingMode",
    # Retry handling
    "RetryHandler",
    "RetryConfig",
    # Reporting
    "ReportGenerator",
    "BatchReport",
    "BatchItemReport",
    # Queue management
    "QueueManager",
    "QueueConfig",
    "QueueStatus",
    # Database
    "BatchDatabase",
]
