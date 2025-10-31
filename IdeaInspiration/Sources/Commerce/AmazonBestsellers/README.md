# Amazon Bestsellers Source

PrismQ module for gathering product trends from Amazon bestsellers as part of the AI-powered content generation ecosystem.

## Overview

This module scrapes Amazon bestseller data across multiple categories to identify trending products, consumer interests, and emerging market opportunities. It transforms raw e-commerce data into structured insights that can inform content creation.

## Features

- **Multi-Category Scraping**: Track bestsellers across configurable product categories
- **Product Metadata**: Capture titles, brands, prices, ratings, and reviews
- **Sales Rankings**: Monitor overall and category-specific sales ranks
- **Trend Analysis**: Calculate popularity scores and trend strength
- **Universal Metrics**: Standardized commerce metrics across platforms
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

# Amazon Configuration
AMAZON_DOMAIN=amazon.com
AMAZON_CATEGORIES=Electronics,Books,Home & Kitchen,Sports & Outdoors
AMAZON_MAX_PRODUCTS=50
AMAZON_DELAY_SECONDS=2
```

## Usage

### Scrape Bestsellers

```bash
# Using Python module
python -m src.cli scrape

# Or using installed script
amazon-bestsellers-source scrape
```

### List Products

```bash
# List all products
python -m src.cli list

# List products from specific category
python -m src.cli list --category Electronics

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
    'source': 'amazon_bestsellers',
    'source_id': 'ASIN',
    'product': {
        'name': 'Product Name',
        'brand': 'Brand Name',
        'category': 'Electronics',
        'price': 99.99,
        'currency': 'USD'
    },
    'seller': {
        'name': 'Seller Name',
        'rating': 4.8,
        'feedback_count': 10000
    },
    'metrics': {
        'sales_rank': 15,
        'category_rank': 3,
        'rating': 4.7,
        'review_count': 5000,
        'review_velocity': 50
    },
    'trends': {
        'rank_change_24h': -5,
        'price_change_pct': -10,
        'review_momentum': 'increasing'
    },
    'universal_metrics': {
        'popularity_score': 8.5,
        'trend_strength': 7.8,
        'consumer_interest': 9.0
    }
}
```

## Architecture

Following SOLID principles:

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Extensible through plugins, closed for modification
- **Liskov Substitution**: All plugins implement CommercePlugin interface
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Depends on abstractions (Config, Database)

```
AmazonBestsellers/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── config.py             # Configuration management
│   │   ├── database.py           # Database operations
│   │   ├── metrics.py            # Universal commerce metrics
│   │   └── commerce_processor.py # Data transformation
│   └── plugins/
│       ├── __init__.py           # Plugin base class
│       └── amazon_bestsellers.py # Amazon scraper plugin
├── _meta/
│   └── tests/                    # Unit tests
├── pyproject.toml                # Project metadata
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Important Notes

### Amazon's Terms of Service

⚠️ **This module currently uses mock data for demonstration purposes.**

For production use, you should:

1. **Use Amazon Product Advertising API** (requires approval from Amazon Associates program)
2. **Respect robots.txt** and Terms of Service
3. **Use authorized scraping services** if scraping is necessary
4. **Implement rate limiting** to avoid overloading servers

### API Integration

To use the real Amazon Product Advertising API:

1. Join the [Amazon Associates Program](https://affiliate-program.amazon.com/)
2. Apply for Product Advertising API access
3. Install the API client: `pip install python-amazon-paapi`
4. Configure your API credentials
5. Implement the `scrape_with_api()` method

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

## Universal Metrics

The module calculates standardized metrics for cross-platform analysis:

- **Popularity Score** (0-10): Based on review count and rating
- **Trend Strength** (0-10): Based on rank changes
- **Consumer Interest** (0-10): Weighted combination of popularity and trend

## License

Proprietary - Part of the PrismQ ecosystem

## Related Modules

- **EtsyTrendingSource**: Handmade and vintage product trends
- **AppStoreTopChartsSource**: Digital app marketplace trends
- **PrismQ.IdeaInspiration.Model**: Standardized idea format
- **PrismQ.IdeaInspiration.Classification**: Idea categorization

## Support

For issues and questions, please refer to the main PrismQ.IdeaInspiration repository.
