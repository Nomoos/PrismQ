# POST-005: T.Idea.Batch - Batch Idea Processing

**Type**: Post-MVP Enhancement  
**Worker**: Worker02 (Python Specialist)  
**Priority**: Medium  
**Effort**: 2 days  
**Module**: `PrismQ.T.Idea.Batch`  
**Sprint**: Sprint 4 (Weeks 9-10)  
**Status**: 🎯 PLANNED

---

## Description

Process multiple ideas in parallel for efficient content pipeline scaling.

This enhancement enables bulk processing of ideas, dramatically increasing throughput and allowing users to transform batches of ideas (10-100+) into titles and scripts efficiently.

---

## Acceptance Criteria

- [ ] Accept list of ideas as input (10-100+ ideas)
- [ ] Process ideas concurrently using async/parallel execution
- [ ] Track batch processing status in real-time
- [ ] Handle failures gracefully with retry logic per item
- [ ] Generate comprehensive batch processing report
- [ ] Queue management for large batches (>100 ideas)
- [ ] Support pause/resume for long-running batches
- [ ] Preserve individual idea context and metadata

---

## Input/Output

**Input**:
- List of idea objects (10-100+ items)
- Batch configuration:
  - Max concurrent workers (default: 5)
  - Retry policy (max attempts: 3)
  - Processing mode (sequential/parallel)

**Output**:
- Batch processing results:
  - Success count
  - Failure count with error details
  - Processing time per idea
  - Total batch duration
- Individual idea processing status
- Batch summary report (JSON/CSV)

---

## Dependencies

- **MVP-001**: T.Idea.From.User module must be complete
- Async processing infrastructure (asyncio or Celery)

---

## Technical Notes

### Parallel Processing Architecture
```python
import asyncio
from typing import List
from dataclasses import dataclass

@dataclass
class BatchResult:
    idea_id: str
    status: str  # 'success' | 'failed'
    result: dict
    duration: float
    error: str = None

async def process_batch(
    ideas: List[dict],
    max_concurrent: int = 5
) -> List[BatchResult]:
    """Process ideas in parallel with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_semaphore(idea):
        async with semaphore:
            return await process_single_idea(idea)
    
    tasks = [process_with_semaphore(idea) for idea in ideas]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### Retry Logic
```python
async def process_with_retry(
    idea: dict,
    max_attempts: int = 3,
    backoff_factor: float = 2.0
) -> BatchResult:
    """Retry failed processing with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return await process_single_idea(idea)
        except Exception as e:
            if attempt == max_attempts - 1:
                return BatchResult(
                    idea_id=idea['id'],
                    status='failed',
                    error=str(e)
                )
            await asyncio.sleep(backoff_factor ** attempt)
```

### Queue Management (for large batches >100)
- Use Redis queue or RabbitMQ for distribution
- Break large batches into chunks (50 ideas per chunk)
- Track progress in database
- Support pause/resume via queue state management

### Files to Create
- `T/Idea/Batch/batch_processor.py` (new)
- `T/Idea/Batch/queue_manager.py` (new)
- `T/Idea/Batch/retry_handler.py` (new)
- `T/Idea/Batch/report_generator.py` (new)
- `T/Idea/Batch/__init__.py` (new)

### Database Schema Extension
```sql
CREATE TABLE batch_jobs (
    id INTEGER PRIMARY KEY,
    batch_id TEXT UNIQUE,
    total_items INTEGER,
    processed_items INTEGER,
    success_count INTEGER,
    failure_count INTEGER,
    status TEXT,  -- 'pending' | 'running' | 'paused' | 'completed' | 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    config JSON
);

CREATE TABLE batch_items (
    id INTEGER PRIMARY KEY,
    batch_id TEXT,
    idea_id TEXT,
    status TEXT,
    result JSON,
    error TEXT,
    processing_time REAL,
    attempts INTEGER,
    FOREIGN KEY (batch_id) REFERENCES batch_jobs(id)
);
```

### Testing Requirements
- [ ] Test with small batch (10 ideas)
- [ ] Test with medium batch (50 ideas)
- [ ] Test with large batch (100+ ideas)
- [ ] Test failure scenarios (network errors, API limits)
- [ ] Test retry logic (transient failures)
- [ ] Test pause/resume functionality
- [ ] Validate batch report accuracy
- [ ] Performance test: measure throughput

---

## Batch Processing Modes

### Sequential Mode
- Process one idea at a time
- Predictable resource usage
- Slower but reliable
- Use for testing or debugging

### Parallel Mode (Default)
- Process multiple ideas concurrently
- Faster processing (5-10x speedup)
- Higher resource usage
- Configurable concurrency limit

### Queue Mode
- For batches >100 ideas
- Distributed processing
- Fault-tolerant
- Supports pause/resume

---

## Example Usage

```python
from T.Idea.Batch import BatchProcessor

# Create batch processor
processor = BatchProcessor(max_concurrent=5)

# Define ideas
ideas = [
    {"id": "idea-1", "text": "AI in healthcare"},
    {"id": "idea-2", "text": "Climate change solutions"},
    # ... 98 more ideas
]

# Process batch
results = await processor.process_batch(
    ideas=ideas,
    mode='parallel',
    retry_attempts=3
)

# Generate report
report = processor.generate_report(results)
print(f"Success: {report.success_count}/{report.total}")
print(f"Duration: {report.total_duration}s")
```

---

## Batch Report Format

```json
{
  "batch_id": "batch-2025-11-23-001",
  "total_items": 100,
  "processed_items": 100,
  "success_count": 97,
  "failure_count": 3,
  "total_duration": 180.5,
  "avg_processing_time": 1.8,
  "started_at": "2025-11-23T10:00:00Z",
  "completed_at": "2025-11-23T10:03:00Z",
  "failures": [
    {
      "idea_id": "idea-42",
      "error": "API rate limit exceeded",
      "attempts": 3
    }
  ]
}
```

---

## Success Metrics

- Parallel speedup: 5-10x vs sequential
- Success rate: >95% for stable processing
- Retry success rate: >80% for transient failures
- Report generation time: <2 seconds
- Queue throughput: >100 ideas/minute

---

**Created**: 2025-11-23  
**Owner**: Worker02 (Python Specialist)
