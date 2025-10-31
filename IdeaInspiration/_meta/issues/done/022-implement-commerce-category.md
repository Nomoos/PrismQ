# Implement Commerce Category Sources

**Type**: Feature
**Priority**: Medium
**Status**: Done
**Category**: Commerce
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement all Commerce category sources for collecting product and marketplace trends that indicate consumer interests and purchasing behavior.

## Sources

### Commerce
- **AmazonBestsellersSource** - Amazon bestsellers and trending products
- **EtsyTrendingSource** - Etsy marketplace trends and popular items
- **AppStoreTopChartsSource** - iOS/Android app store top charts

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Implement all 3 Commerce sources following SOLID principles
2. Extract product trends and marketplace data
3. Identify consumer interests and emerging product categories
4. Transform data to unified commerce signal format
5. Store in SQLite databases with deduplication

## Key Features (Common Across All Sources)

### Data Collection
- Product metadata (name, category, price, ratings)
- Seller/developer information
- Sales rank and trend data
- Review metrics (count, average rating, sentiment)
- Category and subcategory trends
- Pricing history and changes

### Scraping Methods
- API-based collection (where available)
- Web scraping (Amazon, Etsy product pages)
- App store APIs (iOS, Android)
- Bestseller lists and category rankings

### Universal Metrics
- Sales velocity estimates
- Review momentum (reviews per day)
- Price competitiveness
- Category dominance
- Cross-platform normalization

## Technical Requirements

### Architecture (Example: AmazonBestsellers)
```
AmazonBestsellers/
├── src/
│   ├── cli.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── commerce_processor.py
│   └── plugins/
│       ├── __init__.py
│       ├── amazon_bestsellers.py
│       └── amazon_category.py
```

### Dependencies (Varies by Source)
- amazon-paapi or python-amazon-sp-api (Amazon)
- etsy-python (Etsy API)
- google-play-scraper, app-store-scraper (app stores)
- BeautifulSoup, requests (web scraping)
- SQLite, ConfigLoad (all sources)

### Data Model (Generic Commerce Signal)
```python
{
    'source': 'commerce_source_name',
    'source_id': 'product_id',
    'product': {
        'name': 'Product Name',
        'brand': 'Brand Name',
        'category': 'Electronics > Headphones',
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
        'review_velocity': 50  # per day
    },
    'trends': {
        'rank_change_24h': -5,  # moved up 5 positions
        'price_change_pct': -10,  # 10% discount
        'review_momentum': 'increasing'
    },
    'universal_metrics': {
        'popularity_score': 8.5,
        'trend_strength': 7.8,
        'consumer_interest': 9.0
    }
}
```

## Success Criteria

- [x] All 3 Commerce sources implemented
- [x] Each source follows SOLID principles
- [x] Product and trend data extracted
- [x] Sales rank tracking working
- [x] Review metrics calculated
- [x] Deduplication working for all sources
- [x] Data transforms to unified format
- [x] CLI interfaces consistent
- [x] Comprehensive tests (>80% coverage)
- [x] Documentation complete

## Implementation Priority

1. **AmazonBestsellersSource** - Largest e-commerce platform, rich data
2. **AppStoreTopChartsSource** - Digital products, tech trends
3. **EtsyTrendingSource** - Creative/handmade products, niche trends

## Related Issues

- #001 - Unified Pipeline Integration
- #008 - Advanced Source Integrations

## API/Scraping Considerations

### Amazon
- Product Advertising API requires approval
- Scraping bestseller lists may violate ToS - use carefully
- Consider using affiliate APIs if available
- Rate limiting essential

### Etsy
- Etsy Open API requires app registration
- Rate limits: varies by endpoint
- API documentation: https://www.etsy.com/developers/documentation

### App Stores
- Google Play: unofficial libraries (google-play-scraper)
- Apple App Store: unofficial scraping or RSS feeds
- No official public APIs for rankings
- Be respectful with scraping

## Estimated Effort

4-6 weeks total
- AmazonBestsellers: 2-3 weeks
- AppStoreTopCharts: 1-2 weeks
- EtsyTrending: 1 week

## Notes

Commerce data provides valuable insights into consumer interests and emerging product categories. These signals can inform content creation about trending products, reviews, comparisons, and industry trends.

Focus on category-level trends in addition to individual products to identify broader market movements.
