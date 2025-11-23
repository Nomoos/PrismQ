# PrismQ.T.Publishing.SEO.Taxonomy

**Automatic Tag Generation & Category Classification**

This module provides intelligent tag generation and category assignment for content classification, improving content organization, discoverability, and SEO optimization.

## Features

### Tag Generation
- **Keyword-based extraction**: Extract tags from provided SEO keywords
- **Content-based extraction**: Analyze title and script for relevant tags
- **Semantic expansion**: Identify related tags using semantic analysis
- **Relevance scoring**: Each tag has a confidence score (0-1)
- **Deduplication**: Automatically remove similar/duplicate tags
- **Configurable thresholds**: Customize minimum relevance and max tags

### Category Classification
- **Multi-category assignment**: Assign content to 1-3 relevant categories
- **Hierarchical structure**: Support parent/child category relationships
- **Confidence scoring**: Each category has a confidence score (0-1)
- **Keyword matching**: Match content against category keywords
- **Tag-based inference**: Use generated tags to improve classification
- **Custom taxonomies**: Define your own category structure

### Configuration
- **Default taxonomy**: 10+ predefined categories with subcategories
- **Tech-focused taxonomy**: Specialized for technology content
- **Lifestyle-focused taxonomy**: Specialized for lifestyle content
- **Custom taxonomies**: Create your own via JSON or API
- **Flexible rules**: Customize min relevance, max tags, similarity threshold

## Installation

No additional dependencies required beyond the base PrismQ installation.

## Quick Start

### Basic Usage

```python
from T.Publishing.SEO.Taxonomy import process_taxonomy

# Process content for tags and categories
result = process_taxonomy(
    title="Introduction to Machine Learning",
    script="Machine learning is a subset of AI...",
    keywords=["machine learning", "AI", "python"]
)

print(f"Tags: {', '.join(result['tags'])}")
print(f"Categories: {', '.join(result['categories'])}")
print(f"Quality Score: {result['stats']['quality_score']}/100")
```

### Tag Generation Only

```python
from T.Publishing.SEO.Taxonomy import generate_tags

result = generate_tags(
    title="Web Development with React",
    script="React is a popular JavaScript library...",
    keywords=["react", "javascript", "web dev"]
)

print(f"Tags: {result.tags}")
print(f"Relevance scores: {result.relevance_scores}")
```

### Category Classification Only

```python
from T.Publishing.SEO.Taxonomy import classify_categories

result = classify_categories(
    title="Healthy Eating Tips",
    script="Nutrition is key to wellness...",
    tags=["health", "nutrition", "wellness"]
)

print(f"Categories: {result.categories}")
print(f"Hierarchy: {result.hierarchy}")
```

### Custom Taxonomy

```python
from T.Publishing.SEO.Taxonomy import (
    process_taxonomy,
    create_custom_taxonomy
)

# Create custom taxonomy for a cooking blog
config = create_custom_taxonomy(
    categories={
        "Cooking": ["Baking", "Grilling", "Healthy"],
        "Ingredients": ["Vegetables", "Meat", "Dairy"],
        "Cuisine": ["Italian", "Asian", "Mexican"]
    },
    min_relevance=0.65,
    max_tags=8,
    max_categories=2
)

result = process_taxonomy(
    title="Easy Grilled Chicken Recipe",
    script="This healthy grilled chicken...",
    config=config
)
```

## Configuration

### TaxonomyConfig

```python
from T.Publishing.SEO.Taxonomy import TaxonomyConfig

config = TaxonomyConfig(
    categories={
        "Parent1": ["Child1", "Child2"],
        "Parent2": ["Child3"]
    },
    min_relevance=0.7,        # Minimum tag relevance score
    max_tags=10,              # Maximum number of tags
    max_categories=3,         # Maximum number of categories
    tag_similarity_threshold=0.85,  # Deduplication threshold
    enable_hierarchical=True  # Support hierarchical categories
)
```

### Default Taxonomies

Three preset taxonomies are available:

1. **DEFAULT_TAXONOMY**: General-purpose with 10+ categories
   - Technology, Business, Lifestyle, Education, Creative, Entertainment, Science, Sports, News, Personal Finance

2. **TECH_FOCUSED_TAXONOMY**: Technology-focused content
   - Programming, AI & ML, Infrastructure, Security, Databases

3. **LIFESTYLE_FOCUSED_TAXONOMY**: Lifestyle-focused content
   - Health & Wellness, Home & Living, Relationships, Personal Growth, Fashion & Beauty

```python
from T.Publishing.SEO.Taxonomy import (
    DEFAULT_TAXONOMY,
    TECH_FOCUSED_TAXONOMY,
    LIFESTYLE_FOCUSED_TAXONOMY
)
```

## API Reference

### Main Functions

#### `process_taxonomy(title, script, keywords=None, config=None, include_scores=True)`

Complete end-to-end taxonomy processing.

**Parameters:**
- `title` (str): Content title
- `script` (str): Content body text
- `keywords` (list, optional): SEO keywords from POST-001
- `config` (TaxonomyConfig, optional): Custom configuration
- `include_scores` (bool): Include relevance/confidence scores

**Returns:** Dictionary with:
- `tags`: List of generated tags
- `categories`: List of assigned categories
- `tag_scores`: Tag relevance scores (if include_scores=True)
- `category_scores`: Category confidence scores (if include_scores=True)
- `hierarchy`: Hierarchical category structure
- `stats`: Quality metrics

#### `generate_tags(title, script, keywords=None, config=None)`

Generate tags only.

**Returns:** `TagGenerationResult` with tags and scores

#### `classify_categories(title, script, tags=None, config=None)`

Classify categories only.

**Returns:** `CategoryClassificationResult` with categories and scores

### Classes

#### `TagGenerator`

Generate tags from content.

```python
from T.Publishing.SEO.Taxonomy import TagGenerator

generator = TagGenerator(config=custom_config)
result = generator.generate_tags(title, script, base_keywords)
```

#### `CategoryClassifier`

Classify content into categories.

```python
from T.Publishing.SEO.Taxonomy import CategoryClassifier

classifier = CategoryClassifier(config=custom_config)
result = classifier.classify_categories(title, script, tags)
```

## Examples

See `_meta/examples/usage_example.py` for comprehensive examples:

```bash
python T/Publishing/SEO/Taxonomy/_meta/examples/usage_example.py
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest T/Publishing/SEO/Taxonomy/_meta/tests/ -v

# Run specific test file
pytest T/Publishing/SEO/Taxonomy/_meta/tests/test_tag_generator.py -v

# Run with coverage
pytest T/Publishing/SEO/Taxonomy/_meta/tests/ --cov=T.Publishing.SEO.Taxonomy
```

## Performance

- Tag generation: <100ms for typical content
- Category classification: <50ms for typical content
- Memory efficient: Minimal memory footprint
- Scalable: Handles content from 100 to 10,000+ words

## Quality Metrics

The module provides a quality score (0-100) based on:
- **Tag Quality (40%)**: Number of tags (optimal: 5-10), average relevance (target: >0.7)
- **Category Quality (40%)**: Number of categories (optimal: 1-3), average confidence (target: >0.8)
- **Bonus (20%)**: Both tags and categories present, hierarchical structure

Target scores:
- **80-100**: Excellent taxonomy
- **60-79**: Good taxonomy
- **40-59**: Fair taxonomy
- **<40**: Needs improvement

## Integration

### With POST-001 (SEO Keywords)

```python
from T.Publishing.SEO.Keywords import process_content_seo
from T.Publishing.SEO.Taxonomy import process_taxonomy

# Step 1: Extract SEO keywords
seo_result = process_content_seo(title, script)

# Step 2: Generate tags and categories using keywords
taxonomy_result = process_taxonomy(
    title=title,
    script=script,
    keywords=seo_result['primary_keywords']
)
```

### With ContentExport

The taxonomy data can be exported as part of content metadata for publishing platforms.

## Best Practices

1. **Provide Keywords**: For best results, provide SEO keywords from POST-001
2. **Adjust Thresholds**: Lower min_relevance for broader tags, raise for stricter filtering
3. **Use Custom Taxonomies**: Create domain-specific taxonomies for specialized content
4. **Review Quality Score**: Aim for scores >60 for good taxonomy coverage
5. **Tune for Content Type**: Use preset taxonomies (Tech/Lifestyle) for specialized content

## Troubleshooting

### No tags generated
- Check min_relevance threshold (try lowering to 0.6)
- Ensure content has sufficient text (>100 words recommended)
- Verify keywords are provided or content has clear topics

### No categories assigned
- Content may be too ambiguous or short
- Try providing more specific keywords
- Consider using or creating a custom taxonomy that better matches your content domain

### Too many duplicate tags
- Increase tag_similarity_threshold (try 0.90)
- Review content for repetitive terms
- Use keyword extraction from POST-001 for cleaner input

## License

Part of the PrismQ project. See main project LICENSE for details.

## Support

For issues, questions, or contributions, see the main PrismQ repository.

---

**Created**: 2025-11-23  
**Module**: `PrismQ.T.Publishing.SEO.Taxonomy`  
**Issue**: POST-002  
**Owner**: Worker17 (Analytics Specialist)
