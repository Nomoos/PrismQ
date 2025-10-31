# App Store Top Charts Source

PrismQ module for gathering app trends from iOS and Android app stores as part of the AI-powered content generation ecosystem.

## Overview

This module scrapes top app charts from Google Play Store and Apple App Store to identify trending applications, consumer interests in digital products, and emerging app categories. It transforms app store data into structured insights for content creation.

## Features

- **Multi-Platform Support**: Scrape from both Google Play and Apple App Store
- **Category Tracking**: Monitor top apps across multiple categories
- **App Metadata**: Capture titles, developers, ratings, reviews, and installs
- **Ranking Data**: Track category rankings and positions
- **Universal Metrics**: Standardized commerce metrics for digital products
- **SQLite Storage**: Local database with automatic deduplication
- **CLI Interface**: Easy-to-use command-line tools

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=sqlite:///db.s3db

# App Store Configuration
APP_STORE_COUNTRY=us
APP_STORE_CATEGORIES=games,productivity,social-networking,entertainment
APP_STORE_MAX_APPS=50
APP_STORE_DELAY_SECONDS=1

# Google Play Configuration
GOOGLE_PLAY_COUNTRY=us
GOOGLE_PLAY_LANGUAGE=en
```

## Usage

### Scrape App Charts

```bash
# Scrape both platforms
python -m src.cli scrape

# Scrape Google Play only
python -m src.cli scrape --platform google

# Scrape Apple App Store only
python -m src.cli scrape --platform apple

# Using installed script
app-store-top-charts-source scrape
```

### List Apps

```bash
# List all apps
python -m src.cli list

# List apps from specific category
python -m src.cli list --category games

# Limit results
python -m src.cli list --limit 10
```

### View Statistics

```bash
python -m src.cli stats
```

### Clear Database

```bash
python -m src.cli clear
```

## Data Model

Apps are stored with the following structure:

```python
{
    'source': 'google_play_top_charts' or 'apple_app_store_top_charts',
    'source_id': 'app_package_or_id',
    'product': {
        'name': 'App Name',
        'brand': 'Developer Name',
        'category': 'games',
        'price': 0.0,  # or actual price
        'currency': 'USD'
    },
    'metrics': {
        'category_rank': 5,
        'rating': 4.7,
        'review_count': 50000,
    },
    'platform_specific': {
        'platform': 'google_play' or 'apple_app_store',
        'installs': '10,000,000+',
        'content_rating': 'Everyone',
        # ... more platform-specific data
    }
}
```

## Architecture

Following SOLID principles with plugin-based architecture:

```
AppStoreTopCharts/
├── src/
│   ├── cli.py                       # Command-line interface
│   ├── core/
│   │   ├── config.py                # Configuration management
│   │   ├── database.py              # Database operations
│   │   ├── metrics.py               # Universal commerce metrics
│   │   └── commerce_processor.py   # Data transformation
│   └── plugins/
│       ├── __init__.py              # Plugin base class
│       ├── google_play_plugin.py    # Google Play scraper
│       └── apple_app_store_plugin.py # Apple App Store scraper
├── _meta/
│   └── tests/                       # Unit tests
├── pyproject.toml                   # Project metadata
├── requirements.txt                 # Dependencies
└── README.md                        # This file
```

## Scraping Libraries

### Google Play Store
Uses `google-play-scraper` library:
- No API key required
- Unofficial scraping library
- Provides detailed app information
- Rate limiting recommended

### Apple App Store
Uses `app-store-scraper` library and RSS feeds:
- No API key required for RSS feeds
- Unofficial scraping library for reviews
- RSS feeds provide official top charts data
- Respects Apple's public data access

## Important Notes

### Terms of Service

⚠️ **Always respect platform Terms of Service:**

1. **Rate Limiting**: Implement appropriate delays between requests
2. **Data Usage**: Use scraped data responsibly
3. **Caching**: Cache results to minimize requests
4. **Attribution**: Provide proper attribution when using data

### Production Considerations

For production use:

1. **Monitor API Changes**: Unofficial libraries may break with platform updates
2. **Error Handling**: Implement robust error handling and retries
3. **Data Freshness**: Schedule regular scraping runs
4. **Compliance**: Ensure compliance with platform policies

## Universal Metrics

The module calculates standardized metrics for cross-platform analysis:

- **Popularity Score** (0-10): Based on review count and rating
- **Consumer Interest** (0-10): Overall interest indicator
- **Category Dominance**: Ranking within category

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Category Mappings

### Common Categories

- **games**: Mobile games
- **productivity**: Productivity tools
- **social-networking**: Social media apps
- **entertainment**: Entertainment apps
- **education**: Educational apps
- **tools**: Utility apps
- **communication**: Communication apps

## License

Proprietary - Part of the PrismQ ecosystem

## Related Modules

- **AmazonBestsellersSource**: Physical product trends
- **EtsyTrendingSource**: Handmade and vintage product trends
- **PrismQ.IdeaInspiration.Model**: Standardized idea format
- **PrismQ.IdeaInspiration.Classification**: Idea categorization

## Support

For issues and questions, please refer to the main PrismQ.IdeaInspiration repository.
