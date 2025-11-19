# Classification Workers

This directory contains worker implementations for distributed classification processing using the TaskManager API.

## Overview

The Classification module has been refactored to support the Worker pattern, enabling:

- **Distributed Processing**: Multiple workers can process classification tasks concurrently
- **Task Deduplication**: API prevents processing the same content multiple times
- **Priority Management**: API manages task prioritization
- **Fault Tolerance**: API automatically retries failed tasks
- **Monitoring**: Centralized tracking of worker activity and task progress

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TaskManager API                           │
│              (External REST Service)                         │
│  - Task Queue Management                                     │
│  - Task Type Registration                                    │
│  - Worker Coordination                                       │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │ HTTP REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Classification Workers                          │
│  - Poll for tasks                                           │
│  - Claim tasks using policy (FIFO/LIFO/PRIORITY)           │
│  - Process classification                                   │
│  - Report completion                                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              IdeaInspiration Database                        │
│  - Store enriched classification results                    │
└─────────────────────────────────────────────────────────────┘
```

## Worker Types

### ClassificationWorker

Processes classification enrichment tasks for IdeaInspiration objects.

**Task Types:**
- `classification_enrich` - Classify and enrich a single IdeaInspiration
- `classification_batch` - Batch classification of multiple IdeaInspiration objects

**Features:**
- Category classification (8 primary categories)
- Story detection
- Flag generation (is_story, is_usable)
- Tag extraction
- Confidence scoring
- Database persistence

## Getting Started

### Prerequisites

1. **TaskManager API** - Must be running and accessible
2. **Environment Variables** - Configure in `.env` file:
   ```bash
   TASKMANAGER_API_URL=https://api.prismq.nomoos.cz/api
   TASKMANAGER_API_KEY=your-api-key-here
   IDEA_DB_PATH=ideas.db
   ```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Classification module
pip install -e .
```

### Register Task Types

Before starting workers, register the classification task types:

```bash
python scripts/register_task_types.py
```

This registers:
- `PrismQ.Classification.ContentEnrich`
- `PrismQ.Classification.BatchEnrich`

### Start a Worker

```bash
# Start worker with default settings
python scripts/run_worker.py

# Start worker with custom configuration
python scripts/run_worker.py \
    --worker-id classification-worker-001 \
    --claiming-policy LIFO \
    --poll-interval 5 \
    --max-backoff 60

# Start worker for limited iterations (useful for testing)
python scripts/run_worker.py --max-iterations 100
```

### Worker Options

- `--worker-id` - Unique worker identifier (auto-generated if not provided)
- `--task-type` - Task type to process (classification_enrich or classification_batch)
- `--poll-interval` - Seconds between task polls (default: 5)
- `--max-iterations` - Max iterations, 0 = unlimited (default: 0)
- `--claiming-policy` - Task claiming strategy (FIFO, LIFO, PRIORITY)
- `--max-backoff` - Maximum backoff time in seconds (default: 60)
- `--env-file` - Path to .env file (default: .env)
- `--idea-db-path` - Path to IdeaInspiration database

## Claiming Policies

### FIFO (First In, First Out)
Processes oldest tasks first. Good for fair processing order.

```bash
python scripts/run_worker.py --claiming-policy FIFO
```

### LIFO (Last In, First Out)
Processes newest tasks first. Good for time-sensitive content.

```bash
python scripts/run_worker.py --claiming-policy LIFO
```

### PRIORITY
Processes highest priority tasks first. Good for importance-based processing.

```bash
python scripts/run_worker.py --claiming-policy PRIORITY
```

## Task Examples

### Single Classification Task

Create a task via TaskManager API:

```json
{
  "type": "PrismQ.Classification.ContentEnrich",
  "params": {
    "idea_inspiration_id": "12345",
    "save_to_db": true
  },
  "priority": 1
}
```

### Batch Classification Task

```json
{
  "type": "PrismQ.Classification.BatchEnrich",
  "params": {
    "idea_inspiration_ids": ["123", "456", "789"],
    "save_to_db": true
  },
  "priority": 2
}
```

### Classification with Data

```json
{
  "type": "PrismQ.Classification.ContentEnrich",
  "params": {
    "idea_data": {
      "title": "Amazing story about...",
      "description": "This is a narrative about...",
      "content": "Full content here...",
      "keywords": ["story", "inspiration"],
      "source_type": "text"
    },
    "save_to_db": false
  }
}
```

## Monitoring

### Worker Logs

Workers log to:
- **Console** - Real-time progress
- **File** - `classification_worker.log` for history

Log levels:
- `INFO` - Normal operations
- `DEBUG` - Detailed processing information
- `ERROR` - Failures and exceptions

### Statistics

Workers track:
- `tasks_processed` - Successfully completed tasks
- `tasks_failed` - Failed tasks
- `uptime` - Worker running time

Logged periodically and on shutdown.

## Development

### Project Structure

```
src/workers/
├── __init__.py              # Worker types and protocols
├── classification_worker.py # Classification worker implementation
└── factory.py              # Worker factory (OCP pattern)

scripts/
├── run_worker.py           # Main worker launcher
└── register_task_types.py  # Task type registration
```

### Adding New Worker Types

1. Create worker class extending base functionality
2. Register in `factory.py`
3. Add task type registration in `register_task_types.py`
4. Update documentation

### Testing

```bash
# Run with limited iterations for testing
python scripts/run_worker.py --max-iterations 10

# Monitor logs
tail -f classification_worker.log
```

## Troubleshooting

### No Tasks Available

**Problem**: Worker continuously reports "No tasks available"

**Solutions:**
1. Verify tasks exist via TaskManager API
2. Check task types match registered types
3. Ensure tasks are "pending" not "claimed"
4. Verify API connectivity

### Task Processing Failures

**Problem**: Tasks fail during processing

**Solutions:**
1. Check worker logs for detailed errors
2. Verify IdeaInspiration data structure
3. Test classification locally
4. Check database connectivity

### API Connection Issues

**Problem**: "Invalid or missing API key" error

**Solutions:**
1. Verify `TASKMANAGER_API_KEY` in environment
2. Test API key with health check
3. Check API URL is correct
4. Ensure API key has correct permissions

## References

- [TaskManager Worker Implementation Guide](../../Source/TaskManager/_meta/docs/WORKER_IMPLEMENTATION_GUIDE.md)
- [Classification API Documentation](../_meta/docs/API.md)
- [IdeaInspiration Model](../../Model/README.md)
- [TaskManager API Swagger UI](https://api.prismq.nomoos.cz/public/swagger-ui)

## SOLID Principles

This implementation follows SOLID principles:

- **Single Responsibility**: Each worker handles one type of classification
- **Open/Closed**: Factory pattern allows extension without modification
- **Liskov Substitution**: Workers implement consistent interface
- **Interface Segregation**: Minimal, focused protocols
- **Dependency Inversion**: Depends on abstractions, injected dependencies
