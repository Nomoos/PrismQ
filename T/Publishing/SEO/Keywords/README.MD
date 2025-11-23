# PrismQ.T.Publishing.SEO.Keywords

**Automated SEO Keyword Research & Optimization**

## Module Status: ✅ Complete

This module provides intelligent keyword extraction and SEO metadata generation for published content.

## Quick Start

```python
from T.Publishing.SEO.Keywords import process_content_seo

result = process_content_seo(
    title="Your Content Title",
    script="Your content text...",
    brand_name="YourBrand"  # Optional
)

print(result['primary_keywords'])    # Top keywords
print(result['meta_description'])    # SEO-optimized description
print(result['title_tag'])           # Optimized title tag
print(result['quality_score'])       # 0-100 quality rating
```

## Features

✅ **Keyword Extraction** - TF-IDF, frequency, and hybrid methods  
✅ **SEO Metadata** - Meta descriptions (150-160 chars), title tags (<60 chars)  
✅ **Keyword Density** - Calculate density percentages  
✅ **Related Keywords** - Context-based suggestions  
✅ **Quality Score** - 0-100 rating with recommendations  
✅ **Open Graph** - Social media metadata  
✅ **Performance** - <2s processing time  

## Testing

- **85 tests passing** (25 keyword extraction, 31 metadata generation, 29 integration)
- Run tests: `pytest T/Publishing/SEO/Keywords/_meta/tests/ -v`

## Documentation

See [detailed documentation](./_meta/docs/README.md) for:
- Complete API reference
- Usage examples
- Integration guide
- Best practices

## Example

See [usage_example.py](./_meta/examples/usage_example.py) for working examples.

---

**Implementation**: POST-001  
**Status**: Production Ready  
**Created**: 2025-11-23
