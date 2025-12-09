"""Example usage of the Batch Processing module.

This script demonstrates how to use the T.Idea.Batch module for
processing multiple ideas efficiently.
"""

import asyncio
import os
import sys

# Add parent directories to path
script_dir = os.path.dirname(os.path.abspath(__file__))
batch_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, batch_dir)

from src.batch_processor import BatchConfig, BatchProcessor, ProcessingMode
from src.report_generator import ReportGenerator


async def simple_idea_processor(idea):
    """Simple mock processor for ideas.

    In a real application, this would call the IdeaCreator or other
    processing logic.
    """
    # Simulate some processing time
    await asyncio.sleep(0.1)

    # Return processed result
    return {
        "idea_id": idea.get("id"),
        "title": f"Processed: {idea.get('text', 'Untitled')}",
        "status": "completed",
    }


async def example_small_batch():
    """Example: Process a small batch of 10 ideas."""
    print("\n" + "=" * 60)
    print("Example 1: Small Batch (10 ideas)")
    print("=" * 60)

    # Create sample ideas
    ideas = [{"id": f"idea-{i}", "text": f"AI in healthcare topic {i}"} for i in range(1, 11)]

    # Configure batch processor
    config = BatchConfig(max_concurrent=5, mode=ProcessingMode.PARALLEL, retry_attempts=3)

    processor = BatchProcessor(config)

    # Process batch
    report = await processor.process_batch(
        ideas=ideas, process_func=simple_idea_processor, batch_id="example-small-batch"
    )

    # Display results
    generator = ReportGenerator()
    generator.print_summary(report)

    return report


async def example_medium_batch():
    """Example: Process a medium batch of 50 ideas."""
    print("\n" + "=" * 60)
    print("Example 2: Medium Batch (50 ideas)")
    print("=" * 60)

    # Create sample ideas
    ideas = [
        {"id": f"idea-{i}", "text": f"Climate change solution {i}", "category": "environment"}
        for i in range(1, 51)
    ]

    # Configure batch processor
    config = BatchConfig(
        max_concurrent=10,
        mode=ProcessingMode.PARALLEL,
        retry_attempts=2,
        enable_progress_tracking=True,
    )

    processor = BatchProcessor(config)

    # Process batch
    report = await processor.process_batch(
        ideas=ideas, process_func=simple_idea_processor, batch_id="example-medium-batch"
    )

    # Display results
    generator = ReportGenerator()
    generator.print_summary(report)

    # Save report to JSON
    json_report = generator.to_json(report)
    with open("/tmp/batch_report.json", "w") as f:
        f.write(json_report)
    print(f"📄 Full report saved to: /tmp/batch_report.json")

    return report


async def example_sequential_processing():
    """Example: Process ideas sequentially."""
    print("\n" + "=" * 60)
    print("Example 3: Sequential Processing")
    print("=" * 60)

    ideas = [{"id": f"idea-{i}", "text": f"Tech innovation {i}"} for i in range(1, 11)]

    # Sequential mode
    config = BatchConfig(max_concurrent=1, mode=ProcessingMode.SEQUENTIAL, retry_attempts=1)

    processor = BatchProcessor(config)

    report = await processor.process_batch(
        ideas=ideas, process_func=simple_idea_processor, batch_id="example-sequential"
    )

    # Display results
    generator = ReportGenerator()
    generator.print_summary(report)

    return report


async def example_with_failures():
    """Example: Handle processing failures gracefully."""
    print("\n" + "=" * 60)
    print("Example 4: Handling Failures")
    print("=" * 60)

    async def processor_with_failures(idea):
        """Processor that fails on specific IDs."""
        await asyncio.sleep(0.05)

        idea_id = idea.get("id", "")
        # Simulate failures for ideas 3 and 7
        if idea_id in ["idea-3", "idea-7"]:
            raise Exception(f"Simulated failure for {idea_id}")

        return {"idea_id": idea_id, "status": "success"}

    ideas = [{"id": f"idea-{i}", "text": f"Test idea {i}"} for i in range(1, 11)]

    config = BatchConfig(
        max_concurrent=5, mode=ProcessingMode.PARALLEL, retry_attempts=3  # Will retry failed items
    )

    processor = BatchProcessor(config)

    report = await processor.process_batch(
        ideas=ideas, process_func=processor_with_failures, batch_id="example-with-failures"
    )

    # Display results
    generator = ReportGenerator()
    generator.print_summary(report)

    return report


async def example_queue_mode():
    """Example: Use queue mode for large batches."""
    print("\n" + "=" * 60)
    print("Example 5: Queue Mode (Large Batch)")
    print("=" * 60)

    # Create a large batch
    ideas = [{"id": f"idea-{i}", "text": f"Large batch idea {i}"} for i in range(1, 101)]

    config = BatchConfig(
        max_concurrent=10,
        mode=ProcessingMode.QUEUE,
        chunk_size=25,  # Process in chunks of 25
        retry_attempts=2,
    )

    processor = BatchProcessor(config)

    report = await processor.process_batch(
        ideas=ideas, process_func=simple_idea_processor, batch_id="example-queue-mode"
    )

    # Display results
    generator = ReportGenerator()
    generator.print_summary(report)

    return report


async def main():
    """Run all examples."""
    print("\n🚀 T.Idea.Batch - Batch Processing Examples")
    print("=" * 60)

    # Run examples
    await example_small_batch()
    await example_medium_batch()
    await example_sequential_processing()
    await example_with_failures()
    await example_queue_mode()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
