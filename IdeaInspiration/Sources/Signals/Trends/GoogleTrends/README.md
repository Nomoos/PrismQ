# Google Trends Source Module

**Platform-optimized Google Trends signal scraper for early trend detection**

## Overview

This module provides powerful tools for scraping Google Trends data with comprehensive trend metrics extraction and universal metrics collection. It follows SOLID principles for better maintainability and extensibility.

## Architecture (SOLID Principles)

The module follows SOLID design principles:

### Single Responsibility Principle (SRP)
- `Config`: Handles configuration management only
- `Database`: Manages database operations only
- `UniversalMetrics`: Calculates and normalizes metrics only
- `SignalProcessor`: Transforms data to unified signal format only
- `GoogleTrendsPlugin`: Handles Google Trends API interaction only

### Open/Closed Principle (OCP)
- `SignalPlugin` is an abstract base class open for extension
- New scrapers can be added by extending `SignalPlugin` without modifying existing code

### Liskov Substitution Principle (LSP)
- `GoogleTrendsPlugin` can substitute `SignalPlugin`

### Interface Segregation Principle (ISP)
- `SignalPlugin` provides a minimal interface with only required methods: `scrape()` and `get_source_name()`

### Dependency Inversion Principle (DIP)
- High-level modules (CLI) depend on abstractions (`SignalPlugin`) not concrete implementations
- Dependencies are injected through constructors (Config, Database)

## Module Structure

```
GoogleTrends/
├── src/
│   ├── __init__.py                 # Main module exports
│   ├── cli.py                      # Command-line interface
│   ├── core/                       # Core utilities (SRP)
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics calculation
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/                    # Scraper plugins (OCP, LSP, ISP)
│       ├── __init__.py             # SignalPlugin base class
│       └── google_trends_plugin.py # Google Trends scraper
├── tests/                          # Unit and integration tests
├── _meta/                          # Module metadata
│   └── docs/                       # Comprehensive documentation
├── scripts/                        # Utility scripts
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Package configuration
├── .env.example                    # Environment configuration template
└── README.md                       # This file
```

## Features

### Signal Collection
- **Trending Searches**: Current trending queries by region
- **Keyword Tracking**: Monitor specific keywords over time
- **Related Queries**: Discover related search terms
- **Temporal Metrics**: Track velocity and acceleration
- **Universal Metrics**: Standardized metrics for cross-platform analysis

### Key Capabilities

- **Comprehensive Metadata**: Query, region, interest scores, temporal data
- **Universal Metrics**: Trend strength, virality score, velocity, acceleration
- **Deduplication**: Prevents duplicate entries using (source, source_id) constraint
- **SQLite Storage**: Persistent storage with complete metadata
- **Signal Transform**: Compatible with unified signal format

## Installation

### Prerequisites

- Python 3.10 or higher
- Windows OS (recommended) or Linux
- Internet connection for Google Trends API

### Quick Start

```bash
# Navigate to the GoogleTrends module
cd Sources/Signals/Trends/GoogleTrends

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# (Region, timeframe, database path, etc.)

# Run a scrape command
python -m src.cli scrape
```

## Usage

### Command Line Interface

```bash
# Scrape trending searches
python -m src.cli scrape

# Scrape with specific keywords
python -m src.cli scrape --keywords "AI" --keywords "machine learning"

# List collected signals
python -m src.cli list --limit 10

# View statistics
python -m src.cli stats

# Export to JSON
python -m src.cli export --output signals.json

# Clear database
python -m src.cli clear
```

### Python API

```python
from src import Config, Database, GoogleTrendsPlugin, UniversalMetrics

# Initialize components (Dependency Injection)
config = Config()
db = Database(config.database_path)

# Use the scraper plugin (Polymorphism via SignalPlugin)
plugin = GoogleTrendsPlugin(config)
signals = plugin.scrape(keywords=["startup ideas", "AI trends"])

# Process metrics
for signal in signals:
    metrics = UniversalMetrics.from_google_trends(signal['metrics'])
    print(f"Trend strength: {metrics.trend_strength}/10")
    print(f"Virality score: {metrics.virality_score}/10")
    
    # Save to database
    db.insert_signal(
        source=plugin.get_source_name(),
        source_id=signal['source_id'],
        signal_type=signal['signal_type'],
        name=signal['name'],
        description=signal['description'],
        tags=','.join(signal['tags']),
        metrics=signal['metrics'],
        temporal=signal['temporal'],
        universal_metrics=metrics.to_dict()
    )
```

## Configuration

Configuration is managed through `.env` file. See `.env.example` for all available options:

```bash
# Database Configuration
DATABASE_URL=sqlite:///google_trends.db

# Google Trends Configuration
GOOGLE_TRENDS_REGION=US
GOOGLE_TRENDS_LANGUAGE=en-US
GOOGLE_TRENDS_TIMEFRAME=now 7-d
GOOGLE_TRENDS_MAX_RESULTS=25

# Scraping Configuration
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=5
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/
```

## Design Patterns Used

1. **Abstract Factory Pattern**: `SignalPlugin` as factory interface
2. **Strategy Pattern**: Different scraping strategies via plugins
3. **Dependency Injection**: Config and Database injected into components
4. **Repository Pattern**: Database abstraction for data access
5. **Builder Pattern**: Config builder for environment setup

## Integration with PrismQ Ecosystem

This module integrates with the broader PrismQ.IdeaInspiration ecosystem for signal-based content generation.

## Performance Considerations

- **API Rate Limiting**: Google Trends has unofficial rate limits (use delays)
- **Batch Processing**: Process keywords in batches of 5
- **Caching**: Config and database connections are reused
- **Memory Management**: Large datasets are processed iteratively

## Target Platform

- **OS**: Windows (primary), Linux (CI/testing)
- **GPU**: NVIDIA RTX 5090 (for future AI enhancements)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## License

This repository is proprietary software. All Rights Reserved - Copyright (c) 2025 PrismQ

---

**Part of the PrismQ.IdeaInspiration Ecosystem** - AI-powered content generation platform
