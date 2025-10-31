# TrendsFileSource

**Import trends from CSV/JSON files**

## Overview

TrendsFileSource allows importing trend signals from CSV or JSON files. This source is part of the PrismQ.IdeaInspiration ecosystem and provides a way to manually curate or import external trend data.

## Features

- ✅ Imports trends from CSV files
- ✅ Imports trends from JSON files
- ✅ Validates and normalizes imported data
- ✅ Universal signal metrics (trend strength, virality score)
- ✅ SQLite database with deduplication
- ✅ CLI interface for easy management
- ✅ SOLID architecture with plugin system
- ✅ Comprehensive test coverage
- ✅ Flexible schema support

## Installation

```bash
# Navigate to this directory
cd Sources/Signals/Trends/TrendsFile

# Install dependencies
pip install -e .
```

## Dependencies

- `pandas` - Data processing
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_PATH` - Path to SQLite database (default: `signals_trends_file.db`)
- `MAX_RESULTS` - Maximum trends per import (default: 25)
- `RETRY_DELAY_SECONDS` - Delay between operations (default: 2)

## Usage

### CLI Commands

#### Import Trend Signals
```bash
# Import from CSV file
python -m src.cli scrape --file trends.csv --format csv

# Import from JSON file
python -m src.cli scrape --file trends.json --format json

# Import with custom limit
python -m src.cli scrape --file trends.csv --limit 10
```

#### List Signals
```bash
# List all signals
python -m src.cli list

# List with limit
python -m src.cli list --limit 20
```

#### Show Statistics
```bash
python -m src.cli stats
```

#### Export Data
```bash
# Export to CSV
python -m src.cli export trends.csv --format csv

# Export to JSON
python -m src.cli export trends.json --format json
```

#### Clear Database
```bash
python -m src.cli clear
```

## File Formats

### CSV Format
```csv
name,volume,velocity,description,tags
"Trending Topic 1",1000000,85.5,"Description of trend","tag1,tag2,tag3"
"Trending Topic 2",500000,72.3,"Another trend","tag4,tag5"
```

### JSON Format
```json
[
  {
    "name": "Trending Topic 1",
    "volume": 1000000,
    "velocity": 85.5,
    "description": "Description of trend",
    "tags": ["tag1", "tag2", "tag3"]
  },
  {
    "name": "Trending Topic 2",
    "volume": 500000,
    "velocity": 72.3,
    "description": "Another trend",
    "tags": ["tag4", "tag5"]
  }
]
```

## Architecture

```
TrendsFile/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/
│       ├── __init__.py             # SignalPlugin base class
│       └── trends_file_plugin.py   # File import implementation
├── tests/                          # Test suite
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e .[dev]

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

### Code Quality

This implementation follows SOLID principles:
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extensible through plugins
- **Liskov Substitution**: All plugins interchangeable
- **Interface Segregation**: Minimal plugin interface
- **Dependency Inversion**: Depends on abstractions

## License

Proprietary - Part of PrismQ.IdeaInspiration ecosystem

## Status

✅ **IMPLEMENTED** - Fully functional with CSV/JSON support
