# PrismQ CSV Import Source

**Import idea inspirations from CSV/Excel files into the PrismQ content generation ecosystem**

## Overview

The CSV Import Source is part of the PrismQ.IdeaInspiration ecosystem, providing tools to import and manage ideas from CSV and Excel files. This module enables bulk data migration, manual idea entry via spreadsheets, and integration of existing idea backlogs.

## Features

- **Flexible CSV/Excel Import**: Support for both CSV and Excel (.xlsx) files
- **Intelligent Column Mapping**: Automatically recognizes various column name formats
- **Data Validation**: Validates file structure before import
- **Batch Processing**: Import multiple files at once
- **Deduplication**: Automatically prevents duplicate ideas
- **Status Tracking**: Track idea status, priority, and usage
- **IdeaInspiration Format**: Transforms data to standardized format
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

### Import a Single CSV File

```bash
csv-import import-file data/ideas.csv
```

### Import Multiple Files from Directory

```bash
csv-import import-directory -d data/imports/
```

### Validate CSV Structure

```bash
csv-import validate data/ideas.csv
```

### List Imported Ideas

```bash
csv-import list --status new --limit 10
```

### View Statistics

```bash
csv-import stats
```

## CSV File Format

### Required Columns

- **title**: Idea title (required)

### Optional Columns

The importer recognizes various column names:

- **description/desc/details**: Idea description
- **category/type/topic**: Category classification
- **priority/importance**: Priority level (high/medium/low)
- **tags/labels/keywords**: Comma-separated tags
- **status/state**: Status (new/in_progress/used/archived)
- **notes/comments**: Additional notes
- **created_by/author**: Creator name
- **assigned_to/assignee**: Assignee name

### Example CSV

```csv
title,description,category,priority,tags,status,notes
"Video idea 1","Description here","content","high","tag1,tag2","new","Additional notes"
"Video idea 2","Another description","marketing","medium","tag3","in_progress","More notes"
```

### Example Excel

Excel files (.xlsx) are also supported with the same column structure.

## Commands

### import-file

Import ideas from a single CSV or Excel file.

```bash
csv-import import-file FILE_PATH [OPTIONS]

Options:
  -e, --env-file PATH      Path to .env file
  --no-interactive         Disable interactive prompts
  -b, --batch-id TEXT      Optional batch identifier
```

### import-directory

Import all CSV/Excel files from a directory.

```bash
csv-import import-directory [OPTIONS]

Options:
  -d, --directory PATH     Directory containing files (required)
  -p, --pattern TEXT       File pattern (default: *.csv)
  -e, --env-file PATH      Path to .env file
  --no-interactive         Disable interactive prompts
```

### validate

Validate CSV/Excel file structure without importing.

```bash
csv-import validate FILE_PATH
```

### list

List imported ideas from the database.

```bash
csv-import list [OPTIONS]

Options:
  -s, --status TEXT        Filter by status
  -c, --category TEXT      Filter by category
  -l, --limit INTEGER      Limit number of results
  -f, --format [table|json] Output format (default: table)
```

### stats

Show database statistics.

```bash
csv-import stats [OPTIONS]
```

## Configuration

Configuration is managed through environment variables in a `.env` file:

```env
# Database path
CSV_IMPORT_DATABASE_PATH=/path/to/csv_import.db

# Default CSV file (optional)
CSV_IMPORT_DEFAULT_PATH=/path/to/default.csv

# CSV parsing options
CSV_IMPORT_DELIMITER=,
CSV_IMPORT_ENCODING=utf-8

# Batch import settings
CSV_IMPORT_BATCH_SIZE=100

# Default values
CSV_IMPORT_DEFAULT_PRIORITY=medium
CSV_IMPORT_DEFAULT_STATUS=new
CSV_IMPORT_DEFAULT_CATEGORY=general
```

## Data Model

Ideas are stored in IdeaInspiration format:

```json
{
  "source": "csv_import",
  "source_id": "csv_abc123...",
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

- **Single Responsibility**: Separate modules for parsing, database, config
- **Open/Closed**: Plugin-based architecture for extensibility
- **Liskov Substitution**: Implements SourcePlugin interface
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Depends on abstractions (SourcePlugin)

```
CSVImport/
├── src/
│   ├── cli.py                  # Command-line interface
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # SQLite database operations
│   │   └── csv_parser.py      # CSV parsing and transformation
│   └── plugins/
│       ├── __init__.py        # Plugin base class
│       └── csv_import_plugin.py # CSV import implementation
└── _meta/
    └── tests/                 # Unit tests
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

- **Data Migration**: Import existing idea backlogs
- **Bulk Entry**: Create multiple ideas via spreadsheet
- **Team Collaboration**: Share ideas via CSV files
- **External Integration**: Import from other tools
- **Backup/Restore**: Export and re-import data

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
