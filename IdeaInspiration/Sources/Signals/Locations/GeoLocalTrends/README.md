# GeoLocalTrendsSource

**Location-based trending content**

## Overview

GeoLocalTrendsSource collects location-based trend signals to identify regional content trends. This source is part of the PrismQ.IdeaInspiration ecosystem and provides geographic insights for localized content strategy.

## Features

- ✅ Collects location-based trending content
- ✅ Tracks regional trend variations
- ✅ Calculates trend velocity and acceleration
- ✅ Universal signal metrics (trend strength, virality score)
- ✅ SQLite database with deduplication
- ✅ CLI interface for easy management
- ✅ SOLID architecture with plugin system
- ✅ Comprehensive test coverage
- ✅ Stub mode for testing

## Installation

```bash
# Navigate to this directory
cd Sources/Signals/Locations/GeoLocalTrends

# Install dependencies
pip install -e .
```

## Dependencies

- `pytrends` - Google Trends with location data
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_PATH` - Path to SQLite database (default: `signals_geo_local_trends.db`)
- `REGIONS` - Comma-separated list of regions (default: `US,GB,CA,AU`)
- `MAX_RESULTS` - Maximum trends per location (default: 25)
- `TIMEFRAME_DAYS` - Time range for trends (default: 7)
- `RETRY_DELAY_SECONDS` - Delay between API calls (default: 2)

## Usage

### CLI Commands

#### Scrape Location Signals
```bash
# Scrape trends for all configured regions
python -m src.cli scrape

# Scrape with custom limit
python -m src.cli scrape --limit 10

# Scrape specific regions
python -m src.cli scrape --regions "US,GB,JP"
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
python -m src.cli export locations.csv --format csv

# Export to JSON
python -m src.cli export locations.json --format json
```

#### Clear Database
```bash
python -m src.cli clear
```

## Operational Modes

### Production Mode (with pytrends)
Requires pytrends installation:
```bash
pip install pytrends
```

### Stub Mode (without pytrends)
Runs with sample data for testing and development.

## Architecture

```
GeoLocalTrends/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/
│       ├── __init__.py             # SignalPlugin base class
│       └── geo_local_trends_plugin.py  # Location-based implementation
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

✅ **IMPLEMENTED** - Fully functional with stub mode support
