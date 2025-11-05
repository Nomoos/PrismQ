"""
Example workflows demonstrating pattern integration and combinations.

This module provides real-world examples of how to use the TaskOrchestrator
to combine multiple background task patterns for complex workflows.

Examples included:
1. Video Processing Workflow - Concurrent + Long-Running + Fire-and-Forget
2. Data Pipeline Workflow - Simple + Periodic + Pooled
3. ML Training Workflow - Long-Running + Fire-and-Forget + Concurrent
"""

import asyncio
from pathlib import Path
from typing import List
import logging

from ..src.core.task_orchestrator import TaskOrchestrator, TaskPattern, PatternAdvisor

logger = logging.getLogger(__name__)


async def video_processing_workflow(video_paths: List[Path]) -> dict:
    """
    Complex workflow combining multiple patterns for video processing.
    
    This workflow demonstrates:
    - Pattern 3 (Concurrent): Process multiple videos in parallel
    - Pattern 2 (Long-Running): Stream progress for large videos
    - Pattern 5 (Periodic): Clean up temp files every hour
    - Pattern 4 (Fire-and-Forget): Send completion notifications
    
    Args:
        video_paths: List of video file paths to process
    
    Returns:
        Dictionary with processing results and statistics
    
    Example:
        >>> videos = [Path(f"video_{i}.mp4") for i in range(10)]
        >>> results = await video_processing_workflow(videos)
        >>> print(f"Processed {results['total']} videos")
    """
    orchestrator = TaskOrchestrator()
    results = {
        'total': len(video_paths),
        'processed': 0,
        'failed': 0,
        'results': []
    }
    
    logger.info(f"Starting video processing workflow for {len(video_paths)} videos")
    
    # Step 1: Set up periodic cleanup (Pattern 5)
    logger.info("Setting up periodic cleanup task")
    cleanup_task = await orchestrator.execute(
        script_path=Path("scripts/cleanup_temp_files.py"),
        args=[],
        pattern=TaskPattern.PERIODIC,
        interval_seconds=3600,  # Every hour
        task_name="video_temp_cleanup"
    )
    
    # Step 2: Separate videos by size for different processing strategies
    large_videos = [v for v in video_paths if v.stat().st_size > 1_000_000_000]  # > 1GB
    small_videos = [v for v in video_paths if v.stat().st_size <= 1_000_000_000]
    
    # Step 3: Process small videos concurrently (Pattern 3)
    if small_videos:
        logger.info(f"Processing {len(small_videos)} small videos concurrently")
        batch_results = await orchestrator.execute(
            script_path=Path("scripts/process_video.py"),
            args=["--batch"],
            pattern=TaskPattern.CONCURRENT,
            concurrent_tasks=5,  # Process 5 at a time
            tasks=small_videos
        )
        results['processed'] += len([r for r in batch_results if r[0] == 0])
        results['failed'] += len([r for r in batch_results if r[0] != 0])
        results['results'].extend(batch_results)
    
    # Step 4: Process large videos with streaming progress (Pattern 2)
    for video in large_videos:
        logger.info(f"Processing large video: {video.name}")
        exit_code = await orchestrator.execute(
            script_path=Path("scripts/process_large_video.py"),
            args=[str(video)],
            pattern=TaskPattern.LONG_RUNNING,
            streaming=True,
            run_id=f"video_{video.stem}"
        )
        if exit_code == 0:
            results['processed'] += 1
        else:
            results['failed'] += 1
        results['results'].append((exit_code, video.name))
    
    # Step 5: Send completion notification (Pattern 4 - Fire-and-Forget)
    logger.info("Sending completion notification")
    await orchestrator.execute(
        script_path=Path("scripts/send_notification.py"),
        args=[
            "--message", f"Processed {results['processed']}/{results['total']} videos",
            "--type", "completion"
        ],
        pattern=TaskPattern.FIRE_AND_FORGET,
        wait_for_result=False
    )
    
    logger.info(f"Video processing complete: {results['processed']} succeeded, {results['failed']} failed")
    return results


async def data_pipeline_workflow(data_sources: List[str]) -> dict:
    """
    Data processing pipeline combining simple, periodic, and pooled patterns.
    
    This workflow demonstrates:
    - Pattern 1 (Simple): Quick data validation
    - Pattern 6 (Pooled): High-frequency data queries
    - Pattern 5 (Periodic): Scheduled data sync
    
    Args:
        data_sources: List of data source identifiers
    
    Returns:
        Dictionary with pipeline results
    
    Example:
        >>> sources = ["source_a", "source_b", "source_c"]
        >>> results = await data_pipeline_workflow(sources)
        >>> print(f"Validated {results['validated']} sources")
    """
    orchestrator = TaskOrchestrator()
    results = {
        'validated': 0,
        'synced': 0,
        'queries': 0
    }
    
    logger.info(f"Starting data pipeline for {len(data_sources)} sources")
    
    # Step 1: Set up periodic sync (Pattern 5)
    logger.info("Setting up periodic data sync")
    sync_task = await orchestrator.execute(
        script_path=Path("scripts/sync_data.py"),
        args=data_sources,
        pattern=TaskPattern.PERIODIC,
        interval_seconds=300,  # Every 5 minutes
        task_name="data_sync"
    )
    
    # Step 2: Validate each data source (Pattern 1 - Simple)
    for source in data_sources:
        logger.info(f"Validating data source: {source}")
        exit_code, stdout, stderr = await orchestrator.execute(
            script_path=Path("scripts/validate_data.py"),
            args=["--source", source],
            pattern=TaskPattern.SIMPLE
        )
        if exit_code == 0:
            results['validated'] += 1
            logger.info(f"Source {source} validated successfully")
        else:
            logger.error(f"Source {source} validation failed: {stderr}")
    
    # Step 3: Perform high-frequency queries with pooling (Pattern 6)
    logger.info("Performing queries with resource pooling")
    for i in range(100):  # High-frequency queries
        result = await orchestrator.execute(
            script_path=Path("scripts/query_data.py"),
            args=["--query", f"query_{i}"],
            pattern=TaskPattern.POOLED,
            use_pool=True
        )
        results['queries'] += 1
    
    logger.info(f"Data pipeline complete: {results['validated']} validated, {results['queries']} queries")
    return results


async def ml_training_workflow(model_config: dict) -> dict:
    """
    ML model training workflow with progress tracking and notifications.
    
    This workflow demonstrates:
    - Pattern 2 (Long-Running): Train model with progress streaming
    - Pattern 4 (Fire-and-Forget): Send status updates
    - Pattern 3 (Concurrent): Evaluate on multiple datasets
    
    Args:
        model_config: Configuration dictionary for model training
    
    Returns:
        Dictionary with training results
    
    Example:
        >>> config = {'epochs': 100, 'batch_size': 32}
        >>> results = await ml_training_workflow(config)
        >>> print(f"Training accuracy: {results['accuracy']}")
    """
    orchestrator = TaskOrchestrator()
    results = {
        'training_complete': False,
        'accuracy': 0.0,
        'evaluations': []
    }
    
    logger.info("Starting ML training workflow")
    
    # Step 1: Send training start notification (Pattern 4)
    await orchestrator.execute(
        script_path=Path("scripts/send_notification.py"),
        args=["--message", "Model training started", "--type", "info"],
        pattern=TaskPattern.FIRE_AND_FORGET,
        wait_for_result=False
    )
    
    # Step 2: Train model with streaming progress (Pattern 2)
    logger.info("Training model with progress streaming")
    exit_code = await orchestrator.execute(
        script_path=Path("scripts/train_model.py"),
        args=[
            "--epochs", str(model_config.get('epochs', 100)),
            "--batch-size", str(model_config.get('batch_size', 32))
        ],
        pattern=TaskPattern.LONG_RUNNING,
        streaming=True,
        run_id="model_training"
    )
    
    if exit_code == 0:
        results['training_complete'] = True
        logger.info("Model training completed successfully")
        
        # Step 3: Evaluate on multiple datasets concurrently (Pattern 3)
        eval_datasets = ["test_set_1", "test_set_2", "test_set_3"]
        logger.info(f"Evaluating model on {len(eval_datasets)} datasets concurrently")
        
        eval_results = await orchestrator.execute(
            script_path=Path("scripts/evaluate_model.py"),
            args=["--concurrent"],
            pattern=TaskPattern.CONCURRENT,
            concurrent_tasks=3,
            tasks=eval_datasets
        )
        
        results['evaluations'] = eval_results
        results['accuracy'] = sum(r[1] for r in eval_results) / len(eval_results)
        
        # Step 4: Send completion notification (Pattern 4)
        await orchestrator.execute(
            script_path=Path("scripts/send_notification.py"),
            args=[
                "--message", f"Training complete. Accuracy: {results['accuracy']:.2f}",
                "--type", "success"
            ],
            pattern=TaskPattern.FIRE_AND_FORGET,
            wait_for_result=False
        )
    else:
        logger.error("Model training failed")
        # Send failure notification
        await orchestrator.execute(
            script_path=Path("scripts/send_notification.py"),
            args=["--message", "Model training failed", "--type", "error"],
            pattern=TaskPattern.FIRE_AND_FORGET,
            wait_for_result=False
        )
    
    logger.info(f"ML training workflow complete: Success={results['training_complete']}")
    return results


async def pattern_selection_example():
    """
    Demonstrate automatic pattern selection using PatternAdvisor.
    
    Shows how to use PatternAdvisor to get recommendations and
    let TaskOrchestrator auto-select the appropriate pattern.
    """
    logger.info("=== Pattern Selection Examples ===")
    
    # Example 1: Get recommendation for long-running task
    pattern = PatternAdvisor.recommend(
        expected_duration_seconds=300,
        requires_streaming=True
    )
    logger.info(f"Recommended for 5-min streaming task: {pattern.value}")
    
    # Example 2: Get recommendation for concurrent processing
    pattern = PatternAdvisor.recommend(
        concurrent_tasks=10,
        needs_result=True
    )
    logger.info(f"Recommended for 10 concurrent tasks: {pattern.value}")
    
    # Example 3: Get recommendation for periodic task
    pattern = PatternAdvisor.recommend(
        recurring=True
    )
    logger.info(f"Recommended for recurring task: {pattern.value}")
    
    # Example 4: Compare all patterns
    logger.info("\n=== Pattern Comparison ===")
    matrix = PatternAdvisor.compare_patterns()
    for pattern, info in matrix.items():
        logger.info(f"\n{info['name']}:")
        logger.info(f"  Use when: {info['use_when']}")
        logger.info(f"  Benefits: {', '.join(info['benefits'])}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    async def main():
        logger.info("Starting example workflows demonstration")
        
        # Pattern selection examples
        await pattern_selection_example()
    
    asyncio.run(main())
