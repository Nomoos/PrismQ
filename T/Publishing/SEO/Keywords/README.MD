# PrismQ.T.Publishing.SEO.Keywords

**Automated SEO Keyword Research & Optimization**

## Module Status: ✅ Complete (with AI Enhancement)

This module provides intelligent keyword extraction and SEO metadata generation for published content, including AI-powered generation using GPT/LLM models.

## Quick Start

### Basic Usage (Rule-Based)

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

### AI-Powered Generation (POST-001)

```python
from T.Publishing.SEO.Keywords import process_content_seo

result = process_content_seo(
    title="Your Content Title",
    script="Your content text...",
    use_ai=True,  # Enable AI-powered metadata generation 🤖
    brand_name="YourBrand"
)

print(result['meta_description'])  # AI-generated description
print(result['ai_generated'])      # True if AI was used
```

## Features

✅ **Keyword Extraction** - TF-IDF, frequency, and hybrid methods  
✅ **SEO Metadata** - Meta descriptions (150-160 chars), title tags (<60 chars)  
✅ **AI-Powered Generation** - GPT/LLM-based metadata using Ollama (POST-001) 🤖  
✅ **Prompt Engineering** - Optimized prompts for high-quality SEO content  
✅ **Keyword Density** - Calculate density percentages  
✅ **Related Keywords** - Context-based and AI-suggested keywords  
✅ **Quality Score** - 0-100 rating with recommendations  
✅ **Open Graph** - Social media metadata  
✅ **Performance** - <2s rule-based, <20s AI-powered  
✅ **Graceful Fallback** - Automatic fallback when AI unavailable  

## Testing

- **100+ tests passing** (25 keyword extraction, 31 metadata generation, 35+ AI generation, 29 integration)
- Run all tests: `pytest T/Publishing/SEO/Keywords/_meta/tests/ -v`
- Run AI tests: `pytest T/Publishing/SEO/Keywords/_meta/tests/test_ai_metadata_generator.py -v`

## Documentation

See [detailed documentation](./_meta/docs/README.md) for:
- Complete API reference
- Usage examples
- Integration guide
- Best practices

See [AI metadata documentation](./_meta/docs/AI_METADATA.md) for:
- AI-powered generation guide
- Prompt engineering details
- Configuration options
- Performance tuning

## Example

See working examples:
- [usage_example.py](./_meta/examples/usage_example.py) - Rule-based generation
- [ai_usage_example.py](./_meta/examples/ai_usage_example.py) - AI-powered generation 🤖

---

**Implementation**: POST-001  
**Status**: Production Ready (with AI Enhancement)  
**Worker**: Worker13 (Prompt Engineering Master)  
**Created**: 2025-11-23
