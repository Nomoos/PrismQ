# T.Idea.Batch - Batch Idea Processing

Process multiple ideas in parallel for efficient content pipeline scaling.

## Overview

The Batch Processing module enables bulk processing of ideas, dramatically increasing throughput and allowing users to transform batches of ideas (10-100+) into titles and scripts efficiently.

## Features

- ✅ Process 10-100+ ideas in parallel
- ✅ Configurable concurrency limits (default: 5)
- ✅ Automatic retry with exponential backoff
- ✅ Real-time progress tracking
- ✅ Comprehensive batch reports (JSON/CSV)
- ✅ Queue management for large batches (>100 ideas)
- ✅ Pause/resume support for long-running batches
- ✅ Preserve individual idea context and metadata

## Quick Start

```python
import asyncio
from T.Idea.Batch import BatchProcessor, BatchConfig, ProcessingMode

async def process_idea(idea):
    """Your idea processing logic."""
    # Process the idea here
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

## Processing Modes

### Sequential Mode
- Process one idea at a time
- Predictable resource usage
- Slower but reliable
- Use for testing or debugging

```python
config = BatchConfig(mode=ProcessingMode.SEQUENTIAL)
```

### Parallel Mode (Default)
- Process multiple ideas concurrently
- Faster processing (5-10x speedup)
- Configurable concurrency limit
- Higher resource usage

```python
config = BatchConfig(
    mode=ProcessingMode.PARALLEL,
    max_concurrent=10
)
```

### Queue Mode
- For batches >100 ideas
- Distributed processing
- Fault-tolerant
- Supports pause/resume

```python
config = BatchConfig(
    mode=ProcessingMode.QUEUE,
    chunk_size=50
)
```

## Configuration

### BatchConfig

```python
@dataclass
class BatchConfig:
    max_concurrent: int = 5          # Max concurrent workers
    mode: ProcessingMode = PARALLEL  # Processing mode
    retry_attempts: int = 3          # Max retry attempts
    retry_backoff: float = 2.0       # Exponential backoff factor
    timeout_per_item: float = 300.0  # Timeout per item (seconds)
    chunk_size: int = 50             # Chunk size for queue mode
    enable_progress_tracking: bool = True
```

## Components

### BatchProcessor

Main processor for batch operations.

```python
processor = BatchProcessor(config)
report = await processor.process_batch(
    ideas=ideas,
    process_func=your_processor,
    batch_id='optional-id'
)
```

### RetryHandler

Handles retry logic with exponential backoff.

```python
from T.Idea.Batch import RetryHandler, RetryConfig

config = RetryConfig(
    max_attempts=3,
    backoff_factor=2.0,
    initial_delay=1.0
)
handler = RetryHandler(config)
```

### ReportGenerator

Generates comprehensive batch reports.

```python
from T.Idea.Batch import ReportGenerator

generator = ReportGenerator()
generator.print_summary(report)
json_report = generator.to_json(report)
csv_report = generator.to_csv(report)
```

### QueueManager

Manages queue-based processing for large batches.

```python
from T.Idea.Batch import QueueManager, QueueConfig

config = QueueConfig(chunk_size=50)
manager = QueueManager(config)
manager.add_items(ideas)
```

## Batch Report

The batch report includes:

- Batch ID and timestamps
- Total items processed
- Success/failure counts
- Processing times (total and average)
- Detailed failure information
- Configuration used

```json
{
  "batch_id": "batch-20251123-001",
  "total_items": 100,
  "success_count": 97,
  "failure_count": 3,
  "total_duration": 180.5,
  "avg_processing_time": 1.8,
  "failures": [
    {
      "idea_id": "idea-42",
      "error": "API rate limit exceeded",
      "attempts": 3
    }
  ]
}
```

## Error Handling

The batch processor handles errors gracefully:

- **Transient failures**: Automatically retried with exponential backoff
- **Permanent failures**: Logged and included in failure report
- **Timeouts**: Configurable per-item timeout
- **Exceptions**: Caught and reported without stopping batch

## Performance

Expected performance metrics:

- **Parallel speedup**: 5-10x vs sequential
- **Success rate**: >95% for stable processing
- **Retry success rate**: >80% for transient failures
- **Throughput**: >100 ideas/minute (queue mode)

## Examples

See `_meta/examples/batch_example.py` for comprehensive examples including:

- Small batch processing (10 ideas)
- Medium batch processing (50 ideas)
- Sequential processing
- Handling failures
- Queue mode for large batches

Run examples:

```bash
cd T/Idea/Batch/_meta/examples
python batch_example.py
```

## Testing

Run tests:

```bash
cd /home/runner/work/PrismQ/PrismQ
python -m pytest T/Idea/Batch/_meta/tests/test_batch_processing.py -v
```

## Database Integration

The module includes database support for tracking batch jobs:

```python
from T.Idea.Batch import BatchDatabase

db = BatchDatabase("batch.db")
db.connect()
db.create_tables()

# Track batch job
job_id = db.create_batch_job(
    batch_id="batch-001",
    total_items=100,
    config={"max_concurrent": 5}
)

# Add item results
db.add_batch_item(
    batch_id="batch-001",
    idea_id="idea-1",
    status="success",
    processing_time=1.5
)
```

## API Reference

### BatchProcessor

- `__init__(config: BatchConfig)`: Initialize processor
- `process_batch(ideas, process_func, batch_id)`: Process batch
- `generate_report(results)`: Generate batch report

### RetryHandler

- `__init__(config: RetryConfig)`: Initialize handler
- `execute_with_retry(func, *args, **kwargs)`: Execute with retry

### ReportGenerator

- `generate_report(...)`: Generate batch report
- `to_json(report)`: Convert report to JSON
- `to_csv(report)`: Convert report to CSV
- `print_summary(report)`: Print report summary

### QueueManager

- `add_items(items)`: Add items to queue
- `get_next_chunk()`: Get next chunk
- `mark_chunk_processed(results)`: Mark chunk as processed
- `pause()`: Pause processing
- `resume()`: Resume processing
- `get_progress()`: Get progress info

## Integration with T.Idea.From.User

To integrate with the existing IdeaCreator:

```python
import asyncio
from T.Idea.Batch import BatchProcessor, BatchConfig
from T.Idea.From.User import IdeaCreator

async def process_idea_with_creator(idea):
    """Process idea using IdeaCreator."""
    creator = IdeaCreator()
    title = idea.get('text', 'Untitled')
    
    # Generate ideas using IdeaCreator
    generated_ideas = creator.create_from_title(
        title=title,
        num_ideas=1  # One variation per input
    )
    
    return {
        'idea_id': idea.get('id'),
        'generated': generated_ideas[0] if generated_ideas else None
    }

async def main():
    processor = BatchProcessor()
    
    ideas = [
        {"id": f"idea-{i}", "text": f"Topic {i}"}
        for i in range(10)
    ]
    
    report = await processor.process_batch(
        ideas=ideas,
        process_func=process_idea_with_creator
    )
    
    print(f"Processed {report.success_count} ideas")

asyncio.run(main())
```

## Requirements

- Python 3.10+
- asyncio
- pytest (for testing)

## License

Part of the PrismQ project.

## Version

1.0.0 - Initial release

## Author

Worker02 (Python Specialist)
