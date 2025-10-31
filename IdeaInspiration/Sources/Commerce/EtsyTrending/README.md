# Etsy Trending Source

PrismQ module for gathering trending products from Etsy marketplace as part of the AI-powered content generation ecosystem.

## Overview

This module scrapes trending product data from Etsy to identify popular handmade, vintage, and craft supply items. It transforms marketplace data into structured insights that reveal consumer interests in creative and artisan products.

## Features

- **Multi-Category Tracking**: Monitor trending products across craft categories
- **Handmade Focus**: Capture unique, handcrafted product trends
- **Shop Metadata**: Track seller information and shop performance
- **Product Details**: Capture materials, pricing, ratings, and reviews
- **Universal Metrics**: Standardized commerce metrics for marketplace products
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

# Etsy Configuration
ETSY_API_KEY=                     # Optional - for Etsy Open API access
ETSY_CATEGORIES=jewelry,home-living,art,craft-supplies
ETSY_MAX_LISTINGS=50
ETSY_TRENDING_KEYWORDS=trending,popular,bestseller
ETSY_DELAY_SECONDS=1
```

## Usage

### Scrape Trending Products

```bash
# Using Python module
python -m src.cli scrape

# Or using installed script
etsy-trending-source scrape
```

### List Products

```bash
# List all products
python -m src.cli list

# List products from specific category
python -m src.cli list --category jewelry

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

Products are stored with the following structure:

```python
{
    'source': 'etsy_trending',
    'source_id': 'listing_id',
    'product': {
        'name': 'Product Name',
        'brand': 'Shop Name',  # Seller shop name
        'category': 'jewelry',
        'price': 45.99,
        'currency': 'USD'
    },
    'seller': {
        'name': 'Shop Name',
        'rating': 4.8,
        'feedback_count': 2000  # Total shop sales
    },
    'metrics': {
        'rating': 4.7,
        'review_count': 500
    },
    'platform_specific': {
        'platform': 'etsy',
        'is_handmade': True,
        'is_vintage': False,
        'is_supply': False,
        'who_made': 'i_did',
        'when_made': '2020s',
        'materials': ['wood', 'cotton'],
        'favorers': 100,
        'views': 5000
    }
}
```

## Architecture

Following SOLID principles with plugin-based architecture:

```
EtsyTrending/
├── src/
│   ├── cli.py                     # Command-line interface
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database operations
│   │   ├── metrics.py             # Universal commerce metrics
│   │   └── commerce_processor.py # Data transformation
│   └── plugins/
│       ├── __init__.py            # Plugin base class
│       └── etsy_trending.py       # Etsy scraper plugin
├── _meta/
│   └── tests/                     # Unit tests
├── pyproject.toml                 # Project metadata
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

## Important Notes

### Etsy API and Terms of Service

⚠️ **This module currently uses mock data for demonstration purposes.**

For production use, you should:

1. **Use Etsy Open API v3** (requires API key from Etsy developer account)
2. **Implement OAuth 2.0** authentication
3. **Respect robots.txt** and Terms of Service
4. **Implement rate limiting** per API guidelines

### API Integration

To use the real Etsy Open API:

1. Create an [Etsy Developer Account](https://www.etsy.com/developers/)
2. Register your application
3. Obtain API key and OAuth credentials
4. Implement the `scrape_with_api()` method
5. Follow [API documentation](https://developers.etsy.com/documentation/)

### Etsy Open API v3

- Requires OAuth 2.0 authentication
- Rate limits apply (varies by endpoint)
- Some data requires specific scopes
- API provides comprehensive product and shop data

## Categories

Common Etsy categories:

- **jewelry**: Handmade and vintage jewelry
- **home-living**: Home decor and living items
- **art**: Art and collectibles
- **craft-supplies**: Materials and tools
- **clothing**: Handmade clothing and accessories
- **toys-games**: Handmade toys and games
- **weddings**: Wedding-related items
- **paper-party-supplies**: Cards, invitations, party supplies

## Universal Metrics

The module calculates standardized metrics for cross-platform analysis:

- **Popularity Score** (0-10): Based on review count and rating
- **Consumer Interest** (0-10): Overall interest indicator
- **Shop Credibility**: Based on shop rating and sales count

## Product Types

Etsy categorizes items by type:

- **Handmade**: Created by the seller
- **Vintage**: 20+ years old
- **Craft Supplies**: Materials and tools for creating

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

## Trending Indicators

Products are considered trending based on:

- Recent favorites/saves
- Review velocity
- View count trends
- Sales momentum
- Search ranking improvements

## License

Proprietary - Part of the PrismQ ecosystem

## Related Modules

- **AmazonBestsellersSource**: Mass-market product trends
- **AppStoreTopChartsSource**: Digital product trends
- **PrismQ.IdeaInspiration.Model**: Standardized idea format
- **PrismQ.IdeaInspiration.Classification**: Idea categorization

## Use Cases

Commerce data from Etsy can inform content about:

- Handmade product trends
- DIY and craft tutorials
- Artisan business insights
- Creative niche markets
- Seasonal craft trends
- Material and technique popularity

## Support

For issues and questions, please refer to the main PrismQ.IdeaInspiration repository.
