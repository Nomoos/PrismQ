# PrismQ Manual Backlog Source

**Manage manual idea backlog for the PrismQ content generation ecosystem**

## Overview

The Manual Backlog Source is part of the PrismQ.IdeaInspiration ecosystem, providing tools to manually create, update, and manage ideas through a command-line interface. This module enables quick idea capture, status tracking, and backlog management.

## Features

- **Manual Idea Entry**: Quick CLI-based idea creation
- **Full CRUD Operations**: Create, read, update ideas
- **Status Tracking**: Track idea lifecycle (new, in_progress, used, archived)
- **Priority Management**: Set and update priority levels
- **Tag Management**: Organize ideas with tags
- **Assignment Tracking**: Track who created and who's assigned to ideas
- **IdeaInspiration Format**: Standardized data format
- **SQLite Storage**: Efficient local database storage

## Installation

1. Install dependencies:
```bash
pip install -e .
```

2. For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Add a New Idea

```bash
manual-backlog add "Video idea title" -d "Description" -p high
```

### Add with Full Details

```bash
manual-backlog add "Complete idea" \
  --description "Full description here" \
  --notes "Additional notes" \
  --category content \
  --priority high \
  --tags "tag1,tag2,tag3" \
  --assigned-to "Jane"
```

### List Ideas

```bash
manual-backlog list --status new
manual-backlog list --category content --limit 10
```

### Update an Idea

```bash
manual-backlog update manual_abc123 --status in_progress
manual-backlog update manual_abc123 --priority high --assigned-to Jane
```

### Mark as Used

```bash
manual-backlog mark-used manual_abc123
```

### Show Idea Details

```bash
manual-backlog show manual_abc123
```

### View Statistics

```bash
manual-backlog stats
```

## Commands

### add

Add a new idea to the backlog.

```bash
manual-backlog add TITLE [OPTIONS]

Arguments:
  TITLE                  Idea title (required)

Options:
  -d, --description TEXT  Idea description
  -n, --notes TEXT        Additional notes
  -c, --category TEXT     Category classification
  -p, --priority [high|medium|low|critical|urgent]
  -s, --status [new|in_progress|used|archived]
  -t, --tags TEXT         Comma-separated tags
  --created-by TEXT       Creator name
  --assigned-to TEXT      Assignee name
  -e, --env-file PATH     Path to .env file
  --no-interactive        Disable interactive prompts
```

### update

Update an existing idea.

```bash
manual-backlog update SOURCE_ID [OPTIONS]

Arguments:
  SOURCE_ID              ID of the idea to update

Options:
  --title TEXT           Update title
  -d, --description TEXT Update description
  -n, --notes TEXT       Update notes
  -c, --category TEXT    Update category
  -p, --priority [high|medium|low|critical|urgent]
  -s, --status [new|in_progress|used|archived]
  -t, --tags TEXT        Update tags
  --assigned-to TEXT     Update assignee
```

### mark-used

Mark an idea as used (sets status to 'used' and records timestamp).

```bash
manual-backlog mark-used SOURCE_ID
```

### list

List ideas from the backlog.

```bash
manual-backlog list [OPTIONS]

Options:
  -s, --status TEXT        Filter by status
  -c, --category TEXT      Filter by category
  -l, --limit INTEGER      Limit number of results
  -f, --format [table|json] Output format (default: table)
```

### show

Show detailed information about a specific idea.

```bash
manual-backlog show SOURCE_ID
```

### stats

Show backlog statistics (counts by status, category, priority).

```bash
manual-backlog stats
```

## Configuration

Configuration is managed through environment variables in a `.env` file:

```env
# Database path
MANUAL_BACKLOG_DATABASE_PATH=/path/to/manual_backlog.db

# Default values
MANUAL_BACKLOG_DEFAULT_PRIORITY=medium
MANUAL_BACKLOG_DEFAULT_STATUS=new
MANUAL_BACKLOG_DEFAULT_CATEGORY=general
MANUAL_BACKLOG_DEFAULT_USER=your_username
```

## Data Model

Ideas are stored in IdeaInspiration format:

```json
{
  "source": "manual_backlog",
  "source_id": "manual_abc123...",
  "idea": {
    "title": "Idea title",
    "description": "Idea description",
    "notes": "Additional notes",
    "category": "category_name",
    "priority": "high"
  },
  "metadata": {
    "status": "new",
    "created_by": "user_name",
    "assigned_to": "assignee_name",
    "tags": ["tag1", "tag2"]
  },
  "tracking": {
    "created_at": "2025-01-15T10:00:00Z",
    "modified_at": "2025-01-15T10:00:00Z",
    "used_at": null,
    "age_days": 0
  },
  "universal_metrics": {
    "priority_score": 8.0,
    "actionability": 5.0
  }
}
```

## Architecture

Following SOLID principles:

- **Single Responsibility**: Separate modules for management, database, config
- **Open/Closed**: Plugin-based architecture for extensibility
- **Liskov Substitution**: Implements SourcePlugin interface
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Depends on abstractions (SourcePlugin)

```
ManualBacklog/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # SQLite database operations
│   │   └── idea_manager.py      # Idea creation and management
│   └── plugins/
│       ├── __init__.py          # Plugin base class
│       └── manual_entry_plugin.py # Manual entry implementation
└── _meta/
    └── tests/                   # Unit tests
```

## Testing

Run tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

## Integration

This module integrates with:

- **ConfigLoad**: Centralized configuration management
- **Model**: IdeaInspiration data model
- **Classification**: Content categorization
- **Scoring**: Quality evaluation

## Use Cases

- **Quick Capture**: Rapidly capture ideas as they come
- **Backlog Management**: Organize and prioritize ideas
- **Status Tracking**: Track idea lifecycle from new to used
- **Team Collaboration**: Assign ideas to team members
- **Progress Monitoring**: View statistics on backlog status

## Workflow Example

```bash
# Add a new high-priority idea
manual-backlog add "Create tutorial video" \
  -d "Step-by-step tutorial on topic X" \
  -c content \
  -p high \
  -t "tutorial,video,education"

# List new ideas
manual-backlog list --status new

# Start working on an idea
manual-backlog update manual_abc123 --status in_progress --assigned-to John

# Complete and mark as used
manual-backlog mark-used manual_abc123

# View statistics
manual-backlog stats
```

## Target Platform

Optimized for:
- **OS**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ

## Part of PrismQ Ecosystem

- **PrismQ.IdeaCollector**: CLI tool for idea collection
- **StoryGenerator**: Automated story and video generation
- **PrismQ.IdeaInspiration**: Central hub for content ideas
