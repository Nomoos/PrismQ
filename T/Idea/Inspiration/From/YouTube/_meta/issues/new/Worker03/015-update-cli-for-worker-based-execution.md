# Issue #015: Update CLI for Worker-Based Execution

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 03 - Full Stack Developer  
**Language**: Python 3.10+ (CLI)  
**Status**: New  
**Priority**: High  
**Duration**: 2 days  
**Dependencies**: #002 (Worker Base), #013 (Parameter Registration), #014 (API)

---

## Objective

Update the command-line interface to support worker-based task execution, providing user-friendly commands for task submission, status checking, and worker management.

---

## SOLID Principles Analysis

**SRP** ✅ - CLI layer only handles command parsing and display  
**OCP** ✅ - New commands can be added without modifying existing  
**DIP** ✅ - Depends on API/service layer abstractions

---

## Proposed Solution

### CLI Commands

**File**: `Sources/Content/Shorts/YouTube/src/cli/worker_cli.py` (NEW)

```python
"""CLI for worker-based YouTube scraping.

Provides user-friendly commands for task and worker management.
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from datetime import datetime

from ..api.worker_api import queue_db, TaskCreate
from ..core.parameter_schema import ParameterRegistry


console = Console()


@click.group()
def cli():
    """YouTube Worker CLI - Manage tasks and workers."""
    pass


@cli.group()
def task():
    """Task management commands."""
    pass


@task.command('create')
@click.option('--type', 'task_type', required=True, help='Task type (channel_scrape, trending_scrape, keyword_search)')
@click.option('--params', required=True, help='Task parameters as JSON')
@click.option('--priority', default=5, help='Task priority (1-10)')
def create_task(task_type: str, params: str, priority: int):
    """Create a new scraping task.
    
    Example:
        youtube-worker task create --type channel_scrape --params '{"channel_url": "https://youtube.com/@channel", "top_n": 50}'
    """
    try:
        # Parse parameters
        parameters = json.loads(params)
        
        # Validate
        registry = ParameterRegistry.get_instance()
        is_valid, prepared_params, errors = registry.validate_and_prepare(
            task_type,
            parameters
        )
        
        if not is_valid:
            console.print("[red]Parameter validation failed:[/red]")
            for error in errors:
                console.print(f"  [red]✗[/red] {error}")
            return
        
        # Create task via API
        # (In practice, would call API endpoint or use queue_db directly)
        conn = queue_db.get_connection()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO task_queue
            (task_type, parameters, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, 'queued', ?, ?)
        """, (task_type, str(prepared_params), priority, now, now))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        console.print(f"[green]✓[/green] Task created successfully!")
        console.print(f"  Task ID: {task_id}")
        console.print(f"  Type: {task_type}")
        console.print(f"  Priority: {priority}")
        
    except json.JSONDecodeError:
        console.print("[red]Error: Invalid JSON in --params[/red]")
    except Exception as e:
        console.print(f"[red]Error creating task: {e}[/red]")


@task.command('list')
@click.option('--status', help='Filter by status (queued, claimed, completed, failed)')
@click.option('--limit', default=50, help='Maximum number of tasks to show')
def list_tasks(status: str, limit: int):
    """List tasks.
    
    Example:
        youtube-worker task list --status queued
    """
    try:
        conn = queue_db.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, task_type, status, priority, created_at, claimed_by
            FROM task_queue
        """
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Display as table
        table = Table(title="Tasks")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="yellow")
        table.add_column("Priority", style="blue")
        table.add_column("Created", style="green")
        table.add_column("Claimed By")
        
        for row in rows:
            table.add_row(
                str(row['id']),
                row['task_type'],
                row['status'],
                str(row['priority']),
                row['created_at'][:19],  # Trim timestamp
                row['claimed_by'] or "-"
            )
        
        console.print(table)
        console.print(f"\nShowing {len(rows)} tasks")
        
    except Exception as e:
        console.print(f"[red]Error listing tasks: {e}[/red]")


@task.command('status')
@click.argument('task_id', type=int)
def task_status(task_id: int):
    """Show task status.
    
    Example:
        youtube-worker task status 123
    """
    try:
        conn = queue_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, task_type, status, priority, parameters,
                   created_at, claimed_at, completed_at, claimed_by,
                   error_message, result_data
            FROM task_queue
            WHERE id = ?
        """, (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            console.print(f"[red]Task {task_id} not found[/red]")
            return
        
        # Display task details
        console.print(f"\n[bold]Task #{row['id']}[/bold]")
        console.print(f"Type: {row['task_type']}")
        console.print(f"Status: [{_status_color(row['status'])}]{row['status']}[/]")
        console.print(f"Priority: {row['priority']}")
        console.print(f"\n[bold]Timeline:[/bold]")
        console.print(f"Created: {row['created_at']}")
        if row['claimed_at']:
            console.print(f"Claimed: {row['claimed_at']} (by {row['claimed_by']})")
        if row['completed_at']:
            console.print(f"Completed: {row['completed_at']}")
        
        console.print(f"\n[bold]Parameters:[/bold]")
        console.print(row['parameters'])
        
        if row['error_message']:
            console.print(f"\n[red][bold]Error:[/bold][/red]")
            console.print(f"[red]{row['error_message']}[/red]")
        
    except Exception as e:
        console.print(f"[red]Error getting task status: {e}[/red]")


def _status_color(status: str) -> str:
    """Get color for status."""
    colors = {
        'queued': 'yellow',
        'claimed': 'blue',
        'running': 'cyan',
        'completed': 'green',
        'failed': 'red',
        'cancelled': 'dim',
    }
    return colors.get(status, 'white')


@cli.group()
def worker():
    """Worker management commands."""
    pass


@worker.command('list')
def list_workers():
    """List active workers.
    
    Example:
        youtube-worker worker list
    """
    try:
        conn = queue_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT worker_id, last_heartbeat, tasks_processed,
                   tasks_failed, current_task_id, strategy
            FROM worker_heartbeats
            ORDER BY last_heartbeat DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Display as table
        table = Table(title="Workers")
        table.add_column("Worker ID", style="cyan")
        table.add_column("Last Heartbeat", style="green")
        table.add_column("Processed", style="blue")
        table.add_column("Failed", style="red")
        table.add_column("Current Task")
        table.add_column("Strategy")
        
        for row in rows:
            # Check if worker is active (heartbeat < 3 minutes old)
            last_hb = datetime.fromisoformat(row['last_heartbeat'].replace('Z', '+00:00'))
            age_minutes = (datetime.utcnow() - last_hb.replace(tzinfo=None)).total_seconds() / 60
            status = "🟢" if age_minutes < 3 else "🔴"
            
            table.add_row(
                f"{status} {row['worker_id']}",
                row['last_heartbeat'][:19],
                str(row['tasks_processed']),
                str(row['tasks_failed']),
                str(row['current_task_id']) if row['current_task_id'] else "-",
                row['strategy']
            )
        
        console.print(table)
        console.print(f"\nShowing {len(rows)} workers")
        
    except Exception as e:
        console.print(f"[red]Error listing workers: {e}[/red]")


@cli.command('stats')
def show_statistics():
    """Show system statistics.
    
    Example:
        youtube-worker stats
    """
    try:
        stats = queue_db.get_stats()
        
        console.print("\n[bold]YouTube Worker Statistics[/bold]\n")
        
        console.print("[bold]Tasks:[/bold]")
        status_counts = stats.get('status_counts', {})
        for status, count in status_counts.items():
            console.print(f"  {status.capitalize()}: {count}")
        
        console.print(f"\n[bold]Workers:[/bold]")
        console.print(f"  Active: {stats.get('active_workers', 0)}")
        
        console.print(f"\n[bold]Database:[/bold]")
        console.print(f"  Size: {stats.get('db_size_mb', 0):.2f} MB")
        
    except Exception as e:
        console.print(f"[red]Error getting statistics: {e}[/red]")


@cli.command('schema')
@click.argument('task_type', required=False)
def show_schema(task_type: str):
    """Show parameter schema for task type.
    
    Example:
        youtube-worker schema channel_scrape
    """
    try:
        registry = ParameterRegistry.get_instance()
        
        if task_type:
            # Show specific schema
            schema = registry.get_schema(task_type)
            if not schema:
                console.print(f"[red]Unknown task type: {task_type}[/red]")
                return
            
            console.print(f"\n[bold]{schema.description}[/bold]")
            console.print(f"Task Type: {schema.task_type}\n")
            
            table = Table(title="Parameters")
            table.add_column("Parameter", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Required", style="yellow")
            table.add_column("Default")
            table.add_column("Description")
            
            for param in schema.parameters:
                table.add_row(
                    param.name,
                    param.type.value,
                    "✓" if param.required else "",
                    str(param.default) if param.default is not None else "",
                    param.description
                )
            
            console.print(table)
            
            if schema.examples:
                console.print("\n[bold]Examples:[/bold]")
                for i, example in enumerate(schema.examples, 1):
                    console.print(f"  {i}. {json.dumps(example)}")
        
        else:
            # List all schemas
            schemas = registry.list_schemas()
            
            table = Table(title="Available Task Types")
            table.add_column("Task Type", style="cyan")
            table.add_column("Description")
            
            for schema in schemas:
                table.add_row(schema.task_type, schema.description)
            
            console.print(table)
            console.print("\nUse 'youtube-worker schema <task_type>' for details")
        
    except Exception as e:
        console.print(f"[red]Error showing schema: {e}[/red]")


if __name__ == '__main__':
    cli()
```

---

## Implementation Plan

### Day 1: Core Commands
- Setup Click CLI structure
- Implement task commands (create, list, status)
- Add rich formatting

### Day 2: Worker Commands & Polish
- Implement worker commands
- Add statistics command
- Add schema command
- Write CLI tests
- Documentation

---

## Acceptance Criteria

- [ ] All commands implemented
- [ ] Rich console formatting working
- [ ] Error handling comprehensive
- [ ] Help text clear and complete
- [ ] Windows compatibility verified
- [ ] Test coverage >80%

---

## CLI Commands Summary

**Tasks**:
- `youtube-worker task create` - Create task
- `youtube-worker task list` - List tasks
- `youtube-worker task status <id>` - Task details

**Workers**:
- `youtube-worker worker list` - List workers

**General**:
- `youtube-worker stats` - Show statistics
- `youtube-worker schema [type]` - Show schemas

---

## Complete CLI Usage Examples

### Basic Task Management

#### Creating Tasks

```bash
# Create a channel scraping task with basic parameters
youtube-worker task create \
  --type channel_scrape \
  --params '{"channel_url": "https://youtube.com/@TechReviews", "top_n": 50}'

# Output:
# ✓ Task created successfully!
#   Task ID: 123
#   Type: channel_scrape
#   Priority: 5

# Create with custom priority
youtube-worker task create \
  --type channel_scrape \
  --params '{"channel_url": "https://youtube.com/@NewsChannel", "top_n": 100, "max_age_days": 7}' \
  --priority 8

# Create trending scrape
youtube-worker task create \
  --type trending_scrape \
  --params '{"country": "US", "category": "gaming", "top_n": 100}' \
  --priority 6

# Create keyword search
youtube-worker task create \
  --type keyword_search \
  --params '{"query": "python tutorials", "top_n": 75, "sort_by": "views", "date_filter": "month"}'
```

#### Listing Tasks

```bash
# List all tasks (default: 50 most recent)
youtube-worker task list

# Output:
# ┏━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
# ┃ ID ┃ Type           ┃ Status  ┃ Priority ┃ Created             ┃ Claimed By ┃
# ┡━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
# │ 123│ channel_scrape │ queued  │ 5        │ 2024-11-13 08:00:00 │ -          │
# │ 124│ trending_scrape│ claimed │ 6        │ 2024-11-13 08:01:15 │ worker-001 │
# │ 125│ keyword_search │ running │ 7        │ 2024-11-13 08:02:30 │ worker-002 │
# └────┴────────────────┴─────────┴──────────┴─────────────────────┴────────────┘
# Showing 3 tasks

# List only queued tasks
youtube-worker task list --status queued

# List completed tasks with limit
youtube-worker task list --status completed --limit 20

# List failed tasks for debugging
youtube-worker task list --status failed --limit 10
```

#### Checking Task Status

```bash
# Get detailed status for a task
youtube-worker task status 123

# Output:
# Task #123
# Type: channel_scrape
# Status: completed
# Priority: 5
#
# Timeline:
# Created: 2024-11-13T08:00:00Z
# Claimed: 2024-11-13T08:00:15Z (by worker-001)
# Completed: 2024-11-13T08:05:30Z
#
# Parameters:
# {"channel_url": "https://youtube.com/@TechReviews", "top_n": 50}

# Check failed task to see error
youtube-worker task status 126

# Output with error:
# Task #126
# Type: channel_scrape
# Status: failed
# Priority: 5
#
# Timeline:
# Created: 2024-11-13T08:00:00Z
# Claimed: 2024-11-13T08:00:15Z (by worker-003)
# Completed: 2024-11-13T08:01:00Z
#
# Parameters:
# {"channel_url": "https://youtube.com/@InvalidChannel", "top_n": 50}
#
# Error:
# Channel not found or unavailable
```

### Worker Management

#### Listing Workers

```bash
# List all workers
youtube-worker worker list

# Output:
# ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
# ┃ Worker ID     ┃ Last Heartbeat      ┃ Processed ┃ Failed ┃ Current Task ┃ Strategy         ┃
# ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
# │ 🟢 worker-001 │ 2024-11-13 08:05:00 │ 45        │ 2      │ 124          │ channel_scrape   │
# │ 🟢 worker-002 │ 2024-11-13 08:04:55 │ 38        │ 1      │ 125          │ trending_scrape  │
# │ 🟢 worker-003 │ 2024-11-13 08:04:50 │ 52        │ 3      │ -            │ keyword_search   │
# │ 🔴 worker-004 │ 2024-11-13 07:55:00 │ 20        │ 0      │ -            │ channel_scrape   │
# └───────────────┴─────────────────────┴───────────┴────────┴──────────────┴──────────────────┘
# Showing 4 workers
#
# 🟢 = Active (heartbeat < 3 min ago)
# 🔴 = Inactive (heartbeat > 3 min ago)
```

### Schema and Documentation

#### Viewing Available Schemas

```bash
# List all available task types
youtube-worker schema

# Output:
# ┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Task Type       ┃ Description                             ┃
# ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
# │ channel_scrape  │ Scrape videos from YouTube channel     │
# │ trending_scrape │ Scrape videos from YouTube trending    │
# │ keyword_search  │ Search for videos by keywords          │
# └─────────────────┴─────────────────────────────────────────┘
#
# Use 'youtube-worker schema <task_type>' for details

# Get detailed schema for a specific task type
youtube-worker schema channel_scrape

# Output:
# Scrape videos from YouTube channel
# Task Type: channel_scrape
#
# ┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Parameter    ┃ Type    ┃ Required ┃ Default ┃ Description                ┃
# ┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
# │ channel_url  │ string  │ ✓        │         │ YouTube channel URL        │
# │ top_n        │ integer │          │ 10      │ Number of videos to scrape │
# │ max_age_days │ integer │          │         │ Maximum age in days        │
# └──────────────┴─────────┴──────────┴─────────┴────────────────────────────┘
#
# Examples:
#   1. {"channel_url": "https://youtube.com/@channel", "top_n": 50}
#   2. {"channel_url": "https://youtube.com/@channel", "top_n": 100, "max_age_days": 30}
```

### System Statistics

```bash
# Get system statistics
youtube-worker stats

# Output:
# YouTube Worker Statistics
#
# Tasks:
#   Queued: 15
#   Claimed: 3
#   Running: 2
#   Completed: 1,234
#   Failed: 23
#   Cancelled: 5
#
# Workers:
#   Active: 3
#
# Database:
#   Size: 125.50 MB
```

### Advanced Workflow Examples

#### Complete Scraping Workflow

```bash
# Step 1: Check available task types
youtube-worker schema

# Step 2: Get detailed parameters for chosen type
youtube-worker schema channel_scrape

# Step 3: Create the task
youtube-worker task create \
  --type channel_scrape \
  --params '{"channel_url": "https://youtube.com/@TechChannel", "top_n": 100, "max_age_days": 30}' \
  --priority 7

# Output: Task created successfully! Task ID: 150

# Step 4: Monitor task status
youtube-worker task status 150
# (repeat until completed)

# Step 5: Check system stats
youtube-worker stats
```

#### Batch Task Creation Script

```bash
#!/bin/bash
# batch_create_tasks.sh - Create multiple tasks from a list

CHANNELS=(
  "https://youtube.com/@TechReviews"
  "https://youtube.com/@NewsChannel"
  "https://youtube.com/@EducationHub"
)

for channel in "${CHANNELS[@]}"; do
  echo "Creating task for $channel"
  youtube-worker task create \
    --type channel_scrape \
    --params "{\"channel_url\": \"$channel\", \"top_n\": 50}" \
    --priority 5
  sleep 1
done

echo "All tasks created. Checking status..."
youtube-worker task list --status queued
```

#### Monitoring Script

```bash
#!/bin/bash
# monitor_workers.sh - Monitor worker health

while true; do
  clear
  echo "=== Worker Status ==="
  date
  echo ""
  youtube-worker worker list
  echo ""
  echo "=== Task Queue ==="
  youtube-worker task list --status queued --limit 10
  echo ""
  echo "=== Statistics ==="
  youtube-worker stats
  sleep 30
done
```

### Error Handling Examples

#### Invalid Parameters

```bash
# Missing required parameter
youtube-worker task create \
  --type channel_scrape \
  --params '{"top_n": 50}'

# Output:
# Parameter validation failed:
#   ✗ Required parameter missing: channel_url

# Value out of range
youtube-worker task create \
  --type channel_scrape \
  --params '{"channel_url": "https://youtube.com/@test", "top_n": 1000}'

# Output:
# Parameter validation failed:
#   ✗ top_n must be <= 500

# Invalid enum value
youtube-worker task create \
  --type keyword_search \
  --params '{"query": "test", "sort_by": "invalid_option"}'

# Output:
# Parameter validation failed:
#   ✗ sort_by must be one of ['relevance', 'date', 'views', 'rating']
```

#### Invalid JSON

```bash
# Malformed JSON
youtube-worker task create \
  --type channel_scrape \
  --params '{invalid json}'

# Output:
# Error: Invalid JSON in --params
```

#### Unknown Task Type

```bash
# Non-existent task type
youtube-worker task create \
  --type invalid_type \
  --params '{"param": "value"}'

# Output:
# Parameter validation failed:
#   ✗ Unknown task type: invalid_type
# Available types: channel_scrape, trending_scrape, keyword_search
```

### Power User Tips

```bash
# Use jq for advanced filtering
youtube-worker task list --status completed --limit 1000 | jq '.[] | select(.priority > 5)'

# Monitor specific worker
youtube-worker worker list | grep "worker-001"

# Count tasks by status
youtube-worker stats | grep "Tasks:" -A 10

# Quick task creation with defaults
alias yt-channel='youtube-worker task create --type channel_scrape --params'
yt-channel '{"channel_url": "https://youtube.com/@test"}'

# Export task list to CSV
youtube-worker task list --limit 1000 > tasks.json
jq -r '["id","type","status","created"] | @csv' tasks.json > tasks.csv

# Watch task progress in real-time
watch -n 5 'youtube-worker task status 123'
```

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/src/cli/__init__.py` - NEW
2. `Sources/Content/Shorts/YouTube/src/cli/worker_cli.py` - NEW
3. `Sources/Content/Shorts/YouTube/_meta/tests/test_worker_cli.py` - NEW

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker03 - Full Stack Developer  
**Estimated Start**: Week 3, Day 2  
**Estimated Completion**: Week 3, Day 3
