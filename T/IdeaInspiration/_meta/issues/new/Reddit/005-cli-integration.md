# Issue #005: CLI Integration for Reddit Workers

**Priority**: Medium  
**Status**: New  
**Dependencies**: Issue #004 (Worker Factory)  
**Duration**: 2-3 days

## Objective

Add command-line interface commands for managing Reddit workers, enabling easy worker lifecycle management.

## Problem Statement

Currently, workers must be started programmatically. We need CLI commands for:
- Starting workers
- Stopping workers
- Monitoring worker status
- Managing task queue
- Viewing worker metrics

## Proposed Solution

### CLI Commands

Add to `Source/Text/Reddit/Posts/src/cli.py`:

```python
@main.group('worker')
def worker():
    """Reddit worker management commands."""
    pass

@worker.command('start')
@click.option('--worker-id', '-w', required=True, help='Worker ID')
@click.option('--task-type', '-t', required=True, 
              type=click.Choice(['subreddit_scrape', 'trending_scrape', 'search_scrape', 'rising_scrape']))
@click.option('--queue-db', '-q', default='queue.db', help='Queue database path')
@click.option('--strategy', '-s', default='LIFO', 
              type=click.Choice(['FIFO', 'LIFO', 'PRIORITY']))
def worker_start(worker_id, task_type, queue_db, strategy):
    """Start a Reddit worker."""
    # Implementation

@worker.command('status')
@click.option('--queue-db', '-q', default='queue.db')
def worker_status(queue_db):
    """Show worker status and metrics."""
    # Implementation

@worker.command('queue')
@click.option('--queue-db', '-q', default='queue.db')
def worker_queue(queue_db):
    """Show task queue status."""
    # Implementation

@worker.command('add-task')
@click.option('--task-type', '-t', required=True)
@click.option('--params', '-p', required=True, help='JSON parameters')
@click.option('--priority', default=5, type=int)
@click.option('--queue-db', '-q', default='queue.db')
def add_task(task_type, params, priority, queue_db):
    """Add a task to the queue."""
    # Implementation
```

## Acceptance Criteria

- [ ] `worker start` command implemented
- [ ] `worker status` command shows active workers
- [ ] `worker queue` command shows queue status
- [ ] `worker add-task` command adds tasks to queue
- [ ] All commands have proper error handling
- [ ] Help text is clear and complete
- [ ] Examples in documentation

## Testing Strategy

1. Manual testing of all CLI commands
2. Integration tests for worker lifecycle
3. Test error scenarios
4. Test with real queue database

## Usage Examples

```bash
# Start a subreddit worker
python -m src.cli worker start -w worker-01 -t subreddit_scrape

# Add a task to the queue
python -m src.cli worker add-task -t subreddit_scrape -p '{"subreddit":"python","limit":50}'

# Check worker status
python -m src.cli worker status

# View queue
python -m src.cli worker queue
```

## Implementation Notes

- Workers should run in background or foreground mode
- Support graceful shutdown (SIGTERM handling)
- Log to both console and file
- Configuration from .env file

## References

- YouTube CLI: `Source/Video/YouTube/src/cli.py`
- Current Reddit CLI: `Source/Text/Reddit/Posts/src/cli.py`
