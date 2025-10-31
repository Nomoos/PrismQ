# EntertainmentReleases Source

**PrismQ module for gathering event inspirations from movie, TV, game, and music releases**

## Overview

EntertainmentReleases is a PrismQ source module that collects upcoming and recent entertainment releases from various media types to identify content opportunities around these releases.

## Features

- Scrapes entertainment releases from TMDB API (The Movie Database)
- Supports movies and TV shows
- Calculates content windows (pre/post release coverage)
- Assigns significance and importance scores
- Estimates audience interest and viewership
- Stores in SQLite database with deduplication
- Unified event signal format for cross-platform compatibility

## Installation

1. Navigate to this directory:
   ```bash
   cd Sources/Events/EntertainmentReleases
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get a free TMDB API key:
   - Sign up at https://www.themoviedb.org/
   - Go to Settings → API
   - Request an API key (free for non-commercial use)

4. Copy `.env.example` to `.env` and add your API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your TMDB_API_KEY
   ```

## Usage

### Scrape Upcoming Movies

```bash
python -m src.cli scrape --media-type movie
```

### Scrape TV Shows

```bash
python -m src.cli scrape --media-type tv
```

### Scrape by Region

```bash
python -m src.cli scrape --region US --max 30
python -m src.cli scrape --region GB --max 30
```

### List Collected Events

```bash
python -m src.cli list --limit 20
```

### View Statistics

```bash
python -m src.cli stats
```

### Clear Database

```bash
python -m src.cli clear
```

## Configuration

Edit `.env` file:

```env
# Database path
ENTERTAINMENT_RELEASES_DB_PATH=/path/to/data/entertainment_releases.db

# TMDB API key (required)
TMDB_API_KEY=your_api_key_here

# Default media type (movie or tv)
ENTERTAINMENT_DEFAULT_MEDIA_TYPE=movie

# Default region (ISO 3166-1 code)
ENTERTAINMENT_DEFAULT_REGION=US

# Max releases to fetch
ENTERTAINMENT_MAX_RELEASES=50
```

## Supported Media Types

**Currently Supported:**
- Movies (via TMDB)
- TV Shows (via TMDB)

**Future Support:**
- Video Games (via IGDB API)
- Music Albums (via MusicBrainz API)

## Event Signal Format

Each entertainment release is transformed into a unified event signal:

```python
{
    'source': 'tmdb',
    'source_id': '123456',
    'event': {
        'name': 'Spider-Man: Beyond the Spider-Verse',
        'type': 'movie_release',
        'date': '2025-03-29',
        'recurring': False,
        'recurrence_pattern': None
    },
    'significance': {
        'scope': 'worldwide',
        'importance': 'blockbuster',
        'audience_size_estimate': 500000000
    },
    'content_window': {
        'pre_event_days': 30,
        'post_event_days': 14,
        'peak_day': '2025-03-29'
    },
    'metadata': {
        'media_type': 'movie',
        'genre': ['Animation', 'Action', 'Adventure'],
        'rating': 8.5,
        'studio': 'Sony Pictures Animation'
    },
    'universal_metrics': {
        'significance_score': 10.0,
        'content_opportunity': 8.8,
        'audience_interest': 9.5
    }
}
```

## API Information

This module uses [The Movie Database (TMDB) API](https://www.themoviedb.org/documentation/api):
- Free tier available for non-commercial use
- Comprehensive movie and TV show data
- Regularly updated with new releases
- Excellent metadata and image resources

## Architecture

```
EntertainmentReleases/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # SQLite operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── event_processor.py     # Event processing
│   └── plugins/
│       ├── __init__.py             # Plugin base class
│       └── tmdb_plugin.py          # TMDB API plugin
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
black src/
flake8 src/
mypy src/
```

## Related Modules

- **Sources/Events/CalendarHolidays** - Holiday events source
- **Sources/Events/SportsHighlights** - Sports events source
- **Model** - Core IdeaInspiration data model
- **Classification** - Content categorization
- **Scoring** - Content evaluation

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
